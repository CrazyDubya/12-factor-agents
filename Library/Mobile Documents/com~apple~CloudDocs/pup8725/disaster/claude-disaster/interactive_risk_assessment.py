#!/usr/bin/env python3
"""
Interactive Risk Assessment Tool
Personalized risk analysis based on family demographics, location, and circumstances
"""

import json
import pandas as pd
from datetime import datetime
from disaster_probability_matrix import DisasterProbabilityMatrix

class InteractiveRiskAssessment:
    def __init__(self):
        self.base_matrix = DisasterProbabilityMatrix()
        self.user_profile = {}
        self.risk_adjustments = {}
        
    def collect_user_profile(self):
        """Collect user information for personalized assessment"""
        print("=== PERSONALIZED FAMILY RISK ASSESSMENT ===\n")
        
        # Basic Demographics
        print("1. FAMILY DEMOGRAPHICS")
        self.user_profile['adults'] = int(input("Number of adults in household: "))
        self.user_profile['children'] = int(input("Number of children in household: "))
        
        if self.user_profile['children'] > 0:
            ages = []
            for i in range(self.user_profile['children']):
                age = int(input(f"Age of child {i+1}: "))
                ages.append(age)
            self.user_profile['child_ages'] = ages
        
        if self.user_profile['adults'] > 0:
            ages = []
            for i in range(self.user_profile['adults']):
                age = int(input(f"Age of adult {i+1}: "))
                ages.append(age)
            self.user_profile['adult_ages'] = ages
        
        # Location and Housing
        print("\n2. LOCATION & HOUSING")
        location_types = ["urban", "suburban", "rural"]
        print("Location type options:", ", ".join(location_types))
        self.user_profile['location_type'] = input("Location type: ").lower()
        
        housing_types = ["apartment", "house", "condo", "mobile_home"]
        print("Housing type options:", ", ".join(housing_types))
        self.user_profile['housing_type'] = input("Housing type: ").lower()
        
        self.user_profile['own_home'] = input("Do you own your home? (y/n): ").lower() == 'y'
        
        # Geographic Risk Factors
        print("\n3. GEOGRAPHIC RISK FACTORS")
        self.user_profile['earthquake_zone'] = input("Live in earthquake zone? (y/n): ").lower() == 'y'
        self.user_profile['hurricane_zone'] = input("Live in hurricane zone? (y/n): ").lower() == 'y'
        self.user_profile['tornado_zone'] = input("Live in tornado zone? (y/n): ").lower() == 'y'
        self.user_profile['flood_zone'] = input("Live in flood zone? (y/n): ").lower() == 'y'
        self.user_profile['wildfire_zone'] = input("Live in wildfire zone? (y/n): ").lower() == 'y'
        
        # Economic Factors
        print("\n4. ECONOMIC SITUATION")
        income_ranges = ["<30k", "30-50k", "50-75k", "75-100k", "100-150k", ">150k"]
        print("Income ranges:", ", ".join(income_ranges))
        self.user_profile['income_range'] = input("Household income range: ")
        
        self.user_profile['dual_income'] = input("Dual income household? (y/n): ").lower() == 'y'
        self.user_profile['emergency_fund_months'] = float(input("Emergency fund (months of expenses): "))
        
        # Health Factors
        print("\n5. HEALTH CONSIDERATIONS")
        self.user_profile['chronic_conditions'] = input("Any family chronic health conditions? (y/n): ").lower() == 'y'
        self.user_profile['mobility_issues'] = input("Any mobility limitations? (y/n): ").lower() == 'y'
        self.user_profile['medication_dependent'] = input("Anyone dependent on daily medications? (y/n): ").lower() == 'y'
        
        # Special Circumstances
        print("\n6. SPECIAL CIRCUMSTANCES")
        self.user_profile['elderly_care'] = input("Responsible for elderly relatives? (y/n): ").lower() == 'y'
        self.user_profile['pets'] = input("Have pets? (y/n): ").lower() == 'y'
        self.user_profile['home_business'] = input("Run business from home? (y/n): ").lower() == 'y'
        
        return self.user_profile
    
    def calculate_risk_adjustments(self):
        """Calculate personalized risk adjustments based on user profile"""
        adjustments = {}
        
        # Location adjustments
        location_multipliers = {
            'urban': {'crime': 1.5, 'infrastructure': 1.3, 'health_access': 0.7},
            'suburban': {'crime': 1.0, 'infrastructure': 1.0, 'health_access': 1.0},
            'rural': {'crime': 0.7, 'infrastructure': 1.4, 'health_access': 1.5}
        }
        
        loc_type = self.user_profile.get('location_type', 'suburban')
        adjustments.update(location_multipliers.get(loc_type, location_multipliers['suburban']))
        
        # Age-based adjustments
        if 'child_ages' in self.user_profile:
            young_children = sum(1 for age in self.user_profile['child_ages'] if age < 5)
            school_children = sum(1 for age in self.user_profile['child_ages'] if 5 <= age <= 17)
            
            if young_children > 0:
                adjustments['childcare_disruption'] = 1.5
                adjustments['health_emergencies'] = 1.3
            
            if school_children > 0:
                adjustments['education_disruption'] = 1.4
        
        if 'adult_ages' in self.user_profile:
            older_adults = sum(1 for age in self.user_profile['adult_ages'] if age > 50)
            if older_adults > 0:
                adjustments['health_risks'] = 1.2 + (older_adults * 0.1)
        
        # Geographic risk adjustments
        if self.user_profile.get('earthquake_zone'):
            adjustments['earthquake'] = 2.0
        if self.user_profile.get('hurricane_zone'):
            adjustments['hurricane'] = 3.0
        if self.user_profile.get('tornado_zone'):
            adjustments['tornado'] = 2.5
        if self.user_profile.get('flood_zone'):
            adjustments['flood'] = 2.0
        if self.user_profile.get('wildfire_zone'):
            adjustments['wildfire'] = 2.5
        
        # Economic adjustments
        income_stability = {
            '<30k': 1.5, '30-50k': 1.2, '50-75k': 1.0,
            '75-100k': 0.9, '100-150k': 0.8, '>150k': 0.7
        }
        income_range = self.user_profile.get('income_range', '50-75k')
        adjustments['economic_stress'] = income_stability.get(income_range, 1.0)
        
        if not self.user_profile.get('dual_income', True):
            adjustments['job_loss_impact'] = 1.5
        
        # Emergency fund impact
        fund_months = self.user_profile.get('emergency_fund_months', 0)
        if fund_months < 3:
            adjustments['financial_vulnerability'] = 1.4
        elif fund_months >= 6:
            adjustments['financial_vulnerability'] = 0.7
        
        # Health adjustments
        if self.user_profile.get('chronic_conditions'):
            adjustments['health_complications'] = 1.3
        if self.user_profile.get('medication_dependent'):
            adjustments['supply_disruption'] = 1.4
        if self.user_profile.get('mobility_issues'):
            adjustments['evacuation_difficulty'] = 1.6
        
        # Special circumstances
        if self.user_profile.get('elderly_care'):
            adjustments['caregiving_stress'] = 1.3
        if self.user_profile.get('pets'):
            adjustments['evacuation_complexity'] = 1.2
        if self.user_profile.get('home_business'):
            adjustments['income_disruption'] = 1.3
        
        self.risk_adjustments = adjustments
        return adjustments
    
    def generate_personalized_matrix(self):
        """Generate personalized risk matrix with adjustments"""
        base_df = self.base_matrix.generate_matrix()
        personalized_df = base_df.copy()
        
        # Apply adjustments to relevant events
        for idx, row in personalized_df.iterrows():
            event = row['Event'].lower()
            category = row['Category'].lower()
            
            # Apply category-based adjustments
            multiplier = 1.0
            
            if 'crime' in event or category == 'security':
                multiplier *= self.risk_adjustments.get('crime', 1.0)
            
            if 'power' in event or 'infrastructure' in category:
                multiplier *= self.risk_adjustments.get('infrastructure', 1.0)
            
            if 'health' in event or category == 'health':
                multiplier *= self.risk_adjustments.get('health_risks', 1.0)
                multiplier *= self.risk_adjustments.get('health_complications', 1.0)
            
            if 'job' in event or 'economic' in category:
                multiplier *= self.risk_adjustments.get('economic_stress', 1.0)
                multiplier *= self.risk_adjustments.get('job_loss_impact', 1.0)
            
            if 'school' in event or 'childcare' in event:
                multiplier *= self.risk_adjustments.get('education_disruption', 1.0)
                multiplier *= self.risk_adjustments.get('childcare_disruption', 1.0)
            
            # Apply specific event adjustments
            for risk_type, adjustment in self.risk_adjustments.items():
                if risk_type in event:
                    multiplier *= adjustment
            
            # Update probability
            new_prob = min(1.0, float(row['Annual_Probability']) * multiplier)
            personalized_df.at[idx, 'Annual_Probability'] = f"{new_prob:.4f}"
            
            # Adjust impact based on vulnerability factors
            impact_adjustment = 1.0
            if self.risk_adjustments.get('financial_vulnerability', 1.0) > 1.0:
                impact_adjustment *= 1.1
            if self.risk_adjustments.get('evacuation_difficulty', 1.0) > 1.0:
                impact_adjustment *= 1.1
            
            new_impact = min(10, int(row['Impact_Severity'] * impact_adjustment))
            personalized_df.at[idx, 'Impact_Severity'] = new_impact
        
        return personalized_df
    
    def generate_personalized_recommendations(self, df):
        """Generate specific recommendations based on user profile and risks"""
        recommendations = {
            'immediate_priorities': [],
            'medium_term_goals': [],
            'long_term_planning': [],
            'specific_preparations': []
        }
        
        # Analyze top risks
        df['risk_score'] = df['Annual_Probability'].astype(float) * df['Impact_Severity']
        top_risks = df.nlargest(10, 'risk_score')
        
        # Emergency fund recommendations
        fund_months = self.user_profile.get('emergency_fund_months', 0)
        if fund_months < 3:
            recommendations['immediate_priorities'].append(
                f"BUILD EMERGENCY FUND: You have {fund_months} months saved. Target 3 months minimum ($15,000-25,000 typical)"
            )
        elif fund_months < 6:
            recommendations['medium_term_goals'].append(
                f"EXPAND EMERGENCY FUND: Grow from {fund_months} to 6+ months of expenses"
            )
        
        # Location-specific recommendations
        if self.user_profile.get('earthquake_zone'):
            recommendations['specific_preparations'].extend([
                "Earthquake kit with 72-hour supplies",
                "Furniture anchoring and home seismic retrofitting",
                "Earthquake insurance evaluation"
            ])
        
        if self.user_profile.get('hurricane_zone'):
            recommendations['specific_preparations'].extend([
                "Hurricane evacuation plan and supplies",
                "Window protection (shutters/plywood)",
                "Flood insurance (separate from homeowner's)"
            ])
        
        # Family-specific recommendations
        if self.user_profile.get('children', 0) > 0:
            recommendations['immediate_priorities'].append(
                "CHILDCARE BACKUP PLAN: Identify 3+ emergency childcare options"
            )
            recommendations['specific_preparations'].append(
                "Child emergency kit with comfort items, games, medications"
            )
        
        if self.user_profile.get('chronic_conditions'):
            recommendations['immediate_priorities'].append(
                "MEDICAL EMERGENCY PLAN: 30-day medication supply, medical alert system"
            )
        
        if self.user_profile.get('pets'):
            recommendations['specific_preparations'].append(
                "Pet emergency kit and evacuation plan with pet-friendly shelters"
            )
        
        # Income-based recommendations
        if not self.user_profile.get('dual_income'):
            recommendations['medium_term_goals'].append(
                "INCOME DIVERSIFICATION: Develop secondary income streams"
            )
        
        # Housing-specific recommendations
        if not self.user_profile.get('own_home'):
            recommendations['specific_preparations'].append(
                "RENTER'S INSURANCE: Protect belongings and provide temporary housing"
            )
        
        # Top risk-based recommendations
        for _, risk in top_risks.head(5).iterrows():
            if risk['Preparable']:
                prep_action = f"Prepare for {risk['Event']} (Annual probability: {float(risk['Annual_Probability'])*100:.1f}%)"
                recommendations['specific_preparations'].append(prep_action)
        
        return recommendations
    
    def save_assessment(self, df, recommendations):
        """Save assessment results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"personalized_risk_assessment_{timestamp}.json"
        
        assessment_data = {
            'timestamp': timestamp,
            'user_profile': self.user_profile,
            'risk_adjustments': self.risk_adjustments,
            'recommendations': recommendations,
            'top_risks': df.nlargest(15, 'risk_score')[['Event', 'Annual_Probability', 'Impact_Severity', 'Category']].to_dict('records')
        }
        
        with open(filename, 'w') as f:
            json.dump(assessment_data, f, indent=2)
        
        # Also save CSV of personalized matrix
        csv_filename = f"personalized_risk_matrix_{timestamp}.csv"
        df.to_csv(csv_filename, index=False)
        
        return filename, csv_filename
    
    def run_assessment(self):
        """Run complete interactive assessment"""
        print("Starting personalized risk assessment...\n")
        
        # Collect user information
        self.collect_user_profile()
        
        # Calculate adjustments
        print("\nCalculating personalized risk adjustments...")
        self.calculate_risk_adjustments()
        
        # Generate personalized matrix
        print("Generating personalized risk matrix...")
        personalized_df = self.generate_personalized_matrix()
        
        # Calculate risk scores
        personalized_df['risk_score'] = (
            personalized_df['Annual_Probability'].astype(float) * 
            personalized_df['Impact_Severity']
        )
        
        # Generate recommendations
        print("Generating personalized recommendations...")
        recommendations = self.generate_personalized_recommendations(personalized_df)
        
        # Save results
        json_file, csv_file = self.save_assessment(personalized_df, recommendations)
        
        # Display results
        self.display_results(personalized_df, recommendations)
        
        print(f"\nResults saved to: {json_file} and {csv_file}")
        
        return personalized_df, recommendations
    
    def display_results(self, df, recommendations):
        """Display assessment results"""
        print("\n" + "="*60)
        print("PERSONALIZED RISK ASSESSMENT RESULTS")
        print("="*60)
        
        # Top risks
        print("\nTOP 10 RISKS FOR YOUR FAMILY:")
        top_risks = df.nlargest(10, 'risk_score')
        for i, (_, risk) in enumerate(top_risks.iterrows(), 1):
            prob_pct = float(risk['Annual_Probability']) * 100
            print(f"{i:2d}. {risk['Event']:<30} | {prob_pct:5.1f}% | Impact: {risk['Impact_Severity']}/10")
        
        # Recommendations by priority
        print(f"\nIMMEDIATE PRIORITIES ({len(recommendations['immediate_priorities'])} items):")
        for item in recommendations['immediate_priorities']:
            print(f"  • {item}")
        
        print(f"\nMEDIUM-TERM GOALS ({len(recommendations['medium_term_goals'])} items):")
        for item in recommendations['medium_term_goals']:
            print(f"  • {item}")
        
        print(f"\nSPECIFIC PREPARATIONS ({len(recommendations['specific_preparations'])} items):")
        for item in recommendations['specific_preparations'][:10]:  # Show top 10
            print(f"  • {item}")
        
        # Risk summary by category
        print(f"\nRISK SUMMARY BY CATEGORY:")
        category_risk = df.groupby('Category').agg({
            'risk_score': 'sum',
            'Annual_Probability': lambda x: (x.astype(float)).sum()
        }).sort_values('risk_score', ascending=False)
        
        for category, data in category_risk.iterrows():
            print(f"  {category.title():<15}: Risk Score {data['risk_score']:.2f} | Total Probability {data['Annual_Probability']*100:.0f}%")

def main():
    """Main function to run interactive assessment"""
    assessment = InteractiveRiskAssessment()
    df, recommendations = assessment.run_assessment()
    return df, recommendations

if __name__ == "__main__":
    main()