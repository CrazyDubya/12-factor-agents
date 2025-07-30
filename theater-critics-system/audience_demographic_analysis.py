#!/usr/bin/env python3
"""
Audience Demographic Appeal Analysis
Evaluates appeal across different age groups, cultural backgrounds, and audience segments
"""

import json
import re
import time
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
from main import SceneData

@dataclass
class AudienceDemographicAnalysis:
    """Results of audience demographic appeal analysis"""
    scene_title: str
    age_group_appeal_score: float         # 0-10 - Appeal across different age demographics
    cultural_accessibility_score: float   # 0-10 - Cross-cultural appeal and accessibility
    interest_diversity_score: float       # 0-10 - Appeal to diverse interests and backgrounds
    commercial_viability_score: float     # 0-10 - Mainstream commercial appeal potential
    overall_demographic_score: float      # 0-10 - Combined demographic appeal assessment
    
    # Demographic breakdown
    age_group_breakdown: Dict[str, float]  # Appeal scores for different age groups
    cultural_appeal_factors: List[str]
    interest_categories: List[str]
    commercial_indicators: List[str]
    demographic_strengths: List[str]
    
    # Audience characteristics
    primary_demographic: str               # "Family", "Young Adult", "Adult", "Mature", "Universal"
    cultural_scope: str                   # "Universal", "Western", "Contemporary", "Niche"
    commercial_category: str              # "Mainstream", "Art House", "Cult", "Specialized"
    accessibility_level: str             # "Highly Accessible", "Moderately Accessible", "Selective", "Niche"
    
    analysis_time: float

class AudienceDemographicAnalyzer:
    """Specialized analyzer for audience demographic appeal evaluation"""
    
    def __init__(self):
        # Age group appeal patterns
        self.age_group_patterns = {
            "children": [
                r'\b(?:children|kids|young|playful|innocent|wonder)\b',
                r'\b(?:magic|fantasy|adventure|friendship|learning)\b',
                r'\b(?:bright|colorful|fun|silly|games|animals)\b',
                r'\b(?:family|school|playground|toys|stories)\b'
            ],
            "teens": [
                r'\b(?:teen|teenager|adolescent|youth|coming of age)\b',
                r'\b(?:identity|rebellion|first love|growing up)\b',
                r'\b(?:school|college|peer pressure|independence)\b',
                r'\b(?:energy|passion|dreams|future|change)\b'
            ],
            "young_adults": [
                r'\b(?:young adult|twenties|college|career|relationships)\b',
                r'\b(?:dating|romance|ambition|success|failure)\b',
                r'\b(?:city life|technology|social media|networking)\b',
                r'\b(?:finding yourself|life choices|opportunity)\b'
            ],
            "adults": [
                r'\b(?:adult|mature|responsibility|work|family)\b',
                r'\b(?:marriage|parenting|career|mortgage|stability)\b',
                r'\b(?:complex|sophisticated|nuanced|realistic)\b',
                r'\b(?:life experience|wisdom|compromise|sacrifice)\b'
            ],
            "seniors": [
                r'\b(?:senior|elderly|older|retirement|legacy)\b',
                r'\b(?:grandparent|wisdom|experience|reflection)\b',
                r'\b(?:memory|nostalgia|tradition|heritage)\b',
                r'\b(?:life lessons|mentorship|passing on)\b'
            ]
        }
        
        # Cultural accessibility indicators
        self.cultural_indicators = {
            "universal_themes": [
                r'\b(?:love|family|friendship|hope|loss|joy)\b',
                r'\b(?:human nature|emotion|connection|understanding)\b',
                r'\b(?:universal|common|shared|relatable)\b',
                r'\b(?:timeless|classic|enduring|eternal)\b'
            ],
            "western_cultural": [
                r'\b(?:american|european|western|english speaking)\b',
                r'\b(?:christian|judeo-christian|western values)\b',
                r'\b(?:individualism|democracy|capitalism|freedom)\b',
                r'\b(?:popular culture|mainstream|conventional)\b'
            ],
            "contemporary_references": [
                r'\b(?:modern|current|today|contemporary|recent)\b',
                r'\b(?:technology|internet|social media|digital)\b',
                r'\b(?:current events|trending|viral|popular)\b',
                r'\b(?:generation|millennial|gen z|modern life)\b'
            ],
            "multicultural_elements": [
                r'\b(?:multicultural|diverse|international|global)\b',
                r'\b(?:different cultures|various backgrounds|inclusive)\b',
                r'\b(?:ethnicity|race|nationality|heritage)\b',
                r'\b(?:cross-cultural|world music|global perspective)\b'
            ]
        }
        
        # Interest category patterns
        self.interest_patterns = {
            "music_lovers": [
                r'\b(?:music|musical|song|melody|harmony|rhythm)\b',
                r'\b(?:vocal|instrumental|composition|arrangement)\b',
                r'\b(?:genre|style|performance|concert|album)\b'
            ],
            "theater_enthusiasts": [
                r'\b(?:theater|theatre|stage|drama|performance)\b',
                r'\b(?:acting|directing|lighting|costume|set)\b',
                r'\b(?:broadway|musical theater|theatrical)\b'
            ],
            "romance_fans": [
                r'\b(?:romance|love|relationship|dating|marriage)\b',
                r'\b(?:romantic|passion|intimacy|heartbreak|wedding)\b',
                r'\b(?:couple|partner|soulmate|destiny|forever)\b'
            ],
            "comedy_seekers": [
                r'\b(?:comedy|humor|funny|laugh|joke|wit)\b',
                r'\b(?:amusing|entertaining|hilarious|comedic)\b',
                r'\b(?:satire|parody|irony|sarcasm|playful)\b'
            ],
            "drama_appreciators": [
                r'\b(?:drama|dramatic|serious|intense|emotional)\b',
                r'\b(?:conflict|tension|struggle|crisis|depth)\b',
                r'\b(?:complex|sophisticated|profound|meaningful)\b'
            ],
            "fantasy_enthusiasts": [
                r'\b(?:fantasy|magic|magical|supernatural|mystical)\b',
                r'\b(?:imagination|wonder|enchanting|otherworldly)\b',
                r'\b(?:escape|adventure|quest|heroic|legendary)\b'
            ],
            "sci_fi_fans": [
                r'\b(?:science fiction|sci-fi|futuristic|technology)\b',
                r'\b(?:robot|artificial intelligence|space|future)\b',
                r'\b(?:innovation|progress|evolution|advanced)\b'
            ],
            "social_commentary": [
                r'\b(?:social|political|commentary|message|cause)\b',
                r'\b(?:justice|equality|rights|change|activism)\b',
                r'\b(?:society|culture|system|reform|awareness)\b'
            ]
        }
        
        # Commercial viability indicators
        self.commercial_indicators = {
            "mainstream_appeal": [
                r'\b(?:mainstream|popular|accessible|broad appeal)\b',
                r'\b(?:commercial|marketable|sellable|profitable)\b',
                r'\b(?:mass audience|general public|wide appeal)\b'
            ],
            "star_potential": [
                r'\b(?:star|celebrity|famous|notable|renowned)\b',
                r'\b(?:leading role|showcase|spotlight|featured)\b',
                r'\b(?:breakout|standout|memorable|iconic)\b'
            ],
            "memorable_elements": [
                r'\b(?:memorable|catchy|unforgettable|striking)\b',
                r'\b(?:hook|anthem|signature|standout|highlight)\b',
                r'\b(?:quotable|singable|hummable|infectious)\b'
            ],
            "production_value": [
                r'\b(?:spectacular|impressive|grand|elaborate)\b',
                r'\b(?:high production|quality|professional|polished)\b',
                r'\b(?:budget|expensive|lavish|ambitious)\b'
            ],
            "awards_potential": [
                r'\b(?:award|recognition|prestigious|acclaimed)\b',
                r'\b(?:excellence|outstanding|exceptional|superior)\b',
                r'\b(?:critical acclaim|industry recognition)\b'
            ]
        }
        
        # Accessibility barriers
        self.accessibility_barriers = {
            "complex_themes": [
                r'\b(?:complex|complicated|difficult|challenging)\b',
                r'\b(?:sophisticated|nuanced|subtle|abstract)\b',
                r'\b(?:intellectual|cerebral|philosophical|deep)\b'
            ],
            "niche_references": [
                r'\b(?:obscure|niche|specialized|insider|esoteric)\b',
                r'\b(?:specific knowledge|background required)\b',
                r'\b(?:cult|underground|alternative|fringe)\b'
            ],
            "cultural_barriers": [
                r'\b(?:cultural specific|culturally bound|insider knowledge)\b',
                r'\b(?:language barrier|translation|foreign)\b',
                r'\b(?:regional|local|specific community)\b'
            ],
            "mature_content": [
                r'\b(?:mature|adult|explicit|graphic|intense)\b',
                r'\b(?:violence|sexuality|profanity|disturbing)\b',
                r'\b(?:parental guidance|not suitable|restricted)\b'
            ]
        }
    
    def extract_demographic_elements(self, scene: SceneData) -> Dict[str, List[str]]:
        """Extract audience appeal elements"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes}"
        
        demographic_elements = {
            "age_group_indicators": [],
            "cultural_markers": [],
            "interest_signals": [],
            "commercial_elements": []
        }
        
        # Extract age group indicators
        for age_group, patterns in self.age_group_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, all_text, re.IGNORECASE)
                for match in matches:
                    context = self._get_context(all_text, match.start(), match.end())
                    demographic_elements["age_group_indicators"].append(f"{age_group}: {context}")
        
        # Extract cultural markers
        for category, patterns in self.cultural_indicators.items():
            for pattern in patterns:
                matches = re.finditer(pattern, all_text, re.IGNORECASE)
                for match in matches:
                    context = self._get_context(all_text, match.start(), match.end())
                    demographic_elements["cultural_markers"].append(f"{category}: {context}")
        
        return demographic_elements
    
    def _get_context(self, text: str, start: int, end: int, context_size: int = 50) -> str:
        """Get context around a match"""
        context_start = max(0, start - context_size)
        context_end = min(len(text), end + context_size)
        context = text[context_start:context_end].strip()
        return context[:80] + "..." if len(context) > 80 else context
    
    def analyze_age_group_appeal(self, scene: SceneData) -> Tuple[Dict[str, float], float]:
        """Analyze appeal across different age demographics"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes}".lower()
        
        age_scores = {}
        total_appeal = 0.0
        
        # Analyze each age group
        for age_group, patterns in self.age_group_patterns.items():
            group_score = 0.0
            for pattern in patterns:
                matches = len(re.findall(pattern, all_text))
                group_score += matches * 1.0
            
            # Normalize and cap score
            age_scores[age_group] = min(10.0, group_score)
            total_appeal += age_scores[age_group]
        
        # Calculate average appeal across age groups
        average_appeal = total_appeal / len(age_scores) if age_scores else 0.0
        
        # Bonus for universal themes that appeal to all ages
        universal_patterns = [
            r'\b(?:family|love|friendship|hope|dreams|music)\b',
            r'\b(?:journey|adventure|discovery|growth|change)\b',
            r'\b(?:universal appeal|cross-generational|all ages)\b'
        ]
        
        universal_count = sum(len(re.findall(pattern, all_text)) for pattern in universal_patterns)
        if universal_count > 0:
            average_appeal += universal_count * 0.5
        
        final_score = min(10.0, average_appeal)
        
        return age_scores, final_score
    
    def analyze_cultural_accessibility(self, scene: SceneData) -> Tuple[float, List[str]]:
        """Analyze cross-cultural appeal and accessibility"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes}".lower()
        
        cultural_factors = []
        accessibility_score = 0.0
        
        # Analyze cultural indicators
        for category, patterns in self.cultural_indicators.items():
            category_count = 0
            for pattern in patterns:
                category_count += len(re.findall(pattern, all_text))
            
            if category_count > 0:
                # Score based on accessibility level
                accessibility_weights = {
                    "universal_themes": 2.0,
                    "multicultural_elements": 1.5,
                    "contemporary_references": 1.2,
                    "western_cultural": 0.8
                }
                accessibility_score += category_count * accessibility_weights.get(category, 1.0)
                cultural_factors.append(f"{category.replace('_', ' ').title()}: {category_count}")
        
        # Check for accessibility barriers
        barrier_penalty = 0.0
        for barrier_type, patterns in self.accessibility_barriers.items():
            barrier_count = sum(len(re.findall(pattern, all_text)) for pattern in patterns)
            if barrier_count > 0:
                barrier_penalty += barrier_count * 0.5
                cultural_factors.append(f"Barrier - {barrier_type.replace('_', ' ').title()}: {barrier_count}")
        
        # Apply barrier penalty
        accessibility_score = max(0.0, accessibility_score - barrier_penalty)
        
        # Look for inclusive elements
        inclusive_patterns = [
            r'\b(?:inclusive|diverse|welcoming|accessible)\b',
            r'\b(?:everyone|all people|universal|global)\b',
            r'\b(?:cross-cultural|international|worldwide)\b'
        ]
        
        inclusive_count = sum(len(re.findall(pattern, all_text)) for pattern in inclusive_patterns)
        if inclusive_count > 0:
            accessibility_score += inclusive_count * 1.0
            cultural_factors.append(f"Inclusive elements: {inclusive_count}")
        
        final_score = min(10.0, accessibility_score)
        
        return final_score, cultural_factors[:5]
    
    def analyze_interest_diversity(self, scene: SceneData) -> Tuple[float, List[str]]:
        """Analyze appeal to diverse interests and backgrounds"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes}".lower()
        
        interest_categories = []
        diversity_score = 0.0
        active_interests = 0
        
        # Analyze interest categories
        for interest, patterns in self.interest_patterns.items():
            interest_count = 0
            for pattern in patterns:
                interest_count += len(re.findall(pattern, all_text))
            
            if interest_count > 0:
                diversity_score += interest_count * 0.8
                interest_categories.append(f"{interest.replace('_', ' ').title()}: {interest_count}")
                active_interests += 1
        
        # Bonus for multiple interest categories (indicates broad appeal)
        if active_interests >= 3:
            diversity_score += 2.0
            interest_categories.append(f"Multiple interests engaged: {active_interests}")
        elif active_interests >= 2:
            diversity_score += 1.0
            interest_categories.append(f"Dual interest appeal: {active_interests}")
        
        # Look for crossover appeal
        crossover_patterns = [
            r'\b(?:crossover|appeals to many|broad audience|wide range)\b',
            r'\b(?:something for everyone|diverse appeal|varied interests)\b',
            r'\b(?:multiple demographics|different audiences)\b'
        ]
        
        crossover_count = sum(len(re.findall(pattern, all_text)) for pattern in crossover_patterns)
        if crossover_count > 0:
            diversity_score += crossover_count * 1.5
            interest_categories.append(f"Crossover appeal: {crossover_count}")
        
        final_score = min(10.0, diversity_score)
        
        return final_score, interest_categories[:5]
    
    def analyze_commercial_viability(self, scene: SceneData) -> Tuple[float, List[str]]:
        """Analyze mainstream commercial appeal potential"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes}".lower()
        
        commercial_indicators = []
        viability_score = 0.0
        
        # Analyze commercial indicators
        for category, patterns in self.commercial_indicators.items():
            category_count = 0
            for pattern in patterns:
                category_count += len(re.findall(pattern, all_text))
            
            if category_count > 0:
                # Score based on commercial impact
                commercial_weights = {
                    "mainstream_appeal": 2.0,
                    "memorable_elements": 1.8,
                    "production_value": 1.5,
                    "star_potential": 1.3,
                    "awards_potential": 1.2
                }
                viability_score += category_count * commercial_weights.get(category, 1.0)
                commercial_indicators.append(f"{category.replace('_', ' ').title()}: {category_count}")
        
        # Look for marketability factors
        marketing_factors = [
            r'\b(?:marketable|sellable|promotional|buzzworthy)\b',
            r'\b(?:viral potential|social media|shareable)\b',
            r'\b(?:mass appeal|popular|trendy|zeitgeist)\b',
            r'\b(?:commercial success|box office|profitable)\b'
        ]
        
        marketing_count = sum(len(re.findall(pattern, all_text)) for pattern in marketing_factors)
        if marketing_count > 0:
            viability_score += marketing_count * 1.4
            commercial_indicators.append(f"Marketing potential: {marketing_count}")
        
        # Check for franchise potential
        franchise_patterns = [
            r'\b(?:franchise|sequel|series|brand|intellectual property)\b',
            r'\b(?:merchandising|licensing|spin-off|adaptation)\b',
            r'\b(?:expandable|continuing|ongoing|universe)\b'
        ]
        
        franchise_count = sum(len(re.findall(pattern, all_text)) for pattern in franchise_patterns)
        if franchise_count > 0:
            viability_score += franchise_count * 1.2
            commercial_indicators.append(f"Franchise potential: {franchise_count}")
        
        final_score = min(10.0, viability_score)
        
        return final_score, commercial_indicators[:5]
    
    def determine_primary_demographic(self, age_scores: Dict[str, float]) -> str:
        """Determine the primary target demographic"""
        if not age_scores:
            return "Universal"
        
        # Find the highest scoring age group
        max_score = max(age_scores.values())
        top_groups = [group for group, score in age_scores.items() if score == max_score]
        
        # If multiple groups tie, determine category
        if len(top_groups) >= 3:
            return "Universal"
        elif "children" in top_groups:
            return "Family"
        elif "teens" in top_groups or "young_adults" in top_groups:
            return "Young Adult"
        elif "adults" in top_groups:
            return "Adult"
        elif "seniors" in top_groups:
            return "Mature"
        else:
            return "Universal"
    
    def determine_cultural_scope(self, accessibility_score: float, scene: SceneData) -> str:
        """Determine the cultural scope of appeal"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes}".lower()
        
        if accessibility_score >= 8.0:
            return "Universal"
        elif re.search(r'\b(?:multicultural|international|global)\b', all_text):
            return "International"
        elif re.search(r'\b(?:contemporary|modern|current)\b', all_text):
            return "Contemporary"
        elif re.search(r'\b(?:western|american|english)\b', all_text):
            return "Western"
        else:
            return "Niche"
    
    def determine_commercial_category(self, commercial_score: float) -> str:
        """Determine the commercial category"""
        if commercial_score >= 8.0:
            return "Mainstream"
        elif commercial_score >= 6.0:
            return "Art House"
        elif commercial_score >= 4.0:
            return "Cult"
        else:
            return "Specialized"
    
    def determine_accessibility_level(self, accessibility_score: float, interest_score: float) -> str:
        """Determine the overall accessibility level"""
        combined_score = (accessibility_score + interest_score) / 2
        
        if combined_score >= 8.0:
            return "Highly Accessible"
        elif combined_score >= 6.0:
            return "Moderately Accessible"
        elif combined_score >= 4.0:
            return "Selective"
        else:
            return "Niche"
    
    def analyze_scene_audience_demographics(self, scene: SceneData) -> AudienceDemographicAnalysis:
        """Perform comprehensive audience demographic analysis"""
        analysis_start = time.time()
        
        print(f"👥 Analyzing audience demographics for: {scene.title}")
        
        # Extract demographic elements
        demographic_elements = self.extract_demographic_elements(scene)
        print(f"   🎯 Found {len(demographic_elements['age_group_indicators'])} age group indicators")
        print(f"   🌍 Found {len(demographic_elements['cultural_markers'])} cultural markers")
        
        # Perform component analyses
        age_scores, age_appeal = self.analyze_age_group_appeal(scene)
        accessibility_score, cultural_factors = self.analyze_cultural_accessibility(scene)
        interest_score, interest_categories = self.analyze_interest_diversity(scene)
        commercial_score, commercial_indicators = self.analyze_commercial_viability(scene)
        
        # Determine demographic characteristics
        primary_demographic = self.determine_primary_demographic(age_scores)
        cultural_scope = self.determine_cultural_scope(accessibility_score, scene)
        commercial_category = self.determine_commercial_category(commercial_score)
        accessibility_level = self.determine_accessibility_level(accessibility_score, interest_score)
        
        # Calculate overall demographic score
        overall_score = (age_appeal * 0.3 + accessibility_score * 0.25 + 
                        interest_score * 0.25 + commercial_score * 0.2)
        
        # Identify demographic strengths
        demographic_strengths = []
        if age_appeal >= 7.0:
            demographic_strengths.append("Strong cross-generational appeal")
        if accessibility_score >= 7.0:
            demographic_strengths.append("High cultural accessibility")
        if interest_score >= 7.0:
            demographic_strengths.append("Diverse interest appeal")
        if commercial_score >= 7.0:
            demographic_strengths.append("Strong commercial potential")
        
        analysis_time = time.time() - analysis_start
        
        print(f"   👶👵 Age Appeal: {age_appeal:.1f}/10")
        print(f"   🌍 Cultural Access: {accessibility_score:.1f}/10")
        print(f"   🎯 Interest Diversity: {interest_score:.1f}/10")
        print(f"   💰 Commercial: {commercial_score:.1f}/10")
        print(f"   🏆 Overall Demographic Score: {overall_score:.1f}/10")
        print(f"   📈 Demo: {primary_demographic} | Scope: {cultural_scope} | Category: {commercial_category}")
        
        return AudienceDemographicAnalysis(
            scene_title=scene.title,
            age_group_appeal_score=age_appeal,
            cultural_accessibility_score=accessibility_score,
            interest_diversity_score=interest_score,
            commercial_viability_score=commercial_score,
            overall_demographic_score=overall_score,
            age_group_breakdown=age_scores,
            cultural_appeal_factors=cultural_factors,
            interest_categories=interest_categories,
            commercial_indicators=commercial_indicators,
            demographic_strengths=demographic_strengths,
            primary_demographic=primary_demographic,
            cultural_scope=cultural_scope,
            commercial_category=commercial_category,
            accessibility_level=accessibility_level,
            analysis_time=analysis_time
        )

def run_audience_demographic_analysis():
    """Run audience demographic analysis on all musicals"""
    
    print("👥🎯 AUDIENCE DEMOGRAPHIC APPEAL ANALYSIS - FULL IMPULSE!")
    print("=" * 65)
    print("Analyzing appeal across age groups, cultures, and audience segments")
    print("Components: Age Appeal, Cultural Access, Interest Diversity, Commercial\n")
    
    analyzer = AudienceDemographicAnalyzer()
    
    # Musical scenes for demographic analysis
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
            print(f"🎪 DEMOGRAPHIC ANALYSIS {i}/6: {scene_info['musical']}")
            print("-" * 60)
            
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
            
            # Perform demographic analysis
            analysis = analyzer.analyze_scene_audience_demographics(scene)
            
            # Format result
            result = {
                "rank": i,
                "musical_name": scene_info['musical'],
                "genre": scene_info['genre'],
                "scene_title": analysis.scene_title,
                "demographic_scores": {
                    "overall_demographic_score": round(analysis.overall_demographic_score, 2),
                    "age_group_appeal_score": round(analysis.age_group_appeal_score, 2),
                    "cultural_accessibility_score": round(analysis.cultural_accessibility_score, 2),
                    "interest_diversity_score": round(analysis.interest_diversity_score, 2),
                    "commercial_viability_score": round(analysis.commercial_viability_score, 2)
                },
                "demographic_characteristics": {
                    "primary_demographic": analysis.primary_demographic,
                    "cultural_scope": analysis.cultural_scope,
                    "commercial_category": analysis.commercial_category,
                    "accessibility_level": analysis.accessibility_level
                },
                "age_group_breakdown": {
                    age_group: round(score, 1) for age_group, score in analysis.age_group_breakdown.items()
                },
                "demographic_details": {
                    "cultural_appeal_factors": analysis.cultural_appeal_factors,
                    "interest_categories": analysis.interest_categories,
                    "commercial_indicators": analysis.commercial_indicators,
                    "demographic_strengths": analysis.demographic_strengths
                },
                "analysis_time": round(analysis.analysis_time, 2)
            }
            
            results.append(result)
            print()
            
        except Exception as e:
            print(f"❌ Error analyzing {scene_info['musical']}: {e}")
            continue
    
    total_time = time.time() - total_start
    
    # Sort by overall demographic score
    results.sort(key=lambda x: x['demographic_scores']['overall_demographic_score'], reverse=True)
    
    # Update rankings
    for i, result in enumerate(results, 1):
        result['rank'] = i
    
    print("=" * 65)
    print("🏆 AUDIENCE DEMOGRAPHIC APPEAL RANKINGS")
    print("=" * 65)
    
    if results:
        # Calculate statistics
        demographic_scores = [r['demographic_scores']['overall_demographic_score'] for r in results]
        collection_average = sum(demographic_scores) / len(demographic_scores)
        score_range = max(demographic_scores) - min(demographic_scores)
        
        print(f"Collection Average: {collection_average:.1f}/10.0")
        print(f"Score Range: {score_range:.1f} points")
        print(f"Analysis Time: {total_time:.1f} seconds")
        print(f"Musicals Analyzed: {len(results)}/6")
        print()
        
        # Component averages
        age_avg = sum(r['demographic_scores']['age_group_appeal_score'] for r in results) / len(results)
        cultural_avg = sum(r['demographic_scores']['cultural_accessibility_score'] for r in results) / len(results)
        interest_avg = sum(r['demographic_scores']['interest_diversity_score'] for r in results) / len(results)
        commercial_avg = sum(r['demographic_scores']['commercial_viability_score'] for r in results) / len(results)
        
        print("📊 COMPONENT AVERAGES:")
        print(f"   Age Group Appeal: {age_avg:.1f}/10")
        print(f"   Cultural Accessibility: {cultural_avg:.1f}/10")
        print(f"   Interest Diversity: {interest_avg:.1f}/10")
        print(f"   Commercial Viability: {commercial_avg:.1f}/10")
        print()
        
        # Detailed rankings
        print("👥 DETAILED DEMOGRAPHIC RANKINGS:")
        for result in results:
            scores = result['demographic_scores']
            chars = result['demographic_characteristics']
            print(f"{result['rank']}. {result['musical_name']}")
            print(f"   Overall: {scores['overall_demographic_score']}/10 | Genre: {result['genre']}")
            print(f"   Age:{scores['age_group_appeal_score']:.1f} Cult:{scores['cultural_accessibility_score']:.1f} Int:{scores['interest_diversity_score']:.1f} Com:{scores['commercial_viability_score']:.1f}")
            print(f"   Demo: {chars['primary_demographic']} | Scope: {chars['cultural_scope']} | Category: {chars['commercial_category']}")
            print(f"   Accessibility: {chars['accessibility_level']}")
            print()
        
        # Demographic pattern analysis
        print("🎯 AUDIENCE DEMOGRAPHIC PATTERNS:")
        
        # Primary demographics
        primary_demos = {}
        for result in results:
            demo = result['demographic_characteristics']['primary_demographic']
            primary_demos[demo] = primary_demos.get(demo, 0) + 1
        
        print("   Primary Demographics:")
        for demo, count in primary_demos.items():
            print(f"     {demo}: {count} musicals")
        
        # Cultural scope
        cultural_scopes = {}
        for result in results:
            scope = result['demographic_characteristics']['cultural_scope']
            cultural_scopes[scope] = cultural_scopes.get(scope, 0) + 1
        
        print("   Cultural Scope:")
        for scope, count in cultural_scopes.items():
            print(f"     {scope}: {count} musicals")
        
        # Commercial categories
        commercial_cats = {}
        for result in results:
            cat = result['demographic_characteristics']['commercial_category']
            commercial_cats[cat] = commercial_cats.get(cat, 0) + 1
        
        print("   Commercial Categories:")
        for cat, count in commercial_cats.items():
            print(f"     {cat}: {count} musicals")
        
        # Save results
        output_data = {
            "analysis_metadata": {
                "analysis_type": "Audience Demographic Appeal Analysis",
                "analysis_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_musicals": len(results),
                "collection_average": round(collection_average, 2),
                "score_range": round(score_range, 2),
                "analysis_time_seconds": round(total_time, 1),
                "component_averages": {
                    "age_group_appeal": round(age_avg, 2),
                    "cultural_accessibility": round(cultural_avg, 2),
                    "interest_diversity": round(interest_avg, 2),
                    "commercial_viability": round(commercial_avg, 2)
                }
            },
            "demographic_rankings": results,
            "demographic_patterns": {
                "primary_demographics": primary_demos,
                "cultural_scopes": cultural_scopes,
                "commercial_categories": commercial_cats
            }
        }
        
        with open("AUDIENCE_demographic_analysis.json", 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Demographic analysis saved to: AUDIENCE_demographic_analysis.json")
        print("👥🎯 Audience Demographic Appeal Analysis complete - FULL IMPULSE ACHIEVED!")
        
        return results
    
    else:
        print("❌ No analyses completed")
        return []

if __name__ == "__main__":
    print("🚀 Starting Audience Demographic Appeal Analysis - FULL IMPULSE!")
    run_audience_demographic_analysis()