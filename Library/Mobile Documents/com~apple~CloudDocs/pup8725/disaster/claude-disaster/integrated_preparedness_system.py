#!/usr/bin/env python3
"""
Integrated Emergency Preparedness System
Main interface combining all preparedness modules into a unified system
"""

import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional

# Import all modules
from disaster_probability_matrix import DisasterProbabilityMatrix
from interactive_risk_assessment import InteractiveRiskAssessment
from supply_inventory_tracker import SupplyInventoryTracker
from emergency_contacts_manager import EmergencyContactsManager
from alert_monitoring_system import AlertMonitoringSystem
from neighborhood_coordination import NeighborhoodCoordination
from scenario_planning import ScenarioPlanner
from communication_emergency_plan import CommunicationEmergencyPlan
from financial_emergency_planning import FinancialEmergencyPlanner
from simple_engineering_solutions import SimpleEngineeringSolutions
from intuitive_building_guide import IntuitiveBuilder
from materials_calculator import MaterialsCalculator
from step_by_step_builder import StepByStepBuilder
from emergency_drill_simulator import EmergencyDrillSimulator
from visualization_dashboard import VisualizationDashboard
from knowledge_base_search import KnowledgeBaseSearch

# Import Version 2.0 Modern Threat Modules
from v2_modules.cyber_attack_response import CyberAttackResponseModule
from v2_modules.emp_hardening_module import EMPHardeningModule
from v2_modules.nuclear_safety_module import NuclearSafetyModule

class IntegratedPreparednessSystem:
    def __init__(self, data_dir: str = "preparedness_data"):
        """Initialize integrated preparedness system"""
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize all subsystems
        self.risk_matrix = DisasterProbabilityMatrix()
        self.risk_assessment = InteractiveRiskAssessment()
        self.supply_tracker = SupplyInventoryTracker(f"{data_dir}/supplies.db")
        self.contacts = EmergencyContactsManager(f"{data_dir}/contacts.db")
        self.alert_monitor = AlertMonitoringSystem(f"{data_dir}/alerts.db")
        self.neighborhood = NeighborhoodCoordination(f"{data_dir}/neighborhood.db")
        self.scenario_planner = ScenarioPlanner()
        self.communication_plan = CommunicationEmergencyPlan()
        self.financial_plan = FinancialEmergencyPlanner()
        
        # Initialize engineering and building modules
        self.engineering_solutions = SimpleEngineeringSolutions(f"{data_dir}/engineering.db")
        self.building_guide = IntuitiveBuilder(f"{data_dir}/building_guides.db")
        self.materials_calc = MaterialsCalculator(f"{data_dir}/materials.db")
        self.step_builder = StepByStepBuilder(f"{data_dir}/step_builder.db")
        
        # Initialize new enhancement modules
        self.drill_simulator = EmergencyDrillSimulator(f"{data_dir}/drill_simulator.db")
        self.dashboard = VisualizationDashboard(data_dir)
        self.knowledge_base = KnowledgeBaseSearch("disaster_knowledge_base", f"{data_dir}/knowledge_base.db")
        
        # Initialize Version 2.0 Modern Threat Modules
        self.cyber_response = CyberAttackResponseModule(f"{data_dir}/modern_threats.db")
        self.emp_hardening = EMPHardeningModule(f"{data_dir}/modern_threats.db")
        self.nuclear_safety = NuclearSafetyModule(f"{data_dir}/modern_threats.db")
        
        self.system_status = {
            "initialized": datetime.now().isoformat(),
            "modules_active": 19,
            "data_directory": data_dir
        }
        
        # Initialize with default data
        self._initialize_default_data()
    
    def _initialize_default_data(self):
        """Initialize databases with default engineering and building data"""
        try:
            # Initialize engineering solutions database
            self.engineering_solutions.initialize_default_solutions()
            
            # Initialize building guides with default projects
            self.building_guide.initialize_default_guides()
            
            # Initialize step-by-step builder with emergency shelter guide
            try:
                self.step_builder.create_emergency_shelter_guide()
            except:
                pass  # May already exist
                
            # Initialize emergency contacts with default services
            self.contacts.initialize_default_services()
            
            # Initialize drill scenarios
            self.drill_simulator.create_earthquake_drill()
            self.drill_simulator.create_fire_evacuation_drill()
            self.drill_simulator.create_severe_weather_drill()
            
            # Index knowledge base
            self.knowledge_base.index_knowledge_base()
            
        except Exception as e:
            # Non-critical - system can still function
            print(f"Note: Some default data initialization skipped: {e}")
    
    def show_main_menu(self):
        """Display main system menu"""
        print("\n" + "="*60)
        print("🚨 INTEGRATED EMERGENCY PREPAREDNESS SYSTEM 🚨")
        print("="*60)
        print("\n📊 ASSESSMENT & PLANNING")
        print("  1. Risk Assessment & Probability Matrix")
        print("  2. Scenario Planning & Response")
        print("  3. Financial Emergency Planning")
        print("  4. Communication Planning")
        
        print("\n📦 INVENTORY & SUPPLIES")
        print("  5. Supply Inventory Management")
        print("  6. Shopping List Generator")
        print("  7. Expiration Alerts")
        
        print("\n👥 CONTACTS & COORDINATION")
        print("  8. Emergency Contacts Management")
        print("  9. Neighborhood Coordination")
        print(" 10. Community Resource Sharing")
        
        print("\n🌪️  MONITORING & ALERTS")
        print(" 11. Weather & Alert Monitoring")
        print(" 12. Active Alert Dashboard")
        print(" 13. System Status Check")
        
        print("\n🔧 ENGINEERING & BUILDING")
        print(" 17. Engineering Solutions Database")
        print(" 18. Building Project Calculator")
        print(" 19. Step-by-Step Construction Guide")
        print(" 20. Materials & Tools Calculator")
        
        print("\n🎯 TRAINING & DRILLS")
        print(" 21. Emergency Drill Simulator")
        print(" 22. View Drill Performance History")
        
        print("\n📊 ANALYTICS & INSIGHTS")
        print(" 23. Visual Dashboard")
        print(" 24. Export Dashboard to HTML")
        
        print("\n📚 KNOWLEDGE BASE")
        print(" 25. Search Knowledge Base")
        print(" 26. Browse Checklists")
        print(" 27. Generate Quick Reference Cards")
        
        print("\n🚨 MODERN THREATS (V2.0)")
        print(" 28. Cyber Attack Response")
        print(" 29. EMP/Solar Flare Hardening")
        print(" 30. Nuclear/Radiation Safety")
        
        print("\n📋 REPORTS & EXPORT")
        print(" 31. Comprehensive Preparedness Report")
        print(" 32. Export All Data")
        print(" 33. Emergency Quick Reference")
        
        print("\n 0. Exit System")
        print("="*60)
    
    def run_risk_assessment(self):
        """Run comprehensive risk assessment"""
        print("\n🎯 RUNNING COMPREHENSIVE RISK ASSESSMENT")
        print("-" * 50)
        
        # Collect user profile
        self.risk_assessment.collect_user_profile()
        
        # Generate personalized risks
        print("\nCalculating personalized risk matrix...")
        personalized_risks = self.risk_assessment.generate_personalized_matrix()
        
        # Display top risks
        print("\n📈 TOP 10 HIGHEST PROBABILITY RISKS:")
        for i, (event, prob) in enumerate(personalized_risks['high_probability'][:10], 1):
            print(f"{i:2}. {event:<30} {prob:>6.1f}%")
        
        # Generate recommendations
        recommendations = self.risk_assessment.generate_recommendations()
        print(f"\n💡 RECOMMENDATIONS:")
        for category, items in recommendations.items():
            print(f"\n{category.upper()}:")
            for item in items[:3]:  # Top 3 per category
                print(f"  • {item}")
        
        return personalized_risks
    
    def manage_supplies(self):
        """Supply inventory management interface"""
        while True:
            print("\n📦 SUPPLY INVENTORY MANAGEMENT")
            print("-" * 40)
            print("1. View Inventory Summary")
            print("2. Add Supply Item")
            print("3. Check Minimum Levels")
            print("4. Check Expiration Alerts")
            print("5. Generate Shopping List")
            print("6. Record Supply Usage")
            print("0. Return to Main Menu")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                summary = self.supply_tracker.get_inventory_summary()
                print(f"\n📊 INVENTORY SUMMARY")
                print(f"Categories: {len(summary['categories'])}")
                for cat, info in summary['categories'].items():
                    print(f"  {cat}: {info['item_count']} items")
                
            elif choice == "2":
                print("\n➕ ADD SUPPLY ITEM")
                category = input("Category: ")
                name = input("Item name: ")
                quantity = float(input("Quantity: "))
                unit = input("Unit: ")
                expiration = input("Expiration date (YYYY-MM-DD, optional): ").strip() or None
                location = input("Location (optional): ").strip() or None
                
                item_id = self.supply_tracker.add_supply(category, name, quantity, unit, expiration, location)
                print(f"✅ Added item #{item_id}")
                
            elif choice == "3":
                family_size = int(input("Family size: "))
                alerts = self.supply_tracker.check_minimum_levels(family_size)
                print(f"\n⚠️  MINIMUM LEVEL ALERTS ({len(alerts)} items)")
                for alert in alerts:
                    print(f"  {alert['category']}: {alert['current']}/{alert['minimum']} {alert['unit']} (shortage: {alert['shortage']})")
                    
            elif choice == "4":
                days = int(input("Check expiration within how many days? (default 30): ") or 30)
                expiring = self.supply_tracker.check_expiration_alerts(days)
                print(f"\n📅 EXPIRING ITEMS ({len(expiring)} items)")
                for item in expiring:
                    print(f"  {item['item']}: expires in {item['days_until']} days")
                    
            elif choice == "5":
                family_size = int(input("Family size: "))
                shopping = self.supply_tracker.generate_shopping_list(family_size)
                print(f"\n🛒 SHOPPING LIST")
                for priority, items in shopping.items():
                    if items:
                        print(f"\n{priority.upper()}:")
                        for item in items:
                            if 'category' in item:
                                print(f"  • {item['category']}: {item['quantity_needed']} {item['unit']}")
                            else:
                                print(f"  • {item['item']} ({item['reason']})")
    
    def manage_contacts(self):
        """Emergency contacts management interface"""
        while True:
            print("\n👥 EMERGENCY CONTACTS MANAGEMENT")
            print("-" * 40)
            print("1. View Priority Contacts")
            print("2. Add New Contact")
            print("3. Create Contact Group")
            print("4. Generate Emergency Card")
            print("5. Check Verification Status")
            print("0. Return to Main Menu")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                contacts = self.contacts.get_priority_contacts()
                print(f"\n📞 PRIORITY CONTACTS ({len(contacts)} contacts)")
                for contact in contacts[:10]:  # Top 10
                    print(f"  {contact['name']} ({contact['category']}): {contact['primary_phone']}")
                    
            elif choice == "2":
                print("\n➕ ADD EMERGENCY CONTACT")
                category = input("Category: ")
                name = input("Name: ")
                phone = input("Primary phone: ")
                relationship = input("Relationship (optional): ").strip() or None
                email = input("Email (optional): ").strip() or None
                
                contact_id = self.contacts.add_contact(category, name, phone, relationship, None, email)
                print(f"✅ Added contact #{contact_id}")
                
            elif choice == "4":
                card = self.contacts.get_emergency_card()
                print(f"\n💳 EMERGENCY CONTACT CARD")
                print(card)
                
                save = input("\nSave to file? (y/n): ").lower() == 'y'
                if save:
                    with open(f"{self.data_dir}/emergency_card.txt", 'w') as f:
                        f.write(card)
                    print("💾 Saved to emergency_card.txt")
    
    def monitor_alerts(self):
        """Alert monitoring interface"""
        print("\n🌪️  ALERT MONITORING SYSTEM")
        print("-" * 40)
        
        # Check if location is configured
        try:
            results = self.alert_monitor.run_monitoring_cycle()
            if "error" in results:
                print("⚠️  System not configured. Setting up location...")
                lat = float(input("Latitude: "))
                lon = float(input("Longitude: "))
                location = input("Location name: ")
                api_key = input("OpenWeather API key (optional): ").strip() or None
                
                self.alert_monitor.set_location(lat, lon, location, api_key)
                results = self.alert_monitor.run_monitoring_cycle()
            
            print(f"\n📡 MONITORING RESULTS")
            print(f"New alerts: {results['new_alerts']}")
            print(f"Weather risks: {len(results['weather_risks'])}")
            for risk in results['weather_risks']:
                print(f"  ⚠️  {risk}")
            
            if results['errors']:
                print(f"Errors: {len(results['errors'])}")
                for error in results['errors']:
                    print(f"  ❌ {error}")
            
            # Show active alerts
            active = self.alert_monitor.get_active_alerts()
            print(f"\n🚨 ACTIVE ALERTS ({len(active)})")
            for alert in active[:5]:  # Top 5
                print(f"  {alert['title']} (Severity: {alert['severity']})")
                
        except Exception as e:
            print(f"❌ Error running monitoring: {e}")
    
    def generate_comprehensive_report(self) -> Dict:
        """Generate comprehensive preparedness report"""
        print("\n📋 GENERATING COMPREHENSIVE PREPAREDNESS REPORT")
        print("-" * 55)
        
        report = {
            "generated": datetime.now().isoformat(),
            "system_status": self.system_status,
            "preparedness_score": 0,
            "sections": {}
        }
        
        # Supply inventory status
        print("Analyzing supply inventory...")
        supply_summary = self.supply_tracker.get_inventory_summary()
        family_size = 3  # Default
        supply_alerts = self.supply_tracker.check_minimum_levels(family_size)
        expiring_items = self.supply_tracker.check_expiration_alerts(30)
        
        supply_score = max(0, 100 - (len(supply_alerts) * 10) - (len(expiring_items) * 5))
        
        report["sections"]["supplies"] = {
            "score": supply_score,
            "total_categories": len(supply_summary['categories']),
            "shortages": len(supply_alerts),
            "expiring_soon": len(expiring_items),
            "status": "excellent" if supply_score >= 90 else "good" if supply_score >= 70 else "needs_improvement"
        }
        
        # Contact management status
        print("Analyzing contact management...")
        verification_status = self.contacts.get_verification_status()
        contact_score = verification_status['statistics']['verification_rate']
        
        report["sections"]["contacts"] = {
            "score": contact_score,
            "total_contacts": verification_status['statistics']['total'],
            "verified_contacts": verification_status['statistics']['verified'],
            "needs_verification": len(verification_status['needs_verification']),
            "status": "excellent" if contact_score >= 90 else "good" if contact_score >= 70 else "needs_improvement"
        }
        
        # Alert monitoring status
        print("Checking alert monitoring...")
        try:
            alert_summary = self.alert_monitor.generate_alert_summary()
            alert_score = 100 - (alert_summary['urgent_count'] * 20)  # Deduct for urgent alerts
            
            report["sections"]["monitoring"] = {
                "score": max(0, alert_score),
                "active_alerts": alert_summary['total_active'],
                "urgent_alerts": alert_summary['urgent_count'],
                "highest_severity": alert_summary['highest_severity'],
                "status": "excellent" if alert_score >= 90 else "good" if alert_score >= 70 else "needs_attention"
            }
        except:
            report["sections"]["monitoring"] = {
                "score": 50,
                "status": "not_configured"
            }
        
        # Calculate overall preparedness score
        scores = [section.get('score', 0) for section in report["sections"].values()]
        report["preparedness_score"] = sum(scores) / len(scores) if scores else 0
        
        # Recommendations
        recommendations = []
        if supply_score < 80:
            recommendations.append("Address supply shortages - check minimum levels")
        if contact_score < 80:
            recommendations.append("Verify emergency contacts - many outdated")
        if report["sections"]["monitoring"]["status"] == "not_configured":
            recommendations.append("Configure alert monitoring system")
        
        report["recommendations"] = recommendations
        
        return report
    
    def export_all_data(self):
        """Export all system data"""
        print("\n💾 EXPORTING ALL SYSTEM DATA")
        print("-" * 35)
        
        export_dir = f"{self.data_dir}/exports"
        os.makedirs(export_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            # Export supplies
            supply_file = f"{export_dir}/supplies_{timestamp}.json"
            self.supply_tracker.export_inventory(supply_file)
            print(f"✅ Supplies exported: {supply_file}")
            
            # Export contacts
            contact_file = f"{export_dir}/contacts_{timestamp}.json"
            self.contacts.export_contacts(contact_file)
            print(f"✅ Contacts exported: {contact_file}")
            
            # Export comprehensive report
            report = self.generate_comprehensive_report()
            report_file = f"{export_dir}/preparedness_report_{timestamp}.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"✅ Report exported: {report_file}")
            
            # Create quick reference
            quick_ref = self.generate_quick_reference()
            ref_file = f"{export_dir}/quick_reference_{timestamp}.txt"
            with open(ref_file, 'w') as f:
                f.write(quick_ref)
            print(f"✅ Quick reference exported: {ref_file}")
            
            print(f"\n📁 All data exported to: {export_dir}")
            
        except Exception as e:
            print(f"❌ Export error: {e}")
    
    def generate_quick_reference(self) -> str:
        """Generate emergency quick reference guide"""
        ref = f"""
🚨 EMERGENCY QUICK REFERENCE GUIDE 🚨
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

📞 PRIORITY EMERGENCY CONTACTS
{'='*40}
"""
        
        try:
            priority_contacts = self.contacts.get_priority_contacts()
            for contact in priority_contacts[:8]:  # Top 8
                ref += f"{contact['name']:<20} {contact['primary_phone']}\n"
        except:
            ref += "Emergency contacts not configured\n"
        
        ref += f"""
📦 CRITICAL SUPPLY STATUS
{'='*40}
"""
        
        try:
            supply_alerts = self.supply_tracker.check_minimum_levels(3)
            if supply_alerts:
                for alert in supply_alerts[:5]:
                    ref += f"⚠️  {alert['category']}: {alert['current']}/{alert['minimum']} {alert['unit']}\n"
            else:
                ref += "✅ All critical supplies at adequate levels\n"
        except:
            ref += "Supply inventory not configured\n"
        
        ref += f"""
🌪️  CURRENT ALERTS
{'='*40}
"""
        
        try:
            active_alerts = self.alert_monitor.get_active_alerts(3)  # Severe+ only
            if active_alerts:
                for alert in active_alerts[:3]:
                    ref += f"🚨 {alert['title']}\n"
            else:
                ref += "✅ No severe weather alerts\n"
        except:
            ref += "Alert monitoring not configured\n"
        
        ref += f"""
📋 EMERGENCY PROCEDURES
{'='*40}
1. Assess immediate danger
2. Ensure family safety first
3. Contact emergency services if needed (911)
4. Implement family communication plan
5. Check on neighbors if safe to do so
6. Monitor official emergency broadcasts
7. Follow evacuation orders immediately

💡 Remember: Stay calm, think clearly, help others when safe
"""
        
        return ref
    
    def engineering_solutions_interface(self):
        """Engineering solutions database interface"""
        while True:
            print("\n🔧 ENGINEERING SOLUTIONS DATABASE")
            print("-" * 40)
            print("1. Browse Solutions by Category")
            print("2. Find Solutions for Disaster Scenario")
            print("3. Get Solution Details & Instructions")
            print("4. Add New Solution")
            print("5. Search by Available Materials")
            print("0. Return to Main Menu")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                categories = ["water_collection", "water_purification", "shelter", 
                            "power_generation", "heating_cooling", "tools"]
                print("\nAvailable categories:")
                for i, cat in enumerate(categories, 1):
                    print(f"  {i}. {cat.replace('_', ' ').title()}")
                
                try:
                    cat_choice = int(input("Select category: ")) - 1
                    if 0 <= cat_choice < len(categories):
                        solutions = self.engineering_solutions.get_solutions_by_category(categories[cat_choice])
                        print(f"\n{categories[cat_choice].replace('_', ' ').title()} Solutions:")
                        for sol in solutions:
                            print(f"  • {sol['name']} ({sol['difficulty']}) - ${sol['cost_estimate']:.2f}")
                except (ValueError, IndexError):
                    print("Invalid selection")
                    
            elif choice == "2":
                scenario = input("Enter disaster scenario (e.g., 'flood', 'power outage'): ")
                solutions = self.engineering_solutions.find_solutions_by_scenario(scenario)
                print(f"\nSolutions for '{scenario}':")
                for sol in solutions:
                    print(f"  • {sol['name']} ({sol['difficulty']})")
                    
            elif choice == "3":
                try:
                    solution_id = int(input("Enter solution ID: "))
                    details = self.engineering_solutions.get_solution_details(solution_id)
                    if details:
                        print(f"\n📋 {details['name']}")
                        print(f"Category: {details['category']}")
                        print(f"Difficulty: {details['difficulty']}")
                        print(f"Build Time: {details['build_time']}")
                        print(f"Cost: ${details['cost_estimate']:.2f}")
                        print(f"\nMaterials ({len(details['materials'])}):")
                        for mat in details['materials']:
                            print(f"  • {mat['quantity']} {mat['unit']} {mat['name']}")
                        print(f"\nInstructions ({len(details['instructions'])}):")
                        for inst in details['instructions']:
                            print(f"  {inst['step']}. {inst['instruction']}")
                except (ValueError, KeyError):
                    print("Invalid solution ID")
    
    def building_calculator_interface(self):
        """Building project calculator interface"""
        while True:
            print("\n🏗️ BUILDING PROJECT CALCULATOR")
            print("-" * 40)
            print("1. Calculate Complete Shelter")
            print("2. Calculate Foundation Materials")
            print("3. Calculate Frame Materials")
            print("4. Calculate Roofing Materials")
            print("5. Optimize Materials for Budget")
            print("0. Return to Main Menu")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                try:
                    length = float(input("Shelter length (feet): "))
                    width = float(input("Shelter width (feet): "))
                    height = float(input("Shelter height (feet, default 8): ") or 8)
                    foundation = input("Include foundation? (y/n): ").lower() == 'y'
                    
                    calc = self.materials_calc.calculate_complete_shelter(length, width, height, foundation)
                    
                    print(f"\n🏠 COMPLETE SHELTER CALCULATION")
                    print(f"Dimensions: {length}'L x {width}'W x {height}'H")
                    print(f"Material Cost: ${calc['total_material_cost']:,.2f}")
                    print(f"Tool Cost: ${calc['total_tool_cost']:,.2f}")
                    print(f"Build Time: {calc['estimated_build_time']}")
                    print(f"Difficulty: {calc['difficulty_level']}")
                    
                    print(f"\nMATERIALS BREAKDOWN:")
                    for material, details in calc["materials"].items():
                        print(f"  {material}: {details['quantity']} - ${details['total_cost']:.2f}")
                    
                    save = input("\nSave calculation? (y/n): ").lower() == 'y'
                    if save:
                        name = input("Project name: ")
                        self.materials_calc.save_calculation(name, calc)
                        print("✅ Calculation saved")
                        
                except ValueError:
                    print("Invalid input - please enter numbers")
                    
            elif choice == "2":
                try:
                    length = float(input("Foundation length (feet): "))
                    width = float(input("Foundation width (feet): "))
                    thickness = float(input("Foundation thickness (feet, default 0.5): ") or 0.5)
                    
                    calc = self.materials_calc.calculate_foundation_materials(length, width, thickness)
                    
                    print(f"\n🏗️ FOUNDATION CALCULATION")
                    print(f"Dimensions: {length}'L x {width}'W x {thickness}'T")
                    print(f"Total Cost: ${calc['total_cost']:,.2f}")
                    print(f"Volume: {calc['volume_cubic_feet']:.1f} cubic feet")
                    
                    for material, details in calc["materials"].items():
                        print(f"  {material}: {details['quantity']} {details['unit']} - ${details['total_cost']:.2f}")
                        
                except ValueError:
                    print("Invalid input - please enter numbers")
    
    def step_by_step_guide_interface(self):
        """Step-by-step construction guide interface"""
        while True:
            print("\n📋 STEP-BY-STEP CONSTRUCTION GUIDE")
            print("-" * 40)
            print("1. Start New Building Project")
            print("2. Continue Existing Project")
            print("3. View Available Project Guides")
            print("4. Create Emergency Shelter Guide")
            print("0. Return to Main Menu")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                name = input("Your name: ")
                print("\nAvailable Projects:")
                print("  1. Emergency A-Frame Shelter")
                # Add more project options here
                
                try:
                    project_choice = int(input("Select project: "))
                    if project_choice == 1:
                        # Initialize default shelter guide if not exists
                        try:
                            project_id = self.step_builder.create_emergency_shelter_guide()
                        except:
                            project_id = 1  # Assume it exists
                        
                        session_id = self.step_builder.start_user_session(project_id, name)
                        self._run_building_session(session_id)
                except ValueError:
                    print("Invalid selection")
                    
            elif choice == "2":
                try:
                    session_id = int(input("Enter session ID: "))
                    self._run_building_session(session_id)
                except ValueError:
                    print("Invalid session ID")
                    
            elif choice == "4":
                try:
                    project_id = self.step_builder.create_emergency_shelter_guide()
                    print(f"✅ Emergency shelter guide created with ID: {project_id}")
                except Exception as e:
                    print(f"❌ Error creating guide: {e}")
    
    def _run_building_session(self, session_id: int):
        """Run interactive building session"""
        while True:
            progress = self.step_builder.get_user_progress(session_id)
            if not progress:
                print("❌ Session not found")
                return
            
            if progress["current_step"] > progress["total_steps"]:
                print("🎉 Project completed!")
                return
            
            guide = self.step_builder.generate_interactive_guide(
                progress["project_id"], progress["current_step"]
            )
            print(guide)
            
            action = input().lower().strip()
            
            if action == 'y':
                rating = int(input("Quality rating (1-5): ") or 5)
                notes = input("Any notes (optional): ")
                
                self.step_builder.complete_step(session_id, progress["current_step"], rating, notes)
                print("✅ Step completed!")
                
            elif action == 'h':
                step = self.step_builder.get_build_step(progress["project_id"], progress["current_step"])
                print(f"\n💡 HELP FOR STEP {progress['current_step']}:")
                if step.get('common_mistakes'):
                    print("Common mistakes to avoid:")
                    for mistake in step['common_mistakes']:
                        print(f"  • {mistake}")
                        
            elif action == 'q':
                issues = input("Describe quality issues encountered: ")
                # Could integrate with quality tracking system
                print("Quality issues noted")
                
            elif action == 'exit':
                break
    
    def materials_tools_calculator(self):
        """Materials and tools calculator interface"""
        while True:
            print("\n🧮 MATERIALS & TOOLS CALCULATOR")
            print("-" * 40)
            print("1. Beam Load Calculator")
            print("2. Foundation Size Calculator")
            print("3. Material Cost Estimator")
            print("4. Tool Requirements")
            print("5. Bulk Pricing Optimizer")
            print("0. Return to Main Menu")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                try:
                    length = float(input("Beam length (feet): "))
                    load = float(input("Load (pounds): "))
                    material = input("Material (2x4_lumber, 2x6_lumber, etc.): ") or "2x4_lumber"
                    
                    calc = self.building_guide.calculate_beam_load(length, load, material)
                    
                    print(f"\n⚖️ BEAM ANALYSIS")
                    print(f"Status: {calc['status']}")
                    print(f"Deflection: {calc['deflection_inches']} inches")
                    print(f"Max allowable: {calc['max_allowable_inches']} inches")
                    print(f"Safety ratio: {calc['safety_ratio']}")
                    print(f"Recommendation: {calc['recommendation']}")
                    
                except ValueError:
                    print("Invalid input - please enter numbers")
                    
            elif choice == "2":
                try:
                    weight = float(input("Structure weight (pounds): "))
                    soil = input("Soil type (rock/hard_clay/average/soft_clay/sand): ") or "average"
                    
                    calc = self.building_guide.calculate_foundation_size(weight, soil)
                    
                    print(f"\n🏗️ FOUNDATION CALCULATION")
                    print(f"Required area: {calc['required_area_sqft']} sq ft")
                    print(f"Recommended width: {calc['recommended_width_ft']} ft")
                    print(f"Recommended depth: {calc['recommended_depth_ft']} ft")
                    print(f"Concrete needed: {calc['concrete_needed_cubic_ft']} cubic feet")
                    
                except ValueError:
                    print("Invalid input - please enter numbers")
    
    def run_drill_simulator(self):
        """Run emergency drill simulator interface"""
        print("\n🎯 EMERGENCY DRILL SIMULATOR")
        print("-" * 40)
        print("Available Drills:")
        print("  1. Earthquake Response Drill")
        print("  2. Fire Evacuation Drill")
        print("  3. Tornado Warning Drill")
        
        try:
            choice = int(input("\nSelect drill (1-3): "))
            name = input("Participant name: ")
            family_size = int(input("Family size (1-5): ") or 4)
            
            # Run selected drill
            result = self.drill_simulator.run_drill(choice, name, family_size)
            
            # Show recommendations
            recommendations = self.drill_simulator.recommend_next_drill(name)
            if recommendations['recommendations']:
                print(f"\n💡 RECOMMENDED NEXT DRILL:")
                for rec in recommendations['recommendations'][:1]:
                    print(f"  {rec['name']}: {rec['reason']}")
                    
        except (ValueError, KeyError) as e:
            print(f"Error running drill: {e}")
    
    def view_drill_history(self):
        """View drill performance history"""
        name = input("Enter participant name: ")
        history = self.drill_simulator.get_performance_history(name)
        
        print(f"\n📈 PERFORMANCE HISTORY FOR {name.upper()}")
        print(f"Total Drills: {history['total_drills']}")
        print(f"Average Score: {history['average_score']}")
        print(f"Best Score: {history['best_score']}")
        
        if history['recent_drills']:
            print(f"\nRecent Drills:")
            for drill in history['recent_drills']:
                print(f"  • {drill['scenario']} - Score: {drill['score']} ({drill['grade']})")
    
    def show_visual_dashboard(self):
        """Display visual analytics dashboard"""
        print("\n📊 GENERATING VISUAL DASHBOARD...")
        dashboard_output = self.dashboard.generate_full_dashboard()
        print(dashboard_output)
    
    def export_dashboard(self):
        """Export dashboard to HTML file"""
        filename = input("Enter filename (default: emergency_dashboard.html): ").strip()
        if not filename:
            filename = "emergency_dashboard.html"
        
        filepath = self.dashboard.export_dashboard_html(filename)
        print(f"✅ Dashboard exported to: {filepath}")
        print("Open in web browser for best viewing experience")
    
    def search_knowledge_base(self):
        """Search knowledge base interface"""
        while True:
            print("\n📚 KNOWLEDGE BASE SEARCH")
            print("-" * 40)
            query = input("Search query (or 'back' to return): ").strip()
            
            if query.lower() == 'back':
                break
            
            results = self.knowledge_base.search(query)
            
            if results:
                print(f"\n📖 SEARCH RESULTS ({len(results)} found):")
                for i, result in enumerate(results[:5], 1):
                    print(f"\n{i}. {result['title']} ({result['category']})")
                    if result['sections']:
                        print(f"   {result['sections'][0]['content']}")
                
                # Option to view full document
                try:
                    view = input("\nView full document? Enter number (or press Enter to skip): ").strip()
                    if view and view.isdigit():
                        doc_id = results[int(view) - 1]['id']
                        doc = self.knowledge_base.get_document(doc_id)
                        print(f"\n{'='*60}")
                        print(f"📄 {doc['title']}")
                        print(f"{'='*60}")
                        print(doc['content'][:2000])  # First 2000 chars
                        if len(doc['content']) > 2000:
                            print("\n[Document truncated - see full file for complete content]")
                except (ValueError, IndexError):
                    pass
            else:
                print("No results found. Try different keywords.")
    
    def browse_checklists(self):
        """Browse interactive checklists"""
        print("\n✅ INTERACTIVE CHECKLISTS")
        print("-" * 40)
        
        categories = ["water", "food", "shelter", "medical", "evacuation", None]
        print("Categories:")
        for i, cat in enumerate(categories[:-1], 1):
            print(f"  {i}. {cat.title()}")
        print(f"  {len(categories)}. All checklists")
        
        try:
            choice = int(input("\nSelect category: "))
            category = categories[choice - 1] if choice < len(categories) else None
            
            checklists = self.knowledge_base.get_checklists(category)
            
            if checklists:
                for checklist in checklists[:5]:
                    print(f"\n📝 {checklist['title']} ({checklist['category']})")
                    print(f"   Priority: {checklist['priority']}/10")
                    print(f"   Items ({len(checklist['items'])}):")
                    for item in checklist['items'][:5]:
                        check = "✓" if item.get('checked') else "□"
                        print(f"     {check} {item['text']}")
                    if len(checklist['items']) > 5:
                        print(f"     ... and {len(checklist['items']) - 5} more items")
            else:
                print("No checklists found for this category")
                
        except (ValueError, IndexError):
            print("Invalid selection")
    
    def generate_reference_cards(self):
        """Generate printable quick reference cards"""
        print("\n📇 GENERATING QUICK REFERENCE CARDS...")
        
        cards = self.knowledge_base.generate_quick_reference_cards()
        
        for card in cards:
            print(f"\n{'='*50}")
            print(f"📇 {card['title'].upper()}")
            print(f"Category: {card['category']}")
            print(f"{'='*50}")
            print(card['content'])
        
        save = input("\nSave cards to file? (y/n): ").lower() == 'y'
        if save:
            filename = f"{self.data_dir}/quick_reference_cards.txt"
            with open(filename, 'w') as f:
                for card in cards:
                    f.write(f"{'='*50}\n")
                    f.write(f"{card['title'].upper()}\n")
                    f.write(f"Category: {card['category']}\n")
                    f.write(f"{'='*50}\n")
                    f.write(card['content'])
                    f.write("\n\n")
            print(f"✅ Cards saved to: {filename}")
    
    # Version 2.0 Modern Threat Module Handlers
    def run_cyber_attack_response(self):
        """Interface for Cyber Attack Response Module"""
        print("\n🔒 CYBER ATTACK RESPONSE MODULE v2.0")
        print("=" * 50)
        
        while True:
            print("\n1. Assess Cyber Preparedness")
            print("2. Create Offline Backup Plan")
            print("3. Generate Manual Operations Guide")
            print("4. Calculate Financial Alternatives")
            print("5. Setup Communication Backups")
            print("6. Secure Identity Documents")
            print("7. Run Cyber Attack Drill")
            print("8. Generate Comprehensive Report")
            print("0. Return to Main Menu")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                assessment = self.cyber_response.assess_cyber_preparedness(4)
                print(f"\n📊 Cyber Preparedness Score: {assessment['preparedness_score']}%")
                print(f"Level: {assessment['preparedness_level']}")
                if assessment['critical_gaps']:
                    print("\n🚨 Critical Gaps:")
                    for gap in assessment['critical_gaps']:
                        print(f"  • {gap}")
                if assessment['recommendations']:
                    print("\n💡 Recommendations:")
                    for rec in assessment['recommendations']:
                        print(f"  • {rec}")
            elif choice == "2":
                backup_plan = self.cyber_response.create_offline_backup_plan()
                print(f"\n💾 Offline Backup Plan Created")
                print(f"Priority items to backup: {len(backup_plan['priority_items'])}")
                print(f"Estimated total time: {backup_plan['total_estimated_time']} hours")
                print("\nBackup Schedule:")
                for freq, items in backup_plan['backup_schedule'].items():
                    print(f"  {freq.title()}: {', '.join(items)}")
            elif choice == "3":
                manual_guide = self.cyber_response.generate_manual_operations_guide()
                print(f"\n📋 Manual Operations Guide Created")
                print(f"Critical systems covered: {len(manual_guide['critical_systems'])}")
                print(f"Tools required: {len(manual_guide['tools_required'])} items")
                print("\nSkills to develop:")
                for skill in manual_guide['skill_development']:
                    print(f"  • {skill}")
            elif choice == "4":
                financial = self.cyber_response.calculate_financial_alternatives(3000, 4)
                print(f"\n💰 Financial Alternatives Calculated")
                print(f"Total recommended value: ${financial['total_recommended_value']:.2f}")
                print(f"Diversification score: {financial['diversification_score']}/100")
                print("\nRecommendations by type:")
                for asset_type, details in financial['recommendations'].items():
                    print(f"  {asset_type.title()}: {details['amount']} ({details['percentage']})")
            elif choice == "7":
                print("\n🎯 Starting Cyber Attack Drill...")
                drill_result = self.cyber_response.run_cyber_attack_drill("ransomware", ["Adult 1", "Adult 2"])
                print(f"\nDrill Performance: {drill_result['performance_level']}")
            elif choice == "8":
                print("\n📊 Generating Comprehensive Cyber Report...")
                report = self.cyber_response.generate_comprehensive_report()
                print(f"Overall Cyber Preparedness: {report['overall_cyber_preparedness']}%")
                print(f"Level: {report['preparedness_level']}")
            else:
                print("❌ Invalid option. Please try again.")
    
    def run_emp_hardening(self):
        """Interface for EMP Hardening Module"""
        print("\n⚡ EMP/SOLAR FLARE HARDENING MODULE v2.0")
        print("=" * 50)
        
        while True:
            print("\n1. Assess EMP Vulnerability")
            print("2. Design Faraday Cage")
            print("3. Create Manual Systems Plan")
            print("4. Setup Grid-Independent Utilities")
            print("5. Create Hardened Communications")
            print("6. Develop EMP Response Plan")
            print("7. Run EMP Hardening Drill")
            print("8. Generate Comprehensive Report")
            print("0. Return to Main Menu")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                assessment = self.emp_hardening.assess_emp_vulnerability()
                print(f"\n📊 EMP Vulnerability Score: {assessment['vulnerability_score']}%")
                print(f"Protection Level: {assessment['protection_level']}")
                print(f"Protected Items: {assessment['protected_items']}")
                print(f"Vulnerable Items: {assessment['vulnerable_items']}")
                if assessment['critical_gaps']:
                    print("\n🚨 Critical Gaps:")
                    for gap in assessment['critical_gaps']:
                        print(f"  • {gap}")
            elif choice == "2":
                size = input("Cage size needed (small/medium/large): ").strip().lower() or "medium"
                budget = float(input("Budget available ($): ").strip() or "100")
                cage_design = self.emp_hardening.design_faraday_cage(size, budget)
                print(f"\n🛡️ Faraday Cage Design Created")
                print(f"Size: {cage_design['size_category']}")
                print(f"Total Cost: ${cage_design['total_cost']}")
                print(f"Effectiveness: {cage_design['effectiveness_rating']} dB")
                print(f"Materials needed: {len(cage_design['materials_list'])} items")
            elif choice == "3":
                manual_plan = self.emp_hardening.create_manual_systems_plan()
                print(f"\n🔧 Manual Systems Plan Created")
                print(f"Systems covered: {len(manual_plan['manual_systems'])}")
                print(f"Total cost estimate: ${manual_plan['total_cost_estimate']}")
            elif choice == "4":
                utility_type = input("Utility type (power/water/heating/all): ").strip().lower() or "all"
                utilities = self.emp_hardening.setup_grid_independent_utilities(utility_type)
                print(f"\n🏠 Grid-Independent Utilities Designed")
                print(f"Systems: {len(utilities['systems'])}")
                print(f"Total cost: ${utilities['total_cost']}")
            elif choice == "7":
                print("\n🎯 Starting EMP Hardening Drill...")
                drill_result = self.emp_hardening.run_emp_hardening_drill("solar_flare")
                print(f"\nDrill Performance: {drill_result['performance']}")
            elif choice == "8":
                print("\n📊 Generating Comprehensive EMP Report...")
                report = self.emp_hardening.generate_comprehensive_report()
                print(f"EMP Preparedness: {report['emp_preparedness_score']:.1f}%")
                print(f"Level: {report['preparedness_level']}")
            else:
                print("❌ Invalid option. Please try again.")
    
    def run_nuclear_safety(self):
        """Interface for Nuclear Safety Module"""
        print("\n☢️ NUCLEAR/RADIATION SAFETY MODULE v2.0")
        print("=" * 50)
        
        while True:
            print("\n1. Assess Nuclear Preparedness")
            print("2. Recommend Detection Equipment")
            print("3. Create Decontamination Protocol")
            print("4. Plan Evacuation Routes")
            print("5. Develop Medical Protocols")
            print("6. Design Radiation Shelter")
            print("7. Run Nuclear Emergency Drill")
            print("8. Generate Comprehensive Report")
            print("0. Return to Main Menu")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                distance = float(input("Distance to nearest nuclear facility (miles): ").strip() or "20")
                assessment = self.nuclear_safety.assess_nuclear_preparedness(distance)
                print(f"\n📊 Nuclear Preparedness Assessment")
                print(f"Risk Level: {assessment['risk_level']}")
                print(f"Preparedness Score: {assessment['preparedness_score']}%")
                print(f"Detection Capability: {assessment['detection_capability']}%")
                print(f"Medical Readiness: {assessment['medical_readiness']}%")
                if assessment['critical_gaps']:
                    print("\n🚨 Critical Gaps:")
                    for gap in assessment['critical_gaps']:
                        print(f"  • {gap}")
            elif choice == "2":
                budget = float(input("Equipment budget ($): ").strip() or "500")
                risk = input("Risk level (low/moderate/high): ").strip().lower() or "moderate"
                equipment = self.nuclear_safety.recommend_detection_equipment(budget, risk)
                print(f"\n🔍 Detection Equipment Recommendations")
                if equipment['primary_device']:
                    print(f"Primary: {equipment['primary_device']['name']} - ${equipment['primary_device']['cost']}")
                if equipment['secondary_device']:
                    print(f"Secondary: {equipment['secondary_device']['name']} - ${equipment['secondary_device']['cost']}")
                print(f"Total cost: ${equipment['total_cost']}")
            elif choice == "3":
                contamination_type = input("Contamination type (general/specific): ").strip() or "general"
                protocol = self.nuclear_safety.create_decontamination_protocol(contamination_type)
                print(f"\n🚿 Decontamination Protocol Created")
                print(f"Procedures: {len(protocol['procedures'])}")
                print(f"Supplies needed: {len(protocol['supplies_needed'])} items")
            elif choice == "4":
                home = input("Home address (or 'Unknown'): ").strip() or "Unknown"
                distance = float(input("Distance to nuclear facility (miles): ").strip() or "20")
                evacuation = self.nuclear_safety.plan_evacuation_routes(home, distance)
                print(f"\n🚗 Evacuation Planning Complete")
                print(f"Facility distance: {evacuation['facility_distance']} miles")
                print(f"Routes planned: {len(evacuation['routes'])}")
                print(f"Destinations: {len(evacuation['destinations'])}")
            elif choice == "6":
                shelter_type = input("Shelter type (basement/above_ground/purpose_built): ").strip() or "basement"
                budget = float(input("Budget ($): ").strip() or "1000")
                shelter = self.nuclear_safety.design_radiation_shelter(shelter_type, budget)
                print(f"\n🏠 Radiation Shelter Designed")
                print(f"Protection Factor: {shelter['protection_factor']}")
                print(f"Total Cost: ${shelter['total_cost']}")
                print(f"Capacity: {shelter['capacity']} people")
            elif choice == "7":
                print("\n🎯 Starting Nuclear Emergency Drill...")
                drill_result = self.nuclear_safety.run_nuclear_emergency_drill("power_plant_accident")
                print(f"\nDrill Performance: {drill_result['performance']}")
            elif choice == "8":
                print("\n📊 Generating Comprehensive Nuclear Report...")
                report = self.nuclear_safety.generate_comprehensive_report()
                print(f"Nuclear Preparedness: {report['nuclear_preparedness_score']}%")
                print(f"Level: {report['preparedness_level']}")
            else:
                print("❌ Invalid option. Please try again.")
    
    def run(self):
        """Main system interface"""
        print("🚨 Starting Integrated Emergency Preparedness System...")
        
        while True:
            self.show_main_menu()
            choice = input("\nSelect option: ").strip()
            
            if choice == "0":
                print("\n👋 Emergency Preparedness System shutting down. Stay safe!")
                break
            elif choice == "1":
                self.run_risk_assessment()
            elif choice == "5":
                self.manage_supplies()
            elif choice == "8":
                self.manage_contacts()
            elif choice == "11":
                self.monitor_alerts()
            elif choice == "17":
                self.engineering_solutions_interface()
            elif choice == "18":
                self.building_calculator_interface()
            elif choice == "19":
                self.step_by_step_guide_interface()
            elif choice == "20":
                self.materials_tools_calculator()
            elif choice == "21":
                self.run_drill_simulator()
            elif choice == "22":
                self.view_drill_history()
            elif choice == "23":
                self.show_visual_dashboard()
            elif choice == "24":
                self.export_dashboard()
            elif choice == "25":
                self.search_knowledge_base()
            elif choice == "26":
                self.browse_checklists()
            elif choice == "27":
                self.generate_reference_cards()
            elif choice == "28":
                self.run_cyber_attack_response()
            elif choice == "29":
                self.run_emp_hardening()
            elif choice == "30":
                self.run_nuclear_safety()
            elif choice == "31":
                report = self.generate_comprehensive_report()
                print(f"\n📊 PREPAREDNESS SCORE: {report['preparedness_score']:.1f}/100")
                for section, data in report["sections"].items():
                    print(f"  {section.title()}: {data['score']:.1f} ({data['status']})")
                if report["recommendations"]:
                    print(f"\n💡 RECOMMENDATIONS:")
                    for rec in report["recommendations"]:
                        print(f"  • {rec}")
            elif choice == "32":
                self.export_all_data()
            elif choice == "33":
                quick_ref = self.generate_quick_reference()
                print(quick_ref)
            else:
                print("❌ Invalid option. Please try again.")
            
            if choice != "0":
                input("\nPress Enter to continue...")

if __name__ == "__main__":
    system = IntegratedPreparednessSystem()
    system.run()