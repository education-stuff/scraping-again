#!/usr/bin/env python3
"""
OnePrep Scraper - Math Only (Re-scrape with correct ranges)
"""

import json
import logging
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import requests
from bs4 import BeautifulSoup

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OnePrepScraperV2:
    """Enhanced scraper that preserves HTML content"""
    
    def __init__(self, output_dir: str = "scraped_data"):
        self.base_url = "https://oneprep.xyz"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.session = self.setup_session()
        self.csrf_token = 'bv47FTGEONa0XFN7mNmVpAsfiix0GD9X'
    
    def setup_session(self) -> requests.Session:
        """Setup session with authentication"""
        session = requests.Session()
        
        # Headers with cookies included
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Referer': 'https://oneprep.xyz/exams/?source=princeton_review',
            'Connection': 'keep-alive',
            'Cookie': 'csrftoken=bv47FTGEONa0XFN7mNmVpAsfiix0GD9X; initial_url="http://127.0.0.1:5500/"; _ga_9XC7HL2GZF=GS2.1.s1751081527$o41$g0$t1751081527$j60$l0$h1145318045; _ga=GA1.1.612205866.1750286024; _ga_WD0CE4KQWK=GS2.1.s1751081528$o41$g0$t1751081528$j60$l0$h1704481143; sessionid=uoxyo4sfl6rdh8ampevvl9gtidy957ra; messages=W1siX19qc29uX21lc3NhZ2UiLDAsMjUsIlN1Y2Nlc3NmdWxseSBzaWduZWQgaW4gYXMgZzRnNmo3bnR0eXkuIiwiIl1d:1uSW2B:mZtkkSbkf0zqUOJJoN_klzqBMIb6FBIlnmZqCuRDXts',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
        })
        
        return session
    
    def extract_inner_html(self, element) -> str:
        """Extract inner HTML content preserving all formatting"""
        if not element:
            return ''
        
        # Get the inner HTML
        return ''.join(str(child) for child in element.children).strip()
    
    def extract_text_content(self, element) -> str:
        """Extract plain text for analysis (like finding correct answers)"""
        if not element:
            return ''
        return element.get_text(strip=True)
    
    def extract_answer_choices(self, soup: BeautifulSoup) -> tuple[Dict[str, str], Dict[str, int]]:
        """Extract answer choices preserving HTML content"""
        choices = {}
        choice_ids = {}
        
        # Find all divs with x-data containing answer info
        answer_divs = soup.find_all('div', {'x-data': re.compile(r'answer_id')})
        
        for div in answer_divs:
            x_data = div.get('x-data', '')
            
            # Parse answer_id and letter from x-data
            answer_id_match = re.search(r'answer_id:\s*(\d+)', x_data)
            letter_match = re.search(r"letter:\s*'([A-Z])'", x_data)
            
            if answer_id_match and letter_match:
                answer_id = int(answer_id_match.group(1))
                letter = letter_match.group(1)
                choice_ids[letter] = answer_id
                
                # Find the content div - usually has class 'self-center'
                content_div = div.find('div', class_='self-center')
                if content_div:
                    # Preserve the inner HTML
                    choices[letter] = self.extract_inner_html(content_div)
                else:
                    # Fallback: look for any text content in the div
                    choices[letter] = self.extract_inner_html(div)
        
        return choices, choice_ids
    
    def extract_metadata(self, soup: BeautifulSoup) -> Dict:
        """Extract question metadata"""
        metadata = {}
        
        # Find question metadata spans
        meta_spans = soup.find_all('span', class_='text-sm')
        for span in meta_spans:
            text = span.get_text(strip=True)
            if 'Section:' in text:
                metadata['section'] = text.replace('Section:', '').strip()
            elif 'Domain:' in text:
                metadata['domain'] = text.replace('Domain:', '').strip()
            elif 'Skill:' in text:
                metadata['skill'] = text.replace('Skill:', '').strip()
        
        return metadata
    
    def extract_embedded_data_from_page(self, html_content: str) -> tuple[str, str]:
        """Extract correct answer and explanation from embedded JavaScript data"""
        try:
            # Look for answer_choices data in the JavaScript
            pattern = r'answer_choices:\s*(\[.*?\])'
            match = re.search(pattern, html_content, re.DOTALL)
            
            if match:
                choices_json = match.group(1)
                choices_data = json.loads(choices_json)
                
                # Find the correct answer
                correct_answer = ''
                for choice in choices_data:
                    if choice.get('is_correct', False):
                        correct_answer = choice.get('letter', '')
                        break
                
                # Extract explanation from the modal dialog
                explanation = ''
                explanation_pattern = r'<div[^>]*class="[^"]*modal-dialog[^"]*"[^>]*>.*?<div[^>]*class="[^"]*modal-content[^"]*"[^>]*>(.*?)</div>'
                explanation_match = re.search(explanation_pattern, html_content, re.DOTALL)
                
                if explanation_match:
                    explanation = explanation_match.group(1).strip()
                
                return correct_answer, explanation
            
        except Exception as e:
            logger.debug(f"Error extracting embedded data: {e}")
        
        return '', ''
    
    def scrape_question(self, question_id: int, exam_data: Dict) -> Optional[Dict]:
        """Scrape a single question"""
        try:
            # Build URL with exam_id parameter
            url = f"{self.base_url}/question/{question_id}/"
            params = {
                'question_set': 'exam',
                'exam_id': exam_data['exam_id']
            }
            
            logger.info(f"🔍 Scraping question {question_id} (exam {exam_data['exam_id']})")
            
            # Get the page
            response = self.session.get(url, params=params)
            if response.status_code != 200:
                logger.warning(f"Failed to fetch question {question_id}: HTTP {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract question components
            question_data = {
                'question_id': question_id,
                'exam_id': exam_data['exam_id'],
                'exam_name': exam_data['exam_name'],
                'test_series': exam_data['test_series'],
                'subject': exam_data['subject'],
                'module_number': exam_data['module_number'],
                'difficulty': exam_data['difficulty'],
                'scraped_at': datetime.now().isoformat(),
                'url': f"{url}?{requests.compat.urlencode(params)}"
            }
            
            # Extract stimulus (passage/context)
            stimulus_div = soup.find('div', id='question-stimulus')
            if stimulus_div:
                question_data['stimulus'] = self.extract_inner_html(stimulus_div)
            
            # Extract question stem
            stem_div = soup.find('div', id='question-stem')
            if stem_div:
                question_data['question_stem'] = self.extract_inner_html(stem_div)
            else:
                logger.warning(f"No question stem found for question {question_id}")
                return None
            
            # Extract answer choices
            choices_div = soup.find('div', id='answer-choices')
            if choices_div:
                answer_choices, choice_ids = self.extract_answer_choices(choices_div)
                question_data['answer_choices'] = answer_choices
                question_data['choice_ids'] = choice_ids
            else:
                logger.warning(f"No answer choices found for question {question_id}")
                return None
            
            # Extract metadata
            metadata = self.extract_metadata(soup)
            question_data['metadata'] = metadata
            
            # Extract correct answer and explanation from embedded data
            correct_answer, explanation = self.extract_embedded_data_from_page(response.text)
            
            if correct_answer:
                question_data['correct_answer'] = correct_answer
            else:
                logger.warning(f"Could not extract correct answer for question {question_id}")
            
            if explanation:
                question_data['explanation'] = explanation
            else:
                logger.warning(f"Could not extract explanation for question {question_id}")
            
            logger.info(f"✅ Successfully scraped question {question_id}")
            return question_data
            
        except Exception as e:
            logger.error(f"Error scraping question {question_id}: {e}")
            return None
    
    def save_exam_data(self, exam_data: Dict, questions: List[Dict]):
        """Save scraped data to JSON"""
        # Create directory structure
        series_dir = self.output_dir / exam_data['test_series'].replace(' ', '_')
        subject_dir = series_dir / exam_data['subject']
        subject_dir.mkdir(parents=True, exist_ok=True)
        
        # Create filename
        filename = re.sub(r'[^\w\s-]', '', exam_data['exam_name']).strip()
        filename = re.sub(r'[-\s]+', '_', filename) + '.json'
        filepath = subject_dir / filename
        
        # Save to JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(questions, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Saved {len(questions)} questions to {filepath}")
    
    def scrape_exam(self, exam_data: Dict):
        """Scrape all questions for an exam"""
        logger.info(f"\n📚 Starting exam: {exam_data['exam_name']}")
        logger.info(f"   Questions: {exam_data['start_question_id']} to {exam_data['end_question_id']}")
        
        questions = []
        
        for question_id in range(exam_data['start_question_id'], exam_data['end_question_id'] + 1):
            question_data = self.scrape_question(question_id, exam_data)
            
            if question_data:
                questions.append(question_data)
            
            # Small delay to be respectful
            time.sleep(0.5)
        
        # Save the data
        if questions:
            self.save_exam_data(exam_data, questions)
        
        logger.info(f"✅ Completed exam: {exam_data['exam_name']} ({len(questions)} questions)")
    
    def run(self, exam_list: List[Dict]):
        """Run the scraper for all exams"""
        logger.info(f"🚀 Starting OnePrep Math Re-scraper")
        logger.info(f"   Total exams: {len(exam_list)}")
        
        for i, exam_data in enumerate(exam_list, 1):
            logger.info(f"\n{'='*60}")
            logger.info(f"Processing exam {i}/{len(exam_list)}")
            self.scrape_exam(exam_data)
        
        logger.info(f"\n🎉 Math re-scraping complete!")


# Math modules only (corrected ranges)
MATH_MODULES_ONLY = [
    {"exam_id": 419, "exam_name": "The Princeton Review - Digital SAT Advanced Online Test - Math - Module 1", 
     "test_series": "Advanced Online Test", "subject": "Math", "module_number": 1, "difficulty": None,
     "start_question_id": 12562, "end_question_id": 12583},  # 22 questions
    
    {"exam_id": 420, "exam_name": "The Princeton Review - Digital SAT Advanced Online Test - Math - Module 2 - Easy", 
     "test_series": "Advanced Online Test", "subject": "Math", "module_number": 2, "difficulty": "Easy",
     "start_question_id": 12584, "end_question_id": 12605},  # 22 questions
    
    {"exam_id": 421, "exam_name": "The Princeton Review - Digital SAT Advanced Online Test - Math - Module 2 - Hard", 
     "test_series": "Advanced Online Test", "subject": "Math", "module_number": 2, "difficulty": "Hard",
     "start_question_id": 12606, "end_question_id": 12627},  # 22 questions
]

if __name__ == "__main__":
    scraper = OnePrepScraperV2()
    
    # Run the scraper for Math modules only
    scraper.run(MATH_MODULES_ONLY)
