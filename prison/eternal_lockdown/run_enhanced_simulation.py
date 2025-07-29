#!/usr/bin/env python3
"""
Enhanced Temporal Prison Simulation
Expanded game theory + conversational interactions + room-based opportunities
"""

import sys
import os
import time
from datetime import datetime, timedelta

# Add paths
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from temporal_system import TemporalSimulation, TimeSegment, ActivityType, Location
from expanded_game_theory import ExpandedGameEngine, InteractionType, GameType
from room_interaction_system import RoomInteractionManager
from core.game_theory import GameTheoryEngine, Strategy
from core.agents import create_sample_agents, Guard, PersonalityType, IntelligenceLevel
from emotional_system import EmotionalProfile, EmotionalDecisionEngine
from sentence_system import SentenceCalculator
from run_ollama_simulation import SocialNetwork, OllamaDecisionEngine

def log(message, level="INFO"):
    """Live logging with timestamps and colors"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    colors = {
        "INFO": "\033[94m",
        "SUCCESS": "\033[92m", 
        "WARNING": "\033[93m",
        "TEMPORAL": "\033[95m",
        "ACTIVITY": "\033[96m",
        "CONVERSATION": "\033[97m",
        "GAME": "\033[93m"
    }
    color = colors.get(level, "")
    reset = "\033[0m"
    print(f"{color}[{timestamp}] {level}: {message}{reset}")

def run_enhanced_simulation():
    """Run enhanced simulation with expanded game theory and conversations"""
    
    print("🎭 ETERNAL LOCKDOWN - ENHANCED PRISON SIMULATION")
    print("=" * 70)
    print("Expanded Game Theory + Conversational Interactions + Room Dynamics")
    print("=" * 70)
    
    # Initialize all systems
    temporal_sim = TemporalSimulation(pod_capacity=8)
    room_manager = RoomInteractionManager()
    game_engine = GameTheoryEngine()
    emotional_engine = EmotionalDecisionEngine()
    social_network = SocialNetwork()
    ollama_engine = OllamaDecisionEngine()
    sentence_calc = SentenceCalculator()
    
    # Test Ollama
    if ollama_engine.test_connection():
        log("✅ Ollama connected - enhanced AI conversations enabled", "SUCCESS")
    else:
        log("⚠️  Ollama not available - using enhanced fallback conversations", "WARNING")
    
    # Create enhanced agent population
    log("👥 Creating enhanced pod population...", "INFO")
    agents = create_sample_agents()[:6]  # 6 inmates
    
    # Add 2 guards
    agents.extend([
        Guard(7, "Officer Martinez", PersonalityType.STRATEGIC, IntelligenceLevel.MEDIUM),
        Guard(8, "Officer Kim", PersonalityType.COOPERATIVE, IntelligenceLevel.MEDIUM)
    ])
    
    # Initialize enhanced agent data
    agent_emotions = {}
    agent_sentences = {}
    agent_data = {}
    
    for agent in agents:
        agent_emotions[agent.id] = EmotionalProfile()
        agent_data[agent.id] = {
            'id': agent.id,
            'name': agent.name,
            'agent_type': agent.agent_type.value,
            'personality': agent.personality.value,
            'intelligence': agent.intelligence.value,
            'ollama_model': agent.ollama_model
        }
        
        if hasattr(agent, 'crime'):
            sentence_info = sentence_calc.calculate_sentence(agent.crime)
            agent_sentences[agent.id] = sentence_info
            log(f"   {agent.name}: {agent.personality.value}, {sentence_info.actual_days} days for {agent.crime}", "INFO")
        else:
            log(f"   {agent.name}: {agent.agent_type.value}, {agent.personality.value}", "INFO")
    
    # Set up enhanced pod structure
    log("🏠 Setting up enhanced pod structure...", "TEMPORAL")
    agent_ids = [agent.id for agent in agents]
    temporal_sim.assign_cells(agent_ids)
    temporal_sim.assign_work_duties(agent_ids, {aid: agent_data[aid]['personality'] for aid in agent_ids})
    
    # Form gangs
    log("🏴 Forming gangs with enhanced dynamics...", "INFO")
    social_network.form_gang("Los Hermanos", 1, [2])
    social_network.form_gang("Iron Brotherhood", 3, [4])
    
    # Enhanced statistics tracking
    total_interactions = 0
    total_cooperation = 0
    conversation_log = []
    game_type_stats = {}
    
    log("🚀 Starting enhanced temporal simulation - Day 1", "SUCCESS")
    print("\n" + "="*70)
    
    # Simulate enhanced day (6 AM to 10 PM)
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
            
            # Group agents by location
            location_groups = {}
            for agent_id, activity in assignments.items():
                location = temporal_sim.agent_locations[agent_id]
                if location not in location_groups:
                    location_groups[location] = []
                location_groups[location].append(agent_id)
            
            # Generate enhanced interactions for each location
            for location, participants_ids in location_groups.items():
                if len(participants_ids) < 2:
                    continue
                
                # Get participant data
                participants = [agent_data[aid] for aid in participants_ids]
                current_activity = assignments[participants_ids[0]]
                
                # Generate room-based interactions
                interactions = room_manager.generate_room_interactions(
                    location, participants, current_activity, segment.value
                )
                
                if interactions:
                    log(f"🏠 {location.value}: {len(interactions)} enhanced interactions", "ACTIVITY")
                    
                    for interaction in interactions:
                        # Enhanced interaction processing
                        agent1_id = interaction['participants'][0]
                        agent2_id = interaction['participants'][1]
                        
                        # Skip guard-guard interactions (not implemented yet)
                        if (agent_data[agent1_id]['agent_type'] == 'guard' and 
                            agent_data[agent2_id]['agent_type'] == 'guard'):
                            continue
                        
                        # Log conversation
                        log(f"🎭 {interaction['opportunity'].replace('_', ' ').title()}: "
                            f"{interaction['participant_names'][0]} vs {interaction['participant_names'][1]}", "CONVERSATION")
                        
                        conv = interaction['conversation']
                        log(f"   {conv['opening']}", "CONVERSATION")
                        log(f"   {conv['agent1_decision']}", "CONVERSATION")
                        log(f"   {conv['agent2_response']}", "CONVERSATION")
                        
                        # Log game outcome
                        game_type = interaction['game_type']
                        payoffs = interaction['payoffs']
                        log(f"   Game: {game_type.replace('_', ' ').title()} -> Payoffs: {payoffs}", "GAME")
                        
                        # Update statistics
                        total_interactions += 1
                        game_type_stats[game_type] = game_type_stats.get(game_type, 0) + 1
                        
                        # Count cooperation (simplified)
                        choices = interaction['choices']
                        cooperative_choices = ['cooperate', 'trust', 'share_info', 'share_fairly', 'comply']
                        if choices[0] in cooperative_choices:
                            total_cooperation += 1
                        if choices[1] in cooperative_choices:
                            total_cooperation += 1
                        
                        # Update social network and emotions
                        if agent1_id != 999 and agent2_id != 999:  # Skip dummy guard
                            outcome = "mutual_cooperation" if payoffs[0] > 2 and payoffs[1] > 2 else "conflict"
                            social_network.update_relationship(agent1_id, agent2_id, outcome, payoffs)
                            
                            # Update emotions
                            if agent1_id in agent_emotions:
                                relationship = "neutral"  # Simplified for demo
                                agent_emotions[agent1_id] = emotional_engine.update_emotions_from_interaction(
                                    agent_emotions[agent1_id], choices[0], choices[1], payoffs[0], relationship)
                        
                        # Store conversation
                        conversation_log.append({
                            'time': current_time.strftime('%H:%M'),
                            'location': location.value,
                            'participants': interaction['participant_names'],
                            'conversation': conv,
                            'game_type': game_type,
                            'payoffs': payoffs
                        })
        
        # Advance time by 30 minutes
        current_time += timedelta(minutes=30)
        time.sleep(0.3)  # Brief pause for readability
    
    # Enhanced end of day summary
    log("🌙 Enhanced Day 1 Complete - Lights Out", "SUCCESS")
    
    cooperation_rate = total_cooperation / max(total_interactions * 2, 1)
    
    print("\n" + "="*70)
    log("📊 ENHANCED DAILY SUMMARY", "SUCCESS")
    print("="*70)
    
    log(f"Total Enhanced Interactions: {total_interactions}", "INFO")
    log(f"Cooperation Rate: {cooperation_rate:.1%}", "SUCCESS")
    
    # Game type breakdown
    log("🎮 Game Type Distribution:", "GAME")
    for game_type, count in game_type_stats.items():
        percentage = (count / total_interactions) * 100 if total_interactions > 0 else 0
        log(f"   {game_type.replace('_', ' ').title()}: {count} ({percentage:.1f}%)", "GAME")
    
    # Agent emotional status
    log("🧠 Agent Emotional Status:", "INFO")
    for agent in agents:
        if agent.id in agent_emotions:
            emotion = agent_emotions[agent.id]
            wellbeing = emotion.get_overall_wellbeing()
            privilege_count = sum(emotion.privileges.values())
            log(f"   {agent.name}: {emotion.current_emotion.value}, wellbeing: {wellbeing:.2f}, privileges: {privilege_count}/7", "INFO")
    
    # Conversation highlights
    log("💬 Notable Conversations:", "CONVERSATION")
    interesting_conversations = [c for c in conversation_log if c['payoffs'][0] != c['payoffs'][1]][:3]
    for conv in interesting_conversations:
        log(f"   {conv['time']} in {conv['location']}: {conv['participants'][0]} vs {conv['participants'][1]}", "CONVERSATION")
        log(f"     Game: {conv['game_type']}, Payoffs: {conv['payoffs']}", "CONVERSATION")
    
    # Social network status
    network_stats = social_network.get_network_stats()
    log(f"🤝 Social Network: {network_stats['positive_relationships']}/{network_stats['total_relationships']} positive relationships", "INFO")
    
    log("✅ Enhanced simulation complete!", "SUCCESS")
    
    return agents, social_network, agent_emotions, cooperation_rate, conversation_log

if __name__ == "__main__":
    try:
        agents, network, emotions, coop_rate, conversations = run_enhanced_simulation()
        print(f"\n🎉 ENHANCED SIMULATION SUCCESS!")
        print(f"Daily cooperation rate: {coop_rate:.1%}")
        print(f"Total conversations: {len(conversations)}")
        print("🎭 Rich conversational interactions with expanded game theory!")
    except KeyboardInterrupt:
        print("\n⏹️  Simulation stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()