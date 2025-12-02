"""
Synthetic data generation for wellness app users, content, and interactions.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

np.random.seed(42)


# Constants
GOALS = ["weight_loss", "stress_reduction", "better_sleep", "build_strength"]
CONTENT_CATEGORIES = ["fitness", "meditation", "sleep", "nutrition", "strength"]
CONTENT_FORMATS = ["video", "audio", "article"]


def generate_content_library(n_items: int = 50) -> pd.DataFrame:
    """Generate a content library with various wellness content."""
    
    # Map goals to relevant categories
    goal_category_map = {
        "weight_loss": ["fitness", "nutrition"],
        "stress_reduction": ["meditation", "sleep"],
        "better_sleep": ["sleep", "meditation"],
        "build_strength": ["strength", "fitness"],
    }
    
    items = []
    for i in range(n_items):
        category = np.random.choice(CONTENT_CATEGORIES)
        
        # Duration varies by format and category
        base_duration = {"fitness": 15, "meditation": 10, "sleep": 20, "nutrition": 5, "strength": 20}
        duration = int(base_duration[category] * np.random.uniform(0.5, 1.5))
        
        # Simulate content quality (affects completion rates)
        quality_score = np.random.beta(5, 2)  # Skewed toward higher quality
        
        items.append({
            "content_id": f"c_{i:03d}",
            "category": category,
            "format": np.random.choice(CONTENT_FORMATS, p=[0.5, 0.3, 0.2]),
            "duration_minutes": duration,
            "difficulty": np.random.choice(["beginner", "intermediate", "advanced"], p=[0.4, 0.4, 0.2]),
            "quality_score": quality_score,  # Hidden attribute affecting engagement
            "title": f"{category.title()} Session {i+1}",
        })
    
    return pd.DataFrame(items)


def generate_users(n_users: int = 500) -> pd.DataFrame:
    """Generate synthetic user profiles."""
    
    users = []
    for i in range(n_users):
        age = int(np.random.normal(35, 12))
        age = max(18, min(70, age))
        
        users.append({
            "user_id": f"u_{i:05d}",
            "goal": np.random.choice(GOALS),
            "age": age,
            "gender": np.random.choice(["M", "F", "Other"], p=[0.45, 0.50, 0.05]),
            "signup_date": datetime(2024, 10, 1) + timedelta(days=np.random.randint(0, 30)),
        })
    
    return pd.DataFrame(users)


def simulate_user_sessions(
    users_df: pd.DataFrame,
    content_df: pd.DataFrame,
    simulation_days: int = 21
) -> pd.DataFrame:
    """
    Simulate user content interactions with realistic engagement patterns.
    
    Key behaviors:
    - Users more likely to engage with goal-aligned content
    - Completion rate depends on content quality, duration, and user-content fit
    - Engagement decays over time (churn simulation)
    - Some users retain, some churn
    """
    
    goal_category_map = {
        "weight_loss": ["fitness", "nutrition"],
        "stress_reduction": ["meditation", "sleep"],
        "better_sleep": ["sleep", "meditation"],
        "build_strength": ["strength", "fitness"],
    }
    
    interactions = []
    
    for _, user in users_df.iterrows():
        user_id = user["user_id"]
        user_goal = user["goal"]
        signup = user["signup_date"]
        
        # User-level engagement propensity (some users are more engaged)
        base_engagement = np.random.beta(2, 2)  # 0-1, centered around 0.5
        
        # Determine if user will churn (for labeling purposes)
        # Higher base_engagement = less likely to churn
        churn_prob = 0.7 - (base_engagement * 0.5)  # 20%-70% churn probability
        will_churn = np.random.random() < churn_prob
        churn_day = np.random.randint(3, 14) if will_churn else None
        
        # Simulate daily activity
        for day in range(simulation_days):
            current_date = signup + timedelta(days=day)
            
            # Check if user has churned
            if will_churn and day >= churn_day:
                # Small chance of return after churn
                if np.random.random() > 0.05:
                    continue
            
            # Daily engagement probability (decays over time for non-retained users)
            if will_churn:
                decay_factor = max(0.1, 1 - (day / churn_day) * 0.5)
            else:
                decay_factor = min(1.2, 1 + day * 0.02)  # Retained users slightly increase
            
            daily_prob = base_engagement * decay_factor * 0.6
            
            if np.random.random() > daily_prob:
                continue  # No session today
            
            # Number of content pieces this session
            n_content = np.random.choice([1, 2, 3], p=[0.5, 0.35, 0.15])
            
            # Select content
            preferred_categories = goal_category_map[user_goal]
            
            for _ in range(n_content):
                # 70% chance to pick goal-aligned content
                if np.random.random() < 0.7:
                    aligned_content = content_df[content_df["category"].isin(preferred_categories)]
                    if len(aligned_content) > 0:
                        content = aligned_content.sample(1).iloc[0]
                    else:
                        content = content_df.sample(1).iloc[0]
                else:
                    content = content_df.sample(1).iloc[0]
                
                # Calculate completion probability
                # Factors: content quality, duration, goal alignment
                is_aligned = content["category"] in preferred_categories
                
                completion_prob = (
                    0.3  # Base
                    + content["quality_score"] * 0.3  # Quality boost
                    + (0.2 if is_aligned else 0)  # Alignment boost
                    - (content["duration_minutes"] / 60) * 0.2  # Duration penalty
                    + base_engagement * 0.2  # User engagement factor
                )
                completion_prob = max(0.1, min(0.95, completion_prob))
                
                completed = np.random.random() < completion_prob
                
                # Time spent
                if completed:
                    time_spent = content["duration_minutes"] * np.random.uniform(0.9, 1.1)
                else:
                    # Partial completion
                    time_spent = content["duration_minutes"] * np.random.uniform(0.1, 0.7)
                
                interactions.append({
                    "user_id": user_id,
                    "content_id": content["content_id"],
                    "date": current_date,
                    "day_number": day,
                    "completed": completed,
                    "time_spent_minutes": round(time_spent, 1),
                    "session_number": day + 1,  # Simplified: 1 session per active day
                })
    
    return pd.DataFrame(interactions)


def compute_user_features(
    users_df: pd.DataFrame,
    interactions_df: pd.DataFrame,
    content_df: pd.DataFrame,
    as_of_day: int = 7
) -> pd.DataFrame:
    """
    Compute engagement features for each user as of a specific day.
    These features are used for churn analysis.
    """
    
    # Filter interactions to observation window
    obs_interactions = interactions_df[interactions_df["day_number"] <= as_of_day]
    
    features = []
    
    for _, user in users_df.iterrows():
        user_id = user["user_id"]
        user_ints = obs_interactions[obs_interactions["user_id"] == user_id]
        
        if len(user_ints) == 0:
            # No interactions - high churn risk
            features.append({
                "user_id": user_id,
                "goal": user["goal"],
                "total_sessions": 0,
                "total_content_views": 0,
                "total_time_minutes": 0,
                "completion_rate": 0,
                "avg_time_per_content": 0,
                "unique_days_active": 0,
                "days_since_last_activity": as_of_day,
                "first_session_completions": 0,
                "category_diversity": 0,
            })
        else:
            # Merge with content info
            user_ints = user_ints.merge(content_df[["content_id", "category"]], on="content_id")
            
            total_views = len(user_ints)
            completions = user_ints["completed"].sum()
            
            # First session metrics (day 0)
            first_session = user_ints[user_ints["day_number"] == 0]
            first_session_completions = first_session["completed"].sum() if len(first_session) > 0 else 0
            
            features.append({
                "user_id": user_id,
                "goal": user["goal"],
                "total_sessions": user_ints["day_number"].nunique(),
                "total_content_views": total_views,
                "total_time_minutes": user_ints["time_spent_minutes"].sum(),
                "completion_rate": completions / total_views if total_views > 0 else 0,
                "avg_time_per_content": user_ints["time_spent_minutes"].mean(),
                "unique_days_active": user_ints["day_number"].nunique(),
                "days_since_last_activity": as_of_day - user_ints["day_number"].max(),
                "first_session_completions": first_session_completions,
                "category_diversity": user_ints["category"].nunique(),
            })
    
    return pd.DataFrame(features)


def label_churn(
    users_df: pd.DataFrame,
    interactions_df: pd.DataFrame,
    churn_window_start: int = 14,
    churn_window_end: int = 21,
    min_activity_threshold: int = 1
) -> pd.DataFrame:
    """
    Label users as churned or retained based on activity in days 14-21.
    
    Churned = no activity in the churn window
    Retained = at least min_activity_threshold interactions in churn window
    """
    
    churn_window = interactions_df[
        (interactions_df["day_number"] >= churn_window_start) &
        (interactions_df["day_number"] <= churn_window_end)
    ]
    
    activity_in_window = churn_window.groupby("user_id").size().reset_index(name="activity_count")
    
    labels = users_df[["user_id"]].copy()
    labels = labels.merge(activity_in_window, on="user_id", how="left")
    labels["activity_count"] = labels["activity_count"].fillna(0)
    labels["churned"] = labels["activity_count"] < min_activity_threshold
    
    return labels[["user_id", "churned"]]


def generate_dataset(n_users: int = 500, n_content: int = 50):
    """Generate complete dataset for analysis."""
    
    print("Generating content library...")
    content_df = generate_content_library(n_content)
    
    print("Generating users...")
    users_df = generate_users(n_users)
    
    print("Simulating user sessions...")
    interactions_df = simulate_user_sessions(users_df, content_df)
    
    print("Computing user features (as of day 7)...")
    features_df = compute_user_features(users_df, interactions_df, content_df, as_of_day=7)
    
    print("Labeling churn...")
    labels_df = label_churn(users_df, interactions_df)
    
    # Summary
    churn_rate = labels_df["churned"].mean()
    print(f"\n--- Dataset Summary ---")
    print(f"Users: {len(users_df)}")
    print(f"Content items: {len(content_df)}")
    print(f"Total interactions: {len(interactions_df)}")
    print(f"Churn rate (day 14-21): {churn_rate:.1%}")
    
    return {
        "users": users_df,
        "content": content_df,
        "interactions": interactions_df,
        "features": features_df,
        "labels": labels_df,
    }


if __name__ == "__main__":
    data = generate_dataset()
    print("\nSample features:")
    print(data["features"].head())
