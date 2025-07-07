#!/usr/bin/env python3
"""
Performs a deep verification of the scraped math module files.
"""

import json
import os

# Define the expected structure and content for the math modules
EXPECTED_MODULES = {
    "The_Princeton_Review_Digital_SAT_Advanced_Online_Test_Math_Module_1.json": {
        "start_id": 12562, "end_id": 12583, "count": 22
    },
    "The_Princeton_Review_Digital_SAT_Advanced_Online_Test_Math_Module_2_Easy.json": {
        "start_id": 12584, "end_id": 12605, "count": 22
    },
    "The_Princeton_Review_Digital_SAT_Advanced_Online_Test_Math_Module_2_Hard.json": {
        "start_id": 12606, "end_id": 12627, "count": 22
    }
}

MATH_DIR = "scraped_data/Advanced_Online_Test/Math"

print("\n🔬 Performing Deep Verification of Scraped Math Modules...")
print("=" * 60)

all_checks_passed = True

for filename, expected in EXPECTED_MODULES.items():
    file_path = os.path.join(MATH_DIR, filename)
    print(f"\nVerifying file: {filename}...")

    # 1. Check if file exists
    if not os.path.exists(file_path):
        print("  ❌ Status: FAILED - File not found.")
        all_checks_passed = False
        continue
    
    with open(file_path, 'r', encoding='utf-8') as f:
        questions = json.load(f)

    # 2. Verify question count
    actual_count = len(questions)
    if actual_count != expected['count']:
        print(f"  ❌ Status: FAILED - Incorrect question count.")
        print(f"     Expected: {expected['count']}, Found: {actual_count}")
        all_checks_passed = False
        continue
    else:
        print(f"  ✅ Question Count: OK ({actual_count} questions)")

    # 3. Analyze Question IDs
    question_ids = [q['question_id'] for q in questions]
    min_id, max_id = min(question_ids), max(question_ids)
    
    id_check_passed = True
    if min_id != expected['start_id'] or max_id != expected['end_id']:
        print(f"  ❌ ID Range: FAILED - Mismatch.")
        print(f"     Expected: {expected['start_id']}-{expected['end_id']}")
        print(f"     Found:    {min_id}-{max_id}")
        id_check_passed = False
        all_checks_passed = False

    if len(question_ids) != len(set(question_ids)):
        print(f"  ❌ Duplicates: FAILED - Duplicate question IDs found.")
        id_check_passed = False
        all_checks_passed = False

    if id_check_passed:
        print(f"  ✅ Question IDs: OK (Range: {min_id}-{max_id}, No duplicates)")

    # 4. Confirm Content Types
    spr_count = sum(1 for q in questions if not q['answer_choices'])
    mc_count = actual_count - spr_count
    print(f"  ✅ Content Types: OK (MCQs: {mc_count}, SPRs: {spr_count})")

print("\n" + "=" * 60)
if all_checks_passed:
    print("🎉 Final Result: SUCCESS")
    print("   All checks passed. The math files are complete and nothing is missing.")
else:
    print("🔥 Final Result: FAILURE")
    print("   One or more verification checks failed. Please review the output above.")
