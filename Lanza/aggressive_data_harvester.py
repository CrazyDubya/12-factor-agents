import requests
import json
from datetime import datetime
from collections import Counter, defaultdict
import time
import re

API_KEY = "gNyGkkPgvKrEKXaq7OehFL5D65t4S7yM"
BASE_URL = "https://legislation.nysenate.gov/api/3"

def get_all_lanza_involvement():
    """
    Comprehensive search for ALL Lanza legislative involvement:
    - Primary sponsor
    - Co-sponsor
    - Multi-sponsor
    - Amendment sponsor
    - Committee involvement
    """

    print("=== AGGRESSIVE LANZA DATA HARVESTING ===")
    print(f"Timestamp: {datetime.now()}")
    print("Searching for ALL forms of legislative involvement...")
    print()

    sessions = [2007, 2009, 2011, 2013, 2015, 2017, 2019, 2021, 2023, 2025]

    comprehensive_involvement = {
        'timestamp': datetime.now().isoformat(),
        'search_methods': [],
        'all_bills_found': [],
        'involvement_types': {
            'primary_sponsor': [],
            'co_sponsor': [],
            'multi_sponsor': [],
            'mentioned_in_text': [],
            'committee_related': []
        },
        'session_breakdown': {},
        'search_statistics': {}
    }

    all_unique_bills = {}  # Use dict to avoid duplicates by bill ID

    # Search Strategy 1: Broad text search for "Lanza"
    print("=== STRATEGY 1: Broad Text Search ===")
    for session in sessions:
        print(f"Session {session}:")

        search_terms = [
            f"lanza session:{session}",
            f"sponsor:lanza session:{session}",
            f"cosponsor:lanza session:{session}",
            f"\"Andrew Lanza\" session:{session}",
            f"\"A. Lanza\" session:{session}",
            f"\"LANZA\" session:{session}"
        ]

        for term in search_terms:
            try:
                url = f"{BASE_URL}/bills/search"
                params = {"term": term, "key": API_KEY, "limit": 1000}

                response = requests.get(url, params=params, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        bills = data.get('result', {}).get('items', [])
                        print(f"  '{term}': {len(bills)} bills")

                        for bill in bills:
                            bill_id = f"{bill.get('basePrintNo', '')}-{bill.get('session', '')}"
                            if bill_id not in all_unique_bills:
                                all_unique_bills[bill_id] = bill

                                # Determine involvement type
                                involvement_type = determine_involvement_type(bill)
                                comprehensive_involvement['involvement_types'][involvement_type].append(bill)

                    else:
                        print(f"  '{term}': API error")
                else:
                    print(f"  '{term}': HTTP {response.status_code}")

            except Exception as e:
                print(f"  '{term}': Exception - {e}")

        time.sleep(1)  # Rate limiting

    print(f"\nStrategy 1 found {len(all_unique_bills)} unique bills")

    # Search Strategy 2: Session-by-session exhaustive search
    print("\n=== STRATEGY 2: Session Exhaustive Search ===")
    for session in sessions:
        print(f"Session {session}:")

        session_bills = []

        # Try multiple endpoints for each session
        endpoints = [
            f"{BASE_URL}/bills/{session}",
            f"{BASE_URL}/bills/{session}/sponsor/lanza",
            f"{BASE_URL}/bills/{session}/cosponsor/lanza"
        ]

        for endpoint in endpoints:
            try:
                params = {"key": API_KEY, "limit": 1000}
                response = requests.get(endpoint, params=params, timeout=30)

                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        if 'result' in data:
                            if 'items' in data['result']:
                                bills = data['result']['items']
                            else:
                                bills = [data['result']] if isinstance(data['result'], dict) else []
                        else:
                            bills = data if isinstance(data, list) else []

                        # Filter for Lanza involvement
                        lanza_bills = []
                        for bill in bills:
                            if is_lanza_involved(bill):
                                lanza_bills.append(bill)
                                bill_id = f"{bill.get('basePrintNo', '')}-{bill.get('session', '')}"
                                if bill_id not in all_unique_bills:
                                    all_unique_bills[bill_id] = bill
                                    involvement_type = determine_involvement_type(bill)
                                    comprehensive_involvement['involvement_types'][involvement_type].append(bill)

                        print(f"  {endpoint}: {len(lanza_bills)} Lanza bills")
                        session_bills.extend(lanza_bills)

                        if lanza_bills:
                            break  # Use first successful endpoint

            except Exception as e:
                print(f"  {endpoint}: Error - {e}")

        comprehensive_involvement['session_breakdown'][str(session)] = len(session_bills)
        time.sleep(1)

    print(f"\nStrategy 2 added bills, total now: {len(all_unique_bills)}")

    # Search Strategy 3: Member-specific API calls
    print("\n=== STRATEGY 3: Member-Specific API ===")
    member_ids = [409, "lanza", "LANZA"]  # Try different member identifiers

    for member_id in member_ids:
        print(f"Member ID: {member_id}")

        for session in sessions:
            try:
                endpoints = [
                    f"{BASE_URL}/members/{member_id}/bills/{session}",
                    f"{BASE_URL}/members/{member_id}/votes/{session}",
                    f"{BASE_URL}/members/{member_id}"
                ]

                for endpoint in endpoints:
                    response = requests.get(endpoint, params={"key": API_KEY}, timeout=30)
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('success'):
                            print(f"  {endpoint}: Success!")
                            # Process member-specific data
                            process_member_data(data, comprehensive_involvement)
                        else:
                            print(f"  {endpoint}: No success flag")
                    else:
                        print(f"  {endpoint}: HTTP {response.status_code}")

            except Exception as e:
                print(f"  Member {member_id} session {session}: {e}")

        time.sleep(1)

    # Strategy 4: Deep dive into known high-activity sessions
    print("\n=== STRATEGY 4: Deep Dive High Activity ===")
    high_activity_sessions = [2009, 2015, 2019]  # Sessions we know have bills

    for session in high_activity_sessions:
        print(f"Deep diving session {session}:")

        # Get ALL bills from these sessions and search for Lanza
        try:
            url = f"{BASE_URL}/bills/{session}"
            params = {"key": API_KEY, "limit": 10000}  # Much higher limit

            response = requests.get(url, params=params, timeout=60)  # Longer timeout
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    all_session_bills = data.get('result', {}).get('items', [])
                    print(f"  Total bills in session: {len(all_session_bills)}")

                    lanza_involved = 0
                    for bill in all_session_bills:
                        if is_lanza_involved(bill):
                            lanza_involved += 1
                            bill_id = f"{bill.get('basePrintNo', '')}-{bill.get('session', '')}"
                            if bill_id not in all_unique_bills:
                                all_unique_bills[bill_id] = bill
                                involvement_type = determine_involvement_type(bill)
                                comprehensive_involvement['involvement_types'][involvement_type].append(bill)

                    print(f"  Lanza involvement found: {lanza_involved}")

        except Exception as e:
            print(f"  Deep dive {session} error: {e}")

        time.sleep(2)

    # Final compilation
    comprehensive_involvement['all_bills_found'] = list(all_unique_bills.values())

    # Statistics
    comprehensive_involvement['search_statistics'] = {
        'total_unique_bills': len(all_unique_bills),
        'primary_sponsor_count': len(comprehensive_involvement['involvement_types']['primary_sponsor']),
        'co_sponsor_count': len(comprehensive_involvement['involvement_types']['co_sponsor']),
        'multi_sponsor_count': len(comprehensive_involvement['involvement_types']['multi_sponsor']),
        'mentioned_in_text_count': len(comprehensive_involvement['involvement_types']['mentioned_in_text']),
        'sessions_with_activity': len([s for s, c in comprehensive_involvement['session_breakdown'].items() if c > 0])
    }

    # Save comprehensive results
    with open('comprehensive_lanza_involvement.json', 'w') as f:
        json.dump(comprehensive_involvement, f, indent=2, default=str)

    print("\n=== COMPREHENSIVE SEARCH COMPLETE ===")
    print(f"✓ Total unique bills found: {len(all_unique_bills)}")
    print(f"✓ Primary sponsor: {comprehensive_involvement['search_statistics']['primary_sponsor_count']}")
    print(f"✓ Co-sponsor: {comprehensive_involvement['search_statistics']['co_sponsor_count']}")
    print(f"✓ Multi-sponsor: {comprehensive_involvement['search_statistics']['multi_sponsor_count']}")
    print(f"✓ Text mentions: {comprehensive_involvement['search_statistics']['mentioned_in_text_count']}")
    print(f"✓ Active sessions: {comprehensive_involvement['search_statistics']['sessions_with_activity']}")
    print(f"✓ Saved to comprehensive_lanza_involvement.json")

    return comprehensive_involvement

def is_lanza_involved(bill):
    """Check if Lanza is involved in any capacity with this bill"""
    if not bill or not isinstance(bill, dict):
        return False

    # Check primary sponsor
    sponsor = bill.get('sponsor', {})
    if sponsor:
        member = sponsor.get('member', {})
        if member:
            full_name = member.get('fullName', '').lower()
            short_name = member.get('shortName', '').lower()
            member_id = member.get('memberId')

            if ('lanza' in full_name or 'lanza' in short_name or member_id == 409):
                return True

    # Check co-sponsors
    co_sponsors = bill.get('coSponsors', {}).get('items', [])
    for co_sponsor in co_sponsors:
        member = co_sponsor.get('member', {})
        if member:
            full_name = member.get('fullName', '').lower()
            short_name = member.get('shortName', '').lower()
            member_id = member.get('memberId')

            if ('lanza' in full_name or 'lanza' in short_name or member_id == 409):
                return True

    # Check multi-sponsors
    multi_sponsors = bill.get('multiSponsors', {}).get('items', [])
    for multi_sponsor in multi_sponsors:
        member = multi_sponsor.get('member', {})
        if member:
            full_name = member.get('fullName', '').lower()
            short_name = member.get('shortName', '').lower()
            member_id = member.get('memberId')

            if ('lanza' in full_name or 'lanza' in short_name or member_id == 409):
                return True

    # Check additional sponsors
    additional_sponsors = bill.get('additionalSponsors', {}).get('items', [])
    for add_sponsor in additional_sponsors:
        member = add_sponsor.get('member', {})
        if member:
            full_name = member.get('fullName', '').lower()
            short_name = member.get('shortName', '').lower()
            member_id = member.get('memberId')

            if ('lanza' in full_name or 'lanza' in short_name or member_id == 409):
                return True

    # Check bill text/title for mentions
    title = bill.get('title', '').lower()
    summary = bill.get('summary', '').lower()

    if 'lanza' in title or 'lanza' in summary:
        return True

    return False

def determine_involvement_type(bill):
    """Determine the type of Lanza's involvement"""
    if not bill:
        return 'unknown'

    # Check primary sponsor first
    sponsor = bill.get('sponsor', {})
    if sponsor:
        member = sponsor.get('member', {})
        if member and ('lanza' in member.get('fullName', '').lower() or member.get('memberId') == 409):
            return 'primary_sponsor'

    # Check co-sponsors
    co_sponsors = bill.get('coSponsors', {}).get('items', [])
    for co_sponsor in co_sponsors:
        member = co_sponsor.get('member', {})
        if member and ('lanza' in member.get('fullName', '').lower() or member.get('memberId') == 409):
            return 'co_sponsor'

    # Check multi-sponsors
    multi_sponsors = bill.get('multiSponsors', {}).get('items', [])
    for multi_sponsor in multi_sponsors:
        member = multi_sponsor.get('member', {})
        if member and ('lanza' in member.get('fullName', '').lower() or member.get('memberId') == 409):
            return 'multi_sponsor'

    # Check additional sponsors
    additional_sponsors = bill.get('additionalSponsors', {}).get('items', [])
    for add_sponsor in additional_sponsors:
        member = add_sponsor.get('member', {})
        if member and ('lanza' in member.get('fullName', '').lower() or member.get('memberId') == 409):
            return 'co_sponsor'  # Treat additional as co-sponsor

    # If found in text but not as sponsor
    return 'mentioned_in_text'

def process_member_data(data, comprehensive_involvement):
    """Process member-specific API responses"""
    # This function would process member-specific data
    # Implementation depends on the structure of member API responses
    pass

if __name__ == "__main__":
    get_all_lanza_involvement()