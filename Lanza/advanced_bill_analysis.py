import json
from datetime import datetime
from collections import Counter, defaultdict
import re

def analyze_bill_content():
    """Deep analysis of bill content, patterns, and legislative strategy"""

    # Load bill details
    bill_files = [
        ("S5914", 2025, "bill_S5914_2025.json"),
        ("S7356", 2025, "bill_S7356_2025.json"),
        ("S2589", 2017, "bill_S2589_2017.json"),
        ("S5988A", 2017, "bill_S5988A_2017.json"),
        ("S8874", 2017, "bill_S8874_2017.json")
    ]

    analysis = {
        'timestamp': datetime.now().isoformat(),
        'bills_analyzed': [],
        'patterns': {
            'committee_pathway': {},
            'legislative_complexity': {},
            'policy_areas': {},
            'strategic_timing': {},
            'bill_relationships': {}
        },
        'insights': [],
        'updated_profile_data': {}
    }

    bills_data = []

    for bill_no, session, filename in bill_files:
        try:
            with open(filename, 'r') as f:
                bill_data = json.load(f)

            if bill_data.get('success'):
                bill = bill_data['result']
                bills_data.append(bill)
                analysis['bills_analyzed'].append({
                    'bill_no': bill_no,
                    'session': session,
                    'title': bill.get('title'),
                    'status': bill.get('status', {}).get('statusDesc')
                })

        except FileNotFoundError:
            print(f"Warning: {filename} not found")

    if not bills_data:
        print("No bill data found for analysis")
        return None

    # Pattern Analysis

    # 1. Committee Pathway Analysis
    committee_patterns = defaultdict(list)
    for bill in bills_data:
        status = bill.get('status', {})
        committee = status.get('committeeName')
        if committee:
            committee_patterns[committee].append({
                'bill': bill.get('basePrintNo'),
                'title': bill.get('title'),
                'status': status.get('statusDesc')
            })

    analysis['patterns']['committee_pathway'] = dict(committee_patterns)

    # 2. Legislative Complexity Analysis
    complexity_analysis = {}
    for bill in bills_data:
        bill_no = bill.get('basePrintNo')

        # Analyze memo content
        amendments = bill.get('amendments', {}).get('items', {})
        memo_text = ""
        if amendments:
            first_amendment = list(amendments.values())[0]
            memo_text = first_amendment.get('memo', '')

        # Complexity indicators
        complexity_score = 0
        complexity_factors = []

        if len(memo_text) > 2000:
            complexity_score += 2
            complexity_factors.append("Detailed memo")

        if 'prior legislative history' in memo_text.lower():
            prior_versions = memo_text.lower().split('prior legislative history')[1]
            version_count = len(re.findall(r'\d{4}:', prior_versions))
            complexity_score += min(version_count, 5)
            complexity_factors.append(f"Multiple versions ({version_count})")

        if bill.get('previousVersions', {}).get('size', 0) > 0:
            complexity_score += 1
            complexity_factors.append("Previous versions exist")

        complexity_analysis[bill_no] = {
            'score': complexity_score,
            'factors': complexity_factors,
            'memo_length': len(memo_text)
        }

    analysis['patterns']['legislative_complexity'] = complexity_analysis

    # 3. Policy Areas Deep Dive
    policy_classification = {}
    for bill in bills_data:
        bill_no = bill.get('basePrintNo')
        title = bill.get('title', '').lower()
        memo = ""

        amendments = bill.get('amendments', {}).get('items', {})
        if amendments:
            first_amendment = list(amendments.values())[0]
            memo = first_amendment.get('memo', '').lower()

        # Enhanced classification
        categories = []
        subcategories = []

        # Human Trafficking
        if any(term in title + memo for term in ['trafficking', 'sex trafficking', 'victim']):
            categories.append('Human Trafficking')
            if 'child' in title + memo:
                subcategories.append('Child Protection')
            if 'conviction' in title + memo:
                subcategories.append('Criminal Justice Reform')
            if 'victim services' in title + memo:
                subcategories.append('Victim Support')

        # Animal Welfare
        if any(term in title + memo for term in ['animal', 'companion', 'pet']):
            categories.append('Animal Welfare')
            if 'emergency' in title + memo:
                subcategories.append('Emergency Services')
            if 'transportation' in title + memo:
                subcategories.append('Public Transportation Access')

        # Transportation/Consumer Protection
        if any(term in title + memo for term in ['license', 'driver', 'fee', 'vehicle']):
            categories.append('Transportation/Consumer Protection')
            if 'enhanced' in title + memo:
                subcategories.append('Enhanced Documentation')
            if 'fee' in title + memo:
                subcategories.append('Fee Relief')

        policy_classification[bill_no] = {
            'primary_categories': categories,
            'subcategories': subcategories,
            'policy_innovation': 'enhanced' in title or 'new' in memo
        }

    analysis['patterns']['policy_areas'] = policy_classification

    # 4. Strategic Timing Analysis
    timing_patterns = {}
    for bill in bills_data:
        bill_no = bill.get('basePrintNo')
        session = bill.get('session')
        publish_date = bill.get('publishedDateTime', '')

        # Check for bill reintroduction patterns
        previous_versions = bill.get('previousVersions', {}).get('items', [])
        timing_patterns[bill_no] = {
            'session': session,
            'publish_date': publish_date,
            'reintroduction_count': len(previous_versions),
            'persistence_indicator': len(previous_versions) > 2,
            'previous_sessions': [v.get('session') for v in previous_versions]
        }

    analysis['patterns']['strategic_timing'] = timing_patterns

    # 5. Bill Relationships
    relationships = {}
    for bill in bills_data:
        bill_no = bill.get('basePrintNo')
        title = bill.get('title', '').lower()

        related_themes = []
        if 'trafficking' in title:
            related_themes.append('anti-trafficking-initiative')
        if 'animal' in title:
            related_themes.append('animal-welfare-initiative')
        if 'fee' in title or 'license' in title:
            related_themes.append('consumer-protection-initiative')

        relationships[bill_no] = {
            'thematic_groups': related_themes,
            'legislative_session': bill.get('session'),
            'status_progression': bill.get('status', {}).get('statusType')
        }

    analysis['patterns']['bill_relationships'] = relationships

    # Generate Strategic Insights
    insights = []

    # Persistence insight
    persistent_bills = [bill for bill, data in timing_patterns.items() if data['persistence_indicator']]
    if persistent_bills:
        insights.append({
            'type': 'Legislative Persistence',
            'description': f"Shows long-term commitment to key issues with {len(persistent_bills)} bills reintroduced multiple times",
            'bills': persistent_bills,
            'strategic_value': 'Demonstrates sustained policy focus and determination'
        })

    # Thematic expertise
    trafficking_bills = [bill for bill, data in policy_classification.items() if 'Human Trafficking' in data['primary_categories']]
    if len(trafficking_bills) >= 2:
        insights.append({
            'type': 'Subject Matter Expertise',
            'description': f"Recognized expert in anti-human trafficking legislation with {len(trafficking_bills)} related bills",
            'bills': trafficking_bills,
            'strategic_value': 'Establishes policy leadership credentials'
        })

    # Committee strategy
    committee_diversity = len(set(committee_patterns.keys()))
    insights.append({
        'type': 'Committee Strategy',
        'description': f"Strategic committee placement across {committee_diversity} committees",
        'committees': list(committee_patterns.keys()),
        'strategic_value': 'Demonstrates legislative process expertise'
    })

    analysis['insights'] = insights

    # Updated Profile Data
    analysis['updated_profile_data'] = {
        'bills_count': len(bills_data),
        'sessions_active': list(set(bill.get('session') for bill in bills_data)),
        'primary_expertise_areas': ['Anti-Human Trafficking', 'Animal Welfare', 'Consumer Protection'],
        'committee_experience': list(committee_patterns.keys()),
        'legislative_persistence_score': len([bill for bill, data in timing_patterns.items() if data['persistence_indicator']]),
        'policy_innovation_indicators': len([bill for bill, data in policy_classification.items() if data['policy_innovation']])
    }

    return analysis

def main():
    print("=== ADVANCED BILL ANALYSIS ===")
    analysis = analyze_bill_content()

    if analysis:
        # Save analysis
        with open('advanced_bill_analysis.json', 'w') as f:
            json.dump(analysis, f, indent=2, default=str)

        print("✓ Completed advanced bill content analysis")
        print(f"✓ Analyzed {len(analysis['bills_analyzed'])} bills")
        print(f"✓ Generated {len(analysis['insights'])} strategic insights")
        print(f"✓ Identified {len(analysis['patterns']['committee_pathway'])} committee pathways")
        print("✓ Saved to advanced_bill_analysis.json")

        # Print key insights
        print("\n=== KEY INSIGHTS ===")
        for insight in analysis['insights']:
            print(f"• {insight['type']}: {insight['description']}")

        return analysis
    else:
        print("✗ Analysis failed - no data available")
        return None

if __name__ == "__main__":
    main()