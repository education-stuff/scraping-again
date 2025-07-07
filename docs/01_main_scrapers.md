# Main Scrapers

This section details the primary scripts used for scraping question data from OnePrep. These are the core components of the project that perform the data extraction.

---

### `main.py`

*   **Purpose**: This is the main, most comprehensive scraper. It is designed to be the primary entry point for running a full scrape of all tests and questions.
*   **Functionality**:
    *   Iterates through a predefined list of exams and question ID ranges.
    *   Handles both English and Math sections.
    *   Manages session authentication using `oneprep_cookies.json`.
    *   Includes robust error handling, retry logic, and progress tracking.
    *   Saves the scraped data into structured JSON files in the `scraped_data` directory.
*   **Usage**: `python main.py`

---

### `oneprep_scraper.py`

*   **Purpose**: This was the original version of the scraper. It contains the foundational logic for scraping but may be outdated.
*   **Status**: Deprecated in favor of `oneprep_scraper_v2.py` and `main.py`. It is kept for historical reference.

---

### `oneprep_scraper_v2.py`

*   **Purpose**: An updated and refactored version of the original scraper. It introduced significant improvements in data extraction, particularly for handling dynamic content (like explanations) loaded with Alpine.js.
*   **Key Improvements**:
    *   Extracts data from embedded JSON within the page's JavaScript, which is more reliable than parsing HTML.
    *   Preserves HTML formatting for questions and answers.
*   **Usage**: This script's logic is largely integrated into `main.py`. It can be run standalone for specific tests if needed.

---

### `scrape_advanced_test.py`

*   **Purpose**: A specialized script to scrape the "Advanced Online Test" series from Princeton Review.
*   **Functionality**:
    *   Targets a specific set of `exam_id`s and question ranges corresponding to the Advanced test.
    *   Contains logic tailored to the structure of this specific test, which was found to have a different number of math questions than standard tests.
*   **Usage**: `python scrape_advanced_test.py`

---

### `scrape_math_only.py`

*   **Purpose**: A script dedicated to scraping only the Math sections of the tests.
*   **Functionality**: Useful for targeted rescraping if there were issues with the math questions in a full run.
*   **Usage**: `python scrape_math_only.py`

---

### `final_math_rescrape.py` & `rescrape_math_with_gaps.py`

*   **Purpose**: These scripts were created to address specific issues found in the math question data, such as gaps in question IDs or incorrect question counts.
*   **Functionality**: They implement targeted logic to re-fetch and correct the math data.
*   **Status**: These are likely single-use scripts for data correction and may not be needed for a fresh scrape.

---

### `scrape_module_2_hard_only.py`

*   **Purpose**: A highly specific script to scrape only the "Module 2 Hard" section of a test.
*   **Functionality**: Created for debugging or targeted scraping of this specific module, which sometimes presented unique challenges.
*   **Usage**: `python scrape_module_2_hard_only.py`
