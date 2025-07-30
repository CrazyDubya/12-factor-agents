#!/usr/bin/env python3
"""
Demo Analysis - Single scene with primary critic only
Tests system with minimal load
"""

import json

import asyncio

from main import CriticType, SceneData, TheaterCritic


async def demo_single_critic():
    """Demo with just primary critic"""

    # Load one scene
    with open("rainbow_scenes_json/rainbow_act1_scene1.json", "r") as f:
        scene_data = json.load(f)
    scene = SceneData(**scene_data)

    print("🎭 DEMO: Single Critic Analysis")
    print("=" * 50)
    print(f"Scene: {scene.title}")
    print(f"Musical: {scene.musical}")
    print()

    # Create primary critic
    primary_critic = TheaterCritic(
        "Eleanor Hartwell",
        CriticType.PRIMARY,
        "gemma2:9b",
        "comprehensive theatrical analysis",
    )

    print("🎬 Analyzing with primary critic...")

    try:
        review = await primary_critic.analyze_scene(scene)

        print(f"✅ Analysis complete!")
        print(f"Critic: {review.critic_name}")
        print(f"Overall Score: {review.scores.overall}/10.0")
        print(f"Review: {review.review_text[:300]}...")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(demo_single_critic())
