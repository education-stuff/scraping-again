#!/usr/bin/env python3
"""Test fetching a question page and analyzing the submission mechanism"""

import requests
from bs4 import BeautifulSoup
import re

# Setup session
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Cookie': 'csrftoken=bv47FTGEONa0XFN7mNmVpAsfiix0GD9X; initial_url="http://127.0.0.1:5500/"; _ga_9XC7HL2GZF=GS2.1.s1751081527$o41$g0$t1751081527$j60$l0$h1145318045; _ga=GA1.1.612205866.1750286024; _ga_WD0CE4KQWK=GS2.1.s1751081528$o41$g0$t1751081528$j60$l0$h1704481143; sessionid=uoxyo4sfl6rdh8ampevvl9gtidy957ra; messages=W1siX19qc29uX21lc3NhZ2UiLDAsMjUsIlN1Y2Nlc3NmdWxseSBzaWduZWQgaW4gYXMgZzRnNmo3bnR0eXkuIiwiIl1d:1uSW2B:mZtkkSbkf0zqUOJJoN_klzqBMIb6FBIlnmZqCuRDXts',
})

# Fetch question page
question_id = 3130
exam_id = 46
url = f"https://oneprep.xyz/question/{question_id}/?question_set=exam&exam_id={exam_id}"

print(f"Fetching: {url}")
response = session.get(url)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Save for analysis
    with open('question_page.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
    print("Page saved to question_page.html")
    
    # Look for Alpine.js data and submission logic
    print("\n=== Looking for Alpine.js submission logic ===")
    
    # Find scripts
    scripts = soup.find_all('script')
    for i, script in enumerate(scripts):
        if script.string and ('submit' in script.string or 'answer' in script.string):
            print(f"\nScript {i} with submission logic:")
            print(script.string[:500])
    
    # Look for Alpine x-data attributes
    print("\n=== Looking for Alpine.js x-data ===")
    alpine_elements = soup.find_all(attrs={'x-data': True})
    for elem in alpine_elements[:5]:  # First 5
        print(f"\nElement with x-data: {elem.name}")
        print(f"x-data: {elem.get('x-data')[:200]}...")
        
    # Look for submit buttons or forms
    print("\n=== Looking for submit elements ===")
    
    # Forms
    forms = soup.find_all('form')
    for form in forms:
        print(f"\nForm action: {form.get('action', 'N/A')}")
        print(f"Method: {form.get('method', 'N/A')}")
        
    # Buttons with @click
    buttons = soup.find_all(attrs={'@click': True})
    for btn in buttons[:5]:
        print(f"\nButton with @click: {btn.get('@click')}")
        
    # Look for explanation elements
    print("\n=== Looking for explanation elements ===")
    exp_elems = soup.find_all(id=re.compile('explanation'))
    for elem in exp_elems:
        print(f"\nFound element: {elem.name} with id='{elem.get('id')}'")
        print(f"Content: {str(elem)[:200]}...")
        
else:
    print(f"Failed to fetch page: {response.status_code}")
