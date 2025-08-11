#!/usr/bin/env python3
"""
Intuitive Building Guide System
Visual and intuitive construction guides using simple materials and common sense engineering
"""

import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import math

class IntuitiveBuilder:
    def __init__(self, db_path: str = "building_guides.db"):
        self.db_path = db_path
        self.init_database()
        self.construction_principles = {
            "triangulation": "Triangles are strongest shape - use for bracing",
            "compression": "Materials strong in compression: concrete, stone, brick",
            "tension": "Materials strong in tension: rope, cable, fabric",
            "leverage": "Use leverage to multiply force - longer lever = more force",
            "load_distribution": "Spread weight across multiple supports",
            "center_of_gravity": "Keep weight low and centered for stability"
        }
        
        self.common_materials = {
            "2x4_lumber": {"strength": "high", "workability": "easy", "cost": "medium"},
            "plywood": {"strength": "medium", "workability": "easy", "cost": "medium"},
            "pvc_pipe": {"strength": "low", "workability": "very_easy", "cost": "low"},
            "concrete_blocks": {"strength": "very_high", "workability": "medium", "cost": "low"},
            "tarps": {"strength": "low", "workability": "very_easy", "cost": "very_low"},
            "rope": {"strength": "medium", "workability": "easy", "cost": "low"},
            "metal_pipe": {"strength": "high", "workability": "hard", "cost": "high"}
        }
    
    def init_database(self):
        """Initialize database for building guides"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS building_projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                purpose TEXT,
                size_description TEXT,
                load_capacity TEXT,
                weather_resistance TEXT,
                assembly_time TEXT,
                skill_level TEXT,
                created_date TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS construction_phases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                phase_name TEXT,
                phase_order INTEGER,
                description TEXT,
                time_estimate TEXT,
                key_principle TEXT,
                safety_focus TEXT,
                FOREIGN KEY (project_id) REFERENCES building_projects (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS visual_guides (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                phase_id INTEGER,
                guide_type TEXT,
                title TEXT,
                ascii_diagram TEXT,
                measurements TEXT,
                angles TEXT,
                connection_points TEXT,
                FOREIGN KEY (project_id) REFERENCES building_projects (id),
                FOREIGN KEY (phase_id) REFERENCES construction_phases (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS material_substitutions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_material TEXT,
                substitute_material TEXT,
                strength_ratio REAL,
                cost_ratio REAL,
                availability TEXT,
                notes TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quick_calculations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                calculation_type TEXT,
                formula TEXT,
                variables TEXT,
                example_input TEXT,
                example_output TEXT,
                units TEXT,
                safety_factor REAL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_building_project(self, name: str, category: str, purpose: str,
                           size_description: str, load_capacity: str,
                           weather_resistance: str, assembly_time: str,
                           skill_level: str) -> int:
        """Add a new building project guide"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO building_projects (name, category, purpose, size_description,
                                         load_capacity, weather_resistance, assembly_time, skill_level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, category, purpose, size_description, load_capacity,
              weather_resistance, assembly_time, skill_level))
        
        project_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return project_id
    
    def add_construction_phase(self, project_id: int, phase_name: str,
                             phase_order: int, description: str,
                             time_estimate: str, key_principle: str,
                             safety_focus: str) -> int:
        """Add a construction phase to a project"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO construction_phases (project_id, phase_name, phase_order,
                                           description, time_estimate, key_principle, safety_focus)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (project_id, phase_name, phase_order, description, time_estimate, key_principle, safety_focus))
        
        phase_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return phase_id
    
    def add_visual_guide(self, project_id: int, phase_id: int, guide_type: str,
                        title: str, ascii_diagram: str, measurements: str = "",
                        angles: str = "", connection_points: str = "") -> int:
        """Add visual guide with ASCII diagram"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO visual_guides (project_id, phase_id, guide_type, title,
                                     ascii_diagram, measurements, angles, connection_points)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (project_id, phase_id, guide_type, title, ascii_diagram,
              measurements, angles, connection_points))
        
        guide_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return guide_id
    
    def generate_simple_shelter_guide(self) -> int:
        """Generate guide for simple emergency shelter"""
        project_id = self.add_building_project(
            "A-Frame Emergency Shelter",
            "shelter",
            "Weatherproof emergency shelter for 2-3 people",
            "8ft long x 6ft wide x 5ft high",
            "Light snow load, moderate wind",
            "Rain resistant with proper tarp",
            "2-3 hours with 2 people",
            "beginner"
        )
        
        # Phase 1: Foundation and Frame Setup
        phase1_id = self.add_construction_phase(
            project_id, "Foundation & Frame", 1,
            "Level ground, set up A-frame structure using triangulation principle",
            "45 minutes", "triangulation",
            "Level ground, stable footing"
        )
        
        frame_diagram = '''
    A-FRAME STRUCTURE (Side View)
    
         /\\
        /  \\  <- Ridge pole (2x4 or strong branch)
       /    \\
      /      \\
     /        \\ <- A-frame legs (2x4 or poles)
    /          \\
   /____________\\ <- Ground level
   
   |<-- 6 ft -->|
   
    FRONT VIEW:
    
    ┌─────────────────┐ <- Tarp attachment point
    │\\               /│
    │ \\             / │
    │  \\           /  │ <- 5 ft height
    │   \\         /   │
    │    \\       /    │
    │     \\_____/     │
    └─────────────────┘
    '''
        
        self.add_visual_guide(
            project_id, phase1_id, "structure",
            "A-Frame Basic Structure",
            frame_diagram,
            "Base: 6ft, Height: 5ft, Length: 8ft",
            "A-frame angle: ~60 degrees",
            "Ridge connection, ground stakes"
        )
        
        # Phase 2: Wall and Roof Installation
        phase2_id = self.add_construction_phase(
            project_id, "Walls & Roof", 2,
            "Attach covering using load distribution principle",
            "30 minutes", "load_distribution",
            "Secure all attachment points, test tension"
        )
        
        covering_diagram = '''
    TARP ATTACHMENT (Top View)
    
    ●─────●─────●─────● <- Grommets/attachment points
    │                 │
    │   ┌─────────┐   │ <- Ridge pole
    │   │         │   │
    │   │ SHELTER │   │ <- Interior space
    │   │         │   │
    │   └─────────┘   │
    │                 │
    ●─────●─────●─────● <- Ground stakes
    
    SIDE ATTACHMENT:
    
    Tarp \\          / Tarp
          \\        /
           \\______/  <- Overlap at bottom for drainage
    '''
        
        self.add_visual_guide(
            project_id, phase2_id, "covering",
            "Tarp Installation Pattern",
            covering_diagram,
            "Tarp: 10x12 ft minimum",
            "Slope for water runoff",
            "Grommets every 2 feet"
        )
        
        return project_id
    
    def generate_water_collection_system(self) -> int:
        """Generate guide for rainwater collection system"""
        project_id = self.add_building_project(
            "Gutter-Fed Rain Collection",
            "water_systems",
            "Collect rainwater from roof or tarp surface",
            "Collects from 100 sq ft surface",
            "50+ gallons in moderate rainfall",
            "All-weather operation",
            "1-2 hours setup",
            "beginner"
        )
        
        # Phase 1: Collection Surface Setup
        phase1_id = self.add_construction_phase(
            project_id, "Collection Surface", 1,
            "Set up angled surface for maximum water collection",
            "30 minutes", "gravity_flow",
            "Secure all elevated components"
        )
        
        collection_diagram = '''
    COLLECTION SYSTEM (Side View)
    
    ┌─────────────────┐ <- Tarp or roof (angled 15-30°)
    │                /│
    │               / │
    │              /  │ <- Water flows down
    │             /   │
    │            /    │
    │           /     │
    └──────────/──────┘
              /
             /
    ┌───────/───────┐ <- Gutter or PVC half-pipe
    │              │
    │    │         │ <- Downspout
    │    │         │
    │    ▼         │
    │ ┌─────────┐   │
    │ │CONTAINER│   │ <- Storage drum/bucket
    │ └─────────┘   │
    └───────────────┘
    '''
        
        self.add_visual_guide(
            project_id, phase1_id, "system",
            "Rain Collection Flow",
            collection_diagram,
            "Slope: 1/4 inch per foot minimum",
            "Angle: 15-30 degrees",
            "Gutter outlets, container input"
        )
        
        return project_id
    
    def generate_simple_cooking_stove(self) -> int:
        """Generate guide for efficient wood-burning stove"""
        project_id = self.add_building_project(
            "Rocket Stove Heater",
            "heating_cooking",
            "High-efficiency wood burning for cooking and heating",
            "18 inch tall, burns small wood efficiently",
            "Heats 8x10 room, boils water quickly",
            "Outdoor use, rain cover recommended",
            "2 hours construction",
            "intermediate"
        )
        
        phase1_id = self.add_construction_phase(
            project_id, "Combustion Chamber", 1,
            "Build insulated combustion chamber for complete burn",
            "60 minutes", "thermal_mass",
            "Heat-resistant materials only"
        )
        
        stove_diagram = '''
    ROCKET STOVE DESIGN (Cross Section)
    
         ┌─────┐ <- Cooking surface
         │ POT │
    ┌────┴─────┴────┐
    │               │ <- Heat riser (insulated)
    │    ┌─────┐    │
    │    │ HOT │    │ <- Hot gases rise
    │    │ GAS │    │
    │    └─────┘    │
    │               │
    ├───────────────┤ <- Insulation layer
    │ COMBUSTION    │
    │ CHAMBER   ←───┼── Wood feed tube
    │               │
    └───────────────┘
    
    AIRFLOW PATTERN:
    Air → Combustion → Hot Gases ↑ → Heat Transfer → Exhaust
    '''
        
        self.add_visual_guide(
            project_id, phase1_id, "mechanism",
            "Rocket Stove Combustion",
            stove_diagram,
            "Chamber: 6x6x8 inches",
            "Feed tube: 45 degree angle",
            "Insulation critical for efficiency"
        )
        
        return project_id
    
    def calculate_beam_load(self, beam_length_ft: float, load_lbs: float,
                          material_type: str = "2x4_lumber") -> Dict:
        """Calculate simple beam deflection and safety"""
        # Simplified beam calculation for common materials
        material_properties = {
            "2x4_lumber": {"modulus": 1600000, "moment_inertia": 5.36},  # Southern Pine
            "2x6_lumber": {"modulus": 1600000, "moment_inertia": 20.8},
            "2x8_lumber": {"modulus": 1600000, "moment_inertia": 47.6},
            "steel_angle": {"modulus": 29000000, "moment_inertia": 1.0}  # Approximate
        }
        
        if material_type not in material_properties:
            return {"error": f"Material {material_type} not in database"}
        
        props = material_properties[material_type]
        
        # Simple beam with center load formula: δ = (P * L³) / (48 * E * I)
        # Convert to consistent units
        length_inches = beam_length_ft * 12
        
        deflection = (load_lbs * (length_inches ** 3)) / (48 * props["modulus"] * props["moment_inertia"])
        
        # Check against L/360 deflection limit (common building code)
        max_deflection = length_inches / 360
        safety_ratio = max_deflection / deflection if deflection > 0 else float('inf')
        
        return {
            "beam_length_ft": beam_length_ft,
            "load_lbs": load_lbs,
            "material": material_type,
            "deflection_inches": round(deflection, 3),
            "max_allowable_inches": round(max_deflection, 3),
            "safety_ratio": round(safety_ratio, 2),
            "status": "SAFE" if safety_ratio > 1.5 else "CHECK" if safety_ratio > 1.0 else "UNSAFE",
            "recommendation": self._get_beam_recommendation(safety_ratio, beam_length_ft)
        }
    
    def _get_beam_recommendation(self, safety_ratio: float, length_ft: float) -> str:
        """Generate recommendation based on beam analysis"""
        if safety_ratio > 3.0:
            return "Beam is oversized - could use smaller material"
        elif safety_ratio > 1.5:
            return "Good design - adequate safety margin"
        elif safety_ratio > 1.0:
            return "Marginal - add center support or upgrade material"
        else:
            if length_ft > 8:
                return "UNSAFE - reduce span or use larger beam"
            else:
                return "UNSAFE - upgrade to larger beam size"
    
    def calculate_foundation_size(self, structure_weight_lbs: float,
                                soil_type: str = "average") -> Dict:
        """Calculate foundation footing size"""
        # Soil bearing capacity (lbs per sq ft)
        soil_capacities = {
            "rock": 12000,
            "hard_clay": 4000,
            "average": 2000,
            "soft_clay": 1000,
            "sand": 3000
        }
        
        if soil_type not in soil_capacities:
            soil_type = "average"
        
        bearing_capacity = soil_capacities[soil_type]
        safety_factor = 2.0  # Conservative safety factor
        
        required_area = (structure_weight_lbs * safety_factor) / bearing_capacity
        
        # Assume square footing
        footing_width = math.sqrt(required_area)
        
        return {
            "structure_weight_lbs": structure_weight_lbs,
            "soil_type": soil_type,
            "soil_capacity_psf": bearing_capacity,
            "required_area_sqft": round(required_area, 1),
            "recommended_width_ft": round(footing_width, 1),
            "recommended_depth_ft": max(1.5, footing_width / 6),  # Minimum 18" deep
            "concrete_needed_cubic_ft": round(required_area * max(1.5, footing_width / 6), 1)
        }
    
    def get_material_alternatives(self, original_material: str) -> List[Dict]:
        """Get alternative materials with trade-offs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT substitute_material, strength_ratio, cost_ratio, availability, notes
            FROM material_substitutions
            WHERE original_material = ?
        ''', (original_material,))
        
        alternatives = []
        for row in cursor.fetchall():
            alternatives.append({
                "material": row[0],
                "strength_ratio": row[1],
                "cost_ratio": row[2],
                "availability": row[3],
                "notes": row[4]
            })
        
        conn.close()
        return alternatives
    
    def get_building_guide(self, project_id: int) -> Dict:
        """Get complete building guide for a project"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get project info
        cursor.execute("SELECT * FROM building_projects WHERE id = ?", (project_id,))
        project_row = cursor.fetchone()
        if not project_row:
            return {}
        
        project_columns = [desc[0] for desc in cursor.description]
        project = dict(zip(project_columns, project_row))
        
        # Get phases
        cursor.execute('''
            SELECT * FROM construction_phases 
            WHERE project_id = ? 
            ORDER BY phase_order
        ''', (project_id,))
        
        phase_columns = [desc[0] for desc in cursor.description]
        phases = []
        
        for row in cursor.fetchall():
            phase = dict(zip(phase_columns, row))
            
            # Get visual guides for this phase
            cursor.execute('''
                SELECT * FROM visual_guides 
                WHERE phase_id = ?
            ''', (phase['id'],))
            
            guide_columns = [desc[0] for desc in cursor.description]
            visual_guides = []
            
            for guide_row in cursor.fetchall():
                visual_guides.append(dict(zip(guide_columns, guide_row)))
            
            phase['visual_guides'] = visual_guides
            phases.append(phase)
        
        project['phases'] = phases
        
        conn.close()
        return project
    
    def initialize_default_guides(self):
        """Initialize database with default building guides"""
        # Add material substitutions
        substitutions = [
            ("2x4_lumber", "2x3_lumber", 0.75, 0.85, "common", "Slightly less strength"),
            ("2x4_lumber", "metal_studs", 1.2, 1.4, "common", "More precise, rust-resistant"),
            ("plywood", "osb", 0.85, 0.7, "very_common", "More water-sensitive"),
            ("concrete_blocks", "sandbags", 0.6, 0.3, "emergency", "Temporary solution"),
            ("pvc_pipe", "copper_pipe", 2.0, 3.0, "common", "Much stronger, harder to work"),
            ("tarps", "plastic_sheeting", 0.7, 0.5, "very_common", "Less durable, cheaper")
        ]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for orig, sub, strength, cost, avail, notes in substitutions:
            cursor.execute('''
                INSERT OR IGNORE INTO material_substitutions 
                (original_material, substitute_material, strength_ratio, cost_ratio, availability, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (orig, sub, strength, cost, avail, notes))
        
        conn.commit()
        conn.close()
        
        # Generate default project guides
        self.generate_simple_shelter_guide()
        self.generate_water_collection_system()
        self.generate_simple_cooking_stove()

if __name__ == "__main__":
    # Example usage
    builder = IntuitiveBuilder()
    builder.initialize_default_guides()
    
    # Test beam calculation
    beam_calc = builder.calculate_beam_load(8.0, 500, "2x4_lumber")
    print(f"Beam Analysis: {beam_calc['status']}")
    print(f"Deflection: {beam_calc['deflection_inches']} inches")
    print(f"Recommendation: {beam_calc['recommendation']}")
    
    # Test foundation calculation  
    foundation = builder.calculate_foundation_size(5000, "average")
    print(f"\nFoundation size: {foundation['recommended_width_ft']} ft square")
    print(f"Concrete needed: {foundation['concrete_needed_cubic_ft']} cubic feet")
    
    # Get building guide
    guides = builder.get_building_guide(1)  # First project
    if guides:
        print(f"\nProject: {guides['name']}")
        print(f"Phases: {len(guides['phases'])}")
        for phase in guides['phases']:
            print(f"  - {phase['phase_name']}: {phase['time_estimate']}")