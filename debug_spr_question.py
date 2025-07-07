#!/usr/bin/env python3
"""
Debug script to check a specific SPR question
"""

from oneprep_scraper_v2 import OnePrepScraperV2
import logging

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# Create scraper instance
scraper = OnePrepScraperV2()

# Check a specific question that we suspect is SPR (question 12627)
question_id = 12627
exam_data = {
    'exam_id': 421,
    'exam_name': 'The Princeton Review Digital SAT Advanced Online Test Math Module 2 Hard',
    'test_series': 'Advanced Online Test',
    'subject': 'Math',
    'module_number': 2,
    'difficulty': 'Hard'
}

print(f"\n🔍 Checking question {question_id} (suspected SPR question)")
print("=" * 60)

# Scrape the question
result = scraper.scrape_question(question_id, exam_data)

if result:
    print(f"\n✅ Successfully scraped question {question_id}")
    print(f"Answer choices: {len(result['answer_choices'])} choices")
    print(f"Answer IDs: {result['answer_ids']}")
    print(f"Correct answer: {result['correct_answer']}")
    print(f"Has explanation: {'Yes' if result['explanation'] else 'No'}")
    print(f"Question stem length: {len(result['question_stem'])} chars")
    
    # Show answer choices if any
    if result['answer_choices']:
        print("\nAnswer choices:")
        for letter, content in result['answer_choices'].items():
            print(f"  {letter}: {content[:50]}...")
    else:
        print("\n⚠️ No answer choices found - likely an SPR question")
else:
    print(f"\n❌ Failed to scrape question {question_id}")
