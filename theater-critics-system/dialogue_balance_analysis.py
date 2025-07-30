#!/usr/bin/env python3
"""
Dialogue vs Song Balance Analysis
Evaluates the structural composition and pacing balance between spoken and sung content
"""

import json
import re
import time
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
from main import SceneData

@dataclass
class DialogueBalanceAnalysis:
    """Results of dialogue vs song balance analysis"""
    scene_title: str
    dialogue_song_ratio_score: float      # 0-10 - Optimal balance between dialogue and song
    transition_quality_score: float       # 0-10 - Smoothness of dialogue-to-song transitions
    integration_effectiveness_score: float # 0-10 - How well dialogue and song work together
    pacing_balance_score: float           # 0-10 - Overall rhythm and flow effectiveness
    overall_balance_score: float          # 0-10 - Combined structural balance assessment
    
    # Detailed balance mapping
    content_breakdown: Dict[str, float]    # Percentages of dialogue vs song vs stage directions
    transition_moments: List[str]
    integration_techniques: List[str]
    pacing_elements: List[str]
    balance_strengths: List[str]
    
    # Balance characteristics
    content_distribution: str             # "Dialogue Heavy", "Song Heavy", "Balanced", "Stage Heavy"
    transition_style: str                 # "Seamless", "Distinct", "Abrupt", "Gradual"
    integration_approach: str             # "Unified", "Contrasted", "Layered", "Sequential"
    pacing_pattern: str                   # "Steady", "Dynamic", "Accelerating", "Varied"
    
    analysis_time: float

class DialogueBalanceAnalyzer:
    """Specialized analyzer for dialogue vs song balance evaluation"""
    
    def __init__(self):
        # Content type identification patterns
        self.content_patterns = {
            "dialogue": [
                # Direct speech patterns
                r'\*\*[A-Z][A-Z\s]+\*\*:\s*[^*\n]+',  # Character dialogue
                r'says?\s*["\'].*?["\']',              # Quoted speech
                r'speaks?\s*["\'].*?["\']',            # Spoken words
                r'\b(?:whispers?|shouts?|calls?|asks?|replies?)\b.*?["\'].*?["\']'
            ],
            "song": [
                # Musical/lyrical patterns
                r'\*[^*]*sings?[^*]*\*',               # Singing stage directions
                r'\*[^*]*music[^*]*\*',                # Music cues
                r'♪.*?♪',                              # Musical notation
                r'\[SONG[:\s].*?\]',                   # Song markers
                r'\b(?:verse|chorus|bridge|refrain)\b', # Song structure
                r'\b(?:melody|harmony|lyrics|tune)\b'   # Musical terminology
            ],
            "stage_directions": [
                # Stage direction patterns
                r'\*[^*]+\*',                          # Italicized stage directions
                r'\([^)]+\)',                          # Parenthetical directions
                r'\[[^\]]+\]',                         # Bracketed directions
                r'(?:enters?|exits?|moves?|crosses?)',  # Movement directions
                r'(?:lights?|sound|music).*(?:up|down|in|out)' # Technical directions
            ]
        }
        
        # Transition quality indicators
        self.transition_indicators = {
            "seamless": [
                r'\b(?:seamlessly|smoothly|naturally|flows)\b',
                r'\b(?:without pause|continuous|unbroken)\b',
                r'\b(?:melts into|transforms into|becomes)\b'
            ],
            "distinct": [
                r'\b(?:clearly|distinctly|separately|independently)\b',
                r'\b(?:then|next|after|following)\b',
                r'\b(?:switches to|changes to|moves to)\b'
            ],
            "abrupt": [
                r'\b(?:suddenly|abruptly|immediately|instantly)\b',
                r'\b(?:cuts to|jumps to|snaps to)\b',
                r'\b(?:without warning|unexpected)\b'
            ],
            "gradual": [
                r'\b(?:gradually|slowly|gently|softly)\b',
                r'\b(?:builds into|develops into|grows into)\b',
                r'\b(?:ease into|slide into|drift into)\b'
            ]
        }
        
        # Integration technique patterns
        self.integration_patterns = {
            "underscoring": [
                r'\b(?:underscoring|background music|musical underscore)\b',
                r'\b(?:music under|music behind|instrumental backing)\b'
            ],
            "dialogue_in_song": [
                r'\b(?:spoken during song|dialogue over music)\b',
                r'\b(?:rap|recitative|spoken word)\b',
                r'\b(?:talk-singing|speech-song|rhythmic speech)\b'
            ],
            "song_in_dialogue": [
                r'\b(?:humming|singing fragments|musical phrases)\b',
                r'\b(?:whistling|vocal runs|melodic speech)\b'
            ],
            "alternating": [
                r'\b(?:back and forth|alternating|trading)\b',
                r'\b(?:call and response|dialogue exchange)\b'
            ]
        }
        
        # Pacing and rhythm indicators
        self.pacing_patterns = {
            "tempo_changes": [
                r'\b(?:accelerando|ritardando|faster|slower)\b',
                r'\b(?:speed up|slow down|tempo change)\b',
                r'\b(?:rushing|dragging|hurried|leisurely)\b'
            ],
            "rhythmic_elements": [
                r'\b(?:rhythm|beat|pulse|meter)\b',
                r'\b(?:staccato|legato|syncopated)\b',
                r'\b(?:rhythmic|percussive|driving)\b'
            ],
            "breathing_space": [
                r'\b(?:pause|silence|rest|breath)\b',
                r'\b(?:moment of quiet|stillness|calm)\b',
                r'\b(?:space|gap|interval)\b'
            ],
            "energy_shifts": [
                r'\b(?:builds|climax|crescendo|diminuendo)\b',
                r'\b(?:intensity|energy|power|force)\b',
                r'\b(?:explosive|gentle|powerful|subtle)\b'
            ]
        }
    
    def extract_content_elements(self, scene: SceneData) -> Dict[str, List[str]]:
        """Extract dialogue, song, and stage direction elements"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes}"
        
        content_elements = {
            "dialogue_samples": [],
            "song_samples": [],
            "stage_direction_samples": [],
            "transition_samples": []
        }
        
        # Extract dialogue examples
        for pattern in self.content_patterns["dialogue"]:
            matches = re.finditer(pattern, all_text)
            for match in matches:
                content_elements["dialogue_samples"].append(match.group()[:100])
        
        # Extract song examples
        for pattern in self.content_patterns["song"]:
            matches = re.finditer(pattern, all_text)
            for match in matches:
                content_elements["song_samples"].append(match.group()[:100])
        
        # Extract stage direction examples
        for pattern in self.content_patterns["stage_directions"]:
            matches = re.finditer(pattern, all_text)
            for match in matches:
                content_elements["stage_direction_samples"].append(match.group()[:100])
        
        return content_elements
    
    def analyze_content_breakdown(self, scene: SceneData) -> Tuple[Dict[str, float], float]:
        """Analyze the percentage breakdown of content types"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes}"
        total_length = len(all_text)
        
        if total_length == 0:
            return {"dialogue": 0, "song": 0, "stage_directions": 0}, 0.0
        
        content_counts = {"dialogue": 0, "song": 0, "stage_directions": 0}
        
        # Count content by type
        for content_type, patterns in self.content_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, all_text)
                for match in matches:
                    content_counts[content_type] += len(match.group())
        
        # Calculate percentages
        total_categorized = sum(content_counts.values())
        if total_categorized == 0:
            # If no patterns matched, analyze by structure
            lines = all_text.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('*') and line.endswith('*'):
                    content_counts["stage_directions"] += len(line)
                elif '**' in line and ':' in line:
                    content_counts["dialogue"] += len(line)
                else:
                    content_counts["song"] += len(line)
            total_categorized = sum(content_counts.values())
        
        percentages = {}
        for content_type, count in content_counts.items():
            percentages[content_type] = (count / total_categorized * 100) if total_categorized > 0 else 0
        
        # Score based on balance (ideal is roughly 40% song, 30% dialogue, 30% stage directions)
        ideal_ratios = {"song": 40, "dialogue": 30, "stage_directions": 30}
        balance_score = 0.0
        
        for content_type, ideal_pct in ideal_ratios.items():
            actual_pct = percentages[content_type]
            # Score based on deviation from ideal
            deviation = abs(actual_pct - ideal_pct)
            type_score = max(0, 10 - (deviation / 10))  # 10 points minus deviation penalty
            balance_score += type_score * (ideal_pct / 100)  # Weight by ideal importance
        
        return percentages, balance_score
    
    def analyze_transition_quality(self, scene: SceneData) -> Tuple[float, List[str]]:
        """Analyze the quality of transitions between dialogue and song"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes}".lower()
        
        transition_moments = []
        transition_score = 0.0
        
        # Look for explicit transition indicators
        transition_phrases = [
            r'\b(?:transitions? to|moves? into|becomes?|transforms? into)\b',
            r'\b(?:dialogue becomes song|speech becomes music)\b',
            r'\b(?:singing begins|music starts|song emerges)\b',
            r'\b(?:from speaking to singing|speech to song)\b'
        ]
        
        for pattern in transition_phrases:
            matches = re.finditer(pattern, all_text)
            for match in matches:
                # Get context around transition
                start = max(0, match.start() - 50)
                end = min(len(all_text), match.end() + 50)
                context = all_text[start:end].strip()
                transition_moments.append(f"Transition: {context}")
                transition_score += 1.5
        
        # Analyze transition style quality
        for style, patterns in self.transition_indicators.items():
            style_count = 0
            for pattern in patterns:
                style_count += len(re.findall(pattern, all_text))
            
            if style_count > 0:
                # Score based on transition style sophistication
                style_weights = {"seamless": 2.0, "gradual": 1.5, "distinct": 1.0, "abrupt": 0.5}
                transition_score += style_count * style_weights.get(style, 1.0)
                transition_moments.append(f"{style.title()} transitions: {style_count}")
        
        # Look for musical bridge elements
        bridge_patterns = [
            r'\b(?:musical bridge|instrumental|interlude)\b',
            r'\b(?:vamp|musical transition|segue)\b',
            r'\b(?:modulation|key change|tempo shift)\b'
        ]
        
        bridge_count = sum(len(re.findall(pattern, all_text)) for pattern in bridge_patterns)
        if bridge_count > 0:
            transition_score += bridge_count * 1.2
            transition_moments.append(f"Musical bridges: {bridge_count}")
        
        final_score = min(10.0, transition_score)
        
        return final_score, transition_moments[:5]
    
    def analyze_integration_effectiveness(self, scene: SceneData) -> Tuple[float, List[str]]:
        """Analyze how effectively dialogue and song work together"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes}".lower()
        
        integration_techniques = []
        integration_score = 0.0
        
        # Analyze integration techniques
        for technique, patterns in self.integration_patterns.items():
            technique_count = 0
            for pattern in patterns:
                technique_count += len(re.findall(pattern, all_text))
            
            if technique_count > 0:
                # Score based on technique sophistication
                technique_weights = {
                    "underscoring": 1.2,
                    "dialogue_in_song": 1.8,
                    "song_in_dialogue": 1.5,
                    "alternating": 1.3
                }
                integration_score += technique_count * technique_weights.get(technique, 1.0)
                integration_techniques.append(f"{technique.replace('_', ' ').title()}: {technique_count}")
        
        # Look for thematic integration
        thematic_integration = [
            r'\b(?:reinforces the theme|supports the message)\b',
            r'\b(?:same emotional tone|consistent mood)\b',
            r'\b(?:builds on the dialogue|expands the idea)\b',
            r'\b(?:unified vision|cohesive approach)\b'
        ]
        
        thematic_count = sum(len(re.findall(pattern, all_text)) for pattern in thematic_integration)
        if thematic_count > 0:
            integration_score += thematic_count * 1.5
            integration_techniques.append(f"Thematic integration: {thematic_count}")
        
        # Character consistency across dialogue and song
        character_consistency = [
            r'\b(?:same character voice|consistent personality)\b',
            r'\b(?:maintains character|stays in character)\b',
            r'\b(?:character development|character growth)\b'
        ]
        
        character_count = sum(len(re.findall(pattern, all_text)) for pattern in character_consistency)
        if character_count > 0:
            integration_score += character_count * 1.3
            integration_techniques.append(f"Character consistency: {character_count}")
        
        # Narrative flow integration
        narrative_flow = [
            r'\b(?:advances the plot|moves story forward)\b',
            r'\b(?:narrative continuity|story flow)\b',
            r'\b(?:seamless storytelling|unified narrative)\b'
        ]
        
        narrative_count = sum(len(re.findall(pattern, all_text)) for pattern in narrative_flow)
        if narrative_count > 0:
            integration_score += narrative_count * 1.4
            integration_techniques.append(f"Narrative flow: {narrative_count}")
        
        final_score = min(10.0, integration_score)
        
        return final_score, integration_techniques[:5]
    
    def analyze_pacing_balance(self, scene: SceneData) -> Tuple[float, List[str]]:
        """Analyze overall rhythm and flow effectiveness"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes}".lower()
        
        pacing_elements = []
        pacing_score = 0.0
        
        # Analyze pacing patterns
        for pattern_type, patterns in self.pacing_patterns.items():
            pattern_count = 0
            for pattern in patterns:
                pattern_count += len(re.findall(pattern, all_text))
            
            if pattern_count > 0:
                # Score based on pacing element importance
                pattern_weights = {
                    "tempo_changes": 1.5,
                    "rhythmic_elements": 1.3,
                    "breathing_space": 1.4,
                    "energy_shifts": 1.6
                }
                pacing_score += pattern_count * pattern_weights.get(pattern_type, 1.0)
                pacing_elements.append(f"{pattern_type.replace('_', ' ').title()}: {pattern_count}")
        
        # Analyze structural pacing
        structural_pacing = [
            r'\b(?:builds to climax|crescendo|dramatic peak)\b',
            r'\b(?:varies the pace|changes rhythm|shifts tempo)\b',
            r'\b(?:moment of stillness|pause for effect)\b',
            r'\b(?:accelerating action|building tension)\b'
        ]
        
        structural_count = sum(len(re.findall(pattern, all_text)) for pattern in structural_pacing)
        if structural_count > 0:
            pacing_score += structural_count * 1.2
            pacing_elements.append(f"Structural pacing: {structural_count}")
        
        # Emotional pacing
        emotional_pacing = [
            r'\b(?:emotional journey|feeling progression)\b',
            r'\b(?:builds emotion|emotional climax)\b',
            r'\b(?:emotional breathing room|moment to process)\b'
        ]
        
        emotional_count = sum(len(re.findall(pattern, all_text)) for pattern in emotional_pacing)
        if emotional_count > 0:
            pacing_score += emotional_count * 1.3
            pacing_elements.append(f"Emotional pacing: {emotional_count}")
        
        # Audience engagement pacing
        engagement_pacing = [
            r'\b(?:keeps audience engaged|holds attention)\b',
            r'\b(?:varies the energy|dynamic contrast)\b',
            r'\b(?:surprises|unexpected moments)\b'
        ]
        
        engagement_count = sum(len(re.findall(pattern, all_text)) for pattern in engagement_pacing)
        if engagement_count > 0:
            pacing_score += engagement_count * 1.1
            pacing_elements.append(f"Engagement pacing: {engagement_count}")
        
        final_score = min(10.0, pacing_score)
        
        return final_score, pacing_elements[:5]
    
    def determine_content_distribution(self, percentages: Dict[str, float]) -> str:
        """Determine the primary content distribution pattern"""
        max_type = max(percentages, key=percentages.get)
        max_pct = percentages[max_type]
        
        if max_pct > 60:
            if max_type == "dialogue":
                return "Dialogue Heavy"
            elif max_type == "song":
                return "Song Heavy"
            else:
                return "Stage Heavy"
        elif max_pct < 45:
            return "Balanced"
        else:
            return "Moderately " + max_type.replace("_", " ").title()
    
    def determine_transition_style(self, scene: SceneData) -> str:
        """Determine the primary transition style"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes}".lower()
        
        style_scores = {}
        for style, patterns in self.transition_indicators.items():
            score = sum(len(re.findall(pattern, all_text)) for pattern in patterns)
            if score > 0:
                style_scores[style] = score
        
        if style_scores:
            return max(style_scores, key=style_scores.get).title()
        else:
            return "Distinct"
    
    def determine_integration_approach(self, scene: SceneData) -> str:
        """Determine the primary integration approach"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes}".lower()
        
        if re.search(r'\b(?:unified|cohesive|seamless)\b', all_text):
            return "Unified"
        elif re.search(r'\b(?:contrast|different|opposite)\b', all_text):
            return "Contrasted"
        elif re.search(r'\b(?:layered|complex|multiple)\b', all_text):
            return "Layered"
        else:
            return "Sequential"
    
    def determine_pacing_pattern(self, scene: SceneData) -> str:
        """Determine the overall pacing pattern"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes}".lower()
        
        if re.search(r'\b(?:builds|accelerates|speeds up|faster)\b', all_text):
            return "Accelerating"
        elif re.search(r'\b(?:varies|changes|shifts|different)\b', all_text):
            return "Varied"
        elif re.search(r'\b(?:steady|consistent|regular|even)\b', all_text):
            return "Steady"
        else:
            return "Dynamic"
    
    def analyze_scene_dialogue_balance(self, scene: SceneData) -> DialogueBalanceAnalysis:
        """Perform comprehensive dialogue vs song balance analysis"""
        analysis_start = time.time()
        
        print(f"🎭 Analyzing dialogue/song balance for: {scene.title}")
        
        # Extract content elements
        content_elements = self.extract_content_elements(scene)
        print(f"   💬 Found {len(content_elements['dialogue_samples'])} dialogue elements")
        print(f"   🎵 Found {len(content_elements['song_samples'])} song elements")
        
        # Perform component analyses
        percentages, ratio_score = self.analyze_content_breakdown(scene)
        transition_score, transitions = self.analyze_transition_quality(scene)
        integration_score, integration_techniques = self.analyze_integration_effectiveness(scene)
        pacing_score, pacing_elements = self.analyze_pacing_balance(scene)
        
        # Determine balance characteristics
        content_distribution = self.determine_content_distribution(percentages)
        transition_style = self.determine_transition_style(scene)
        integration_approach = self.determine_integration_approach(scene)
        pacing_pattern = self.determine_pacing_pattern(scene)
        
        # Calculate overall balance score
        overall_score = (ratio_score * 0.3 + transition_score * 0.25 + 
                        integration_score * 0.25 + pacing_score * 0.2)
        
        # Identify balance strengths
        balance_strengths = []
        if ratio_score >= 7.0:
            balance_strengths.append("Well-balanced content distribution")
        if transition_score >= 7.0:
            balance_strengths.append("Smooth dialogue-song transitions")
        if integration_score >= 7.0:
            balance_strengths.append("Effective content integration")
        if pacing_score >= 7.0:
            balance_strengths.append("Dynamic pacing and rhythm")
        
        analysis_time = time.time() - analysis_start
        
        print(f"   📊 Content Ratio: {ratio_score:.1f}/10")
        print(f"   🔄 Transitions: {transition_score:.1f}/10")
        print(f"   🤝 Integration: {integration_score:.1f}/10")
        print(f"   ⚡ Pacing: {pacing_score:.1f}/10")
        print(f"   🏆 Overall Balance Score: {overall_score:.1f}/10")
        print(f"   📈 Distribution: {content_distribution} | Style: {transition_style} | Approach: {integration_approach}")
        
        return DialogueBalanceAnalysis(
            scene_title=scene.title,
            dialogue_song_ratio_score=ratio_score,
            transition_quality_score=transition_score,
            integration_effectiveness_score=integration_score,
            pacing_balance_score=pacing_score,
            overall_balance_score=overall_score,
            content_breakdown=percentages,
            transition_moments=transitions,
            integration_techniques=integration_techniques,
            pacing_elements=pacing_elements,
            balance_strengths=balance_strengths,
            content_distribution=content_distribution,
            transition_style=transition_style,
            integration_approach=integration_approach,
            pacing_pattern=pacing_pattern,
            analysis_time=analysis_time
        )

def run_dialogue_balance_analysis():
    """Run dialogue vs song balance analysis on all musicals"""
    
    print("🎭⚡ DIALOGUE VS SONG BALANCE ANALYSIS - FULL IMPULSE!")
    print("=" * 60)
    print("Analyzing structural composition and pacing balance")
    print("Components: Content Ratio, Transitions, Integration, Pacing\n")
    
    analyzer = DialogueBalanceAnalyzer()
    
    # Musical scenes for dialogue balance analysis
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
            print(f"🎪 BALANCE ANALYSIS {i}/6: {scene_info['musical']}")
            print("-" * 55)
            
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
            
            # Perform dialogue balance analysis
            analysis = analyzer.analyze_scene_dialogue_balance(scene)
            
            # Format result
            result = {
                "rank": i,
                "musical_name": scene_info['musical'],
                "genre": scene_info['genre'],
                "scene_title": analysis.scene_title,
                "balance_scores": {
                    "overall_balance_score": round(analysis.overall_balance_score, 2),
                    "dialogue_song_ratio_score": round(analysis.dialogue_song_ratio_score, 2),
                    "transition_quality_score": round(analysis.transition_quality_score, 2),
                    "integration_effectiveness_score": round(analysis.integration_effectiveness_score, 2),
                    "pacing_balance_score": round(analysis.pacing_balance_score, 2)
                },
                "balance_characteristics": {
                    "content_distribution": analysis.content_distribution,
                    "transition_style": analysis.transition_style,
                    "integration_approach": analysis.integration_approach,
                    "pacing_pattern": analysis.pacing_pattern
                },
                "content_breakdown": {
                    "dialogue_percent": round(analysis.content_breakdown.get("dialogue", 0), 1),
                    "song_percent": round(analysis.content_breakdown.get("song", 0), 1),
                    "stage_directions_percent": round(analysis.content_breakdown.get("stage_directions", 0), 1)
                },
                "balance_details": {
                    "transition_moments": analysis.transition_moments,
                    "integration_techniques": analysis.integration_techniques,
                    "pacing_elements": analysis.pacing_elements,
                    "balance_strengths": analysis.balance_strengths
                },
                "analysis_time": round(analysis.analysis_time, 2)
            }
            
            results.append(result)
            print()
            
        except Exception as e:
            print(f"❌ Error analyzing {scene_info['musical']}: {e}")
            continue
    
    total_time = time.time() - total_start
    
    # Sort by overall balance score
    results.sort(key=lambda x: x['balance_scores']['overall_balance_score'], reverse=True)
    
    # Update rankings
    for i, result in enumerate(results, 1):
        result['rank'] = i
    
    print("=" * 60)
    print("🏆 DIALOGUE VS SONG BALANCE RANKINGS")
    print("=" * 60)
    
    if results:
        # Calculate statistics
        balance_scores = [r['balance_scores']['overall_balance_score'] for r in results]
        collection_average = sum(balance_scores) / len(balance_scores)
        score_range = max(balance_scores) - min(balance_scores)
        
        print(f"Collection Average: {collection_average:.1f}/10.0")
        print(f"Score Range: {score_range:.1f} points")
        print(f"Analysis Time: {total_time:.1f} seconds")
        print(f"Musicals Analyzed: {len(results)}/6")
        print()
        
        # Component averages
        ratio_avg = sum(r['balance_scores']['dialogue_song_ratio_score'] for r in results) / len(results)
        transition_avg = sum(r['balance_scores']['transition_quality_score'] for r in results) / len(results)
        integration_avg = sum(r['balance_scores']['integration_effectiveness_score'] for r in results) / len(results)
        pacing_avg = sum(r['balance_scores']['pacing_balance_score'] for r in results) / len(results)
        
        print("📊 COMPONENT AVERAGES:")
        print(f"   Content Ratio: {ratio_avg:.1f}/10")
        print(f"   Transition Quality: {transition_avg:.1f}/10")
        print(f"   Integration Effectiveness: {integration_avg:.1f}/10")
        print(f"   Pacing Balance: {pacing_avg:.1f}/10")
        print()
        
        # Detailed rankings
        print("🎭 DETAILED BALANCE RANKINGS:")
        for result in results:
            scores = result['balance_scores']
            chars = result['balance_characteristics']
            breakdown = result['content_breakdown']
            print(f"{result['rank']}. {result['musical_name']}")
            print(f"   Overall: {scores['overall_balance_score']}/10 | Genre: {result['genre']}")
            print(f"   Ratio:{scores['dialogue_song_ratio_score']:.1f} Trans:{scores['transition_quality_score']:.1f} Integ:{scores['integration_effectiveness_score']:.1f} Pace:{scores['pacing_balance_score']:.1f}")
            print(f"   Content: {breakdown['dialogue_percent']:.0f}% dialogue, {breakdown['song_percent']:.0f}% song, {breakdown['stage_directions_percent']:.0f}% stage")
            print(f"   Style: {chars['transition_style']} | Approach: {chars['integration_approach']} | Pattern: {chars['pacing_pattern']}")
            print()
        
        # Balance pattern analysis
        print("⚖️ DIALOGUE-SONG BALANCE PATTERNS:")
        
        # Content distributions
        distribution_counts = {}
        for result in results:
            dist = result['balance_characteristics']['content_distribution']
            distribution_counts[dist] = distribution_counts.get(dist, 0) + 1
        
        print("   Content Distributions:")
        for dist, count in distribution_counts.items():
            print(f"     {dist}: {count} musicals")
        
        # Average content breakdown
        avg_dialogue = sum(r['content_breakdown']['dialogue_percent'] for r in results) / len(results)
        avg_song = sum(r['content_breakdown']['song_percent'] for r in results) / len(results)
        avg_stage = sum(r['content_breakdown']['stage_directions_percent'] for r in results) / len(results)
        
        print(f"   Collection Averages:")
        print(f"     Dialogue: {avg_dialogue:.1f}%")
        print(f"     Song: {avg_song:.1f}%")
        print(f"     Stage Directions: {avg_stage:.1f}%")
        
        # Save results
        output_data = {
            "analysis_metadata": {
                "analysis_type": "Dialogue vs Song Balance Analysis",
                "analysis_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_musicals": len(results),
                "collection_average": round(collection_average, 2),
                "score_range": round(score_range, 2),
                "analysis_time_seconds": round(total_time, 1),
                "component_averages": {
                    "dialogue_song_ratio": round(ratio_avg, 2),
                    "transition_quality": round(transition_avg, 2),
                    "integration_effectiveness": round(integration_avg, 2),
                    "pacing_balance": round(pacing_avg, 2)
                },
                "content_averages": {
                    "dialogue_percent": round(avg_dialogue, 1),
                    "song_percent": round(avg_song, 1),
                    "stage_directions_percent": round(avg_stage, 1)
                }
            },
            "balance_rankings": results,
            "distribution_patterns": distribution_counts
        }
        
        with open("DIALOGUE_balance_analysis.json", 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Balance analysis saved to: DIALOGUE_balance_analysis.json")
        print("🎭⚡ Dialogue vs Song Balance Analysis complete - FULL IMPULSE ACHIEVED!")
        
        return results
    
    else:
        print("❌ No analyses completed")
        return []

if __name__ == "__main__":
    print("🚀 Starting Dialogue vs Song Balance Analysis - FULL IMPULSE!")
    run_dialogue_balance_analysis()