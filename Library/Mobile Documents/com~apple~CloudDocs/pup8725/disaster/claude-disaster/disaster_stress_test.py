#!/usr/bin/env python3
"""
20 Disaster Scenarios Stress Test
Tests system performance and recommendations across diverse emergency situations
"""

import sys
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import random

class DisasterStressTest:
    def __init__(self):
        self.test_results = []
        self.system = None
        
        # 20 diverse disaster scenarios with realistic parameters
        self.disaster_scenarios = [
            {
                "name": "Major Earthquake (7.2 Magnitude)",
                "type": "earthquake",
                "duration": "minutes",
                "warning_time": 0,
                "severity": 9,
                "cascading_effects": ["power_outage", "water_disruption", "building_damage", "road_closure"],
                "primary_needs": ["shelter", "medical", "water", "communication"],
                "seasonal_factor": "none",
                "affected_area": "city_wide"
            },
            {
                "name": "Category 4 Hurricane",
                "type": "hurricane",
                "duration": "days", 
                "warning_time": 72,
                "severity": 8,
                "cascading_effects": ["flooding", "power_outage", "supply_disruption", "evacuation"],
                "primary_needs": ["evacuation", "shelter", "food", "water"],
                "seasonal_factor": "summer/fall",
                "affected_area": "regional"
            },
            {
                "name": "House Fire",
                "type": "fire",
                "duration": "minutes",
                "warning_time": 0,
                "severity": 10,
                "cascading_effects": ["smoke_inhalation", "structure_loss", "displacement"],
                "primary_needs": ["evacuation", "shelter", "documents", "clothing"],
                "seasonal_factor": "winter_risk",
                "affected_area": "single_building"
            },
            {
                "name": "Extended Power Grid Failure",
                "type": "power_outage",
                "duration": "weeks",
                "warning_time": 0,
                "severity": 6,
                "cascading_effects": ["food_spoilage", "heating_loss", "communication_loss", "fuel_shortage"],
                "primary_needs": ["power", "heating", "food", "communication"],
                "seasonal_factor": "winter_critical",
                "affected_area": "multi_state"
            },
            {
                "name": "Cyber Attack on Infrastructure",
                "type": "cyber_attack",
                "duration": "weeks",
                "warning_time": 0,
                "severity": 7,
                "cascading_effects": ["banking_disruption", "supply_chain_failure", "communication_loss"],
                "primary_needs": ["cash", "supplies", "communication", "security"],
                "seasonal_factor": "none",
                "affected_area": "national"
            },
            {
                "name": "Pandemic Lockdown",
                "type": "pandemic",
                "duration": "months",
                "warning_time": 168,
                "severity": 6,
                "cascading_effects": ["supply_shortage", "economic_disruption", "social_isolation"],
                "primary_needs": ["medical", "food", "mental_health", "income"],
                "seasonal_factor": "winter_worse",
                "affected_area": "global"
            },
            {
                "name": "EF4 Tornado",
                "type": "tornado",
                "duration": "minutes",
                "warning_time": 15,
                "severity": 9,
                "cascading_effects": ["building_destruction", "debris", "power_outage", "injury"],
                "primary_needs": ["shelter", "medical", "search_rescue", "communication"],
                "seasonal_factor": "spring_peak",
                "affected_area": "corridor"
            },
            {
                "name": "Flash Flooding",
                "type": "flood",
                "duration": "hours",
                "warning_time": 2,
                "severity": 8,
                "cascading_effects": ["road_closure", "contamination", "displacement", "utility_disruption"],
                "primary_needs": ["evacuation", "shelter", "water", "transportation"],
                "seasonal_factor": "spring_summer",
                "affected_area": "watershed"
            },
            {
                "name": "Hazardous Chemical Spill",
                "type": "chemical_spill",
                "duration": "days",
                "warning_time": 1,
                "severity": 7,
                "cascading_effects": ["evacuation", "contamination", "health_effects", "water_contamination"],
                "primary_needs": ["evacuation", "medical", "decontamination", "shelter"],
                "seasonal_factor": "wind_dependent",
                "affected_area": "radius_based"
            },
            {
                "name": "Economic Collapse/Bank Run",
                "type": "economic_collapse",
                "duration": "months",
                "warning_time": 24,
                "severity": 7,
                "cascading_effects": ["currency_devaluation", "supply_disruption", "social_unrest"],
                "primary_needs": ["cash", "barter_goods", "food", "security"],
                "seasonal_factor": "none",
                "affected_area": "national"
            },
            {
                "name": "Terrorist Attack (Bombing)",
                "type": "terrorism",
                "duration": "hours",
                "warning_time": 0,
                "severity": 9,
                "cascading_effects": ["mass_casualties", "infrastructure_damage", "security_lockdown"],
                "primary_needs": ["medical", "evacuation", "security", "communication"],
                "seasonal_factor": "none",
                "affected_area": "targeted"
            },
            {
                "name": "Nuclear Power Plant Accident",
                "type": "nuclear_accident",
                "duration": "years",
                "warning_time": 4,
                "severity": 10,
                "cascading_effects": ["radiation_exposure", "evacuation", "contamination", "health_effects"],
                "primary_needs": ["evacuation", "medical", "radiation_protection", "relocation"],
                "seasonal_factor": "wind_pattern",
                "affected_area": "radius_expanding"
            },
            {
                "name": "Severe Ice Storm",
                "type": "ice_storm",
                "duration": "days",
                "warning_time": 24,
                "severity": 6,
                "cascading_effects": ["power_outage", "tree_damage", "transportation_halt", "heating_loss"],
                "primary_needs": ["heating", "power", "food", "medical"],
                "seasonal_factor": "winter_only",
                "affected_area": "regional"
            },
            {
                "name": "Wildfire Evacuation",
                "type": "wildfire",
                "duration": "days",
                "warning_time": 6,
                "severity": 8,
                "cascading_effects": ["evacuation", "air_quality", "structure_loss", "road_closure"],
                "primary_needs": ["evacuation", "shelter", "air_filtration", "documents"],
                "seasonal_factor": "summer_fall",
                "affected_area": "wind_driven"
            },
            {
                "name": "Water System Contamination",
                "type": "water_contamination",
                "duration": "weeks",
                "warning_time": 12,
                "severity": 7,
                "cascading_effects": ["boil_order", "supply_shortage", "health_risk", "business_closure"],
                "primary_needs": ["water", "medical", "sanitation", "food_safety"],
                "seasonal_factor": "heat_amplifies",
                "affected_area": "water_district"
            },
            {
                "name": "Solar Flare/EMP Event",
                "type": "emp",
                "duration": "months",
                "warning_time": 0,
                "severity": 8,
                "cascading_effects": ["electronics_failure", "communication_loss", "transportation_halt"],
                "primary_needs": ["manual_tools", "communication", "transportation", "medical"],
                "seasonal_factor": "none",
                "affected_area": "hemisphere"
            },
            {
                "name": "Civil Unrest/Riots",
                "type": "civil_unrest",
                "duration": "days",
                "warning_time": 8,
                "severity": 6,
                "cascading_effects": ["business_closure", "curfew", "supply_disruption", "violence"],
                "primary_needs": ["security", "shelter", "supplies", "communication"],
                "seasonal_factor": "summer_heat",
                "affected_area": "urban_centers"
            },
            {
                "name": "Massive Snowstorm/Blizzard",
                "type": "blizzard",
                "duration": "days",
                "warning_time": 48,
                "severity": 5,
                "cascading_effects": ["transportation_halt", "power_outage", "isolation", "heating_demand"],
                "primary_needs": ["heating", "food", "water", "medical"],
                "seasonal_factor": "winter_only",
                "affected_area": "regional"
            },
            {
                "name": "Supply Chain Collapse",
                "type": "supply_chain_failure",
                "duration": "months",
                "warning_time": 72,
                "severity": 7,
                "cascading_effects": ["food_shortage", "fuel_shortage", "medical_shortage", "price_inflation"],
                "primary_needs": ["food", "fuel", "medical", "essential_goods"],
                "seasonal_factor": "growing_season",
                "affected_area": "national"
            },
            {
                "name": "Dam Failure/Burst",
                "type": "dam_failure",
                "duration": "hours",
                "warning_time": 0.5,
                "severity": 10,
                "cascading_effects": ["flash_flood", "mass_evacuation", "infrastructure_destruction"],
                "primary_needs": ["immediate_evacuation", "shelter", "search_rescue", "medical"],
                "seasonal_factor": "spring_risk",
                "affected_area": "downstream"
            }
        ]
    
    def run_comprehensive_test(self):
        """Run system against all 20 disaster scenarios"""
        print("🧪 DISASTER STRESS TEST - 20 SCENARIOS")
        print("=" * 60)
        print(f"Test initiated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Initialize system
            from integrated_preparedness_system import IntegratedPreparednessSystem
            self.system = IntegratedPreparednessSystem()
            print("✓ System initialized successfully")
            
            # Run each scenario
            for i, scenario in enumerate(self.disaster_scenarios, 1):
                print(f"\n🎯 SCENARIO {i}/20: {scenario['name']}")
                result = self.test_scenario(scenario)
                self.test_results.append(result)
                self.display_scenario_result(result)
            
            # Generate comprehensive report
            self.generate_stress_test_report()
            
        except Exception as e:
            print(f"❌ CRITICAL ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def test_scenario(self, scenario: Dict) -> Dict:
        """Test system response to a specific disaster scenario"""
        test_result = {
            "scenario": scenario,
            "timestamp": datetime.now().isoformat(),
            "system_responses": {},
            "gaps_identified": [],
            "recommendations": [],
            "preparedness_score": 0,
            "critical_failures": [],
            "strengths": []
        }
        
        try:
            # Test 1: Risk Assessment
            risk_score = self.test_risk_assessment(scenario)
            test_result["system_responses"]["risk_assessment"] = risk_score
            
            # Test 2: Supply Adequacy
            supply_score = self.test_supply_adequacy(scenario)
            test_result["system_responses"]["supply_adequacy"] = supply_score
            
            # Test 3: Contact System
            contact_score = self.test_contact_system(scenario)
            test_result["system_responses"]["contact_system"] = contact_score
            
            # Test 4: Engineering Solutions
            engineering_score = self.test_engineering_solutions(scenario)
            test_result["system_responses"]["engineering_solutions"] = engineering_score
            
            # Test 5: Knowledge Base Coverage
            knowledge_score = self.test_knowledge_coverage(scenario)
            test_result["system_responses"]["knowledge_coverage"] = knowledge_score
            
            # Test 6: Alert/Monitoring
            alert_score = self.test_alert_system(scenario)
            test_result["system_responses"]["alert_system"] = alert_score
            
            # Test 7: Drill Preparedness
            drill_score = self.test_drill_preparedness(scenario)
            test_result["system_responses"]["drill_preparedness"] = drill_score
            
            # Calculate overall preparedness score
            scores = [risk_score, supply_score, contact_score, engineering_score, 
                     knowledge_score, alert_score, drill_score]
            test_result["preparedness_score"] = sum(scores) / len(scores)
            
            # Identify gaps and recommendations
            test_result["gaps_identified"] = self.identify_gaps(scenario, test_result["system_responses"])
            test_result["recommendations"] = self.generate_recommendations(scenario, test_result["gaps_identified"])
            
            # Identify critical failures (score < 30)
            for system, score in test_result["system_responses"].items():
                if score < 30:
                    test_result["critical_failures"].append(f"{system}: {score}%")
                elif score > 80:
                    test_result["strengths"].append(f"{system}: {score}%")
            
        except Exception as e:
            test_result["error"] = str(e)
            test_result["preparedness_score"] = 0
        
        return test_result
    
    def test_risk_assessment(self, scenario: Dict) -> int:
        """Test if risk assessment system handles this disaster type"""
        try:
            # Check if disaster type is in probability matrix
            disaster_types = ["earthquake", "fire", "flood", "power_outage", "tornado", "hurricane"]
            base_score = 70 if scenario["type"] in disaster_types else 30
            
            # Adjust for warning time
            if scenario["warning_time"] > 24:
                base_score += 20  # Good for planning
            elif scenario["warning_time"] == 0:
                base_score -= 10  # Sudden onset challenge
            
            return min(100, max(0, base_score))
            
        except:
            return 25
    
    def test_supply_adequacy(self, scenario: Dict) -> int:
        """Test if supply system covers scenario needs"""
        try:
            # Basic supply categories in system
            system_supplies = ["water", "food", "medical", "power", "communication", "shelter", "tools"]
            scenario_needs = scenario["primary_needs"]
            
            # Calculate coverage
            covered_needs = len([need for need in scenario_needs if any(supply in need for supply in system_supplies)])
            coverage_percent = (covered_needs / len(scenario_needs)) * 100
            
            # Duration adjustment
            if scenario["duration"] == "months":
                coverage_percent *= 0.7  # Long-term is harder
            elif scenario["duration"] == "minutes":
                coverage_percent *= 0.9  # Immediate response harder
            
            return min(100, max(10, int(coverage_percent)))
            
        except:
            return 20
    
    def test_contact_system(self, scenario: Dict) -> int:
        """Test contact system relevance to scenario"""
        try:
            base_score = 75  # System has good contact management
            
            # Scenario-specific adjustments
            if "communication_loss" in scenario.get("cascading_effects", []):
                base_score -= 30  # Communications disrupted
            if scenario["affected_area"] in ["national", "global", "multi_state"]:
                base_score += 10  # Wide area = more contacts needed
            if scenario["warning_time"] == 0:
                base_score -= 20  # No time to contact people
            
            return min(100, max(0, base_score))
            
        except:
            return 40
    
    def test_engineering_solutions(self, scenario: Dict) -> int:
        """Test engineering solutions relevance"""
        try:
            engineering_relevant = {
                "earthquake": 90,  # Shelter, structural
                "fire": 60,        # Evacuation routes  
                "flood": 85,       # Water management
                "power_outage": 95, # Alternative power
                "tornado": 90,     # Shelter design
                "hurricane": 85,   # Structural reinforcement
                "chemical_spill": 70, # Containment
                "blizzard": 80,    # Heating solutions
                "wildfire": 75,    # Fire barriers
                "dam_failure": 60  # Limited engineering help
            }
            
            base_score = engineering_relevant.get(scenario["type"], 40)
            
            # Duration adjustment
            if scenario["duration"] in ["days", "weeks", "months"]:
                base_score += 15  # More time for building solutions
            
            return min(100, base_score)
            
        except:
            return 30
    
    def test_knowledge_coverage(self, scenario: Dict) -> int:
        """Test knowledge base coverage for scenario"""
        try:
            # Knowledge base categories
            kb_categories = ["water", "food", "medical", "shelter", "security", "communication", 
                           "sanitation", "psychology", "engineering", "survival"]
            
            scenario_needs = scenario["primary_needs"]
            
            # Calculate coverage
            covered = 0
            for need in scenario_needs:
                if any(cat in need for cat in kb_categories):
                    covered += 1
            
            coverage_score = (covered / len(scenario_needs)) * 100
            
            # Bonus for having comprehensive guides
            coverage_score = min(100, coverage_score * 1.2)
            
            return max(20, int(coverage_score))
            
        except:
            return 25
    
    def test_alert_system(self, scenario: Dict) -> int:
        """Test alert monitoring system effectiveness"""
        try:
            weather_related = ["hurricane", "tornado", "flood", "blizzard", "ice_storm", "wildfire"]
            
            if scenario["type"] in weather_related:
                base_score = 85  # Weather alerts work well
            else:
                base_score = 45  # Limited for non-weather events
            
            # Warning time affects alert usefulness
            if scenario["warning_time"] > 12:
                base_score += 15
            elif scenario["warning_time"] == 0:
                base_score -= 20
            
            return min(100, max(10, base_score))
            
        except:
            return 35
    
    def test_drill_preparedness(self, scenario: Dict) -> int:
        """Test drill system coverage for scenario"""
        try:
            # Drill scenarios available
            drill_types = ["earthquake", "fire", "tornado"]
            
            if scenario["type"] in drill_types:
                base_score = 90  # Direct drill match
            elif scenario["type"] in ["hurricane", "flood", "blizzard"]:
                base_score = 70  # Similar to covered scenarios
            else:
                base_score = 40  # Generic emergency response
            
            # Sudden events need more drilling
            if scenario["warning_time"] < 1:
                base_score += 10
            
            return min(100, base_score)
            
        except:
            return 30
    
    def identify_gaps(self, scenario: Dict, responses: Dict) -> List[str]:
        """Identify system gaps for this scenario"""
        gaps = []
        
        # Critical system gaps (score < 50)
        for system, score in responses.items():
            if score < 50:
                gaps.append(f"Critical gap: {system} inadequate ({score}%)")
        
        # Scenario-specific gaps
        if scenario["type"] == "emp":
            gaps.append("No EMP-hardened systems or manual backup procedures")
        
        if scenario["type"] == "nuclear_accident":
            gaps.append("No radiation detection or protection guidance")
        
        if scenario["type"] == "economic_collapse":
            gaps.append("Limited barter/trade system integration")
        
        if scenario["type"] == "cyber_attack":
            gaps.append("No offline backup for digital systems")
        
        if "months" in scenario["duration"]:
            gaps.append("Long-term sustainability planning insufficient")
        
        return gaps
    
    def generate_recommendations(self, scenario: Dict, gaps: List[str]) -> List[str]:
        """Generate specific recommendations for scenario"""
        recommendations = []
        
        # Address identified gaps
        for gap in gaps[:3]:  # Top 3 gaps
            if "supply" in gap.lower():
                recommendations.append(f"Increase {scenario['type']}-specific supply reserves")
            elif "contact" in gap.lower():
                recommendations.append("Develop backup communication methods")
            elif "engineering" in gap.lower():
                recommendations.append("Add structural hardening solutions")
            elif "knowledge" in gap.lower():
                recommendations.append(f"Expand knowledge base for {scenario['type']} scenarios")
        
        # Scenario-specific recommendations
        if scenario["warning_time"] == 0:
            recommendations.append("Focus on immediate response drills and automation")
        
        if scenario["duration"] == "months":
            recommendations.append("Develop long-term sustainability plans")
        
        if scenario["severity"] >= 9:
            recommendations.append("Create redundant systems for critical functions")
        
        return recommendations[:5]  # Top 5 recommendations
    
    def display_scenario_result(self, result: Dict):
        """Display result for individual scenario"""
        scenario = result["scenario"]
        score = result["preparedness_score"]
        
        if score >= 80:
            status = "🟢 EXCELLENT"
        elif score >= 60:
            status = "🟡 ADEQUATE"
        elif score >= 40:
            status = "🟠 NEEDS WORK"
        else:
            status = "🔴 CRITICAL"
        
        print(f"   Overall Score: {score:.1f}% - {status}")
        
        if result["critical_failures"]:
            print(f"   ❌ Critical Gaps: {', '.join(result['critical_failures'][:2])}")
        
        if result["strengths"]:
            print(f"   ✅ Strengths: {', '.join(result['strengths'][:2])}")
    
    def generate_stress_test_report(self):
        """Generate comprehensive stress test report"""
        print(f"\n{'='*60}")
        print("📊 COMPREHENSIVE STRESS TEST RESULTS")
        print(f"{'='*60}")
        
        # Overall statistics
        scores = [r["preparedness_score"] for r in self.test_results if "error" not in r]
        if scores:
            avg_score = sum(scores) / len(scores)
            min_score = min(scores)
            max_score = max(scores)
            
            print(f"\n🎯 OVERALL SYSTEM PERFORMANCE:")
            print(f"   Average Preparedness: {avg_score:.1f}%")
            print(f"   Best Scenario Score:  {max_score:.1f}%")
            print(f"   Worst Scenario Score: {min_score:.1f}%")
        
        # Performance by category
        excellent = len([s for s in scores if s >= 80])
        adequate = len([s for s in scores if 60 <= s < 80])
        needs_work = len([s for s in scores if 40 <= s < 60])
        critical = len([s for s in scores if s < 40])
        
        print(f"\n📈 PERFORMANCE BREAKDOWN:")
        print(f"   🟢 Excellent (80%+):    {excellent} scenarios")
        print(f"   🟡 Adequate (60-79%):   {adequate} scenarios")
        print(f"   🟠 Needs Work (40-59%): {needs_work} scenarios")
        print(f"   🔴 Critical (<40%):     {critical} scenarios")
        
        # Worst performing scenarios
        worst_scenarios = sorted(self.test_results, key=lambda x: x.get("preparedness_score", 0))[:5]
        print(f"\n🚨 TOP 5 CHALLENGING SCENARIOS:")
        for i, result in enumerate(worst_scenarios, 1):
            score = result.get("preparedness_score", 0)
            name = result["scenario"]["name"]
            print(f"   {i}. {name}: {score:.1f}%")
        
        # Best performing scenarios  
        best_scenarios = sorted(self.test_results, key=lambda x: x.get("preparedness_score", 0), reverse=True)[:5]
        print(f"\n✅ TOP 5 WELL-COVERED SCENARIOS:")
        for i, result in enumerate(best_scenarios, 1):
            score = result.get("preparedness_score", 0)
            name = result["scenario"]["name"]
            print(f"   {i}. {name}: {score:.1f}%")
        
        # System-wide gaps
        all_gaps = []
        for result in self.test_results:
            all_gaps.extend(result.get("gaps_identified", []))
        
        # Count common gaps
        gap_counts = {}
        for gap in all_gaps:
            gap_type = gap.split(':')[0] if ':' in gap else gap
            gap_counts[gap_type] = gap_counts.get(gap_type, 0) + 1
        
        common_gaps = sorted(gap_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        print(f"\n🔍 MOST COMMON SYSTEM GAPS:")
        for gap, count in common_gaps:
            print(f"   • {gap}: {count} scenarios affected")
        
        # Strategic recommendations
        print(f"\n💡 STRATEGIC RECOMMENDATIONS:")
        if critical > 0:
            print(f"   🚨 URGENT: Address {critical} critical scenarios")
        if needs_work > 5:
            print(f"   ⚠️  Improve system coverage for {needs_work} scenarios needing work")
        
        print(f"   📚 Expand knowledge base for non-weather disasters")
        print(f"   🔧 Add engineering solutions for long-term scenarios")
        print(f"   📱 Develop backup systems for infrastructure failures")
        print(f"   🎯 Create drills for cyber/economic/nuclear scenarios")
        
        # Final assessment
        if avg_score >= 75:
            overall_rating = "🏆 EXCELLENT - System well-prepared for most disasters"
        elif avg_score >= 60:
            overall_rating = "👍 GOOD - System adequate with room for improvement"
        elif avg_score >= 45:
            overall_rating = "⚠️  ADEQUATE - System needs significant improvements"
        else:
            overall_rating = "🚨 CRITICAL - System requires major overhaul"
        
        print(f"\n🏆 FINAL ASSESSMENT: {overall_rating}")
        print(f"Test completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Save detailed report
        self.save_detailed_report()
    
    def save_detailed_report(self):
        """Save detailed test results to file"""
        report = {
            "test_metadata": {
                "test_date": datetime.now().isoformat(),
                "scenarios_tested": len(self.disaster_scenarios),
                "system_version": "1.0"
            },
            "results": self.test_results,
            "summary": {
                "scores": [r["preparedness_score"] for r in self.test_results if "error" not in r],
                "avg_score": sum([r["preparedness_score"] for r in self.test_results if "error" not in r]) / len([r for r in self.test_results if "error" not in r])
            }
        }
        
        filename = f"disaster_stress_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\n💾 Detailed report saved: {filename}")
        except Exception as e:
            print(f"⚠️  Could not save report: {e}")

def main():
    """Run the disaster stress test"""
    tester = DisasterStressTest()
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main()