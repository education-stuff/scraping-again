#!/usr/bin/env python3
import json
import os

def count_questions():
    total = 0
    base_path = 'scraped_data/Advanced_Online_Test'
    
    print("Advanced Online Test - Question Count Summary:")
    print("=" * 50)
    
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith('.json'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        count = len(data)
                        total += count
                        # Get subject from the folder name
                        subject = os.path.basename(root)
                        print(f"{subject} - {file.replace('The_Princeton_Review_Digital_SAT_Advanced_Online_Test_', '').replace('.json', '')}: {count} questions")
                except Exception as e:
                    print(f"Error reading {file}: {e}")
    
    print("=" * 50)
    print(f"Total questions scraped: {total}")
    print(f"Expected: 126 questions (12481-12606)")
    print(f"Status: {'SUCCESS' if total >= 120 else 'INCOMPLETE'}")

if __name__ == "__main__":
    count_questions()
