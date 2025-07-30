#!/usr/bin/env python3
"""
Test single musical analysis
"""

import asyncio
import json
from pathlib import Path
from main import SceneData, TheaterCritic, CriticType

async def test_single():
    """Test analysis of one scene"""
    
    print("🎭 Testing single scene analysis...")
    
    # Load Echo Musical opening scene
    scene_file = Path("all_musicals_analysis/echo_musical/json/scene_01.json")
    
    with open(scene_file, 'r', encoding='utf-8') as f:
        scene_data = json.load(f)
    scene = SceneData(**scene_data)
    
    print(f"Scene: {scene.title}")
    print(f"Musical: {scene.musical}")
    
    # Create critic
    critic = TheaterCritic(
        "Eleanor Hartwell", 
        CriticType.PRIMARY, 
        "gemma2:9b", 
        "comprehensive theatrical analysis"
    )
    
    print("Analyzing...")
    try:
        review = await critic.analyze_scene(scene)
        print(f"✅ Success! Score: {review.scores.overall}/10.0")
        print(f"Review: {review.review_text[:150]}...")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_single())