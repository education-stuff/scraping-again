#!/usr/bin/env python3
"""
Directly scrape one module and save all questions including SPR
"""

from oneprep_scraper_v2 import OnePrepScraperV2
import json
import os

# Create scraper
scraper = OnePrepScraperV2()

# Test with Math Module 1
exam_data = {
    "exam_id": 419, 
    "exam_name": "The Princeton Review - Digital SAT Advanced Online Test - Math - Module 1", 
    "test_series": "Advanced Online Test", 
    "subject": "Math", 
    "module_number": 1, 
    "difficulty": None,
    "start_question_id": 12562, 
    "end_question_id": 12583
}

print(f"🔍 Scraping {exam_data['exam_name']}")
print(f"   Range: {exam_data['start_question_id']} - {exam_data['end_question_id']}")
print("=" * 60)

questions = []
scraped_ids = []
failed_ids = []

# Scrape each question in the range
for qid in range(exam_data['start_question_id'], exam_data['end_question_id'] + 1):
    print(f"\n📝 Attempting question {qid}...", end="")
    
    result = scraper.scrape_question(qid, exam_data)
    
    if result:
        questions.append(result)
        scraped_ids.append(qid)
        
        # Show info about the question
        if result['answer_choices']:
            print(f" ✅ Multiple choice ({len(result['answer_choices'])} choices)")
        else:
            print(f" ✅ SPR question (no choices)")
    else:
        failed_ids.append(qid)
        print(f" ❌ Failed")

print("\n" + "=" * 60)
print(f"\n📊 Summary:")
print(f"   Total attempted: {exam_data['end_question_id'] - exam_data['start_question_id'] + 1}")
print(f"   Successfully scraped: {len(scraped_ids)}")
print(f"   Failed: {len(failed_ids)}")

if scraped_ids:
    print(f"\n   Scraped IDs: {scraped_ids}")
if failed_ids:
    print(f"   Failed IDs: {failed_ids}")

# Save to a test file
if questions:
    output_file = "test_math_module_1_all_questions.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)
    print(f"\n💾 Saved {len(questions)} questions to {output_file}")
