#!/usr/bin/env python3
"""
Simple Engineering Solutions for Disaster Preparedness
Practical, buildable solutions using common materials and basic tools
"""

import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class EngineeringSolution:
    id: int
    name: str
    category: str
    difficulty: str
    build_time: str
    materials: List[Dict]
    tools: List[str]
    instructions: List[str]
    applications: List[str]
    cost_estimate: float

class SimpleEngineeringSolutions:
    def __init__(self, db_path: str = "engineering_solutions.db"):
        self.db_path = db_path
        self.init_database()
        self.difficulty_levels = {
            "beginner": {"skill_required": 1, "color": "green"},
            "intermediate": {"skill_required": 3, "color": "yellow"}, 
            "advanced": {"skill_required": 5, "color": "orange"}
        }
        self.categories = [
            "water_collection", "water_purification", "shelter", "power_generation",
            "food_preservation", "heating_cooling", "communication", "tools",
            "security", "sanitation", "lighting", "storage"
        ]
    
    def init_database(self):
        """Initialize SQLite database for engineering solutions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS solutions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                build_time TEXT,
                cost_estimate REAL,
                description TEXT,
                applications TEXT,
                created_date TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS solution_materials (
                solution_id INTEGER,
                material_name TEXT,
                quantity TEXT,
                unit TEXT,
                cost_per_unit REAL,
                alternatives TEXT,
                source_locations TEXT,
                FOREIGN KEY (solution_id) REFERENCES solutions (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS solution_tools (
                solution_id INTEGER,
                tool_name TEXT,
                essential INTEGER DEFAULT 1,
                alternatives TEXT,
                rental_option INTEGER DEFAULT 0,
                FOREIGN KEY (solution_id) REFERENCES solutions (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS solution_steps (
                solution_id INTEGER,
                step_number INTEGER,
                instruction TEXT,
                safety_notes TEXT,
                time_estimate TEXT,
                difficulty_rating INTEGER,
                FOREIGN KEY (solution_id) REFERENCES solutions (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_builds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                solution_id INTEGER,
                builder_name TEXT,
                build_date TEXT,
                actual_cost REAL,
                actual_time TEXT,
                difficulty_rating INTEGER,
                success_rating INTEGER,
                notes TEXT,
                photo_path TEXT,
                FOREIGN KEY (solution_id) REFERENCES solutions (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_solution(self, name: str, category: str, difficulty: str,
                    build_time: str, cost_estimate: float, description: str,
                    applications: List[str]) -> int:
        """Add a new engineering solution"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO solutions (name, category, difficulty, build_time, 
                                 cost_estimate, description, applications)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, category, difficulty, build_time, cost_estimate,
              description, json.dumps(applications)))
        
        solution_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return solution_id
    
    def add_material(self, solution_id: int, material_name: str, quantity: str,
                    unit: str, cost_per_unit: float, alternatives: List[str] = None,
                    source_locations: List[str] = None):
        """Add material requirement to a solution"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO solution_materials (solution_id, material_name, quantity, unit,
                                          cost_per_unit, alternatives, source_locations)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (solution_id, material_name, quantity, unit, cost_per_unit,
              json.dumps(alternatives or []), json.dumps(source_locations or [])))
        
        conn.commit()
        conn.close()
    
    def add_tool(self, solution_id: int, tool_name: str, essential: bool = True,
                alternatives: List[str] = None, rental_option: bool = False):
        """Add tool requirement to a solution"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO solution_tools (solution_id, tool_name, essential, alternatives, rental_option)
            VALUES (?, ?, ?, ?, ?)
        ''', (solution_id, tool_name, int(essential), json.dumps(alternatives or []), int(rental_option)))
        
        conn.commit()
        conn.close()
    
    def add_instruction_step(self, solution_id: int, step_number: int,
                           instruction: str, safety_notes: str = "",
                           time_estimate: str = "", difficulty_rating: int = 3):
        """Add instruction step to a solution"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO solution_steps (solution_id, step_number, instruction,
                                      safety_notes, time_estimate, difficulty_rating)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (solution_id, step_number, instruction, safety_notes, time_estimate, difficulty_rating))
        
        conn.commit()
        conn.close()
    
    def get_solutions_by_category(self, category: str, max_difficulty: str = "advanced") -> List[Dict]:
        """Get solutions filtered by category and difficulty"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        difficulty_order = ["beginner", "intermediate", "advanced"]
        max_diff_idx = difficulty_order.index(max_difficulty)
        allowed_difficulties = difficulty_order[:max_diff_idx + 1]
        
        placeholders = ','.join(['?'] * len(allowed_difficulties))
        query = f'''
            SELECT * FROM solutions
            WHERE category = ? AND difficulty IN ({placeholders})
            ORDER BY difficulty, cost_estimate
        '''
        
        cursor.execute(query, [category] + allowed_difficulties)
        columns = [desc[0] for desc in cursor.description]
        
        solutions = []
        for row in cursor.fetchall():
            solution = dict(zip(columns, row))
            solution['applications'] = json.loads(solution['applications'] or '[]')
            solutions.append(solution)
        
        conn.close()
        return solutions
    
    def get_solution_details(self, solution_id: int) -> Dict:
        """Get complete details for a specific solution"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get solution info
        cursor.execute("SELECT * FROM solutions WHERE id = ?", (solution_id,))
        solution_row = cursor.fetchone()
        if not solution_row:
            conn.close()
            return {}
        
        columns = [desc[0] for desc in cursor.description]
        solution = dict(zip(columns, solution_row))
        solution['applications'] = json.loads(solution['applications'] or '[]')
        
        # Get materials
        cursor.execute('''
            SELECT material_name, quantity, unit, cost_per_unit, alternatives, source_locations
            FROM solution_materials WHERE solution_id = ?
            ORDER BY material_name
        ''', (solution_id,))
        
        materials = []
        for row in cursor.fetchall():
            materials.append({
                "name": row[0],
                "quantity": row[1],
                "unit": row[2],
                "cost_per_unit": row[3],
                "alternatives": json.loads(row[4] or '[]'),
                "source_locations": json.loads(row[5] or '[]')
            })
        
        # Get tools
        cursor.execute('''
            SELECT tool_name, essential, alternatives, rental_option
            FROM solution_tools WHERE solution_id = ?
            ORDER BY essential DESC, tool_name
        ''', (solution_id,))
        
        tools = []
        for row in cursor.fetchall():
            tools.append({
                "name": row[0],
                "essential": bool(row[1]),
                "alternatives": json.loads(row[2] or '[]'),
                "rental_option": bool(row[3])
            })
        
        # Get instructions
        cursor.execute('''
            SELECT step_number, instruction, safety_notes, time_estimate, difficulty_rating
            FROM solution_steps WHERE solution_id = ?
            ORDER BY step_number
        ''', (solution_id,))
        
        instructions = []
        for row in cursor.fetchall():
            instructions.append({
                "step": row[0],
                "instruction": row[1],
                "safety_notes": row[2],
                "time_estimate": row[3],
                "difficulty": row[4]
            })
        
        conn.close()
        
        solution.update({
            "materials": materials,
            "tools": tools,
            "instructions": instructions
        })
        
        return solution
    
    def calculate_total_cost(self, solution_id: int) -> Dict:
        """Calculate total cost for building a solution"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT material_name, quantity, cost_per_unit
            FROM solution_materials 
            WHERE solution_id = ?
        ''', (solution_id,))
        
        total_cost = 0
        material_costs = []
        
        for row in cursor.fetchall():
            try:
                quantity = float(row[1])
                cost_per_unit = float(row[2])
                material_total = quantity * cost_per_unit
                total_cost += material_total
                
                material_costs.append({
                    "material": row[0],
                    "quantity": quantity,
                    "unit_cost": cost_per_unit,
                    "total_cost": material_total
                })
            except ValueError:
                # Handle non-numeric quantities
                material_costs.append({
                    "material": row[0],
                    "quantity": row[1],
                    "unit_cost": row[2],
                    "total_cost": "Variable"
                })
        
        conn.close()
        
        return {
            "total_cost": total_cost,
            "material_breakdown": material_costs,
            "currency": "USD"
        }
    
    def find_solutions_by_scenario(self, scenario: str, available_materials: List[str] = None) -> List[Dict]:
        """Find solutions applicable to a specific disaster scenario"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Search in applications field
        cursor.execute('''
            SELECT id, name, category, difficulty, applications
            FROM solutions
            WHERE applications LIKE ?
            ORDER BY difficulty, cost_estimate
        ''', (f'%{scenario}%',))
        
        solutions = []
        for row in cursor.fetchall():
            applications = json.loads(row[4] or '[]')
            if any(scenario.lower() in app.lower() for app in applications):
                solutions.append({
                    "id": row[0],
                    "name": row[1],
                    "category": row[2],
                    "difficulty": row[3],
                    "applications": applications
                })
        
        # Filter by available materials if specified
        if available_materials:
            filtered_solutions = []
            for solution in solutions:
                solution_details = self.get_solution_details(solution['id'])
                required_materials = [m['name'].lower() for m in solution_details['materials']]
                available_lower = [m.lower() for m in available_materials]
                
                # Check if at least 70% of materials are available
                matches = sum(1 for req in required_materials if any(avail in req for avail in available_lower))
                if matches / len(required_materials) >= 0.7:
                    solution['material_match'] = f"{matches}/{len(required_materials)}"
                    filtered_solutions.append(solution)
            
            solutions = filtered_solutions
        
        conn.close()
        return solutions
    
    def record_build_attempt(self, solution_id: int, builder_name: str,
                           actual_cost: float, actual_time: str,
                           difficulty_rating: int, success_rating: int,
                           notes: str = "") -> int:
        """Record a user's attempt at building a solution"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO user_builds (solution_id, builder_name, build_date, actual_cost,
                                   actual_time, difficulty_rating, success_rating, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (solution_id, builder_name, datetime.now().isoformat(), actual_cost,
              actual_time, difficulty_rating, success_rating, notes))
        
        build_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return build_id
    
    def get_build_statistics(self, solution_id: int) -> Dict:
        """Get build statistics for a solution"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) as attempts,
                   AVG(actual_cost) as avg_cost,
                   AVG(difficulty_rating) as avg_difficulty,
                   AVG(success_rating) as avg_success,
                   MIN(actual_cost) as min_cost,
                   MAX(actual_cost) as max_cost
            FROM user_builds
            WHERE solution_id = ?
        ''', (solution_id,))
        
        stats = cursor.fetchone()
        
        conn.close()
        
        if stats and stats[0] > 0:
            return {
                "total_attempts": stats[0],
                "average_cost": round(stats[1], 2) if stats[1] else 0,
                "average_difficulty": round(stats[2], 1) if stats[2] else 0,
                "average_success": round(stats[3], 1) if stats[3] else 0,
                "cost_range": {
                    "min": stats[4] if stats[4] else 0,
                    "max": stats[5] if stats[5] else 0
                }
            }
        
        return {"total_attempts": 0}
    
    def initialize_default_solutions(self):
        """Initialize database with common disaster preparedness solutions"""
        
        # Water Collection - Rain Catchment System
        solution_id = self.add_solution(
            "Simple Rain Water Catchment",
            "water_collection",
            "beginner",
            "2-3 hours",
            45.0,
            "Collect and store rainwater using common materials",
            ["drought", "water shortage", "emergency water", "off-grid living"]
        )
        
        self.add_material(solution_id, "55-gallon plastic drum", "1", "each", 25.0, 
                         ["large storage tubs", "multiple 5-gallon buckets"])
        self.add_material(solution_id, "PVC pipe (4 inch)", "10", "feet", 1.50,
                         ["gutters", "large funnel"])
        self.add_material(solution_id, "Screen mesh", "2", "sq ft", 3.0,
                         ["fine cloth", "coffee filters"])
        self.add_material(solution_id, "Spigot valve", "1", "each", 8.0,
                         ["garden hose valve"])
        
        self.add_tool(solution_id, "Drill with bits", True, ["hand drill", "awl"])
        self.add_tool(solution_id, "Measuring tape", True, ["ruler"])
        self.add_tool(solution_id, "Level", False, ["smartphone level app"])
        
        self.add_instruction_step(solution_id, 1, "Clean the drum thoroughly with soap and water", 
                                 "Ensure drum previously held food-safe materials only")
        self.add_instruction_step(solution_id, 2, "Drill hole near bottom for spigot installation",
                                 "Use proper bit size for threading", "15 min")
        self.add_instruction_step(solution_id, 3, "Install spigot and test for leaks",
                                 "Use thread sealant if available", "10 min")
        self.add_instruction_step(solution_id, 4, "Cut collection funnel from PVC or use existing gutters",
                                 "Smooth all sharp edges", "30 min")
        self.add_instruction_step(solution_id, 5, "Install screen filter to prevent debris",
                                 "Secure mesh tightly to prevent gaps", "15 min")
        self.add_instruction_step(solution_id, 6, "Position system to collect maximum rainfall",
                                 "Ensure stable base and overflow plan", "20 min")
        
        # Solar Still for Water Purification
        solution_id = self.add_solution(
            "Emergency Solar Still",
            "water_purification",
            "beginner",
            "1-2 hours",
            12.0,
            "Purify water using solar evaporation and condensation",
            ["contaminated water", "salt water", "emergency purification"]
        )
        
        self.add_material(solution_id, "Clear plastic sheet", "4", "sq ft", 3.0,
                         ["glass panel", "clear tarp"])
        self.add_material(solution_id, "Large bowl or pot", "1", "each", 5.0,
                         ["any wide container"])
        self.add_material(solution_id, "Small collection cup", "1", "each", 1.0,
                         ["any small container"])
        self.add_material(solution_id, "Small rocks", "handful", "each", 0.0,
                         ["any weights"])
        self.add_material(solution_id, "Duct tape", "3", "feet", 2.0,
                         ["any sealing tape"])
        
        self.add_tool(solution_id, "Scissors or knife", True)
        
        self.add_instruction_step(solution_id, 1, "Pour contaminated water into large bowl",
                                 "Don't fill completely - leave room for collection cup")
        self.add_instruction_step(solution_id, 2, "Place small cup in center of bowl",
                                 "Cup should float or sit stable in center", "5 min")
        self.add_instruction_step(solution_id, 3, "Cover bowl tightly with plastic sheet",
                                 "Ensure good seal around edges", "10 min")
        self.add_instruction_step(solution_id, 4, "Place small rock in center of plastic",
                                 "Create downward funnel pointing to cup", "5 min")
        self.add_instruction_step(solution_id, 5, "Place in direct sunlight",
                                 "Position for maximum sun exposure", "2 min")
        self.add_instruction_step(solution_id, 6, "Wait 2-4 hours for water to distill",
                                 "Don't disturb during process - check periodically")
        
        # Simple Rocket Stove
        solution_id = self.add_solution(
            "Tin Can Rocket Stove",
            "heating_cooling",
            "intermediate",
            "1 hour",
            8.0,
            "Efficient wood-burning stove from tin cans",
            ["cooking", "heating", "fuel efficiency", "emergency cooking"]
        )
        
        self.add_material(solution_id, "Large tin can (#10)", "1", "each", 2.0,
                         ["coffee can", "paint can"])
        self.add_material(solution_id, "Smaller tin cans", "2", "each", 1.0,
                         ["soup cans", "vegetable cans"])
        self.add_material(solution_id, "Insulation material", "2", "cups", 3.0,
                         ["vermiculite", "perlite", "ash", "sand"])
        self.add_material(solution_id, "Metal grate", "1", "each", 2.0,
                         ["oven rack", "cooling rack"])
        
        self.add_tool(solution_id, "Tin snips", True, ["sturdy scissors"])
        self.add_tool(solution_id, "Can opener", True)
        self.add_tool(solution_id, "Pliers", True)
        self.add_tool(solution_id, "File or sandpaper", False)
        
        self.add_instruction_step(solution_id, 1, "Remove labels and clean all cans thoroughly",
                                 "Sharp edges - handle carefully", "10 min")
        self.add_instruction_step(solution_id, 2, "Cut feed hole in large can near bottom",
                                 "Size hole to fit smaller can snugly", "15 min")
        self.add_instruction_step(solution_id, 3, "Insert small can horizontally through hole",
                                 "This becomes the combustion chamber", "5 min")
        self.add_instruction_step(solution_id, 4, "Fill space around small can with insulation",
                                 "Don't block air flow paths", "10 min")
        self.add_instruction_step(solution_id, 5, "Position grate on top for cooking surface",
                                 "Ensure stable and level", "5 min")
        self.add_instruction_step(solution_id, 6, "Test with small fire using dry kindling",
                                 "Start small - stove will burn very hot", "15 min")

if __name__ == "__main__":
    # Example usage
    solutions = SimpleEngineeringSolutions()
    
    # Initialize with default solutions
    solutions.initialize_default_solutions()
    
    # Find water solutions
    water_solutions = solutions.get_solutions_by_category("water_collection")
    print(f"Water Collection Solutions: {len(water_solutions)}")
    
    # Get detailed solution
    if water_solutions:
        details = solutions.get_solution_details(water_solutions[0]['id'])
        print(f"\nSolution: {details['name']}")
        print(f"Materials needed: {len(details['materials'])}")
        print(f"Steps: {len(details['instructions'])}")
        
        # Calculate cost
        cost_info = solutions.calculate_total_cost(details['id'])
        print(f"Estimated cost: ${cost_info['total_cost']:.2f}")
    
    # Find solutions for drought scenario
    drought_solutions = solutions.find_solutions_by_scenario("drought")
    print(f"\nDrought preparedness solutions: {len(drought_solutions)}")