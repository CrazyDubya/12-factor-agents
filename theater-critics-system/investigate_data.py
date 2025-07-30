#!/usr/bin/env python3
"""
Data Investigation - Check actual analysis results vs manual projections
"""

import json
import asyncio
from pathlib import Path
from main import SceneData, CriticEnsemble, ConsensusAnalyzer

async def investigate_real_vs_projected():
    """Compare actual AI analysis with projected results"""
    
    print("🔍 INVESTIGATING DATA QUALITY ISSUE")
    print("="*60)
    print("Problem: Reviews lack variety, scores too similar")
    print("Hypothesis: Using projected data instead of real AI analysis\n")
    
    # Test actual analysis on different musicals
    ensemble = CriticEnsemble()
    
    test_scenes = [
        ("all_musicals_analysis/echo_musical/json/scene_01.json", "Echo - The Lab"),
        ("all_musicals_analysis/electric_dreams_musical/json/scene_01.json", "Electric Dreams - Opening"),
        ("all_musicals_analysis/midnight_at_the_majestic_musical/json/scene_01.json", "Midnight - Opening Night"),
        ("all_musicals_analysis/neon_rebellion_musical/json/scene_01.json", "Neon Rebellion - Algorithm Paradise")
    ]
    
    real_results = []
    
    for scene_file, description in test_scenes:
        try:
            print(f"🎭 Testing: {description}")
            print("-" * 40)
            
            # Load scene
            with open(scene_file, 'r', encoding='utf-8') as f:
                scene_data = json.load(f)
            scene = SceneData(**scene_data)
            
            print(f"Scene: {scene.title}")
            print(f"Musical: {scene.musical}")
            print(f"Description: {scene.description[:80]}...")
            
            # Get actual AI analysis (primary critic only for speed)
            reviews = await ensemble.review_scene(scene, num_rotating_critics=0)  # Just primary
            consensus = ConsensusAnalyzer.calculate_consensus(reviews)
            
            result = {
                "scene": description,
                "title": scene.title,
                "overall_score": consensus['average_scores']['overall'],
                "category_scores": consensus['average_scores'],
                "review_excerpt": reviews[0].review_text[:200] + "...",
                "strengths": reviews[0].key_strengths,
                "improvements": reviews[0].areas_for_improvement,
                "critic": reviews[0].critic_name
            }
            
            real_results.append(result)
            
            print(f"✅ REAL Score: {result['overall_score']:.1f}/10.0")
            print(f"Critic: {result['critic']}")
            print(f"Review: {result['review_excerpt']}")
            print(f"Strengths: {', '.join(result['strengths'][:2])}")
            print()
            
        except Exception as e:
            print(f"❌ Error: {e}\n")
    
    # Compare with current projected data
    print("="*60)
    print("📊 COMPARISON: REAL vs PROJECTED")
    print("="*60)
    
    projected_scores = [7.5, 7.5, 7.2, 7.0, 6.8, 6.5]  # From manual_analysis.py
    real_scores = [r['overall_score'] for r in real_results]
    
    print("Projected Scores:", projected_scores)
    print("Real AI Scores:", real_scores)
    print()
    print("Projected Range:", max(projected_scores) - min(projected_scores))
    print("Real Range:", max(real_scores) - min(real_scores) if real_scores else "N/A")
    print()
    
    # Show variety in real reviews
    print("REAL REVIEW VARIETY:")
    print("-" * 30)
    for result in real_results:
        print(f"• {result['scene']}: {result['overall_score']:.1f}")
        print(f"  Unique insight: {result['review_excerpt'][:60]}...")
        print()
    
    # Save real results
    if real_results:
        with open("real_analysis_investigation.json", 'w') as f:
            json.dump({
                "investigation_date": "2025-07-28",
                "problem": "Lack of variety in reviews and scores",
                "solution": "Use actual AI analysis instead of projections",
                "real_results": real_results,
                "recommendations": [
                    "Replace manual projections with actual AI critic analysis",
                    "Run full ensemble analysis for more diverse perspectives",
                    "Use different critics for different scenes to increase variety",
                    "Implement actual analysis pipeline instead of placeholder data"
                ]
            }, f, indent=2)
        
        print("💾 Investigation results saved to: real_analysis_investigation.json")
    
    return real_results

if __name__ == "__main__":
    asyncio.run(investigate_real_vs_projected())