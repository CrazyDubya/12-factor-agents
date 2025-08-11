#!/usr/bin/env python3
"""
Deep Dive Risk Category Analysis
Detailed exploration of each major risk category for urban family
"""

from disaster_probability_matrix import DisasterProbabilityMatrix
import pandas as pd
import json

class DeepRiskAnalysis:
    def __init__(self):
        self.matrix = DisasterProbabilityMatrix()
        self.df = self.matrix.generate_matrix()
        self.df['prob_numeric'] = self.df['Annual_Probability'].astype(float)
    
    def analyze_health_risks(self):
        """Deep dive into health-related risks"""
        health_events = self.df[self.df['Category'] == 'Health'].copy()
        health_events = health_events.sort_values('prob_numeric', ascending=False)
        
        analysis = {
            'category': 'Health',
            'total_events': len(health_events),
            'cumulative_probability': health_events['prob_numeric'].sum(),
            'average_impact': health_events['Impact_Severity'].mean(),
            'key_insights': [
                "Child injuries are most likely health event (48% annual)",
                "Parent health risks increase significantly after age 40",
                "Stomach flu affects entire family unit (72% probability)",
                "Major medical events have low probability but catastrophic impact"
            ],
            'top_events': health_events.head(8)[['Event', 'Probability_Percent', 'Impact_Severity', 'Family_Disruption']].to_dict('records'),
            'preparation_strategies': [
                "Establish relationships with pediatrician, family doctor, specialists",
                "Maintain comprehensive health insurance with low deductibles",
                "Build health emergency fund for deductibles/co-pays",
                "Keep updated medical records and medication lists",
                "Learn basic first aid and CPR",
                "Create medical emergency action plan",
                "Identify 24/7 urgent care and hospital locations",
                "Maintain healthy lifestyle to prevent chronic conditions"
            ],
            'cost_factors': {
                'minor_events': '$100-500 per incident',
                'major_events': '$5,000-50,000+ per incident',
                'insurance_premiums': '$800-1,500/month for family',
                'preventive_care': '$2,000-3,000/year'
            }
        }
        return analysis
    
    def analyze_security_risks(self):
        """Deep dive into security-related risks"""
        security_events = self.df[self.df['Category'] == 'Security'].copy()
        security_events = security_events.sort_values('prob_numeric', ascending=False)
        
        analysis = {
            'category': 'Security',
            'total_events': len(security_events),
            'cumulative_probability': security_events['prob_numeric'].sum(),
            'average_impact': security_events['Impact_Severity'].mean(),
            'urban_factor_impact': 'Security risks 1.6-2.0x higher in urban areas',
            'key_insights': [
                "Burglary attempts most common (15.8% annual in urban areas)",
                "Home break-ins during short absences (8.8% probability)",
                "Identity theft growing concern (6.6% probability)",
                "Catastrophic events rare but require different preparation"
            ],
            'top_events': security_events[['Event', 'Probability_Percent', 'Impact_Severity', 'Urban_Factor']].to_dict('records'),
            'preparation_strategies': [
                "Install comprehensive home security system",
                "Use smart locks and security cameras",
                "Establish neighborhood watch participation",
                "Teach child basic safety protocols",
                "Secure important documents in fireproof safe",
                "Use identity monitoring services",
                "Maintain situational awareness in public",
                "Create family safety communication plan"
            ],
            'layered_security_approach': {
                'deterrence': 'Visible security measures, lighting, landscaping',
                'detection': 'Alarms, cameras, motion sensors',
                'delay': 'Reinforced doors, window locks, safe rooms',
                'response': 'Police contact, neighbor network, escape routes'
            }
        }
        return analysis
    
    def analyze_economic_risks(self):
        """Deep dive into economic-related risks"""
        economic_events = self.df[self.df['Category'] == 'Economic'].copy()
        economic_events = economic_events.sort_values('prob_numeric', ascending=False)
        
        analysis = {
            'category': 'Economic',
            'total_events': len(economic_events),
            'cumulative_probability': economic_events['prob_numeric'].sum(),
            'average_impact': economic_events['Impact_Severity'].mean(),
            'key_insights': [
                "Financial strain affects 25% of families annually",
                "Temporary job loss probability: 15% per year",
                "Economic recessions occur every 7-10 years (15% annual probability)",
                "Extended unemployment can devastate family finances"
            ],
            'top_events': economic_events[['Event', 'Probability_Percent', 'Impact_Severity', 'Family_Disruption']].to_dict('records'),
            'preparation_strategies': [
                "Build 6-month emergency fund minimum",
                "Diversify income sources when possible",
                "Maintain marketable skills and certifications",
                "Consider disability insurance for both parents",
                "Optimize tax strategies and retirement savings",
                "Reduce fixed expenses and debt",
                "Build professional network and references",
                "Create multiple revenue streams if feasible"
            ],
            'financial_resilience_metrics': {
                'emergency_fund_target': '6 months expenses ($30,000-40,000)',
                'debt_to_income_ratio': 'Keep below 36%',
                'insurance_coverage': '10x annual income life insurance',
                'retirement_savings': '15-20% of gross income'
            }
        }
        return analysis
    
    def analyze_infrastructure_risks(self):
        """Deep dive into infrastructure-related risks"""
        infra_events = self.df[self.df['Category'] == 'Infrastructure'].copy()
        infra_events = infra_events.sort_values('prob_numeric', ascending=False)
        
        analysis = {
            'category': 'Infrastructure',
            'total_events': len(infra_events),
            'cumulative_probability': infra_events['prob_numeric'].sum(),
            'average_impact': infra_events['Impact_Severity'].mean(),
            'urban_dependency': 'Higher complexity = higher failure rates',
            'key_insights': [
                "Power outages virtually guaranteed annually (100%)",
                "Water and utility disruptions common (20-50%)",
                "Urban infrastructure more complex but better maintained",
                "Cascading failures can multiply impact"
            ],
            'top_events': infra_events[['Event', 'Probability_Percent', 'Impact_Severity', 'Urban_Factor']].to_dict('records'),
            'preparation_strategies': [
                "Install backup power system (generator or batteries)",
                "Maintain water storage (1 gallon/person/day minimum)",
                "Keep non-perishable food supplies",
                "Learn location of utility shutoffs",
                "Maintain battery-powered communication devices",
                "Create manual alternatives for electric-dependent activities",
                "Build relationships with reliable contractors",
                "Understand local utility emergency procedures"
            ],
            'backup_systems': {
                'power': 'Generator, battery banks, solar panels',
                'water': 'Storage tanks, filtration systems, rainwater collection',
                'heating': 'Alternative heat sources, extra insulation',
                'communication': 'Battery radios, satellite communicators'
            }
        }
        return analysis
    
    def analyze_weather_risks(self):
        """Deep dive into weather-related risks"""
        weather_events = self.df[self.df['Category'] == 'Weather'].copy()
        weather_events = weather_events.sort_values('prob_numeric', ascending=False)
        
        analysis = {
            'category': 'Weather',
            'total_events': len(weather_events),
            'cumulative_probability': weather_events['prob_numeric'].sum(),
            'average_impact': weather_events['Impact_Severity'].mean(),
            'climate_trends': 'Increasing frequency and intensity of extreme weather',
            'key_insights': [
                "Severe thunderstorms most common (45% annual)",
                "Flash floods significant urban risk (14% probability)",
                "Tornadoes rare but devastating (1.6% probability)",
                "Urban heat island effect increases some risks"
            ],
            'top_events': weather_events[['Event', 'Probability_Percent', 'Impact_Severity', 'Duration']].to_dict('records'),
            'preparation_strategies': [
                "Monitor weather alerts and warnings",
                "Identify safe rooms for severe weather",
                "Maintain emergency supplies for 72+ hours",
                "Understand local evacuation routes",
                "Weatherproof home exterior",
                "Trim trees and secure outdoor items",
                "Install storm shutters or reinforced windows",
                "Create family severe weather plan"
            ],
            'seasonal_considerations': {
                'spring': 'Tornado season, flooding from snowmelt',
                'summer': 'Severe thunderstorms, heat waves, hurricanes',
                'fall': 'Hurricane season, early winter storms',
                'winter': 'Blizzards, ice storms, extreme cold'
            }
        }
        return analysis
    
    def generate_comprehensive_report(self):
        """Generate complete deep dive analysis"""
        categories = {
            'Health': self.analyze_health_risks(),
            'Security': self.analyze_security_risks(),
            'Economic': self.analyze_economic_risks(),
            'Infrastructure': self.analyze_infrastructure_risks(),
            'Weather': self.analyze_weather_risks()
        }
        
        return categories

def main():
    analyzer = DeepRiskAnalysis()
    comprehensive_analysis = analyzer.generate_comprehensive_report()
    
    print("DEEP DIVE RISK CATEGORY ANALYSIS")
    print("=" * 80)
    print("Urban Family Risk Assessment - Detailed Category Breakdown\n")
    
    for category_name, analysis in comprehensive_analysis.items():
        print(f"\n{'='*20} {category_name.upper()} RISKS {'='*20}")
        print(f"Total Events: {analysis['total_events']}")
        print(f"Cumulative Annual Probability: {analysis['cumulative_probability']:.2f}")
        print(f"Average Impact Severity: {analysis['average_impact']:.1f}/10")
        
        print(f"\nKey Insights:")
        for insight in analysis['key_insights']:
            print(f"  • {insight}")
        
        print(f"\nTop Events:")
        for i, event in enumerate(analysis['top_events'][:5], 1):
            print(f"  {i}. {event['Event']}: {event['Probability_Percent']} (Impact: {event['Impact_Severity']}/10)")
        
        print(f"\nPreparation Strategies:")
        for strategy in analysis['preparation_strategies'][:6]:
            print(f"  ✓ {strategy}")
        
        if len(analysis['preparation_strategies']) > 6:
            print(f"  ... and {len(analysis['preparation_strategies']) - 6} more strategies")
    
    # Save detailed analysis
    with open('deep_dive_analysis.json', 'w') as f:
        json.dump(comprehensive_analysis, f, indent=2, default=str)
    
    print(f"\n\nDetailed analysis saved to: deep_dive_analysis.json")
    return comprehensive_analysis

if __name__ == "__main__":
    main()