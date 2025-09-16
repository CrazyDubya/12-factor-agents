import requests
import json
from datetime import datetime
from collections import Counter, defaultdict
import time

API_KEY = "gNyGkkPgvKrEKXaq7OehFL5D65t4S7yM"
BASE_URL = "https://legislation.nysenate.gov/api/3"

def test_every_single_year():
    """Test EVERY year from 2007-2025 individually with multiple strategies"""

    print("=== TESTING EVERY SINGLE YEAR 2007-2025 ===")
    print("Checking if we're missing years due to API access issues...")
    print()

    # Test EVERY year, not just odd-numbered sessions
    all_years = list(range(2007, 2026))  # 2007, 2008, 2009, ..., 2025

    results = {}

    for year in all_years:
        print(f"=== YEAR {year} ===")
        year_results = {
            'year': year,
            'strategies_tested': [],
            'bills_found': [],
            'total_bills_in_year': 0,
            'lanza_bills': 0
        }

        # Strategy 1: Try as session year
        print(f"  Strategy 1: Bills endpoint /bills/{year}")
        try:
            url = f"{BASE_URL}/bills/{year}"
            response = requests.get(url, params={"key": API_KEY, "limit": 100}, timeout=30)

            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    bills = data.get('result', {}).get('items', [])
                    total_available = data.get('result', {}).get('total', len(bills))

                    print(f"    ✓ Success: {len(bills)} bills returned, {total_available} total available")

                    # Check for Lanza bills
                    lanza_count = 0
                    lanza_bills = []
                    for bill in bills:
                        if is_lanza_bill(bill):
                            lanza_count += 1
                            lanza_bills.append(bill)
                            print(f"      FOUND: {bill.get('basePrintNo', 'N/A')}: {bill.get('title', '')[:60]}...")

                    year_results['strategies_tested'].append('bills_endpoint')
                    year_results['bills_found'].extend(lanza_bills)
                    year_results['total_bills_in_year'] = total_available
                    year_results['lanza_bills'] += lanza_count

                    print(f"    Lanza bills: {lanza_count}")

                else:
                    print(f"    ✗ API Error: {data.get('message', 'Unknown error')}")
            else:
                print(f"    ✗ HTTP Error: {response.status_code}")
        except Exception as e:
            print(f"    ✗ Exception: {e}")

        # Strategy 2: Search by year
        print(f"  Strategy 2: Search with year filter")
        try:
            search_terms = [
                f"lanza year:{year}",
                f"sponsor:lanza year:{year}",
                f"session:{year} lanza",
                f"session:{year} sponsor:lanza"
            ]

            for term in search_terms:
                url = f"{BASE_URL}/bills/search"
                response = requests.get(url, params={"term": term, "key": API_KEY, "limit": 100}, timeout=30)

                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        bills = data.get('result', {}).get('items', [])

                        if bills:
                            print(f"    ✓ Search '{term}': {len(bills)} bills")

                            for bill in bills:
                                if is_lanza_bill(bill) and bill not in year_results['bills_found']:
                                    year_results['bills_found'].append(bill)
                                    year_results['lanza_bills'] += 1
                                    print(f"      NEW: {bill.get('basePrintNo', 'N/A')}: {bill.get('title', '')[:60]}...")
                        else:
                            print(f"    - Search '{term}': 0 bills")
                    else:
                        print(f"    ✗ Search '{term}': {data.get('message', 'API Error')}")
                else:
                    print(f"    ✗ Search '{term}': HTTP {response.status_code}")

                time.sleep(0.5)  # Rate limiting

        except Exception as e:
            print(f"    ✗ Search exception: {e}")

        # Strategy 3: Check if this might be an "off-year"
        if year_results['total_bills_in_year'] == 0:
            print(f"    NOTE: {year} appears to be an off-year (0 total bills)")
        elif year_results['lanza_bills'] == 0 and year_results['total_bills_in_year'] > 0:
            print(f"    ⚠️  WARNING: {year} has {year_results['total_bills_in_year']} total bills but 0 Lanza bills")

        results[str(year)] = year_results
        print(f"  YEAR {year} SUMMARY: {year_results['lanza_bills']} Lanza bills found")
        print()

        time.sleep(1)  # Rate limiting between years

    return results

def check_continuous_service():
    """Verify Lanza's continuous service and expected bill patterns"""

    print("=== CHECKING CONTINUOUS SERVICE PATTERN ===")

    # First, let's verify he's been continuously in office
    try:
        # Check his member profile
        member_url = f"{BASE_URL}/members"
        response = requests.get(member_url, params={"key": API_KEY}, timeout=30)

        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                members = data.get('result', {}).get('items', [])

                lanza_member = None
                for member in members:
                    if 'lanza' in str(member.get('fullName', '')).lower():
                        lanza_member = member
                        break

                if lanza_member:
                    print(f"✓ Found Lanza in members list:")
                    print(f"  Full Name: {lanza_member.get('fullName')}")
                    print(f"  Member ID: {lanza_member.get('memberId')}")
                    print(f"  District: {lanza_member.get('districtCode')}")
                    print(f"  Chamber: {lanza_member.get('chamber')}")
                    print(f"  Incumbent: {lanza_member.get('incumbent')}")
                else:
                    print("✗ Lanza not found in current members list")
            else:
                print(f"✗ Members API error: {data.get('message')}")
        else:
            print(f"✗ Members API HTTP error: {response.status_code}")

    except Exception as e:
        print(f"✗ Members API exception: {e}")

    print()

    # Check what years have ANY legislative activity
    print("=== CHECKING WHICH YEARS HAVE ANY BILLS ===")
    active_years = []

    for year in range(2007, 2026):
        try:
            url = f"{BASE_URL}/bills/{year}"
            response = requests.get(url, params={"key": API_KEY, "limit": 1}, timeout=15)

            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    bills = data.get('result', {}).get('items', [])
                    total = data.get('result', {}).get('total', 0)

                    if total > 0:
                        active_years.append(year)
                        print(f"  {year}: ✓ {total} total bills")
                    else:
                        print(f"  {year}: - No bills")
            else:
                print(f"  {year}: HTTP {response.status_code}")
        except Exception as e:
            print(f"  {year}: Error {e}")

        time.sleep(0.3)

    print(f"\nActive legislative years: {active_years}")
    print(f"Inactive years: {[y for y in range(2007, 2026) if y not in active_years]}")

    return active_years

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

            if ('lanza' in full_name or member_id == 409 or member_id == "409"):
                return True

    # Check other sponsor types
    sponsor_fields = ['coSponsors', 'multiSponsors', 'additionalSponsors']

    for field in sponsor_fields:
        sponsors = bill.get(field, {})

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

                    if ('lanza' in full_name or member_id == 409 or member_id == "409"):
                        return True

    return False

def main():
    """Main verification function"""

    print("=== COMPREHENSIVE YEAR-BY-YEAR VERIFICATION ===")
    print("Checking EVERY year from 2007-2025 individually")
    print("Looking for gaps in legislative activity...")
    print("=" * 60)
    print()

    # Step 1: Check continuous service
    active_years = check_continuous_service()
    print()

    # Step 2: Test every single year
    year_results = test_every_single_year()

    # Step 3: Analyze results
    print("=" * 60)
    print("=== COMPREHENSIVE ANALYSIS ===")

    years_with_lanza_bills = []
    years_with_no_lanza_bills = []
    total_lanza_bills = 0

    for year_str, data in year_results.items():
        year = int(year_str)
        lanza_count = data['lanza_bills']

        if lanza_count > 0:
            years_with_lanza_bills.append(year)
            total_lanza_bills += lanza_count
            print(f"  {year}: ✓ {lanza_count} Lanza bills")
        else:
            years_with_no_lanza_bills.append(year)
            if data['total_bills_in_year'] > 0:
                print(f"  {year}: ⚠️  0 Lanza bills ({data['total_bills_in_year']} total bills available)")
            else:
                print(f"  {year}: - No legislative activity")

    print()
    print(f"SUMMARY:")
    print(f"✓ Years with Lanza bills: {len(years_with_lanza_bills)}")
    print(f"✓ Active years list: {years_with_lanza_bills}")
    print(f"✓ Total Lanza bills found: {total_lanza_bills}")
    print(f"⚠️  Years with no Lanza bills: {len(years_with_no_lanza_bills)}")
    print(f"⚠️  No-bill years: {years_with_no_lanza_bills}")

    # Save comprehensive results
    final_results = {
        'verification_timestamp': datetime.now().isoformat(),
        'active_legislative_years': active_years,
        'year_by_year_results': year_results,
        'summary': {
            'total_years_checked': len(year_results),
            'years_with_lanza_bills': years_with_lanza_bills,
            'years_with_no_lanza_bills': years_with_no_lanza_bills,
            'total_lanza_bills_found': total_lanza_bills
        }
    }

    with open('year_by_year_verification.json', 'w') as f:
        json.dump(final_results, f, indent=2, default=str)

    print(f"\n✓ Complete year-by-year verification saved to 'year_by_year_verification.json'")

    if len(years_with_no_lanza_bills) > 10:
        print(f"\n🚨 ANOMALY: Too many years without bills ({len(years_with_no_lanza_bills)}/19)")
        print("This suggests systematic data collection issues!")

    return final_results

if __name__ == "__main__":
    main()