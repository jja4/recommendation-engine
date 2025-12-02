# Simplification: 2-Day Sprint

If limited to **2 days**, here's what to keep vs cut.

## Day 1: Churn Analysis Only

| Task | Deliverable |
|------|-------------|
| Define churn with PM | Clear metric: "No activity in days 14-21" |
| Compute basic features | Sessions, completions, time spent, recency |
| Correlation analysis | Which features predict churn? |
| Cohort comparison | Churned vs retained differences |

**Output**: 1-page summary of churn predictors.

## Day 2: Content Analysis

| Task | Deliverable |
|------|-------------|
| First-session content analysis | Retention rate by content |
| Category performance | Which categories drive retention? |
| Simple recommendation rules | "For goal X, show content Y, Z" |

**Output**: Lookup table of top content per goal.

---

## What to Cut

- **ML models** — Correlation analysis gives majority of insight
- **Sophisticated scoring** — Simple rules work for MVP
- **Adaptive weights** — Tune later with A/B tests
- **Synthetic data** — Use real data directly

---

## Key Principle

> **Insight before infrastructure.**

A simple analysis showing "completion rate correlates 0.4 with retention" is more valuable than a sophisticated model trained on assumptions.
