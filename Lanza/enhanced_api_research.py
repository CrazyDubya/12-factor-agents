import requests
import json
from datetime import datetime

API_KEY = "gNyGkkPgvKrEKXaq7OehFL5D65t4S7yM"

# Multiple API endpoints to try
endpoints = [
    "https://legislation.nysenate.gov/api/3/bills/search",
    "https://legislation.nysenate.gov/api/3/bills",
    "https://nysenate.gov/api/3/bills/search",
    "https://legislation.nysenate.gov/api/v2/bills/search",
    "https://www.nysenate.gov/api/3/bills/search"
]

# Enhanced search parameters
search_params = [
    {"term": "sponsor:Lanza", "key": API_KEY, "limit": 100},
    {"sponsor": "Lanza", "key": API_KEY, "limit": 100},
    {"query": "sponsor:Lanza", "key": API_KEY, "limit": 100},
    {"term": "Lanza", "key": API_KEY, "limit": 100}
]

print("=== NY Senate API Research ===")
print(f"Timestamp: {datetime.now()}")
print()

for i, base_url in enumerate(endpoints):
    print(f"Testing endpoint {i+1}: {base_url}")

    for j, params in enumerate(search_params):
        try:
            response = requests.get(base_url, params=params, timeout=10)
            print(f"  Params {j+1}: Status {response.status_code}")

            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"    SUCCESS! Found data structure:")
                    if isinstance(data, dict):
                        print(f"    Keys: {list(data.keys())}")
                        if 'result' in data and 'items' in data['result']:
                            print(f"    Bill count: {len(data['result']['items'])}")
                            if data['result']['items']:
                                first_bill = data['result']['items'][0]
                                print(f"    First bill: {first_bill.get('printNo', 'N/A')} - {first_bill.get('title', 'N/A')[:100]}...")
                    elif isinstance(data, list):
                        print(f"    List length: {len(data)}")

                    # Save successful response
                    with open(f'api_response_{i+1}_{j+1}.json', 'w') as f:
                        json.dump(data, f, indent=2)
                    print(f"    Saved response to api_response_{i+1}_{j+1}.json")

                except json.JSONDecodeError:
                    print(f"    Response not JSON. Length: {len(response.text)}")

            else:
                print(f"    Error: {response.status_code}")
                if len(response.text) < 500:
                    print(f"    Response: {response.text[:200]}...")

        except requests.exceptions.RequestException as e:
            print(f"    Request failed: {e}")
        except Exception as e:
            print(f"    Unexpected error: {e}")

    print()

# Try direct bill lookup if we know specific bill numbers
known_bills = ["S5914", "S7356", "S2589", "S5988A", "S8874"]
print("=== Testing known bill lookups ===")

bill_endpoints = [
    "https://legislation.nysenate.gov/api/3/bills/2025/",
    "https://www.nysenate.gov/api/3/bills/2025/",
]

for bill in known_bills:
    year = "2025" if bill in ["S5914", "S7356"] else "2017"
    print(f"Looking up {bill} ({year}):")

    for endpoint in bill_endpoints:
        try:
            url = f"{endpoint.replace('2025', year)}{bill}"
            response = requests.get(url, params={"key": API_KEY}, timeout=10)
            print(f"  {url}: Status {response.status_code}")

            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"    Found bill data! Keys: {list(data.keys()) if isinstance(data, dict) else 'List'}")
                    with open(f'bill_{bill}_{year}.json', 'w') as f:
                        json.dump(data, f, indent=2)
                    print(f"    Saved to bill_{bill}_{year}.json")
                except json.JSONDecodeError:
                    print(f"    Not JSON response")

        except Exception as e:
            print(f"    Error: {e}")
    print()

print("Research complete! Check generated JSON files for data.")