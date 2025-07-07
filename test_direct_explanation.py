#!/usr/bin/env python3
"""Test fetching explanation directly"""

import requests
import json
import os

# --- Configuration ---
BASE_URL = "https://oneprep.xyz"
TEST_QUESTION_ID = 3130
TEST_EXAM_ID = 46

COOKIES_FILE = 'oneprep_cookies.json'

def load_cookies():
    """Load cookies from the cookies file."""
    if not os.path.exists(COOKIES_FILE):
        print(f"Error: Cookies file not found at {COOKIES_FILE}")
        return None

    with open(COOKIES_FILE, 'r') as f:
        cookies_list = json.load(f)
    
    return {c['name']: c['value'] for c in cookies_list}

def test_direct_explanation_endpoint():
    """Makes a direct GET request to the explanation endpoint and prints the response."""
    print("--- Starting Direct Explanation Endpoint Test ---")
    
    cookies = load_cookies()
    if not cookies:
        return

    # This is the endpoint the website's frontend code seems to call
    explanation_url = f"{BASE_URL}/question/{TEST_QUESTION_ID}/explanation/"
    
    params = {
        'exam_id': str(TEST_EXAM_ID)
    }
    
    headers = {
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': f"{BASE_URL}/question/{TEST_QUESTION_ID}/?question_set=exam&exam_id={TEST_EXAM_ID}"
    }
    
    print(f"Sending GET request to: {explanation_url}")
    print(f"Params: {params}")
    
    try:
        with requests.Session() as session:
            session.cookies.update(cookies)
            response = session.get(explanation_url, params=params, headers=headers)
            
            print(f"\n--- API Response ---")
            print(f"Status Code: {response.status_code}")
            
            print("\nResponse Body:")
            try:
                # Try to pretty-print if it's JSON
                response_json = response.json()
                print(json.dumps(response_json, indent=2))
            except json.JSONDecodeError:
                # Otherwise, print as raw text
                print(response.text)

    except requests.exceptions.RequestException as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    test_direct_explanation_endpoint()
