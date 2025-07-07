#!/usr/bin/env python3
"""
Check the test results from direct_scrape_test.py
"""

import json

# Load the test results
with open('test_math_module_1_all_questions.json', 'r', encoding='utf-8') as f:
    questions = json.load(f)

print(f"Total questions scraped: {len(questions)}")

# Get question IDs
question_ids = sorted([q['question_id'] for q in questions])
print(f"\nQuestion IDs: {question_ids}")

# Count SPR questions
spr_count = sum(1 for q in questions if not q['answer_choices'])
mc_count = sum(1 for q in questions if q['answer_choices'])

print(f"\nQuestion types:")
print(f"  - Multiple choice: {mc_count}")
print(f"  - SPR (open-ended): {spr_count}")

# Check the range
print(f"\nID range: {min(question_ids)} - {max(question_ids)}")
print(f"Expected count for full module: 22 questions")
print(f"Actual count: {len(questions)} questions")
