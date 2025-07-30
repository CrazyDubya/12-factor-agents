#!/usr/bin/env python3
"""
Multi-Musical Converter
Discovers and converts all musicals from BroadwayMusical projects folder
"""

import json
import re
import shutil
from pathlib import Path
from main import SceneData

class MultiMusicalConverter:
    """Converts all musicals in BroadwayMusical projects to critic analysis format"""
    
    def __init__(self, source_dir: str = "/Users/pup/BroadwayMusical/projects"):
        self.source_dir = Path(source_dir)
        self.output_dir = Path("all_musicals_analysis")
        self.output_dir.mkdir(exist_ok=True)
        
        # Musical project mappings (excluding incomplete ones)
        self.musicals = {
            "echo_musical": "Echo Musical - AI Consciousness & Memory",
            "electric_dreams_musical": "Electric Dreams Musical - Technology & Desire", 
            "midnight_at_the_majestic_musical": "Midnight at the Majestic Musical - Theater Murder Mystery",
            "neon_hearts_burlesque_musical": "Neon Hearts Burlesque Musical - Underground Cabaret",
            "neon_rebellion_musical": "Neon Rebellion Musical - Dystopian Resistance",
            "rainbow_academy_musical": "Rainbow Academy Musical - Magic School Adventure"
        }
    
    def copy_musical_scenes(self, musical_dir: str, musical_name: str):
        """Copy scene files for a specific musical"""
        source_scenes = self.source_dir / musical_dir / "scenes"
        
        if not source_scenes.exists():
            print(f"⚠️  No scenes folder found for {musical_name}")
            return []
        
        # Create output directory for this musical
        output_musical_dir = self.output_dir / musical_dir
        output_scenes_dir = output_musical_dir / "scenes"
        output_scenes_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy all scene files
        scene_files = list(source_scenes.glob("*.md"))
        
        # Prioritize main scenes over revised ones
        main_scenes = [f for f in scene_files if "_revised" not in f.name and "_TRANSCENDENT" not in f.name]
        if not main_scenes:
            main_scenes = scene_files  # Use whatever is available
        
        copied_files = []
        for scene_file in main_scenes:
            dest_file = output_scenes_dir / scene_file.name
            shutil.copy2(scene_file, dest_file)
            copied_files.append(dest_file)
        
        print(f"📁 {musical_name}: Copied {len(copied_files)} scenes")
        return copied_files
    
    def extract_scene_info(self, content: str, musical_type: str) -> dict:
        """Extract scene information based on musical type"""
        info = {}
        
        # Common extraction patterns
        title_patterns = [
            r'# ACT [IVX]+, SCENE \d+: (.+)',  # Rainbow Academy format
            r'# Act [IVX]+ Scene \d+: (.+)',   # Alternative format
            r'# Scene: (.+)',                   # Simple format
            r'# (.+)',                          # Fallback to first header
        ]
        
        for pattern in title_patterns:
            title_match = re.search(pattern, content)
            if title_match:
                info['title'] = title_match.group(1).strip()
                break
        
        if 'title' not in info:
            info['title'] = "Unknown Scene"
        
        # Extract basic metadata
        for field, pattern in [
            ('location', r'\*\*Location\*\*: (.+)'),
            ('time', r'\*\*Time\*\*: (.+)'),
            ('characters', r'\*\*Characters.*?\*\*: (.+)'),
            ('plot_function', r'\*\*Plot Function\*\*: (.+)'),
            ('emotional_beat', r'\*\*Emotional Beat\*\*: (.+)'),
        ]:
            match = re.search(pattern, content)
            if match:
                info[field] = match.group(1).strip()
        
        # Extract setting/description
        setting_patterns = [
            r'## Setting Description\n\n(.*?)\n\n##',
            r'## Scene Description\n\n(.*?)\n\n##',
            r'\*([^*\n]{50,200})\*',  # Long stage directions
        ]
        
        for pattern in setting_patterns:
            setting_match = re.search(pattern, content, re.DOTALL)
            if setting_match:
                setting = setting_match.group(1).strip()
                setting = re.sub(r'\*([^*]+)\*', r'\1', setting)  # Remove italics
                info['setting'] = setting[:300]  # Limit length
                break
        
        # Extract lyrics from various formats
        lyrics = []
        lyrics_patterns = [
            r'```\n(.*?)\n```',                    # Code blocks
            r'### Verse.*?\n(.*?)(?=\n###|\n##|\Z)', # Verse sections
            r'"([^"]{20,})"',                      # Quoted lyrics
        ]
        
        for pattern in lyrics_patterns:
            for match in re.finditer(pattern, content, re.DOTALL):
                lyric_block = match.group(1).strip()
                if len(lyric_block) > 20 and ':' in lyric_block:  # Likely lyrics
                    lyrics.append(lyric_block)
        
        if lyrics:
            info['lyrics'] = '\n\n'.join(lyrics[:3])  # First 3 blocks
        
        # Extract stage directions
        stage_directions = []
        direction_pattern = r'\*([^*\n]{15,100})\*'
        for match in re.finditer(direction_pattern, content):
            direction = match.group(1).strip()
            if not direction.startswith('*'):
                stage_directions.append(direction)
        
        if stage_directions:
            info['stage_directions'] = '. '.join(stage_directions[:2])
        
        return info
    
    def create_scene_description(self, info: dict, musical_name: str) -> str:
        """Create comprehensive scene description"""
        desc_parts = [musical_name]
        
        if 'plot_function' in info:
            desc_parts.append(f"Plot: {info['plot_function']}")
        
        if 'emotional_beat' in info:
            desc_parts.append(f"Emotion: {info['emotional_beat']}")
            
        if 'location' in info and 'time' in info:
            desc_parts.append(f"Setting: {info['location']} at {info['time']}")
            
        if 'characters' in info:
            desc_parts.append(f"Characters: {info['characters']}")
        
        return ' | '.join(desc_parts)
    
    def convert_musical_scenes(self, musical_dir: str, musical_name: str) -> list:
        """Convert all scenes for a specific musical"""
        scenes_dir = self.output_dir / musical_dir / "scenes"
        
        if not scenes_dir.exists():
            return []
        
        scenes = []
        scene_files = sorted(scenes_dir.glob("*.md"))
        
        for i, filepath in enumerate(scene_files, 1):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                info = self.extract_scene_info(content, musical_dir)
                
                scene = SceneData(
                    title=info.get('title', f"Scene {i}"),
                    musical=musical_name,
                    description=self.create_scene_description(info, musical_name),
                    lyrics=info.get('lyrics'),
                    stage_directions=info.get('stage_directions'),
                    character_notes=info.get('setting', f"Scene from {musical_name}")
                )
                
                scenes.append(scene)
                
            except Exception as e:
                print(f"❌ Error converting {filepath.name}: {e}")
        
        return scenes
    
    def save_musical_scenes_json(self, musical_dir: str, scenes: list):
        """Save converted scenes as JSON files"""
        json_dir = self.output_dir / musical_dir / "json"
        json_dir.mkdir(exist_ok=True)
        
        for i, scene in enumerate(scenes, 1):
            filename = f"scene_{i:02d}.json"
            filepath = json_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(scene.__dict__, f, indent=2, ensure_ascii=False)
        
        return json_dir
    
    def process_all_musicals(self):
        """Process all musicals in the collection"""
        print("🎭 PROCESSING ALL BROADWAY MUSICALS")
        print("="*60)
        
        all_results = {}
        
        for musical_dir, musical_name in self.musicals.items():
            print(f"\n🎪 Processing: {musical_name}")
            print("-" * 50)
            
            try:
                # Copy scene files
                copied_files = self.copy_musical_scenes(musical_dir, musical_name)
                
                if not copied_files:
                    print(f"⚠️  No scenes found for {musical_name}")
                    continue
                
                # Convert to SceneData format
                scenes = self.convert_musical_scenes(musical_dir, musical_name)
                
                if scenes:
                    # Save as JSON
                    json_dir = self.save_musical_scenes_json(musical_dir, scenes)
                    
                    print(f"✅ Converted {len(scenes)} scenes")
                    print(f"📁 JSON files saved to: {json_dir}")
                    
                    all_results[musical_dir] = {
                        "name": musical_name,
                        "scene_count": len(scenes),
                        "json_dir": str(json_dir),
                        "scenes": [{"title": s.title, "has_lyrics": bool(s.lyrics)} for s in scenes]
                    }
                else:
                    print(f"❌ No scenes converted for {musical_name}")
                    
            except Exception as e:
                print(f"❌ Error processing {musical_name}: {e}")
        
        # Save summary
        summary_file = self.output_dir / "conversion_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(all_results, f, indent=2)
        
        print(f"\n🏁 CONVERSION COMPLETE")
        print(f"📊 Processed {len(all_results)} musicals")
        print(f"📄 Summary saved to: {summary_file}")
        
        return all_results

if __name__ == "__main__":
    converter = MultiMusicalConverter()
    results = converter.process_all_musicals()
    
    print(f"\n🎭 CONVERSION SUMMARY")
    print("="*40)
    total_scenes = 0
    for musical_dir, info in results.items():
        total_scenes += info['scene_count']
        print(f"• {info['name']}: {info['scene_count']} scenes")
    
    print(f"\n📊 Total: {total_scenes} scenes across {len(results)} musicals")
    print("🚀 Ready for critic ensemble analysis!")