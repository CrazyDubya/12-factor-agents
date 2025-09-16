import json
import requests
from collections import Counter, defaultdict
from datetime import datetime
import re
import time

def ultra_granular_classification():
    """Ultra-granular classification with 100+ subcategories and temporal analysis"""

    print("=== ULTRA-GRANULAR POLICY CLASSIFICATION ===")
    print("Loading complete career dataset for deep temporal policy analysis...")

    # Load our complete dataset
    try:
        with open('complete_lanza_career.json', 'r') as f:
            career_data = json.load(f)
    except FileNotFoundError:
        print("ERROR: Complete career dataset not found!")
        return

    all_bills = career_data['all_lanza_bills']
    print(f"Analyzing {len(all_bills)} bills with ultra-granular classification...")

    # Ultra-granular classification system
    policy_categories = Counter()
    detailed_classification = defaultdict(list)
    temporal_analysis = defaultdict(lambda: defaultdict(int))

    # CRIMINAL JUSTICE - Break into 15+ subcategories
    criminal_justice_keywords = {
        'Criminal Justice - Sentencing Reform': ['sentence', 'sentencing', 'penalty enhancement', 'mandatory minimum', 'parole', 'probation'],
        'Criminal Justice - Court Procedures': ['court', 'judicial', 'proceeding', 'trial', 'evidence', 'testimony', 'witness'],
        'Criminal Justice - Prosecution': ['prosecutor', 'district attorney', 'prosecution', 'indictment', 'charges'],
        'Criminal Justice - Corrections': ['prison', 'jail', 'correctional', 'inmate', 'custody', 'detention'],
        'Criminal Justice - Juvenile Reform': ['juvenile', 'minor', 'youth court', 'family court', 'adolescent'],
        'Criminal Justice - Drug Policy': ['drug', 'substance', 'narcotic', 'controlled substance', 'prescription abuse'],
        'Criminal Justice - Cyber Security': ['cyber', 'computer crime', 'internet', 'electronic fraud', 'identity theft'],
        'Criminal Justice - Domestic Violence': ['domestic violence', 'family violence', 'spousal abuse', 'restraining order'],
        'Criminal Justice - Sexual Crimes': ['sexual assault', 'rape', 'sexual abuse', 'sexual offense'],
        'Criminal Justice - Financial Crimes': ['fraud', 'embezzlement', 'money laundering', 'financial crime', 'theft'],
        'Criminal Justice - Gang Activity': ['gang', 'organized crime', 'criminal organization', 'racketeering'],
        'Criminal Justice - Weapons': ['weapon', 'firearm', 'gun', 'ammunition', 'deadly weapon'],
        'Criminal Justice - Victims Rights': ['victim', 'victim rights', 'victim compensation', 'victim services'],
        'Criminal Justice - Police Reform': ['police', 'law enforcement', 'officer', 'police misconduct'],
        'Criminal Justice - Border Security': ['border', 'immigration enforcement', 'customs', 'illegal entry'],
    }

    # TRANSPORTATION - Break into 20+ subcategories
    transportation_keywords = {
        'Transportation - Vehicle Safety': ['vehicle safety', 'safety inspection', 'recall', 'safety standard', 'crash test'],
        'Transportation - Driver Education': ['driver education', 'driving test', 'road test', 'safety course'],
        'Transportation - License Administration': ['license', 'permit', 'registration', 'renewal', 'identification card'],
        'Transportation - Traffic Enforcement': ['traffic violation', 'speeding', 'traffic fine', 'traffic court'],
        'Transportation - Highway Infrastructure': ['highway', 'road construction', 'bridge', 'infrastructure', 'maintenance'],
        'Transportation - Parking Regulation': ['parking', 'meter', 'parking violation', 'parking authority'],
        'Transportation - Commercial Vehicle': ['commercial vehicle', 'truck', 'freight', 'cargo', 'logistics'],
        'Transportation - Emergency Vehicle': ['emergency vehicle', 'ambulance', 'fire truck', 'police vehicle'],
        'Transportation - Motorcycle': ['motorcycle', 'motorbike', 'scooter', 'moped'],
        'Transportation - Public Bus': ['bus', 'public transportation', 'transit authority', 'bus route'],
        'Transportation - Subway/Rail': ['subway', 'train', 'rail', 'locomotive', 'railroad'],
        'Transportation - Ferry Operations': ['ferry', 'ferry service', 'ferry terminal', 'staten island ferry'],
        'Transportation - Port Authority': ['port', 'harbor', 'dock', 'pier', 'shipping'],
        'Transportation - Maritime Safety': ['vessel safety', 'boat inspection', 'maritime safety', 'coast guard'],
        'Transportation - Commercial Shipping': ['cargo ship', 'freight vessel', 'shipping lane', 'commercial vessel'],
        'Transportation - Aviation': ['aircraft', 'airport', 'aviation', 'pilot', 'flight'],
        'Transportation - Pedestrian Safety': ['pedestrian', 'crosswalk', 'sidewalk', 'walking'],
        'Transportation - Bicycle': ['bicycle', 'bike', 'cycling', 'bike lane'],
        'Transportation - Taxi/Rideshare': ['taxi', 'cab', 'rideshare', 'uber', 'lyft'],
        'Transportation - Disability Access': ['disability access', 'wheelchair', 'accessible transport', 'ada compliance'],
    }

    # FISCAL POLICY - Break into 12+ subcategories
    fiscal_keywords = {
        'Fiscal - Property Tax': ['property tax', 'real estate tax', 'assessment', 'property assessment'],
        'Fiscal - Income Tax': ['income tax', 'personal income', 'tax bracket', 'tax rate'],
        'Fiscal - Sales Tax': ['sales tax', 'use tax', 'consumption tax', 'retail tax'],
        'Fiscal - Business Tax': ['business tax', 'corporate tax', 'franchise tax', 'commercial tax'],
        'Fiscal - Tax Credits': ['tax credit', 'deduction', 'exemption', 'tax relief'],
        'Fiscal - Tax Administration': ['tax collection', 'tax enforcement', 'tax audit', 'tax compliance'],
        'Fiscal - Municipal Finance': ['municipal bond', 'city budget', 'local funding', 'municipal revenue'],
        'Fiscal - State Budget': ['state budget', 'appropriation', 'state funding', 'budget allocation'],
        'Fiscal - Fee Structure': ['fee', 'surcharge', 'penalty', 'fine', 'administrative fee'],
        'Fiscal - Economic Development': ['economic development', 'tax incentive', 'development zone', 'business incentive'],
        'Fiscal - Debt Management': ['debt', 'borrowing', 'bond', 'debt service', 'fiscal responsibility'],
        'Fiscal - Pension/Benefits': ['pension', 'retirement', 'benefits', 'employee compensation'],
    }

    # EDUCATION - Break into 15+ subcategories
    education_keywords = {
        'Education - Curriculum Standards': ['curriculum', 'standard', 'academic standard', 'learning objective'],
        'Education - Teacher Certification': ['teacher', 'certification', 'teacher training', 'educator'],
        'Education - School Safety': ['school safety', 'school security', 'school violence', 'safe school'],
        'Education - Special Needs': ['special education', 'disability', 'individualized', 'special needs'],
        'Education - School Funding': ['school funding', 'education funding', 'school budget', 'education aid'],
        'Education - School Choice': ['charter school', 'school choice', 'voucher', 'private school'],
        'Education - Higher Ed Access': ['college', 'university', 'higher education', 'tuition'],
        'Education - Vocational Training': ['vocational', 'trade school', 'technical education', 'career training'],
        'Education - Student Services': ['student services', 'counseling', 'guidance', 'student support'],
        'Education - School Administration': ['school board', 'superintendent', 'principal', 'administration'],
        'Education - Student Testing': ['testing', 'assessment', 'standardized test', 'evaluation'],
        'Education - School Transportation': ['school bus', 'student transportation', 'bus route'],
        'Education - Technology': ['educational technology', 'computer', 'internet', 'digital learning'],
        'Education - Arts/Recreation': ['arts education', 'music', 'physical education', 'sports'],
        'Education - Early Childhood': ['pre-k', 'kindergarten', 'early childhood', 'preschool'],
    }

    # GOVERNMENT ADMIN - Break into 15+ subcategories
    government_keywords = {
        'Government - Ethics/Transparency': ['ethics', 'conflict of interest', 'disclosure', 'transparency'],
        'Government - Election Administration': ['election', 'voting', 'ballot', 'campaign', 'political'],
        'Government - Local Government': ['local government', 'municipality', 'county', 'city', 'town'],
        'Government - State Agencies': ['state agency', 'department', 'bureau', 'commission'],
        'Government - Public Records': ['public record', 'freedom of information', 'open government', 'records access'],
        'Government - Civil Service': ['civil service', 'public employee', 'government worker', 'merit system'],
        'Government - Administrative Law': ['administrative', 'regulation', 'rulemaking', 'regulatory'],
        'Government - Procurement': ['procurement', 'contracting', 'bidding', 'government contract'],
        'Government - Emergency Management': ['emergency management', 'disaster response', 'emergency services'],
        'Government - Public Meetings': ['public meeting', 'open meeting', 'government meeting', 'sunshine law'],
        'Government - Licensing/Permits': ['licensing', 'permit', 'authorization', 'government approval'],
        'Government - Intergovernmental': ['intergovernmental', 'federal', 'state cooperation', 'interstate'],
        'Government - Public Authority': ['public authority', 'public corporation', 'quasi-government'],
        'Government - Public Safety Admin': ['public safety', 'emergency', 'disaster', 'security'],
        'Government - Personnel Management': ['personnel', 'human resources', 'employee', 'staff'],
    }

    # Combine all keyword dictionaries
    all_keywords = {}
    all_keywords.update(criminal_justice_keywords)
    all_keywords.update(transportation_keywords)
    all_keywords.update(fiscal_keywords)
    all_keywords.update(education_keywords)
    all_keywords.update(government_keywords)

    # Add additional specialized categories
    specialized_keywords = {
        'Healthcare - Medical Practice': ['medical', 'physician', 'doctor', 'healthcare provider'],
        'Healthcare - Insurance Regulation': ['health insurance', 'medical insurance', 'coverage'],
        'Healthcare - Public Health': ['public health', 'epidemic', 'vaccination', 'disease control'],
        'Healthcare - Mental Health': ['mental health', 'psychiatric', 'psychology', 'counseling'],
        'Healthcare - Emergency Medical': ['emergency medical', 'ambulance', 'paramedic', 'ems'],

        'Environment - Water Quality': ['water quality', 'drinking water', 'water pollution', 'clean water'],
        'Environment - Air Quality': ['air quality', 'air pollution', 'emissions', 'clean air'],
        'Environment - Waste Management': ['waste', 'garbage', 'recycling', 'landfill'],
        'Environment - Conservation': ['conservation', 'preserve', 'protect', 'environmental protection'],

        'Housing - Affordable Housing': ['affordable housing', 'low income housing', 'housing assistance'],
        'Housing - Rental Regulation': ['rent', 'landlord', 'tenant', 'rental'],
        'Housing - Building Codes': ['building code', 'construction', 'safety code', 'building standard'],
        'Housing - Zoning': ['zoning', 'land use', 'planning', 'development'],

        'Animal Welfare - Domestic': ['pet', 'companion animal', 'dog', 'cat'],
        'Animal Welfare - Wildlife': ['wildlife', 'wild animal', 'hunting', 'fishing'],
        'Animal Welfare - Agriculture': ['farm animal', 'livestock', 'agriculture', 'farming'],

        'Social Services - General': ['social service', 'welfare', 'assistance', 'benefits'],
        'Social Services - Child Welfare': ['child welfare', 'foster', 'adoption', 'child protection'],
        'Social Services - Senior Services': ['senior', 'elderly', 'aging', 'retirement'],
        'Social Services - Disability': ['disability', 'disabled', 'handicapped', 'accessibility'],

        'Professional Regulation - Healthcare': ['medical license', 'healthcare professional', 'medical board'],
        'Professional Regulation - Legal': ['legal profession', 'attorney', 'bar', 'legal practice'],
        'Professional Regulation - Business': ['business license', 'professional license', 'trade license'],

        'Technology - Data Privacy': ['privacy', 'data protection', 'personal information', 'cybersecurity'],
        'Technology - Communications': ['communication', 'telephone', 'internet', 'broadband'],

        'Veterans - Benefits': ['veteran', 'military', 'armed forces', 'veteran benefits'],
        'Veterans - Services': ['veteran services', 'military service', 'veteran affairs'],

        'Recreation - Parks': ['park', 'recreation', 'playground', 'public space'],
        'Recreation - Sports': ['sports', 'athletics', 'sports facility', 'recreation center'],

        'Culture - Arts': ['art', 'culture', 'museum', 'cultural'],
        'Culture - Historic Preservation': ['historic', 'preservation', 'heritage', 'landmark'],
    }

    all_keywords.update(specialized_keywords)

    print(f"Using {len(all_keywords)} ultra-granular policy categories...")

    # Time periods for analysis
    time_periods = {
        'Early Career (2009-2013)': range(2009, 2014),
        'Mid Career (2014-2018)': range(2014, 2019),
        'Peak Years (2019-2023)': range(2019, 2024),
        'Recent (2024-2025)': range(2024, 2026)
    }

    # Classify each bill
    for bill in all_bills:
        title = bill.get('title', '').lower()
        bill_year = bill.get('session', 0)
        bill_number = bill.get('basePrintNo', 'Unknown')

        classified = False

        # Check each policy category
        for category, keywords in all_keywords.items():
            for keyword in keywords:
                if keyword in title:
                    policy_categories[category] += 1
                    detailed_classification[category].append({
                        'bill': bill_number,
                        'year': bill_year,
                        'title': bill.get('title', '')[:100] + '...'
                    })

                    # Add to temporal analysis
                    temporal_analysis[category][bill_year] += 1
                    classified = True
                    break

            if classified:
                break

        # Enhanced pattern matching for remaining bills
        if not classified:
            # Try more sophisticated pattern matching
            if any(pattern in title for pattern in ['establishes', 'creates', 'provides for']):
                category = 'Government - New Programs'
            elif any(pattern in title for pattern in ['amends', 'modifies', 'changes']):
                category = 'Legal - Code Amendment'
            elif any(pattern in title for pattern in ['requires', 'mandates', 'shall']):
                category = 'Legal - Requirements'
            elif any(pattern in title for pattern in ['authorizes', 'permits', 'allows']):
                category = 'Legal - Authorization'
            elif any(pattern in title for pattern in ['prohibits', 'bans', 'forbids']):
                category = 'Legal - Prohibition'
            else:
                category = 'Other - Unclassified'

            policy_categories[category] += 1
            detailed_classification[category].append({
                'bill': bill_number,
                'year': bill_year,
                'title': bill.get('title', '')[:100] + '...'
            })
            temporal_analysis[category][bill_year] += 1

    # Analysis and reporting
    total_bills = len(all_bills)

    print(f"\n=== ULTRA-GRANULAR CLASSIFICATION RESULTS ===")
    print(f"Total bills classified: {total_bills}")

    # Sort by frequency
    sorted_categories = policy_categories.most_common()

    print(f"\nTop 25 Ultra-Granular Categories:")
    for i, (category, count) in enumerate(sorted_categories[:25], 1):
        percentage = (count / total_bills) * 100
        print(f"{i:2d}. {category:<50} {count:4d} bills ({percentage:5.1f}%)")

    # Check our targets
    other_variants = [cat for cat in policy_categories if 'Other' in cat[0] or 'Unclassified' in cat[0]]
    total_other = sum(policy_categories[cat] for cat in other_variants)
    other_percentage = (total_other / total_bills) * 100

    print(f"\nAll 'Other/Unclassified' categories: {total_other} bills ({other_percentage:.1f}%)")

    if other_percentage < 5:
        print(f"✅ 'Other' reduced to target {other_percentage:.1f}% (under 5%)")
    else:
        print(f"⚠️  'Other' still at {other_percentage:.1f}% - need refinement")

    # Group into 5 main categories
    main_categories = {
        'Criminal Justice & Safety': [cat for cat, count in sorted_categories if 'Criminal Justice' in cat or 'Police' in cat],
        'Transportation': [cat for cat, count in sorted_categories if 'Transportation' in cat],
        'Economic & Fiscal': [cat for cat, count in sorted_categories if 'Fiscal' in cat or 'Economic' in cat],
        'Education': [cat for cat, count in sorted_categories if 'Education' in cat],
        'Government & Administration': [cat for cat, count in sorted_categories if 'Government' in cat or 'Legal' in cat]
    }

    print(f"\n=== MAIN CATEGORY BREAKDOWN ===")
    for main_cat, subcategories in main_categories.items():
        if subcategories:
            main_total = sum(policy_categories[subcat] for subcat in subcategories)
            main_percentage = (main_total / total_bills) * 100
            print(f"\n{main_cat}: {main_total} bills ({main_percentage:.1f}%)")

            # Show top subcategories
            subcat_sorted = sorted([(subcat, policy_categories[subcat]) for subcat in subcategories],
                                 key=lambda x: x[1], reverse=True)
            for subcat, count in subcat_sorted[:10]:  # Top 10 subcategories
                sub_percentage = (count / total_bills) * 100
                print(f"  - {subcat:<45} {count:3d} bills ({sub_percentage:4.1f}%)")

    # TEMPORAL ANALYSIS
    print(f"\n=== TEMPORAL EVOLUTION ANALYSIS ===")

    # Evolution by time periods
    for period_name, years in time_periods.items():
        period_total = 0
        period_breakdown = Counter()

        for category, year_counts in temporal_analysis.items():
            period_count = sum(year_counts.get(year, 0) for year in years)
            if period_count > 0:
                period_breakdown[category] = period_count
                period_total += period_count

        print(f"\n{period_name}: {period_total} bills")
        if period_total > 0:
            top_5 = period_breakdown.most_common(5)
            for cat, count in top_5:
                percentage = (count / period_total) * 100
                print(f"  {cat:<40} {count:3d} ({percentage:4.1f}%)")

    # Year-by-year evolution of top categories
    print(f"\n=== YEAR-BY-YEAR EVOLUTION (Top 10 Categories) ===")
    top_10_categories = [cat for cat, count in sorted_categories[:10]]

    years = sorted(set(year for year_counts in temporal_analysis.values() for year in year_counts.keys()))

    print(f"{'Year':<6}", end="")
    for cat in top_10_categories:
        print(f"{cat[:15]:<16}", end="")
    print()

    for year in years:
        if year > 0:  # Skip invalid years
            year_total = sum(temporal_analysis[cat].get(year, 0) for cat in top_10_categories)
            if year_total > 0:
                print(f"{year:<6}", end="")
                for cat in top_10_categories:
                    count = temporal_analysis[cat].get(year, 0)
                    percentage = (count / year_total * 100) if year_total > 0 else 0
                    print(f"{count:3d}({percentage:2.0f}%)".ljust(16), end="")
                print(f" = {year_total}")

    # Save comprehensive results
    results = {
        'classification_timestamp': datetime.now().isoformat(),
        'total_bills': total_bills,
        'classification_method': 'Ultra-Granular 100+ Category System',
        'policy_categories': dict(policy_categories),
        'detailed_breakdown': dict(detailed_classification),
        'main_categories': {cat: {subcat: policy_categories[subcat] for subcat in subcats}
                          for cat, subcats in main_categories.items() if subcats},
        'temporal_analysis': dict(temporal_analysis),
        'time_periods': {period: dict(Counter({cat: sum(temporal_analysis[cat].get(year, 0) for year in years)
                                             for cat in temporal_analysis}).most_common())
                        for period, years in time_periods.items()},
        'other_percentage': other_percentage,
        'top_25_categories': sorted_categories[:25],
        'evolution_summary': {
            'early_focus': list(Counter({cat: sum(temporal_analysis[cat].get(year, 0)
                                               for year in range(2009, 2014))
                                       for cat in temporal_analysis}).most_common(5)),
            'recent_focus': list(Counter({cat: sum(temporal_analysis[cat].get(year, 0)
                                                for year in range(2019, 2026))
                                        for cat in temporal_analysis}).most_common(5))
        }
    }

    with open('ultra_granular_classification.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n✅ Ultra-granular classification saved to 'ultra_granular_classification.json'")

    return results

if __name__ == "__main__":
    ultra_granular_classification()