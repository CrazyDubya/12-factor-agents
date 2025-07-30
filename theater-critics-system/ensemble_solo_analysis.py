#!/usr/bin/env python3
"""
Ensemble vs Solo Performance Requirements Analysis
Evaluates the balance and demands of group vs individual performance elements
"""

import json
import re
import time
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
from main import SceneData

@dataclass
class EnsembleSoloAnalysis:
    """Results of ensemble vs solo performance requirements analysis"""
    scene_title: str
    ensemble_complexity_score: float      # 0-10 - Complexity of group performance requirements
    solo_demands_score: float             # 0-10 - Individual performance challenges and showcase opportunities
    balance_integration_score: float      # 0-10 - How well ensemble and solo elements work together
    performance_variety_score: float      # 0-10 - Range and diversity of performance opportunities
    overall_performance_score: float      # 0-10 - Combined ensemble/solo performance assessment
    
    # Performance distribution
    performance_breakdown: Dict[str, float]  # Percentages of ensemble vs solo vs mixed performance
    ensemble_moments: List[str]
    solo_opportunities: List[str]
    integration_techniques: List[str]
    performance_strengths: List[str]
    
    # Performance characteristics
    ensemble_style: str                    # "Chorus Heavy", "Small Group", "Full Company", "Minimal"
    solo_prominence: str                   # "Featured", "Balanced", "Supporting", "Background"
    integration_approach: str              # "Seamless", "Alternating", "Layered", "Contrasted"
    performance_scope: str                 # "Intimate", "Moderate", "Spectacular", "Epic"
    
    analysis_time: float

class EnsembleSoloAnalyzer:
    """Specialized analyzer for ensemble vs solo performance evaluation"""
    
    def __init__(self):
        # Ensemble performance patterns
        self.ensemble_patterns = {
            "chorus_elements": [
                r'\b(?:chorus|ensemble|all|together|group|company)\b',
                r'\b(?:choir|harmony|unison|collective)\b',
                r'\b(?:everyone|cast|full company|entire group)\b',
                r'\*[^*]*(?:all|everyone|group|together)[^*]*\*'
            ],
            "small_group": [
                r'\b(?:trio|quartet|quintet|duet|pair)\b',
                r'\b(?:small group|few voices|select members)\b',
                r'\b(?:backup singers|supporting cast)\b',
                r'\*[^*]*(?:group of|several|few)[^*]*\*'
            ],
            "layered_vocals": [
                r'\b(?:harmony|counterpoint|layered|overlapping)\b',
                r'\b(?:call and response|antiphonal|divided)\b',
                r'\b(?:soprano|alto|tenor|bass|section)\b',
                r'\*[^*]*(?:layered|harmony|divided)[^*]*\*'
            ],
            "choreographed_movement": [
                r'\b(?:choreography|dance|movement|formation)\b',
                r'\b(?:synchronized|coordinated|staged)\b',
                r'\b(?:blocking|positioning|ensemble staging)\b',
                r'\*[^*]*(?:move|dance|formation)[^*]*\*'
            ]
        }
        
        # Solo performance patterns
        self.solo_patterns = {
            "featured_solos": [
                r'\b(?:solo|soloist|alone|individual|featured)\b',
                r'\b(?:spotlight|center stage|main character)\b',
                r'\b(?:aria|ballad|showcase|feature number)\b',
                r'\*[^*]*(?:solo|alone|spotlight)[^*]*\*'
            ],
            "character_moments": [
                r'\b(?:monologue|soliloquy|aside|reflection)\b',
                r'\b(?:character development|personal moment)\b',
                r'\b(?:inner thoughts|emotional journey)\b',
                r'\*[^*]*(?:character|personal|inner)[^*]*\*'
            ],
            "vocal_showcases": [
                r'\b(?:vocal run|melisma|riff|improvisation)\b',
                r'\b(?:high note|belt|falsetto|range)\b',
                r'\b(?:virtuosic|demanding|challenging)\b',
                r'\*[^*]*(?:vocal|singing|voice)[^*]*\*'
            ],
            "solo_staging": [
                r'\b(?:downstage center|isolated|separate)\b',
                r'\b(?:single performer|one person|individual)\b',
                r'\b(?:personal space|intimate moment)\b',
                r'\*[^*]*(?:stands alone|by themselves)[^*]*\*'
            ]
        }
        
        # Integration technique patterns
        self.integration_patterns = {
            "seamless_transitions": [
                r'\b(?:seamlessly|smoothly|naturally flows)\b',
                r'\b(?:transitions into|becomes|transforms)\b',
                r'\b(?:without break|continuous|uninterrupted)\b'
            ],
            "alternating_structure": [
                r'\b(?:back and forth|alternating|trading)\b',
                r'\b(?:verse and chorus|solo then group)\b',
                r'\b(?:call and response|question and answer)\b'
            ],
            "layered_approach": [
                r'\b(?:layered|overlapping|simultaneous)\b',
                r'\b(?:while|during|as|background)\b',
                r'\b(?:underneath|behind|supporting)\b'
            ],
            "contrasted_sections": [
                r'\b(?:contrasts|different|opposite|distinct)\b',
                r'\b(?:then switches|changes to|shifts)\b',
                r'\b(?:dramatic change|sudden shift)\b'
            ]
        }
        
        # Performance complexity indicators
        self.complexity_indicators = {
            "vocal_complexity": [
                r'\b(?:complex harmony|difficult vocals|challenging)\b',
                r'\b(?:intricate|sophisticated|advanced)\b',
                r'\b(?:professional level|expert|masterful)\b'
            ],
            "choreographic_complexity": [
                r'\b(?:complex choreography|intricate movement)\b',
                r'\b(?:synchronized|precise|coordinated)\b',
                r'\b(?:dance sequence|staged movement)\b'
            ],
            "timing_precision": [
                r'\b(?:precise timing|exact|synchronized)\b',
                r'\b(?:coordination|together|in unison)\b',
                r'\b(?:split-second|perfect timing)\b'
            ],
            "emotional_range": [
                r'\b(?:emotional range|versatility|depth)\b',
                r'\b(?:from|to|through|across)\b.*(?:emotion|feeling)',
                r'\b(?:complex emotions|nuanced|subtle)\b'
            ]
        }
    
    def extract_performance_elements(self, scene: SceneData) -> Dict[str, List[str]]:
        """Extract ensemble and solo performance elements"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes}"
        
        performance_elements = {
            "ensemble_samples": [],
            "solo_samples": [],
            "integration_samples": [],
            "complexity_samples": []
        }
        
        # Extract ensemble examples
        for category, patterns in self.ensemble_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, all_text, re.IGNORECASE)
                for match in matches:
                    context = self._get_context(all_text, match.start(), match.end())
                    performance_elements["ensemble_samples"].append(f"{category}: {context}")
        
        # Extract solo examples
        for category, patterns in self.solo_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, all_text, re.IGNORECASE)
                for match in matches:
                    context = self._get_context(all_text, match.start(), match.end())
                    performance_elements["solo_samples"].append(f"{category}: {context}")
        
        return performance_elements
    
    def _get_context(self, text: str, start: int, end: int, context_size: int = 50) -> str:
        """Get context around a match"""
        context_start = max(0, start - context_size)
        context_end = min(len(text), end + context_size)
        context = text[context_start:context_end].strip()
        return context[:80] + "..." if len(context) > 80 else context
    
    def analyze_performance_breakdown(self, scene: SceneData) -> Tuple[Dict[str, float], float]:
        """Analyze the percentage breakdown of ensemble vs solo vs mixed performance"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes}"
        total_length = len(all_text)
        
        if total_length == 0:
            return {"ensemble": 0, "solo": 0, "mixed": 0}, 0.0
        
        performance_counts = {"ensemble": 0, "solo": 0, "mixed": 0}
        
        # Count ensemble content
        for patterns in self.ensemble_patterns.values():
            for pattern in patterns:
                matches = re.finditer(pattern, all_text, re.IGNORECASE)
                for match in matches:
                    performance_counts["ensemble"] += len(match.group())
        
        # Count solo content
        for patterns in self.solo_patterns.values():
            for pattern in patterns:
                matches = re.finditer(pattern, all_text, re.IGNORECASE)
                for match in matches:
                    performance_counts["solo"] += len(match.group())
        
        # Identify mixed sections (both ensemble and solo indicators present)
        mixed_patterns = [
            r'\b(?:solo with backup|featured with ensemble)\b',
            r'\b(?:lead and chorus|solo over group)\b',
            r'\b(?:individual within group|personal moment with support)\b'
        ]
        
        for pattern in mixed_patterns:
            matches = re.finditer(pattern, all_text, re.IGNORECASE)
            for match in matches:
                performance_counts["mixed"] += len(match.group())
        
        # Calculate percentages
        total_categorized = sum(performance_counts.values())
        if total_categorized == 0:
            # Fallback analysis based on character count
            lines = all_text.split('\n')
            for line in lines:
                line = line.strip()
                if any(word in line.lower() for word in ['all', 'everyone', 'chorus', 'ensemble']):
                    performance_counts["ensemble"] += len(line)
                elif any(word in line.lower() for word in ['solo', 'alone', 'individual']):
                    performance_counts["solo"] += len(line)
                else:
                    performance_counts["mixed"] += len(line)
            total_categorized = sum(performance_counts.values())
        
        percentages = {}
        for perf_type, count in performance_counts.items():
            percentages[perf_type] = (count / total_categorized * 100) if total_categorized > 0 else 0
        
        # Score based on balance (ideal varies by scene type, but generally 30% ensemble, 40% solo, 30% mixed)
        ideal_ratios = {"ensemble": 30, "solo": 40, "mixed": 30}
        balance_score = 0.0
        
        for perf_type, ideal_pct in ideal_ratios.items():
            actual_pct = percentages[perf_type]
            deviation = abs(actual_pct - ideal_pct)
            type_score = max(0, 10 - (deviation / 8))  # More lenient scoring
            balance_score += type_score * (ideal_pct / 100)
        
        return percentages, balance_score
    
    def analyze_ensemble_complexity(self, scene: SceneData) -> Tuple[float, List[str]]:
        """Analyze the complexity of ensemble performance requirements"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes}".lower()
        
        ensemble_moments = []
        complexity_score = 0.0
        
        # Analyze ensemble patterns
        for category, patterns in self.ensemble_patterns.items():
            category_count = 0
            for pattern in patterns:
                category_count += len(re.findall(pattern, all_text))
            
            if category_count > 0:
                # Score based on complexity type
                complexity_weights = {
                    "chorus_elements": 1.2,
                    "small_group": 1.0,
                    "layered_vocals": 1.8,
                    "choreographed_movement": 1.5
                }
                complexity_score += category_count * complexity_weights.get(category, 1.0)
                ensemble_moments.append(f"{category.replace('_', ' ').title()}: {category_count}")
        
        # Check for complexity indicators
        for indicator_type, patterns in self.complexity_indicators.items():
            indicator_count = sum(len(re.findall(pattern, all_text)) for pattern in patterns)
            if indicator_count > 0:
                complexity_score += indicator_count * 0.8
                ensemble_moments.append(f"{indicator_type.replace('_', ' ').title()}: {indicator_count}")
        
        # Look for specific ensemble challenges
        ensemble_challenges = [
            r'\b(?:difficult ensemble|challenging group|complex coordination)\b',
            r'\b(?:tight harmonies|intricate vocals|sophisticated)\b',
            r'\b(?:synchronized movement|precise choreography)\b',
            r'\b(?:large cast|full company|entire ensemble)\b'
        ]
        
        challenge_count = sum(len(re.findall(pattern, all_text)) for pattern in ensemble_challenges)
        if challenge_count > 0:
            complexity_score += challenge_count * 1.3
            ensemble_moments.append(f"Ensemble challenges: {challenge_count}")
        
        final_score = min(10.0, complexity_score)
        
        return final_score, ensemble_moments[:5]
    
    def analyze_solo_demands(self, scene: SceneData) -> Tuple[float, List[str]]:
        """Analyze individual performance challenges and showcase opportunities"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes}".lower()
        
        solo_opportunities = []
        demands_score = 0.0
        
        # Analyze solo patterns
        for category, patterns in self.solo_patterns.items():
            category_count = 0
            for pattern in patterns:
                category_count += len(re.findall(pattern, all_text))
            
            if category_count > 0:
                # Score based on demand type
                demand_weights = {
                    "featured_solos": 1.5,
                    "character_moments": 1.2,
                    "vocal_showcases": 1.8,
                    "solo_staging": 1.0
                }
                demands_score += category_count * demand_weights.get(category, 1.0)
                solo_opportunities.append(f"{category.replace('_', ' ').title()}: {category_count}")
        
        # Look for specific solo challenges
        solo_challenges = [
            r'\b(?:demanding solo|challenging vocal|difficult|virtuosic)\b',
            r'\b(?:high notes|vocal range|belt|powerful)\b',
            r'\b(?:emotional depth|character work|acting)\b',
            r'\b(?:spotlight moment|featured performance|showcase)\b'
        ]
        
        challenge_count = sum(len(re.findall(pattern, all_text)) for pattern in solo_challenges)
        if challenge_count > 0:
            demands_score += challenge_count * 1.4
            solo_opportunities.append(f"Solo challenges: {challenge_count}")
        
        # Character development opportunities
        character_development = [
            r'\b(?:character arc|personal growth|transformation)\b',
            r'\b(?:emotional journey|inner conflict|revelation)\b',
            r'\b(?:backstory|motivation|personal story)\b'
        ]
        
        character_count = sum(len(re.findall(pattern, all_text)) for pattern in character_development)
        if character_count > 0:
            demands_score += character_count * 1.1
            solo_opportunities.append(f"Character development: {character_count}")
        
        final_score = min(10.0, demands_score)
        
        return final_score, solo_opportunities[:5]
    
    def analyze_balance_integration(self, scene: SceneData) -> Tuple[float, List[str]]:
        """Analyze how well ensemble and solo elements work together"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes}".lower()
        
        integration_techniques = []
        integration_score = 0.0
        
        # Analyze integration patterns
        for technique, patterns in self.integration_patterns.items():
            technique_count = 0
            for pattern in patterns:
                technique_count += len(re.findall(pattern, all_text))
            
            if technique_count > 0:
                # Score based on integration sophistication
                technique_weights = {
                    "seamless_transitions": 2.0,
                    "alternating_structure": 1.3,
                    "layered_approach": 1.7,
                    "contrasted_sections": 1.2
                }
                integration_score += technique_count * technique_weights.get(technique, 1.0)
                integration_techniques.append(f"{technique.replace('_', ' ').title()}: {technique_count}")
        
        # Look for specific integration elements
        integration_elements = [
            r'\b(?:builds from solo to ensemble|grows into group)\b',
            r'\b(?:ensemble supports solo|backup|accompaniment)\b',
            r'\b(?:weaves together|intertwines|connects)\b',
            r'\b(?:unified vision|cohesive|integrated)\b'
        ]
        
        element_count = sum(len(re.findall(pattern, all_text)) for pattern in integration_elements)
        if element_count > 0:
            integration_score += element_count * 1.5
            integration_techniques.append(f"Integration elements: {element_count}")
        
        # Musical integration
        musical_integration = [
            r'\b(?:harmonic support|vocal arrangement|orchestration)\b',
            r'\b(?:countermelody|harmony line|backing vocals)\b',
            r'\b(?:musical conversation|call and response)\b'
        ]
        
        musical_count = sum(len(re.findall(pattern, all_text)) for pattern in musical_integration)
        if musical_count > 0:
            integration_score += musical_count * 1.3
            integration_techniques.append(f"Musical integration: {musical_count}")
        
        final_score = min(10.0, integration_score)
        
        return final_score, integration_techniques[:5]
    
    def analyze_performance_variety(self, scene: SceneData) -> Tuple[float, List[str]]:
        """Analyze range and diversity of performance opportunities"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes}".lower()
        
        variety_elements = []
        variety_score = 0.0
        
        # Count different types of performance opportunities
        variety_types = {
            "vocal_styles": [
                r'\b(?:ballad|uptempo|jazz|rock|classical|folk|pop)\b',
                r'\b(?:aria|recitative|rap|spoken word|chant)\b'
            ],
            "emotional_ranges": [
                r'\b(?:joyful|sad|angry|fearful|surprised|disgusted)\b',
                r'\b(?:romantic|comedic|dramatic|tragic|triumphant)\b'
            ],
            "performance_styles": [
                r'\b(?:intimate|powerful|gentle|explosive|subtle)\b',
                r'\b(?:theatrical|naturalistic|stylized|abstract)\b'
            ],
            "character_types": [
                r'\b(?:protagonist|antagonist|comic relief|romantic lead)\b',
                r'\b(?:narrator|supporting|ensemble|featured)\b'
            ]
        }
        
        for variety_type, patterns in variety_types.items():
            unique_elements = set()
            for pattern in patterns:
                matches = re.findall(pattern, all_text)
                unique_elements.update(matches)
            
            if unique_elements:
                variety_count = len(unique_elements)
                variety_score += variety_count * 0.8
                variety_elements.append(f"{variety_type.replace('_', ' ').title()}: {variety_count} types")
        
        # Check for dynamic range
        dynamic_elements = [
            r'\b(?:builds|crescendo|diminuendo|climax)\b',
            r'\b(?:soft|loud|quiet|powerful|gentle|intense)\b',
            r'\b(?:varies|changes|shifts|contrasts)\b'
        ]
        
        dynamic_count = sum(len(re.findall(pattern, all_text)) for pattern in dynamic_elements)
        if dynamic_count > 0:
            variety_score += dynamic_count * 0.5
            variety_elements.append(f"Dynamic range: {dynamic_count}")
        
        # Check for role diversity
        role_diversity = [
            r'\b(?:multiple characters|different roles|various parts)\b',
            r'\b(?:versatility|range|flexibility|adaptability)\b',
            r'\b(?:ensemble member|soloist|dancer|actor)\b'
        ]
        
        role_count = sum(len(re.findall(pattern, all_text)) for pattern in role_diversity)
        if role_count > 0:
            variety_score += role_count * 0.7
            variety_elements.append(f"Role diversity: {role_count}")
        
        final_score = min(10.0, variety_score)
        
        return final_score, variety_elements[:5]
    
    def determine_ensemble_style(self, percentages: Dict[str, float], scene: SceneData) -> str:
        """Determine the primary ensemble style"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes}".lower()
        
        ensemble_pct = percentages.get("ensemble", 0)
        
        if ensemble_pct > 60:
            return "Chorus Heavy"
        elif ensemble_pct > 30:
            if re.search(r'\b(?:full company|entire cast|everyone)\b', all_text):
                return "Full Company"
            else:
                return "Small Group"
        else:
            return "Minimal"
    
    def determine_solo_prominence(self, percentages: Dict[str, float], scene: SceneData) -> str:
        """Determine the level of solo prominence"""
        solo_pct = percentages.get("solo", 0)
        
        if solo_pct > 60:
            return "Featured"
        elif solo_pct > 30:
            return "Balanced"
        elif solo_pct > 10:
            return "Supporting"
        else:
            return "Background"
    
    def determine_integration_approach(self, scene: SceneData) -> str:
        """Determine the primary integration approach"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes}".lower()
        
        approach_scores = {}
        for approach, patterns in self.integration_patterns.items():
            score = sum(len(re.findall(pattern, all_text)) for pattern in patterns)
            if score > 0:
                approach_scores[approach] = score
        
        if approach_scores:
            top_approach = max(approach_scores, key=approach_scores.get)
            return top_approach.replace('_', ' ').title()
        else:
            return "Contrasted"
    
    def determine_performance_scope(self, scene: SceneData) -> str:
        """Determine the overall performance scope"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes}".lower()
        
        if re.search(r'\b(?:spectacular|grand|epic|massive|huge)\b', all_text):
            return "Epic"
        elif re.search(r'\b(?:big|large|full|company|cast)\b', all_text):
            return "Spectacular"
        elif re.search(r'\b(?:moderate|medium|standard)\b', all_text):
            return "Moderate"
        else:
            return "Intimate"
    
    def analyze_scene_ensemble_solo(self, scene: SceneData) -> EnsembleSoloAnalysis:
        """Perform comprehensive ensemble vs solo performance analysis"""
        analysis_start = time.time()
        
        print(f"🎭 Analyzing ensemble/solo balance for: {scene.title}")
        
        # Extract performance elements
        performance_elements = self.extract_performance_elements(scene)
        print(f"   🎭 Found {len(performance_elements['ensemble_samples'])} ensemble elements")
        print(f"   🎤 Found {len(performance_elements['solo_samples'])} solo elements")
        
        # Perform component analyses
        percentages, balance_score = self.analyze_performance_breakdown(scene)
        ensemble_score, ensemble_moments = self.analyze_ensemble_complexity(scene)
        solo_score, solo_opportunities = self.analyze_solo_demands(scene)
        integration_score, integration_techniques = self.analyze_balance_integration(scene)
        variety_score, variety_elements = self.analyze_performance_variety(scene)
        
        # Determine performance characteristics
        ensemble_style = self.determine_ensemble_style(percentages, scene)
        solo_prominence = self.determine_solo_prominence(percentages, scene)
        integration_approach = self.determine_integration_approach(scene)
        performance_scope = self.determine_performance_scope(scene)
        
        # Calculate overall performance score
        overall_score = (ensemble_score * 0.25 + solo_score * 0.25 + 
                        integration_score * 0.25 + variety_score * 0.25)
        
        # Identify performance strengths
        performance_strengths = []
        if ensemble_score >= 7.0:
            performance_strengths.append("Strong ensemble requirements")
        if solo_score >= 7.0:
            performance_strengths.append("Excellent solo opportunities")
        if integration_score >= 7.0:
            performance_strengths.append("Well-integrated performance elements")
        if variety_score >= 7.0:
            performance_strengths.append("Diverse performance opportunities")
        
        analysis_time = time.time() - analysis_start
        
        print(f"   🎭 Ensemble: {ensemble_score:.1f}/10")
        print(f"   🎤 Solo: {solo_score:.1f}/10")
        print(f"   🤝 Integration: {integration_score:.1f}/10")
        print(f"   🎨 Variety: {variety_score:.1f}/10")
        print(f"   🏆 Overall Performance Score: {overall_score:.1f}/10")
        print(f"   📈 Style: {ensemble_style} | Prominence: {solo_prominence} | Scope: {performance_scope}")
        
        return EnsembleSoloAnalysis(
            scene_title=scene.title,
            ensemble_complexity_score=ensemble_score,
            solo_demands_score=solo_score,
            balance_integration_score=integration_score,
            performance_variety_score=variety_score,
            overall_performance_score=overall_score,
            performance_breakdown=percentages,
            ensemble_moments=ensemble_moments,
            solo_opportunities=solo_opportunities,
            integration_techniques=integration_techniques,
            performance_strengths=performance_strengths,
            ensemble_style=ensemble_style,
            solo_prominence=solo_prominence,
            integration_approach=integration_approach,
            performance_scope=performance_scope,
            analysis_time=analysis_time
        )

def run_ensemble_solo_analysis():
    """Run ensemble vs solo performance analysis on all musicals"""
    
    print("🎭🎤 ENSEMBLE VS SOLO PERFORMANCE ANALYSIS - FULL IMPULSE!")
    print("=" * 60)
    print("Analyzing group vs individual performance requirements")
    print("Components: Ensemble Complexity, Solo Demands, Integration, Variety\n")
    
    analyzer = EnsembleSoloAnalyzer()
    
    # Musical scenes for ensemble/solo analysis
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
            print(f"🎪 PERFORMANCE ANALYSIS {i}/6: {scene_info['musical']}")
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
            
            # Perform ensemble/solo analysis
            analysis = analyzer.analyze_scene_ensemble_solo(scene)
            
            # Format result
            result = {
                "rank": i,
                "musical_name": scene_info['musical'],
                "genre": scene_info['genre'],
                "scene_title": analysis.scene_title,
                "performance_scores": {
                    "overall_performance_score": round(analysis.overall_performance_score, 2),
                    "ensemble_complexity_score": round(analysis.ensemble_complexity_score, 2),
                    "solo_demands_score": round(analysis.solo_demands_score, 2),
                    "balance_integration_score": round(analysis.balance_integration_score, 2),
                    "performance_variety_score": round(analysis.performance_variety_score, 2)
                },
                "performance_characteristics": {
                    "ensemble_style": analysis.ensemble_style,
                    "solo_prominence": analysis.solo_prominence,
                    "integration_approach": analysis.integration_approach,
                    "performance_scope": analysis.performance_scope
                },
                "performance_breakdown": {
                    "ensemble_percent": round(analysis.performance_breakdown.get("ensemble", 0), 1),
                    "solo_percent": round(analysis.performance_breakdown.get("solo", 0), 1),
                    "mixed_percent": round(analysis.performance_breakdown.get("mixed", 0), 1)
                },
                "performance_details": {
                    "ensemble_moments": analysis.ensemble_moments,
                    "solo_opportunities": analysis.solo_opportunities,
                    "integration_techniques": analysis.integration_techniques,
                    "performance_strengths": analysis.performance_strengths
                },
                "analysis_time": round(analysis.analysis_time, 2)
            }
            
            results.append(result)
            print()
            
        except Exception as e:
            print(f"❌ Error analyzing {scene_info['musical']}: {e}")
            continue
    
    total_time = time.time() - total_start
    
    # Sort by overall performance score
    results.sort(key=lambda x: x['performance_scores']['overall_performance_score'], reverse=True)
    
    # Update rankings
    for i, result in enumerate(results, 1):
        result['rank'] = i
    
    print("=" * 60)
    print("🏆 ENSEMBLE VS SOLO PERFORMANCE RANKINGS")
    print("=" * 60)
    
    if results:
        # Calculate statistics
        performance_scores = [r['performance_scores']['overall_performance_score'] for r in results]
        collection_average = sum(performance_scores) / len(performance_scores)
        score_range = max(performance_scores) - min(performance_scores)
        
        print(f"Collection Average: {collection_average:.1f}/10.0")
        print(f"Score Range: {score_range:.1f} points")
        print(f"Analysis Time: {total_time:.1f} seconds")
        print(f"Musicals Analyzed: {len(results)}/6")
        print()
        
        # Component averages
        ensemble_avg = sum(r['performance_scores']['ensemble_complexity_score'] for r in results) / len(results)
        solo_avg = sum(r['performance_scores']['solo_demands_score'] for r in results) / len(results)
        integration_avg = sum(r['performance_scores']['balance_integration_score'] for r in results) / len(results)
        variety_avg = sum(r['performance_scores']['performance_variety_score'] for r in results) / len(results)
        
        print("📊 COMPONENT AVERAGES:")
        print(f"   Ensemble Complexity: {ensemble_avg:.1f}/10")
        print(f"   Solo Demands: {solo_avg:.1f}/10")
        print(f"   Balance Integration: {integration_avg:.1f}/10")
        print(f"   Performance Variety: {variety_avg:.1f}/10")
        print()
        
        # Detailed rankings
        print("🎭 DETAILED PERFORMANCE RANKINGS:")
        for result in results:
            scores = result['performance_scores']
            chars = result['performance_characteristics']
            breakdown = result['performance_breakdown']
            print(f"{result['rank']}. {result['musical_name']}")
            print(f"   Overall: {scores['overall_performance_score']}/10 | Genre: {result['genre']}")
            print(f"   Ens:{scores['ensemble_complexity_score']:.1f} Solo:{scores['solo_demands_score']:.1f} Int:{scores['balance_integration_score']:.1f} Var:{scores['performance_variety_score']:.1f}")
            print(f"   Performance: {breakdown['ensemble_percent']:.0f}% ensemble, {breakdown['solo_percent']:.0f}% solo, {breakdown['mixed_percent']:.0f}% mixed")
            print(f"   Style: {chars['ensemble_style']} | Prominence: {chars['solo_prominence']} | Scope: {chars['performance_scope']}")
            print()
        
        # Performance pattern analysis
        print("🎭🎤 ENSEMBLE-SOLO PERFORMANCE PATTERNS:")
        
        # Ensemble styles
        ensemble_styles = {}
        for result in results:
            style = result['performance_characteristics']['ensemble_style']
            ensemble_styles[style] = ensemble_styles.get(style, 0) + 1
        
        print("   Ensemble Styles:")
        for style, count in ensemble_styles.items():
            print(f"     {style}: {count} musicals")
        
        # Solo prominence levels
        solo_levels = {}
        for result in results:
            level = result['performance_characteristics']['solo_prominence']
            solo_levels[level] = solo_levels.get(level, 0) + 1
        
        print("   Solo Prominence Levels:")
        for level, count in solo_levels.items():
            print(f"     {level}: {count} musicals")
        
        # Average performance breakdown
        avg_ensemble = sum(r['performance_breakdown']['ensemble_percent'] for r in results) / len(results)
        avg_solo = sum(r['performance_breakdown']['solo_percent'] for r in results) / len(results)
        avg_mixed = sum(r['performance_breakdown']['mixed_percent'] for r in results) / len(results)
        
        print(f"   Collection Performance Averages:")
        print(f"     Ensemble: {avg_ensemble:.1f}%")
        print(f"     Solo: {avg_solo:.1f}%")
        print(f"     Mixed: {avg_mixed:.1f}%")
        
        # Save results
        output_data = {
            "analysis_metadata": {
                "analysis_type": "Ensemble vs Solo Performance Requirements",
                "analysis_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_musicals": len(results),
                "collection_average": round(collection_average, 2),
                "score_range": round(score_range, 2),
                "analysis_time_seconds": round(total_time, 1),
                "component_averages": {
                    "ensemble_complexity": round(ensemble_avg, 2),
                    "solo_demands": round(solo_avg, 2),
                    "balance_integration": round(integration_avg, 2),
                    "performance_variety": round(variety_avg, 2)
                },
                "performance_averages": {
                    "ensemble_percent": round(avg_ensemble, 1),
                    "solo_percent": round(avg_solo, 1),
                    "mixed_percent": round(avg_mixed, 1)
                }
            },
            "performance_rankings": results,
            "performance_patterns": {
                "ensemble_styles": ensemble_styles,
                "solo_prominence_levels": solo_levels
            }
        }
        
        with open("ENSEMBLE_solo_analysis.json", 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Performance analysis saved to: ENSEMBLE_solo_analysis.json")
        print("🎭🎤 Ensemble vs Solo Performance Analysis complete - FULL IMPULSE ACHIEVED!")
        
        return results
    
    else:
        print("❌ No analyses completed")
        return []

if __name__ == "__main__":
    print("🚀 Starting Ensemble vs Solo Performance Analysis - FULL IMPULSE!")
    run_ensemble_solo_analysis()