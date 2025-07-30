#!/usr/bin/env python3
"""
Fast Broadway Analysis - One scene per musical with primary critic only
"""

import json
import time
from pathlib import Path

import asyncio

from main import CriticType, SceneData, TheaterCritic


async def fast_broadway_analysis():
    """Fast analysis of all Broadway musicals - opening scenes only"""

    print("🎭 FAST BROADWAY COLLECTION ANALYSIS")
    print("=" * 60)
    print("Analyzing opening scene from each musical")
    print("Using primary critic (Gemma2:9b) for speed\n")

    # Create primary critic
    primary_critic = TheaterCritic(
        "Eleanor Hartwell",
        CriticType.PRIMARY,
        "gemma2:9b",
        "comprehensive theatrical analysis",
    )

    # Load conversion summary
    summary_file = Path("all_musicals_analysis/conversion_summary.json")
    with open(summary_file, "r") as f:
        musicals = json.load(f)

    results = []
    total_start = time.time()

    for musical_dir, musical_info in musicals.items():
        try:
            print(f"🎪 {musical_info['name']}")
            print("-" * 50)

            # Find opening scene
            json_dir = Path("all_musicals_analysis") / musical_dir / "json"
            scene_files = sorted(json_dir.glob("scene_*.json"))

            if not scene_files:
                print("❌ No scenes found")
                continue

            # Load opening scene
            with open(scene_files[0], "r", encoding="utf-8") as f:
                scene_data = json.load(f)
            scene = SceneData(**scene_data)

            print(f"Opening: {scene.title}")
            print(f"Description: {scene.description[:80]}...")

            # Analyze with primary critic
            start_time = time.time()
            review = await primary_critic.analyze_scene(scene)
            analysis_time = time.time() - start_time

            result = {
                "musical": musical_info["name"],
                "total_scenes": musical_info["scene_count"],
                "opening_scene": scene.title,
                "overall_score": review.scores.overall,
                "category_scores": {
                    "musical_composition": review.scores.musical_composition,
                    "performance_quality": review.scores.performance_quality,
                    "production_elements": review.scores.production_elements,
                    "narrative_integration": review.scores.narrative_integration,
                    "audience_engagement": review.scores.audience_engagement,
                },
                "strengths": review.key_strengths,
                "improvements": review.areas_for_improvement,
                "review_excerpt": review.review_text[:300] + "...",
                "analysis_time": round(analysis_time, 1),
            }

            results.append(result)

            print(f"✅ Score: {result['overall_score']:.1f}/10.0")
            print(f"⏱️  Time: {result['analysis_time']}s")
            print(f"🎯 Strengths: {', '.join(result['strengths'][:2])}")
            print()

        except Exception as e:
            print(f"❌ Error: {e}\n")

    total_time = time.time() - total_start

    # Generate rankings
    results.sort(key=lambda x: x["overall_score"], reverse=True)
    collection_average = (
        sum(r["overall_score"] for r in results) / len(results) if results else 0
    )

    print("=" * 60)
    print("🏆 BROADWAY COLLECTION RANKINGS")
    print("=" * 60)
    print(f"Collection Average: {collection_average:.1f}/10.0")
    print(f"Total Analysis Time: {total_time:.1f}s")
    print(f"Musicals Analyzed: {len(results)}")
    print()

    for i, result in enumerate(results, 1):
        print(f"{i}. {result['musical']}: {result['overall_score']:.1f}/10.0")
        print(f"   Opening: {result['opening_scene']}")
        print(f"   Scenes: {result['total_scenes']} | Time: {result['analysis_time']}s")
        print()

    # Detailed reviews
    print("=" * 60)
    print("🎬 DETAILED REVIEWS")
    print("=" * 60)

    for result in results:
        print(f"\n🎪 {result['musical']} ({result['overall_score']:.1f}/10.0)")
        print("-" * 50)
        print(f"Opening Scene: {result['opening_scene']}")
        print(f"\nEleanor Hartwell's Review:")
        print(f'"{result['review_excerpt']}"')
        print(f"\nStrengths: {', '.join(result['strengths'])}")
        print(f"Areas for Improvement: {', '.join(result['improvements'])}")

        print(f"\nCategory Scores:")
        for category, score in result["category_scores"].items():
            category_name = category.replace("_", " ").title()
            print(f"  {category_name}: {score:.1f}/10.0")

    # Save results
    final_data = {
        "analysis_metadata": {
            "analysis_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "system": "Theater Critics - Primary Critic (Gemma2:9b)",
            "scope": "Opening scenes from all Broadway musicals",
            "total_time_seconds": round(total_time, 1),
            "collection_average": round(collection_average, 1),
        },
        "rankings": results,
    }

    with open("fast_broadway_analysis.json", "w", encoding="utf-8") as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Results saved to: fast_broadway_analysis.json")
    print(f"🎭 Fast analysis complete! {len(results)} musicals ranked")


if __name__ == "__main__":
    asyncio.run(fast_broadway_analysis())
