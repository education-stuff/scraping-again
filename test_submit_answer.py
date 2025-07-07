#!/usr/bin/env python3
"""Test submitting an answer to get explanation"""

import requests
from bs4 import BeautifulSoup
import json

# Setup session
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Cookie': 'csrftoken=bv47FTGEONa0XFN7mNmVpAsfiix0GD9X; initial_url="http://127.0.0.1:5500/"; _ga_9XC7HL2GZF=GS2.1.s1751081527$o41$g0$t1751081527$j60$l0$h1145318045; _ga=GA1.1.612205866.1750286024; _ga_WD0CE4KQWK=GS2.1.s1751081528$o41$g0$t1751081528$j60$l0$h1704481143; sessionid=uoxyo4sfl6rdh8ampevvl9gtidy957ra; messages=W1siX19qc29uX21lc3NhZ2UiLDAsMjUsIlN1Y2Nlc3NmdWxseSBzaWduZWQgaW4gYXMgZzRnNmo3bnR0eXkuIiwiIl1d:1uSW2B:mZtkkSbkf0zqUOJJoN_klzqBMIb6FBIlnmZqCuRDXts',
})

# Test submitting answer
question_id = 3130
exam_id = 46
answer_id = 11045  # Answer A

submit_url = f"https://oneprep.xyz/question/{question_id}/submit/"
csrf_token = 'bv47FTGEONa0XFN7mNmVpAsfiix0GD9X'

data = {
    'csrfmiddlewaretoken': csrf_token,
    'answer_choice_id': str(answer_id),
    'exam_id': str(exam_id),
    'question_set': 'exam'
}

headers = {
    'X-CSRFToken': csrf_token,
    'Content-Type': 'application/x-www-form-urlencoded',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': f'https://oneprep.xyz/question/{question_id}/?question_set=exam&exam_id={exam_id}'
}

print(f"Submitting answer to: {submit_url}")
print(f"Data: {data}")

response = session.post(submit_url, data=data, headers=headers)
print(f"\nStatus code: {response.status_code}")
print(f"Content-Type: {response.headers.get('Content-Type', 'N/A')}")

if response.status_code == 200:
    # Check if JSON
    if 'json' in response.headers.get('Content-Type', ''):
        try:
            data = response.json()
            print("\nJSON Response:")
            print(json.dumps(data, indent=2))
            
            # Save full response for analysis
            with open('submit_response.json', 'w') as f:
                json.dump(data, f, indent=2)
            print("\nFull response saved to submit_response.json")
            
        except Exception as e:
            print(f"Failed to parse as JSON: {e}")
    else:
        print(f"\nHTML Response (first 1000 chars):")
        print(response.text[:1000])
        
        # Save for analysis
        with open('submit_response.html', 'w') as f:
            f.write(response.text)
        print("\nFull response saved to submit_response.html")
else:
    print(f"Failed with status: {response.status_code}")
    print(response.text[:500])
