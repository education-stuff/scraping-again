#!/usr/bin/env python3
"""
Quick check of the newly scraped Math Module 1
"""

import json

file_path = "scraped_data/Advanced_Online_Test/Math/The_Princeton_Review_Digital_SAT_Advanced_Online_Test_Math_Module_1.json"

with open(file_path, 'r', encoding='utf-8') as f:
    questions = json.load(f)

print(f"Total questions in Math Module 1: {len(questions)}")

# Count types
spr_count = sum(1 for q in questions if not q['answer_choices'])
mc_count = sum(1 for q in questions if q['answer_choices'])

print(f"  - Multiple choice: {mc_count}")
print(f"  - SPR (open-ended): {spr_count}")

# Show question IDs
question_ids = sorted([q['question_id'] for q in questions])
print(f"\nQuestion IDs: {question_ids}")
