"""Main demo script for the Humanoo churn analysis and recommendation engine."""

from humanoo.data_generator import generate_dataset
from humanoo.churn_analysis import run_churn_analysis
from humanoo.content_recommender import ContentRecommender
from humanoo.logging_config import setup_logging
from humanoo.results import ResultsManager


def main():
    """Run the full demo pipeline."""
    # Setup logging and results manager
    logger = setup_logging()
    results_manager = ResultsManager()
    
    logger.info("=" * 60)
    logger.info("HUMANOO CHURN ANALYSIS & CONTENT RECOMMENDATION DEMO")
    logger.info("=" * 60)
    
    # Step 1: Generate synthetic data
    logger.info("\n[Step 1] Generating synthetic dataset...")
    data = generate_dataset(n_users=500, n_content=50)
    logger.info(f"  - Users: {len(data['users'])}")
    logger.info(f"  - Content items: {len(data['content'])}")
    logger.info(f"  - Interactions: {len(data['interactions'])}")
    logger.info(f"  - Churn rate: {data['labels']['churned'].mean():.1%}")
    
    # Step 2: Run churn analysis
    logger.info("\n[Step 2] Running churn analysis...")
    analysis_results = run_churn_analysis(data)
    
    logger.info("\nTop features correlated with churn:")
    correlations_df = analysis_results["correlations"]
    # Sort by absolute correlation
    correlations_df["abs_corr"] = correlations_df["correlation_with_churn"].abs()
    top_corrs = correlations_df.nlargest(5, "abs_corr")
    for _, row in top_corrs.iterrows():
        logger.info(f"  - {row['feature']}: {row['correlation_with_churn']:+.3f}")
    
    logger.info("\nRandom Forest feature importance:")
    importance = analysis_results["model_results"]["feature_importance"]
    for feature, imp in sorted(importance.items(), key=lambda x: x[1], reverse=True)[:5]:
        logger.info(f"  - {feature}: {imp:.3f}")
    
    logger.info(f"\nModel ROC AUC: {analysis_results['model_results']['roc_auc']:.3f}")
    
    # Save analysis results
    saved_paths = results_manager.save_churn_results(analysis_results)
    logger.info(f"  Analysis results saved to: {results_manager.run_dir}")
    
    # Step 3: Demonstrate content recommendations
    logger.info("\n[Step 3] Content recommendation demo...")
    recommender = ContentRecommender(
        content_df=data["content"],
        content_performance=analysis_results["content_performance"]
    )
    
    # Demo: recommendations for different user profiles
    demo_users = [
        {"user_id": "demo_1", "goal": "weight_loss", "session_number": 1},
        {"user_id": "demo_2", "goal": "stress_reduction", "session_number": 3},
        {"user_id": "demo_3", "goal": "better_sleep", "session_number": 5},
    ]
    
    all_recommendations = []
    content_df = data["content"]
    for user in demo_users:
        logger.info(f"\nRecommendations for {user['user_id']} (goal: {user['goal']}, session: {user['session_number']}):")
        recs = recommender.recommend(
            user_goal=user["goal"],
            session_number=user["session_number"],
            n_recommendations=3
        )
        for i, rec in enumerate(recs, 1):
            title = content_df[content_df["content_id"] == rec.content_id]["title"].iloc[0]
            logger.info(f"  {i}. {title} (score: {rec.score:.3f})")
            all_recommendations.append({
                "user_id": user["user_id"],
                "goal": user["goal"],
                "session": user["session_number"],
                "rank": i,
                "content_id": rec.content_id,
                "title": title,
                "score": rec.score,
            })
    
    # Save recommendations
    results_manager.save_recommendations(all_recommendations)
    logger.info(f"\n  Recommendations saved to: {results_manager.run_dir}")
    
    # Save summary
    summary = {
        "run_timestamp": results_manager.timestamp,
        "dataset_stats": {
            "n_users": len(data['users']),
            "n_content": len(data['content']),
            "n_interactions": len(data['interactions']),
            "churn_rate": float(data['labels']['churned'].mean()),
        },
        "model_performance": {
            "roc_auc": analysis_results['model_results']['roc_auc'],
        },
        "recommendations_generated": len(all_recommendations),
    }
    results_manager.save_summary(summary)
    
    logger.info("\n" + "=" * 60)
    logger.info("DEMO COMPLETE")
    logger.info(f"All outputs saved to: {results_manager.run_dir}")
    logger.info(f"Logs saved to: logs/")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
