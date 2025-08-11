#!/usr/bin/env python3
"""
Scenario-Based Planning for Urban Family
Creates specific scenarios combining multiple risk factors
"""

import pandas as pd
import json
from datetime import datetime, timedelta
from disaster_probability_matrix import DisasterProbabilityMatrix

class ScenarioPlanner:
    def __init__(self):
        self.matrix = DisasterProbabilityMatrix()
        self.df = self.matrix.generate_matrix()
        self.df['prob_numeric'] = self.df['Annual_Probability'].astype(float)
    
    def create_realistic_scenarios(self):
        """Create realistic multi-event scenarios"""
        scenarios = {
            "Winter Storm Cascade": {
                "description": "Severe winter weather triggers multiple infrastructure failures",
                "trigger_event": "Blizzard/ice storm",
                "cascading_events": [
                    "Extended power outage",
                    "Water service disruption", 
                    "School closure (extended)",
                    "Public transport strike",
                    "Home heating failure"
                ],
                "timeline": "3-7 days",
                "probability": 0.12,
                "total_impact": 8,
                "preparation_time": "24-48 hours warning",
                "critical_needs": [
                    "Alternative heating source",
                    "Water storage (7+ days)",
                    "Non-perishable food",
                    "Battery power/generator",
                    "Childcare plan during school closure"
                ],
                "decision_points": [
                    "Hour 0: Storm warning issued - begin preparations",
                    "Hour 12: Power outage begins - activate backup systems",
                    "Day 2: Water service fails - switch to stored water",
                    "Day 3: School closure extended - implement childcare plan",
                    "Day 5: Transportation disrupted - work from home protocols"
                ]
            },
            
            "Economic Shock Wave": {
                "description": "Job loss during economic downturn with health emergency",
                "trigger_event": "Temporary job loss",
                "cascading_events": [
                    "Financial strain",
                    "Serious illness (parent)",
                    "Extended unemployment",
                    "Home repairs needed",
                    "Relationship stress"
                ],
                "timeline": "3-12 months",
                "probability": 0.08,
                "total_impact": 9,
                "preparation_time": "Varies - some sudden, some gradual",
                "critical_needs": [
                    "6+ month emergency fund",
                    "Comprehensive health insurance",
                    "Updated resume and job search plan",
                    "Debt reduction strategy",
                    "Family support system"
                ],
                "decision_points": [
                    "Week 1: Job loss occurs - file unemployment, review finances",
                    "Month 1: Health issue emerges - prioritize medical care",
                    "Month 2: Savings depleting - reduce expenses, seek assistance",
                    "Month 4: Home repairs needed - defer or find low-cost solutions",
                    "Month 6: Relationship stress - seek counseling, family support"
                ]
            },
            
            "Health Crisis Cluster": {
                "description": "Child injury leads to extended family health challenges",
                "trigger_event": "Child injury (minor)",
                "cascading_events": [
                    "Hospital emergency",
                    "Extended illness (parent)",
                    "Childcare emergency",
                    "Workplace emergency",
                    "Financial strain"
                ],
                "timeline": "2-8 weeks",
                "probability": 0.15,
                "total_impact": 7,
                "preparation_time": "Immediate response required",
                "critical_needs": [
                    "Emergency childcare network",
                    "Flexible work arrangements",
                    "Health savings account",
                    "Medical emergency plan",
                    "Family support coordination"
                ],
                "decision_points": [
                    "Hour 1: Injury occurs - emergency medical response",
                    "Day 1: Hospital treatment - coordinate work/childcare",
                    "Week 1: Parent illness develops - expand support network",
                    "Week 2: Work disruption - negotiate flexible arrangements",
                    "Month 1: Financial impact - review insurance, adjust budget"
                ]
            },
            
            "Infrastructure Domino Effect": {
                "description": "Cyber attack on utilities creates widespread disruption",
                "trigger_event": "Widespread blackout",
                "cascading_events": [
                    "Internet/cable outage",
                    "Water service disruption",
                    "Public transport strike",
                    "Workplace closure",
                    "School closure (extended)"
                ],
                "timeline": "1-3 weeks",
                "probability": 0.05,
                "total_impact": 8,
                "preparation_time": "No warning - sudden onset",
                "critical_needs": [
                    "Offline communication methods",
                    "Cash reserves",
                    "Manual backup systems",
                    "Community coordination",
                    "Alternative work/school arrangements"
                ],
                "decision_points": [
                    "Hour 1: Blackout begins - assess scope and duration",
                    "Hour 6: Communications down - activate manual systems",
                    "Day 2: Water systems fail - implement conservation",
                    "Day 5: Work/school closures - establish routines",
                    "Week 2: Extended duration - community resource sharing"
                ]
            },
            
            "Security Escalation": {
                "description": "Home break-in leads to broader security concerns",
                "trigger_event": "Home break-in",
                "cascading_events": [
                    "Identity theft",
                    "Legal issues",
                    "Relationship stress",
                    "Childcare disruption",
                    "Financial strain"
                ],
                "timeline": "1-6 months",
                "probability": 0.04,
                "total_impact": 7,
                "preparation_time": "Immediate response, long-term recovery",
                "critical_needs": [
                    "Enhanced security measures",
                    "Identity monitoring services",
                    "Legal assistance resources",
                    "Psychological support",
                    "Financial recovery plan"
                ],
                "decision_points": [
                    "Hour 1: Break-in discovered - police report, safety assessment",
                    "Day 1: Security upgrade - locks, alarms, cameras",
                    "Week 1: Identity monitoring - credit freeze, account reviews",
                    "Month 1: Legal issues emerge - attorney consultation",
                    "Month 3: Ongoing stress - family counseling, support groups"
                ]
            }
        }
        
        return scenarios
    
    def create_monthly_scenario_calendar(self):
        """Create month-by-month scenario planning calendar"""
        calendar = {}
        base_date = datetime.now()
        
        for month in range(12):
            month_date = base_date + timedelta(days=30*month)
            month_name = month_date.strftime("%B %Y")
            
            # Seasonal risk adjustments
            season_risks = self.get_seasonal_risks(month_date.month)
            
            calendar[month_name] = {
                "primary_risks": season_risks["high_probability"],
                "secondary_risks": season_risks["moderate_probability"],
                "preparation_focus": season_risks["preparation_focus"],
                "monthly_drills": season_risks["recommended_drills"],
                "supply_checks": season_risks["supply_maintenance"],
                "family_activities": season_risks["family_preparedness_activities"]
            }
        
        return calendar
    
    def get_seasonal_risks(self, month):
        """Get seasonal risk adjustments"""
        seasonal_data = {
            # Winter months (Dec, Jan, Feb)
            12: {"season": "winter", "weather_multiplier": 1.5, "health_multiplier": 1.3},
            1: {"season": "winter", "weather_multiplier": 1.5, "health_multiplier": 1.3},
            2: {"season": "winter", "weather_multiplier": 1.5, "health_multiplier": 1.3},
            
            # Spring months (Mar, Apr, May)
            3: {"season": "spring", "weather_multiplier": 1.2, "health_multiplier": 1.1},
            4: {"season": "spring", "weather_multiplier": 1.3, "health_multiplier": 1.0},
            5: {"season": "spring", "weather_multiplier": 1.2, "health_multiplier": 1.0},
            
            # Summer months (Jun, Jul, Aug)
            6: {"season": "summer", "weather_multiplier": 1.1, "health_multiplier": 0.9},
            7: {"season": "summer", "weather_multiplier": 1.2, "health_multiplier": 0.9},
            8: {"season": "summer", "weather_multiplier": 1.2, "health_multiplier": 0.9},
            
            # Fall months (Sep, Oct, Nov)
            9: {"season": "fall", "weather_multiplier": 1.1, "health_multiplier": 1.0},
            10: {"season": "fall", "weather_multiplier": 1.0, "health_multiplier": 1.1},
            11: {"season": "fall", "weather_multiplier": 1.1, "health_multiplier": 1.2}
        }
        
        season_info = seasonal_data[month]
        
        if season_info["season"] == "winter":
            return {
                "high_probability": ["Power outages", "Heating failures", "Flu/illness", "School closures"],
                "moderate_probability": ["Blizzards", "Water pipe freezing", "Car breakdowns"],
                "preparation_focus": "Heating, food storage, health supplies",
                "recommended_drills": "Cold weather emergency, power outage response",
                "supply_maintenance": "Check heating systems, winter clothing, emergency food",
                "family_preparedness_activities": "Winter safety education, indoor emergency games"
            }
        elif season_info["season"] == "spring":
            return {
                "high_probability": ["Severe storms", "Flooding", "Allergies", "Home repairs"],
                "moderate_probability": ["Tornadoes", "Power outages", "Basement flooding"],
                "preparation_focus": "Storm preparedness, home maintenance",
                "recommended_drills": "Severe weather response, evacuation procedures",
                "supply_maintenance": "Check storm supplies, clean gutters, test sump pumps",
                "family_preparedness_activities": "Weather safety education, emergency kit review"
            }
        elif season_info["season"] == "summer":
            return {
                "high_probability": ["Heat waves", "Thunderstorms", "Travel disruptions", "Childcare gaps"],
                "moderate_probability": ["Hurricanes", "Wildfires", "Air quality issues"],
                "preparation_focus": "Heat safety, travel preparedness, childcare backup",
                "recommended_drills": "Heat emergency response, evacuation with pets",
                "supply_maintenance": "Check cooling systems, travel emergency kits, sun protection",
                "family_preparedness_activities": "Summer safety rules, outdoor emergency skills"
            }
        else:  # fall
            return {
                "high_probability": ["Back-to-school illness", "Early storms", "Flu season prep"],
                "moderate_probability": ["Hurricane season", "Early winter weather", "Seasonal depression"],
                "preparation_focus": "Health preparedness, winter preparation",
                "recommended_drills": "School emergency procedures, family communication",
                "supply_maintenance": "Flu shots, winter supply check, heating system service",
                "family_preparedness_activities": "School safety review, family health planning"
            }
    
    def generate_action_timelines(self):
        """Generate specific action timelines for top scenarios"""
        scenarios = self.create_realistic_scenarios()
        action_timelines = {}
        
        for scenario_name, scenario in scenarios.items():
            timeline = {
                "scenario": scenario_name,
                "probability": scenario["probability"],
                "preparation_phase": {
                    "duration": "Ongoing",
                    "actions": [
                        f"Build emergency fund targeting {scenario['timeline']} duration",
                        f"Prepare supplies for {len(scenario['cascading_events'])} simultaneous issues",
                        "Create contact lists for all support services",
                        "Practice family communication procedures",
                        "Document all important information and procedures"
                    ]
                },
                "immediate_response": {
                    "duration": "First 24 hours",
                    "actions": scenario["decision_points"][:2]
                },
                "short_term_management": {
                    "duration": "Days 2-7",
                    "actions": scenario["decision_points"][2:4] if len(scenario["decision_points"]) > 2 else []
                },
                "long_term_recovery": {
                    "duration": "Week 2+",
                    "actions": scenario["decision_points"][4:] if len(scenario["decision_points"]) > 4 else []
                }
            }
            action_timelines[scenario_name] = timeline
        
        return action_timelines

def main():
    planner = ScenarioPlanner()
    
    print("SCENARIO-BASED PLANNING ANALYSIS")
    print("=" * 80)
    print("Urban Family Multi-Event Risk Scenarios\n")
    
    # Generate realistic scenarios
    scenarios = planner.create_realistic_scenarios()
    
    print("TOP 5 REALISTIC MULTI-EVENT SCENARIOS")
    print("-" * 50)
    
    for i, (name, scenario) in enumerate(scenarios.items(), 1):
        print(f"\n{i}. {name}")
        print(f"   Probability: {scenario['probability']*100:.1f}% annually")
        print(f"   Impact Level: {scenario['total_impact']}/10")
        print(f"   Duration: {scenario['timeline']}")
        print(f"   Description: {scenario['description']}")
        print(f"   Trigger: {scenario['trigger_event']}")
        print(f"   Cascading Events: {', '.join(scenario['cascading_events'][:3])}...")
        
        print(f"   Critical Preparations:")
        for prep in scenario['critical_needs'][:3]:
            print(f"     • {prep}")
    
    # Generate monthly calendar
    calendar = planner.create_monthly_scenario_calendar()
    
    print(f"\n\nMONTHLY PREPAREDNESS CALENDAR")
    print("-" * 50)
    
    for month, activities in list(calendar.items())[:6]:  # Show first 6 months
        print(f"\n{month}:")
        print(f"  Focus Risks: {', '.join(activities['primary_risks'])}")
        print(f"  Preparation Focus: {activities['preparation_focus']}")
        print(f"  Monthly Drill: {activities['recommended_drills']}")
    
    # Generate action timelines
    timelines = planner.generate_action_timelines()
    
    print(f"\n\nACTION TIMELINES FOR TOP SCENARIOS")
    print("-" * 50)
    
    for scenario_name, timeline in list(timelines.items())[:2]:  # Show top 2
        print(f"\n{scenario_name} Response Timeline:")
        print(f"  Preparation Phase: {timeline['preparation_phase']['duration']}")
        for action in timeline['preparation_phase']['actions'][:3]:
            print(f"    • {action}")
        
        print(f"  Immediate Response: {timeline['immediate_response']['duration']}")
        for action in timeline['immediate_response']['actions']:
            print(f"    • {action}")
    
    # Save all data
    all_data = {
        'scenarios': scenarios,
        'monthly_calendar': calendar,
        'action_timelines': timelines
    }
    
    with open('scenario_planning_data.json', 'w') as f:
        json.dump(all_data, f, indent=2, default=str)
    
    print(f"\n\nComplete scenario planning data saved to: scenario_planning_data.json")
    return all_data

if __name__ == "__main__":
    main()