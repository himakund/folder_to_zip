import os
import zipfile
import shutil
from datetime import datetime

def folder_report_and_zip(folder_path, delete_after=True):
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

    # 3. Delete original folder (optional)
    if delete_after:
        shutil.rmtree(folder_path)
        print("Original folder deleted.")
    else:
        print("Original folder kept (not deleted).")

    print("Done!")
    print(f"Report created and zipped to: {zip_path}")

# ---- RUN HERE ----
if __name__ == "__main__":
    folder = input("Enter full path to folder: ").strip()
    delete_prompt = input("Delete original folder after zipping? (y/n) [y]: ").strip().lower()
    delete_after = delete_prompt != "n" and delete_prompt != "no"
    folder_report_and_zip(folder, delete_after=delete_after)
