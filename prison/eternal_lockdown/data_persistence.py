"""
Data Persistence System for Eternal Lockdown
Saves all simulation data: agents, interactions, social networks, gang dynamics
"""

import json
import sqlite3
import csv
import yaml
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List, Any
import os

class DataPersistence:
    """Comprehensive data persistence system"""
    
    def __init__(self, base_path: str = "simulation_data"):
        self.base_path = base_path
        self.ensure_directories()
        
    def ensure_directories(self):
        """Create all necessary directories"""
        directories = [
            self.base_path,
            f"{self.base_path}/json",
            f"{self.base_path}/yaml", 
            f"{self.base_path}/xml",
            f"{self.base_path}/csv",
            f"{self.base_path}/sqlite"
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def save_simulation_state(self, agents: List, social_network, game_stats: Dict, 
                            simulation_metadata: Dict):
        """Save complete simulation state in multiple formats"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print(f"💾 Saving simulation data (timestamp: {timestamp})...")
        
        # 1. JSON: Agent states and detailed data
        self._save_json_data(agents, social_network, game_stats, timestamp)
        
        # 2. YAML: Human-readable configuration and summary
        self._save_yaml_data(agents, social_network, game_stats, simulation_metadata, timestamp)
        
        # 3. XML: Structured event logs
        self._save_xml_logs(agents, social_network, timestamp)
        
        # 4. CSV: Tabular data for analysis
        self._save_csv_data(agents, social_network, game_stats, timestamp)
        
        # 5. SQLite: Queryable database
        self._save_sqlite_data(agents, social_network, game_stats, timestamp)
        
        print(f"✅ All data saved successfully to {self.base_path}/")
        return timestamp
    
    def _save_json_data(self, agents: List, social_network, game_stats: Dict, timestamp: str):
        """Save detailed JSON data"""
        
        # Agent states
        agent_data = []
        for agent in agents:
            agent_dict = {
                "id": agent.id,
                "name": agent.name,
                "type": agent.agent_type.value,
                "personality": agent.personality.value,
                "intelligence": agent.intelligence.value,
                "cooperation_tendency": agent.cooperation_tendency,
                "ollama_model": agent.ollama_model,
                "interaction_history": getattr(agent, 'interaction_history', [])
            }
            
            # Add type-specific data
            if hasattr(agent, 'crime'):
                agent_dict.update({
                    "crime": agent.crime,
                    "sentence_days": agent.sentence_days,
                    "gang_affiliation": getattr(agent, 'gang_affiliation', None)
                })
            elif hasattr(agent, 'rank'):
                agent_dict.update({
                    "rank": agent.rank,
                    "years_experience": agent.years_experience,
                    "authority_level": agent.authority_level
                })
            
            agent_data.append(agent_dict)
        
        # Social network data
        network_data = {
            "relationships": {f"{k[0]}-{k[1]}": v for k, v in social_network.relationships.items()},
            "gangs": {name: list(members) for name, members in social_network.gangs.items()},
            "alliances": {str(k): list(v) for k, v in social_network.alliances.items()},
            "enemies": {str(k): list(v) for k, v in social_network.enemies.items()},
            "influence_scores": social_network.influence_scores
        }
        
        # Complete simulation state
        simulation_data = {
            "timestamp": timestamp,
            "agents": agent_data,
            "social_network": network_data,
            "game_statistics": game_stats,
            "metadata": {
                "total_agents": len(agents),
                "total_gangs": len(social_network.gangs),
                "simulation_version": "1.0"
            }
        }
        
        # Save to JSON file
        json_path = f"{self.base_path}/json/simulation_{timestamp}.json"
        with open(json_path, 'w') as f:
            json.dump(simulation_data, f, indent=2, default=str)
        
        print(f"   📄 JSON data saved: {json_path}")
    
    def _save_yaml_data(self, agents: List, social_network, game_stats: Dict, 
                       metadata: Dict, timestamp: str):
        """Save human-readable YAML configuration"""
        
        # Summary statistics
        summary = {
            "simulation_summary": {
                "timestamp": timestamp,
                "total_agents": len(agents),
                "cooperation_rate": game_stats.get("cooperation_rate", 0),
                "total_interactions": game_stats.get("total_interactions", 0),
                "gangs": {
                    name: {
                        "members": list(members),
                        "size": len(members)
                    } for name, members in social_network.gangs.items()
                }
            },
            "agent_summary": [
                {
                    "name": agent.name,
                    "type": agent.agent_type.value,
                    "personality": agent.personality.value,
                    "cooperation_tendency": round(agent.cooperation_tendency, 3),
                    "gang": getattr(agent, 'gang_affiliation', None)
                } for agent in agents
            ],
            "network_statistics": social_network.get_network_stats()
        }
        
        yaml_path = f"{self.base_path}/yaml/simulation_summary_{timestamp}.yaml"
        with open(yaml_path, 'w') as f:
            yaml.dump(summary, f, default_flow_style=False, indent=2)
        
        print(f"   📋 YAML summary saved: {yaml_path}")
    
    def _save_xml_logs(self, agents: List, social_network, timestamp: str):
        """Save structured XML event logs"""
        
        root = ET.Element("simulation_log")
        root.set("timestamp", timestamp)
        
        # Simulation metadata
        metadata = ET.SubElement(root, "metadata")
        ET.SubElement(metadata, "total_agents").text = str(len(agents))
        ET.SubElement(metadata, "total_gangs").text = str(len(social_network.gangs))
        
        # Agents section
        agents_elem = ET.SubElement(root, "agents")
        for agent in agents:
            agent_elem = ET.SubElement(agents_elem, "agent")
            agent_elem.set("id", str(agent.id))
            agent_elem.set("name", agent.name)
            agent_elem.set("type", agent.agent_type.value)
            
            ET.SubElement(agent_elem, "personality").text = agent.personality.value
            ET.SubElement(agent_elem, "intelligence").text = agent.intelligence.value
            ET.SubElement(agent_elem, "cooperation_tendency").text = str(agent.cooperation_tendency)
            
            if hasattr(agent, 'gang_affiliation') and agent.gang_affiliation:
                ET.SubElement(agent_elem, "gang").text = agent.gang_affiliation
        
        # Gangs section
        gangs_elem = ET.SubElement(root, "gangs")
        for gang_name, members in social_network.gangs.items():
            gang_elem = ET.SubElement(gangs_elem, "gang")
            gang_elem.set("name", gang_name)
            gang_elem.set("size", str(len(members)))
            
            for member_id in members:
                member_elem = ET.SubElement(gang_elem, "member")
                member_elem.set("id", str(member_id))
        
        # Relationships section
        relationships_elem = ET.SubElement(root, "relationships")
        for (agent1, agent2), trust in social_network.relationships.items():
            rel_elem = ET.SubElement(relationships_elem, "relationship")
            rel_elem.set("agent1", str(agent1))
            rel_elem.set("agent2", str(agent2))
            rel_elem.set("trust_level", str(trust))
        
        # Save XML
        tree = ET.ElementTree(root)
        xml_path = f"{self.base_path}/xml/simulation_log_{timestamp}.xml"
        tree.write(xml_path, encoding='utf-8', xml_declaration=True)
        
        print(f"   🗂️  XML log saved: {xml_path}")
    
    def _save_csv_data(self, agents: List, social_network, game_stats: Dict, timestamp: str):
        """Save CSV data for analysis"""
        
        # Agents CSV
        agents_csv_path = f"{self.base_path}/csv/agents_{timestamp}.csv"
        with open(agents_csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'id', 'name', 'type', 'personality', 'intelligence', 
                'cooperation_tendency', 'ollama_model', 'gang_affiliation',
                'crime', 'sentence_days', 'rank', 'years_experience'
            ])
            
            for agent in agents:
                row = [
                    agent.id, agent.name, agent.agent_type.value, 
                    agent.personality.value, agent.intelligence.value,
                    agent.cooperation_tendency, agent.ollama_model,
                    getattr(agent, 'gang_affiliation', ''),
                    getattr(agent, 'crime', ''),
                    getattr(agent, 'sentence_days', ''),
                    getattr(agent, 'rank', ''),
                    getattr(agent, 'years_experience', '')
                ]
                writer.writerow(row)
        
        # Relationships CSV
        relationships_csv_path = f"{self.base_path}/csv/relationships_{timestamp}.csv"
        with open(relationships_csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['agent1_id', 'agent2_id', 'trust_level', 'relationship_type'])
            
            for (agent1, agent2), trust in social_network.relationships.items():
                if trust > 0.4:
                    rel_type = "alliance"
                elif trust < -0.4:
                    rel_type = "enemy"
                else:
                    rel_type = "neutral"
                
                writer.writerow([agent1, agent2, trust, rel_type])
        
        print(f"   📊 CSV data saved: {agents_csv_path}, {relationships_csv_path}")
    
    def _save_sqlite_data(self, agents: List, social_network, game_stats: Dict, timestamp: str):
        """Save to SQLite database for queries"""
        
        db_path = f"{self.base_path}/sqlite/simulation_{timestamp}.db"
        conn = sqlite3.connect(db_path)
        
        # Create tables
        conn.execute('''
            CREATE TABLE agents (
                id INTEGER PRIMARY KEY,
                name TEXT,
                type TEXT,
                personality TEXT,
                intelligence TEXT,
                cooperation_tendency REAL,
                ollama_model TEXT,
                gang_affiliation TEXT,
                crime TEXT,
                sentence_days INTEGER,
                rank TEXT,
                years_experience INTEGER
            )
        ''')
        
        conn.execute('''
            CREATE TABLE relationships (
                agent1_id INTEGER,
                agent2_id INTEGER,
                trust_level REAL,
                relationship_type TEXT,
                PRIMARY KEY (agent1_id, agent2_id)
            )
        ''')
        
        conn.execute('''
            CREATE TABLE gangs (
                gang_name TEXT,
                member_id INTEGER,
                is_leader BOOLEAN,
                PRIMARY KEY (gang_name, member_id)
            )
        ''')
        
        # Insert agent data
        for agent in agents:
            conn.execute('''
                INSERT INTO agents VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                agent.id, agent.name, agent.agent_type.value,
                agent.personality.value, agent.intelligence.value,
                agent.cooperation_tendency, agent.ollama_model,
                getattr(agent, 'gang_affiliation', None),
                getattr(agent, 'crime', None),
                getattr(agent, 'sentence_days', None),
                getattr(agent, 'rank', None),
                getattr(agent, 'years_experience', None)
            ))
        
        # Insert relationship data
        for (agent1, agent2), trust in social_network.relationships.items():
            rel_type = "alliance" if trust > 0.4 else "enemy" if trust < -0.4 else "neutral"
            conn.execute('''
                INSERT INTO relationships VALUES (?, ?, ?, ?)
            ''', (agent1, agent2, trust, rel_type))
        
        # Insert gang data
        for gang_name, members in social_network.gangs.items():
            for i, member_id in enumerate(members):
                is_leader = i == 0  # First member is leader
                conn.execute('''
                    INSERT INTO gangs VALUES (?, ?, ?)
                ''', (gang_name, member_id, is_leader))
        
        conn.commit()
        conn.close()
        
        print(f"   🗄️  SQLite database saved: {db_path}")
    
    def load_simulation_state(self, timestamp: str) -> Dict:
        """Load complete simulation state from JSON"""
        json_path = f"{self.base_path}/json/simulation_{timestamp}.json"
        
        try:
            with open(json_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Simulation data not found: {json_path}")
            return None
    
    def list_saved_simulations(self) -> List[str]:
        """List all saved simulation timestamps"""
        json_dir = f"{self.base_path}/json"
        if not os.path.exists(json_dir):
            return []
        
        files = os.listdir(json_dir)
        timestamps = []
        for file in files:
            if file.startswith("simulation_") and file.endswith(".json"):
                timestamp = file.replace("simulation_", "").replace(".json", "")
                timestamps.append(timestamp)
        
        return sorted(timestamps, reverse=True)  # Most recent first