#!/usr/bin/env python3
import json

# Check the ranges for each Math module
math_files = [
    'scraped_data/Advanced_Online_Test/Math/The_Princeton_Review_Digital_SAT_Advanced_Online_Test_Math_Module_1.json',
    'scraped_data/Advanced_Online_Test/Math/The_Princeton_Review_Digital_SAT_Advanced_Online_Test_Math_Module_2_Easy.json',
    'scraped_data/Advanced_Online_Test/Math/The_Princeton_Review_Digital_SAT_Advanced_Online_Test_Math_Module_2_Hard.json'
]

for file in math_files:
    with open(file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        print(f"File: {file.split('/')[-1]}")
        print(f"  Questions: {len(data)}")
        print(f"  Range: {data[0]['question_id']} to {data[-1]['question_id']}")
        print(f"  Exam ID: {data[0]['exam_id']}")
        print()
