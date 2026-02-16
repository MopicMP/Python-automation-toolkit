#!/usr/bin/env python3
"""
Example: Send a daily HTML report via email.

Set these environment variables (or create a .env file):
    EMAIL_ADDRESS=you@gmail.com
    EMAIL_PASSWORD=your_app_password
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))

from email_sender import send_html_email


def daily_report():
    html = """
    <h2>Daily Automation Report</h2>
    <p>Here is your daily summary:</p>
    <table border="1" cellpadding="8" cellspacing="0">
        <tr style="background: #2F5496; color: white;">
            <th>Task</th><th>Status</th><th>Duration</th>
        </tr>
        <tr><td>File backup</td><td>OK</td><td>2m 15s</td></tr>
        <tr><td>Price check</td><td>OK</td><td>45s</td></tr>
        <tr><td>Folder cleanup</td><td>OK</td><td>12s</td></tr>
    </table>
    <p>All tasks completed successfully.</p>
    """

    send_html_email(
        to="recipient@example.com",
        subject="Daily Automation Report",
        html_body=html,
        plain_fallback="Daily report: all tasks OK.",
    )


if __name__ == "__main__":
    daily_report()

