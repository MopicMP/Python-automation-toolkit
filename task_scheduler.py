#!/usr/bin/env python3
"""
Task Scheduler
==============
Schedule and run recurring Python tasks with error handling,
retry logic, and persistent configuration.

Requires: schedule

Usage:
    python task_scheduler.py             # Run demo scheduler
    python task_scheduler.py --help      # Show help

Learn more: https://raccoonette.gumroad.com/l/Python-for-automating-every-day-tasks
"""

import sys
import json
import time
import logging
import threading
from pathlib import Path
from datetime import datetime

import schedule


logger = logging.getLogger("task_scheduler")


class TaskScheduler:
    """
    Manage recurring tasks with retry, logging, and JSON config.

    Example
    -------
    >>> sched = TaskScheduler()
    >>> sched.add_task("greet", lambda: print("Hello!"), "every 10 seconds")
    >>> sched.run()
    """

    def __init__(self, config_file: str = "scheduler_config.json"):
        self.config_file = Path(config_file)
        self.tasks = {}
        self.stats = {}
        self._stop_event = threading.Event()

    # ------------------------------------------------------------------
    # Task management
    # ------------------------------------------------------------------

    def add_task(
        self,
        name: str,
        func,
        interval: str,
        max_retries: int = 3,
        retry_delay: float = 5.0,
    ):
        """
        Register a task.

        Parameters
        ----------
        name : str
            Unique task name.
        func : callable
            The function to run.
        interval : str
            Human-readable schedule, e.g. "every 30 seconds", "every 5 minutes",
            "every 1 hour", "daily at 09:00".
        max_retries : int
            Retry count on failure.
        retry_delay : float
            Seconds between retries.
        """
        self.tasks[name] = {
            "func": func,
            "interval": interval,
            "max_retries": max_retries,
            "retry_delay": retry_delay,
        }
        self.stats[name] = {"runs": 0, "successes": 0, "failures": 0, "last_run": None}
        self._schedule_task(name)
        logger.info("Registered task: %s (%s)", name, interval)

    def remove_task(self, name: str):
        if name in self.tasks:
            del self.tasks[name]
            schedule.clear(name)
            logger.info("Removed task: %s", name)

    # ------------------------------------------------------------------
    # Scheduling logic
    # ------------------------------------------------------------------

    def _schedule_task(self, name: str):
        info = self.tasks[name]
        interval = info["interval"].lower()

        job = None
        if "second" in interval:
            n = self._extract_number(interval, 10)
            job = schedule.every(n).seconds
        elif "minute" in interval:
            n = self._extract_number(interval, 1)
            job = schedule.every(n).minutes
        elif "hour" in interval:
            n = self._extract_number(interval, 1)
            job = schedule.every(n).hours
        elif "daily" in interval or "day" in interval:
            import re
            m = re.search(r"(\d{1,2}:\d{2})", interval)
            if m:
                job = schedule.every().day.at(m.group(1))
            else:
                job = schedule.every().day
        else:
            job = schedule.every(60).seconds

        job.do(self._run_task, name).tag(name)

    def _run_task(self, name: str):
        info = self.tasks.get(name)
        if not info:
            return

        self.stats[name]["runs"] += 1
        self.stats[name]["last_run"] = datetime.now().isoformat()

        for attempt in range(1, info["max_retries"] + 1):
            try:
                info["func"]()
                self.stats[name]["successes"] += 1
                logger.info("[%s] OK (attempt %d)", name, attempt)
                return
            except Exception as exc:
                logger.warning("[%s] attempt %d failed: %s", name, attempt, exc)
                if attempt < info["max_retries"]:
                    time.sleep(info["retry_delay"])

        self.stats[name]["failures"] += 1
        logger.error("[%s] All %d attempts failed", name, info["max_retries"])

    @staticmethod
    def _extract_number(text: str, default: int) -> int:
        import re
        m = re.search(r"(\d+)", text)
        return int(m.group(1)) if m else default

    # ------------------------------------------------------------------
    # Run loop
    # ------------------------------------------------------------------

    def run(self):
        """Block and run all scheduled tasks until Ctrl+C."""
        print(f"Scheduler running with {len(self.tasks)} task(s). Ctrl+C to stop.")
        try:
            while not self._stop_event.is_set():
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nScheduler stopped.")

    def stop(self):
        self._stop_event.set()

    def print_stats(self):
        print("Task Statistics:")
        print("-" * 60)
        for name, s in self.stats.items():
            print(
                f"  {name}: {s['runs']} runs, "
                f"{s['successes']} ok, {s['failures']} failed, "
                f"last: {s['last_run'] or 'never'}"
            )


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def demo():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    sched = TaskScheduler()

    def say_hello():
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Hello from scheduled task!")

    def check_disk():
        import shutil
        usage = shutil.disk_usage("/")
        free_gb = usage.free / (1024 ** 3)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Free disk: {free_gb:.1f} GB")

    sched.add_task("hello", say_hello, "every 10 seconds")
    sched.add_task("disk_check", check_disk, "every 30 seconds")

    print("Demo scheduler started. Two tasks: 'hello' (10s) and 'disk_check' (30s)")
    sched.run()


def main():
    if "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__)
        return
    demo()


if __name__ == "__main__":
    main()
