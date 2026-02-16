#!/usr/bin/env python3
"""
Auto-Organizer
==============
Watches a folder (default: ~/Downloads) and automatically sorts new
files into category subfolders the moment they appear.

Waits 3 seconds after the last write to ensure downloads are complete
before moving the file.

Usage:
    python auto_organizer.py                   # Watch ~/Downloads
    python auto_organizer.py /path/to/folder   # Watch a custom folder

Press Ctrl+C to stop.

Learn more: https://raccoonette.gumroad.com/l/Python-for-automating-every-day-tasks
"""

import time
import sys
import shutil
from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ---------------------------------------------------------------------------
# Category definitions (same as file_organizer.py)
# ---------------------------------------------------------------------------

FILE_CATEGORIES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"],
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".xls", ".xlsx", ".ppt", ".pptx"],
    "Videos": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm"],
    "Music": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Programs": [".exe", ".msi", ".dmg", ".pkg"],
}


class DownloadOrganizer(FileSystemEventHandler):
    """Move new files to category subfolders after they finish downloading."""

    # Extensions that indicate an incomplete download
    TEMP_EXTENSIONS = {".tmp", ".part", ".crdownload", ".partial"}

    def __init__(self, downloads_folder):
        super().__init__()
        self.downloads_folder = Path(downloads_folder)
        self.pending = {}  # path -> last_modified_time

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def get_category(extension: str) -> str:
        ext = extension.lower()
        for category, extensions in FILE_CATEGORIES.items():
            if ext in extensions:
                return category
        return "Other"

    def organize_file(self, file_path: str):
        path = Path(file_path)
        if not path.exists() or not path.is_file():
            return
        if path.suffix.lower() in self.TEMP_EXTENSIONS or path.name.startswith("."):
            return

        category = self.get_category(path.suffix)
        dest_dir = self.downloads_folder / category
        dest_dir.mkdir(exist_ok=True)

        destination = dest_dir / path.name
        counter = 1
        while destination.exists():
            destination = dest_dir / f"{path.stem}_{counter}{path.suffix}"
            counter += 1

        try:
            shutil.move(str(path), str(destination))
            print(f"Organized: {path.name} -> {category}/")
        except Exception as exc:
            print(f"Error: {path.name}: {exc}")

    # ------------------------------------------------------------------
    # Watchdog callbacks
    # ------------------------------------------------------------------

    def on_created(self, event):
        if event.is_directory:
            return
        print(f"New file detected: {Path(event.src_path).name}")
        self.pending[event.src_path] = time.time()

    def on_modified(self, event):
        if event.is_directory:
            return
        if event.src_path in self.pending:
            self.pending[event.src_path] = time.time()

    # ------------------------------------------------------------------
    # Periodic check
    # ------------------------------------------------------------------

    def process_pending(self, settle_seconds: float = 3.0):
        """Move files that haven't been modified for *settle_seconds*."""
        now = time.time()
        ready = [p for p, t in self.pending.items() if now - t > settle_seconds]
        for path in ready:
            del self.pending[path]
            self.organize_file(path)


def auto_organize(folder: str = None):
    if folder is None:
        folder = str(Path.home() / "Downloads")

    folder = Path(folder)
    print(f"Auto-organizing: {folder}")
    print("New files will be sorted automatically.")
    print("Press Ctrl+C to stop")
    print("-" * 50)

    handler = DownloadOrganizer(folder)
    observer = Observer()
    observer.schedule(handler, str(folder), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
            handler.process_pending()
    except KeyboardInterrupt:
        print("\nStopping...")
        observer.stop()

    observer.join()
    print("Auto-organizer stopped.")


def main():
    if "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__)
        return
    folder = sys.argv[1] if len(sys.argv) > 1 else None
    auto_organize(folder)


if __name__ == "__main__":
    main()

