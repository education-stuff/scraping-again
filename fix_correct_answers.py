#!/usr/bin/env python3
"""
Parse correct answers from explanation text and update JSON files
"""

import json
import re
from pathlib import Path

def extract_correct_answer_from_explanation(explanation):
    """Extract correct answer letter from explanation text"""
    if not explanation:
        return ''
    
    # Pattern 1: "(A) is correct because..."
    match = re.search(r'\(([A-D])\)\s+is\s+(?:correct|the\s+correct\s+answer)', explanation, re.IGNORECASE)
    if match:
        return match.group(1)
    
    # Pattern 2: "The correct answer is (A)"
    match = re.search(r'(?:correct answer is|Answer:)\s*\(?([A-D])\)?', explanation, re.IGNORECASE)
    if match:
        return match.group(1)
    
    # Pattern 3: "Choice A is correct"
    match = re.search(r'Choice\s+([A-D])\s+is\s+(?:correct|the\s+correct)', explanation, re.IGNORECASE)
    if match:
        return match.group(1)
    
    return ''

def fix_json_file(filepath):
    """Update correct answers in a JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    updated = 0
    for question in data:
        if not question.get('correct_answer') and question.get('explanation'):
            answer = extract_correct_answer_from_explanation(question['explanation'])
            if answer:
                question['correct_answer'] = answer
                updated += 1
    
    if updated > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Updated {updated} answers in {filepath.name}")
    else:
        print(f"ℹ️  No updates needed for {filepath.name}")

def main():
    scraped_dir = Path(__file__).parent / 'scraped_data'
    
    # Find all JSON files
    json_files = list(scraped_dir.rglob('*.json'))
    
    print(f"Found {len(json_files)} JSON files to process...")
    
    for json_file in json_files:
        fix_json_file(json_file)

if __name__ == '__main__':
    main()
