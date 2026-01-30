import os
import zipfile
import shutil
from datetime import datetime
import tkinter as tk
from tkinter import filedialog

def format_size(size_bytes):
    """Convert bytes to KB / MB / GB"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / (1024 ** 2):.2f} MB"
    else:
        return f"{size_bytes / (1024 ** 3):.2f} GB"

def folder_report_and_zip(folder_path):
    report_file = os.path.join(folder_path, "folder_report.txt")
    zip_path = folder_path.rstrip(os.sep) + ".zip"

    print("\n📄 Creating folder report...")

    total_files = 0

    with open(report_file, "w", encoding="utf-8") as report:
        report.write(f"Folder report for: {folder_path}\n")
        report.write("=" * 60 + "\n\n")

        for root, dirs, files in os.walk(folder_path):
            for name in files:
                total_files += 1
                file_path = os.path.join(root, name)

                try:
                    size = os.path.getsize(file_path)
                    mtime = os.path.getmtime(file_path)
                    modified = datetime.fromtimestamp(mtime)

                    report.write(
                        f"File: {file_path}\n"
                        f"Size: {format_size(size)}\n"
                        f"Modified: {modified}\n\n"
                    )

                    print(f"  ✔ Logged: {name}")

                except Exception as e:
                    report.write(f"Could not read {file_path}: {e}\n\n")

    print(f"\n📦 Zipping {total_files} files...")

    zipped_files = 0
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname)
                zipped_files += 1

                print(f"  🧵 Zipped ({zipped_files}/{total_files}): {file}")

    print("\n🗑️ Deleting original folder...")
    shutil.rmtree(folder_path)

    print("\n✅ DONE!")
    print(f"📁 ZIP created: {zip_path}")
    print("❌ Original folder deleted")

def select_folder_gui():
    root = tk.Tk()
    root.withdraw()  # Hide main window

    folder_selected = filedialog.askdirectory(
        title="Select folder to report, zip, and delete"
    )

    if folder_selected:
        print(f"📂 Selected folder: {folder_selected}")
        folder_report_and_zip(folder_selected)
    else:
        print("❌ No folder selected. Exiting.")

# ---- RUN ----
if __name__ == "__main__":
    select_folder_gui()
