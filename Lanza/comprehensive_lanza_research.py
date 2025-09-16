import requests
import json
from datetime import datetime
from collections import defaultdict, Counter

API_KEY = "gNyGkkPgvKrEKXaq7OehFL5D65t4S7yM"
BASE_URL = "https://legislation.nysenate.gov/api/3"

def search_bills(term, limit=1000):
    """Search for bills using the working API endpoint"""
    url = f"{BASE_URL}/bills/search"
    params = {"term": term, "key": API_KEY, "limit": limit}

    try:
        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error searching bills: {e}")
    return None

def get_bill_details(bill_no, session):
    """Get detailed information for a specific bill"""
    url = f"{BASE_URL}/bills/{session}/{bill_no}"
    params = {"key": API_KEY}

    try:
        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error getting bill {bill_no}: {e}")
    return None

def analyze_lanza_legislation():
    """Comprehensive analysis of Senator Lanza's legislative record"""

    print("=== COMPREHENSIVE LANZA LEGISLATIVE RESEARCH ===")
    print(f"Timestamp: {datetime.now()}")
    print()

    # Search strategies
    search_terms = [
        "sponsor:lanza",
        "Lanza AND senate",
        "sponsor:\"Andrew Lanza\"",
        "sponsor:\"A. Lanza\"",
        "lanza trafficking",
        "lanza animal",
        "lanza staten island"
    ]

    all_bills = []
    bill_ids_seen = set()

    for term in search_terms:
        print(f"Searching: {term}")
        results = search_bills(term)

        if results and results.get('success'):
            bills = results.get('result', {}).get('items', [])
            print(f"  Found {len(bills)} bills")

            for bill in bills:
                bill_id = f"{bill.get('basePrintNo', '')}-{bill.get('session', '')}"
                if bill_id not in bill_ids_seen:
                    bill_ids_seen.add(bill_id)
                    all_bills.append(bill)

        else:
            print(f"  No results or error")
        print()

    print(f"Total unique bills found: {len(all_bills)}")

    # Detailed analysis
    if all_bills:
        print("\n=== BILL ANALYSIS ===")

        # Group by session year
        by_session = defaultdict(list)
        status_counts = Counter()
        keyword_analysis = defaultdict(int)
        committee_analysis = defaultdict(int)

        lanza_sponsored = []

        for bill in all_bills:
            session = bill.get('session')
            by_session[session].append(bill)

            # Check if Lanza is primary sponsor
            sponsor = bill.get('sponsor', {})
            if sponsor and isinstance(sponsor, dict):
                sponsor_member = sponsor.get('member', {})
                if sponsor_member and 'lanza' in sponsor_member.get('fullName', '').lower():
                    lanza_sponsored.append(bill)

            # Status analysis
            status = bill.get('status', {})
            status_type = status.get('statusType', 'Unknown')
            status_counts[status_type] += 1

            # Keyword analysis from title
            title = bill.get('title', '').lower()
            keywords = ['trafficking', 'animal', 'welfare', 'transportation', 'crime', 'emergency', 'license', 'victim', 'child', 'drug', 'abuse']
            for keyword in keywords:
                if keyword in title:
                    keyword_analysis[keyword] += 1

            # Committee analysis
            committee = status.get('committeeName')
            if committee:
                committee_analysis[committee] += 1

        print(f"Bills where Lanza is primary sponsor: {len(lanza_sponsored)}")
        print(f"Session distribution: {dict(Counter(by_session.keys()))}")
        print(f"Status distribution: {dict(status_counts)}")
        print(f"Top keywords: {dict(keyword_analysis.most_common(10))}")
        print(f"Top committees: {dict(committee_analysis.most_common(10))}")

        # Get detailed info for Lanza-sponsored bills
        print("\n=== LANZA-SPONSORED BILLS DETAILS ===")
        detailed_bills = []

        for bill in lanza_sponsored[:20]:  # Limit to prevent too many API calls
            bill_no = bill.get('basePrintNo')
            session = bill.get('session')

            if bill_no and session:
                print(f"Getting details for {bill_no}-{session}")
                details = get_bill_details(bill_no, session)
                if details and details.get('success'):
                    detailed_bills.append(details['result'])

        # Save comprehensive results
        research_data = {
            'timestamp': datetime.now().isoformat(),
            'search_summary': {
                'total_bills_found': len(all_bills),
                'lanza_sponsored_count': len(lanza_sponsored),
                'session_distribution': dict(Counter(by_session.keys())),
                'status_distribution': dict(status_counts),
                'keyword_analysis': dict(keyword_analysis),
                'committee_analysis': dict(committee_analysis)
            },
            'lanza_sponsored_bills': lanza_sponsored,
            'detailed_bill_info': detailed_bills,
            'api_metadata': {
                'api_key_used': API_KEY[:8] + "...",
                'base_url': BASE_URL,
                'search_terms_used': search_terms
            }
        }

        # Save to file
        with open('comprehensive_lanza_research.json', 'w') as f:
            json.dump(research_data, f, indent=2, default=str)

        print(f"\nSaved comprehensive research to comprehensive_lanza_research.json")

        # Generate summary report
        print("\n=== RESEARCH SUMMARY ===")
        print(f"• Found {len(all_bills)} total bills mentioning Lanza")
        print(f"• {len(lanza_sponsored)} bills where Lanza is primary sponsor")
        print(f"• Active across {len(by_session)} different sessions")
        print(f"• Top issue areas: {', '.join([k for k, v in keyword_analysis.most_common(5)])}")
        print(f"• Most common status: {status_counts.most_common(1)[0] if status_counts else 'N/A'}")
        print(f"• Primary committees: {', '.join([k for k, v in committee_analysis.most_common(3)])}")

        return research_data

    else:
        print("No bills found")
        return None

if __name__ == "__main__":
    analyze_lanza_legislation()