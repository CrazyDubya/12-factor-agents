#!/usr/bin/env python3
"""
EMP/Solar Flare Hardening Module - Version 2.0
Protection against electromagnetic pulse and solar events

Target: Improve EMP event preparedness from 41.0% to 60%+
"""

import sqlite3
import json
import math
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import random

class EMPHardeningModule:
    def __init__(self, db_path: str = "modern_threats.db"):
        """Initialize EMP Hardening Module with comprehensive protection systems"""
        self.db_path = db_path
        self.init_database()
        self.load_emp_threats()
        self.initialize_protection_systems()
    
    def init_database(self):
        """Initialize database for EMP hardening data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Faraday cage designs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS faraday_cages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cage_name TEXT NOT NULL,
                size_category TEXT,
                materials TEXT,
                cost_estimate REAL,
                effectiveness_db INTEGER,
                build_time TEXT,
                difficulty_level INTEGER,
                items_protected TEXT,
                instructions TEXT
            )
        ''')
        
        # Protected equipment inventory
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS protected_equipment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                equipment_name TEXT NOT NULL,
                equipment_type TEXT,
                priority_level INTEGER,
                protection_method TEXT,
                backup_available BOOLEAN,
                manual_alternative TEXT,
                last_tested TIMESTAMP,
                notes TEXT
            )
        ''')
        
        # Manual system alternatives
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS manual_systems (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                electronic_system TEXT NOT NULL,
                manual_alternative TEXT,
                tools_required TEXT,
                skill_level INTEGER,
                setup_time TEXT,
                effectiveness_rating INTEGER,
                instructions TEXT
            )
        ''')
        
        # Grid-independent utilities
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS independent_utilities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                utility_type TEXT NOT NULL,
                independent_solution TEXT,
                equipment_needed TEXT,
                cost_estimate REAL,
                maintenance_schedule TEXT,
                capacity_rating TEXT,
                installation_time TEXT
            )
        ''')
        
        # Hardened communications
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hardened_comms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                comm_method TEXT NOT NULL,
                protection_level INTEGER,
                equipment_list TEXT,
                frequency_range TEXT,
                range_miles REAL,
                setup_instructions TEXT,
                backup_power TEXT
            )
        ''')
        
        # EMP event planning
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS emp_response_plan (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phase_name TEXT NOT NULL,
                time_frame TEXT,
                priority_actions TEXT,
                resources_needed TEXT,
                personnel_required INTEGER,
                success_criteria TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def load_emp_threats(self):
        """Load EMP and solar flare threat scenarios"""
        self.emp_threats = {
            "solar_flare": {
                "probability": 0.12,  # Carrington Event level per decade
                "warning_time": 18,  # Hours (from detection)
                "impact_radius": "Hemisphere",
                "duration": "Days to weeks",
                "effects": [
                    "Power grid collapse",
                    "Satellite disruption", 
                    "Communications blackout",
                    "GPS failure",
                    "Internet infrastructure damage"
                ],
                "protection_effectiveness": {
                    "faraday_cage": 0.95,
                    "unplugged": 0.70,
                    "surge_protector": 0.30,
                    "nothing": 0.05
                }
            },
            "nuclear_emp": {
                "probability": 0.02,  # Annual
                "warning_time": 0,  # Minutes
                "impact_radius": "500-1000 miles",
                "duration": "Instant + months recovery",
                "effects": [
                    "Instant electronics failure",
                    "Vehicle ECU damage",
                    "Power grid destruction",
                    "Water pump failure",
                    "Banking system collapse"
                ],
                "protection_effectiveness": {
                    "faraday_cage": 0.90,
                    "metal_building": 0.60,
                    "underground": 0.80,
                    "nothing": 0.02
                }
            },
            "localized_emp": {
                "probability": 0.05,  # Terrorist/military
                "warning_time": 0,
                "impact_radius": "1-10 miles",
                "duration": "Instant",
                "effects": [
                    "Local electronics failure",
                    "Building systems down",
                    "Local communications out",
                    "Security systems fail",
                    "Medical equipment damaged"
                ],
                "protection_effectiveness": {
                    "faraday_cage": 0.95,
                    "distance": 0.50,
                    "shielded_room": 0.85,
                    "nothing": 0.10
                }
            }
        }
    
    def initialize_protection_systems(self):
        """Initialize comprehensive EMP protection systems"""
        self.protection_systems = {
            "faraday_designs": {
                "trash_can": {
                    "size": "Small items",
                    "materials": ["Galvanized trash can", "Aluminum tape", "Cardboard"],
                    "effectiveness": 40,  # dB attenuation
                    "cost": 50
                },
                "ammo_can": {
                    "size": "Handheld devices",
                    "materials": ["Metal ammo can", "Foam padding", "Conductive tape"],
                    "effectiveness": 50,
                    "cost": 30
                },
                "room_cage": {
                    "size": "Entire room",
                    "materials": ["Copper mesh", "Aluminum foil", "Conductive paint"],
                    "effectiveness": 60,
                    "cost": 500
                },
                "mylar_bag": {
                    "size": "Small electronics",
                    "materials": ["Anti-static bags", "Mylar blankets", "Tape"],
                    "effectiveness": 30,
                    "cost": 20
                }
            },
            "critical_electronics": {
                "communications": ["HAM radio", "CB radio", "Weather radio", "Walkie-talkies"],
                "power": ["Solar charge controller", "Inverter", "Batteries", "Generator parts"],
                "computing": ["Laptop", "Tablets", "USB drives", "External drives"],
                "medical": ["Glucose meter", "CPAP", "Hearing aids", "Medical monitors"],
                "tools": ["Multimeter", "Oscilloscope", "Soldering iron", "Power tools"]
            },
            "manual_alternatives": {
                "navigation": "Paper maps and magnetic compass",
                "calculation": "Slide rule and abacus",
                "communication": "Mirrors and flags",
                "lighting": "Oil lamps and candles",
                "cooking": "Wood stove and manual tools",
                "water": "Hand pump and gravity feed",
                "security": "Mechanical locks and dogs"
            }
        }
    
    def assess_emp_vulnerability(self, household_items: Dict = None) -> Dict:
        """Assess household vulnerability to EMP events"""
        assessment = {
            "assessment_date": datetime.now().isoformat(),
            "vulnerability_score": 100,  # Start at maximum vulnerability
            "protected_items": 0,
            "vulnerable_items": 0,
            "critical_gaps": [],
            "protection_level": "CRITICAL",
            "recommendations": []
        }
        
        if not household_items:
            household_items = self.get_typical_household_items()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check protection levels
        for category, items in household_items.items():
            for item in items:
                cursor.execute("""
                    SELECT protection_method FROM protected_equipment 
                    WHERE equipment_name = ?
                """, (item,))
                result = cursor.fetchone()
                
                if result and result[0] != "None":
                    assessment["protected_items"] += 1
                    assessment["vulnerability_score"] -= 2
                else:
                    assessment["vulnerable_items"] += 1
                    if category in ["communications", "medical", "power"]:
                        assessment["critical_gaps"].append(f"Unprotected: {item}")
        
        # Check Faraday cage availability
        cursor.execute("SELECT COUNT(*) FROM faraday_cages")
        cage_count = cursor.fetchone()[0]
        
        if cage_count > 0:
            assessment["vulnerability_score"] -= (cage_count * 10)
            assessment["protection_level"] = "PARTIAL"
        
        # Check manual alternatives
        cursor.execute("SELECT COUNT(*) FROM manual_systems")
        manual_count = cursor.fetchone()[0]
        
        if manual_count > 10:
            assessment["vulnerability_score"] -= 20
            assessment["protection_level"] = "MODERATE"
        
        # Check grid-independent utilities
        cursor.execute("SELECT COUNT(*) FROM independent_utilities")
        independent_count = cursor.fetchone()[0]
        
        if independent_count > 3:
            assessment["vulnerability_score"] -= 15
            assessment["protection_level"] = "GOOD"
        
        conn.close()
        
        # Generate recommendations
        if assessment["vulnerability_score"] > 70:
            assessment["recommendations"] = [
                "URGENT: Build basic Faraday cages immediately",
                "Store critical electronics in protection",
                "Develop manual operation procedures",
                "Acquire non-electronic alternatives"
            ]
        elif assessment["vulnerability_score"] > 40:
            assessment["recommendations"] = [
                "Expand Faraday cage capacity",
                "Test protection methods regularly",
                "Increase manual system alternatives",
                "Develop grid-independent utilities"
            ]
        else:
            assessment["recommendations"] = [
                "Maintain current protection levels",
                "Regular testing and rotation",
                "Update protection as technology changes"
            ]
        
        assessment["vulnerability_score"] = max(0, assessment["vulnerability_score"])
        
        return assessment
    
    def design_faraday_cage(self, size_needed: str = "medium", budget: float = 100) -> Dict:
        """Design appropriate Faraday cage based on needs and budget"""
        design = {
            "design_date": datetime.now().isoformat(),
            "size_category": size_needed,
            "budget": budget,
            "recommended_design": {},
            "materials_list": [],
            "build_instructions": [],
            "effectiveness_rating": 0,
            "total_cost": 0
        }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Determine best design for size and budget
        if size_needed == "small" and budget < 50:
            design_type = "ammo_can"
            materials = [
                ("Metal ammo can (50 cal)", 25),
                ("Conductive foam padding", 10),
                ("Aluminum HVAC tape", 8),
                ("Rubber gasket seal", 5)
            ]
            effectiveness = 50
            
        elif size_needed == "medium" and budget < 100:
            design_type = "trash_can"
            materials = [
                ("31-gallon galvanized trash can", 40),
                ("Aluminum HVAC tape", 15),
                ("Cardboard for lining", 10),
                ("Foam padding sheets", 20),
                ("Conductive copper tape", 10)
            ]
            effectiveness = 45
            
        elif size_needed == "large" and budget < 300:
            design_type = "cabinet"
            materials = [
                ("Metal filing cabinet", 100),
                ("Copper mesh screen", 80),
                ("Conductive adhesive", 30),
                ("Weather stripping", 20),
                ("Aluminum foil (heavy duty)", 40)
            ]
            effectiveness = 55
            
        else:  # Room-sized or unlimited budget
            design_type = "room"
            materials = [
                ("Copper mesh (100 sq ft)", 300),
                ("Aluminum foil (1000 sq ft)", 150),
                ("Conductive paint (5 gallons)", 200),
                ("Copper tape (500 ft)", 100),
                ("Grounding kit", 50)
            ]
            effectiveness = 65
        
        # Calculate total cost
        for item, cost in materials:
            design["materials_list"].append({"item": item, "cost": cost})
            design["total_cost"] += cost
        
        # Generate build instructions
        if design_type == "ammo_can":
            design["build_instructions"] = [
                "Clean ammo can thoroughly, remove any rust",
                "Test seal - should be watertight when closed",
                "Line interior with non-conductive foam padding",
                "Create item compartments with cardboard dividers",
                "Wrap items in anti-static bags before storing",
                "Seal lid gap with aluminum HVAC tape when closed",
                "Test with AM radio - should block signal completely"
            ]
            
        elif design_type == "trash_can":
            design["build_instructions"] = [
                "Purchase galvanized steel trash can (NOT aluminum)",
                "Ensure lid fits tightly with no gaps",
                "Line interior with cardboard (insulation layer)",
                "Add foam padding for device protection",
                "Create shelving with cardboard platforms",
                "Seal lid rim with aluminum tape when closed",
                "Ground the can if possible (wire to ground rod)",
                "Test effectiveness with radio inside"
            ]
            
        elif design_type == "cabinet":
            design["build_instructions"] = [
                "Start with metal filing cabinet (check with magnet)",
                "Remove any plastic or rubber parts",
                "Line interior with copper mesh, ensuring overlap",
                "Seal all seams with conductive adhesive",
                "Add weather stripping to door edges",
                "Ensure door makes metal-to-metal contact when closed",
                "Install copper finger stock on door gaps",
                "Ground cabinet to earth ground if available"
            ]
            
        else:  # Room cage
            design["build_instructions"] = [
                "Calculate room surface area (walls + ceiling + floor)",
                "Install copper mesh on all surfaces, 6-inch overlap",
                "Seal all seams with conductive tape or solder",
                "Pay special attention to door and window openings",
                "Install conductive gaskets on door frame",
                "Cover windows with removable mesh panels",
                "Ground entire cage to building ground system",
                "Test with spectrum analyzer for verification"
            ]
        
        design["effectiveness_rating"] = effectiveness
        
        # Store design in database
        cursor.execute('''
            INSERT INTO faraday_cages
            (cage_name, size_category, materials, cost_estimate, effectiveness_db,
             build_time, difficulty_level, instructions)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (design_type, size_needed, json.dumps(design["materials_list"]),
              design["total_cost"], effectiveness,
              self.estimate_build_time(design_type),
              self.get_difficulty_level(design_type),
              json.dumps(design["build_instructions"])))
        
        conn.commit()
        conn.close()
        
        # Add testing procedure
        design["testing_procedure"] = [
            "Place AM/FM radio inside cage playing loud static",
            "Close/seal the cage completely",
            "Radio should go completely silent if effective",
            "Try cell phone - should lose all signal bars",
            "Use field strength meter for accurate measurement"
        ]
        
        return design
    
    def create_manual_systems_plan(self) -> Dict:
        """Create comprehensive manual backup systems plan"""
        plan = {
            "created_date": datetime.now().isoformat(),
            "manual_systems": {},
            "tools_needed": [],
            "skills_required": [],
            "implementation_timeline": {},
            "total_cost_estimate": 0
        }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Define manual alternatives for critical systems
        systems = [
            {
                "electronic": "GPS Navigation",
                "manual": "Map and compass navigation",
                "tools": ["Topographic maps", "Magnetic compass", "Protractor", "Ruler"],
                "skill": 3,
                "time": "2 hours training",
                "effectiveness": 8
            },
            {
                "electronic": "Electric Water Pump",
                "manual": "Hand pump or gravity system",
                "tools": ["Manual pump", "Check valves", "PVC pipe", "Storage tanks"],
                "skill": 4,
                "time": "1 day installation",
                "effectiveness": 7
            },
            {
                "electronic": "Electronic Ignition",
                "manual": "Magneto or points ignition",
                "tools": ["Magneto kit", "Points/condenser", "Timing light", "Tools"],
                "skill": 5,
                "time": "4 hours installation",
                "effectiveness": 9
            },
            {
                "electronic": "Digital Thermostat",
                "manual": "Mercury or mechanical thermostat",
                "tools": ["Mechanical thermostat", "Thermometer", "Screwdriver"],
                "skill": 2,
                "time": "30 minutes",
                "effectiveness": 8
            },
            {
                "electronic": "Electric Stove",
                "manual": "Wood stove or propane",
                "tools": ["Wood/propane stove", "Chimney/vent", "Fuel supply"],
                "skill": 3,
                "time": "1 day installation",
                "effectiveness": 9
            },
            {
                "electronic": "Security System",
                "manual": "Mechanical locks and bells",
                "tools": ["Deadbolts", "Window locks", "Trip wires", "Bells"],
                "skill": 2,
                "time": "4 hours installation",
                "effectiveness": 7
            },
            {
                "electronic": "Electronic Medical Devices",
                "manual": "Manual medical alternatives",
                "tools": ["Manual BP cuff", "Mechanical scale", "Thermometer", "Stethoscope"],
                "skill": 3,
                "time": "Immediate",
                "effectiveness": 8
            },
            {
                "electronic": "Power Tools",
                "manual": "Hand tools",
                "tools": ["Hand saw", "Manual drill", "Screwdrivers", "Wrenches"],
                "skill": 2,
                "time": "Immediate",
                "effectiveness": 6
            }
        ]
        
        total_cost = 0
        for system in systems:
            # Store in database
            cursor.execute('''
                INSERT INTO manual_systems
                (electronic_system, manual_alternative, tools_required,
                 skill_level, setup_time, effectiveness_rating, instructions)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (system["electronic"], system["manual"], 
                  json.dumps(system["tools"]), system["skill"],
                  system["time"], system["effectiveness"],
                  self.generate_manual_instructions(system)))
            
            plan["manual_systems"][system["electronic"]] = {
                "alternative": system["manual"],
                "setup_time": system["time"],
                "difficulty": f"Level {system['skill']}/5",
                "effectiveness": f"{system['effectiveness']}/10"
            }
            
            plan["tools_needed"].extend(system["tools"])
            
            # Estimate costs
            cost = self.estimate_manual_system_cost(system)
            total_cost += cost
        
        conn.commit()
        conn.close()
        
        plan["total_cost_estimate"] = total_cost
        plan["tools_needed"] = list(set(plan["tools_needed"]))  # Remove duplicates
        
        # Skills development plan
        plan["skills_required"] = [
            "Basic navigation (map and compass)",
            "Manual water pumping",
            "Fire starting and management",
            "Mechanical repair basics",
            "First aid without electronics",
            "Manual calculation methods",
            "Non-electric food preservation"
        ]
        
        # Implementation timeline
        plan["implementation_timeline"] = {
            "Week 1": ["Purchase essential hand tools", "Learn map/compass basics"],
            "Week 2": ["Install mechanical thermostats", "Set up manual water backup"],
            "Week 3": ["Convert to manual locks", "Practice manual cooking"],
            "Week 4": ["Test all manual systems", "Conduct full drill"],
            "Ongoing": ["Monthly practice sessions", "Skill development"]
        }
        
        return plan
    
    def setup_grid_independent_utilities(self, utility_type: str = "all") -> Dict:
        """Design grid-independent utility systems"""
        utilities = {
            "setup_date": datetime.now().isoformat(),
            "utility_type": utility_type,
            "systems": {},
            "equipment_required": [],
            "total_cost": 0,
            "installation_time": "",
            "maintenance_schedule": {}
        }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Define independent utility solutions
        utility_systems = {
            "power": {
                "solution": "Solar + Battery Bank",
                "equipment": [
                    "Solar panels (400W x 4)",
                    "Charge controller (MPPT 60A)",
                    "Deep cycle batteries (200Ah x 4)",
                    "Inverter (3000W pure sine)",
                    "Wiring and breakers"
                ],
                "cost": 3500,
                "capacity": "4.8kWh daily",
                "installation": "2-3 days",
                "maintenance": "Monthly cleaning, annual inspection"
            },
            "water": {
                "solution": "Well + Hand Pump + Storage",
                "equipment": [
                    "Deep well hand pump",
                    "Check valves",
                    "Storage tanks (500 gal)",
                    "Gravity feed system",
                    "Purification filters"
                ],
                "cost": 2000,
                "capacity": "50 gallons/day manual",
                "installation": "2 days",
                "maintenance": "Quarterly filter change"
            },
            "heating": {
                "solution": "Wood Stove + Passive Solar",
                "equipment": [
                    "EPA certified wood stove",
                    "Chimney system",
                    "Heat shields",
                    "Thermal mass materials",
                    "Window insulation"
                ],
                "cost": 2500,
                "capacity": "1500 sq ft heating",
                "installation": "3 days",
                "maintenance": "Annual chimney cleaning"
            },
            "cooling": {
                "solution": "Passive Cooling + Battery Fans",
                "equipment": [
                    "DC ceiling fans",
                    "Window shades",
                    "Ventilation system",
                    "Evaporative cooler",
                    "Insulation upgrade"
                ],
                "cost": 1500,
                "capacity": "10-15°F reduction",
                "installation": "2 days",
                "maintenance": "Seasonal cleaning"
            },
            "waste": {
                "solution": "Composting Toilet + Greywater",
                "equipment": [
                    "Composting toilet system",
                    "Greywater filtration",
                    "Drainage field",
                    "Composting bins",
                    "Ventilation fan"
                ],
                "cost": 1800,
                "capacity": "Family of 4",
                "installation": "2 days",
                "maintenance": "Weekly composting"
            },
            "food_storage": {
                "solution": "Root Cellar + Smoking/Drying",
                "equipment": [
                    "Root cellar construction",
                    "Smoking chamber",
                    "Drying racks",
                    "Canning equipment",
                    "Temperature monitoring"
                ],
                "cost": 1200,
                "capacity": "6 months food storage",
                "installation": "1 week",
                "maintenance": "Monthly inspection"
            }
        }
        
        if utility_type == "all":
            selected_systems = utility_systems
        else:
            selected_systems = {utility_type: utility_systems.get(utility_type, {})}
        
        for util_type, system in selected_systems.items():
            if system:
                # Store in database
                cursor.execute('''
                    INSERT INTO independent_utilities
                    (utility_type, independent_solution, equipment_needed,
                     cost_estimate, maintenance_schedule, capacity_rating,
                     installation_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (util_type, system["solution"], 
                      json.dumps(system["equipment"]),
                      system["cost"], system["maintenance"],
                      system["capacity"], system["installation"]))
                
                utilities["systems"][util_type] = {
                    "solution": system["solution"],
                    "capacity": system["capacity"],
                    "cost": f"${system['cost']}",
                    "installation": system["installation"]
                }
                
                utilities["equipment_required"].extend(system["equipment"])
                utilities["total_cost"] += system["cost"]
                utilities["maintenance_schedule"][util_type] = system["maintenance"]
        
        conn.commit()
        conn.close()
        
        # Add prioritization
        utilities["implementation_priority"] = [
            "1. Water (essential for survival)",
            "2. Power (enables other systems)",
            "3. Heating/Cooling (climate dependent)",
            "4. Waste (sanitation critical)",
            "5. Food Storage (long-term sustainability)"
        ]
        
        # Add integration notes
        utilities["integration_notes"] = {
            "power_dependencies": "Water pump, cooling fans, lighting",
            "water_uses": "Drinking, cooking, hygiene, cooling",
            "synergies": "Solar powers water pump, composting creates fertilizer",
            "backup_systems": "Manual overrides for all powered systems"
        }
        
        return utilities
    
    def create_hardened_communications(self) -> Dict:
        """Design EMP-hardened communication systems"""
        comm_system = {
            "created_date": datetime.now().isoformat(),
            "primary_systems": {},
            "backup_systems": {},
            "protection_methods": {},
            "equipment_list": [],
            "frequency_plan": {},
            "total_cost": 0
        }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Define hardened communication methods
        comm_methods = [
            {
                "method": "Tube-based HAM Radio",
                "protection": 9,
                "equipment": [
                    "Vacuum tube transceiver",
                    "Manual antenna tuner",
                    "Dipole antenna wire",
                    "12V battery bank",
                    "Mechanical keyer"
                ],
                "frequency": "HF bands 3-30 MHz",
                "range": 1000,
                "setup": "Store in Faraday cage, deploy post-EMP",
                "backup_power": "Deep cycle batteries + manual charger"
            },
            {
                "method": "Crystal Radio",
                "protection": 10,
                "equipment": [
                    "Crystal diode",
                    "Variable capacitor",
                    "Coil wire",
                    "High impedance headphones",
                    "Long wire antenna"
                ],
                "frequency": "AM broadcast band",
                "range": 50,
                "setup": "No power required, instant operation",
                "backup_power": "None needed"
            },
            {
                "method": "Spark Gap Transmitter",
                "protection": 10,
                "equipment": [
                    "Spark gap assembly",
                    "Induction coil",
                    "Telegraph key",
                    "Antenna system",
                    "Power source"
                ],
                "frequency": "Wide band interference",
                "range": 20,
                "setup": "Emergency only - causes interference",
                "backup_power": "Hand crank generator"
            },
            {
                "method": "Optical Signaling",
                "protection": 10,
                "equipment": [
                    "Signal mirrors",
                    "Powerful LED flashlights",
                    "Colored filters",
                    "Binoculars",
                    "Morse code chart"
                ],
                "frequency": "Visual light",
                "range": 10,
                "setup": "Line of sight required",
                "backup_power": "Solar rechargeable batteries"
            },
            {
                "method": "Mechanical Telegraph",
                "protection": 10,
                "equipment": [
                    "Telegraph sounder",
                    "Telegraph key",
                    "Wire (miles)",
                    "Batteries",
                    "Insulators"
                ],
                "frequency": "Direct current",
                "range": 100,
                "setup": "Requires wire connection",
                "backup_power": "Chemical batteries (homemade)"
            }
        ]
        
        for method in comm_methods:
            # Store in database
            cursor.execute('''
                INSERT INTO hardened_comms
                (comm_method, protection_level, equipment_list, frequency_range,
                 range_miles, setup_instructions, backup_power)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (method["method"], method["protection"],
                  json.dumps(method["equipment"]), method["frequency"],
                  method["range"], method["setup"], method["backup_power"]))
            
            comm_system["primary_systems"][method["method"]] = {
                "protection_level": f"{method['protection']}/10",
                "range": f"{method['range']} miles",
                "power": method["backup_power"]
            }
            
            comm_system["equipment_list"].extend(method["equipment"])
            
            # Estimate costs
            cost = self.estimate_comm_system_cost(method)
            comm_system["total_cost"] += cost
        
        conn.commit()
        conn.close()
        
        # Add frequency plan
        comm_system["frequency_plan"] = {
            "emergency": "3.965 MHz (80m emergency net)",
            "regional": "146.520 MHz (2m simplex calling)",
            "local": "462.675 MHz (GMRS emergency)",
            "backup": "CB Channel 9 (27.065 MHz)",
            "international": "14.230 MHz (20m emergency)"
        }
        
        # Protection methods
        comm_system["protection_methods"] = {
            "storage": "Keep all electronic radios in Faraday cages",
            "deployment": "Only remove from protection after EMP confirmed over",
            "testing": "Test monthly without removing from protection",
            "redundancy": "Multiple identical units in separate cages",
            "documentation": "Laminated frequency guides and procedures"
        }
        
        # Operating procedures
        comm_system["operating_procedures"] = {
            "post_emp_activation": [
                "Wait 24 hours after event",
                "Test environment with sacrificial device",
                "Deploy tube/mechanical systems first",
                "Gradually activate solid-state devices",
                "Establish communication network"
            ],
            "communication_protocol": [
                "Listen before transmitting",
                "Use minimum power necessary",
                "Keep transmissions brief",
                "Use predetermined codes",
                "Maintain radio silence when not essential"
            ]
        }
        
        return comm_system
    
    def develop_emp_response_plan(self) -> Dict:
        """Create comprehensive EMP event response plan"""
        response_plan = {
            "plan_date": datetime.now().isoformat(),
            "threat_assessment": {},
            "response_phases": {},
            "resource_allocation": {},
            "personnel_assignments": {},
            "success_metrics": {}
        }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Define response phases
        phases = [
            {
                "phase": "Pre-Event Warning",
                "timeframe": "T-24 to T-0 hours",
                "actions": [
                    "Monitor space weather alerts",
                    "Disconnect sensitive electronics",
                    "Fill water containers",
                    "Charge all batteries",
                    "Fuel vehicles and generators",
                    "Alert family and neighbors",
                    "Move electronics to Faraday cages"
                ],
                "resources": ["Alert systems", "Storage containers", "Fuel"],
                "personnel": 2,
                "success": "All electronics protected, resources secured"
            },
            {
                "phase": "Impact",
                "timeframe": "T+0 to T+1 hour",
                "actions": [
                    "Verify EMP occurrence",
                    "Check vehicle functionality",
                    "Test sacrificial electronics",
                    "Assess local damage",
                    "Secure property",
                    "Gather family members"
                ],
                "resources": ["Test devices", "Security equipment"],
                "personnel": 4,
                "success": "Situation assessed, family secure"
            },
            {
                "phase": "Immediate Response",
                "timeframe": "T+1 to T+24 hours",
                "actions": [
                    "Activate manual water systems",
                    "Deploy protected communications",
                    "Establish security watch",
                    "Begin rationing protocol",
                    "Contact neighbors for mutual aid",
                    "Start manual operation procedures"
                ],
                "resources": ["Manual systems", "Protected radios", "Supplies"],
                "personnel": 4,
                "success": "Basic systems operational, communication established"
            },
            {
                "phase": "Short-term Adaptation",
                "timeframe": "T+1 to T+7 days",
                "actions": [
                    "Establish daily routines",
                    "Organize neighborhood resources",
                    "Set up communal kitchen",
                    "Create information center",
                    "Begin repairs on damaged systems",
                    "Establish trade networks"
                ],
                "resources": ["Tools", "Building materials", "Trade goods"],
                "personnel": 8,
                "success": "Community organization, resource sharing active"
            },
            {
                "phase": "Long-term Survival",
                "timeframe": "T+1 week to recovery",
                "actions": [
                    "Maintain manual operations",
                    "Develop local production",
                    "Establish governance structure",
                    "Create education system",
                    "Build resilient infrastructure",
                    "Plan for winter/summer extremes"
                ],
                "resources": ["Seeds", "Tools", "Building supplies", "Fuel"],
                "personnel": "Community-wide",
                "success": "Sustainable operations without electronics"
            }
        ]
        
        for phase in phases:
            # Store in database
            cursor.execute('''
                INSERT INTO emp_response_plan
                (phase_name, time_frame, priority_actions, resources_needed,
                 personnel_required, success_criteria)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (phase["phase"], phase["timeframe"],
                  json.dumps(phase["actions"]), json.dumps(phase["resources"]),
                  phase["personnel"], phase["success"]))
            
            response_plan["response_phases"][phase["phase"]] = {
                "timeframe": phase["timeframe"],
                "actions": len(phase["actions"]),
                "personnel": phase["personnel"],
                "success_criteria": phase["success"]
            }
        
        conn.commit()
        conn.close()
        
        # Threat assessment
        response_plan["threat_assessment"] = {
            "solar_flare_probability": "12% per decade (Carrington-level)",
            "nuclear_emp_probability": "2% annual (geopolitical dependent)",
            "warning_time": "0-18 hours depending on type",
            "impact_duration": "Months to years for full recovery",
            "geographic_scope": "Continental to hemispheric"
        }
        
        # Resource allocation
        response_plan["resource_allocation"] = {
            "protection_equipment": "30% of resources",
            "manual_alternatives": "25% of resources",
            "food_water": "20% of resources",
            "medical_supplies": "15% of resources",
            "tools_materials": "10% of resources"
        }
        
        # Personnel assignments
        response_plan["personnel_assignments"] = {
            "leader": "Coordinate response, decisions",
            "communications": "Operate protected radios",
            "security": "Property and resource protection",
            "medical": "Health and sanitation",
            "logistics": "Resource management and distribution"
        }
        
        return response_plan
    
    def run_emp_hardening_drill(self, scenario: str = "solar_flare") -> Dict:
        """Execute EMP preparedness drill with scoring"""
        drill_result = {
            "drill_date": datetime.now().isoformat(),
            "scenario": scenario,
            "phases_completed": {},
            "total_score": 0,
            "time_taken": {},
            "improvements_needed": [],
            "strengths_identified": []
        }
        
        print(f"\n⚡ EMP HARDENING DRILL: {scenario.upper()}")
        print("=" * 50)
        
        if scenario == "solar_flare":
            print("\nSCENARIO: Space Weather Alert!")
            print("Major X-class solar flare detected.")
            print("Coronal Mass Ejection heading toward Earth.")
            print("Impact expected in 18 hours.")
            print("\nYou must protect your electronics and prepare for grid failure...")
            
            # Phase 1: Protection Sprint (30 minutes)
            print("\n⏱️ PHASE 1: PROTECTION SPRINT (30 minutes)")
            print("Protect critical electronics before EMP arrival!")
            
            actions = [
                "Disconnect and unplug all electronics",
                "Place radios in Faraday cage",
                "Store backup power equipment",
                "Protect medical devices",
                "Secure vehicle in garage/cover"
            ]
            
            completed = 0
            for action in actions:
                response = input(f"Did you {action}? (y/n): ").lower()
                if response == 'y':
                    completed += 1
            
            drill_result["phases_completed"]["protection"] = (completed / len(actions)) * 100
            drill_result["total_score"] += (completed / len(actions)) * 25
            
            # Phase 2: Resource Preparation (1 hour)
            print("\n⏱️ PHASE 2: RESOURCE PREPARATION (1 hour)")
            
            actions = [
                "Fill all water containers",
                "Charge all batteries",
                "Fuel vehicles and generators",
                "Prepare manual tools",
                "Brief family on plan"
            ]
            
            completed = 0
            for action in actions:
                response = input(f"Did you {action}? (y/n): ").lower()
                if response == 'y':
                    completed += 1
            
            drill_result["phases_completed"]["resources"] = (completed / len(actions)) * 100
            drill_result["total_score"] += (completed / len(actions)) * 25
            
            # Phase 3: Manual Systems Check (30 minutes)
            print("\n⏱️ PHASE 3: MANUAL SYSTEMS CHECK")
            
            actions = [
                "Test manual water pump",
                "Verify mechanical tools work",
                "Check non-electric heating/cooling",
                "Test manual communications",
                "Confirm food preparation methods"
            ]
            
            completed = 0
            for action in actions:
                response = input(f"Can you operate: {action}? (y/n): ").lower()
                if response == 'y':
                    completed += 1
            
            drill_result["phases_completed"]["manual_systems"] = (completed / len(actions)) * 100
            drill_result["total_score"] += (completed / len(actions)) * 25
            
            # Phase 4: Recovery Planning
            print("\n⏱️ PHASE 4: RECOVERY PLANNING")
            
            actions = [
                "Know how to test for EMP end",
                "Have deployment sequence ready",
                "Understand gradual activation",
                "Community coordination plan",
                "Long-term sustainability plan"
            ]
            
            completed = 0
            for action in actions:
                response = input(f"Do you have: {action}? (y/n): ").lower()
                if response == 'y':
                    completed += 1
            
            drill_result["phases_completed"]["recovery"] = (completed / len(actions)) * 100
            drill_result["total_score"] += (completed / len(actions)) * 25
        
        # Analyze performance
        if drill_result["total_score"] >= 80:
            drill_result["performance"] = "EXCELLENT"
            drill_result["strengths_identified"].append("Well-prepared for EMP events")
        elif drill_result["total_score"] >= 60:
            drill_result["performance"] = "GOOD"
            drill_result["strengths_identified"].append("Basic EMP protection in place")
        else:
            drill_result["performance"] = "NEEDS IMPROVEMENT"
            drill_result["improvements_needed"].append("Requires significant preparation")
        
        # Specific recommendations
        for phase, score in drill_result["phases_completed"].items():
            if score < 80:
                drill_result["improvements_needed"].append(f"Improve {phase} procedures")
        
        print(f"\n📊 DRILL RESULTS")
        print(f"Total Score: {drill_result['total_score']:.1f}%")
        print(f"Performance: {drill_result['performance']}")
        
        if drill_result["improvements_needed"]:
            print(f"Areas to improve: {', '.join(drill_result['improvements_needed'])}")
        
        return drill_result
    
    # Helper methods
    def get_typical_household_items(self) -> Dict:
        """Return typical household electronic items"""
        return {
            "communications": ["Cell phones", "Tablets", "Radios", "Routers"],
            "power": ["Solar controllers", "Inverters", "Generators", "UPS"],
            "medical": ["CPAP", "Glucose meters", "Hearing aids", "Monitors"],
            "computing": ["Laptops", "Desktops", "Hard drives", "Printers"],
            "appliances": ["Refrigerator", "Microwave", "Washer", "HVAC"],
            "vehicles": ["Cars", "Motorcycles", "ATVs", "Boats"],
            "tools": ["Power tools", "Multimeters", "Chargers", "Compressors"]
        }
    
    def estimate_build_time(self, cage_type: str) -> str:
        """Estimate time to build Faraday cage"""
        times = {
            "ammo_can": "30 minutes",
            "trash_can": "1 hour",
            "cabinet": "4 hours",
            "room": "2-3 days"
        }
        return times.get(cage_type, "Unknown")
    
    def get_difficulty_level(self, cage_type: str) -> int:
        """Get difficulty level for Faraday cage construction"""
        difficulty = {
            "ammo_can": 1,
            "trash_can": 2,
            "cabinet": 3,
            "room": 5
        }
        return difficulty.get(cage_type, 3)
    
    def generate_manual_instructions(self, system: Dict) -> str:
        """Generate instructions for manual system conversion"""
        return f"""
        Converting {system['electronic']} to {system['manual']}:
        1. Acquire necessary tools: {', '.join(system['tools'])}
        2. Installation time: {system['time']}
        3. Skill level required: {system['skill']}/5
        4. Follow manual alternative procedures
        5. Practice regularly to maintain proficiency
        6. Effectiveness rating: {system['effectiveness']}/10
        """
    
    def estimate_manual_system_cost(self, system: Dict) -> float:
        """Estimate cost for manual system alternatives"""
        base_costs = {
            "GPS Navigation": 50,
            "Electric Water Pump": 300,
            "Electronic Ignition": 200,
            "Digital Thermostat": 30,
            "Electric Stove": 500,
            "Security System": 100,
            "Electronic Medical Devices": 150,
            "Power Tools": 200
        }
        return base_costs.get(system["electronic"], 100)
    
    def estimate_comm_system_cost(self, method: Dict) -> float:
        """Estimate cost for hardened communication system"""
        base_costs = {
            "Tube-based HAM Radio": 800,
            "Crystal Radio": 30,
            "Spark Gap Transmitter": 100,
            "Optical Signaling": 150,
            "Mechanical Telegraph": 200
        }
        return base_costs.get(method["method"], 100)
    
    def calculate_shielding_effectiveness(self, frequency_mhz: float, 
                                         material: str, thickness_mm: float) -> float:
        """Calculate shielding effectiveness in dB"""
        # Simplified shielding effectiveness calculation
        conductivity = {
            "copper": 5.8e7,
            "aluminum": 3.5e7,
            "steel": 1.0e7,
            "brass": 1.5e7
        }
        
        sigma = conductivity.get(material.lower(), 1e7)
        skin_depth = 503 / math.sqrt(frequency_mhz * sigma / 5.8e7)
        
        if thickness_mm > skin_depth:
            effectiveness = 20 * math.log10(thickness_mm / skin_depth) + 50
        else:
            effectiveness = 20 * math.log10(thickness_mm / skin_depth) + 10
        
        return min(effectiveness, 120)  # Cap at 120 dB
    
    def generate_comprehensive_report(self) -> Dict:
        """Generate complete EMP hardening report"""
        report = {
            "report_date": datetime.now().isoformat(),
            "module_version": "2.0.0",
            "sections": {}
        }
        
        # Vulnerability Assessment
        report["sections"]["vulnerability"] = self.assess_emp_vulnerability()
        
        # Faraday Cage Design
        report["sections"]["faraday_protection"] = self.design_faraday_cage("medium", 100)
        
        # Manual Systems Plan
        report["sections"]["manual_systems"] = self.create_manual_systems_plan()
        
        # Grid-Independent Utilities
        report["sections"]["independent_utilities"] = self.setup_grid_independent_utilities()
        
        # Hardened Communications
        report["sections"]["communications"] = self.create_hardened_communications()
        
        # Response Plan
        report["sections"]["response_plan"] = self.develop_emp_response_plan()
        
        # Overall preparedness
        vulnerability = report["sections"]["vulnerability"]["vulnerability_score"]
        report["emp_preparedness_score"] = 100 - vulnerability
        report["preparedness_level"] = self.get_preparedness_level(report["emp_preparedness_score"])
        
        return report
    
    def get_preparedness_level(self, score: float) -> str:
        """Determine EMP preparedness level"""
        if score >= 80:
            return "EXCELLENT - Well hardened against EMP"
        elif score >= 60:
            return "GOOD - Basic EMP protection in place"
        elif score >= 40:
            return "MODERATE - Some protection but vulnerabilities remain"
        elif score >= 20:
            return "POOR - Highly vulnerable to EMP"
        else:
            return "CRITICAL - No EMP protection"


def main():
    """Test the EMP Hardening Module"""
    print("⚡ EMP/SOLAR FLARE HARDENING MODULE v2.0")
    print("=" * 50)
    
    # Initialize module
    emp_module = EMPHardeningModule()
    
    # Assess vulnerability
    print("\n📊 Assessing EMP Vulnerability...")
    assessment = emp_module.assess_emp_vulnerability()
    print(f"Vulnerability Score: {assessment['vulnerability_score']}%")
    print(f"Protection Level: {assessment['protection_level']}")
    print(f"Protected Items: {assessment['protected_items']}")
    print(f"Vulnerable Items: {assessment['vulnerable_items']}")
    
    # Design Faraday cage
    print("\n🛡️ Designing Faraday Cage...")
    cage_design = emp_module.design_faraday_cage("medium", 100)
    print(f"Recommended Design: {cage_design['size_category']} cage")
    print(f"Total Cost: ${cage_design['total_cost']}")
    print(f"Effectiveness: {cage_design['effectiveness_rating']} dB")
    
    # Create manual systems plan
    print("\n🔧 Planning Manual Systems...")
    manual_plan = emp_module.create_manual_systems_plan()
    print(f"Manual Systems: {len(manual_plan['manual_systems'])}")
    print(f"Total Cost Estimate: ${manual_plan['total_cost_estimate']}")
    
    # Setup grid-independent utilities
    print("\n🏠 Designing Grid-Independent Utilities...")
    utilities = emp_module.setup_grid_independent_utilities("power")
    print(f"Utility Systems: {len(utilities['systems'])}")
    print(f"Total Cost: ${utilities['total_cost']}")
    
    # Create hardened communications
    print("\n📡 Setting Up Hardened Communications...")
    comms = emp_module.create_hardened_communications()
    print(f"Communication Methods: {len(comms['primary_systems'])}")
    print(f"Total Cost: ${comms['total_cost']}")
    
    # Develop response plan
    print("\n📋 Developing EMP Response Plan...")
    response = emp_module.develop_emp_response_plan()
    print(f"Response Phases: {len(response['response_phases'])}")
    
    print("\n✅ EMP Hardening Module initialized successfully!")
    print("Ready to improve EMP preparedness from 41.0% to 60%+")


if __name__ == "__main__":
    main()