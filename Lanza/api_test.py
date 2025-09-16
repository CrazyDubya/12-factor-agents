import requests

API_KEY = "gNyGkkPgvKrEKXaq7OehFL5D65t4S7yM"
URL = "http://legislation.nysenate.gov/api/v2/bills/search"

params = {
    "term": "sponsor:Lanza",
    "key": API_KEY,
    "view": "short"
}

try:
    response = requests.get(URL, params=params)
    print(f"Status Code: {response.status_code}")
    print("Response Text:")
    print(response.text)
except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")