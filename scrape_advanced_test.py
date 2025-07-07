#!/usr/bin/env python3
"""
OnePrep Scraper v2 - For Digital SAT Advanced Online Test
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
    
    def submit_answer_and_get_explanation(self, question_id: int, exam_id: int, answer_id: int) -> Tuple[Optional[str], Optional[str]]:
        """Submit an answer using the original working method to get explanation and correct answer"""
        try:
            # Submit answer
            submit_url = f"{self.base_url}/question/{question_id}/submit/"
            submit_data = {
                'csrfmiddlewaretoken': self.csrf_token,
                'answer_id': answer_id,
                'exam_id': exam_id
            }
            
            response = self.session.post(submit_url, data=submit_data)
            
            if response.status_code == 200:
                try:
                    submit_response = response.json()
                    
                    # Extract correct answer and explanation
                    correct_answer = submit_response.get('correct_answer', '')
                    explanation = submit_response.get('explanation', '')
                    
                    # Get explanation from separate endpoint if needed
                    if not explanation:
                        explanation_url = f"{self.base_url}/question/{question_id}/explanation/"
                        explanation_data = {
                            'exam_id': exam_id
                        }
                        
                        exp_response = self.session.get(explanation_url, params=explanation_data)
                        if exp_response.status_code == 200:
                            try:
                                exp_json = exp_response.json()
                                explanation = exp_json.get('explanation', '')
                            except:
                                explanation = exp_response.text
                    
                    return correct_answer, explanation
                    
                except json.JSONDecodeError:
                    logger.warning(f"Failed to decode JSON response for question {question_id}")
                    return None, None
            else:
                logger.warning(f"Submit failed with status {response.status_code} for question {question_id}")
                return None, None
                
        except Exception as e:
            logger.error(f"Error submitting answer for question {question_id}: {e}")
            return None, None
    
    def extract_correct_answer_from_explanation(self, explanation_html: str) -> str:
        """Extract correct answer letter from explanation HTML without modifying it."""
        if not explanation_html:
            return ''
        
        # Parse the explanation HTML
        soup = BeautifulSoup(explanation_html, 'html.parser')
        
        # Look for patterns that indicate correct answer
        text_content = soup.get_text().lower()
        
        # Pattern 1: "The correct answer is A" or "The answer is A"
        answer_pattern = r'(?:correct\s+answer|answer)\s+is\s+([A-Z])'
        match = re.search(answer_pattern, text_content, re.IGNORECASE)
        if match:
            return match.group(1).upper()
        
        # Pattern 2: "(A)" at the beginning of explanation
        choice_pattern = r'^\s*\(([A-Z])\)'
        match = re.search(choice_pattern, text_content, re.IGNORECASE)
        if match:
            return match.group(1).upper()
        
        return ''
    
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
    
    def extract_correct_answer_from_page(self, html_content: str) -> str:
        """Extract correct answer from page data if available"""
        correct_answer, _ = self.extract_embedded_data_from_page(html_content)
        return correct_answer
    
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
        logger.info(f"🚀 Starting OnePrep Scraper v2")
        logger.info(f"   Total exams: {len(exam_list)}")
        
        for i, exam_data in enumerate(exam_list, 1):
            logger.info(f"\n{'='*60}")
            logger.info(f"Processing exam {i}/{len(exam_list)}")
            self.scrape_exam(exam_data)
        
        logger.info(f"\n🎉 Scraping complete!")


# COMMENTED OUT: Original Princeton Review exam list (37-155)
# This was the original exam list that was already scraped
"""
PRINCETON_REVIEW_EXAMS = [
    # Free Practice Test
    {"exam_id": 37, "exam_name": "The Princeton Review - Digital SAT Free Practice Test - English - Module 1", 
     "test_series": "Free Practice Test", "subject": "English", "module_number": 1, "difficulty": None,
     "start_question_id": 2900, "end_question_id": 2926},
    
    {"exam_id": 38, "exam_name": "The Princeton Review - Digital SAT Free Practice Test - English - Module 2 - Easy", 
     "test_series": "Free Practice Test", "subject": "English", "module_number": 2, "difficulty": "Easy",
     "start_question_id": 2927, "end_question_id": 2953},
    
    {"exam_id": 39, "exam_name": "The Princeton Review - Digital SAT Free Practice Test - English - Module 2 - Hard", 
     "test_series": "Free Practice Test", "subject": "English", "module_number": 2, "difficulty": "Hard",
     "start_question_id": 2954, "end_question_id": 2980},
    
    {"exam_id": 40, "exam_name": "The Princeton Review - Digital SAT Free Practice Test - Math - Module 1", 
     "test_series": "Free Practice Test", "subject": "Math", "module_number": 1, "difficulty": None,
     "start_question_id": 2981, "end_question_id": 3002},
    
    {"exam_id": 41, "exam_name": "The Princeton Review - Digital SAT Free Practice Test - Math - Module 2 - Easy", 
     "test_series": "Free Practice Test", "subject": "Math", "module_number": 2, "difficulty": "Easy",
     "start_question_id": 3003, "end_question_id": 3024},
    
    {"exam_id": 42, "exam_name": "The Princeton Review - Digital SAT Free Practice Test - Math - Module 2 - Hard", 
     "test_series": "Free Practice Test", "subject": "Math", "module_number": 2, "difficulty": "Hard",
     "start_question_id": 3025, "end_question_id": 3046},
]
"""

# NEW: Princeton Review Advanced Online Test (exam_ids 416-421)
# Based on the URL pattern provided: https://oneprep.xyz/question/12481/?question_set=exam&exam_id=416
# And ending at: https://oneprep.xyz/question/12606/?question_set=exam&exam_id=421
# Total questions: 12606 - 12481 + 1 = 126 questions
# 
# Standard SAT test structure:
# English Module 1: 27 questions
# English Module 2 Easy: 27 questions  
# English Module 2 Hard: 27 questions
# Math Module 1: 22 questions
# Math Module 2 Easy: 22 questions
# Math Module 2 Hard: 22 questions
# Total: 147 questions
#
# Since we have 126 questions total (12481-12606), let's distribute them as:
# English: 81 questions (27 each), Math: 45 questions (15 each)
# But let's use standard distribution and adjust the last module

ADVANCED_ONLINE_TEST_EXAMS = [
    # English modules (27 questions each)
    {"exam_id": 416, "exam_name": "The Princeton Review - Digital SAT Advanced Online Test - English - Module 1", 
     "test_series": "Advanced Online Test", "subject": "English", "module_number": 1, "difficulty": None,
     "start_question_id": 12481, "end_question_id": 12507},  # 27 questions
    
    {"exam_id": 417, "exam_name": "The Princeton Review - Digital SAT Advanced Online Test - English - Module 2 - Easy", 
     "test_series": "Advanced Online Test", "subject": "English", "module_number": 2, "difficulty": "Easy",
     "start_question_id": 12508, "end_question_id": 12534},  # 27 questions
    
    {"exam_id": 418, "exam_name": "The Princeton Review - Digital SAT Advanced Online Test - English - Module 2 - Hard", 
     "test_series": "Advanced Online Test", "subject": "English", "module_number": 2, "difficulty": "Hard",
     "start_question_id": 12535, "end_question_id": 12561},  # 27 questions
    
    # Math modules (22 questions each, corrected range to 12627)
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
    
    # Run the scraper for the Advanced Online Test exams
    scraper.run(ADVANCED_ONLINE_TEST_EXAMS)
