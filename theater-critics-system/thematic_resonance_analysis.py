#!/usr/bin/env python3
"""
Cross-Musical Thematic Resonance Study
Evaluates how themes and messages resonate across the entire musical collection
"""

import json
import re
import time
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
from main import SceneData

@dataclass
class ThematicResonanceAnalysis:
    """Results of cross-musical thematic resonance analysis"""
    scene_title: str
    universal_theme_score: float          # 0-10 - Connection to universal human themes
    collection_coherence_score: float     # 0-10 - How well it fits with other musicals
    thematic_depth_score: float           # 0-10 - Sophistication and complexity of themes
    cross_reference_score: float          # 0-10 - Thematic connections to other works
    overall_resonance_score: float        # 0-10 - Combined thematic resonance assessment
    
    # Thematic analysis details
    universal_themes_identified: List[str]
    collection_connections: List[str]
    thematic_depth_elements: List[str]
    cross_references: List[str]
    resonance_strengths: List[str]
    
    # Resonance characteristics
    primary_universal_theme: str          # Core universal theme
    collection_role: str                  # "Anchor", "Bridge", "Outlier", "Complement"
    thematic_complexity: str              # "Simple", "Moderate", "Complex", "Sophisticated"
    resonance_pattern: str                # "Individual", "Collective", "Universal", "Transcendent"
    
    analysis_time: float

class ThematicResonanceAnalyzer:
    """Specialized analyzer for cross-musical thematic resonance evaluation"""
    
    def __init__(self):
        # Initialize with existing analysis data
        self.load_existing_analyses()
        
        # Universal theme patterns
        self.universal_themes = {
            "love_connection": [
                r'\b(?:love|romance|connection|relationship|bond)\b',
                r'\b(?:heart|soul|passion|intimacy|devotion)\b',
                r'\b(?:together|unity|harmony|partnership)\b'
            ],
            "identity_discovery": [
                r'\b(?:identity|self|who am i|discovery|finding)\b',
                r'\b(?:authentic|true self|real me|becoming)\b',
                r'\b(?:growth|transformation|journey|evolution)\b'
            ],
            "power_corruption": [
                r'\b(?:power|control|authority|dominance|rule)\b',
                r'\b(?:corruption|abuse|misuse|tyranny|oppression)\b',
                r'\b(?:resistance|rebellion|fight|freedom)\b'
            ],
            "sacrifice_redemption": [
                r'\b(?:sacrifice|redemption|forgiveness|atonement)\b',
                r'\b(?:giving up|letting go|price|cost|consequence)\b',
                r'\b(?:salvation|second chance|making amends)\b'
            ],
            "hope_despair": [
                r'\b(?:hope|optimism|faith|belief|trust)\b',
                r'\b(?:despair|hopelessness|darkness|doubt|fear)\b',
                r'\b(?:light|dawn|future|possibility|dream)\b'
            ],
            "family_belonging": [
                r'\b(?:family|home|belonging|acceptance|place)\b',
                r'\b(?:roots|heritage|legacy|tradition|ancestry)\b',
                r'\b(?:community|tribe|group|clan|kinship)\b'
            ],
            "truth_deception": [
                r'\b(?:truth|honesty|reality|fact|genuine)\b',
                r'\b(?:lie|deception|facade|pretense|illusion)\b',
                r'\b(?:reveal|expose|unmask|uncover|discover)\b'
            ],
            "mortality_legacy": [
                r'\b(?:death|mortality|end|final|last)\b',
                r'\b(?:legacy|memory|remembrance|immortal|eternal)\b',
                r'\b(?:life|living|existence|being|purpose)\b'
            ],
            "freedom_oppression": [
                r'\b(?:freedom|liberty|independence|autonomy)\b',
                r'\b(?:oppression|slavery|bondage|chains|prison)\b',
                r'\b(?:break free|escape|liberation|release)\b'
            ],
            "creation_destruction": [
                r'\b(?:create|build|make|construct|generate)\b',
                r'\b(?:destroy|demolish|ruin|end|annihilate)\b',
                r'\b(?:birth|death|beginning|ending|cycle)\b'
            ]
        }
        
        # Collection coherence patterns (shared themes across musicals)
        self.collection_patterns = {
            "technology_humanity": [
                r'\b(?:technology|artificial|digital|electronic|cyber)\b',
                r'\b(?:human|humanity|soul|emotion|feeling)\b',
                r'\b(?:connection|relationship|understanding|empathy)\b'
            ],
            "performance_reality": [
                r'\b(?:performance|act|show|theater|stage)\b',
                r'\b(?:reality|real|authentic|genuine|true)\b',
                r'\b(?:mask|role|character|persona|identity)\b'
            ],
            "rebellion_conformity": [
                r'\b(?:rebel|resistance|fight|oppose|challenge)\b',
                r'\b(?:conform|comply|follow|obey|submit)\b',
                r'\b(?:system|authority|establishment|order)\b'
            ],
            "isolation_community": [
                r'\b(?:alone|isolated|lonely|separate|apart)\b',
                r'\b(?:community|together|group|collective|united)\b',
                r'\b(?:connection|belonging|acceptance|inclusion)\b'
            ],
            "past_future": [
                r'\b(?:past|history|memory|tradition|heritage)\b',
                r'\b(?:future|tomorrow|next|coming|ahead)\b',
                r'\b(?:change|progress|evolution|development)\b'
            ]
        }
        
        # Thematic depth indicators
        self.depth_indicators = {
            "philosophical": [
                r'\b(?:meaning|purpose|existence|being|consciousness)\b',
                r'\b(?:philosophy|metaphysical|spiritual|transcendent)\b',
                r'\b(?:universe|cosmos|infinite|eternal|divine)\b'
            ],
            "psychological": [
                r'\b(?:mind|psyche|mental|emotional|internal)\b',
                r'\b(?:subconscious|unconscious|memory|trauma)\b',
                r'\b(?:psychology|behavior|motivation|drive)\b'
            ],
            "sociological": [
                r'\b(?:society|social|cultural|community|civilization)\b',
                r'\b(?:class|status|hierarchy|structure|system)\b',
                r'\b(?:collective|group|masses|population)\b'
            ],
            "moral_ethical": [
                r'\b(?:moral|ethical|right|wrong|good|evil)\b',
                r'\b(?:justice|fairness|virtue|sin|guilt)\b',
                r'\b(?:conscience|values|principles|beliefs)\b'
            ],
            "existential": [
                r'\b(?:existence|being|reality|life|death)\b',
                r'\b(?:purpose|meaning|significance|worth)\b',
                r'\b(?:absurd|meaningless|void|empty|nothing)\b'
            ]
        }
        
        # Cross-reference patterns (connections to broader works/ideas)
        self.cross_reference_patterns = {
            "literary_classical": [
                r'\b(?:shakespeare|greek tragedy|classical|epic)\b',
                r'\b(?:hero|tragic|dramatic|noble|heroic)\b',
                r'\b(?:myth|legend|archetypal|timeless)\b'
            ],
            "contemporary_media": [
                r'\b(?:film|movie|television|media|pop culture)\b',
                r'\b(?:reference|allusion|homage|tribute)\b',
                r'\b(?:modern|contemporary|current|today)\b'
            ],
            "historical_events": [
                r'\b(?:war|revolution|historical|period|era)\b',
                r'\b(?:social movement|change|progress|reform)\b',
                r'\b(?:documented|recorded|real|actual)\b'
            ],
            "artistic_movements": [
                r'\b(?:artistic|aesthetic|movement|style|school)\b',
                r'\b(?:avant-garde|experimental|innovative|creative)\b',
                r'\b(?:expression|form|technique|method)\b'
            ]
        }
    
    def load_existing_analyses(self):
        """Load data from previous analyses for cross-referencing"""
        self.existing_data = {}
        
        # Load key analyses for thematic comparison
        analysis_files = [
            "LYRICAL_analysis.json",
            "CHARACTER_arc_analysis.json", 
            "EMOTIONAL_journey_analysis.json",
            "CULTURAL_commentary_analysis.json"
        ]
        
        for file_name in analysis_files:
            try:
                file_path = Path(file_name)
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        analysis_type = file_name.replace('.json', '').replace('_analysis', '')
                        self.existing_data[analysis_type] = data
                        print(f"   📊 Loaded {analysis_type} data for cross-reference")
            except Exception as e:
                print(f"   ⚠️ Could not load {file_name}: {e}")
    
    def extract_thematic_elements(self, scene: SceneData) -> Dict[str, List[str]]:
        """Extract thematic elements for resonance analysis"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes}"
        
        thematic_elements = {
            "universal_themes": [],
            "collection_themes": [],
            "depth_indicators": [],
            "cross_references": []
        }
        
        # Extract universal themes
        for theme, patterns in self.universal_themes.items():
            for pattern in patterns:
                matches = re.finditer(pattern, all_text, re.IGNORECASE)
                for match in matches:
                    context = self._get_context(all_text, match.start(), match.end())
                    thematic_elements["universal_themes"].append(f"{theme}: {context}")
        
        # Extract collection patterns
        for pattern, keywords in self.collection_patterns.items():
            for keyword in keywords:
                matches = re.finditer(keyword, all_text, re.IGNORECASE)
                for match in matches:
                    context = self._get_context(all_text, match.start(), match.end())
                    thematic_elements["collection_themes"].append(f"{pattern}: {context}")
        
        return thematic_elements
    
    def _get_context(self, text: str, start: int, end: int, context_size: int = 50) -> str:
        """Get context around a match"""
        context_start = max(0, start - context_size)
        context_end = min(len(text), end + context_size)
        context = text[context_start:context_end].strip()
        return context[:80] + "..." if len(context) > 80 else context
    
    def analyze_universal_themes(self, scene: SceneData) -> Tuple[float, List[str]]:
        """Analyze connection to universal human themes"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes}".lower()
        
        universal_themes = []
        theme_score = 0.0
        themes_found = 0
        
        # Analyze each universal theme
        for theme, patterns in self.universal_themes.items():
            theme_count = 0
            for pattern in patterns:
                theme_count += len(re.findall(pattern, all_text))
            
            if theme_count > 0:
                theme_score += theme_count * 1.0
                universal_themes.append(f"{theme.replace('_', ' ').title()}: {theme_count}")
                themes_found += 1
        
        # Bonus for multiple universal themes (indicates thematic richness)
        if themes_found >= 3:
            theme_score += 2.0
            universal_themes.append(f"Multiple universal themes: {themes_found}")
        elif themes_found >= 2:
            theme_score += 1.0
            universal_themes.append(f"Dual universal themes: {themes_found}")
        
        # Look for archetypal elements
        archetypal_patterns = [
            r'\b(?:hero|villain|mentor|guide|wise|fool)\b',
            r'\b(?:journey|quest|trial|test|challenge)\b',
            r'\b(?:archetypal|universal|timeless|eternal)\b'
        ]
        
        archetypal_count = sum(len(re.findall(pattern, all_text)) for pattern in archetypal_patterns)
        if archetypal_count > 0:
            theme_score += archetypal_count * 1.2
            universal_themes.append(f"Archetypal elements: {archetypal_count}")
        
        final_score = min(10.0, theme_score)
        
        return final_score, universal_themes[:5]
    
    def analyze_collection_coherence(self, scene: SceneData) -> Tuple[float, List[str]]:
        """Analyze how well it fits with other musicals in the collection"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes}".lower()
        
        collection_connections = []
        coherence_score = 0.0
        
        # Analyze collection pattern matches
        for pattern, keywords in self.collection_patterns.items():
            pattern_count = 0
            for keyword in keywords:
                pattern_count += len(re.findall(keyword, all_text))
            
            if pattern_count > 0:
                coherence_score += pattern_count * 1.5
                collection_connections.append(f"{pattern.replace('_', ' ').title()}: {pattern_count}")
        
        # Cross-reference with existing analyses if available
        if self.existing_data:
            for analysis_type, data in self.existing_data.items():
                if 'rankings' in data:
                    # Find this scene in the existing data
                    scene_matches = [
                        item for item in data['rankings'] 
                        if scene.title.lower() in item.get('scene_title', '').lower()
                    ]
                    
                    if scene_matches:
                        scene_data = scene_matches[0]
                        # Award points for high scores in related analyses
                        for score_key in scene_data.get('scores', {}):
                            score = scene_data['scores'][score_key]
                            if 'overall' in score_key and score >= 7.0:
                                coherence_score += 1.0
                                collection_connections.append(f"High {analysis_type} score: {score}")
        
        # Look for shared motifs across the collection
        shared_motifs = [
            r'\b(?:transformation|change|growth|evolution)\b',
            r'\b(?:connection|relationship|bond|unity)\b',
            r'\b(?:performance|show|display|presentation)\b',
            r'\b(?:reality|truth|authentic|genuine)\b',
            r'\b(?:future|past|time|history|memory)\b'
        ]
        
        motif_count = sum(len(re.findall(pattern, all_text)) for pattern in shared_motifs)
        if motif_count > 0:
            coherence_score += motif_count * 0.8
            collection_connections.append(f"Shared collection motifs: {motif_count}")
        
        final_score = min(10.0, coherence_score)
        
        return final_score, collection_connections[:5]
    
    def analyze_thematic_depth(self, scene: SceneData) -> Tuple[float, List[str]]:
        """Analyze sophistication and complexity of themes"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes}".lower()
        
        depth_elements = []
        depth_score = 0.0
        
        # Analyze depth indicators
        for category, patterns in self.depth_indicators.items():
            category_count = 0
            for pattern in patterns:
                category_count += len(re.findall(pattern, all_text))
            
            if category_count > 0:
                # Score based on depth category sophistication
                depth_weights = {
                    "philosophical": 2.0,
                    "existential": 1.8,
                    "psychological": 1.5,
                    "moral_ethical": 1.3,
                    "sociological": 1.2
                }
                depth_score += category_count * depth_weights.get(category, 1.0)
                depth_elements.append(f"{category.replace('_', ' ').title()}: {category_count}")
        
        # Look for complexity indicators
        complexity_patterns = [
            r'\b(?:complex|complicated|nuanced|sophisticated)\b',
            r'\b(?:multi-layered|multi-faceted|intricate|elaborate)\b',
            r'\b(?:paradox|contradiction|irony|ambiguity)\b',
            r'\b(?:subtle|implicit|underlying|deeper)\b'
        ]
        
        complexity_count = sum(len(re.findall(pattern, all_text)) for pattern in complexity_patterns)
        if complexity_count > 0:
            depth_score += complexity_count * 1.4
            depth_elements.append(f"Complexity indicators: {complexity_count}")
        
        # Check for thematic layering
        layering_patterns = [
            r'\b(?:surface|beneath|under|hidden|concealed)\b',
            r'\b(?:multiple meanings|double meaning|symbolism)\b',
            r'\b(?:metaphor|allegory|subtext|implication)\b'
        ]
        
        layering_count = sum(len(re.findall(pattern, all_text)) for pattern in layering_patterns)
        if layering_count > 0:
            depth_score += layering_count * 1.2
            depth_elements.append(f"Thematic layering: {layering_count}")
        
        final_score = min(10.0, depth_score)
        
        return final_score, depth_elements[:5]
    
    def analyze_cross_references(self, scene: SceneData) -> Tuple[float, List[str]]:
        """Analyze thematic connections to other works and ideas"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes}".lower()
        
        cross_references = []
        reference_score = 0.0
        
        # Analyze cross-reference patterns
        for category, patterns in self.cross_reference_patterns.items():
            category_count = 0
            for pattern in patterns:
                category_count += len(re.findall(pattern, all_text))
            
            if category_count > 0:
                # Score based on reference sophistication
                reference_weights = {
                    "literary_classical": 1.8,
                    "artistic_movements": 1.5,
                    "historical_events": 1.3,
                    "contemporary_media": 1.0
                }
                reference_score += category_count * reference_weights.get(category, 1.0)
                cross_references.append(f"{category.replace('_', ' ').title()}: {category_count}")
        
        # Look for intertextual elements
        intertextual_patterns = [
            r'\b(?:reference|allusion|homage|tribute|nod)\b',
            r'\b(?:inspired by|based on|influenced by|echoes)\b',
            r'\b(?:reminiscent|similar to|parallels|mirrors)\b'
        ]
        
        intertextual_count = sum(len(re.findall(pattern, all_text)) for pattern in intertextual_patterns)
        if intertextual_count > 0:
            reference_score += intertextual_count * 1.3
            cross_references.append(f"Intertextual elements: {intertextual_count}")
        
        # Check for cultural resonance
        cultural_patterns = [
            r'\b(?:cultural|tradition|heritage|legacy)\b',
            r'\b(?:generational|timeless|enduring|lasting)\b',
            r'\b(?:speaks to|resonates|connects|touches)\b'
        ]
        
        cultural_count = sum(len(re.findall(pattern, all_text)) for pattern in cultural_patterns)
        if cultural_count > 0:
            reference_score += cultural_count * 1.1
            cross_references.append(f"Cultural resonance: {cultural_count}")
        
        final_score = min(10.0, reference_score)
        
        return final_score, cross_references[:5]
    
    def determine_primary_universal_theme(self, scene: SceneData) -> str:
        """Determine the core universal theme"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes}".lower()
        
        theme_scores = {}
        for theme, patterns in self.universal_themes.items():
            score = sum(len(re.findall(pattern, all_text)) for pattern in patterns)
            if score > 0:
                theme_scores[theme] = score
        
        if theme_scores:
            primary_theme = max(theme_scores, key=theme_scores.get)
            return primary_theme.replace('_', ' ').title()
        else:
            return "Human Experience"
    
    def determine_collection_role(self, coherence_score: float, scene: SceneData) -> str:
        """Determine the role within the collection"""
        if coherence_score >= 8.0:
            return "Anchor"
        elif coherence_score >= 6.0:
            return "Bridge"
        elif coherence_score >= 4.0:
            return "Complement"
        else:
            return "Outlier"
    
    def determine_thematic_complexity(self, depth_score: float) -> str:
        """Determine the level of thematic complexity"""
        if depth_score >= 8.0:
            return "Sophisticated"
        elif depth_score >= 6.0:
            return "Complex"
        elif depth_score >= 4.0:
            return "Moderate"
        else:
            return "Simple"
    
    def determine_resonance_pattern(self, universal_score: float, cross_ref_score: float) -> str:
        """Determine the resonance pattern"""
        combined_score = (universal_score + cross_ref_score) / 2
        
        if combined_score >= 8.0:
            return "Transcendent"
        elif combined_score >= 6.0:
            return "Universal"
        elif combined_score >= 4.0:
            return "Collective"
        else:
            return "Individual"
    
    def analyze_scene_thematic_resonance(self, scene: SceneData) -> ThematicResonanceAnalysis:
        """Perform comprehensive thematic resonance analysis"""
        analysis_start = time.time()
        
        print(f"🎭 Analyzing thematic resonance for: {scene.title}")
        
        # Extract thematic elements
        thematic_elements = self.extract_thematic_elements(scene)
        print(f"   🌍 Found {len(thematic_elements['universal_themes'])} universal theme connections")
        print(f"   🔗 Found {len(thematic_elements['collection_themes'])} collection pattern matches")
        
        # Perform component analyses
        universal_score, universal_themes = self.analyze_universal_themes(scene)
        coherence_score, collection_connections = self.analyze_collection_coherence(scene)
        depth_score, depth_elements = self.analyze_thematic_depth(scene)
        cross_ref_score, cross_references = self.analyze_cross_references(scene)
        
        # Determine resonance characteristics
        primary_theme = self.determine_primary_universal_theme(scene)
        collection_role = self.determine_collection_role(coherence_score, scene)
        thematic_complexity = self.determine_thematic_complexity(depth_score)
        resonance_pattern = self.determine_resonance_pattern(universal_score, cross_ref_score)
        
        # Calculate overall resonance score
        overall_score = (universal_score * 0.3 + coherence_score * 0.25 + 
                        depth_score * 0.25 + cross_ref_score * 0.2)
        
        # Identify resonance strengths
        resonance_strengths = []
        if universal_score >= 7.0:
            resonance_strengths.append("Strong universal theme connection")
        if coherence_score >= 7.0:
            resonance_strengths.append("Excellent collection coherence")
        if depth_score >= 7.0:
            resonance_strengths.append("Sophisticated thematic depth")
        if cross_ref_score >= 7.0:
            resonance_strengths.append("Rich cross-cultural references")
        
        analysis_time = time.time() - analysis_start
        
        print(f"   🌍 Universal: {universal_score:.1f}/10")
        print(f"   🔗 Coherence: {coherence_score:.1f}/10")
        print(f"   📚 Depth: {depth_score:.1f}/10")
        print(f"   🎨 Cross-Ref: {cross_ref_score:.1f}/10")
        print(f"   🏆 Overall Resonance Score: {overall_score:.1f}/10")
        print(f"   📈 Theme: {primary_theme} | Role: {collection_role} | Pattern: {resonance_pattern}")
        
        return ThematicResonanceAnalysis(
            scene_title=scene.title,
            universal_theme_score=universal_score,
            collection_coherence_score=coherence_score,
            thematic_depth_score=depth_score,
            cross_reference_score=cross_ref_score,
            overall_resonance_score=overall_score,
            universal_themes_identified=universal_themes,
            collection_connections=collection_connections,
            thematic_depth_elements=depth_elements,
            cross_references=cross_references,
            resonance_strengths=resonance_strengths,
            primary_universal_theme=primary_theme,
            collection_role=collection_role,
            thematic_complexity=thematic_complexity,
            resonance_pattern=resonance_pattern,
            analysis_time=analysis_time
        )

def run_thematic_resonance_analysis():
    """Run cross-musical thematic resonance analysis on all musicals"""
    
    print("🎭🌍 CROSS-MUSICAL THEMATIC RESONANCE STUDY - GRAND FINALE!")
    print("=" * 70)
    print("Analyzing thematic connections and resonance across the entire collection")
    print("Components: Universal Themes, Collection Coherence, Depth, Cross-References\n")
    
    analyzer = ThematicResonanceAnalyzer()
    
    # Musical scenes for thematic resonance analysis
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
            print(f"🎪 RESONANCE ANALYSIS {i}/6: {scene_info['musical']}")
            print("-" * 65)
            
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
            
            # Perform thematic resonance analysis
            analysis = analyzer.analyze_scene_thematic_resonance(scene)
            
            # Format result
            result = {
                "rank": i,
                "musical_name": scene_info['musical'],
                "genre": scene_info['genre'],
                "scene_title": analysis.scene_title,
                "resonance_scores": {
                    "overall_resonance_score": round(analysis.overall_resonance_score, 2),
                    "universal_theme_score": round(analysis.universal_theme_score, 2),
                    "collection_coherence_score": round(analysis.collection_coherence_score, 2),
                    "thematic_depth_score": round(analysis.thematic_depth_score, 2),
                    "cross_reference_score": round(analysis.cross_reference_score, 2)
                },
                "resonance_characteristics": {
                    "primary_universal_theme": analysis.primary_universal_theme,
                    "collection_role": analysis.collection_role,
                    "thematic_complexity": analysis.thematic_complexity,
                    "resonance_pattern": analysis.resonance_pattern
                },
                "resonance_details": {
                    "universal_themes_identified": analysis.universal_themes_identified,
                    "collection_connections": analysis.collection_connections,
                    "thematic_depth_elements": analysis.thematic_depth_elements,
                    "cross_references": analysis.cross_references,
                    "resonance_strengths": analysis.resonance_strengths
                },
                "analysis_time": round(analysis.analysis_time, 2)
            }
            
            results.append(result)
            print()
            
        except Exception as e:
            print(f"❌ Error analyzing {scene_info['musical']}: {e}")
            continue
    
    total_time = time.time() - total_start
    
    # Sort by overall resonance score
    results.sort(key=lambda x: x['resonance_scores']['overall_resonance_score'], reverse=True)
    
    # Update rankings
    for i, result in enumerate(results, 1):
        result['rank'] = i
    
    print("=" * 70)
    print("🏆 CROSS-MUSICAL THEMATIC RESONANCE RANKINGS")
    print("=" * 70)
    
    if results:
        # Calculate statistics
        resonance_scores = [r['resonance_scores']['overall_resonance_score'] for r in results]
        collection_average = sum(resonance_scores) / len(resonance_scores)
        score_range = max(resonance_scores) - min(resonance_scores)
        
        print(f"Collection Average: {collection_average:.1f}/10.0")
        print(f"Score Range: {score_range:.1f} points")
        print(f"Analysis Time: {total_time:.1f} seconds")
        print(f"Musicals Analyzed: {len(results)}/6")
        print()
        
        # Component averages
        universal_avg = sum(r['resonance_scores']['universal_theme_score'] for r in results) / len(results)
        coherence_avg = sum(r['resonance_scores']['collection_coherence_score'] for r in results) / len(results)
        depth_avg = sum(r['resonance_scores']['thematic_depth_score'] for r in results) / len(results)
        cross_ref_avg = sum(r['resonance_scores']['cross_reference_score'] for r in results) / len(results)
        
        print("📊 COMPONENT AVERAGES:")
        print(f"   Universal Themes: {universal_avg:.1f}/10")
        print(f"   Collection Coherence: {coherence_avg:.1f}/10")
        print(f"   Thematic Depth: {depth_avg:.1f}/10")
        print(f"   Cross-References: {cross_ref_avg:.1f}/10")
        print()
        
        # Detailed rankings
        print("🎭 DETAILED RESONANCE RANKINGS:")
        for result in results:
            scores = result['resonance_scores']
            chars = result['resonance_characteristics']
            print(f"{result['rank']}. {result['musical_name']}")
            print(f"   Overall: {scores['overall_resonance_score']}/10 | Genre: {result['genre']}")
            print(f"   Univ:{scores['universal_theme_score']:.1f} Coh:{scores['collection_coherence_score']:.1f} Dep:{scores['thematic_depth_score']:.1f} Ref:{scores['cross_reference_score']:.1f}")
            print(f"   Theme: {chars['primary_universal_theme']} | Role: {chars['collection_role']}")
            print(f"   Complexity: {chars['thematic_complexity']} | Pattern: {chars['resonance_pattern']}")
            print()
        
        # Cross-collection thematic analysis
        print("🌍 CROSS-COLLECTION THEMATIC PATTERNS:")
        
        # Universal themes distribution
        themes = {}
        for result in results:
            theme = result['resonance_characteristics']['primary_universal_theme']
            themes[theme] = themes.get(theme, 0) + 1
        
        print("   Primary Universal Themes:")
        for theme, count in themes.items():
            print(f"     {theme}: {count} musicals")
        
        # Collection roles
        roles = {}
        for result in results:
            role = result['resonance_characteristics']['collection_role']
            roles[role] = roles.get(role, 0) + 1
        
        print("   Collection Roles:")
        for role, count in roles.items():
            print(f"     {role}: {count} musicals")
        
        # Resonance patterns
        patterns = {}
        for result in results:
            pattern = result['resonance_characteristics']['resonance_pattern']
            patterns[pattern] = patterns.get(pattern, 0) + 1
        
        print("   Resonance Patterns:")
        for pattern, count in patterns.items():
            print(f"     {pattern}: {count} musicals")
        
        # Collection coherence analysis
        print("🔗 COLLECTION COHERENCE INSIGHTS:")
        high_coherence = [r for r in results if r['resonance_scores']['collection_coherence_score'] >= 7.0]
        if high_coherence:
            print(f"   High Coherence Musicals: {len(high_coherence)}/6")
            for musical in high_coherence:
                print(f"     - {musical['musical_name']} ({musical['resonance_scores']['collection_coherence_score']}/10)")
        else:
            print("   No musicals achieved high collection coherence (7.0+)")
        
        # Save results
        output_data = {
            "analysis_metadata": {
                "analysis_type": "Cross-Musical Thematic Resonance Study",
                "analysis_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_musicals": len(results),
                "collection_average": round(collection_average, 2),
                "score_range": round(score_range, 2),
                "analysis_time_seconds": round(total_time, 1),
                "component_averages": {
                    "universal_themes": round(universal_avg, 2),
                    "collection_coherence": round(coherence_avg, 2),
                    "thematic_depth": round(depth_avg, 2),
                    "cross_references": round(cross_ref_avg, 2)
                }
            },
            "resonance_rankings": results,
            "collection_patterns": {
                "universal_themes": themes,
                "collection_roles": roles,
                "resonance_patterns": patterns
            },
            "cross_collection_analysis": {
                "high_coherence_count": len(high_coherence),
                "thematic_diversity": len(themes),
                "dominant_theme": max(themes, key=themes.get) if themes else "None",
                "collection_unity_score": round(coherence_avg, 2)
            }
        }
        
        with open("THEMATIC_resonance_analysis.json", 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Thematic resonance analysis saved to: THEMATIC_resonance_analysis.json")
        print("🎭🌍 Cross-Musical Thematic Resonance Study complete - GRAND FINALE ACHIEVED!")
        
        return results
    
    else:
        print("❌ No analyses completed")
        return []

if __name__ == "__main__":
    print("🚀 Starting Cross-Musical Thematic Resonance Study - GRAND FINALE!")
    run_thematic_resonance_analysis()