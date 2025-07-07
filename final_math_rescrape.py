#!/usr/bin/env python3
"""
Final re-scrape of Math modules with proper handling of all questions including SPR
"""

from oneprep_scraper_v2 import OnePrepScraperV2
import logging
import os
import shutil
import json

# Set up detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('math_rescrape.log')
    ]
)

# Math modules to re-scrape
MATH_MODULES = [
    {"exam_id": 419, "exam_name": "The Princeton Review - Digital SAT Advanced Online Test - Math - Module 1", 
     "test_series": "Advanced Online Test", "subject": "Math", "module_number": 1, "difficulty": None,
     "start_question_id": 12562, "end_question_id": 12583},
    
    {"exam_id": 420, "exam_name": "The Princeton Review - Digital SAT Advanced Online Test - Math - Module 2 - Easy", 
     "test_series": "Advanced Online Test", "subject": "Math", "module_number": 2, "difficulty": "Easy",
     "start_question_id": 12584, "end_question_id": 12605},
    
    {"exam_id": 421, "exam_name": "The Princeton Review - Digital SAT Advanced Online Test - Math - Module 2 - Hard", 
     "test_series": "Advanced Online Test", "subject": "Math", "module_number": 2, "difficulty": "Hard",
     "start_question_id": 12606, "end_question_id": 12627},
]

if __name__ == "__main__":
    # Clean up old files
    math_dir = "scraped_data/Advanced_Online_Test/Math"
    backup_dir = "scraped_data/Advanced_Online_Test/Math_backup"
    
    # Remove old backup if exists
    if os.path.exists(backup_dir):
        print(f"🗑️ Removing old backup directory")
        shutil.rmtree(backup_dir)
    
    # Back up current Math files
    if os.path.exists(math_dir):
        print(f"📁 Backing up existing Math files to {backup_dir}")
        shutil.copytree(math_dir, backup_dir)
        # Remove current files to start fresh
        shutil.rmtree(math_dir)
        
    scraper = OnePrepScraperV2()
    
    print("\n🚀 Final re-scrape of Math modules")
    print("=" * 60)
    
    # Run the scraper
    scraper.run(MATH_MODULES)
    
    print("\n" + "=" * 60)
    print("✅ Re-scraping complete!")
    
    # Verify the results
    print("\n📊 Verification:")
    json_files = [
        f"{math_dir}/The_Princeton_Review_Digital_SAT_Advanced_Online_Test_Math_Module_1.json",
        f"{math_dir}/The_Princeton_Review_Digital_SAT_Advanced_Online_Test_Math_Module_2_Easy.json",
        f"{math_dir}/The_Princeton_Review_Digital_SAT_Advanced_Online_Test_Math_Module_2_Hard.json"
    ]
    
    total_questions = 0
    total_spr = 0
    
    for file_path in json_files:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                questions = json.load(f)
            
            spr_count = sum(1 for q in questions if not q['answer_choices'])
            mc_count = sum(1 for q in questions if q['answer_choices'])
            
            module_name = os.path.basename(file_path).replace('.json', '').split('_')[-1]
            print(f"\n{module_name}:")
            print(f"  Total: {len(questions)} questions")
            print(f"  Multiple choice: {mc_count}")
            print(f"  SPR (open-ended): {spr_count}")
            
            total_questions += len(questions)
            total_spr += spr_count
    
    print(f"\n📈 Grand Total:")
    print(f"  All Math modules: {total_questions} questions")
    print(f"  SPR questions: {total_spr}")
    print(f"  Expected: 66 questions (22 per module)")
