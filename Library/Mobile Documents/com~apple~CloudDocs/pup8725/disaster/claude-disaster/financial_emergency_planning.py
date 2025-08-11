#!/usr/bin/env python3
"""
Financial Emergency Planning Module
Comprehensive financial preparedness strategies, calculators, and optimization guides
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

class FinancialEmergencyPlanner:
    def __init__(self):
        self.financial_profile = {}
        self.emergency_scenarios = {}
        self.recommendations = {}
        
    def collect_financial_profile(self):
        """Collect detailed financial information"""
        print("=== FINANCIAL EMERGENCY PLANNING ASSESSMENT ===\n")
        
        # Income Information
        print("1. INCOME INFORMATION")
        self.financial_profile['primary_income'] = float(input("Primary earner annual income: $"))
        
        has_secondary = input("Secondary earner? (y/n): ").lower() == 'y'
        if has_secondary:
            self.financial_profile['secondary_income'] = float(input("Secondary earner annual income: $"))
        else:
            self.financial_profile['secondary_income'] = 0
        
        self.financial_profile['other_income'] = float(input("Other annual income (investments, side jobs): $"))
        self.financial_profile['total_income'] = (
            self.financial_profile['primary_income'] + 
            self.financial_profile['secondary_income'] + 
            self.financial_profile['other_income']
        )
        
        # Monthly Expenses
        print("\n2. MONTHLY EXPENSES")
        expenses = {}
        expense_categories = [
            ('housing', 'Housing (rent/mortgage, utilities, maintenance)'),
            ('food', 'Food and groceries'),
            ('transportation', 'Transportation (car payment, gas, insurance)'),
            ('healthcare', 'Healthcare (insurance, medications, copays)'),
            ('childcare', 'Childcare and education'),
            ('debt', 'Debt payments (credit cards, loans)'),
            ('insurance', 'Insurance (life, disability, etc.)'),
            ('savings', 'Current savings/investments'),
            ('discretionary', 'Discretionary spending (entertainment, dining out)')
        ]
        
        for category, description in expense_categories:
            expenses[category] = float(input(f"{description}: $"))
        
        self.financial_profile['monthly_expenses'] = expenses
        self.financial_profile['total_monthly_expenses'] = sum(expenses.values())
        self.financial_profile['annual_expenses'] = self.financial_profile['total_monthly_expenses'] * 12
        
        # Assets and Debts
        print("\n3. ASSETS AND DEBTS")
        self.financial_profile['emergency_fund'] = float(input("Current emergency fund: $"))
        self.financial_profile['checking_savings'] = float(input("Checking/savings accounts: $"))
        self.financial_profile['retirement_401k'] = float(input("401k/retirement accounts: $"))
        self.financial_profile['investments'] = float(input("Other investments: $"))
        self.financial_profile['home_equity'] = float(input("Home equity (if applicable): $"))
        
        self.financial_profile['credit_card_debt'] = float(input("Credit card debt: $"))
        self.financial_profile['student_loans'] = float(input("Student loan debt: $"))
        self.financial_profile['mortgage'] = float(input("Mortgage balance: $"))
        self.financial_profile['other_debt'] = float(input("Other debt: $"))
        
        # Insurance Coverage
        print("\n4. INSURANCE COVERAGE")
        self.financial_profile['health_insurance'] = input("Health insurance coverage (excellent/good/basic/none): ").lower()
        self.financial_profile['health_deductible'] = float(input("Health insurance annual deductible: $"))
        
        self.financial_profile['disability_insurance'] = input("Disability insurance? (y/n): ").lower() == 'y'
        if self.financial_profile['disability_insurance']:
            self.financial_profile['disability_coverage'] = float(input("Monthly disability benefit: $"))
        else:
            self.financial_profile['disability_coverage'] = 0
        
        self.financial_profile['life_insurance'] = float(input("Life insurance coverage: $"))
        self.financial_profile['property_insurance'] = input("Property insurance (homeowner's/renter's)? (y/n): ").lower() == 'y'
        
        # Employment Stability
        print("\n5. EMPLOYMENT INFORMATION")
        self.financial_profile['job_security'] = input("Job security level (high/medium/low): ").lower()
        self.financial_profile['industry_stability'] = input("Industry stability (stable/volatile/uncertain): ").lower()
        self.financial_profile['sick_leave_days'] = int(input("Paid sick leave days per year: "))
        self.financial_profile['vacation_days'] = int(input("Paid vacation days per year: "))
        
        return self.financial_profile
    
    def calculate_emergency_fund_needs(self):
        """Calculate optimal emergency fund size"""
        monthly_expenses = self.financial_profile['total_monthly_expenses']
        
        # Base calculation: 3-6 months of expenses
        base_minimum = monthly_expenses * 3
        base_recommended = monthly_expenses * 6
        
        # Adjustments based on risk factors
        risk_multiplier = 1.0
        
        # Job security adjustments
        if self.financial_profile['job_security'] == 'low':
            risk_multiplier += 0.5
        elif self.financial_profile['job_security'] == 'high':
            risk_multiplier -= 0.2
        
        # Industry stability adjustments
        if self.financial_profile['industry_stability'] == 'volatile':
            risk_multiplier += 0.3
        elif self.financial_profile['industry_stability'] == 'uncertain':
            risk_multiplier += 0.5
        
        # Income source adjustments
        if self.financial_profile['secondary_income'] == 0:
            risk_multiplier += 0.3  # Single income household
        
        # Debt adjustments
        debt_to_income = (
            self.financial_profile['credit_card_debt'] + 
            self.financial_profile['student_loans']
        ) / self.financial_profile['total_income']
        
        if debt_to_income > 0.3:
            risk_multiplier += 0.2
        
        # Health insurance adjustments
        if self.financial_profile['health_insurance'] in ['basic', 'none']:
            risk_multiplier += 0.3
        
        # Calculate adjusted targets
        adjusted_minimum = base_minimum * risk_multiplier
        adjusted_recommended = base_recommended * risk_multiplier
        
        # Conservative target for high-risk situations
        conservative_target = monthly_expenses * 12 if risk_multiplier > 1.5 else adjusted_recommended
        
        return {
            'base_minimum': base_minimum,
            'base_recommended': base_recommended,
            'adjusted_minimum': adjusted_minimum,
            'adjusted_recommended': adjusted_recommended,
            'conservative_target': conservative_target,
            'current_fund': self.financial_profile['emergency_fund'],
            'months_covered': self.financial_profile['emergency_fund'] / monthly_expenses,
            'risk_multiplier': risk_multiplier
        }
    
    def analyze_insurance_gaps(self):
        """Analyze insurance coverage and identify gaps"""
        gaps = []
        recommendations = []
        
        # Health insurance analysis
        if self.financial_profile['health_insurance'] == 'none':
            gaps.append("No health insurance coverage")
            recommendations.append("CRITICAL: Obtain health insurance immediately")
        elif self.financial_profile['health_deductible'] > 5000:
            gaps.append("High health insurance deductible")
            recommendations.append("Consider supplemental insurance or HSA to cover deductible")
        
        # Disability insurance analysis
        if not self.financial_profile['disability_insurance']:
            gaps.append("No disability insurance")
            recommendations.append("IMPORTANT: Obtain disability insurance (60-70% income replacement)")
        else:
            monthly_income = self.financial_profile['total_income'] / 12
            coverage_ratio = self.financial_profile['disability_coverage'] / monthly_income
            if coverage_ratio < 0.6:
                gaps.append("Insufficient disability insurance coverage")
                recommendations.append(f"Increase disability coverage to ${monthly_income * 0.65:.0f}/month")
        
        # Life insurance analysis
        recommended_life_insurance = self.financial_profile['total_income'] * 10
        if self.financial_profile['life_insurance'] < recommended_life_insurance:
            gaps.append("Insufficient life insurance")
            recommendations.append(f"Increase life insurance to ${recommended_life_insurance:,.0f}")
        
        # Property insurance
        if not self.financial_profile['property_insurance']:
            gaps.append("No property insurance")
            recommendations.append("Obtain homeowner's or renter's insurance")
        
        return {
            'gaps': gaps,
            'recommendations': recommendations,
            'insurance_score': max(0, 100 - len(gaps) * 20)
        }
    
    def calculate_disaster_financial_impact(self):
        """Calculate financial impact of various disaster scenarios"""
        scenarios = {}
        monthly_income = self.financial_profile['total_income'] / 12
        monthly_expenses = self.financial_profile['total_monthly_expenses']
        
        # Job Loss Scenario
        scenarios['job_loss'] = {
            'description': 'Primary earner job loss',
            'income_loss': self.financial_profile['primary_income'] / 12,
            'duration_months': 6,  # Average job search time
            'additional_costs': 500,  # COBRA, job search costs
            'total_impact': (self.financial_profile['primary_income'] / 12 * 6) + (500 * 6),
            'emergency_fund_months_needed': 8
        }
        
        # Medical Emergency
        max_out_of_pocket = max(10000, self.financial_profile['health_deductible'] * 2)
        scenarios['medical_emergency'] = {
            'description': 'Major medical emergency',
            'immediate_costs': max_out_of_pocket,
            'income_loss_months': 2,
            'income_loss': monthly_income * 2 * 0.5,  # Partial income loss
            'additional_costs': 2000,  # Travel, childcare, etc.
            'total_impact': max_out_of_pocket + (monthly_income * 2 * 0.5) + 2000,
            'emergency_fund_months_needed': 4
        }
        
        # Home Disaster
        scenarios['home_disaster'] = {
            'description': 'Home uninhabitable (fire, flood, etc.)',
            'immediate_costs': 5000,  # Temporary housing, immediate needs
            'monthly_additional_costs': 2000,  # Extended temporary housing
            'duration_months': 6,
            'insurance_deductible': 2500,
            'total_impact': 5000 + (2000 * 6) + 2500,
            'emergency_fund_months_needed': 3
        }
        
        # Dual Income Loss
        if self.financial_profile['secondary_income'] > 0:
            scenarios['dual_job_loss'] = {
                'description': 'Both earners lose jobs',
                'income_loss': monthly_income,
                'duration_months': 4,
                'additional_costs': 1000,  # Job search, COBRA for both
                'total_impact': (monthly_income * 4) + (1000 * 4),
                'emergency_fund_months_needed': 12
            }
        
        # Economic Recession
        scenarios['economic_recession'] = {
            'description': 'Economic recession impact',
            'income_reduction': monthly_income * 0.2,  # 20% income reduction
            'duration_months': 18,
            'investment_losses': self.financial_profile['investments'] * 0.3,
            'additional_costs': 0,
            'total_impact': (monthly_income * 0.2 * 18) + (self.financial_profile['investments'] * 0.3),
            'emergency_fund_months_needed': 9
        }
        
        return scenarios
    
    def create_emergency_budget(self):
        """Create bare-bones emergency budget"""
        current_expenses = self.financial_profile['monthly_expenses']
        
        # Essential expenses only
        emergency_budget = {
            'housing': current_expenses['housing'] * 0.9,  # Reduce utilities
            'food': current_expenses['food'] * 0.7,  # Basic groceries only
            'transportation': current_expenses['transportation'] * 0.6,  # Minimal driving
            'healthcare': current_expenses['healthcare'],  # Keep full coverage
            'childcare': current_expenses['childcare'],  # Usually essential
            'debt_minimum': current_expenses['debt'] * 0.5,  # Minimum payments only
            'insurance': current_expenses['insurance'],  # Keep essential coverage
            'utilities_basic': 200,  # Basic utilities only
            'emergency_misc': 300  # Unexpected emergency costs
        }
        
        # Remove discretionary spending
        emergency_budget['discretionary'] = 0
        emergency_budget['savings'] = 0
        
        emergency_total = sum(emergency_budget.values())
        reduction = current_expenses['total'] - emergency_total if hasattr(current_expenses, 'total') else sum(current_expenses.values()) - emergency_total
        
        return {
            'emergency_budget': emergency_budget,
            'emergency_total': emergency_total,
            'current_total': sum(current_expenses.values()),
            'monthly_reduction': reduction,
            'reduction_percentage': (reduction / sum(current_expenses.values())) * 100
        }
    
    def generate_savings_plan(self, target_amount):
        """Generate plan to reach emergency fund target"""
        current_fund = self.financial_profile['emergency_fund']
        needed = target_amount - current_fund
        
        if needed <= 0:
            return {'status': 'Target already met', 'needed': 0}
        
        # Calculate available savings capacity
        monthly_income = self.financial_profile['total_income'] / 12
        monthly_expenses = self.financial_profile['total_monthly_expenses']
        monthly_surplus = monthly_income - monthly_expenses
        
        # Suggest different savings rates
        plans = {}
        
        for rate_name, rate_pct in [('Conservative', 0.1), ('Moderate', 0.2), ('Aggressive', 0.3)]:
            monthly_savings = monthly_surplus * rate_pct
            if monthly_savings > 0:
                months_to_target = needed / monthly_savings
                plans[rate_name] = {
                    'monthly_amount': monthly_savings,
                    'months_to_target': months_to_target,
                    'years_to_target': months_to_target / 12,
                    'percentage_of_surplus': rate_pct * 100
                }
        
        # Add fixed amount options
        for amount in [200, 500, 1000]:
            if amount <= monthly_surplus:
                months_to_target = needed / amount
                plans[f'${amount}/month'] = {
                    'monthly_amount': amount,
                    'months_to_target': months_to_target,
                    'years_to_target': months_to_target / 12,
                    'percentage_of_surplus': (amount / monthly_surplus) * 100 if monthly_surplus > 0 else 0
                }
        
        return {
            'needed': needed,
            'monthly_surplus': monthly_surplus,
            'plans': plans
        }
    
    def optimize_financial_resilience(self):
        """Provide comprehensive financial resilience optimization"""
        optimizations = []
        
        # Emergency fund optimization
        fund_analysis = self.calculate_emergency_fund_needs()
        if fund_analysis['current_fund'] < fund_analysis['adjusted_minimum']:
            optimizations.append({
                'priority': 'HIGH',
                'category': 'Emergency Fund',
                'action': f"Increase emergency fund to ${fund_analysis['adjusted_minimum']:,.0f}",
                'current': f"${fund_analysis['current_fund']:,.0f}",
                'target': f"${fund_analysis['adjusted_recommended']:,.0f}",
                'impact': 'Protects against income loss and unexpected expenses'
            })
        
        # Debt optimization
        total_debt = (self.financial_profile['credit_card_debt'] + 
                     self.financial_profile['student_loans'])
        if total_debt > 0:
            debt_to_income = total_debt / self.financial_profile['total_income']
            if debt_to_income > 0.2:
                optimizations.append({
                    'priority': 'HIGH',
                    'category': 'Debt Reduction',
                    'action': f"Reduce high-interest debt by ${total_debt * 0.5:,.0f}",
                    'current': f"${total_debt:,.0f} ({debt_to_income*100:.1f}% of income)",
                    'target': "< 20% of income",
                    'impact': 'Reduces monthly obligations and financial stress'
                })
        
        # Insurance optimization
        insurance_analysis = self.analyze_insurance_gaps()
        for gap in insurance_analysis['gaps']:
            optimizations.append({
                'priority': 'MEDIUM',
                'category': 'Insurance',
                'action': gap,
                'current': 'Insufficient coverage',
                'target': 'Adequate protection',
                'impact': 'Protects against catastrophic financial loss'
            })
        
        # Income diversification
        if self.financial_profile['secondary_income'] == 0:
            optimizations.append({
                'priority': 'MEDIUM',
                'category': 'Income',
                'action': 'Develop secondary income stream',
                'current': 'Single income source',
                'target': 'Multiple income sources',
                'impact': 'Reduces risk of total income loss'
            })
        
        # Investment optimization
        if self.financial_profile['investments'] < self.financial_profile['total_income']:
            optimizations.append({
                'priority': 'LOW',
                'category': 'Investments',
                'action': 'Increase investment portfolio',
                'current': f"${self.financial_profile['investments']:,.0f}",
                'target': f"${self.financial_profile['total_income']:,.0f}+",
                'impact': 'Long-term wealth building and inflation protection'
            })
        
        return optimizations
    
    def generate_financial_action_plan(self):
        """Generate comprehensive financial action plan"""
        fund_analysis = self.calculate_emergency_fund_needs()
        insurance_analysis = self.analyze_insurance_gaps()
        scenarios = self.calculate_disaster_financial_impact()
        emergency_budget = self.create_emergency_budget()
        optimizations = self.optimize_financial_resilience()
        
        # Create savings plan for emergency fund
        savings_plan = self.generate_savings_plan(fund_analysis['adjusted_recommended'])
        
        action_plan = {
            'immediate_actions': [],
            'short_term_goals': [],
            'long_term_planning': [],
            'emergency_procedures': []
        }
        
        # Immediate actions (0-30 days)
        if fund_analysis['current_fund'] < fund_analysis['base_minimum']:
            action_plan['immediate_actions'].append(
                f"Open high-yield emergency savings account and deposit ${min(5000, fund_analysis['base_minimum']):,.0f}"
            )
        
        for rec in insurance_analysis['recommendations']:
            if 'CRITICAL' in rec:
                action_plan['immediate_actions'].append(rec)
        
        action_plan['immediate_actions'].extend([
            "Review and organize all financial documents",
            "Set up automatic transfers to emergency fund",
            "Create list of all accounts, passwords, and contacts"
        ])
        
        # Short-term goals (1-12 months)
        if savings_plan.get('plans'):
            best_plan = min(savings_plan['plans'].items(), 
                          key=lambda x: x[1]['months_to_target'])
            action_plan['short_term_goals'].append(
                f"Build emergency fund using {best_plan[0]} plan: ${best_plan[1]['monthly_amount']:.0f}/month"
            )
        
        for opt in optimizations:
            if opt['priority'] in ['HIGH', 'MEDIUM']:
                action_plan['short_term_goals'].append(opt['action'])
        
        # Long-term planning (1+ years)
        action_plan['long_term_planning'].extend([
            "Maximize retirement contributions",
            "Consider investment property or business ownership",
            "Review and update financial plan annually",
            "Build multiple income streams"
        ])
        
        # Emergency procedures
        action_plan['emergency_procedures'].extend([
            f"Activate emergency budget (reduces expenses to ${emergency_budget['emergency_total']:,.0f}/month)",
            "Contact insurance companies immediately for claims",
            "Apply for unemployment benefits if applicable",
            "Negotiate payment plans with creditors if needed",
            "Access emergency fund in order: savings → checking → investments"
        ])
        
        return {
            'action_plan': action_plan,
            'fund_analysis': fund_analysis,
            'insurance_analysis': insurance_analysis,
            'scenarios': scenarios,
            'emergency_budget': emergency_budget,
            'savings_plan': savings_plan,
            'optimizations': optimizations
        }
    
    def save_financial_plan(self, plan_data):
        """Save financial plan to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"financial_emergency_plan_{timestamp}.json"
        
        # Prepare data for JSON serialization
        save_data = {
            'timestamp': timestamp,
            'financial_profile': self.financial_profile,
            'plan_data': plan_data
        }
        
        with open(filename, 'w') as f:
            json.dump(save_data, f, indent=2, default=str)
        
        return filename
    
    def display_financial_summary(self, plan_data):
        """Display comprehensive financial summary"""
        print("\n" + "="*70)
        print("FINANCIAL EMERGENCY PLANNING SUMMARY")
        print("="*70)
        
        # Current financial position
        print(f"\nCURRENT FINANCIAL POSITION:")
        print(f"  Annual Income: ${self.financial_profile['total_income']:,.0f}")
        print(f"  Monthly Expenses: ${self.financial_profile['total_monthly_expenses']:,.0f}")
        print(f"  Emergency Fund: ${self.financial_profile['emergency_fund']:,.0f}")
        print(f"  Months Covered: {plan_data['fund_analysis']['months_covered']:.1f}")
        
        # Emergency fund targets
        fund_analysis = plan_data['fund_analysis']
        print(f"\nEMERGENCY FUND TARGETS:")
        print(f"  Minimum Target: ${fund_analysis['adjusted_minimum']:,.0f}")
        print(f"  Recommended Target: ${fund_analysis['adjusted_recommended']:,.0f}")
        print(f"  Amount Needed: ${max(0, fund_analysis['adjusted_recommended'] - fund_analysis['current_fund']):,.0f}")
        
        # Top financial risks
        print(f"\nTOP FINANCIAL RISK SCENARIOS:")
        scenarios = plan_data['scenarios']
        for name, scenario in list(scenarios.items())[:3]:
            print(f"  • {scenario['description']}: ${scenario['total_impact']:,.0f} impact")
        
        # Priority actions
        print(f"\nIMMEDIATE PRIORITY ACTIONS:")
        for action in plan_data['action_plan']['immediate_actions'][:5]:
            print(f"  • {action}")
        
        # Insurance gaps
        insurance_gaps = plan_data['insurance_analysis']['gaps']
        if insurance_gaps:
            print(f"\nINSURANCE GAPS TO ADDRESS:")
            for gap in insurance_gaps:
                print(f"  • {gap}")
        
        # Emergency budget
        emergency_budget = plan_data['emergency_budget']
        print(f"\nEMERGENCY BUDGET:")
        print(f"  Current Monthly Expenses: ${emergency_budget['current_total']:,.0f}")
        print(f"  Emergency Budget: ${emergency_budget['emergency_total']:,.0f}")
        print(f"  Monthly Reduction: ${emergency_budget['monthly_reduction']:,.0f} ({emergency_budget['reduction_percentage']:.1f}%)")
    
    def run_financial_planning(self):
        """Run complete financial emergency planning process"""
        print("Starting comprehensive financial emergency planning...\n")
        
        # Collect financial information
        self.collect_financial_profile()
        
        # Generate comprehensive plan
        print("\nAnalyzing financial position and generating plan...")
        plan_data = self.generate_financial_action_plan()
        
        # Display results
        self.display_financial_summary(plan_data)
        
        # Save plan
        filename = self.save_financial_plan(plan_data)
        print(f"\nDetailed financial plan saved to: {filename}")
        
        return plan_data

def main():
    """Main function to run financial planning"""
    planner = FinancialEmergencyPlanner()
    plan = planner.run_financial_planning()
    return plan

if __name__ == "__main__":
    main()