# Folder Zipper

This repository contains a Python tool to create a folder report (with file sizes, dates, and MD5 checksums), detect and remove duplicate files, zip the folder, and optionally delete the original folder. It is available as a GUI app or a command-line script.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [Acknowledgements](#acknowledgements)

## Overview

Folder Zipper helps you archive a folder by generating a detailed report of all files (including MD5 checksums for duplicate detection), removing duplicate copies (keeping one per checksum), and creating a ZIP archive. The GUI version uses a file picker; the CLI version accepts a folder path.

## Features

- **Folder report**: Lists every file with path, size (B/KB/MB/GB), modified date, and MD5 checksum.
- **Duplicate detection**: Finds files with the same MD5 checksum.
- **Duplicate removal**: Keeps one copy per checksum and deletes the rest before zipping.
- **ZIP archive**: Creates a single ZIP file (e.g. `C:\MyFolder.zip`) containing all remaining files and the report.
- **GUI**: Select a folder via a dialog; report and zip run automatically, then the original folder is deleted.
- **CLI**: Run from the terminal with a folder path for scripting or automation.

## Installation

### Prerequisites

- Python 3.6 or later
- No external pip packages required (uses only the standard library)

### Steps

1. Clone or download the repository:
   ```sh
   git clone <repository-url>
   cd folder_to_zip
   ```

2. (Optional) Use a virtual environment:
   ```sh
   python -m venv venv
   venv\Scripts\activate   # Windows
   # or: source venv/bin/activate   # Linux/macOS
   ```

3. Dependencies are in the standard library; see `requirements.txt` for notes. No `pip install` is needed unless you add new dependencies later.

## Usage

### GUI (recommended)

1. Run the GUI script:
   ```sh
   python folder_zipper_gui.py
   ```

2. In the dialog, select the folder to report, zip, and delete.

3. The script will:
   - Build a report with MD5 checksums and remove duplicate files (keeping one copy each).
   - Write `folder_report.txt` inside the folder (included in the ZIP).
   - Create `<folder_name>.zip` in the parent directory.
   - Delete the original folder.

### CLI

1. Run the CLI script and enter the full path when prompted:
   ```sh
   python folder_to_zip.py
   ```
   Then type the folder path and press Enter.

2. The same steps (report, duplicate removal, zip, delete) run as in the GUI; output is printed to the console.

### Report contents

- **Per file**: path, size, modified date, MD5.
- **Duplicates section**: For each MD5 that had multiple files, which path was **Kept** and which were **Removed**.

## Project Structure

```
folder_to_zip/
├── folder_zipper_gui.py   # GUI app (folder picker, report, zip, delete)
├── folder_to_zip.py       # CLI app (prompt for path, same logic)
├── requirements.txt       # Dependency notes (std lib only)
├── sample_readme.txt      # Template used for this README
└── README.md              # This file
```

## Contributing

Contributions are welcome. To contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a Pull Request.

## Acknowledgements

Thanks to the Python community for the standard library modules (e.g. `zipfile`, `hashlib`, `tkinter`) that make this tool possible.

---

If you have questions or need help, feel free to open an issue or reach out.
