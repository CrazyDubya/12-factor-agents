#!/usr/bin/env python3
"""
Materials and Tools Calculator for Disaster Preparedness Building Projects
Calculate exact quantities, costs, and alternatives for construction projects
"""

import json
import sqlite3
import math
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class MaterialsCalculator:
    def __init__(self, db_path: str = "materials_calculator.db"):
        self.db_path = db_path
        self.init_database()
        
        # Standard material properties and costs (USD, typical retail)
        self.material_database = {
            "lumber_2x4_8ft": {
                "unit": "each", "cost_per_unit": 4.50, "weight_lbs": 9.0,
                "dimensions": {"length": 8, "width": 3.5, "height": 1.5},
                "strength_rating": 8, "weather_rating": 6, "workability": 9
            },
            "lumber_2x6_8ft": {
                "unit": "each", "cost_per_unit": 8.50, "weight_lbs": 13.0,
                "dimensions": {"length": 8, "width": 5.5, "height": 1.5},
                "strength_rating": 9, "weather_rating": 6, "workability": 8
            },
            "plywood_4x8_half": {
                "unit": "sheet", "cost_per_unit": 35.0, "weight_lbs": 38.0,
                "dimensions": {"length": 8, "width": 4, "height": 0.5},
                "strength_rating": 7, "weather_rating": 4, "workability": 9
            },
            "concrete_block_8x8x16": {
                "unit": "each", "cost_per_unit": 2.25, "weight_lbs": 35.0,
                "dimensions": {"length": 16, "width": 8, "height": 8},
                "strength_rating": 10, "weather_rating": 10, "workability": 6
            },
            "pvc_pipe_4in_10ft": {
                "unit": "each", "cost_per_unit": 12.0, "weight_lbs": 8.0,
                "dimensions": {"length": 10, "width": 4, "height": 4},
                "strength_rating": 4, "weather_rating": 9, "workability": 10
            },
            "tarp_10x12_heavy": {
                "unit": "each", "cost_per_unit": 25.0, "weight_lbs": 3.0,
                "dimensions": {"length": 12, "width": 10, "height": 0.01},
                "strength_rating": 5, "weather_rating": 8, "workability": 10
            },
            "rebar_half_inch_20ft": {
                "unit": "each", "cost_per_unit": 8.50, "weight_lbs": 10.0,
                "dimensions": {"length": 20, "width": 0.5, "height": 0.5},
                "strength_rating": 10, "weather_rating": 8, "workability": 4
            },
            "portland_cement_94lb": {
                "unit": "bag", "cost_per_unit": 4.75, "weight_lbs": 94.0,
                "coverage": {"cubic_feet": 0.75}, "mix_ratio": "1:2:3",
                "strength_rating": 9, "weather_rating": 10, "workability": 6
            },
            "gravel_50lb_bag": {
                "unit": "bag", "cost_per_unit": 3.25, "weight_lbs": 50.0,
                "coverage": {"cubic_feet": 0.5},
                "strength_rating": 8, "weather_rating": 10, "workability": 8
            },
            "sand_50lb_bag": {
                "unit": "bag", "cost_per_unit": 2.85, "weight_lbs": 50.0,
                "coverage": {"cubic_feet": 0.4},
                "strength_rating": 6, "weather_rating": 10, "workability": 9
            }
        }
        
        self.tool_database = {
            "hammer_16oz": {"cost": 15.0, "essential": True, "rental": False},
            "saw_circular_7_25": {"cost": 85.0, "essential": True, "rental": True},
            "drill_cordless": {"cost": 60.0, "essential": True, "rental": True},
            "level_24in": {"cost": 25.0, "essential": True, "rental": False},
            "tape_measure_25ft": {"cost": 12.0, "essential": True, "rental": False},
            "square_framing": {"cost": 8.0, "essential": True, "rental": False},
            "shovel": {"cost": 25.0, "essential": False, "rental": False},
            "wheelbarrow": {"cost": 120.0, "essential": False, "rental": True},
            "cement_mixer": {"cost": 450.0, "essential": False, "rental": True}
        }
    
    def init_database(self):
        """Initialize database for materials calculations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS project_calculations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name TEXT NOT NULL,
                project_type TEXT,
                dimensions TEXT,
                calculated_materials TEXT,
                total_cost REAL,
                total_weight REAL,
                difficulty_score INTEGER,
                created_date TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS material_pricing (
                material_id TEXT PRIMARY KEY,
                current_price REAL,
                price_date TEXT,
                supplier TEXT,
                location TEXT,
                availability TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tool_requirements (
                project_id INTEGER,
                tool_name TEXT,
                required INTEGER,
                alternative TEXT,
                rental_cost_daily REAL,
                FOREIGN KEY (project_id) REFERENCES project_calculations (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def calculate_frame_materials(self, length_ft: float, width_ft: float, 
                                height_ft: float, spacing_ft: float = 2.0) -> Dict:
        """Calculate materials for basic frame structure"""
        
        # Calculate number of studs needed
        wall_perimeter = 2 * (length_ft + width_ft)
        studs_needed = math.ceil(wall_perimeter / spacing_ft) + 4  # Add corners
        
        # Calculate plates (top and bottom)
        plate_length = wall_perimeter * 2  # Double plates
        plates_needed = math.ceil(plate_length / 8)  # 8ft lumber pieces
        
        # Calculate headers and blocking
        door_openings = 2  # Assume 2 openings
        header_pieces = door_openings * 2
        
        # Total lumber calculation
        total_2x4s = studs_needed + plates_needed + header_pieces
        
        # Sheathing calculation (plywood)
        wall_area = wall_perimeter * height_ft
        sheet_area = 4 * 8  # 4x8 sheets
        sheets_needed = math.ceil(wall_area / sheet_area)
        
        materials = {
            "lumber_2x4_8ft": {
                "quantity": total_2x4s,
                "purpose": "Framing studs, plates, headers",
                "unit_cost": self.material_database["lumber_2x4_8ft"]["cost_per_unit"],
                "total_cost": total_2x4s * self.material_database["lumber_2x4_8ft"]["cost_per_unit"]
            },
            "plywood_4x8_half": {
                "quantity": sheets_needed,
                "purpose": "Wall sheathing",
                "unit_cost": self.material_database["plywood_4x8_half"]["cost_per_unit"],
                "total_cost": sheets_needed * self.material_database["plywood_4x8_half"]["cost_per_unit"]
            }
        }
        
        total_cost = sum(item["total_cost"] for item in materials.values())
        total_weight = (total_2x4s * 9.0) + (sheets_needed * 38.0)  # lbs
        
        return {
            "project_type": "frame_structure",
            "dimensions": {"length": length_ft, "width": width_ft, "height": height_ft},
            "materials": materials,
            "total_cost": round(total_cost, 2),
            "total_weight": round(total_weight, 1),
            "construction_notes": [
                f"Stud spacing: {spacing_ft} feet on center",
                f"Total wall area: {wall_area} sq ft",
                f"Material efficiency: {round((wall_area / sheets_needed) / sheet_area * 100, 1)}%"
            ]
        }
    
    def calculate_foundation_materials(self, length_ft: float, width_ft: float,
                                     thickness_ft: float = 0.5, 
                                     foundation_type: str = "concrete_pad") -> Dict:
        """Calculate foundation materials"""
        
        area_sqft = length_ft * width_ft
        volume_cuft = area_sqft * thickness_ft
        
        if foundation_type == "concrete_pad":
            # Concrete calculation - typical mix is 1:2:3 (cement:sand:gravel)
            cement_cuft = volume_cuft / 6  # 1/6 of total volume
            sand_cuft = volume_cuft / 3    # 2/6 of total volume  
            gravel_cuft = volume_cuft / 2  # 3/6 of total volume
            
            # Convert to bags
            cement_bags = math.ceil(cement_cuft / 0.75)  # 94lb bag coverage
            sand_bags = math.ceil(sand_cuft / 0.4)       # 50lb bag coverage
            gravel_bags = math.ceil(gravel_cuft / 0.5)   # 50lb bag coverage
            
            materials = {
                "portland_cement_94lb": {
                    "quantity": cement_bags,
                    "purpose": "Concrete binder",
                    "unit_cost": self.material_database["portland_cement_94lb"]["cost_per_unit"],
                    "total_cost": cement_bags * self.material_database["portland_cement_94lb"]["cost_per_unit"]
                },
                "sand_50lb_bag": {
                    "quantity": sand_bags,
                    "purpose": "Concrete aggregate",
                    "unit_cost": self.material_database["sand_50lb_bag"]["cost_per_unit"],
                    "total_cost": sand_bags * self.material_database["sand_50lb_bag"]["cost_per_unit"]
                },
                "gravel_50lb_bag": {
                    "quantity": gravel_bags,
                    "purpose": "Concrete aggregate",
                    "unit_cost": self.material_database["gravel_50lb_bag"]["cost_per_unit"],
                    "total_cost": gravel_bags * self.material_database["gravel_50lb_bag"]["cost_per_unit"]
                }
            }
            
        elif foundation_type == "block":
            # Concrete block calculation
            block_area = (16/12) * (8/12)  # Convert inches to feet
            blocks_needed = math.ceil(area_sqft / block_area)
            
            materials = {
                "concrete_block_8x8x16": {
                    "quantity": blocks_needed,
                    "purpose": "Foundation blocks",
                    "unit_cost": self.material_database["concrete_block_8x8x16"]["cost_per_unit"],
                    "total_cost": blocks_needed * self.material_database["concrete_block_8x8x16"]["cost_per_unit"]
                }
            }
        
        total_cost = sum(item["total_cost"] for item in materials.values())
        
        return {
            "project_type": f"foundation_{foundation_type}",
            "dimensions": {"length": length_ft, "width": width_ft, "thickness": thickness_ft},
            "materials": materials,
            "total_cost": round(total_cost, 2),
            "volume_cubic_feet": round(volume_cuft, 2),
            "construction_notes": [
                f"Foundation area: {area_sqft} sq ft",
                f"Concrete volume: {volume_cuft} cubic feet",
                "Allow 7 days for full cure"
            ]
        }
    
    def calculate_roofing_materials(self, length_ft: float, width_ft: float,
                                  roof_type: str = "gable", pitch: float = 4.0) -> Dict:
        """Calculate roofing materials based on roof type and pitch"""
        
        base_area = length_ft * width_ft
        
        if roof_type == "gable":
            # Gable roof - calculate slope multiplier
            pitch_factor = math.sqrt(1 + (pitch/12)**2)
            roof_area = base_area * pitch_factor
            
        elif roof_type == "shed":
            # Shed roof - simple slope
            pitch_factor = math.sqrt(1 + (pitch/12)**2)  
            roof_area = base_area * pitch_factor
            
        elif roof_type == "flat":
            roof_area = base_area
            
        # Rafters calculation
        if roof_type == "gable":
            rafter_length = math.sqrt((width_ft/2)**2 + (pitch * width_ft/24)**2)
            rafters_needed = math.ceil(length_ft / 2) * 2  # Every 2 feet
        else:
            rafter_length = math.sqrt(width_ft**2 + (pitch * width_ft/12)**2)
            rafters_needed = math.ceil(length_ft / 2)
        
        # Account for rafter length - use appropriate lumber
        if rafter_length <= 8:
            lumber_type = "lumber_2x6_8ft"
        else:
            lumber_type = "lumber_2x6_8ft"  # Would need multiple pieces
            rafters_needed *= math.ceil(rafter_length / 8)
        
        # Sheathing calculation
        sheets_needed = math.ceil(roof_area / 32)  # 4x8 sheets = 32 sq ft
        
        # Roofing material (assume metal or shingles)
        roofing_squares = math.ceil(roof_area / 100)  # 100 sq ft per square
        
        materials = {
            lumber_type: {
                "quantity": rafters_needed,
                "purpose": "Roof rafters",
                "unit_cost": self.material_database[lumber_type]["cost_per_unit"],
                "total_cost": rafters_needed * self.material_database[lumber_type]["cost_per_unit"]
            },
            "plywood_4x8_half": {
                "quantity": sheets_needed,
                "purpose": "Roof sheathing",
                "unit_cost": self.material_database["plywood_4x8_half"]["cost_per_unit"],
                "total_cost": sheets_needed * self.material_database["plywood_4x8_half"]["cost_per_unit"]
            },
            "metal_roofing": {
                "quantity": roofing_squares,
                "purpose": "Weather protection",
                "unit_cost": 120.0,  # Estimated per square
                "total_cost": roofing_squares * 120.0
            }
        }
        
        total_cost = sum(item["total_cost"] for item in materials.values())
        
        return {
            "project_type": f"roof_{roof_type}",
            "dimensions": {"length": length_ft, "width": width_ft, "pitch": pitch},
            "materials": materials,
            "total_cost": round(total_cost, 2),
            "roof_area": round(roof_area, 1),
            "construction_notes": [
                f"Roof area: {roof_area} sq ft",
                f"Rafter length: {round(rafter_length, 1)} ft",
                f"Pitch factor: {round(pitch_factor, 2)}"
            ]
        }
    
    def calculate_complete_shelter(self, length_ft: float, width_ft: float,
                                 height_ft: float = 8.0, include_foundation: bool = True) -> Dict:
        """Calculate materials for complete shelter structure"""
        
        # Calculate all components
        frame_calc = self.calculate_frame_materials(length_ft, width_ft, height_ft)
        roof_calc = self.calculate_roofing_materials(length_ft, width_ft)
        
        combined_materials = {}
        combined_materials.update(frame_calc["materials"])
        
        # Merge roof materials
        for material, details in roof_calc["materials"].items():
            if material in combined_materials:
                combined_materials[material]["quantity"] += details["quantity"]
                combined_materials[material]["total_cost"] += details["total_cost"]
                combined_materials[material]["purpose"] += f", {details['purpose']}"
            else:
                combined_materials[material] = details
        
        total_cost = frame_calc["total_cost"] + roof_calc["total_cost"]
        
        if include_foundation:
            foundation_calc = self.calculate_foundation_materials(length_ft, width_ft)
            total_cost += foundation_calc["total_cost"]
            
            # Add foundation materials
            for material, details in foundation_calc["materials"].items():
                combined_materials[material] = details
        
        # Calculate tools needed
        required_tools = self.calculate_tools_needed("complete_shelter")
        
        return {
            "project_type": "complete_shelter",
            "dimensions": {"length": length_ft, "width": width_ft, "height": height_ft},
            "materials": combined_materials,
            "tools": required_tools,
            "total_material_cost": round(total_cost, 2),
            "total_tool_cost": sum(tool["cost"] for tool in required_tools.values()),
            "estimated_build_time": "40-60 hours with 2 people",
            "difficulty_level": "intermediate",
            "construction_notes": [
                "Foundation must cure 7 days before framing",
                "Frame first, then roof, then sheathing",
                "Check local building codes",
                "Consider permit requirements"
            ]
        }
    
    def calculate_tools_needed(self, project_type: str) -> Dict:
        """Calculate tools needed for project type"""
        
        tool_requirements = {
            "complete_shelter": [
                "hammer_16oz", "saw_circular_7_25", "drill_cordless", 
                "level_24in", "tape_measure_25ft", "square_framing",
                "shovel", "wheelbarrow"
            ],
            "foundation": [
                "shovel", "wheelbarrow", "level_24in", "tape_measure_25ft",
                "cement_mixer"
            ],
            "frame_only": [
                "hammer_16oz", "saw_circular_7_25", "drill_cordless",
                "level_24in", "tape_measure_25ft", "square_framing"
            ]
        }
        
        required_tools = {}
        for tool in tool_requirements.get(project_type, []):
            if tool in self.tool_database:
                required_tools[tool] = {
                    "cost": self.tool_database[tool]["cost"],
                    "essential": self.tool_database[tool]["essential"],
                    "rental_available": self.tool_database[tool]["rental"]
                }
        
        return required_tools
    
    def optimize_materials(self, materials_needed: Dict, budget_limit: Optional[float] = None) -> Dict:
        """Optimize materials list for cost or availability"""
        
        optimized = {}
        total_savings = 0
        
        for material, details in materials_needed.items():
            current_cost = details["total_cost"]
            quantity = details["quantity"]
            
            # Check for bulk pricing (10+ units get 10% discount)
            if quantity >= 10:
                bulk_discount = current_cost * 0.10
                optimized_cost = current_cost - bulk_discount
                total_savings += bulk_discount
                
                optimized[material] = details.copy()
                optimized[material]["total_cost"] = optimized_cost
                optimized[material]["savings"] = bulk_discount
                optimized[material]["notes"] = "Bulk pricing applied"
            else:
                optimized[material] = details.copy()
        
        return {
            "optimized_materials": optimized,
            "total_savings": round(total_savings, 2),
            "optimization_notes": [
                "Bulk discounts applied where applicable",
                "Consider buying in larger quantities",
                "Check local suppliers for better pricing"
            ]
        }
    
    def save_calculation(self, project_name: str, calculation_result: Dict) -> int:
        """Save calculation to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO project_calculations (project_name, project_type, dimensions,
                                            calculated_materials, total_cost, total_weight)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (project_name, calculation_result["project_type"],
              json.dumps(calculation_result["dimensions"]),
              json.dumps(calculation_result["materials"]),
              calculation_result["total_cost"],
              calculation_result.get("total_weight", 0)))
        
        calc_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return calc_id

if __name__ == "__main__":
    # Example usage
    calculator = MaterialsCalculator()
    
    print("=== DISASTER PREPAREDNESS SHELTER CALCULATOR ===\n")
    
    # Calculate complete 10x12 shelter
    shelter_calc = calculator.calculate_complete_shelter(10, 12, 8)
    
    print(f"Project: Complete Emergency Shelter")
    print(f"Dimensions: 10' x 12' x 8' high")
    print(f"Total Material Cost: ${shelter_calc['total_material_cost']:,.2f}")
    print(f"Total Tool Cost: ${shelter_calc['total_tool_cost']:,.2f}")
    print(f"Build Time: {shelter_calc['estimated_build_time']}")
    
    print(f"\nMATERIALS BREAKDOWN:")
    for material, details in shelter_calc["materials"].items():
        print(f"  {material}: {details['quantity']} {self.material_database.get(material, {}).get('unit', 'units')} - ${details['total_cost']:.2f}")
    
    print(f"\nTOOLS NEEDED:")
    for tool, details in shelter_calc["tools"].items():
        rental_note = " (rental available)" if details["rental_available"] else ""
        essential = " *ESSENTIAL*" if details["essential"] else ""
        print(f"  {tool}: ${details['cost']:.2f}{rental_note}{essential}")
    
    # Optimize for cost
    optimized = calculator.optimize_materials(shelter_calc["materials"])
    if optimized["total_savings"] > 0:
        print(f"\nCOST OPTIMIZATION:")
        print(f"Potential savings: ${optimized['total_savings']:.2f}")
        print("Optimization tips:")
        for tip in optimized["optimization_notes"]:
            print(f"  • {tip}")
    
    # Save calculation
    calc_id = calculator.save_calculation("Emergency Shelter 10x12", shelter_calc)
    print(f"\nCalculation saved with ID: {calc_id}")