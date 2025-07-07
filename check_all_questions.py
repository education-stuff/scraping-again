#!/usr/bin/env python3
"""
Check all questions in the Math modules including their IDs
"""

import json
import glob

# Get all Math JSON files
json_files = glob.glob('scraped_data/Advanced_Online_Test/Math/*.json')

for file_path in json_files:
    with open(file_path, 'r', encoding='utf-8') as f:
        questions = json.load(f)
    
    if not questions:
        print(f"\nNo questions in {file_path}")
        continue
        
    # Get exam info from first question
    first_q = questions[0]
    print(f"\n{first_q['exam_name']}")
    print(f"Total questions: {len(questions)}")
    
    # Get question IDs
    question_ids = [q['question_id'] for q in questions]
    question_ids.sort()
    
    print(f"Question ID range: {question_ids[0]} - {question_ids[-1]}")
    
    # Try to infer expected range from question IDs
    expected_start = question_ids[0]
    expected_end = question_ids[-1]
    
    # Check for missing IDs within the range
    expected_ids = list(range(expected_start, expected_end + 1))
    missing_ids = set(expected_ids) - set(question_ids)
    
    if missing_ids:
        print(f"⚠️ Missing question IDs within range: {sorted(missing_ids)}")
    else:
        print("✅ No gaps in question ID sequence")
    
    # Count SPR questions (those with empty answer_choices)
    spr_count = sum(1 for q in questions if not q['answer_choices'])
    print(f"SPR questions (no answer choices): {spr_count}")
    
    # Show question IDs for debugging
    print(f"Question IDs: {question_ids}")
