"""
Core Prison Simulation Engine
Orchestrates agent interactions with game theory and temporal dynamics
"""

import random
import time
from typing import List, Dict, Tuple, Any
from datetime import datetime, timedelta
import sqlite3
import json

from .game_theory import GameTheoryEngine, Strategy
from .agents import Agent, Prisoner, Guard, Warden, create_sample_agents

class PrisonSimulation:
    """Main simulation engine coordinating all components"""
    
    def __init__(self, db_path: str = "prison_simulation.db"):
        self.agents: Dict[int, Agent] = {}
        self.game_engine = GameTheoryEngine()
        self.db_path = db_path
        self.simulation_time = datetime.now()
        self.interaction_log = []
        
        # Simulation parameters
        self.time_acceleration = 3600  # 1 real second = 1 sim hour
        self.interaction_probability = 0.1  # Chance of interaction per step
        
        self._setup_database()
    
    def _setup_database(self):
        """Initialize SQLite database for persistence"""
        conn = sqlite3.connect(self.db_path)
        
        # Agents table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS agents (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                agent_type TEXT NOT NULL,
                personality TEXT NOT NULL,
                intelligence TEXT NOT NULL,
                cooperation_tendency REAL,
                reputation_score REAL,
                data JSON
            )
        ''')
        
        # Interactions table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                agent1_id INTEGER,
                agent2_id INTEGER,
                agent1_choice TEXT,
                agent2_choice TEXT,
                agent1_payoff REAL,
                agent2_payoff REAL,
                situation TEXT,
                FOREIGN KEY (agent1_id) REFERENCES agents (id),
                FOREIGN KEY (agent2_id) REFERENCES agents (id)
            )
        ''')
        
        # Population statistics
        conn.execute('''
            CREATE TABLE IF NOT EXISTS population_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                cooperation_rate REAL,
                total_interactions INTEGER,
                nash_equilibrium JSON
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_agent(self, agent: Agent):
        """Add agent to simulation"""
        self.agents[agent.id] = agent
        self.game_engine.register_agent(agent.id)
        self._save_agent(agent)
    
    def add_agents(self, agents: List[Agent]):
        """Add multiple agents"""
        for agent in agents:
            self.add_agent(agent)
    
    def _save_agent(self, agent: Agent):
        """Save agent to database"""
        conn = sqlite3.connect(self.db_path)
        
        # Serialize agent data
        agent_data = {
            "ollama_model": agent.ollama_model,
            "interaction_history": agent.interaction_history,
            "relationships": agent.relationships
        }
        
        # Add type-specific data
        if isinstance(agent, Prisoner):
            agent_data.update({
                "crime": agent.crime,
                "sentence_days": agent.sentence_days,
                "time_served": agent.time_served,
                "gang_affiliation": agent.gang_affiliation
            })
        elif isinstance(agent, Guard):
            agent_data.update({
                "rank": agent.rank,
                "years_experience": agent.years_experience,
                "authority_level": agent.authority_level,
                "shift": agent.shift
            })
        
        conn.execute('''
            INSERT OR REPLACE INTO agents 
            (id, name, agent_type, personality, intelligence, cooperation_tendency, reputation_score, data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            agent.id, agent.name, agent.agent_type.value, agent.personality.value,
            agent.intelligence.value, agent.cooperation_tendency, agent.reputation_score,
            json.dumps(agent_data)
        ))
        
        conn.commit()
        conn.close()
    
    def run_interaction(self, agent1_id: int, agent2_id: int, situation: str = "General interaction") -> Dict[str, Any]:
        """Run single interaction between two agents"""
        
        if agent1_id not in self.agents or agent2_id not in self.agents:
            raise ValueError("Invalid agent IDs")
        
        agent1 = self.agents[agent1_id]
        agent2 = self.agents[agent2_id]
        
        # Get decisions from both agents
        choice1 = agent1.make_decision(situation, agent2_id, self.game_engine)
        choice2 = agent2.make_decision(situation, agent1_id, self.game_engine)
        
        # Calculate payoffs using game engine
        payoffs = self.game_engine.agent_interaction(agent1_id, agent2_id, choice1, choice2)
        
        # Update agents with results
        agent1.update_from_interaction(agent2_id, choice1, choice2, payoffs[0])
        agent2.update_from_interaction(agent1_id, choice2, choice1, payoffs[1])
        
        # Log interaction
        interaction_record = {
            "timestamp": self.simulation_time.isoformat(),
            "agent1_id": agent1_id,
            "agent2_id": agent2_id,
            "agent1_name": agent1.name,
            "agent2_name": agent2.name,
            "agent1_choice": choice1.value,
            "agent2_choice": choice2.value,
            "agent1_payoff": payoffs[0],
            "agent2_payoff": payoffs[1],
            "situation": situation
        }
        
        self.interaction_log.append(interaction_record)
        self._save_interaction(interaction_record)
        
        return interaction_record
    
    def _save_interaction(self, interaction: Dict[str, Any]):
        """Save interaction to database"""
        conn = sqlite3.connect(self.db_path)
        
        conn.execute('''
            INSERT INTO interactions 
            (timestamp, agent1_id, agent2_id, agent1_choice, agent2_choice, 
             agent1_payoff, agent2_payoff, situation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            interaction["timestamp"], interaction["agent1_id"], interaction["agent2_id"],
            interaction["agent1_choice"], interaction["agent2_choice"],
            interaction["agent1_payoff"], interaction["agent2_payoff"], interaction["situation"]
        ))
        
        conn.commit()
        conn.close()
    
    def run_simulation_step(self):
        """Run one simulation step with potential interactions"""
        
        # Advance simulation time
        self.simulation_time += timedelta(seconds=self.time_acceleration)
        
        # Get list of agent IDs
        agent_ids = list(self.agents.keys())
        
        if len(agent_ids) < 2:
            return
        
        # Determine interactions for this step
        interactions_this_step = []
        
        for i, agent1_id in enumerate(agent_ids):
            for agent2_id in agent_ids[i+1:]:
                if random.random() < self.interaction_probability:
                    interactions_this_step.append((agent1_id, agent2_id))
        
        # Run interactions
        for agent1_id, agent2_id in interactions_this_step:
            situation = self._generate_situation()
            self.run_interaction(agent1_id, agent2_id, situation)
        
        # Evolve population strategies
        self.game_engine.evolve_population()
        
        # Save population statistics
        self._save_population_stats()
    
    def _generate_situation(self) -> str:
        """Generate random situation for interaction"""
        situations = [
            "Meal time in cafeteria",
            "Recreation yard activity", 
            "Work assignment coordination",
            "Cell block interaction",
            "Program participation",
            "Conflict resolution",
            "Resource sharing decision",
            "Information exchange",
            "Alliance formation opportunity",
            "Dispute over territory"
        ]
        return random.choice(situations)
    
    def _save_population_stats(self):
        """Save population-level statistics"""
        stats = self.game_engine.get_statistics()
        
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            INSERT INTO population_stats (timestamp, cooperation_rate, total_interactions, nash_equilibrium)
            VALUES (?, ?, ?, ?)
        ''', (
            self.simulation_time.isoformat(),
            stats["population_cooperation_rate"],
            stats["total_interactions"],
            json.dumps(stats["nash_equilibrium"])
        ))
        conn.commit()
        conn.close()
    
    def run_simulation(self, steps: int = 100, step_delay: float = 0.1):
        """Run simulation for specified number of steps"""
        
        print(f"🏢 Starting Prison Simulation with {len(self.agents)} agents")
        print(f"⏱️  Running {steps} steps with {step_delay}s delay")
        print("=" * 60)
        
        for step in range(steps):
            self.run_simulation_step()
            
            # Print progress every 10 steps
            if (step + 1) % 10 == 0:
                stats = self.game_engine.get_statistics()
                print(f"Step {step+1:3d}: Cooperation Rate: {stats['population_cooperation_rate']:.3f}, "
                      f"Interactions: {stats['total_interactions']}")
            
            time.sleep(step_delay)
        
        # Final statistics
        self.print_final_statistics()
    
    def print_final_statistics(self):
        """Print comprehensive simulation statistics"""
        stats = self.game_engine.get_statistics()
        
        print("\n" + "=" * 60)
        print("📊 FINAL SIMULATION STATISTICS")
        print("=" * 60)
        
        print(f"Total Agents: {len(self.agents)}")
        print(f"Total Interactions: {stats['total_interactions']}")
        print(f"Final Cooperation Rate: {stats['population_cooperation_rate']:.3f}")
        print(f"Nash Equilibrium: {stats['nash_equilibrium']}")
        
        # Agent-specific statistics
        print("\n👥 Agent Statistics:")
        for agent_id, agent in self.agents.items():
            interactions = len(agent.interaction_history)
            avg_payoff = sum(i.get("my_payoff", 0) for i in agent.interaction_history) / max(interactions, 1)
            print(f"  {agent.name}: {interactions} interactions, avg payoff: {avg_payoff:.2f}, "
                  f"cooperation tendency: {agent.cooperation_tendency:.3f}")
        
        # Recent interactions
        print(f"\n🔄 Recent Interactions (last 5):")
        for interaction in self.interaction_log[-5:]:
            print(f"  {interaction['agent1_name']} ({interaction['agent1_choice']}) vs "
                  f"{interaction['agent2_name']} ({interaction['agent2_choice']}) -> "
                  f"Payoffs: ({interaction['agent1_payoff']}, {interaction['agent2_payoff']})")
    
    def get_agent_relationships(self, agent_id: int) -> Dict[str, Any]:
        """Get relationship network for specific agent"""
        if agent_id not in self.agents:
            return {}
        
        agent = self.agents[agent_id]
        relationships = {}
        
        for other_id, trust_level in agent.relationships.items():
            if other_id in self.agents:
                relationships[self.agents[other_id].name] = {
                    "trust_level": trust_level,
                    "agent_type": self.agents[other_id].agent_type.value,
                    "interactions": len([i for i in agent.interaction_history 
                                       if i.get("opponent_id") == other_id])
                }
        
        return relationships

def run_demo_simulation():
    """Run a demonstration simulation"""
    
    # Create simulation
    sim = PrisonSimulation()
    
    # Add sample agents
    agents = create_sample_agents()
    sim.add_agents(agents)
    
    print("🎮 Created agents:")
    for agent in agents:
        print(f"  {agent.name} ({agent.agent_type.value}, {agent.personality.value}, {agent.ollama_model})")
    
    # Run simulation
    sim.run_simulation(steps=50, step_delay=0.05)
    
    # Show relationships
    print("\n🤝 Agent Relationships:")
    for agent_id in [1, 2, 3]:  # Show prisoner relationships
        relationships = sim.get_agent_relationships(agent_id)
        agent_name = sim.agents[agent_id].name
        print(f"\n{agent_name}:")
        for other_name, data in relationships.items():
            print(f"  -> {other_name}: trust={data['trust_level']:.2f}, "
                  f"interactions={data['interactions']}")
    
    return sim

if __name__ == "__main__":
    run_demo_simulation()