#!/usr/bin/env python3
"""Test the v2 scraper on a single English question"""

from oneprep_scraper_v2 import OnePrepScraperV2
import json

# English Question from Prep Test 1, English Module 1
# This question has a stimulus passage.
QUESTION_ID = 3104
EXAM_DATA = {
    'exam_id': 45,
    'exam_name': 'The Princeton Review - Digital SAT Prep Test 1 - English - Module 1',
    'test_series': 'Prep Test 1',
    'subject': 'English',
    'module_number': 1,
    'difficulty': None
}

def main():
    scraper = OnePrepScraperV2()
    question_data = scraper.scrape_question(QUESTION_ID, EXAM_DATA)
    
    if question_data:
        print("\n============================================================")
        print("SCRAPED ENGLISH QUESTION DATA:")
        print("============================================================\n")
        
        # Print a summary
        print(f"Question ID: {question_data.get('question_id')}")
        print(f"Subject: {question_data.get('subject')}")
        print(f"Domain: {question_data.get('metadata', {}).get('domain')}")
        print(f"Skill: {question_data.get('metadata', {}).get('skill')}")
        print(f"Stimulus (Passage) present: {'✓' if question_data.get('stimulus') else '✗'}")
        print(f"Correct Answer: {question_data.get('correct_answer')}")
        print(f"Explanation present: {'✓' if question_data.get('explanation') else '✗'}")

        # Save full output to a JSON file for inspection
        output_filename = 'test_v2_output_english.json'
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(question_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Full output saved to {output_filename}")

if __name__ == '__main__':
    main()
