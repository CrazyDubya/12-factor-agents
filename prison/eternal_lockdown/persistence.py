"""
Simple Auto-Save/Load System for Eternal Lockdown
Handles simulation state persistence with JSON format
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

class SimulationPersistence:
    """Simple persistence system for simulation state"""
    
    def __init__(self, save_dir: str = "saves"):
        self.save_dir = save_dir
        self.latest_file = os.path.join(save_dir, "latest.json")
        self.ensure_save_directory()
    
    def ensure_save_directory(self):
        """Create save directory if it doesn't exist"""
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
    
    def auto_save(self, agents: List, social_network, game_stats: Dict, metadata: Dict) -> str:
        """Auto-save simulation state"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Prepare save data
        save_data = {
            "timestamp": timestamp,
            "metadata": metadata,
            "game_statistics": game_stats,
            "agents": [self._serialize_agent(agent) for agent in agents],
            "social_network": self._serialize_social_network(social_network)
        }
        
        # Save timestamped file
        timestamped_file = os.path.join(self.save_dir, f"simulation_{timestamp}.json")
        with open(timestamped_file, 'w') as f:
            json.dump(save_data, f, indent=2, default=str)
        
        # Update latest file
        with open(self.latest_file, 'w') as f:
            json.dump(save_data, f, indent=2, default=str)
        
        print(f"💾 Auto-saved: {timestamped_file}")
        return timestamp
    
    def auto_load(self) -> Optional[Dict]:
        """Auto-load latest simulation state"""
        if not os.path.exists(self.latest_file):
            print("📂 No previous save found - starting fresh")
            return None
        
        try:
            with open(self.latest_file, 'r') as f:
                data = json.load(f)
            print(f"📂 Auto-loaded save from: {data.get('timestamp', 'unknown')}")
            return data
        except Exception as e:
            print(f"❌ Failed to load save: {e}")
            return None
    
    def _serialize_agent(self, agent) -> Dict:
        """Convert agent to serializable format"""
        return {
            "id": agent.id,
            "name": agent.name,
            "agent_type": agent.agent_type.value,
            "personality": agent.personality.value,
            "intelligence": agent.intelligence.value,
            "cooperation_tendency": agent.cooperation_tendency,
            "reputation_score": agent.reputation_score,
            "ollama_model": agent.ollama_model,
            "gang_affiliation": getattr(agent, 'gang_affiliation', None),
            "crime": getattr(agent, 'crime', None),
            "sentence_days": getattr(agent, 'sentence_days', None),
            "time_served": getattr(agent, 'time_served', 0),
            "rank": getattr(agent, 'rank', None),
            "years_experience": getattr(agent, 'years_experience', None)
        }
    
    def _serialize_social_network(self, network) -> Dict:
        """Convert social network to serializable format"""
        return {
            "relationships": {f"{k[0]}-{k[1]}": v for k, v in network.relationships.items()},
            "gangs": {name: list(members) for name, members in network.gangs.items()},
            "alliances": {str(k): list(v) for k, v in network.alliances.items()},
            "enemies": {str(k): list(v) for k, v in network.enemies.items()},
            "influence_scores": {str(k): v for k, v in network.influence_scores.items()}
        }
    
    def list_saves(self) -> List[str]:
        """List all available save files"""
        saves = []
        for file in os.listdir(self.save_dir):
            if file.startswith("simulation_") and file.endswith(".json"):
                saves.append(file)
        return sorted(saves, reverse=True)  # Most recent first