#!/usr/bin/env python3
"""
Full Pipeline Example
=====================
Combines multiple tools into a single automated workflow:

1. Organize the Downloads folder
2. Back up important documents
3. Check tracked product prices
4. Generate an Excel report
5. (Optional) Email the report

This demonstrates how the toolkit tools compose together.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))

from pathlib import Path
from datetime import datetime

from file_organizer import organize_folder
from backup_system import BackupSystem
from spreadsheet_manager import SpreadsheetManager


def run_pipeline():
    print("=" * 60)
    print("  Automation Pipeline")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    results = {}

    # Step 1: Organize Downloads (dry run for safety)
    print("\n--- Step 1: Organize Downloads (dry run) ---")
    organized = organize_folder(dry_run=True)
    results["files_organized"] = sum(len(v) for v in (organized or {}).values())

    # Step 2: Incremental backup of Documents
    print("\n--- Step 2: Backup Documents ---")
    docs = Path.home() / "Documents"
    backup_dest = Path.home() / "Backups"

    if docs.exists():
        backup = BackupSystem(str(backup_dest))
        stats = backup.backup_folder(
            str(docs),
            incremental=True,
            exclude_patterns=["*.tmp", "~$*"],
        )
        results["files_backed_up"] = stats["files_backed_up"]
    else:
        print("  Documents folder not found, skipping.")
        results["files_backed_up"] = 0

    # Step 3: Generate summary report
    print("\n--- Step 3: Generate Report ---")
    mgr = SpreadsheetManager("pipeline_report.xlsx")
    mgr.create_sheet(
        "Summary",
        headers=["Metric", "Value"],
        data=[
            ["Date", datetime.now().strftime("%Y-%m-%d")],
            ["Files organized", results["files_organized"]],
            ["Files backed up", results["files_backed_up"]],
        ],
    )
    mgr.auto_fit_columns()

    if "Sheet" in mgr.workbook.sheetnames and len(mgr.workbook.sheetnames) > 1:
        del mgr.workbook["Sheet"]

    mgr.save()

    print("\n" + "=" * 60)
    print("  Pipeline complete!")
    print(f"  Files organized: {results['files_organized']}")
    print(f"  Files backed up: {results['files_backed_up']}")
    print(f"  Report: pipeline_report.xlsx")
    print("=" * 60)


if __name__ == "__main__":
    run_pipeline()
