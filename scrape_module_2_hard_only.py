#!/usr/bin/env python3
"""
Scrape just Math Module 2 Hard
"""

from oneprep_scraper_v2 import OnePrepScraperV2
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('module_2_hard_scrape.log', mode='w') # Log to a file
    ]
)

# Just Math Module 2 Hard
MATH_MODULE_2_HARD = [
    {"exam_id": 421, "exam_name": "The Princeton Review - Digital SAT Advanced Online Test - Math - Module 2 - Hard", 
     "test_series": "Advanced Online Test", "subject": "Math", "module_number": 2, "difficulty": "Hard",
     "start_question_id": 12606, "end_question_id": 12627}
]

if __name__ == "__main__":
    scraper = OnePrepScraperV2()
    
    print("\n🚀 Scraping Math Module 2 Hard only")
    print("=" * 60)
    
    # Run the scraper
    scraper.run(MATH_MODULE_2_HARD)
    
    print("\n✅ Complete!")
