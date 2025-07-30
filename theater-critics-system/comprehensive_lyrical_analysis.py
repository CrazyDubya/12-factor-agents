#!/usr/bin/env python3
"""
Comprehensive Lyrical Analysis - All Broadway Musicals Collection
Analyzes every musical's representative scene for lyrical sophistication
"""

import asyncio
import json
import time
from pathlib import Path
from lyrical_analysis import LyricalContentAnalyzer, LyricalAnalysis
from main import SceneData

async def run_comprehensive_lyrical_analysis():
    """Run lyrical analysis on all musicals in collection"""
    
    print("🎭🎵 COMPREHENSIVE LYRICAL ANALYSIS - ALL MUSICALS")
    print("=" * 60)
    print("Analyzing lyrical content across the entire Broadway collection")
    print("Focus: Rhyme schemes, metaphors, themes, and vocabulary sophistication\n")
    
    analyzer = LyricalContentAnalyzer()
    
    # All musical scenes for comprehensive analysis
    musical_scenes = [
        {
            "file": "all_musicals_analysis/echo_musical/json/scene_01.json",
            "musical": "Echo Musical - AI Consciousness & Memory",
            "genre": "Sci-Fi Drama"
        },
        {
            "file": "all_musicals_analysis/electric_dreams_musical/json/scene_01.json", 
            "musical": "Electric Dreams Musical - Technology & Desire",
            "genre": "Techno-Romance"
        },
        {
            "file": "all_musicals_analysis/midnight_at_the_majestic_musical/json/scene_02.json",
            "musical": "Midnight at the Majestic Musical - Theater Murder Mystery",
            "genre": "Murder Mystery"
        },
        {
            "file": "all_musicals_analysis/neon_hearts_burlesque_musical/json/scene_01.json",
            "musical": "Neon Hearts Burlesque Musical - Underground Cabaret", 
            "genre": "Contemporary Drama"
        },
        {
            "file": "all_musicals_analysis/neon_rebellion_musical/json/scene_01.json",
            "musical": "Neon Rebellion Musical - Dystopian Resistance",
            "genre": "Dystopian Action"
        },
        {
            "file": "all_musicals_analysis/rainbow_academy_musical/json/scene_01.json",
            "musical": "Rainbow Academy Musical - Magic School Adventure", 
            "genre": "Fantasy Musical Theater"
        }
    ]
    
    results = []
    total_start = time.time()
    
    for i, scene_info in enumerate(musical_scenes, 1):
        try:
            print(f"🎪 LYRICAL ANALYSIS {i}/6: {scene_info['musical']}")
            print("-" * 50)
            
            # Load scene content
            scene_path = Path(scene_info['file'])
            if not scene_path.exists():
                print(f"❌ Scene file not found: {scene_info['file']}")
                continue
                
            with open(scene_path, 'r', encoding='utf-8') as f:
                scene_data = json.load(f)
            scene = SceneData(**scene_data)
            
            print(f"Scene: {scene.title}")
            print(f"Genre: {scene_info['genre']}")
            
            # Perform comprehensive lyrical analysis
            analysis = await analyzer.analyze_scene_lyrics(scene)
            
            # Add genre classification
            analysis_dict = {
                "rank": i,  # Will be updated after sorting
                "musical_name": scene_info['musical'],
                "genre": scene_info['genre'],
                "scene_title": analysis.scene_title,
                "lyrical_scores": {
                    "overall_lyrical_score": round(analysis.overall_lyrical_score, 2),
                    "rhyme_scheme_score": round(analysis.rhyme_scheme_score, 2), 
                    "metaphor_usage_score": round(analysis.metaphor_usage_score, 2),
                    "thematic_coherence_score": round(analysis.thematic_coherence_score, 2),
                    "vocabulary_sophistication_score": round(analysis.lyrical_sophistication_score, 2)
                },
                "lyrical_details": {
                    "rhyme_patterns": analysis.rhyme_patterns,
                    "metaphors_identified": analysis.metaphors_identified[:3],  # Top 3
                    "thematic_elements": analysis.thematic_elements[:5],  # Top 5
                    "vocabulary_complexity": analysis.vocabulary_complexity
                },
                "ai_critic_insights": {
                    "lyrical_strengths": analysis.lyrical_strengths,
                    "lyrical_improvements": analysis.lyrical_improvements,
                    "specialist_commentary": analysis.specialist_commentary
                },
                "analysis_metadata": {
                    "analysis_time": round(analysis.analysis_time, 1),
                    "critic_used": analysis.critic_used
                }
            }
            
            results.append(analysis_dict)
            
            print(f"✅ LYRICAL SCORE: {analysis.overall_lyrical_score:.1f}/10.0")
            print(f"   Rhyme: {analysis.rhyme_scheme_score:.1f} | Metaphor: {analysis.metaphor_usage_score:.1f}")
            print(f"   Theme: {analysis.thematic_coherence_score:.1f} | Vocab: {analysis.lyrical_sophistication_score:.1f} ({analysis.vocabulary_complexity})")
            
            if analysis.lyrical_strengths:
                print(f"   Top Strength: {analysis.lyrical_strengths[0]}")
            
            print(f"   Analysis Time: {analysis.analysis_time:.1f}s")
            print()
            
            # Brief pause between analyses
            if i < len(musical_scenes):
                await asyncio.sleep(2)
                
        except Exception as e:
            print(f"❌ Error analyzing {scene_info['musical']}: {e}")
            continue
    
    total_time = time.time() - total_start
    
    # Sort by overall lyrical score
    results.sort(key=lambda x: x['lyrical_scores']['overall_lyrical_score'], reverse=True)
    
    # Update rankings
    for i, result in enumerate(results, 1):
        result['rank'] = i
    
    print("=" * 60)
    print("🏆 COMPREHENSIVE LYRICAL ANALYSIS RANKINGS")
    print("=" * 60)
    
    if results:
        # Calculate collection statistics
        lyrical_scores = [r['lyrical_scores']['overall_lyrical_score'] for r in results]
        collection_average = sum(lyrical_scores) / len(lyrical_scores)
        score_range = max(lyrical_scores) - min(lyrical_scores)
        
        print(f"Collection Lyrical Average: {collection_average:.1f}/10.0")
        print(f"Lyrical Score Range: {score_range:.1f} points")
        print(f"Total Analysis Time: {total_time/60:.1f} minutes")
        print(f"Musicals Analyzed: {len(results)}/6")
        print()
        
        # Component analysis averages
        rhyme_avg = sum(r['lyrical_scores']['rhyme_scheme_score'] for r in results) / len(results)
        metaphor_avg = sum(r['lyrical_scores']['metaphor_usage_score'] for r in results) / len(results)
        theme_avg = sum(r['lyrical_scores']['thematic_coherence_score'] for r in results) / len(results)
        vocab_avg = sum(r['lyrical_scores']['vocabulary_sophistication_score'] for r in results) / len(results)
        
        print("📊 COMPONENT AVERAGES:")
        print(f"   Rhyme Scheme: {rhyme_avg:.1f}/10")
        print(f"   Metaphor Usage: {metaphor_avg:.1f}/10") 
        print(f"   Thematic Coherence: {theme_avg:.1f}/10")
        print(f"   Vocabulary Sophistication: {vocab_avg:.1f}/10")
        print()
        
        # Detailed rankings
        print("🎭 DETAILED LYRICAL RANKINGS:")
        for result in results:
            scores = result['lyrical_scores']
            print(f"{result['rank']}. {result['musical_name']}")
            print(f"   Overall Lyrical: {scores['overall_lyrical_score']}/10")
            print(f"   Components: R:{scores['rhyme_scheme_score']:.1f} M:{scores['metaphor_usage_score']:.1f} T:{scores['thematic_coherence_score']:.1f} V:{scores['vocabulary_sophistication_score']:.1f}")
            print(f"   Genre: {result['genre']} | Vocabulary: {result['lyrical_details']['vocabulary_complexity']}")
            
            if result['ai_critic_insights']['lyrical_strengths']:
                print(f"   Strength: {result['ai_critic_insights']['lyrical_strengths'][0]}")
            print()
        
        # Genre analysis
        print("🎨 LYRICAL ANALYSIS BY GENRE:")
        genre_scores = {}
        for result in results:
            genre = result['genre']
            score = result['lyrical_scores']['overall_lyrical_score']
            if genre not in genre_scores:
                genre_scores[genre] = []
            genre_scores[genre].append(score)
        
        for genre, scores in genre_scores.items():
            avg_score = sum(scores) / len(scores)
            print(f"   {genre}: {avg_score:.1f}/10 (n={len(scores)})")
        
        # Save comprehensive results
        output_data = {
            "analysis_metadata": {
                "analysis_type": "Comprehensive Lyrical Content Analysis",
                "analysis_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "system": "Advanced Lyrical Analysis - Dr. Melody Wordsworth AI Critic",
                "methodology": "Rhyme scheme, metaphor, theme, and vocabulary analysis",
                "collection_statistics": {
                    "total_musicals": len(results),
                    "collection_average": round(collection_average, 2),
                    "score_range": round(score_range, 2),
                    "analysis_time_minutes": round(total_time/60, 1)
                },
                "component_averages": {
                    "rhyme_scheme": round(rhyme_avg, 2),
                    "metaphor_usage": round(metaphor_avg, 2),  
                    "thematic_coherence": round(theme_avg, 2),
                    "vocabulary_sophistication": round(vocab_avg, 2)
                }
            },
            "lyrical_rankings": results,
            "genre_analysis": {
                genre: {
                    "average_score": round(sum(scores)/len(scores), 2),
                    "sample_size": len(scores),
                    "score_list": scores
                } for genre, scores in genre_scores.items()
            }
        }
        
        # Save to file
        output_file = "COMPREHENSIVE_lyrical_analysis.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Comprehensive lyrical analysis saved to: {output_file}")
        print("🎵 First additional evaluation complete - lyrical sophistication analyzed!")
        
        return results
    
    else:
        print("❌ No successful lyrical analyses completed")
        return []

if __name__ == "__main__":
    print("🚀 Starting Comprehensive Lyrical Analysis...")
    print("This will analyze lyrical content across all 6 Broadway musicals\n")
    
    asyncio.run(run_comprehensive_lyrical_analysis())