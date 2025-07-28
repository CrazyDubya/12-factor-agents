"""
Unified Agent System for Eternal Lockdown Prison Simulation
Integrates game theory with Ollama-powered decision making
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import random
import requests
import json
from datetime import datetime

from .game_theory import Strategy, GameTheoryEngine, StrategyLearning

class AgentType(Enum):
    PRISONER = "prisoner"
    GUARD = "guard"
    WARDEN = "warden"

class PersonalityType(Enum):
    IMPULSIVE = "impulsive"
    STRATEGIC = "strategic"
    COOPERATIVE = "cooperative"
    AGGRESSIVE = "aggressive"
    WITHDRAWN = "withdrawn"

class IntelligenceLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

@dataclass
class Agent:
    """Base agent class with game theory integration"""
    id: int
    name: str
    agent_type: AgentType
    personality: PersonalityType
    intelligence: IntelligenceLevel
    
    # Game theory parameters
    cooperation_tendency: float = 0.5
    trust_threshold: float = 0.5
    reputation_score: float = 0.0
    
    # Ollama model assignment
    ollama_model: str = field(init=False)
    
    # Interaction tracking
    interaction_history: List[Dict] = field(default_factory=list)
    relationships: Dict[int, float] = field(default_factory=dict)  # agent_id -> trust_level
    
    def __post_init__(self):
        self._assign_ollama_model()
    
    def _assign_ollama_model(self):
        """Assign Ollama model based on agent type and intelligence"""
        model_map = {
            (AgentType.PRISONER, IntelligenceLevel.LOW): "phi:2b",
            (AgentType.PRISONER, IntelligenceLevel.MEDIUM): "gemma:7b", 
            (AgentType.PRISONER, IntelligenceLevel.HIGH): "llama3:8b",
            (AgentType.GUARD, IntelligenceLevel.LOW): "gemma:7b",
            (AgentType.GUARD, IntelligenceLevel.MEDIUM): "mixtral:8x7b",
            (AgentType.GUARD, IntelligenceLevel.HIGH): "mixtral:8x7b",
            (AgentType.WARDEN, IntelligenceLevel.LOW): "llama3:8b",
            (AgentType.WARDEN, IntelligenceLevel.MEDIUM): "llama3:70b",
            (AgentType.WARDEN, IntelligenceLevel.HIGH): "llama3:70b"
        }
        
        self.ollama_model = model_map.get(
            (self.agent_type, self.intelligence), 
            "phi:2b"  # fallback
        )
    
    def make_decision(self, situation: str, opponent_id: int, game_engine: GameTheoryEngine) -> Strategy:
        """Make PD decision using Ollama + game theory"""
        
        # Get game theory recommendation
        opponent_history = self._get_opponent_history(opponent_id)
        gt_recommendation = game_engine.get_agent_recommendation(self.id, opponent_history)
        
        # Get relationship context
        trust_level = self.relationships.get(opponent_id, 0.0)
        
        # Create Ollama prompt
        prompt = self._create_decision_prompt(situation, opponent_id, gt_recommendation, trust_level)
        
        # Get Ollama decision
        ollama_choice = self._query_ollama(prompt)
        
        # Combine with game theory (weighted decision)
        final_choice = self._combine_decisions(ollama_choice, gt_recommendation)
        
        return final_choice
    
    def _get_opponent_history(self, opponent_id: int) -> List[Strategy]:
        """Get recent interaction history with specific opponent"""
        history = []
        for interaction in self.interaction_history[-10:]:  # Last 10 interactions
            if interaction.get("opponent_id") == opponent_id:
                choice = interaction.get("opponent_choice")
                if choice:
                    history.append(Strategy(choice))
        return history
    
    def _create_decision_prompt(self, situation: str, opponent_id: int, 
                              gt_recommendation: float, trust_level: float) -> str:
        """Create Ollama prompt for decision making"""
        
        opponent_history = self._get_opponent_history(opponent_id)
        recent_cooperations = sum(1 for choice in opponent_history[-3:] if choice == Strategy.COOPERATE)
        recent_total = len(opponent_history[-3:])
        
        prompt = f"""
You are {self.name}, a {self.agent_type.value} with {self.personality.value} personality.

SITUATION: {situation}

OPPONENT INFO:
- Agent ID: {opponent_id}
- Your trust level with them: {trust_level:.2f} (-1.0 to 1.0)
- Their recent cooperations: {recent_cooperations}/{recent_total} in last 3 interactions
- Game theory recommendation: {gt_recommendation:.2f} cooperation probability

PRISONER'S DILEMMA CHOICE:
You must choose COOPERATE or DEFECT.

Payoffs:
- Both cooperate: 3 points each
- You defect, they cooperate: 5 points for you, 0 for them  
- Both defect: 1 point each
- You cooperate, they defect: 0 for you, 5 for them

Consider your personality ({self.personality.value}), the situation, and your relationship.

Respond with ONLY "COOPERATE" or "DEFECT" (one word).
"""
        
        return prompt
    
    def _query_ollama(self, prompt: str) -> Strategy:
        """Query Ollama for decision"""
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.7}
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()["response"].strip().upper()
                if "COOPERATE" in result:
                    return Strategy.COOPERATE
                elif "DEFECT" in result:
                    return Strategy.DEFECT
            
        except Exception as e:
            print(f"Ollama error for {self.name}: {e}")
        
        # Fallback to personality-based decision
        return self._personality_fallback()
    
    def _personality_fallback(self) -> Strategy:
        """Fallback decision based on personality"""
        personality_tendencies = {
            PersonalityType.COOPERATIVE: 0.8,
            PersonalityType.STRATEGIC: 0.6,
            PersonalityType.IMPULSIVE: 0.4,
            PersonalityType.WITHDRAWN: 0.3,
            PersonalityType.AGGRESSIVE: 0.2
        }
        
        coop_prob = personality_tendencies.get(self.personality, 0.5)
        return Strategy.COOPERATE if random.random() < coop_prob else Strategy.DEFECT
    
    def _combine_decisions(self, ollama_choice: Strategy, gt_recommendation: float) -> Strategy:
        """Combine Ollama decision with game theory recommendation"""
        # Weight: 70% Ollama, 30% game theory
        ollama_weight = 0.7
        gt_weight = 0.3
        
        ollama_coop_prob = 1.0 if ollama_choice == Strategy.COOPERATE else 0.0
        combined_prob = ollama_weight * ollama_coop_prob + gt_weight * gt_recommendation
        
        return Strategy.COOPERATE if random.random() < combined_prob else Strategy.DEFECT
    
    def update_from_interaction(self, opponent_id: int, my_choice: Strategy, 
                              opponent_choice: Strategy, my_payoff: float):
        """Update agent state after interaction"""
        
        # Record interaction
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "opponent_id": opponent_id,
            "my_choice": my_choice.value,
            "opponent_choice": opponent_choice.value,
            "my_payoff": my_payoff
        }
        self.interaction_history.append(interaction)
        
        # Update relationship/trust
        self._update_relationship(opponent_id, opponent_choice, my_payoff)
        
        # Update cooperation tendency based on outcome
        self._update_cooperation_tendency(opponent_choice, my_payoff)
    
    def _update_relationship(self, opponent_id: int, opponent_choice: Strategy, my_payoff: float):
        """Update trust/relationship with opponent"""
        current_trust = self.relationships.get(opponent_id, 0.0)
        
        if opponent_choice == Strategy.COOPERATE:
            # Cooperation increases trust
            trust_change = 0.1
        else:
            # Defection decreases trust
            trust_change = -0.2
        
        # Adjust based on payoff outcome
        if my_payoff >= 3:  # Good outcome
            trust_change *= 1.2
        elif my_payoff == 0:  # Exploited
            trust_change *= 1.5
        
        new_trust = max(-1.0, min(1.0, current_trust + trust_change))
        self.relationships[opponent_id] = new_trust
    
    def _update_cooperation_tendency(self, opponent_choice: Strategy, my_payoff: float):
        """Update base cooperation tendency based on outcomes"""
        learning_rate = 0.05
        
        if my_payoff > 2.5:  # Good outcome
            if opponent_choice == Strategy.COOPERATE:
                # Mutual cooperation - reinforce cooperation
                self.cooperation_tendency += learning_rate
        else:  # Poor outcome
            if opponent_choice == Strategy.DEFECT:
                # Exploited - reduce cooperation
                self.cooperation_tendency -= learning_rate * 1.5
        
        # Keep in bounds
        self.cooperation_tendency = max(0.0, min(1.0, self.cooperation_tendency))

@dataclass 
class Prisoner(Agent):
    """Prisoner agent with crime-specific attributes"""
    crime: str = "Unknown"
    sentence_days: int = 365
    time_served: int = 0
    gang_affiliation: Optional[str] = None
    
    def __init__(self, id: int, name: str, personality: PersonalityType, 
                 intelligence: IntelligenceLevel, crime: str = "Unknown", 
                 sentence_days: int = 365, time_served: int = 0, 
                 gang_affiliation: Optional[str] = None, **kwargs):
        super().__init__(id, name, AgentType.PRISONER, personality, intelligence, **kwargs)
        self.crime = crime
        self.sentence_days = sentence_days
        self.time_served = time_served
        self.gang_affiliation = gang_affiliation

@dataclass
class Guard(Agent):
    """Guard agent with authority and role"""
    rank: str = "Officer"
    years_experience: int = 1
    authority_level: int = 1
    shift: str = "day"
    
    def __init__(self, id: int, name: str, personality: PersonalityType,
                 intelligence: IntelligenceLevel, rank: str = "Officer",
                 years_experience: int = 1, authority_level: int = 1,
                 shift: str = "day", **kwargs):
        super().__init__(id, name, AgentType.GUARD, personality, intelligence, **kwargs)
        self.rank = rank
        self.years_experience = years_experience
        self.authority_level = authority_level
        self.shift = shift

@dataclass
class Warden(Agent):
    """Warden agent with administrative oversight"""
    years_experience: int = 10
    management_style: str = "balanced"
    
    def __post_init__(self):
        super().__post_init__()
        self.agent_type = AgentType.WARDEN
        self.authority_level = 4

def create_sample_agents() -> List[Agent]:
    """Create diverse sample agents for testing"""
    agents = [
        Prisoner(
            id=1, name="Marcus Johnson", 
            personality=PersonalityType.COOPERATIVE,
            intelligence=IntelligenceLevel.MEDIUM,
            crime="Drug possession", sentence_days=1825, time_served=730
        ),
        Prisoner(
            id=2, name="Carlos Mendez",
            personality=PersonalityType.STRATEGIC, 
            intelligence=IntelligenceLevel.HIGH,
            crime="Racketeering", sentence_days=2920, time_served=1095,
            gang_affiliation="Los Hermanos"
        ),
        Prisoner(
            id=3, name="Tommy Rodriguez",
            personality=PersonalityType.AGGRESSIVE,
            intelligence=IntelligenceLevel.LOW, 
            crime="Armed robbery", sentence_days=4380, time_served=2920
        ),
        Guard(
            id=4, name="Officer Martinez",
            personality=PersonalityType.STRATEGIC,
            intelligence=IntelligenceLevel.MEDIUM,
            rank="Correctional Officer II", years_experience=8
        ),
        Guard(
            id=5, name="Sergeant Thompson", 
            personality=PersonalityType.COOPERATIVE,
            intelligence=IntelligenceLevel.HIGH,
            rank="Correctional Sergeant", years_experience=15, authority_level=2
        )
    ]
    
    return agents