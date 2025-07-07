# Debugging & Inspection Scripts

This section covers scripts created specifically for debugging the scraper and inspecting the raw HTML content of the question pages. These are essential tools for diagnosing problems when the scraper fails or extracts incorrect data.

---

### `debug_explanation_api.py`

*   **Purpose**: Used to investigate issues with fetching explanations. Early versions of the scraper struggled with the explanation API.
*   **Functionality**: This script likely makes direct requests to the explanation endpoint (`/question/{id}/explanation/`) to analyze the response and headers.
*   **Status**: Likely obsolete, as the final scraper version (`oneprep_scraper_v2.py`) discovered that explanations are embedded in the main page's JavaScript and not fetched from a separate API endpoint anymore.

---

### `debug_missing_questions.py`

*   **Purpose**: To diagnose why certain questions within a known range were not being scraped successfully.
*   **Functionality**: It attempts to fetch a specific, known-missing question ID to check for 404 errors, redirects, or unexpected page structures that might cause the main scraper to fail.

---

### `debug_page_content.py`

*   **Purpose**: A general-purpose script to download and save the full HTML of a specific question page for manual inspection.
*   **Functionality**: Takes a question ID as input, fetches the page, and saves it to a file (like `current_page.html`). This allows developers to analyze the HTML structure without having to repeatedly hit the server.

---

### `debug_spr_question.py`

*   **Purpose**: To debug issues related to "Student-Produced Response" (SPR) questions, which are common in the Math sections.
*   **Functionality**: This script would focus on scraping an SPR question to see how its structure differs from multiple-choice questions and ensure the parser handles it correctly.

---

### `inspect_current_page.py`

*   **Purpose**: To parse a locally saved HTML file (`current_page.html` or `question_page.html`) and test extraction logic on it.
*   **Functionality**: Instead of fetching from the web, it reads the local file. This is crucial for developing and refining parsing functions (e.g., for `BeautifulSoup`) without making network requests, speeding up the development cycle.

---

### `current_page.html` & `question_page.html`

*   **Purpose**: These are raw HTML files saved from the OnePrep website. They serve as static test cases for the parsing and debugging scripts.
*   **Usage**: They are used as input for `inspect_current_page.py` or can be opened in a browser for manual inspection of the page structure, scripts, and CSS classes.
