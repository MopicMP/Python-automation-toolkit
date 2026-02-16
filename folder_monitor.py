#!/usr/bin/env python3
"""
Folder Monitor
==============
Watch any directory for real-time file-system events:
created, modified, deleted, and moved/renamed.

Usage:
    python folder_monitor.py                  # Watch current directory
    python folder_monitor.py /path/to/watch   # Watch a specific folder

Press Ctrl+C to stop.

Learn more: https://raccoonette.gumroad.com/l/Python-for-automating-every-day-tasks
"""

import time
import sys
from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class FolderMonitor(FileSystemEventHandler):
    """Print (and optionally callback) every file-system event."""

    def __init__(self, callback=None):
        super().__init__()
        self.callback = callback

    def on_created(self, event):
        kind = "Directory" if event.is_directory else "File"
        print(f"[CREATED] {kind}: {event.src_path}")
        if self.callback and not event.is_directory:
            self.callback("created", event.src_path)

    def on_modified(self, event):
        if event.is_directory:
            return
        print(f"[MODIFIED] File: {event.src_path}")
        if self.callback:
            self.callback("modified", event.src_path)

    def on_deleted(self, event):
        kind = "Directory" if event.is_directory else "File"
        print(f"[DELETED] {kind}: {event.src_path}")
        if self.callback and not event.is_directory:
            self.callback("deleted", event.src_path)

    def on_moved(self, event):
        kind = "Directory" if event.is_directory else "File"
        print(f"[MOVED] {kind}: {event.src_path} -> {event.dest_path}")
        if self.callback and not event.is_directory:
            self.callback("moved", event.src_path, event.dest_path)


def start_monitoring(folder_path, callback=None, recursive=True):
    """Block until Ctrl+C, printing every event in *folder_path*."""
    folder_path = Path(folder_path)
    if not folder_path.is_dir():
        raise FileNotFoundError(f"Not a directory: {folder_path}")

    print(f"Watching: {folder_path}")
    print(f"Recursive: {recursive}")
    print("Press Ctrl+C to stop")
    print("-" * 50)

    handler = FolderMonitor(callback=callback)
    observer = Observer()
    observer.schedule(handler, str(folder_path), recursive=recursive)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping...")
        observer.stop()

    observer.join()
    print("Monitor stopped.")


def main():
    if "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__)
        return

    folder = sys.argv[1] if len(sys.argv) > 1 else str(Path.cwd())
    start_monitoring(folder)


if __name__ == "__main__":
    main()
