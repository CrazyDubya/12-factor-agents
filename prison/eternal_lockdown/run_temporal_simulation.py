#!/usr/bin/env python3
"""
Temporal Prison Simulation - Full Day Progression
Realistic daily schedule with pod-based activities and interactions
"""

import sys
import os
import time
from datetime import datetime, timedelta

# Add paths
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from temporal_system import TemporalSimulation, TimeSegment, ActivityType
from core.game_theory import GameTheoryEngine, Strategy
from core.agents import create_sample_agents
from emotional_system import EmotionalProfile, EmotionalDecisionEngine
from sentence_system import SentenceCalculator
from run_ollama_simulation import SocialNetwork, OllamaDecisionEngine

def log(message, level="INFO"):
    """Live logging with timestamps"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    colors = {
        "INFO": "\033[94m",
        "SUCCESS": "\033[92m", 
        "WARNING": "\033[93m",
        "TEMPORAL": "\033[95m",
        "ACTIVITY": "\033[96m"
    }
    color = colors.get(level, "")
    reset = "\033[0m"
    print(f"{color}[{timestamp}] {level}: {message}{reset}")

def run_temporal_simulation():
    """Run full temporal simulation with realistic daily schedule"""
    
    print("⏰ ETERNAL LOCKDOWN - TEMPORAL PRISON SIMULATION")
    print("=" * 60)
    print("Realistic Daily Schedule with Pod-Based Activities")
    print("=" * 60)
    
    # Initialize systems
    temporal_sim = TemporalSimulation(pod_capacity=8)
    game_engine = GameTheoryEngine()
    emotional_engine = EmotionalDecisionEngine()
    social_network = SocialNetwork()
    ollama_engine = OllamaDecisionEngine()
    sentence_calc = SentenceCalculator()
    
    # Test Ollama
    if ollama_engine.test_connection():
        log("✅ Ollama connected and ready", "SUCCESS")
    else:
        log("⚠️  Ollama not available - using enhanced fallback", "WARNING")
    
    # Create agents
    log("👥 Creating pod population...", "INFO")
    agents = create_sample_agents()[:6]  # 6 agents for pod simulation
    
    # Add 2 guards for 8 total (pod capacity)
    from core.agents import Guard, PersonalityType, IntelligenceLevel
    agents.extend([
        Guard(7, "Officer Martinez", PersonalityType.STRATEGIC, IntelligenceLevel.MEDIUM),
        Guard(8, "Officer Kim", PersonalityType.COOPERATIVE, IntelligenceLevel.MEDIUM)
    ])
    
    # Initialize agent data
    agent_emotions = {}
    agent_sentences = {}
    agent_personalities = {}
    
    for agent in agents:
        agent_emotions[agent.id] = EmotionalProfile()
        agent_personalities[agent.id] = agent.personality.value
        
        if hasattr(agent, 'crime'):
            sentence_info = sentence_calc.calculate_sentence(agent.crime)
            agent_sentences[agent.id] = sentence_info
            log(f"   {agent.name}: {agent.personality.value}, {sentence_info.actual_days} days for {agent.crime}", "INFO")
        else:
            log(f"   {agent.name}: {agent.agent_type.value}, {agent.personality.value}", "INFO")
    
    # Set up pod structure
    log("🏠 Setting up pod structure...", "TEMPORAL")
    agent_ids = [agent.id for agent in agents]
    temporal_sim.assign_cells(agent_ids)
    temporal_sim.assign_work_duties(agent_ids, agent_personalities)
    
    # Form gangs in social network
    log("🏴 Forming gangs...", "INFO")
    social_network.form_gang("Los Hermanos", 1, [2])
    social_network.form_gang("Iron Brotherhood", 3, [4])
    
    # Statistics tracking
    total_interactions = 0
    total_cooperation = 0
    daily_stats = []
    
    log("🚀 Starting temporal simulation - Day 1", "SUCCESS")
    print("\n" + "="*60)
    
    # Simulate one full day (6 AM to 10 PM)
    start_time = datetime.now().replace(hour=6, minute=0, second=0, microsecond=0)
    current_time = start_time
    
    while current_time.hour < 22:  # Until 10 PM
        temporal_sim.current_time = current_time
        
        # Get current time segment and activities
        segment, available_activities = temporal_sim.get_current_time_segment()
        
        if available_activities:
            log(f"⏰ {current_time.strftime('%H:%M')} - {segment.value}", "TEMPORAL")
            
            # Assign agents to activities
            assignments = temporal_sim.assign_agents_to_activities(agent_ids, available_activities)
            
            # Show activity assignments
            activity_summary = {}
            for agent_id, activity in assignments.items():
                agent_name = next(a.name for a in agents if a.id == agent_id)
                if activity not in activity_summary:
                    activity_summary[activity] = []
                activity_summary[activity].append(agent_name)
            
            for activity, participants in activity_summary.items():
                log(f"   {activity.value}: {', '.join(participants)}", "ACTIVITY")
            
            # Generate interactions
            interactions = temporal_sim.get_interaction_opportunities(assignments)
            
            if interactions:
                log(f"🎭 {len(interactions)} interaction opportunities", "INFO")
                
                for agent1_id, agent2_id, context in interactions:
                    # Get agent objects
                    agent1 = next(a for a in agents if a.id == agent1_id)
                    agent2 = next(a for a in agents if a.id == agent2_id)
                    
                    # Get emotional and sentence context
                    emotion1 = agent_emotions.get(agent1_id)
                    emotion2 = agent_emotions.get(agent2_id)
                    sentence1 = agent_sentences.get(agent1_id)
                    sentence2 = agent_sentences.get(agent2_id)
                    
                    days_remaining1 = sentence1.days_remaining if sentence1 else 0
                    days_remaining2 = sentence2.days_remaining if sentence2 else 0
                    
                    # Make decisions
                    game_context = {"time_segment": segment.value, "activity": context}
                    
                    decision1, reasoning1 = ollama_engine.make_decision(
                        agent1, agent2_id, context, social_network, game_context, emotion1, days_remaining1)
                    decision2, reasoning2 = ollama_engine.make_decision(
                        agent2, agent1_id, context, social_network, game_context, emotion2, days_remaining2)
                    
                    # Calculate payoffs
                    payoffs = game_engine.agent_interaction(agent1_id, agent2_id, decision1, decision2)
                    
                    # Determine outcome
                    if decision1 == Strategy.COOPERATE and decision2 == Strategy.COOPERATE:
                        outcome = "mutual_cooperation"
                        outcome_emoji = "🤝"
                    elif decision1 == Strategy.DEFECT and decision2 == Strategy.DEFECT:
                        outcome = "mutual_defection"
                        outcome_emoji = "💥"
                    elif decision1 == Strategy.COOPERATE:
                        outcome = f"{agent1.name}_exploited"
                        outcome_emoji = "😢"
                    else:
                        outcome = f"{agent2.name}_exploited"
                        outcome_emoji = "😢"
                    
                    log(f"   {agent1.name} ({decision1.value}) vs {agent2.name} ({decision2.value}) -> {outcome_emoji} {outcome}", "INFO")
                    
                    # Update social network and emotions
                    social_network.update_relationship(agent1_id, agent2_id, outcome, payoffs)
                    
                    if emotion1:
                        relationship1 = "gang member" if agent2_id in social_network.get_gang_members(agent1_id) else \
                                       "ally" if agent2_id in social_network.alliances.get(agent1_id, set()) else \
                                       "enemy" if agent2_id in social_network.enemies.get(agent1_id, set()) else "neutral"
                        agent_emotions[agent1_id] = emotional_engine.update_emotions_from_interaction(
                            emotion1, decision1.value, decision2.value, payoffs[0], relationship1)
                    
                    # Update statistics
                    total_interactions += 1
                    if decision1 == Strategy.COOPERATE:
                        total_cooperation += 1
                    if decision2 == Strategy.COOPERATE:
                        total_cooperation += 1
            
            # Apply daily need decay during certain activities
            if segment in [TimeSegment.LUNCH, TimeSegment.DINNER]:
                for agent_id in agent_ids:
                    if agent_id in agent_emotions:
                        agent_emotions[agent_id] = emotional_engine.daily_need_decay(agent_emotions[agent_id])
        
        # Advance time by 30 minutes
        current_time += timedelta(minutes=30)
        time.sleep(0.5)  # Brief pause for readability
    
    # End of day summary
    log("🌙 Day 1 Complete - Lights Out", "SUCCESS")
    
    cooperation_rate = total_cooperation / max(total_interactions * 2, 1)
    
    print("\n" + "="*60)
    log("📊 DAILY SUMMARY", "SUCCESS")
    print("="*60)
    
    log(f"Total Interactions: {total_interactions}", "INFO")
    log(f"Cooperation Rate: {cooperation_rate:.1%}", "SUCCESS")
    
    # Agent status
    log("👥 Agent Status:", "INFO")
    for agent in agents:
        if agent.id in agent_emotions:
            emotion = agent_emotions[agent.id]
            wellbeing = emotion.get_overall_wellbeing()
            privilege_count = sum(emotion.privileges.values())
            log(f"   {agent.name}: {emotion.current_emotion.value}, wellbeing: {wellbeing:.2f}, privileges: {privilege_count}/7", "INFO")
    
    # Social network status
    network_stats = social_network.get_network_stats()
    log(f"Social Network: {network_stats['positive_relationships']}/{network_stats['total_relationships']} positive relationships", "INFO")
    
    log("✅ Temporal simulation complete!", "SUCCESS")
    
    return agents, social_network, agent_emotions, cooperation_rate

if __name__ == "__main__":
    try:
        agents, network, emotions, coop_rate = run_temporal_simulation()
        print(f"\n🎉 SUCCESS! Daily cooperation rate: {coop_rate:.1%}")
    except KeyboardInterrupt:
        print("\n⏹️  Simulation stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()