#!/usr/bin/env python3
"""
Emergency Drill Simulator
Interactive disaster scenario training system with timed exercises and performance scoring
"""

import json
import sqlite3
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import threading

@dataclass
class DrillScenario:
    id: int
    name: str
    disaster_type: str
    difficulty: str
    duration_minutes: int
    objectives: List[str]
    decision_points: List[Dict]
    success_criteria: Dict
    family_roles: List[str]

@dataclass
class DrillResult:
    scenario_id: int
    participant_name: str
    start_time: str
    end_time: str
    decisions_made: List[Dict]
    objectives_completed: List[str]
    score: int
    time_taken: float
    lessons_learned: List[str]

class EmergencyDrillSimulator:
    def __init__(self, db_path: str = "drill_simulator.db"):
        self.db_path = db_path
        self.init_database()
        self.current_drill = None
        self.drill_timer = None
        self.decision_history = []
        
        self.scenarios = {
            "earthquake": {
                "phases": ["initial_shock", "aftershock", "evacuation", "shelter"],
                "time_pressure": "high",
                "injury_risk": "high"
            },
            "fire": {
                "phases": ["detection", "alert_family", "evacuation", "assembly"],
                "time_pressure": "extreme",
                "injury_risk": "extreme"
            },
            "flood": {
                "phases": ["warning", "preparation", "evacuation", "recovery"],
                "time_pressure": "medium",
                "injury_risk": "medium"
            },
            "power_outage": {
                "phases": ["detection", "assessment", "backup_systems", "communication"],
                "time_pressure": "low",
                "injury_risk": "low"
            },
            "tornado": {
                "phases": ["warning", "shelter", "impact", "assessment"],
                "time_pressure": "extreme",
                "injury_risk": "high"
            }
        }
    
    def init_database(self):
        """Initialize database for drill scenarios and results"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS drill_scenarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                disaster_type TEXT NOT NULL,
                difficulty TEXT,
                duration_minutes INTEGER,
                objectives TEXT,
                decision_points TEXT,
                success_criteria TEXT,
                family_roles TEXT,
                created_date TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS drill_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scenario_id INTEGER,
                participant_name TEXT,
                family_size INTEGER,
                start_time TEXT,
                end_time TEXT,
                decisions_made TEXT,
                objectives_completed TEXT,
                score INTEGER,
                time_taken REAL,
                performance_grade TEXT,
                lessons_learned TEXT,
                created_date TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (scenario_id) REFERENCES drill_scenarios (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS decision_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scenario_id INTEGER,
                decision_point TEXT,
                option_chosen TEXT,
                outcome TEXT,
                time_to_decide REAL,
                stress_level INTEGER,
                created_date TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (scenario_id) REFERENCES drill_scenarios (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS family_member_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                drill_result_id INTEGER,
                member_name TEXT,
                member_age INTEGER,
                assigned_role TEXT,
                actions_taken TEXT,
                performance_score INTEGER,
                FOREIGN KEY (drill_result_id) REFERENCES drill_results (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_earthquake_drill(self) -> int:
        """Create a comprehensive earthquake drill scenario"""
        objectives = [
            "Drop, cover, and hold within 5 seconds",
            "Secure all family members",
            "Turn off gas and electricity if safe",
            "Gather emergency supplies",
            "Evacuate to safe assembly point",
            "Account for all family members",
            "Check on neighbors",
            "Monitor emergency broadcasts"
        ]
        
        decision_points = [
            {
                "phase": "initial_shock",
                "time_limit": 10,
                "prompt": "The ground starts shaking violently. What's your immediate action?",
                "options": {
                    "A": {"action": "Drop, cover, hold under sturdy furniture", "score": 10, "risk": 0},
                    "B": {"action": "Run outside immediately", "score": 2, "risk": 8},
                    "C": {"action": "Stand in doorway", "score": 5, "risk": 3},
                    "D": {"action": "Try to grab valuables", "score": 0, "risk": 10}
                }
            },
            {
                "phase": "during_quake",
                "time_limit": 15,
                "prompt": "While under cover, you hear glass breaking. Your 6-year-old is crying in another room. What do you do?",
                "options": {
                    "A": {"action": "Stay under cover and call out reassuringly", "score": 10, "risk": 0},
                    "B": {"action": "Crawl to child while staying low", "score": 7, "risk": 3},
                    "C": {"action": "Run to child immediately", "score": 3, "risk": 7},
                    "D": {"action": "Wait silently", "score": 5, "risk": 2}
                }
            },
            {
                "phase": "after_shock",
                "time_limit": 30,
                "prompt": "Shaking stopped. You smell gas and see cracks in walls. Priority action?",
                "options": {
                    "A": {"action": "Shut off gas main immediately", "score": 10, "risk": 1},
                    "B": {"action": "Evacuate first, then utilities", "score": 8, "risk": 2},
                    "C": {"action": "Check injuries first", "score": 7, "risk": 3},
                    "D": {"action": "Call 911", "score": 3, "risk": 5}
                }
            },
            {
                "phase": "evacuation",
                "time_limit": 60,
                "prompt": "Building seems unstable. You need to evacuate. What do you grab? (Multiple items = more time)",
                "options": {
                    "A": {"action": "Emergency kit only (30 seconds)", "score": 10, "risk": 1},
                    "B": {"action": "Kit + important documents (60 seconds)", "score": 8, "risk": 2},
                    "C": {"action": "Kit + documents + electronics (90 seconds)", "score": 5, "risk": 5},
                    "D": {"action": "Try to pack everything (3 minutes)", "score": 1, "risk": 9}
                }
            },
            {
                "phase": "aftershock_warning",
                "time_limit": 5,
                "prompt": "AFTERSHOCK! You're outside but near buildings. Quick decision:",
                "options": {
                    "A": {"action": "Move to open area away from structures", "score": 10, "risk": 0},
                    "B": {"action": "Get in car", "score": 4, "risk": 5},
                    "C": {"action": "Stand against building wall", "score": 0, "risk": 10},
                    "D": {"action": "Re-enter building for supplies", "score": 0, "risk": 10}
                }
            }
        ]
        
        success_criteria = {
            "excellent": {"min_score": 45, "max_time": 5, "objectives": 7},
            "good": {"min_score": 35, "max_time": 8, "objectives": 5},
            "adequate": {"min_score": 25, "max_time": 12, "objectives": 4},
            "needs_improvement": {"min_score": 0, "max_time": 999, "objectives": 0}
        }
        
        family_roles = [
            "Incident Commander - Make decisions, coordinate family",
            "Safety Officer - Check for hazards, injuries",
            "Supply Manager - Gather emergency supplies",
            "Communications - Monitor radio, contact relatives",
            "Child Care - Keep children calm and safe"
        ]
        
        return self.save_scenario(
            "Earthquake Response Drill",
            "earthquake",
            "intermediate",
            15,
            objectives,
            decision_points,
            success_criteria,
            family_roles
        )
    
    def create_fire_evacuation_drill(self) -> int:
        """Create a home fire evacuation drill"""
        objectives = [
            "Detect fire/smoke within 30 seconds",
            "Alert all family members",
            "Evacuate in under 2 minutes",
            "Close doors behind you",
            "Meet at designated assembly point",
            "Call 911 from safe location",
            "Account for all family and pets",
            "Do NOT re-enter building"
        ]
        
        decision_points = [
            {
                "phase": "detection",
                "time_limit": 5,
                "prompt": "You smell smoke at 2 AM. Smoke alarm hasn't activated yet. First action?",
                "options": {
                    "A": {"action": "Yell 'FIRE!' and wake everyone", "score": 10, "risk": 0},
                    "B": {"action": "Investigate the source first", "score": 3, "risk": 7},
                    "C": {"action": "Grab fire extinguisher", "score": 5, "risk": 5},
                    "D": {"action": "Open windows for ventilation", "score": 0, "risk": 10}
                }
            },
            {
                "phase": "evacuation_route",
                "time_limit": 3,
                "prompt": "Smoke filling hallway. Primary exit route blocked. What now?",
                "options": {
                    "A": {"action": "Use secondary exit route immediately", "score": 10, "risk": 1},
                    "B": {"action": "Try to push through smoke", "score": 1, "risk": 10},
                    "C": {"action": "Go back and exit through window", "score": 8, "risk": 2},
                    "D": {"action": "Wait for rescue", "score": 2, "risk": 8}
                }
            },
            {
                "phase": "door_check",
                "time_limit": 2,
                "prompt": "At bedroom door. How do you check if it's safe to open?",
                "options": {
                    "A": {"action": "Feel door with back of hand first", "score": 10, "risk": 0},
                    "B": {"action": "Open immediately to escape", "score": 0, "risk": 10},
                    "C": {"action": "Look for smoke under door", "score": 7, "risk": 2},
                    "D": {"action": "Open slightly to peek", "score": 2, "risk": 8}
                }
            },
            {
                "phase": "family_member_missing",
                "time_limit": 5,
                "prompt": "Outside safe. 8-year-old not at assembly point. Other parent says they're still inside. You:",
                "options": {
                    "A": {"action": "Tell firefighters immediately - exact location", "score": 10, "risk": 0},
                    "B": {"action": "Re-enter to search yourself", "score": 0, "risk": 10},
                    "C": {"action": "Yell from outside", "score": 3, "risk": 2},
                    "D": {"action": "Wait and hope they escape", "score": 1, "risk": 8}
                }
            }
        ]
        
        success_criteria = {
            "excellent": {"min_score": 38, "max_time": 2, "objectives": 8},
            "good": {"min_score": 30, "max_time": 3, "objectives": 6},
            "adequate": {"min_score": 20, "max_time": 5, "objectives": 4},
            "needs_improvement": {"min_score": 0, "max_time": 999, "objectives": 0}
        }
        
        family_roles = [
            "Fire Marshal - Lead evacuation, ensure all exit",
            "Child Wrangler - Get kids out safely",
            "Pet Rescuer - Grab pets if immediately accessible",
            "911 Caller - Call from safe location",
            "Assembly Coordinator - Count heads at meeting point"
        ]
        
        return self.save_scenario(
            "Fire Evacuation Drill",
            "fire",
            "beginner",
            5,
            objectives,
            decision_points,
            success_criteria,
            family_roles
        )
    
    def create_severe_weather_drill(self) -> int:
        """Create a tornado/severe weather drill"""
        objectives = [
            "Monitor weather alerts",
            "Identify safe room/shelter area",
            "Gather emergency supplies to shelter",
            "Move family to shelter within 2 minutes of warning",
            "Protect heads and necks",
            "Stay in shelter until all-clear",
            "Check for damage after storm",
            "Report injuries/damage appropriately"
        ]
        
        decision_points = [
            {
                "phase": "watch_issued",
                "time_limit": 30,
                "prompt": "Tornado WATCH issued for your county. Current actions?",
                "options": {
                    "A": {"action": "Review plan, prep safe room, monitor weather", "score": 10, "risk": 0},
                    "B": {"action": "Continue normal activities", "score": 3, "risk": 5},
                    "C": {"action": "Evacuate immediately", "score": 2, "risk": 3},
                    "D": {"action": "Go outside to look at sky", "score": 0, "risk": 8}
                }
            },
            {
                "phase": "warning_issued",
                "time_limit": 10,
                "prompt": "Tornado WARNING! Funnel cloud spotted 2 miles away. You have maybe 3 minutes.",
                "options": {
                    "A": {"action": "Everyone to safe room NOW with helmets", "score": 10, "risk": 0},
                    "B": {"action": "Grab supplies first, then shelter", "score": 5, "risk": 5},
                    "C": {"action": "Try to drive away", "score": 0, "risk": 10},
                    "D": {"action": "Keep watching from window", "score": 0, "risk": 10}
                }
            },
            {
                "phase": "impact_imminent",
                "time_limit": 5,
                "prompt": "Roaring sound approaching. House shaking. Final protective action:",
                "options": {
                    "A": {"action": "Get low, cover heads with mattress/blankets", "score": 10, "risk": 0},
                    "B": {"action": "Stand in doorway", "score": 3, "risk": 7},
                    "C": {"action": "Lie flat in bathtub with cover", "score": 9, "risk": 1},
                    "D": {"action": "Try to video the tornado", "score": 0, "risk": 10}
                }
            }
        ]
        
        success_criteria = {
            "excellent": {"min_score": 28, "max_time": 3, "objectives": 7},
            "good": {"min_score": 22, "max_time": 5, "objectives": 5},
            "adequate": {"min_score": 15, "max_time": 8, "objectives": 3},
            "needs_improvement": {"min_score": 0, "max_time": 999, "objectives": 0}
        }
        
        family_roles = [
            "Weather Monitor - Track alerts and warnings",
            "Shelter Captain - Prepare and manage safe room",
            "Supply Gatherer - Quick grab emergency items",
            "Child Protector - Ensure kids are covered",
            "Pet Handler - Secure pets quickly"
        ]
        
        return self.save_scenario(
            "Tornado Warning Drill",
            "tornado",
            "intermediate",
            10,
            objectives,
            decision_points,
            success_criteria,
            family_roles
        )
    
    def save_scenario(self, name: str, disaster_type: str, difficulty: str,
                     duration_minutes: int, objectives: List[str],
                     decision_points: List[Dict], success_criteria: Dict,
                     family_roles: List[str]) -> int:
        """Save a drill scenario to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO drill_scenarios (name, disaster_type, difficulty, duration_minutes,
                                        objectives, decision_points, success_criteria, family_roles)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, disaster_type, difficulty, duration_minutes,
              json.dumps(objectives), json.dumps(decision_points),
              json.dumps(success_criteria), json.dumps(family_roles)))
        
        scenario_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return scenario_id
    
    def run_drill(self, scenario_id: int, participant_name: str, family_size: int = 4) -> Dict:
        """Run an interactive emergency drill"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM drill_scenarios WHERE id = ?", (scenario_id,))
        scenario_row = cursor.fetchone()
        
        if not scenario_row:
            conn.close()
            return {"error": "Scenario not found"}
        
        # Parse scenario data
        scenario = {
            "id": scenario_row[0],
            "name": scenario_row[1],
            "disaster_type": scenario_row[2],
            "difficulty": scenario_row[3],
            "duration_minutes": scenario_row[4],
            "objectives": json.loads(scenario_row[5]),
            "decision_points": json.loads(scenario_row[6]),
            "success_criteria": json.loads(scenario_row[7]),
            "family_roles": json.loads(scenario_row[8])
        }
        
        conn.close()
        
        # Initialize drill
        start_time = datetime.now()
        total_score = 0
        decisions_made = []
        objectives_completed = []
        total_risk = 0
        
        print(f"\n{'='*70}")
        print(f"🚨 EMERGENCY DRILL: {scenario['name']} 🚨")
        print(f"{'='*70}")
        print(f"Difficulty: {scenario['difficulty'].upper()}")
        print(f"Time Limit: {scenario['duration_minutes']} minutes")
        print(f"Family Size: {family_size} members")
        print(f"\nOBJECTIVES:")
        for i, obj in enumerate(scenario['objectives'], 1):
            print(f"  {i}. {obj}")
        
        print(f"\nFAMILY ROLE ASSIGNMENTS:")
        for i, role in enumerate(scenario['family_roles'][:family_size], 1):
            print(f"  Member {i}: {role}")
        
        input("\n⚡ Press Enter to START THE DRILL...")
        
        # Run through decision points
        for decision in scenario['decision_points']:
            print(f"\n{'='*60}")
            print(f"⏰ PHASE: {decision['phase'].upper()}")
            print(f"Time Limit: {decision['time_limit']} seconds")
            print(f"\n❗ {decision['prompt']}")
            print("\nOPTIONS:")
            for key, option in decision['options'].items():
                print(f"  {key}) {option['action']}")
            
            # Start timer
            start_decision = time.time()
            
            # Get user choice with timeout
            print(f"\nYou have {decision['time_limit']} seconds to decide!")
            choice = input("Your choice (A/B/C/D): ").upper().strip()
            
            decision_time = time.time() - start_decision
            
            # Validate choice
            if choice not in decision['options']:
                choice = 'A'  # Default to first option if invalid
                print("❌ Invalid choice - defaulting to option A")
            
            # Score the decision
            if decision_time > decision['time_limit']:
                print(f"⏰ TOO SLOW! Took {decision_time:.1f} seconds")
                score_modifier = 0.5  # Half points for slow decisions
            else:
                print(f"✅ Quick decision: {decision_time:.1f} seconds")
                score_modifier = 1.0
            
            option_chosen = decision['options'][choice]
            points = int(option_chosen['score'] * score_modifier)
            risk = option_chosen['risk']
            
            total_score += points
            total_risk += risk
            
            # Record decision
            decisions_made.append({
                "phase": decision['phase'],
                "choice": choice,
                "action": option_chosen['action'],
                "score": points,
                "risk": risk,
                "time": decision_time
            })
            
            # Provide feedback
            if points >= 8:
                print(f"✅ EXCELLENT CHOICE! (+{points} points)")
            elif points >= 5:
                print(f"👍 Good decision. (+{points} points)")
            elif points >= 3:
                print(f"⚠️  Acceptable but risky. (+{points} points)")
            else:
                print(f"❌ DANGEROUS CHOICE! (+{points} points, Risk: {risk}/10)")
            
            if risk >= 7:
                print(f"🚨 WARNING: This action could result in injury or death!")
            elif risk >= 4:
                print(f"⚠️  Caution: Moderate risk involved")
            
            time.sleep(2)  # Brief pause between phases
        
        # Calculate final results
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds() / 60.0
        
        # Determine objectives completed based on score
        if total_score >= 40:
            objectives_completed = scenario['objectives'][:7]
        elif total_score >= 30:
            objectives_completed = scenario['objectives'][:5]
        elif total_score >= 20:
            objectives_completed = scenario['objectives'][:3]
        else:
            objectives_completed = scenario['objectives'][:1]
        
        # Determine performance grade
        for grade, criteria in scenario['success_criteria'].items():
            if (total_score >= criteria['min_score'] and 
                total_time <= criteria['max_time'] and
                len(objectives_completed) >= criteria['objectives']):
                performance_grade = grade
                break
        else:
            performance_grade = "needs_improvement"
        
        # Generate lessons learned
        lessons = []
        if total_risk > 30:
            lessons.append("Reduce risk-taking behavior - safety first!")
        if total_time > scenario['duration_minutes']:
            lessons.append("Practice to improve response time")
        if total_score < 30:
            lessons.append("Review emergency procedures and best practices")
        
        for decision in decisions_made:
            if decision['risk'] >= 8:
                lessons.append(f"Never: {decision['action']}")
            elif decision['score'] >= 9:
                lessons.append(f"Good: {decision['action']}")
        
        # Save results
        drill_result_id = self.save_drill_result(
            scenario_id, participant_name, family_size,
            start_time.isoformat(), end_time.isoformat(),
            decisions_made, objectives_completed,
            total_score, total_time, performance_grade, lessons
        )
        
        # Display results
        print(f"\n{'='*70}")
        print(f"📊 DRILL COMPLETE - AFTER ACTION REPORT")
        print(f"{'='*70}")
        print(f"Participant: {participant_name}")
        print(f"Final Score: {total_score}/{len(scenario['decision_points']) * 10}")
        print(f"Performance Grade: {performance_grade.upper().replace('_', ' ')}")
        print(f"Total Time: {total_time:.1f} minutes")
        print(f"Risk Events: {total_risk}")
        print(f"Objectives Completed: {len(objectives_completed)}/{len(scenario['objectives'])}")
        
        print(f"\n📚 LESSONS LEARNED:")
        for lesson in lessons[:5]:  # Top 5 lessons
            print(f"  • {lesson}")
        
        if performance_grade == "excellent":
            print(f"\n🏆 OUTSTANDING! Your family is well-prepared!")
        elif performance_grade == "good":
            print(f"\n👍 Good job! A few areas to improve.")
        elif performance_grade == "adequate":
            print(f"\n📖 Adequate response. More practice recommended.")
        else:
            print(f"\n⚠️  Significant improvement needed. Practice regularly!")
        
        return {
            "drill_result_id": drill_result_id,
            "score": total_score,
            "grade": performance_grade,
            "time": total_time,
            "decisions": decisions_made,
            "lessons": lessons
        }
    
    def save_drill_result(self, scenario_id: int, participant_name: str,
                         family_size: int, start_time: str, end_time: str,
                         decisions_made: List[Dict], objectives_completed: List[str],
                         score: int, time_taken: float, performance_grade: str,
                         lessons_learned: List[str]) -> int:
        """Save drill results to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO drill_results (scenario_id, participant_name, family_size,
                                     start_time, end_time, decisions_made, objectives_completed,
                                     score, time_taken, performance_grade, lessons_learned)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (scenario_id, participant_name, family_size, start_time, end_time,
              json.dumps(decisions_made), json.dumps(objectives_completed),
              score, time_taken, performance_grade, json.dumps(lessons_learned)))
        
        result_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return result_id
    
    def get_performance_history(self, participant_name: str) -> Dict:
        """Get drill performance history for a participant"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT dr.*, ds.name, ds.disaster_type
            FROM drill_results dr
            JOIN drill_scenarios ds ON dr.scenario_id = ds.id
            WHERE dr.participant_name = ?
            ORDER BY dr.created_date DESC
        ''', (participant_name,))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "date": row[12],  # created_date
                "scenario": row[13],  # scenario name
                "disaster_type": row[14],
                "score": row[8],
                "grade": row[10],
                "time": row[9]
            })
        
        # Calculate statistics
        if results:
            avg_score = sum(r['score'] for r in results) / len(results)
            best_score = max(r['score'] for r in results)
            total_drills = len(results)
            
            # Count grades
            grade_counts = {}
            for r in results:
                grade_counts[r['grade']] = grade_counts.get(r['grade'], 0) + 1
        else:
            avg_score = 0
            best_score = 0
            total_drills = 0
            grade_counts = {}
        
        conn.close()
        
        return {
            "participant": participant_name,
            "total_drills": total_drills,
            "average_score": round(avg_score, 1),
            "best_score": best_score,
            "grade_distribution": grade_counts,
            "recent_drills": results[:5]
        }
    
    def recommend_next_drill(self, participant_name: str) -> Dict:
        """Recommend next drill based on performance history"""
        history = self.get_performance_history(participant_name)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all available scenarios
        cursor.execute("SELECT id, name, disaster_type, difficulty FROM drill_scenarios")
        all_scenarios = cursor.fetchall()
        
        # Get completed scenario types
        cursor.execute('''
            SELECT DISTINCT ds.disaster_type
            FROM drill_results dr
            JOIN drill_scenarios ds ON dr.scenario_id = ds.id
            WHERE dr.participant_name = ?
        ''', (participant_name,))
        
        completed_types = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        recommendations = []
        
        # Recommend untried disaster types first
        for scenario in all_scenarios:
            scenario_id, name, disaster_type, difficulty = scenario
            
            if disaster_type not in completed_types:
                recommendations.append({
                    "id": scenario_id,
                    "name": name,
                    "reason": f"You haven't practiced {disaster_type} scenarios yet",
                    "priority": "high"
                })
            elif history['average_score'] < 30 and difficulty == "beginner":
                recommendations.append({
                    "id": scenario_id,
                    "name": name,
                    "reason": "Good for building fundamental skills",
                    "priority": "medium"
                })
            elif history['average_score'] > 40 and difficulty == "advanced":
                recommendations.append({
                    "id": scenario_id,
                    "name": name,
                    "reason": "Challenge yourself with advanced scenarios",
                    "priority": "medium"
                })
        
        return {
            "recommendations": recommendations[:3],
            "focus_areas": self._identify_weak_areas(participant_name)
        }
    
    def _identify_weak_areas(self, participant_name: str) -> List[str]:
        """Identify areas needing improvement"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT decisions_made FROM drill_results
            WHERE participant_name = ?
        ''', (participant_name,))
        
        weak_areas = []
        total_decisions = []
        
        for row in cursor.fetchall():
            decisions = json.loads(row[0])
            total_decisions.extend(decisions)
        
        conn.close()
        
        if not total_decisions:
            return ["Complete your first drill to identify areas for improvement"]
        
        # Analyze decisions
        high_risk_count = sum(1 for d in total_decisions if d.get('risk', 0) >= 7)
        slow_decisions = sum(1 for d in total_decisions if d.get('time', 0) > 10)
        low_scores = sum(1 for d in total_decisions if d.get('score', 0) < 5)
        
        if high_risk_count > len(total_decisions) * 0.2:
            weak_areas.append("Risk assessment - too many dangerous choices")
        if slow_decisions > len(total_decisions) * 0.3:
            weak_areas.append("Decision speed - practice quick thinking")
        if low_scores > len(total_decisions) * 0.4:
            weak_areas.append("Emergency procedures - review best practices")
        
        return weak_areas if weak_areas else ["Great job! Continue regular practice"]

if __name__ == "__main__":
    # Example usage
    simulator = EmergencyDrillSimulator()
    
    # Create scenarios
    earthquake_id = simulator.create_earthquake_drill()
    fire_id = simulator.create_fire_evacuation_drill()
    tornado_id = simulator.create_severe_weather_drill()
    
    print("Emergency Drill Simulator Initialized")
    print(f"Available Drills:")
    print(f"  1. Earthquake Response (ID: {earthquake_id})")
    print(f"  2. Fire Evacuation (ID: {fire_id})")
    print(f"  3. Tornado Warning (ID: {tornado_id})")
    
    # Run a drill
    choice = input("\nSelect drill to run (1-3): ")
    name = input("Your name: ")
    family = int(input("Family size (1-5): ") or 4)
    
    drill_map = {'1': earthquake_id, '2': fire_id, '3': tornado_id}
    if choice in drill_map:
        result = simulator.run_drill(drill_map[choice], name, family)
        
        # Show performance history
        history = simulator.get_performance_history(name)
        print(f"\n📈 YOUR PERFORMANCE HISTORY:")
        print(f"Total Drills: {history['total_drills']}")
        print(f"Average Score: {history['average_score']}")
        
        # Get recommendations
        recommendations = simulator.recommend_next_drill(name)
        if recommendations['recommendations']:
            print(f"\n💡 RECOMMENDED NEXT DRILL:")
            for rec in recommendations['recommendations'][:1]:
                print(f"  {rec['name']}: {rec['reason']}")