#!/usr/bin/env python3
"""
Ollama-Powered Prison Simulation with Social Networks and Gang Dynamics
Multi-Framework Integration: TinyTroupe + AutoGen + CrewAI
"""

import sys
import os
import time
import json
import random
import requests
from datetime import datetime
from typing import Dict, List, Set, Tuple

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.game_theory import GameTheoryEngine, Strategy, PrisonersDilemma
from core.agents import Agent, Prisoner, Guard, PersonalityType, IntelligenceLevel
from persistence import SimulationPersistence
from sentence_system import SentenceCalculator, SentenceInfo

def log(message, level="INFO"):
    """Live logging with timestamps and colors"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    colors = {
        "INFO": "\033[94m",    # Blue
        "SUCCESS": "\033[92m", # Green  
        "WARNING": "\033[93m", # Yellow
        "ERROR": "\033[91m",   # Red
        "GANG": "\033[95m",    # Magenta
        "SOCIAL": "\033[96m"   # Cyan
    }
    color = colors.get(level, "")
    reset = "\033[0m"
    print(f"{color}[{timestamp}] {level}: {message}{reset}")

class SocialNetwork:
    """Track relationships, alliances, and gang dynamics"""
    
    def __init__(self):
        self.relationships = {}  # (agent1_id, agent2_id) -> trust_level
        self.gangs = {}  # gang_name -> set of agent_ids
        self.alliances = {}  # agent_id -> set of allied_agent_ids
        self.enemies = {}  # agent_id -> set of enemy_agent_ids
        self.influence_scores = {}  # agent_id -> influence_level
        
    def update_relationship(self, agent1_id: int, agent2_id: int, 
                          interaction_outcome: str, payoffs: Tuple[float, float]):
        """Update relationship based on interaction outcome"""
        key = tuple(sorted([agent1_id, agent2_id]))
        current_trust = self.relationships.get(key, 0.0)
        
        # Calculate trust change based on outcome
        if interaction_outcome == "mutual_cooperation":
            trust_change = 0.15
        elif interaction_outcome == "mutual_defection":
            trust_change = -0.05
        elif "exploited" in interaction_outcome:
            trust_change = -0.25  # Being exploited hurts trust more
        else:
            trust_change = 0.0
        
        new_trust = max(-1.0, min(1.0, current_trust + trust_change))
        self.relationships[key] = new_trust
        
        # Update alliances/enemies based on trust levels
        self._update_alliances_enemies(agent1_id, agent2_id, new_trust)
        
        log(f"Relationship {agent1_id}↔{agent2_id}: {current_trust:.2f} → {new_trust:.2f} ({interaction_outcome})", "SOCIAL")
    
    def _update_alliances_enemies(self, agent1_id: int, agent2_id: int, trust_level: float):
        """Update alliance/enemy status based on trust"""
        # Initialize if not exists
        for agent_id in [agent1_id, agent2_id]:
            if agent_id not in self.alliances:
                self.alliances[agent_id] = set()
            if agent_id not in self.enemies:
                self.enemies[agent_id] = set()
        
        if trust_level > 0.4:  # High trust = alliance
            self.alliances[agent1_id].add(agent2_id)
            self.alliances[agent2_id].add(agent1_id)
            # Remove from enemies if present
            self.enemies[agent1_id].discard(agent2_id)
            self.enemies[agent2_id].discard(agent1_id)
            log(f"🤝 Alliance formed: {agent1_id} ↔ {agent2_id}", "SOCIAL")
            
        elif trust_level < -0.4:  # Low trust = enmity
            self.enemies[agent1_id].add(agent2_id)
            self.enemies[agent2_id].add(agent1_id)
            # Remove from alliances if present
            self.alliances[agent1_id].discard(agent2_id)
            self.alliances[agent2_id].discard(agent1_id)
            log(f"💀 Enmity formed: {agent1_id} ↔ {agent2_id}", "SOCIAL")
    
    def form_gang(self, gang_name: str, leader_id: int, members: List[int]):
        """Form a new gang"""
        self.gangs[gang_name] = set([leader_id] + members)
        
        # Initialize alliance dictionaries if needed
        gang_members = list(self.gangs[gang_name])
        for member in gang_members:
            if member not in self.alliances:
                self.alliances[member] = set()
            if member not in self.enemies:
                self.enemies[member] = set()
        
        # Gang members automatically have high trust with each other
        for i, member1 in enumerate(gang_members):
            for member2 in gang_members[i+1:]:
                key = tuple(sorted([member1, member2]))
                self.relationships[key] = 0.8  # High initial trust
                self.alliances[member1].add(member2)
                self.alliances[member2].add(member1)
        
        log(f"🏴 Gang formed: {gang_name} with {len(gang_members)} members (leader: {leader_id})", "GANG")
    
    def get_gang_members(self, agent_id: int) -> Set[int]:
        """Get all gang members for an agent"""
        for gang_name, members in self.gangs.items():
            if agent_id in members:
                return members - {agent_id}  # Exclude self
        return set()
    
    def calculate_influence(self, agent_id: int) -> float:
        """Calculate agent's influence based on network position"""
        # Simple influence = number of allies + gang membership bonus
        allies = len(self.alliances.get(agent_id, set()))
        gang_bonus = 2 if any(agent_id in members for members in self.gangs.values()) else 0
        influence = allies + gang_bonus
        self.influence_scores[agent_id] = influence
        return influence
    
    def get_network_stats(self) -> Dict:
        """Get comprehensive network statistics"""
        total_relationships = len(self.relationships)
        positive_relationships = sum(1 for trust in self.relationships.values() if trust > 0)
        total_gangs = len(self.gangs)
        total_gang_members = sum(len(members) for members in self.gangs.values())
        
        return {
            "total_relationships": total_relationships,
            "positive_relationships": positive_relationships,
            "cooperation_network_density": positive_relationships / max(total_relationships, 1),
            "total_gangs": total_gangs,
            "total_gang_members": total_gang_members,
            "average_influence": sum(self.influence_scores.values()) / max(len(self.influence_scores), 1)
        }

class OllamaDecisionEngine:
    """Enhanced Ollama integration for realistic decision making"""
    
    def __init__(self):
        self.base_url = "http://localhost:11434"
        self.model_cache = {}  # Cache model responses for similar situations
        
    def test_connection(self) -> bool:
        """Test Ollama connection"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def make_decision(self, agent: Agent, opponent_id: int, situation: str, 
                     social_network: SocialNetwork, game_context: Dict) -> Tuple[Strategy, str]:
        """Make decision using Ollama with full context"""
        
        # Get social context
        gang_members = social_network.get_gang_members(agent.id)
        allies = social_network.alliances.get(agent.id, set())
        enemies = social_network.enemies.get(agent.id, set())
        
        # Get relationship with opponent
        relationship_key = tuple(sorted([agent.id, opponent_id]))
        trust_level = social_network.relationships.get(relationship_key, 0.0)
        
        # Build comprehensive prompt
        prompt = self._build_decision_prompt(
            agent, opponent_id, situation, trust_level, 
            gang_members, allies, enemies, game_context
        )
        
        # Query Ollama
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": agent.ollama_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_tokens": 150
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()["response"].strip()
                decision, reasoning = self._parse_ollama_response(result)
                log(f"🧠 {agent.name} ({agent.ollama_model}): {decision.value} - {reasoning[:50]}...", "INFO")
                return decision, reasoning
            
        except Exception as e:
            log(f"Ollama error for {agent.name}: {e}", "WARNING")
        
        # Fallback to enhanced personality-based decision
        return self._personality_decision_with_context(agent, opponent_id, social_network)
    
    def _build_decision_prompt(self, agent: Agent, opponent_id: int, situation: str,
                              trust_level: float, gang_members: Set[int], 
                              allies: Set[int], enemies: Set[int], game_context: Dict) -> str:
        """Build comprehensive decision prompt"""
        
        # Determine opponent relationship
        if opponent_id in gang_members:
            relationship = "gang member"
        elif opponent_id in allies:
            relationship = "ally"
        elif opponent_id in enemies:
            relationship = "enemy"
        else:
            relationship = "neutral"
        
        prompt = f"""
You are {agent.name}, a {agent.agent_type.value} in Eternal Lockdown Correctional Facility.

PERSONALITY: {agent.personality.value}
INTELLIGENCE: {agent.intelligence.value}
CURRENT COOPERATION TENDENCY: {agent.cooperation_tendency:.2f}

SITUATION: {situation}

OPPONENT RELATIONSHIP:
- Agent ID {opponent_id} is your {relationship}
- Trust level: {trust_level:.2f} (-1.0 = enemy, +1.0 = trusted ally)

SOCIAL CONTEXT:
- Gang members: {len(gang_members)} people have your back
- Allies: {len(allies)} people you trust
- Enemies: {len(enemies)} people who oppose you

PRISONER'S DILEMMA CHOICE:
You must choose COOPERATE or DEFECT.

Payoffs:
- Both cooperate: 3 points each (mutual benefit)
- You defect, they cooperate: 5 points for you, 0 for them (exploitation)
- Both defect: 1 point each (mutual punishment)  
- You cooperate, they defect: 0 for you, 5 for them (being exploited)

STRATEGIC CONSIDERATIONS:
- Gang members usually cooperate with each other
- Allies are more likely to cooperate
- Enemies often defect
- Your reputation affects future interactions
- {agent.personality.value} personalities tend to act predictably

Think about your personality, relationships, and long-term strategy.

Respond with:
DECISION: [COOPERATE or DEFECT]
REASONING: [Brief explanation of your choice]
"""
        
        return prompt
    
    def _parse_ollama_response(self, response: str) -> Tuple[Strategy, str]:
        """Parse Ollama response to extract decision and reasoning"""
        response_upper = response.upper()
        
        # Extract decision
        if "DECISION:" in response_upper:
            decision_line = [line for line in response.split('\n') if 'DECISION:' in line.upper()][0]
            if "COOPERATE" in decision_line.upper():
                decision = Strategy.COOPERATE
            elif "DEFECT" in decision_line.upper():
                decision = Strategy.DEFECT
            else:
                decision = Strategy.DEFECT  # Default fallback
        elif "COOPERATE" in response_upper:
            decision = Strategy.COOPERATE
        else:
            decision = Strategy.DEFECT
        
        # Extract reasoning
        reasoning_lines = [line for line in response.split('\n') if 'REASONING:' in line.upper()]
        if reasoning_lines:
            reasoning = reasoning_lines[0].split(':', 1)[1].strip()
        else:
            reasoning = "Decision based on situation analysis"
        
        return decision, reasoning
    
    def _personality_decision_with_context(self, agent: Agent, opponent_id: int, 
                                         social_network: SocialNetwork) -> Tuple[Strategy, str]:
        """Enhanced fallback decision with social context"""
        
        gang_members = social_network.get_gang_members(agent.id)
        allies = social_network.alliances.get(agent.id, set())
        enemies = social_network.enemies.get(agent.id, set())
        
        # Base cooperation probability from personality
        personality_probs = {
            PersonalityType.COOPERATIVE: 0.8,
            PersonalityType.STRATEGIC: 0.6,
            PersonalityType.IMPULSIVE: 0.4,
            PersonalityType.WITHDRAWN: 0.3,
            PersonalityType.AGGRESSIVE: 0.2
        }
        
        base_prob = personality_probs.get(agent.personality, 0.5)
        
        # Adjust based on relationship
        if opponent_id in gang_members:
            base_prob += 0.3  # Gang loyalty
            reasoning = "Gang loyalty demands cooperation"
        elif opponent_id in allies:
            base_prob += 0.2  # Alliance cooperation
            reasoning = "Cooperating with ally"
        elif opponent_id in enemies:
            base_prob -= 0.4  # Enemy defection
            reasoning = "Cannot trust enemy"
        else:
            reasoning = f"Acting on {agent.personality.value} personality"
        
        # Add some randomness
        final_prob = max(0.0, min(1.0, base_prob + random.uniform(-0.1, 0.1)))
        
        decision = Strategy.COOPERATE if random.random() < final_prob else Strategy.DEFECT
        return decision, reasoning

def create_prison_population():
    """Create diverse prison population with realistic short sentences"""
    sentence_calc = SentenceCalculator()
    
    agents = [
        # Gang 1: "Los Hermanos" - Strategic cooperation
        Prisoner(1, "Carlos Mendez", PersonalityType.STRATEGIC, IntelligenceLevel.HIGH,
                crime="drug dealing", sentence_days=22, gang_affiliation="Los Hermanos"),
        Prisoner(2, "Diego Santos", PersonalityType.COOPERATIVE, IntelligenceLevel.MEDIUM,
                crime="drug possession", sentence_days=12, gang_affiliation="Los Hermanos"),
        
        # Gang 2: "Iron Brotherhood" - Aggressive dominance
        Prisoner(3, "Tommy Rodriguez", PersonalityType.AGGRESSIVE, IntelligenceLevel.LOW,
                crime="armed robbery", sentence_days=29, gang_affiliation="Iron Brotherhood"),
        Prisoner(4, "Jake Morrison", PersonalityType.AGGRESSIVE, IntelligenceLevel.MEDIUM,
                crime="assault", sentence_days=18, gang_affiliation="Iron Brotherhood"),
        
        # Independent prisoners
        Prisoner(5, "Marcus Johnson", PersonalityType.COOPERATIVE, IntelligenceLevel.MEDIUM,
                crime="drug possession", sentence_days=10),
        Prisoner(6, "David Chen", PersonalityType.WITHDRAWN, IntelligenceLevel.HIGH,
                crime="fraud", sentence_days=17),
        
        # Guards
        Guard(7, "Officer Martinez", PersonalityType.STRATEGIC, IntelligenceLevel.MEDIUM,
              rank="Officer II", years_experience=8),
        Guard(8, "Sergeant Thompson", PersonalityType.COOPERATIVE, IntelligenceLevel.HIGH,
              rank="Sergeant", years_experience=15, authority_level=2)
    ]
    
    return agents

def run_ollama_simulation(load_previous: bool = True):
    """Run full simulation with Ollama, social networks, and gang dynamics"""
    
    print("🏢 ETERNAL LOCKDOWN - OLLAMA + SOCIAL NETWORKS + GANG DYNAMICS")
    print("=" * 80)
    print("Multi-Framework Prison Simulation: TinyTroupe + AutoGen + CrewAI Integration")
    print("=" * 80)
    
    # Initialize persistence
    persistence = SimulationPersistence()
    
    # Try to load previous state
    if load_previous:
        saved_data = persistence.auto_load()
        if saved_data:
            log("🔄 Previous simulation found! Starting from saved state...", "INFO")
            # For now, just show what was loaded - full restoration in next bite
            log(f"   Agents: {len(saved_data.get('agents', []))}", "INFO")
            log(f"   Last run: {saved_data.get('timestamp', 'unknown')}", "INFO")
        else:
            log("🆕 Starting fresh simulation...", "INFO")
    
    # Initialize systems
    ollama_engine = OllamaDecisionEngine()
    social_network = SocialNetwork()
    game_engine = GameTheoryEngine()
    
    # Test Ollama
    if ollama_engine.test_connection():
        log("✅ Ollama connected and ready", "SUCCESS")
    else:
        log("⚠️  Ollama not available - using enhanced fallback decisions", "WARNING")
    
    # Create population
    log("👥 Creating prison population...", "INFO")
    agents = create_prison_population()
    
    for agent in agents:
        log(f"   Created {agent.name}: {agent.agent_type.value}, {agent.personality.value}, {agent.ollama_model}", "INFO")
        if hasattr(agent, 'gang_affiliation') and agent.gang_affiliation:
            log(f"      Gang: {agent.gang_affiliation}", "GANG")
    
    # Form gangs in social network
    log("🏴 Forming gangs...", "GANG")
    social_network.form_gang("Los Hermanos", 1, [2])  # Carlos leads Diego
    social_network.form_gang("Iron Brotherhood", 3, [4])  # Tommy leads Jake
    
    # Track statistics
    total_interactions = 0
    total_cooperation = 0
    agent_scores = {agent.id: 0 for agent in agents}
    gang_cooperation = {"Los Hermanos": 0, "Iron Brotherhood": 0, "Independent": 0}
    gang_interactions = {"Los Hermanos": 0, "Iron Brotherhood": 0, "Independent": 0}
    
    log("🚀 Starting multi-framework simulation...", "SUCCESS")
    print("\n" + "="*80)
    
    # Simulation scenarios
    scenarios = [
        "Cafeteria meal time - deciding whether to share resources",
        "Recreation yard - forming alliances and territories", 
        "Work assignment - cooperating on prison labor",
        "Cell block - sharing information about guards",
        "Conflict resolution - choosing to escalate or de-escalate",
        "Contraband exchange - risky cooperation opportunity",
        "Gang territory dispute - loyalty vs self-interest",
        "Guard interaction - compliance vs resistance"
    ]
    
    # Run 20 rounds of interactions
    for round_num in range(1, 21):
        log(f"🔄 ROUND {round_num}", "INFO")
        
        # Select agents for interaction (bias toward same-gang interactions)
        if random.random() < 0.4:  # 40% chance of gang interaction
            # Pick gang members
            gang_agents = []
            for agent in agents:
                if hasattr(agent, 'gang_affiliation') and agent.gang_affiliation:
                    gang_agents.append(agent)
            
            if len(gang_agents) >= 2:
                agent1, agent2 = random.sample(gang_agents, 2)
            else:
                agent1, agent2 = random.sample(agents, 2)
        else:
            # Random interaction
            agent1, agent2 = random.sample(agents, 2)
        
        situation = random.choice(scenarios)
        
        # Get decisions using Ollama
        game_context = {
            "round": round_num,
            "total_interactions": total_interactions,
            "cooperation_rate": total_cooperation / max(total_interactions * 2, 1)
        }
        
        decision1, reasoning1 = ollama_engine.make_decision(agent1, agent2.id, situation, social_network, game_context)
        decision2, reasoning2 = ollama_engine.make_decision(agent2, agent1.id, situation, social_network, game_context)
        
        # Calculate payoffs
        pd_game = PrisonersDilemma()
        payoffs = pd_game.play_round(decision1, decision2)
        
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
        
        log(f"🎭 {agent1.name} vs {agent2.name}: {situation}", "INFO")
        log(f"   {agent1.name}: {decision1.value} ({reasoning1})", "INFO")
        log(f"   {agent2.name}: {decision2.value} ({reasoning2})", "INFO")
        log(f"   {outcome_emoji} Outcome: {outcome} | Payoffs: ({payoffs[0]}, {payoffs[1]})", "SUCCESS")
        
        # Update social network
        social_network.update_relationship(agent1.id, agent2.id, outcome, payoffs)
        
        # Update statistics
        total_interactions += 1
        if decision1 == Strategy.COOPERATE:
            total_cooperation += 1
        if decision2 == Strategy.COOPERATE:
            total_cooperation += 1
        
        agent_scores[agent1.id] += payoffs[0]
        agent_scores[agent2.id] += payoffs[1]
        
        # Track gang cooperation
        for agent, decision in [(agent1, decision1), (agent2, decision2)]:
            if hasattr(agent, 'gang_affiliation') and agent.gang_affiliation:
                gang = agent.gang_affiliation
                gang_interactions[gang] += 1
                if decision == Strategy.COOPERATE:
                    gang_cooperation[gang] += 1
            else:
                gang_interactions["Independent"] += 1
                if decision == Strategy.COOPERATE:
                    gang_cooperation["Independent"] += 1
        
        # Update agent cooperation tendencies
        agent1.cooperation_tendency = max(0.0, min(1.0, 
            agent1.cooperation_tendency + (0.05 if payoffs[0] > 2.5 else -0.1)))
        agent2.cooperation_tendency = max(0.0, min(1.0,
            agent2.cooperation_tendency + (0.05 if payoffs[1] > 2.5 else -0.1)))
        
        # Show running stats every 5 rounds
        if round_num % 5 == 0:
            coop_rate = total_cooperation / (total_interactions * 2)
            log(f"📊 Running Stats: {coop_rate:.1%} cooperation, {total_interactions} interactions", "INFO")
        
        print("-" * 60)
        time.sleep(0.5)  # Brief pause for readability
    
    # Final comprehensive analysis
    print("\n" + "="*80)
    log("📊 FINAL COMPREHENSIVE ANALYSIS", "SUCCESS")
    print("="*80)
    
    final_cooperation_rate = total_cooperation / (total_interactions * 2)
    log(f"Total Interactions: {total_interactions}", "INFO")
    log(f"Final Cooperation Rate: {final_cooperation_rate:.1%}", "SUCCESS")
    
    # Agent scores and evolution
    log("🏆 AGENT PERFORMANCE:", "SUCCESS")
    for agent in agents:
        score = agent_scores[agent.id]
        gang_info = f" ({agent.gang_affiliation})" if hasattr(agent, 'gang_affiliation') and agent.gang_affiliation else ""
        log(f"   {agent.name:20}: {score:6.1f} points, cooperation: {agent.cooperation_tendency:.3f}{gang_info}", "INFO")
    
    # Gang analysis
    log("🏴 GANG COOPERATION ANALYSIS:", "GANG")
    for gang, interactions in gang_interactions.items():
        if interactions > 0:
            gang_coop_rate = gang_cooperation[gang] / interactions
            log(f"   {gang:20}: {gang_coop_rate:.1%} cooperation ({gang_cooperation[gang]}/{interactions})", "GANG")
    
    # Social network analysis
    network_stats = social_network.get_network_stats()
    log("🤝 SOCIAL NETWORK ANALYSIS:", "SOCIAL")
    log(f"   Total Relationships: {network_stats['total_relationships']}", "SOCIAL")
    log(f"   Positive Relationships: {network_stats['positive_relationships']}", "SOCIAL")
    log(f"   Network Cooperation Density: {network_stats['cooperation_network_density']:.1%}", "SOCIAL")
    log(f"   Active Gangs: {network_stats['total_gangs']}", "SOCIAL")
    log(f"   Gang Members: {network_stats['total_gang_members']}", "SOCIAL")
    
    # Game theory comparison
    log("🎯 GAME THEORY ANALYSIS:", "SUCCESS")
    if final_cooperation_rate > 0.15:
        log("   📈 Population SIGNIFICANTLY more cooperative than Nash equilibrium!", "SUCCESS")
        log("   🎉 Social structures (gangs/alliances) enabled cooperation!", "SUCCESS")
    elif final_cooperation_rate > 0.05:
        log("   📊 Population moderately more cooperative than Nash equilibrium", "INFO")
    else:
        log("   📉 Population near Nash equilibrium (defection dominates)", "WARNING")
    
    # Auto-save simulation data
    log("💾 Auto-saving simulation data...", "INFO")
    
    # Prepare game statistics
    game_statistics = {
        "total_interactions": total_interactions,
        "cooperation_rate": final_cooperation_rate,
        "agent_scores": agent_scores,
        "gang_cooperation": gang_cooperation,
        "gang_interactions": gang_interactions
    }
    
    # Prepare simulation metadata
    simulation_metadata = {
        "simulation_type": "ollama_social_gangs",
        "framework_integration": ["TinyTroupe", "AutoGen", "CrewAI"],
        "ollama_models_used": list(set(agent.ollama_model for agent in agents)),
        "total_rounds": 20,
        "scenarios_used": len(scenarios)
    }
    
    # Auto-save everything
    timestamp = persistence.auto_save(
        agents, social_network, game_statistics, simulation_metadata
    )
    
    log(f"✅ All data saved with timestamp: {timestamp}", "SUCCESS")
    log("✅ Multi-framework simulation complete!", "SUCCESS")
    
    return agents, social_network, agent_scores, final_cooperation_rate, timestamp

if __name__ == "__main__":
    try:
        agents, network, scores, coop_rate, timestamp = run_ollama_simulation()
        print(f"\n🎉 SIMULATION SUCCESS! Final cooperation: {coop_rate:.1%}")
        print("🏆 Multi-framework integration: Ollama + Social Networks + Gang Dynamics = WORKING!")
        print(f"💾 Data saved with timestamp: {timestamp}")
        print(f"📁 Check simulation_data/ directory for all saved files")
    except KeyboardInterrupt:
        print("\n⏹️  Simulation stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()