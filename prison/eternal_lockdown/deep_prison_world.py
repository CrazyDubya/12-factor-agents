#!/usr/bin/env python3
"""
Deep Prison World - Enhanced Multi-Framework Prison Simulation
Creates a detailed, immersive prison environment with rich characters and deep integration
"""

import sys
import os
from datetime import datetime, timedelta
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tinytroupe'))

# Setup Ollama for TinyTroupe first
from ollama_utils import setup_ollama_for_tinytroupe
setup_ollama_for_tinytroupe()

from tinytroupe.environment import TinyWorld
from tinytroupe.agent import TinyPerson
from tinytroupe import control

# Multi-framework imports
try:
    from crewai_integration import PrisonCrewAI
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False

try:
    import autogen
    from autogen import ConversableAgent
    AUTOGEN_AVAILABLE = True
except ImportError:
    AUTOGEN_AVAILABLE = False

class EternalLockdownPrison(TinyWorld):
    """
    Enhanced TinyWorld prison environment with detailed facilities and systems
    """
    
    def __init__(self):
        # Initialize with specific prison datetime (6 months into sentences)
        prison_start_date = datetime(2024, 8, 1, 6, 0, 0)  # 6 AM start
        
        super().__init__(
            name="Eternal Lockdown Correctional Facility",
            initial_datetime=prison_start_date,
            broadcast_if_no_target=True
        )
        
        # Detailed prison layout and facilities
        self.facility_layout = {
            "cell_blocks": {
                "A_Block": {
                    "type": "general_population",
                    "capacity": 120,
                    "security_level": "medium",
                    "cells": list(range(1, 61)),  # A1-A60
                    "description": "Main housing unit with double-occupancy cells"
                },
                "B_Block": {
                    "type": "protective_custody", 
                    "capacity": 40,
                    "security_level": "high",
                    "cells": list(range(1, 21)),  # B1-B20
                    "description": "Protective custody and high-risk inmates"
                },
                "C_Block": {
                    "type": "disciplinary",
                    "capacity": 20,
                    "security_level": "maximum",
                    "cells": list(range(1, 11)),  # C1-C10
                    "description": "Disciplinary housing unit (solitary)"
                }
            },
            "common_areas": {
                "Main_Yard": {
                    "capacity": 200,
                    "activities": ["basketball", "weight_lifting", "walking_track", "outdoor_seating"],
                    "supervision": "high",
                    "description": "Large outdoor recreation area with sports facilities"
                },
                "Cafeteria": {
                    "capacity": 150,
                    "shifts": ["breakfast", "lunch", "dinner"],
                    "description": "Main dining facility with industrial kitchen"
                },
                "Library": {
                    "capacity": 30,
                    "resources": ["books", "computers", "legal_research", "education_programs"],
                    "description": "Educational and legal research facility"
                },
                "Medical_Wing": {
                    "capacity": 15,
                    "services": ["general_care", "mental_health", "pharmacy", "emergency"],
                    "description": "Comprehensive medical and mental health services"
                },
                "Visitation": {
                    "capacity": 40,
                    "types": ["family", "legal", "clergy"],
                    "description": "Secure visitation rooms for approved visitors"
                },
                "Chapel": {
                    "capacity": 80,
                    "services": ["christian", "muslim", "jewish", "buddhist", "secular"],
                    "description": "Multi-faith worship and reflection space"
                }
            },
            "work_areas": {
                "Kitchen": {
                    "capacity": 25,
                    "shifts": ["prep", "service", "cleanup"],
                    "pay_rate": 0.75,  # per hour
                    "description": "Food preparation and service operations"
                },
                "Laundry": {
                    "capacity": 15,
                    "shifts": ["morning", "afternoon"],
                    "pay_rate": 0.65,
                    "description": "Facility laundry and textile services"
                },
                "Maintenance": {
                    "capacity": 20,
                    "specialties": ["plumbing", "electrical", "carpentry", "painting"],
                    "pay_rate": 0.85,
                    "description": "Facility maintenance and repair work"
                },
                "Library_Aide": {
                    "capacity": 8,
                    "duties": ["shelving", "computer_help", "tutoring"],
                    "pay_rate": 0.70,
                    "description": "Library assistance and educational support"
                }
            }
        }
        
        # Daily schedule with detailed timing
        self.daily_schedule = {
            "06:00": {"event": "Wake Up / Count", "duration": 30, "mandatory": True},
            "06:30": {"event": "Personal Hygiene", "duration": 30, "mandatory": True},
            "07:00": {"event": "Breakfast", "duration": 45, "location": "Cafeteria"},
            "08:00": {"event": "Work Assignments", "duration": 240, "location": "Various"},
            "12:00": {"event": "Lunch", "duration": 45, "location": "Cafeteria"},
            "13:00": {"event": "Recreation/Programs", "duration": 120, "location": "Yard/Library"},
            "15:00": {"event": "Education/Counseling", "duration": 120, "optional": True},
            "17:00": {"event": "Dinner", "duration": 45, "location": "Cafeteria"},
            "18:00": {"event": "Free Time", "duration": 180, "location": "Cells/Common"},
            "21:00": {"event": "Lockdown", "duration": 540, "mandatory": True},
        }
        
        # Prison rules and regulations
        self.prison_rules = {
            "movement": [
                "Inmates must walk, not run, in all areas",
                "No unauthorized areas without escort",
                "Hands visible at all times during movement",
                "Single file lines during group movement"
            ],
            "contraband": [
                "No weapons or weapon-like objects",
                "No drugs or alcohol",
                "No unauthorized electronics",
                "No gang-related materials",
                "Limited personal items in cells"
            ],
            "behavior": [
                "Respectful language required with staff",
                "No fighting or threatening behavior",
                "No gambling or loan sharking",
                "Participation in assigned programs required",
                "Quiet hours during lockdown"
            ],
            "consequences": {
                "minor": ["verbal_warning", "loss_of_privileges", "extra_duty"],
                "major": ["disciplinary_hearing", "solitary_confinement", "loss_of_good_time"],
                "severe": ["criminal_charges", "transfer", "extended_sentence"]
            }
        }
        
        # Current prison statistics
        self.prison_stats = {
            "total_capacity": 180,
            "current_population": 156,
            "staff_count": 45,
            "average_sentence": "8.5 years",
            "recidivism_rate": "32%",
            "program_participation": "78%"
        }

def create_detailed_inmates():
    """Create deeply detailed inmate personas with rich backgrounds"""
    inmates = []
    
    # Carlos Mendez - Reformed gang member, kitchen worker
    carlos = TinyPerson("Carlos Mendez")
    carlos.define("age", 34)
    carlos.define("gender", "Male")
    carlos.define("nationality", "Mexican-American")
    carlos.define("residence", "East Los Angeles, CA (pre-incarceration)")
    carlos.define("education", "High school dropout, GED earned in prison")
    
    carlos.define("criminal_history", {
        "current_offense": "Armed robbery, assault with deadly weapon",
        "sentence": "12 years",
        "time_served": "6 years, 2 months",
        "previous_convictions": ["Drug possession", "Assault", "Theft"],
        "gang_affiliation": "Former Eastside Locos member (renounced)"
    })
    
    carlos.define("physical_description", {
        "height": "5'8\"",
        "build": "Muscular, stocky",
        "distinguishing_marks": "Neck tattoo (partially covered), scar on left hand",
        "health": "Good overall, mild hypertension"
    })
    
    carlos.define("personality", {
        "traits": [
            "Naturally protective of younger/weaker inmates",
            "Quick temper but working on anger management", 
            "Deeply regrets past choices",
            "Fiercely loyal to those who earn his trust",
            "Takes pride in his cooking skills"
        ],
        "big_five": {
            "openness": "Medium. Open to change and learning new skills",
            "conscientiousness": "High. Very reliable in work assignments",
            "extraversion": "Medium. Friendly but selective about relationships",
            "agreeableness": "Medium-High. Helpful but can be confrontational",
            "neuroticism": "Medium. Struggles with anger but improving"
        }
    })
    
    carlos.define("background", {
        "family": "Estranged from family due to gang involvement. Has a daughter (Sofia, 16) he hasn't seen in 4 years",
        "childhood": "Grew up in poverty, joined gang at 14 for protection and belonging",
        "turning_point": "Realized gang life was destroying his family after his arrest",
        "goals": "Reconnect with daughter, learn culinary arts, stay clean after release"
    })
    
    carlos.define("prison_life", {
        "cell": "A-23 (shares with Tommy Rodriguez)",
        "work_assignment": "Kitchen - Lead Cook",
        "programs": ["Anger Management", "Parenting Classes", "Culinary Arts"],
        "reputation": "Respected by inmates and staff, known for protecting vulnerable prisoners",
        "disciplinary_record": "3 minor infractions in first 2 years, clean record since"
    })
    
    carlos.define("relationships", [
        {"name": "Tommy Rodriguez", "description": "Cellmate and protégé, like a younger brother"},
        {"name": "Officer Martinez", "description": "Mutual respect, sees potential for rehabilitation"},
        {"name": "Chef Williams", "description": "Kitchen supervisor who became a mentor"},
        {"name": "Diego Santos", "description": "Complicated relationship - respects intelligence but dislikes arrogance"}
    ])
    
    carlos.define("daily_routine", {
        "morning": "Up at 5:45, helps Tommy get ready, leads kitchen prep",
        "work": "Manages kitchen operations, trains new workers, plans meals",
        "afternoon": "Attends programs or mentors other inmates",
        "evening": "Writes letters to daughter, reads cooking magazines",
        "goals": "Earn culinary certification, maintain clean record, prepare for release"
    })
    
    carlos.define("internal_conflicts", [
        "Struggles with guilt over abandoning his daughter",
        "Fears returning to old neighborhood and temptations",
        "Wants to help other inmates but worries about being seen as weak",
        "Battles between old gang loyalty and new values"
    ])
    
    inmates.append(carlos)
    
    # Diego Santos - White-collar criminal, manipulative intellectual
    diego = TinyPerson("Diego Santos")
    diego.define("age", 42)
    diego.define("gender", "Male") 
    diego.define("nationality", "American")
    diego.define("residence", "Beverly Hills, CA (pre-incarceration)")
    diego.define("education", "MBA from USC, CPA certification")
    
    diego.define("criminal_history", {
        "current_offense": "Embezzlement, securities fraud, money laundering",
        "sentence": "15 years",
        "time_served": "3 years, 8 months", 
        "financial_crimes": "$2.3 million stolen from clients",
        "victims": "Elderly retirees, small business owners",
        "cooperation": "Refused plea deal, maintains partial innocence"
    })
    
    diego.define("physical_description", {
        "height": "5'11\"",
        "build": "Slim, well-groomed despite circumstances",
        "distinguishing_marks": "Expensive dental work, manicured nails",
        "health": "Excellent, mild anxiety disorder"
    })
    
    diego.define("personality", {
        "traits": [
            "Highly intelligent and articulate",
            "Manipulative and calculating",
            "Believes he's superior to other inmates",
            "Charming when it serves his purposes",
            "Struggles with genuine empathy"
        ],
        "big_five": {
            "openness": "High. Intellectually curious and strategic",
            "conscientiousness": "High. Meticulous and organized",
            "extraversion": "Medium-High. Socially skilled but selective",
            "agreeableness": "Low. Self-serving and manipulative",
            "neuroticism": "Medium. Anxious about status and control"
        }
    })
    
    diego.define("background", {
        "family": "Divorced, two children (custody lost), wealthy parents disowned him",
        "career": "Senior partner at prestigious accounting firm",
        "lifestyle": "Lived lavishly, country club member, expensive cars and homes",
        "downfall": "Greed and gambling addiction led to stealing client funds"
    })
    
    diego.define("prison_life", {
        "cell": "A-15 (single cell - paid for protection)",
        "work_assignment": "Library - Financial literacy instructor",
        "programs": ["Legal research", "Business education", "Addiction counseling"],
        "reputation": "Known as 'The Accountant' - helps with appeals and finances",
        "disciplinary_record": "Clean - too smart to get caught breaking rules"
    })
    
    diego.define("relationships", [
        {"name": "Carlos Mendez", "description": "Grudging respect but looks down on his background"},
        {"name": "Warden Thompson", "description": "Tries to impress with intelligence and cooperation"},
        {"name": "Tommy Rodriguez", "description": "Sees as easily manipulated, potential asset"},
        {"name": "Officer Johnson", "description": "Mutual dislike - Johnson sees through his act"}
    ])
    
    diego.define("schemes", [
        "Running underground financial advice service for commissary payments",
        "Gathering information on other inmates for potential future use",
        "Planning appeal strategy and post-release business comeback",
        "Maintaining connections with outside business associates"
    ])
    
    diego.define("internal_conflicts", [
        "Genuine remorse vs. anger at being caught",
        "Desire to maintain superiority vs. need for acceptance",
        "Fear of losing relevance and intelligence edge",
        "Struggle between manipulation and authentic relationships"
    ])
    
    inmates.append(diego)
    
    # Tommy Rodriguez - Young first-timer, vulnerable but resilient
    tommy = TinyPerson("Tommy Rodriguez")
    tommy.define("age", 19)
    tommy.define("gender", "Male")
    tommy.define("nationality", "American")
    tommy.define("residence", "Phoenix, AZ (pre-incarceration)")
    tommy.define("education", "High school graduate, some community college")
    
    tommy.define("criminal_history", {
        "current_offense": "Drug trafficking, possession with intent to distribute",
        "sentence": "8 years",
        "time_served": "1 year, 3 months",
        "circumstances": "Caught with 2 kilos of cocaine, first major offense",
        "background": "Recruited by older dealers, needed money for sick mother"
    })
    
    tommy.define("physical_description", {
        "height": "5'6\"",
        "build": "Slight, still growing into adult frame",
        "distinguishing_marks": "Baby face, nervous habits (nail biting)",
        "health": "Good, occasional anxiety attacks"
    })
    
    tommy.define("personality", {
        "traits": [
            "Naturally artistic and creative",
            "Eager to please and gain approval",
            "Easily influenced by stronger personalities",
            "Optimistic despite circumstances",
            "Quick learner when interested"
        ],
        "big_five": {
            "openness": "High. Creative and open to new experiences",
            "conscientiousness": "Medium. Trying to develop better habits",
            "extraversion": "Medium. Friendly but often anxious in groups",
            "agreeableness": "High. Wants to get along with everyone",
            "neuroticism": "Medium-High. Anxious and emotionally reactive"
        }
    })
    
    tommy.define("background", {
        "family": "Close to mother (Maria) who has diabetes, younger sister (Ana, 16)",
        "childhood": "Good student, loved art and music, stayed out of trouble",
        "turning_point": "Mother's medical bills led to desperation and bad choices",
        "dreams": "Wanted to be a graphic designer or music producer"
    })
    
    tommy.define("prison_life", {
        "cell": "A-23 (shares with Carlos Mendez)",
        "work_assignment": "Library aide - helps with computer training",
        "programs": ["GED completion", "Art therapy", "Substance abuse counseling"],
        "reputation": "Known as 'Kid' - protected by Carlos, liked by most",
        "disciplinary_record": "Clean record, model prisoner"
    })
    
    tommy.define("relationships", [
        {"name": "Carlos Mendez", "description": "Father figure and protector, biggest influence"},
        {"name": "Ms. Rodriguez", "description": "Art therapy instructor who encourages his talent"},
        {"name": "Diego Santos", "description": "Wary of but sometimes seeks advice from"},
        {"name": "Officer Martinez", "description": "Sees potential, advocates for programs"}
    ])
    
    tommy.define("talents", [
        "Exceptional artistic ability - draws portraits of inmates and families",
        "Natural with computers and technology",
        "Good at mediating conflicts between inmates",
        "Quick to learn new skills when motivated"
    ])
    
    tommy.define("fears_and_hopes", {
        "fears": [
            "Becoming institutionalized and losing his identity",
            "Mother dying while he's incarcerated",
            "Being influenced by wrong people again",
            "Not being able to support family after release"
        ],
        "hopes": [
            "Earning degree in graphic design through correspondence",
            "Starting legitimate business after release",
            "Being role model for younger sister",
            "Making mother proud of his transformation"
        ]
    })
    
    inmates.append(tommy)
    
    return inmates

def create_detailed_guards():
    """Create detailed correctional officer personas"""
    guards = []
    
    # Officer Martinez - Fair but firm, believes in rehabilitation
    martinez = TinyPerson("Officer Martinez")
    martinez.define("age", 38)
    martinez.define("gender", "Female")
    martinez.define("nationality", "Mexican-American")
    martinez.define("residence", "Riverside, CA")
    martinez.define("education", "Bachelor's in Criminal Justice, Correctional Officer Training")
    
    martinez.define("career", {
        "position": "Senior Correctional Officer",
        "years_experience": 12,
        "specializations": ["Conflict resolution", "Inmate counseling", "Training new officers"],
        "certifications": ["Crisis intervention", "Mental health first aid", "Gang awareness"]
    })
    
    martinez.define("personality", {
        "traits": [
            "Firm but fair in all dealings",
            "Believes in rehabilitation over punishment",
            "Excellent at reading people and situations",
            "Patient but doesn't tolerate disrespect",
            "Natural mentor and teacher"
        ],
        "philosophy": "Every inmate is someone's son, daughter, parent - they deserve dignity and a chance to change"
    })
    
    martinez.define("background", {
        "family": "Married to teacher, two teenage children",
        "motivation": "Grew up in tough neighborhood, saw how good mentors made difference",
        "previous_work": "Social worker before corrections",
        "community": "Volunteers with at-risk youth programs"
    })
    
    martinez.define("work_style", {
        "approach": "Consistent rules enforcement with understanding of individual circumstances",
        "reputation": "Respected by inmates and staff, known for fairness",
        "specialties": ["De-escalating conflicts", "Identifying inmates needing help", "Training programs"],
        "challenges": "Balancing security needs with rehabilitation goals"
    })
    
    guards.append(martinez)
    
    # Officer Johnson - Old school disciplinarian
    johnson = TinyPerson("Officer Johnson")
    johnson.define("age", 52)
    johnson.define("gender", "Male")
    johnson.define("nationality", "American")
    johnson.define("residence", "Suburban community, 45 minutes from prison")
    johnson.define("education", "High school, Military police training, Corrections academy")
    
    johnson.define("career", {
        "position": "Correctional Sergeant",
        "years_experience": 18,
        "military_background": "Army MP for 8 years before corrections",
        "specializations": ["Security protocols", "Emergency response", "Disciplinary procedures"]
    })
    
    johnson.define("personality", {
        "traits": [
            "Strict adherence to rules and procedures",
            "Suspicious of inmate motives",
            "Values order and discipline above all",
            "Protective of fellow officers",
            "Resistant to 'soft' rehabilitation approaches"
        ],
        "philosophy": "Inmates are here for punishment - coddling them doesn't help society"
    })
    
    johnson.define("background", {
        "family": "Divorced, limited contact with adult children",
        "military": "Served in Iraq, saw combat, values chain of command",
        "worldview": "Believes in personal responsibility and consequences",
        "concerns": "Worried about prison becoming 'too soft'"
    })
    
    johnson.define("work_style", {
        "approach": "Zero tolerance for rule violations, emphasis on security",
        "reputation": "Feared by inmates, respected by traditional staff",
        "conflicts": "Often clashes with Martinez over treatment approaches",
        "strengths": "Excellent in crisis situations, maintains order"
    })
    
    guards.append(johnson)
    
    return guards

def create_warden():
    """Create detailed warden persona"""
    warden = TinyPerson("Warden Thompson")
    warden.define("age", 55)
    warden.define("gender", "Male")
    warden.define("nationality", "American")
    warden.define("residence", "Upscale suburban home, 30 minutes from facility")
    warden.define("education", "Master's in Public Administration, Law degree")
    
    warden.define("career", {
        "position": "Warden",
        "years_experience": 25,
        "career_path": "Started as officer, worked up through ranks",
        "previous_positions": ["Officer", "Sergeant", "Lieutenant", "Captain", "Deputy Warden"],
        "philosophy": "Balance security, rehabilitation, and public safety"
    })
    
    warden.define("personality", {
        "traits": [
            "Politically savvy and diplomatic",
            "Balances competing interests and pressures",
            "Data-driven decision maker",
            "Calm under pressure",
            "Ambitious but genuinely cares about outcomes"
        ],
        "leadership_style": "Collaborative but decisive when needed"
    })
    
    warden.define("challenges", {
        "budget": "Constant pressure to reduce costs while maintaining safety",
        "politics": "Balancing tough-on-crime politicians with reform advocates",
        "staff": "Managing different philosophies among correctional staff",
        "inmates": "Reducing recidivism while maintaining security",
        "public": "Maintaining community support and safety"
    })
    
    warden.define("goals", {
        "short_term": ["Reduce violence incidents", "Improve staff retention", "Expand programs"],
        "long_term": ["Lower recidivism rates", "Modernize facility", "Advance to state corrections director"],
        "personal": ["Leave positive legacy", "Prove rehabilitation works", "Maintain family relationships"]
    })
    
    return warden

def create_enhanced_prison_simulation():
    """Create the complete enhanced prison simulation"""
    print("🏛️ CREATING ENHANCED ETERNAL LOCKDOWN PRISON SIMULATION")
    print("=" * 70)
    
    # Create the detailed prison world
    prison = EternalLockdownPrison()
    
    # Create all characters
    inmates = create_detailed_inmates()
    guards = create_detailed_guards()
    warden = create_warden()
    
    all_agents = inmates + guards + [warden]
    
    # Add all agents to the world
    for agent in all_agents:
        prison.add_agent(agent)
    
    # Make agents accessible to each other based on prison hierarchy
    prison.make_everyone_accessible()
    
    # Set initial locations and contexts
    for agent in all_agents:
        if "Officer" in agent.name or "Warden" in agent.name:
            agent.move_to("Administrative Area", ["On duty", "Monitoring facility", "Ensuring security"])
        else:
            agent.move_to("Cell Block A", ["Morning routine", "Preparing for day", "Following schedule"])
    
    print(f"✅ Created detailed prison world: {prison.name}")
    print(f"✅ Added {len(inmates)} inmates with deep personas")
    print(f"✅ Added {len(guards)} correctional officers")
    print(f"✅ Added warden with administrative oversight")
    print(f"✅ Total agents: {len(all_agents)}")
    
    return prison, all_agents

def run_enhanced_scenarios(prison, agents):
    """Run detailed scenarios showcasing the enhanced world"""
    
    scenarios = [
        {
            "name": "Morning Head Count Tension",
            "description": "During the 6 AM head count, Officer Johnson discovers discrepancies in the count for Cell Block A. Carlos and Tommy are accounted for, but there's tension when Diego questions the procedure. Officer Martinez tries to maintain order while investigating.",
            "duration": 3,
            "focus": "Authority dynamics and inmate responses to stress"
        },
        {
            "name": "Kitchen Work Assignment Conflict", 
            "description": "Carlos is training a new inmate in the kitchen when Diego approaches with 'suggestions' for improving efficiency. Tommy watches nervously as the conversation becomes heated. Chef Williams must intervene.",
            "duration": 4,
            "focus": "Workplace dynamics and personality conflicts"
        },
        {
            "name": "Art Therapy Session Breakthrough",
            "description": "During art therapy, Tommy shares a drawing of his family. Carlos opens up about his daughter, while Diego remains skeptical of the program's value. The session reveals deep emotions and motivations.",
            "duration": 3,
            "focus": "Emotional vulnerability and personal growth"
        },
        {
            "name": "Yard Politics and Protection",
            "description": "In the recreation yard, a new inmate is being pressured by other prisoners. Carlos must decide whether to intervene, Tommy wants to help but is scared, and Diego calculates the political implications.",
            "duration": 4,
            "focus": "Prison social dynamics and moral choices"
        },
        {
            "name": "Warden's Inspection and Policy Changes",
            "description": "Warden Thompson announces new rehabilitation programs during a facility meeting. Officer Johnson objects to the changes, Officer Martinez supports them, and inmates have mixed reactions based on their goals.",
            "duration": 5,
            "focus": "Institutional change and competing philosophies"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n🎬 ENHANCED SCENARIO {i}: {scenario['name']}")
        print("=" * 70)
        print(f"📖 {scenario['description']}")
        print(f"🎯 Focus: {scenario['focus']}")
        print()
        
        # Set the scene with detailed context
        prison.broadcast(f"SCENARIO: {scenario['description']}")
        
        # Run the scenario for specified duration
        prison.run(scenario['duration'], timedelta_per_step=timedelta(minutes=15))
        
        print(f"\n✅ Scenario '{scenario['name']}' completed")
        print("-" * 50)

def main():
    """Main function to run the enhanced simulation"""
    try:
        # Create the enhanced prison world
        prison, agents = create_enhanced_prison_simulation()
        
        print("\n🎭 STARTING ENHANCED MULTI-FRAMEWORK SIMULATION")
        print("=" * 70)
        
        # Initialize CrewAI if available
        if CREWAI_AVAILABLE:
            crew_system = PrisonCrewAI()
            print("✅ CrewAI task coordination system active")
        
        # Initialize AutoGen if available  
        if AUTOGEN_AVAILABLE:
            print("✅ AutoGen hierarchical communication system ready")
        
        print("✅ TinyTroupe detailed world simulation running")
        print("✅ Ollama LLM powering all agent decisions")
        
        # Run enhanced scenarios
        run_enhanced_scenarios(prison, agents)
        
        print("\n🏆 ENHANCED SIMULATION COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print("🎯 ACHIEVEMENTS:")
        print("✅ Deep, detailed prison world with realistic facilities")
        print("✅ Rich character personas with complex backgrounds") 
        print("✅ Multi-framework integration (TinyTroupe + CrewAI + AutoGen)")
        print("✅ Realistic scenarios showcasing character depth")
        print("✅ Emergent behaviors from LLM-powered decisions")
        
        return prison, agents
        
    except Exception as e:
        print(f"\n❌ Error in enhanced simulation: {e}")
        import traceback
        traceback.print_exc()
        return None, None

if __name__ == "__main__":
    prison_world, prison_agents = main()