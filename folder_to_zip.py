import os
import zipfile
import shutil
from datetime import datetime

def folder_report_and_zip(folder_path):
    # Output files
    report_file = os.path.join(folder_path, "folder_report.txt")
    zip_path = folder_path.rstrip(os.sep) + ".zip"

    # 1. Create report
    with open(report_file, "w", encoding="utf-8") as report:
        report.write(f"Folder report for: {folder_path}\n")
        report.write("=" * 60 + "\n\n")

        for root, dirs, files in os.walk(folder_path):
            for name in files:
                file_path = os.path.join(root, name)

                try:
                    size = os.path.getsize(file_path)
                    mtime = os.path.getmtime(file_path)
                    modified = datetime.fromtimestamp(mtime)

                    report.write(
                        f"File: {file_path}\n"
                        f"Size: {size} bytes\n"
                        f"Modified: {modified}\n\n"
                    )
                except Exception as e:
                    report.write(f"Could not read {file_path}: {e}\n\n")

    # 2. Zip folder (including the report)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname)

    # 3. Delete original folder
    shutil.rmtree(folder_path)

    print("Done!")
    print(f"Report created and zipped to: {zip_path}")
    print("Original folder deleted.")

# ---- RUN HERE ----
if __name__ == "__main__":
    folder = input("Enter full path to folder: ").strip()
    folder_report_and_zip(folder)
