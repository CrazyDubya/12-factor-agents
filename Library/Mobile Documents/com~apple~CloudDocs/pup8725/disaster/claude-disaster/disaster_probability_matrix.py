#!/usr/bin/env python3
"""
Disaster Probability Matrix for Urban Family
Family Profile: Parents (avg 40), 6-year-old daughter, urban setting
Duration Categories: Sudden (<1 hour), Short (1-24 hours), Medium (1-30 days), Long (>30 days)
Impact Spectrum: Mundane to Catastrophic
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Tuple
import json

@dataclass
class DisasterEvent:
    name: str
    category: str
    duration_type: str  # sudden, short, medium, long
    probability_annual: float  # probability per year (0-1)
    impact_severity: int  # 1-10 scale
    financial_impact: str  # low, medium, high, catastrophic
    family_disruption: int  # 1-10 scale
    preparation_possible: bool
    insurance_coverage: str  # none, partial, full
    urban_factor: float  # multiplier for urban vs rural (0.5-2.0)

class DisasterProbabilityMatrix:
    def __init__(self):
        self.events = self._initialize_events()
        
    def _initialize_events(self) -> List[DisasterEvent]:
        """Initialize comprehensive disaster event database"""
        events = [
            # SUDDEN DURATION (<1 hour)
            # Mundane to Minor
            DisasterEvent("Power outage (local)", "Infrastructure", "sudden", 0.8, 2, "low", 3, True, "none", 1.2),
            DisasterEvent("Water main break", "Infrastructure", "sudden", 0.3, 3, "low", 4, False, "none", 1.5),
            DisasterEvent("Internet/cable outage", "Infrastructure", "sudden", 0.6, 1, "low", 2, False, "partial", 1.1),
            DisasterEvent("Gas leak (minor)", "Infrastructure", "sudden", 0.1, 4, "medium", 5, True, "partial", 1.3),
            DisasterEvent("Car accident (minor)", "Transportation", "sudden", 0.15, 3, "medium", 4, True, "full", 1.0),
            DisasterEvent("Food poisoning", "Health", "sudden", 0.25, 3, "low", 5, True, "partial", 1.0),
            DisasterEvent("Child injury (minor)", "Health", "sudden", 0.4, 4, "medium", 6, True, "full", 1.0),
            DisasterEvent("Burglary attempt", "Security", "sudden", 0.08, 5, "medium", 7, True, "partial", 1.8),
            
            # Moderate
            DisasterEvent("Severe thunderstorm", "Weather", "sudden", 0.5, 4, "medium", 5, True, "partial", 0.9),
            DisasterEvent("Flash flood", "Weather", "sudden", 0.1, 6, "high", 7, True, "partial", 1.4),
            DisasterEvent("Tornado", "Weather", "sudden", 0.02, 8, "catastrophic", 9, True, "partial", 0.8),
            DisasterEvent("Earthquake (minor)", "Natural", "sudden", 0.05, 5, "medium", 6, True, "partial", 1.2),
            DisasterEvent("Building fire", "Infrastructure", "sudden", 0.03, 7, "high", 8, True, "partial", 1.3),
            DisasterEvent("Chemical spill nearby", "Environmental", "sudden", 0.02, 6, "medium", 7, False, "none", 1.8),
            DisasterEvent("Car accident (major)", "Transportation", "sudden", 0.05, 7, "high", 8, True, "full", 1.0),
            DisasterEvent("Heart attack (parent)", "Health", "sudden", 0.008, 8, "high", 9, True, "full", 1.0),
            
            # Severe to Catastrophic
            DisasterEvent("Earthquake (major)", "Natural", "sudden", 0.005, 9, "catastrophic", 10, True, "partial", 1.2),
            DisasterEvent("Terrorist attack nearby", "Security", "sudden", 0.001, 9, "high", 10, False, "none", 2.0),
            DisasterEvent("Industrial explosion", "Environmental", "sudden", 0.002, 8, "high", 9, False, "partial", 1.5),
            DisasterEvent("Sudden death (parent)", "Health", "sudden", 0.002, 10, "catastrophic", 10, False, "partial", 1.0),
            
            # SHORT DURATION (1-24 hours)
            # Mundane to Minor
            DisasterEvent("Extended power outage", "Infrastructure", "short", 0.4, 3, "medium", 5, True, "none", 1.2),
            DisasterEvent("Water service disruption", "Infrastructure", "short", 0.2, 4, "medium", 6, True, "none", 1.3),
            DisasterEvent("School closure (weather)", "Education", "short", 0.8, 2, "low", 4, False, "none", 1.0),
            DisasterEvent("Public transport strike", "Transportation", "short", 0.3, 3, "medium", 5, False, "none", 1.5),
            DisasterEvent("Stomach flu (family)", "Health", "short", 0.6, 3, "low", 6, True, "partial", 1.0),
            DisasterEvent("Childcare emergency", "Social", "short", 0.4, 4, "medium", 7, True, "none", 1.0),
            DisasterEvent("Home heating failure", "Infrastructure", "short", 0.15, 4, "medium", 5, True, "partial", 1.1),
            
            # Moderate
            DisasterEvent("Blizzard/ice storm", "Weather", "short", 0.2, 5, "medium", 6, True, "partial", 0.8),
            DisasterEvent("Severe flooding", "Weather", "short", 0.08, 6, "high", 7, True, "partial", 1.3),
            DisasterEvent("Widespread blackout", "Infrastructure", "short", 0.1, 5, "medium", 7, False, "none", 1.4),
            DisasterEvent("Hospital emergency", "Health", "short", 0.2, 6, "high", 8, True, "full", 1.0),
            DisasterEvent("Home break-in", "Security", "short", 0.05, 6, "medium", 8, True, "partial", 1.6),
            DisasterEvent("Workplace emergency", "Economic", "short", 0.1, 4, "medium", 5, False, "none", 1.2),
            
            # Severe
            DisasterEvent("Hurricane/typhoon", "Weather", "short", 0.05, 7, "high", 8, True, "partial", 0.7),
            DisasterEvent("Major earthquake", "Natural", "short", 0.003, 8, "catastrophic", 9, True, "partial", 1.2),
            DisasterEvent("Chemical emergency", "Environmental", "short", 0.01, 7, "high", 8, False, "partial", 1.6),
            DisasterEvent("Mass casualty event", "Security", "short", 0.002, 9, "high", 10, False, "none", 1.8),
            
            # MEDIUM DURATION (1-30 days)
            # Mundane to Minor
            DisasterEvent("Extended illness (parent)", "Health", "medium", 0.3, 4, "medium", 6, True, "partial", 1.0),
            DisasterEvent("Temporary job loss", "Economic", "medium", 0.15, 5, "high", 7, True, "partial", 1.0),
            DisasterEvent("School closure (extended)", "Education", "medium", 0.1, 3, "medium", 6, False, "none", 1.0),
            DisasterEvent("Home repairs needed", "Infrastructure", "medium", 0.2, 4, "medium", 5, True, "partial", 1.0),
            DisasterEvent("Car breakdown/repair", "Transportation", "medium", 0.25, 3, "medium", 4, True, "partial", 1.0),
            DisasterEvent("Childcare disruption", "Social", "medium", 0.2, 4, "medium", 7, True, "none", 1.0),
            DisasterEvent("Utility service issues", "Infrastructure", "medium", 0.15, 3, "medium", 4, True, "none", 1.2),
            
            # Moderate
            DisasterEvent("Serious illness (child)", "Health", "medium", 0.1, 6, "high", 8, True, "full", 1.0),
            DisasterEvent("Serious illness (parent)", "Health", "medium", 0.08, 7, "high", 8, True, "full", 1.0),
            DisasterEvent("Home damage (storm)", "Infrastructure", "medium", 0.06, 6, "high", 7, True, "partial", 1.1),
            DisasterEvent("Identity theft", "Security", "medium", 0.05, 5, "medium", 6, True, "partial", 1.2),
            DisasterEvent("Legal issues", "Legal", "medium", 0.03, 5, "high", 6, True, "none", 1.0),
            DisasterEvent("Family emergency", "Social", "medium", 0.1, 5, "medium", 7, False, "none", 1.0),
            DisasterEvent("Workplace closure", "Economic", "medium", 0.05, 5, "medium", 6, False, "partial", 1.2),
            
            # Severe
            DisasterEvent("Major illness/surgery", "Health", "medium", 0.04, 7, "high", 8, True, "full", 1.0),
            DisasterEvent("Home uninhabitable", "Infrastructure", "medium", 0.02, 8, "high", 9, True, "partial", 1.2),
            DisasterEvent("Major accident/injury", "Health", "medium", 0.02, 8, "high", 9, True, "full", 1.0),
            DisasterEvent("Pandemic lockdown", "Health", "medium", 0.01, 6, "medium", 8, False, "none", 1.0),
            
            # LONG DURATION (>30 days)
            # Mundane to Minor
            DisasterEvent("Chronic illness (mild)", "Health", "long", 0.1, 4, "medium", 5, True, "partial", 1.0),
            DisasterEvent("Extended unemployment", "Economic", "long", 0.08, 6, "high", 7, True, "partial", 1.0),
            DisasterEvent("Aging parent care", "Social", "long", 0.15, 5, "medium", 6, True, "none", 1.0),
            DisasterEvent("Educational disruption", "Education", "long", 0.05, 4, "medium", 6, True, "none", 1.0),
            DisasterEvent("Relationship stress", "Social", "long", 0.2, 3, "low", 5, True, "none", 1.0),
            DisasterEvent("Financial strain", "Economic", "long", 0.25, 5, "medium", 6, True, "none", 1.0),
            
            # Moderate
            DisasterEvent("Chronic illness (serious)", "Health", "long", 0.05, 7, "high", 8, True, "partial", 1.0),
            DisasterEvent("Disability (parent)", "Health", "long", 0.02, 8, "high", 9, True, "partial", 1.0),
            DisasterEvent("Disability (child)", "Health", "long", 0.01, 9, "high", 10, True, "partial", 1.0),
            DisasterEvent("Divorce/separation", "Social", "long", 0.1, 6, "medium", 8, True, "none", 1.0),
            DisasterEvent("Economic recession", "Economic", "long", 0.15, 5, "medium", 6, False, "none", 1.0),
            DisasterEvent("Climate change effects", "Environmental", "long", 0.3, 4, "medium", 5, True, "none", 1.1),
            
            # Severe to Catastrophic
            DisasterEvent("Terminal illness", "Health", "long", 0.008, 10, "catastrophic", 10, True, "partial", 1.0),
            DisasterEvent("Permanent disability", "Health", "long", 0.01, 9, "high", 9, True, "partial", 1.0),
            DisasterEvent("Economic collapse", "Economic", "long", 0.005, 8, "catastrophic", 9, False, "none", 1.2),
            DisasterEvent("Environmental disaster", "Environmental", "long", 0.01, 8, "high", 8, False, "partial", 1.3),
            DisasterEvent("Social unrest/war", "Security", "long", 0.002, 9, "catastrophic", 10, False, "none", 1.5),
        ]
        
        return events
    
    def calculate_adjusted_probability(self, event: DisasterEvent) -> float:
        """Calculate probability adjusted for urban setting and family profile"""
        base_prob = event.probability_annual
        urban_adjusted = base_prob * event.urban_factor
        
        # Family-specific adjustments
        family_factor = 1.0
        
        # Adjust for having a young child
        if "child" in event.name.lower() or event.category in ["Health", "Education"]:
            family_factor *= 1.2
            
        # Adjust for parent age (40s - moderate risk increase)
        if "parent" in event.name.lower() and event.category == "Health":
            family_factor *= 1.1
            
        # Adjust for urban density effects
        if event.category in ["Security", "Infrastructure"]:
            family_factor *= 1.1
            
        return min(urban_adjusted * family_factor, 1.0)
    
    def generate_matrix(self) -> pd.DataFrame:
        """Generate the complete probability matrix"""
        data = []
        
        for event in self.events:
            adjusted_prob = self.calculate_adjusted_probability(event)
            
            data.append({
                'Event': event.name,
                'Category': event.category,
                'Duration': event.duration_type,
                'Annual_Probability': f"{adjusted_prob:.4f}",
                'Probability_Percent': f"{adjusted_prob * 100:.2f}%",
                'Impact_Severity': event.impact_severity,
                'Financial_Impact': event.financial_impact,
                'Family_Disruption': event.family_disruption,
                'Preparable': event.preparation_possible,
                'Insurance': event.insurance_coverage,
                'Urban_Factor': event.urban_factor
            })
        
        return pd.DataFrame(data)
    
    def get_summary_statistics(self) -> Dict:
        """Generate summary statistics"""
        df = self.generate_matrix()
        
        # Convert probability strings back to float for calculations
        df['prob_numeric'] = df['Annual_Probability'].astype(float)
        
        stats = {
            'total_events': len(df),
            'by_duration': df.groupby('Duration')['prob_numeric'].agg(['count', 'mean', 'sum']).to_dict(),
            'by_category': df.groupby('Category')['prob_numeric'].agg(['count', 'mean', 'sum']).to_dict(),
            'high_probability_events': df[df['prob_numeric'] > 0.1].sort_values('prob_numeric', ascending=False)[['Event', 'Probability_Percent']].to_dict('records'),
            'high_impact_events': df[df['Impact_Severity'] >= 8].sort_values('Impact_Severity', ascending=False)[['Event', 'Impact_Severity', 'Probability_Percent']].to_dict('records'),
            'preparable_events': df[df['Preparable'] == True]['Event'].count(),
            'insured_events': df[df['Insurance'] != 'none']['Event'].count()
        }
        
        return stats

def main():
    """Generate and display the disaster probability matrix"""
    matrix = DisasterProbabilityMatrix()
    
    # Generate the full matrix
    df = matrix.generate_matrix()
    
    # Display results
    print("DISASTER PROBABILITY MATRIX")
    print("=" * 80)
    print(f"Family Profile: Parents (avg 40), 6-year-old daughter, urban setting")
    print(f"Total Events Analyzed: {len(df)}")
    print("\n")
    
    # Show matrix by duration
    for duration in ['sudden', 'short', 'medium', 'long']:
        duration_df = df[df['Duration'] == duration].sort_values('Annual_Probability', ascending=False)
        print(f"\n{duration.upper()} DURATION EVENTS")
        print("-" * 60)
        print(duration_df[['Event', 'Category', 'Probability_Percent', 'Impact_Severity', 'Family_Disruption']].to_string(index=False))
    
    # Summary statistics
    stats = matrix.get_summary_statistics()
    print(f"\n\nSUMMARY STATISTICS")
    print("=" * 50)
    print(f"Total events analyzed: {stats['total_events']}")
    print(f"Events with preparation possible: {stats['preparable_events']}")
    print(f"Events with insurance coverage: {stats['insured_events']}")
    
    print(f"\nHIGH PROBABILITY EVENTS (>10% annual):")
    for event in stats['high_probability_events'][:10]:
        print(f"  • {event['Event']}: {event['Probability_Percent']}")
    
    print(f"\nHIGH IMPACT EVENTS (severity ≥8):")
    for event in stats['high_impact_events'][:10]:
        print(f"  • {event['Event']}: Severity {event['Impact_Severity']}, Probability {event['Probability_Percent']}")
    
    # Save to CSV
    df.to_csv('disaster_probability_matrix.csv', index=False)
    print(f"\nFull matrix saved to: disaster_probability_matrix.csv")
    
    return df, stats

if __name__ == "__main__":
    df, stats = main()