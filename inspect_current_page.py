#!/usr/bin/env python3
"""Inspect the current page structure to understand how explanations work now"""

import requests
from bs4 import BeautifulSoup
import json
import os

# Load cookies
def load_cookies():
    cookies_file = 'oneprep_cookies.json'
    if not os.path.exists(cookies_file):
        print(f"Error: Cookies file not found at {cookies_file}")
        return None
    
    with open(cookies_file, 'r') as f:
        cookies_list = json.load(f)
    
    return {c['name']: c['value'] for c in cookies_list}

def inspect_page():
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
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Look for explanation-related elements
    print("=== SEARCHING FOR EXPLANATION ELEMENTS ===")
    
    # Check for explanation div
    exp_div = soup.find('div', id='question-explanation')
    if exp_div:
        print(f"Found explanation div: {exp_div}")
    else:
        print("No explanation div found")
    
    # Look for explanation button
    exp_button = soup.find('button', string=lambda x: x and 'explanation' in x.lower())
    if exp_button:
        print(f"Found explanation button: {exp_button}")
    else:
        print("No explanation button found")
    
    # Look for Alpine.js data with explanation
    elements_with_alpine = soup.find_all(attrs={'x-data': True})
    print(f"\nFound {len(elements_with_alpine)} elements with x-data attributes")
    
    for elem in elements_with_alpine:
        alpine_data = elem.get('x-data', '')
        if 'explanation' in alpine_data.lower():
            print(f"Alpine element with explanation: {elem}")
    
    # Look for any scripts containing explanation logic
    scripts = soup.find_all('script')
    print(f"\nFound {len(scripts)} script tags")
    
    for script in scripts:
        if script.string and 'explanation' in script.string.lower():
            print(f"Script with explanation: {script.string[:200]}...")
    
    # Look for any forms or buttons that might submit answers
    forms = soup.find_all('form')
    print(f"\nFound {len(forms)} forms")
    
    for form in forms:
        print(f"Form action: {form.get('action', 'No action')}")
        print(f"Form method: {form.get('method', 'No method')}")
    
    # Look for answer choice elements
    answer_choices = soup.find('div', id='answer-choices')
    if answer_choices:
        print("\nAnswer choices container found")
        # Look for clickable elements
        clickable = answer_choices.find_all(attrs={'@click': True})
        print(f"Found {len(clickable)} clickable elements in answer choices")
        for elem in clickable:
            print(f"Clickable: @click='{elem.get('@click')}'")
    
    # Save full page for inspection
    with open('current_page.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
    print("\nFull page saved to current_page.html")

if __name__ == "__main__":
    inspect_page()
