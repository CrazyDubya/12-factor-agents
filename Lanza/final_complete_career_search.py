import requests
import json
from datetime import datetime
from collections import Counter, defaultdict
import time

API_KEY = "gNyGkkPgvKrEKXaq7OehFL5D65t4S7yM"
BASE_URL = "https://legislation.nysenate.gov/api/3"

def complete_career_search():
    """Complete search across ALL years with proper deep pagination"""

    print("=== COMPLETE LANZA CAREER SEARCH (2007-2025) ===")
    print("Using deep pagination to find ALL bills across entire career")
    print("=" * 60)

    # All years from 2007-2025
    all_years = list(range(2007, 2026))

    career_results = {
        'search_timestamp': datetime.now().isoformat(),
        'years_searched': all_years,
        'year_results': {},
        'all_lanza_bills': [],
        'career_totals': {}
    }

    total_career_bills = 0

    for year in all_years:
        print(f"\n{'='*50}")
        print(f"SEARCHING YEAR {year}")
        print(f"{'='*50}")

        year_bills = search_year_complete(year)

        career_results['year_results'][str(year)] = {
            'bills_found': len(year_bills),
            'bills': year_bills
        }

        career_results['all_lanza_bills'].extend(year_bills)
        total_career_bills += len(year_bills)

        print(f"Year {year} complete: {len(year_bills)} Lanza bills found")

        if len(year_bills) > 0:
            print("Sample bills:")
            for bill in year_bills[:3]:
                print(f"  {bill.get('basePrintNo', 'N/A')}: {bill.get('title', '')[:60]}...")

    # Final career analysis
    print(f"\n{'='*60}")
    print("=== COMPLETE CAREER SUMMARY ===")
    print(f"✓ Total years searched: {len(all_years)}")
    print(f"✓ Total career bills found: {total_career_bills}")

    # Year-by-year breakdown
    years_with_activity = []
    for year_str, data in career_results['year_results'].items():
        year = int(year_str)
        bill_count = data['bills_found']

        if bill_count > 0:
            years_with_activity.append(year)
            print(f"  {year}: {bill_count} bills")

    print(f"✓ Years with legislative activity: {len(years_with_activity)}")
    print(f"✓ Active years: {years_with_activity}")

    # Policy analysis
    policy_classification = Counter()
    for bill in career_results['all_lanza_bills']:
        title = bill.get('title', '').lower()

        if any(term in title for term in ['trafficking', 'victim', 'exploitation']):
            policy_classification['Human Trafficking'] += 1
        elif any(term in title for term in ['animal', 'companion', 'pet']):
            policy_classification['Animal Welfare'] += 1
        elif any(term in title for term in ['crime', 'criminal', 'penalty', 'sentence']):
            policy_classification['Criminal Justice'] += 1
        elif any(term in title for term in ['license', 'driver', 'vehicle', 'motor']):
            policy_classification['Transportation'] += 1
        elif any(term in title for term in ['education', 'school', 'student', 'teacher']):
            policy_classification['Education'] += 1
        elif any(term in title for term in ['health', 'medical', 'insurance']):
            policy_classification['Healthcare'] += 1
        elif any(term in title for term in ['tax', 'revenue', 'budget']):
            policy_classification['Fiscal Policy'] += 1
        else:
            policy_classification['Other'] += 1

    career_results['career_totals'] = {
        'total_bills': total_career_bills,
        'years_active': len(years_with_activity),
        'active_years_list': years_with_activity,
        'policy_breakdown': dict(policy_classification),
        'most_productive_year': max(career_results['year_results'].items(),
                                   key=lambda x: x[1]['bills_found'])[0] if career_results['year_results'] else None
    }

    print(f"✓ Policy breakdown: {dict(policy_classification.most_common(5))}")

    # Save complete results
    with open('complete_lanza_career.json', 'w') as f:
        json.dump(career_results, f, indent=2, default=str)

    print(f"\n✅ Complete career search saved to 'complete_lanza_career.json'")

    return career_results

def search_year_complete(year):
    """Complete search of a single year with deep pagination"""

    url = f"{BASE_URL}/bills/{year}"
    year_lanza_bills = []

    # Start with larger offsets since we know bills can be scattered
    offset = 0
    limit = 1000  # Larger chunks for efficiency

    consecutive_empty = 0  # Track empty responses
    max_empty = 3  # Stop after 3 consecutive empty responses

    while consecutive_empty < max_empty:
        try:
            params = {
                "key": API_KEY,
                "limit": limit,
                "offset": offset
            }

            response = requests.get(url, params=params, timeout=60)

            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    result = data.get('result', {})
                    items = result.get('items', [])

                    if not items:
                        consecutive_empty += 1
                        if consecutive_empty == 1:  # First empty response
                            print(f"    No more bills at offset {offset}")
                        offset += limit
                        continue
                    else:
                        consecutive_empty = 0  # Reset counter

                    print(f"    Checking offset {offset}: {len(items)} bills")

                    # Check for Lanza bills
                    lanza_in_chunk = 0
                    for bill in items:
                        if is_lanza_bill(bill):
                            lanza_in_chunk += 1
                            # Avoid duplicates
                            bill_id = f"{bill.get('basePrintNo', '')}-{year}"
                            if not any(b.get('basePrintNo') == bill.get('basePrintNo') for b in year_lanza_bills):
                                year_lanza_bills.append(bill)

                    if lanza_in_chunk > 0:
                        print(f"      → Found {lanza_in_chunk} Lanza bills in this chunk")

                    offset += len(items)

                    # Safety limit - if we've gone through 10k+ bills and no recent finds, stop
                    if offset > 10000:
                        print(f"    Reached safety limit at offset {offset}")
                        break

                else:
                    print(f"    API Error: {data.get('message', 'Unknown')}")
                    break
            else:
                print(f"    HTTP Error: {response.status_code}")
                break

        except Exception as e:
            print(f"    Exception: {e}")
            break

        time.sleep(0.2)  # Minimal rate limiting

    return year_lanza_bills

def is_lanza_bill(bill):
    """Check if bill is sponsored by Lanza"""
    if not bill or not isinstance(bill, dict):
        return False

    sponsor = bill.get('sponsor', {})
    if not sponsor:
        return False

    member = sponsor.get('member', {})
    if not member:
        return False

    full_name = member.get('fullName', '')
    member_id = member.get('memberId')

    return ('lanza' in str(full_name).lower() or member_id == 409)

if __name__ == "__main__":
    complete_career_search()