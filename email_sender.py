#!/usr/bin/env python3
"""
Email Sender
============
Send plain-text, HTML, and attachment emails through any SMTP server.

Supports Gmail, Outlook, Yahoo, and custom SMTP.

Usage:
    python email_sender.py             # Interactive mode
    python email_sender.py --help      # Show help

Environment variables or .env file:
    EMAIL_ADDRESS=you@gmail.com
    EMAIL_PASSWORD=your_app_password
    SMTP_SERVER=smtp.gmail.com
    SMTP_PORT=587

Learn more: https://raccoonette.gumroad.com/l/Python-for-automating-every-day-tasks
"""

import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path


# ---------------------------------------------------------------------------
# SMTP presets
# ---------------------------------------------------------------------------

SMTP_PRESETS = {
    "gmail":   {"server": "smtp.gmail.com",       "port": 587},
    "outlook": {"server": "smtp-mail.outlook.com", "port": 587},
    "yahoo":   {"server": "smtp.mail.yahoo.com",  "port": 587},
}


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------

def send_plain_email(
    to: str,
    subject: str,
    body: str,
    sender: str = None,
    password: str = None,
    smtp_server: str = None,
    smtp_port: int = None,
):
    """Send a simple plain-text email."""
    sender = sender or os.environ.get("EMAIL_ADDRESS", "")
    password = password or os.environ.get("EMAIL_PASSWORD", "")
    smtp_server = smtp_server or os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = smtp_port or int(os.environ.get("SMTP_PORT", "587"))

    msg = MIMEText(body, "plain")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to

    _send(msg, sender, password, smtp_server, smtp_port)
    print(f"Sent plain email to {to}")


def send_html_email(
    to: str,
    subject: str,
    html_body: str,
    plain_fallback: str = "",
    sender: str = None,
    password: str = None,
    smtp_server: str = None,
    smtp_port: int = None,
):
    """Send an HTML email with a plain-text fallback."""
    sender = sender or os.environ.get("EMAIL_ADDRESS", "")
    password = password or os.environ.get("EMAIL_PASSWORD", "")
    smtp_server = smtp_server or os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = smtp_port or int(os.environ.get("SMTP_PORT", "587"))

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to

    if plain_fallback:
        msg.attach(MIMEText(plain_fallback, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    _send(msg, sender, password, smtp_server, smtp_port)
    print(f"Sent HTML email to {to}")


def send_email_with_attachments(
    to: str,
    subject: str,
    body: str,
    attachments: list,
    sender: str = None,
    password: str = None,
    smtp_server: str = None,
    smtp_port: int = None,
):
    """Send an email with one or more file attachments."""
    sender = sender or os.environ.get("EMAIL_ADDRESS", "")
    password = password or os.environ.get("EMAIL_PASSWORD", "")
    smtp_server = smtp_server or os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = smtp_port or int(os.environ.get("SMTP_PORT", "587"))

    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to
    msg.attach(MIMEText(body, "plain"))

    for file_path in attachments:
        path = Path(file_path)
        if not path.exists():
            print(f"  Warning: attachment not found: {path}")
            continue

        with open(path, "rb") as fh:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(fh.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f'attachment; filename="{path.name}"')
        msg.attach(part)
        print(f"  Attached: {path.name}")

    _send(msg, sender, password, smtp_server, smtp_port)
    print(f"Sent email with {len(attachments)} attachment(s) to {to}")


# ---------------------------------------------------------------------------
# Internal
# ---------------------------------------------------------------------------

def _send(msg, sender, password, server, port):
    with smtplib.SMTP(server, port) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(sender, password)
        smtp.send_message(msg)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    if "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__)
        return

    # Load .env if present
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip().strip("\"'"))

    print("Email Sender")
    print("=" * 50)
    to = input("To: ").strip()
    subject = input("Subject: ").strip()
    body = input("Body: ").strip()
    attach = input("Attachments (comma-separated paths, or blank): ").strip()

    attachments = [a.strip() for a in attach.split(",") if a.strip()] if attach else []

    if attachments:
        send_email_with_attachments(to, subject, body, attachments)
    else:
        send_plain_email(to, subject, body)


if __name__ == "__main__":
    main()
