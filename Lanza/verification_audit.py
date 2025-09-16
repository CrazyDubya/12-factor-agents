import requests
import json
from datetime import datetime
from collections import Counter, defaultdict
import time

API_KEY = "gNyGkkPgvKrEKXaq7OehFL5D65t4S7yM"
BASE_URL = "https://legislation.nysenate.gov/api/3"

def test_api_connectivity():
    """Test basic API connectivity and available endpoints"""

    print("=== API CONNECTIVITY VERIFICATION ===")
    print(f"Base URL: {BASE_URL}")
    print(f"API Key: {API_KEY[:8]}...")
    print()

    # Test basic endpoints
    test_endpoints = [
        f"{BASE_URL}/bills/2025",
        f"{BASE_URL}/bills/search",
        f"{BASE_URL}/members",
        f"{BASE_URL}/bills/2019",
        f"{BASE_URL}/bills/2017"
    ]

    connectivity_results = {}

    for endpoint in test_endpoints:
        try:
            print(f"Testing: {endpoint}")

            # Test with minimal parameters
            response = requests.get(endpoint, params={"key": API_KEY, "limit": 5}, timeout=30)

            print(f"  Status: {response.status_code}")

            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('success'):
                        print(f"  Success: True")
                        if 'result' in data:
                            if 'items' in data['result']:
                                print(f"  Items found: {len(data['result']['items'])}")
                            else:
                                print(f"  Result type: {type(data['result'])}")
                        connectivity_results[endpoint] = 'SUCCESS'
                    else:
                        print(f"  Success: False - {data.get('message', 'Unknown error')}")
                        connectivity_results[endpoint] = 'API_ERROR'
                except json.JSONDecodeError:
                    print(f"  Invalid JSON response")
                    connectivity_results[endpoint] = 'JSON_ERROR'
            else:
                print(f"  HTTP Error: {response.status_code}")
                if len(response.text) < 200:
                    print(f"  Response: {response.text}")
                connectivity_results[endpoint] = f'HTTP_{response.status_code}'

        except requests.exceptions.Timeout:
            print(f"  Timeout error")
            connectivity_results[endpoint] = 'TIMEOUT'
        except Exception as e:
            print(f"  Exception: {e}")
            connectivity_results[endpoint] = 'EXCEPTION'

        print()
        time.sleep(1)  # Rate limiting

    return connectivity_results

def comprehensive_lanza_search():
    """Comprehensive search for ALL Lanza bills using multiple strategies"""

    print("=== COMPREHENSIVE LANZA BILL SEARCH ===")
    print("Using multiple search strategies to ensure complete coverage...")
    print()

    # All sessions since Lanza entered (2007)
    all_sessions = list(range(2007, 2026, 2))  # 2007, 2009, 2011, ..., 2025
    print(f"Sessions to search: {all_sessions}")
    print()

    search_results = {
        'timestamp': datetime.now().isoformat(),
        'sessions_searched': all_sessions,
        'strategies': {},
        'all_bills_found': {},
        'summary': {}
    }

    # Strategy 1: Direct session-by-session bill retrieval
    print("STRATEGY 1: Direct session bill retrieval")
    strategy1_results = {}

    for session in all_sessions:
        print(f"  Session {session}:")
        session_bills = []

        try:
            # Get ALL bills from this session
            url = f"{BASE_URL}/bills/{session}"

            # Use pagination to get all bills
            offset = 0
            limit = 1000
            total_session_bills = []

            while True:
                params = {
                    "key": API_KEY,
                    "limit": limit,
                    "offset": offset
                }

                response = requests.get(url, params=params, timeout=60)

                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        bills = data.get('result', {}).get('items', [])
                        if not bills:  # No more bills
                            break

                        total_session_bills.extend(bills)
                        offset += limit

                        print(f"    Retrieved {len(bills)} bills (offset {offset-limit})")

                        if len(bills) < limit:  # Last page
                            break
                    else:
                        print(f"    API Error: {data.get('message')}")
                        break
                else:
                    print(f"    HTTP Error: {response.status_code}")
                    break

                time.sleep(0.5)  # Rate limiting

            print(f"    Total bills in session: {len(total_session_bills)}")

            # Filter for Lanza involvement
            lanza_bills = []
            for bill in total_session_bills:
                if is_lanza_involved_comprehensive(bill):
                    lanza_bills.append(bill)
                    bill_id = f"{bill.get('basePrintNo', '')}-{session}"
                    search_results['all_bills_found'][bill_id] = {
                        'bill': bill,
                        'found_by': 'strategy1',
                        'involvement_type': determine_lanza_involvement_type(bill)
                    }

            print(f"    Lanza bills found: {len(lanza_bills)}")
            strategy1_results[str(session)] = len(lanza_bills)

            # Show some examples
            for bill in lanza_bills[:3]:
                print(f"      {bill.get('basePrintNo', 'N/A')}: {bill.get('title', 'No title')[:60]}...")

        except Exception as e:
            print(f"    Error: {e}")
            strategy1_results[str(session)] = 0

        print()

    search_results['strategies']['direct_session_retrieval'] = strategy1_results

    # Strategy 2: Text-based search across all sessions
    print("STRATEGY 2: Text-based searches")
    strategy2_results = {}

    search_terms = [
        "sponsor:lanza",
        "LANZA",
        "Andrew Lanza",
        "A. Lanza",
        '"Andrew J. Lanza"',
        "Lanza AND senate",
        "cosponsor:lanza"
    ]

    for term in search_terms:
        print(f"  Searching for: '{term}'")
        try:
            url = f"{BASE_URL}/bills/search"
            params = {
                "term": term,
                "key": API_KEY,
                "limit": 2000  # Higher limit
            }

            response = requests.get(url, params=params, timeout=60)

            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    bills = data.get('result', {}).get('items', [])
                    print(f"    Found {len(bills)} bills")

                    lanza_bills = []
                    for bill in bills:
                        if is_lanza_involved_comprehensive(bill):
                            lanza_bills.append(bill)
                            bill_id = f"{bill.get('basePrintNo', '')}-{bill.get('session', '')}"
                            if bill_id not in search_results['all_bills_found']:
                                search_results['all_bills_found'][bill_id] = {
                                    'bill': bill,
                                    'found_by': f'strategy2_{term}',
                                    'involvement_type': determine_lanza_involvement_type(bill)
                                }

                    print(f"    Lanza involvement: {len(lanza_bills)}")
                    strategy2_results[term] = len(lanza_bills)
                else:
                    print(f"    API Error: {data.get('message')}")
                    strategy2_results[term] = 0
            else:
                print(f"    HTTP Error: {response.status_code}")
                strategy2_results[term] = 0

        except Exception as e:
            print(f"    Error: {e}")
            strategy2_results[term] = 0

        time.sleep(1)

    search_results['strategies']['text_search'] = strategy2_results

    # Strategy 3: Try member-specific endpoints (if they exist)
    print("\nSTRATEGY 3: Member-specific searches")
    strategy3_results = {}

    member_identifiers = [409, "lanza", "LANZA", "Andrew Lanza"]

    for member_id in member_identifiers:
        print(f"  Member ID: {member_id}")
        try:
            # Try different member endpoint patterns
            member_endpoints = [
                f"{BASE_URL}/members/{member_id}",
                f"{BASE_URL}/senators/{member_id}",
                f"{BASE_URL}/members/{member_id}/bills"
            ]

            for endpoint in member_endpoints:
                try:
                    response = requests.get(endpoint, params={"key": API_KEY}, timeout=30)
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('success'):
                            print(f"    SUCCESS: {endpoint}")
                            strategy3_results[f'{member_id}_{endpoint}'] = 'SUCCESS'
                            # Process member data if available
                        else:
                            print(f"    No success: {endpoint}")
                    else:
                        print(f"    HTTP {response.status_code}: {endpoint}")
                except Exception as e:
                    print(f"    Error {endpoint}: {e}")

        except Exception as e:
            print(f"  Error with member {member_id}: {e}")

        time.sleep(1)

    search_results['strategies']['member_specific'] = strategy3_results

    # Compile final results
    total_bills = len(search_results['all_bills_found'])

    # Analyze involvement types
    involvement_types = defaultdict(int)
    sessions_with_bills = defaultdict(int)

    for bill_id, bill_info in search_results['all_bills_found'].items():
        involvement_types[bill_info['involvement_type']] += 1
        session = bill_info['bill'].get('session', 'unknown')
        sessions_with_bills[str(session)] += 1

    search_results['summary'] = {
        'total_unique_bills': total_bills,
        'involvement_types': dict(involvement_types),
        'sessions_with_bills': dict(sessions_with_bills),
        'years_active': sorted([int(s) for s in sessions_with_bills.keys() if s.isdigit()])
    }

    print("=== COMPREHENSIVE SEARCH COMPLETE ===")
    print(f"✓ Total unique bills found: {total_bills}")
    print(f"✓ Involvement types: {dict(involvement_types)}")
    print(f"✓ Active sessions: {list(sessions_with_bills.keys())}")
    print(f"✓ Years with activity: {search_results['summary']['years_active']}")

    return search_results

def is_lanza_involved_comprehensive(bill):
    """Comprehensive check for Lanza involvement in any capacity"""

    if not bill or not isinstance(bill, dict):
        return False

    # Helper function to check if a member object represents Lanza
    def is_lanza_member(member):
        if not member or not isinstance(member, dict):
            return False

        full_name = str(member.get('fullName', '')).lower()
        short_name = str(member.get('shortName', '')).lower()
        member_id = member.get('memberId')

        # Check various identifiers
        lanza_indicators = [
            'lanza' in full_name,
            'lanza' in short_name,
            member_id == 409,
            member_id == "409",
            'andrew' in full_name and 'lanza' in full_name
        ]

        return any(lanza_indicators)

    # Check primary sponsor
    sponsor = bill.get('sponsor', {})
    if sponsor and isinstance(sponsor, dict):
        member = sponsor.get('member', {})
        if is_lanza_member(member):
            return True

    # Check co-sponsors
    co_sponsors_container = bill.get('coSponsors', {})
    if isinstance(co_sponsors_container, dict):
        co_sponsors = co_sponsors_container.get('items', [])
    elif isinstance(co_sponsors_container, list):
        co_sponsors = co_sponsors_container
    else:
        co_sponsors = []

    for co_sponsor in co_sponsors:
        if isinstance(co_sponsor, dict):
            member = co_sponsor.get('member', {})
            if is_lanza_member(member):
                return True

    # Check multi-sponsors
    multi_sponsors_container = bill.get('multiSponsors', {})
    if isinstance(multi_sponsors_container, dict):
        multi_sponsors = multi_sponsors_container.get('items', [])
    elif isinstance(multi_sponsors_container, list):
        multi_sponsors = multi_sponsors_container
    else:
        multi_sponsors = []

    for multi_sponsor in multi_sponsors:
        if isinstance(multi_sponsor, dict):
            member = multi_sponsor.get('member', {})
            if is_lanza_member(member):
                return True

    # Check additional sponsors
    additional_sponsors_container = bill.get('additionalSponsors', {})
    if isinstance(additional_sponsors_container, dict):
        additional_sponsors = additional_sponsors_container.get('items', [])
    elif isinstance(additional_sponsors_container, list):
        additional_sponsors = additional_sponsors_container
    else:
        additional_sponsors = []

    for add_sponsor in additional_sponsors:
        if isinstance(add_sponsor, dict):
            member = add_sponsor.get('member', {})
            if is_lanza_member(member):
                return True

    # Check text mentions (more comprehensive)
    text_fields = [
        bill.get('title', ''),
        bill.get('summary', ''),
        str(bill.get('sponsor', {}))  # Sometimes sponsor info is in text
    ]

    for text in text_fields:
        if isinstance(text, str) and text:
            text_lower = text.lower()
            if any(term in text_lower for term in ['lanza', 'andrew j. lanza', 'a. lanza']):
                return True

    return False

def determine_lanza_involvement_type(bill):
    """Determine the specific type of Lanza's involvement"""

    if not bill:
        return 'unknown'

    def is_lanza_member(member):
        if not member:
            return False
        full_name = str(member.get('fullName', '')).lower()
        member_id = member.get('memberId')
        return ('lanza' in full_name or member_id == 409 or member_id == "409")

    # Check primary sponsor first
    sponsor = bill.get('sponsor', {})
    if sponsor:
        member = sponsor.get('member', {})
        if is_lanza_member(member):
            return 'primary_sponsor'

    # Check co-sponsors
    co_sponsors = bill.get('coSponsors', {})
    if isinstance(co_sponsors, dict):
        items = co_sponsors.get('items', [])
    else:
        items = co_sponsors if isinstance(co_sponsors, list) else []

    for co_sponsor in items:
        if isinstance(co_sponsor, dict):
            member = co_sponsor.get('member', {})
            if is_lanza_member(member):
                return 'co_sponsor'

    # Check multi-sponsors
    multi_sponsors = bill.get('multiSponsors', {})
    if isinstance(multi_sponsors, dict):
        items = multi_sponsors.get('items', [])
    else:
        items = multi_sponsors if isinstance(multi_sponsors, list) else []

    for multi_sponsor in items:
        if isinstance(multi_sponsor, dict):
            member = multi_sponsor.get('member', {})
            if is_lanza_member(member):
                return 'multi_sponsor'

    # Check additional sponsors
    additional_sponsors = bill.get('additionalSponsors', {})
    if isinstance(additional_sponsors, dict):
        items = additional_sponsors.get('items', [])
    else:
        items = additional_sponsors if isinstance(additional_sponsors, list) else []

    for add_sponsor in items:
        if isinstance(add_sponsor, dict):
            member = add_sponsor.get('member', {})
            if is_lanza_member(member):
                return 'additional_sponsor'

    return 'text_mention'

def cross_reference_known_bills():
    """Cross-reference with bills we know exist from previous searches"""

    print("=== CROSS-REFERENCE WITH KNOWN BILLS ===")

    # Bills we definitely know exist
    known_bills = [
        ("S5914", 2025),
        ("S7356", 2025),
        ("S2589", 2017),
        ("S5988A", 2017),
        ("S8874", 2017)
    ]

    verification_results = {}

    for bill_no, session in known_bills:
        print(f"Verifying {bill_no}-{session}:")

        try:
            # Direct bill lookup
            url = f"{BASE_URL}/bills/{session}/{bill_no}"
            response = requests.get(url, params={"key": API_KEY}, timeout=30)

            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    bill = data['result']

                    # Verify it's actually Lanza's bill
                    is_lanza = is_lanza_involved_comprehensive(bill)
                    involvement_type = determine_lanza_involvement_type(bill)

                    verification_results[f"{bill_no}-{session}"] = {
                        'found': True,
                        'is_lanza': is_lanza,
                        'involvement_type': involvement_type,
                        'title': bill.get('title', 'No title')[:100]
                    }

                    print(f"  ✓ Found: {is_lanza} ({involvement_type})")
                    print(f"  Title: {bill.get('title', '')[:80]}...")
                else:
                    verification_results[f"{bill_no}-{session}"] = {
                        'found': False,
                        'error': data.get('message', 'Unknown error')
                    }
                    print(f"  ✗ API Error: {data.get('message')}")
            else:
                verification_results[f"{bill_no}-{session}"] = {
                    'found': False,
                    'error': f"HTTP {response.status_code}"
                }
                print(f"  ✗ HTTP Error: {response.status_code}")

        except Exception as e:
            verification_results[f"{bill_no}-{session}"] = {
                'found': False,
                'error': str(e)
            }
            print(f"  ✗ Exception: {e}")

        time.sleep(1)

    print()
    return verification_results

def main():
    """Main verification function"""

    print("=== COMPREHENSIVE LANZA BILL VERIFICATION AUDIT ===")
    print(f"Timestamp: {datetime.now()}")
    print("Re-checking API access, bill counts, and data completeness...")
    print("=" * 60)
    print()

    # Step 1: Test API connectivity
    connectivity = test_api_connectivity()

    # Step 2: Cross-reference known bills
    known_verification = cross_reference_known_bills()

    # Step 3: Comprehensive search
    comprehensive_results = comprehensive_lanza_search()

    # Step 4: Compile final audit report
    audit_report = {
        'audit_timestamp': datetime.now().isoformat(),
        'api_connectivity': connectivity,
        'known_bills_verification': known_verification,
        'comprehensive_search': comprehensive_results,
        'final_assessment': {}
    }

    # Final assessment
    total_unique_bills = len(comprehensive_results['all_bills_found'])

    # Count by involvement type
    primary_sponsor_count = sum(1 for b in comprehensive_results['all_bills_found'].values()
                               if b['involvement_type'] == 'primary_sponsor')
    co_sponsor_count = sum(1 for b in comprehensive_results['all_bills_found'].values()
                          if b['involvement_type'] in ['co_sponsor', 'additional_sponsor'])
    multi_sponsor_count = sum(1 for b in comprehensive_results['all_bills_found'].values()
                             if b['involvement_type'] == 'multi_sponsor')

    audit_report['final_assessment'] = {
        'total_unique_bills_found': total_unique_bills,
        'primary_sponsor_bills': primary_sponsor_count,
        'co_sponsor_bills': co_sponsor_count,
        'multi_sponsor_bills': multi_sponsor_count,
        'years_of_activity': len(comprehensive_results['summary']['years_active']),
        'active_years': comprehensive_results['summary']['years_active'],
        'api_endpoints_working': sum(1 for status in connectivity.values() if status == 'SUCCESS'),
        'known_bills_verified': sum(1 for result in known_verification.values() if result.get('found', False))
    }

    # Save comprehensive audit
    with open('lanza_bill_verification_audit.json', 'w') as f:
        json.dump(audit_report, f, indent=2, default=str)

    # Final report
    print("=" * 60)
    print("=== FINAL VERIFICATION REPORT ===")
    print(f"✓ API endpoints tested: {len(connectivity)}")
    print(f"✓ Working endpoints: {audit_report['final_assessment']['api_endpoints_working']}")
    print(f"✓ Known bills verified: {audit_report['final_assessment']['known_bills_verified']}/5")
    print(f"✓ Total unique bills found: {total_unique_bills}")
    print(f"   - Primary sponsor: {primary_sponsor_count}")
    print(f"   - Co-sponsor: {co_sponsor_count}")
    print(f"   - Multi-sponsor: {multi_sponsor_count}")
    print(f"✓ Years of legislative activity: {audit_report['final_assessment']['years_of_activity']}")
    print(f"✓ Active years: {audit_report['final_assessment']['active_years']}")
    print(f"✓ Full audit saved to: lanza_bill_verification_audit.json")

    if total_unique_bills != 68:
        print(f"\n🚨 DISCREPANCY DETECTED:")
        print(f"   Previous count: 68 bills")
        print(f"   New verified count: {total_unique_bills} bills")
        print(f"   Difference: {total_unique_bills - 68}")
    else:
        print(f"\n✅ BILL COUNT CONFIRMED: {total_unique_bills} bills verified")

    return audit_report

if __name__ == "__main__":
    main()