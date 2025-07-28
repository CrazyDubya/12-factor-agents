"""
AutoGen Prison Agents for Eternal Lockdown
Integrates AutoGen's multi-agent conversation capabilities with our prison simulation
"""

import sys
import os
from typing import List, Dict, Any, Optional
import json

# Add our paths
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'tinytroupe'))

try:
    import autogen
    from autogen import ConversableAgent, GroupChat, GroupChatManager
    AUTOGEN_AVAILABLE = True
except ImportError:
    print("AutoGen not installed. Install with: pip install pyautogen")
    AUTOGEN_AVAILABLE = False

from personas.inmates import create_diverse_inmates, PrisonInmate
from personas.guards import create_diverse_guards, PrisonGuard

class PrisonAutoGenAgent(ConversableAgent):
    """Base class for prison agents using AutoGen"""
    
    def __init__(self, name: str, persona_type: str, system_message: str, **kwargs):
        self.persona_type = persona_type
        self.prison_role = kwargs.get('prison_role', 'unknown')
        self.security_level = kwargs.get('security_level', 'medium')
        self.authority_level = kwargs.get('authority_level', 0)  # 0=prisoner, 1=guard, 2=sergeant, 3=warden
        
        # Configure for Ollama
        llm_config = {
            "config_list": [{
                "model": "llama2:latest",
                "base_url": "http://localhost:11434/v1",
                "api_key": "ollama",  # Dummy key for Ollama
                "api_type": "openai"
            }],
            "temperature": 0.7,
            "timeout": 120,
        }
        
        super().__init__(
            name=name,
            system_message=system_message,
            llm_config=llm_config,
            **kwargs
        )

class PrisonInmateAgent(PrisonAutoGenAgent):
    """AutoGen agent representing a prison inmate"""
    
    def __init__(self, name: str, crime_type: str, sentence_length: str, 
                 background: str = "", personality: str = "", **kwargs):
        
        self.crime_type = crime_type
        self.sentence_length = sentence_length
        self.background = background
        self.personality = personality
        
        system_message = f"""
You are {name}, an inmate at Eternal Lockdown Correctional Facility.

BACKGROUND:
- Crime: {crime_type}
- Sentence: {sentence_length}
- Background: {background}
- Personality: {personality}

BEHAVIOR GUIDELINES:
- Speak respectfully to guards and staff (address them as "Officer" or by rank)
- Follow prison rules and protocols
- Show your personality while being realistic about prison life
- Ask for permission before making requests
- Be aware of the prison hierarchy and your place in it
- Express your thoughts and feelings authentically
- Seek help when needed but don't be overly demanding

COMMUNICATION STYLE:
- Use appropriate language for your background
- Show respect for authority while maintaining your dignity
- Be honest about your situation and needs
- Demonstrate growth and rehabilitation efforts when appropriate

Remember: You are a human being with hopes, fears, and goals, not just defined by your crime.
"""
        
        super().__init__(
            name=name,
            persona_type="inmate",
            system_message=system_message,
            prison_role="inmate",
            authority_level=0,
            **kwargs
        )

class PrisonGuardAgent(PrisonAutoGenAgent):
    """AutoGen agent representing a prison guard"""
    
    def __init__(self, name: str, rank: str, years_experience: int,
                 approach_style: str = "professional", specialization: str = "general", **kwargs):
        
        self.rank = rank
        self.years_experience = years_experience
        self.approach_style = approach_style
        self.specialization = specialization
        
        authority_map = {
            "Officer": 1,
            "Correctional Officer": 1,
            "Senior Officer": 1,
            "Sergeant": 2,
            "Lieutenant": 2,
            "Captain": 3,
            "Warden": 4
        }
        
        authority_level = authority_map.get(rank.split()[-1], 1)
        
        system_message = f"""
You are {name}, a {rank} at Eternal Lockdown Correctional Facility.

PROFESSIONAL PROFILE:
- Rank: {rank}
- Experience: {years_experience} years in corrections
- Approach: {approach_style}
- Specialization: {specialization}

RESPONSIBILITIES:
- Maintain security and order in the facility
- Treat all inmates with dignity and respect
- Follow departmental policies and procedures
- De-escalate conflicts when possible
- Support rehabilitation and reintegration efforts
- Document incidents and observations accurately

COMMUNICATION GUIDELINES:
- Be professional and authoritative when needed
- Use clear, direct communication
- Show respect for inmates as human beings
- Maintain appropriate boundaries
- Escalate serious issues to supervisors
- Provide guidance and support when appropriate

AUTHORITY LEVEL: {authority_level}
- You can make decisions within your scope of authority
- Escalate complex issues to higher-ranking staff
- Coordinate with other officers as needed

Remember: Your role is to maintain safety while supporting rehabilitation and human dignity.
"""
        
        super().__init__(
            name=name,
            persona_type="guard",
            system_message=system_message,
            prison_role=rank.lower().replace(" ", "_"),
            authority_level=authority_level,
            **kwargs
        )

class WardenAgent(PrisonAutoGenAgent):
    """AutoGen agent representing the prison warden"""
    
    def __init__(self, name: str = "Warden Sarah Mitchell", **kwargs):
        
        system_message = f"""
You are {name}, the Warden of Eternal Lockdown Correctional Facility.

LEADERSHIP ROLE:
- Ultimate authority and responsibility for the facility
- 20+ years experience in corrections and administration
- Master's degree in Public Administration
- Committed to both security and rehabilitation

RESPONSIBILITIES:
- Oversee all facility operations and staff
- Make final decisions on complex issues
- Ensure compliance with policies and regulations
- Support staff development and training
- Maintain relationships with external stakeholders
- Balance security needs with rehabilitation goals

MANAGEMENT STYLE:
- Collaborative but decisive leadership
- Open door policy for staff and reasonable inmate concerns
- Data-driven decision making
- Focus on continuous improvement
- Strong advocate for both staff and inmate welfare

COMMUNICATION APPROACH:
- Professional and authoritative
- Listen to all perspectives before deciding
- Provide clear direction and expectations
- Support staff while holding them accountable
- Treat everyone with dignity and respect

AUTHORITY: You have final decision-making authority on all facility matters.
"""
        
        super().__init__(
            name=name,
            persona_type="warden",
            system_message=system_message,
            prison_role="warden",
            authority_level=4,
            **kwargs
        )

class PrisonGroupChat:
    """Manages group conversations in prison settings"""
    
    def __init__(self, scenario_name: str, participants: List[PrisonAutoGenAgent]):
        self.scenario_name = scenario_name
        self.participants = participants
        self.chat_history = []
        
        # Sort participants by authority level for proper speaking order
        self.participants.sort(key=lambda x: x.authority_level, reverse=True)
        
        # Create AutoGen GroupChat
        self.group_chat = GroupChat(
            agents=participants,
            messages=[],
            max_round=20,
            speaker_selection_method="round_robin"
        )
        
        # Create GroupChatManager with highest authority agent as admin
        admin_agent = max(participants, key=lambda x: x.authority_level)
        self.manager = GroupChatManager(
            groupchat=self.group_chat,
            llm_config=admin_agent.llm_config
        )
    
    def start_conversation(self, initial_message: str, initiator: Optional[PrisonAutoGenAgent] = None):
        """Start a group conversation with an initial message"""
        
        if initiator is None:
            initiator = self.participants[0]
        
        print(f"\n🎭 Starting {self.scenario_name}")
        print("=" * 50)
        print(f"Participants: {[agent.name for agent in self.participants]}")
        print(f"Initiated by: {initiator.name}")
        print("-" * 50)
        
        # Start the conversation
        result = initiator.initiate_chat(
            self.manager,
            message=initial_message
        )
        
        return result

def create_guard_prisoner_dialogue():
    """Create a simple guard-prisoner dialogue scenario"""
    
    if not AUTOGEN_AVAILABLE:
        print("AutoGen not available. Please install: pip install pyautogen")
        return None
    
    # Create participants
    inmate = PrisonInmateAgent(
        name="Marcus Johnson",
        crime_type="Drug possession with intent to distribute",
        sentence_length="5 years",
        background="Urban background, struggling with addiction, has young daughter",
        personality="Respectful but sometimes frustrated, wants to rehabilitate"
    )
    
    guard = PrisonGuardAgent(
        name="Officer Martinez",
        rank="Correctional Officer II",
        years_experience=8,
        approach_style="firm but fair",
        specialization="general population"
    )
    
    # Create group chat
    dialogue = PrisonGroupChat(
        scenario_name="Education Program Inquiry",
        participants=[inmate, guard]
    )
    
    return dialogue

def create_warden_oversight_scenario():
    """Create a scenario with warden oversight of a complex situation"""
    
    if not AUTOGEN_AVAILABLE:
        print("AutoGen not available. Please install: pip install pyautogen")
        return None
    
    # Create participants
    inmate1 = PrisonInmateAgent(
        name="James Thompson",
        crime_type="Gang-related assault",
        sentence_length="6 years",
        background="Young offender, gang background",
        personality="Defensive but seeking change"
    )
    
    inmate2 = PrisonInmateAgent(
        name="Robert Hayes",
        crime_type="Second-degree murder",
        sentence_length="Life with possibility of parole",
        background="Long-term inmate, model prisoner",
        personality="Wise, mentoring, reformed"
    )
    
    guard = PrisonGuardAgent(
        name="Officer Kim",
        rank="Correctional Officer I",
        years_experience=1,
        approach_style="rehabilitation-focused",
        specialization="programs support"
    )
    
    sergeant = PrisonGuardAgent(
        name="Sergeant Thompson",
        rank="Correctional Sergeant",
        years_experience=15,
        approach_style="mentoring",
        specialization="staff supervision"
    )
    
    warden = WardenAgent()
    
    # Create group chat
    oversight = PrisonGroupChat(
        scenario_name="Conflict Resolution with Warden Oversight",
        participants=[inmate1, inmate2, guard, sergeant, warden]
    )
    
    return oversight

def demo_autogen_integration():
    """Demonstrate AutoGen integration with prison simulation"""
    
    print("🏢 AutoGen Integration Demo for Eternal Lockdown")
    print("=" * 60)
    
    if not AUTOGEN_AVAILABLE:
        print("❌ AutoGen not installed. Please install with:")
        print("   pip install pyautogen")
        return False
    
    try:
        # Test simple dialogue
        print("\n1️⃣ Testing Guard-Prisoner Dialogue...")
        dialogue = create_guard_prisoner_dialogue()
        
        if dialogue:
            result = dialogue.start_conversation(
                "Officer Martinez, I'd like to ask about the GED program. "
                "I want to complete my education while I'm here.",
                initiator=dialogue.participants[0]  # Inmate initiates
            )
            print("✅ Guard-Prisoner dialogue completed")
        
        # Test oversight scenario
        print("\n2️⃣ Testing Warden Oversight Scenario...")
        oversight = create_warden_oversight_scenario()
        
        if oversight:
            result = oversight.start_conversation(
                "We have a situation in the common area. James and Robert had a disagreement "
                "about TV programming that's escalating. I need guidance on how to handle this.",
                initiator=oversight.participants[2]  # Guard reports to sergeant
            )
            print("✅ Warden oversight scenario completed")
        
        print("\n🎉 AutoGen integration successful!")
        return True
        
    except Exception as e:
        print(f"❌ Error in AutoGen integration: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    demo_autogen_integration()