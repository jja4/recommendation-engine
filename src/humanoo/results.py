"""
Results persistence for saving analysis outputs.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Any
import pandas as pd


class ResultsManager:
    """Manages saving and loading analysis results."""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create timestamped run directory
        self.run_dir = self.output_dir / f"run_{self.timestamp}"
        self.run_dir.mkdir(exist_ok=True)
    
    def save_dataframe(self, df: pd.DataFrame, name: str) -> Path:
        """Save a DataFrame to CSV."""
        path = self.run_dir / f"{name}.csv"
        df.to_csv(path, index=False)
        return path
    
    def save_json(self, data: dict, name: str) -> Path:
        """Save a dictionary to JSON."""
        path = self.run_dir / f"{name}.json"
        
        # Convert non-serializable types
        serializable = self._make_serializable(data)
        
        with open(path, "w") as f:
            json.dump(serializable, f, indent=2)
        return path
    
    def _make_serializable(self, obj: Any) -> Any:
        """Convert objects to JSON-serializable types."""
        if isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(v) for v in obj]
        elif isinstance(obj, pd.DataFrame):
            return obj.to_dict(orient="records")
        elif isinstance(obj, (int, float, str, bool, type(None))):
            return obj
        elif hasattr(obj, "__dict__"):
            return self._make_serializable(obj.__dict__)
        else:
            return str(obj)
    
    def save_churn_results(self, churn_results: dict) -> dict:
        """Save all churn analysis results."""
        paths = {}
        
        # Feature correlations
        if "correlations" in churn_results:
            paths["correlations"] = str(self.save_dataframe(
                churn_results["correlations"], "churn_correlations"
            ))
        
        # Cohort comparison
        if "cohort_comparison" in churn_results:
            paths["cohort_comparison"] = str(self.save_dataframe(
                churn_results["cohort_comparison"], "cohort_comparison"
            ))
        
        # Content performance
        if "content_performance" in churn_results:
            paths["content_performance"] = str(self.save_dataframe(
                churn_results["content_performance"], "content_performance"
            ))
        
        # Model results (feature importance, metrics)
        if "model_results" in churn_results:
            model_data = {
                "roc_auc": churn_results["model_results"].get("roc_auc"),
                "feature_importance": churn_results["model_results"].get("feature_importance"),
                "classification_report": churn_results["model_results"].get("classification_report"),
            }
            paths["model_results"] = str(self.save_json(model_data, "model_results"))
        
        return paths
    
    def save_recommendations(self, recommendations: list) -> Path:
        """Save recommendations list to CSV."""
        df = pd.DataFrame(recommendations)
        return self.save_dataframe(df, "recommendations")
    
    def save_summary(self, summary: dict) -> Path:
        """Save run summary."""
        return self.save_json(summary, "run_summary")
    
    def get_run_dir(self) -> Path:
        """Get the current run output directory."""
        return self.run_dir
