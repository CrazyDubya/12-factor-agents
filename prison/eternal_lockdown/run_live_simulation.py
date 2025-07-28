#!/usr/bin/env python3
"""
LIVE Prison Simulation with Real-Time Monitoring
Shows everything happening as it happens
"""

import sys
import os
import time
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.game_theory import GameTheoryEngine, Strategy, PrisonersDilemma
from core.agents import Agent, Prisoner, Guard, PersonalityType, IntelligenceLevel

def log(message, level="INFO"):
    """Live logging with timestamps"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")

def create_simple_agents():
    """Create simple agents for live demo"""
    agents = [
        Prisoner(1, "Marcus", PersonalityType.COOPERATIVE, IntelligenceLevel.MEDIUM, 
                crime="Drug possession", sentence_days=1825),
        Prisoner(2, "Carlos", PersonalityType.STRATEGIC, IntelligenceLevel.HIGH,
                crime="Racketeering", sentence_days=2920),
        Prisoner(3, "Tommy", PersonalityType.AGGRESSIVE, IntelligenceLevel.LOW,
                crime="Armed robbery", sentence_days=4380),
        Guard(4, "Officer Martinez", PersonalityType.STRATEGIC, IntelligenceLevel.MEDIUM,
              rank="Officer II", years_experience=8)
    ]
    return agents

def test_ollama_live():
    """Test Ollama with live feedback"""
    log("Testing Ollama connection...")
    
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            log(f"✅ Ollama connected! Found {len(models)} models")
            for model in models[:3]:
                log(f"   📦 {model['name']}")
            return True
        else:
            log(f"❌ Ollama returned status {response.status_code}")
            return False
    except Exception as e:
        log(f"❌ Ollama connection failed: {e}")
        return False

def run_single_interaction_live(agent1, agent2, situation):
    """Run single interaction with full visibility"""
    log(f"🎭 INTERACTION: {agent1.name} vs {agent2.name}")
    log(f"   Situation: {situation}")
    log(f"   {agent1.name}: {agent1.personality.value} personality, {agent1.cooperation_tendency:.2f} cooperation tendency")
    log(f"   {agent2.name}: {agent2.personality.value} personality, {agent2.cooperation_tendency:.2f} cooperation tendency")
    
    # Create game engine
    game = PrisonersDilemma()
    
    # Get decisions (simplified without Ollama for now)
    log("🤔 Agents making decisions...")
    
    # Agent 1 decision
    if agent1.personality == PersonalityType.COOPERATIVE:
        choice1 = Strategy.COOPERATE
        log(f"   {agent1.name} chooses COOPERATE (cooperative personality)")
    elif agent1.personality == PersonalityType.AGGRESSIVE:
        choice1 = Strategy.DEFECT
        log(f"   {agent1.name} chooses DEFECT (aggressive personality)")
    else:
        choice1 = Strategy.COOPERATE if agent1.cooperation_tendency > 0.5 else Strategy.DEFECT
        log(f"   {agent1.name} chooses {choice1.value} (tendency: {agent1.cooperation_tendency:.2f})")
    
    # Agent 2 decision
    if agent2.personality == PersonalityType.COOPERATIVE:
        choice2 = Strategy.COOPERATE
        log(f"   {agent2.name} chooses COOPERATE (cooperative personality)")
    elif agent2.personality == PersonalityType.AGGRESSIVE:
        choice2 = Strategy.DEFECT
        log(f"   {agent2.name} chooses DEFECT (aggressive personality)")
    else:
        choice2 = Strategy.COOPERATE if agent2.cooperation_tendency > 0.5 else Strategy.DEFECT
        log(f"   {agent2.name} chooses {choice2.value} (tendency: {agent2.cooperation_tendency:.2f})")
    
    # Calculate payoffs
    payoffs = game.play_round(choice1, choice2)
    
    log(f"💰 RESULTS:")
    log(f"   {agent1.name}: {choice1.value} -> {payoffs[0]} points")
    log(f"   {agent2.name}: {choice2.value} -> {payoffs[1]} points")
    
    # Determine outcome type
    if choice1 == Strategy.COOPERATE and choice2 == Strategy.COOPERATE:
        outcome = "🤝 MUTUAL COOPERATION"
    elif choice1 == Strategy.DEFECT and choice2 == Strategy.DEFECT:
        outcome = "💥 MUTUAL DEFECTION"
    elif choice1 == Strategy.COOPERATE:
        outcome = f"😢 {agent1.name} EXPLOITED by {agent2.name}"
    else:
        outcome = f"😢 {agent2.name} EXPLOITED by {agent1.name}"
    
    log(f"   Outcome: {outcome}")
    
    # Update cooperation tendencies based on outcome
    if payoffs[0] > 2.5:  # Good outcome for agent1
        agent1.cooperation_tendency = min(1.0, agent1.cooperation_tendency + 0.05)
    else:  # Poor outcome
        agent1.cooperation_tendency = max(0.0, agent1.cooperation_tendency - 0.1)
    
    if payoffs[1] > 2.5:  # Good outcome for agent2
        agent2.cooperation_tendency = min(1.0, agent2.cooperation_tendency + 0.05)
    else:  # Poor outcome
        agent2.cooperation_tendency = max(0.0, agent2.cooperation_tendency - 0.1)
    
    log(f"📈 LEARNING:")
    log(f"   {agent1.name} cooperation tendency: {agent1.cooperation_tendency:.3f}")
    log(f"   {agent2.name} cooperation tendency: {agent2.cooperation_tendency:.3f}")
    
    return payoffs, choice1, choice2

def run_live_simulation():
    """Run simulation with full live monitoring"""
    
    print("🏢 ETERNAL LOCKDOWN - LIVE PRISON SIMULATION")
    print("=" * 60)
    print("Real-time monitoring of game theory dynamics")
    print("=" * 60)
    
    # Test Ollama
    ollama_working = test_ollama_live()
    if not ollama_working:
        log("⚠️  Continuing without Ollama (using personality-based decisions)")
    
    # Create agents
    log("👥 Creating prison agents...")
    agents = create_simple_agents()
    
    for agent in agents:
        log(f"   Created {agent.name}: {agent.agent_type.value}, {agent.personality.value}, {agent.intelligence.value}")
    
    # Track statistics
    total_interactions = 0
    total_cooperation = 0
    agent_scores = {agent.id: 0 for agent in agents}
    
    log("🚀 Starting live simulation...")
    print("\n" + "="*60)
    
    # Run multiple rounds
    situations = [
        "Cafeteria meal time - deciding whether to share food",
        "Recreation yard - forming alliances", 
        "Work assignment - cooperating on tasks",
        "Cell block - sharing information",
        "Conflict resolution - choosing to escalate or de-escalate"
    ]
    
    for round_num in range(1, 11):  # 10 rounds
        log(f"🔄 ROUND {round_num}")
        
        # Pick random pair of agents
        import random
        agent1, agent2 = random.sample(agents, 2)
        situation = random.choice(situations)
        
        # Run interaction
        payoffs, choice1, choice2 = run_single_interaction_live(agent1, agent2, situation)
        
        # Update statistics
        total_interactions += 1
        if choice1 == Strategy.COOPERATE:
            total_cooperation += 1
        if choice2 == Strategy.COOPERATE:
            total_cooperation += 1
        
        agent_scores[agent1.id] += payoffs[0]
        agent_scores[agent2.id] += payoffs[1]
        
        # Show running statistics
        cooperation_rate = total_cooperation / (total_interactions * 2)
        log(f"📊 RUNNING STATS: Cooperation rate: {cooperation_rate:.1%}, Total interactions: {total_interactions}")
        
        print("-" * 40)
        time.sleep(1)  # Pause between rounds
    
    # Final statistics
    print("\n" + "="*60)
    log("📊 FINAL STATISTICS")
    print("="*60)
    
    final_cooperation_rate = total_cooperation / (total_interactions * 2)
    log(f"Total Interactions: {total_interactions}")
    log(f"Final Cooperation Rate: {final_cooperation_rate:.1%}")
    
    log("🏆 AGENT SCORES:")
    for agent in agents:
        score = agent_scores[agent.id]
        avg_score = score / max(1, sum(1 for a in agents if a.id in [agent.id]))  # Rough average
        log(f"   {agent.name:20}: {score:6.1f} points, cooperation: {agent.cooperation_tendency:.3f}")
    
    # Game theory analysis
    log("🎯 GAME THEORY ANALYSIS:")
    nash_coop_rate = 0.0  # Nash equilibrium predicts mutual defection
    if final_cooperation_rate > nash_coop_rate + 0.1:
        log("   📈 Population MORE cooperative than Nash equilibrium!")
        log("   🎉 Agents learned to cooperate despite game theory predictions")
    elif final_cooperation_rate < 0.1:
        log("   📉 Population following Nash equilibrium (mutual defection)")
        log("   😔 Agents stuck in defection trap")
    else:
        log("   ⚖️  Population near Nash equilibrium")
    
    log("✅ Simulation complete!")
    
    return agents, agent_scores, final_cooperation_rate

if __name__ == "__main__":
    try:
        agents, scores, coop_rate = run_live_simulation()
        print(f"\n🎉 SUCCESS! Final cooperation rate: {coop_rate:.1%}")
    except KeyboardInterrupt:
        print("\n⏹️  Simulation stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()