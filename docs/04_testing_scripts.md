# Testing Scripts

These scripts are designed to test isolated pieces of functionality. Unlike debugging scripts, which are for diagnosing unknown problems, testing scripts are typically used to confirm that a specific, known feature is working as expected.

---

### `direct_scrape_test.py`

*   **Purpose**: To test the core scraping logic on a single, hardcoded question ID.
*   **Functionality**: It runs the main extraction function for one question and prints the result to the console, providing a quick way to see if the scraper can successfully parse a page.

---

### `test_api_response.py`

*   **Purpose**: To test the response of one of the website's APIs.
*   **Functionality**: This script would make a request to a specific API endpoint (e.g., the old `/submit/` or `/explanation/` endpoints) and print the status code and response data to check for changes.

---

### `test_direct_explanation.py` & `test_explanation_fetch.py`

*   **Purpose**: These scripts were created to test different methods of fetching explanations.
*   **Functionality**: They likely contain various attempts and strategies to get the explanation data, which was one of the most challenging parts of this project. This was part of the discovery process that led to finding the data embedded in the page's JavaScript.

---

### `test_missing_question.py`

*   **Purpose**: Similar to `debug_missing_questions.py`, but framed as a repeatable test.
*   **Functionality**: It asserts that a request to a known non-existent question ID returns a 404, or that a valid ID returns a 200. This helps ensure the scraper's assumptions about the website are still valid.

---

### `test_question_page.py`

*   **Purpose**: To test the parsing logic of a question page from a saved HTML file.
*   **Functionality**: It reads a local HTML file and runs the data extraction functions on it, asserting that the correct data (stem, choices, etc.) is extracted. This is a form of unit testing for the parser.

---

### `test_submit_answer.py`

*   **Purpose**: To test the functionality of submitting an answer to the website.
*   **Functionality**: This was important when it was believed that submitting an answer was required to reveal the explanation. The script would POST data to the submission endpoint and analyze the result.
*   **Status**: Obsolete, as answer submission is not required with the final scraping method.

---

### `test_v2_scraper.py` & `test_v2_scraper_english.py`

*   **Purpose**: To test the `oneprep_scraper_v2.py` script on a small sample of questions.
*   **Functionality**: These scripts run the v2 scraper for a few hardcoded question IDs (for both math/english or just english) and save the output to a test JSON file (e.g., `test_v2_output.json`). This allows for quick verification of the v2 scraper's output without running a full scrape.
