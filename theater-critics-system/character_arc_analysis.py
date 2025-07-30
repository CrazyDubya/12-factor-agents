#!/usr/bin/env python3
"""
Character Arc Progression Analysis - Evaluation of character development
Analyzes character growth, transformation, motivation clarity, and arc completion
"""

import json
import re
import time
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
from main import SceneData

@dataclass
class CharacterAnalysis:
    """Results of character arc progression analysis"""
    scene_title: str
    character_development_score: float  # 0-10
    transformation_depth_score: float   # 0-10
    motivation_clarity_score: float     # 0-10
    arc_progression_score: float        # 0-10
    overall_character_score: float      # 0-10
    
    # Detailed analysis
    characters_identified: List[str]
    character_relationships: List[str]
    transformation_moments: List[str]
    motivation_indicators: List[str]
    progression_elements: List[str]
    
    # Quality metrics
    character_count: int
    dialogue_distribution: str  # "Balanced", "Uneven", "Single Focus"
    arc_completeness: str       # "Complete", "Developing", "Minimal"
    
    analysis_time: float

class CharacterArcAnalyzer:
    """Specialized analyzer for character development and progression"""
    
    def __init__(self):
        self.character_indicators = [
            # Character introduction patterns
            r'\b([A-Z][A-Z\s]+):\s*\(',  # Character names in dialogue
            r'\*([A-Z][A-Z\s]+)\s+',     # Character names in stage directions
            r'enters?\s+([A-Z][A-Z\s]+)', # Character entrances
            r'([A-Z][A-Z\s]+)\s+sings?',  # Singing characters
        ]
        
        self.transformation_indicators = [
            # Change and growth patterns
            r'\b(?:becomes?|transforms?|changes?|grows?|evolves?)\b',
            r'\b(?:realizes?|understands?|learns?|discovers?)\b',
            r'\b(?:different|new|changed|transformed)\b',
            r'\b(?:was|used to be|once)\b.*\b(?:but now|however|yet)\b',
            r'\b(?:journey|path|quest|mission)\b'
        ]
        
        self.motivation_indicators = [
            # Goal and desire expressions
            r'\b(?:wants?|needs?|desires?|seeks?|hopes?|dreams?)\b',
            r'\b(?:must|have to|need to|got to)\b',
            r'\b(?:because|since|for|in order to)\b',
            r'\b(?:goal|purpose|reason|mission|quest)\b',
            r'\b(?:loves?|hates?|fears?|hopes?)\b'
        ]
        
        self.relationship_indicators = [
            # Character interaction patterns
            r'\b(?:with|to|from|between)\s+([A-Z][A-Z\s]+)',
            r'\b(?:loves?|hates?|trusts?|betrays?)\b',
            r'\b(?:friend|enemy|partner|rival|ally)\b',
            r'\b(?:together|apart|against|alongside)\b',
            r'\b(?:family|mother|father|sister|brother)\b'
        ]
    
    def extract_characters(self, scene: SceneData) -> List[str]:
        """Extract character names from scene content"""
        characters = set()
        
        # Combine all text content
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes}"
        
        # Extract from dialogue patterns
        dialogue_pattern = r'\*\*([A-Z][A-Z\s]+)\*\*:'
        for match in re.finditer(dialogue_pattern, all_text):
            char_name = match.group(1).strip()
            if len(char_name) > 1 and len(char_name) < 30:  # Reasonable name length
                characters.add(char_name)
        
        # Extract from stage directions
        stage_pattern = r'\*([A-Z][A-Z\s]+)(?:\s+[a-z])'  # Name followed by action
        for match in re.finditer(stage_pattern, all_text):
            char_name = match.group(1).strip()
            if len(char_name) > 1 and len(char_name) < 30:
                characters.add(char_name)
        
        # Extract from character notes
        if scene.character_notes:
            # Look for "Characters Present:" or similar
            char_section = re.search(r'Characters?[:\s]*(.*)', scene.character_notes, re.IGNORECASE)
            if char_section:
                char_text = char_section.group(1)
                # Split by common delimiters
                for char in re.split(r'[,\n\-•]', char_text):
                    clean_char = re.sub(r'[^A-Za-z\s]', '', char).strip()
                    if clean_char and len(clean_char) > 1:
                        characters.add(clean_char.upper())
        
        return list(characters)
    
    def analyze_character_development(self, scene: SceneData, characters: List[str]) -> Tuple[float, List[str]]:
        """Analyze depth of character development"""
        if not characters:
            return 0.0, []
        
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes}".lower()
        
        development_elements = []
        development_score = 0.0
        
        # Check for character depth indicators
        depth_patterns = [
            r'\b(?:personality|character|nature|soul|heart)\b',
            r'\b(?:background|history|past|memory)\b',
            r'\b(?:feelings?|emotions?|thoughts?|believes?)\b',
            r'\b(?:struggles?|conflicts?|challenges?)\b',
            r'\b(?:strengths?|weaknesses?|flaws?)\b'
        ]
        
        for pattern in depth_patterns:
            matches = len(re.findall(pattern, all_text))
            if matches > 0:
                development_score += min(2.0, matches * 0.3)
                development_elements.append(f"Character depth indicators: {matches}")
        
        # Individual character analysis
        character_development = {}
        for char in characters:
            char_lower = char.lower()
            # Count character-specific development
            char_mentions = all_text.count(char_lower)
            if char_mentions > 1:
                development_score += min(1.0, char_mentions * 0.1)
                character_development[char] = char_mentions
        
        if character_development:
            development_elements.append(f"Multi-dimensional characters: {len(character_development)}")
        
        # Cap the score
        final_score = min(10.0, development_score)
        
        return final_score, development_elements
    
    def analyze_transformation_depth(self, scene: SceneData) -> Tuple[float, List[str]]:
        """Analyze character transformation and change"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes}".lower()
        
        transformation_moments = []
        transformation_score = 0.0
        
        # Check for transformation indicators
        for pattern in self.transformation_indicators:
            matches = re.finditer(pattern, all_text)
            for match in matches:
                # Get context around the match
                start = max(0, match.start() - 30)
                end = min(len(all_text), match.end() + 30)
                context = all_text[start:end].strip()
                transformation_moments.append(context)
                transformation_score += 1.0
        
        # Look for before/after contrasts
        contrast_patterns = [
            r'\b(?:before|previously|used to)\b.*\b(?:now|currently|today)\b',
            r'\b(?:was|were)\b.*\b(?:but now|however|yet)\b',
            r'\b(?:from|changed from)\b.*\b(?:to|into|becomes?)\b'
        ]
        
        for pattern in contrast_patterns:
            matches = len(re.findall(pattern, all_text))
            if matches > 0:
                transformation_score += matches * 1.5
                transformation_moments.append(f"Transformation contrast: {matches} instances")
        
        # Emotional transformation
        emotion_changes = re.findall(r'\b(?:from|was)\s+(\w+)\s+(?:to|but now)\s+(\w+)\b', all_text)
        if emotion_changes:
            transformation_score += len(emotion_changes) * 2.0
            transformation_moments.append(f"Emotional shifts: {len(emotion_changes)}")
        
        final_score = min(10.0, transformation_score * 0.8)
        
        return final_score, transformation_moments[:5]  # Top 5 examples
    
    def analyze_motivation_clarity(self, scene: SceneData) -> Tuple[float, List[str]]:
        """Analyze clarity of character motivations and goals"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes}".lower()
        
        motivation_indicators = []
        motivation_score = 0.0
        
        # Direct goal statements
        goal_patterns = [
            r'\b(?:i want|i need|i must|i have to)\b',
            r'\b(?:my goal|my purpose|my mission)\b',
            r'\b(?:because i|since i|for i)\b',
            r'\b(?:to achieve|to accomplish|to reach|to find)\b'
        ]
        
        for pattern in goal_patterns:
            matches = len(re.findall(pattern, all_text))
            if matches > 0:
                motivation_score += matches * 1.5
                motivation_indicators.append(f"Direct goals: {matches}")
        
        # Desire expressions
        for pattern in self.motivation_indicators:
            matches = len(re.findall(pattern, all_text))
            if matches > 0:
                motivation_score += matches * 0.8
        
        # Obstacle mentions (shows clearer motivation)
        obstacle_patterns = [
            r'\b(?:obstacle|challenge|problem|difficulty)\b',
            r'\b(?:prevents?|stops?|blocks?|hinders?)\b',
            r'\b(?:if only|if i could|wish i could)\b'
        ]
        
        for pattern in obstacle_patterns:
            matches = len(re.findall(pattern, all_text))
            if matches > 0:
                motivation_score += matches * 1.2
                motivation_indicators.append(f"Obstacles identified: {matches}")
        
        # Stakes and consequences
        stakes_patterns = [
            r'\b(?:or else|otherwise|if not|unless)\b',
            r'\b(?:everything depends|life depends|future depends)\b',
            r'\b(?:lose everything|risk everything)\b'
        ]
        
        for pattern in stakes_patterns:
            matches = len(re.findall(pattern, all_text))
            if matches > 0:
                motivation_score += matches * 2.0
                motivation_indicators.append(f"High stakes: {matches}")
        
        final_score = min(10.0, motivation_score * 0.6)
        
        return final_score, motivation_indicators[:5]
    
    def analyze_arc_progression(self, scene: SceneData) -> Tuple[float, List[str]]:
        """Analyze progression within the character arc"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes}".lower()
        
        progression_elements = []
        progression_score = 0.0
        
        # Beginning, middle, end indicators
        structure_patterns = [
            r'\b(?:begins?|starts?|commences?)\b',
            r'\b(?:continues?|proceeds?|develops?)\b',
            r'\b(?:ends?|concludes?|finishes?|completes?)\b',
            r'\b(?:climax|turning point|moment of truth)\b'
        ]
        
        for pattern in structure_patterns:
            matches = len(re.findall(pattern, all_text))
            if matches > 0:
                progression_score += matches * 1.0
        
        # Progression markers
        progression_markers = [
            r'\b(?:first|initially|at first)\b',
            r'\b(?:then|next|after|later)\b',
            r'\b(?:meanwhile|during|while)\b',
            r'\b(?:finally|eventually|in the end)\b'
        ]
        
        marker_count = 0
        for pattern in progression_markers:
            matches = len(re.findall(pattern, all_text))
            marker_count += matches
        
        progression_score += min(3.0, marker_count * 0.3)
        progression_elements.append(f"Progression markers: {marker_count}")
        
        # Character agency (making choices)
        agency_patterns = [
            r'\b(?:decides?|chooses?|determines?)\b',
            r'\b(?:i will|i shall|i choose to)\b',
            r'\b(?:acts?|takes action|takes charge)\b'
        ]
        
        agency_count = 0
        for pattern in agency_patterns:
            matches = len(re.findall(pattern, all_text))
            agency_count += matches
        
        if agency_count > 0:
            progression_score += min(2.0, agency_count * 0.5)
            progression_elements.append(f"Character agency: {agency_count}")
        
        # Conflict resolution
        resolution_patterns = [
            r'\b(?:resolves?|solves?|overcomes?)\b',
            r'\b(?:victory|success|achievement)\b',
            r'\b(?:learns?|realizes?|understands?)\b'
        ]
        
        resolution_count = 0
        for pattern in resolution_patterns:
            matches = len(re.findall(pattern, all_text))
            resolution_count += matches
        
        if resolution_count > 0:
            progression_score += min(2.0, resolution_count * 0.4)
            progression_elements.append(f"Conflict resolution: {resolution_count}")
        
        final_score = min(10.0, progression_score)
        
        return final_score, progression_elements
    
    def analyze_character_relationships(self, scene: SceneData, characters: List[str]) -> List[str]:
        """Analyze relationships between characters"""
        if len(characters) < 2:
            return ["Single character focus"]
        
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes}".lower()
        relationships = []
        
        # Look for character pairs
        for i, char1 in enumerate(characters):
            for char2 in characters[i+1:]:
                char1_lower = char1.lower()
                char2_lower = char2.lower()
                
                # Check if both characters appear together
                if char1_lower in all_text and char2_lower in all_text:
                    relationships.append(f"{char1} & {char2}")
        
        # Check for relationship words
        relationship_types = []
        relationship_patterns = [
            (r'\b(?:loves?|romance|romantic)\b', "romantic"),
            (r'\b(?:friends?|friendship|allies?)\b', "friendship"),
            (r'\b(?:enemies?|rivals?|opponents?)\b', "conflict"),
            (r'\b(?:family|relatives?|siblings?)\b', "family"),
            (r'\b(?:mentor|teacher|guide)\b', "mentorship")
        ]
        
        for pattern, rel_type in relationship_patterns:
            if re.search(pattern, all_text):
                relationship_types.append(rel_type)
        
        if relationship_types:
            relationships.extend(relationship_types)
        
        return relationships[:5]  # Top 5 relationships
    
    def determine_dialogue_distribution(self, scene: SceneData, characters: List[str]) -> str:
        """Determine how dialogue is distributed among characters"""
        if len(characters) <= 1:
            return "Single Focus"
        
        all_text = f"{scene.lyrics} {scene.stage_directions}".lower()
        
        # Count character speaking opportunities
        speaking_counts = {}
        for char in characters:
            char_lower = char.lower()
            # Count dialogue markers
            dialogue_count = len(re.findall(rf'\*\*{re.escape(char_lower)}\*\*:', all_text, re.IGNORECASE))
            singing_count = len(re.findall(rf'{re.escape(char_lower)}\s+sings?', all_text, re.IGNORECASE))
            speaking_counts[char] = dialogue_count + singing_count
        
        if not speaking_counts or all(count == 0 for count in speaking_counts.values()):
            return "Unclear"
        
        total_speaking = sum(speaking_counts.values())
        if total_speaking == 0:
            return "No Dialogue"
        
        # Check distribution
        max_count = max(speaking_counts.values())
        max_percentage = max_count / total_speaking
        
        if max_percentage > 0.7:
            return "Single Focus"
        elif max_percentage > 0.4:
            return "Uneven"
        else:
            return "Balanced"
    
    def determine_arc_completeness(self, transformation_score: float, progression_score: float) -> str:
        """Determine the completeness of character arcs"""
        combined_score = (transformation_score + progression_score) / 2
        
        if combined_score >= 7.0:
            return "Complete"
        elif combined_score >= 4.0:
            return "Developing"
        else:
            return "Minimal"
    
    def analyze_scene_characters(self, scene: SceneData) -> CharacterAnalysis:
        """Perform comprehensive character analysis on a scene"""
        analysis_start = time.time()
        
        print(f"👥 Analyzing characters for: {scene.title}")
        
        # Extract characters
        characters = self.extract_characters(scene)
        print(f"   🎭 Found {len(characters)} characters: {', '.join(characters[:3])}{'...' if len(characters) > 3 else ''}")
        
        if not characters:
            print("   ⚠️ No characters identified")
            return CharacterAnalysis(
                scene_title=scene.title,
                character_development_score=0.0,
                transformation_depth_score=0.0,
                motivation_clarity_score=0.0,
                arc_progression_score=0.0,
                overall_character_score=0.0,
                characters_identified=[],
                character_relationships=[],
                transformation_moments=[],
                motivation_indicators=[],
                progression_elements=[],
                character_count=0,
                dialogue_distribution="No Characters",
                arc_completeness="None",
                analysis_time=time.time() - analysis_start
            )
        
        # Perform component analyses
        dev_score, dev_elements = self.analyze_character_development(scene, characters)
        trans_score, trans_moments = self.analyze_transformation_depth(scene)
        motiv_score, motiv_indicators = self.analyze_motivation_clarity(scene)
        prog_score, prog_elements = self.analyze_arc_progression(scene)
        
        # Additional analyses
        relationships = self.analyze_character_relationships(scene, characters)
        dialogue_dist = self.determine_dialogue_distribution(scene, characters)
        arc_complete = self.determine_arc_completeness(trans_score, prog_score)
        
        # Calculate overall score
        overall_score = (dev_score + trans_score + motiv_score + prog_score) / 4
        
        analysis_time = time.time() - analysis_start
        
        print(f"   👤 Development: {dev_score:.1f}/10")
        print(f"   🔄 Transformation: {trans_score:.1f}/10")
        print(f"   🎯 Motivation: {motiv_score:.1f}/10")
        print(f"   📈 Progression: {prog_score:.1f}/10")
        print(f"   🏆 Overall Character Score: {overall_score:.1f}/10")
        print(f"   📊 Distribution: {dialogue_dist} | Completeness: {arc_complete}")
        
        return CharacterAnalysis(
            scene_title=scene.title,
            character_development_score=dev_score,
            transformation_depth_score=trans_score,
            motivation_clarity_score=motiv_score,
            arc_progression_score=prog_score,
            overall_character_score=overall_score,
            characters_identified=characters,
            character_relationships=relationships,
            transformation_moments=trans_moments,
            motivation_indicators=motiv_indicators,
            progression_elements=prog_elements,
            character_count=len(characters),
            dialogue_distribution=dialogue_dist,
            arc_completeness=arc_complete,
            analysis_time=analysis_time
        )

def run_character_arc_analysis():
    """Run character arc analysis on all musicals"""
    
    print("🎭👥 CHARACTER ARC PROGRESSION ANALYSIS")
    print("=" * 50)
    print("Analyzing character development, transformation, motivation, and progression")
    print()
    
    analyzer = CharacterArcAnalyzer()
    
    # Musical scenes for analysis
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
            print(f"🎪 CHARACTER ANALYSIS {i}/6: {scene_info['musical']}")
            print("-" * 45)
            
            # Load scene
            scene_path = Path(scene_info['file'])
            if not scene_path.exists():
                print(f"❌ Scene file not found: {scene_info['file']}")
                continue
            
            with open(scene_path, 'r', encoding='utf-8') as f:
                scene_data = json.load(f)
            scene = SceneData(**scene_data)
            
            print(f"Scene: {scene.title}")
            print(f"Genre: {scene_info['genre']}")
            
            # Perform character analysis
            analysis = analyzer.analyze_scene_characters(scene)
            
            # Format result
            result = {
                "rank": i,
                "musical_name": scene_info['musical'],
                "genre": scene_info['genre'],
                "scene_title": analysis.scene_title,
                "character_scores": {
                    "overall_character_score": round(analysis.overall_character_score, 2),
                    "character_development_score": round(analysis.character_development_score, 2),
                    "transformation_depth_score": round(analysis.transformation_depth_score, 2),
                    "motivation_clarity_score": round(analysis.motivation_clarity_score, 2),
                    "arc_progression_score": round(analysis.arc_progression_score, 2)
                },
                "character_details": {
                    "character_count": analysis.character_count,
                    "characters_identified": analysis.characters_identified,
                    "character_relationships": analysis.character_relationships,
                    "dialogue_distribution": analysis.dialogue_distribution,
                    "arc_completeness": analysis.arc_completeness
                },
                "analysis_insights": {
                    "transformation_moments": analysis.transformation_moments,
                    "motivation_indicators": analysis.motivation_indicators,
                    "progression_elements": analysis.progression_elements
                },
                "analysis_time": round(analysis.analysis_time, 2)
            }
            
            results.append(result)
            print()
            
        except Exception as e:
            print(f"❌ Error analyzing {scene_info['musical']}: {e}")
            continue
    
    total_time = time.time() - total_start
    
    # Sort by overall character score
    results.sort(key=lambda x: x['character_scores']['overall_character_score'], reverse=True)
    
    # Update rankings
    for i, result in enumerate(results, 1):
        result['rank'] = i
    
    print("=" * 50)
    print("🏆 CHARACTER ARC ANALYSIS RANKINGS")
    print("=" * 50)
    
    if results:
        # Calculate statistics
        char_scores = [r['character_scores']['overall_character_score'] for r in results]
        collection_average = sum(char_scores) / len(char_scores)
        score_range = max(char_scores) - min(char_scores)
        
        print(f"Collection Average: {collection_average:.1f}/10.0")
        print(f"Score Range: {score_range:.1f} points")
        print(f"Analysis Time: {total_time:.1f} seconds")
        print(f"Musicals Analyzed: {len(results)}/6")
        print()
        
        # Component averages
        dev_avg = sum(r['character_scores']['character_development_score'] for r in results) / len(results)
        trans_avg = sum(r['character_scores']['transformation_depth_score'] for r in results) / len(results)
        motiv_avg = sum(r['character_scores']['motivation_clarity_score'] for r in results) / len(results)
        prog_avg = sum(r['character_scores']['arc_progression_score'] for r in results) / len(results)
        
        print("📊 COMPONENT AVERAGES:")
        print(f"   Character Development: {dev_avg:.1f}/10")
        print(f"   Transformation Depth: {trans_avg:.1f}/10")
        print(f"   Motivation Clarity: {motiv_avg:.1f}/10")
        print(f"   Arc Progression: {prog_avg:.1f}/10")
        print()
        
        # Rankings
        print("🎭 CHARACTER RANKINGS:")
        for result in results:
            scores = result['character_scores']
            details = result['character_details']
            print(f"{result['rank']}. {result['musical_name']}")
            print(f"   Overall: {scores['overall_character_score']}/10 | Characters: {details['character_count']}")
            print(f"   Dev:{scores['character_development_score']:.1f} Trans:{scores['transformation_depth_score']:.1f} Motiv:{scores['motivation_clarity_score']:.1f} Prog:{scores['arc_progression_score']:.1f}")
            print(f"   Distribution: {details['dialogue_distribution']} | Completeness: {details['arc_completeness']}")
            
            if details['characters_identified']:
                print(f"   Characters: {', '.join(details['characters_identified'][:3])}")
            print()
        
        # Save results
        output_data = {
            "analysis_metadata": {
                "analysis_type": "Character Arc Progression Analysis",
                "analysis_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_musicals": len(results),
                "collection_average": round(collection_average, 2),
                "score_range": round(score_range, 2),
                "analysis_time_seconds": round(total_time, 1),
                "component_averages": {
                    "character_development": round(dev_avg, 2),
                    "transformation_depth": round(trans_avg, 2),
                    "motivation_clarity": round(motiv_avg, 2),
                    "arc_progression": round(prog_avg, 2)
                }
            },
            "character_rankings": results
        }
        
        with open("CHARACTER_arc_analysis.json", 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Character analysis saved to: CHARACTER_arc_analysis.json")
        print("👥 Character Arc Progression Analysis complete!")
        
        return results
    
    else:
        print("❌ No analyses completed")
        return []

if __name__ == "__main__":
    print("🚀 Starting Character Arc Progression Analysis...")
    run_character_arc_analysis()