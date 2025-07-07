# Project Files

This section provides an overview of miscellaneous project files, such as the main `README.md`, Git-related files, and Python cache directories.

---

### `README.md` (Root)

*   **Purpose**: The main entry point for someone new to the project.
*   **Content**: It should contain a brief project description, setup instructions (like installing dependencies and creating the `oneprep_cookies.json` file), and basic usage instructions for running the main scraper.
*   **Note**: This documentation effort will supplement the main `README.md`. A link to this `docs` directory should be added to the main `README.md`.

---

### `.gitignore`

*   **Purpose**: To specify files and directories that should be ignored by Git version control.
*   **Key Entries**:
    *   `oneprep_cookies.json`: To protect sensitive authentication credentials.
    *   `scraped_data/`: To avoid committing large amounts of data to the repository.
    *   `__pycache__/`: To ignore Python's compiled bytecode files.
    *   `*.log`: To ignore log files.
    *   `*.html`: To ignore saved page content used for debugging.

---

### `__pycache__/`

*   **Purpose**: This directory is automatically created by Python.
*   **Content**: It stores the compiled bytecode (`.pyc` files) of the Python scripts. This helps speed up subsequent runs by avoiding the need to re-compile the source code. It is safe to delete this directory; Python will regenerate it as needed.

---

### `.git/`

*   **Purpose**: This directory is created when you initialize a Git repository (`git init`).
*   **Content**: It contains all the information about your project's version control history, including commits, branches, and remote repository addresses. You should not manually edit files in this directory.
