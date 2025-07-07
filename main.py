#!/usr/bin/env python3
"""
Comprehensive Fixed Princeton Review Scraper - FINAL VERSION
This scraper properly extracts ALL data: explanations, passages, questions, answers, metadata, etc.
"""

import json
import time
import requests
from bs4 import BeautifulSoup
import re
from pathlib import Path
from datetime import datetime

# Get the directory where the script is located.
SCRIPT_DIR = Path(__file__).parent.resolve()

class ComprehensiveFixedScraper:
    def __init__(self, cookies_file='oneprepxyz-cookies.json'):
        self.base_url = 'https://oneprep.xyz'
        self.session = requests.Session()
        
        # Use the successful headers and cookie from the debug script
        self.session.headers.update({
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

        self.output_dir = SCRIPT_DIR / 'scraped_data'
        
        # Complete exam data
        self.exams = [
            # Free Practice Test
            {'exam_id': 37, 'exam_name': 'The Princeton Review - Digital SAT Free Practice Test - English - Module 1', 'test_series': 'Free Practice Test', 'subject': 'English', 'module_number': 1, 'difficulty': None, 'start_question_id': 2900, 'end_question_id': 2926},
            {'exam_id': 38, 'exam_name': 'The Princeton Review - Digital SAT Free Practice Test - English - Module 2 - Easy', 'test_series': 'Free Practice Test', 'subject': 'English', 'module_number': 2, 'difficulty': 'Easy', 'start_question_id': 2927, 'end_question_id': 2953},
            {'exam_id': 39, 'exam_name': 'The Princeton Review - Digital SAT Free Practice Test - English - Module 2 - Hard', 'test_series': 'Free Practice Test', 'subject': 'English', 'module_number': 2, 'difficulty': 'Hard', 'start_question_id': 2954, 'end_question_id': 2980},
            {'exam_id': 40, 'exam_name': 'The Princeton Review - Digital SAT Free Practice Test - Math - Module 1', 'test_series': 'Free Practice Test', 'subject': 'Math', 'module_number': 1, 'difficulty': None, 'start_question_id': 2981, 'end_question_id': 3002},
            {'exam_id': 41, 'exam_name': 'The Princeton Review - Digital SAT Free Practice Test - Math - Module 2 - Easy', 'test_series': 'Free Practice Test', 'subject': 'Math', 'module_number': 2, 'difficulty': 'Easy', 'start_question_id': 3003, 'end_question_id': 3024},
            {'exam_id': 42, 'exam_name': 'The Princeton Review - Digital SAT Free Practice Test - Math - Module 2 - Hard', 'test_series': 'Free Practice Test', 'subject': 'Math', 'module_number': 2, 'difficulty': 'Hard', 'start_question_id': 3025, 'end_question_id': 3046},
            
            # Prep Test 1
            {'exam_id': 1, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 1 - English - Module 1', 'test_series': 'Prep Test 1', 'subject': 'English', 'module_number': 1, 'difficulty': None, 'start_question_id': 1, 'end_question_id': 27},
            {'exam_id': 2, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 1 - English - Module 2 - Easy', 'test_series': 'Prep Test 1', 'subject': 'English', 'module_number': 2, 'difficulty': 'Easy', 'start_question_id': 28, 'end_question_id': 54},
            {'exam_id': 3, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 1 - English - Module 2 - Hard', 'test_series': 'Prep Test 1', 'subject': 'English', 'module_number': 2, 'difficulty': 'Hard', 'start_question_id': 55, 'end_question_id': 81},
            {'exam_id': 4, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 1 - Math - Module 1', 'test_series': 'Prep Test 1', 'subject': 'Math', 'module_number': 1, 'difficulty': None, 'start_question_id': 82, 'end_question_id': 103},
            {'exam_id': 5, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 1 - Math - Module 2 - Easy', 'test_series': 'Prep Test 1', 'subject': 'Math', 'module_number': 2, 'difficulty': 'Easy', 'start_question_id': 104, 'end_question_id': 125},
            {'exam_id': 6, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 1 - Math - Module 2 - Hard', 'test_series': 'Prep Test 1', 'subject': 'Math', 'module_number': 2, 'difficulty': 'Hard', 'start_question_id': 126, 'end_question_id': 147},
            
            # Prep Test 2
            {'exam_id': 7, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 2 - English - Module 1', 'test_series': 'Prep Test 2', 'subject': 'English', 'module_number': 1, 'difficulty': None, 'start_question_id': 148, 'end_question_id': 174},
            {'exam_id': 8, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 2 - English - Module 2 - Easy', 'test_series': 'Prep Test 2', 'subject': 'English', 'module_number': 2, 'difficulty': 'Easy', 'start_question_id': 175, 'end_question_id': 201},
            {'exam_id': 9, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 2 - English - Module 2 - Hard', 'test_series': 'Prep Test 2', 'subject': 'English', 'module_number': 2, 'difficulty': 'Hard', 'start_question_id': 202, 'end_question_id': 228},
            {'exam_id': 10, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 2 - Math - Module 1', 'test_series': 'Prep Test 2', 'subject': 'Math', 'module_number': 1, 'difficulty': None, 'start_question_id': 229, 'end_question_id': 250},
            {'exam_id': 11, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 2 - Math - Module 2 - Easy', 'test_series': 'Prep Test 2', 'subject': 'Math', 'module_number': 2, 'difficulty': 'Easy', 'start_question_id': 251, 'end_question_id': 272},
            {'exam_id': 12, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 2 - Math - Module 2 - Hard', 'test_series': 'Prep Test 2', 'subject': 'Math', 'module_number': 2, 'difficulty': 'Hard', 'start_question_id': 273, 'end_question_id': 294},
            
            # Prep Test 3
            {'exam_id': 13, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 3 - English - Module 1', 'test_series': 'Prep Test 3', 'subject': 'English', 'module_number': 1, 'difficulty': None, 'start_question_id': 295, 'end_question_id': 321},
            {'exam_id': 14, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 3 - English - Module 2 - Easy', 'test_series': 'Prep Test 3', 'subject': 'English', 'module_number': 2, 'difficulty': 'Easy', 'start_question_id': 322, 'end_question_id': 348},
            {'exam_id': 15, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 3 - English - Module 2 - Hard', 'test_series': 'Prep Test 3', 'subject': 'English', 'module_number': 2, 'difficulty': 'Hard', 'start_question_id': 349, 'end_question_id': 375},
            {'exam_id': 16, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 3 - Math - Module 1', 'test_series': 'Prep Test 3', 'subject': 'Math', 'module_number': 1, 'difficulty': None, 'start_question_id': 376, 'end_question_id': 397},
            {'exam_id': 17, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 3 - Math - Module 2 - Easy', 'test_series': 'Prep Test 3', 'subject': 'Math', 'module_number': 2, 'difficulty': 'Easy', 'start_question_id': 398, 'end_question_id': 419},
            {'exam_id': 18, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 3 - Math - Module 2 - Hard', 'test_series': 'Prep Test 3', 'subject': 'Math', 'module_number': 2, 'difficulty': 'Hard', 'start_question_id': 420, 'end_question_id': 441},
            
            # Prep Test 4
            {'exam_id': 19, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 4 - English - Module 1', 'test_series': 'Prep Test 4', 'subject': 'English', 'module_number': 1, 'difficulty': None, 'start_question_id': 442, 'end_question_id': 468},
            {'exam_id': 20, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 4 - English - Module 2 - Easy', 'test_series': 'Prep Test 4', 'subject': 'English', 'module_number': 2, 'difficulty': 'Easy', 'start_question_id': 469, 'end_question_id': 495},
            {'exam_id': 21, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 4 - English - Module 2 - Hard', 'test_series': 'Prep Test 4', 'subject': 'English', 'module_number': 2, 'difficulty': 'Hard', 'start_question_id': 496, 'end_question_id': 522},
            {'exam_id': 22, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 4 - Math - Module 1', 'test_series': 'Prep Test 4', 'subject': 'Math', 'module_number': 1, 'difficulty': None, 'start_question_id': 523, 'end_question_id': 544},
            {'exam_id': 23, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 4 - Math - Module 2 - Easy', 'test_series': 'Prep Test 4', 'subject': 'Math', 'module_number': 2, 'difficulty': 'Easy', 'start_question_id': 545, 'end_question_id': 566},
            {'exam_id': 24, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 4 - Math - Module 2 - Hard', 'test_series': 'Prep Test 4', 'subject': 'Math', 'module_number': 2, 'difficulty': 'Hard', 'start_question_id': 567, 'end_question_id': 588},
            
            # Prep Test 5
            {'exam_id': 25, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 5 - English - Module 1', 'test_series': 'Prep Test 5', 'subject': 'English', 'module_number': 1, 'difficulty': None, 'start_question_id': 589, 'end_question_id': 615},
            {'exam_id': 26, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 5 - English - Module 2 - Easy', 'test_series': 'Prep Test 5', 'subject': 'English', 'module_number': 2, 'difficulty': 'Easy', 'start_question_id': 616, 'end_question_id': 642},
            {'exam_id': 27, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 5 - English - Module 2 - Hard', 'test_series': 'Prep Test 5', 'subject': 'English', 'module_number': 2, 'difficulty': 'Hard', 'start_question_id': 643, 'end_question_id': 669},
            {'exam_id': 28, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 5 - Math - Module 1', 'test_series': 'Prep Test 5', 'subject': 'Math', 'module_number': 1, 'difficulty': None, 'start_question_id': 670, 'end_question_id': 691},
            {'exam_id': 29, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 5 - Math - Module 2 - Easy', 'test_series': 'Prep Test 5', 'subject': 'Math', 'module_number': 2, 'difficulty': 'Easy', 'start_question_id': 692, 'end_question_id': 713},
            {'exam_id': 30, 'exam_name': 'The Princeton Review - Digital SAT Prep Test 5 - Math - Module 2 - Hard', 'test_series': 'Prep Test 5', 'subject': 'Math', 'module_number': 2, 'difficulty': 'Hard', 'start_question_id': 714, 'end_question_id': 735},
            
            # Advanced Online Test
            {'exam_id': 31, 'exam_name': 'The Princeton Review - Digital SAT Advanced Online Test - English - Module 1', 'test_series': 'Advanced Online Test', 'subject': 'English', 'module_number': 1, 'difficulty': None, 'start_question_id': 736, 'end_question_id': 762},
            {'exam_id': 32, 'exam_name': 'The Princeton Review - Digital SAT Advanced Online Test - English - Module 2 - Easy', 'test_series': 'Advanced Online Test', 'subject': 'English', 'module_number': 2, 'difficulty': 'Easy', 'start_question_id': 763, 'end_question_id': 789},
            {'exam_id': 33, 'exam_name': 'The Princeton Review - Digital SAT Advanced Online Test - English - Module 2 - Hard', 'test_series': 'Advanced Online Test', 'subject': 'English', 'module_number': 2, 'difficulty': 'Hard', 'start_question_id': 790, 'end_question_id': 816},
            {'exam_id': 34, 'exam_name': 'The Princeton Review - Digital SAT Advanced Online Test - Math - Module 1', 'test_series': 'Advanced Online Test', 'subject': 'Math', 'module_number': 1, 'difficulty': None, 'start_question_id': 817, 'end_question_id': 838},
            {'exam_id': 35, 'exam_name': 'The Princeton Review - Digital SAT Advanced Online Test - Math - Module 2 - Easy', 'test_series': 'Advanced Online Test', 'subject': 'Math', 'module_number': 2, 'difficulty': 'Easy', 'start_question_id': 839, 'end_question_id': 860},
            {'exam_id': 36, 'exam_name': 'The Princeton Review - Digital SAT Advanced Online Test - Math - Module 2 - Hard', 'test_series': 'Advanced Online Test', 'subject': 'Math', 'module_number': 2, 'difficulty': 'Hard', 'start_question_id': 861, 'end_question_id': 882},
        ]
        
        # Initialize after exams are defined
        self.login()
        self.create_directory_structure()

    def login(self):
        """Verify login status"""
        try:
            response = self.session.get(f"{self.base_url}/dashboard/", timeout=10)
            if "dashboard" in response.url.lower() or response.status_code == 200:
                print("✅ Authentication verified")
            else:
                print("⚠️  Authentication may have failed")
        except Exception as e:
            print(f"⚠️  Could not verify authentication: {e}")

    def create_directory_structure(self):
        """Create output directory structure"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        for exam in self.exams:
            series_dir = self.output_dir / exam['test_series'].replace(' ', '_')
            subject_dir = series_dir / exam['subject']
            subject_dir.mkdir(parents=True, exist_ok=True)

    def extract_content_from_element(self, element):
        """Extract clean text content from HTML element"""
        if not element:
            return ''
        
        # Remove script and style elements
        for script in element(["script", "style"]):
            script.decompose()
        
        # Get text and clean it up
        text = element.get_text(separator=' ', strip=True)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def extract_explanation_advanced(self, html_content, question_id, exam_id):
        """Advanced explanation extraction using multiple methods"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Method 1: Look for explanation in modal dialog
        explanation_modal = soup.find('dialog', {'id': 'explanation'})
        if explanation_modal:
            explanation_text = self.extract_content_from_element(explanation_modal)
            if explanation_text and len(explanation_text) > 10:
                return explanation_text
        
        # Method 2: Look for explanation in div with id
        explanation_div = soup.find('div', id='question-explanation')
        if explanation_div:
            explanation_text = self.extract_content_from_element(explanation_div)
            if explanation_text and len(explanation_text) > 10:
                return explanation_text
        
        # Method 3: Look for explanation by class
        explanation_selectors = [
            'div[class*="explanation"]',
            '.explanation',
            '.solution',
            '.answer-explanation',
            '[data-explanation]'
        ]
        
        for selector in explanation_selectors:
            elements = soup.select(selector)
            for element in elements:
                explanation_text = self.extract_content_from_element(element)
                if explanation_text and len(explanation_text) > 10:
                    # Basic check to avoid capturing irrelevant text
                    if 'explanation' in explanation_text.lower() or 'correct answer' in explanation_text.lower():
                        return explanation_text
        
        # Method 4: Look in JavaScript data for explanation patterns
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                content = script.string
                
                # Pattern 1: Direct explanation field
                explanation_patterns = [
                    r'"explanation":\s*"([^"]+(?:\\.[^"]*)*)"',
                    r'"explanation":\s*\'([^\']+(?:\\.[^\']*)*)\'',
                    r'explanation:\s*["\']([^"\']+)["\']'
                ]
                
                for pattern in explanation_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
                    for match in matches:
                        if match and len(match) > 10:
                            # Clean up the explanation text
                            explanation = match.replace('\\n', ' ').replace('\\"', '"').replace("\\'", "'")
                            explanation = re.sub(r'\\(.)', r'\1', explanation)  # Unescape characters
                            explanation = re.sub(r'\s+', ' ', explanation).strip()
                            if len(explanation) > 10 and 'explanation' not in explanation.lower()[:20]:
                                return explanation
        
        return None

    def extract_metadata_from_html(self, soup):
        """Extracts metadata by parsing the stats divs in the HTML."""
        metadata = {
            'section': None,
            'domain': None,
            'skill': None,
        }
        
        stats_container = soup.find('div', class_='question-metadata')
        if not stats_container:
            return metadata # Return empty metadata if not found
            
        stats_divs = stats_container.find_all('div', class_='stat')
        if not stats_divs:
            return metadata

        for stat_div in stats_divs:
            title_div = stat_div.find('div', class_='stat-title')
            value_div = stat_div.find('div', class_='stat-value')
            
            if title_div and value_div:
                title = title_div.get_text(strip=True).lower()
                value = value_div.get_text(strip=True)
                
                if 'section' in title:
                    metadata['section'] = value
                elif 'domain' in title:
                    metadata['domain'] = value
                elif 'skill' in title:
                    metadata['skill'] = value
        
        return metadata

    def extract_answer_choices_enhanced(self, soup):
        """Enhanced answer choice extraction with better selectors"""
        choices = {}
        choice_ids = {}
        answer_type = 'spr'  # Default to student produced response
        
        # Multiple strategies to find answer choices
        choice_selectors = [
            'div.choice',
            '.choice',
            '[class*="choice"]',
            'div[x-data*="answer_id"]',
            '.answer-choice',
            '.option'
        ]
        
        choice_elements = []
        for selector in choice_selectors:
            elements = soup.select(selector)
            if elements:
                choice_elements = elements
                break
        
        if choice_elements:
            answer_type = 'mcq'
            print(f"      🔍 Found {len(choice_elements)} choice elements")
            
            for choice_elem in choice_elements:
                try:
                    # Multiple ways to extract letter (A, B, C, D)
                    letter = None
                    
                    # Method 1: Look for choice-letter class
                    letter_elem = choice_elem.find('div', class_='choice-letter')
                    if letter_elem:
                        letter = letter_elem.get_text().strip()
                    
                    # Method 2: Look for any element with "letter" in class
                    if not letter:
                        letter_elem = choice_elem.select_one('[class*="letter"]')
                        if letter_elem:
                            letter = letter_elem.get_text().strip()
                    
                    # Method 3: Look for single letter at start of text
                    if not letter:
                        text = choice_elem.get_text().strip()
                        if text and len(text) > 0 and text[0] in ['A', 'B', 'C', 'D']:
                            letter = text[0]
                    
                    # Method 4: Look in x-data for letter
                    if not letter:
                        x_data = choice_elem.get('x-data', '')
                        letter_match = re.search(r'letter:\s*["\']([A-D])["\']', x_data)
                        if letter_match:
                            letter = letter_match.group(1)
                    
                    if not letter or letter not in ['A', 'B', 'C', 'D']:
                        continue
                    
                    print(f"      📝 Processing choice {letter}")
                    
                    # Extract choice text - multiple methods
                    choice_text = None
                    
                    # Method 1: Look for choice-content class
                    choice_content = choice_elem.find('div', class_='choice-content')
                    if choice_content:
                        choice_text = self.extract_content_from_element(choice_content)
                    
                    # Method 2: Look for self-center class (common pattern)
                    if not choice_text:
                        choice_content = choice_elem.find('div', class_='self-center')
                        if choice_content:
                            choice_text = self.extract_content_from_element(choice_content)
                    
                    # Method 3: Look for any div with "content" in class
                    if not choice_text:
                        choice_content = choice_elem.select_one('[class*="content"]')
                        if choice_content:
                            choice_text = self.extract_content_from_element(choice_content)
                    
                    # Method 4: Extract from x-data
                    if not choice_text:
                        x_data = choice_elem.get('x-data', '')
                        text_match = re.search(r'text:\s*["\']([^"\']+)["\']', x_data)
                        if text_match:
                            choice_text = text_match.group(1)
                    
                    # Method 5: Get all text and remove the letter
                    if not choice_text:
                        full_text = self.extract_content_from_element(choice_elem)
                        if full_text and full_text.startswith(letter):
                            choice_text = full_text[1:].strip()
                            if choice_text.startswith('.') or choice_text.startswith(')'):
                                choice_text = choice_text[1:].strip()
                    
                    if choice_text:
                        choices[letter] = choice_text
                        print(f"      ✅ Choice {letter}: {choice_text[:30]}...")
                    
                    # Extract choice ID from data attributes or x-data
                    choice_id = None
                    
                    # Method 1: x-data
                    x_data = choice_elem.get('x-data', '')
                    if x_data:
                        id_match = re.search(r'answer_id:\s*(\d+)', x_data)
                        if id_match:
                            choice_id = int(id_match.group(1))
                    
                    # Method 2: data attributes
                    if not choice_id:
                        data_id = choice_elem.get('data-answer-id') or choice_elem.get('data-id')
                        if data_id:
                            try:
                                choice_id = int(data_id)
                            except ValueError:
                                pass
                    
                    if choice_id:
                        choice_ids[letter] = choice_id
                
                except Exception as e:
                    print(f"      ⚠️  Error processing choice: {e}")
                    continue
        
        # Also try to extract from JavaScript data as backup
        if not choices:
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string:
                    content = script.string
                    
                    # Look for answer choices in JSON format
                    choice_patterns = [
                        r'"answer_choices":\s*\[(.*?)\]',
                        r'"choices":\s*\[(.*?)\]',
                        r'answer_choices:\s*\[(.*?)\]'
                    ]
                    
                    for pattern in choice_patterns:
                        match = re.search(pattern, content, re.DOTALL)
                        if match:
                            choices_json = match.group(1)
                            # Try to extract individual choices
                            choice_matches = re.findall(r'"letter":\s*"([A-D])".*?"text":\s*"([^"]+)"', choices_json)
                            if choice_matches:
                                answer_type = 'mcq'
                                for letter, text in choice_matches:
                                    choices[letter] = text
                                break
                    
                    if choices:
                        break
        
        print(f"      📊 Final result: {answer_type}, {len(choices)} choices found")
        return answer_type, choices, choice_ids

    def extract_correct_answer_enhanced(self, soup, answer_type, choices=None):
        """Enhanced correct answer extraction"""
        correct_answer = ''
        
        # Look in JavaScript data
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                content = script.string
                
                if answer_type == 'mcq':
                    # Multiple patterns to find correct answer
                    correct_patterns = [
                        r'"is_correct":\s*true.*?"letter":\s*"([A-D])"',
                        r'"letter":\s*"([A-D])".*?"is_correct":\s*true',
                        r'"correct":\s*true.*?"letter":\s*"([A-D])"',
                        r'"letter":\s*"([A-D])".*?"correct":\s*true',
                        r'is_correct:\s*true.*?letter:\s*["\']([A-D])["\']',
                        r'letter:\s*["\']([A-D])["\'].*?is_correct:\s*true',
                        r'"correct_answer":\s*"([A-D])"',
                        r'correct_answer:\s*["\']([A-D])["\']'
                    ]
                    
                    for pattern in correct_patterns:
                        matches = re.findall(pattern, content, re.DOTALL)
                        for match in matches:
                            if match in ['A', 'B', 'C', 'D']:
                                correct_answer = match
                                print(f"      ✅ Found correct answer: {correct_answer}")
                                break
                        if correct_answer:
                            break
                    
                    if correct_answer:
                        break
                
                elif answer_type == 'spr':
                    # Look for SPR answer value
                    spr_patterns = [
                        r'"value":\s*"([^"]+)"',
                        r'"answer":\s*"([^"]+)"',
                        r'"correct_answer":\s*"([^"]+)"',
                        r'value:\s*["\']([^"\']+)["\']',
                        r'answer:\s*["\']([^"\']+)["\']'
                    ]
                    
                    for pattern in spr_patterns:
                        match = re.search(pattern, content)
                        if match:
                            correct_answer = match.group(1)
                            print(f"      ✅ Found SPR answer: {correct_answer}")
                            break
                    
                    if correct_answer:
                        break
        
        # Backup method: look for correct answer in HTML elements
        if not correct_answer and answer_type == 'mcq':
            # Look for checked/selected answer choice
            correct_choice = soup.find('div', class_='choice correct') or soup.find('.choice.correct')
            if correct_choice:
                letter_elem = correct_choice.find('div', class_='choice-letter')
                if letter_elem:
                    correct_answer = letter_elem.get_text().strip()
        
        return correct_answer

    def extract_question_data_comprehensive(self, html_content, question_url):
        """Comprehensive question data extraction - gets EVERYTHING"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Parse question ID from URL
            question_id_match = re.search(r'/question/(\d+)/', question_url)
            if not question_id_match:
                return None
            
            question_id = int(question_id_match.group(1))
            
            # Initialize question data structure
            question_data = {
                'question_id': question_id,
                'section': '',
                'domain': '',
                'skill': '',
                'answer_type': '',
                'correct_answer': '',
                'answer_choices_enhanced': {},
                'answer_choice_ids': {},
                'stimulus': '',
                'question_stem': '',
                'explanation': ''
            }
            
            print(f"   📊 Extracting comprehensive data for question {question_id}...")
            
            # Extract metadata (section, domain, skill)
            metadata = self.extract_metadata_from_html(soup)
            question_data.update(metadata)
            
            # Extract answer choices and determine answer type
            answer_type, choices, choice_ids = self.extract_answer_choices_enhanced(soup)
            question_data['answer_type'] = answer_type
            question_data['answer_choices_enhanced'] = choices
            question_data['answer_choice_ids'] = choice_ids
            
            # Extract correct answer
            correct_answer = self.extract_correct_answer_enhanced(soup, answer_type, choices)
            question_data['correct_answer'] = correct_answer
            
            # Extract stimulus (passage/context)
            stimulus_elem = soup.find('div', id='question-stimulus')
            if stimulus_elem:
                question_data['stimulus'] = self.extract_content_from_element(stimulus_elem)
            
            # Extract question stem
            stem_elem = soup.find('div', id='question-stem')
            if stem_elem:
                question_data['question_stem'] = self.extract_content_from_element(stem_elem)
            
            # Extract explanation using advanced methods
            explanation = self.extract_explanation_advanced(html_content, question_id, question_data.get('exam_id'))
            question_data['explanation'] = explanation or ''
            
            # Validation and reporting
            print(f"   ✅ Data extracted:")
            print(f"      📝 Question stem: {'✅' if question_data['question_stem'] else '❌'}")
            print(f"      📖 Stimulus: {'✅' if question_data['stimulus'] else '❌'}")
            print(f"      🔤 Answer choices: {'✅' if question_data['answer_choices_enhanced'] else '❌'}")
            print(f"      ✔️  Correct answer: {'✅' if question_data['correct_answer'] else '❌'}")
            print(f"      💡 Explanation: {'✅' if question_data['explanation'] else '❌'}")
            print(f"      📊 Metadata: {'✅' if question_data['section'] or question_data['domain'] else '❌'}")
            
            return question_data
            
        except Exception as e:
            print(f"❌ Error extracting comprehensive question data: {e}")
            return None

    def scrape_question_comprehensive(self, question_id, exam_data):
        """Comprehensive question scraping"""
        url = f"{self.base_url}/question/{question_id}/?question_set=exam&exam_id={exam_data['exam_id']}"
        
        for attempt in range(2):
            try:
                response = self.session.get(url, timeout=20)
                response.raise_for_status()
                html_content = response.text

                # Check if we got a valid question page
                if 'question-stem' in html_content or 'question-stimulus' in html_content:
                    question_data = self.extract_question_data_comprehensive(html_content, url)
                    if question_data:
                        # Add exam metadata
                        question_data['exam_id'] = exam_data['exam_id']
                        question_data['exam_name'] = exam_data['exam_name']
                        question_data['test_series'] = exam_data['test_series']
                        question_data['subject'] = exam_data['subject']
                        question_data['module_number'] = exam_data['module_number']
                        question_data['difficulty'] = exam_data['difficulty']
                        question_data['url'] = url
                        question_data['scraped_at'] = datetime.now().isoformat()
                    return question_data
                else:
                    print(f"⚠️  Invalid page for {url} on attempt {attempt + 1}")
                    if attempt == 0:
                        self.login()
                    time.sleep(2)

            except requests.exceptions.RequestException as e:
                print(f"❌ HTTP Error scraping {url} on attempt {attempt + 1}: {e}")
                if attempt == 1:
                    return None
                time.sleep(2)

        return None

    def test_comprehensive_extraction(self, test_questions=[2900, 2901, 2902]):
        """Test comprehensive extraction on multiple questions"""
        print("🔬 COMPREHENSIVE EXTRACTION TEST")
        print("=" * 50)
        
        test_exam = self.exams[0]  # Free practice test
        results = []
        
        for question_id in test_questions:
            print(f"\n🧪 Testing Question {question_id}")
            print("-" * 30)
            
            result = self.scrape_question_comprehensive(question_id, test_exam)
            if result:
                results.append(result)
                
                # Show detailed results
                print(f"\n📋 QUESTION {question_id} RESULTS:")
                print(f"   ID: {result['question_id']}")
                print(f"   Section: {result['section']}")
                print(f"   Domain: {result['domain']}")
                print(f"   Skill: {result['skill']}")
                print(f"   Type: {result['answer_type']}")
                print(f"   Correct Answer: {result['correct_answer']}")
                print(f"   Question Stem: {result['question_stem'][:80]}..." if result['question_stem'] else "   Question Stem: [MISSING]")
                print(f"   Stimulus: {result['stimulus'][:80]}..." if result['stimulus'] else "   Stimulus: [MISSING]")
                print(f"   Answer Choices: {list(result['answer_choices_enhanced'].keys())}")
                print(f"   Explanation: {result['explanation'][:100]}..." if result['explanation'] else "   Explanation: [MISSING]")
                
            else:
                print(f"❌ Failed to extract question {question_id}")
            
            time.sleep(1)
        
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print(f"✅ Successfully extracted: {len(results)}/{len(test_questions)} questions")
        
        if results:
            # Calculate success rates for different data types
            explanations_found = sum(1 for r in results if r['explanation'])
            stems_found = sum(1 for r in results if r['question_stem'])
            choices_found = sum(1 for r in results if r['answer_choices_enhanced'])
            correct_answers_found = sum(1 for r in results if r['correct_answer'])
            
            print(f"📈 Data Quality:")
            print(f"   Explanations: {explanations_found}/{len(results)} ({explanations_found/len(results)*100:.1f}%)")
            print(f"   Question Stems: {stems_found}/{len(results)} ({stems_found/len(results)*100:.1f}%)")
            print(f"   Answer Choices: {choices_found}/{len(results)} ({choices_found/len(results)*100:.1f}%)")
            print(f"   Correct Answers: {correct_answers_found}/{len(results)} ({correct_answers_found/len(results)*100:.1f}%)")
        
        return results

    def save_questions_to_file(self, exam_data, questions):
        """Save a list of questions to a JSON file."""
        series_dir = self.output_dir / exam_data['test_series'].replace(' ', '_')
        subject_dir = series_dir / exam_data['subject']
        subject_dir.mkdir(parents=True, exist_ok=True)
        
        # Sanitize filename
        filename = re.sub(r'[^\w\s-]', '', exam_data['exam_name']).strip()
        filename = re.sub(r'[-\s]+', '_', filename) + '.json'
        
        output_path = subject_dir / filename
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(questions, f, indent=2, ensure_ascii=False)
            print(f"   💾 Saved {len(questions)} questions to {output_path}")
        except Exception as e:
            print(f"   ❌ Error saving file {output_path}: {e}")


def main():
    """Main function to run the scraper in production mode."""
    print("🚀 Starting Comprehensive Princeton Review Scraper")
    start_time = time.time()
    
    scraper = ComprehensiveFixedScraper()
    
    total_questions_scraped = 0
    total_exams_processed = 0
    errors = []
    
    # --- PRODUCTION MODE: Scrape all exams ---
    for exam in scraper.exams:
        print("-" * 60)
        print(f" scraping exam: {exam['exam_name']}")
        
        try:
            questions = []
            for question_id in range(exam['start_question_id'], exam['end_question_id'] + 1):
                question_data = scraper.scrape_question_comprehensive(question_id, exam)
                if question_data:
                    questions.append(question_data)
                    total_questions_scraped += 1
            
            # Save the collected questions to a file
            scraper.save_questions_to_file(exam, questions)
            total_exams_processed += 1
            
        except Exception as e:
            error_message = f"Failed to scrape exam '{exam['exam_name']}' (ID: {exam['exam_id']}): {e}"
            print(f"❌ {error_message}")
            errors.append(error_message)

    # --- End of scraping ---
    end_time = time.time()
    duration = end_time - start_time
    
    print("\n" + "="*60)
    print("🎉 Scraping Complete!")
    print(f"  Total Exams Processed: {total_exams_processed}/{len(scraper.exams)}")
    print(f"  Total Questions Scraped: {total_questions_scraped}")
    print(f"  Total Errors: {len(errors)}")
    print(f"  Duration: {time.strftime('%H:%M:%S', time.gmtime(duration))}")
    
    if errors:
        print("\n⚠️  Errors Encountered:")
        for error in errors:
            print(f"  - {error}")


if __name__ == '__main__':
    main()