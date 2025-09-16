import requests
import json
from datetime import datetime
import time

API_KEY = "gNyGkkPgvKrEKXaq7OehFL5D65t4S7yM"
BASE_URL = "https://legislation.nysenate.gov/api/3"

def find_lanza_in_pagination(session=2019):
    """Find exactly where Lanza's bills appear in the pagination"""

    print(f"=== FINDING LANZA BILLS IN {session} PAGINATION ===")

    url = f"{BASE_URL}/bills/{session}"

    # Search through larger chunks to find where Lanza bills are
    offsets_to_try = [0, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000]

    total_lanza_found = 0
    lanza_bills_locations = []

    for offset in offsets_to_try:
        print(f"\nTesting offset {offset}:")

        try:
            params = {
                "key": API_KEY,
                "limit": 500,
                "offset": offset
            }

            response = requests.get(url, params=params, timeout=60)

            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    result = data.get('result', {})
                    items = result.get('items', [])
                    total_available = result.get('total', 0)
                    offset_start = result.get('offsetStart', offset)
                    offset_end = result.get('offsetEnd', offset + len(items))

                    print(f"  Retrieved {len(items)} bills")
                    print(f"  Total available: {total_available}")
                    print(f"  Offset range: {offset_start} to {offset_end}")

                    if not items:
                        print(f"  No more bills at offset {offset}")
                        break

                    # Check for Lanza bills in this chunk
                    lanza_in_chunk = 0
                    for i, bill in enumerate(items):
                        sponsor = bill.get('sponsor', {}).get('member', {})
                        if sponsor:
                            full_name = sponsor.get('fullName', '')
                            member_id = sponsor.get('memberId')

                            if 'lanza' in full_name.lower() or member_id == 409:
                                lanza_in_chunk += 1
                                bill_position = offset + i

                                lanza_bills_locations.append({
                                    'position': bill_position,
                                    'offset_chunk': offset,
                                    'bill_number': bill.get('basePrintNo', 'N/A'),
                                    'title': bill.get('title', '')[:60] + '...'
                                })

                                print(f"    🎯 LANZA BILL #{bill_position}: {bill.get('basePrintNo')} - {bill.get('title', '')[:50]}...")

                    total_lanza_found += lanza_in_chunk
                    print(f"  Lanza bills in this chunk: {lanza_in_chunk}")

                    # If we hit the limit, we may need to adjust
                    if len(items) < 500:
                        print(f"  Reached end of results (got {len(items)} < 500)")
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

        time.sleep(1)  # Rate limiting

    print(f"\n=== PAGINATION SEARCH RESULTS ===")
    print(f"Total Lanza bills found: {total_lanza_found}")
    print(f"Bill positions: {[loc['position'] for loc in lanza_bills_locations]}")

    if lanza_bills_locations:
        print(f"Bills found in these offset ranges:")
        for loc in lanza_bills_locations:
            print(f"  Position {loc['position']} (offset {loc['offset_chunk']}): {loc['bill_number']} - {loc['title']}")

    return lanza_bills_locations

def compare_with_previous_method():
    """Compare with our previous successful method"""

    print(f"\n=== COMPARING WITH PREVIOUS METHOD ===")

    # Use the exact same approach that worked before
    url = f"{BASE_URL}/bills/2019"

    try:
        params = {
            "key": API_KEY,
            "limit": 1000,
            "offset": 0
        }

        response = requests.get(url, params=params, timeout=60)

        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                result = data.get('result', {})
                items = result.get('items', [])

                print(f"Previous method retrieved {len(items)} bills")

                # Check for Lanza bills
                lanza_count = 0
                for bill in items:
                    sponsor = bill.get('sponsor', {}).get('member', {})
                    if sponsor:
                        full_name = sponsor.get('fullName', '')
                        member_id = sponsor.get('memberId')

                        if 'lanza' in full_name.lower() or member_id == 409:
                            lanza_count += 1
                            print(f"  FOUND: {bill.get('basePrintNo')} - {bill.get('title', '')[:50]}...")

                print(f"Previous method found {lanza_count} Lanza bills")

                # Try second page
                print(f"\nTrying second page (offset 1000):")
                params['offset'] = 1000
                response2 = requests.get(url, params=params, timeout=60)

                if response2.status_code == 200:
                    data2 = response2.json()
                    if data2.get('success'):
                        items2 = data2.get('result', {}).get('items', [])

                        print(f"Second page retrieved {len(items2)} bills")

                        lanza_count2 = 0
                        for bill in items2:
                            sponsor = bill.get('sponsor', {}).get('member', {})
                            if sponsor:
                                full_name = sponsor.get('fullName', '')
                                member_id = sponsor.get('memberId')

                                if 'lanza' in full_name.lower() or member_id == 409:
                                    lanza_count2 += 1
                                    print(f"  FOUND: {bill.get('basePrintNo')} - {bill.get('title', '')[:50]}...")

                        print(f"Second page found {lanza_count2} Lanza bills")
                        print(f"Total from both pages: {lanza_count + lanza_count2}")

        else:
            print(f"Previous method HTTP Error: {response.status_code}")

    except Exception as e:
        print(f"Previous method exception: {e}")

def main():
    # Find where Lanza's bills are in pagination
    locations_2019 = find_lanza_in_pagination(2019)

    # Compare with what worked before
    compare_with_previous_method()

    # Test other sessions too
    for session in [2009, 2017]:
        print(f"\n{'='*50}")
        locations = find_lanza_in_pagination(session)

if __name__ == "__main__":
    main()