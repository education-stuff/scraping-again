#!/usr/bin/env python3
"""Test fetching explanations directly"""

import requests
from bs4 import BeautifulSoup
import json

# Setup session
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Cookie': 'csrftoken=bv47FTGEONa0XFN7mNmVpAsfiix0GD9X; initial_url="http://127.0.0.1:5500/"; _ga_9XC7HL2GZF=GS2.1.s1751081527$o41$g0$t1751081527$j60$l0$h1145318045; _ga=GA1.1.612205866.1750286024; _ga_WD0CE4KQWK=GS2.1.s1751081528$o41$g0$t1751081528$j60$l0$h1704481143; sessionid=uoxyo4sfl6rdh8ampevvl9gtidy957ra; messages=W1siX19qc29uX21lc3NhZ2UiLDAsMjUsIlN1Y2Nlc3NmdWxseSBzaWduZWQgaW4gYXMgZzRnNmo3bnR0eXkuIiwiIl1d:1uSW2B:mZtkkSbkf0zqUOJJoN_klzqBMIb6FBIlnmZqCuRDXts',
})

# Test fetching explanation directly from endpoint
question_id = 3130
exam_id = 46

exp_url = f"https://oneprep.xyz/question/{question_id}/explanation/?exam_id={exam_id}"
print(f"Fetching explanation from: {exp_url}")

response = session.get(exp_url)
print(f"Status code: {response.status_code}")
print(f"Content-Type: {response.headers.get('Content-Type', 'N/A')}")

if response.status_code == 200:
    # Check if JSON
    if 'json' in response.headers.get('Content-Type', ''):
        try:
            data = response.json()
            print("\nJSON Response:")
            print(json.dumps(data, indent=2)[:500])
            
            if 'explanation' in data:
                print(f"\nExplanation field found, length: {len(data['explanation'])}")
            if 'html' in data:
                print(f"\nHTML field found, length: {len(data['html'])}")
        except:
            print("Failed to parse as JSON")
    else:
        print(f"\nHTML Response (first 500 chars):")
        print(response.text[:500])
        
        # Try to parse and find explanation
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for various explanation containers
        for selector in ['#question-explanation', '.explanation', '[class*=explanation]', '.content']:
            elem = soup.select_one(selector)
            if elem:
                print(f"\nFound element with selector '{selector}':")
                print(str(elem)[:200])
                break
else:
    print(f"Failed with status: {response.status_code}")
    print(response.text[:200])
