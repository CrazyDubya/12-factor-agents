#!/usr/bin/env python3
"""
Risk Visualization and Analysis Tools
Creates charts and additional insights for the disaster probability matrix
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from disaster_probability_matrix import DisasterProbabilityMatrix

def create_risk_visualizations():
    """Generate risk visualization charts"""
    matrix = DisasterProbabilityMatrix()
    df = matrix.generate_matrix()
    
    # Convert probability to numeric
    df['prob_numeric'] = df['Annual_Probability'].astype(float)
    
    # Set up the plotting style
    plt.style.use('default')
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Urban Family Disaster Risk Analysis', fontsize=16, fontweight='bold')
    
    # 1. Risk by Duration (bubble chart)
    ax1 = axes[0, 0]
    duration_colors = {'sudden': 'red', 'short': 'orange', 'medium': 'yellow', 'long': 'green'}
    
    for duration in df['Duration'].unique():
        subset = df[df['Duration'] == duration]
        ax1.scatter(subset['prob_numeric'], subset['Impact_Severity'], 
                   s=subset['Family_Disruption']*20, alpha=0.6, 
                   c=duration_colors[duration], label=duration.title())
    
    ax1.set_xlabel('Annual Probability')
    ax1.set_ylabel('Impact Severity (1-10)')
    ax1.set_title('Risk Matrix by Duration\n(Bubble size = Family Disruption)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Category Risk Distribution
    ax2 = axes[0, 1]
    category_risk = df.groupby('Category').agg({
        'prob_numeric': 'sum',
        'Impact_Severity': 'mean'
    }).sort_values('prob_numeric', ascending=True)
    
    bars = ax2.barh(category_risk.index, category_risk['prob_numeric'])
    ax2.set_xlabel('Total Annual Probability')
    ax2.set_title('Risk by Category')
    
    # Color bars by average impact
    norm = plt.Normalize(category_risk['Impact_Severity'].min(), 
                        category_risk['Impact_Severity'].max())
    colors = plt.cm.Reds(norm(category_risk['Impact_Severity']))
    for bar, color in zip(bars, colors):
        bar.set_color(color)
    
    # 3. Preparedness vs Impact
    ax3 = axes[1, 0]
    prep_yes = df[df['Preparable'] == True]
    prep_no = df[df['Preparable'] == False]
    
    ax3.scatter(prep_yes['prob_numeric'], prep_yes['Impact_Severity'], 
               alpha=0.6, c='green', label='Preparable', s=60)
    ax3.scatter(prep_no['prob_numeric'], prep_no['Impact_Severity'], 
               alpha=0.6, c='red', label='Not Preparable', s=60)
    
    ax3.set_xlabel('Annual Probability')
    ax3.set_ylabel('Impact Severity')
    ax3.set_title('Preparedness vs Risk Level')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Insurance Coverage Analysis
    ax4 = axes[1, 1]
    insurance_data = df['Insurance'].value_counts()
    colors = ['lightcoral', 'gold', 'lightgreen']
    wedges, texts, autotexts = ax4.pie(insurance_data.values, labels=insurance_data.index, 
                                      autopct='%1.1f%%', colors=colors)
    ax4.set_title('Insurance Coverage Distribution')
    
    plt.tight_layout()
    plt.savefig('risk_analysis_charts.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return fig

def generate_risk_scenarios():
    """Generate specific risk scenarios for planning"""
    scenarios = {
        "High Probability Cluster": {
            "events": ["Power outage", "School closure", "Minor illness", "Internet outage"],
            "combined_probability": 0.95,
            "preparation": "Emergency kit, backup plans, communication strategy",
            "timeline": "Occurs multiple times per year"
        },
        
        "Medium Impact Disruption": {
            "events": ["Extended illness", "Job loss", "Home repairs", "Childcare issues"],
            "combined_probability": 0.60,
            "preparation": "Emergency fund, insurance, backup care arrangements",
            "timeline": "1-2 events per year likely"
        },
        
        "Low Probability/High Impact": {
            "events": ["Major earthquake", "Serious accident", "Terminal illness"],
            "combined_probability": 0.08,
            "preparation": "Comprehensive insurance, legal documents, support networks",
            "timeline": "Once every 10-15 years"
        },
        
        "Cascading Infrastructure": {
            "events": ["Power outage → Water issues → Transportation problems"],
            "combined_probability": 0.25,
            "preparation": "Multi-system backup plans, alternative routes/methods",
            "timeline": "Annual occurrence likely"
        }
    }
    
    return scenarios

def calculate_annual_risk_budget():
    """Calculate expected annual costs from disasters"""
    matrix = DisasterProbabilityMatrix()
    df = matrix.generate_matrix()
    df['prob_numeric'] = df['Annual_Probability'].astype(float)
    
    # Estimate financial costs by impact level
    cost_estimates = {
        'low': 500,
        'medium': 2500,
        'high': 15000,
        'catastrophic': 100000
    }
    
    df['expected_cost'] = df.apply(lambda row: 
        row['prob_numeric'] * cost_estimates[row['Financial_Impact']], axis=1)
    
    total_expected_annual_cost = df['expected_cost'].sum()
    
    cost_by_category = df.groupby('Category')['expected_cost'].sum().sort_values(ascending=False)
    cost_by_duration = df.groupby('Duration')['expected_cost'].sum()
    
    return {
        'total_annual_expected_cost': total_expected_annual_cost,
        'by_category': cost_by_category.to_dict(),
        'by_duration': cost_by_duration.to_dict(),
        'top_cost_drivers': df.nlargest(10, 'expected_cost')[['Event', 'expected_cost', 'Financial_Impact']].to_dict('records')
    }

if __name__ == "__main__":
    print("Generating risk visualizations...")
    create_risk_visualizations()
    
    print("\nRisk Scenarios for Planning:")
    scenarios = generate_risk_scenarios()
    for name, scenario in scenarios.items():
        print(f"\n{name}:")
        print(f"  Events: {', '.join(scenario['events'])}")
        print(f"  Probability: {scenario['combined_probability']*100:.0f}%")
        print(f"  Preparation: {scenario['preparation']}")
        print(f"  Timeline: {scenario['timeline']}")
    
    print("\nAnnual Risk Budget Analysis:")
    budget = calculate_annual_risk_budget()
    print(f"Expected annual cost from disasters: ${budget['total_annual_expected_cost']:,.0f}")
    print(f"\nTop cost drivers:")
    for driver in budget['top_cost_drivers'][:5]:
        print(f"  • {driver['Event']}: ${driver['expected_cost']:,.0f}")