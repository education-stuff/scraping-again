#!/usr/bin/env python3
"""
Post-process scraped data to extract correct answers from explanations
"""

import json
import re
from pathlib import Path
import logging
import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CorrectAnswerProcessor:
    def __init__(self):
        self.base_url = "https://oneprep.xyz"
        self.session = self.setup_session()
    
    def setup_session(self):
        """Setup session with authentication"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Cookie': 'csrftoken=bv47FTGEONa0XFN7mNmVpAsfiix0GD9X; initial_url="http://127.0.0.1:5500/"; _ga_9XC7HL2GZF=GS2.1.s1751081527$o41$g0$t1751081527$j60$l0$h1145318045; _ga=GA1.1.612205866.1750286024; _ga_WD0CE4KQWK=GS2.1.s1751081528$o41$g0$t1751081528$j60$l0$h1704481143; sessionid=uoxyo4sfl6rdh8ampevvl9gtidy957ra; messages=W1siX19qc29uX21lc3NhZ2UiLDAsMjUsIlN1Y2Nlc3NmdWxseSBzaWduZWQgaW4gYXMgZzRnNmo3bnR0eXkuIiwiIl1d:1uSW2B:mZtkkSbkf0zqUOJJoN_klzqBMIb6FBIlnmZqCuRDXts',
        })
        return session
    
    def fetch_explanation_directly(self, question_id, exam_id):
        """Fetch explanation from the dedicated endpoint preserving HTML"""
        exp_url = f"{self.base_url}/question/{question_id}/explanation/?exam_id={exam_id}"
        
        try:
            response = self.session.get(exp_url, timeout=10)
            if response.status_code == 200:
                # Try to parse as JSON first
                try:
                    json_data = response.json()
                    # The explanation might be directly in the response
                    if 'explanation' in json_data:
                        return json_data['explanation']
                    # Or it might be wrapped in HTML
                    if 'html' in json_data:
                        soup = BeautifulSoup(json_data['html'], 'html.parser')
                        # Look for explanation div
                        exp_elem = soup.find('div', class_=re.compile(r'explanation|content'))
                        if exp_elem:
                            # Extract inner HTML to preserve formatting
                            return ''.join(str(child) for child in exp_elem.children).strip()
                        # Sometimes the entire HTML is the explanation
                        return json_data['html']
                except json.JSONDecodeError:
                    # Response is HTML
                    soup = BeautifulSoup(response.text, 'html.parser')
                    # Try to find explanation content
                    exp_elem = soup.find('div', class_=re.compile(r'explanation|content'))
                    if exp_elem:
                        # Extract inner HTML
                        return ''.join(str(child) for child in exp_elem.children).strip()
                    # Sometimes the whole response is the explanation
                    return response.text.strip()
        except Exception as e:
            logger.error(f"Failed to fetch explanation for Q{question_id}: {e}")
        
        return ''
    
    def extract_correct_answer_from_explanation(self, explanation_html):
        """Extract correct answer from explanation HTML"""
        if not explanation_html:
            return ''
        
        # Convert to plain text for analysis
        soup = BeautifulSoup(explanation_html, 'html.parser')
        text = soup.get_text()
        
        # Try various patterns
        patterns = [
            r'\(([A-D])\)\s+is\s+(?:correct|the\s+correct\s+answer)',
            r'(?:correct answer is|Answer:)\s*\(?([A-D])\)?',
            r'Choice\s+([A-D])\s+is\s+(?:correct|the\s+correct)',
            r'The\s+answer\s+is\s+\(([A-D])\)',
            r'\(([A-D])\)\s+is\s+the\s+answer',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).upper()
        
        return ''
    
    def process_json_file(self, filepath):
        """Process a single JSON file to add correct answers"""
        logger.info(f"Processing: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            questions = json.load(f)
        
        updated_count = 0
        
        for q in questions:
            if not q.get('correct_answer'):
                # First try to get from existing explanation
                if q.get('explanation'):
                    answer = self.extract_correct_answer_from_explanation(q['explanation'])
                    if answer:
                        q['correct_answer'] = answer
                        updated_count += 1
                        logger.info(f"  Q{q['question_id']}: Found answer {answer} in existing explanation")
                        continue
                
                # If no explanation or couldn't find answer, fetch it
                explanation = self.fetch_explanation_directly(q['question_id'], q['exam_id'])
                if explanation:
                    q['explanation'] = explanation
                    answer = self.extract_correct_answer_from_explanation(explanation)
                    if answer:
                        q['correct_answer'] = answer
                        updated_count += 1
                        logger.info(f"  Q{q['question_id']}: Fetched explanation and found answer {answer}")
                    else:
                        logger.warning(f"  Q{q['question_id']}: Got explanation but couldn't extract answer")
                else:
                    logger.warning(f"  Q{q['question_id']}: Failed to fetch explanation")
        
        # Save updated file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(questions, f, indent=2, ensure_ascii=False)
        
        logger.info(f"  Updated {updated_count} questions in {filepath.name}")
    
    def process_all_files(self, scraped_dir='scraped_data'):
        """Process all JSON files in the scraped data directory"""
        scraped_path = Path(scraped_dir)
        json_files = list(scraped_path.rglob('*.json'))
        
        logger.info(f"Found {len(json_files)} JSON files to process")
        
        for filepath in json_files:
            self.process_json_file(filepath)
        
        logger.info("Processing complete!")


if __name__ == "__main__":
    processor = CorrectAnswerProcessor()
    processor.process_all_files()
