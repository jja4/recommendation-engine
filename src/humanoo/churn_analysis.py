"""
Churn Analysis Module

Analyzes user engagement features to identify patterns that correlate with retention vs. churn.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score


class ChurnAnalyzer:
    """Analyzes engagement features and their correlation with churn."""
    
    FEATURE_COLUMNS = [
        "total_sessions",
        "total_content_views",
        "total_time_minutes",
        "completion_rate",
        "avg_time_per_content",
        "unique_days_active",
        "days_since_last_activity",
        "first_session_completions",
        "category_diversity",
    ]
    
    def __init__(self):
        self.model = None
        self.feature_importance = None
    
    def analyze_correlations(self, features_df: pd.DataFrame, labels_df: pd.DataFrame) -> pd.DataFrame:
        """Compute correlation of each feature with churn."""
        
        data = features_df.merge(labels_df, on="user_id")
        data["churned_int"] = data["churned"].astype(int)
        
        correlations = []
        for col in self.FEATURE_COLUMNS:
            corr = data[col].corr(data["churned_int"])
            correlations.append({"feature": col, "correlation_with_churn": corr})
        
        return pd.DataFrame(correlations).sort_values("correlation_with_churn")
    
    def compare_cohorts(self, features_df: pd.DataFrame, labels_df: pd.DataFrame) -> pd.DataFrame:
        """Compare mean feature values between churned and retained users."""
        
        data = features_df.merge(labels_df, on="user_id")
        
        churned = data[data["churned"]][self.FEATURE_COLUMNS].mean()
        retained = data[~data["churned"]][self.FEATURE_COLUMNS].mean()
        
        comparison = pd.DataFrame({
            "feature": self.FEATURE_COLUMNS,
            "churned_mean": churned.values,
            "retained_mean": retained.values,
        })
        comparison["difference"] = comparison["retained_mean"] - comparison["churned_mean"]
        comparison["pct_difference"] = (comparison["difference"] / comparison["churned_mean"].replace(0, np.nan)) * 100
        
        return comparison.sort_values("pct_difference", ascending=False)
    
    def train_importance_model(self, features_df: pd.DataFrame, labels_df: pd.DataFrame) -> dict:
        """Train a model to identify feature importance for churn prediction."""
        
        data = features_df.merge(labels_df, on="user_id")
        
        X = data[self.FEATURE_COLUMNS].fillna(0)
        y = data["churned"].astype(int)
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        self.model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
        self.model.fit(X_train, y_train)
        
        # Feature importance
        self.feature_importance = dict(zip(self.FEATURE_COLUMNS, self.model.feature_importances_))
        
        # Evaluation
        y_pred = self.model.predict(X_test)
        y_prob = self.model.predict_proba(X_test)[:, 1]
        
        return {
            "feature_importance": self.feature_importance,
            "roc_auc": roc_auc_score(y_test, y_prob),
            "classification_report": classification_report(y_test, y_pred, output_dict=True),
        }
    
    def analyze_content_performance(
        self,
        interactions_df: pd.DataFrame,
        content_df: pd.DataFrame,
        labels_df: pd.DataFrame
    ) -> pd.DataFrame:
        """Analyze which content drives retention."""
        
        # Merge all data
        data = interactions_df.merge(labels_df, on="user_id")
        data = data.merge(content_df, on="content_id")
        
        # First session only (day 0)
        first_session = data[data["day_number"] == 0]
        
        # Content performance metrics
        content_stats = first_session.groupby("content_id").agg({
            "user_id": "count",
            "completed": "mean",
            "churned": lambda x: 1 - x.mean(),  # Retention rate
            "time_spent_minutes": "mean",
        }).reset_index()
        
        content_stats.columns = ["content_id", "view_count", "completion_rate", "retention_rate", "avg_time_spent"]
        
        # Merge with content info
        content_stats = content_stats.merge(content_df[["content_id", "category", "format", "duration_minutes"]], on="content_id")
        
        # Filter to content with enough views
        content_stats = content_stats[content_stats["view_count"] >= 5]
        
        return content_stats.sort_values("retention_rate", ascending=False)
    
    def plot_analysis(
        self,
        features_df: pd.DataFrame,
        labels_df: pd.DataFrame,
        save_path: str = None
    ):
        """Generate visualization of churn analysis."""
        
        data = features_df.merge(labels_df, on="user_id")
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle("Churn Analysis Dashboard", fontsize=14, fontweight="bold")
        
        # 1. Completion rate by churn status
        ax1 = axes[0, 0]
        data.boxplot(column="completion_rate", by="churned", ax=ax1)
        ax1.set_title("Completion Rate by Churn Status")
        ax1.set_xlabel("Churned")
        ax1.set_ylabel("Completion Rate")
        plt.suptitle("")  # Remove automatic title
        
        # 2. First session completions distribution
        ax2 = axes[0, 1]
        churned_fsc = data[data["churned"]]["first_session_completions"]
        retained_fsc = data[~data["churned"]]["first_session_completions"]
        ax2.hist(churned_fsc, bins=range(0, 8), alpha=0.6, label="Churned", color="red")
        ax2.hist(retained_fsc, bins=range(0, 8), alpha=0.6, label="Retained", color="green")
        ax2.set_title("First Session Completions")
        ax2.set_xlabel("Completions in First Session")
        ax2.set_ylabel("Count")
        ax2.legend()
        
        # 3. Feature importance
        ax3 = axes[1, 0]
        if self.feature_importance:
            sorted_imp = sorted(self.feature_importance.items(), key=lambda x: x[1], reverse=True)
            features, importances = zip(*sorted_imp)
            ax3.barh(range(len(features)), importances, color="steelblue")
            ax3.set_yticks(range(len(features)))
            ax3.set_yticklabels(features, fontsize=8)
            ax3.invert_yaxis()
            ax3.set_title("Feature Importance for Churn Prediction")
            ax3.set_xlabel("Importance")
        else:
            ax3.text(0.5, 0.5, "Train model first", ha="center", va="center")
        
        # 4. Days since last activity
        ax4 = axes[1, 1]
        data.boxplot(column="days_since_last_activity", by="churned", ax=ax4)
        ax4.set_title("Days Since Last Activity by Churn Status")
        ax4.set_xlabel("Churned")
        ax4.set_ylabel("Days")
        plt.suptitle("")
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches="tight")
            print(f"Saved plot to {save_path}")
        
        plt.close()
        return fig


def run_churn_analysis(data: dict) -> dict:
    """Run complete churn analysis and return results."""
    
    analyzer = ChurnAnalyzer()
    
    print("\n" + "="*50)
    print("CHURN ANALYSIS RESULTS")
    print("="*50)
    
    # Correlations
    print("\n--- Feature Correlations with Churn ---")
    correlations = analyzer.analyze_correlations(data["features"], data["labels"])
    print(correlations.to_string(index=False))
    
    # Cohort comparison
    print("\n--- Retained vs Churned Comparison ---")
    comparison = analyzer.compare_cohorts(data["features"], data["labels"])
    print(comparison.to_string(index=False))
    
    # Feature importance
    print("\n--- Training Churn Prediction Model ---")
    model_results = analyzer.train_importance_model(data["features"], data["labels"])
    print(f"ROC AUC: {model_results['roc_auc']:.3f}")
    print("\nTop 5 Important Features:")
    sorted_imp = sorted(model_results["feature_importance"].items(), key=lambda x: x[1], reverse=True)
    for feat, imp in sorted_imp[:5]:
        print(f"  {feat}: {imp:.3f}")
    
    # Content performance
    print("\n--- Top Content by Retention Rate (First Session) ---")
    content_perf = analyzer.analyze_content_performance(
        data["interactions"], data["content"], data["labels"]
    )
    print(content_perf.head(10).to_string(index=False))
    
    # Generate plot
    analyzer.plot_analysis(data["features"], data["labels"], save_path="churn_analysis.png")
    
    return {
        "correlations": correlations,
        "cohort_comparison": comparison,
        "model_results": model_results,
        "content_performance": content_perf,
        "analyzer": analyzer,
    }
