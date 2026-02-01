import os
import zipfile
import shutil
import hashlib
import csv
from datetime import datetime
import tkinter as tk
from tkinter import filedialog

def file_md5(file_path, chunk_size=8192):
    """Compute MD5 checksum of a file (chunked for large files)."""
    h = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None

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

def folder_report_and_zip(folder_path, delete_after=True, compression_level=6):
    report_file_txt = os.path.join(folder_path, "folder_report.txt")
    report_file_csv = os.path.join(folder_path, "folder_report.csv")
    zip_path = folder_path.rstrip(os.sep) + ".zip"

    print(f"\n📄 Creating folder report (with MD5, duplicate check)...")
    print(f"🗜️ Compression level: {compression_level} (0=none, 9=max)")

    total_files = 0
    file_entries = []   # (path, size, mtime, md5 or None)
    md5_to_paths = {}   # md5 -> [paths] for duplicate detection

    for root, dirs, files in os.walk(folder_path):
        for name in files:
            total_files += 1
            file_path = os.path.join(root, name)

            try:
                size = os.path.getsize(file_path)
                mtime = os.path.getmtime(file_path)
                modified = datetime.fromtimestamp(mtime)
                md5 = file_md5(file_path)

                file_entries.append((file_path, size, modified, md5, None))
                if md5 is not None:
                    md5_to_paths.setdefault(md5, []).append(file_path)

                print(f"  ✔ Logged: {name}")

            except Exception as e:
                file_entries.append((file_path, None, None, None, str(e)))
                print(f"  ⚠ Skip (error): {name}")

    # Remove duplicate files (keep first copy per MD5)
    paths_to_delete = set()
    duplicates = {md5: paths for md5, paths in md5_to_paths.items() if len(paths) > 1}
    for md5, paths in duplicates.items():
        kept, removed = paths[0], paths[1:]
        paths_to_delete.update(removed)
        for p in removed:
            try:
                os.remove(p)
                print(f"  🗑 Removed duplicate: {os.path.basename(p)}")
            except Exception as e:
                print(f"  ⚠ Could not remove {p}: {e}")

    # Generate TXT report
    with open(report_file_txt, "w", encoding="utf-8") as report:
        report.write(f"Folder report for: {folder_path}\n")
        report.write("=" * 60 + "\n\n")

        for entry in file_entries:
            file_path, size, modified, md5, err = entry
            if file_path in paths_to_delete:
                continue
            if err is not None:
                report.write(f"Could not read {file_path}: {err}\n\n")
            else:
                report.write(
                    f"File: {file_path}\n"
                    f"Size: {format_size(size)}\n"
                    f"Modified: {modified}\n"
                    f"MD5: {md5 if md5 else '(unable to compute)'}\n\n"
                )

        # Duplicates section (kept vs removed)
        if duplicates:
            report.write("=" * 60 + "\n")
            report.write("DUPLICATES (same MD5) — kept 1 copy, removed rest\n")
            report.write("=" * 60 + "\n\n")
            for md5, paths in duplicates.items():
                kept, removed = paths[0], paths[1:]
                report.write(f"MD5: {md5}\n")
                report.write(f"  Kept:   {kept}\n")
                for p in removed:
                    report.write(f"  Removed: {p}\n")
                report.write("\n")
        else:
            report.write("=" * 60 + "\n")
            report.write("No duplicate files (by MD5) found.\n")

    # Generate CSV report
    with open(report_file_csv, "w", encoding="utf-8", newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        
        # Write header
        csv_writer.writerow([
            "File Path", 
            "File Name", 
            "Size (Bytes)", 
            "Size (Formatted)", 
            "Modified Date", 
            "MD5 Checksum", 
            "Status",
            "Error"
        ])
        
        # Write file entries
        for entry in file_entries:
            file_path, size, modified, md5, err = entry
            status = "Removed (Duplicate)" if file_path in paths_to_delete else "Kept"
            
            csv_writer.writerow([
                file_path,
                os.path.basename(file_path),
                size if size is not None else "",
                format_size(size) if size is not None else "",
                modified.strftime("%Y-%m-%d %H:%M:%S") if modified else "",
                md5 if md5 else "",
                status,
                err if err else ""
            ])
        
        # Write duplicates summary section
        if duplicates:
            csv_writer.writerow([])  # Empty row
            csv_writer.writerow(["DUPLICATE FILES SUMMARY"])
            csv_writer.writerow(["MD5 Checksum", "Status", "File Path"])
            
            for md5, paths in duplicates.items():
                kept, removed = paths[0], paths[1:]
                csv_writer.writerow([md5, "Kept", kept])
                for p in removed:
                    csv_writer.writerow([md5, "Removed", p])

    print(f"  📄 TXT report saved: folder_report.txt")
    print(f"  📊 CSV report saved: folder_report.csv")

    total_files -= len(paths_to_delete)
    print(f"\n📦 Zipping {total_files} files...")

    zipped_files = 0
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=compression_level) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname)
                zipped_files += 1

                print(f"  🧵 Zipped ({zipped_files}/{total_files}): {file}")

    if delete_after:
        print("\n🗑️ Deleting original folder...")
        shutil.rmtree(folder_path)
        print("❌ Original folder deleted")
    else:
        print("\n📂 Original folder kept (not deleted).")

    print("\n✅ DONE!")
    print(f"📁 ZIP created: {zip_path}")

def select_folder_gui():
    root = tk.Tk()
    root.title("Folder Zipper")
    root.resizable(False, False)

    keep_folder_var = tk.BooleanVar(value=False)
    compression_var = tk.IntVar(value=6)

    def on_select():
        folder_selected = filedialog.askdirectory(
            title="Select folder to report and zip"
        )
        if folder_selected:
            root.destroy()
            print(f"📂 Selected folder: {folder_selected}")
            folder_report_and_zip(
                folder_selected, 
                delete_after=not keep_folder_var.get(),
                compression_level=compression_var.get()
            )
        else:
            print("❌ No folder selected. Exiting.")
            root.destroy()

    frame = tk.Frame(root, padx=20, pady=20)
    frame.pack()

    tk.Checkbutton(
        frame,
        text="Keep original folder (don't delete after zipping)",
        variable=keep_folder_var,
        anchor="w",
    ).pack(fill="x", pady=(0, 10))

    # Compression level selector
    compression_frame = tk.Frame(frame)
    compression_frame.pack(fill="x", pady=(0, 15))
    
    tk.Label(
        compression_frame,
        text="Compression level:",
        anchor="w"
    ).pack(side="left", padx=(0, 10))
    
    compression_scale = tk.Scale(
        compression_frame,
        from_=0,
        to=9,
        orient="horizontal",
        variable=compression_var,
        length=200
    )
    compression_scale.pack(side="left")
    
    tk.Label(
        compression_frame,
        text="(0=none, 9=max)",
        fg="gray"
    ).pack(side="left", padx=(10, 0))

    tk.Button(frame, text="Select folder", command=on_select, width=20).pack()

    root.mainloop()

# ---- RUN ----
if __name__ == "__main__":
    select_folder_gui()
