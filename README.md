# Humanoo Wellness Assistant Prototype

AI-powered churn analysis and content recommendation engine to improve early user retention.

## Overview

This prototype addresses the challenge of user drop-off after the first two weeks in a digital wellness app. It implements:

1. **Churn Analysis** — Identify which engagement patterns correlate with retention vs. churn
2. **Content Recommendation Engine** — Personalize first-session content to maximize early perceived value

## Quick Start

### Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) package manager

### Setup

```bash
# Clone/navigate to the project
cd humanoo

# Install dependencies
uv sync
```

### Run the Demo

```bash
uv run python -m humanoo.main
```

This will:
1. Generate synthetic user/content/interaction data
2. Run churn analysis and display feature correlations
3. Demonstrate content recommendations for different user goals
4. Save a visualization to `churn_analysis.png`

## Project Structure

```
humanoo/
├── README.md                      # This file
├── pyproject.toml                 # Project configuration
├── docs/
│   ├── 01_problem_exploration.md  # Problem analysis
│   ├── 02_solution_proposal.md    # Solution design
│   ├── 03_tradeoffs_and_risks.md  # Risks and limitations
│   ├── 04_simplification.md       # 2-day sprint scope
│   └── EXPLANATION.md             # Technical deep-dive
└── src/humanoo/
    ├── __init__.py
    ├── data_generator.py          # Synthetic data generation
    ├── churn_analysis.py          # Feature analysis & ML
    ├── content_recommender.py     # Recommendation engine
    └── main.py                    # Demo entry point
```

## What's Implemented

### Churn Analysis (`churn_analysis.py`)

- Feature correlation with churn
- Cohort comparison (churned vs retained users)
- Random Forest feature importance ranking
- Content performance analysis (which content drives retention)

**Key Findings** (from synthetic data):
- `days_since_last_activity` is the strongest churn predictor
- First-session completion rate strongly correlates with retention
- Retained users have ~2x more engagement time

### Content Recommender (`content_recommender.py`)

Hybrid scoring function combining:
- **Goal alignment**: Match content category to user's stated goal
- **Retention lift**: Boost content that historically correlates with retention
- **Completion probability**: Favor shorter, beginner-friendly content for new users
- **Freshness**: Avoid recommending already-seen content

Features:
- Cold-start handling for new users
- Adaptive weights (first session vs returning users)
- Explainable recommendations with human-readable reasons

### Data Generator (`data_generator.py`)

Creates realistic synthetic data including:
- User profiles with goals and demographics
- Content library across wellness categories
- Interaction history with realistic engagement patterns
- Simulated churn behavior

## Sample Output

```
--- Recommendations for New User (Goal: weight_loss) ---

1. **Fitness Session 47**
   Category: fitness | Format: video | 11 min
   Score: 0.91
   Why: Matches your weight_loss goal, High retention content, Easy to complete

2. **Nutrition Session 45**
   Category: nutrition | Format: audio | 4 min
   Score: 0.89
   Why: Matches your weight_loss goal, High retention content
```

## Documentation

| Document | Description |
|----------|-------------|
| [Problem Exploration](docs/01_problem_exploration.md) | Core problem analysis and assumptions |
| [Solution Proposal](docs/02_solution_proposal.md) | Two-part approach design |
| [Trade-offs & Risks](docs/03_tradeoffs_and_risks.md) | Key limitations and mitigations |
| [Simplification](docs/04_simplification.md) | What to cut for a 2-day sprint |
| [Technical Explanation](docs/EXPLANATION.md) | How the code works |

## Limitations

- **Synthetic data**: Models need retraining on real data before production use
- **Cold-start**: Limited personalization for brand new users
- **No A/B testing**: Would need experimentation framework to validate improvements

See [Trade-offs & Risks](docs/03_tradeoffs_and_risks.md) for full analysis.

## Next Steps

If this were to move toward production:

1. **Data integration**: Connect to real user event streams
2. **A/B testing**: Validate that recommendations improve retention
3. **Feedback loops**: Update models based on recommendation outcomes
4. **Scaling**: Pre-compute scores for large content libraries

---

*Built as a case study prototype demonstrating churn analysis and content personalization approaches.*
