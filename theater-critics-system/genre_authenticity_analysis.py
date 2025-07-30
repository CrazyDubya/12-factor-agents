#!/usr/bin/env python3
"""
Genre Authenticity & Innovation Assessment
Evaluates how well musicals represent their genres while introducing creative innovations
"""

import json
import re
import time
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
from main import SceneData

@dataclass
class GenreAnalysis:
    """Results of genre authenticity and innovation analysis"""
    scene_title: str
    genre_authenticity_score: float     # 0-10 - How well it fits genre conventions
    innovation_creativity_score: float  # 0-10 - Creative departures and innovations
    genre_convention_adherence: float   # 0-10 - Adherence to expected elements
    creative_risk_taking_score: float   # 0-10 - Bold creative choices
    overall_genre_score: float          # 0-10 - Combined assessment
    
    # Detailed analysis
    genre: str
    authentic_elements: List[str]
    innovative_elements: List[str]
    genre_conventions_met: List[str]
    creative_risks_identified: List[str]
    cross_genre_influences: List[str]
    
    # Quality assessment
    authenticity_level: str       # "Traditional", "Contemporary", "Experimental"
    innovation_level: str         # "Conservative", "Moderate", "Groundbreaking"
    genre_balance: str           # "Pure Genre", "Genre Blend", "Genre Fusion"
    
    analysis_time: float

class GenreAuthenticityAnalyzer:
    """Specialized analyzer for genre authenticity and innovation"""
    
    def __init__(self):
        # Define genre conventions and expectations
        self.genre_conventions = {
            "Sci-Fi Drama": {
                "themes": ["technology", "future", "artificial", "digital", "consciousness", "memory", "evolution", "progress"],
                "settings": ["laboratory", "space", "future", "virtual", "digital", "cybernetic", "robotic", "scientific"],
                "vocabulary": ["neural", "synthetic", "data", "algorithm", "protocol", "system", "interface", "quantum"],
                "conflicts": ["human vs machine", "ethics", "identity", "consciousness", "reality vs virtual"],
                "innovations": ["new tech concepts", "philosophical depth", "human-AI relationships", "digital consciousness"]
            },
            "Techno-Romance": {
                "themes": ["love", "desire", "technology", "connection", "digital romance", "virtual reality", "cyber love"],
                "settings": ["digital world", "virtual space", "cybernetic", "online", "networked", "electronic"],
                "vocabulary": ["electric", "digital", "virtual", "cyber", "electronic", "networked", "synthetic", "coded"],
                "conflicts": ["real vs virtual love", "human vs digital", "connection vs isolation", "authentic vs artificial"],
                "innovations": ["digital love stories", "VR romance", "AI relationships", "cyber intimacy"]
            },
            "Murder Mystery": {
                "themes": ["murder", "mystery", "secrets", "investigation", "truth", "deception", "suspicion", "revelation"],
                "settings": ["theater", "backstage", "crime scene", "investigation room", "dark corners", "hidden spaces"],
                "vocabulary": ["clues", "suspects", "evidence", "alibi", "motive", "investigation", "reveal", "confession"],
                "conflicts": ["detective vs criminal", "truth vs lies", "justice vs corruption", "past vs present"],
                "innovations": ["musical investigation", "sung confessions", "theatrical meta-mystery", "ensemble suspicion"]
            },
            "Contemporary Drama": {
                "themes": ["relationships", "personal struggle", "identity", "society", "modern life", "social issues"],
                "settings": ["urban", "contemporary", "realistic", "everyday", "workplace", "home", "social spaces"],
                "vocabulary": ["real", "authentic", "personal", "emotional", "relationship", "struggle", "identity"],
                "conflicts": ["personal vs social", "individual vs system", "past vs future", "dreams vs reality"],
                "innovations": ["modern storytelling", "current issues", "realistic characters", "social commentary"]
            },
            "Dystopian Action": {
                "themes": ["oppression", "rebellion", "freedom", "control", "resistance", "dystopia", "totalitarian", "fight"],
                "settings": ["oppressive society", "controlled environment", "underground", "resistance hideout", "surveillance state"],
                "vocabulary": ["rebellion", "resistance", "freedom", "oppression", "control", "surveillance", "totalitarian", "fight"],
                "conflicts": ["individual vs system", "freedom vs control", "rebellion vs oppression", "hope vs despair"],
                "innovations": ["musical rebellion", "sung resistance", "choreographed fights", "dystopian world-building"]
            },
            "Fantasy Musical Theater": {
                "themes": ["magic", "adventure", "friendship", "growth", "wonder", "fantastical", "mythical", "heroic"],
                "settings": ["magical world", "academy", "enchanted", "fantastical", "mystical", "otherworldly"],
                "vocabulary": ["magic", "spell", "enchanted", "mystical", "wonder", "adventure", "quest", "magical"],
                "conflicts": ["good vs evil", "learning vs ignorance", "friendship vs rivalry", "growth vs stagnation"],
                "innovations": ["magical elements in song", "fantastical choreography", "creative world-building", "magic systems"]
            }
        }
        
        # Innovation indicators across all genres
        self.innovation_patterns = [
            # Structural innovations
            r'\b(?:meta|fourth wall|audience|breaking|unconventional)\b',
            r'\b(?:experimental|avant-garde|groundbreaking|revolutionary)\b',
            r'\b(?:fusion|blend|cross-genre|hybrid|mixing)\b',
            
            # Creative risks
            r'\b(?:risky|bold|daring|unprecedented|unorthodox)\b',
            r'\b(?:challenging|provocative|controversial|boundary-pushing)\b',
            r'\b(?:innovative|creative|original|unique|distinctive)\b',
            
            # Cross-genre elements
            r'\b(?:comedy|drama|thriller|romance|action|fantasy|sci-fi)\b',
            r'\b(?:jazz|rock|pop|classical|electronic|hip-hop|folk)\b'
        ]
    
    def extract_content_elements(self, scene: SceneData) -> Dict[str, List[str]]:
        """Extract thematic, setting, vocabulary, and conflict elements from scene"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes} {scene.description}".lower()
        
        elements = {
            "themes": [],
            "settings": [],
            "vocabulary": [],
            "conflicts": []
        }
        
        # Extract words and phrases that might indicate genre elements
        words = re.findall(r'\b\w+\b', all_text)
        phrases = re.findall(r'\b\w+\s+\w+\b', all_text)
        
        # Collect all potential elements
        all_content = words + phrases
        
        return {
            "themes": [word for word in all_content if len(word) > 3],
            "settings": [word for word in all_content if len(word) > 4],
            "vocabulary": [word for word in all_content if len(word) > 4],
            "conflicts": [phrase for phrase in phrases if 'vs' in phrase or 'against' in phrase]
        }
    
    def analyze_genre_authenticity(self, scene: SceneData, genre: str) -> Tuple[float, List[str]]:
        """Analyze how authentically the scene represents its genre"""
        if genre not in self.genre_conventions:
            return 5.0, [f"Unknown genre: {genre}"]
        
        conventions = self.genre_conventions[genre]
        content_elements = self.extract_content_elements(scene)
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes} {scene.description}".lower()
        
        authentic_elements = []
        authenticity_score = 0.0
        
        # Check for genre-specific themes
        theme_matches = 0
        for theme in conventions["themes"]:
            if theme.lower() in all_text:
                theme_matches += 1
                authentic_elements.append(f"Theme: {theme}")
        
        if theme_matches > 0:
            authenticity_score += min(3.0, theme_matches * 0.5)
        
        # Check for genre-specific settings
        setting_matches = 0
        for setting in conventions["settings"]:
            if setting.lower() in all_text:
                setting_matches += 1
                authentic_elements.append(f"Setting: {setting}")
        
        if setting_matches > 0:
            authenticity_score += min(2.5, setting_matches * 0.4)
        
        # Check for genre-specific vocabulary
        vocab_matches = 0
        for vocab_word in conventions["vocabulary"]:
            if vocab_word.lower() in all_text:
                vocab_matches += 1
                authentic_elements.append(f"Vocabulary: {vocab_word}")
        
        if vocab_matches > 0:
            authenticity_score += min(2.5, vocab_matches * 0.3)
        
        # Check for genre-specific conflicts
        conflict_matches = 0
        for conflict in conventions["conflicts"]:
            # Look for conflict-related words
            conflict_words = conflict.split()
            if any(word in all_text for word in conflict_words):
                conflict_matches += 1
                authentic_elements.append(f"Conflict: {conflict}")
        
        if conflict_matches > 0:
            authenticity_score += min(2.0, conflict_matches * 0.4)
        
        final_score = min(10.0, authenticity_score)
        
        return final_score, authentic_elements[:5]  # Top 5 elements
    
    def analyze_innovation_creativity(self, scene: SceneData, genre: str) -> Tuple[float, List[str]]:
        """Analyze creative innovations and departures from genre norms"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes} {scene.description}".lower()
        
        innovative_elements = []
        innovation_score = 0.0
        
        # Check for innovation patterns
        for pattern in self.innovation_patterns:
            matches = re.finditer(pattern, all_text)
            for match in matches:
                # Get context
                start = max(0, match.start() - 25)
                end = min(len(all_text), match.end() + 25)
                context = all_text[start:end].strip()
                innovative_elements.append(f"Innovation: {context}")
                innovation_score += 0.8
        
        # Look for genre-blending elements
        if genre in self.genre_conventions:
            other_genres = [g for g in self.genre_conventions.keys() if g != genre]
            
            for other_genre in other_genres:
                other_conventions = self.genre_conventions[other_genre]
                
                # Check if elements from other genres appear
                cross_genre_matches = 0
                for theme in other_conventions["themes"][:3]:  # Check top 3 themes
                    if theme.lower() in all_text:
                        cross_genre_matches += 1
                        innovative_elements.append(f"Cross-genre: {theme} (from {other_genre})")
                
                if cross_genre_matches > 0:
                    innovation_score += min(2.0, cross_genre_matches * 0.6)
        
        # Creative structural elements
        structural_innovations = [
            r'\bshow within.?show\b',
            r'\bmeta.?theatrical\b',
            r'\bbreaking.?fourth.?wall\b',
            r'\bnarrative.?device\b',
            r'\bunconventional.?structure\b'
        ]
        
        for pattern in structural_innovations:
            if re.search(pattern, all_text):
                innovation_score += 1.5
                innovative_elements.append(f"Structural innovation: {pattern}")
        
        # Musical innovations
        musical_innovations = [
            r'\b(?:rap|hip.?hop|electronic|synthesized)\b',
            r'\b(?:a capella|vocal percussion|beatboxing)\b',
            r'\b(?:jazz fusion|rock opera|pop musical)\b',
            r'\b(?:experimental|atonal|microtonal)\b'
        ]
        
        for pattern in musical_innovations:
            if re.search(pattern, all_text):
                innovation_score += 1.2
                innovative_elements.append(f"Musical innovation: {pattern}")
        
        # Thematic innovations
        contemporary_themes = [
            r'\b(?:social media|internet|digital|virtual reality)\b',
            r'\b(?:climate change|environmental|sustainability)\b',
            r'\b(?:ai|artificial intelligence|machine learning)\b',
            r'\b(?:diversity|inclusion|representation)\b'
        ]
        
        for pattern in contemporary_themes:
            if re.search(pattern, all_text):
                innovation_score += 1.0
                innovative_elements.append(f"Contemporary theme: {pattern}")
        
        final_score = min(10.0, innovation_score)
        
        return final_score, innovative_elements[:5]  # Top 5 innovations
    
    def analyze_convention_adherence(self, scene: SceneData, genre: str) -> Tuple[float, List[str]]:
        """Analyze adherence to expected genre conventions"""
        if genre not in self.genre_conventions:
            return 5.0, ["Genre conventions unknown"]
        
        conventions = self.genre_conventions[genre]
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes} {scene.description}".lower()
        
        conventions_met = []
        adherence_score = 0.0
        
        # Core conventions checklist
        convention_checklist = {
            "thematic_alignment": 0,
            "setting_appropriateness": 0,
            "vocabulary_consistency": 0,
            "conflict_structure": 0,
            "tone_matching": 0
        }
        
        # Thematic alignment
        theme_count = sum(1 for theme in conventions["themes"] if theme.lower() in all_text)
        if theme_count >= 3:
            convention_checklist["thematic_alignment"] = 2.0
            conventions_met.append(f"Strong thematic alignment ({theme_count} themes)")
        elif theme_count >= 1:
            convention_checklist["thematic_alignment"] = 1.0
            conventions_met.append(f"Moderate thematic alignment ({theme_count} themes)")
        
        # Setting appropriateness
        setting_count = sum(1 for setting in conventions["settings"] if setting.lower() in all_text)
        if setting_count >= 2:
            convention_checklist["setting_appropriateness"] = 2.0
            conventions_met.append(f"Appropriate setting elements ({setting_count} settings)")
        elif setting_count >= 1:
            convention_checklist["setting_appropriateness"] = 1.0
            conventions_met.append(f"Some setting elements ({setting_count} settings)")
        
        # Vocabulary consistency
        vocab_count = sum(1 for vocab in conventions["vocabulary"] if vocab.lower() in all_text)
        if vocab_count >= 3:
            convention_checklist["vocabulary_consistency"] = 2.0
            conventions_met.append(f"Consistent genre vocabulary ({vocab_count} terms)")
        elif vocab_count >= 1:
            convention_checklist["vocabulary_consistency"] = 1.0
            conventions_met.append(f"Some genre vocabulary ({vocab_count} terms)")
        
        # Conflict structure
        conflict_indicators = sum(1 for conflict in conventions["conflicts"] 
                                 if any(word in all_text for word in conflict.split()))
        if conflict_indicators >= 2:
            convention_checklist["conflict_structure"] = 2.0
            conventions_met.append(f"Genre-appropriate conflicts ({conflict_indicators} types)")
        elif conflict_indicators >= 1:
            convention_checklist["conflict_structure"] = 1.0
            conventions_met.append(f"Some genre conflicts ({conflict_indicators} types)")
        
        # Tone matching (basic sentiment analysis)
        if genre in ["Fantasy Musical Theater", "Contemporary Drama"]:
            # Look for positive/uplifting elements
            positive_words = ["hope", "dream", "love", "joy", "wonder", "magic", "friendship"]
            positive_count = sum(1 for word in positive_words if word in all_text)
            if positive_count >= 2:
                convention_checklist["tone_matching"] = 2.0
                conventions_met.append(f"Appropriate positive tone ({positive_count} indicators)")
        elif genre in ["Murder Mystery", "Dystopian Action"]:
            # Look for dark/tense elements
            dark_words = ["danger", "fear", "threat", "mystery", "secret", "tension", "conflict"]
            dark_count = sum(1 for word in dark_words if word in all_text)
            if dark_count >= 2:
                convention_checklist["tone_matching"] = 2.0
                conventions_met.append(f"Appropriate tense tone ({dark_count} indicators)")
        
        adherence_score = sum(convention_checklist.values())
        final_score = min(10.0, adherence_score)
        
        return final_score, conventions_met
    
    def analyze_creative_risks(self, scene: SceneData) -> Tuple[float, List[str]]:
        """Analyze creative risk-taking and bold choices"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes} {scene.description}".lower()
        
        creative_risks = []
        risk_score = 0.0
        
        # Identify risky creative choices
        risk_indicators = [
            # Structural risks
            (r'\bcomplex|complicated|challenging\b', "Complex structure", 1.0),
            (r'\bunconventional|unusual|unexpected\b', "Unconventional approach", 1.2),
            (r'\bexperimental|avant.?garde|innovative\b', "Experimental elements", 1.5),
            
            # Content risks
            (r'\bcontroversial|provocative|challenging\b', "Provocative content", 1.3),
            (r'\bpolitical|social commentary|critique\b', "Social/political themes", 1.1),
            (r'\bphilosophical|existential|metaphysical\b', "Deep philosophical content", 1.2),
            
            # Technical risks
            (r'\bmultimedia|technology|digital integration\b', "Technical innovation", 1.0),
            (r'\binteractive|audience participation\b', "Interactive elements", 1.4),
            (r'\bimmersive|environmental|site.?specific\b', "Immersive staging", 1.3),
            
            # Artistic risks
            (r'\babstract|non.?linear|stream.?of.?consciousness\b', "Abstract narrative", 1.5),
            (r'\bminimalist|sparse|stripped.?down\b', "Minimalist approach", 1.1),
            (r'\bmaximalist|overwhelming|sensory.?overload\b', "Maximalist approach", 1.1)
        ]
        
        for pattern, description, score_weight in risk_indicators:
            matches = len(re.findall(pattern, all_text))
            if matches > 0:
                risk_score += matches * score_weight
                creative_risks.append(f"{description}: {matches} instances")
        
        # Length and complexity as risk factors
        word_count = len(all_text.split())
        if word_count > 1000:  # Very long scene
            risk_score += 0.8
            creative_risks.append(f"Complex length: {word_count} words")
        
        # Multiple character complexity
        character_mentions = len(re.findall(r'\*\*[A-Z][A-Z\s]+\*\*:', scene.lyrics))
        if character_mentions > 5:
            risk_score += 0.6
            creative_risks.append(f"Complex cast: {character_mentions} character voices")
        
        final_score = min(10.0, risk_score)
        
        return final_score, creative_risks[:5]
    
    def determine_authenticity_level(self, authenticity_score: float, convention_score: float) -> str:
        """Determine the level of genre authenticity"""
        combined_score = (authenticity_score + convention_score) / 2
        
        if combined_score >= 8.0:
            return "Traditional"
        elif combined_score >= 5.0:
            return "Contemporary"
        else:
            return "Experimental"
    
    def determine_innovation_level(self, innovation_score: float, risk_score: float) -> str:
        """Determine the level of innovation"""
        combined_score = (innovation_score + risk_score) / 2
        
        if combined_score >= 7.0:
            return "Groundbreaking"
        elif combined_score >= 4.0:
            return "Moderate"
        else:
            return "Conservative"
    
    def determine_genre_balance(self, authenticity_score: float, innovation_score: float) -> str:
        """Determine the balance between authenticity and innovation"""
        auth_ratio = authenticity_score / 10.0
        innov_ratio = innovation_score / 10.0
        
        if abs(auth_ratio - innov_ratio) < 0.2:
            return "Genre Fusion"
        elif auth_ratio > innov_ratio + 0.3:
            return "Pure Genre"
        else:
            return "Genre Blend"
    
    def find_cross_genre_influences(self, scene: SceneData, primary_genre: str) -> List[str]:
        """Identify influences from other genres"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes} {scene.description}".lower()
        cross_influences = []
        
        for genre, conventions in self.genre_conventions.items():
            if genre != primary_genre:
                # Check for elements from other genres
                matches = 0
                for theme in conventions["themes"][:3]:  # Top 3 themes
                    if theme.lower() in all_text:
                        matches += 1
                
                if matches >= 2:
                    cross_influences.append(f"{genre} elements ({matches} themes)")
        
        return cross_influences[:3]  # Top 3 influences
    
    def analyze_scene_genre(self, scene: SceneData, genre: str) -> GenreAnalysis:
        """Perform comprehensive genre analysis on a scene"""
        analysis_start = time.time()
        
        print(f"🎭 Analyzing genre for: {scene.title}")
        print(f"   🎪 Genre: {genre}")
        
        # Perform component analyses
        auth_score, auth_elements = self.analyze_genre_authenticity(scene, genre)
        innov_score, innov_elements = self.analyze_innovation_creativity(scene, genre)
        conv_score, conv_met = self.analyze_convention_adherence(scene, genre)
        risk_score, risks = self.analyze_creative_risks(scene)
        
        # Find cross-genre influences
        cross_influences = self.find_cross_genre_influences(scene, genre)
        
        # Determine qualitative assessments
        auth_level = self.determine_authenticity_level(auth_score, conv_score)
        innov_level = self.determine_innovation_level(innov_score, risk_score)
        genre_balance = self.determine_genre_balance(auth_score, innov_score)
        
        # Calculate overall score
        overall_score = (auth_score + innov_score + conv_score + risk_score) / 4
        
        analysis_time = time.time() - analysis_start
        
        print(f"   🎯 Authenticity: {auth_score:.1f}/10")
        print(f"   ✨ Innovation: {innov_score:.1f}/10")
        print(f"   📋 Conventions: {conv_score:.1f}/10")
        print(f"   🎲 Creative Risk: {risk_score:.1f}/10")
        print(f"   🏆 Overall Genre Score: {overall_score:.1f}/10")
        print(f"   📊 Level: {auth_level} | Innovation: {innov_level} | Balance: {genre_balance}")
        
        return GenreAnalysis(
            scene_title=scene.title,
            genre_authenticity_score=auth_score,
            innovation_creativity_score=innov_score,
            genre_convention_adherence=conv_score,
            creative_risk_taking_score=risk_score,
            overall_genre_score=overall_score,
            genre=genre,
            authentic_elements=auth_elements,
            innovative_elements=innov_elements,
            genre_conventions_met=conv_met,
            creative_risks_identified=risks,
            cross_genre_influences=cross_influences,
            authenticity_level=auth_level,
            innovation_level=innov_level,
            genre_balance=genre_balance,
            analysis_time=analysis_time
        )

def run_genre_authenticity_analysis():
    """Run genre authenticity analysis on all musicals"""
    
    print("🎭🎪 GENRE AUTHENTICITY & INNOVATION ASSESSMENT")
    print("=" * 55)
    print("Analyzing genre representation and creative innovation")
    print("Components: Authenticity, Innovation, Conventions, Risk-Taking\n")
    
    analyzer = GenreAuthenticityAnalyzer()
    
    # Musical scenes with their declared genres
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
            print(f"🎪 GENRE ANALYSIS {i}/6: {scene_info['musical']}")
            print("-" * 50)
            
            # Load scene
            scene_path = Path(scene_info['file'])
            if not scene_path.exists():
                print(f"❌ Scene file not found: {scene_info['file']}")
                continue
            
            with open(scene_path, 'r', encoding='utf-8') as f:
                scene_data = json.load(f)
            scene = SceneData(**scene_data)
            
            # Perform genre analysis
            analysis = analyzer.analyze_scene_genre(scene, scene_info['genre'])
            
            # Format result
            result = {
                "rank": i,
                "musical_name": scene_info['musical'],
                "declared_genre": scene_info['genre'],
                "scene_title": analysis.scene_title,
                "genre_scores": {
                    "overall_genre_score": round(analysis.overall_genre_score, 2),
                    "genre_authenticity_score": round(analysis.genre_authenticity_score, 2),
                    "innovation_creativity_score": round(analysis.innovation_creativity_score, 2),
                    "genre_convention_adherence": round(analysis.genre_convention_adherence, 2),
                    "creative_risk_taking_score": round(analysis.creative_risk_taking_score, 2)
                },
                "genre_assessment": {
                    "authenticity_level": analysis.authenticity_level,
                    "innovation_level": analysis.innovation_level,
                    "genre_balance": analysis.genre_balance
                },
                "genre_details": {
                    "authentic_elements": analysis.authentic_elements,
                    "innovative_elements": analysis.innovative_elements,
                    "conventions_met": analysis.genre_conventions_met,
                    "creative_risks": analysis.creative_risks_identified,
                    "cross_genre_influences": analysis.cross_genre_influences
                },
                "analysis_time": round(analysis.analysis_time, 2)
            }
            
            results.append(result)
            print()
            
        except Exception as e:
            print(f"❌ Error analyzing {scene_info['musical']}: {e}")
            continue
    
    total_time = time.time() - total_start
    
    # Sort by overall genre score
    results.sort(key=lambda x: x['genre_scores']['overall_genre_score'], reverse=True)
    
    # Update rankings
    for i, result in enumerate(results, 1):
        result['rank'] = i
    
    print("=" * 55)
    print("🏆 GENRE AUTHENTICITY & INNOVATION RANKINGS")
    print("=" * 55)
    
    if results:
        # Calculate statistics
        genre_scores = [r['genre_scores']['overall_genre_score'] for r in results]
        collection_average = sum(genre_scores) / len(genre_scores)
        score_range = max(genre_scores) - min(genre_scores)
        
        print(f"Collection Average: {collection_average:.1f}/10.0")
        print(f"Score Range: {score_range:.1f} points")
        print(f"Analysis Time: {total_time:.1f} seconds")
        print(f"Musicals Analyzed: {len(results)}/6")
        print()
        
        # Component averages
        auth_avg = sum(r['genre_scores']['genre_authenticity_score'] for r in results) / len(results)
        innov_avg = sum(r['genre_scores']['innovation_creativity_score'] for r in results) / len(results)
        conv_avg = sum(r['genre_scores']['genre_convention_adherence'] for r in results) / len(results)
        risk_avg = sum(r['genre_scores']['creative_risk_taking_score'] for r in results) / len(results)
        
        print("📊 COMPONENT AVERAGES:")
        print(f"   Genre Authenticity: {auth_avg:.1f}/10")
        print(f"   Innovation/Creativity: {innov_avg:.1f}/10")
        print(f"   Convention Adherence: {conv_avg:.1f}/10")
        print(f"   Creative Risk-Taking: {risk_avg:.1f}/10")
        print()
        
        # Rankings with details
        print("🎭 DETAILED GENRE RANKINGS:")
        for result in results:
            scores = result['genre_scores']
            assessment = result['genre_assessment']
            print(f"{result['rank']}. {result['musical_name']}")
            print(f"   Overall: {scores['overall_genre_score']}/10 | Genre: {result['declared_genre']}")
            print(f"   Auth:{scores['genre_authenticity_score']:.1f} Innov:{scores['innovation_creativity_score']:.1f} Conv:{scores['genre_convention_adherence']:.1f} Risk:{scores['creative_risk_taking_score']:.1f}")
            print(f"   Level: {assessment['authenticity_level']} | Innovation: {assessment['innovation_level']} | Balance: {assessment['genre_balance']}")
            
            # Show top authentic element
            if result['genre_details']['authentic_elements']:
                print(f"   Authentic: {result['genre_details']['authentic_elements'][0]}")
            print()
        
        # Genre analysis summary
        print("🎨 GENRE AUTHENTICITY PATTERNS:")
        auth_levels = {}
        innov_levels = {}
        for result in results:
            assessment = result['genre_assessment']
            auth_level = assessment['authenticity_level']
            innov_level = assessment['innovation_level']
            
            auth_levels[auth_level] = auth_levels.get(auth_level, 0) + 1
            innov_levels[innov_level] = innov_levels.get(innov_level, 0) + 1
        
        print("   Authenticity Levels:")
        for level, count in auth_levels.items():
            print(f"     {level}: {count} musicals")
        
        print("   Innovation Levels:")
        for level, count in innov_levels.items():
            print(f"     {level}: {count} musicals")
        
        # Save results
        output_data = {
            "analysis_metadata": {
                "analysis_type": "Genre Authenticity & Innovation Assessment",
                "analysis_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_musicals": len(results),
                "collection_average": round(collection_average, 2),
                "score_range": round(score_range, 2),
                "analysis_time_seconds": round(total_time, 1),
                "component_averages": {
                    "genre_authenticity": round(auth_avg, 2),
                    "innovation_creativity": round(innov_avg, 2),
                    "convention_adherence": round(conv_avg, 2),
                    "creative_risk_taking": round(risk_avg, 2)
                }
            },
            "genre_rankings": results,
            "authenticity_distribution": auth_levels,
            "innovation_distribution": innov_levels
        }
        
        with open("GENRE_authenticity_analysis.json", 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Genre analysis saved to: GENRE_authenticity_analysis.json")
        print("🎪 Genre Authenticity & Innovation Assessment complete!")
        
        return results
    
    else:
        print("❌ No analyses completed")
        return []

if __name__ == "__main__":
    print("🚀 Starting Genre Authenticity & Innovation Assessment...")
    run_genre_authenticity_analysis()