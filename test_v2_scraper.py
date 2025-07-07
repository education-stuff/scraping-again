#!/usr/bin/env python3
"""Test the v2 scraper on a single math question"""

from oneprep_scraper_v2 import OnePrepScraperV2
import json

# Test on question 3130 from Prep Test 1 which has an explanation
scraper = OnePrepScraperV2()

exam_data = {
    "exam_id": 46,
    "exam_name": "The Princeton Review - Digital SAT Prep Test 1 - Math - Module 1",
    "test_series": "Prep Test 1",
    "subject": "Math",
    "module_number": 1,
    "difficulty": None
}

# Scrape single question that has explanation
question_data = scraper.scrape_question(3130, exam_data)

if question_data:
    print("\n" + "="*60)
    print("SCRAPED QUESTION DATA:")
    print("="*60)
    
    print(f"\nQuestion ID: {question_data['question_id']}")
    print(f"Subject: {question_data['metadata'].get('section', 'N/A')}")
    print(f"Domain: {question_data['metadata'].get('domain', 'N/A')}")
    print(f"Skill: {question_data['metadata'].get('skill', 'N/A')}")
    
    print(f"\nQuestion Stem (HTML preserved):")
    print(question_data['question_stem'][:200] + "..." if len(question_data['question_stem']) > 200 else question_data['question_stem'])
    
    print(f"\nAnswer Choices (HTML preserved):")
    for letter, choice in question_data['answer_choices'].items():
        print(f"{letter}: {choice}")
    
    print(f"\nCorrect Answer: {question_data['correct_answer']}")
    
    print(f"\nExplanation (first 200 chars):")
    print(question_data['explanation'][:200] + "..." if len(question_data['explanation']) > 200 else question_data['explanation'])
    
    # Save to file for inspection
    with open('test_v2_output.json', 'w', encoding='utf-8') as f:
        json.dump(question_data, f, indent=2, ensure_ascii=False)
    
    print("\n✅ Full output saved to test_v2_output.json")
else:
    print("❌ Failed to scrape question")
