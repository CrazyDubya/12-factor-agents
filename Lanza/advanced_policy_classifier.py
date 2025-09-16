import json
import requests
from collections import Counter, defaultdict
from datetime import datetime
import re
import time

def enhanced_policy_classification():
    """Advanced classification with 50+ policy categories"""

    print("=== ADVANCED POLICY CLASSIFICATION ===")
    print("Loading complete career dataset for deep policy analysis...")

    # Load our complete dataset
    try:
        with open('complete_lanza_career.json', 'r') as f:
            career_data = json.load(f)
    except FileNotFoundError:
        print("ERROR: Complete career dataset not found!")
        return

    all_bills = career_data['all_lanza_bills']
    print(f"Analyzing {len(all_bills)} bills with enhanced classification...")

    # Enhanced classification system with 50+ categories
    policy_categories = Counter()
    detailed_classification = defaultdict(list)

    # Define comprehensive policy keywords
    policy_keywords = {
        # Criminal Justice & Public Safety (expanded)
        'Criminal Justice - General': ['criminal', 'crime', 'penalty', 'sentence', 'conviction', 'felony', 'misdemeanor'],
        'Criminal Justice - Trafficking': ['trafficking', 'human trafficking', 'sex trafficking', 'exploitation', 'victim'],
        'Criminal Justice - Drug Crimes': ['drug', 'substance', 'narcotic', 'controlled substance', 'prescription'],
        'Criminal Justice - Violent Crime': ['assault', 'murder', 'rape', 'violence', 'domestic violence', 'battery'],
        'Criminal Justice - Cyber Crime': ['cyber', 'computer', 'internet', 'electronic', 'identity theft'],
        'Criminal Justice - Juvenile': ['juvenile', 'minor', 'child', 'youth', 'adolescent'],
        'Public Safety': ['safety', 'emergency', 'disaster', 'security', 'protection'],
        'Law Enforcement': ['police', 'officer', 'law enforcement', 'sheriff', 'detective'],

        # Transportation (expanded)
        'Transportation - Motor Vehicle': ['vehicle', 'motor', 'automobile', 'car', 'truck', 'motorcycle'],
        'Transportation - Driver License': ['driver', 'license', 'permit', 'registration', 'identification'],
        'Transportation - Traffic': ['traffic', 'highway', 'road', 'street', 'intersection'],
        'Transportation - Public Transit': ['transit', 'bus', 'subway', 'train', 'transportation authority'],
        'Transportation - Commercial': ['commercial vehicle', 'truck', 'freight', 'cargo', 'logistics'],
        'Transportation - Aviation': ['aircraft', 'airport', 'aviation', 'pilot', 'flight'],
        'Transportation - Maritime': ['vessel', 'boat', 'ship', 'port', 'maritime', 'ferry'],

        # Education (expanded)
        'Education - K-12': ['school', 'student', 'teacher', 'education', 'classroom', 'curriculum'],
        'Education - Higher Ed': ['college', 'university', 'higher education', 'tuition', 'degree'],
        'Education - Special Ed': ['special education', 'disability', 'individualized', 'special needs'],
        'Education - Funding': ['school funding', 'education funding', 'school budget', 'education aid'],
        'Education - Administration': ['school board', 'superintendent', 'principal', 'administration'],

        # Healthcare (expanded)
        'Healthcare - General': ['health', 'medical', 'hospital', 'healthcare', 'medicine'],
        'Healthcare - Insurance': ['insurance', 'coverage', 'premium', 'deductible', 'copay'],
        'Healthcare - Mental Health': ['mental health', 'psychiatric', 'psychology', 'counseling', 'therapy'],
        'Healthcare - Public Health': ['public health', 'epidemic', 'vaccination', 'immunization', 'disease'],
        'Healthcare - Long-term Care': ['nursing home', 'assisted living', 'elder care', 'hospice'],
        'Healthcare - Emergency Medical': ['emergency medical', 'ambulance', 'paramedic', 'emergency room'],

        # Economic & Fiscal (expanded)
        'Fiscal - Taxation': ['tax', 'levy', 'assessment', 'property tax', 'income tax'],
        'Fiscal - Budget': ['budget', 'appropriation', 'funding', 'expenditure', 'allocation'],
        'Fiscal - Revenue': ['revenue', 'fee', 'fine', 'penalty', 'surcharge'],
        'Economic Development': ['economic', 'development', 'business', 'commerce', 'industry'],
        'Banking & Finance': ['bank', 'financial', 'credit', 'loan', 'mortgage'],

        # Housing & Development
        'Housing': ['housing', 'residential', 'apartment', 'rent', 'landlord', 'tenant'],
        'Urban Planning': ['zoning', 'planning', 'development', 'construction', 'building code'],
        'Real Estate': ['real estate', 'property', 'deed', 'title', 'appraisal'],

        # Environment & Energy
        'Environmental': ['environment', 'environmental', 'pollution', 'clean', 'conservation'],
        'Energy': ['energy', 'electric', 'utility', 'renewable', 'solar', 'wind'],
        'Water': ['water', 'sewer', 'wastewater', 'drinking water', 'aquifer'],

        # Social Services
        'Social Services': ['social service', 'welfare', 'assistance', 'benefits', 'support'],
        'Child Welfare': ['child welfare', 'foster', 'adoption', 'child protection', 'family services'],
        'Senior Services': ['senior', 'elderly', 'aging', 'retirement', 'medicare'],
        'Disability Services': ['disability', 'disabled', 'handicapped', 'accessibility', 'accommodation'],

        # Animal Welfare
        'Animal Welfare': ['animal', 'pet', 'companion animal', 'veterinary', 'animal cruelty'],
        'Agriculture': ['agriculture', 'farm', 'farming', 'livestock', 'crop'],

        # Government Operations
        'Government - Ethics': ['ethics', 'conflict of interest', 'disclosure', 'transparency'],
        'Government - Elections': ['election', 'voting', 'ballot', 'campaign', 'political'],
        'Government - Administrative': ['administrative', 'bureaucracy', 'agency', 'department'],
        'Government - Local': ['local government', 'municipality', 'county', 'city', 'town'],

        # Professional Regulation
        'Professional Licensing': ['license', 'professional', 'certification', 'board', 'practice'],
        'Business Regulation': ['business', 'commercial', 'trade', 'industry', 'regulation'],

        # Technology & Communications
        'Technology': ['technology', 'computer', 'software', 'digital', 'information'],
        'Communications': ['communication', 'telephone', 'internet', 'broadband', 'wireless'],

        # Recreation & Culture
        'Recreation': ['recreation', 'park', 'sports', 'leisure', 'entertainment'],
        'Culture & Arts': ['art', 'culture', 'museum', 'library', 'historic'],

        # Military & Veterans
        'Veterans Affairs': ['veteran', 'military', 'armed forces', 'service member'],
    }

    print(f"Using {len(policy_keywords)} detailed policy categories...")

    # Classify each bill
    for bill in all_bills:
        title = bill.get('title', '').lower()
        bill_year = bill.get('session', 'Unknown')
        bill_number = bill.get('basePrintNo', 'Unknown')

        classified = False

        # Check each policy category
        for category, keywords in policy_keywords.items():
            for keyword in keywords:
                if keyword in title:
                    policy_categories[category] += 1
                    detailed_classification[category].append({
                        'bill': bill_number,
                        'year': bill_year,
                        'title': bill.get('title', '')[:100] + '...'
                    })
                    classified = True
                    break

            if classified:
                break

        # If still unclassified, put in "Other" but try some broader patterns
        if not classified:
            # Try some pattern matching for missed categories
            if any(word in title for word in ['act', 'law', 'code', 'statute']):
                policy_categories['Legal - General'] += 1
                detailed_classification['Legal - General'].append({
                    'bill': bill_number,
                    'year': bill_year,
                    'title': bill.get('title', '')[:100] + '...'
                })
            elif any(word in title for word in ['establish', 'create', 'fund']):
                policy_categories['Government - New Programs'] += 1
                detailed_classification['Government - New Programs'].append({
                    'bill': bill_number,
                    'year': bill_year,
                    'title': bill.get('title', '')[:100] + '...'
                })
            else:
                policy_categories['Other'] += 1
                detailed_classification['Other'].append({
                    'bill': bill_number,
                    'year': bill_year,
                    'title': bill.get('title', '')[:100] + '...'
                })

    # Analysis and reporting
    total_bills = len(all_bills)

    print(f"\n=== ENHANCED POLICY CLASSIFICATION RESULTS ===")
    print(f"Total bills classified: {total_bills}")

    # Sort by frequency
    sorted_categories = policy_categories.most_common()

    print(f"\nTop 20 Policy Categories:")
    for i, (category, count) in enumerate(sorted_categories[:20], 1):
        percentage = (count / total_bills) * 100
        print(f"{i:2d}. {category:<35} {count:4d} bills ({percentage:5.1f}%)")

    # Check our "Other" percentage
    other_count = policy_categories.get('Other', 0)
    other_percentage = (other_count / total_bills) * 100
    print(f"\n'Other' category: {other_count} bills ({other_percentage:.1f}%)")

    if other_percentage > 10:
        print(f"⚠️  'Other' still too high at {other_percentage:.1f}% - need more categories")
        print("\nSample 'Other' bills for analysis:")
        for bill in detailed_classification['Other'][:10]:
            print(f"  {bill['bill']} ({bill['year']}): {bill['title']}")
    else:
        print(f"✅ 'Other' reduced to acceptable {other_percentage:.1f}%")

    # Group related categories
    category_groups = {
        'Criminal Justice & Safety': [cat for cat in sorted_categories if 'Criminal Justice' in cat[0] or 'Public Safety' in cat[0] or 'Law Enforcement' in cat[0]],
        'Transportation': [cat for cat in sorted_categories if 'Transportation' in cat[0]],
        'Education': [cat for cat in sorted_categories if 'Education' in cat[0]],
        'Healthcare': [cat for cat in sorted_categories if 'Healthcare' in cat[0]],
        'Government & Administration': [cat for cat in sorted_categories if 'Government' in cat[0]],
        'Economic & Fiscal': [cat for cat in sorted_categories if 'Fiscal' in cat[0] or 'Economic' in cat[0] or 'Banking' in cat[0]],
    }

    print(f"\n=== POLICY AREA SUMMARY ===")
    for area, categories in category_groups.items():
        if categories:
            area_total = sum(cat[1] for cat in categories)
            area_percentage = (area_total / total_bills) * 100
            print(f"{area}: {area_total} bills ({area_percentage:.1f}%)")
            for cat, count in categories:
                sub_percentage = (count / total_bills) * 100
                print(f"  - {cat}: {count} bills ({sub_percentage:.1f}%)")

    # Save detailed results
    results = {
        'classification_timestamp': datetime.now().isoformat(),
        'total_bills': total_bills,
        'classification_method': 'Enhanced 50+ Category System',
        'policy_categories': dict(policy_categories),
        'detailed_breakdown': dict(detailed_classification),
        'category_groups': {area: {cat: count for cat, count in categories}
                          for area, categories in category_groups.items() if categories},
        'other_percentage': other_percentage,
        'top_20_categories': sorted_categories[:20]
    }

    with open('enhanced_policy_classification.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n✅ Enhanced classification saved to 'enhanced_policy_classification.json'")

    return results

if __name__ == "__main__":
    enhanced_policy_classification()