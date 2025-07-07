#!/usr/bin/env python3
"""Debug page content to see answer data"""

from oneprep_scraper_v2 import OnePrepScraperV2
from bs4 import BeautifulSoup
import re

scraper = OnePrepScraperV2()
question_id = 3130
exam_id = 46

# Fetch the page
question_url = f"https://oneprep.xyz/question/{question_id}/?question_set=exam&exam_id={exam_id}"
response = scraper.session.get(question_url)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Look for scripts containing answer data
    scripts = soup.find_all('script')
    
    for i, script in enumerate(scripts):
        if script.string and 'answer_choices' in script.string:
            print(f"\n=== Script {i} with answer_choices ===")
            # Extract just the relevant part
            lines = script.string.split('\n')
            in_answer_section = False
            
            for line in lines:
                if 'answer_choices_status:' in line:
                    in_answer_section = True
                    print("Found answer_choices_status:")
                    
                if in_answer_section and ('},' in line or '}' in line):
                    print(line.strip())
                    
                if 'answer_choices:' in line:
                    print("\nFound answer_choices:")
                    # Look for the next few lines that contain the answer data
                    idx = lines.index(line)
                    for j in range(idx, min(idx + 10, len(lines))):
                        if 'is_correct' in lines[j]:
                            print(lines[j].strip())
                            
    # Also try the scraper's method
    print("\n=== Testing extract_correct_answer_from_page ===")
    correct_answer = scraper.extract_correct_answer_from_page(response.text)
    print(f"Extracted correct answer: {correct_answer}")
    
    # Check if the patterns are matching
    for script in scripts:
        if script.string and 'is_correct' in script.string:
            print("\n=== Raw script content with is_correct ===")
            # Find lines with is_correct
            for line in script.string.split('\n'):
                if 'is_correct' in line:
                    print(line[:100])
