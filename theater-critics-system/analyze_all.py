#!/usr/bin/env python3
"""
Comprehensive Broadway Collection Analysis
Analyzes key scenes from all musicals with full critic ensemble
"""

import asyncio
import json
import time
from pathlib import Path
from main import SceneData, CriticEnsemble, ConsensusAnalyzer

async def analyze_all_broadway_musicals():
    """Comprehensive analysis of all Broadway musicals"""
    
    print("🎭 COMPREHENSIVE BROADWAY MUSICALS ANALYSIS")
    print("="*80)
    print("Analyzing representative scenes from all 6 musicals")
    print("Using full critic ensemble for professional evaluation\n")
    
    # Load conversion summary
    summary_file = Path("all_musicals_analysis/conversion_summary.json")
    with open(summary_file, 'r') as f:
        musicals = json.load(f)
    
    ensemble = CriticEnsemble()
    all_results = {}
    
    total_start = time.time()
    
    # Define key scenes to analyze per musical
    scene_selections = {
        "echo_musical": [1, 6, 12],  # Opening, middle, finale
        "electric_dreams_musical": [1, 5, 10, 15, 20],  # Comprehensive sampling
        "midnight_at_the_majestic_musical": [1, 3, 6],  # Opening, crisis, resolution
        "neon_hearts_burlesque_musical": [1, 2],  # Both scenes
        "neon_rebellion_musical": [1, 2, 4],  # Opening, development, finale
        "rainbow_academy_musical": [1, 4, 11]  # Opening, crisis, finale
    }
    
    for musical_dir, musical_info in musicals.items():
        print(f"\n🎪 ANALYZING: {musical_info['name']}")
        print("="*60)
        
        # Get scene selection for this musical
        scene_numbers = scene_selections.get(musical_dir, [1])
        
        json_dir = Path("all_musicals_analysis") / musical_dir / "json"
        scene_files = sorted(json_dir.glob("scene_*.json"))
        
        selected_scenes = []
        for scene_num in scene_numbers:
            if scene_num <= len(scene_files):
                selected_scenes.append(scene_files[scene_num - 1])
        
        print(f"📊 Analyzing {len(selected_scenes)} key scenes")
        
        musical_results = {
            "musical_name": musical_info['name'],
            "total_scenes": musical_info['scene_count'],
            "analyzed_scenes": len(selected_scenes),
            "scene_analyses": [],
            "musical_average": 0,
            "analysis_time": 0
        }
        
        musical_start = time.time()
        
        for i, scene_file in enumerate(selected_scenes, 1):
            try:
                # Load scene
                with open(scene_file, 'r', encoding='utf-8') as f:
                    scene_data = json.load(f)
                scene = SceneData(**scene_data)
                
                print(f"\n🎬 Scene {i}: {scene.title}")
                print("-" * 50)
                
                # Analyze with full ensemble (primary + 2 rotating critics)
                reviews = await ensemble.review_scene(scene, num_rotating_critics=2)
                consensus = ConsensusAnalyzer.calculate_consensus(reviews)
                
                scene_result = {
                    "scene_number": int(scene_file.stem.split('_')[1]),
                    "scene_title": scene.title,
                    "overall_score": consensus['average_scores']['overall'],
                    "consensus_level": consensus['consensus_level'],
                    "critics": [r.critic_name for r in reviews],
                    "category_scores": consensus['average_scores'],
                    "reviews": [
                        {
                            "critic": r.critic_name,
                            "critic_type": r.critic_type.value,
                            "score": r.scores.overall,
                            "specialty_score": r.scores.specialty_score,
                            "review_preview": r.review_text[:200] + "...",
                            "strengths": r.key_strengths[:2],
                            "improvements": r.areas_for_improvement[:2]
                        }
                        for r in reviews
                    ]
                }
                
                musical_results["scene_analyses"].append(scene_result)
                
                print(f"Overall Score: {scene_result['overall_score']:.1f}/10.0")
                print(f"Consensus: {scene_result['consensus_level']}")
                print(f"Critics: {', '.join(scene_result['critics'])}")
                
                # Show primary critic's brief take
                primary_review = scene_result['reviews'][0]
                print(f"\n{primary_review['critic']} says:")
                print(f'"{primary_review['review_preview']}"')
                
                # Delay between scenes
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f"❌ Error analyzing scene {i}: {e}")
        
        # Calculate musical average
        if musical_results["scene_analyses"]:
            scores = [s["overall_score"] for s in musical_results["scene_analyses"]]
            musical_results["musical_average"] = sum(scores) / len(scores)
        
        musical_results["analysis_time"] = time.time() - musical_start
        all_results[musical_dir] = musical_results
        
        print(f"\n✅ {musical_info['name']} Analysis Complete")
        print(f"Musical Average: {musical_results['musical_average']:.1f}/10.0")
        print(f"Analysis Time: {musical_results['analysis_time']/60:.1f} minutes")
        
        # Delay between musicals
        await asyncio.sleep(3)
    
    total_time = time.time() - total_start
    
    # Generate final summary
    print(f"\n{'='*80}")
    print("🏆 COMPREHENSIVE ANALYSIS COMPLETE")
    print(f"{'='*80}")
    print(f"Total Analysis Time: {total_time/60:.1f} minutes")
    
    # Calculate collection statistics
    all_scores = []
    musical_rankings = []
    
    for musical_dir, result in all_results.items():
        if result.get('musical_average', 0) > 0:
            musical_rankings.append({
                "name": result['musical_name'],
                "average": result['musical_average'],
                "scenes": result['analyzed_scenes']
            })
            
            # Collect all scene scores
            for scene in result['scene_analyses']:
                all_scores.append(scene['overall_score'])
    
    # Sort musicals by score
    musical_rankings.sort(key=lambda x: x['average'], reverse=True)
    
    collection_average = sum(all_scores) / len(all_scores) if all_scores else 0
    
    print(f"\n🎭 BROADWAY COLLECTION RESULTS")
    print("-" * 50)
    print(f"Collection Average: {collection_average:.1f}/10.0")
    print(f"Total Scenes Analyzed: {len(all_scores)}")
    print(f"Musicals Ranked: {len(musical_rankings)}")
    
    print(f"\n🏆 MUSICAL RANKINGS")
    print("-" * 40)
    for i, musical in enumerate(musical_rankings, 1):
        print(f"{i}. {musical['name']}")
        print(f"   Score: {musical['average']:.1f}/10.0 ({musical['scenes']} scenes)")
    
    # Save comprehensive results
    final_results = {
        "analysis_metadata": {
            "analysis_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "system": "Theater Critics Multi-Agent Ensemble",
            "total_analysis_time_minutes": round(total_time/60, 1),
            "collection_average": round(collection_average, 1),
            "scenes_analyzed": len(all_scores)
        },
        "musical_rankings": musical_rankings,
        "detailed_results": all_results
    }
    
    with open("comprehensive_broadway_analysis.json", 'w', encoding='utf-8') as f:
        json.dump(final_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Complete results saved to: comprehensive_broadway_analysis.json")
    print(f"🎭 Analysis complete! {len(musical_rankings)} musicals ranked by AI critics")
    
    return final_results

if __name__ == "__main__":
    asyncio.run(analyze_all_broadway_musicals())