#!/usr/bin/env python3
"""
Quick Multi-Musical Demo
Analyzes 1 representative scene from each musical for rapid overview
"""

import asyncio
import json
from pathlib import Path
from main import SceneData, TheaterCritic, CriticType

async def quick_multi_demo():
    """Quick demo analyzing opening scene from each musical"""
    
    print("🎭 QUICK MULTI-MUSICAL DEMO")
    print("="*50)
    print("Analyzing opening scene from each Broadway musical")
    print("Using primary critic only for speed\n")
    
    # Load conversion summary
    summary_file = Path("all_musicals_analysis/conversion_summary.json")
    with open(summary_file, 'r') as f:
        musicals = json.load(f)
    
    # Create primary critic
    primary_critic = TheaterCritic(
        "Eleanor Hartwell", 
        CriticType.PRIMARY, 
        "gemma2:9b", 
        "comprehensive theatrical analysis"
    )
    
    results = []
    
    for musical_dir, musical_info in musicals.items():
        try:
            # Find first scene
            json_dir = Path("all_musicals_analysis") / musical_dir / "json"
            scene_files = sorted(json_dir.glob("scene_*.json"))
            
            if not scene_files:
                print(f"❌ No scenes found for {musical_info['name']}")
                continue
            
            # Load opening scene
            with open(scene_files[0], 'r', encoding='utf-8') as f:
                scene_data = json.load(f)
            scene = SceneData(**scene_data)
            
            print(f"🎬 {musical_info['name']}")
            print(f"   Opening: {scene.title}")
            
            # Analyze
            review = await primary_critic.analyze_scene(scene)
            
            result = {
                "musical": musical_info['name'],
                "scene": scene.title,
                "score": review.scores.overall,
                "preview": review.review_text[:100] + "..."
            }
            
            results.append(result)
            print(f"   Score: {result['score']:.1f}/10.0")
            print(f"   Review: {result['preview']}")
            print()
            
        except Exception as e:
            print(f"❌ Error with {musical_info['name']}: {e}")
    
    # Summary
    if results:
        avg_score = sum(r['score'] for r in results) / len(results)
        print("="*50)
        print("🎭 QUICK DEMO SUMMARY")
        print("="*50)
        print(f"Collection Average: {avg_score:.1f}/10.0")
        print("\nRankings:")
        
        results.sort(key=lambda x: x['score'], reverse=True)
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['musical']}: {result['score']:.1f}/10.0")

if __name__ == "__main__":
    asyncio.run(quick_multi_demo())