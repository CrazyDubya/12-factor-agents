#!/usr/bin/env python3
"""
Fast Lyrical Analysis - Technical analysis without AI delay
Quick evaluation of lyrical content across all musicals
"""

import json
import time
from pathlib import Path
from lyrical_analysis import LyricalContentAnalyzer
from main import SceneData

def run_fast_lyrical_analysis():
    """Run technical lyrical analysis without AI delays"""
    
    print("🎭🎵 FAST LYRICAL ANALYSIS - TECHNICAL EVALUATION")
    print("=" * 55)
    print("Quick technical analysis of lyrical content")
    print("Components: Rhyme, Metaphor, Theme, Vocabulary\n")
    
    analyzer = LyricalContentAnalyzer()
    
    # All musical scenes
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
            print(f"🎪 ANALYZING {i}/6: {scene_info['musical']}")
            print("-" * 45)
            
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
            
            # Extract lyrics
            lyrics = analyzer.extract_lyrics_from_scene(scene)
            
            if not lyrics:
                print("   ⚠️ No lyrics found")
                continue
            
            print(f"   📝 Found {len(lyrics)} lyrical lines")
            
            # Technical analysis (no AI delay)
            rhyme_score, rhyme_patterns = analyzer.analyze_rhyme_scheme(lyrics)
            metaphor_score, metaphors = analyzer.analyze_metaphors(lyrics)
            theme_score, themes = analyzer.analyze_thematic_coherence(lyrics, scene.title)
            vocab_score, vocab_level = analyzer.analyze_vocabulary_complexity(lyrics)
            
            # Calculate overall score
            overall_score = (rhyme_score + metaphor_score + theme_score + vocab_score) / 4
            
            result = {
                "rank": i,
                "musical_name": scene_info['musical'],
                "genre": scene_info['genre'],
                "scene_title": scene.title,
                "lyrical_scores": {
                    "overall_lyrical_score": round(overall_score, 2),
                    "rhyme_scheme_score": round(rhyme_score, 2), 
                    "metaphor_usage_score": round(metaphor_score, 2),
                    "thematic_coherence_score": round(theme_score, 2),
                    "vocabulary_sophistication_score": round(vocab_score, 2)
                },
                "lyrical_details": {
                    "lyric_line_count": len(lyrics),
                    "rhyme_patterns": rhyme_patterns,
                    "metaphors_identified": metaphors[:3],
                    "thematic_elements": themes[:5],
                    "vocabulary_complexity": vocab_level
                }
            }
            
            results.append(result)
            
            print(f"   🎼 Rhyme Scheme: {rhyme_score:.1f}/10")
            print(f"   🎭 Metaphors: {metaphor_score:.1f}/10") 
            print(f"   🎯 Themes: {theme_score:.1f}/10")
            print(f"   📚 Vocabulary: {vocab_score:.1f}/10 ({vocab_level})")
            print(f"   🏆 Overall: {overall_score:.1f}/10")
            print()
                
        except Exception as e:
            print(f"❌ Error analyzing {scene_info['musical']}: {e}")
            continue
    
    total_time = time.time() - total_start
    
    # Sort by overall lyrical score
    results.sort(key=lambda x: x['lyrical_scores']['overall_lyrical_score'], reverse=True)
    
    # Update rankings
    for i, result in enumerate(results, 1):
        result['rank'] = i
    
    print("=" * 55)
    print("🏆 FAST LYRICAL ANALYSIS RANKINGS")
    print("=" * 55)
    
    if results:
        # Calculate statistics
        lyrical_scores = [r['lyrical_scores']['overall_lyrical_score'] for r in results]
        collection_average = sum(lyrical_scores) / len(lyrical_scores)
        score_range = max(lyrical_scores) - min(lyrical_scores)
        
        print(f"Collection Average: {collection_average:.1f}/10.0")
        print(f"Score Range: {score_range:.1f} points")
        print(f"Analysis Time: {total_time:.1f} seconds")
        print(f"Musicals Analyzed: {len(results)}/6")
        print()
        
        # Component averages
        rhyme_avg = sum(r['lyrical_scores']['rhyme_scheme_score'] for r in results) / len(results)
        metaphor_avg = sum(r['lyrical_scores']['metaphor_usage_score'] for r in results) / len(results)
        theme_avg = sum(r['lyrical_scores']['thematic_coherence_score'] for r in results) / len(results)
        vocab_avg = sum(r['lyrical_scores']['vocabulary_sophistication_score'] for r in results) / len(results)
        
        print("📊 COMPONENT AVERAGES:")
        print(f"   Rhyme Scheme: {rhyme_avg:.1f}/10")
        print(f"   Metaphor Usage: {metaphor_avg:.1f}/10") 
        print(f"   Thematic Coherence: {theme_avg:.1f}/10")
        print(f"   Vocabulary: {vocab_avg:.1f}/10")
        print()
        
        # Rankings
        print("🎭 LYRICAL RANKINGS:")
        for result in results:
            scores = result['lyrical_scores']
            details = result['lyrical_details']
            print(f"{result['rank']}. {result['musical_name']}")
            print(f"   Overall: {scores['overall_lyrical_score']}/10 | Lines: {details['lyric_line_count']}")
            print(f"   R:{scores['rhyme_scheme_score']:.1f} M:{scores['metaphor_usage_score']:.1f} T:{scores['thematic_coherence_score']:.1f} V:{scores['vocabulary_sophistication_score']:.1f}")
            print(f"   Vocabulary: {details['vocabulary_complexity']} | Genre: {result['genre']}")
            
            if details['thematic_elements']:
                print(f"   Top Theme: {details['thematic_elements'][0]}")
            print()
        
        # Save results
        output_data = {
            "analysis_metadata": {
                "analysis_type": "Fast Technical Lyrical Analysis",
                "analysis_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_musicals": len(results),
                "collection_average": round(collection_average, 2),
                "score_range": round(score_range, 2),
                "analysis_time_seconds": round(total_time, 1),
                "component_averages": {
                    "rhyme_scheme": round(rhyme_avg, 2),
                    "metaphor_usage": round(metaphor_avg, 2),  
                    "thematic_coherence": round(theme_avg, 2),
                    "vocabulary_sophistication": round(vocab_avg, 2)
                }
            },
            "lyrical_rankings": results
        }
        
        with open("FAST_lyrical_analysis.json", 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Fast analysis saved to: FAST_lyrical_analysis.json")
        print("🎵 Technical lyrical analysis complete!")
        
        return results
    
    else:
        print("❌ No analyses completed")
        return []

if __name__ == "__main__":
    print("🚀 Starting Fast Lyrical Analysis...")
    run_fast_lyrical_analysis()