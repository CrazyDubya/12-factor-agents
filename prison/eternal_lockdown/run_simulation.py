#!/usr/bin/env python3
"""
Eternal Lockdown Prison Simulation - Main Runner
Complete game theory-driven prison simulation with Ollama integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.game_theory import GameTheoryEngine, Strategy
from core.agents import create_sample_agents, Prisoner, Guard
from core.simulation import PrisonSimulation

def main():
    """Run the complete prison simulation"""
    
    print("🏢 ETERNAL LOCKDOWN PRISON SIMULATION")
    print("=" * 60)
    print("Game Theory-Driven Multi-Agent Prison Dynamics")
    print("Powered by Ollama + Prisoner's Dilemma + Replicator Dynamics")
    print("=" * 60)
    
    # Test Ollama connection
    print("\n🔍 Testing Ollama connection...")
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f"✅ Ollama connected with {len(models)} models")
        else:
            print("⚠️  Ollama not responding - using fallback decisions")
    except Exception as e:
        print(f"⚠️  Ollama connection failed: {e}")
        print("   Continuing with personality-based fallback decisions")
    
    # Create simulation
    print("\n🎮 Initializing simulation...")
    sim = PrisonSimulation()
    
    # Add diverse agents
    agents = create_sample_agents()
    sim.add_agents(agents)
    
    print(f"\n👥 Created {len(agents)} agents:")
    for agent in agents:
        print(f"   {agent.name:20} | {agent.agent_type.value:8} | {agent.personality.value:12} | {agent.ollama_model}")
    
    # Run some manual interactions first
    print("\n🎭 Running manual test interactions...")
    
    # Test prisoner-prisoner interaction
    interaction1 = sim.run_interaction(1, 2, "Cafeteria meal time - deciding whether to share information")
    print(f"   {interaction1['agent1_name']} ({interaction1['agent1_choice']}) vs "
          f"{interaction1['agent2_name']} ({interaction1['agent2_choice']}) -> "
          f"Payoffs: ({interaction1['agent1_payoff']}, {interaction1['agent2_payoff']})")
    
    # Test prisoner-guard interaction  
    interaction2 = sim.run_interaction(1, 4, "Recreation yard - guard observing prisoner behavior")
    print(f"   {interaction2['agent1_name']} ({interaction2['agent1_choice']}) vs "
          f"{interaction2['agent2_name']} ({interaction2['agent2_choice']}) -> "
          f"Payoffs: ({interaction2['agent1_payoff']}, {interaction2['agent2_payoff']})")
    
    # Test strategic vs aggressive
    interaction3 = sim.run_interaction(2, 3, "Work assignment - resource allocation conflict")
    print(f"   {interaction3['agent1_name']} ({interaction3['agent1_choice']}) vs "
          f"{interaction3['agent2_name']} ({interaction3['agent2_choice']}) -> "
          f"Payoffs: ({interaction3['agent1_payoff']}, {interaction3['agent2_payoff']})")
    
    # Run full simulation
    print(f"\n🚀 Running full simulation...")
    sim.run_simulation(steps=100, step_delay=0.02)
    
    # Show final relationships
    print("\n🤝 Final Agent Relationships:")
    for agent_id in [1, 2, 3]:  # Prisoners
        relationships = sim.get_agent_relationships(agent_id)
        agent_name = sim.agents[agent_id].name
        print(f"\n   {agent_name}:")
        for other_name, data in relationships.items():
            trust_emoji = "🤝" if data['trust_level'] > 0.3 else "⚠️" if data['trust_level'] > -0.3 else "💀"
            print(f"      {trust_emoji} {other_name:20} | Trust: {data['trust_level']:+.2f} | Interactions: {data['interactions']}")
    
    # Game theory analysis
    print("\n📊 Game Theory Analysis:")
    stats = sim.game_engine.get_statistics()
    nash_eq = stats['nash_equilibrium']
    print(f"   Nash Equilibrium: {nash_eq[0]:.3f} cooperation, {nash_eq[1]:.3f} defection")
    print(f"   Actual Population: {stats['population_cooperation_rate']:.3f} cooperation")
    
    if stats['population_cooperation_rate'] > nash_eq[0]:
        print("   📈 Population MORE cooperative than Nash equilibrium predicts!")
    else:
        print("   📉 Population following Nash equilibrium (mutual defection)")
    
    print(f"\n🎯 Simulation Complete!")
    print(f"   Database: {sim.db_path}")
    print(f"   Total Interactions: {stats['total_interactions']}")
    print(f"   Final Cooperation Rate: {stats['population_cooperation_rate']:.1%}")
    
    return sim

if __name__ == "__main__":
    try:
        simulation = main()
        print("\n✅ Simulation completed successfully!")
    except KeyboardInterrupt:
        print("\n⏹️  Simulation interrupted by user")
    except Exception as e:
        print(f"\n❌ Simulation failed: {e}")
        import traceback
        traceback.print_exc()