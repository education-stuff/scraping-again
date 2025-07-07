import requests
import json
import os

# --- Configuration ---
BASE_URL = "https://oneprep.xyz"
# Use a question and answer ID that we know exists from previous tests
TEST_QUESTION_ID = 3130
TEST_ANSWER_ID = 11047 # This is the ID for answer C
TEST_EXAM_ID = 46

COOKIES_FILE = 'oneprep_cookies.json'

def load_cookies_and_token():
    """Load cookies and CSRF token from the cookies file."""
    if not os.path.exists(COOKIES_FILE):
        print(f"Error: Cookies file not found at {COOKIES_FILE}")
        print("Please run the main scraper once to generate it.")
        return None, None

    with open(COOKIES_FILE, 'r') as f:
        cookies_list = json.load(f)
    
    cookies = {c['name']: c['value'] for c in cookies_list}
    csrf_token = cookies.get('csrftoken')
    
    if not csrf_token:
        print("Error: CSRF token not found in cookies file.")
        return None, None
        
    return cookies, csrf_token

def debug_explanation_api():
    """Makes a direct call to the explanation API and prints the full response."""
    print("--- Starting Explanation API Debug ---")
    
    cookies, csrf_token = load_cookies_and_token()
    if not cookies:
        return

    api_url = f"{BASE_URL}/api/v1/questions/answers/submit"
    
    payload = {
        'question_id': str(TEST_QUESTION_ID),
        'answer_choice_id': str(TEST_ANSWER_ID),
        'exam_id': str(TEST_EXAM_ID),
        'question_set': 'exam'
    }
    
    headers = {
        'X-CSRFToken': csrf_token,
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': f"{BASE_URL}/question/{TEST_QUESTION_ID}/?question_set=exam&exam_id={TEST_EXAM_ID}"
    }
    
    print(f"Sending POST request to: {api_url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        with requests.Session() as session:
            session.cookies.update(cookies)
            response = session.post(api_url, json=payload, headers=headers)
            
            print(f"\n--- API Response ---")
            print(f"Status Code: {response.status_code}")
            print("\nResponse Headers:")
            for key, value in response.headers.items():
                print(f"  {key}: {value}")
            
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
    debug_explanation_api()
