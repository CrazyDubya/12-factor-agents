import requests
import json
from datetime import datetime

API_KEY = "gNyGkkPgvKrEKXaq7OehFL5D65t4S7yM"
BASE_URL = "https://legislation.nysenate.gov/api/3"

def debug_known_bill_structure():
    """Debug the exact structure of a bill we KNOW is Lanza's"""

    print("=== DEBUGGING BILL STRUCTURE FOR KNOWN LANZA BILLS ===")

    # Test with a bill we absolutely know is Lanza's
    known_lanza_bills = [
        ("S5914", 2025),
        ("S2589", 2017),
        ("S5988A", 2017)
    ]

    for bill_no, session in known_lanza_bills:
        print(f"\n=== ANALYZING {bill_no}-{session} ===")

        try:
            url = f"{BASE_URL}/bills/{session}/{bill_no}"
            response = requests.get(url, params={"key": API_KEY}, timeout=30)

            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    bill = data['result']

                    print(f"Bill Number: {bill.get('basePrintNo')}")
                    print(f"Session: {bill.get('session')}")
                    print(f"Title: {bill.get('title', '')[:100]}...")
                    print()

                    # Deep dive into sponsor structure
                    print("=== SPONSOR STRUCTURE ===")
                    sponsor = bill.get('sponsor', {})
                    print(f"Sponsor object type: {type(sponsor)}")
                    print(f"Sponsor keys: {list(sponsor.keys()) if isinstance(sponsor, dict) else 'Not a dict'}")

                    if isinstance(sponsor, dict):
                        member = sponsor.get('member', {})
                        print(f"Member object type: {type(member)}")
                        print(f"Member keys: {list(member.keys()) if isinstance(member, dict) else 'Not a dict'}")

                        if isinstance(member, dict):
                            print(f"  fullName: '{member.get('fullName')}'")
                            print(f"  shortName: '{member.get('shortName')}'")
                            print(f"  memberId: {member.get('memberId')} (type: {type(member.get('memberId'))})")
                            print(f"  chamber: '{member.get('chamber')}'")
                            print(f"  districtCode: {member.get('districtCode')}")

                    print()

                    # Check co-sponsors
                    print("=== CO-SPONSORS STRUCTURE ===")
                    co_sponsors = bill.get('coSponsors', {})
                    print(f"CoSponsors type: {type(co_sponsors)}")
                    print(f"CoSponsors keys: {list(co_sponsors.keys()) if isinstance(co_sponsors, dict) else 'Not a dict'}")

                    if isinstance(co_sponsors, dict):
                        items = co_sponsors.get('items', [])
                        print(f"CoSponsors items count: {len(items)}")
                        for i, item in enumerate(items[:2]):  # Show first 2
                            print(f"  CoSponsor {i}: {item}")

                    print()

                    # Test our current detection logic
                    print("=== TESTING DETECTION LOGIC ===")
                    result = test_detection_logic(bill)
                    print(f"Current detection result: {result}")

                    # Test improved detection
                    result2 = improved_detection_logic(bill)
                    print(f"Improved detection result: {result2}")

                    # Raw dump for debugging
                    print("\n=== RAW SPONSOR DATA ===")
                    print(json.dumps(sponsor, indent=2, default=str)[:500])

                else:
                    print(f"API Error: {data.get('message')}")
            else:
                print(f"HTTP Error: {response.status_code}")

        except Exception as e:
            print(f"Error: {e}")

def test_detection_logic(bill):
    """Test our current broken logic"""
    if not bill or not isinstance(bill, dict):
        return False

    sponsor = bill.get('sponsor', {})
    if sponsor:
        member = sponsor.get('member', {})
        if member:
            full_name = str(member.get('fullName', '')).lower()
            member_id = member.get('memberId')

            if ('lanza' in full_name or member_id == 409 or member_id == "409"):
                return True

    return False

def improved_detection_logic(bill):
    """Improved detection logic with more debugging"""
    if not bill or not isinstance(bill, dict):
        return False, "Not a valid bill dict"

    sponsor = bill.get('sponsor', {})
    if not sponsor:
        return False, "No sponsor field"

    member = sponsor.get('member', {})
    if not member:
        return False, "No member field in sponsor"

    full_name = member.get('fullName', '')
    short_name = member.get('shortName', '')
    member_id = member.get('memberId')

    # Debug output
    debug_info = {
        'fullName': full_name,
        'shortName': short_name,
        'memberId': member_id,
        'memberId_type': type(member_id)
    }

    # Test various conditions
    conditions = {
        'lanza_in_fullname': 'lanza' in str(full_name).lower(),
        'lanza_in_shortname': 'lanza' in str(short_name).lower(),
        'memberid_409_int': member_id == 409,
        'memberid_409_str': member_id == "409",
        'memberid_409_any': str(member_id) == "409"
    }

    is_lanza = any(conditions.values())

    return is_lanza, {
        'debug_info': debug_info,
        'conditions': conditions,
        'final_result': is_lanza
    }

def test_random_2019_bills():
    """Test detection on random 2019 bills to see what we're missing"""

    print("\n=== TESTING RANDOM 2019 BILLS ===")

    try:
        url = f"{BASE_URL}/bills/2019"
        response = requests.get(url, params={"key": API_KEY, "limit": 20, "offset": 500}, timeout=30)

        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                bills = data.get('result', {}).get('items', [])

                print(f"Retrieved {len(bills)} random bills from 2019")

                for i, bill in enumerate(bills):
                    sponsor = bill.get('sponsor', {}).get('member', {})
                    full_name = sponsor.get('fullName', 'Unknown')
                    member_id = sponsor.get('memberId', 'Unknown')

                    # Test our improved detection
                    is_lanza, details = improved_detection_logic(bill)

                    print(f"  Bill {i+1}: {bill.get('basePrintNo', 'N/A')} - Sponsor: {full_name} (ID: {member_id}) - Lanza: {is_lanza}")

                    if is_lanza:
                        print(f"    🎯 FOUND LANZA BILL: {bill.get('title', '')[:60]}...")

    except Exception as e:
        print(f"Error testing 2019 bills: {e}")

def main():
    debug_known_bill_structure()
    test_random_2019_bills()

if __name__ == "__main__":
    main()