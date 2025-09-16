import requests
import json
from datetime import datetime
from collections import defaultdict, Counter

API_KEY = "gNyGkkPgvKrEKXaq7OehFL5D65t4S7yM"
BASE_URL = "https://legislation.nysenate.gov/api/3"

def search_bills_by_sponsor(limit=1000):
    """Search for bills by sponsor using member API"""
    # Try different approaches to find Lanza-sponsored bills
    approaches = [
        {"url": f"{BASE_URL}/members", "params": {"key": API_KEY}},
        {"url": f"{BASE_URL}/bills/search", "params": {"term": "lanza", "key": API_KEY, "limit": limit}}
    ]

    all_results = []

    for approach in approaches:
        try:
            print(f"Trying: {approach['url']}")
            response = requests.get(approach['url'], params=approach['params'], timeout=30)
            if response.status_code == 200:
                data = response.json()
                print(f"  Success! Keys: {list(data.keys()) if isinstance(data, dict) else 'List'}")
                all_results.append(data)
            else:
                print(f"  Failed: {response.status_code}")
        except Exception as e:
            print(f"  Error: {e}")

    return all_results

def get_member_bills(member_id, session_year=2025):
    """Get bills for a specific member"""
    url = f"{BASE_URL}/members/{member_id}/bills/{session_year}"
    params = {"key": API_KEY}

    try:
        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error getting member bills: {e}")
    return None

def analyze_known_bills():
    """Analyze the bills we already know about"""
    known_bills = [
        {"bill": "S5914", "session": 2025, "description": "Enhanced driver's license fees"},
        {"bill": "S7356", "session": 2025, "description": "Sex trafficking protections"},
        {"bill": "S2589", "session": 2017, "description": "Animals on public transportation"},
        {"bill": "S5988A", "session": 2017, "description": "Sex trafficking of a child"},
        {"bill": "S8874", "session": 2017, "description": "Human trafficking victim services"}
    ]

    print("=== ANALYZING KNOWN LANZA BILLS ===")

    detailed_analysis = {
        'bills': [],
        'patterns': {
            'topics': Counter(),
            'years': Counter(),
            'status_types': Counter(),
            'committees': Counter()
        },
        'legislative_themes': [],
        'timeline': []
    }

    for bill_info in known_bills:
        bill_no = bill_info['bill']
        session = bill_info['session']

        # We already have some bill details from previous API calls
        bill_file = f"bill_{bill_no}_{session}.json"

        try:
            with open(bill_file, 'r') as f:
                bill_data = json.load(f)

            if bill_data.get('success'):
                bill = bill_data['result']
                detailed_analysis['bills'].append(bill)

                # Extract patterns
                title = bill.get('title', '').lower()
                status = bill.get('status', {})

                # Topic classification
                if any(word in title for word in ['trafficking', 'victim']):
                    detailed_analysis['patterns']['topics']['Human Trafficking'] += 1
                elif any(word in title for word in ['animal', 'companion']):
                    detailed_analysis['patterns']['topics']['Animal Welfare'] += 1
                elif any(word in title for word in ['license', 'driver', 'fee']):
                    detailed_analysis['patterns']['topics']['Transportation/Licensing'] += 1
                else:
                    detailed_analysis['patterns']['topics']['Other'] += 1

                detailed_analysis['patterns']['years'][session] += 1
                detailed_analysis['patterns']['status_types'][status.get('statusType', 'Unknown')] += 1

                committee = status.get('committeeName')
                if committee:
                    detailed_analysis['patterns']['committees'][committee] += 1

                # Timeline entry
                detailed_analysis['timeline'].append({
                    'bill': bill_no,
                    'session': session,
                    'date': bill.get('publishedDateTime', ''),
                    'title': bill.get('title', ''),
                    'status': status.get('statusDesc', ''),
                    'committee': committee
                })

                print(f"✓ {bill_no}-{session}: {bill.get('title', '')[:80]}...")

        except FileNotFoundError:
            print(f"✗ {bill_no}-{session}: File not found")
        except Exception as e:
            print(f"✗ {bill_no}-{session}: Error - {e}")

    # Sort timeline by date
    detailed_analysis['timeline'].sort(key=lambda x: x['date'])

    # Identify legislative themes
    themes = []
    if detailed_analysis['patterns']['topics']['Human Trafficking'] >= 2:
        themes.append("Anti-Human Trafficking Advocate")
    if detailed_analysis['patterns']['topics']['Animal Welfare'] >= 1:
        themes.append("Animal Welfare Champion")
    if detailed_analysis['patterns']['topics']['Transportation/Licensing'] >= 1:
        themes.append("Transportation/Consumer Protection")

    detailed_analysis['legislative_themes'] = themes

    # Convert Counter objects to regular dicts for JSON serialization
    for key in detailed_analysis['patterns']:
        detailed_analysis['patterns'][key] = dict(detailed_analysis['patterns'][key])

    return detailed_analysis

def research_additional_sessions():
    """Research bills from multiple sessions"""
    sessions = [2025, 2023, 2021, 2019, 2017]
    additional_bills = []

    print("\n=== RESEARCHING ADDITIONAL SESSIONS ===")

    for session in sessions:
        print(f"Session {session}:")

        # Try to search for Lanza bills in this session
        search_url = f"{BASE_URL}/bills/search"
        params = {
            "term": f"session:{session} lanza",
            "key": API_KEY,
            "limit": 100
        }

        try:
            response = requests.get(search_url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    bills = data.get('result', {}).get('items', [])
                    print(f"  Found {len(bills)} bills")

                    # Filter for Lanza as primary sponsor
                    lanza_bills = []
                    for bill in bills:
                        sponsor = bill.get('sponsor', {})
                        if sponsor:
                            member = sponsor.get('member', {})
                            if member and 'lanza' in member.get('fullName', '').lower():
                                lanza_bills.append(bill)

                    print(f"  Lanza sponsored: {len(lanza_bills)}")
                    additional_bills.extend(lanza_bills)

                    # Show some examples
                    for bill in lanza_bills[:3]:
                        print(f"    {bill.get('basePrintNo')}: {bill.get('title', '')[:60]}...")

            else:
                print(f"  API Error: {response.status_code}")

        except Exception as e:
            print(f"  Error: {e}")

    return additional_bills

def main():
    print("=== ENHANCED LANZA LEGISLATIVE RESEARCH ===")
    print(f"Timestamp: {datetime.now()}")
    print()

    # Step 1: Analyze known bills in detail
    known_analysis = analyze_known_bills()

    # Step 2: Research additional sessions
    additional_bills = research_additional_sessions()

    # Step 3: Compile comprehensive report
    comprehensive_report = {
        'timestamp': datetime.now().isoformat(),
        'api_info': {
            'base_url': BASE_URL,
            'key_prefix': API_KEY[:8] + "..."
        },
        'known_bills_analysis': known_analysis,
        'additional_bills_found': len(additional_bills),
        'additional_bills': additional_bills,
        'research_summary': {
            'total_bills_analyzed': len(known_analysis['bills']) + len(additional_bills),
            'primary_topics': list(known_analysis['patterns']['topics'].keys()),
            'legislative_themes': known_analysis['legislative_themes'],
            'active_sessions': list(known_analysis['patterns']['years'].keys()),
            'committees_involved': list(known_analysis['patterns']['committees'].keys())
        }
    }

    # Save comprehensive report
    with open('enhanced_lanza_research.json', 'w') as f:
        json.dump(comprehensive_report, f, indent=2, default=str)

    print("\n=== RESEARCH SUMMARY ===")
    print(f"✓ Analyzed {len(known_analysis['bills'])} known bills in detail")
    print(f"✓ Found {len(additional_bills)} additional bills")
    print(f"✓ Primary legislative themes: {', '.join(known_analysis['legislative_themes'])}")
    print(f"✓ Active in sessions: {', '.join(map(str, known_analysis['patterns']['years'].keys()))}")
    print(f"✓ Main committees: {', '.join(known_analysis['patterns']['committees'].keys())}")
    print(f"✓ Saved comprehensive report to enhanced_lanza_research.json")

    return comprehensive_report

if __name__ == "__main__":
    main()