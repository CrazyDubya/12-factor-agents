#!/usr/bin/env python3
"""
Comparative Genre Evolution Analysis
Evaluates how each musical innovates within or evolves their respective genres
"""

import json
import re
import time
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
from main import SceneData

@dataclass
class GenreEvolutionAnalysis:
    """Results of comparative genre evolution analysis"""
    scene_title: str
    genre_tradition_score: float          # 0-10 - Adherence to established genre conventions
    innovation_factor_score: float        # 0-10 - Creative departures and genre innovations
    evolution_impact_score: float         # 0-10 - Potential influence on genre development
    cross_genre_synthesis_score: float    # 0-10 - Effective blending of multiple genres
    overall_evolution_score: float        # 0-10 - Combined genre evolution assessment
    
    # Evolution analysis details
    traditional_elements: List[str]
    innovative_departures: List[str]
    cross_genre_influences: List[str]
    evolution_techniques: List[str]
    genre_impact_potential: List[str]
    
    # Genre characteristics
    primary_genre: str                     # Main genre classification
    secondary_genres: List[str]            # Additional genre influences
    evolution_type: str                    # "Traditional", "Evolutionary", "Revolutionary", "Hybrid"
    innovation_level: str                  # "Conservative", "Moderate", "Progressive", "Groundbreaking"
    
    analysis_time: float

class GenreEvolutionAnalyzer:
    """Specialized analyzer for comparative genre evolution evaluation"""
    
    def __init__(self):
        # Genre tradition patterns
        self.genre_traditions = {
            "musical_theater": [
                r'\b(?:book musical|classic musical|traditional musical)\b',
                r'\b(?:broadway|west end|musical theater|show tunes)\b',
                r'\b(?:opening number|i want song|11 o\'clock number)\b',
                r'\b(?:ensemble finale|reprise|leitmotif|underscoring)\b'
            ],
            "opera": [
                r'\b(?:opera|operatic|aria|recitative|libretto)\b',
                r'\b(?:soprano|tenor|baritone|bass|coloratura)\b',
                r'\b(?:dramatic|tragic|heroic|mythological)\b',
                r'\b(?:classical|orchestral|symphonic|grand)\b'
            ],
            "rock_musical": [
                r'\b(?:rock musical|rock opera|concept album)\b',
                r'\b(?:electric guitar|drums|bass|amplified)\b',
                r'\b(?:anthemic|driving|power|energy|rebellion)\b',
                r'\b(?:youth|counterculture|protest|freedom)\b'
            ],
            "folk_musical": [
                r'\b(?:folk|traditional|acoustic|storytelling)\b',
                r'\b(?:community|heritage|roots|cultural)\b',
                r'\b(?:simple|authentic|earthy|natural)\b',
                r'\b(?:ballad|narrative|oral tradition)\b'
            ],
            "pop_musical": [
                r'\b(?:pop musical|contemporary|commercial|radio)\b',
                r'\b(?:catchy|hook|mainstream|accessible)\b',
                r'\b(?:dance|choreography|spectacle|production)\b',
                r'\b(?:star vehicle|celebrity|marketable)\b'
            ],
            "cabaret": [
                r'\b(?:cabaret|intimate|nightclub|lounge)\b',
                r'\b(?:torch song|chanson|standards|jazz)\b',
                r'\b(?:sophisticated|adult|worldly|cynical)\b',
                r'\b(?:piano bar|small venue|personal|confessional)\b'
            ],
            "revue": [
                r'\b(?:revue|variety|vaudeville|sketch)\b',
                r'\b(?:numbers|acts|performers|entertainment)\b',
                r'\b(?:showcase|talent|diverse|eclectic)\b',
                r'\b(?:themed|conceptual|anthology)\b'
            ],
            "jukebox_musical": [
                r'\b(?:jukebox|catalog|greatest hits|compilation)\b',
                r'\b(?:existing songs|popular music|artist tribute)\b',
                r'\b(?:nostalgic|familiar|recognizable|beloved)\b',
                r'\b(?:biographical|tribute|celebration)\b'
            ]
        }
        
        # Innovation patterns
        self.innovation_patterns = {
            "structural_innovation": [
                r'\b(?:non-linear|fragmented|experimental structure)\b',
                r'\b(?:through-composed|continuous|seamless)\b',
                r'\b(?:unconventional|unique|groundbreaking form)\b',
                r'\b(?:innovative staging|new approach|fresh perspective)\b'
            ],
            "musical_innovation": [
                r'\b(?:fusion|blend|hybrid|cross-pollination)\b',
                r'\b(?:new sound|original|creative|inventive)\b',
                r'\b(?:genre-bending|style-mixing|eclectic)\b',
                r'\b(?:contemporary|modern|cutting-edge|progressive)\b'
            ],
            "thematic_innovation": [
                r'\b(?:contemporary issues|modern themes|current topics)\b',
                r'\b(?:social commentary|political|cultural relevance)\b',
                r'\b(?:psychological|complex|nuanced|sophisticated)\b',
                r'\b(?:taboo|controversial|challenging|provocative)\b'
            ],
            "technological_innovation": [
                r'\b(?:technology|digital|multimedia|interactive)\b',
                r'\b(?:projection|led|virtual|augmented reality)\b',
                r'\b(?:electronic|synthesized|computer|automated)\b',
                r'\b(?:high-tech|futuristic|advanced|innovative)\b'
            ],
            "narrative_innovation": [
                r'\b(?:meta-theatrical|self-referential|breaking fourth wall)\b',
                r'\b(?:multiple perspectives|unreliable narrator|complex)\b',
                r'\b(?:non-traditional|experimental|avant-garde)\b',
                r'\b(?:immersive|participatory|interactive|engaging)\b'
            ]
        }
        
        # Cross-genre synthesis patterns
        self.cross_genre_patterns = {
            "classical_contemporary": [
                r'\b(?:classical meets contemporary|traditional and modern)\b',
                r'\b(?:orchestral with pop|opera meets rock|symphonic fusion)\b',
                r'\b(?:timeless and current|heritage and innovation)\b'
            ],
            "global_fusion": [
                r'\b(?:world music|international|multicultural fusion)\b',
                r'\b(?:ethnic|traditional|folk|indigenous)\b',
                r'\b(?:global|universal|cross-cultural|diverse)\b'
            ],
            "genre_blending": [
                r'\b(?:genre-defying|category-crossing|hybrid)\b',
                r'\b(?:combines|merges|integrates|synthesizes)\b',
                r'\b(?:unexpected|surprising|unique combination)\b'
            ],
            "style_evolution": [
                r'\b(?:evolves|develops|advances|progresses)\b',
                r'\b(?:next generation|future|evolution|development)\b',
                r'\b(?:builds on|expands|extends|enhances)\b'
            ]
        }
        
        # Evolution impact indicators
        self.impact_indicators = {
            "trendsetting": [
                r'\b(?:trendsetting|pioneering|influential|groundbreaking)\b',
                r'\b(?:sets new standard|breaks new ground|leads the way)\b',
                r'\b(?:game-changing|revolutionary|paradigm shift)\b'
            ],
            "genre_defining": [
                r'\b(?:defines|establishes|creates|originates)\b',
                r'\b(?:landmark|milestone|watershed|turning point)\b',
                r'\b(?:seminal|foundational|essential|definitive)\b'
            ],
            "industry_impact": [
                r'\b(?:industry|business|commercial|market)\b',
                r'\b(?:changes everything|transforms|revolutionizes)\b',
                r'\b(?:influences|inspires|spawns|generates)\b'
            ],
            "artistic_impact": [
                r'\b(?:artistic|creative|aesthetic|cultural)\b',
                r'\b(?:raises the bar|elevates|enhances|enriches)\b',
                r'\b(?:artistic merit|creative achievement|cultural significance)\b'
            ]
        }
        
        # Genre classification patterns
        self.genre_classification = {
            "sci_fi_drama": ["sci-fi", "science fiction", "futuristic", "technology", "artificial intelligence"],
            "techno_romance": ["techno", "technology", "romance", "digital", "electronic"],
            "murder_mystery": ["mystery", "murder", "detective", "crime", "thriller"],
            "contemporary_drama": ["contemporary", "modern", "realistic", "drama", "current"],
            "dystopian_action": ["dystopian", "post-apocalyptic", "resistance", "rebellion", "action"],
            "fantasy_musical": ["fantasy", "magic", "magical", "adventure", "quest"]
        }
    
    def extract_evolution_elements(self, scene: SceneData) -> Dict[str, List[str]]:
        """Extract genre tradition and innovation elements"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes}"
        
        evolution_elements = {
            "traditional_markers": [],
            "innovation_markers": [],
            "cross_genre_markers": [],
            "impact_markers": []
        }
        
        # Extract traditional elements
        for genre, patterns in self.genre_traditions.items():
            for pattern in patterns:
                matches = re.finditer(pattern, all_text, re.IGNORECASE)
                for match in matches:
                    context = self._get_context(all_text, match.start(), match.end())
                    evolution_elements["traditional_markers"].append(f"{genre}: {context}")
        
        # Extract innovation markers
        for category, patterns in self.innovation_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, all_text, re.IGNORECASE)
                for match in matches:
                    context = self._get_context(all_text, match.start(), match.end())
                    evolution_elements["innovation_markers"].append(f"{category}: {context}")
        
        return evolution_elements
    
    def _get_context(self, text: str, start: int, end: int, context_size: int = 50) -> str:
        """Get context around a match"""
        context_start = max(0, start - context_size)
        context_end = min(len(text), end + context_size)
        context = text[context_start:context_end].strip()
        return context[:80] + "..." if len(context) > 80 else context
    
    def analyze_genre_tradition(self, scene: SceneData, genre: str) -> Tuple[float, List[str]]:
        """Analyze adherence to established genre conventions"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes}".lower()
        
        traditional_elements = []
        tradition_score = 0.0
        
        # Map genre to tradition patterns
        genre_map = {
            "sci-fi drama": "musical_theater",
            "techno-romance": "pop_musical", 
            "murder mystery": "musical_theater",
            "contemporary drama": "musical_theater",
            "dystopian action": "rock_musical",
            "fantasy musical theater": "musical_theater"
        }
        
        primary_tradition = genre_map.get(genre.lower(), "musical_theater")
        
        # Analyze primary genre traditions
        if primary_tradition in self.genre_traditions:
            for pattern in self.genre_traditions[primary_tradition]:
                matches = len(re.findall(pattern, all_text))
                if matches > 0:
                    tradition_score += matches * 1.5
                    traditional_elements.append(f"{primary_tradition}: {matches} elements")
        
        # Check for other genre traditions
        for tradition, patterns in self.genre_traditions.items():
            if tradition != primary_tradition:
                tradition_count = sum(len(re.findall(pattern, all_text)) for pattern in patterns)
                if tradition_count > 0:
                    tradition_score += tradition_count * 1.0
                    traditional_elements.append(f"{tradition}: {tradition_count} elements")
        
        # Look for classic musical theater elements
        classic_elements = [
            r'\b(?:verse|chorus|bridge|refrain|hook)\b',
            r'\b(?:character development|plot advancement|emotional arc)\b',
            r'\b(?:ensemble|solo|duet|group number)\b',
            r'\b(?:dramatic|comedic|romantic|conflict)\b'
        ]
        
        classic_count = sum(len(re.findall(pattern, all_text)) for pattern in classic_elements)
        if classic_count > 0:
            tradition_score += classic_count * 0.8
            traditional_elements.append(f"Classic musical elements: {classic_count}")
        
        final_score = min(10.0, tradition_score)
        
        return final_score, traditional_elements[:5]
    
    def analyze_innovation_factor(self, scene: SceneData) -> Tuple[float, List[str]]:
        """Analyze creative departures and genre innovations"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes}".lower()
        
        innovative_departures = []
        innovation_score = 0.0
        
        # Analyze innovation categories
        for category, patterns in self.innovation_patterns.items():
            category_count = 0
            for pattern in patterns:
                category_count += len(re.findall(pattern, all_text))
            
            if category_count > 0:
                # Score based on innovation impact
                innovation_weights = {
                    "structural_innovation": 2.0,
                    "musical_innovation": 1.8,
                    "thematic_innovation": 1.5,
                    "technological_innovation": 1.7,
                    "narrative_innovation": 1.6
                }
                innovation_score += category_count * innovation_weights.get(category, 1.0)
                innovative_departures.append(f"{category.replace('_', ' ').title()}: {category_count}")
        
        # Look for experimental elements
        experimental_patterns = [
            r'\b(?:experimental|avant-garde|unconventional|radical)\b',
            r'\b(?:pushes boundaries|breaks rules|challenges norms)\b',
            r'\b(?:never been done|first time|unprecedented)\b',
            r'\b(?:innovative|creative|original|unique)\b'
        ]
        
        experimental_count = sum(len(re.findall(pattern, all_text)) for pattern in experimental_patterns)
        if experimental_count > 0:
            innovation_score += experimental_count * 1.5
            innovative_departures.append(f"Experimental elements: {experimental_count}")
        
        # Check for risk-taking
        risk_patterns = [
            r'\b(?:risky|bold|daring|courageous)\b',
            r'\b(?:takes chances|pushes limits|explores new territory)\b',
            r'\b(?:controversial|provocative|challenging)\b'
        ]
        
        risk_count = sum(len(re.findall(pattern, all_text)) for pattern in risk_patterns)
        if risk_count > 0:
            innovation_score += risk_count * 1.2
            innovative_departures.append(f"Risk-taking elements: {risk_count}")
        
        final_score = min(10.0, innovation_score)
        
        return final_score, innovative_departures[:5]
    
    def analyze_cross_genre_synthesis(self, scene: SceneData) -> Tuple[float, List[str]]:
        """Analyze effective blending of multiple genres"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes}".lower()
        
        cross_genre_influences = []
        synthesis_score = 0.0
        
        # Analyze cross-genre patterns
        for category, patterns in self.cross_genre_patterns.items():
            category_count = 0
            for pattern in patterns:
                category_count += len(re.findall(pattern, all_text))
            
            if category_count > 0:
                # Score based on synthesis sophistication
                synthesis_weights = {
                    "classical_contemporary": 1.8,
                    "global_fusion": 1.6,
                    "genre_blending": 2.0,
                    "style_evolution": 1.4
                }
                synthesis_score += category_count * synthesis_weights.get(category, 1.0)
                cross_genre_influences.append(f"{category.replace('_', ' ').title()}: {category_count}")
        
        # Count different genre influences present
        genre_count = 0
        for genre, keywords in self.genre_classification.items():
            for keyword in keywords:
                if keyword in all_text:
                    genre_count += 1
                    break
        
        if genre_count >= 2:
            synthesis_score += genre_count * 1.0
            cross_genre_influences.append(f"Multiple genre influences: {genre_count}")
        
        # Look for fusion indicators
        fusion_patterns = [
            r'\b(?:fusion|blend|hybrid|crossover|synthesis)\b',
            r'\b(?:combines|merges|integrates|mixes|weaves)\b',
            r'\b(?:multi-genre|cross-genre|genre-spanning)\b'
        ]
        
        fusion_count = sum(len(re.findall(pattern, all_text)) for pattern in fusion_patterns)
        if fusion_count > 0:
            synthesis_score += fusion_count * 1.3
            cross_genre_influences.append(f"Fusion indicators: {fusion_count}")
        
        final_score = min(10.0, synthesis_score)
        
        return final_score, cross_genre_influences[:5]
    
    def analyze_evolution_impact(self, scene: SceneData) -> Tuple[float, List[str]]:
        """Analyze potential influence on genre development"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes}".lower()
        
        impact_potential = []
        impact_score = 0.0
        
        # Analyze impact indicators
        for category, patterns in self.impact_indicators.items():
            category_count = 0
            for pattern in patterns:
                category_count += len(re.findall(pattern, all_text))
            
            if category_count > 0:
                # Score based on impact potential
                impact_weights = {
                    "trendsetting": 2.0,
                    "genre_defining": 1.8,
                    "industry_impact": 1.5,
                    "artistic_impact": 1.3
                }
                impact_score += category_count * impact_weights.get(category, 1.0)
                impact_potential.append(f"{category.replace('_', ' ').title()}: {category_count}")
        
        # Look for influence indicators
        influence_patterns = [
            r'\b(?:influential|inspiring|pioneering|leading)\b',
            r'\b(?:sets example|shows the way|breaks new ground)\b',
            r'\b(?:will inspire|likely to influence|potential impact)\b'
        ]
        
        influence_count = sum(len(re.findall(pattern, all_text)) for pattern in influence_patterns)
        if influence_count > 0:
            impact_score += influence_count * 1.4
            impact_potential.append(f"Influence indicators: {influence_count}")
        
        # Check for legacy potential
        legacy_patterns = [
            r'\b(?:legacy|lasting|enduring|timeless)\b',
            r'\b(?:classic|landmark|milestone|historic)\b',
            r'\b(?:memorable|unforgettable|significant)\b'
        ]
        
        legacy_count = sum(len(re.findall(pattern, all_text)) for pattern in legacy_patterns)
        if legacy_count > 0:
            impact_score += legacy_count * 1.2
            impact_potential.append(f"Legacy potential: {legacy_count}")
        
        final_score = min(10.0, impact_score)
        
        return final_score, impact_potential[:5]
    
    def determine_primary_genre(self, scene: SceneData, provided_genre: str) -> str:
        """Determine the primary genre classification"""
        # Use provided genre as primary classification
        return provided_genre
    
    def identify_secondary_genres(self, scene: SceneData) -> List[str]:
        """Identify additional genre influences"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes}".lower()
        
        secondary_genres = []
        for genre, keywords in self.genre_classification.items():
            for keyword in keywords:
                if keyword in all_text:
                    secondary_genres.append(genre.replace('_', ' ').title())
                    break
        
        return secondary_genres[:3]
    
    def determine_evolution_type(self, tradition_score: float, innovation_score: float) -> str:
        """Determine the type of genre evolution"""
        if innovation_score >= 8.0 and tradition_score <= 4.0:
            return "Revolutionary"
        elif innovation_score >= 6.0 and tradition_score >= 6.0:
            return "Hybrid"
        elif innovation_score >= 5.0:
            return "Evolutionary"
        else:
            return "Traditional"
    
    def determine_innovation_level(self, innovation_score: float) -> str:
        """Determine the level of innovation"""
        if innovation_score >= 8.0:
            return "Groundbreaking"
        elif innovation_score >= 6.0:
            return "Progressive"
        elif innovation_score >= 4.0:
            return "Moderate"
        else:
            return "Conservative"
    
    def analyze_scene_genre_evolution(self, scene: SceneData, genre: str) -> GenreEvolutionAnalysis:
        """Perform comprehensive genre evolution analysis"""
        analysis_start = time.time()
        
        print(f"🎭 Analyzing genre evolution for: {scene.title}")
        
        # Extract evolution elements
        evolution_elements = self.extract_evolution_elements(scene)
        print(f"   🎨 Found {len(evolution_elements['traditional_markers'])} traditional elements")
        print(f"   ⚡ Found {len(evolution_elements['innovation_markers'])} innovation markers")
        
        # Perform component analyses
        tradition_score, traditional_elements = self.analyze_genre_tradition(scene, genre)
        innovation_score, innovative_departures = self.analyze_innovation_factor(scene)
        synthesis_score, cross_genre_influences = self.analyze_cross_genre_synthesis(scene)
        impact_score, impact_potential = self.analyze_evolution_impact(scene)
        
        # Determine genre characteristics
        primary_genre = self.determine_primary_genre(scene, genre)
        secondary_genres = self.identify_secondary_genres(scene)
        evolution_type = self.determine_evolution_type(tradition_score, innovation_score)
        innovation_level = self.determine_innovation_level(innovation_score)
        
        # Calculate overall evolution score
        overall_score = (tradition_score * 0.2 + innovation_score * 0.3 + 
                        synthesis_score * 0.25 + impact_score * 0.25)
        
        # Identify evolution techniques
        evolution_techniques = []
        if tradition_score >= 6.0:
            evolution_techniques.append("Strong genre foundation")
        if innovation_score >= 6.0:
            evolution_techniques.append("Creative innovation")
        if synthesis_score >= 6.0:
            evolution_techniques.append("Cross-genre synthesis")
        if impact_score >= 6.0:
            evolution_techniques.append("Industry impact potential")
        
        analysis_time = time.time() - analysis_start
        
        print(f"   🏛️ Tradition: {tradition_score:.1f}/10")
        print(f"   ⚡ Innovation: {innovation_score:.1f}/10")
        print(f"   🔄 Synthesis: {synthesis_score:.1f}/10")
        print(f"   📈 Impact: {impact_score:.1f}/10")
        print(f"   🏆 Overall Evolution Score: {overall_score:.1f}/10")
        print(f"   📈 Type: {evolution_type} | Level: {innovation_level}")
        
        return GenreEvolutionAnalysis(
            scene_title=scene.title,
            genre_tradition_score=tradition_score,
            innovation_factor_score=innovation_score,
            evolution_impact_score=impact_score,
            cross_genre_synthesis_score=synthesis_score,
            overall_evolution_score=overall_score,
            traditional_elements=traditional_elements,
            innovative_departures=innovative_departures,
            cross_genre_influences=cross_genre_influences,
            evolution_techniques=evolution_techniques,
            genre_impact_potential=impact_potential,
            primary_genre=primary_genre,
            secondary_genres=secondary_genres,
            evolution_type=evolution_type,
            innovation_level=innovation_level,
            analysis_time=analysis_time
        )

def run_genre_evolution_analysis():
    """Run comparative genre evolution analysis on all musicals"""
    
    print("🎭⚡ COMPARATIVE GENRE EVOLUTION ANALYSIS - FULL IMPULSE!")
    print("=" * 65)
    print("Analyzing genre innovation and evolution across musical styles")
    print("Components: Tradition, Innovation, Synthesis, Impact\n")
    
    analyzer = GenreEvolutionAnalyzer()
    
    # Musical scenes for genre evolution analysis
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
            print(f"🎪 EVOLUTION ANALYSIS {i}/6: {scene_info['musical']}")
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
            
            # Perform genre evolution analysis
            analysis = analyzer.analyze_scene_genre_evolution(scene, scene_info['genre'])
            
            # Format result
            result = {
                "rank": i,
                "musical_name": scene_info['musical'],
                "genre": scene_info['genre'],
                "scene_title": analysis.scene_title,
                "evolution_scores": {
                    "overall_evolution_score": round(analysis.overall_evolution_score, 2),
                    "genre_tradition_score": round(analysis.genre_tradition_score, 2),
                    "innovation_factor_score": round(analysis.innovation_factor_score, 2),
                    "evolution_impact_score": round(analysis.evolution_impact_score, 2),
                    "cross_genre_synthesis_score": round(analysis.cross_genre_synthesis_score, 2)
                },
                "evolution_characteristics": {
                    "primary_genre": analysis.primary_genre,
                    "secondary_genres": analysis.secondary_genres,
                    "evolution_type": analysis.evolution_type,
                    "innovation_level": analysis.innovation_level
                },
                "evolution_details": {
                    "traditional_elements": analysis.traditional_elements,
                    "innovative_departures": analysis.innovative_departures,
                    "cross_genre_influences": analysis.cross_genre_influences,
                    "evolution_techniques": analysis.evolution_techniques,
                    "genre_impact_potential": analysis.genre_impact_potential
                },
                "analysis_time": round(analysis.analysis_time, 2)
            }
            
            results.append(result)
            print()
            
        except Exception as e:
            print(f"❌ Error analyzing {scene_info['musical']}: {e}")
            continue
    
    total_time = time.time() - total_start
    
    # Sort by overall evolution score
    results.sort(key=lambda x: x['evolution_scores']['overall_evolution_score'], reverse=True)
    
    # Update rankings
    for i, result in enumerate(results, 1):
        result['rank'] = i
    
    print("=" * 65)
    print("🏆 COMPARATIVE GENRE EVOLUTION RANKINGS")
    print("=" * 65)
    
    if results:
        # Calculate statistics
        evolution_scores = [r['evolution_scores']['overall_evolution_score'] for r in results]
        collection_average = sum(evolution_scores) / len(evolution_scores)
        score_range = max(evolution_scores) - min(evolution_scores)
        
        print(f"Collection Average: {collection_average:.1f}/10.0")
        print(f"Score Range: {score_range:.1f} points")
        print(f"Analysis Time: {total_time:.1f} seconds")
        print(f"Musicals Analyzed: {len(results)}/6")
        print()
        
        # Component averages
        tradition_avg = sum(r['evolution_scores']['genre_tradition_score'] for r in results) / len(results)
        innovation_avg = sum(r['evolution_scores']['innovation_factor_score'] for r in results) / len(results)
        impact_avg = sum(r['evolution_scores']['evolution_impact_score'] for r in results) / len(results)
        synthesis_avg = sum(r['evolution_scores']['cross_genre_synthesis_score'] for r in results) / len(results)
        
        print("📊 COMPONENT AVERAGES:")
        print(f"   Genre Tradition: {tradition_avg:.1f}/10")
        print(f"   Innovation Factor: {innovation_avg:.1f}/10")
        print(f"   Evolution Impact: {impact_avg:.1f}/10")
        print(f"   Cross-Genre Synthesis: {synthesis_avg:.1f}/10")
        print()
        
        # Detailed rankings
        print("🎭 DETAILED EVOLUTION RANKINGS:")
        for result in results:
            scores = result['evolution_scores']
            chars = result['evolution_characteristics']
            print(f"{result['rank']}. {result['musical_name']}")
            print(f"   Overall: {scores['overall_evolution_score']}/10 | Genre: {result['genre']}")
            print(f"   Trad:{scores['genre_tradition_score']:.1f} Innov:{scores['innovation_factor_score']:.1f} Impact:{scores['evolution_impact_score']:.1f} Synth:{scores['cross_genre_synthesis_score']:.1f}")
            print(f"   Type: {chars['evolution_type']} | Level: {chars['innovation_level']}")
            if chars['secondary_genres']:
                print(f"   Secondary Genres: {', '.join(chars['secondary_genres'])}")
            print()
        
        # Evolution pattern analysis
        print("🔄 GENRE EVOLUTION PATTERNS:")
        
        # Evolution types
        evolution_types = {}
        for result in results:
            evo_type = result['evolution_characteristics']['evolution_type']
            evolution_types[evo_type] = evolution_types.get(evo_type, 0) + 1
        
        print("   Evolution Types:")
        for evo_type, count in evolution_types.items():
            print(f"     {evo_type}: {count} musicals")
        
        # Innovation levels
        innovation_levels = {}
        for result in results:
            level = result['evolution_characteristics']['innovation_level']
            innovation_levels[level] = innovation_levels.get(level, 0) + 1
        
        print("   Innovation Levels:")
        for level, count in innovation_levels.items():
            print(f"     {level}: {count} musicals")
        
        # Cross-genre analysis
        all_secondary_genres = []
        for result in results:
            all_secondary_genres.extend(result['evolution_characteristics']['secondary_genres'])
        
        secondary_genre_counts = {}
        for genre in all_secondary_genres:
            secondary_genre_counts[genre] = secondary_genre_counts.get(genre, 0) + 1
        
        if secondary_genre_counts:
            print("   Most Common Secondary Genres:")
            sorted_genres = sorted(secondary_genre_counts.items(), key=lambda x: x[1], reverse=True)
            for genre, count in sorted_genres[:5]:
                print(f"     {genre}: {count} appearances")
        
        # Save results
        output_data = {
            "analysis_metadata": {
                "analysis_type": "Comparative Genre Evolution Analysis",
                "analysis_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_musicals": len(results),
                "collection_average": round(collection_average, 2),
                "score_range": round(score_range, 2),
                "analysis_time_seconds": round(total_time, 1),
                "component_averages": {
                    "genre_tradition": round(tradition_avg, 2),
                    "innovation_factor": round(innovation_avg, 2),
                    "evolution_impact": round(impact_avg, 2),
                    "cross_genre_synthesis": round(synthesis_avg, 2)
                }
            },
            "evolution_rankings": results,
            "evolution_patterns": {
                "evolution_types": evolution_types,
                "innovation_levels": innovation_levels,
                "secondary_genre_counts": secondary_genre_counts
            }
        }
        
        with open("GENRE_evolution_analysis.json", 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Genre evolution analysis saved to: GENRE_evolution_analysis.json")
        print("🎭⚡ Comparative Genre Evolution Analysis complete - FULL IMPULSE ACHIEVED!")
        
        return results
    
    else:
        print("❌ No analyses completed")
        return []

if __name__ == "__main__":
    print("🚀 Starting Comparative Genre Evolution Analysis - FULL IMPULSE!")
    run_genre_evolution_analysis()