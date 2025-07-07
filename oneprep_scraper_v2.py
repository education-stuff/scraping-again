#!/usr/bin/env python3
"""
OnePrep Scraper v2 - Preserves HTML content for proper math rendering
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
    
    def extract_metadata(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract question metadata"""
        metadata = {}
        
        # Find stat divs
        stat_divs = soup.find_all('div', class_='stat')
        for stat in stat_divs:
            title_elem = stat.find('div', class_='stat-title')
            value_elem = stat.find('div', class_='stat-value')
            
            if title_elem and value_elem:
                title = title_elem.get_text(strip=True).lower()
                value = value_elem.get_text(strip=True)
                
                if title in ['section', 'domain', 'skill']:
                    metadata[title] = value
        
        return metadata
    
    def submit_answer_and_get_explanation(self, question_id: int, exam_id: int, answer_id: int) -> Tuple[str, str]:
        """Submit an answer using the original working method to get explanation and correct answer"""
        # Use the old endpoint that actually works
        submit_url = f"{self.base_url}/question/{question_id}/submit/"
        
        # Use form data like the original scraper
        data = {
            'csrfmiddlewaretoken': self.csrf_token,
            'answer_choice_id': str(answer_id),
            'exam_id': str(exam_id),
            'question_set': 'exam'
        }
        
        headers = {
            'X-CSRFToken': self.csrf_token,
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': f"{self.base_url}/question/{question_id}/?question_set=exam&exam_id={exam_id}"
        }
        
        try:
            response = self.session.post(submit_url, data=data, headers=headers, timeout=10)
            
            if response.status_code == 200:
                # Check if response is JSON
                try:
                    json_data = response.json()
                    
                    # Extract explanation from JSON response
                    explanation_html = json_data.get('explanation', '')
                    if not explanation_html and 'html' in json_data:
                        # Sometimes the explanation is embedded in HTML field
                        soup = BeautifulSoup(json_data['html'], 'html.parser')
                        exp_elem = soup.find('div', id='question-explanation')
                        if exp_elem:
                            explanation_html = self.extract_inner_html(exp_elem)
                    
                    # Look for correct answer in the response
                    correct_answer = ''
                    if 'answer_choices' in json_data:
                        for choice in json_data['answer_choices']:
                            if choice.get('is_correct', False):
                                correct_answer = choice.get('letter', '')
                                break
                    
                    return explanation_html, correct_answer
                    
                except json.JSONDecodeError:
                    # Response is HTML, parse it
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Find explanation in HTML
                    exp_elem = soup.find('div', id='question-explanation')
                    explanation_html = self.extract_inner_html(exp_elem) if exp_elem else ''
                    
                    # Find correct answer from success styling
                    correct_answer = ''
                    success_divs = soup.find_all('div', class_=re.compile(r'border-success'))
                    for div in success_divs:
                        # Look for the answer letter
                        letter_div = div.find('div', class_='font-bold')
                        if letter_div:
                            letter = letter_div.get_text(strip=True)
                            if letter in ['A', 'B', 'C', 'D']:
                                correct_answer = letter
                                break
                    
                    # Try to extract correct answer from page data as fallback
                    if not correct_answer:
                        correct_answer = self.extract_correct_answer_from_page(response.text)
                    
                    return explanation_html, correct_answer
                    
        except Exception as e:
            logger.error(f"Failed to submit answer for question {question_id}: {e}")
        
        return '', ''

    def extract_correct_answer_from_explanation(self, explanation_html: str) -> Optional[str]:
        """Extract correct answer letter from explanation HTML without modifying it."""
        if not explanation_html:
            return None
        soup = BeautifulSoup(explanation_html, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        patterns = [
            r'correct answer is ([A-D])',
            r'The correct answer is ([A-D])\.',
            r'Choice ([A-D]) is correct',
            r'The answer is ([A-D])\.',
            r'\b([A-D])\b is the correct choice',
            r'correct choice is option ([A-D])'
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).upper()
        return None

    def extract_embedded_data_from_page(self, html_content: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract correct answer and explanation from embedded JavaScript data"""
        # Look for answer_choices data pattern
        answer_choices_pattern = r'answer_choices:\s*(\[.*?\])'
        match = re.search(answer_choices_pattern, html_content, re.DOTALL)
        
        correct_answer = None
        
        if match:
            try:
                answer_choices_str = match.group(1)
                answer_choices_data = json.loads(answer_choices_str)
                
                # Find the correct answer
                for choice in answer_choices_data:
                    if choice.get('is_correct', False):
                        correct_answer = choice.get('letter', '')
                        break
                        
            except json.JSONDecodeError:
                logger.warning("Failed to parse answer_choices JSON from page")
        
        # Look for explanation in the modal
        explanation_html = ''
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find the explanation modal
        explanation_modal = soup.find('dialog', id='explanation')
        if explanation_modal:
            # Look for the explanation content within the modal
            explanation_content = explanation_modal.find('div', class_=lambda x: x and 'explanation' in x.lower() if x else False)
            if not explanation_content:
                # Try to find any div with explanation text
                explanation_content = explanation_modal.find('div', string=lambda x: x and 'explanation' in x.lower() if x else False)
            if not explanation_content:
                # Get all content from the modal, excluding buttons and form elements
                for unwanted in explanation_modal.find_all(['button', 'form', 'input']):
                    unwanted.decompose()
                explanation_content = explanation_modal.find('div')
            
            if explanation_content:
                explanation_html = self.extract_inner_html(explanation_content)
        
        return correct_answer, explanation_html
    
    def extract_correct_answer_from_page(self, html_content: str) -> Optional[str]:
        """Extract correct answer from page data if available"""
        correct_answer, _ = self.extract_embedded_data_from_page(html_content)
        return correct_answer
    
    def scrape_question(self, question_id: int, exam_data: Dict) -> Optional[Dict]:
        """Scrape a single question"""
        url = f"{self.base_url}/question/{question_id}/?question_set=exam&exam_id={exam_data['exam_id']}"
        
        try:
            # Fetch the question page
            response = self.session.get(url, timeout=20)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Initialize question data
            question_data = {
                'question_id': question_id,
                'stimulus': '',
                'question_stem': '',
                'answer_choices': {},
                'answer_ids': {},
                'metadata': {},
                'explanation': '',
                'correct_answer': ''
            }
            
            # Extract metadata
            metadata = self.extract_metadata(soup)
            question_data['metadata'] = metadata
            
            # Extract stimulus only for English questions
            if metadata.get('section') == 'English':
                stimulus_elem = soup.find('div', id='question-stimulus')
                if stimulus_elem:
                    question_data['stimulus'] = self.extract_inner_html(stimulus_elem)
            
            # Extract question stem (preserve HTML)
            stem_elem = soup.find('div', id='question-stem')
            if stem_elem:
                question_data['question_stem'] = self.extract_inner_html(stem_elem)
            
            # Extract answer choices
            question_data['answer_choices'], question_data['answer_ids'] = self.extract_answer_choices(soup)
            
            # Extract correct answer and explanation from embedded page data
            correct_answer, explanation = self.extract_embedded_data_from_page(response.text)
            
            if correct_answer:
                question_data['correct_answer'] = correct_answer
            
            if explanation:
                question_data['explanation'] = explanation
            
            # If explanation is still missing, try to get it from the old method (fallback)
            if not question_data['explanation'] and question_data['answer_ids']:
                # Pick an answer to submit. Use correct one if known, else first one.
                answer_letter = question_data.get('correct_answer') or list(question_data['answer_ids'].keys())[0]
                answer_id = question_data['answer_ids'][answer_letter]
                
                fallback_explanation, fallback_answer = self.submit_answer_and_get_explanation(
                    question_id, exam_data['exam_id'], answer_id
                )
                if fallback_explanation:
                    question_data['explanation'] = fallback_explanation
                    # Update correct answer if we got it from the explanation and didn't have it before
                    if fallback_answer and not question_data['correct_answer']:
                        question_data['correct_answer'] = fallback_answer

            # Final fallback: try to extract correct answer from explanation text
            if question_data['explanation'] and not question_data['correct_answer']:
                answer = self.extract_correct_answer_from_explanation(question_data['explanation'])
                if answer:
                    question_data['correct_answer'] = answer
            
            # Add exam metadata
            question_data.update({
                'exam_id': exam_data['exam_id'],
                'exam_name': exam_data['exam_name'],
                'test_series': exam_data['test_series'],
                'subject': exam_data['subject'],
                'module_number': exam_data['module_number'],
                'difficulty': exam_data.get('difficulty'),
                'url': url,
                'scraped_at': datetime.now().isoformat()
            })
            
            logger.info(f"✅ Scraped question {question_id}: "
                       f"stem={'✓' if question_data['question_stem'] else '✗'}, "
                       f"choices={len(question_data['answer_choices'])}, "
                       f"explanation={'✓' if question_data['explanation'] else '✗'}, "
                       f"answer={question_data['correct_answer'] or '✗'}")
            
            return question_data
            
        except Exception as e:
            logger.error(f"❌ Failed to scrape question {question_id}: {e}")
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


# Princeton Review exam list
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

if __name__ == "__main__":
    scraper = OnePrepScraperV2()
    
    # Run the scraper for all exams in the list
    scraper.run(PRINCETON_REVIEW_EXAMS)
