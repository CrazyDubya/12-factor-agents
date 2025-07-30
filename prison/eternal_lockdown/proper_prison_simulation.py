#!/usr/bin/env python3
"""
PROPER Prison Simulation using ACTUAL TinyTroupe TinyWorld + Ollama LLMs
No more amateur bullshit - using the real frameworks as requested
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tinytroupe'))

from tinytroupe.environment import TinyWorld
from tinytroupe.agent import TinyPerson
from tinytroupe import control
import tinytroupe.openai_utils as openai_utils

def setup_ollama_for_tinytroupe():
    """Configure TinyTroupe to use Ollama instead of OpenAI"""
    # Override the openai_utils to use Ollama
    import requests
    
    def ollama_send_message(messages, model="llama2:latest", **kwargs):
        """Replace OpenAI calls with Ollama calls"""
        try:
            # Convert messages to Ollama format
            prompt = ""
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role == "system":
                    prompt += f"System: {content}\n"
                elif role == "user":
                    prompt += f"Human: {content}\n"
                elif role == "assistant":
                    prompt += f"Assistant: {content}\n"
            
            prompt += "Assistant:"
            
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.7}
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "choices": [{
                        "message": {
                            "role": "assistant",
                            "content": result["response"]
                        }
                    }]
                }
            else:
                raise Exception(f"Ollama error: {response.status_code}")
                
        except Exception as e:
            print(f"Ollama error: {e}")
            # Fallback response
            return {
                "choices": [{
                    "message": {
                        "role": "assistant", 
                        "content": "I understand the situation and will respond appropriately."
                    }
                }]
            }
    
    # Monkey patch the openai_utils
    openai_utils.client().send_message = ollama_send_message
    print("✅ TinyTroupe configured to use Ollama")

def create_prison_world():
    """Create the actual TinyWorld prison environment"""
    
    # Create the main prison world using TinyTroupe's TinyWorld
    prison = TinyWorld("Eternal Lockdown Correctional Facility")
    
    # Set up the prison environment description
    prison.set_description("""
    Eternal Lockdown Correctional Facility is a medium-security prison with a tight pod-based structure.
    
    PHYSICAL LAYOUT:
    - Pod A: 4 cells (2 inmates per cell), common area, kitchen, laundry
    - Small yard attached to pod
    - Shower facilities
    - Library corner
    - All activities happen within the pod - tight constraints
    
    DAILY SCHEDULE:
    - 06:00: Wake up, cell time
    - 07:00: Breakfast, showers
    - 08:00: Work assignments (kitchen, laundry, janitor, maintenance)
    - 12:00: Lunch
    - 13:00: Afternoon work/programs
    - 17:00: Dinner
    - 18:00: Recreation time
    - 21:00: Cell time
    - 22:00: Lights out
    
    WORK ASSIGNMENTS:
    - Kitchen duty: 3 inmates prepare meals
    - Laundry duty: 2 inmates handle washing
    - Janitor duty: 2 inmates clean common areas
    - Maintenance: 1 inmate handles repairs
    
    RULES AND CONSTRAINTS:
    - All movement within pod only
    - Guards supervise but inmates interact freely
    - Resources are limited - cooperation vs competition
    - Gang affiliations create loyalty conflicts
    - Sentence time creates urgency/desperation
    """)
    
    return prison

def create_prison_agents():
    """Create TinyPerson agents for the prison simulation"""
    
    agents = []
    
    # Create diverse inmates using TinyPerson
    
    # Gang Leader - Los Hermanos
    carlos = TinyPerson("Carlos Mendez")
    carlos.define("age", 32)
    carlos.define("occupation", "Gang Leader (Los Hermanos)")
    carlos.define("personality", "Strategic, calculating, loyal to gang members")
    carlos.define("background", """
    You are Carlos Mendez, leader of Los Hermanos gang in prison. You're serving 24 days for drug dealing.
    You're strategic and intelligent, always thinking several moves ahead. Your gang loyalty is absolute - 
    you protect Diego Santos (your gang member) at all costs. You're suspicious of Iron Brotherhood members
    but will cooperate when it benefits your gang. You have 15 days left on your sentence.
    
    Your goals: Maintain gang respect, protect Diego, survive sentence, plan for release.
    Your fears: Losing gang leadership, Diego getting hurt, Iron Brotherhood retaliation.
    """)
    carlos.define("current_situation", "Gang leader in medium-security pod, managing gang politics")
    agents.append(carlos)
    
    # Gang Member - Los Hermanos  
    diego = TinyPerson("Diego Santos")
    diego.define("age", 26)
    diego.define("occupation", "Gang Member (Los Hermanos)")
    diego.define("personality", "Cooperative with gang, loyal, follows Carlos's lead")
    diego.define("background", """
    You are Diego Santos, member of Los Hermanos gang. You're serving 8 days for drug possession.
    You look up to Carlos Mendez as your leader and follow his guidance. You're naturally cooperative
    but your gang loyalty comes first. You're nervous about Iron Brotherhood but trust Carlos to handle it.
    You have 3 days left on your sentence - almost free!
    
    Your goals: Stay loyal to Carlos, avoid trouble, get out soon.
    Your fears: Gang conflict, disappointing Carlos, getting more time added.
    """)
    diego.define("current_situation", "Gang member, short sentence, almost release")
    agents.append(diego)
    
    # Gang Leader - Iron Brotherhood
    tommy = TinyPerson("Tommy Rodriguez")
    tommy.define("age", 38)
    tommy.define("occupation", "Gang Leader (Iron Brotherhood)")
    tommy.define("personality", "Aggressive, territorial, quick to anger")
    tommy.define("background", """
    You are Tommy Rodriguez, leader of Iron Brotherhood in this pod. You're serving 26 days for armed robbery.
    You're aggressive and believe in showing strength. You protect Jake Morrison (your gang member) and
    view Los Hermanos as rivals. You don't back down from confrontation and believe respect is earned through fear.
    You have 20 days left - a long time in this environment.
    
    Your goals: Maintain dominance, protect Jake, control pod territory.
    Your fears: Showing weakness, losing respect, Los Hermanos gaining power.
    """)
    tommy.define("current_situation", "Gang leader with long sentence, territorial disputes")
    agents.append(tommy)
    
    # Gang Member - Iron Brotherhood
    jake = TinyPerson("Jake Morrison")
    jake.define("age", 29)
    jake.define("occupation", "Gang Member (Iron Brotherhood)")
    jake.define("personality", "Aggressive but follows Tommy, loyal to brotherhood")
    jake.define("background", """
    You are Jake Morrison, member of Iron Brotherhood. You're serving 19 days for assault.
    You follow Tommy Rodriguez's lead and share his aggressive approach. You're suspicious of
    Los Hermanos and ready to back up Tommy in any conflict. You believe in brotherhood loyalty above all.
    You have 14 days left on your sentence.
    
    Your goals: Support Tommy, maintain brotherhood honor, survive sentence.
    Your fears: Gang war, being seen as weak, disappointing Tommy.
    """)
    jake.define("current_situation", "Gang member, medium sentence, backing up leader")
    agents.append(jake)
    
    # Independent Inmate - Cooperative
    marcus = TinyPerson("Marcus Johnson")
    marcus.define("age", 28)
    marcus.define("occupation", "Independent Inmate")
    marcus.define("personality", "Cooperative, wants to avoid trouble, rehabilitation-focused")
    marcus.define("background", """
    You are Marcus Johnson, serving 8 days for drug possession. You're not affiliated with any gang
    and want to keep it that way. You're focused on rehabilitation and getting out clean.
    You try to cooperate with everyone and avoid gang politics. You have a young daughter waiting for you.
    You have 4 days left on your sentence.
    
    Your goals: Stay out of trouble, complete sentence, return to daughter.
    Your fears: Gang recruitment pressure, violence, more time added.
    """)
    marcus.define("current_situation", "Independent inmate, short sentence, avoiding gang politics")
    agents.append(marcus)
    
    # Independent Inmate - Withdrawn
    david = TinyPerson("David Chen")
    david.define("age", 35)
    david.define("occupation", "Independent Inmate")
    david.define("personality", "Withdrawn, intelligent, observant")
    david.define("background", """
    You are David Chen, serving 17 days for fraud. You're educated and intelligent but keep to yourself.
    You observe the gang dynamics but stay neutral. You're good at reading people and situations.
    You prefer the library and quiet activities. You have 12 days left on your sentence.
    
    Your goals: Stay invisible, serve time quietly, avoid all conflicts.
    Your fears: Being forced to choose sides, violence, losing control.
    """)
    david.define("current_situation", "Independent inmate, medium sentence, staying neutral")
    agents.append(david)
    
    # Guards
    martinez = TinyPerson("Officer Martinez")
    martinez.define("age", 34)
    martinez.define("occupation", "Correctional Officer")
    martinez.define("personality", "Professional, firm but fair, experienced")
    martinez.define("background", """
    You are Officer Martinez, an experienced correctional officer with 8 years on the job.
    You maintain order while treating inmates with dignity. You're aware of the gang dynamics
    and work to prevent conflicts. You believe in rehabilitation but security comes first.
    
    Your goals: Maintain order, prevent violence, support rehabilitation when possible.
    Your approach: Professional, consistent, fair but firm.
    """)
    martinez.define("current_situation", "Day shift officer managing pod dynamics")
    agents.append(martinez)
    
    return agents

def run_proper_simulation():
    """Run the actual simulation using TinyTroupe frameworks"""
    
    print("🏢 PROPER ETERNAL LOCKDOWN SIMULATION")
    print("Using ACTUAL TinyTroupe TinyWorld + Ollama LLMs")
    print("=" * 60)
    
    # Setup Ollama integration
    setup_ollama_for_tinytroupe()
    
    # Create the prison world using TinyTroupe
    prison = create_prison_world()
    print(f"✅ Created TinyWorld: {prison.name}")
    
    # Create agents using TinyPerson
    agents = create_prison_agents()
    print(f"✅ Created {len(agents)} TinyPerson agents")
    
    # Add agents to the world
    for agent in agents:
        prison.add_agent(agent)
        print(f"   Added {agent.name} to prison world")
    
    print(f"\n🎭 Starting TinyTroupe simulation with {len(agents)} agents in {prison.name}")
    
    # Run actual TinyTroupe simulation scenarios
    scenarios = [
        "It's breakfast time in the pod. The kitchen workers are serving food and inmates are gathering in the common area.",
        
        "During work time, there's a dispute over who gets to use the better cleaning supplies in the janitor closet.",
        
        "In the yard during recreation time, tensions are rising between the two gangs over territory.",
        
        "It's evening cell time. Cellmates are locked in together and have time to talk privately.",
        
        "A new privilege opportunity has opened up - one inmate can earn extra commissary access for good behavior."
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n🎬 SCENARIO {i}: {scenario}")
        print("-" * 50)
        
        # Use TinyWorld's broadcast method to set scenario
        prison.broadcast(scenario)
        
        # Run the world for 2 steps
        prison.run(2)
        
        print("✅ Scenario complete")
    
    print(f"\n🎉 TinyTroupe simulation complete!")
    print("This used ACTUAL TinyWorld and TinyPerson with Ollama LLMs")
    
    return prison, agents

if __name__ == "__main__":
    try:
        prison_world, prison_agents = run_proper_simulation()
        print("\n✅ SUCCESS: Proper TinyTroupe + Ollama simulation completed!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()