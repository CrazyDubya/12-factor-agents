import requests
import json
from datetime import datetime
import time

API_KEY = "gNyGkkPgvKrEKXaq7OehFL5D65t4S7yM"
BASE_URL = "https://legislation.nysenate.gov/api/3"

def quick_career_verification():
    """Quick verification of key years to get immediate results"""

    print("=== QUICK CAREER VERIFICATION ===")
    print("Testing key years with focused pagination...")

    # Focus on key years we know have bills
    test_years = [2019, 2017, 2015, 2013, 2011, 2009, 2025, 2023, 2021]

    career_total = 0
    year_totals = {}

    for year in test_years:
        print(f"\nChecking {year}:")

        # Quick sample from multiple offsets
        year_bills = 0
        sample_offsets = [0, 1000, 2000, 3000, 4000, 5000]

        for offset in sample_offsets:
            try:
                url = f"{BASE_URL}/bills/{year}"
                params = {"key": API_KEY, "limit": 500, "offset": offset}

                response = requests.get(url, params=params, timeout=30)

                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        items = data.get('result', {}).get('items', [])

                        if not items:
                            break  # No more bills at this offset

                        lanza_in_chunk = 0
                        for bill in items:
                            if is_lanza_bill(bill):
                                lanza_in_chunk += 1

                        year_bills += lanza_in_chunk

                        if lanza_in_chunk > 0:
                            print(f"  Offset {offset}: {lanza_in_chunk} bills")
                    else:
                        break
                else:
                    break

            except Exception as e:
                print(f"  Error at offset {offset}: {e}")
                break

            time.sleep(0.3)

        year_totals[year] = year_bills
        career_total += year_bills
        print(f"  {year} TOTAL: {year_bills} bills")

    print(f"\n=== QUICK SUMMARY ===")
    for year, count in sorted(year_totals.items()):
        print(f"{year}: {count} bills")
    print(f"SAMPLE CAREER TOTAL (key years only): {career_total} bills")

    return year_totals, career_total

def is_lanza_bill(bill):
    """Check if bill involves Lanza"""
    if not bill or not isinstance(bill, dict):
        return False

    # Check primary sponsor
    sponsor = bill.get('sponsor', {})
    if sponsor:
        member = sponsor.get('member', {})
        if member:
            full_name = str(member.get('fullName', '')).lower()
            member_id = member.get('memberId')

            if ('lanza' in full_name or member_id == 409):
                return True

    # Check co-sponsors
    for sponsor_field in ['coSponsors', 'multiSponsors', 'additionalSponsors']:
        sponsors = bill.get(sponsor_field, {})

        if isinstance(sponsors, dict):
            items = sponsors.get('items', [])
        elif isinstance(sponsors, list):
            items = sponsors
        else:
            continue

        for sponsor_item in items:
            if isinstance(sponsor_item, dict):
                member = sponsor_item.get('member', {})
                if member:
                    full_name = str(member.get('fullName', '')).lower()
                    member_id = member.get('memberId')

                    if ('lanza' in full_name or member_id == 409):
                        return True

    return False

if __name__ == "__main__":
    quick_career_verification()