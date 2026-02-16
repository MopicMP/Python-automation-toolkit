#!/usr/bin/env python3
"""
Example: Create a styled sales report with charts.

Demonstrates: SpreadsheetManager creating headers, data,
currency formatting, conditional highlighting, and charts.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))

from spreadsheet_manager import SpreadsheetManager


def create_sales_report():
    mgr = SpreadsheetManager("sales_report.xlsx")

    headers = ["Product", "Q1 Sales", "Q2 Sales", "Q3 Sales", "Q4 Sales", "Total"]
    data = [
        ["Widget A",  15200, 18400, 22100, 19800, 75500],
        ["Widget B",  8900,  9200,  11500, 12800, 42400],
        ["Widget C",  22300, 25100, 28700, 31200, 107300],
        ["Service X", 45000, 48000, 52000, 55000, 200000],
        ["Service Y", 12000, 13500, 14200, 15800, 55500],
    ]

    mgr.create_sheet("Annual Sales", data=data, headers=headers)

    # Format currency columns (2-6)
    for col in range(2, 7):
        mgr.format_column_as_currency(col)

    # Highlight totals above 100k
    mgr.highlight_cells(col=6, threshold=100000, color="92D050")

    mgr.auto_fit_columns()
    mgr.add_bar_chart("Quarterly Revenue", data_col=2, position="H2")

    # Remove default empty sheet
    if "Sheet" in mgr.workbook.sheetnames and len(mgr.workbook.sheetnames) > 1:
        del mgr.workbook["Sheet"]

    mgr.save()
    print("Created: sales_report.xlsx")


if __name__ == "__main__":
    create_sales_report()
