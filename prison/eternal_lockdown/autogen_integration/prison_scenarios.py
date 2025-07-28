"""
Prison Scenarios using AutoGen for Multi-Agent Conversations
Specific scenarios for guard-prisoner dialogues and hierarchical oversight
"""

import sys
import os
from typing import List, Dict, Any, Optional

# Add our paths
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, current_dir)

try:
    from autogen_integration.autogen_prison_agents import (
        PrisonInmateAgent, PrisonGuardAgent, WardenAgent, PrisonGroupChat
    )
    AUTOGEN_AVAILABLE = True
except ImportError:
    print("AutoGen integration not available")
    AUTOGEN_AVAILABLE = False

class PrisonScenarioManager:
    """Manages different prison scenarios using AutoGen"""
    
    def __init__(self):
        self.scenarios = {}
        self.active_conversations = {}
    
    def register_scenario(self, name: str, scenario_func):
        """Register a new scenario"""
        self.scenarios[name] = scenario_func
    
    def run_scenario(self, name: str, **kwargs):
        """Run a registered scenario"""
        if name not in self.scenarios:
            raise ValueError(f"Scenario '{name}' not found")
        
        return self.scenarios[name](**kwargs)
    
    def list_scenarios(self):
        """List all available scenarios"""
        return list(self.scenarios.keys())

# Global scenario manager
scenario_manager = PrisonScenarioManager()

def education_program_inquiry():
    """Scenario: Inmate asks guard about education programs"""
    
    inmate = PrisonInmateAgent(
        name="Alex Rivera",
        crime_type="DUI causing injury",
        sentence_length="18 months",
        background="College graduate, first-time offender",
        personality="Eager to learn, respectful, anxious about future"
    )
    
    guard = PrisonGuardAgent(
        name="Officer Martinez",
        rank="Correctional Officer II",
        years_experience=8,
        approach_style="supportive and informative",
        specialization="education programs"
    )
    
    chat = PrisonGroupChat(
        scenario_name="Education Program Inquiry",
        participants=[inmate, guard]
    )
    
    return chat.start_conversation(
        "Officer Martinez, I hope you have a moment. I've been thinking about my future "
        "and I'd really like to get information about the GED program here. I dropped out "
        "of high school and this seems like a good opportunity to complete my education. "
        "Could you tell me about the requirements and how to apply?",
        initiator=inmate
    )

def medical_emergency_response():
    """Scenario: Medical emergency requiring hierarchical response"""
    
    inmate = PrisonInmateAgent(
        name="Frank Morrison",
        crime_type="Tax evasion",
        sentence_length="4 years",
        background="67-year-old with heart condition",
        personality="Polite, concerned about health"
    )
    
    guard = PrisonGuardAgent(
        name="Officer Chen",
        rank="Correctional Officer I",
        years_experience=2,
        approach_style="by-the-book, careful",
        specialization="medical response"
    )
    
    sergeant = PrisonGuardAgent(
        name="Sergeant Williams",
        rank="Correctional Sergeant",
        years_experience=12,
        approach_style="experienced decision-maker",
        specialization="emergency response"
    )
    
    warden = WardenAgent(name="Warden Mitchell")
    
    chat = PrisonGroupChat(
        scenario_name="Medical Emergency Response",
        participants=[inmate, guard, sergeant, warden]
    )
    
    return chat.start_conversation(
        "Officer Chen, I'm not feeling well. I'm having chest pains and I'm worried "
        "it might be my heart. I need medical attention right away.",
        initiator=inmate
    )

def conflict_resolution_session():
    """Scenario: Conflict between inmates requiring mediation"""
    
    inmate1 = PrisonInmateAgent(
        name="Carlos Mendez",
        crime_type="Racketeering",
        sentence_length="8 years",
        background="Former gang leader, street smart",
        personality="Proud, defensive, but capable of reason"
    )
    
    inmate2 = PrisonInmateAgent(
        name="David Chen",
        crime_type="Embezzlement",
        sentence_length="3 years",
        background="White-collar criminal, educated",
        personality="Analytical, non-confrontational, seeks fairness"
    )
    
    counselor = PrisonGuardAgent(
        name="Counselor Brown",
        rank="Correctional Counselor",
        years_experience=7,
        approach_style="therapeutic and mediating",
        specialization="conflict resolution"
    )
    
    sergeant = PrisonGuardAgent(
        name="Sergeant Davis",
        rank="Correctional Sergeant",
        years_experience=15,
        approach_style="firm but fair",
        specialization="discipline and order"
    )
    
    chat = PrisonGroupChat(
        scenario_name="Conflict Resolution Session",
        participants=[inmate1, inmate2, counselor, sergeant]
    )
    
    return chat.start_conversation(
        "Gentlemen, we're here because there was an incident in the recreation area yesterday. "
        "Carlos, you and David had a disagreement that escalated. We need to resolve this "
        "before it becomes a bigger problem. Let's start by having each of you explain "
        "your perspective on what happened.",
        initiator=counselor
    )

def family_visit_preparation():
    """Scenario: Preparing inmate for family visit with counselor guidance"""
    
    inmate = PrisonInmateAgent(
        name="Lisa Williams",
        crime_type="Assault (domestic violence case)",
        sentence_length="2 years",
        background="Mother of three, children in foster care",
        personality="Emotional, regretful, desperate to reconnect with children"
    )
    
    counselor = PrisonGuardAgent(
        name="Counselor Johnson",
        rank="Family Services Counselor",
        years_experience=10,
        approach_style="empathetic and supportive",
        specialization="family reunification"
    )
    
    social_worker = PrisonGuardAgent(
        name="Ms. Rodriguez",
        rank="Social Worker",
        years_experience=8,
        approach_style="professional advocate",
        specialization="child welfare"
    )
    
    chat = PrisonGroupChat(
        scenario_name="Family Visit Preparation",
        participants=[inmate, counselor, social_worker]
    )
    
    return chat.start_conversation(
        "Lisa, your children's caseworker has approved a supervised visit next week. "
        "This is a big step, and we want to help you prepare. It's been six months "
        "since you've seen them. Let's talk about what to expect and how to make "
        "this visit positive for everyone, especially the children.",
        initiator=counselor
    )

def policy_change_announcement():
    """Scenario: Warden announces new policy to staff and inmates"""
    
    warden = WardenAgent(name="Warden Mitchell")
    
    lieutenant = PrisonGuardAgent(
        name="Lieutenant Parker",
        rank="Correctional Lieutenant",
        years_experience=18,
        approach_style="administrative and procedural",
        specialization="policy implementation"
    )
    
    guard = PrisonGuardAgent(
        name="Officer Thompson",
        rank="Correctional Officer II",
        years_experience=6,
        approach_style="practical and questioning",
        specialization="general population"
    )
    
    inmate_rep = PrisonInmateAgent(
        name="Robert Hayes",
        crime_type="Second-degree murder",
        sentence_length="Life with possibility of parole",
        background="Long-term inmate, respected by peers",
        personality="Thoughtful, articulate, advocates for inmates"
    )
    
    chat = PrisonGroupChat(
        scenario_name="Policy Change Announcement",
        participants=[warden, lieutenant, guard, inmate_rep]
    )
    
    return chat.start_conversation(
        "I've called this meeting to announce an important policy change regarding "
        "recreational time and programming. Effective next month, we're extending "
        "evening recreation hours by one hour and adding new educational programming. "
        "This change comes after reviewing our rehabilitation outcomes and inmate feedback. "
        "I want to discuss implementation and address any concerns.",
        initiator=warden
    )

def crisis_management_drill():
    """Scenario: Emergency lockdown drill with multiple stakeholders"""
    
    warden = WardenAgent(name="Warden Mitchell")
    
    captain = PrisonGuardAgent(
        name="Captain Rodriguez",
        rank="Correctional Captain",
        years_experience=20,
        approach_style="tactical and decisive",
        specialization="emergency management"
    )
    
    sergeant = PrisonGuardAgent(
        name="Sergeant Kim",
        rank="Correctional Sergeant",
        years_experience=10,
        approach_style="calm under pressure",
        specialization="crisis response"
    )
    
    guard = PrisonGuardAgent(
        name="Officer Jackson",
        rank="Correctional Officer III",
        years_experience=15,
        approach_style="experienced and reliable",
        specialization="security operations"
    )
    
    medical = PrisonGuardAgent(
        name="Nurse Patterson",
        rank="Medical Staff",
        years_experience=12,
        approach_style="medical professional",
        specialization="emergency medical response"
    )
    
    chat = PrisonGroupChat(
        scenario_name="Crisis Management Drill",
        participants=[warden, captain, sergeant, guard, medical]
    )
    
    return chat.start_conversation(
        "This is a drill scenario: We have reports of a disturbance in Cell Block C "
        "with potential injuries. I need immediate status reports and coordinated response. "
        "Captain Rodriguez, initiate lockdown procedures. Sergeant Kim, secure the area. "
        "Officer Jackson, account for all inmates. Nurse Patterson, prepare for potential casualties. "
        "Let's execute our emergency protocols.",
        initiator=warden
    )

# Register all scenarios
scenario_manager.register_scenario("education_inquiry", education_program_inquiry)
scenario_manager.register_scenario("medical_emergency", medical_emergency_response)
scenario_manager.register_scenario("conflict_resolution", conflict_resolution_session)
scenario_manager.register_scenario("family_visit", family_visit_preparation)
scenario_manager.register_scenario("policy_announcement", policy_change_announcement)
scenario_manager.register_scenario("crisis_drill", crisis_management_drill)

def run_demo_scenarios():
    """Run demonstration of various prison scenarios"""
    
    if not AUTOGEN_AVAILABLE:
        print("❌ AutoGen not available. Please install: pip install pyautogen")
        return False
    
    print("🏢 Prison Scenarios Demo with AutoGen")
    print("=" * 50)
    
    scenarios_to_demo = [
        ("education_inquiry", "Education Program Inquiry"),
        ("conflict_resolution", "Conflict Resolution Session"),
        ("policy_announcement", "Policy Change Announcement")
    ]
    
    for scenario_key, scenario_name in scenarios_to_demo:
        print(f"\n🎭 Running: {scenario_name}")
        print("-" * 40)
        
        try:
            result = scenario_manager.run_scenario(scenario_key)
            print(f"✅ {scenario_name} completed successfully")
        except Exception as e:
            print(f"❌ Error in {scenario_name}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n🎉 All demo scenarios completed!")
    return True

if __name__ == "__main__":
    run_demo_scenarios()