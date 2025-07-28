"""
Daily Routine Scenario for Eternal Lockdown Prison Simulation
Tests basic interactions between inmates and guards during normal operations
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eternal_lockdown.tinytroupe.environment import TinyWorld
from eternal_lockdown.personas.inmates import create_diverse_inmates
from eternal_lockdown.personas.guards import create_diverse_guards
from eternal_lockdown.tinytroupe import config_manager

def setup_prison_environment():
    """Set up the basic prison environment"""
    
    # Configure for Ollama
    config_manager.set_config("Ollama", "MODEL", "llama2:latest")
    config_manager.set_config("Ollama", "BASE_URL", "http://localhost:11434")
    config_manager.set_config("Simulation", "PARALLEL_AGENT_GENERATION", "False")
    config_manager.set_config("Simulation", "PARALLEL_AGENT_ACTIONS", "False")
    
    # Create the prison world
    prison = TinyWorld("Eternal Lockdown Correctional Facility")
    
    # Set up the environment description
    prison.set_description("""
    Eternal Lockdown Correctional Facility is a medium-security prison housing 350 inmates.
    The facility operates on a structured daily schedule with meals, work assignments, 
    recreation time, and various rehabilitation programs.
    
    AREAS:
    - Cell blocks (A, B, C, D)
    - Cafeteria and kitchen
    - Recreation yard
    - Library and education center
    - Medical facility
    - Visiting room
    - Administrative offices
    - Workshop areas
    
    DAILY SCHEDULE:
    - 6:00 AM: Wake-up and count
    - 7:00 AM: Breakfast
    - 8:00 AM: Work assignments/programs
    - 12:00 PM: Lunch and count
    - 1:00 PM: Afternoon activities
    - 5:00 PM: Dinner
    - 6:00 PM: Recreation time
    - 9:00 PM: Return to cells
    - 10:00 PM: Lights out
    
    RULES:
    - Respect all staff and fellow inmates
    - Follow the daily schedule
    - No contraband items
    - Participate in assigned work/programs
    - Maintain personal hygiene and cell cleanliness
    """)
    
    return prison

def run_morning_routine_scenario():
    """Run a morning routine scenario with interactions"""
    
    print("🏢 Setting up Eternal Lockdown Prison Simulation...")
    
    # Create environment
    prison = setup_prison_environment()
    
    # Create personas
    print("👥 Creating inmate personas...")
    inmates = create_diverse_inmates()[:3]  # Start with 3 inmates for testing
    
    print("👮 Creating guard personas...")
    guards = create_diverse_guards()[:2]  # Start with 2 guards for testing
    
    # Add everyone to the prison
    for inmate in inmates:
        prison.add_agent(inmate)
        print(f"   Added inmate: {inmate.name}")
    
    for guard in guards:
        prison.add_agent(guard)
        print(f"   Added guard: {guard.name}")
    
    print(f"\n🏢 Prison population: {len(inmates)} inmates, {len(guards)} guards")
    
    # Start the simulation
    print("\n⏰ Starting morning routine simulation...")
    
    # Morning wake-up announcement
    prison.broadcast("""
    ATTENTION ALL INMATES: This is the 6:00 AM wake-up call. 
    Please prepare for morning count. Stand by your cell doors for inspection.
    Breakfast will be served in the cafeteria at 7:00 AM.
    """)
    
    print("\n📢 Wake-up announcement broadcast to all agents")
    
    # Run a few simulation steps
    print("\n🔄 Running simulation steps...")
    
    for step in range(3):
        print(f"\n--- Simulation Step {step + 1} ---")
        prison.run(1)  # Run one step
        
        # Get some interactions
        if step == 0:
            # Guard does morning count
            guard = guards[0]
            guard.listen_and_act("Conduct the morning inmate count. Check each inmate and ensure they are accounted for.")
            
        elif step == 1:
            # Inmates respond to wake-up
            for inmate in inmates:
                inmate.listen_and_act("Respond to the wake-up call and prepare for morning count.")
                
        elif step == 2:
            # Breakfast time interaction
            prison.broadcast("Breakfast is now being served in the cafeteria. Please proceed in an orderly fashion.")
            
    print("\n✅ Morning routine simulation completed!")
    
    # Display some results
    print("\n📊 Simulation Results:")
    print("=" * 50)
    
    for agent in prison.agents:
        print(f"\n{agent.name} ({agent.__class__.__name__}):")
        # Get recent actions/thoughts
        if hasattr(agent, 'episodic_memory') and agent.episodic_memory:
            recent_memories = agent.episodic_memory.retrieve_recent(3)
            for memory in recent_memories:
                print(f"  - {memory}")
    
    return prison, inmates, guards

def test_inmate_guard_interaction():
    """Test specific interaction between an inmate and guard"""
    
    print("\n🎭 Testing specific inmate-guard interaction...")
    
    prison = setup_prison_environment()
    
    # Create specific personas for interaction
    from eternal_lockdown.personas.inmates import PrisonInmate
    from eternal_lockdown.personas.guards import PrisonGuard
    
    # Create a nervous first-time inmate
    nervous_inmate = PrisonInmate(
        name="Alex Rivera",
        crime_type="DUI causing injury", 
        sentence_length="18 months",
        time_served="1 week",
        age=26,
        background="college graduate, first offense",
        behavior_record="anxious but compliant"
    )
    
    # Create an experienced, mentoring guard
    mentor_guard = PrisonGuard(
        name="Sergeant Thompson",
        rank="Correctional Sergeant",
        years_experience=15,
        approach_style="mentoring and supportive"
    )
    
    prison.add_agent(nervous_inmate)
    prison.add_agent(mentor_guard)
    
    print(f"👤 Created interaction between {nervous_inmate.name} and {mentor_guard.name}")
    
    # Set up interaction scenario
    prison.broadcast("It's recreation time. Inmates may use the yard, library, or common areas.")
    
    # Inmate asks for help
    nervous_inmate.listen_and_act(
        "You're feeling overwhelmed and confused about prison procedures. "
        "Approach Sergeant Thompson and ask for guidance about how things work here."
    )
    
    # Guard responds helpfully
    mentor_guard.listen_and_act(
        "A new inmate approaches you looking confused and anxious. "
        "Use your experience to provide helpful guidance while maintaining appropriate boundaries."
    )
    
    print("✅ Interaction test completed!")

if __name__ == "__main__":
    try:
        # Test basic setup first
        print("🧪 Testing Ollama connection...")
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f"✅ Ollama connected. Available models: {[m['name'] for m in models[:3]]}")
        else:
            print("❌ Ollama not responding")
            exit(1)
            
        # Run the main scenario
        prison, inmates, guards = run_morning_routine_scenario()
        
        # Run interaction test
        test_inmate_guard_interaction()
        
        print("\n🎉 All tests completed successfully!")
        print("\n📝 Next steps:")
        print("1. Review the simulation output above")
        print("2. Modify personas and scenarios as needed")
        print("3. Add more complex interactions and events")
        print("4. Implement data collection and analysis")
        
    except Exception as e:
        print(f"❌ Error running simulation: {e}")
        import traceback
        traceback.print_exc()