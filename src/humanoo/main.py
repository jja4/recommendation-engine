"""
Main demonstration script for Humanoo Wellness Assistant Prototype.

Runs the complete pipeline:
1. Generate synthetic data
2. Perform churn analysis
3. Demonstrate content recommendations
"""

from humanoo.data_generator import generate_dataset
from humanoo.churn_analysis import run_churn_analysis
from humanoo.content_recommender import demonstrate_recommendations


def main():
    print("="*60)
    print("  HUMANOO WELLNESS ASSISTANT PROTOTYPE")
    print("  Churn Analysis + Content Recommendation Engine")
    print("="*60)
    
    # Step 1: Generate data
    print("\n[1/3] GENERATING SYNTHETIC DATA")
    print("-" * 40)
    data = generate_dataset(n_users=500, n_content=50)
    
    # Step 2: Run churn analysis
    print("\n[2/3] RUNNING CHURN ANALYSIS")
    print("-" * 40)
    churn_results = run_churn_analysis(data)
    
    # Step 3: Demonstrate recommendations
    print("\n[3/3] DEMONSTRATING RECOMMENDATIONS")
    print("-" * 40)
    recommender = demonstrate_recommendations(data, churn_results)
    
    # Summary
    print("\n" + "="*60)
    print("  SUMMARY")
    print("="*60)
    
    churn_rate = data["labels"]["churned"].mean()
    print(f"\nDataset: {len(data['users'])} users, {len(data['content'])} content items")
    print(f"Churn rate: {churn_rate:.1%}")
    
    print("\nKey Findings from Churn Analysis:")
    top_features = sorted(
        churn_results["model_results"]["feature_importance"].items(),
        key=lambda x: x[1],
        reverse=True
    )[:3]
    for feat, imp in top_features:
        print(f"  • {feat}: {imp:.3f} importance")
    
    print("\nRecommendation Engine:")
    print("  • Uses goal alignment + retention lift + completion probability")
    print("  • Adapts weights based on session number (first session vs returning)")
    print("  • Learns from retained users' behavior")
    
    print("\nGenerated Artifacts:")
    print("  • churn_analysis.png - Visualization of churn patterns")
    
    print("\n" + "="*60)
    print("  DEMO COMPLETE")
    print("="*60)


if __name__ == "__main__":
    main()
