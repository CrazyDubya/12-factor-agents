"""
Room-Based Interaction System for Eternal Lockdown
Multiple interaction opportunities per room with varied game types
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Set, Optional, Any
import random
import itertools

from expanded_game_theory import ExpandedGameEngine, InteractionType, GameType
from temporal_system import Location, ActivityType

class InteractionOpportunity(Enum):
    # Work-based interactions
    TASK_COORDINATION = "task_coordination"
    RESOURCE_ALLOCATION = "resource_allocation"
    WORK_DISPUTE = "work_dispute"
    HELP_REQUEST = "help_request"
    
    # Social interactions
    CASUAL_CONVERSATION = "casual_conversation"
    INFORMATION_SHARING = "information_sharing"
    ALLIANCE_BUILDING = "alliance_building"
    TERRITORY_NEGOTIATION = "territory_negotiation"
    
    # Conflict interactions
    PERSONAL_CONFLICT = "personal_conflict"
    GANG_BUSINESS = "gang_business"
    REPUTATION_CHALLENGE = "reputation_challenge"
    
    # Authority interactions (inmate-guard only)
    RULE_ENFORCEMENT = "rule_enforcement"
    PRIVILEGE_REQUEST = "privilege_request"
    COMPLAINT_FILING = "complaint_filing"
    ROUTINE_CHECK = "routine_check"

@dataclass
class RoomInteractionProfile:
    """Defines interaction opportunities available in each room"""
    location: Location
    max_simultaneous_interactions: int
    interaction_frequency: float  # 0.0-1.0, how often interactions occur
    available_opportunities: List[InteractionOpportunity]
    privacy_level: float  # 0.0-1.0, affects conversation content
    guard_presence_probability: float  # 0.0-1.0, chance guard is present
    
    # Interaction type weights
    inmate_inmate_weight: float = 0.7
    inmate_guard_weight: float = 0.2
    group_interaction_weight: float = 0.1

class RoomInteractionManager:
    """Manages all interactions within prison rooms"""
    
    def __init__(self):
        self.game_engine = ExpandedGameEngine()
        self.room_profiles = self._initialize_room_profiles()
        self.interaction_history = []
        
    def _initialize_room_profiles(self) -> Dict[Location, RoomInteractionProfile]:
        """Initialize interaction profiles for each room"""
        profiles = {}
        
        # Cells - High privacy, limited interactions
        for cell in [Location.CELL_A, Location.CELL_B, Location.CELL_C, Location.CELL_D]:
            profiles[cell] = RoomInteractionProfile(
                location=cell,
                max_simultaneous_interactions=1,  # Only 2 people per cell
                interaction_frequency=0.8,
                available_opportunities=[
                    InteractionOpportunity.CASUAL_CONVERSATION,
                    InteractionOpportunity.INFORMATION_SHARING,
                    InteractionOpportunity.ALLIANCE_BUILDING,
                    InteractionOpportunity.PERSONAL_CONFLICT,
                    InteractionOpportunity.GANG_BUSINESS
                ],
                privacy_level=0.9,  # Very private
                guard_presence_probability=0.1,  # Guards rarely in cells
                inmate_inmate_weight=0.9,
                inmate_guard_weight=0.1,
                group_interaction_weight=0.0
            )
        
        # Kitchen - Work coordination, resource disputes
        profiles[Location.POD_KITCHEN] = RoomInteractionProfile(
            location=Location.POD_KITCHEN,
            max_simultaneous_interactions=3,  # Up to 3 workers
            interaction_frequency=0.9,
            available_opportunities=[
                InteractionOpportunity.TASK_COORDINATION,
                InteractionOpportunity.RESOURCE_ALLOCATION,
                InteractionOpportunity.WORK_DISPUTE,
                InteractionOpportunity.HELP_REQUEST,
                InteractionOpportunity.CASUAL_CONVERSATION,
                InteractionOpportunity.RULE_ENFORCEMENT
            ],
            privacy_level=0.4,  # Moderate privacy
            guard_presence_probability=0.3,
            inmate_inmate_weight=0.6,
            inmate_guard_weight=0.3,
            group_interaction_weight=0.1
        )
        
        # Common Area - High interaction, mixed types
        profiles[Location.POD_COMMON_AREA] = RoomInteractionProfile(
            location=Location.POD_COMMON_AREA,
            max_simultaneous_interactions=4,
            interaction_frequency=0.7,
            available_opportunities=[
                InteractionOpportunity.CASUAL_CONVERSATION,
                InteractionOpportunity.INFORMATION_SHARING,
                InteractionOpportunity.ALLIANCE_BUILDING,
                InteractionOpportunity.TERRITORY_NEGOTIATION,
                InteractionOpportunity.PERSONAL_CONFLICT,
                InteractionOpportunity.REPUTATION_CHALLENGE,
                InteractionOpportunity.GANG_BUSINESS,
                InteractionOpportunity.RULE_ENFORCEMENT,
                InteractionOpportunity.PRIVILEGE_REQUEST
            ],
            privacy_level=0.2,  # Low privacy, everyone can see
            guard_presence_probability=0.5,
            inmate_inmate_weight=0.5,
            inmate_guard_weight=0.3,
            group_interaction_weight=0.2
        )
        
        # Yard - Territory disputes, alliances, conflicts
        profiles[Location.POD_YARD] = RoomInteractionProfile(
            location=Location.POD_YARD,
            max_simultaneous_interactions=5,
            interaction_frequency=0.8,
            available_opportunities=[
                InteractionOpportunity.TERRITORY_NEGOTIATION,
                InteractionOpportunity.ALLIANCE_BUILDING,
                InteractionOpportunity.PERSONAL_CONFLICT,
                InteractionOpportunity.REPUTATION_CHALLENGE,
                InteractionOpportunity.GANG_BUSINESS,
                InteractionOpportunity.CASUAL_CONVERSATION,
                InteractionOpportunity.INFORMATION_SHARING,
                InteractionOpportunity.RULE_ENFORCEMENT
            ],
            privacy_level=0.3,
            guard_presence_probability=0.6,  # Higher guard presence
            inmate_inmate_weight=0.6,
            inmate_guard_weight=0.2,
            group_interaction_weight=0.2
        )
        
        # Shower - Private but tense
        profiles[Location.POD_SHOWER] = RoomInteractionProfile(
            location=Location.POD_SHOWER,
            max_simultaneous_interactions=1,  # Only 2 people max
            interaction_frequency=0.6,
            available_opportunities=[
                InteractionOpportunity.PERSONAL_CONFLICT,
                InteractionOpportunity.TERRITORY_NEGOTIATION,
                InteractionOpportunity.INFORMATION_SHARING,
                InteractionOpportunity.GANG_BUSINESS,
                InteractionOpportunity.ROUTINE_CHECK
            ],
            privacy_level=0.7,  # Private but vulnerable
            guard_presence_probability=0.2,
            inmate_inmate_weight=0.8,
            inmate_guard_weight=0.2,
            group_interaction_weight=0.0
        )
        
        # Library - Quiet conversations, information exchange
        profiles[Location.POD_LIBRARY] = RoomInteractionProfile(
            location=Location.POD_LIBRARY,
            max_simultaneous_interactions=2,
            interaction_frequency=0.5,
            available_opportunities=[
                InteractionOpportunity.INFORMATION_SHARING,
                InteractionOpportunity.CASUAL_CONVERSATION,
                InteractionOpportunity.ALLIANCE_BUILDING,
                InteractionOpportunity.HELP_REQUEST,
                InteractionOpportunity.PRIVILEGE_REQUEST
            ],
            privacy_level=0.6,
            guard_presence_probability=0.2,
            inmate_inmate_weight=0.7,
            inmate_guard_weight=0.2,
            group_interaction_weight=0.1
        )
        
        # Laundry - Work-focused, some privacy
        profiles[Location.POD_LAUNDRY] = RoomInteractionProfile(
            location=Location.POD_LAUNDRY,
            max_simultaneous_interactions=1,  # 2 workers max
            interaction_frequency=0.7,
            available_opportunities=[
                InteractionOpportunity.TASK_COORDINATION,
                InteractionOpportunity.WORK_DISPUTE,
                InteractionOpportunity.CASUAL_CONVERSATION,
                InteractionOpportunity.INFORMATION_SHARING,
                InteractionOpportunity.HELP_REQUEST
            ],
            privacy_level=0.5,
            guard_presence_probability=0.2,
            inmate_inmate_weight=0.8,
            inmate_guard_weight=0.2,
            group_interaction_weight=0.0
        )
        
        return profiles
    
    def generate_room_interactions(self, location: Location, participants: List[Dict],
                                 current_activity: ActivityType, time_segment: str) -> List[Dict]:
        """Generate multiple interaction opportunities for a room"""
        
        if location not in self.room_profiles:
            return []
        
        profile = self.room_profiles[location]
        interactions = []
        
        # Determine if interactions occur
        if random.random() > profile.interaction_frequency:
            return []
        
        # Separate inmates and guards
        inmates = [p for p in participants if p.get('agent_type') != 'guard']
        guards = [p for p in participants if p.get('agent_type') == 'guard']
        
        # Add guard presence based on probability
        if not guards and random.random() < profile.guard_presence_probability:
            # Simulate guard presence
            guards = [{'id': 999, 'name': 'Officer on Duty', 'agent_type': 'guard'}]
        
        # Generate different types of interactions
        interaction_count = 0
        max_interactions = min(profile.max_simultaneous_interactions, len(participants) // 2)
        
        # 1. Inmate-Inmate interactions
        if len(inmates) >= 2 and random.random() < profile.inmate_inmate_weight:
            inmate_pairs = list(itertools.combinations(inmates, 2))
            selected_pairs = random.sample(inmate_pairs, min(max_interactions, len(inmate_pairs)))
            
            for inmate1, inmate2 in selected_pairs:
                if interaction_count >= max_interactions:
                    break
                
                opportunity = self._select_interaction_opportunity(profile, InteractionType.INMATE_INMATE)
                interaction = self._create_interaction(
                    inmate1, inmate2, opportunity, location, current_activity, time_segment, profile
                )
                interactions.append(interaction)
                interaction_count += 1
        
        # 2. Inmate-Guard interactions (only one per room)
        if (guards and inmates and interaction_count < max_interactions and 
            random.random() < profile.inmate_guard_weight):
            
            guard = random.choice(guards)
            inmate = random.choice(inmates)
            
            opportunity = self._select_interaction_opportunity(profile, InteractionType.INMATE_GUARD)
            interaction = self._create_interaction(
                inmate, guard, opportunity, location, current_activity, time_segment, profile
            )
            interactions.append(interaction)
            interaction_count += 1
        
        # 3. Group interactions (if 3+ people and space allows)
        if (len(participants) >= 3 and interaction_count < max_interactions and
            random.random() < profile.group_interaction_weight):
            
            group = random.sample(participants, min(4, len(participants)))
            opportunity = self._select_interaction_opportunity(profile, InteractionType.GROUP_DISCUSSION)
            
            # For group interactions, create multiple pairwise interactions
            group_pairs = list(itertools.combinations(group, 2))
            selected_pair = random.choice(group_pairs)
            
            interaction = self._create_interaction(
                selected_pair[0], selected_pair[1], opportunity, location, 
                current_activity, time_segment, profile, is_group=True
            )
            interactions.append(interaction)
        
        return interactions
    
    def _select_interaction_opportunity(self, profile: RoomInteractionProfile, 
                                     interaction_type: InteractionType) -> InteractionOpportunity:
        """Select appropriate interaction opportunity for the context"""
        
        # Filter opportunities by interaction type
        if interaction_type == InteractionType.INMATE_GUARD:
            authority_opportunities = [
                InteractionOpportunity.RULE_ENFORCEMENT,
                InteractionOpportunity.PRIVILEGE_REQUEST,
                InteractionOpportunity.COMPLAINT_FILING,
                InteractionOpportunity.ROUTINE_CHECK
            ]
            available = [op for op in profile.available_opportunities if op in authority_opportunities]
            if not available:
                available = [InteractionOpportunity.RULE_ENFORCEMENT]  # Default
        else:
            # Inmate-inmate opportunities
            available = [op for op in profile.available_opportunities 
                        if op not in [InteractionOpportunity.RULE_ENFORCEMENT, 
                                     InteractionOpportunity.PRIVILEGE_REQUEST,
                                     InteractionOpportunity.COMPLAINT_FILING,
                                     InteractionOpportunity.ROUTINE_CHECK]]
        
        return random.choice(available) if available else InteractionOpportunity.CASUAL_CONVERSATION
    
    def _create_interaction(self, participant1: Dict, participant2: Dict,
                          opportunity: InteractionOpportunity, location: Location,
                          activity: ActivityType, time_segment: str,
                          profile: RoomInteractionProfile, is_group: bool = False) -> Dict:
        """Create a complete interaction with game theory and conversation"""
        
        # Determine interaction type
        if participant1.get('agent_type') == 'guard' or participant2.get('agent_type') == 'guard':
            interaction_type = InteractionType.INMATE_GUARD
        elif is_group:
            interaction_type = InteractionType.GROUP_DISCUSSION
        elif 'work' in activity.value:
            interaction_type = InteractionType.WORK_COLLABORATION
        else:
            interaction_type = InteractionType.INMATE_INMATE
        
        # Select game scenario
        context = f"{opportunity.value}_in_{location.value}_during_{activity.value}"
        scenario = self.game_engine.select_game_scenario(
            interaction_type, context, [participant1, participant2]
        )
        
        # Generate choices (would be made by agents in actual simulation)
        choice1 = random.choice(scenario.choices)
        choice2 = random.choice(scenario.choices)
        
        # Calculate payoffs
        payoffs = self.game_engine.calculate_payoffs(scenario, choice1, choice2)
        
        # Generate conversation
        conversation = self.game_engine.generate_conversation(
            scenario, 
            participant1.get('name', 'Agent1'),
            participant2.get('name', 'Agent2'),
            participant1.get('personality', 'cooperative'),
            participant2.get('personality', 'cooperative'),
            choice1, choice2
        )
        
        # Create interaction record
        interaction = {
            'participants': [participant1['id'], participant2['id']],
            'participant_names': [participant1['name'], participant2['name']],
            'location': location.value,
            'activity': activity.value,
            'time_segment': time_segment,
            'opportunity': opportunity.value,
            'interaction_type': interaction_type.value,
            'game_type': scenario.game_type.value,
            'choices': [choice1, choice2],
            'payoffs': payoffs,
            'conversation': conversation,
            'privacy_level': profile.privacy_level,
            'is_group': is_group,
            'context': context
        }
        
        return interaction
    
    def get_interaction_summary(self, interactions: List[Dict]) -> str:
        """Generate a summary of all interactions in a room"""
        if not interactions:
            return "No significant interactions occurred."
        
        summary_parts = []
        
        for interaction in interactions:
            names = interaction['participant_names']
            opportunity = interaction['opportunity'].replace('_', ' ').title()
            game_type = interaction['game_type'].replace('_', ' ').title()
            
            summary_parts.append(
                f"{names[0]} and {names[1]} engaged in {opportunity} "
                f"({game_type}) with payoffs {interaction['payoffs']}"
            )
        
        return "; ".join(summary_parts)

def test_room_interaction_system():
    """Test the room interaction system"""
    print("🏠 Testing Room Interaction System")
    print("=" * 50)
    
    manager = RoomInteractionManager()
    
    # Test participants
    participants = [
        {'id': 1, 'name': 'Carlos', 'agent_type': 'prisoner', 'personality': 'strategic'},
        {'id': 2, 'name': 'Marcus', 'agent_type': 'prisoner', 'personality': 'cooperative'},
        {'id': 3, 'name': 'Tommy', 'agent_type': 'prisoner', 'personality': 'aggressive'},
        {'id': 7, 'name': 'Officer Martinez', 'agent_type': 'guard', 'personality': 'strategic'}
    ]
    
    # Test different rooms
    test_rooms = [
        (Location.POD_KITCHEN, ActivityType.KITCHEN_DUTY),
        (Location.POD_YARD, ActivityType.YARD_TIME),
        (Location.CELL_A, ActivityType.CELL_REST),
        (Location.POD_COMMON_AREA, ActivityType.TELEVISION)
    ]
    
    for location, activity in test_rooms:
        print(f"\n🏠 {location.value} - {activity.value}")
        
        # Select participants for this room
        if location in [Location.CELL_A, Location.CELL_B, Location.CELL_C, Location.CELL_D]:
            room_participants = participants[:2]  # Only 2 in cells
        elif location == Location.POD_KITCHEN:
            room_participants = [p for p in participants if p['agent_type'] == 'prisoner'][:3]
        else:
            room_participants = participants
        
        interactions = manager.generate_room_interactions(
            location, room_participants, activity, "morning"
        )
        
        print(f"   Generated {len(interactions)} interactions")
        
        for i, interaction in enumerate(interactions, 1):
            print(f"\n   Interaction {i}:")
            print(f"     Type: {interaction['opportunity']}")
            print(f"     Game: {interaction['game_type']}")
            print(f"     Conversation:")
            conv = interaction['conversation']
            print(f"       {conv['opening']}")
            print(f"       {conv['agent1_decision']}")
            print(f"       {conv['agent2_response']}")
            print(f"     Payoffs: {interaction['payoffs']}")

if __name__ == "__main__":
    test_room_interaction_system()