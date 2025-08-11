#!/usr/bin/env python3
"""
Step-by-Step Building Instructions System
Interactive, progressive building guides with safety checks and quality control
"""

import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class BuildStep:
    step_number: int
    title: str
    description: str
    time_estimate: str
    difficulty: int
    safety_warnings: List[str]
    quality_checks: List[str]
    tools_needed: List[str]
    materials_used: List[str]
    visual_aid: str
    common_mistakes: List[str]

class StepByStepBuilder:
    def __init__(self, db_path: str = "step_builder.db"):
        self.db_path = db_path
        self.init_database()
        self.difficulty_scale = {
            1: "Very Easy - No experience needed",
            2: "Easy - Basic tools only", 
            3: "Moderate - Some construction knowledge helpful",
            4: "Challenging - Previous building experience recommended",
            5: "Expert - Professional skills required"
        }
        
    def init_database(self):
        """Initialize database for step-by-step instructions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS building_projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name TEXT NOT NULL,
                category TEXT,
                description TEXT,
                total_steps INTEGER,
                estimated_time TEXT,
                skill_level INTEGER,
                tools_overview TEXT,
                materials_overview TEXT,
                created_date TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS build_steps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                step_number INTEGER,
                title TEXT NOT NULL,
                description TEXT,
                time_estimate TEXT,
                difficulty INTEGER,
                safety_warnings TEXT,
                quality_checks TEXT,
                tools_needed TEXT,
                materials_used TEXT,
                visual_aid TEXT,
                common_mistakes TEXT,
                FOREIGN KEY (project_id) REFERENCES building_projects (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                user_name TEXT,
                current_step INTEGER,
                steps_completed TEXT,
                start_date TEXT,
                notes TEXT,
                quality_ratings TEXT,
                FOREIGN KEY (project_id) REFERENCES building_projects (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS step_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                step_number INTEGER,
                user_name TEXT,
                difficulty_rating INTEGER,
                time_actual TEXT,
                problems_encountered TEXT,
                suggestions TEXT,
                date_completed TEXT,
                FOREIGN KEY (project_id) REFERENCES building_projects (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_project(self, project_name: str, category: str, description: str,
                      estimated_time: str, skill_level: int,
                      tools_overview: List[str], materials_overview: List[str]) -> int:
        """Create a new step-by-step building project"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO building_projects (project_name, category, description,
                                         estimated_time, skill_level, tools_overview, materials_overview)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (project_name, category, description, estimated_time, skill_level,
              json.dumps(tools_overview), json.dumps(materials_overview)))
        
        project_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return project_id
    
    def add_build_step(self, project_id: int, step_number: int, title: str,
                      description: str, time_estimate: str, difficulty: int,
                      safety_warnings: List[str], quality_checks: List[str],
                      tools_needed: List[str], materials_used: List[str],
                      visual_aid: str = "", common_mistakes: List[str] = None) -> int:
        """Add a detailed build step to a project"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO build_steps (project_id, step_number, title, description,
                                   time_estimate, difficulty, safety_warnings, quality_checks,
                                   tools_needed, materials_used, visual_aid, common_mistakes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (project_id, step_number, title, description, time_estimate, difficulty,
              json.dumps(safety_warnings), json.dumps(quality_checks),
              json.dumps(tools_needed), json.dumps(materials_used),
              visual_aid, json.dumps(common_mistakes or [])))
        
        step_id = cursor.lastrowid
        
        # Update total steps count
        cursor.execute('''
            UPDATE building_projects 
            SET total_steps = (SELECT MAX(step_number) FROM build_steps WHERE project_id = ?)
            WHERE id = ?
        ''', (project_id, project_id))
        
        conn.commit()
        conn.close()
        
        return step_id
    
    def get_project_overview(self, project_id: int) -> Dict:
        """Get complete project overview"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM building_projects WHERE id = ?", (project_id,))
        project_row = cursor.fetchone()
        
        if not project_row:
            conn.close()
            return {}
        
        columns = [desc[0] for desc in cursor.description]
        project = dict(zip(columns, project_row))
        
        # Parse JSON fields
        project['tools_overview'] = json.loads(project['tools_overview'] or '[]')
        project['materials_overview'] = json.loads(project['materials_overview'] or '[]')
        
        conn.close()
        return project
    
    def get_build_step(self, project_id: int, step_number: int) -> Dict:
        """Get detailed information for a specific build step"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM build_steps 
            WHERE project_id = ? AND step_number = ?
        ''', (project_id, step_number))
        
        step_row = cursor.fetchone()
        if not step_row:
            conn.close()
            return {}
        
        columns = [desc[0] for desc in cursor.description]
        step = dict(zip(columns, step_row))
        
        # Parse JSON fields
        step['safety_warnings'] = json.loads(step['safety_warnings'] or '[]')
        step['quality_checks'] = json.loads(step['quality_checks'] or '[]')
        step['tools_needed'] = json.loads(step['tools_needed'] or '[]')
        step['materials_used'] = json.loads(step['materials_used'] or '[]')
        step['common_mistakes'] = json.loads(step['common_mistakes'] or '[]')
        
        conn.close()
        return step
    
    def start_user_session(self, project_id: int, user_name: str) -> int:
        """Start a new building session for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO user_progress (project_id, user_name, current_step, 
                                     steps_completed, start_date)
            VALUES (?, ?, 1, ?, ?)
        ''', (project_id, user_name, json.dumps([]), datetime.now().isoformat()))
        
        session_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return session_id
    
    def complete_step(self, session_id: int, step_number: int, 
                     quality_rating: int = 5, notes: str = "") -> bool:
        """Mark a step as completed and move to next step"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get current progress
        cursor.execute('''
            SELECT steps_completed, quality_ratings FROM user_progress WHERE id = ?
        ''', (session_id,))
        
        row = cursor.fetchone()
        if not row:
            conn.close()
            return False
        
        completed_steps = json.loads(row[0] or '[]')
        quality_ratings = json.loads(row[1] or '{}')
        
        # Add completed step
        if step_number not in completed_steps:
            completed_steps.append(step_number)
            completed_steps.sort()
        
        # Record quality rating
        quality_ratings[str(step_number)] = quality_rating
        
        # Update current step to next uncompleted step
        next_step = step_number + 1
        
        cursor.execute('''
            UPDATE user_progress 
            SET current_step = ?, steps_completed = ?, quality_ratings = ?, notes = ?
            WHERE id = ?
        ''', (next_step, json.dumps(completed_steps), json.dumps(quality_ratings), notes, session_id))
        
        conn.commit()
        conn.close()
        
        return True
    
    def get_user_progress(self, session_id: int) -> Dict:
        """Get user's current progress"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT up.*, bp.project_name, bp.total_steps
            FROM user_progress up
            JOIN building_projects bp ON up.project_id = bp.id
            WHERE up.id = ?
        ''', (session_id,))
        
        row = cursor.fetchone()
        if not row:
            conn.close()
            return {}
        
        progress = {
            "session_id": row[0],
            "project_id": row[1],
            "user_name": row[2],
            "current_step": row[3],
            "steps_completed": json.loads(row[4] or '[]'),
            "start_date": row[5],
            "notes": row[6],
            "quality_ratings": json.loads(row[7] or '{}'),
            "project_name": row[8],
            "total_steps": row[9]
        }
        
        # Calculate completion percentage
        if progress["total_steps"]:
            completion_pct = len(progress["steps_completed"]) / progress["total_steps"] * 100
            progress["completion_percentage"] = round(completion_pct, 1)
        else:
            progress["completion_percentage"] = 0
        
        conn.close()
        return progress
    
    def record_step_feedback(self, project_id: int, step_number: int, user_name: str,
                           difficulty_rating: int, time_actual: str,
                           problems_encountered: str = "", suggestions: str = ""):
        """Record user feedback for a specific step"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO step_feedback (project_id, step_number, user_name, difficulty_rating,
                                     time_actual, problems_encountered, suggestions, date_completed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (project_id, step_number, user_name, difficulty_rating, time_actual,
              problems_encountered, suggestions, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def generate_interactive_guide(self, project_id: int, current_step: int) -> str:
        """Generate interactive text guide for current step"""
        project = self.get_project_overview(project_id)
        step = self.get_build_step(project_id, current_step)
        
        if not project or not step:
            return "Project or step not found."
        
        guide = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║ {project['project_name'].upper().center(76)} ║
║ Step {current_step}/{project['total_steps']}: {step['title'].center(76-len(f'Step {current_step}/{project["total_steps"]}: '))} ║
╚══════════════════════════════════════════════════════════════════════════════╝

📋 DESCRIPTION:
{step['description']}

⏱️  TIME ESTIMATE: {step['time_estimate']}
🎯 DIFFICULTY: {step['difficulty']}/5 - {self.difficulty_scale.get(step['difficulty'], 'Unknown')}

🔧 TOOLS NEEDED:
"""
        
        for tool in step['tools_needed']:
            guide += f"   • {tool}\n"
        
        guide += f"\n📦 MATERIALS FOR THIS STEP:\n"
        for material in step['materials_used']:
            guide += f"   • {material}\n"
        
        if step['safety_warnings']:
            guide += f"\n⚠️  SAFETY WARNINGS:\n"
            for warning in step['safety_warnings']:
                guide += f"   ⚠️  {warning}\n"
        
        if step['visual_aid']:
            guide += f"\n📐 VISUAL GUIDE:\n{step['visual_aid']}\n"
        
        guide += f"\n✅ QUALITY CHECKS (Complete before moving to next step):\n"
        for check in step['quality_checks']:
            guide += f"   ✓ {check}\n"
        
        if step['common_mistakes']:
            guide += f"\n❌ COMMON MISTAKES TO AVOID:\n"
            for mistake in step['common_mistakes']:
                guide += f"   × {mistake}\n"
        
        guide += f"\n{'─' * 80}\n"
        guide += "Complete this step? (y/n) | Need help? (h) | Mark quality issues? (q)\n"
        
        return guide
    
    def create_emergency_shelter_guide(self) -> int:
        """Create complete step-by-step guide for emergency shelter"""
        project_id = self.create_project(
            "Emergency A-Frame Shelter",
            "shelter",
            "Build a weatherproof emergency shelter using basic materials",
            "4-6 hours with 2 people",
            2,  # Easy skill level
            ["hammer", "saw", "drill", "level", "measuring_tape"],
            ["2x4 lumber", "plywood", "tarp", "rope", "stakes", "screws"]
        )
        
        # Step 1: Site Preparation
        self.add_build_step(
            project_id, 1,
            "Site Selection and Ground Preparation",
            "Select level ground with good drainage, away from hazards like dead trees. Clear area of debris and level as much as possible.",
            "30 minutes",
            1,
            ["Check for overhead hazards", "Avoid low areas that collect water", "Watch for underground utilities"],
            ["Ground is reasonably level", "Area is clear of debris", "Good drainage confirmed"],
            ["shovel", "rake", "measuring_tape"],
            ["stakes for marking"],
            '''
    SITE SELECTION CRITERIA:
    
    ✓ GOOD SITE:                    ✗ AVOID:
    ┌─────────────────┐           ┌─────────────────┐
    │    Shelter      │           │    Shelter      │
    │                 │           │                 │
    └─────────────────┘           └─────────────────┘
     Slight slope →                      ← Low spot
     Good drainage                    Water collects
     
    Check 10ft radius for:
    • Dead tree branches overhead
    • Rocky or extremely uneven ground  
    • Areas that would flood in rain
            ''',
            ["Building too close to water", "Not checking overhead hazards", "Ignoring drainage"]
        )
        
        # Step 2: Frame Assembly
        self.add_build_step(
            project_id, 2,
            "A-Frame Structure Assembly",
            "Construct the triangular A-frame ends and ridge pole. Triangle shape provides maximum strength.",
            "45 minutes",
            2,
            ["Ensure all connections are tight", "Check angles with level", "Watch for splitting wood"],
            ["A-frames are identical", "Ridge pole is straight and level", "All joints are secure"],
            ["hammer", "saw", "drill", "level", "square"],
            ["2x4 lumber", "3-inch screws", "brackets"],
            '''
    A-FRAME CONSTRUCTION:
    
         /\\  <- Ridge pole (2x4)
        /  \\
       /    \\  <- A-frame legs (2x4)
      /      \\    60° angle optimal
     /        \\
    /_________ \\
    
    CONNECTION DETAIL:
    ┌─────────┐
    │    ╱╲   │ <- Use metal brackets
    │   ╱  ╲  │    or cut notches
    │  ╱____╲ │
    └─────────┘
    
    Build TWO identical A-frames, then connect with ridge pole
            ''',
            ["Wrong angle - too steep or shallow", "Uneven A-frames", "Weak connections"]
        )
        
        # Step 3: Foundation and Anchoring
        self.add_build_step(
            project_id, 3,
            "Foundation Setup and Anchoring", 
            "Set A-frames in position and anchor securely. Level and square the structure.",
            "30 minutes",
            2,
            ["Heavy lifting - use proper technique", "Ensure structure is stable before continuing"],
            ["A-frames are plumb and level", "Structure is square", "All anchors are secure"],
            ["level", "measuring_tape", "hammer", "shovel"],
            ["concrete blocks or treated lumber", "ground anchors", "stakes"],
            '''
    FOUNDATION OPTIONS:
    
    Option A - Concrete Blocks:        Option B - Ground Stakes:
    ┌─────────────────┐               ┌─────────────────┐
    │       ╱╲        │               │       ╱╲        │
    │      ╱  ╲       │               │      ╱  ╲       │
    │     ╱    ╲      │               │     ╱    ╲      │
    │ ■■■╱      ╲■■■  │               │    ╱      ╲     │
    └─────────────────┘               └───╱────────╲────┘
         Blocks                           Stakes driven
         for stability                   into ground
            ''',
            ["Not checking for level", "Inadequate anchoring", "Forgetting to square"]
        )
        
        # Step 4: Wall Covering
        self.add_build_step(
            project_id, 4,
            "Install Wall Covering",
            "Attach plywood or tarp to create weatherproof walls. Ensure good overlap and secure attachment.",
            "60 minutes", 
            2,
            ["Pre-drill holes to prevent splitting", "Watch for sharp edges", "Secure ladder properly"],
            ["No gaps in covering", "All attachments are secure", "Water will shed properly"],
            ["drill", "screws", "measuring_tape", "utility_knife"],
            ["plywood sheets or heavy tarp", "screws", "washers"],
            '''
    COVERING ATTACHMENT PATTERN:
    
    PLYWOOD METHOD:                TARP METHOD:
    ┌─────────────────┐           ╔═════════════════╗
    │ ■─■─■─■─■─■─■─■ │ Screws    ║ ●───●───●───●   ║ Grommets
    │■               ■│ every     ║●               ●║ every 
    │ ■             ■ │ 12"       ║ ●             ● ║ 18"
    │■               ■│           ║●               ●║
    │ ■─■─■─■─■─■─■─■ │           ║ ●───●───●───●   ║
    └─────────────────┘           ╚═════════════════╝
            ''',
            ["Not overlapping seams", "Insufficient fasteners", "Creating water collection points"]
        )
        
        # Step 5: Final Weatherproofing
        self.add_build_step(
            project_id, 5,
            "Weatherproofing and Final Details",
            "Seal gaps, add drainage, install door, and perform final safety checks.",
            "45 minutes",
            2,
            ["Test all entry points", "Check stability in wind", "Verify ventilation"],
            ["No water intrusion", "Structure is stable", "Safe entry/exit", "Adequate ventilation"],
            ["caulk_gun", "utility_knife", "hammer"],
            ["caulk", "door material", "hinges", "weatherstripping"],
            '''
    FINAL DETAILS:
    
    DOOR INSTALLATION:        DRAINAGE:
    ┌─────────────────┐       Water flow
    │     ╔═══╗       │           ↓
    │     ║   ║ Door  │       ┌─────────┐
    │     ║   ║       │       │  \\ /   │ Shelter
    │     ╚═╤═╝       │       │   V    │ 
    └───────┴─────────┘       └────────────┘
       Hinges                      ↓
                                Ground slopes away
            ''',
            ["Poor door fit", "Forgetting drainage", "No ventilation plan"]
        )
        
        return project_id

if __name__ == "__main__":
    # Example usage
    builder = StepByStepBuilder()
    
    # Create emergency shelter guide
    project_id = builder.create_emergency_shelter_guide()
    
    # Start a user session
    session_id = builder.start_user_session(project_id, "Test Builder")
    
    # Display first step
    progress = builder.get_user_progress(session_id)
    guide = builder.generate_interactive_guide(project_id, progress["current_step"])
    
    print(guide)
    
    # Simulate completing first step
    builder.complete_step(session_id, 1, 5, "Site prepared successfully")
    
    # Record feedback
    builder.record_step_feedback(project_id, 1, "Test Builder", 2, "25 minutes", 
                               "Had to clear more debris than expected", 
                               "Add note about checking for rocks underground")
    
    # Show updated progress
    updated_progress = builder.get_user_progress(session_id)
    print(f"\nProgress: {updated_progress['completion_percentage']}% complete")
    print(f"Steps completed: {updated_progress['steps_completed']}")
    print(f"Current step: {updated_progress['current_step']}")