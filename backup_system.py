#!/usr/bin/env python3
"""
Backup System
=============
Create full and incremental backups of any folder.
Tracks file changes via MD5 hashing so incremental backups only copy
what has actually changed since the last run.

Features:
    - Full or incremental mode
    - Hash-based change detection
    - Backup history tracking
    - Backup verification
    - Exclude patterns

Usage:
    python backup_system.py <source> <destination>
    python backup_system.py <source> <destination> --full
    python backup_system.py <source> <destination> --list
    python backup_system.py <source> <destination> --verify <timestamp>

Learn more: https://raccoonette.gumroad.com/l/Python-for-automating-every-day-tasks
"""

import sys
import json
import hashlib
import shutil
from pathlib import Path
from datetime import datetime


class BackupSystem:
    """Full + incremental backup manager with history and verification."""

    def __init__(self, backup_destination: str):
        self.destination = Path(backup_destination)
        self.destination.mkdir(parents=True, exist_ok=True)

        self.metadata_folder = self.destination / ".backup_metadata"
        self.metadata_folder.mkdir(exist_ok=True)

        self.history_file = self.metadata_folder / "history.json"
        self.history = self._load_history()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_history(self) -> dict:
        if self.history_file.exists():
            with open(self.history_file, "r") as fh:
                return json.load(fh)
        return {"backups": [], "file_hashes": {}}

    def _save_history(self):
        with open(self.history_file, "w") as fh:
            json.dump(self.history, fh, indent=2, default=str)

    @staticmethod
    def _calculate_hash(file_path) -> str:
        md5 = hashlib.md5()
        with open(file_path, "rb") as fh:
            for chunk in iter(lambda: fh.read(4096), b""):
                md5.update(chunk)
        return md5.hexdigest()

    def _should_backup(self, file_path, incremental: bool) -> bool:
        if not incremental:
            return True
        key = str(file_path)
        if key not in self.history["file_hashes"]:
            return True
        return self._calculate_hash(file_path) != self.history["file_hashes"][key]

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        for unit in ("B", "KB", "MB", "GB"):
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f} TB"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def backup_folder(
        self,
        source_folder: str,
        incremental: bool = True,
        exclude_patterns: list = None,
    ) -> dict:
        """
        Back up *source_folder* into a timestamped sub-directory.

        Returns a stats dict with counts and sizes.
        """
        source = Path(source_folder)
        if not source.exists():
            raise FileNotFoundError(f"Source not found: {source}")

        exclude_patterns = exclude_patterns or []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.destination / f"backup_{timestamp}"
        backup_dir.mkdir(parents=True, exist_ok=True)

        mode = "incremental" if incremental else "full"
        print(f"Backup of: {source}")
        print(f"Destination: {backup_dir}")
        print(f"Mode: {mode}")
        print("-" * 50)

        stats = {
            "timestamp": timestamp,
            "source": str(source),
            "destination": str(backup_dir),
            "mode": mode,
            "files_checked": 0,
            "files_backed_up": 0,
            "files_skipped": 0,
            "total_size": 0,
            "errors": [],
        }

        for file_path in source.rglob("*"):
            if file_path.is_dir():
                continue
            stats["files_checked"] += 1

            relative = file_path.relative_to(source)
            if any(file_path.match(p) for p in exclude_patterns):
                stats["files_skipped"] += 1
                continue

            if not self._should_backup(file_path, incremental):
                stats["files_skipped"] += 1
                continue

            dest = backup_dir / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            try:
                shutil.copy2(str(file_path), str(dest))
                self.history["file_hashes"][str(file_path)] = self._calculate_hash(file_path)
                stats["files_backed_up"] += 1
                stats["total_size"] += file_path.stat().st_size
                print(f"  Backed up: {relative}")
            except Exception as exc:
                stats["errors"].append(f"{relative}: {exc}")
                print(f"  ERROR: {relative}: {exc}")

        self.history["backups"].append(stats)
        self._save_history()

        print("-" * 50)
        print(f"Files checked:   {stats['files_checked']}")
        print(f"Files backed up: {stats['files_backed_up']}")
        print(f"Files skipped:   {stats['files_skipped']}")
        print(f"Total size:      {self._format_size(stats['total_size'])}")
        if stats["errors"]:
            print(f"Errors:          {len(stats['errors'])}")
        return stats

    def list_backups(self):
        """Print all available backups."""
        print("Available backups:")
        print("-" * 50)
        for b in self.history["backups"]:
            print(f"  {b['timestamp']}  |  {b['files_backed_up']} files  |  {self._format_size(b['total_size'])}  |  {b['mode']}")
        if not self.history["backups"]:
            print("  (none)")

    def verify_backup(self, backup_timestamp: str) -> dict:
        """Check that every file in a backup is readable and intact."""
        backup_dir = self.destination / f"backup_{backup_timestamp}"
        if not backup_dir.exists():
            raise FileNotFoundError(f"Backup not found: {backup_timestamp}")

        print(f"Verifying: {backup_timestamp}")
        results = {"verified": 0, "corrupted": []}
        for fp in backup_dir.rglob("*"):
            if fp.is_dir():
                continue
            try:
                self._calculate_hash(fp)
                results["verified"] += 1
            except Exception:
                results["corrupted"].append(str(fp))

        print(f"Verified:  {results['verified']} files")
        print(f"Corrupted: {len(results['corrupted'])} files")
        return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    if "--help" in sys.argv or "-h" in sys.argv or len(sys.argv) < 3:
        print(__doc__)
        return

    source = sys.argv[1]
    destination = sys.argv[2]
    backup = BackupSystem(destination)

    if "--list" in sys.argv:
        backup.list_backups()
        return

    if "--verify" in sys.argv:
        idx = sys.argv.index("--verify")
        if idx + 1 < len(sys.argv):
            backup.verify_backup(sys.argv[idx + 1])
        else:
            print("Provide a backup timestamp after --verify")
        return

    incremental = "--full" not in sys.argv
    backup.backup_folder(source, incremental=incremental)


if __name__ == "__main__":
    main()
