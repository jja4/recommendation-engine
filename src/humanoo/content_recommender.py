"""
Content Recommendation Engine

Recommends personalized content for new users based on their goals and similar user behavior.
"""

import numpy as np
import pandas as pd
from typing import Optional
from dataclasses import dataclass


@dataclass
class Recommendation:
    """A content recommendation with scoring details."""
    content_id: str
    score: float
    reasons: list[str]


class ContentRecommender:
    """
    Hybrid recommender combining:
    1. Goal alignment (content-based)
    2. Retention lift from churn analysis (data-driven)
    3. Similar user preferences (collaborative)
    """
    
    GOAL_CATEGORY_MAP = {
        "weight_loss": ["fitness", "nutrition"],
        "stress_reduction": ["meditation", "sleep"],
        "better_sleep": ["sleep", "meditation"],
        "build_strength": ["strength", "fitness"],
    }
    
    def __init__(
        self,
        content_df: pd.DataFrame,
        content_performance: Optional[pd.DataFrame] = None,
        interactions_df: Optional[pd.DataFrame] = None,
        labels_df: Optional[pd.DataFrame] = None,
    ):
        """
        Initialize recommender.
        
        Args:
            content_df: Content library
            content_performance: Content retention stats from churn analysis
            interactions_df: Historical user interactions (for collaborative filtering)
            labels_df: Churn labels (for learning from retained users)
        """
        self.content_df = content_df
        self.content_performance = content_performance
        self.interactions_df = interactions_df
        self.labels_df = labels_df
        
        # Precompute retention lift scores
        self._compute_retention_scores()
        
        # Precompute similar user patterns
        self._compute_user_patterns()
    
    def _compute_retention_scores(self):
        """Compute retention lift for each content item."""
        
        self.retention_scores = {}
        
        if self.content_performance is not None:
            # Normalize retention rate to 0-1 score
            min_ret = self.content_performance["retention_rate"].min()
            max_ret = self.content_performance["retention_rate"].max()
            
            for _, row in self.content_performance.iterrows():
                if max_ret > min_ret:
                    score = (row["retention_rate"] - min_ret) / (max_ret - min_ret)
                else:
                    score = 0.5
                self.retention_scores[row["content_id"]] = score
        
        # Default score for content not in performance data
        self.default_retention_score = 0.5
    
    def _compute_user_patterns(self):
        """Learn content preferences from retained users (collaborative filtering basis)."""
        
        self.goal_content_prefs = {goal: {} for goal in self.GOAL_CATEGORY_MAP}
        
        if self.interactions_df is None or self.labels_df is None:
            return
        
        # Focus on retained users' first sessions
        retained_users = self.labels_df[~self.labels_df["churned"]]["user_id"].tolist()
        
        retained_interactions = self.interactions_df[
            (self.interactions_df["user_id"].isin(retained_users)) &
            (self.interactions_df["day_number"] == 0) &  # First session
            (self.interactions_df["completed"] == True)  # Completed content
        ]
        
        if len(retained_interactions) == 0:
            return
        
        # Need user goals - this would come from users_df in practice
        # For now, we'll compute category preferences by goal from interactions
        merged = retained_interactions.merge(
            self.content_df[["content_id", "category"]], on="content_id"
        )
        
        # Count category preferences (simplified - in practice we'd join with user goals)
        category_counts = merged.groupby("category")["content_id"].count()
        total = category_counts.sum()
        
        self.popular_categories = (category_counts / total).to_dict()
    
    def score_content(
        self,
        content_id: str,
        user_goal: str,
        seen_content: list[str] = None,
        weights: dict = None,
    ) -> tuple[float, list[str]]:
        """
        Score a content item for a user.
        
        Returns:
            (score, reasons) tuple
        """
        if seen_content is None:
            seen_content = []
        
        if weights is None:
            weights = {
                "goal_alignment": 0.35,
                "retention_lift": 0.30,
                "completion_friendly": 0.20,
                "freshness": 0.15,
            }
        
        content = self.content_df[self.content_df["content_id"] == content_id].iloc[0]
        
        score = 0.0
        reasons = []
        
        # 1. Goal alignment
        preferred_categories = self.GOAL_CATEGORY_MAP.get(user_goal, [])
        if content["category"] in preferred_categories:
            score += weights["goal_alignment"]
            reasons.append(f"Matches your {user_goal} goal")
        
        # 2. Retention lift (from churn analysis)
        retention_score = self.retention_scores.get(content_id, self.default_retention_score)
        score += weights["retention_lift"] * retention_score
        if retention_score > 0.7:
            reasons.append("High retention content")
        
        # 3. Completion-friendly (shorter, beginner content for new users)
        duration_score = max(0, 1 - (content["duration_minutes"] - 5) / 30)  # Prefer 5-15 min
        difficulty_score = {"beginner": 1.0, "intermediate": 0.6, "advanced": 0.3}.get(content["difficulty"], 0.5)
        completion_score = (duration_score + difficulty_score) / 2
        score += weights["completion_friendly"] * completion_score
        if content["difficulty"] == "beginner" and content["duration_minutes"] <= 15:
            reasons.append("Easy to complete")
        
        # 4. Freshness (penalize already-seen content)
        if content_id in seen_content:
            score -= weights["freshness"]
        else:
            score += weights["freshness"] * 0.5
        
        return score, reasons
    
    def recommend(
        self,
        user_goal: str,
        n_recommendations: int = 5,
        seen_content: list[str] = None,
        session_number: int = 1,
    ) -> list[Recommendation]:
        """
        Generate content recommendations for a user.
        
        Args:
            user_goal: User's stated goal
            n_recommendations: Number of recommendations to return
            seen_content: Content IDs already viewed by user
            session_number: Which session this is (1 = first session)
            
        Returns:
            List of Recommendation objects
        """
        if seen_content is None:
            seen_content = []
        
        # Adjust weights based on session number
        if session_number == 1:
            # First session: prioritize completion-friendly and goal alignment
            weights = {
                "goal_alignment": 0.40,
                "retention_lift": 0.25,
                "completion_friendly": 0.25,
                "freshness": 0.10,
            }
        else:
            # Later sessions: more balanced, add diversity
            weights = {
                "goal_alignment": 0.30,
                "retention_lift": 0.30,
                "completion_friendly": 0.15,
                "freshness": 0.25,
            }
        
        # Score all content
        scores = []
        for _, content in self.content_df.iterrows():
            content_id = content["content_id"]
            score, reasons = self.score_content(content_id, user_goal, seen_content, weights)
            scores.append(Recommendation(content_id=content_id, score=score, reasons=reasons))
        
        # Sort by score and return top N
        scores.sort(key=lambda x: x.score, reverse=True)
        
        return scores[:n_recommendations]
    
    def explain_recommendation(self, rec: Recommendation) -> str:
        """Generate human-readable explanation for a recommendation."""
        
        content = self.content_df[self.content_df["content_id"] == rec.content_id].iloc[0]
        
        explanation = f"**{content['title']}**\n"
        explanation += f"  Category: {content['category']} | Format: {content['format']} | {content['duration_minutes']} min\n"
        explanation += f"  Score: {rec.score:.2f}\n"
        
        if rec.reasons:
            explanation += f"  Why: {', '.join(rec.reasons)}\n"
        
        return explanation


def demonstrate_recommendations(data: dict, churn_results: dict = None):
    """Demonstrate the recommendation engine with sample users."""
    
    print("\n" + "="*50)
    print("CONTENT RECOMMENDATION DEMO")
    print("="*50)
    
    # Initialize recommender
    content_performance = churn_results["content_performance"] if churn_results else None
    
    recommender = ContentRecommender(
        content_df=data["content"],
        content_performance=content_performance,
        interactions_df=data["interactions"],
        labels_df=data["labels"],
    )
    
    # Demo for each goal type
    goals = ["weight_loss", "stress_reduction", "better_sleep", "build_strength"]
    
    for goal in goals:
        print(f"\n--- Recommendations for New User (Goal: {goal}) ---")
        
        recommendations = recommender.recommend(
            user_goal=goal,
            n_recommendations=3,
            session_number=1,
        )
        
        for i, rec in enumerate(recommendations, 1):
            print(f"\n{i}. {recommender.explain_recommendation(rec)}")
    
    # Simulate a returning user
    print("\n--- Recommendations for Returning User (Session 2) ---")
    print("Goal: weight_loss | Already seen: [c_001, c_005, c_010]")
    
    recommendations = recommender.recommend(
        user_goal="weight_loss",
        n_recommendations=3,
        seen_content=["c_001", "c_005", "c_010"],
        session_number=2,
    )
    
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. {recommender.explain_recommendation(rec)}")
    
    return recommender
