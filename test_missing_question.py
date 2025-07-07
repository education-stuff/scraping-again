#!/usr/bin/env python3
"""
Test accessing a missing question ID
"""

from oneprep_scraper_v2 import OnePrepScraperV2
import requests

# Create scraper instance
scraper = OnePrepScraperV2()

# Test a missing question ID
missing_id = 12565
exam_id = 419

print(f"Testing missing question ID: {missing_id}")
print(f"URL: {scraper.base_url}/question/{missing_id}/?question_set=exam&exam_id={exam_id}")

# Try to access it
url = f"{scraper.base_url}/question/{missing_id}/?question_set=exam&exam_id={exam_id}"
response = scraper.session.get(url, timeout=20)

print(f"\nResponse status: {response.status_code}")
print(f"Response length: {len(response.text)} chars")

# Check if it's a 404 or redirects
if response.status_code == 404:
    print("❌ Question not found (404)")
elif response.status_code == 200:
    # Check if there's actual question content
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    stem_elem = soup.find('div', id='question-stem')
    if stem_elem:
        print("✅ Question exists but was skipped")
        print(f"Question stem: {stem_elem.text.strip()[:100]}...")
    else:
        print("⚠️ Page loads but no question content found")
