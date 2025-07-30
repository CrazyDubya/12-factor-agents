#!/usr/bin/env python3
"""
Cultural & Social Commentary Evaluation - Analysis of social themes and cultural relevance
Evaluates social impact, cultural depth, contemporary relevance, and commentary sophistication
"""

import json
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from main import SceneData


@dataclass
class CulturalAnalysis:
    """Results of cultural and social commentary analysis"""

    scene_title: str
    social_theme_depth: float  # 0-10 - Depth of social issue exploration
    cultural_relevance_score: float  # 0-10 - Contemporary cultural connection
    commentary_sophistication: (
        float  # 0-10 - Nuance and complexity of social commentary
    )
    societal_impact_potential: float  # 0-10 - Potential to influence or provoke thought
    overall_cultural_score: float  # 0-10 - Combined cultural/social effectiveness

    # Detailed cultural mapping
    social_themes_identified: List[str]
    cultural_references: List[str]
    commentary_techniques: List[str]
    impact_indicators: List[str]
    contemporary_connections: List[str]

    # Cultural characteristics
    primary_social_theme: str  # Dominant social issue addressed
    cultural_perspective: str  # "Historical", "Contemporary", "Futuristic", "Universal"
    commentary_approach: str  # "Direct", "Allegorical", "Satirical", "Subtle"
    societal_scope: str  # "Individual", "Community", "National", "Global"

    analysis_time: float


class CulturalCommentaryAnalyzer:
    """Specialized analyzer for cultural and social commentary evaluation"""

    def __init__(self):
        # Comprehensive social themes taxonomy
        self.social_themes = {
            "identity_belonging": {
                "keywords": [
                    "identity",
                    "belonging",
                    "self",
                    "who am i",
                    "place",
                    "home",
                    "roots",
                    "heritage",
                    "culture",
                    "tradition",
                    "community",
                    "acceptance",
                    "otherness",
                    "outsider",
                ],
                "weight": 1.2,
                "description": "Questions of personal and cultural identity",
            },
            "social_justice": {
                "keywords": [
                    "justice",
                    "equality",
                    "fairness",
                    "rights",
                    "discrimination",
                    "prejudice",
                    "oppression",
                    "freedom",
                    "liberation",
                    "activism",
                    "protest",
                    "resistance",
                ],
                "weight": 1.5,
                "description": "Issues of fairness and social equity",
            },
            "technology_society": {
                "keywords": [
                    "technology",
                    "digital",
                    "artificial intelligence",
                    "automation",
                    "surveillance",
                    "privacy",
                    "connection",
                    "isolation",
                    "virtual",
                    "real",
                    "human vs machine",
                ],
                "weight": 1.3,
                "description": "Impact of technology on human society",
            },
            "power_corruption": {
                "keywords": [
                    "power",
                    "authority",
                    "corruption",
                    "abuse",
                    "control",
                    "manipulation",
                    "government",
                    "politics",
                    "hierarchy",
                    "elite",
                    "system",
                    "establishment",
                ],
                "weight": 1.4,
                "description": "Dynamics of power and its corrupting influence",
            },
            "economic_inequality": {
                "keywords": [
                    "wealth",
                    "poverty",
                    "class",
                    "rich",
                    "poor",
                    "money",
                    "capitalism",
                    "work",
                    "labor",
                    "exploitation",
                    "privilege",
                    "disadvantage",
                    "opportunity",
                ],
                "weight": 1.3,
                "description": "Economic disparities and class issues",
            },
            "environmental_crisis": {
                "keywords": [
                    "environment",
                    "climate",
                    "nature",
                    "pollution",
                    "destruction",
                    "sustainability",
                    "future generations",
                    "earth",
                    "planet",
                    "conservation",
                    "crisis",
                ],
                "weight": 1.4,
                "description": "Environmental concerns and sustainability",
            },
            "human_relationships": {
                "keywords": [
                    "love",
                    "family",
                    "friendship",
                    "relationships",
                    "community",
                    "connection",
                    "loneliness",
                    "isolation",
                    "trust",
                    "betrayal",
                    "communication",
                    "understanding",
                ],
                "weight": 1.1,
                "description": "Human connection and relationship dynamics",
            },
            "generational_conflict": {
                "keywords": [
                    "generation",
                    "old",
                    "young",
                    "tradition",
                    "change",
                    "progress",
                    "past",
                    "future",
                    "wisdom",
                    "youth",
                    "experience",
                    "innovation",
                ],
                "weight": 1.2,
                "description": "Tensions between different generations",
            },
            "mental_health": {
                "keywords": [
                    "mental health",
                    "depression",
                    "anxiety",
                    "trauma",
                    "healing",
                    "therapy",
                    "stigma",
                    "wellness",
                    "mind",
                    "psychological",
                    "emotional wellbeing",
                ],
                "weight": 1.3,
                "description": "Mental health awareness and stigma",
            },
            "diversity_inclusion": {
                "keywords": [
                    "diversity",
                    "inclusion",
                    "representation",
                    "minority",
                    "majority",
                    "tolerance",
                    "acceptance",
                    "difference",
                    "multiculturalism",
                    "racism",
                    "sexism",
                    "bias",
                ],
                "weight": 1.4,
                "description": "Issues of diversity and social inclusion",
            },
        }

        # Contemporary cultural references
        self.cultural_markers = {
            "current_events": [
                r"\b(?:pandemic|covid|lockdown|quarantine)\b",
                r"\b(?:social media|instagram|twitter|tiktok|facebook)\b",
                r"\b(?:climate change|global warming|carbon)\b",
                r"\b(?:election|democracy|voting|political)\b",
                r"\b(?:inequality|systemic|institutional)\b",
            ],
            "generational_markers": [
                r"\b(?:millennial|gen z|boomer|generation)\b",
                r"\b(?:digital native|smartphone|app|online)\b",
                r"\b(?:gig economy|remote work|streaming)\b",
                r"\b(?:mental health|therapy|self-care)\b",
            ],
            "cultural_movements": [
                r"\b(?:metoo|black lives matter|lgbtq|pride)\b",
                r"\b(?:feminism|gender equality|representation)\b",
                r"\b(?:activism|protest|movement|solidarity)\b",
                r"\b(?:awareness|advocacy|allyship)\b",
            ],
            "technological_cultural": [
                r"\b(?:artificial intelligence|ai|algorithm|data)\b",
                r"\b(?:virtual reality|augmented|digital twin)\b",
                r"\b(?:cryptocurrency|blockchain|nft)\b",
                r"\b(?:automation|robotics|machine learning)\b",
            ],
        }

        # Commentary techniques and approaches
        self.commentary_techniques = {
            "direct_commentary": [
                r"\b(?:we must|society needs|it\'s time to|we should)\b",
                r"\b(?:the problem is|the issue is|what\'s wrong)\b",
                r"\b(?:change|reform|revolution|transformation)\b",
            ],
            "allegorical_approach": [
                r"\b(?:represents|symbolizes|stands for|metaphor)\b",
                r"\b(?:like|similar to|reminds me of|parallel)\b",
                r"\b(?:allegory|parable|fable|story)\b",
            ],
            "satirical_critique": [
                r"\b(?:irony|ironic|sarcasm|ridiculous|absurd)\b",
                r"\b(?:mockery|parody|satire|comedy|humor)\b",
                r"\b(?:exaggeration|extreme|over the top)\b",
            ],
            "questioning_approach": [
                r"\b(?:what if|imagine if|suppose|consider)\b",
                r"\b(?:why|how|when|where|who)\b.*\?",
                r"\b(?:question|wonder|curious|ponder)\b",
            ],
        }

        # Impact and influence indicators
        self.impact_indicators = [
            # Call to action patterns
            r"\b(?:action|act|do something|make a difference)\b",
            r"\b(?:wake up|open your eyes|realize|understand)\b",
            r"\b(?:together|unity|collective|community)\b",
            # Emotional impact patterns
            r"\b(?:powerful|moving|touching|inspiring)\b",
            r"\b(?:shocking|disturbing|eye-opening|revealing)\b",
            r"\b(?:hope|despair|anger|passion|commitment)\b",
            # Systemic change patterns
            r"\b(?:system|structure|institution|establishment)\b",
            r"\b(?:reform|revolution|change|transformation)\b",
            r"\b(?:future|next generation|legacy|impact)\b",
        ]

    def extract_social_content(self, scene: SceneData) -> Dict[str, List[str]]:
        """Extract social and cultural content from scene"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes} {scene.description}".lower()

        social_content = {
            "themes": [],
            "references": [],
            "techniques": [],
            "contemporary_markers": [],
        }

        # Extract social themes
        for theme_category, data in self.social_themes.items():
            matches = sum(1 for keyword in data["keywords"] if keyword in all_text)
            if matches > 0:
                social_content["themes"].append(
                    f"{data['description']}: {matches} references"
                )

        # Extract cultural markers
        for marker_category, patterns in self.cultural_markers.items():
            for pattern in patterns:
                if re.search(pattern, all_text):
                    social_content["contemporary_markers"].append(
                        f"{marker_category}: {pattern}"
                    )

        # Extract commentary techniques
        for technique, patterns in self.commentary_techniques.items():
            for pattern in patterns:
                matches = len(re.findall(pattern, all_text))
                if matches > 0:
                    social_content["techniques"].append(
                        f"{technique}: {matches} instances"
                    )

        return social_content

    def analyze_social_theme_depth(self, scene: SceneData) -> Tuple[float, List[str]]:
        """Analyze the depth and complexity of social theme exploration"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes} {scene.description}".lower()

        theme_elements = []
        depth_score = 0.0

        # Analyze each social theme for depth
        theme_scores = {}
        for theme_category, data in self.social_themes.items():
            theme_count = 0
            theme_complexity = 0

            # Count basic keyword matches
            for keyword in data["keywords"]:
                if keyword in all_text:
                    theme_count += 1

            if theme_count > 0:
                # Analyze complexity of treatment
                # Multi-faceted exploration
                if theme_count >= 3:
                    theme_complexity += 2.0
                    theme_elements.append(
                        f"{data['description']}: Multi-faceted exploration ({theme_count} aspects)"
                    )
                elif theme_count >= 2:
                    theme_complexity += 1.0
                    theme_elements.append(
                        f"{data['description']}: Dual perspective ({theme_count} aspects)"
                    )
                else:
                    theme_complexity += 0.5
                    theme_elements.append(f"{data['description']}: Basic mention")

                # Look for nuanced treatment
                nuance_patterns = [
                    r"\b(?:complex|complicated|nuanced|multifaceted)\b",
                    r"\b(?:on one hand|on the other hand|however|but|yet)\b",
                    r"\b(?:both|neither|either|paradox|contradiction)\b",
                ]

                nuance_count = sum(
                    len(re.findall(pattern, all_text)) for pattern in nuance_patterns
                )
                if nuance_count > 0:
                    theme_complexity += min(1.5, nuance_count * 0.3)

                theme_scores[theme_category] = theme_complexity * data["weight"]

        # Calculate overall depth score
        if theme_scores:
            # Primary theme depth
            primary_theme_score = max(theme_scores.values())
            depth_score += min(4.0, primary_theme_score)

            # Theme variety bonus
            theme_variety = len(theme_scores)
            if theme_variety >= 3:
                depth_score += 2.5
                theme_elements.append(
                    f"Thematic complexity: {theme_variety} social themes"
                )
            elif theme_variety >= 2:
                depth_score += 1.5
                theme_elements.append(
                    f"Dual thematic focus: {theme_variety} social themes"
                )

            # Interconnection bonus (themes that relate to each other)
            interconnection_patterns = [
                r"\b(?:related|connected|linked|intertwined)\b",
                r"\b(?:because of|leads to|results in|causes)\b",
                r"\b(?:systemic|systematic|structural)\b",
            ]

            interconnection_count = sum(
                len(re.findall(pattern, all_text))
                for pattern in interconnection_patterns
            )
            if interconnection_count > 0:
                depth_score += min(2.0, interconnection_count * 0.4)
                theme_elements.append(
                    f"Thematic interconnection: {interconnection_count} connections"
                )

        final_score = min(10.0, depth_score)

        return final_score, theme_elements[:5]

    def analyze_cultural_relevance(self, scene: SceneData) -> Tuple[float, List[str]]:
        """Analyze contemporary cultural relevance and connection"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes} {scene.description}".lower()

        relevance_indicators = []
        relevance_score = 0.0

        # Contemporary cultural markers
        for marker_category, patterns in self.cultural_markers.items():
            category_matches = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, all_text))
                if matches > 0:
                    category_matches += matches

            if category_matches > 0:
                relevance_score += min(2.5, category_matches * 0.8)
                relevance_indicators.append(
                    f"{marker_category.replace('_', ' ').title()}: {category_matches} references"
                )

        # Current event references and zeitgeist
        zeitgeist_patterns = [
            r"\b(?:today|nowadays|currently|these days|modern)\b",
            r"\b(?:2020s|pandemic era|post-covid|new normal)\b",
            r"\b(?:trending|viral|breaking news|latest)\b",
            r"\b(?:generation|youth|young people|kids today)\b",
        ]

        zeitgeist_count = sum(
            len(re.findall(pattern, all_text)) for pattern in zeitgeist_patterns
        )
        if zeitgeist_count > 0:
            relevance_score += min(2.0, zeitgeist_count * 0.5)
            relevance_indicators.append(
                f"Contemporary zeitgeist: {zeitgeist_count} references"
            )

        # Universal themes with contemporary applications
        universal_contemporary = [
            (
                r"\b(?:communication|misunderstanding|connection)\b",
                "Digital age communication",
            ),
            (
                r"\b(?:privacy|surveillance|data|information)\b",
                "Digital privacy concerns",
            ),
            (r"\b(?:work|career|job|employment|gig)\b", "Modern work culture"),
            (r"\b(?:education|learning|school|knowledge)\b", "Educational challenges"),
            (r"\b(?:health|wellness|medicine|care)\b", "Healthcare and wellness"),
        ]

        for pattern, theme in universal_contemporary:
            matches = len(re.findall(pattern, all_text))
            if matches > 0:
                relevance_score += matches * 0.6
                relevance_indicators.append(f"{theme}: {matches} references")

        # Cross-generational relevance
        generational_bridge = [
            r"\b(?:parents|children|family|generations)\b",
            r"\b(?:tradition|heritage|legacy|future)\b",
            r"\b(?:old|new|change|continuity)\b",
        ]

        bridge_count = sum(
            len(re.findall(pattern, all_text)) for pattern in generational_bridge
        )
        if bridge_count > 2:  # Only count if significant
            relevance_score += min(1.5, (bridge_count - 2) * 0.3)
            relevance_indicators.append(
                f"Cross-generational relevance: {bridge_count} bridges"
            )

        final_score = min(10.0, relevance_score)

        return final_score, relevance_indicators[:5]

    def analyze_commentary_sophistication(
        self, scene: SceneData
    ) -> Tuple[float, List[str]]:
        """Analyze the sophistication and nuance of social commentary"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes} {scene.description}".lower()

        sophistication_elements = []
        sophistication_score = 0.0

        # Commentary technique analysis
        technique_scores = {}
        for technique, patterns in self.commentary_techniques.items():
            technique_count = 0
            for pattern in patterns:
                technique_count += len(re.findall(pattern, all_text))

            if technique_count > 0:
                technique_scores[technique] = technique_count
                sophistication_elements.append(
                    f"{technique.replace('_', ' ').title()}: {technique_count} instances"
                )

        # Sophistication based on technique variety and depth
        if technique_scores:
            # Variety bonus
            technique_variety = len(technique_scores)
            if technique_variety >= 3:
                sophistication_score += 3.0
                sophistication_elements.append(
                    f"Multi-technique approach: {technique_variety} styles"
                )
            elif technique_variety >= 2:
                sophistication_score += 2.0
                sophistication_elements.append(
                    f"Dual-technique approach: {technique_variety} styles"
                )

            # Depth bonus (sophisticated techniques weighted higher)
            sophistication_weights = {
                "allegorical_approach": 1.5,
                "satirical_critique": 1.3,
                "questioning_approach": 1.2,
                "direct_commentary": 1.0,
            }

            weighted_score = sum(
                count * sophistication_weights.get(technique, 1.0)
                for technique, count in technique_scores.items()
            )
            sophistication_score += min(3.0, weighted_score * 0.3)

        # Nuance and complexity indicators
        nuance_patterns = [
            r"\b(?:nuanced|subtle|complex|layered|multifaceted)\b",
            r"\b(?:paradox|contradiction|irony|duality)\b",
            r"\b(?:both sides|multiple perspectives|various viewpoints)\b",
            r"\b(?:gray area|not black and white|complicated)\b",
        ]

        nuance_count = sum(
            len(re.findall(pattern, all_text)) for pattern in nuance_patterns
        )
        if nuance_count > 0:
            sophistication_score += min(2.5, nuance_count * 0.6)
            sophistication_elements.append(
                f"Nuanced perspective: {nuance_count} complexity indicators"
            )

        # Intellectual depth markers
        intellectual_patterns = [
            r"\b(?:philosophy|philosophical|ethics|moral)\b",
            r"\b(?:theory|concept|principle|framework)\b",
            r"\b(?:analyze|examine|consider|evaluate)\b",
            r"\b(?:implications|consequences|ramifications)\b",
        ]

        intellectual_count = sum(
            len(re.findall(pattern, all_text)) for pattern in intellectual_patterns
        )
        if intellectual_count > 0:
            sophistication_score += min(2.0, intellectual_count * 0.4)
            sophistication_elements.append(
                f"Intellectual depth: {intellectual_count} analytical elements"
            )

        # Historical/cultural context awareness
        context_patterns = [
            r"\b(?:history|historical|context|background)\b",
            r"\b(?:culture|cultural|society|social)\b",
            r"\b(?:precedent|tradition|evolution|development)\b",
        ]

        context_count = sum(
            len(re.findall(pattern, all_text)) for pattern in context_patterns
        )
        if context_count > 2:
            sophistication_score += min(1.5, (context_count - 2) * 0.2)
            sophistication_elements.append(
                f"Contextual awareness: {context_count} context references"
            )

        final_score = min(10.0, sophistication_score)

        return final_score, sophistication_elements[:5]

    def analyze_societal_impact_potential(
        self, scene: SceneData
    ) -> Tuple[float, List[str]]:
        """Analyze potential for societal influence and thought provocation"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes} {scene.description}".lower()

        impact_elements = []
        impact_score = 0.0

        # Direct impact indicators
        for pattern in self.impact_indicators:
            matches = len(re.findall(pattern, all_text))
            if matches > 0:
                impact_score += matches * 0.8
                impact_elements.append(f"Impact indicator: {matches} instances")

        # Emotional resonance (key to impact)
        emotional_impact_patterns = [
            r"\b(?:powerful|moving|touching|inspiring|motivating)\b",
            r"\b(?:shocking|disturbing|eye-opening|revealing|awakening)\b",
            r"\b(?:unforgettable|memorable|haunting|profound)\b",
            r"\b(?:tears|cry|laugh|anger|passion|outrage)\b",
        ]

        emotional_count = sum(
            len(re.findall(pattern, all_text)) for pattern in emotional_impact_patterns
        )
        if emotional_count > 0:
            impact_score += min(3.0, emotional_count * 0.6)
            impact_elements.append(
                f"Emotional resonance: {emotional_count} impact words"
            )

        # Call to action elements
        action_patterns = [
            r"\b(?:must|should|need to|have to|ought to)\b",
            r"\b(?:action|act|do|make a difference|change)\b",
            r"\b(?:together|unity|collective|community|solidarity)\b",
            r"\b(?:responsibility|duty|obligation|commitment)\b",
        ]

        action_count = sum(
            len(re.findall(pattern, all_text)) for pattern in action_patterns
        )
        if action_count > 0:
            impact_score += min(2.5, action_count * 0.4)
            impact_elements.append(f"Call to action: {action_count} action words")

        # Thought provocation (questions and challenges)
        provocation_patterns = [
            r"\?",  # Questions
            r"\b(?:what if|imagine|suppose|consider|think about)\b",
            r"\b(?:challenge|question|doubt|wonder|ponder)\b",
            r"\b(?:assumptions|beliefs|values|preconceptions)\b",
        ]

        provocation_count = sum(
            len(re.findall(pattern, all_text)) for pattern in provocation_patterns
        )
        if provocation_count > 0:
            impact_score += min(2.0, provocation_count * 0.3)
            impact_elements.append(
                f"Thought provocation: {provocation_count} challenges"
            )

        # Urgency and timeliness
        urgency_patterns = [
            r"\b(?:urgent|crisis|emergency|now|immediately)\b",
            r"\b(?:before it\'s too late|time is running out|critical)\b",
            r"\b(?:future|next generation|legacy|tomorrow)\b",
        ]

        urgency_count = sum(
            len(re.findall(pattern, all_text)) for pattern in urgency_patterns
        )
        if urgency_count > 0:
            impact_score += min(2.0, urgency_count * 0.5)
            impact_elements.append(
                f"Urgency markers: {urgency_count} time-sensitive elements"
            )

        # Systemic change potential
        systemic_patterns = [
            r"\b(?:system|structure|institution|establishment)\b",
            r"\b(?:reform|revolution|transformation|overhaul)\b",
            r"\b(?:widespread|society-wide|cultural shift)\b",
        ]

        systemic_count = sum(
            len(re.findall(pattern, all_text)) for pattern in systemic_patterns
        )
        if systemic_count > 0:
            impact_score += min(1.5, systemic_count * 0.4)
            impact_elements.append(
                f"Systemic change potential: {systemic_count} system references"
            )

        final_score = min(10.0, impact_score)

        return final_score, impact_elements[:5]

    def identify_primary_social_theme(self, scene: SceneData) -> str:
        """Identify the dominant social theme in the scene"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes} {scene.description}".lower()

        theme_scores = {}
        for theme_category, data in self.social_themes.items():
            score = (
                sum(1 for keyword in data["keywords"] if keyword in all_text)
                * data["weight"]
            )
            if score > 0:
                theme_scores[theme_category] = score

        if theme_scores:
            primary_theme = max(theme_scores, key=theme_scores.get)
            return self.social_themes[primary_theme]["description"]
        else:
            return "No dominant social theme identified"

    def determine_cultural_perspective(self, scene: SceneData) -> str:
        """Determine the cultural/temporal perspective of the commentary"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes} {scene.description}".lower()

        # Temporal markers
        if re.search(
            r"\b(?:future|tomorrow|2030|2040|2050|sci-fi|futuristic)\b", all_text
        ):
            return "Futuristic"
        elif re.search(r"\b(?:history|past|traditional|ancient|classical)\b", all_text):
            return "Historical"
        elif re.search(
            r"\b(?:today|current|modern|contemporary|now|2020s)\b", all_text
        ):
            return "Contemporary"
        else:
            return "Universal"

    def determine_commentary_approach(self, scene: SceneData) -> str:
        """Determine the primary approach to social commentary"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes} {scene.description}".lower()

        approach_scores = {}
        for approach, patterns in self.commentary_techniques.items():
            score = sum(len(re.findall(pattern, all_text)) for pattern in patterns)
            if score > 0:
                approach_scores[approach] = score

        if approach_scores:
            primary_approach = max(approach_scores, key=approach_scores.get)
            return (
                primary_approach.replace("_", " ")
                .title()
                .replace(" Approach", "")
                .replace(" Commentary", "")
            )
        else:
            return "Subtle"

    def determine_societal_scope(self, scene: SceneData) -> str:
        """Determine the scope of societal focus"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes} {scene.description}".lower()

        scope_patterns = {
            "Global": [r"\b(?:world|global|international|humanity|planet|earth)\b"],
            "National": [r"\b(?:country|nation|america|government|congress|state)\b"],
            "Community": [r"\b(?:community|neighborhood|town|city|local|society)\b"],
            "Individual": [r"\b(?:personal|individual|self|me|i|my|myself)\b"],
        }

        scope_scores = {}
        for scope, patterns in scope_patterns.items():
            score = sum(len(re.findall(pattern, all_text)) for pattern in patterns)
            if score > 0:
                scope_scores[scope] = score

        if scope_scores:
            return max(scope_scores, key=scope_scores.get)
        else:
            return "Individual"

    def analyze_scene_cultural_commentary(self, scene: SceneData) -> CulturalAnalysis:
        """Perform comprehensive cultural and social commentary analysis"""
        analysis_start = time.time()

        print(f"🌍 Analyzing cultural commentary for: {scene.title}")

        # Extract social and cultural content
        social_content = self.extract_social_content(scene)
        print(f"   📢 Found {len(social_content['themes'])} social themes")

        # Perform component analyses
        theme_score, theme_elements = self.analyze_social_theme_depth(scene)
        relevance_score, relevance_indicators = self.analyze_cultural_relevance(scene)
        sophistication_score, sophistication_elements = (
            self.analyze_commentary_sophistication(scene)
        )
        impact_score, impact_elements = self.analyze_societal_impact_potential(scene)

        # Determine cultural characteristics
        primary_theme = self.identify_primary_social_theme(scene)
        cultural_perspective = self.determine_cultural_perspective(scene)
        commentary_approach = self.determine_commentary_approach(scene)
        societal_scope = self.determine_societal_scope(scene)

        # Calculate overall cultural score
        overall_score = (
            theme_score + relevance_score + sophistication_score + impact_score
        ) / 4

        analysis_time = time.time() - analysis_start

        print(f"   🏛️ Theme Depth: {theme_score:.1f}/10")
        print(f"   📱 Cultural Relevance: {relevance_score:.1f}/10")
        print(f"   🧠 Sophistication: {sophistication_score:.1f}/10")
        print(f"   💥 Impact Potential: {impact_score:.1f}/10")
        print(f"   🏆 Overall Cultural Score: {overall_score:.1f}/10")
        print(
            f"   🎯 Focus: {primary_theme[:30]}... | Perspective: {cultural_perspective} | Approach: {commentary_approach}"
        )

        return CulturalAnalysis(
            scene_title=scene.title,
            social_theme_depth=theme_score,
            cultural_relevance_score=relevance_score,
            commentary_sophistication=sophistication_score,
            societal_impact_potential=impact_score,
            overall_cultural_score=overall_score,
            social_themes_identified=social_content["themes"],
            cultural_references=social_content["contemporary_markers"],
            commentary_techniques=social_content["techniques"],
            impact_indicators=impact_elements,
            contemporary_connections=relevance_indicators,
            primary_social_theme=primary_theme,
            cultural_perspective=cultural_perspective,
            commentary_approach=commentary_approach,
            societal_scope=societal_scope,
            analysis_time=analysis_time,
        )


def run_cultural_commentary_analysis():
    """Run cultural and social commentary analysis on all musicals"""

    print("🖖🌍 CULTURAL & SOCIAL COMMENTARY EVALUATION - KEEP ON TREKKIN!")
    print("=" * 65)
    print("Analyzing social impact, cultural depth, and commentary sophistication")
    print("Components: Theme Depth, Cultural Relevance, Sophistication, Impact\n")

    analyzer = CulturalCommentaryAnalyzer()

    # Musical scenes for cultural commentary analysis
    musical_scenes = [
        {
            "file": "all_musicals_analysis/echo_musical/json/scene_01.json",
            "musical": "Echo Musical - AI Consciousness & Memory",
            "genre": "Sci-Fi Drama",
        },
        {
            "file": "all_musicals_analysis/electric_dreams_musical/json/scene_01.json",
            "musical": "Electric Dreams Musical - Technology & Desire",
            "genre": "Techno-Romance",
        },
        {
            "file": "all_musicals_analysis/midnight_at_the_majestic_musical/json/scene_02.json",
            "musical": "Midnight at the Majestic Musical - Theater Murder Mystery",
            "genre": "Murder Mystery",
        },
        {
            "file": "all_musicals_analysis/neon_hearts_burlesque_musical/json/scene_01.json",
            "musical": "Neon Hearts Burlesque Musical - Underground Cabaret",
            "genre": "Contemporary Drama",
        },
        {
            "file": "all_musicals_analysis/neon_rebellion_musical/json/scene_01.json",
            "musical": "Neon Rebellion Musical - Dystopian Resistance",
            "genre": "Dystopian Action",
        },
        {
            "file": "all_musicals_analysis/rainbow_academy_musical/json/scene_01.json",
            "musical": "Rainbow Academy Musical - Magic School Adventure",
            "genre": "Fantasy Musical Theater",
        },
    ]

    results = []
    total_start = time.time()

    for i, scene_info in enumerate(musical_scenes, 1):
        try:
            print(f"🎪 CULTURAL ANALYSIS {i}/6: {scene_info['musical']}")
            print("-" * 60)

            # Load scene
            scene_path = Path(scene_info["file"])
            if not scene_path.exists():
                print(f"❌ Scene file not found: {scene_info['file']}")
                continue

            with open(scene_path, "r", encoding="utf-8") as f:
                scene_data = json.load(f)
            scene = SceneData(**scene_data)

            print(f"Scene: {scene.title}")
            print(f"Genre: {scene_info['genre']}")

            # Perform cultural commentary analysis
            analysis = analyzer.analyze_scene_cultural_commentary(scene)

            # Format result
            result = {
                "rank": i,
                "musical_name": scene_info["musical"],
                "genre": scene_info["genre"],
                "scene_title": analysis.scene_title,
                "cultural_scores": {
                    "overall_cultural_score": round(analysis.overall_cultural_score, 2),
                    "social_theme_depth": round(analysis.social_theme_depth, 2),
                    "cultural_relevance_score": round(
                        analysis.cultural_relevance_score, 2
                    ),
                    "commentary_sophistication": round(
                        analysis.commentary_sophistication, 2
                    ),
                    "societal_impact_potential": round(
                        analysis.societal_impact_potential, 2
                    ),
                },
                "cultural_characteristics": {
                    "primary_social_theme": analysis.primary_social_theme,
                    "cultural_perspective": analysis.cultural_perspective,
                    "commentary_approach": analysis.commentary_approach,
                    "societal_scope": analysis.societal_scope,
                },
                "cultural_details": {
                    "social_themes_identified": analysis.social_themes_identified,
                    "cultural_references": analysis.cultural_references,
                    "commentary_techniques": analysis.commentary_techniques,
                    "impact_indicators": analysis.impact_indicators,
                    "contemporary_connections": analysis.contemporary_connections,
                },
                "analysis_time": round(analysis.analysis_time, 2),
            }

            results.append(result)
            print()

        except Exception as e:
            print(f"❌ Error analyzing {scene_info['musical']}: {e}")
            continue

    total_time = time.time() - total_start

    # Sort by overall cultural score
    results.sort(
        key=lambda x: x["cultural_scores"]["overall_cultural_score"], reverse=True
    )

    # Update rankings
    for i, result in enumerate(results, 1):
        result["rank"] = i

    print("=" * 65)
    print("🏆 CULTURAL & SOCIAL COMMENTARY RANKINGS")
    print("=" * 65)

    if results:
        # Calculate statistics
        cultural_scores = [
            r["cultural_scores"]["overall_cultural_score"] for r in results
        ]
        collection_average = sum(cultural_scores) / len(cultural_scores)
        score_range = max(cultural_scores) - min(cultural_scores)

        print(f"Collection Average: {collection_average:.1f}/10.0")
        print(f"Score Range: {score_range:.1f} points")
        print(f"Analysis Time: {total_time:.1f} seconds")
        print(f"Musicals Analyzed: {len(results)}/6")
        print()

        # Component averages
        theme_avg = sum(
            r["cultural_scores"]["social_theme_depth"] for r in results
        ) / len(results)
        relevance_avg = sum(
            r["cultural_scores"]["cultural_relevance_score"] for r in results
        ) / len(results)
        sophistication_avg = sum(
            r["cultural_scores"]["commentary_sophistication"] for r in results
        ) / len(results)
        impact_avg = sum(
            r["cultural_scores"]["societal_impact_potential"] for r in results
        ) / len(results)

        print("📊 COMPONENT AVERAGES:")
        print(f"   Social Theme Depth: {theme_avg:.1f}/10")
        print(f"   Cultural Relevance: {relevance_avg:.1f}/10")
        print(f"   Commentary Sophistication: {sophistication_avg:.1f}/10")
        print(f"   Societal Impact Potential: {impact_avg:.1f}/10")
        print()

        # Detailed rankings
        print("🎭 DETAILED CULTURAL RANKINGS:")
        for result in results:
            scores = result["cultural_scores"]
            chars = result["cultural_characteristics"]
            print(f"{result['rank']}. {result['musical_name']}")
            print(
                f"   Overall: {scores['overall_cultural_score']}/10 | Genre: {result['genre']}"
            )
            print(
                f"   Theme:{scores['social_theme_depth']:.1f} Relevance:{scores['cultural_relevance_score']:.1f} Sophist:{scores['commentary_sophistication']:.1f} Impact:{scores['societal_impact_potential']:.1f}"
            )
            print(f"   Focus: {chars['primary_social_theme'][:40]}...")
            print(
                f"   Perspective: {chars['cultural_perspective']} | Approach: {chars['commentary_approach']} | Scope: {chars['societal_scope']}"
            )
            print()

        # Cultural pattern analysis
        print("🌍 CULTURAL COMMENTARY PATTERNS:")

        # Perspectives
        perspective_counts = {}
        for result in results:
            perspective = result["cultural_characteristics"]["cultural_perspective"]
            perspective_counts[perspective] = perspective_counts.get(perspective, 0) + 1

        print("   Cultural Perspectives:")
        for perspective, count in perspective_counts.items():
            print(f"     {perspective}: {count} musicals")

        # Approaches
        approach_counts = {}
        for result in results:
            approach = result["cultural_characteristics"]["commentary_approach"]
            approach_counts[approach] = approach_counts.get(approach, 0) + 1

        print("   Commentary Approaches:")
        for approach, count in approach_counts.items():
            print(f"     {approach}: {count} musicals")

        # Societal scope
        scope_counts = {}
        for result in results:
            scope = result["cultural_characteristics"]["societal_scope"]
            scope_counts[scope] = scope_counts.get(scope, 0) + 1

        print("   Societal Scope:")
        for scope, count in scope_counts.items():
            print(f"     {scope}: {count} musicals")

        # Save results
        output_data = {
            "analysis_metadata": {
                "analysis_type": "Cultural & Social Commentary Evaluation",
                "analysis_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_musicals": len(results),
                "collection_average": round(collection_average, 2),
                "score_range": round(score_range, 2),
                "analysis_time_seconds": round(total_time, 1),
                "component_averages": {
                    "social_theme_depth": round(theme_avg, 2),
                    "cultural_relevance_score": round(relevance_avg, 2),
                    "commentary_sophistication": round(sophistication_avg, 2),
                    "societal_impact_potential": round(impact_avg, 2),
                },
            },
            "cultural_rankings": results,
            "cultural_patterns": {
                "perspectives": perspective_counts,
                "approaches": approach_counts,
                "societal_scope": scope_counts,
            },
        }

        with open("CULTURAL_commentary_analysis.json", "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Cultural analysis saved to: CULTURAL_commentary_analysis.json")
        print(
            "🌍🖖 Cultural & Social Commentary Evaluation complete - KEPT ON TREKKIN!"
        )

        return results

    else:
        print("❌ No analyses completed")
        return []


if __name__ == "__main__":
    print("🚀 Starting Cultural & Social Commentary Evaluation - KEEP ON TREKKIN!")
    run_cultural_commentary_analysis()
