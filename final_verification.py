#!/usr/bin/env python3
"""
Final verification script to check all scraped Math modules.
"""

import json
import os

# Directory containing the scraped math files
math_dir = "scraped_data/Advanced_Online_Test/Math"

# List of expected JSON files
json_files = [
    os.path.join(math_dir, "The_Princeton_Review_Digital_SAT_Advanced_Online_Test_Math_Module_1.json"),
    os.path.join(math_dir, "The_Princeton_Review_Digital_SAT_Advanced_Online_Test_Math_Module_2_Easy.json"),
    os.path.join(math_dir, "The_Princeton_Review_Digital_SAT_Advanced_Online_Test_Math_Module_2_Hard.json")
]

print("\n📊 Final Verification of Scraped Math Modules")
print("=" * 50)

total_questions = 0
all_files_found = True

for file_path in json_files:
    if not os.path.exists(file_path):
        print(f"\n❌ ERROR: File not found: {os.path.basename(file_path)}")
        all_files_found = False
        continue

    with open(file_path, 'r', encoding='utf-8') as f:
        questions = json.load(f)
    
    num_questions = len(questions)
    spr_count = sum(1 for q in questions if not q['answer_choices'])
    mc_count = num_questions - spr_count
    total_questions += num_questions

    print(f"\n✅ File: {os.path.basename(file_path)}")
    print(f"   - Total Questions: {num_questions}")
    print(f"   - Multiple Choice: {mc_count}")
    print(f"   - SPR (Open-Ended): {spr_count}")

print("\n" + "=" * 50)
if all_files_found:
    print(f"📈 Grand Total Scraped: {total_questions} questions")
    if total_questions == 66:
        print("🎉 SUCCESS: All 66 math questions (22 per module) have been scraped correctly!")
    else:
        print(f"⚠️ WARNING: Expected 66 questions, but found {total_questions}.")
else:
    print("🔥 FAILURE: One or more JSON files were missing.")
