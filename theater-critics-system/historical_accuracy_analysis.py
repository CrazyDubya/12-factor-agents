#!/usr/bin/env python3
"""
Historical Accuracy & Research Quality Analysis
Evaluates authenticity, period detail, and scholarly rigor in musical content
"""

import json
import re
import time
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
from main import SceneData

@dataclass
class HistoricalAccuracyAnalysis:
    """Results of historical accuracy and research quality analysis"""
    scene_title: str
    period_authenticity_score: float      # 0-10 - Accuracy of historical period details
    research_depth_score: float           # 0-10 - Quality and thoroughness of research
    cultural_context_score: float         # 0-10 - Understanding of historical cultural context
    anachronism_penalty_score: float      # 0-10 - Deductions for historical inaccuracies
    overall_accuracy_score: float         # 0-10 - Combined historical accuracy assessment
    
    # Historical analysis details
    historical_references: List[str]
    period_details: List[str]
    cultural_elements: List[str]
    anachronisms_found: List[str]
    research_strengths: List[str]
    
    # Historical characteristics
    time_period: str                       # "Contemporary", "Historical", "Futuristic", "Timeless"
    accuracy_level: str                   # "Excellent", "Good", "Fair", "Poor"
    research_quality: str                 # "Scholarly", "Adequate", "Basic", "Insufficient"
    cultural_sensitivity: str             # "High", "Moderate", "Low", "Problematic"
    
    analysis_time: float

class HistoricalAccuracyAnalyzer:
    """Specialized analyzer for historical accuracy and research quality evaluation"""
    
    def __init__(self):
        # Historical period markers
        self.period_markers = {
            "ancient": [
                r'\b(?:ancient|antiquity|classical|roman|greek|egyptian)\b',
                r'\b(?:bc|bce|ancient times|classical period)\b',
                r'\b(?:pharaoh|emperor|caesar|oracle|temple)\b'
            ],
            "medieval": [
                r'\b(?:medieval|middle ages|feudal|knight|castle)\b',
                r'\b(?:lord|lady|peasant|serf|monastery|abbey)\b',
                r'\b(?:crusade|plague|guild|manor|cathedral)\b'
            ],
            "renaissance": [
                r'\b(?:renaissance|elizabethan|tudor|baroque)\b',
                r'\b(?:court|palace|nobility|patron|artist)\b',
                r'\b(?:printing press|exploration|reformation)\b'
            ],
            "18th_century": [
                r'\b(?:18th century|1700s|georgian|colonial|enlightenment)\b',
                r'\b(?:revolution|founding fathers|powdered wig)\b',
                r'\b(?:carriage|tavern|colonies|independence)\b'
            ],
            "19th_century": [
                r'\b(?:19th century|1800s|victorian|industrial|civil war)\b',
                r'\b(?:railroad|telegraph|gaslight|corset|top hat)\b',
                r'\b(?:factory|immigration|westward expansion)\b'
            ],
            "early_20th": [
                r'\b(?:early 1900s|edwardian|world war|great depression)\b',
                r'\b(?:automobile|telephone|radio|jazz age)\b',
                r'\b(?:prohibition|suffrage|roaring twenties)\b'
            ],
            "mid_20th": [
                r'\b(?:1940s|1950s|world war ii|post-war|cold war)\b',
                r'\b(?:television|suburbs|rock and roll|civil rights)\b',
                r'\b(?:atomic age|space race|baby boom)\b'
            ],
            "late_20th": [
                r'\b(?:1960s|1970s|1980s|1990s|vietnam|watergate)\b',
                r'\b(?:counterculture|disco|punk|grunge|hip hop)\b',
                r'\b(?:computer|internet|cable tv|mtv)\b'
            ],
            "contemporary": [
                r'\b(?:21st century|2000s|2010s|2020s|modern|current)\b',
                r'\b(?:social media|smartphone|streaming|covid)\b',
                r'\b(?:climate change|globalization|digital age)\b'
            ],
            "futuristic": [
                r'\b(?:future|futuristic|sci-fi|dystopian|utopian)\b',
                r'\b(?:space travel|artificial intelligence|robot|cyborg)\b',
                r'\b(?:virtual reality|genetic engineering|terraforming)\b'
            ]
        }
        
        # Research quality indicators
        self.research_indicators = {
            "scholarly_references": [
                r'\b(?:historically accurate|documented|verified|authentic)\b',
                r'\b(?:according to records|historical evidence|primary source)\b',
                r'\b(?:academic research|scholarly|peer reviewed)\b'
            ],
            "specific_details": [
                r'\b(?:specific date|exact location|precise detail)\b',
                r'\b(?:historically|documented fact|recorded event)\b',
                r'\b(?:archaeological evidence|historical record)\b'
            ],
            "cultural_knowledge": [
                r'\b(?:cultural context|social customs|period appropriate)\b',
                r'\b(?:traditional|customary|conventional|typical)\b',
                r'\b(?:cultural significance|historical importance)\b'
            ],
            "linguistic_accuracy": [
                r'\b(?:period language|historical dialect|authentic speech)\b',
                r'\b(?:archaic|old-fashioned|traditional terminology)\b',
                r'\b(?:linguistic|vocabulary|pronunciation)\b'
            ]
        }
        
        # Anachronism detection patterns
        self.anachronism_patterns = {
            "technology_anachronisms": [
                r'\b(?:computer|internet|cell phone|smartphone|television)\b.*\b(?:medieval|ancient|18th century)\b',
                r'\b(?:medieval|ancient)\b.*\b(?:electricity|airplane|automobile)\b',
                r'\b(?:victorian|19th century)\b.*\b(?:radio|television|computer)\b'
            ],
            "language_anachronisms": [
                r'\b(?:okay|cool|awesome|totally|basically)\b.*\b(?:shakespeare|medieval|ancient)\b',
                r'\b(?:ancient|medieval)\b.*\b(?:slang|modern expression|contemporary phrase)\b'
            ],
            "cultural_anachronisms": [
                r'\b(?:democracy|human rights|feminism)\b.*\b(?:ancient|medieval)\b',
                r'\b(?:ancient|medieval)\b.*\b(?:gender equality|civil rights|modern values)\b'
            ],
            "fashion_anachronisms": [
                r'\b(?:jeans|t-shirt|sneakers|baseball cap)\b.*\b(?:victorian|medieval|ancient)\b',
                r'\b(?:ancient|medieval)\b.*\b(?:modern clothing|contemporary fashion)\b'
            ]
        }
        
        # Cultural context elements
        self.cultural_elements = {
            "social_structures": [
                r'\b(?:class system|hierarchy|social order|caste)\b',
                r'\b(?:nobility|aristocracy|commoner|peasant)\b',
                r'\b(?:family structure|marriage customs|social roles)\b'
            ],
            "religious_context": [
                r'\b(?:religious|spiritual|sacred|holy|divine)\b',
                r'\b(?:church|temple|mosque|synagogue|cathedral)\b',
                r'\b(?:priest|monk|bishop|rabbi|imam)\b'
            ],
            "economic_systems": [
                r'\b(?:trade|commerce|merchant|guild|market)\b',
                r'\b(?:currency|money|coin|barter|exchange)\b',
                r'\b(?:agriculture|farming|industry|labor)\b'
            ],
            "political_context": [
                r'\b(?:government|ruler|king|queen|emperor)\b',
                r'\b(?:law|justice|court|trial|punishment)\b',
                r'\b(?:war|peace|treaty|alliance|conflict)\b'
            ]
        }
        
        # Accuracy assessment criteria
        self.accuracy_criteria = {
            "excellent": [
                r'\b(?:meticulously researched|historically precise|authentic)\b',
                r'\b(?:documented accuracy|verified details|scholarly rigor)\b'
            ],
            "good": [
                r'\b(?:generally accurate|well-researched|appropriate)\b',
                r'\b(?:historically sound|reasonable accuracy)\b'
            ],
            "fair": [
                r'\b(?:somewhat accurate|basic research|adequate)\b',
                r'\b(?:minor inaccuracies|generally appropriate)\b'
            ],
            "poor": [
                r'\b(?:inaccurate|anachronistic|poorly researched)\b',
                r'\b(?:historical errors|inappropriate|unrealistic)\b'
            ]
        }
    
    def extract_historical_elements(self, scene: SceneData) -> Dict[str, List[str]]:
        """Extract historical references and period details"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes}"
        
        historical_elements = {
            "period_references": [],
            "cultural_references": [],
            "research_evidence": [],
            "potential_anachronisms": []
        }
        
        # Extract period references
        for period, patterns in self.period_markers.items():
            for pattern in patterns:
                matches = re.finditer(pattern, all_text, re.IGNORECASE)
                for match in matches:
                    context = self._get_context(all_text, match.start(), match.end())
                    historical_elements["period_references"].append(f"{period}: {context}")
        
        # Extract cultural references
        for category, patterns in self.cultural_elements.items():
            for pattern in patterns:
                matches = re.finditer(pattern, all_text, re.IGNORECASE)
                for match in matches:
                    context = self._get_context(all_text, match.start(), match.end())
                    historical_elements["cultural_references"].append(f"{category}: {context}")
        
        return historical_elements
    
    def _get_context(self, text: str, start: int, end: int, context_size: int = 50) -> str:
        """Get context around a match"""
        context_start = max(0, start - context_size)
        context_end = min(len(text), end + context_size)
        context = text[context_start:context_end].strip()
        return context[:80] + "..." if len(context) > 80 else context
    
    def analyze_period_authenticity(self, scene: SceneData) -> Tuple[float, List[str]]:
        """Analyze accuracy of historical period details"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes}".lower()
        
        period_details = []
        authenticity_score = 0.0
        
        # Identify time period
        period_scores = {}
        for period, patterns in self.period_markers.items():
            score = sum(len(re.findall(pattern, all_text)) for pattern in patterns)
            if score > 0:
                period_scores[period] = score
        
        if period_scores:
            dominant_period = max(period_scores, key=period_scores.get)
            period_strength = period_scores[dominant_period]
            authenticity_score += period_strength * 1.2
            period_details.append(f"Identified period: {dominant_period} ({period_strength} references)")
        
        # Check for period-appropriate details
        period_appropriate = [
            r'\b(?:period accurate|historically correct|authentic)\b',
            r'\b(?:period costume|historical dress|appropriate attire)\b',
            r'\b(?:period music|traditional song|historical style)\b',
            r'\b(?:period language|historical dialect|authentic speech)\b'
        ]
        
        appropriate_count = sum(len(re.findall(pattern, all_text)) for pattern in period_appropriate)
        if appropriate_count > 0:
            authenticity_score += appropriate_count * 1.5
            period_details.append(f"Period-appropriate elements: {appropriate_count}")
        
        # Look for specific historical details
        specific_details = [
            r'\b(?:specific date|exact year|precise location)\b',
            r'\b(?:historical figure|real person|documented event)\b',
            r'\b(?:historical fact|recorded incident|verified detail)\b'
        ]
        
        detail_count = sum(len(re.findall(pattern, all_text)) for pattern in specific_details)
        if detail_count > 0:
            authenticity_score += detail_count * 1.8
            period_details.append(f"Specific historical details: {detail_count}")
        
        final_score = min(10.0, authenticity_score)
        
        return final_score, period_details[:5]
    
    def analyze_research_depth(self, scene: SceneData) -> Tuple[float, List[str]]:
        """Analyze quality and thoroughness of research"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes}".lower()
        
        research_evidence = []
        research_score = 0.0
        
        # Analyze research quality indicators
        for category, patterns in self.research_indicators.items():
            category_count = 0
            for pattern in patterns:
                category_count += len(re.findall(pattern, all_text))
            
            if category_count > 0:
                # Score based on research quality type
                quality_weights = {
                    "scholarly_references": 2.0,
                    "specific_details": 1.5,
                    "cultural_knowledge": 1.3,
                    "linguistic_accuracy": 1.2
                }
                research_score += category_count * quality_weights.get(category, 1.0)
                research_evidence.append(f"{category.replace('_', ' ').title()}: {category_count}")
        
        # Look for depth indicators
        depth_indicators = [
            r'\b(?:extensively researched|thoroughly documented|comprehensive study)\b',
            r'\b(?:primary sources|archival research|historical documents)\b',
            r'\b(?:expert consultation|academic collaboration|scholarly review)\b',
            r'\b(?:detailed analysis|in-depth study|comprehensive examination)\b'
        ]
        
        depth_count = sum(len(re.findall(pattern, all_text)) for pattern in depth_indicators)
        if depth_count > 0:
            research_score += depth_count * 1.8
            research_evidence.append(f"Research depth indicators: {depth_count}")
        
        # Check for bibliography/source references
        source_indicators = [
            r'\b(?:source|reference|bibliography|citation)\b',
            r'\b(?:based on|according to|derived from|inspired by)\b',
            r'\b(?:historical record|documented in|found in archives)\b'
        ]
        
        source_count = sum(len(re.findall(pattern, all_text)) for pattern in source_indicators)
        if source_count > 0:
            research_score += source_count * 1.4
            research_evidence.append(f"Source references: {source_count}")
        
        final_score = min(10.0, research_score)
        
        return final_score, research_evidence[:5]
    
    def analyze_cultural_context(self, scene: SceneData) -> Tuple[float, List[str]]:
        """Analyze understanding of historical cultural context"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes}".lower()
        
        cultural_elements = []
        context_score = 0.0
        
        # Analyze cultural context elements
        for category, patterns in self.cultural_elements.items():
            category_count = 0
            for pattern in patterns:
                category_count += len(re.findall(pattern, all_text))
            
            if category_count > 0:
                # Score based on cultural element importance
                element_weights = {
                    "social_structures": 1.5,
                    "religious_context": 1.4,
                    "economic_systems": 1.3,
                    "political_context": 1.2
                }
                context_score += category_count * element_weights.get(category, 1.0)
                cultural_elements.append(f"{category.replace('_', ' ').title()}: {category_count}")
        
        # Look for cultural sensitivity indicators
        sensitivity_indicators = [
            r'\b(?:culturally sensitive|respectful portrayal|appropriate representation)\b',
            r'\b(?:cultural understanding|historical perspective|period mindset)\b',
            r'\b(?:avoids stereotypes|nuanced portrayal|complex representation)\b'
        ]
        
        sensitivity_count = sum(len(re.findall(pattern, all_text)) for pattern in sensitivity_indicators)
        if sensitivity_count > 0:
            context_score += sensitivity_count * 1.6
            cultural_elements.append(f"Cultural sensitivity: {sensitivity_count}")
        
        # Check for diverse perspectives
        perspective_indicators = [
            r'\b(?:multiple perspectives|different viewpoints|various voices)\b',
            r'\b(?:marginalized groups|underrepresented|diverse representation)\b',
            r'\b(?:complex portrayal|nuanced understanding|multifaceted)\b'
        ]
        
        perspective_count = sum(len(re.findall(pattern, all_text)) for pattern in perspective_indicators)
        if perspective_count > 0:
            context_score += perspective_count * 1.3
            cultural_elements.append(f"Diverse perspectives: {perspective_count}")
        
        final_score = min(10.0, context_score)
        
        return final_score, cultural_elements[:5]
    
    def analyze_anachronism_penalty(self, scene: SceneData) -> Tuple[float, List[str]]:
        """Identify and penalize historical inaccuracies"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes}".lower()
        
        anachronisms_found = []
        penalty_score = 10.0  # Start with perfect score, deduct for errors
        
        # Check for anachronisms
        for category, patterns in self.anachronism_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, all_text)
                if matches:
                    penalty_score -= len(matches) * 2.0  # Heavy penalty
                    anachronisms_found.append(f"{category.replace('_', ' ').title()}: {len(matches)} found")
        
        # Look for general historical errors
        error_patterns = [
            r'\b(?:historically inaccurate|anachronistic|out of place)\b',
            r'\b(?:impossible for the period|didn\'t exist then|not invented yet)\b',
            r'\b(?:modern concept|contemporary idea|current thinking)\b'
        ]
        
        error_count = sum(len(re.findall(pattern, all_text)) for pattern in error_patterns)
        if error_count > 0:
            penalty_score -= error_count * 1.5
            anachronisms_found.append(f"General historical errors: {error_count}")
        
        # Check for inappropriate modern references
        modern_references = [
            r'\b(?:social media|internet|computer|smartphone|television)\b',
            r'\b(?:democracy|human rights|gender equality|civil rights)\b',
            r'\b(?:modern slang|contemporary expression|current terminology)\b'
        ]
        
        # Only penalize if scene is supposed to be historical
        historical_markers = sum(len(re.findall(pattern, all_text)) 
                                for patterns in list(self.period_markers.values())[:-2]  # Exclude contemporary and futuristic
                                for pattern in patterns)
        
        if historical_markers > 0:  # Only check if scene claims to be historical
            modern_count = sum(len(re.findall(pattern, all_text)) for pattern in modern_references)
            if modern_count > 0:
                penalty_score -= modern_count * 1.0
                anachronisms_found.append(f"Inappropriate modern references: {modern_count}")
        
        final_score = max(0.0, penalty_score)
        
        return final_score, anachronisms_found[:5]
    
    def determine_time_period(self, scene: SceneData) -> str:
        """Determine the primary time period of the scene"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes}".lower()
        
        period_scores = {}
        for period, patterns in self.period_markers.items():
            score = sum(len(re.findall(pattern, all_text)) for pattern in patterns)
            if score > 0:
                period_scores[period] = score
        
        if period_scores:
            dominant_period = max(period_scores, key=period_scores.get)
            return dominant_period.replace('_', ' ').title()
        else:
            return "Timeless"
    
    def determine_accuracy_level(self, overall_score: float) -> str:
        """Determine the overall accuracy level"""
        if overall_score >= 8.0:
            return "Excellent"
        elif overall_score >= 6.0:
            return "Good"
        elif overall_score >= 4.0:
            return "Fair"
        else:
            return "Poor"
    
    def determine_research_quality(self, research_score: float) -> str:
        """Determine the research quality level"""
        if research_score >= 8.0:
            return "Scholarly"
        elif research_score >= 6.0:
            return "Adequate"
        elif research_score >= 4.0:
            return "Basic"
        else:
            return "Insufficient"
    
    def determine_cultural_sensitivity(self, cultural_score: float) -> str:
        """Determine the cultural sensitivity level"""
        if cultural_score >= 8.0:
            return "High"
        elif cultural_score >= 6.0:
            return "Moderate"
        elif cultural_score >= 4.0:
            return "Low"
        else:
            return "Problematic"
    
    def analyze_scene_historical_accuracy(self, scene: SceneData) -> HistoricalAccuracyAnalysis:
        """Perform comprehensive historical accuracy analysis"""
        analysis_start = time.time()
        
        print(f"📚 Analyzing historical accuracy for: {scene.title}")
        
        # Extract historical elements
        historical_elements = self.extract_historical_elements(scene)
        print(f"   🏛️ Found {len(historical_elements['period_references'])} period references")
        print(f"   🎭 Found {len(historical_elements['cultural_references'])} cultural references")
        
        # Perform component analyses
        authenticity_score, period_details = self.analyze_period_authenticity(scene)
        research_score, research_evidence = self.analyze_research_depth(scene)
        cultural_score, cultural_elements = self.analyze_cultural_context(scene)
        penalty_score, anachronisms = self.analyze_anachronism_penalty(scene)
        
        # Determine historical characteristics
        time_period = self.determine_time_period(scene)
        
        # Calculate overall accuracy score
        overall_score = (authenticity_score * 0.3 + research_score * 0.25 + 
                        cultural_score * 0.25 + penalty_score * 0.2)
        
        accuracy_level = self.determine_accuracy_level(overall_score)
        research_quality = self.determine_research_quality(research_score)
        cultural_sensitivity = self.determine_cultural_sensitivity(cultural_score)
        
        # Identify research strengths
        research_strengths = []
        if authenticity_score >= 7.0:
            research_strengths.append("Strong period authenticity")
        if research_score >= 7.0:
            research_strengths.append("Thorough research depth")
        if cultural_score >= 7.0:
            research_strengths.append("Excellent cultural context")
        if penalty_score >= 8.0:
            research_strengths.append("Minimal historical errors")
        
        analysis_time = time.time() - analysis_start
        
        print(f"   🏛️ Period Auth: {authenticity_score:.1f}/10")
        print(f"   📖 Research: {research_score:.1f}/10")
        print(f"   🎭 Cultural: {cultural_score:.1f}/10")
        print(f"   ⚖️ Accuracy: {penalty_score:.1f}/10")
        print(f"   🏆 Overall Accuracy Score: {overall_score:.1f}/10")
        print(f"   📈 Period: {time_period} | Level: {accuracy_level} | Quality: {research_quality}")
        
        return HistoricalAccuracyAnalysis(
            scene_title=scene.title,
            period_authenticity_score=authenticity_score,
            research_depth_score=research_score,
            cultural_context_score=cultural_score,
            anachronism_penalty_score=penalty_score,
            overall_accuracy_score=overall_score,
            historical_references=historical_elements["period_references"],
            period_details=period_details,
            cultural_elements=cultural_elements,
            anachronisms_found=anachronisms,
            research_strengths=research_strengths,
            time_period=time_period,
            accuracy_level=accuracy_level,
            research_quality=research_quality,
            cultural_sensitivity=cultural_sensitivity,
            analysis_time=analysis_time
        )

def run_historical_accuracy_analysis():
    """Run historical accuracy analysis on all musicals"""
    
    print("📚🏛️ HISTORICAL ACCURACY & RESEARCH QUALITY ANALYSIS - FULL IMPULSE!")
    print("=" * 70)
    print("Analyzing authenticity, period detail, and scholarly rigor")
    print("Components: Period Authenticity, Research Depth, Cultural Context, Accuracy\n")
    
    analyzer = HistoricalAccuracyAnalyzer()
    
    # Musical scenes for historical accuracy analysis
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
            print(f"🎪 HISTORICAL ANALYSIS {i}/6: {scene_info['musical']}")
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
            
            # Perform historical accuracy analysis
            analysis = analyzer.analyze_scene_historical_accuracy(scene)
            
            # Format result
            result = {
                "rank": i,
                "musical_name": scene_info['musical'],
                "genre": scene_info['genre'],
                "scene_title": analysis.scene_title,
                "accuracy_scores": {
                    "overall_accuracy_score": round(analysis.overall_accuracy_score, 2),
                    "period_authenticity_score": round(analysis.period_authenticity_score, 2),
                    "research_depth_score": round(analysis.research_depth_score, 2),
                    "cultural_context_score": round(analysis.cultural_context_score, 2),
                    "anachronism_penalty_score": round(analysis.anachronism_penalty_score, 2)
                },
                "historical_characteristics": {
                    "time_period": analysis.time_period,
                    "accuracy_level": analysis.accuracy_level,
                    "research_quality": analysis.research_quality,
                    "cultural_sensitivity": analysis.cultural_sensitivity
                },
                "historical_details": {
                    "historical_references": analysis.historical_references[:3],
                    "period_details": analysis.period_details,
                    "cultural_elements": analysis.cultural_elements,
                    "anachronisms_found": analysis.anachronisms_found,
                    "research_strengths": analysis.research_strengths
                },
                "analysis_time": round(analysis.analysis_time, 2)
            }
            
            results.append(result)
            print()
            
        except Exception as e:
            print(f"❌ Error analyzing {scene_info['musical']}: {e}")
            continue
    
    total_time = time.time() - total_start
    
    # Sort by overall accuracy score
    results.sort(key=lambda x: x['accuracy_scores']['overall_accuracy_score'], reverse=True)
    
    # Update rankings
    for i, result in enumerate(results, 1):
        result['rank'] = i
    
    print("=" * 70)
    print("🏆 HISTORICAL ACCURACY & RESEARCH QUALITY RANKINGS")
    print("=" * 70)
    
    if results:
        # Calculate statistics
        accuracy_scores = [r['accuracy_scores']['overall_accuracy_score'] for r in results]
        collection_average = sum(accuracy_scores) / len(accuracy_scores)
        score_range = max(accuracy_scores) - min(accuracy_scores)
        
        print(f"Collection Average: {collection_average:.1f}/10.0")
        print(f"Score Range: {score_range:.1f} points")
        print(f"Analysis Time: {total_time:.1f} seconds")
        print(f"Musicals Analyzed: {len(results)}/6")
        print()
        
        # Component averages
        authenticity_avg = sum(r['accuracy_scores']['period_authenticity_score'] for r in results) / len(results)
        research_avg = sum(r['accuracy_scores']['research_depth_score'] for r in results) / len(results)
        cultural_avg = sum(r['accuracy_scores']['cultural_context_score'] for r in results) / len(results)
        penalty_avg = sum(r['accuracy_scores']['anachronism_penalty_score'] for r in results) / len(results)
        
        print("📊 COMPONENT AVERAGES:")
        print(f"   Period Authenticity: {authenticity_avg:.1f}/10")
        print(f"   Research Depth: {research_avg:.1f}/10")
        print(f"   Cultural Context: {cultural_avg:.1f}/10")
        print(f"   Accuracy (No Penalties): {penalty_avg:.1f}/10")
        print()
        
        # Detailed rankings
        print("📚 DETAILED ACCURACY RANKINGS:")
        for result in results:
            scores = result['accuracy_scores']
            chars = result['historical_characteristics']
            print(f"{result['rank']}. {result['musical_name']}")
            print(f"   Overall: {scores['overall_accuracy_score']}/10 | Genre: {result['genre']}")
            print(f"   Auth:{scores['period_authenticity_score']:.1f} Res:{scores['research_depth_score']:.1f} Cult:{scores['cultural_context_score']:.1f} Acc:{scores['anachronism_penalty_score']:.1f}")
            print(f"   Period: {chars['time_period']} | Level: {chars['accuracy_level']} | Quality: {chars['research_quality']}")
            print(f"   Cultural Sensitivity: {chars['cultural_sensitivity']}")
            print()
        
        # Historical pattern analysis
        print("🏛️ HISTORICAL ACCURACY PATTERNS:")
        
        # Time periods
        time_periods = {}
        for result in results:
            period = result['historical_characteristics']['time_period']
            time_periods[period] = time_periods.get(period, 0) + 1
        
        print("   Time Periods:")
        for period, count in time_periods.items():
            print(f"     {period}: {count} musicals")
        
        # Accuracy levels
        accuracy_levels = {}
        for result in results:
            level = result['historical_characteristics']['accuracy_level']
            accuracy_levels[level] = accuracy_levels.get(level, 0) + 1
        
        print("   Accuracy Levels:")
        for level, count in accuracy_levels.items():
            print(f"     {level}: {count} musicals")
        
        # Research quality distribution
        research_quality = {}
        for result in results:
            quality = result['historical_characteristics']['research_quality']
            research_quality[quality] = research_quality.get(quality, 0) + 1
        
        print("   Research Quality:")
        for quality, count in research_quality.items():
            print(f"     {quality}: {count} musicals")
        
        # Save results
        output_data = {
            "analysis_metadata": {
                "analysis_type": "Historical Accuracy & Research Quality",
                "analysis_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_musicals": len(results),
                "collection_average": round(collection_average, 2),
                "score_range": round(score_range, 2),
                "analysis_time_seconds": round(total_time, 1),
                "component_averages": {
                    "period_authenticity": round(authenticity_avg, 2),
                    "research_depth": round(research_avg, 2),
                    "cultural_context": round(cultural_avg, 2),
                    "anachronism_penalty": round(penalty_avg, 2)
                }
            },
            "accuracy_rankings": results,
            "historical_patterns": {
                "time_periods": time_periods,
                "accuracy_levels": accuracy_levels,
                "research_quality_distribution": research_quality
            }
        }
        
        with open("HISTORICAL_accuracy_analysis.json", 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Historical accuracy analysis saved to: HISTORICAL_accuracy_analysis.json")
        print("📚🏛️ Historical Accuracy & Research Quality Analysis complete - FULL IMPULSE ACHIEVED!")
        
        return results
    
    else:
        print("❌ No analyses completed")
        return []

if __name__ == "__main__":
    print("🚀 Starting Historical Accuracy & Research Quality Analysis - FULL IMPULSE!")
    run_historical_accuracy_analysis()