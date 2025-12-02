# Trade-offs and Risks

## Key Risks

| Risk | Severity | Status |
|------|----------|--------|
| **Cold-start** | Medium | Mitigated via goal-based defaults |
| **Synthetic data** | High | Must retrain on real data |
| **Feedback loops** | Medium | Freshness component helps |
| **Fairness** | Medium | Not audited |
| **Content gaps** | High | Depends on content library |

---

### Cold-Start Problem
New users have no behavioral data. We use stated goals and population-level retention data as defaults.

### Synthetic Data
Models trained on synthetic data won't transfer directly. Weights and thresholds need retraining on real user data.

### Feedback Loop Bias
Only recommending high-retention content prevents learning about other content. The `Freshness` component encourages some diversity, but explicit exploration (epsilon-greedy) would help.

### Fairness
Haven't audited for demographic bias. Goal-based personalization is demographic-agnostic, but should verify performance across segments.

### Content Quality Dependency
Recommender can only surface what exists. If content library has gaps for certain goals, recommendations suffer.

---

## What's Working Well

- **Explainability**: Every recommendation includes human-readable reasons
- **Latency**: Simple scoring function runs in milliseconds
- **Modularity**: Clear separation between churn analysis and recommendation logic