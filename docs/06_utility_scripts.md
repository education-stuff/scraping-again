# Utility & Helper Scripts

This section covers various helper scripts that perform post-processing, data fixing, or other utility functions that support the main scraping and verification tasks.

---

### `extract_page_data.py`

*   **Purpose**: To run the data extraction logic on a locally saved HTML file and print the extracted JSON data.
*   **Functionality**: This is a utility version of `inspect_current_page.py`. While the inspection script is for debugging the *process*, this script is for getting the final *output* from a local file. It's useful for quickly getting the data for a single page without needing to run the full scraper.

---

### `fix_correct_answers.py`

*   **Purpose**: A script written to correct the `correct_answer` field in already scraped data.
*   **Functionality**: This was likely created when a more reliable method for finding the correct answer was discovered. The script would iterate through existing JSON files, re-apply the new logic, and update the files in place.

---

### `post_process_correct_answers.py`

*   **Purpose**: Similar to `fix_correct_answers.py`, but likely more comprehensive.
*   **Functionality**: This script probably performs a more complex post-processing routine on the scraped data to fix answer-related issues. It might handle different question types or edge cases that the simpler fix script did not. This is a common pattern: a simple fix script is created, and then a more robust "post-processing" script is developed as more edge cases are found.
