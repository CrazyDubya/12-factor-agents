"""
Deep Personality System for Eternal Lockdown
Personal goals, motivations, background stories, and character depth
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import random

class PersonalGoal(Enum):
    SURVIVE_SENTENCE = "survive_sentence"
    PROTECT_FAMILY = "protect_family"
    GAIN_RESPECT = "gain_respect"
    FIND_REDEMPTION = "find_redemption"
    MAINTAIN_INNOCENCE = "maintain_innocence"
    BUILD_CONNECTIONS = "build_connections"
    LEARN_SKILLS = "learn_skills"
    PLAN_REVENGE = "plan_revenge"
    STAY_INVISIBLE = "stay_invisible"
    HELP_OTHERS = "help_others"

class PersonalFear(Enum):
    VIOLENCE = "violence"
    ISOLATION = "isolation"
    LOSING_FAMILY = "losing_family"
    BEING_FORGOTTEN = "being_forgotten"
    RETALIATION = "retaliation"
    AUTHORITY = "authority"
    FAILURE = "failure"
    EXPOSURE = "exposure"

class BackgroundType(Enum):
    STREET_SMART = "street_smart"
    EDUCATED = "educated"
    MILITARY = "military"
    FAMILY_MAN = "family_man"
    LONER = "loner"
    GANG_MEMBER = "gang_member"
    FIRST_TIMER = "first_timer"
    REPEAT_OFFENDER = "repeat_offender"

@dataclass
class PersonalHistory:
    """Detailed background affecting decisions"""
    background_type: BackgroundType
    family_situation: str
    education_level: str
    work_history: str
    criminal_history: str
    defining_moment: str
    
    # Personal relationships outside prison
    has_children: bool = False
    children_ages: List[int] = field(default_factory=list)
    relationship_status: str = "single"
    family_support: float = 0.5  # 0.0-1.0
    
    # Skills and knowledge
    street_knowledge: float = 0.5
    book_knowledge: float = 0.5
    social_skills: float = 0.5
    survival_instinct: float = 0.5

@dataclass
class PersonalMotivation:
    """What drives the character's decisions"""
    primary_goal: PersonalGoal
    primary_fear: PersonalFear
    secondary_goals: List[PersonalGoal] = field(default_factory=list)
    secondary_fears: List[PersonalFear] = field(default_factory=list)
    
    # Values and principles (0.0-1.0)
    loyalty_value: float = 0.5
    honor_value: float = 0.5
    family_value: float = 0.5
    survival_value: float = 0.5
    justice_value: float = 0.5
    
    # What they want most
    deepest_desire: str = "to go home"
    greatest_regret: str = "getting caught"
    
    def get_motivation_strength(self, situation_type: str) -> float:
        """Get motivation strength for specific situation"""
        situation_motivations = {
            "family_related": self.family_value,
            "gang_related": self.loyalty_value,
            "authority_conflict": self.honor_value,
            "survival_threat": self.survival_value,
            "moral_choice": self.justice_value
        }
        return situation_motivations.get(situation_type, 0.5)

@dataclass
class DeepPersonality:
    """Complete personality profile with depth"""
    history: PersonalHistory
    motivation: PersonalMotivation
    
    # Internal monologue patterns
    thought_patterns: List[str] = field(default_factory=list)
    common_phrases: List[str] = field(default_factory=list)
    decision_style: str = "calculated"
    
    # Relationship patterns
    trust_easily: bool = False
    holds_grudges: bool = True
    leadership_style: str = "follower"
    conflict_style: str = "avoid"
    
    def get_decision_context(self, situation: str, opponent_name: str) -> str:
        """Get deep personality context for decisions"""
        
        context = f"""
PERSONAL BACKGROUND:
- Background: {self.history.background_type.value}
- Family: {self.history.family_situation}
- Education: {self.history.education_level}
- Criminal History: {self.history.criminal_history}

CORE MOTIVATIONS:
- Primary Goal: {self.motivation.primary_goal.value}
- Primary Fear: {self.motivation.primary_fear.value}
- Deepest Desire: {self.motivation.deepest_desire}
- Greatest Regret: {self.motivation.greatest_regret}

DECISION STYLE:
- You are {self.decision_style} in your choices
- You {'' if self.trust_easily else 'do not '}trust people easily
- You {'hold grudges' if self.holds_grudges else 'forgive easily'}
- In conflict, you tend to {self.conflict_style}

INTERNAL VOICE:
{random.choice(self.thought_patterns) if self.thought_patterns else 'You think carefully about each choice'}
"""
        
        return context.strip()

class PersonalityGenerator:
    """Generate deep personalities for different agent types"""
    
    def __init__(self):
        self.background_templates = {
            BackgroundType.STREET_SMART: {
                "family_situation": "Grew up in tough neighborhood, family struggled",
                "education_level": "High school dropout, street educated",
                "work_history": "Odd jobs, hustling, survival work",
                "criminal_history": "Started young, escalated over time",
                "defining_moment": "First arrest changed everything",
                "street_knowledge": 0.9,
                "book_knowledge": 0.3,
                "survival_instinct": 0.8
            },
            BackgroundType.EDUCATED: {
                "family_situation": "Middle class family, high expectations",
                "education_level": "College degree, professional background",
                "work_history": "White collar career, respected position",
                "criminal_history": "First offense, white collar crime",
                "defining_moment": "Moment of weakness led to crime",
                "street_knowledge": 0.2,
                "book_knowledge": 0.9,
                "survival_instinct": 0.4
            },
            BackgroundType.FAMILY_MAN: {
                "family_situation": "Devoted father/husband, family is everything",
                "education_level": "Working class education",
                "work_history": "Steady job to support family",
                "criminal_history": "Crime to help family financially",
                "defining_moment": "Chose family over law",
                "family_support": 0.9,
                "family_value": 0.9,
                "has_children": True
            },
            BackgroundType.GANG_MEMBER: {
                "family_situation": "Gang became family, blood family distant",
                "education_level": "Street education, some formal schooling",
                "work_history": "Gang activities, illegal income",
                "criminal_history": "Gang-related crimes, loyalty conflicts",
                "defining_moment": "Chose gang over everything else",
                "loyalty_value": 0.9,
                "street_knowledge": 0.8
            }
        }
    
    def generate_personality(self, agent_name: str, crime: str, 
                           background_type: BackgroundType = None) -> DeepPersonality:
        """Generate complete personality profile"""
        
        if not background_type:
            background_type = self._infer_background_from_crime(crime)
        
        # Generate history
        template = self.background_templates.get(background_type, {})
        history = PersonalHistory(
            background_type=background_type,
            family_situation=template.get("family_situation", "Unknown family background"),
            education_level=template.get("education_level", "High school"),
            work_history=template.get("work_history", "Various jobs"),
            criminal_history=template.get("criminal_history", "First offense"),
            defining_moment=template.get("defining_moment", "A moment that changed everything"),
            has_children=template.get("has_children", random.choice([True, False])),
            family_support=template.get("family_support", random.uniform(0.2, 0.8)),
            street_knowledge=template.get("street_knowledge", random.uniform(0.3, 0.7)),
            book_knowledge=template.get("book_knowledge", random.uniform(0.3, 0.7)),
            survival_instinct=template.get("survival_instinct", random.uniform(0.4, 0.8))
        )
        
        if history.has_children:
            history.children_ages = [random.randint(5, 18) for _ in range(random.randint(1, 3))]
        
        # Generate motivation
        motivation = self._generate_motivation(background_type, history)
        
        # Generate thought patterns
        thought_patterns = self._generate_thought_patterns(background_type, agent_name)
        
        return DeepPersonality(
            history=history,
            motivation=motivation,
            thought_patterns=thought_patterns,
            decision_style=self._get_decision_style(background_type),
            trust_easily=background_type in [BackgroundType.FIRST_TIMER, BackgroundType.FAMILY_MAN],
            holds_grudges=background_type in [BackgroundType.GANG_MEMBER, BackgroundType.STREET_SMART],
            leadership_style=self._get_leadership_style(background_type),
            conflict_style=self._get_conflict_style(background_type)
        )
    
    def _infer_background_from_crime(self, crime: str) -> BackgroundType:
        """Infer background type from crime"""
        crime_lower = crime.lower()
        
        if "gang" in crime_lower or "racketeering" in crime_lower:
            return BackgroundType.GANG_MEMBER
        elif "fraud" in crime_lower or "embezzlement" in crime_lower:
            return BackgroundType.EDUCATED
        elif "drug possession" in crime_lower and "intent" not in crime_lower:
            return BackgroundType.FIRST_TIMER
        elif "armed" in crime_lower or "robbery" in crime_lower:
            return BackgroundType.STREET_SMART
        else:
            return random.choice(list(BackgroundType))
    
    def _generate_motivation(self, background_type: BackgroundType, history: PersonalHistory) -> PersonalMotivation:
        """Generate motivation based on background"""
        
        motivation_map = {
            BackgroundType.FAMILY_MAN: {
                "primary_goal": PersonalGoal.PROTECT_FAMILY,
                "primary_fear": PersonalFear.LOSING_FAMILY,
                "deepest_desire": "to see my children again",
                "family_value": 0.9
            },
            BackgroundType.GANG_MEMBER: {
                "primary_goal": PersonalGoal.GAIN_RESPECT,
                "primary_fear": PersonalFear.RETALIATION,
                "deepest_desire": "to maintain my reputation",
                "loyalty_value": 0.9
            },
            BackgroundType.EDUCATED: {
                "primary_goal": PersonalGoal.FIND_REDEMPTION,
                "primary_fear": PersonalFear.BEING_FORGOTTEN,
                "deepest_desire": "to rebuild my reputation",
                "justice_value": 0.7
            },
            BackgroundType.FIRST_TIMER: {
                "primary_goal": PersonalGoal.SURVIVE_SENTENCE,
                "primary_fear": PersonalFear.VIOLENCE,
                "deepest_desire": "to get through this safely",
                "survival_value": 0.8
            }
        }
        
        template = motivation_map.get(background_type, {})
        
        return PersonalMotivation(
            primary_goal=template.get("primary_goal", PersonalGoal.SURVIVE_SENTENCE),
            primary_fear=template.get("primary_fear", PersonalFear.ISOLATION),
            deepest_desire=template.get("deepest_desire", "to go home"),
            greatest_regret="the choices that brought me here",
            loyalty_value=template.get("loyalty_value", 0.5),
            family_value=template.get("family_value", 0.5),
            survival_value=template.get("survival_value", 0.5),
            honor_value=random.uniform(0.3, 0.8),
            justice_value=template.get("justice_value", random.uniform(0.3, 0.7))
        )
    
    def _generate_thought_patterns(self, background_type: BackgroundType, name: str) -> List[str]:
        """Generate internal thought patterns"""
        
        patterns = {
            BackgroundType.FAMILY_MAN: [
                f"I need to get home to my family",
                f"Every decision affects my children",
                f"I can't let my family down again"
            ],
            BackgroundType.GANG_MEMBER: [
                f"Respect is everything in here",
                f"I can't show weakness",
                f"My reputation depends on this choice"
            ],
            BackgroundType.EDUCATED: [
                f"I need to think this through logically",
                f"There has to be a rational solution",
                f"I can't let emotions cloud my judgment"
            ],
            BackgroundType.STREET_SMART: [
                f"Trust no one completely",
                f"Always watch your back",
                f"Survival comes first"
            ]
        }
        
        return patterns.get(background_type, [f"I need to be careful about my choices"])
    
    def _get_decision_style(self, background_type: BackgroundType) -> str:
        styles = {
            BackgroundType.EDUCATED: "analytical",
            BackgroundType.STREET_SMART: "instinctive", 
            BackgroundType.GANG_MEMBER: "loyalty-based",
            BackgroundType.FAMILY_MAN: "family-focused"
        }
        return styles.get(background_type, "cautious")
    
    def _get_leadership_style(self, background_type: BackgroundType) -> str:
        styles = {
            BackgroundType.GANG_MEMBER: "leader",
            BackgroundType.EDUCATED: "advisor",
            BackgroundType.STREET_SMART: "independent"
        }
        return styles.get(background_type, "follower")
    
    def _get_conflict_style(self, background_type: BackgroundType) -> str:
        styles = {
            BackgroundType.GANG_MEMBER: "confront",
            BackgroundType.EDUCATED: "negotiate",
            BackgroundType.FAMILY_MAN: "avoid"
        }
        return styles.get(background_type, "adapt")

def test_personality_system():
    """Test the personality generation system"""
    generator = PersonalityGenerator()
    
    print("🧠 Testing Deep Personality System")
    print("=" * 50)
    
    test_cases = [
        ("Carlos Mendez", "racketeering"),
        ("David Chen", "fraud"),
        ("Marcus Johnson", "drug possession"),
        ("Tommy Rodriguez", "armed robbery")
    ]
    
    for name, crime in test_cases:
        personality = generator.generate_personality(name, crime)
        print(f"\n👤 {name} ({crime}):")
        print(f"   Background: {personality.history.background_type.value}")
        print(f"   Goal: {personality.motivation.primary_goal.value}")
        print(f"   Fear: {personality.motivation.primary_fear.value}")
        print(f"   Desire: {personality.motivation.deepest_desire}")
        print(f"   Style: {personality.decision_style}")
        if personality.thought_patterns:
            print(f"   Thinks: '{personality.thought_patterns[0]}'")

if __name__ == "__main__":
    test_personality_system()