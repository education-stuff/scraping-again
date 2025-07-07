#!/usr/bin/env python3
"""
Re-scrape Math modules understanding that there are gaps in question numbering
and all questions (including SPR) should be saved
"""

from oneprep_scraper_v2 import OnePrepScraperV2
import logging
import os
import shutil

# Set up logging to see what's happening
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# Math modules to re-scrape
MATH_MODULES = [
    {"exam_id": 419, "exam_name": "The Princeton Review - Digital SAT Advanced Online Test - Math - Module 1", 
     "test_series": "Advanced Online Test", "subject": "Math", "module_number": 1, "difficulty": None,
     "start_question_id": 12562, "end_question_id": 12583},  # 22 questions with gaps
    
    {"exam_id": 420, "exam_name": "The Princeton Review - Digital SAT Advanced Online Test - Math - Module 2 - Easy", 
     "test_series": "Advanced Online Test", "subject": "Math", "module_number": 2, "difficulty": "Easy",
     "start_question_id": 12584, "end_question_id": 12605},  # 22 questions with gaps
    
    {"exam_id": 421, "exam_name": "The Princeton Review - Digital SAT Advanced Online Test - Math - Module 2 - Hard", 
     "test_series": "Advanced Online Test", "subject": "Math", "module_number": 2, "difficulty": "Hard",
     "start_question_id": 12606, "end_question_id": 12627},  # 22 questions with gaps
]

if __name__ == "__main__":
    # Back up existing Math files first
    math_dir = "scraped_data/Advanced_Online_Test/Math"
    backup_dir = "scraped_data/Advanced_Online_Test/Math_backup"
    
    if os.path.exists(math_dir):
        print(f"📁 Backing up existing Math files to {backup_dir}")
        if os.path.exists(backup_dir):
            shutil.rmtree(backup_dir)
        shutil.copytree(math_dir, backup_dir)
        
    scraper = OnePrepScraperV2()
    
    print("\n🚀 Re-scraping Math modules with gap awareness")
    print("=" * 60)
    
    # Run the scraper for Math modules only
    scraper.run(MATH_MODULES)
    
    print("\n✅ Re-scraping complete!")
    print("The scraper will save all questions it can access, including SPR questions.")
