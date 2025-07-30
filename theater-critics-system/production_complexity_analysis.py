#!/usr/bin/env python3
"""
Production Complexity & Staging Requirements Analysis
Evaluates technical demands, staging complexity, resource requirements, and production feasibility
"""

import json
import re
import time
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
from main import SceneData

@dataclass
class ProductionAnalysis:
    """Results of production complexity and staging requirements analysis"""
    scene_title: str
    technical_demands_score: float        # 0-10 - Complexity of technical requirements
    staging_complexity_score: float       # 0-10 - Difficulty of staging and choreography
    resource_requirements_score: float    # 0-10 - Budget and resource intensity
    production_feasibility_score: float   # 0-10 - Practical implementation difficulty
    overall_production_score: float       # 0-10 - Combined production complexity
    
    # Detailed production mapping
    technical_elements: List[str]
    staging_challenges: List[str]
    resource_needs: List[str]
    feasibility_factors: List[str]
    production_scale_indicators: List[str]
    
    # Production characteristics
    technical_complexity: str       # "Basic", "Intermediate", "Advanced", "Expert"
    staging_difficulty: str         # "Simple", "Moderate", "Complex", "Virtuosic"
    budget_category: str           # "Low", "Medium", "High", "Premium"
    production_scale: str          # "Intimate", "Standard", "Large", "Spectacular"
    
    analysis_time: float

class ProductionComplexityAnalyzer:
    """Specialized analyzer for production complexity and staging requirements"""
    
    def __init__(self):
        # Technical elements taxonomy
        self.technical_elements = {
            "lighting": {
                "basic": ["lights", "spotlight", "lighting", "bright", "dim", "dark"],
                "intermediate": ["color change", "follow spot", "gobo", "haze", "fog", "strobe"],
                "advanced": ["moving lights", "led wall", "projection", "mapping", "automated", "dmx"],
                "expert": ["holographic", "3d projection", "volumetric", "laser", "pyrotechnics", "special effects"],
                "weight": 1.2
            },
            "sound": {
                "basic": ["music", "sound", "audio", "microphone", "speaker"],
                "intermediate": ["amplification", "sound effects", "reverb", "echo", "mixing"],
                "advanced": ["surround sound", "multi-track", "live mixing", "sound design", "spatial audio"],
                "expert": ["immersive audio", "binaural", "3d audio", "real-time processing", "ai-driven sound"],
                "weight": 1.1
            },
            "set_design": {
                "basic": ["stage", "backdrop", "props", "furniture", "curtain"],
                "intermediate": ["multi-level", "platforms", "stairs", "turntable", "fly system"],
                "advanced": ["automated scenery", "hydraulics", "moving platforms", "complex rigging", "scene changes"],
                "expert": ["robotic sets", "augmented reality", "interactive environments", "real-time transformation"],
                "weight": 1.3
            },
            "costumes": {
                "basic": ["costume", "clothing", "dress", "outfit", "wardrobe"],
                "intermediate": ["period costumes", "character design", "makeup", "wigs", "accessories"],
                "advanced": ["quick changes", "transformation", "complex makeup", "prosthetics", "special materials"],
                "expert": ["interactive costumes", "led integration", "motion capture suits", "shape-shifting"],
                "weight": 1.0
            },
            "choreography": {
                "basic": ["dance", "movement", "choreography", "blocking", "staging"],
                "intermediate": ["ensemble", "formation", "partner work", "lifts", "synchronized"],
                "advanced": ["aerial work", "acrobatics", "complex partnering", "multi-level", "precision timing"],
                "expert": ["circus arts", "wire work", "parkour", "extreme athletics", "gravity-defying"],
                "weight": 1.2
            },
            "special_effects": {
                "basic": ["smoke", "fog", "bubble", "confetti", "streamers"],
                "intermediate": ["pyrotechnics", "flash pots", "flame", "explosions", "wind"],
                "advanced": ["holographics", "projection mapping", "augmented reality", "interactive effects"],
                "expert": ["volumetric display", "force feedback", "environmental control", "weather simulation"],
                "weight": 1.4
            }
        }
        
        # Staging complexity indicators
        self.staging_complexity_markers = {
            "cast_size": [
                (r'\bensemble\b', 2),
                (r'\bchorus\b', 2),
                (r'\bmultiple characters\b', 3),
                (r'\bcrowd\b', 3),
                (r'\bmultitudes\b', 4)
            ],
            "movement_complexity": [
                (r'\bchoreography\b', 1),
                (r'\bdance\b', 1),
                (r'\bformation\b', 2),
                (r'\bsynchronized\b', 2),
                (r'\bacrobatic\b', 3),
                (r'\baerial\b', 4)
            ],
            "scene_changes": [
                (r'\bscene change\b', 2),
                (r'\btransformation\b', 2),
                (r'\bquick change\b', 3),
                (r'\binstant\b', 3),
                (r'\bseamless\b', 2)
            ],
            "timing_precision": [
                (r'\bprecise\b', 1),
                (r'\btiming\b', 1),
                (r'\bsynchronize\b', 2),
                (r'\bcoordination\b', 2),
                (r'\bsplit-second\b', 3)
            ]
        }
        
        # Resource requirement indicators
        self.resource_indicators = {
            "personnel": [
                r'\bcast of \d+\b',
                r'\borchestra\b',
                r'\bmusicians\b',
                r'\btechnicians\b',
                r'\bcrew\b',
                r'\boperators\b'
            ],
            "equipment": [
                r'\bequipment\b',
                r'\bmachinery\b',
                r'\bapparatus\b',
                r'\brig\b',
                r'\bsystem\b',
                r'\btechnology\b'
            ],
            "space": [
                r'\blarge stage\b',
                r'\bmultiple levels\b',
                r'\bexpansive\b',
                r'\bwide area\b',
                r'\bvast space\b'
            ],
            "time": [
                r'\brehearsals\b',
                r'\btraining\b',
                r'\bpreparation\b',
                r'\bmonths\b',
                r'\bextensive\b'
            ]
        }
        
        # Feasibility challenge indicators
        self.feasibility_challenges = {
            "technical_difficulty": [
                r'\bcomplex\b',
                r'\bdifficult\b',
                r'\bchallenging\b',
                r'\bintricate\b',
                r'\bsophisticated\b',
                r'\badvanced\b'
            ],
            "safety_concerns": [
                r'\bdangerous\b',
                r'\brisky\b',
                r'\bsafety\b',
                r'\bhazard\b',
                r'\bprecaution\b',
                r'\bprotection\b'
            ],
            "coordination_needs": [
                r'\bcoordination\b',
                r'\bsynchronization\b',
                r'\btiming\b',
                r'\bprecision\b',
                r'\bexact\b'
            ],
            "budget_constraints": [
                r'\bexpensive\b',
                r'\bcostly\b',
                r'\bhigh-end\b',
                r'\bpremium\b',
                r'\bluxury\b',
                r'\bcustom\b'
            ]
        }
        
        # Production scale indicators
        self.scale_indicators = {
            "intimate": ["small", "intimate", "minimal", "simple", "basic", "solo", "duo"],
            "standard": ["standard", "typical", "normal", "regular", "conventional", "moderate"],
            "large": ["large", "big", "extensive", "major", "significant", "substantial"],
            "spectacular": ["spectacular", "grand", "epic", "massive", "enormous", "extraordinary", "breathtaking"]
        }
    
    def extract_production_elements(self, scene: SceneData) -> Dict[str, List[str]]:
        """Extract production-related content from scene"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes} {scene.description}".lower()
        
        production_content = {
            "technical": [],
            "staging": [],
            "resources": [],
            "scale_indicators": []
        }
        
        # Extract technical elements
        for category, levels in self.technical_elements.items():
            for level, keywords in levels.items():
                if level == "weight":
                    continue
                matches = sum(1 for keyword in keywords if keyword in all_text)
                if matches > 0:
                    production_content["technical"].append(f"{category.title()} ({level}): {matches} references")
        
        # Extract staging complexity markers
        for category, patterns in self.staging_complexity_markers.items():
            for pattern, weight in patterns:
                matches = len(re.findall(pattern, all_text))
                if matches > 0:
                    production_content["staging"].append(f"{category.replace('_', ' ').title()}: {matches} instances")
        
        # Extract resource indicators
        for category, patterns in self.resource_indicators.items():
            for pattern in patterns:
                matches = len(re.findall(pattern, all_text))
                if matches > 0:
                    production_content["resources"].append(f"{category.title()}: {matches} references")
        
        return production_content
    
    def analyze_technical_demands(self, scene: SceneData) -> Tuple[float, List[str]]:
        """Analyze the complexity of technical requirements"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes} {scene.description}".lower()
        
        technical_elements = []
        technical_score = 0.0
        
        # Analyze each technical category
        for category, levels in self.technical_elements.items():
            category_score = 0.0
            category_complexity = "basic"
            
            # Check complexity levels (higher levels override lower ones)
            for level in ["basic", "intermediate", "advanced", "expert"]:
                if level == "weight":
                    continue
                    
                keywords = levels.get(level, [])
                matches = sum(1 for keyword in keywords if keyword in all_text)
                
                if matches > 0:
                    # Score based on complexity level
                    level_multipliers = {"basic": 1.0, "intermediate": 2.0, "advanced": 3.5, "expert": 5.0}
                    level_score = matches * level_multipliers[level]
                    
                    if level_score > category_score:
                        category_score = level_score
                        category_complexity = level
            
            if category_score > 0:
                # Apply category weight
                weighted_score = category_score * levels.get("weight", 1.0)
                technical_score += weighted_score
                technical_elements.append(f"{category.title()}: {category_complexity} level")
        
        # Look for cutting-edge technology indicators
        cutting_edge_patterns = [
            r'\b(?:ai|artificial intelligence|machine learning)\b',
            r'\b(?:virtual reality|vr|augmented reality|ar|mixed reality)\b',
            r'\b(?:holographic|hologram|3d projection|volumetric)\b',
            r'\b(?:real-time|interactive|responsive|adaptive)\b',
            r'\b(?:motion capture|mocap|facial capture|performance capture)\b'
        ]
        
        cutting_edge_count = sum(len(re.findall(pattern, all_text)) for pattern in cutting_edge_patterns)
        if cutting_edge_count > 0:
            technical_score += cutting_edge_count * 2.5
            technical_elements.append(f"Cutting-edge technology: {cutting_edge_count} innovations")
        
        # Integration complexity bonus
        integration_patterns = [
            r'\b(?:synchronized|coordinated|integrated|unified)\b',
            r'\b(?:seamless|smooth|flowing|continuous)\b',
            r'\b(?:multi-system|cross-platform|interconnected)\b'
        ]
        
        integration_count = sum(len(re.findall(pattern, all_text)) for pattern in integration_patterns)
        if integration_count > 0:
            technical_score += min(2.0, integration_count * 0.4)
            technical_elements.append(f"System integration: {integration_count} coordination points")
        
        final_score = min(10.0, technical_score * 0.4)  # Scale to 0-10
        
        return final_score, technical_elements[:5]
    
    def analyze_staging_complexity(self, scene: SceneData) -> Tuple[float, List[str]]:
        """Analyze the difficulty of staging and choreography"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes} {scene.description}".lower()
        
        staging_challenges = []
        staging_score = 0.0
        
        # Analyze staging complexity markers
        for category, patterns in self.staging_complexity_markers.items():
            category_total = 0
            for pattern, weight in patterns:
                matches = len(re.findall(pattern, all_text))
                if matches > 0:
                    category_total += matches * weight
            
            if category_total > 0:
                staging_score += min(2.5, category_total * 0.3)
                staging_challenges.append(f"{category.replace('_', ' ').title()}: {category_total} complexity points")
        
        # Multi-level staging analysis
        level_patterns = [
            r'\b(?:multi-level|multiple levels|different heights)\b',
            r'\b(?:platforms|raised|elevated|tiered)\b',
            r'\b(?:stairs|ramps|bridges|catwalks)\b',
            r'\b(?:upper|lower|above|below|beneath)\b'
        ]
        
        level_count = sum(len(re.findall(pattern, all_text)) for pattern in level_patterns)
        if level_count > 0:
            staging_score += min(2.0, level_count * 0.6)
            staging_challenges.append(f"Multi-level staging: {level_count} vertical elements")
        
        # Crowd and ensemble management
        crowd_patterns = [
            r'\b(?:ensemble|chorus|crowd|multitude|masses)\b',
            r'\b(?:hundreds|dozens|many|numerous|countless)\b',
            r'\b(?:formation|group|collective|together)\b'
        ]
        
        crowd_count = sum(len(re.findall(pattern, all_text)) for pattern in crowd_patterns)
        if crowd_count > 2:  # Only count if significant
            staging_score += min(2.0, (crowd_count - 2) * 0.4)
            staging_challenges.append(f"Ensemble management: {crowd_count} group elements")
        
        # Movement and choreography complexity
        movement_patterns = [
            r'\b(?:intricate|complex|elaborate|sophisticated)\s+(?:choreography|movement|dance)\b',
            r'\b(?:acrobatic|athletic|gymnastic|aerial)\b',
            r'\b(?:lifts|throws|catches|partner work)\b',
            r'\b(?:precision|exact|perfect|flawless)\b'
        ]
        
        movement_count = sum(len(re.findall(pattern, all_text)) for pattern in movement_patterns)
        if movement_count > 0:
            staging_score += movement_count * 0.8
            staging_challenges.append(f"Complex movement: {movement_count} advanced techniques")
        
        # Timing and synchronization challenges
        timing_patterns = [
            r'\b(?:split-second|precise timing|exact moment)\b',
            r'\b(?:synchronized|coordinated|simultaneous)\b',
            r'\b(?:cue|signal|mark|beat)\b'
        ]
        
        timing_count = sum(len(re.findall(pattern, all_text)) for pattern in timing_patterns)
        if timing_count > 0:
            staging_score += min(1.5, timing_count * 0.3)
            staging_challenges.append(f"Timing precision: {timing_count} synchronization points")
        
        final_score = min(10.0, staging_score)
        
        return final_score, staging_challenges[:5]
    
    def analyze_resource_requirements(self, scene: SceneData) -> Tuple[float, List[str]]:
        """Analyze budget and resource intensity"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes} {scene.description}".lower()
        
        resource_needs = []
        resource_score = 0.0
        
        # Personnel requirements
        personnel_patterns = [
            (r'\bcast of (\d+)\b', 3),  # Specific cast size
            (r'\borchestra\b', 2),
            (r'\bmultiple musicians\b', 2),
            (r'\btechnicians\b', 1),
            (r'\bspecialists\b', 2),
            (r'\bexperts\b', 2)
        ]
        
        personnel_total = 0
        for pattern, multiplier in personnel_patterns:
            matches = re.findall(pattern, all_text)
            if matches:
                if pattern.startswith(r'\bcast of'):  # Handle numeric cast size
                    cast_size = int(matches[0])
                    personnel_total += cast_size * 0.1
                else:
                    personnel_total += len(matches) * multiplier
        
        if personnel_total > 0:
            resource_score += min(3.0, personnel_total * 0.2)
            resource_needs.append(f"Personnel requirements: {personnel_total:.1f} resource points")
        
        # Equipment and technology costs
        equipment_patterns = [
            (r'\b(?:custom|bespoke|specially made|one-of-a-kind)\b', 3),
            (r'\b(?:high-end|premium|professional|commercial grade)\b', 2),
            (r'\b(?:automated|robotic|computer-controlled)\b', 2),
            (r'\b(?:specialized|unique|rare|exotic)\b', 2)
        ]
        
        equipment_total = 0
        for pattern, multiplier in equipment_patterns:
            matches = len(re.findall(pattern, all_text))
            equipment_total += matches * multiplier
        
        if equipment_total > 0:
            resource_score += min(2.5, equipment_total * 0.3)
            resource_needs.append(f"Equipment complexity: {equipment_total} tech points")
        
        # Space and venue requirements
        space_patterns = [
            r'\b(?:large stage|expansive|vast|enormous)\b',
            r'\b(?:multiple venues|different locations|various spaces)\b',
            r'\b(?:outdoor|arena|stadium|amphitheater)\b',
            r'\b(?:custom venue|specially designed|purpose-built)\b'
        ]
        
        space_count = sum(len(re.findall(pattern, all_text)) for pattern in space_patterns)
        if space_count > 0:
            resource_score += space_count * 0.8
            resource_needs.append(f"Space requirements: {space_count} venue factors")
        
        # Time and preparation intensity
        time_patterns = [
            r'\b(?:months of rehearsal|extensive preparation|long training)\b',
            r'\b(?:complex rehearsal|intensive practice)\b',
            r'\b(?:specialized training|expert coaching)\b'
        ]
        
        time_count = sum(len(re.findall(pattern, all_text)) for pattern in time_patterns)
        if time_count > 0:
            resource_score += time_count * 0.6
            resource_needs.append(f"Time investment: {time_count} preparation factors")
        
        # Material and construction costs
        material_patterns = [
            r'\b(?:elaborate sets|complex scenery|intricate props)\b',
            r'\b(?:custom costumes|designer|handmade|artisan)\b',
            r'\b(?:expensive materials|premium|luxury|high-quality)\b'
        ]
        
        material_count = sum(len(re.findall(pattern, all_text)) for pattern in material_patterns)
        if material_count > 0:
            resource_score += material_count * 0.7
            resource_needs.append(f"Material costs: {material_count} luxury factors")
        
        final_score = min(10.0, resource_score)
        
        return final_score, resource_needs[:5]
    
    def analyze_production_feasibility(self, scene: SceneData) -> Tuple[float, List[str]]:
        """Analyze practical implementation difficulty"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes} {scene.description}".lower()
        
        feasibility_factors = []
        feasibility_score = 10.0  # Start high, subtract for challenges
        
        # Technical feasibility challenges
        for challenge_type, patterns in self.feasibility_challenges.items():
            challenge_count = sum(len(re.findall(pattern, all_text)) for pattern in patterns)
            if challenge_count > 0:
                # Subtract points for each challenge type
                penalty_weights = {
                    "technical_difficulty": 0.8,
                    "safety_concerns": 1.2,
                    "coordination_needs": 0.6,
                    "budget_constraints": 1.0
                }
                
                penalty = challenge_count * penalty_weights.get(challenge_type, 0.7)
                feasibility_score -= min(2.5, penalty)
                feasibility_factors.append(f"{challenge_type.replace('_', ' ').title()}: {challenge_count} challenges")
        
        # Implementation risk factors
        risk_patterns = [
            r'\b(?:untested|experimental|unproven|prototype)\b',
            r'\b(?:first time|never done|unprecedented|groundbreaking)\b',
            r'\b(?:risky|dangerous|hazardous|uncertain)\b',
            r'\b(?:might fail|could break|may not work)\b'
        ]
        
        risk_count = sum(len(re.findall(pattern, all_text)) for pattern in risk_patterns)
        if risk_count > 0:
            feasibility_score -= risk_count * 0.9
            feasibility_factors.append(f"Implementation risks: {risk_count} risk factors")
        
        # Dependency complexity
        dependency_patterns = [
            r'\b(?:depends on|requires|needs|must have)\b',
            r'\b(?:contingent|conditional|subject to)\b',
            r'\b(?:if and only if|provided that|assuming)\b'
        ]
        
        dependency_count = sum(len(re.findall(pattern, all_text)) for pattern in dependency_patterns)
        if dependency_count > 3:  # Only penalize excessive dependencies
            feasibility_score -= (dependency_count - 3) * 0.3
            feasibility_factors.append(f"Dependencies: {dependency_count} conditional factors")
        
        # Skill availability challenges
        skill_patterns = [
            r'\b(?:expert|specialist|master|virtuoso|professional)\b',
            r'\b(?:rare skill|unique talent|special ability)\b',
            r'\b(?:years of training|extensive experience)\b'
        ]
        
        skill_count = sum(len(re.findall(pattern, all_text)) for pattern in skill_patterns)
        if skill_count > 2:
            feasibility_score -= (skill_count - 2) * 0.4
            feasibility_factors.append(f"Specialized skills: {skill_count} expert requirements")
        
        # Add feasibility bonuses for practical elements
        practical_patterns = [
            r'\b(?:simple|straightforward|easy|basic)\b',
            r'\b(?:standard|conventional|traditional|proven)\b',
            r'\b(?:reliable|stable|tested|established)\b'
        ]
        
        practical_count = sum(len(re.findall(pattern, all_text)) for pattern in practical_patterns)
        if practical_count > 0:
            feasibility_score += min(2.0, practical_count * 0.2)
            feasibility_factors.append(f"Practical elements: {practical_count} simplifying factors")
        
        final_score = max(0.0, min(10.0, feasibility_score))
        
        return final_score, feasibility_factors[:5]
    
    def determine_technical_complexity(self, technical_score: float) -> str:
        """Determine overall technical complexity level"""
        if technical_score >= 8.0:
            return "Expert"
        elif technical_score >= 6.0:
            return "Advanced"
        elif technical_score >= 3.0:
            return "Intermediate"
        else:
            return "Basic"
    
    def determine_staging_difficulty(self, staging_score: float) -> str:
        """Determine staging difficulty level"""
        if staging_score >= 8.0:
            return "Virtuosic"
        elif staging_score >= 6.0:
            return "Complex"
        elif staging_score >= 3.0:
            return "Moderate"
        else:
            return "Simple"
    
    def determine_budget_category(self, resource_score: float) -> str:
        """Determine budget category"""
        if resource_score >= 7.5:
            return "Premium"
        elif resource_score >= 5.0:
            return "High"
        elif resource_score >= 2.5:
            return "Medium"
        else:
            return "Low"
    
    def determine_production_scale(self, scene: SceneData) -> str:
        """Determine overall production scale"""
        all_text = f"{scene.lyrics} {scene.stage_directions} {scene.character_notes} {scene.description}".lower()
        
        scale_scores = {}
        for scale, keywords in self.scale_indicators.items():
            score = sum(1 for keyword in keywords if keyword in all_text)
            if score > 0:
                scale_scores[scale] = score
        
        if scale_scores:
            return max(scale_scores, key=scale_scores.get).title()
        else:
            return "Standard"
    
    def analyze_scene_production(self, scene: SceneData) -> ProductionAnalysis:
        """Perform comprehensive production complexity analysis"""
        analysis_start = time.time()
        
        print(f"🎭 Analyzing production complexity for: {scene.title}")
        
        # Extract production elements
        production_content = self.extract_production_elements(scene)
        print(f"   🔧 Found {len(production_content['technical'])} technical elements")
        
        # Perform component analyses
        technical_score, technical_elements = self.analyze_technical_demands(scene)
        staging_score, staging_challenges = self.analyze_staging_complexity(scene)
        resource_score, resource_needs = self.analyze_resource_requirements(scene)
        feasibility_score, feasibility_factors = self.analyze_production_feasibility(scene)
        
        # Determine production characteristics
        technical_complexity = self.determine_technical_complexity(technical_score)
        staging_difficulty = self.determine_staging_difficulty(staging_score)
        budget_category = self.determine_budget_category(resource_score)
        production_scale = self.determine_production_scale(scene)
        
        # Calculate overall production score (weighted average)
        # Feasibility is inverted (higher feasibility = lower complexity for overall score)
        overall_score = (technical_score * 0.3 + staging_score * 0.3 + 
                        resource_score * 0.2 + (10 - feasibility_score) * 0.2)
        
        analysis_time = time.time() - analysis_start
        
        print(f"   ⚙️ Technical Demands: {technical_score:.1f}/10")
        print(f"   🎪 Staging Complexity: {staging_score:.1f}/10")
        print(f"   💰 Resource Requirements: {resource_score:.1f}/10")
        print(f"   ✅ Production Feasibility: {feasibility_score:.1f}/10")
        print(f"   🏆 Overall Production Score: {overall_score:.1f}/10")
        print(f"   📊 Tech: {technical_complexity} | Staging: {staging_difficulty} | Budget: {budget_category} | Scale: {production_scale}")
        
        return ProductionAnalysis(
            scene_title=scene.title,
            technical_demands_score=technical_score,
            staging_complexity_score=staging_score,
            resource_requirements_score=resource_score,
            production_feasibility_score=feasibility_score,
            overall_production_score=overall_score,
            technical_elements=technical_elements,
            staging_challenges=staging_challenges,
            resource_needs=resource_needs,
            feasibility_factors=feasibility_factors,
            production_scale_indicators=production_content["technical"],
            technical_complexity=technical_complexity,
            staging_difficulty=staging_difficulty,
            budget_category=budget_category,
            production_scale=production_scale,
            analysis_time=analysis_time
        )

def run_production_complexity_analysis():
    """Run production complexity analysis on all musicals"""
    
    print("🖖⚡ PRODUCTION COMPLEXITY & STAGING REQUIREMENTS - ENGAGE!")
    print("=" * 65)
    print("Analyzing technical demands, staging complexity, and resource requirements")
    print("Components: Technical, Staging, Resources, Feasibility\n")
    
    analyzer = ProductionComplexityAnalyzer()
    
    # Musical scenes for production analysis
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
            print(f"🎪 PRODUCTION ANALYSIS {i}/6: {scene_info['musical']}")
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
            
            # Perform production analysis
            analysis = analyzer.analyze_scene_production(scene)
            
            # Format result
            result = {
                "rank": i,
                "musical_name": scene_info['musical'],
                "genre": scene_info['genre'],
                "scene_title": analysis.scene_title,
                "production_scores": {
                    "overall_production_score": round(analysis.overall_production_score, 2),
                    "technical_demands_score": round(analysis.technical_demands_score, 2),
                    "staging_complexity_score": round(analysis.staging_complexity_score, 2),
                    "resource_requirements_score": round(analysis.resource_requirements_score, 2),
                    "production_feasibility_score": round(analysis.production_feasibility_score, 2)
                },
                "production_characteristics": {
                    "technical_complexity": analysis.technical_complexity,
                    "staging_difficulty": analysis.staging_difficulty,
                    "budget_category": analysis.budget_category,
                    "production_scale": analysis.production_scale
                },
                "production_details": {
                    "technical_elements": analysis.technical_elements,
                    "staging_challenges": analysis.staging_challenges,
                    "resource_needs": analysis.resource_needs,
                    "feasibility_factors": analysis.feasibility_factors
                },
                "analysis_time": round(analysis.analysis_time, 2)
            }
            
            results.append(result)
            print()
            
        except Exception as e:
            print(f"❌ Error analyzing {scene_info['musical']}: {e}")
            continue
    
    total_time = time.time() - total_start
    
    # Sort by overall production score (higher = more complex)
    results.sort(key=lambda x: x['production_scores']['overall_production_score'], reverse=True)
    
    # Update rankings
    for i, result in enumerate(results, 1):
        result['rank'] = i
    
    print("=" * 65)
    print("🏆 PRODUCTION COMPLEXITY & STAGING RANKINGS")
    print("=" * 65)
    
    if results:
        # Calculate statistics
        production_scores = [r['production_scores']['overall_production_score'] for r in results]
        collection_average = sum(production_scores) / len(production_scores)
        score_range = max(production_scores) - min(production_scores)
        
        print(f"Collection Average: {collection_average:.1f}/10.0")
        print(f"Score Range: {score_range:.1f} points")
        print(f"Analysis Time: {total_time:.1f} seconds")
        print(f"Musicals Analyzed: {len(results)}/6")
        print()
        
        # Component averages
        technical_avg = sum(r['production_scores']['technical_demands_score'] for r in results) / len(results)
        staging_avg = sum(r['production_scores']['staging_complexity_score'] for r in results) / len(results)
        resource_avg = sum(r['production_scores']['resource_requirements_score'] for r in results) / len(results)
        feasibility_avg = sum(r['production_scores']['production_feasibility_score'] for r in results) / len(results)
        
        print("📊 COMPONENT AVERAGES:")
        print(f"   Technical Demands: {technical_avg:.1f}/10")
        print(f"   Staging Complexity: {staging_avg:.1f}/10")
        print(f"   Resource Requirements: {resource_avg:.1f}/10")
        print(f"   Production Feasibility: {feasibility_avg:.1f}/10")
        print()
        
        # Detailed rankings
        print("🎭 DETAILED PRODUCTION RANKINGS:")
        for result in results:
            scores = result['production_scores']
            chars = result['production_characteristics']
            print(f"{result['rank']}. {result['musical_name']}")
            print(f"   Overall: {scores['overall_production_score']}/10 | Genre: {result['genre']}")
            print(f"   Tech:{scores['technical_demands_score']:.1f} Stage:{scores['staging_complexity_score']:.1f} Resource:{scores['resource_requirements_score']:.1f} Feasible:{scores['production_feasibility_score']:.1f}")
            print(f"   Complexity: {chars['technical_complexity']} | Difficulty: {chars['staging_difficulty']} | Budget: {chars['budget_category']} | Scale: {chars['production_scale']}")
            
            if result['production_details']['technical_elements']:
                print(f"   Technical: {result['production_details']['technical_elements'][0]}")
            print()
        
        # Production pattern analysis
        print("🎭 PRODUCTION COMPLEXITY PATTERNS:")
        
        # Technical complexity
        tech_counts = {}
        for result in results:
            tech = result['production_characteristics']['technical_complexity']
            tech_counts[tech] = tech_counts.get(tech, 0) + 1
        
        print("   Technical Complexity:")
        for tech, count in tech_counts.items():
            print(f"     {tech}: {count} musicals")
        
        # Budget categories
        budget_counts = {}
        for result in results:
            budget = result['production_characteristics']['budget_category']
            budget_counts[budget] = budget_counts.get(budget, 0) + 1
        
        print("   Budget Categories:")
        for budget, count in budget_counts.items():
            print(f"     {budget}: {count} musicals")
        
        # Production scales
        scale_counts = {}
        for result in results:
            scale = result['production_characteristics']['production_scale']
            scale_counts[scale] = scale_counts.get(scale, 0) + 1
        
        print("   Production Scales:")
        for scale, count in scale_counts.items():
            print(f"     {scale}: {count} musicals")
        
        # Save results
        output_data = {
            "analysis_metadata": {
                "analysis_type": "Production Complexity & Staging Requirements",
                "analysis_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_musicals": len(results),
                "collection_average": round(collection_average, 2),
                "score_range": round(score_range, 2),
                "analysis_time_seconds": round(total_time, 1),
                "component_averages": {
                    "technical_demands": round(technical_avg, 2),
                    "staging_complexity": round(staging_avg, 2),
                    "resource_requirements": round(resource_avg, 2),
                    "production_feasibility": round(feasibility_avg, 2)
                }
            },
            "production_rankings": results,
            "production_patterns": {
                "technical_complexity": tech_counts,
                "budget_categories": budget_counts,
                "production_scales": scale_counts
            }
        }
        
        with open("PRODUCTION_complexity_analysis.json", 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Production analysis saved to: PRODUCTION_complexity_analysis.json")
        print("🎭⚡ Production Complexity & Staging Requirements complete - ENGAGED!")
        
        return results
    
    else:
        print("❌ No analyses completed")
        return []

if __name__ == "__main__":
    print("🚀 Starting Production Complexity & Staging Requirements - ENGAGE!")
    run_production_complexity_analysis()