#!/usr/bin/env python3
"""
Instant Multi-Musical Demo
Shows 1 scene from each musical without full analysis - just display info
"""

import json
from pathlib import Path

def instant_multi_demo():
    """Display overview of all musicals and their scenes"""
    
    print("🎭 BROADWAY MUSICALS COLLECTION - INSTANT OVERVIEW")
    print("="*70)
    
    # Load conversion summary
    summary_file = Path("all_musicals_analysis/conversion_summary.json")
    
    if not summary_file.exists():
        print("❌ No conversion summary found. Run multi_musical_converter.py first.")
        return
    
    with open(summary_file, 'r') as f:
        musicals = json.load(f)
    
    total_scenes = 0
    musical_previews = []
    
    for musical_dir, musical_info in musicals.items():
        # Load first scene for preview
        json_dir = Path("all_musicals_analysis") / musical_dir / "json"
        scene_files = sorted(json_dir.glob("scene_*.json"))
        
        if scene_files:
            try:
                with open(scene_files[0], 'r', encoding='utf-8') as f:
                    scene_data = json.load(f)
                
                opening_scene = scene_data['title']
                description = scene_data.get('description', 'No description')
                has_lyrics = bool(scene_data.get('lyrics'))
                
            except Exception:
                opening_scene = "Unknown Scene"
                description = "Could not load scene data"
                has_lyrics = False
        else:
            opening_scene = "No scenes found"
            description = "No scene data available"
            has_lyrics = False
        
        musical_previews.append({
            "name": musical_info['name'],
            "scene_count": musical_info['scene_count'],
            "opening_scene": opening_scene,
            "description": description,
            "has_lyrics": has_lyrics
        })
        
        total_scenes += musical_info['scene_count']
    
    # Display overview
    print(f"📊 COLLECTION STATS")
    print(f"Total Musicals: {len(musicals)}")
    print(f"Total Scenes: {total_scenes}")
    print(f"Average Scenes per Musical: {total_scenes/len(musicals):.1f}")
    print()
    
    # Display each musical
    for i, preview in enumerate(musical_previews, 1):
        print(f"🎪 {i}. {preview['name']}")
        print(f"   Scenes: {preview['scene_count']}")
        print(f"   Opening: {preview['opening_scene']}")
        print(f"   Musical Content: {'✅ Has lyrics' if preview['has_lyrics'] else '❌ No lyrics'}")
        
        # Show description preview
        desc_preview = preview['description'][:80] + "..." if len(preview['description']) > 80 else preview['description']
        print(f"   Preview: {desc_preview}")
        print()
    
    print("🎭 READY FOR CRITIC ANALYSIS")
    print("="*50)
    print("All musicals have been converted and are ready for:")
    print("• Individual scene analysis with cli.py")
    print("• Full multi-musical analysis with multi_musical_analyzer.py")
    print("• Custom batch analysis with batch_analyzer.py")
    
    # Show available commands
    print(f"\n🚀 ANALYSIS COMMANDS")
    print("="*30)
    print("# Analyze single scene from any musical:")
    print("python3 cli.py --file all_musicals_analysis/echo_musical/json/scene_01.json")
    print()
    print("# Quick overview (1 scene per musical):")
    print("python3 quick_multi_demo.py")
    print()
    print("# Full multi-musical analysis:")
    print("python3 multi_musical_analyzer.py")

if __name__ == "__main__":
    instant_multi_demo()