"""
Game Theory Engine for Eternal Lockdown Prison Simulation
Core Prisoner's Dilemma mechanics with replicator dynamics
"""

import numpy as np
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import random

class Strategy(Enum):
    COOPERATE = "cooperate"
    DEFECT = "defect"

@dataclass
class PDPayoffs:
    """Prisoner's Dilemma payoff matrix: T > R > P > S"""
    T: float = 5.0  # Temptation (defect when opponent cooperates)
    R: float = 3.0  # Reward (mutual cooperation)
    P: float = 1.0  # Punishment (mutual defection)
    S: float = 0.0  # Sucker (cooperate when opponent defects)
    
    def __post_init__(self):
        """Validate T > R > P > S constraint"""
        if not (self.T > self.R > self.P > self.S):
            raise ValueError(f"Invalid payoffs: T({self.T}) > R({self.R}) > P({self.P}) > S({self.S}) required")

class PrisonersDilemma:
    """Core Prisoner's Dilemma game mechanics"""
    
    def __init__(self, payoffs: PDPayoffs = None):
        self.payoffs = payoffs or PDPayoffs()
        self.interaction_history = []
    
    def play_round(self, agent1_choice: Strategy, agent2_choice: Strategy) -> Tuple[float, float]:
        """
        Play one round of PD and return payoffs
        
        Returns:
            (agent1_payoff, agent2_payoff)
        """
        choice_key = (agent1_choice.value, agent2_choice.value)
        
        payoff_matrix = {
            ("cooperate", "cooperate"): (self.payoffs.R, self.payoffs.R),
            ("cooperate", "defect"): (self.payoffs.S, self.payoffs.T),
            ("defect", "cooperate"): (self.payoffs.T, self.payoffs.S),
            ("defect", "defect"): (self.payoffs.P, self.payoffs.P)
        }
        
        payoffs = payoff_matrix[choice_key]
        
        # Log interaction
        self.interaction_history.append({
            "agent1_choice": agent1_choice.value,
            "agent2_choice": agent2_choice.value,
            "agent1_payoff": payoffs[0],
            "agent2_payoff": payoffs[1]
        })
        
        return payoffs
    
    def get_expected_payoff(self, my_strategy: Strategy, opponent_coop_prob: float) -> float:
        """Calculate expected payoff given opponent's cooperation probability"""
        if my_strategy == Strategy.COOPERATE:
            return opponent_coop_prob * self.payoffs.R + (1 - opponent_coop_prob) * self.payoffs.S
        else:  # DEFECT
            return opponent_coop_prob * self.payoffs.T + (1 - opponent_coop_prob) * self.payoffs.P

class ReplicatorDynamics:
    """
    Implements replicator dynamics for strategy evolution
    ẋᵢ = xᵢ(fᵢ - f̄) where xᵢ is strategy frequency, fᵢ is fitness, f̄ is average fitness
    """
    
    def __init__(self, payoffs: PDPayoffs = None):
        self.payoffs = payoffs or PDPayoffs()
        self.pd_game = PrisonersDilemma(self.payoffs)
    
    def calculate_fitness(self, strategy_frequencies: np.ndarray) -> np.ndarray:
        """
        Calculate fitness for each strategy given current population frequencies
        
        Args:
            strategy_frequencies: [coop_freq, defect_freq] where sum = 1.0
            
        Returns:
            [coop_fitness, defect_fitness]
        """
        coop_freq, defect_freq = strategy_frequencies
        
        # Fitness = expected payoff when playing against population
        coop_fitness = (coop_freq * self.payoffs.R + defect_freq * self.payoffs.S)
        defect_fitness = (coop_freq * self.payoffs.T + defect_freq * self.payoffs.P)
        
        return np.array([coop_fitness, defect_fitness])
    
    def evolve_step(self, strategy_frequencies: np.ndarray, dt: float = 0.01) -> np.ndarray:
        """
        Single evolution step using replicator dynamics
        
        Args:
            strategy_frequencies: Current [coop_freq, defect_freq]
            dt: Time step size
            
        Returns:
            Updated strategy frequencies
        """
        fitness = self.calculate_fitness(strategy_frequencies)
        avg_fitness = np.dot(strategy_frequencies, fitness)
        
        # ẋᵢ = xᵢ(fᵢ - f̄)
        dx_dt = strategy_frequencies * (fitness - avg_fitness)
        
        # Update frequencies
        new_frequencies = strategy_frequencies + dt * dx_dt
        
        # Ensure frequencies stay in [0,1] and sum to 1
        new_frequencies = np.clip(new_frequencies, 0.0, 1.0)
        new_frequencies = new_frequencies / np.sum(new_frequencies)
        
        return new_frequencies
    
    def find_equilibrium(self, initial_frequencies: np.ndarray, 
                        max_iterations: int = 1000, tolerance: float = 1e-6) -> np.ndarray:
        """Find Nash equilibrium through iterative evolution"""
        frequencies = initial_frequencies.copy()
        
        for _ in range(max_iterations):
            new_frequencies = self.evolve_step(frequencies)
            
            if np.allclose(frequencies, new_frequencies, atol=tolerance):
                break
                
            frequencies = new_frequencies
        
        return frequencies
    
    def simulate_evolution(self, initial_frequencies: np.ndarray, 
                          steps: int = 100, dt: float = 0.01) -> List[np.ndarray]:
        """Simulate strategy evolution over time"""
        evolution = [initial_frequencies.copy()]
        frequencies = initial_frequencies.copy()
        
        for _ in range(steps):
            frequencies = self.evolve_step(frequencies, dt)
            evolution.append(frequencies.copy())
        
        return evolution

class StrategyLearning:
    """Individual agent strategy learning mechanisms"""
    
    def __init__(self, learning_rate: float = 0.1, memory_length: int = 10):
        self.learning_rate = learning_rate
        self.memory_length = memory_length
        self.interaction_history = []
    
    def update_strategy(self, my_choice: Strategy, opponent_choice: Strategy, 
                       my_payoff: float, cooperation_tendency: float) -> float:
        """
        Update cooperation tendency based on interaction outcome
        
        Args:
            my_choice: What I chose
            opponent_choice: What opponent chose  
            my_payoff: Payoff I received
            cooperation_tendency: Current cooperation probability
            
        Returns:
            Updated cooperation tendency
        """
        # Record interaction
        self.interaction_history.append({
            "my_choice": my_choice.value,
            "opponent_choice": opponent_choice.value,
            "my_payoff": my_payoff
        })
        
        # Keep only recent history
        if len(self.interaction_history) > self.memory_length:
            self.interaction_history = self.interaction_history[-self.memory_length:]
        
        # Simple reinforcement learning
        if my_payoff > 2.5:  # Good outcome (above average)
            if my_choice == Strategy.COOPERATE:
                # Reward cooperation when it pays off
                cooperation_tendency += self.learning_rate * 0.1
            else:
                # Punish defection when cooperation might have been better
                if opponent_choice == Strategy.COOPERATE:
                    cooperation_tendency += self.learning_rate * 0.05
        else:  # Poor outcome
            if my_choice == Strategy.COOPERATE:
                # Punish cooperation when exploited
                cooperation_tendency -= self.learning_rate * 0.15
            else:
                # Slightly reward defection when it prevents exploitation
                cooperation_tendency -= self.learning_rate * 0.05
        
        # Keep in bounds [0, 1]
        return np.clip(cooperation_tendency, 0.0, 1.0)
    
    def get_cooperation_probability(self, opponent_history: List[Strategy] = None) -> float:
        """Calculate cooperation probability based on opponent's history"""
        if not opponent_history:
            return 0.5  # Default neutral
        
        # Tit-for-tat style: cooperate if opponent cooperated recently
        recent_cooperations = sum(1 for choice in opponent_history[-3:] 
                                if choice == Strategy.COOPERATE)
        recent_total = min(len(opponent_history), 3)
        
        if recent_total == 0:
            return 0.5
        
        return recent_cooperations / recent_total

class GameTheoryEngine:
    """Main game theory engine orchestrating all mechanisms"""
    
    def __init__(self, payoffs: PDPayoffs = None):
        self.payoffs = payoffs or PDPayoffs()
        self.pd_game = PrisonersDilemma(self.payoffs)
        self.replicator = ReplicatorDynamics(self.payoffs)
        self.agent_learners = {}  # agent_id -> StrategyLearning
        
        # Population-level tracking
        self.population_strategies = np.array([0.5, 0.5])  # [coop, defect]
        self.strategy_evolution_history = []
    
    def register_agent(self, agent_id: int, learning_rate: float = 0.1, memory_length: int = 10):
        """Register an agent for strategy learning"""
        self.agent_learners[agent_id] = StrategyLearning(learning_rate, memory_length)
    
    def agent_interaction(self, agent1_id: int, agent2_id: int, 
                         agent1_choice: Strategy, agent2_choice: Strategy) -> Tuple[float, float]:
        """
        Process interaction between two agents
        
        Returns:
            (agent1_payoff, agent2_payoff)
        """
        # Play the game
        payoffs = self.pd_game.play_round(agent1_choice, agent2_choice)
        
        # Update individual learning if agents are registered
        if agent1_id in self.agent_learners:
            self.agent_learners[agent1_id].update_strategy(
                agent1_choice, agent2_choice, payoffs[0], 0.5  # placeholder cooperation tendency
            )
        
        if agent2_id in self.agent_learners:
            self.agent_learners[agent2_id].update_strategy(
                agent2_choice, agent1_choice, payoffs[1], 0.5  # placeholder cooperation tendency
            )
        
        # Update population-level statistics
        self._update_population_stats(agent1_choice, agent2_choice)
        
        return payoffs
    
    def _update_population_stats(self, choice1: Strategy, choice2: Strategy):
        """Update population-level strategy frequencies"""
        total_choices = 2
        cooperations = sum(1 for choice in [choice1, choice2] if choice == Strategy.COOPERATE)
        
        # Exponential moving average update
        alpha = 0.1  # Learning rate for population stats
        new_coop_freq = cooperations / total_choices
        
        self.population_strategies[0] = (1 - alpha) * self.population_strategies[0] + alpha * new_coop_freq
        self.population_strategies[1] = 1 - self.population_strategies[0]
    
    def evolve_population(self, steps: int = 1) -> np.ndarray:
        """Evolve population strategies using replicator dynamics"""
        for _ in range(steps):
            self.population_strategies = self.replicator.evolve_step(self.population_strategies)
        
        self.strategy_evolution_history.append(self.population_strategies.copy())
        return self.population_strategies
    
    def get_nash_equilibrium(self) -> np.ndarray:
        """Calculate Nash equilibrium for current payoffs"""
        return self.replicator.find_equilibrium(self.population_strategies)
    
    def get_agent_recommendation(self, agent_id: int, opponent_history: List[Strategy] = None) -> float:
        """Get cooperation probability recommendation for an agent"""
        if agent_id in self.agent_learners:
            return self.agent_learners[agent_id].get_cooperation_probability(opponent_history)
        return 0.5  # Default neutral
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive game theory statistics"""
        return {
            "population_cooperation_rate": self.population_strategies[0],
            "population_defection_rate": self.population_strategies[1],
            "total_interactions": len(self.pd_game.interaction_history),
            "nash_equilibrium": self.get_nash_equilibrium().tolist(),
            "payoff_matrix": {
                "T": self.payoffs.T,
                "R": self.payoffs.R, 
                "P": self.payoffs.P,
                "S": self.payoffs.S
            },
            "registered_agents": len(self.agent_learners)
        }

# Quick test function
def test_game_theory_engine():
    """Test the game theory engine with sample interactions"""
    engine = GameTheoryEngine()
    
    # Register some agents
    engine.register_agent(1)
    engine.register_agent(2)
    
    # Simulate some interactions
    interactions = [
        (Strategy.COOPERATE, Strategy.COOPERATE),
        (Strategy.COOPERATE, Strategy.DEFECT),
        (Strategy.DEFECT, Strategy.COOPERATE),
        (Strategy.DEFECT, Strategy.DEFECT),
    ]
    
    print("🎮 Testing Game Theory Engine")
    print("=" * 40)
    
    for i, (choice1, choice2) in enumerate(interactions):
        payoffs = engine.agent_interaction(1, 2, choice1, choice2)
        print(f"Round {i+1}: Agent1({choice1.value}) vs Agent2({choice2.value}) -> Payoffs: {payoffs}")
    
    # Show statistics
    stats = engine.get_statistics()
    print(f"\n📊 Final Statistics:")
    print(f"Cooperation Rate: {stats['population_cooperation_rate']:.3f}")
    print(f"Total Interactions: {stats['total_interactions']}")
    print(f"Nash Equilibrium: {stats['nash_equilibrium']}")
    
    return engine

if __name__ == "__main__":
    test_game_theory_engine()