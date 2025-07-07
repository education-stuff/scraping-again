#!/usr/bin/env python3
"""
OnePrep SAT Question Bank Scraper
Cleanly extracts all question data including explanations from oneprep.xyz
"""

import json
import time
import requests
from bs4 import BeautifulSoup
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class OnePrepScraper:
    """Clean implementation of OnePrep scraper with focus on extracting all data"""
    
    def __init__(self):
        self.base_url = 'https://oneprep.xyz'
        self.session = self._setup_session()
        self.output_dir = Path(__file__).parent / 'scraped_data'
        self.output_dir.mkdir(exist_ok=True)
        
    def _setup_session(self) -> requests.Session:
        """Setup session with proper headers and cookies"""
        session = requests.Session()
        
        # Headers from the working scraper
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Connection": "keep-alive",
            "Cookie": "csrftoken=bv47FTGEONa0XFN7mNmVpAsfiix0GD9X; initial_url=\"http://127.0.0.1:5500/\"; _ga_9XC7HL2GZF=GS2.1.s1751081527$o41$g0$t1751081527$j60$l0$h1145318045; _ga=GA1.1.612205866.1750286024; _ga_WD0CE4KQWK=GS2.1.s1751081528$o41$g0$t1751081528$j60$l0$h1704481143; sessionid=uoxyo4sfl6rdh8ampevvl9gtidy957ra; messages=W1siX19qc29uX21lc3NhZ2UiLDAsMjUsIlN1Y2Nlc3NmdWxseSBzaWduZWQgaW4gYXMgZzRnNmo3bnR0eXkuIiwiIl1d:1uSW2B:mZtkkSbkf0zqUOJJoN_klzqBMIb6FBIlnmZqCuRDXts",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "cross-site",
        })
        
        return session
    
    def extract_html_content(self, element):
        """Extract inner HTML content from an element, preserving all formatting"""
        if not element:
            return ''
        
        # Return the inner HTML as a string
        return ''.join(str(child) for child in element.children)
    
    def extract_question_data(self, html: str, question_id: int, exam_id: int) -> Dict:
        """Extract all question data from the HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        
        data = {
            'question_id': question_id,
            'stimulus': '',
            'question_stem': '',
            'answer_choices': {},
            'answer_ids': {},
            'metadata': {}
        }
        
        # Extract stimulus (passage/context)
        stimulus_elem = soup.find('div', id='question-stimulus')
        if stimulus_elem:
            data['stimulus'] = self.extract_html_content(stimulus_elem)
            
        # Extract question stem
        stem_elem = soup.find('div', id='question-stem')
        if stem_elem:
            data['question_stem'] = self.extract_html_content(stem_elem)
            
        # Extract answer choices - they have x-data attributes
        choices_container = soup.find('div', id='answer-choices')
        if choices_container:
            data['answer_choices'], data['answer_ids'] = self.extract_answer_choices_from_html(soup)
        
        # Extract metadata (section, domain, skill)
        stats_divs = soup.find_all('div', class_='stat')
        for stat in stats_divs:
            title_elem = stat.find('div', class_='stat-title')
            value_elem = stat.find('div', class_='stat-value')
            if title_elem and value_elem:
                title = title_elem.get_text(strip=True).lower()
                value = value_elem.get_text(strip=True)
                if 'section' in title:
                    data['metadata']['section'] = value
                elif 'domain' in title:
                    data['metadata']['domain'] = value
                elif 'skill' in title:
                    data['metadata']['skill'] = value
        
        return data
    
    def extract_explanation_from_html(self, soup: BeautifulSoup) -> str:
        """Extract explanation from various possible locations in HTML"""
        # Method 1: Look in dialog modal
        explanation_modal = soup.find('dialog', {'id': 'explanation'})
        if explanation_modal:
            text = explanation_modal.get_text(strip=True)
            if text and len(text) > 10:
                return text
        
        # Method 2: Look for divs with explanation-related IDs
        for elem_id in ['question-explanation', 'explanation-content', 'explanation']:
            elem = soup.find(id=elem_id)
            if elem:
                text = elem.get_text(strip=True)
                if text and len(text) > 10:
                    return text
        
        # Method 3: Look for explanation in scripts (sometimes in JSON)
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                content = script.string
                # Look for explanation in JSON data
                patterns = [
                    r'"explanation":\s*"([^"]+(?:\\.[^"]*)*)"',
                    r'explanation:\s*["\']([^"\']+)["\']'
                ]
                for pattern in patterns:
                    match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
                    if match:
                        explanation = match.group(1)
                        # Clean up escaped characters
                        explanation = explanation.replace('\\n', ' ').replace('\\"', '"')
                        explanation = re.sub(r'\\(.)', r'\1', explanation)
                        explanation = re.sub(r'\s+', ' ', explanation).strip()
                        if len(explanation) > 10:
                            return explanation
        
        return ''
    
    def submit_answer_and_get_explanation(self, question_id: int, exam_id: int, answer_id: int) -> Tuple[str, str]:
        """Submit an answer to get the explanation and correct answer"""
        # This simulates clicking the submit button with an answer
        url = f"{self.base_url}/question/{question_id}/submit/"
        
        data = {
            'answer_id': answer_id,
            'exam_id': exam_id,
            'csrfmiddlewaretoken': 'bv47FTGEONa0XFN7mNmVpAsfiix0GD9X'  # From cookie
        }
        
        try:
            response = self.session.post(url, data=data, timeout=10)
            
            # The response might contain the explanation or redirect to a page with it
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract explanation from response
            explanation = self.extract_explanation_from_html(soup)
            
            # Look for correct answer indicator
            correct_answer = ''
            # Check for success border on answer choices
            for letter in ['A', 'B', 'C', 'D']:
                # Look for answer choice with success indicator
                choice = soup.find('div', {'x-data': re.compile(f"letter:\s*'{letter}'")})
                if choice:
                    # Check if this choice has success styling
                    content_div = choice.find('div', class_=re.compile(r'border-success|correct|bg-success'))
                    if content_div:
                        correct_answer = letter
                        break
            
            # Alternative: look in explanation text
            if not correct_answer and explanation:
                answer_match = re.search(r'(?:correct answer is|Answer:)\s*\(?([A-Z])\)?', explanation, re.IGNORECASE)
                if answer_match:
                    correct_answer = answer_match.group(1)
            
            return explanation, correct_answer
            
        except Exception as e:
            logger.debug(f"Failed to submit answer for question {question_id}: {e}")
            return '', ''
    
    def fetch_explanation(self, question_id: int, exam_id: int, answer_ids: Dict[str, int], initial_html: str) -> Tuple[str, str]:
        """Fetch explanation using multiple methods"""
        # First check if explanation is already in the HTML
        soup = BeautifulSoup(initial_html, 'html.parser')
        explanation = self.extract_explanation_from_html(soup)
        
        if explanation:
            # Try to find correct answer
            correct_answer = ''
            answer_match = re.search(r'(?:correct answer is|Answer:)\s*\(?([A-Z])\)?', explanation, re.IGNORECASE)
            if answer_match:
                correct_answer = answer_match.group(1)
            return explanation, correct_answer
        
        # Try direct explanation endpoint
        url = f"{self.base_url}/question/{question_id}/explanation/?exam_id={exam_id}"
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                explanation = self.extract_explanation_from_html(soup)
                if explanation:
                    correct_answer = ''
                    answer_match = re.search(r'(?:correct answer is|Answer:)\s*\(?([A-Z])\)?', explanation, re.IGNORECASE)
                    if answer_match:
                        correct_answer = answer_match.group(1)
                    return explanation, correct_answer
        except:
            pass
        
        # If no explanation yet, try submitting an answer (choose A)
        if answer_ids and 'A' in answer_ids:
            explanation, correct_answer = self.submit_answer_and_get_explanation(
                question_id, exam_id, answer_ids['A']
            )
            if explanation:
                return explanation, correct_answer
        
        return '', ''
    
    def scrape_question(self, question_id: int, exam_data: Dict) -> Optional[Dict]:
        """Scrape a single question with all its data"""
        url = f"{self.base_url}/question/{question_id}/?question_set=exam&exam_id={exam_data['exam_id']}"
        
        try:
            # Fetch main question page
            response = self.session.get(url, timeout=20)
            response.raise_for_status()
            
            # Extract basic question data
            question_data = self.extract_question_data(response.text, question_id, exam_data['exam_id'])
            
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
            
            # Fetch explanation and correct answer
            explanation, correct_answer = self.fetch_explanation(
                question_id, 
                exam_data['exam_id'],
                question_data['answer_ids'],
                response.text
            )
            question_data['explanation'] = explanation
            question_data['correct_answer'] = correct_answer
            
            # If we didn't get correct answer from explanation, try to infer from HTML
            if not correct_answer and response.text:
                # Look for success border class which indicates correct answer
                soup = BeautifulSoup(response.text, 'html.parser')
                for letter in ['A', 'B', 'C', 'D']:
                    # This is a bit tricky as the correct answer might only show after submission
                    # We'll rely on the explanation endpoint for this
                    pass
            
            logger.info(f"✅ Scraped question {question_id}: "
                       f"stem={'✓' if question_data['question_stem'] else '✗'}, "
                       f"choices={'✓' if question_data['answer_choices'] else '✗'}, "
                       f"explanation={'✓' if question_data['explanation'] else '✗'}, "
                       f"answer={'✓' if question_data['correct_answer'] else '✗'}")
            
            return question_data
            
        except Exception as e:
            logger.error(f"Failed to scrape question {question_id}: {e}")
            return None
    
    def save_exam_data(self, exam_data: Dict, questions: List[Dict]):
        """Save scraped questions to organized JSON files"""
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
    
    def scrape_exam(self, exam_data: Dict) -> List[Dict]:
        """Scrape all questions for a single exam"""
        logger.info(f"\n{'='*60}")
        logger.info(f"📚 Scraping: {exam_data['exam_name']}")
        logger.info(f"Question range: {exam_data['start_question_id']} - {exam_data['end_question_id']}")
        
        questions = []
        
        for question_id in range(exam_data['start_question_id'], exam_data['end_question_id'] + 1):
            question_data = self.scrape_question(question_id, exam_data)
            
            if question_data:
                questions.append(question_data)
            
            # Small delay to be respectful
            time.sleep(0.5)
        
        logger.info(f"✅ Completed: {len(questions)}/{exam_data['end_question_id'] - exam_data['start_question_id'] + 1} questions scraped")
        
        return questions


# Princeton Review exam definitions - Complete list
PRINCETON_REVIEW_EXAMS = [
    # Free Practice Test
    {'exam_id': 37, 'exam_name': 'The Princeton Review - Digital SAT Free Practice Test - English - Module 1', 'test_series': 'Free Practice Test', 'subject': 'English', 'module_number': 1, 'difficulty': None, 'start_question_id': 2900, 'end_question_id': 2926},
    {'exam_id': 38, 'exam_name': 'The Princeton Review - Digital SAT Free Practice Test - English - Module 2 - Easy', 'test_series': 'Free Practice Test', 'subject': 'English', 'module_number': 2, 'difficulty': 'Easy', 'start_question_id': 2927, 'end_question_id': 2953},
    {'exam_id': 39, 'exam_name': 'The Princeton Review - Digital SAT Free Practice Test - English - Module 2 - Hard', 'test_series': 'Free Practice Test', 'subject': 'English', 'module_number': 2, 'difficulty': 'Hard', 'start_question_id': 2954, 'end_question_id': 2980},
    {'exam_id': 40, 'exam_name': 'The Princeton Review - Digital SAT Free Practice Test - Math - Module 1', 'test_series': 'Free Practice Test', 'subject': 'Math', 'module_number': 1, 'difficulty': None, 'start_question_id': 2981, 'end_question_id': 3002},
    {'exam_id': 41, 'exam_name': 'The Princeton Review - Digital SAT Free Practice Test - Math - Module 2 - Easy', 'test_series': 'Free Practice Test', 'subject': 'Math', 'module_number': 2, 'difficulty': 'Easy', 'start_question_id': 3003, 'end_question_id': 3024},
    {'exam_id': 42, 'exam_name': 'The Princeton Review - Digital SAT Free Practice Test - Math - Module 2 - Hard', 'test_series': 'Free Practice Test', 'subject': 'Math', 'module_number': 2, 'difficulty': 'Hard', 'start_question_id': 3025, 'end_question_id': 3046},
    
    # Prep Test 1
    {'exam_id': 43, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 1 - English - Module 1', 'test_series': 'Prep Test 1', 'subject': 'English', 'module_number': 1, 'difficulty': None, 'start_question_id': 3047, 'end_question_id': 3073},
    {'exam_id': 44, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 1 - English - Module 2 - Easy', 'test_series': 'Prep Test 1', 'subject': 'English', 'module_number': 2, 'difficulty': 'Easy', 'start_question_id': 3074, 'end_question_id': 3100},
    {'exam_id': 45, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 1 - English - Module 2 - Hard', 'test_series': 'Prep Test 1', 'subject': 'English', 'module_number': 2, 'difficulty': 'Hard', 'start_question_id': 3101, 'end_question_id': 3127},
    {'exam_id': 46, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 1 - Math - Module 1', 'test_series': 'Prep Test 1', 'subject': 'Math', 'module_number': 1, 'difficulty': None, 'start_question_id': 3128, 'end_question_id': 3149},
    {'exam_id': 47, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 1 - Math - Module 2 - Easy', 'test_series': 'Prep Test 1', 'subject': 'Math', 'module_number': 2, 'difficulty': 'Easy', 'start_question_id': 3150, 'end_question_id': 3171},
    {'exam_id': 48, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 1 - Math - Module 2 - Hard', 'test_series': 'Prep Test 1', 'subject': 'Math', 'module_number': 2, 'difficulty': 'Hard', 'start_question_id': 3172, 'end_question_id': 3193},
    
    # Prep Test 2
    {'exam_id': 49, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 2 - English - Module 1', 'test_series': 'Prep Test 2', 'subject': 'English', 'module_number': 1, 'difficulty': None, 'start_question_id': 3194, 'end_question_id': 3220},
    {'exam_id': 50, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 2 - English - Module 2 - Easy', 'test_series': 'Prep Test 2', 'subject': 'English', 'module_number': 2, 'difficulty': 'Easy', 'start_question_id': 3221, 'end_question_id': 3247},
    {'exam_id': 51, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 2 - English - Module 2 - Hard', 'test_series': 'Prep Test 2', 'subject': 'English', 'module_number': 2, 'difficulty': 'Hard', 'start_question_id': 3248, 'end_question_id': 3274},
    {'exam_id': 52, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 2 - Math - Module 1', 'test_series': 'Prep Test 2', 'subject': 'Math', 'module_number': 1, 'difficulty': None, 'start_question_id': 3275, 'end_question_id': 3296},
    {'exam_id': 53, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 2 - Math - Module 2 - Easy', 'test_series': 'Prep Test 2', 'subject': 'Math', 'module_number': 2, 'difficulty': 'Easy', 'start_question_id': 3297, 'end_question_id': 3318},
    {'exam_id': 54, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 2 - Math - Module 2 - Hard', 'test_series': 'Prep Test 2', 'subject': 'Math', 'module_number': 2, 'difficulty': 'Hard', 'start_question_id': 3319, 'end_question_id': 3340},
    
    # Prep Test 3
    {'exam_id': 55, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 3 - English - Module 1', 'test_series': 'Prep Test 3', 'subject': 'English', 'module_number': 1, 'difficulty': None, 'start_question_id': 3341, 'end_question_id': 3367},
    {'exam_id': 56, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 3 - English - Module 2 - Easy', 'test_series': 'Prep Test 3', 'subject': 'English', 'module_number': 2, 'difficulty': 'Easy', 'start_question_id': 3368, 'end_question_id': 3394},
    {'exam_id': 57, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 3 - English - Module 2 - Hard', 'test_series': 'Prep Test 3', 'subject': 'English', 'module_number': 2, 'difficulty': 'Hard', 'start_question_id': 3395, 'end_question_id': 3421},
    {'exam_id': 58, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 3 - Math - Module 1', 'test_series': 'Prep Test 3', 'subject': 'Math', 'module_number': 1, 'difficulty': None, 'start_question_id': 3422, 'end_question_id': 3443},
    {'exam_id': 59, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 3 - Math - Module 2 - Easy', 'test_series': 'Prep Test 3', 'subject': 'Math', 'module_number': 2, 'difficulty': 'Easy', 'start_question_id': 3444, 'end_question_id': 3465},
    {'exam_id': 60, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 3 - Math - Module 2 - Hard', 'test_series': 'Prep Test 3', 'subject': 'Math', 'module_number': 2, 'difficulty': 'Hard', 'start_question_id': 3466, 'end_question_id': 3487},
    
    # Prep Test 4
    {'exam_id': 61, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 4 - English - Module 1', 'test_series': 'Prep Test 4', 'subject': 'English', 'module_number': 1, 'difficulty': None, 'start_question_id': 3488, 'end_question_id': 3514},
    {'exam_id': 62, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 4 - English - Module 2 - Easy', 'test_series': 'Prep Test 4', 'subject': 'English', 'module_number': 2, 'difficulty': 'Easy', 'start_question_id': 3515, 'end_question_id': 3541},
    {'exam_id': 63, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 4 - English - Module 2 - Hard', 'test_series': 'Prep Test 4', 'subject': 'English', 'module_number': 2, 'difficulty': 'Hard', 'start_question_id': 3542, 'end_question_id': 3568},
    {'exam_id': 64, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 4 - Math - Module 1', 'test_series': 'Prep Test 4', 'subject': 'Math', 'module_number': 1, 'difficulty': None, 'start_question_id': 3569, 'end_question_id': 3590},
    {'exam_id': 65, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 4 - Math - Module 2 - Easy', 'test_series': 'Prep Test 4', 'subject': 'Math', 'module_number': 2, 'difficulty': 'Easy', 'start_question_id': 3591, 'end_question_id': 3612},
    {'exam_id': 66, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 4 - Math - Module 2 - Hard', 'test_series': 'Prep Test 4', 'subject': 'Math', 'module_number': 2, 'difficulty': 'Hard', 'start_question_id': 3613, 'end_question_id': 3634},
    
    # Prep Test 5  
    {'exam_id': 67, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 5 - English - Module 1', 'test_series': 'Prep Test 5', 'subject': 'English', 'module_number': 1, 'difficulty': None, 'start_question_id': 3635, 'end_question_id': 3661},
    {'exam_id': 68, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 5 - English - Module 2 - Easy', 'test_series': 'Prep Test 5', 'subject': 'English', 'module_number': 2, 'difficulty': 'Easy', 'start_question_id': 3662, 'end_question_id': 3688},
    {'exam_id': 69, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 5 - English - Module 2 - Hard', 'test_series': 'Prep Test 5', 'subject': 'English', 'module_number': 2, 'difficulty': 'Hard', 'start_question_id': 3689, 'end_question_id': 3715},
    {'exam_id': 70, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 5 - Math - Module 1', 'test_series': 'Prep Test 5', 'subject': 'Math', 'module_number': 1, 'difficulty': None, 'start_question_id': 3716, 'end_question_id': 3737},
    {'exam_id': 71, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 5 - Math - Module 2 - Easy', 'test_series': 'Prep Test 5', 'subject': 'Math', 'module_number': 2, 'difficulty': 'Easy', 'start_question_id': 3738, 'end_question_id': 3759},
    {'exam_id': 72, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 5 - Math - Module 2 - Hard', 'test_series': 'Prep Test 5', 'subject': 'Math', 'module_number': 2, 'difficulty': 'Hard', 'start_question_id': 3760, 'end_question_id': 3781},
]


def main():
    """Main function to run the scraper"""
    logger.info("🚀 Starting OnePrep Scraper")
    start_time = time.time()
    
    scraper = OnePrepScraper()
    
    total_questions = 0
    total_exams = 0
    
    # Process each exam
    for exam_data in PRINCETON_REVIEW_EXAMS:
        try:
            questions = scraper.scrape_exam(exam_data)
            
            if questions:
                scraper.save_exam_data(exam_data, questions)
                total_questions += len(questions)
                total_exams += 1
                
        except Exception as e:
            logger.error(f"Failed to process exam {exam_data['exam_name']}: {e}")
    
    # Summary
    duration = time.time() - start_time
    logger.info(f"\n{'='*60}")
    logger.info(f"🎉 Scraping Complete!")
    logger.info(f"📊 Total exams processed: {total_exams}/{len(PRINCETON_REVIEW_EXAMS)}")
    logger.info(f"📝 Total questions scraped: {total_questions}")
    logger.info(f"⏱️  Duration: {duration:.2f} seconds")


if __name__ == '__main__':
    main()
