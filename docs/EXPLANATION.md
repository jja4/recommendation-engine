# Technical Explanation

This document explains how the prototype works at a high level.

## 1. Synthetic Data Generation

Since we don't have access to real Humanoo user data, we generate synthetic data that mimics realistic wellness app behavior patterns.

### Data Entities

| Entity | Description |
|--------|-------------|
| **Users** | 500 simulated users with goals, demographics, signup dates |
| **Content** | 50 wellness content items across categories (fitness, meditation, sleep, nutrition, strength) |
| **Interactions** | ~4,000 user-content interactions over 21 simulated days |

### How User Behavior is Simulated

```
For each user:
    1. Assign base engagement propensity (random 0-1)
    2. Determine if user will churn (higher engagement = lower churn probability)
    3. If churning, pick a churn day (day 3-14)
    
    For each day (0-21):
        - Calculate daily engagement probability
        - Apply decay for churning users / growth for retained users
        - If engaged: select 1-3 content pieces
        - 70% chance to pick goal-aligned content
        - Calculate completion based on content quality, duration, alignment
```

### Key Realism Features

- **Goal-content alignment**: Users prefer content matching their stated goals
- **Engagement decay**: Churning users show declining activity before dropping off
- **Completion modeling**: Shorter, easier, higher-quality content has higher completion rates
- **Return patterns**: Retained users show slight engagement growth over time

---

## 2. Churn Analysis

The churn analysis module answers: **What early signals predict whether a user will churn?**

### Features Computed (as of Day 7)

| Feature | Description |
|---------|-------------|
| `total_sessions` | Number of active days |
| `total_content_views` | Total content interactions |
| `total_time_minutes` | Total engagement time |
| `completion_rate` | % of started content that was finished |
| `avg_time_per_content` | Average time spent per content piece |
| `unique_days_active` | Days with at least one interaction |
| `days_since_last_activity` | Recency of last engagement |
| `first_session_completions` | Content completed in first session |
| `category_diversity` | Number of different categories explored |

### Churn Labeling

- **Observation window**: Features computed from days 0-7
- **Churn window**: Days 14-21
- **Churned**: No activity in churn window
- **Retained**: At least 1 interaction in churn window

### Analysis Methods

1. **Correlation Analysis**: Pearson correlation of each feature with churn
2. **Cohort Comparison**: Mean feature values for churned vs. retained users
3. **Feature Importance**: Random Forest classifier to rank predictive power
4. **Content Performance**: Which content items correlate with retention

### Typical Findings

- `days_since_last_activity` is the strongest churn predictor (positive correlation)
- `total_time_minutes` and `completion_rate` are strong retention signals
- First-session completions matter: users who complete content early are more likely to return

---

## 3. Content Recommendation Engine

The recommender answers: **What content should we show a new user to maximize their chance of retention?**

### Scoring Function

For each content item, we compute:

```
Score = w1 × GoalAlignment
      + w2 × RetentionLift
      + w3 × CompletionFriendly
      + w4 × Freshness
```

### Score Components

| Component | What It Measures | How It's Calculated |
|-----------|------------------|---------------------|
| **GoalAlignment** | Does content match user's stated goal? | Binary: category in goal's preferred categories |
| **RetentionLift** | Does this content correlate with retention? | From churn analysis: retention rate of users who viewed this content in first session |
| **CompletionFriendly** | Is this easy to complete? | Combines duration (shorter = better) and difficulty (beginner = better) |
| **Freshness** | Has user seen this before? | Penalty for already-viewed content |

### Adaptive Weights

Weights change based on session number:

| Session | GoalAlignment | RetentionLift | CompletionFriendly | Freshness |
|---------|---------------|---------------|---------------------|-----------|
| First session | 0.40 | 0.25 | 0.25 | 0.10 |
| Later sessions | 0.30 | 0.30 | 0.15 | 0.25 |

**Rationale**: First sessions prioritize goal alignment and easy wins. Later sessions balance more toward proven retention content and avoiding repetition.

### Cold-Start Handling

For brand new users with no interaction history:
1. Use stated goal to filter relevant categories
2. Prioritize content with high retention rates across all users
3. Favor beginner-friendly, shorter content
4. No freshness penalty (nothing seen yet)

### Output

Each recommendation includes:
- Content ID and metadata
- Numeric score
- Human-readable reasons (e.g., "Matches your weight_loss goal", "High retention content")

---

## 4. How It All Connects

```
┌─────────────────────────────────────────────────────────────────┐
│                        Data Pipeline                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [Synthetic Data]                                               │
│       │                                                         │
│       ▼                                                         │
│  ┌─────────────────┐                                            │
│  │ Churn Analysis  │──── Identifies which content drives        │
│  │                 │      retention (retention_lift scores)     │
│  └────────┬────────┘                                            │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────┐                                            │
│  │  Recommender    │──── Uses retention_lift + goal alignment   │
│  │                 │      + completion probability              │
│  └────────┬────────┘                                            │
│           │                                                     │
│           ▼                                                     │
│  [Personalized Recommendations]                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

The churn analysis **informs** the recommender. Content that historically correlates with retention gets boosted in recommendations. This creates a data-driven feedback loop where insights from user behavior directly improve the recommendation quality.
