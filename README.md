# OnePrep SAT Scraper

A comprehensive web scraper for extracting SAT practice questions from OnePrep.xyz (Princeton Review Digital SAT practice tests).

## Overview

This scraper extracts complete question data including:
- Question stems with HTML formatting preserved
- Answer choices with HTML formatting
- Explanations with HTML formatting
- Correct answers
- Metadata (section, domain, skill)

## Features

- **Comprehensive Coverage**: Scrapes all Princeton Review Digital SAT practice tests
  - Free Practice Test
  - Prep Tests 1-5
  - Advanced Online Test
- **Complete Question Data**: Extracts questions, answers, explanations, and metadata
- **HTML Preservation**: Maintains original formatting including SVG images and math notation
- **Robust Extraction**: Uses embedded JavaScript data extraction for reliability
- **Session Management**: Handles authentication and session management
- **Error Handling**: Built-in retry logic and comprehensive error handling
- **Organized Output**: Structures data by test series and subject

## Test Coverage

- **English Section**: 27 questions per module (Module 1 & 2)
- **Math Section**: 22 questions per module (Module 1 & 2)
- **Total**: 36 exams covering 3000+ questions (ID range 1-3046)

## Structure

```
scraping-oneprep-again/
├── oneprep_scraper_v2.py    # Main scraper implementation
├── main.py                  # Original scraper (legacy)
├── scraped_data/           # Output directory
│   ├── Free_Practice_Test/
│   ├── Prep_Test_1/
│   ├── Prep_Test_2/
│   ├── Prep_Test_3/
│   ├── Prep_Test_4/
│   ├── Prep_Test_5/
│   └── Advanced_Online_Test/
└── test_*.py              # Testing and debugging scripts
```

## Usage

1. **Setup Authentication**: Configure session cookies in `oneprep_cookies.json`
2. **Run the Scraper**: Execute `oneprep_scraper_v2.py`
3. **Check Output**: Results are saved in `scraped_data/` directory organized by test series

## Technical Details

### Data Extraction Method

The scraper uses a sophisticated approach to extract data:

1. **Page-Based Extraction**: Parses embedded JavaScript data from question pages
2. **HTML Preservation**: Maintains all original HTML formatting
3. **Dynamic Content Handling**: Extracts explanations from embedded Alpine.js data structures
4. **Robust Parsing**: Uses multiple fallback methods for data extraction

### Key Components

- **Session Management**: Handles authentication cookies
- **HTML Content Extraction**: Preserves formatting, images, and math notation
- **Embedded Data Parsing**: Extracts answers and explanations from JavaScript
- **Error Handling**: Comprehensive retry logic and error reporting
- **Data Validation**: Ensures complete data extraction

## Requirements

- Python 3.x
- requests
- beautifulsoup4
- json
- re (regex)

## Installation

```bash
pip install requests beautifulsoup4
```

## Configuration

Create a `oneprep_cookies.json` file with your session cookies:

```json
{
  "sessionid": "your_session_id",
  "csrftoken": "your_csrf_token"
}
```

## Output Format

Questions are saved as JSON files with the following structure:

```json
{
  "question_id": "1234",
  "question_stem": "<p>Question text with HTML formatting</p>",
  "stimulus": "<div>Passage or context</div>",
  "answer_choices": [
    {
      "letter": "A",
      "text": "<p>Answer choice with HTML</p>",
      "is_correct": false
    }
  ],
  "correct_answer": "B",
  "explanation": "<p>Explanation with HTML formatting</p>",
  "metadata": {
    "section": "Math",
    "domain": "Algebra",
    "skill": "Linear equations"
  }
}
```

## Status

✅ **WORKING** - All features functional as of latest update

- Question stems: ✓ (HTML preserved)
- Answer choices: ✓ (HTML preserved) 
- Explanations: ✓ (HTML preserved)
- Correct answers: ✓ (extracted from embedded data)
- Metadata: ✓ (section, domain, skill)

## Notes

- The scraper has been updated to handle changes in the OnePrep website structure
- Explanations are now extracted from embedded page data rather than API calls
- All HTML formatting is preserved for proper rendering of math questions
- The scraper is designed to be respectful of the website's resources with built-in delays

---

*This tool is for educational purposes only. Please respect the website's terms of service and use responsibly.*
