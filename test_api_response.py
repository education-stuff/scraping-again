#!/usr/bin/env python3
"""Test the new API response to see what it returns"""

from oneprep_scraper_v2 import OnePrepScraperV2
import json

scraper = OnePrepScraperV2()
question_id = 3130
exam_id = 46
answer_id = 11047  # Choice C

# Submit the answer
submit_url = "https://oneprep.xyz/api/v1/questions/answers/submit"

data = {
    'question_id': str(question_id),
    'answer_choice_id': str(answer_id),
    'exam_id': str(exam_id),
    'question_set': 'exam'
}

headers = {
    'X-CSRFToken': scraper.csrf_token,
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest',
}

try:
    response = scraper.session.post(submit_url, json=data, headers=headers)
    
    print(f"Status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('content-type')}")
    
    if response.status_code == 200:
        result = response.json()
        print("\nFull Response:")
        print(json.dumps(result, indent=2))
        
        # Check structure
        print("\nResponse type:", type(result))
        if isinstance(result, dict):
            print("Keys:", list(result.keys()))
        elif isinstance(result, int):
            print("Got an integer response:", result)
    else:
        print(f"Error response: {response.text}")
except Exception as e:
    print(f"Exception: {e}")
