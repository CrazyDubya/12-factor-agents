#!/usr/bin/env python3
"""
Emotional Journey Mapping - Advanced evaluation of emotional progression and audience connection
Analyzes emotional arc development, feeling transitions, cathartic moments, and audience engagement patterns
"""

import json
import re
import time
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
from main import SceneData

@dataclass
class EmotionalAnalysis:
    """Results of emotional journey mapping analysis"""
    scene_title: str
    emotional_arc_progression: float     # 0-10 - Development of emotional trajectory
    feeling_transition_quality: float   # 0-10 - Smoothness of emotional shifts
    cathartic_moment_power: float       # 0-10 - Strength of emotional peaks/releases
    audience_connection_potential: float # 0-10 - Relatability and engagement power
    overall_emotional_score: float      # 0-10 - Combined emotional effectiveness
    
    # Detailed emotional mapping
    emotions_identified: List[str]
    emotional_progression: List[str]
    transition_moments: List[str]
    cathartic_elements: List[str]
    connection_indicators: List[str]
    
    # Emotional characteristics
    dominant_emotion: str              # Primary emotion throughout scene
    emotional_range: str               # "Narrow", "Moderate", "Wide"
    journey_pattern: str               # "Rising", "Falling", "Complex", "Steady"
    cathartic_intensity: str           # "Subtle", "Moderate", "Intense"
    
    analysis_time: float

class EmotionalJourneyAnalyzer:
    """Specialized analyzer for emotional progression and audience connection"""
    
    def __init__(self):
        # Comprehensive emotional vocabulary mapping
        self.emotion_categories = {
            "joy": {
                "keywords": ["joy", "happy", "happiness", "delight", "elation", "euphoria", "bliss", "cheerful", 
                           "jubilant", "ecstatic", "gleeful", "merry", "bright", "sunny", "radiant", "beaming"],
                "intensity": {"high": ["ecstatic", "euphoria", "elation"], "medium": ["joy", "happy", "delight"], 
                            "low": ["cheerful", "pleasant", "content"]},
                "valence": 1.0
            },
            "sadness": {
                "keywords": ["sad", "sadness", "sorrow", "grief", "melancholy", "despair", "gloom", "dejected", 
                           "downcast", "sorrowful", "mournful", "blue", "heavy", "dark", "tears", "crying"],
                "intensity": {"high": ["despair", "grief", "anguish"], "medium": ["sadness", "sorrow"], 
                            "low": ["melancholy", "blue", "downcast"]},
                "valence": -1.0
            },
            "anger": {
                "keywords": ["anger", "angry", "rage", "fury", "wrath", "ire", "indignation", "outrage", "mad", 
                           "furious", "livid", "incensed", "irritated", "annoyed", "frustrated", "hostile"],
                "intensity": {"high": ["rage", "fury", "livid"], "medium": ["anger", "angry", "mad"], 
                            "low": ["annoyed", "irritated", "frustrated"]},
                "valence": -0.8
            },
            "fear": {
                "keywords": ["fear", "afraid", "scared", "terror", "horror", "dread", "anxiety", "panic", 
                           "frightened", "terrified", "alarmed", "worried", "nervous", "uneasy", "apprehensive"],
                "intensity": {"high": ["terror", "horror", "panic"], "medium": ["fear", "scared", "afraid"], 
                            "low": ["worried", "nervous", "uneasy"]},
                "valence": -0.9
            },
            "love": {
                "keywords": ["love", "adoration", "affection", "devotion", "passion", "romance", "tender", 
                           "caring", "cherish", "treasure", "beloved", "darling", "heart", "soul", "embrace"],
                "intensity": {"high": ["adoration", "passion", "devotion"], "medium": ["love", "affection"], 
                            "low": ["caring", "tender", "fond"]},
                "valence": 0.9
            },
            "hope": {
                "keywords": ["hope", "hopeful", "optimism", "faith", "trust", "belief", "confidence", "aspiration", 
                           "dream", "wish", "desire", "yearning", "longing", "anticipation", "expectation"],
                "intensity": {"high": ["faith", "confidence", "aspiration"], "medium": ["hope", "optimism"], 
                            "low": ["wish", "desire", "yearning"]},
                "valence": 0.7
            },
            "wonder": {
                "keywords": ["wonder", "awe", "amazement", "astonishment", "marvel", "magic", "mystical", 
                           "enchanted", "fascinated", "curious", "intrigued", "captivated", "spellbound"],
                "intensity": {"high": ["awe", "astonishment", "spellbound"], "medium": ["wonder", "amazement"], 
                            "low": ["curious", "intrigued", "fascinated"]},
                "valence": 0.6
            },
            "peace": {
                "keywords": ["peace", "calm", "serene", "tranquil", "peaceful", "quiet", "still", "gentle", 
                           "soothing", "restful", "harmonious", "balanced", "centered", "grounded"],
                "intensity": {"high": ["serene", "tranquil"], "medium": ["peace", "calm"], 
                            "low": ["quiet", "gentle", "still"]},
                "valence": 0.5
            },
            "excitement": {
                "keywords": ["excitement", "excited", "thrilled", "exhilarated", "energized", "animated", 
                           "enthusiastic", "eager", "anticipation", "rush", "adrenaline", "electric", "vibrant"],
                "intensity": {"high": ["thrilled", "exhilarated", "electric"], "medium": ["excited", "enthusiastic"], 
                            "low": ["eager", "animated", "interested"]},
                "valence": 0.8
            },
            "confusion": {
                "keywords": ["confusion", "confused", "bewildered", "perplexed", "puzzled", "lost", "uncertain", 
                           "unclear", "mixed up", "disoriented", "baffled", "mystified", "questioning"],
                "intensity": {"high": ["bewildered", "baffled"], "medium": ["confused", "perplexed"], 
                            "low": ["uncertain", "puzzled", "questioning"]},
                "valence": -0.3
            }
        }
        
        # Emotional transition patterns
        self.transition_patterns = [
            # Common emotional arcs
            r'\b(?:from|was)\s+(\w+)\s+(?:to|but now|became|turned)\s+(\w+)\b',
            r'\b(?:started|began)\s+(\w+).*(?:ended|finished|became)\s+(\w+)\b',
            r'\b(?:once|before)\s.*(\w+).*(?:now|today|currently)\s.*(\w+)\b',
            
            # Emotional progression indicators
            r'\b(?:gradually|slowly|suddenly|quickly)\s+(?:became|turned|grew|felt)\s+(\w+)\b',
            r'\b(?:more and more|increasingly|progressively)\s+(\w+)\b',
            r'\b(?:overwhelming|building|rising|growing)\s+(\w+)\b'
        ]
        
        # Cathartic moment indicators
        self.cathartic_patterns = [
            # Release and breakthrough moments
            r'\b(?:breakthrough|revelation|epiphany|realization|awakening)\b',
            r'\b(?:release|let go|freed|liberated|unburdened)\b',
            r'\b(?:climax|peak|pinnacle|crescendo|height)\b',
            r'\b(?:transformation|metamorphosis|change|shift)\b',
            
            # Emotional intensity peaks
            r'\b(?:overwhelming|overpowering|all-consuming|intense)\b',  
            r'\b(?:exploded|erupted|burst|flooded|rushed)\b',
            r'\b(?:tears|crying|sobbing|weeping|laughter|laughing)\b',
            r'\b(?:screamed|shouted|whispered|gasped|sighed)\b'
        ]
        
        # Audience connection indicators
        self.connection_patterns = [
            # Universal experiences
            r'\b(?:everyone|we all|human|universal|shared)\b',
            r'\b(?:remember|recall|familiar|recognize|relate)\b',
            r'\b(?:family|friends|relationships|community)\b',
            
            # Relatable situations
            r'\b(?:work|job|school|home|childhood|growing up)\b',
            r'\b(?:struggle|challenge|difficulty|problem|issue)\b',
            r'\b(?:dream|goal|ambition|hope|wish|desire)\b',
            
            # Direct audience address
            r'\b(?:you|your|ourselves|together|us|we)\b'
        ]
    
    def extract_emotional_content(self, scene: SceneData) -> Dict[str, List[str]]:
        """Extract emotional language and expressions from scene content"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes} {scene.description}".lower()
        
        emotional_content = {
            "emotions": [],
            "intensifiers": [],
            "expressions": [],
            "physical_manifestations": []
        }
        
        # Extract emotional words and phrases
        words = re.findall(r'\b\w+\b', all_text)
        phrases = re.findall(r'\b\w+(?:\s+\w+){1,3}\b', all_text)
        
        # Collect emotional vocabulary
        for word in words:
            for emotion_category, data in self.emotion_categories.items():
                if word in data["keywords"]:
                    emotional_content["emotions"].append(f"{emotion_category}: {word}")
        
        # Extract intensifiers
        intensifiers = ["very", "extremely", "incredibly", "deeply", "profoundly", "utterly", "completely", 
                       "absolutely", "entirely", "totally", "overwhelmingly", "intensely"]
        for intensifier in intensifiers:
            if intensifier in all_text:
                emotional_content["intensifiers"].append(intensifier)
        
        # Extract emotional expressions
        expression_patterns = [
            r'\bheart\s+(?:breaks|soars|pounds|aches|sings)\b',
            r'\bsoul\s+(?:cries|rejoices|yearns|aches|sings)\b',
            r'\beyes\s+(?:sparkle|tear up|light up|dim|brighten)\b',
            r'\bvoice\s+(?:trembles|soars|breaks|cracks|lifts)\b'
        ]
        
        for pattern in expression_patterns:
            matches = re.findall(pattern, all_text)
            emotional_content["expressions"].extend(matches)
        
        return emotional_content
    
    def analyze_emotional_arc_progression(self, scene: SceneData) -> Tuple[float, List[str]]:
        """Analyze the development and progression of emotional trajectory"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes} {scene.description}".lower()
        
        progression_elements = []
        progression_score = 0.0
        
        # Identify emotional words throughout the text
        emotion_timeline = []
        text_segments = all_text.split('\n')
        
        for i, segment in enumerate(text_segments):
            segment_emotions = []
            for emotion_category, data in self.emotion_categories.items():
                for keyword in data["keywords"]:
                    if keyword in segment:
                        segment_emotions.append((emotion_category, data["valence"]))
            
            if segment_emotions:
                emotion_timeline.append((i, segment_emotions))
        
        # Analyze progression patterns
        if len(emotion_timeline) >= 2:
            # Calculate emotional trajectory
            valences = []
            for _, emotions in emotion_timeline:
                avg_valence = sum(valence for _, valence in emotions) / len(emotions)
                valences.append(avg_valence)
            
            # Score based on progression complexity and development
            if len(valences) >= 3:
                # Check for emotional development (change over time)
                valence_range = max(valences) - min(valences)
                if valence_range > 0.5:  # Significant emotional range
                    progression_score += 3.0
                    progression_elements.append(f"Significant emotional range: {valence_range:.1f}")
                
                # Check for clear progression (not just random changes)
                changes = [valences[i+1] - valences[i] for i in range(len(valences)-1)]
                consistent_direction = sum(1 for change in changes if abs(change) > 0.2)
                if consistent_direction >= len(changes) * 0.6:  # 60% of changes in clear direction
                    progression_score += 2.5
                    progression_elements.append(f"Clear emotional direction: {consistent_direction}/{len(changes)} changes")
        
        # Look for explicit progression indicators
        progression_indicators = [
            r'\b(?:beginning|start|first|initially)\b.*(?:end|final|last|eventually)\b',
            r'\b(?:journey|path|arc|progression|development)\b',
            r'\b(?:grows|develops|evolves|transforms|changes)\b',
            r'\b(?:step by step|gradually|slowly|over time)\b'
        ]
        
        for pattern in progression_indicators:
            matches = len(re.findall(pattern, all_text))
            if matches > 0:
                progression_score += matches * 1.0
                progression_elements.append(f"Progression indicator: {pattern}")
        
        # Check for emotional complexity (multiple emotions present)
        unique_emotions = set()
        for emotion_category, data in self.emotion_categories.items():
            for keyword in data["keywords"]:
                if keyword in all_text:
                    unique_emotions.add(emotion_category)
        
        if len(unique_emotions) >= 3:
            progression_score += 2.0
            progression_elements.append(f"Emotional complexity: {len(unique_emotions)} emotion types")
        
        final_score = min(10.0, progression_score)
        
        return final_score, progression_elements[:5]
    
    def analyze_feeling_transition_quality(self, scene: SceneData) -> Tuple[float, List[str]]:
        """Analyze the smoothness and effectiveness of emotional transitions"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes} {scene.description}".lower()
        
        transition_moments = []
        transition_score = 0.0
        
        # Look for explicit transition patterns
        for pattern in self.transition_patterns:
            matches = re.finditer(pattern, all_text)
            for match in matches:
                # Get context around the transition
                start = max(0, match.start() - 30)
                end = min(len(all_text), match.end() + 30)
                context = all_text[start:end].strip()
                transition_moments.append(f"Emotional transition: {context}")
                transition_score += 1.5
        
        # Look for transition facilitators (words that help smooth emotional changes)
        transition_facilitators = [
            r'\b(?:but|however|yet|still|though|although)\b',  # Contrast transitions
            r'\b(?:suddenly|gradually|slowly|quickly|immediately)\b',  # Temporal transitions
            r'\b(?:because|since|as|when|while|after|before)\b',  # Causal transitions
            r'\b(?:meanwhile|during|at the same time)\b'  # Parallel transitions
        ]
        
        facilitator_count = 0
        for pattern in transition_facilitators:
            matches = len(re.findall(pattern, all_text))
            facilitator_count += matches
        
        if facilitator_count > 0:
            transition_score += min(3.0, facilitator_count * 0.3)
            transition_moments.append(f"Transition facilitators: {facilitator_count}")
        
        # Analyze emotional bridges (elements that connect different emotional states)
        bridge_patterns = [
            r'\b(?:memory|remember|flashback|recall)\b',  # Memory bridges
            r'\b(?:music|song|melody|rhythm)\b',  # Musical bridges
            r'\b(?:image|vision|dream|imagine)\b',  # Imagery bridges
            r'\b(?:metaphor|like|as if|resembles)\b'  # Metaphorical bridges
        ]
        
        bridge_count = 0
        for pattern in bridge_patterns:
            matches = len(re.findall(pattern, all_text))
            bridge_count += matches
        
        if bridge_count > 0:
            transition_score += min(2.5, bridge_count * 0.4)
            transition_moments.append(f"Emotional bridges: {bridge_count}")
        
        # Look for smooth vs. jarring transitions
        # Smooth transitions often have preparation or building
        smooth_indicators = [
            r'\b(?:building|growing|rising|swelling)\b',
            r'\b(?:preparing|leading|moving toward)\b',
            r'\b(?:gentle|soft|tender|gradual)\b'
        ]
        
        smooth_count = sum(len(re.findall(pattern, all_text)) for pattern in smooth_indicators)
        if smooth_count > 0:
            transition_score += min(2.0, smooth_count * 0.5)
            transition_moments.append(f"Smooth transition indicators: {smooth_count}")
        
        final_score = min(10.0, transition_score)
        
        return final_score, transition_moments[:5]
    
    def analyze_cathartic_moments(self, scene: SceneData) -> Tuple[float, List[str]]:
        """Analyze the power and effectiveness of cathartic moments"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes} {scene.description}".lower()
        
        cathartic_elements = []
        cathartic_score = 0.0
        
        # Look for cathartic moment indicators
        for pattern in self.cathartic_patterns:
            matches = re.finditer(pattern, all_text)
            for match in matches:
                # Get context
                start = max(0, match.start() - 25)
                end = min(len(all_text), match.end() + 25)
                context = all_text[start:end].strip()
                cathartic_elements.append(f"Cathartic moment: {context}")
                cathartic_score += 1.2
        
        # Look for emotional intensity peaks
        intensity_indicators = [
            r'\b(?:overwhelming|overpowering|all-consuming|intense|powerful)\b',
            r'\b(?:exploded|erupted|burst|flooded|rushed|surged)\b',
            r'\b(?:climax|peak|pinnacle|crescendo|height|summit)\b'
        ]
        
        intensity_count = 0
        for pattern in intensity_indicators:
            matches = len(re.findall(pattern, all_text))
            intensity_count += matches
        
        if intensity_count > 0:
            cathartic_score += min(3.0, intensity_count * 0.8)
            cathartic_elements.append(f"Intensity peaks: {intensity_count}")
        
        # Look for release and resolution indicators
        release_patterns = [
            r'\b(?:release|let go|freed|liberated|unburdened|relief)\b',
            r'\b(?:peace|calm|resolution|closure|completion)\b',
            r'\b(?:understanding|clarity|realization|truth|answer)\b'
        ]
        
        release_count = 0
        for pattern in release_patterns:
            matches = len(re.findall(pattern, all_text))
            release_count += matches
        
        if release_count > 0:
            cathartic_score += min(2.5, release_count * 0.6)
            cathartic_elements.append(f"Release indicators: {release_count}")
        
        # Physical manifestations of catharsis
        physical_patterns = [
            r'\b(?:tears|crying|sobbing|weeping)\b',
            r'\b(?:laughter|laughing|joy|celebration)\b',
            r'\b(?:screamed|shouted|called out|cried out)\b',
            r'\b(?:collapsed|fell|embraced|reached out)\b'
        ]
        
        physical_count = 0
        for pattern in physical_patterns:
            matches = len(re.findall(pattern, all_text))
            physical_count += matches
        
        if physical_count > 0:
            cathartic_score += min(2.0, physical_count * 0.7)
            cathartic_elements.append(f"Physical manifestations: {physical_count}")
        
        # Musical/theatrical catharsis
        theatrical_catharsis = [
            r'\b(?:crescendo|fortissimo|diminuendo)\b',
            r'\b(?:solo|ensemble|chorus|harmony)\b',
            r'\b(?:spotlight|stage|audience|applause)\b'
        ]
        
        theatrical_count = sum(len(re.findall(pattern, all_text)) for pattern in theatrical_catharsis)
        if theatrical_count > 0:
            cathartic_score += min(1.5, theatrical_count * 0.4)
            cathartic_elements.append(f"Theatrical catharsis: {theatrical_count}")
        
        final_score = min(10.0, cathartic_score)
        
        return final_score, cathartic_elements[:5]
    
    def analyze_audience_connection(self, scene: SceneData) -> Tuple[float, List[str]]:
        """Analyze the potential for audience connection and relatability"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes} {scene.description}".lower()
        
        connection_indicators = []
        connection_score = 0.0
        
        # Universal human experiences
        universal_themes = [
            (r'\b(?:love|family|friendship|relationships)\b', "Relationships", 1.5),
            (r'\b(?:loss|death|grief|goodbye|farewell)\b', "Loss and grief", 1.4),
            (r'\b(?:hope|dream|aspiration|future|tomorrow)\b', "Hope and dreams", 1.3),
            (r'\b(?:fear|worry|anxiety|concern|doubt)\b', "Fear and anxiety", 1.2),
            (r'\b(?:childhood|growing up|youth|memories)\b', "Growing up", 1.1),
            (r'\b(?:work|job|career|success|failure)\b', "Work and achievement", 1.0),
            (r'\b(?:home|belonging|place|identity)\b', "Identity and belonging", 1.2)
        ]
        
        for pattern, theme, weight in universal_themes:
            matches = len(re.findall(pattern, all_text))
            if matches > 0:
                connection_score += matches * weight
                connection_indicators.append(f"{theme}: {matches} references")
        
        # Direct audience engagement
        for pattern in self.connection_patterns:
            matches = len(re.findall(pattern, all_text))
            if matches > 0:
                connection_score += matches * 0.6
        
        # Relatability factors
        relatable_situations = [
            r'\b(?:struggle|challenge|difficulty|obstacle|problem)\b',
            r'\b(?:celebration|achievement|success|victory|triumph)\b',
            r'\b(?:mistake|failure|regret|lesson learned)\b',
            r'\b(?:change|transformation|growth|learning)\b'
        ]
        
        relatable_count = 0
        for pattern in relatable_situations:
            matches = len(re.findall(pattern, all_text))
            relatable_count += matches
        
        if relatable_count > 0:
            connection_score += min(3.0, relatable_count * 0.4)
            connection_indicators.append(f"Relatable situations: {relatable_count}")
        
        # Emotional accessibility (simple, clear emotional expression)
        simple_emotions = ["happy", "sad", "angry", "scared", "excited", "worried", "proud", "ashamed"]
        simple_emotion_count = sum(1 for emotion in simple_emotions if emotion in all_text)
        
        if simple_emotion_count > 0:
            connection_score += min(2.0, simple_emotion_count * 0.3)
            connection_indicators.append(f"Accessible emotions: {simple_emotion_count}")
        
        # Sensory and physical connection
        sensory_patterns = [
            r'\b(?:see|look|watch|sight|visual|eyes)\b',
            r'\b(?:hear|listen|sound|music|voice|silence)\b',
            r'\b(?:feel|touch|warm|cold|soft|hard)\b',
            r'\b(?:taste|sweet|bitter|flavor)\b',
            r'\b(?:smell|scent|fragrance|aroma)\b'
        ]
        
        sensory_count = sum(len(re.findall(pattern, all_text)) for pattern in sensory_patterns)
        if sensory_count > 3:  # Only count if there's significant sensory content
            connection_score += min(2.0, (sensory_count - 3) * 0.2)
            connection_indicators.append(f"Sensory connection: {sensory_count} sensory references")
        
        final_score = min(10.0, connection_score)
        
        return final_score, connection_indicators[:5]
    
    def identify_dominant_emotion(self, scene: SceneData) -> str:
        """Identify the primary emotion throughout the scene"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes} {scene.description}".lower()
        
        emotion_counts = {}
        for emotion_category, data in self.emotion_categories.items():
            count = sum(1 for keyword in data["keywords"] if keyword in all_text)
            if count > 0:
                emotion_counts[emotion_category] = count
        
        if emotion_counts:
            return max(emotion_counts, key=emotion_counts.get)
        else:
            return "neutral"
    
    def determine_emotional_range(self, scene: SceneData) -> str:
        """Determine the breadth of emotional range in the scene"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes} {scene.description}".lower()
        
        emotions_present = set()
        for emotion_category, data in self.emotion_categories.items():
            for keyword in data["keywords"]:
                if keyword in all_text:
                    emotions_present.add(emotion_category)
        
        emotion_count = len(emotions_present)
        if emotion_count >= 5:
            return "Wide"
        elif emotion_count >= 3:
            return "Moderate"
        else:
            return "Narrow"
    
    def determine_journey_pattern(self, scene: SceneData) -> str:
        """Determine the overall pattern of the emotional journey"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes} {scene.description}".lower()
        
        # Look for pattern indicators
        if re.search(r'\b(?:builds|building|rising|growing|ascending|climbing)\b', all_text):
            return "Rising"
        elif re.search(r'\b(?:falls|falling|declining|descending|diminishing)\b', all_text):
            return "Falling"
        elif re.search(r'\b(?:complex|varied|changing|shifting|dynamic)\b', all_text):
            return "Complex"
        else:
            return "Steady"
    
    def determine_cathartic_intensity(self, cathartic_score: float) -> str:
        """Determine the intensity level of cathartic moments"""
        if cathartic_score >= 7.0:
            return "Intense"
        elif cathartic_score >= 4.0:
            return "Moderate"
        else:
            return "Subtle"
    
    def analyze_scene_emotions(self, scene: SceneData) -> EmotionalAnalysis:
        """Perform comprehensive emotional journey analysis on a scene"""
        analysis_start = time.time()
        
        print(f"💖 Analyzing emotional journey for: {scene.title}")
        
        # Extract emotional content
        emotional_content = self.extract_emotional_content(scene)
        print(f"   🎭 Found {len(emotional_content['emotions'])} emotional elements")
        
        # Perform component analyses
        arc_score, progression = self.analyze_emotional_arc_progression(scene)
        transition_score, transitions = self.analyze_feeling_transition_quality(scene)
        cathartic_score, cathartic_elements = self.analyze_cathartic_moments(scene)
        connection_score, connections = self.analyze_audience_connection(scene)
        
        # Determine emotional characteristics
        dominant_emotion = self.identify_dominant_emotion(scene)
        emotional_range = self.determine_emotional_range(scene)
        journey_pattern = self.determine_journey_pattern(scene)
        cathartic_intensity = self.determine_cathartic_intensity(cathartic_score)
        
        # Calculate overall emotional score
        overall_score = (arc_score + transition_score + cathartic_score + connection_score) / 4
        
        analysis_time = time.time() - analysis_start
        
        print(f"   📈 Arc Progression: {arc_score:.1f}/10")
        print(f"   🔄 Transitions: {transition_score:.1f}/10")
        print(f"   ⭐ Cathartic Power: {cathartic_score:.1f}/10")
        print(f"   🤝 Connection: {connection_score:.1f}/10")
        print(f"   🏆 Overall Emotional Score: {overall_score:.1f}/10")
        print(f"   🎪 Dominant: {dominant_emotion.title()} | Range: {emotional_range} | Pattern: {journey_pattern}")
        
        return EmotionalAnalysis(
            scene_title=scene.title,
            emotional_arc_progression=arc_score,
            feeling_transition_quality=transition_score,
            cathartic_moment_power=cathartic_score,
            audience_connection_potential=connection_score,
            overall_emotional_score=overall_score,
            emotions_identified=[e.split(': ')[1] for e in emotional_content['emotions'][:10]],
            emotional_progression=progression,
            transition_moments=transitions,
            cathartic_elements=cathartic_elements,
            connection_indicators=connections,
            dominant_emotion=dominant_emotion,
            emotional_range=emotional_range,
            journey_pattern=journey_pattern,
            cathartic_intensity=cathartic_intensity,
            analysis_time=analysis_time
        )

def run_emotional_journey_analysis():
    """Run emotional journey analysis on all musicals"""
    
    print("🎭💖 EMOTIONAL JOURNEY MAPPING - MAKE IT SO!")
    print("=" * 55)
    print("Analyzing emotional progression and audience connection")
    print("Components: Arc Progression, Transitions, Catharsis, Connection\n")
    
    analyzer = EmotionalJourneyAnalyzer()
    
    # Musical scenes for emotional analysis
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
            print(f"🎪 EMOTIONAL ANALYSIS {i}/6: {scene_info['musical']}")
            print("-" * 50)
            
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
            
            # Perform emotional analysis
            analysis = analyzer.analyze_scene_emotions(scene)
            
            # Format result
            result = {
                "rank": i,
                "musical_name": scene_info['musical'],
                "genre": scene_info['genre'],
                "scene_title": analysis.scene_title,
                "emotional_scores": {
                    "overall_emotional_score": round(analysis.overall_emotional_score, 2),
                    "emotional_arc_progression": round(analysis.emotional_arc_progression, 2),
                    "feeling_transition_quality": round(analysis.feeling_transition_quality, 2),
                    "cathartic_moment_power": round(analysis.cathartic_moment_power, 2),
                    "audience_connection_potential": round(analysis.audience_connection_potential, 2)
                },
                "emotional_characteristics": {
                    "dominant_emotion": analysis.dominant_emotion,
                    "emotional_range": analysis.emotional_range,
                    "journey_pattern": analysis.journey_pattern,
                    "cathartic_intensity": analysis.cathartic_intensity
                },
                "emotional_details": {
                    "emotions_identified": analysis.emotions_identified,
                    "emotional_progression": analysis.emotional_progression,
                    "transition_moments": analysis.transition_moments,
                    "cathartic_elements": analysis.cathartic_elements,
                    "connection_indicators": analysis.connection_indicators
                },
                "analysis_time": round(analysis.analysis_time, 2)
            }
            
            results.append(result)
            print()
            
        except Exception as e:
            print(f"❌ Error analyzing {scene_info['musical']}: {e}")
            continue
    
    total_time = time.time() - total_start
    
    # Sort by overall emotional score
    results.sort(key=lambda x: x['emotional_scores']['overall_emotional_score'], reverse=True)
    
    # Update rankings
    for i, result in enumerate(results, 1):
        result['rank'] = i
    
    print("=" * 55)
    print("🏆 EMOTIONAL JOURNEY ANALYSIS RANKINGS")
    print("=" * 55)
    
    if results:
        # Calculate statistics
        emotional_scores = [r['emotional_scores']['overall_emotional_score'] for r in results]
        collection_average = sum(emotional_scores) / len(emotional_scores)
        score_range = max(emotional_scores) - min(emotional_scores)
        
        print(f"Collection Average: {collection_average:.1f}/10.0")
        print(f"Score Range: {score_range:.1f} points")
        print(f"Analysis Time: {total_time:.1f} seconds")
        print(f"Musicals Analyzed: {len(results)}/6")
        print()
        
        # Component averages
        arc_avg = sum(r['emotional_scores']['emotional_arc_progression'] for r in results) / len(results)
        trans_avg = sum(r['emotional_scores']['feeling_transition_quality'] for r in results) / len(results)
        cath_avg = sum(r['emotional_scores']['cathartic_moment_power'] for r in results) / len(results)
        conn_avg = sum(r['emotional_scores']['audience_connection_potential'] for r in results) / len(results)
        
        print("📊 COMPONENT AVERAGES:")
        print(f"   Emotional Arc Progression: {arc_avg:.1f}/10")
        print(f"   Feeling Transition Quality: {trans_avg:.1f}/10")
        print(f"   Cathartic Moment Power: {cath_avg:.1f}/10")
        print(f"   Audience Connection: {conn_avg:.1f}/10")
        print()
        
        # Detailed rankings
        print("🎭 DETAILED EMOTIONAL RANKINGS:")
        for result in results:
            scores = result['emotional_scores']
            chars = result['emotional_characteristics']
            print(f"{result['rank']}. {result['musical_name']}")
            print(f"   Overall: {scores['overall_emotional_score']}/10 | Genre: {result['genre']}")
            print(f"   Arc:{scores['emotional_arc_progression']:.1f} Trans:{scores['feeling_transition_quality']:.1f} Cath:{scores['cathartic_moment_power']:.1f} Conn:{scores['audience_connection_potential']:.1f}")
            print(f"   Emotion: {chars['dominant_emotion'].title()} | Range: {chars['emotional_range']} | Pattern: {chars['journey_pattern']}")
            
            if result['emotional_details']['connection_indicators']:
                print(f"   Connection: {result['emotional_details']['connection_indicators'][0]}")
            print()
        
        # Emotional pattern analysis
        print("💖 EMOTIONAL PATTERN ANALYSIS:")
        
        # Dominant emotions
        emotion_counts = {}
        for result in results:
            emotion = result['emotional_characteristics']['dominant_emotion']
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        print("   Dominant Emotions:")
        for emotion, count in emotion_counts.items():
            print(f"     {emotion.title()}: {count} musicals")
        
        # Emotional ranges
        range_counts = {}
        for result in results:
            range_type = result['emotional_characteristics']['emotional_range']
            range_counts[range_type] = range_counts.get(range_type, 0) + 1
        
        print("   Emotional Ranges:")
        for range_type, count in range_counts.items():
            print(f"     {range_type}: {count} musicals")
        
        # Journey patterns
        pattern_counts = {}
        for result in results:
            pattern = result['emotional_characteristics']['journey_pattern']
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
        
        print("   Journey Patterns:")
        for pattern, count in pattern_counts.items():
            print(f"     {pattern}: {count} musicals")
        
        # Save results
        output_data = {
            "analysis_metadata": {
                "analysis_type": "Emotional Journey Mapping",
                "analysis_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_musicals": len(results),
                "collection_average": round(collection_average, 2),
                "score_range": round(score_range, 2),
                "analysis_time_seconds": round(total_time, 1),
                "component_averages": {
                    "emotional_arc_progression": round(arc_avg, 2),
                    "feeling_transition_quality": round(trans_avg, 2),
                    "cathartic_moment_power": round(cath_avg, 2),
                    "audience_connection_potential": round(conn_avg, 2)
                }
            },
            "emotional_rankings": results,
            "emotional_patterns": {
                "dominant_emotions": emotion_counts,
                "emotional_ranges": range_counts,
                "journey_patterns": pattern_counts
            }
        }
        
        with open("EMOTIONAL_journey_analysis.json", 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Emotional analysis saved to: EMOTIONAL_journey_analysis.json")
        print("💖 Emotional Journey Mapping complete - MADE IT SO!")
        
        return results
    
    else:
        print("❌ No analyses completed")
        return []

if __name__ == "__main__":
    print("🚀 Starting Emotional Journey Mapping - MAKE IT SO!")
    run_emotional_journey_analysis()