import requests
import json
from datetime import datetime
from collections import Counter, defaultdict
import time

API_KEY = "gNyGkkPgvKrEKXaq7OehFL5D65t4S7yM"
BASE_URL = "https://legislation.nysenate.gov/api/3"

def test_pagination_parameters():
    """Test different pagination parameters to understand API behavior"""

    print("=== TESTING PAGINATION PARAMETERS ===")

    # Test session 2019 (we know has many bills) with different pagination
    test_session = 2019
    url = f"{BASE_URL}/bills/{test_session}"

    pagination_tests = [
        {"limit": 10, "offset": 0},
        {"limit": 100, "offset": 0},
        {"limit": 500, "offset": 0},
        {"limit": 1000, "offset": 0},
        {"limit": 100, "offset": 100},
        {"limit": 100, "offset": 500},
        {"limit": 100, "offset": 1000},
    ]

    results = {}

    for params in pagination_tests:
        try:
            test_params = {"key": API_KEY}
            test_params.update(params)

            print(f"Testing limit={params['limit']}, offset={params['offset']}")

            response = requests.get(url, params=test_params, timeout=30)

            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    result = data.get('result', {})
                    items = result.get('items', [])
                    total = result.get('total', 0)

                    print(f"  Items returned: {len(items)}")
                    print(f"  Total available: {total}")
                    print(f"  Offset start: {result.get('offsetStart', 'N/A')}")
                    print(f"  Offset end: {result.get('offsetEnd', 'N/A')}")

                    # Check for Lanza bills in this page
                    lanza_count = 0
                    for bill in items:
                        sponsor = bill.get('sponsor', {}).get('member', {})
                        if ('lanza' in str(sponsor.get('fullName', '')).lower() or
                            sponsor.get('memberId') == 409):
                            lanza_count += 1

                    print(f"  Lanza bills in this page: {lanza_count}")

                    results[f"limit_{params['limit']}_offset_{params['offset']}"] = {
                        'items_returned': len(items),
                        'total_available': total,
                        'lanza_bills': lanza_count,
                        'offset_start': result.get('offsetStart'),
                        'offset_end': result.get('offsetEnd')
                    }

                else:
                    print(f"  API Error: {data.get('message')}")
            else:
                print(f"  HTTP Error: {response.status_code}")

        except Exception as e:
            print(f"  Exception: {e}")

        print()
        time.sleep(1)

    return results

def complete_session_harvest(session):
    """Harvest ALL bills from a session using proper pagination"""

    print(f"=== COMPLETE SESSION {session} HARVEST ===")

    url = f"{BASE_URL}/bills/{session}"

    all_bills = []
    offset = 0
    limit = 1000  # Large page size

    while True:
        params = {
            "key": API_KEY,
            "limit": limit,
            "offset": offset
        }

        print(f"Fetching bills {offset} to {offset + limit - 1}...")

        try:
            response = requests.get(url, params=params, timeout=60)

            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    result = data.get('result', {})
                    items = result.get('items', [])
                    total = result.get('total', 0)

                    print(f"  Retrieved {len(items)} bills")
                    print(f"  Total available: {total}")

                    if not items:  # No more bills
                        print("  No more bills - pagination complete")
                        break

                    all_bills.extend(items)
                    offset += len(items)

                    # If we got fewer items than requested, we're at the end
                    if len(items) < limit:
                        print("  Reached end of results")
                        break

                    # Safety check - don't infinite loop
                    if offset > total + 1000:  # Some buffer for total count discrepancies
                        print("  Safety break - offset exceeds total")
                        break

                else:
                    print(f"  API Error: {data.get('message')}")
                    break
            else:
                print(f"  HTTP Error: {response.status_code}")
                break

        except Exception as e:
            print(f"  Exception: {e}")
            break

        time.sleep(0.5)  # Rate limiting

    print(f"Total bills retrieved from session {session}: {len(all_bills)}")

    # Filter for Lanza bills
    lanza_bills = []
    for bill in all_bills:
        if is_lanza_involved_complete(bill):
            lanza_bills.append(bill)

    print(f"Lanza bills found in session {session}: {len(lanza_bills)}")

    # Show some examples
    for bill in lanza_bills[:5]:
        print(f"  {bill.get('basePrintNo', 'N/A')}: {bill.get('title', 'No title')[:60]}...")

    return all_bills, lanza_bills

def is_lanza_involved_complete(bill):
    """Complete check for Lanza involvement"""

    if not bill or not isinstance(bill, dict):
        return False

    def check_member(member):
        if not member or not isinstance(member, dict):
            return False

        full_name = str(member.get('fullName', '')).lower()
        short_name = str(member.get('shortName', '')).lower()
        member_id = member.get('memberId')

        return (
            'lanza' in full_name or
            'lanza' in short_name or
            member_id == 409 or
            member_id == "409"
        )

    # Check primary sponsor
    sponsor = bill.get('sponsor', {})
    if sponsor:
        member = sponsor.get('member', {})
        if check_member(member):
            return True

    # Check all sponsor types
    sponsor_fields = [
        'coSponsors',
        'multiSponsors',
        'additionalSponsors'
    ]

    for field in sponsor_fields:
        sponsors_data = bill.get(field, {})

        # Handle different data structures
        if isinstance(sponsors_data, dict):
            sponsors_list = sponsors_data.get('items', [])
        elif isinstance(sponsors_data, list):
            sponsors_list = sponsors_data
        else:
            continue

        for sponsor_item in sponsors_list:
            if isinstance(sponsor_item, dict):
                member = sponsor_item.get('member', {})
                if check_member(member):
                    return True

    return False

def comprehensive_lanza_harvest():
    """Comprehensive harvest of ALL Lanza bills using proper pagination"""

    print("=== COMPREHENSIVE LANZA BILL HARVEST ===")
    print("Using proper pagination to capture complete dataset")
    print()

    # Test pagination first
    pagination_test_results = test_pagination_parameters()

    # All sessions to check
    sessions = [2007, 2009, 2011, 2013, 2015, 2017, 2019, 2021, 2023, 2025]

    all_lanza_bills = {}
    session_summaries = {}

    for session in sessions:
        print(f"\n{'='*50}")
        print(f"PROCESSING SESSION {session}")
        print(f"{'='*50}")

        try:
            all_session_bills, lanza_bills = complete_session_harvest(session)

            session_summaries[str(session)] = {
                'total_bills_in_session': len(all_session_bills),
                'lanza_bills_found': len(lanza_bills),
                'lanza_percentage': (len(lanza_bills) / len(all_session_bills) * 100) if all_session_bills else 0
            }

            # Store Lanza bills
            for bill in lanza_bills:
                bill_id = f"{bill.get('basePrintNo', '')}-{session}"
                all_lanza_bills[bill_id] = {
                    'bill': bill,
                    'session': session,
                    'involvement_type': determine_involvement_type(bill)
                }

        except Exception as e:
            print(f"Error processing session {session}: {e}")
            session_summaries[str(session)] = {
                'total_bills_in_session': 0,
                'lanza_bills_found': 0,
                'error': str(e)
            }

    # Compile final results
    final_results = {
        'harvest_timestamp': datetime.now().isoformat(),
        'pagination_test_results': pagination_test_results,
        'session_summaries': session_summaries,
        'all_lanza_bills': all_lanza_bills,
        'final_statistics': {
            'total_unique_bills': len(all_lanza_bills),
            'sessions_with_activity': len([s for s, data in session_summaries.items()
                                          if data.get('lanza_bills_found', 0) > 0]),
            'most_active_session': max(session_summaries.items(),
                                     key=lambda x: x[1].get('lanza_bills_found', 0))[0]
                                     if session_summaries else None
        }
    }

    # Analyze involvement types
    involvement_counts = Counter()
    for bill_data in all_lanza_bills.values():
        involvement_counts[bill_data['involvement_type']] += 1

    final_results['final_statistics']['involvement_breakdown'] = dict(involvement_counts)

    # Save complete results
    with open('complete_lanza_harvest.json', 'w') as f:
        json.dump(final_results, f, indent=2, default=str)

    print("\n" + "="*60)
    print("=== COMPLETE HARVEST RESULTS ===")
    print(f"✓ Total unique Lanza bills found: {len(all_lanza_bills)}")
    print(f"✓ Sessions with Lanza activity: {final_results['final_statistics']['sessions_with_activity']}")
    print(f"✓ Most active session: {final_results['final_statistics']['most_active_session']}")
    print(f"✓ Involvement breakdown: {final_results['final_statistics']['involvement_breakdown']}")
    print()

    print("Session-by-session breakdown:")
    for session, data in session_summaries.items():
        if 'error' in data:
            print(f"  {session}: ERROR - {data['error']}")
        else:
            print(f"  {session}: {data['lanza_bills_found']} Lanza bills out of {data['total_bills_in_session']} total ({data['lanza_percentage']:.1f}%)")

    print(f"\n✓ Complete results saved to 'complete_lanza_harvest.json'")

    return final_results

def determine_involvement_type(bill):
    """Determine type of Lanza involvement"""

    def is_lanza_member(member):
        if not member:
            return False
        full_name = str(member.get('fullName', '')).lower()
        return ('lanza' in full_name or member.get('memberId') == 409)

    # Check primary sponsor
    sponsor = bill.get('sponsor', {}).get('member', {})
    if is_lanza_member(sponsor):
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

    return 'other'

if __name__ == "__main__":
    comprehensive_lanza_harvest()