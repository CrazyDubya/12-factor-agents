#!/usr/bin/env python3
"""
Rainbow Academy Musical Scene Converter
Converts markdown scene files to SceneData format for critic analysis
"""

import json
import re
from pathlib import Path
from main import SceneData

class RainbowSceneConverter:
    """Converts Rainbow Academy markdown scenes to SceneData format"""
    
    def __init__(self, scenes_dir: str = "rainbow_academy_scenes"):
        self.scenes_dir = Path(scenes_dir)
    
    def extract_scene_info(self, content: str) -> dict:
        """Extract structured information from markdown scene"""
        info = {}
        
        # Extract title from header
        title_match = re.search(r'# ACT [IVX]+, SCENE \d+: (.+)', content)
        if title_match:
            info['title'] = title_match.group(1).strip()
        else:
            info['title'] = "Unknown Scene"
        
        # Extract act and scene from header
        act_scene_match = re.search(r'# ACT ([IVX]+), SCENE (\d+)', content)
        if act_scene_match:
            info['act'] = act_scene_match.group(1)
            info['scene_num'] = act_scene_match.group(2)
        
        # Extract location and time
        location_match = re.search(r'\*\*Location\*\*: (.+)', content)
        if location_match:
            info['location'] = location_match.group(1).strip()
            
        time_match = re.search(r'\*\*Time\*\*: (.+)', content)
        if time_match:
            info['time'] = time_match.group(1).strip()
        
        # Extract characters
        chars_match = re.search(r'\*\*Characters Present\*\*: (.+)', content)
        if chars_match:
            info['characters'] = chars_match.group(1).strip()
        
        # Extract scene purpose and emotional beat
        purpose_match = re.search(r'\*\*Plot Function\*\*: (.+)', content)
        if purpose_match:
            info['plot_function'] = purpose_match.group(1).strip()
            
        emotion_match = re.search(r'\*\*Emotional Beat\*\*: (.+)', content)
        if emotion_match:
            info['emotional_beat'] = emotion_match.group(1).strip()
        
        # Extract setting description
        setting_match = re.search(r'## Setting Description\n\n(.*?)\n\n##', content, re.DOTALL)
        if setting_match:
            # Clean up markdown formatting
            setting = setting_match.group(1).strip()
            setting = re.sub(r'\*([^*]+)\*', r'\1', setting)  # Remove italics
            info['setting'] = setting
        
        # Extract lyrics from musical numbers
        lyrics = []
        lyrics_pattern = r'```\n(.*?)\n```'
        for match in re.finditer(lyrics_pattern, content, re.DOTALL):
            lyric_block = match.group(1).strip()
            if any(char in lyric_block for char in [':', '\n']):  # Likely lyrics
                lyrics.append(lyric_block)
        
        if lyrics:
            info['lyrics'] = '\n\n'.join(lyrics)
        
        # Extract stage directions from scene content
        stage_directions = []
        direction_pattern = r'\*([^*\n]+)\*'
        for match in re.finditer(direction_pattern, content):
            direction = match.group(1).strip()
            if len(direction) > 20 and not direction.startswith('*'):  # Substantial stage directions
                stage_directions.append(direction)
        
        if stage_directions:
            info['stage_directions'] = '. '.join(stage_directions[:3])  # First 3 directions
        
        return info
    
    def create_scene_description(self, info: dict) -> str:
        """Create comprehensive scene description"""
        desc_parts = []
        
        if 'plot_function' in info:
            desc_parts.append(f"Plot: {info['plot_function']}")
        
        if 'emotional_beat' in info:
            desc_parts.append(f"Emotion: {info['emotional_beat']}")
            
        if 'location' in info and 'time' in info:
            desc_parts.append(f"Setting: {info['location']} at {info['time']}")
            
        if 'characters' in info:
            desc_parts.append(f"Characters: {info['characters']}")
        
        return ' | '.join(desc_parts)
    
    def convert_scene_file(self, filepath: Path) -> SceneData:
        """Convert single markdown scene file to SceneData"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        info = self.extract_scene_info(content)
        
        # Create SceneData object
        scene = SceneData(
            title=info.get('title', filepath.stem),
            musical="Rainbow Academy Musical",
            description=self.create_scene_description(info),
            lyrics=info.get('lyrics'),
            stage_directions=info.get('stage_directions'),
            character_notes=info.get('setting')  # Use setting as character context
        )
        
        return scene
    
    def convert_all_scenes(self) -> list:
        """Convert all scene files in directory"""
        scenes = []
        scene_files = sorted(self.scenes_dir.glob("*.md"))
        
        for filepath in scene_files:
            print(f"Converting: {filepath.name}")
            try:
                scene = self.convert_scene_file(filepath)
                scenes.append(scene)
            except Exception as e:
                print(f"Error converting {filepath.name}: {e}")
        
        return scenes
    
    def save_scenes_as_json(self, scenes: list, output_dir: str = "rainbow_scenes_json"):
        """Save converted scenes as JSON files for cli.py"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        for i, scene in enumerate(scenes, 1):
            filename = f"rainbow_act{1 if i <= 6 else 2}_scene{i if i <= 6 else i-6}.json"
            filepath = output_path / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(scene.__dict__, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(scenes)} scenes to {output_dir}/")
        return output_path

if __name__ == "__main__":
    converter = RainbowSceneConverter()
    scenes = converter.convert_all_scenes()
    
    print(f"\n🎭 Converted {len(scenes)} Rainbow Academy scenes:")
    for i, scene in enumerate(scenes, 1):
        print(f"{i:2d}. {scene.title}")
        print(f"     {scene.description[:80]}...")
        if scene.lyrics:
            lyric_preview = scene.lyrics.replace('\n', ' ')[:60]
            print(f"     ♪ {lyric_preview}...")
        print()
    
    # Save as JSON files
    converter.save_scenes_as_json(scenes)