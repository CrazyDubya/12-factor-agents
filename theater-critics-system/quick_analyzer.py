#!/usr/bin/env python3
"""
Quick Rainbow Academy Analysis - Sample of key scenes
Analyzes 3 representative scenes to demonstrate the system
"""

import asyncio
import json
from pathlib import Path
from main import SceneData, CriticEnsemble, ConsensusAnalyzer

async def quick_analysis():
    """Analyze 3 key scenes from Rainbow Academy Musical"""
    
    # Load key scenes: Opening, Crisis, Finale
    key_scenes = [
        "rainbow_scenes_json/rainbow_act1_scene1.json",  # Welcome to Rainbow Academy
        "rainbow_scenes_json/rainbow_act1_scene4.json",  # The Crystal Disappears
        "rainbow_scenes_json/rainbow_act2_scene5.json"   # We Are Rainbow Academy
    ]
    
    ensemble = CriticEnsemble()
    results = []
    
    print("🎭 RAINBOW ACADEMY MUSICAL - QUICK CRITIC ANALYSIS")
    print("="*60)
    print("Analyzing 3 key scenes: Opening, Crisis, Finale")
    print()
    
    for i, scene_file in enumerate(key_scenes, 1):
        try:
            # Load scene
            with open(scene_file, 'r') as f:
                scene_data = json.load(f)
            scene = SceneData(**scene_data)
            
            print(f"Scene {i}: {scene.title}")
            print("-" * 40)
            
            # Analyze with 2 rotating critics for speed
            reviews = await ensemble.review_scene(scene, num_rotating_critics=2)
            consensus = ConsensusAnalyzer.calculate_consensus(reviews)
            
            # Print quick summary
            print(f"Overall Score: {consensus['average_scores']['overall']:.1f}/10.0")
            print(f"Consensus: {consensus['consensus_level']}")
            print(f"Critics: {', '.join([r.critic_name for r in reviews])}")
            
            # Show one sample review
            primary_review = reviews[0]  # Primary critic
            print(f"\n{primary_review.critic_name} says:")
            review_preview = primary_review.review_text[:200] + "..."
            print(f'"{review_preview}"')
            print()
            
            results.append({
                "scene": scene.title,
                "score": consensus['average_scores']['overall'],
                "consensus": consensus['consensus_level'],
                "critics": [r.critic_name for r in reviews]
            })
            
        except Exception as e:
            print(f"Error analyzing scene {i}: {e}")
            print()
    
    # Final summary
    if results:
        avg_score = sum(r['score'] for r in results) / len(results)
        print("="*60)
        print("🎭 QUICK ANALYSIS SUMMARY")
        print("="*60)
        print(f"Rainbow Academy Musical Overall: {avg_score:.1f}/10.0")
        print("\nScene Scores:")
        for result in results:
            print(f"• {result['scene']}: {result['score']:.1f}/10.0")

if __name__ == "__main__":
    asyncio.run(quick_analysis())