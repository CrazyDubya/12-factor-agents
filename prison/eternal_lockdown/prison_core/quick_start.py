#!/usr/bin/env python3
"""
ETERNAL LOCKDOWN - PRISON SIMULATION QUICK START
Make the prison GO! Immediate working demo.
"""

import requests
import json
import sqlite3
import random
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, Tuple, List

# ============================================================================
# ENTITIES - Prison Population
# ============================================================================

@dataclass
class Prisoner:
    id: int
    name: str
    crime: str
    sentence_days: int
    personality: str  # "impulsive", "strategic", "cooperative"
    intelligence: str  # "low", "medium", "high"
    
    def get_ollama_model(self):
        """Get appropriate Ollama model based on intelligence"""
        models = {
            "low": "phi:2b",
            "medium": "gemma:7b", 
            "high": "mixtral:8x7b"
        }
        return models.get(self.intelligence, "phi:2b")

@dataclass
class Guard:
    id: int
    name: str
    rank: str
    experience_years: int
    role: str  # "patrol", "enforce", "supervise"
    
    def get_ollama_model(self):
        """Guards use higher intelligence models"""
        return "mixtral:8x7b"

@dataclass
class Warden:
    id: int
    name: str
    experience_years: int
    
    def get_ollama_model(self):
        """Warden uses highest intelligence model"""
        return "llama3:70b"

# ============================================================================
# PRISONER'S DILEMMA ENGINE
# ============================================================================

class PrisonersDilemmaEngine:
    """Core game theory engine for prisoner interactions"""
    
    def __init__(self):
        # Classic PD payoff matrix
        self.payoffs = {
            ("cooperate", "cooperate"): (3, 3),  # R = Reward
            ("cooperate", "defect"): (0, 5),     # S = Sucker, T = Temptation
            ("defect", "cooperate"): (5, 0),     # T = Temptation, S = Sucker
            ("defect", "defect"): (1, 1)         # P = Punishment
        }
    
    def calculate_payoffs(self, decision_a: str, decision_b: str) -> Tuple[int, int]:
        """Calculate payoffs for both players"""
        return self.payoffs.get((decision_a, decision_b), (0, 0))
    
    def get_decision_prompt(self, prisoner: Prisoner, history: str = "") -> str:
        """Generate decision prompt based on prisoner personality"""
        base_prompt = f"""
You are {prisoner.name}, a {prisoner.personality} prisoner serving time for {prisoner.crime}.

PRISONER'S DILEMMA SITUATION:
You must choose: COOPERATE or DEFECT

Payoffs:
- Both cooperate: 3 points each (mutual benefit)
- You defect, they cooperate: 5 points for you, 0 for them (you win big)
- Both defect: 1 point each (mutual punishment)  
- You cooperate, they defect: 0 for you, 5 for them (you get betrayed)

Your personality: {prisoner.personality}
"""
        
        if prisoner.personality == "impulsive":
            base_prompt += "\nYou tend to make quick decisions based on immediate gain. You often defect."
        elif prisoner.personality == "strategic":
            base_prompt += "\nYou think carefully about long-term consequences and reputation."
        elif prisoner.personality == "cooperative":
            base_prompt += "\nYou prefer working together and building trust, even if risky."
        
        if history:
            base_prompt += f"\n\nPrevious interactions: {history}"
        
        base_prompt += "\n\nDecide now: COOPERATE or DEFECT (respond with just one word)"
        
        return base_prompt

# ============================================================================
# OLLAMA INTEGRATION
# ============================================================================

class OllamaInterface:
    """Interface to Ollama for AI decision making"""
    
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url
    
    def is_available(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_decision(self, prompt: str, model: str = "phi:2b") -> str:
        """Get decision from Ollama model"""
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 10  # Short response
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()["response"].strip().upper()
                
                # Extract decision
                if "COOPERATE" in result:
                    return "cooperate"
                elif "DEFECT" in result:
                    return "defect"
                else:
                    # Fallback based on personality
                    return "defect"  # Default to defect if unclear
            else:
                return "defect"  # Fallback
                
        except Exception as e:
            print(f"Ollama error: {e}")
            return "defect"  # Fallback

# ============================================================================
# DATABASE STORAGE
# ============================================================================

class PrisonDatabase:
    """SQLite database for prison simulation"""
    
    def __init__(self, db_path="prison_simulation.db"):
        self.db_path = db_path
        self.setup_database()
    
    def setup_database(self):
        """Create database tables"""
        conn = sqlite3.connect(self.db_path)
        
        # Prisoners table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS prisoners (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                crime TEXT NOT NULL,
                sentence_days INTEGER NOT NULL,
                personality TEXT NOT NULL,
                intelligence TEXT NOT NULL
            )
        ''')
        
        # Guards table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS guards (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                rank TEXT NOT NULL,
                experience_years INTEGER NOT NULL,
                role TEXT NOT NULL
            )
        ''')
        
        # Interactions table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY,
                prisoner_a_id INTEGER NOT NULL,
                prisoner_b_id INTEGER NOT NULL,
                decision_a TEXT NOT NULL,
                decision_b TEXT NOT NULL,
                payoff_a INTEGER NOT NULL,
                payoff_b INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                round_number INTEGER NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_prisoner(self, prisoner: Prisoner):
        """Add prisoner to database"""
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT OR REPLACE INTO prisoners VALUES (?, ?, ?, ?, ?, ?)",
            (prisoner.id, prisoner.name, prisoner.crime, prisoner.sentence_days, 
             prisoner.personality, prisoner.intelligence)
        )
        conn.commit()
        conn.close()
    
    def log_interaction(self, p1_id: int, p2_id: int, decision_a: str, decision_b: str, 
                       payoff_a: int, payoff_b: int, round_num: int):
        """Log prisoner interaction"""
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT INTO interactions VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?)",
            (p1_id, p2_id, decision_a, decision_b, payoff_a, payoff_b, 
             datetime.now().isoformat(), round_num)
        )
        conn.commit()
        conn.close()
    
    def get_interaction_history(self, p1_id: int, p2_id: int) -> str:
        """Get interaction history between two prisoners"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            "SELECT decision_a, decision_b, round_number FROM interactions "
            "WHERE (prisoner_a_id = ? AND prisoner_b_id = ?) "
            "OR (prisoner_a_id = ? AND prisoner_b_id = ?) "
            "ORDER BY round_number",
            (p1_id, p2_id, p2_id, p1_id)
        )
        
        history = []
        for row in cursor.fetchall():
            dec_a, dec_b, round_num = row
            history.append(f"Round {round_num}: {dec_a} vs {dec_b}")
        
        conn.close()
        return "; ".join(history)

# ============================================================================
# PRISON SIMULATION ENGINE
# ============================================================================

class PrisonSimulation:
    """Main prison simulation engine"""
    
    def __init__(self):
        self.pd_engine = PrisonersDilemmaEngine()
        self.ollama = OllamaInterface()
        self.db = PrisonDatabase()
        self.prisoners: List[Prisoner] = []
        self.guards: List[Guard] = []
        self.round_number = 0
        
        # Check Ollama availability
        if not self.ollama.is_available():
            print("⚠️  WARNING: Ollama not available. Using random decisions.")
    
    def create_sample_prisoners(self):
        """Create sample prisoner population"""
        sample_prisoners = [
            Prisoner(1, "Marcus Johnson", "Drug possession", 1825, "impulsive", "low"),
            Prisoner(2, "Carlos Mendez", "Racketeering", 2920, "strategic", "high"),
            Prisoner(3, "David Chen", "Embezzlement", 1095, "cooperative", "medium"),
            Prisoner(4, "Tommy Rodriguez", "Armed robbery", 4380, "strategic", "medium"),
            Prisoner(5, "Lisa Williams", "Assault", 730, "impulsive", "low")
        ]
        
        for prisoner in sample_prisoners:
            self.prisoners.append(prisoner)
            self.db.add_prisoner(prisoner)
        
        print(f"✅ Created {len(sample_prisoners)} prisoners")
    
    def run_pd_interaction(self, p1: Prisoner, p2: Prisoner) -> Tuple[str, str, Tuple[int, int]]:
        """Run single PD interaction between two prisoners"""
        self.round_number += 1
        
        # Get interaction history
        history = self.db.get_interaction_history(p1.id, p2.id)
        
        # Get decisions
        if self.ollama.is_available():
            # Use Ollama for decisions
            prompt_1 = self.pd_engine.get_decision_prompt(p1, history)
            prompt_2 = self.pd_engine.get_decision_prompt(p2, history)
            
            decision_1 = self.ollama.get_decision(prompt_1, p1.get_ollama_model())
            decision_2 = self.ollama.get_decision(prompt_2, p2.get_ollama_model())
        else:
            # Fallback to personality-based random decisions
            decision_1 = self._get_personality_decision(p1)
            decision_2 = self._get_personality_decision(p2)
        
        # Calculate payoffs
        payoffs = self.pd_engine.calculate_payoffs(decision_1, decision_2)
        
        # Log interaction
        self.db.log_interaction(p1.id, p2.id, decision_1, decision_2, 
                               payoffs[0], payoffs[1], self.round_number)
        
        return decision_1, decision_2, payoffs
    
    def _get_personality_decision(self, prisoner: Prisoner) -> str:
        """Fallback personality-based decision"""
        if prisoner.personality == "cooperative":
            return "cooperate" if random.random() > 0.3 else "defect"
        elif prisoner.personality == "strategic":
            return "cooperate" if random.random() > 0.5 else "defect"
        else:  # impulsive
            return "defect" if random.random() > 0.3 else "cooperate"
    
    def run_simulation_round(self):
        """Run one round of interactions"""
        print(f"\n🔄 Running Simulation Round {self.round_number + 1}")
        print("=" * 50)
        
        # Pair up prisoners randomly
        available_prisoners = self.prisoners.copy()
        random.shuffle(available_prisoners)
        
        interactions = []
        for i in range(0, len(available_prisoners) - 1, 2):
            p1 = available_prisoners[i]
            p2 = available_prisoners[i + 1]
            
            print(f"\n👥 {p1.name} ({p1.personality}) vs {p2.name} ({p2.personality})")
            
            decision_1, decision_2, payoffs = self.run_pd_interaction(p1, p2)
            
            print(f"   {p1.name}: {decision_1.upper()} → {payoffs[0]} points")
            print(f"   {p2.name}: {decision_2.upper()} → {payoffs[1]} points")
            
            interactions.append((p1, p2, decision_1, decision_2, payoffs))
        
        return interactions
    
    def get_statistics(self):
        """Get simulation statistics"""
        conn = sqlite3.connect(self.db.db_path)
        
        # Total interactions
        total_interactions = conn.execute("SELECT COUNT(*) FROM interactions").fetchone()[0]
        
        # Cooperation rate
        cooperations = conn.execute(
            "SELECT COUNT(*) FROM interactions WHERE decision_a = 'cooperate' OR decision_b = 'cooperate'"
        ).fetchone()[0]
        
        cooperation_rate = (cooperations / max(total_interactions * 2, 1)) * 100
        
        # Top cooperators
        top_cooperators = conn.execute("""
            SELECT p.name, COUNT(*) as cooperations
            FROM interactions i
            JOIN prisoners p ON (p.id = i.prisoner_a_id AND i.decision_a = 'cooperate')
                             OR (p.id = i.prisoner_b_id AND i.decision_b = 'cooperate')
            GROUP BY p.name
            ORDER BY cooperations DESC
            LIMIT 3
        """).fetchall()
        
        conn.close()
        
        return {
            'total_interactions': total_interactions,
            'cooperation_rate': round(cooperation_rate, 1),
            'top_cooperators': top_cooperators
        }

# ============================================================================
# MAIN EXECUTION - MAKE THE PRISON GO!
# ============================================================================

def main():
    """Main execution - Start the prison simulation!"""
    
    print("🏢 ETERNAL LOCKDOWN PRISON SIMULATION")
    print("=" * 60)
    print("🚀 MAKING THE PRISON GO!")
    print()
    
    # Initialize simulation
    prison = PrisonSimulation()
    
    # Create prisoner population
    print("👥 Creating prisoner population...")
    prison.create_sample_prisoners()
    
    # Check Ollama status
    if prison.ollama.is_available():
        print("🤖 Ollama AI: ONLINE")
        print("   Models will make intelligent decisions based on personality")
    else:
        print("🎲 Ollama AI: OFFLINE")
        print("   Using personality-based random decisions")
    
    print("\n💾 Database: READY")
    print("🎯 Prisoner's Dilemma Engine: LOADED")
    
    # Run simulation rounds
    print("\n" + "=" * 60)
    print("🎮 STARTING PRISON INTERACTIONS")
    print("=" * 60)
    
    try:
        # Run 3 rounds of interactions
        for round_num in range(3):
            interactions = prison.run_simulation_round()
            
            # Brief pause between rounds
            input(f"\n⏸️  Press Enter to continue to round {round_num + 2} (or Ctrl+C to stop)...")
        
        # Show final statistics
        print("\n" + "=" * 60)
        print("📊 SIMULATION STATISTICS")
        print("=" * 60)
        
        stats = prison.get_statistics()
        print(f"Total Interactions: {stats['total_interactions']}")
        print(f"Cooperation Rate: {stats['cooperation_rate']}%")
        print(f"Top Cooperators: {[name for name, count in stats['top_cooperators']]}")
        
        print("\n✅ PRISON SIMULATION COMPLETE!")
        print("💾 All data saved to prison_simulation.db")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Simulation stopped by user")
        print("💾 Data saved to prison_simulation.db")

if __name__ == "__main__":
    main()