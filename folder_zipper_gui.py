import os
import zipfile
import shutil
import hashlib
import csv
from datetime import datetime
import tkinter as tk
from tkinter import filedialog
import tkinter.ttk as ttk

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

# ---- UI theme (modern light theme)
COLORS = {
    "bg": "#f0f4f8",
    "card": "#ffffff",
    "card_border": "#e2e8f0",
    "accent": "#2563eb",
    "accent_hover": "#1d4ed8",
    "text": "#1e293b",
    "text_muted": "#64748b",
    "success": "#059669",
}
FONTS = {
    "title": ("Segoe UI", 18, "bold"),
    "section": ("Segoe UI", 10, "bold"),
    "body": ("Segoe UI", 10),
    "hint": ("Segoe UI", 9),
}


def select_folder_gui():
    root = tk.Tk()
    root.title("Folder Zipper")
    root.resizable(True, True)
    root.configure(bg=COLORS["bg"])

    # Center window and set size (roomy for button, slider, and padding)
    root.update_idletasks()
    w, h = 520, 340
    x = (root.winfo_screenwidth() // 2) - (w // 2)
    y = (root.winfo_screenheight() // 2) - (h // 2)
    root.geometry(f"{w}x{h}+{x}+{y}")
    root.minsize(460, 300)

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
                compression_level=int(compression_var.get()),
            )
        else:
            print("❌ No folder selected. Exiting.")
            root.destroy()

    # Main container with padding
    main = tk.Frame(root, bg=COLORS["bg"], padx=28, pady=24)
    main.pack(fill="both", expand=True)

    # ---- Header ----
    header = tk.Frame(main, bg=COLORS["bg"])
    header.pack(fill="x", pady=(0, 20))
    tk.Label(
        header,
        text="📦 Folder Zipper",
        font=FONTS["title"],
        fg=COLORS["text"],
        bg=COLORS["bg"],
    ).pack(anchor="w")
    tk.Label(
        header,
        text="Report, deduplicate & zip a folder",
        font=FONTS["hint"],
        fg=COLORS["text_muted"],
        bg=COLORS["bg"],
    ).pack(anchor="w")

    # ---- Options card ----
    card = tk.Frame(main, bg=COLORS["card"], relief="flat", bd=0)
    card.pack(fill="x", pady=(0, 20))
    card_inner = tk.Frame(card, bg=COLORS["card"], padx=20, pady=16)
    card_inner.pack(fill="x")
    # Subtle border effect
    card_border = tk.Frame(card, bg=COLORS["card_border"], height=1)
    card_border.pack(fill="x", side="bottom")

    # Keep folder option
    keep_row = tk.Frame(card_inner, bg=COLORS["card"])
    keep_row.pack(fill="x", pady=(0, 14))
    cb = tk.Checkbutton(
        keep_row,
        text="Keep original folder after zipping",
        variable=keep_folder_var,
        anchor="w",
        font=FONTS["body"],
        fg=COLORS["text"],
        bg=COLORS["card"],
        activebackground=COLORS["card"],
        activeforeground=COLORS["text"],
        selectcolor=COLORS["card"],
        highlightthickness=0,
    )
    cb.pack(side="left")

    # Compression section
    comp_label_row = tk.Frame(card_inner, bg=COLORS["card"])
    comp_label_row.pack(fill="x", pady=(4, 6))
    tk.Label(
        comp_label_row,
        text="Compression level",
        font=FONTS["section"],
        fg=COLORS["text"],
        bg=COLORS["card"],
    ).pack(side="left")
    tk.Label(
        comp_label_row,
        text="0 = none · 9 = max",
        font=FONTS["hint"],
        fg=COLORS["text_muted"],
        bg=COLORS["card"],
    ).pack(side="right")

    comp_scale_frame = tk.Frame(card_inner, bg=COLORS["card"])
    comp_scale_frame.pack(fill="x")
    scale = ttk.Scale(
        comp_scale_frame,
        from_=0,
        to=9,
        orient="horizontal",
        variable=compression_var,
        length=380,
    )
    scale.pack(side="left", fill="x", expand=True, padx=(0, 12))
    comp_value = tk.Label(
        comp_scale_frame,
        text="6",
        font=FONTS["body"],
        fg=COLORS["accent"],
        bg=COLORS["card"],
        width=2,
    )
    comp_value.pack(side="left")

    def update_comp_label(*args):
        try:
            comp_value.config(text=str(int(compression_var.get())))
        except (ValueError, tk.TclError):
            pass

    compression_var.trace_add("write", update_comp_label)

    # ---- Primary button ----
    btn_frame = tk.Frame(main, bg=COLORS["bg"])
    btn_frame.pack(fill="x")
    btn = tk.Button(
        btn_frame,
        text="  Select folder to zip  ",
        command=on_select,
        font=FONTS["body"],
        fg="white",
        bg=COLORS["accent"],
        activeforeground="white",
        activebackground=COLORS["accent_hover"],
        relief="flat",
        bd=0,
        padx=20,
        pady=10,
        cursor="hand2",
    )
    btn.pack()
    btn.bind("<Enter>", lambda e: btn.config(bg=COLORS["accent_hover"]))
    btn.bind("<Leave>", lambda e: btn.config(bg=COLORS["accent"]))

    root.mainloop()

# ---- RUN ----
if __name__ == "__main__":
    select_folder_gui()
