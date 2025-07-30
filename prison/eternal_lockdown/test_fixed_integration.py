#!/usr/bin/env python3
"""
Test the fixed Ollama integration with proper JSON formatting
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Ollama for TinyTroupe
from ollama_utils import setup_ollama_for_tinytroupe, OllamaClient
setup_ollama_for_tinytroupe()

from tinytroupe.environment import TinyWorld
from tinytroupe.agent import TinyPerson
from datetime import datetime, timedelta

def test_simple_scenario():
    """Test a simple scenario with fixed JSON formatting"""
    print("🧪 Testing Fixed Ollama Integration")
    print("=" * 50)
    
    # Create simple world
    prison = TinyWorld("Test Prison", initial_datetime=datetime(2024, 8, 1, 6, 0))
    
    # Create one simple agent
    carlos = TinyPerson("Carlos")
    carlos.define("age", 28)
    carlos.define("occupation", "Kitchen worker inmate")
    carlos.define("personality", "Tough but trying to reform")
    carlos.define("background", "Former gang member, works in kitchen, wants to change")
    carlos.define("current_situation", "In prison, trying to stay out of trouble")
    
    # Add to world
    prison.add_agent(carlos)
    
    print(f"✅ Created world: {prison.name}")
    print(f"✅ Created agent: {carlos.name}")
    
    # Test simple interaction
    print("\n🎬 Testing simple scenario...")
    prison.broadcast("It's morning head count time. All inmates must be accounted for.")
    
    # Run one step
    try:
        prison.run(1, timedelta_per_step=timedelta(minutes=15))
        print("✅ Scenario completed successfully!")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_simple_scenario()
    if success:
        print("\n🎉 Fixed integration working!")
    else:
        print("\n⚠️ Still needs more fixes")