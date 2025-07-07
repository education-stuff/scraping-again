#!/usr/bin/env python3
"""
Debug why certain questions are missing from the scrape
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

# Test the missing questions
missing_ids = [12565, 12566, 12571, 12573, 12578, 12579]
exam_data = {
    'exam_id': 419,
    'exam_name': 'The Princeton Review Digital SAT Advanced Online Test Math Module 1',
    'test_series': 'Advanced Online Test',
    'subject': 'Math',
    'module_number': 1,
    'difficulty': None
}

print("\n🔍 Testing missing questions")
print("=" * 60)

for qid in missing_ids[:2]:  # Test first 2 missing questions
    print(f"\n📋 Testing question {qid}")
    result = scraper.scrape_question(qid, exam_data)
    
    if result:
        print(f"✅ Successfully scraped!")
        print(f"   Answer choices: {len(result['answer_choices'])}")
        print(f"   Correct answer: {result['correct_answer'] or 'None'}")
        print(f"   Has explanation: {'Yes' if result['explanation'] else 'No'}")
        
        # Check if it's SPR
        if not result['answer_choices']:
            print("   📝 This is an SPR question (no answer choices)")
            print(f"   Question stem preview: {result['question_stem'][:100]}...")
    else:
        print(f"❌ Failed to scrape")
