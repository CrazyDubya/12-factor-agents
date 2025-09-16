import requests
import json
from datetime import datetime
from collections import Counter

API_KEY = "gNyGkkPgvKrEKXaq7OehFL5D65t4S7yM"
BASE_URL = "https://legislation.nysenate.gov/api/3"

def quick_bill_verification():
    """Quick verification of bill counting and API access"""

    print("=== QUICK LANZA BILL VERIFICATION ===")
    print(f"API: {BASE_URL}")
    print(f"Key: {API_KEY[:8]}...")
    print()

    # Test 1: Verify known bills exist and are correctly identified
    print("TEST 1: Known Bills Verification")
    known_bills = [
        ("S5914", 2025),
        ("S7356", 2025),
        ("S2589", 2017),
        ("S5988A", 2017),
        ("S8874", 2017)
    ]

    verified_count = 0
    for bill_no, session in known_bills:
        try:
            url = f"{BASE_URL}/bills/{session}/{bill_no}"
            response = requests.get(url, params={"key": API_KEY}, timeout=15)

            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    bill = data['result']
                    sponsor = bill.get('sponsor', {}).get('member', {})
                    is_lanza = ('lanza' in str(sponsor.get('fullName', '')).lower() or
                               sponsor.get('memberId') == 409)

                    print(f"  {bill_no}-{session}: {'✓' if is_lanza else '✗'} - {sponsor.get('fullName', 'Unknown')}")
                    if is_lanza:
                        verified_count += 1
                else:
                    print(f"  {bill_no}-{session}: ✗ API Error")
            else:
                print(f"  {bill_no}-{session}: ✗ HTTP {response.status_code}")
        except Exception as e:
            print(f"  {bill_no}-{session}: ✗ {e}")

    print(f"  Verified: {verified_count}/5 known bills")
    print()

    # Test 2: Sample high-activity sessions
    print("TEST 2: High-Activity Sessions Sample")
    high_sessions = [2019, 2009, 2017]  # Sessions we know have activity

    total_found = 0
    session_results = {}

    for session in high_sessions:
        print(f"  Session {session}:")
        try:
            # Get first 500 bills from session
            url = f"{BASE_URL}/bills/{session}"
            response = requests.get(url, params={"key": API_KEY, "limit": 500}, timeout=30)

            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    bills = data.get('result', {}).get('items', [])
                    print(f"    Retrieved {len(bills)} bills")

                    lanza_count = 0
                    for bill in bills:
                        sponsor = bill.get('sponsor', {}).get('member', {})
                        if ('lanza' in str(sponsor.get('fullName', '')).lower() or
                            sponsor.get('memberId') == 409):
                            lanza_count += 1

                    print(f"    Lanza bills: {lanza_count}")
                    session_results[session] = lanza_count
                    total_found += lanza_count

                    # Show some examples
                    examples = [bill for bill in bills
                               if ('lanza' in str(bill.get('sponsor', {}).get('member', {}).get('fullName', '')).lower() or
                                   bill.get('sponsor', {}).get('member', {}).get('memberId') == 409)][:3]

                    for ex in examples:
                        print(f"      {ex.get('basePrintNo', 'N/A')}: {ex.get('title', 'No title')[:50]}...")

                else:
                    print(f"    API Error: {data.get('message')}")
                    session_results[session] = 0
            else:
                print(f"    HTTP Error: {response.status_code}")
                session_results[session] = 0

        except Exception as e:
            print(f"    Error: {e}")
            session_results[session] = 0

    print(f"  Total found in sample sessions: {total_found}")
    print(f"  Session breakdown: {session_results}")
    print()

    # Test 3: Text search verification
    print("TEST 3: Text Search Verification")
    search_terms = ["sponsor:lanza", "LANZA"]

    search_results = {}
    for term in search_terms:
        try:
            url = f"{BASE_URL}/bills/search"
            response = requests.get(url, params={"term": term, "key": API_KEY, "limit": 100}, timeout=20)

            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    bills = data.get('result', {}).get('items', [])

                    # Filter for actual Lanza bills
                    lanza_bills = []
                    for bill in bills:
                        sponsor = bill.get('sponsor', {}).get('member', {})
                        if ('lanza' in str(sponsor.get('fullName', '')).lower() or
                            sponsor.get('memberId') == 409):
                            lanza_bills.append(bill)

                    print(f"  '{term}': {len(bills)} total, {len(lanza_bills)} Lanza bills")
                    search_results[term] = len(lanza_bills)
                else:
                    print(f"  '{term}': API Error - {data.get('message')}")
                    search_results[term] = 0
            else:
                print(f"  '{term}': HTTP Error {response.status_code}")
                search_results[term] = 0

        except Exception as e:
            print(f"  '{term}': Error - {e}")
            search_results[term] = 0

    print()

    # Test 4: Check our existing data
    print("TEST 4: Existing Data Verification")
    try:
        with open('comprehensive_lanza_involvement.json', 'r') as f:
            existing_data = json.load(f)

        existing_bills = existing_data.get('all_bills_found', [])
        existing_count = len(existing_bills)

        # Check involvement types in existing data
        involvement_counts = Counter()
        session_counts = Counter()

        for bill in existing_bills:
            if isinstance(bill, dict):
                session = bill.get('session', 'unknown')
                session_counts[str(session)] += 1

                # Quick involvement type check
                sponsor = bill.get('sponsor', {}).get('member', {})
                if sponsor and ('lanza' in str(sponsor.get('fullName', '')).lower() or
                               sponsor.get('memberId') == 409):
                    involvement_counts['primary_sponsor'] += 1
                else:
                    involvement_counts['other'] += 1

        print(f"  Existing data: {existing_count} bills")
        print(f"  Session distribution: {dict(session_counts)}")
        print(f"  Involvement types: {dict(involvement_counts)}")

    except FileNotFoundError:
        print("  No existing data file found")
        existing_count = 0
    except Exception as e:
        print(f"  Error reading existing data: {e}")
        existing_count = 0

    print()

    # Summary
    print("=== VERIFICATION SUMMARY ===")
    print(f"✓ Known bills verified: {verified_count}/5")
    print(f"✓ High-activity sessions sample: {total_found} bills")
    print(f"✓ Text search results: {dict(search_results)}")
    print(f"✓ Previous data file: {existing_count} bills")

    # Estimated total based on samples
    if session_results.get(2019, 0) > 0:
        # We know 2019 has the most activity
        estimated_total = session_results.get(2019, 0) + session_results.get(2009, 0) + session_results.get(2017, 0)
        # Add estimates for other sessions (2007, 2011, 2013, 2015, 2021, 2023, 2025)
        other_sessions_estimate = 10  # Conservative estimate
        total_estimate = estimated_total + other_sessions_estimate

        print(f"✓ Estimated total range: {total_estimate}-{total_estimate + 20} bills")

        if abs(existing_count - total_estimate) > 10:
            print(f"🚨 POTENTIAL DISCREPANCY: Existing count ({existing_count}) vs estimated ({total_estimate})")
        else:
            print(f"✅ COUNTS ALIGN: Existing data appears accurate")

    return {
        'verified_known_bills': verified_count,
        'session_samples': session_results,
        'search_results': search_results,
        'existing_count': existing_count,
        'total_sample_found': total_found
    }

if __name__ == "__main__":
    quick_bill_verification()