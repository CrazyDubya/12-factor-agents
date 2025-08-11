#!/usr/bin/env python3
"""
Nuclear/Radiation Safety Module - Version 2.0
Comprehensive nuclear accident response and radiation protection

Target: Improve nuclear accident preparedness from 40.7% to 65%+
"""

import sqlite3
import json
import math
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import random

class NuclearSafetyModule:
    def __init__(self, db_path: str = "modern_threats.db"):
        """Initialize Nuclear Safety Module with comprehensive radiation protection"""
        self.db_path = db_path
        self.init_database()
        self.load_nuclear_threats()
        self.initialize_protection_systems()
    
    def init_database(self):
        """Initialize database for nuclear safety data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Radiation detection equipment
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS radiation_detection (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_name TEXT NOT NULL,
                detection_type TEXT,
                sensitivity TEXT,
                cost_range TEXT,
                battery_life TEXT,
                calibration_needed BOOLEAN,
                units_measured TEXT,
                recommended_for TEXT,
                notes TEXT
            )
        ''')
        
        # Decontamination procedures
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS decontamination_procedures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contamination_type TEXT NOT NULL,
                procedure_name TEXT,
                priority_level INTEGER,
                time_required TEXT,
                supplies_needed TEXT,
                effectiveness_percent INTEGER,
                precautions TEXT,
                instructions TEXT
            )
        ''')
        
        # Evacuation planning
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS evacuation_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scenario_type TEXT NOT NULL,
                distance_miles REAL,
                evacuation_time TEXT,
                transportation_method TEXT,
                destination_type TEXT,
                route_planning TEXT,
                shelter_duration TEXT,
                supplies_needed TEXT
            )
        ''')
        
        # Medical response protocols
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS medical_protocols (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exposure_level TEXT NOT NULL,
                symptoms TEXT,
                immediate_treatment TEXT,
                medications_needed TEXT,
                medical_facility_type TEXT,
                prognosis TEXT,
                long_term_care TEXT
            )
        ''')
        
        # Shelter and protection
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS radiation_shelters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                shelter_type TEXT NOT NULL,
                protection_factor INTEGER,
                construction_materials TEXT,
                build_time TEXT,
                cost_estimate REAL,
                capacity_people INTEGER,
                ventilation_needed BOOLEAN,
                instructions TEXT
            )
        ''')
        
        # Nuclear incident tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS nuclear_incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_type TEXT NOT NULL,
                severity_level INTEGER,
                detection_time TIMESTAMP,
                evacuation_zone_miles REAL,
                wind_direction TEXT,
                estimated_duration TEXT,
                response_actions TEXT,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def load_nuclear_threats(self):
        """Load nuclear threat scenarios and radiation data"""
        self.nuclear_threats = {
            "power_plant_accident": {
                "probability": 0.001,  # Per plant per year
                "warning_time": 2,  # Hours typical
                "evacuation_zones": {
                    "immediate": 2,  # miles
                    "precautionary": 10,
                    "ingestion": 50
                },
                "duration": "Weeks to years",
                "radiation_types": ["Gamma", "Beta", "Alpha", "Neutron"],
                "health_effects": {
                    "acute": "Radiation sickness, burns",
                    "chronic": "Cancer, genetic damage",
                    "psychological": "Stress, anxiety"
                }
            },
            "nuclear_terrorism": {
                "probability": 0.005,  # Annual urban areas
                "warning_time": 0,
                "evacuation_zones": {
                    "immediate": 0.5,
                    "precautionary": 3,
                    "ingestion": 20
                },
                "duration": "Days to months",
                "radiation_types": ["Gamma", "Alpha", "Beta"],
                "health_effects": {
                    "acute": "Localized radiation exposure",
                    "chronic": "Increased cancer risk",
                    "psychological": "Mass panic, displacement"
                }
            },
            "nuclear_weapon": {
                "probability": 0.001,  # Annual geopolitical
                "warning_time": 15,  # Minutes if detected
                "evacuation_zones": {
                    "immediate": 1,
                    "precautionary": 5,
                    "fallout": 100
                },
                "duration": "Minutes blast, years fallout",
                "radiation_types": ["Gamma", "Neutron", "Fallout"],
                "health_effects": {
                    "acute": "Severe radiation syndrome",
                    "chronic": "Lifelong health impacts",
                    "psychological": "PTSD, survivor syndrome"
                }
            },
            "transportation_accident": {
                "probability": 0.01,  # Annual transportation
                "warning_time": 1,
                "evacuation_zones": {
                    "immediate": 0.3,
                    "precautionary": 1,
                    "ingestion": 5
                },
                "duration": "Hours to days",
                "radiation_types": ["Varies by material"],
                "health_effects": {
                    "acute": "Localized exposure",
                    "chronic": "Minimal if proper response",
                    "psychological": "Community concern"
                }
            }
        }
        
        # Radiation protection factors
        self.protection_factors = {
            "open_area": 1,
            "vehicle": 2,
            "wood_frame_house": 4,
            "basement": 10,
            "brick_building": 15,
            "large_office_building": 20,
            "underground_shelter": 100,
            "purpose_built_fallout": 1000
        }
        
        # Radiation exposure limits (mSv)
        self.exposure_limits = {
            "public_annual": 1,
            "worker_annual": 20,
            "emergency_worker": 100,
            "life_saving": 500,
            "acute_mild": 250,
            "acute_severe": 1000,
            "acute_lethal": 4000
        }
    
    def initialize_protection_systems(self):
        """Initialize radiation protection and detection systems"""
        self.protection_systems = {
            "detection_equipment": {
                "survey_meter": {
                    "type": "Geiger counter",
                    "cost": "$200-800",
                    "sensitivity": "Good for gamma/beta",
                    "units": "mR/hr, CPM",
                    "battery": "AA batteries, 200+ hours"
                },
                "dosimeter": {
                    "type": "Personal radiation badge",
                    "cost": "$50-150",
                    "sensitivity": "Cumulative exposure",
                    "units": "mSv total",
                    "battery": "None needed"
                },
                "spectrometer": {
                    "type": "Isotope identifier",
                    "cost": "$2000-5000",
                    "sensitivity": "Identifies specific isotopes",
                    "units": "Energy spectrum",
                    "battery": "Rechargeable, 8+ hours"
                }
            },
            "decontamination_supplies": {
                "personal": [
                    "Potassium iodide (KI) tablets",
                    "Soap and water",
                    "Disposable coveralls",
                    "Nitrile gloves",
                    "N95 respirators",
                    "Plastic bags for contaminated items"
                ],
                "equipment": [
                    "Garden sprayer",
                    "Scrub brushes",
                    "Detergent",
                    "Plastic sheeting",
                    "Duct tape",
                    "Contamination bags"
                ]
            },
            "shelter_materials": {
                "basic_shelter": [
                    "Concrete blocks",
                    "Sand bags",
                    "Steel sheeting",
                    "Plastic sheeting",
                    "Ventilation filter"
                ],
                "advanced_shelter": [
                    "Lead sheets",
                    "Concrete pour",
                    "HEPA filtration",
                    "Air monitoring",
                    "Waste containment"
                ]
            }
        }
    
    def assess_nuclear_preparedness(self, distance_to_plant: float = 20) -> Dict:
        """Assess nuclear accident preparedness based on proximity and preparations"""
        assessment = {
            "assessment_date": datetime.now().isoformat(),
            "plant_distance": distance_to_plant,
            "risk_level": "",
            "preparedness_score": 0,
            "detection_capability": 0,
            "decontamination_readiness": 0,
            "evacuation_preparedness": 0,
            "medical_readiness": 0,
            "shelter_capability": 0,
            "critical_gaps": [],
            "recommendations": []
        }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Determine risk level based on distance
        if distance_to_plant <= 10:
            assessment["risk_level"] = "HIGH - Emergency Planning Zone"
            risk_multiplier = 3
        elif distance_to_plant <= 50:
            assessment["risk_level"] = "MODERATE - Ingestion Planning Zone"
            risk_multiplier = 2
        else:
            assessment["risk_level"] = "LOW - Outside primary zones"
            risk_multiplier = 1
        
        # Check detection equipment
        cursor.execute("SELECT COUNT(*) FROM radiation_detection")
        detection_count = cursor.fetchone()[0]
        
        if detection_count >= 2:
            assessment["detection_capability"] = 85
            assessment["preparedness_score"] += 17 * risk_multiplier
        elif detection_count == 1:
            assessment["detection_capability"] = 60
            assessment["preparedness_score"] += 12 * risk_multiplier
            assessment["critical_gaps"].append("Need backup radiation detector")
        else:
            assessment["detection_capability"] = 20
            assessment["critical_gaps"].append("No radiation detection equipment")
        
        # Check decontamination procedures
        cursor.execute("SELECT COUNT(*) FROM decontamination_procedures")
        decon_procedures = cursor.fetchone()[0]
        
        if decon_procedures >= 5:
            assessment["decontamination_readiness"] = 80
            assessment["preparedness_score"] += 16 * risk_multiplier
        elif decon_procedures >= 2:
            assessment["decontamination_readiness"] = 50
            assessment["preparedness_score"] += 10 * risk_multiplier
        else:
            assessment["decontamination_readiness"] = 20
            assessment["critical_gaps"].append("Limited decontamination procedures")
        
        # Check evacuation planning
        cursor.execute("SELECT COUNT(*) FROM evacuation_plans WHERE distance_miles >= ?", (distance_to_plant,))
        evacuation_plans = cursor.fetchone()[0]
        
        if evacuation_plans >= 3:
            assessment["evacuation_preparedness"] = 85
            assessment["preparedness_score"] += 17 * risk_multiplier
        elif evacuation_plans >= 1:
            assessment["evacuation_preparedness"] = 60
            assessment["preparedness_score"] += 12 * risk_multiplier
        else:
            assessment["evacuation_preparedness"] = 25
            assessment["critical_gaps"].append("No specific evacuation plans")
        
        # Check medical protocols
        cursor.execute("SELECT COUNT(*) FROM medical_protocols")
        medical_protocols = cursor.fetchone()[0]
        
        if medical_protocols >= 4:
            assessment["medical_readiness"] = 75
            assessment["preparedness_score"] += 15 * risk_multiplier
        elif medical_protocols >= 2:
            assessment["medical_readiness"] = 45
            assessment["preparedness_score"] += 9 * risk_multiplier
        else:
            assessment["medical_readiness"] = 20
            assessment["critical_gaps"].append("Limited medical response protocols")
        
        # Check shelter capability
        cursor.execute("SELECT COUNT(*) FROM radiation_shelters WHERE protection_factor >= 10")
        adequate_shelters = cursor.fetchone()[0]
        
        if adequate_shelters >= 1:
            assessment["shelter_capability"] = 70
            assessment["preparedness_score"] += 14 * risk_multiplier
        else:
            assessment["shelter_capability"] = 30
            assessment["critical_gaps"].append("No adequate radiation shelter")
        
        conn.close()
        
        # Cap score at 100
        assessment["preparedness_score"] = min(100, assessment["preparedness_score"])
        
        # Generate recommendations
        if assessment["preparedness_score"] < 40:
            assessment["recommendations"] = [
                "URGENT: Acquire radiation detection equipment",
                "Develop evacuation routes and plans",
                "Stock potassium iodide tablets",
                "Identify or build radiation shelter"
            ]
        elif assessment["preparedness_score"] < 70:
            assessment["recommendations"] = [
                "Enhance decontamination procedures",
                "Improve shelter protection factor",
                "Practice evacuation drills",
                "Expand medical supplies"
            ]
        else:
            assessment["recommendations"] = [
                "Maintain current preparations",
                "Regular equipment testing",
                "Update plans annually",
                "Consider community coordination"
            ]
        
        return assessment
    
    def recommend_detection_equipment(self, budget: float = 500, risk_level: str = "moderate") -> Dict:
        """Recommend radiation detection equipment based on budget and risk"""
        recommendations = {
            "recommendation_date": datetime.now().isoformat(),
            "budget": budget,
            "risk_level": risk_level,
            "primary_device": {},
            "secondary_device": {},
            "accessories": [],
            "total_cost": 0,
            "detection_coverage": []
        }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Define equipment options
        equipment_options = [
            {
                "name": "RadAlert 100",
                "type": "Basic Geiger Counter",
                "cost": 150,
                "sensitivity": "High",
                "detection": "Gamma, X-ray",
                "battery": "9V, 2000+ hours",
                "calibrated": False,
                "recommended_for": "Basic monitoring"
            },
            {
                "name": "Inspector Alert",
                "type": "Alpha/Beta/Gamma Detector",
                "cost": 600,
                "sensitivity": "Very High",
                "detection": "Alpha, Beta, Gamma, X-ray",
                "battery": "AA, 2000+ hours",
                "calibrated": True,
                "recommended_for": "Comprehensive detection"
            },
            {
                "name": "Digilert 100",
                "type": "Digital Survey Meter", 
                "cost": 350,
                "sensitivity": "High",
                "detection": "Gamma, X-ray",
                "battery": "AA, 1000+ hours",
                "calibrated": True,
                "recommended_for": "Accurate measurement"
            },
            {
                "name": "Personal Dosimeter",
                "type": "Cumulative Dose Monitor",
                "cost": 75,
                "sensitivity": "Medium",
                "detection": "Gamma accumulation",
                "battery": "None",
                "calibrated": False,
                "recommended_for": "Personal protection"
            },
            {
                "name": "Digital Dosimeter",
                "type": "Electronic Personal Monitor",
                "cost": 400,
                "sensitivity": "High",
                "detection": "Real-time dose rate",
                "battery": "Rechargeable",
                "calibrated": True,
                "recommended_for": "Professional use"
            }
        ]
        
        # Select primary device based on budget and risk
        if risk_level == "high" and budget >= 600:
            primary = next(d for d in equipment_options if d["name"] == "Inspector Alert")
        elif budget >= 350:
            primary = next(d for d in equipment_options if d["name"] == "Digilert 100")
        else:
            primary = next(d for d in equipment_options if d["name"] == "RadAlert 100")
        
        recommendations["primary_device"] = primary
        recommendations["total_cost"] += primary["cost"]
        
        # Add secondary device if budget allows
        remaining_budget = budget - primary["cost"]
        if remaining_budget >= 75:
            if primary["name"] != "Personal Dosimeter":
                secondary = next(d for d in equipment_options if d["name"] == "Personal Dosimeter")
                recommendations["secondary_device"] = secondary
                recommendations["total_cost"] += secondary["cost"]
        
        # Store recommendations in database
        for device in [recommendations["primary_device"], recommendations["secondary_device"]]:
            if device:
                cursor.execute('''
                    INSERT INTO radiation_detection
                    (device_name, detection_type, sensitivity, cost_range,
                     battery_life, calibration_needed, units_measured, recommended_for)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (device["name"], device["type"], device["sensitivity"],
                      f"${device['cost']}", device["battery"], device["calibrated"],
                      device["detection"], device["recommended_for"]))
        
        # Add accessories
        remaining_budget = budget - recommendations["total_cost"]
        accessories = [
            {"item": "Carrying case", "cost": 30},
            {"item": "Spare batteries", "cost": 20},
            {"item": "Calibration check source", "cost": 50},
            {"item": "Detection log book", "cost": 15}
        ]
        
        for accessory in accessories:
            if remaining_budget >= accessory["cost"]:
                recommendations["accessories"].append(accessory)
                recommendations["total_cost"] += accessory["cost"]
                remaining_budget -= accessory["cost"]
        
        conn.commit()
        conn.close()
        
        # Detection coverage
        recommendations["detection_coverage"] = [
            f"Gamma radiation: {primary['detection']}",
            "Background monitoring capability",
            "Contamination detection",
            "Personal exposure tracking" if recommendations["secondary_device"] else "Area monitoring only"
        ]
        
        # Usage instructions
        recommendations["usage_instructions"] = [
            "Take background readings in clean areas",
            "Monitor at chest height for personal exposure",
            "Check for contamination 1 inch from surfaces",
            "Log all readings with date/time/location",
            "Replace batteries before long-term storage"
        ]
        
        return recommendations
    
    def create_decontamination_protocol(self, contamination_type: str = "general") -> Dict:
        """Create comprehensive decontamination protocol"""
        protocol = {
            "protocol_date": datetime.now().isoformat(),
            "contamination_type": contamination_type,
            "procedures": {},
            "supplies_needed": [],
            "time_estimates": {},
            "effectiveness_rates": {},
            "safety_precautions": []
        }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Define decontamination procedures
        procedures = [
            {
                "type": "Personal Decontamination",
                "priority": 1,
                "time": "15-30 minutes",
                "supplies": [
                    "Soap and warm water",
                    "Disposable towels",
                    "Clean clothing",
                    "Plastic bags",
                    "Radiation detector"
                ],
                "effectiveness": 95,
                "precautions": "Remove contaminated clothing carefully",
                "steps": [
                    "Remove outer clothing and shoes",
                    "Place in sealed plastic bags",
                    "Shower with soap and warm water",
                    "Wash hair thoroughly",
                    "Monitor with radiation detector",
                    "Repeat if contamination remains"
                ]
            },
            {
                "type": "Clothing Decontamination", 
                "priority": 2,
                "time": "2-4 hours",
                "supplies": [
                    "Detergent",
                    "Washing machine",
                    "Hot water",
                    "Rubber gloves",
                    "Disposal bags"
                ],
                "effectiveness": 85,
                "precautions": "Wash contaminated items separately",
                "steps": [
                    "Sort by contamination level",
                    "Pre-treat heavily contaminated areas",
                    "Wash in hot water with detergent",
                    "Run through multiple cycles",
                    "Monitor before and after washing",
                    "Dispose if decontamination fails"
                ]
            },
            {
                "type": "Vehicle Decontamination",
                "priority": 3,
                "time": "1-3 hours",
                "supplies": [
                    "Garden hose",
                    "Car soap",
                    "Sponges/brushes",
                    "Pressure washer",
                    "Protective equipment"
                ],
                "effectiveness": 80,
                "precautions": "Start from top, work downward",
                "steps": [
                    "Remove floor mats and seat covers",
                    "Rinse entire vehicle thoroughly",
                    "Scrub with soap and water",
                    "Pay attention to wheel wells",
                    "Monitor contamination levels",
                    "Repeat cleaning as needed"
                ]
            },
            {
                "type": "Home Decontamination",
                "priority": 4,
                "time": "4-8 hours",
                "supplies": [
                    "HEPA vacuum",
                    "Cleaning solutions",
                    "Mops and buckets",
                    "Plastic sheeting",
                    "Disposal containers"
                ],
                "effectiveness": 75,
                "precautions": "Work from clean to contaminated areas",
                "steps": [
                    "Seal HVAC system",
                    "Remove contaminated items",
                    "HEPA vacuum all surfaces",
                    "Wet clean with detergent",
                    "Monitor contamination levels",
                    "Seal and dispose waste properly"
                ]
            },
            {
                "type": "Food Decontamination",
                "priority": 2,
                "time": "30 minutes",
                "supplies": [
                    "Clean water",
                    "Produce wash",
                    "Paper towels",
                    "Clean containers",
                    "Radiation detector"
                ],
                "effectiveness": 90,
                "precautions": "Cannot decontaminate internally contaminated food",
                "steps": [
                    "Remove outer packaging",
                    "Wash fruits and vegetables",
                    "Peel when possible",
                    "Monitor contamination levels",
                    "Discard if heavily contaminated",
                    "Cook thoroughly if safe to consume"
                ]
            }
        ]
        
        for procedure in procedures:
            # Store in database
            cursor.execute('''
                INSERT INTO decontamination_procedures
                (contamination_type, procedure_name, priority_level, time_required,
                 supplies_needed, effectiveness_percent, precautions, instructions)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (contamination_type, procedure["type"], procedure["priority"],
                  procedure["time"], json.dumps(procedure["supplies"]),
                  procedure["effectiveness"], procedure["precautions"],
                  json.dumps(procedure["steps"])))
            
            protocol["procedures"][procedure["type"]] = {
                "priority": procedure["priority"],
                "time_required": procedure["time"],
                "effectiveness": f"{procedure['effectiveness']}%"
            }
            
            protocol["supplies_needed"].extend(procedure["supplies"])
            protocol["time_estimates"][procedure["type"]] = procedure["time"]
            protocol["effectiveness_rates"][procedure["type"]] = procedure["effectiveness"]
        
        conn.commit()
        conn.close()
        
        # Remove duplicate supplies
        protocol["supplies_needed"] = list(set(protocol["supplies_needed"]))
        
        # General safety precautions
        protocol["safety_precautions"] = [
            "Wear protective equipment during decontamination",
            "Monitor radiation levels throughout process",
            "Work from least to most contaminated areas",
            "Dispose of contaminated materials properly",
            "Keep contaminated and clean areas separate",
            "Document all decontamination efforts"
        ]
        
        # Disposal guidelines
        protocol["disposal_guidelines"] = {
            "low_level": "Double bag and label, follow local guidelines",
            "moderate_level": "Contact local emergency management",
            "high_level": "Professional disposal required",
            "liquids": "Absorb and treat as solid waste",
            "electronics": "Professional assessment required"
        }
        
        return protocol
    
    def plan_evacuation_routes(self, home_address: str = "Unknown", 
                              nuclear_facility_distance: float = 20) -> Dict:
        """Plan comprehensive evacuation routes for nuclear emergency"""
        evacuation = {
            "plan_date": datetime.now().isoformat(),
            "home_location": home_address,
            "facility_distance": nuclear_facility_distance,
            "evacuation_zones": {},
            "routes": {},
            "destinations": {},
            "timing": {},
            "supplies_needed": []
        }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Define evacuation zones
        zones = [
            {
                "zone": "Immediate Evacuation",
                "distance": 2,
                "time_limit": "30 minutes",
                "transport": "Personal vehicle or emergency transport",
                "destination": "Reception center 20+ miles away",
                "shelter_duration": "Days to weeks"
            },
            {
                "zone": "Precautionary Evacuation", 
                "distance": 10,
                "time_limit": "2 hours",
                "transport": "Personal vehicle",
                "destination": "Friends/family 50+ miles away",
                "shelter_duration": "Weeks to months"
            },
            {
                "zone": "Sheltering in Place",
                "distance": 20,
                "time_limit": "12-24 hours decision",
                "transport": "May shelter in place initially",
                "destination": "Home shelter or evacuation if ordered",
                "shelter_duration": "Hours to days"
            },
            {
                "zone": "Monitoring Zone",
                "distance": 50,
                "time_limit": "Monitor situation",
                "transport": "Normal transportation",
                "destination": "Home with monitoring",
                "shelter_duration": "Normal living with precautions"
            }
        ]
        
        # Determine applicable zone
        applicable_zone = None
        for zone in zones:
            if nuclear_facility_distance <= zone["distance"]:
                applicable_zone = zone
                break
        
        if not applicable_zone:
            applicable_zone = zones[-1]  # Monitoring zone
        
        # Store evacuation plans
        for zone in zones:
            cursor.execute('''
                INSERT INTO evacuation_plans
                (scenario_type, distance_miles, evacuation_time, transportation_method,
                 destination_type, shelter_duration, supplies_needed)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', ("nuclear_emergency", zone["distance"], zone["time_limit"],
                  zone["transport"], zone["destination"], zone["shelter_duration"],
                  json.dumps(self.get_evacuation_supplies(zone["shelter_duration"]))))
        
        conn.commit()
        conn.close()
        
        # Plan primary and alternate routes
        evacuation["routes"] = {
            "primary": {
                "direction": "Upwind/crosswind from facility",
                "highways": "Major highways away from facility",
                "distance": f"{nuclear_facility_distance + 50} miles minimum",
                "estimated_time": f"{applicable_zone['time_limit']} available",
                "traffic_considerations": "Heavy congestion expected"
            },
            "alternate": {
                "direction": "Secondary roads if highways blocked",
                "highways": "Back roads and local routes",
                "distance": "Same destination via different route",
                "estimated_time": "50-100% longer than primary",
                "traffic_considerations": "May be less congested"
            },
            "emergency": {
                "direction": "Any direction away from facility",
                "highways": "Any available transportation",
                "distance": "Maximum distance possible",
                "estimated_time": "Immediate departure",
                "traffic_considerations": "Extreme congestion likely"
            }
        }
        
        # Destination planning
        evacuation["destinations"] = {
            "primary": {
                "type": "Friends/family home",
                "distance": f"{nuclear_facility_distance + 75} miles",
                "accommodations": "Private residence",
                "duration": "Extended stay possible",
                "contact_info": "Pre-arranged contact"
            },
            "secondary": {
                "type": "Commercial lodging",
                "distance": f"{nuclear_facility_distance + 50} miles", 
                "accommodations": "Hotel/motel",
                "duration": "Short to medium term",
                "contact_info": "Multiple backup options"
            },
            "emergency": {
                "type": "Public shelter",
                "distance": f"{nuclear_facility_distance + 30} miles",
                "accommodations": "Red Cross or government shelter",
                "duration": "Temporary",
                "contact_info": "Emergency management"
            }
        }
        
        # Timing considerations
        evacuation["timing"] = {
            "immediate_departure": "If ordered to evacuate immediately",
            "planned_departure": "If given advance warning",
            "shelter_first": "If told to shelter then evacuate",
            "traffic_windows": "Early morning or late night least congested"
        }
        
        # Essential supplies
        evacuation["supplies_needed"] = [
            # Personal items
            "Important documents in waterproof container",
            "3 days clothing per person",
            "Medications for 2+ weeks",
            "Cash and credit cards",
            "Personal hygiene items",
            # Emergency supplies
            "Battery powered radio",
            "Flashlights and batteries",
            "First aid kit",
            "Food and water for 3 days",
            "Cell phone chargers",
            # Radiation specific
            "Potassium iodide tablets",
            "Radiation detector if available",
            "Plastic bags for contaminated items",
            "Masking tape and plastic sheeting"
        ]
        
        # Special considerations
        evacuation["special_considerations"] = {
            "pets": "Pet carriers, food, medications, records",
            "elderly": "Medical equipment, extra medications, assistance",
            "children": "Comfort items, games, formula/diapers",
            "vehicles": "Full gas tank, emergency kit, maps",
            "weather": "Seasonal clothing, weather protection"
        }
        
        return evacuation
    
    def develop_medical_protocols(self, exposure_scenario: str = "general") -> Dict:
        """Develop medical response protocols for radiation exposure"""
        protocols = {
            "protocol_date": datetime.now().isoformat(),
            "exposure_scenario": exposure_scenario,
            "exposure_levels": {},
            "treatment_protocols": {},
            "medications_needed": [],
            "medical_facilities": {},
            "triage_guidelines": {}
        }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Define exposure levels and treatments
        exposure_levels = [
            {
                "level": "Minimal Exposure",
                "dose_range": "0-250 mSv",
                "symptoms": "No immediate symptoms",
                "immediate_treatment": "Monitor, potassium iodide if indicated",
                "medications": ["Potassium iodide (if thyroid exposure)"],
                "facility_type": "Outpatient clinic or home monitoring",
                "prognosis": "Excellent, minimal long-term risk",
                "long_term": "Annual cancer screening"
            },
            {
                "level": "Mild Exposure",
                "dose_range": "250-1000 mSv", 
                "symptoms": "Fatigue, nausea, possible skin irritation",
                "immediate_treatment": "Supportive care, decontamination",
                "medications": ["Anti-nausea medication", "Potassium iodide"],
                "facility_type": "Hospital outpatient or short admission",
                "prognosis": "Good with treatment",
                "long_term": "Regular medical monitoring"
            },
            {
                "level": "Moderate Exposure",
                "dose_range": "1-4 Sv",
                "symptoms": "Nausea, vomiting, fatigue, possible hair loss",
                "immediate_treatment": "Hospitalization, supportive care",
                "medications": ["Anti-emetics", "Antibiotics", "Growth factors"],
                "facility_type": "Hospital with radiation medicine capability",
                "prognosis": "Fair to good with prompt treatment",
                "long_term": "Lifelong medical monitoring"
            },
            {
                "level": "Severe Exposure",
                "dose_range": "4-8 Sv",
                "symptoms": "Severe nausea, vomiting, diarrhea, weakness",
                "immediate_treatment": "Intensive hospital care",
                "medications": ["Multiple support medications", "Blood products"],
                "facility_type": "Major medical center with radiation specialists",
                "prognosis": "Guarded, requires intensive treatment",
                "long_term": "Significant long-term health effects likely"
            },
            {
                "level": "Critical Exposure",
                "dose_range": ">8 Sv",
                "symptoms": "Severe illness, bleeding, infection, organ failure",
                "immediate_treatment": "Emergency intensive care",
                "medications": ["Full supportive care", "Experimental treatments"],
                "facility_type": "Tertiary care center with radiation medicine",
                "prognosis": "Poor without aggressive treatment",
                "long_term": "Survivors have significant long-term effects"
            }
        ]
        
        for level in exposure_levels:
            # Store in database
            cursor.execute('''
                INSERT INTO medical_protocols
                (exposure_level, symptoms, immediate_treatment, medications_needed,
                 medical_facility_type, prognosis, long_term_care)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (level["level"], level["symptoms"], level["immediate_treatment"],
                  json.dumps(level["medications"]), level["facility_type"],
                  level["prognosis"], level["long_term"]))
            
            protocols["exposure_levels"][level["level"]] = {
                "dose_range": level["dose_range"],
                "symptoms": level["symptoms"],
                "prognosis": level["prognosis"]
            }
            
            protocols["treatment_protocols"][level["level"]] = {
                "immediate": level["immediate_treatment"],
                "facility": level["facility_type"],
                "medications": level["medications"]
            }
            
            protocols["medications_needed"].extend(level["medications"])
        
        conn.commit()
        conn.close()
        
        # Remove duplicate medications
        protocols["medications_needed"] = list(set(protocols["medications_needed"]))
        
        # Medical facility hierarchy
        protocols["medical_facilities"] = {
            "level_1": {
                "type": "Local hospital emergency room",
                "capabilities": "Basic supportive care, decontamination",
                "radiation_expertise": "Limited",
                "equipment": "Standard emergency equipment"
            },
            "level_2": {
                "type": "Regional medical center", 
                "capabilities": "Intermediate radiation medicine",
                "radiation_expertise": "Some specialized staff",
                "equipment": "Basic radiation detection, isolation rooms"
            },
            "level_3": {
                "type": "Major academic medical center",
                "capabilities": "Advanced radiation medicine",
                "radiation_expertise": "Radiation medicine specialists",
                "equipment": "Advanced monitoring, treatment protocols"
            },
            "level_4": {
                "type": "National radiation emergency center",
                "capabilities": "Cutting-edge radiation treatment",
                "radiation_expertise": "World-class specialists",
                "equipment": "Experimental treatments, research protocols"
            }
        }
        
        # Triage guidelines
        protocols["triage_guidelines"] = {
            "immediate": "Life-threatening symptoms requiring immediate care",
            "urgent": "Serious symptoms requiring care within hours",
            "delayed": "Symptoms requiring care within days",
            "minimal": "Minor symptoms, outpatient follow-up",
            "expectant": "Severe exposure with poor prognosis"
        }
        
        # Self-care guidelines
        protocols["self_care_guidelines"] = [
            "Monitor for symptoms of radiation sickness",
            "Take potassium iodide only if recommended by authorities",
            "Seek medical attention for persistent nausea/vomiting",
            "Follow decontamination procedures if exposed",
            "Document exposure circumstances and symptoms",
            "Follow all public health recommendations"
        ]
        
        # Emergency medication kit
        protocols["emergency_kit_medications"] = [
            "Potassium iodide tablets (adult and pediatric)",
            "Anti-nausea medication (ondansetron)",
            "Pain relievers (acetaminophen, ibuprofen)",
            "Anti-diarrheal medication",
            "Antihistamines for allergic reactions",
            "Prescription medications (2+ week supply)"
        ]
        
        return protocols
    
    def design_radiation_shelter(self, shelter_type: str = "basement", 
                                budget: float = 1000) -> Dict:
        """Design radiation shelter based on existing space and budget"""
        shelter_design = {
            "design_date": datetime.now().isoformat(),
            "shelter_type": shelter_type,
            "budget": budget,
            "protection_factor": 0,
            "materials_needed": [],
            "construction_steps": [],
            "total_cost": 0,
            "capacity": 0,
            "duration": ""
        }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Define shelter designs
        shelter_designs = {
            "basement": {
                "base_pf": 10,
                "improvements": [
                    {"item": "Sand-filled blocks above windows", "pf_increase": 5, "cost": 200},
                    {"item": "Concrete blocks on exposed walls", "pf_increase": 10, "cost": 400},
                    {"item": "Overhead concrete slab", "pf_increase": 15, "cost": 600},
                    {"item": "Interior room creation", "pf_increase": 5, "cost": 300}
                ]
            },
            "above_ground": {
                "base_pf": 4,
                "improvements": [
                    {"item": "Interior room with thick walls", "pf_increase": 6, "cost": 500},
                    {"item": "Concrete block walls", "pf_increase": 10, "cost": 800},
                    {"item": "Earth berming around structure", "pf_increase": 8, "cost": 400},
                    {"item": "Thick concrete roof", "pf_increase": 12, "cost": 1000}
                ]
            },
            "purpose_built": {
                "base_pf": 100,
                "improvements": [
                    {"item": "HEPA filtration system", "pf_increase": 50, "cost": 2000},
                    {"item": "Lead-lined walls", "pf_increase": 100, "cost": 3000},
                    {"item": "Blast-resistant construction", "pf_increase": 200, "cost": 10000},
                    {"item": "Independent life support", "pf_increase": 50, "cost": 5000}
                ]
            }
        }
        
        if shelter_type not in shelter_designs:
            shelter_type = "basement"
        
        design = shelter_designs[shelter_type]
        shelter_design["protection_factor"] = design["base_pf"]
        
        # Select improvements within budget
        remaining_budget = budget
        for improvement in design["improvements"]:
            if remaining_budget >= improvement["cost"]:
                shelter_design["materials_needed"].append(improvement["item"])
                shelter_design["protection_factor"] += improvement["pf_increase"]
                shelter_design["total_cost"] += improvement["cost"]
                remaining_budget -= improvement["cost"]
        
        # Generate construction steps
        if shelter_type == "basement":
            shelter_design["construction_steps"] = [
                "Clear and clean basement area",
                "Identify interior corner or room",
                "Install sand-filled blocks above ground-level windows",
                "Add concrete blocks to exposed walls",
                "Create overhead protection with concrete or earth",
                "Install ventilation system with filters",
                "Stock with emergency supplies",
                "Test radiation levels inside and outside"
            ]
        elif shelter_type == "above_ground":
            shelter_design["construction_steps"] = [
                "Select interior room with fewest exterior walls",
                "Reinforce walls with concrete blocks or sandbags",
                "Add overhead protection",
                "Seal gaps and openings",
                "Install filtered ventilation",
                "Create separate entrance if possible",
                "Stock with supplies",
                "Mark shelter location clearly"
            ]
        
        # Calculate capacity and duration
        shelter_design["capacity"] = max(2, int(budget / 200))  # Rough estimate
        shelter_design["duration"] = "2 weeks to several months depending on scenario"
        
        # Store in database
        cursor.execute('''
            INSERT INTO radiation_shelters
            (shelter_type, protection_factor, construction_materials,
             build_time, cost_estimate, capacity_people, instructions)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (shelter_type, shelter_design["protection_factor"],
              json.dumps(shelter_design["materials_needed"]),
              "1-3 days", shelter_design["total_cost"],
              shelter_design["capacity"],
              json.dumps(shelter_design["construction_steps"])))
        
        conn.commit()
        conn.close()
        
        # Add essential supplies list
        shelter_design["essential_supplies"] = [
            "Water: 1 gallon per person per day",
            "Food: Non-perishable for 2+ weeks",
            "Battery powered radio and NOAA weather radio",
            "Flashlights and batteries",
            "First aid supplies",
            "Medications",
            "Plastic sheeting and duct tape",
            "Sanitation supplies",
            "Entertainment items (books, games)",
            "Tools for maintenance"
        ]
        
        # Ventilation requirements
        shelter_design["ventilation"] = {
            "requirement": "15 cubic feet per minute per person",
            "filtration": "HEPA or high-efficiency filters preferred",
            "intake": "Low, protected location",
            "exhaust": "High, away from intake",
            "manual_backup": "Hand-crank fan system"
        }
        
        return shelter_design
    
    def run_nuclear_emergency_drill(self, scenario: str = "power_plant_accident") -> Dict:
        """Execute nuclear emergency preparedness drill"""
        drill_result = {
            "drill_date": datetime.now().isoformat(),
            "scenario": scenario,
            "phases_completed": {},
            "total_score": 0,
            "response_times": {},
            "areas_for_improvement": [],
            "strengths": []
        }
        
        print(f"\n☢️ NUCLEAR EMERGENCY DRILL: {scenario.upper()}")
        print("=" * 60)
        
        if scenario == "power_plant_accident":
            print("\nSCENARIO: Nuclear Power Plant Emergency Alert")
            print("Site Area Emergency declared at nearby nuclear facility")
            print("General Emergency may be declared within 2 hours")
            print("Radioactive release possible")
            print("\nYou must prepare for possible evacuation or sheltering...")
            
            # Phase 1: Immediate Response (15 minutes)
            print("\n⏱️ PHASE 1: IMMEDIATE RESPONSE (15 minutes)")
            
            actions = [
                "Turn on battery radio for emergency information",
                "Close all windows and doors",
                "Turn off air conditioning/heating intake",
                "Gather family members indoors",
                "Check emergency kit location and contents"
            ]
            
            completed = 0
            for action in actions:
                response = input(f"Did you {action}? (y/n): ").lower()
                if response == 'y':
                    completed += 1
            
            drill_result["phases_completed"]["immediate_response"] = (completed / len(actions)) * 100
            drill_result["total_score"] += (completed / len(actions)) * 25
            
            # Phase 2: Information Gathering (30 minutes)
            print("\n⏱️ PHASE 2: INFORMATION GATHERING")
            
            actions = [
                "Monitor EAS (Emergency Alert System) broadcasts",
                "Check radiation detection equipment if available",
                "Locate potassium iodide tablets",
                "Review evacuation routes and destinations",
                "Contact family members to inform of situation"
            ]
            
            completed = 0
            for action in actions:
                response = input(f"Did you {action}? (y/n): ").lower()
                if response == 'y':
                    completed += 1
            
            drill_result["phases_completed"]["information_gathering"] = (completed / len(actions)) * 100
            drill_result["total_score"] += (completed / len(actions)) * 25
            
            # Phase 3: Protection Decision (1 hour)
            print("\n⏱️ PHASE 3: PROTECTION DECISION")
            print("Authorities recommend either EVACUATION or SHELTER IN PLACE")
            
            evacuation_actions = [
                "Pack evacuation kit with essentials",
                "Secure home (utilities, windows, doors)",
                "Load family and pets in vehicle",
                "Follow designated evacuation route",
                "Go to designated reception center"
            ]
            
            shelter_actions = [
                "Move to basement or interior room",
                "Seal room with plastic and tape if needed",
                "Set up supplies for extended stay",
                "Monitor radiation levels if possible",
                "Maintain communication with authorities"
            ]
            
            decision = input("Authorities order: (E)vacuate or (S)helter? ").lower()
            
            if decision == 'e':
                actions = evacuation_actions
                print("EVACUATION ordered - you have 30 minutes")
            else:
                actions = shelter_actions
                print("SHELTER IN PLACE ordered - seal your location")
            
            completed = 0
            for action in actions:
                response = input(f"Did you {action}? (y/n): ").lower()
                if response == 'y':
                    completed += 1
            
            drill_result["phases_completed"]["protection_action"] = (completed / len(actions)) * 100
            drill_result["total_score"] += (completed / len(actions)) * 25
            
            # Phase 4: Long-term Management
            print("\n⏱️ PHASE 4: LONG-TERM MANAGEMENT")
            
            actions = [
                "Establish communication schedule",
                "Monitor health for radiation symptoms",
                "Follow decontamination procedures if exposed",
                "Maintain supplies and equipment",
                "Stay informed on recovery operations"
            ]
            
            completed = 0
            for action in actions:
                response = input(f"Can you {action}? (y/n): ").lower()
                if response == 'y':
                    completed += 1
            
            drill_result["phases_completed"]["long_term_management"] = (completed / len(actions)) * 100
            drill_result["total_score"] += (completed / len(actions)) * 25
        
        # Performance analysis
        if drill_result["total_score"] >= 85:
            drill_result["performance"] = "EXCELLENT"
            drill_result["strengths"].append("Well prepared for nuclear emergency")
        elif drill_result["total_score"] >= 70:
            drill_result["performance"] = "GOOD"
            drill_result["strengths"].append("Basic nuclear preparedness in place")
        elif drill_result["total_score"] >= 50:
            drill_result["performance"] = "NEEDS IMPROVEMENT"
            drill_result["areas_for_improvement"].append("Significant gaps in nuclear preparedness")
        else:
            drill_result["performance"] = "POOR"
            drill_result["areas_for_improvement"].append("Major nuclear preparedness deficiencies")
        
        # Specific recommendations
        for phase, score in drill_result["phases_completed"].items():
            if score < 75:
                drill_result["areas_for_improvement"].append(f"Improve {phase.replace('_', ' ')} procedures")
        
        print(f"\n📊 NUCLEAR EMERGENCY DRILL RESULTS")
        print(f"Total Score: {drill_result['total_score']:.1f}%")
        print(f"Performance: {drill_result['performance']}")
        
        return drill_result
    
    def generate_comprehensive_report(self) -> Dict:
        """Generate complete nuclear safety preparedness report"""
        report = {
            "report_date": datetime.now().isoformat(),
            "module_version": "2.0.0",
            "sections": {}
        }
        
        # Nuclear preparedness assessment
        report["sections"]["preparedness"] = self.assess_nuclear_preparedness(20)
        
        # Detection equipment recommendations
        report["sections"]["detection_equipment"] = self.recommend_detection_equipment(500, "moderate")
        
        # Decontamination protocols
        report["sections"]["decontamination"] = self.create_decontamination_protocol("general")
        
        # Evacuation planning
        report["sections"]["evacuation"] = self.plan_evacuation_routes("Unknown", 20)
        
        # Medical protocols
        report["sections"]["medical"] = self.develop_medical_protocols("general")
        
        # Radiation shelter design
        report["sections"]["shelter"] = self.design_radiation_shelter("basement", 1000)
        
        # Overall nuclear preparedness
        report["nuclear_preparedness_score"] = report["sections"]["preparedness"]["preparedness_score"]
        report["preparedness_level"] = self.get_preparedness_level(report["nuclear_preparedness_score"])
        
        return report
    
    def get_preparedness_level(self, score: float) -> str:
        """Determine nuclear preparedness level"""
        if score >= 80:
            return "EXCELLENT - Well prepared for nuclear emergencies"
        elif score >= 65:
            return "GOOD - Adequate nuclear emergency preparations"
        elif score >= 45:
            return "MODERATE - Some nuclear preparations but gaps remain"
        elif score >= 25:
            return "POOR - Significant nuclear preparedness deficiencies"
        else:
            return "CRITICAL - No meaningful nuclear emergency preparations"
    
    def get_evacuation_supplies(self, duration: str) -> List[str]:
        """Get evacuation supplies based on expected duration"""
        base_supplies = [
            "Important documents", "Cash", "Medications", "First aid kit",
            "Flashlight", "Battery radio", "Batteries", "Cell phone charger"
        ]
        
        if "days" in duration.lower():
            base_supplies.extend([
                "3+ days clothing", "Personal hygiene items", 
                "Non-perishable food", "Water bottles"
            ])
        elif "weeks" in duration.lower():
            base_supplies.extend([
                "1-2 weeks clothing", "Extended medications",
                "Comfort items", "Books/games"
            ])
        elif "months" in duration.lower():
            base_supplies.extend([
                "Seasonal clothing", "Important personal items",
                "School/work materials", "Pet supplies"
            ])
        
        return base_supplies


def main():
    """Test the Nuclear Safety Module"""
    print("☢️ NUCLEAR/RADIATION SAFETY MODULE v2.0")
    print("=" * 50)
    
    # Initialize module
    nuclear_module = NuclearSafetyModule()
    
    # Assess preparedness
    print("\n📊 Assessing Nuclear Preparedness...")
    assessment = nuclear_module.assess_nuclear_preparedness(distance_to_plant=20)
    print(f"Risk Level: {assessment['risk_level']}")
    print(f"Preparedness Score: {assessment['preparedness_score']}%")
    print(f"Detection Capability: {assessment['detection_capability']}%")
    
    # Equipment recommendations
    print("\n🔍 Recommending Detection Equipment...")
    equipment = nuclear_module.recommend_detection_equipment(budget=500, risk_level="moderate")
    print(f"Primary Device: {equipment['primary_device'].get('name', 'None')}")
    print(f"Total Cost: ${equipment['total_cost']}")
    
    # Decontamination protocol
    print("\n🚿 Creating Decontamination Protocol...")
    decon = nuclear_module.create_decontamination_protocol("general")
    print(f"Procedures: {len(decon['procedures'])}")
    print(f"Supplies Needed: {len(decon['supplies_needed'])} items")
    
    # Evacuation planning
    print("\n🚗 Planning Evacuation Routes...")
    evacuation = nuclear_module.plan_evacuation_routes("Unknown", 20)
    print(f"Facility Distance: {evacuation['facility_distance']} miles")
    print(f"Routes Planned: {len(evacuation['routes'])}")
    
    # Medical protocols
    print("\n🏥 Developing Medical Protocols...")
    medical = nuclear_module.develop_medical_protocols("general")
    print(f"Exposure Levels: {len(medical['exposure_levels'])}")
    print(f"Medications Needed: {len(medical['medications_needed'])}")
    
    # Radiation shelter
    print("\n🏠 Designing Radiation Shelter...")
    shelter = nuclear_module.design_radiation_shelter("basement", 1000)
    print(f"Protection Factor: {shelter['protection_factor']}")
    print(f"Total Cost: ${shelter['total_cost']}")
    print(f"Capacity: {shelter['capacity']} people")
    
    print("\n✅ Nuclear Safety Module initialized successfully!")
    print("Ready to improve nuclear preparedness from 40.7% to 65%+")


if __name__ == "__main__":
    main()