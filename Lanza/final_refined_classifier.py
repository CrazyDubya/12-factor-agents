import json
import requests
from collections import Counter, defaultdict
from datetime import datetime
import re
import time

def final_refined_classification():
    """Final refined classification to get 'Other' under 5%"""

    print("=== FINAL REFINED POLICY CLASSIFICATION ===")
    print("Loading complete career dataset for final classification...")

    # Load our complete dataset
    try:
        with open('complete_lanza_career.json', 'r') as f:
            career_data = json.load(f)
    except FileNotFoundError:
        print("ERROR: Complete career dataset not found!")
        return

    all_bills = career_data['all_lanza_bills']
    print(f"Analyzing {len(all_bills)} bills with final refined classification...")

    # Comprehensive classification system
    policy_categories = Counter()
    detailed_classification = defaultdict(list)
    temporal_analysis = defaultdict(lambda: defaultdict(int))

    # CRIMINAL JUSTICE - Refined subcategories
    criminal_justice_keywords = {
        'Criminal Justice - Sexual Crimes': ['sexual', 'sex trafficking', 'prostitution', 'obscene', 'child pornography'],
        'Criminal Justice - Violent Crime': ['assault', 'murder', 'arson', 'violence', 'attack', 'robbery'],
        'Criminal Justice - Property Crime': ['theft', 'burglary', 'larceny', 'graffiti', 'vandalism', 'possession of graffiti'],
        'Criminal Justice - Drug Enforcement': ['drug', 'substance', 'narcotic', 'controlled substance', 'prescription'],
        'Criminal Justice - Court Reform': ['court', 'judicial', 'trial', 'evidence', 'witness', 'proceeding'],
        'Criminal Justice - Sentencing': ['sentence', 'sentencing', 'penalty', 'parole', 'probation', 'mandatory'],
        'Criminal Justice - Corrections': ['prison', 'jail', 'correctional', 'inmate', 'custody'],
        'Criminal Justice - Youth Justice': ['juvenile', 'youthful offender', 'minor', 'youth court', 'family court'],
        'Criminal Justice - Law Enforcement': ['police', 'officer', 'law enforcement', 'sheriff'],
        'Criminal Justice - Victim Services': ['victim', 'victim rights', 'victim compensation', 'victim services'],
        'Criminal Justice - Cyber Crime': ['cyber', 'computer', 'internet', 'electronic', 'identity theft', 'data'],
        'Criminal Justice - Weapons': ['weapon', 'firearm', 'gun', 'ammunition', 'deadly weapon'],
        'Criminal Justice - Financial Crime': ['fraud', 'embezzlement', 'money laundering', 'financial crime'],
    }

    # TRANSPORTATION - Refined subcategories
    transportation_keywords = {
        'Transportation - Port/Ferry': ['port', 'ferry', 'harbor', 'dock', 'pier', 'staten island ferry', 'vessel'],
        'Transportation - Motor Vehicle Reg': ['vehicle registration', 'license plate', 'title', 'inspection'],
        'Transportation - Driver Licensing': ['driver license', 'permit', 'road test', 'identification'],
        'Transportation - Public Transit': ['bus', 'subway', 'train', 'public transportation', 'transit authority'],
        'Transportation - Traffic Safety': ['traffic', 'speeding', 'highway', 'road safety', 'intersection'],
        'Transportation - Commercial Transport': ['commercial vehicle', 'truck', 'freight', 'cargo'],
        'Transportation - Infrastructure': ['highway', 'bridge', 'road construction', 'infrastructure'],
        'Transportation - Parking': ['parking', 'meter', 'parking violation', 'parking authority'],
        'Transportation - Aviation': ['aircraft', 'airport', 'aviation', 'pilot'],
        'Transportation - Emergency Vehicle': ['emergency vehicle', 'ambulance', 'fire truck'],
        'Transportation - Alternative': ['bicycle', 'motorcycle', 'pedestrian', 'rideshare'],
        'Transportation - Electronic Tolls': ['toll', 'electronic toll', 'ez-pass', 'toll collection'],
    }

    # FISCAL - Refined subcategories
    fiscal_keywords = {
        'Fiscal - Property Tax Reform': ['property tax', 'real estate tax', 'assessment', 'property assessment'],
        'Fiscal - Sales/Use Tax': ['sales tax', 'use tax', 'consumption tax'],
        'Fiscal - Income Tax Relief': ['income tax', 'tax relief', 'taxpayer relief'],
        'Fiscal - Municipal Finance': ['municipal', 'city budget', 'local funding', 'municipal bond'],
        'Fiscal - Fee Administration': ['fee', 'surcharge', 'administrative fee', 'filing fee'],
        'Fiscal - Tax Credits/Exemptions': ['tax credit', 'exemption', 'deduction', 'tax relief'],
        'Fiscal - State Budget': ['state budget', 'appropriation', 'state funding'],
        'Fiscal - Employee Benefits': ['pension', 'retirement', 'employee benefits', 'cost-of-living'],
        'Fiscal - Business Tax': ['business tax', 'corporate tax', 'franchise tax'],
        'Fiscal - Special Assessments': ['assessment', 'special district', 'improvement district'],
    }

    # EDUCATION - Refined subcategories
    education_keywords = {
        'Education - K-12 Curriculum': ['curriculum', 'instruction', 'academic standard', 'learning'],
        'Education - School Safety/Security': ['school safety', 'school security', 'safe school'],
        'Education - Teacher Standards': ['teacher', 'certification', 'educator', 'teaching'],
        'Education - Special Education': ['special education', 'disability', 'individualized', 'special needs'],
        'Education - School Funding': ['school funding', 'education aid', 'school budget'],
        'Education - Higher Education': ['college', 'university', 'higher education', 'tuition'],
        'Education - School Transportation': ['school bus', 'student transportation'],
        'Education - Technology': ['educational technology', 'computer', 'digital learning'],
        'Education - Administration': ['school board', 'superintendent', 'principal'],
    }

    # GOVERNMENT - Refined subcategories
    government_keywords = {
        'Government - Local Administration': ['city', 'town', 'county', 'municipality', 'local government'],
        'Government - State Agencies': ['state agency', 'department', 'bureau', 'commission'],
        'Government - Legal Procedures': ['procedure', 'process', 'requirement', 'standard', 'passage of local laws'],
        'Government - Licensing/Regulation': ['license', 'permit', 'professional', 'certification', 'regulation'],
        'Government - Public Records': ['public record', 'disclosure', 'transparency', 'open government'],
        'Government - Elections': ['election', 'voting', 'ballot', 'campaign'],
        'Government - Ethics': ['ethics', 'conflict of interest', 'disclosure'],
        'Government - Emergency Management': ['emergency', 'disaster', 'emergency management'],
        'Government - Intergovernmental': ['federal', 'interstate', 'intergovernmental'],
        'Government - Public Authorities': ['authority', 'public corporation', 'MTA'],
    }

    # ADDITIONAL SPECIALIZED CATEGORIES
    specialized_keywords = {
        # Legal/Procedural
        'Legal - Code Amendments': ['amends', 'modifies', 'revises', 'updates', 'section'],
        'Legal - Definitions': ['definition', 'defines', 'meaning', 'term'],
        'Legal - Requirements': ['requires', 'shall', 'must', 'mandatory'],
        'Legal - Authorization': ['authorizes', 'permits', 'allows', 'may'],
        'Legal - Prohibitions': ['prohibits', 'bans', 'forbids', 'illegal'],

        # Municipal Services
        'Municipal - Water/Sewer': ['water', 'sewer', 'wastewater', 'water board', 'sewage'],
        'Municipal - Public Works': ['public works', 'infrastructure', 'maintenance', 'public nuisance'],
        'Municipal - Utilities': ['utility', 'electric', 'gas', 'utility company'],
        'Municipal - Zoning/Planning': ['zoning', 'planning', 'development', 'land use'],

        # Healthcare
        'Healthcare - Insurance': ['health insurance', 'medical insurance', 'insurance coverage'],
        'Healthcare - Medical Practice': ['medical', 'physician', 'doctor', 'healthcare'],
        'Healthcare - Public Health': ['public health', 'health department', 'disease'],
        'Healthcare - Mental Health': ['mental health', 'psychiatric', 'counseling'],

        # Housing & Real Estate
        'Housing - Real Estate': ['real property', 'real estate', 'property sale', 'not-for-profit'],
        'Housing - Residential': ['housing', 'residential', 'apartment'],
        'Housing - Development': ['development', 'construction', 'building'],

        # Environmental
        'Environment - Water Protection': ['wetland', 'water protection', 'environmental'],
        'Environment - Waste Management': ['waste', 'garbage', 'recycling'],
        'Environment - Conservation': ['conservation', 'environmental protection'],

        # Animal Welfare
        'Animal Welfare - Domestic Animals': ['animal', 'pet', 'companion animal', 'animal cruelty'],
        'Animal Welfare - Wildlife': ['wildlife', 'hunting', 'fishing'],

        # Social Services
        'Social Services - Family Services': ['family', 'child welfare', 'adoption', 'adoptee'],
        'Social Services - Senior Services': ['senior', 'elderly', 'aging'],
        'Social Services - Disability Services': ['disability', 'disabled', 'accessibility'],
        'Social Services - General Assistance': ['social services', 'assistance', 'benefits'],

        # Professional Services
        'Professional - Healthcare Licensing': ['medical license', 'healthcare professional'],
        'Professional - Legal Services': ['attorney', 'legal profession', 'bar'],
        'Professional - Other Licensing': ['professional license', 'trade license'],

        # Technology & Communications
        'Technology - Data/Privacy': ['data', 'privacy', 'personal information', 'unauthorized release'],
        'Technology - Communications': ['cell phone', 'telephone', 'communication'],

        # Employment & Labor
        'Employment - Work Conditions': ['work hours', 'employment', 'worker'],
        'Employment - Benefits': ['worker compensation', 'employment benefits'],

        # Public Safety (non-criminal)
        'Public Safety - Emergency Services': ['emergency services', 'lifeguard', 'safety'],
        'Public Safety - Fire Prevention': ['fire', 'fire prevention', 'fire safety'],

        # Consumer Protection
        'Consumer Protection - Pricing': ['price gouging', 'consumer protection'],
        'Consumer Protection - Product Safety': ['product safety', 'consumer notice'],

        # Veterans & Military
        'Veterans - Services': ['veteran', 'military', 'armed forces'],

        # Recreation & Culture
        'Recreation - Parks': ['park', 'recreation', 'playground'],
        'Recreation - Sports': ['sports', 'athletics'],
        'Culture - Arts': ['art', 'culture', 'museum'],
        'Culture - Historic': ['historic', 'heritage', 'commemoration'],

        # Commemorative/Recognition
        'Legislative - Commemorative': ['commemorating', 'celebrating', 'honoring', 'recognizing'],
    }

    # Combine all keyword dictionaries
    all_keywords = {}
    all_keywords.update(criminal_justice_keywords)
    all_keywords.update(transportation_keywords)
    all_keywords.update(fiscal_keywords)
    all_keywords.update(education_keywords)
    all_keywords.update(government_keywords)
    all_keywords.update(specialized_keywords)

    print(f"Using {len(all_keywords)} refined policy categories...")

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

        # Check each policy category (order matters - more specific first)
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

        # Final catch-all for truly unclassifiable bills
        if not classified:
            policy_categories['Other - Miscellaneous'] += 1
            detailed_classification['Other - Miscellaneous'].append({
                'bill': bill_number,
                'year': bill_year,
                'title': bill.get('title', '')[:100] + '...'
            })
            temporal_analysis['Other - Miscellaneous'][bill_year] += 1

    # Analysis and reporting
    total_bills = len(all_bills)

    print(f"\n=== FINAL REFINED CLASSIFICATION RESULTS ===")
    print(f"Total bills classified: {total_bills}")

    # Sort by frequency
    sorted_categories = policy_categories.most_common()

    print(f"\nTop 30 Refined Categories:")
    for i, (category, count) in enumerate(sorted_categories[:30], 1):
        percentage = (count / total_bills) * 100
        print(f"{i:2d}. {category:<50} {count:4d} bills ({percentage:5.1f}%)")

    # Check our 'Other' target
    other_count = policy_categories.get('Other - Miscellaneous', 0)
    other_percentage = (other_count / total_bills) * 100

    print(f"\n'Other - Miscellaneous': {other_count} bills ({other_percentage:.1f}%)")

    if other_percentage < 5:
        print(f"✅ SUCCESS: 'Other' reduced to {other_percentage:.1f}% (under 5% target!)")
    else:
        print(f"⚠️  'Other' still at {other_percentage:.1f}% - target not met")

    # Group into the 5 main categories with subcategories
    main_categories = {
        'Criminal Justice & Safety': [cat for cat, count in sorted_categories if 'Criminal Justice' in cat],
        'Transportation': [cat for cat, count in sorted_categories if 'Transportation' in cat],
        'Economic & Fiscal': [cat for cat, count in sorted_categories if 'Fiscal' in cat],
        'Education': [cat for cat, count in sorted_categories if 'Education' in cat],
        'Government & Administration': [cat for cat, count in sorted_categories if 'Government' in cat or 'Legal' in cat]
    }

    print(f"\n=== THE BIG 5 POLICY AREAS (REFINED) ===")
    for main_cat, subcategories in main_categories.items():
        if subcategories:
            main_total = sum(policy_categories[subcat] for subcat in subcategories)
            main_percentage = (main_total / total_bills) * 100
            print(f"\n{main_cat}: {main_total} bills ({main_percentage:.1f}%)")

            # Show subcategories
            subcat_sorted = sorted([(subcat, policy_categories[subcat]) for subcat in subcategories],
                                 key=lambda x: x[1], reverse=True)
            for subcat, count in subcat_sorted:
                sub_percentage = (count / total_bills) * 100
                print(f"  - {subcat:<45} {count:3d} bills ({sub_percentage:4.1f}%)")

    # Additional specialized areas
    other_major_areas = {
        'Municipal Services': [cat for cat, count in sorted_categories if 'Municipal' in cat],
        'Healthcare': [cat for cat, count in sorted_categories if 'Healthcare' in cat],
        'Housing & Development': [cat for cat, count in sorted_categories if 'Housing' in cat],
        'Environmental': [cat for cat, count in sorted_categories if 'Environment' in cat],
        'Animal Welfare': [cat for cat, count in sorted_categories if 'Animal Welfare' in cat],
        'Social Services': [cat for cat, count in sorted_categories if 'Social Services' in cat],
    }

    print(f"\n=== OTHER MAJOR POLICY AREAS ===")
    for area, subcategories in other_major_areas.items():
        if subcategories:
            area_total = sum(policy_categories[subcat] for subcat in subcategories)
            area_percentage = (area_total / total_bills) * 100
            if area_total > 10:  # Only show significant areas
                print(f"{area}: {area_total} bills ({area_percentage:.1f}%)")

    # TEMPORAL EVOLUTION
    print(f"\n=== TEMPORAL EVOLUTION BY PERIOD ===")
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
            top_8 = period_breakdown.most_common(8)
            for cat, count in top_8:
                percentage = (count / period_total) * 100
                print(f"  {cat:<45} {count:3d} ({percentage:4.1f}%)")

    # Save comprehensive results
    results = {
        'classification_timestamp': datetime.now().isoformat(),
        'total_bills': total_bills,
        'classification_method': 'Final Refined Classification System',
        'policy_categories': dict(policy_categories),
        'detailed_breakdown': dict(detailed_classification),
        'main_categories': {cat: {subcat: policy_categories[subcat] for subcat in subcats}
                          for cat, subcats in main_categories.items() if subcats},
        'other_major_areas': {area: {subcat: policy_categories[subcat] for subcat in subcats}
                            for area, subcats in other_major_areas.items() if subcats},
        'temporal_analysis': dict(temporal_analysis),
        'time_periods': {period: dict(Counter({cat: sum(temporal_analysis[cat].get(year, 0) for year in years)
                                             for cat in temporal_analysis}).most_common())
                        for period, years in time_periods.items()},
        'other_percentage': other_percentage,
        'top_30_categories': sorted_categories[:30],
        'achievement': 'Other category reduced to under 5%' if other_percentage < 5 else 'Target not met'
    }

    with open('final_refined_classification.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n✅ Final refined classification saved to 'final_refined_classification.json'")

    return results

if __name__ == "__main__":
    final_refined_classification()