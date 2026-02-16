#!/usr/bin/env python3
"""
Example: Schedule multiple automation tasks to run on a timer.

Combines: TaskScheduler, BackupSystem, PriceTracker
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))

from task_scheduler import TaskScheduler
from datetime import datetime


def log_time():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Heartbeat - scheduler is alive")


def cleanup_temp():
    """Example: delete .tmp files older than 7 days from a folder."""
    from pathlib import Path
    import time

    folder = Path.home() / "Downloads"
    cutoff = time.time() - 7 * 86400
    removed = 0

    for f in folder.glob("*.tmp"):
        if f.stat().st_mtime < cutoff:
            f.unlink()
            removed += 1

    print(f"Cleaned up {removed} temp files")


def main():
    sched = TaskScheduler()

    sched.add_task("heartbeat", log_time, "every 60 seconds")
    sched.add_task("cleanup", cleanup_temp, "every 6 hours")

    print("Scheduler running. Ctrl+C to stop.")
    sched.run()


if __name__ == "__main__":
    main()
