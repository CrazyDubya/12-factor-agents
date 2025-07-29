"""
Expanded Game Theory Beyond Prisoner's Dilemma
Multiple game types, conversational interactions, and complex scenarios
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Any
import random
import numpy as np

class GameType(Enum):
    PRISONERS_DILEMMA = "prisoners_dilemma"
    COORDINATION_GAME = "coordination_game"
    CHICKEN_GAME = "chicken_game"
    TRUST_GAME = "trust_game"
    RESOURCE_SHARING = "resource_sharing"
    INFORMATION_EXCHANGE = "information_exchange"
    ALLIANCE_FORMATION = "alliance_formation"
    TERRITORY_DISPUTE = "territory_dispute"
    FAVOR_EXCHANGE = "favor_exchange"
    REPUTATION_GAME = "reputation_game"

class InteractionType(Enum):
    INMATE_INMATE = "inmate_inmate"
    INMATE_GUARD = "inmate_guard"
    GUARD_GUARD = "guard_guard"
    GROUP_DISCUSSION = "group_discussion"
    WORK_COLLABORATION = "work_collaboration"
    LEISURE_INTERACTION = "leisure_interaction"

@dataclass
class GameScenario:
    """Defines a specific game scenario with payoffs and context"""
    game_type: GameType
    interaction_type: InteractionType
    context: str
    choices: List[str]
    payoff_matrix: Dict[Tuple[str, str], Tuple[float, float]]
    description: str
    conversation_starters: List[str]

class ExpandedGameEngine:
    """Enhanced game engine with multiple game types and conversational elements"""
    
    def __init__(self):
        self.game_scenarios = self._initialize_game_scenarios()
        self.conversation_templates = self._initialize_conversation_templates()
    
    def _initialize_game_scenarios(self) -> Dict[str, GameScenario]:
        """Initialize all game scenarios"""
        scenarios = {}
        
        # Classic Prisoner's Dilemma
        scenarios["pd_basic"] = GameScenario(
            game_type=GameType.PRISONERS_DILEMMA,
            interaction_type=InteractionType.INMATE_INMATE,
            context="resource_sharing",
            choices=["cooperate", "defect"],
            payoff_matrix={
                ("cooperate", "cooperate"): (3.0, 3.0),
                ("cooperate", "defect"): (0.0, 5.0),
                ("defect", "cooperate"): (5.0, 0.0),
                ("defect", "defect"): (1.0, 1.0)
            },
            description="Classic cooperation vs self-interest dilemma",
            conversation_starters=[
                "We need to figure out how to handle this situation...",
                "I'm thinking we should work together on this...",
                "Look, I don't know you well, but...",
                "This could go either way for both of us..."
            ]
        )
        
        # Coordination Game (both benefit from same choice)
        scenarios["coordination_work"] = GameScenario(
            game_type=GameType.COORDINATION_GAME,
            interaction_type=InteractionType.WORK_COLLABORATION,
            context="work_coordination",
            choices=["method_a", "method_b"],
            payoff_matrix={
                ("method_a", "method_a"): (4.0, 4.0),
                ("method_a", "method_b"): (0.0, 0.0),
                ("method_b", "method_a"): (0.0, 0.0),
                ("method_b", "method_b"): (3.0, 3.0)
            },
            description="Coordinating work methods for efficiency",
            conversation_starters=[
                "How do you usually handle this kind of work?",
                "We should probably do this the same way...",
                "I've seen this done a couple different ways...",
                "What works best for you?"
            ]
        )
        
        # Trust Game (one person trusts, other decides to honor or exploit)
        scenarios["trust_favor"] = GameScenario(
            game_type=GameType.TRUST_GAME,
            interaction_type=InteractionType.INMATE_INMATE,
            context="favor_request",
            choices=["trust", "distrust"],
            payoff_matrix={
                ("trust", "honor"): (3.0, 4.0),
                ("trust", "exploit"): (-1.0, 5.0),
                ("distrust", "honor"): (1.0, 1.0),
                ("distrust", "exploit"): (1.0, 1.0)
            },
            description="One person asks for a favor, other decides whether to help",
            conversation_starters=[
                "I need to ask you for something...",
                "Can I trust you with this?",
                "I'm in a bit of a situation...",
                "Would you be willing to help me out?"
            ]
        )
        
        # Information Exchange
        scenarios["info_exchange"] = GameScenario(
            game_type=GameType.INFORMATION_EXCHANGE,
            interaction_type=InteractionType.INMATE_INMATE,
            context="information_sharing",
            choices=["share_info", "withhold_info"],
            payoff_matrix={
                ("share_info", "share_info"): (3.0, 3.0),
                ("share_info", "withhold_info"): (-1.0, 4.0),
                ("withhold_info", "share_info"): (4.0, -1.0),
                ("withhold_info", "withhold_info"): (0.0, 0.0)
            },
            description="Sharing valuable information about prison life",
            conversation_starters=[
                "I heard something you might want to know...",
                "There's word going around about...",
                "I might have some information that could help you...",
                "You seem like someone I can talk to..."
            ]
        )
        
        # Inmate-Guard Interactions (different dynamics)
        scenarios["guard_compliance"] = GameScenario(
            game_type=GameType.PRISONERS_DILEMMA,
            interaction_type=InteractionType.INMATE_GUARD,
            context="rule_compliance",
            choices=["comply", "resist"],
            payoff_matrix={
                ("comply", "lenient"): (2.0, 3.0),
                ("comply", "strict"): (1.0, 4.0),
                ("resist", "lenient"): (3.0, 1.0),
                ("resist", "strict"): (-2.0, 2.0)
            },
            description="Inmate compliance with guard instructions",
            conversation_starters=[
                "I need you to follow the rules here...",
                "You know how this works...",
                "Let's keep this simple...",
                "I'm just doing my job..."
            ]
        )
        
        # Resource Sharing (multiple people, limited resources)
        scenarios["resource_sharing"] = GameScenario(
            game_type=GameType.RESOURCE_SHARING,
            interaction_type=InteractionType.GROUP_DISCUSSION,
            context="limited_resources",
            choices=["share_fairly", "take_more", "give_up_share"],
            payoff_matrix={
                ("share_fairly", "share_fairly"): (3.0, 3.0),
                ("share_fairly", "take_more"): (1.0, 4.0),
                ("take_more", "share_fairly"): (4.0, 1.0),
                ("take_more", "take_more"): (0.0, 0.0),
                ("give_up_share", "share_fairly"): (1.0, 4.0),
                ("give_up_share", "take_more"): (-1.0, 5.0)
            },
            description="Dividing limited resources among group members",
            conversation_starters=[
                "We need to figure out how to split this...",
                "There's not enough for everyone to get what they want...",
                "How should we handle this fairly?",
                "I think we can work something out..."
            ]
        )
        
        return scenarios
    
    def _initialize_conversation_templates(self) -> Dict[str, Dict]:
        """Initialize conversation templates for different scenarios"""
        return {
            "opening": {
                "friendly": [
                    "Hey, {name}, got a minute?",
                    "{name}, I wanted to talk to you about something...",
                    "What's up, {name}? How you holding up?",
                    "{name}, you seem like someone I can reason with..."
                ],
                "cautious": [
                    "{name}, we need to discuss this situation...",
                    "Listen, {name}, I don't know you well, but...",
                    "{name}, I'm not sure how to approach this...",
                    "We have a situation here, {name}..."
                ],
                "aggressive": [
                    "{name}, here's how this is going to work...",
                    "Listen up, {name}, I'm only saying this once...",
                    "{name}, you better understand something...",
                    "I don't have time for games, {name}..."
                ],
                "authority": [
                    "{name}, I need your cooperation here...",
                    "Let's keep this professional, {name}...",
                    "{name}, you know the rules...",
                    "I'm going to need you to comply, {name}..."
                ]
            },
            "decision_explanation": {
                "cooperative": [
                    "I think we can both benefit if we work together on this.",
                    "The way I see it, we're better off helping each other.",
                    "I'm willing to do my part if you do yours.",
                    "Let's be smart about this and cooperate."
                ],
                "defective": [
                    "I've got to look out for myself first.",
                    "Sorry, but I can't take that risk.",
                    "I don't know you well enough to trust you.",
                    "I'm going to have to protect my own interests."
                ],
                "strategic": [
                    "I've been thinking about this carefully...",
                    "Based on what I know about this place...",
                    "I've seen how these things usually go...",
                    "Let me be strategic about this..."
                ]
            },
            "response": {
                "positive": [
                    "I appreciate you being straight with me.",
                    "That sounds reasonable to me.",
                    "I think we can make this work.",
                    "I respect that approach."
                ],
                "negative": [
                    "I can't say I'm surprised by that choice.",
                    "That's disappointing, but I understand.",
                    "I guess that's how it's going to be.",
                    "I should have seen that coming."
                ],
                "neutral": [
                    "Fair enough.",
                    "I can live with that.",
                    "That's your choice to make.",
                    "We'll see how this plays out."
                ]
            }
        }
    
    def select_game_scenario(self, interaction_type: InteractionType, 
                           activity_context: str, participants: List[Any]) -> GameScenario:
        """Select appropriate game scenario based on context"""
        
        # Filter scenarios by interaction type
        suitable_scenarios = [
            scenario for scenario in self.game_scenarios.values()
            if scenario.interaction_type == interaction_type
        ]
        
        if not suitable_scenarios:
            # Default to basic PD
            return self.game_scenarios["pd_basic"]
        
        # Context-based selection
        if "work" in activity_context.lower():
            work_scenarios = [s for s in suitable_scenarios if "work" in s.context or "coordination" in s.context]
            if work_scenarios:
                return random.choice(work_scenarios)
        
        elif "guard" in activity_context.lower() or interaction_type == InteractionType.INMATE_GUARD:
            guard_scenarios = [s for s in suitable_scenarios if s.interaction_type == InteractionType.INMATE_GUARD]
            if guard_scenarios:
                return random.choice(guard_scenarios)
        
        elif len(participants) > 2:
            group_scenarios = [s for s in suitable_scenarios if "group" in s.context or "resource" in s.context]
            if group_scenarios:
                return random.choice(group_scenarios)
        
        # Default selection
        return random.choice(suitable_scenarios)
    
    def generate_conversation(self, scenario: GameScenario, agent1_name: str, agent2_name: str,
                            agent1_personality: str, agent2_personality: str,
                            agent1_choice: str, agent2_choice: str) -> Dict[str, str]:
        """Generate conversational prose for the interaction"""
        
        # Select conversation style based on personalities
        style_map = {
            "cooperative": "friendly",
            "strategic": "cautious", 
            "aggressive": "aggressive",
            "withdrawn": "cautious",
            "impulsive": "aggressive"
        }
        
        agent1_style = style_map.get(agent1_personality, "cautious")
        agent2_style = style_map.get(agent2_personality, "cautious")
        
        # Generate opening
        opening_templates = self.conversation_templates["opening"][agent1_style]
        opening = random.choice(opening_templates).format(name=agent2_name)
        
        # Generate scenario introduction
        scenario_intro = random.choice(scenario.conversation_starters)
        
        # Generate decision explanations
        decision_templates = self.conversation_templates["decision_explanation"]
        
        if agent1_choice in ["cooperate", "share_info", "trust", "share_fairly"]:
            agent1_explanation = random.choice(decision_templates["cooperative"])
        elif agent1_choice in ["defect", "withhold_info", "distrust", "take_more"]:
            agent1_explanation = random.choice(decision_templates["defective"])
        else:
            agent1_explanation = random.choice(decision_templates["strategic"])
        
        # Generate response based on choices
        response_templates = self.conversation_templates["response"]
        
        # Determine if choices align
        if (agent1_choice in ["cooperate", "trust", "share_info"] and 
            agent2_choice in ["cooperate", "honor", "share_info"]):
            agent2_response = random.choice(response_templates["positive"])
        elif (agent1_choice in ["defect", "exploit", "withhold_info"] or 
              agent2_choice in ["defect", "exploit", "withhold_info"]):
            agent2_response = random.choice(response_templates["negative"])
        else:
            agent2_response = random.choice(response_templates["neutral"])
        
        return {
            "opening": f"{agent1_name}: \"{opening}\"",
            "scenario_setup": f"{agent1_name}: \"{scenario_intro}\"",
            "agent1_decision": f"{agent1_name}: \"{agent1_explanation}\"",
            "agent2_response": f"{agent2_name}: \"{agent2_response}\"",
            "context": scenario.description
        }
    
    def calculate_payoffs(self, scenario: GameScenario, choice1: str, choice2: str) -> Tuple[float, float]:
        """Calculate payoffs for the given choices"""
        
        # Handle special cases for asymmetric games
        if scenario.game_type == GameType.TRUST_GAME:
            if choice1 == "trust":
                # Second player chooses to honor or exploit
                if choice2 in ["cooperate", "honor", "share_fairly"]:
                    return scenario.payoff_matrix[("trust", "honor")]
                else:
                    return scenario.payoff_matrix[("trust", "exploit")]
            else:
                return scenario.payoff_matrix[("distrust", "honor")]
        
        # Standard symmetric games
        choice_key = (choice1, choice2)
        if choice_key in scenario.payoff_matrix:
            return scenario.payoff_matrix[choice_key]
        
        # Fallback to default PD payoffs
        pd_mapping = {
            ("cooperate", "cooperate"): (3.0, 3.0),
            ("cooperate", "defect"): (0.0, 5.0),
            ("defect", "cooperate"): (5.0, 0.0),
            ("defect", "defect"): (1.0, 1.0)
        }
        
        # Map choices to cooperate/defect
        cooperative_choices = ["cooperate", "trust", "share_info", "share_fairly", "method_a", "comply"]
        
        mapped_choice1 = "cooperate" if choice1 in cooperative_choices else "defect"
        mapped_choice2 = "cooperate" if choice2 in cooperative_choices else "defect"
        
        return pd_mapping[(mapped_choice1, mapped_choice2)]

def test_expanded_game_theory():
    """Test the expanded game theory system"""
    print("🎮 Testing Expanded Game Theory System")
    print("=" * 50)
    
    engine = ExpandedGameEngine()
    
    # Test different interaction types
    test_cases = [
        (InteractionType.INMATE_INMATE, "yard_time", ["Agent1", "Agent2"]),
        (InteractionType.INMATE_GUARD, "rule_compliance", ["Prisoner", "Guard"]),
        (InteractionType.WORK_COLLABORATION, "kitchen_duty", ["Worker1", "Worker2"]),
        (InteractionType.GROUP_DISCUSSION, "resource_sharing", ["A", "B", "C"])
    ]
    
    for interaction_type, context, participants in test_cases:
        print(f"\n🎭 {interaction_type.value} - {context}")
        
        scenario = engine.select_game_scenario(interaction_type, context, participants)
        print(f"   Game: {scenario.game_type.value}")
        print(f"   Choices: {scenario.choices}")
        
        # Test conversation generation
        if len(participants) >= 2:
            choice1 = random.choice(scenario.choices)
            choice2 = random.choice(scenario.choices)
            
            conversation = engine.generate_conversation(
                scenario, participants[0], participants[1],
                "strategic", "cooperative", choice1, choice2
            )
            
            print(f"   Conversation:")
            print(f"     {conversation['opening']}")
            print(f"     {conversation['agent1_decision']}")
            print(f"     {conversation['agent2_response']}")
            
            payoffs = engine.calculate_payoffs(scenario, choice1, choice2)
            print(f"   Payoffs: {payoffs}")

if __name__ == "__main__":
    test_expanded_game_theory()