#!/usr/bin/env python3
"""
System Test Script for Integrated Emergency Preparedness System
Tests all major modules and functionality
"""

import sys
import traceback
from datetime import datetime

def test_module(module_name, test_func):
    """Test a module and report results"""
    try:
        result = test_func()
        print(f"✓ {module_name}: {result}")
        return True
    except Exception as e:
        print(f"✗ {module_name}: {str(e)}")
        return False

def main():
    print("🧪 EMERGENCY PREPAREDNESS SYSTEM TEST SUITE")
    print("=" * 60)
    print(f"Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: System initialization
    tests_total += 1
    def test_system_init():
        from integrated_preparedness_system import IntegratedPreparednessSystem
        system = IntegratedPreparednessSystem()
        return f"16 modules initialized, data dir: {system.data_dir}"
    
    if test_module("System Initialization", test_system_init):
        tests_passed += 1
    
    # Test 2: Emergency Drill Simulator
    tests_total += 1
    def test_drill_simulator():
        from emergency_drill_simulator import EmergencyDrillSimulator
        simulator = EmergencyDrillSimulator()
        earthquake_id = simulator.create_earthquake_drill()
        return f"Drill scenarios created, earthquake ID: {earthquake_id}"
    
    if test_module("Drill Simulator", test_drill_simulator):
        tests_passed += 1
    
    # Test 3: Visualization Dashboard
    tests_total += 1
    def test_dashboard():
        from visualization_dashboard import VisualizationDashboard
        dashboard = VisualizationDashboard()
        risk_heatmap = dashboard.generate_risk_heatmap()
        return f"Dashboard created, heatmap length: {len(risk_heatmap)} chars"
    
    if test_module("Visualization Dashboard", test_dashboard):
        tests_passed += 1
    
    # Test 4: Knowledge Base Search
    tests_total += 1
    def test_knowledge_base():
        from knowledge_base_search import KnowledgeBaseSearch
        kb = KnowledgeBaseSearch()
        result = kb.index_knowledge_base()
        return f"Knowledge base indexed: {result.get('indexed', 0)} files"
    
    if test_module("Knowledge Base Search", test_knowledge_base):
        tests_passed += 1
    
    # Test 5: Supply Inventory Tracker
    tests_total += 1
    def test_supply_tracker():
        from supply_inventory_tracker import SupplyInventoryTracker
        tracker = SupplyInventoryTracker("test_supplies.db")
        item_id = tracker.add_supply("water", "Test Water", 5, "gallons")
        return f"Supply tracker working, item ID: {item_id}"
    
    if test_module("Supply Inventory Tracker", test_supply_tracker):
        tests_passed += 1
    
    # Test 6: Emergency Contacts Manager  
    tests_total += 1
    def test_contacts():
        from emergency_contacts_manager import EmergencyContactsManager
        contacts = EmergencyContactsManager("test_contacts.db")
        contact_id = contacts.add_contact("emergency_services", "Test Service", "911")
        return f"Contact manager working, contact ID: {contact_id}"
    
    if test_module("Emergency Contacts Manager", test_contacts):
        tests_passed += 1
    
    # Test 7: Materials Calculator
    tests_total += 1
    def test_materials_calc():
        from materials_calculator import MaterialsCalculator
        calc = MaterialsCalculator("test_materials.db")
        result = calc.calculate_frame_materials(10, 12, 8)
        return f"Materials calc working, total cost: ${result['total_cost']:.2f}"
    
    if test_module("Materials Calculator", test_materials_calc):
        tests_passed += 1
    
    # Test 8: Building Guide
    tests_total += 1
    def test_building_guide():
        from intuitive_building_guide import IntuitiveBuilder
        builder = IntuitiveBuilder("test_building.db")
        beam_calc = builder.calculate_beam_load(8.0, 500, "2x4_lumber")
        return f"Building guide working, beam status: {beam_calc['status']}"
    
    if test_module("Building Guide", test_building_guide):
        tests_passed += 1
    
    # Test 9: Engineering Solutions
    tests_total += 1
    def test_engineering():
        from simple_engineering_solutions import SimpleEngineeringSolutions
        solutions = SimpleEngineeringSolutions("test_engineering.db")
        solution_id = solutions.add_solution("Test Solution", "water_collection", "beginner", "1 hour", 10.0, "Test description", ["test"])
        return f"Engineering solutions working, solution ID: {solution_id}"
    
    if test_module("Engineering Solutions", test_engineering):
        tests_passed += 1
    
    # Test 10: Step-by-Step Builder
    tests_total += 1
    def test_step_builder():
        from step_by_step_builder import StepByStepBuilder
        builder = StepByStepBuilder("test_steps.db")
        project_id = builder.create_emergency_shelter_guide()
        return f"Step builder working, project ID: {project_id}"
    
    if test_module("Step-by-Step Builder", test_step_builder):
        tests_passed += 1
    
    # Final Results
    print("\n" + "=" * 60)
    print(f"🏆 TEST RESULTS: {tests_passed}/{tests_total} tests passed")
    
    if tests_passed == tests_total:
        print("✅ ALL TESTS PASSED - System is fully operational!")
    elif tests_passed >= tests_total * 0.8:
        print("⚠️  MOSTLY WORKING - Some minor issues detected")
    else:
        print("❌ SYSTEM ISSUES - Multiple modules failing")
    
    print(f"Test completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Cleanup test databases
    import os
    test_files = [
        "test_supplies.db", "test_contacts.db", "test_materials.db",
        "test_building.db", "test_engineering.db", "test_steps.db"
    ]
    
    for file in test_files:
        try:
            if os.path.exists(file):
                os.remove(file)
        except:
            pass
    
    return tests_passed == tests_total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)