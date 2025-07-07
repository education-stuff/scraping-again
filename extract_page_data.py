#!/usr/bin/env python3
"""Extract the Alpine.js data structure from the page"""

import requests
from bs4 import BeautifulSoup
import json
import re
import os

def load_cookies():
    cookies_file = 'oneprep_cookies.json'
    if not os.path.exists(cookies_file):
        print(f"Error: Cookies file not found at {cookies_file}")
        return None
    
    with open(cookies_file, 'r') as f:
        cookies_list = json.load(f)
    
    return {c['name']: c['value'] for c in cookies_list}

def extract_data():
    cookies = load_cookies()
    if not cookies:
        return
    
    # Get the page
    question_id = 3130
    exam_id = 46
    url = f"https://oneprep.xyz/question/{question_id}/?question_set=exam&exam_id={exam_id}"
    
    session = requests.Session()
    session.cookies.update(cookies)
    
    response = session.get(url)
    
    if response.status_code != 200:
        print(f"Failed to get page: {response.status_code}")
        return
    
    html = response.text
    
    # Look for answer_choices data
    answer_choices_pattern = r'answer_choices:\s*(\[.*?\])'
    match = re.search(answer_choices_pattern, html, re.DOTALL)
    
    if match:
        answer_choices_str = match.group(1)
        print("Found answer_choices data:")
        print(answer_choices_str)
        
        # Try to parse as JSON
        try:
            answer_choices_data = json.loads(answer_choices_str)
            print("\nParsed answer_choices:")
            print(json.dumps(answer_choices_data, indent=2))
            
            # Check if any explanations are present
            for choice in answer_choices_data:
                if choice.get('explanation'):
                    print(f"\nExplanation found for {choice['letter']}: {choice['explanation']}")
                else:
                    print(f"\nNo explanation for {choice['letter']}")
                    
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")
    else:
        print("No answer_choices pattern found")
    
    # Look for explanation modal content
    explanation_pattern = r'<dialog id="explanation".*?</dialog>'
    exp_match = re.search(explanation_pattern, html, re.DOTALL)
    
    if exp_match:
        print("\nFound explanation modal:")
        print(exp_match.group(0)[:500] + "...")
    else:
        print("\nNo explanation modal found")
    
    # Look for Alpine.js store initialization
    store_pattern = r'Alpine\.store\([^)]+\)'
    store_matches = re.findall(store_pattern, html)
    
    if store_matches:
        print(f"\nFound {len(store_matches)} Alpine store initializations:")
        for match in store_matches:
            print(f"  {match}")
    else:
        print("\nNo Alpine.store initializations found")

if __name__ == "__main__":
    extract_data()
