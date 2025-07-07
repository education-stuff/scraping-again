#!/usr/bin/env python3
import json

# Check the Math Module 2 Hard range
with open('scraped_data/Advanced_Online_Test/Math/The_Princeton_Review_Digital_SAT_Advanced_Online_Test_Math_Module_2_Hard.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Math Module 2 Hard:")
print(f"  Total questions: {len(data)}")
print(f"  First question: {data[0]['question_id']}")
print(f"  Last question: {data[-1]['question_id']}")
print(f"  Expected range: 12606-12627 (22 questions)")
print(f"  Missing: {22 - len(data)} questions")

if data[-1]['question_id'] != 12627:
    print(f"  🚨 Missing question 12627!")
else:
    print(f"  ✅ All questions present")

# Check all question IDs to see if there are gaps
question_ids = [q['question_id'] for q in data]
expected_ids = list(range(12606, 12628))  # 12606 to 12627
missing_ids = [id for id in expected_ids if id not in question_ids]

if missing_ids:
    print(f"  Missing question IDs: {missing_ids}")
else:
    print(f"  All question IDs present")
