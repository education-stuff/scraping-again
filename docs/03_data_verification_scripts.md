# Data Verification & Analysis Scripts

After scraping, it's crucial to verify the data's integrity. These scripts are used to check for completeness, count questions, and perform deep analysis to ensure the quality of the scraped JSON files.

---

### `check_all_questions.py`

*   **Purpose**: To iterate through all scraped JSON files and verify that each question object is well-formed.
*   **Functionality**: It might check for the presence of key fields like `question_stem`, `answer_choices`, `correct_answer`, and `explanation` in every question.

---

### `check_missing.py`

*   **Purpose**: To identify gaps in the scraped data.
*   **Functionality**: This script reads the `scraped_data` directory, compiles a list of all scraped question IDs, and compares it against the expected complete range of IDs. It then reports any missing numbers.

---

### `check_ranges.py`

*   **Purpose**: To verify that the question IDs within each scraped test file fall within the expected range for that exam module.
*   **Functionality**: It helps catch issues where the scraper might have over- or under-scraped a particular module.

---

### `check_test_results.py`

*   **Purpose**: A script to quickly summarize the results of a scrape for a single test.
*   **Functionality**: It would typically load a JSON file and report the number of questions scraped, and perhaps list the question IDs found.

---

### `count_questions.py`

*   **Purpose**: To provide a summary of the total number of questions scraped across all files.
*   **Functionality**: It recursively scans the `scraped_data` directory, opens each JSON file, and aggregates the count of questions, providing a total count for the entire dataset.

---

### `deep_verification.py` & `final_verification.py`

*   **Purpose**: These scripts perform more thorough checks than the simple counting or missing-ID scripts.
*   **Functionality**: They might validate the content itself, for example:
    *   Ensuring `correct_answer` is one of the `answer_choices`.
    *   Checking that `explanation` fields are not empty.
    *   Validating metadata fields.
*   **`final_verification.py`** was likely the last check run after all scraping and data fixing was complete.

---

### `quick_check.py`

*   **Purpose**: A lightweight script for a fast spot-check on the data, likely used during development.
*   **Functionality**: It might just check if the most recent output file was created and is not empty.

---

### `monitor_progress.py`

*   **Purpose**: To provide a real-time view of the scraping progress.
*   **Functionality**: While a long scraping job is running, this script can be run in a separate terminal. It would periodically count the files and questions in the output directory to show how many have been completed so far.

---

### `verification_report.txt`

*   **Purpose**: A text file containing the output of one of the verification scripts.
*   **Functionality**: It's a saved log of a past data verification run, useful for historical reference.
