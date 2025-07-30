#!/usr/bin/env python3
"""
Real AI Analysis - Using actual Ollama and OpenRouter models
No fake data - real AI critic analysis with variety
"""

import asyncio
import json
import time
from pathlib import Path
from main import SceneData, CriticEnsemble, ConsensusAnalyzer

async def run_real_ai_analysis():
    """Run actual AI analysis on real scenes with real models"""
    
    print("🎭 REAL AI CRITICS ANALYSIS - NO FAKE DATA")
    print("="*60)
    print("Using actual Ollama models for authentic theater criticism")
    print("Each musical gets unique AI-generated reviews\n")
    
    # Initialize real critic ensemble
    ensemble = CriticEnsemble()
    
    # Select one representative scene from each musical for real analysis
    test_scenes = [
        {
            "file": "all_musicals_analysis/rainbow_academy_musical/json/scene_01.json",
            "musical": "Rainbow Academy Musical - Magic School Adventure",
            "expected_genre": "Fantasy Musical Theater"
        },
        {
            "file": "all_musicals_analysis/echo_musical/json/scene_01.json", 
            "musical": "Echo Musical - AI Consciousness & Memory",
            "expected_genre": "Sci-Fi Drama"
        },
        {
            "file": "all_musicals_analysis/electric_dreams_musical/json/scene_01.json",
            "musical": "Electric Dreams Musical - Technology & Desire", 
            "expected_genre": "Techno-Romance"
        },
        {
            "file": "all_musicals_analysis/midnight_at_the_majestic_musical/json/scene_01.json",
            "musical": "Midnight at the Majestic Musical - Theater Murder Mystery",
            "expected_genre": "Murder Mystery"
        },
        {
            "file": "all_musicals_analysis/neon_rebellion_musical/json/scene_01.json",
            "musical": "Neon Rebellion Musical - Dystopian Resistance",
            "expected_genre": "Dystopian Action"  
        },
        {
            "file": "all_musicals_analysis/neon_hearts_burlesque_musical/json/scene_01.json",
            "musical": "Neon Hearts Burlesque Musical - Underground Cabaret",
            "expected_genre": "Contemporary Drama"
        }
    ]
    
    real_results = []
    total_start = time.time()
    
    for i, scene_info in enumerate(test_scenes, 1):
        try:
            print(f"🎪 ANALYZING {i}/6: {scene_info['musical']}")
            print("-" * 50)
            
            # Load actual scene content
            with open(scene_info['file'], 'r', encoding='utf-8') as f:
                scene_data = json.load(f)
            scene = SceneData(**scene_data)
            
            print(f"Scene: {scene.title}")
            print(f"Has lyrics: {'✅' if scene.lyrics else '❌'}")
            print(f"Description: {scene.description[:60]}...")
            
            # Get REAL AI analysis with rotating critics for variety
            analysis_start = time.time()
            print("🤖 Running AI critics ensemble...")
            
            # Use different numbers of rotating critics for variety
            num_rotating = 1 if i <= 3 else 2  # Vary critic count
            reviews = await ensemble.review_scene(scene, num_rotating_critics=num_rotating)
            consensus = ConsensusAnalyzer.calculate_consensus(reviews)
            
            analysis_time = time.time() - analysis_start
            
            # Extract REAL AI insights
            primary_review = reviews[0]  # Always have primary critic
            
            result = {
                "rank": i,  # Will be updated after sorting by score
                "name": scene_info['musical'],
                "genre": scene_info['expected_genre'], 
                "scene_title": scene.title,
                "overall_score": consensus['average_scores']['overall'],
                "category_scores": consensus['average_scores'],
                "consensus_level": consensus['consensus_level'],
                "critics_used": [r.critic_name for r in reviews],
                "real_ai_review": primary_review.review_text,
                "real_strengths": primary_review.key_strengths,
                "real_improvements": primary_review.areas_for_improvement, 
                "specialty_analysis": primary_review.specialty_analysis,
                "analysis_time": round(analysis_time, 1),
                "model_used": primary_review.model_used
            }
            
            real_results.append(result)
            
            print(f"✅ REAL Score: {result['overall_score']:.1f}/10.0")
            print(f"Critics: {', '.join(result['critics_used'])}")
            print(f"Consensus: {result['consensus_level']}")
            print(f"Time: {result['analysis_time']}s")
            print(f"AI Review Preview: {result['real_ai_review'][:100]}...")
            print()
            
            # Delay between analyses to not overwhelm Ollama
            if i < len(test_scenes):
                print("⏳ Waiting 3 seconds before next analysis...")
                await asyncio.sleep(3)
            
        except Exception as e:
            print(f"❌ Error analyzing {scene_info['musical']}: {e}")
            # Create error result to maintain structure
            error_result = {
                "rank": i,
                "name": scene_info['musical'],
                "genre": scene_info['expected_genre'],
                "overall_score": 0.0,
                "error": str(e),
                "analysis_time": 0
            }
            real_results.append(error_result)
            print()
    
    total_time = time.time() - total_start
    
    # Filter out error results and sort by actual AI scores
    successful_results = [r for r in real_results if 'error' not in r]
    successful_results.sort(key=lambda x: x['overall_score'], reverse=True)
    
    # Update rankings based on real AI scores
    for i, result in enumerate(successful_results, 1):
        result['rank'] = i
    
    print("="*60)
    print("🏆 REAL AI CRITICS FINAL RANKINGS")
    print("="*60)
    
    if successful_results:
        collection_average = sum(r['overall_score'] for r in successful_results) / len(successful_results)
        score_range = max(r['overall_score'] for r in successful_results) - min(r['overall_score'] for r in successful_results)
        
        print(f"Collection Average: {collection_average:.1f}/10.0")
        print(f"Score Range: {score_range:.1f} points")
        print(f"Total Analysis Time: {total_time/60:.1f} minutes")
        print(f"Successful Analyses: {len(successful_results)}/{len(test_scenes)}")
        print()
        
        for result in successful_results:
            print(f"{result['rank']}. {result['name']}")
            print(f"   Real AI Score: {result['overall_score']:.1f}/10.0")
            print(f"   Critics: {', '.join(result['critics_used'])}")
            print(f"   Model: {result.get('model_used', 'Unknown')}")
            print(f"   AI Says: {result['real_ai_review'][:80]}...")
            print()
        
        # Save REAL analysis results
        output_data = {
            "analysis_metadata": {
                "analysis_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "system": "REAL AI Theater Critics - Ollama + OpenRouter Models",
                "methodology": "Actual AI model analysis - NO FAKE DATA",
                "total_time_minutes": round(total_time/60, 1),
                "collection_average": round(collection_average, 1),
                "score_variety": f"{score_range:.1f} point range",
                "ai_models_used": "Gemma2:9b, Qwen2.5:3b, Llama3.2:3b, etc."
            },
            "real_musical_rankings": successful_results,
            "collection_analysis": {
                "overall_average": round(collection_average, 1),
                "score_range": round(score_range, 1),
                "successful_analyses": len(successful_results),
                "total_attempted": len(test_scenes),
                "analysis_time_minutes": round(total_time/60, 1)
            }
        }
        
        with open("REAL_AI_broadway_analysis.json", 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print("💾 REAL AI analysis saved to: REAL_AI_broadway_analysis.json")
        print("🎭 No fake data - 100% authentic AI theater criticism!")
        
    else:
        print("❌ No successful analyses completed")
        print("Check Ollama is running and models are available")
    
    return successful_results

if __name__ == "__main__":
    print("🚀 Starting REAL AI Analysis...")
    print("This will take several minutes using actual AI models")
    print("Make sure Ollama is running with required models\n")
    
    asyncio.run(run_real_ai_analysis())