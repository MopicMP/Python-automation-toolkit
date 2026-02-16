# Python Automation Toolkit

A collection of ready-to-use Python scripts for automating everyday tasks: file management, web scraping, email, spreadsheets, PDFs, and scheduling.

**No complex setup.** Each tool works standalone. Pick the one you need and run it.

---

## What's Inside

| Tool | Description | Dependencies |
|------|-------------|--------------|
| [File Organizer](tools/file_organizer.py) | Sort files in any folder by type (images, docs, videos...) | None |
| [Folder Monitor](tools/folder_monitor.py) | Watch a folder in real-time, react to changes | `watchdog` |
| [Auto-Organizer](tools/auto_organizer.py) | Auto-sort new downloads the moment they appear | `watchdog` |
| [Backup System](tools/backup_system.py) | Full + incremental backups with hash verification | None |
| [Price Tracker](tools/price_tracker.py) | Monitor product prices across websites, get alerts | `requests`, `beautifulsoup4` |
| [Weather Dashboard](tools/weather_dashboard.py) | Current weather + forecasts for any city (free API) | `requests` |
| [Spreadsheet Manager](tools/spreadsheet_manager.py) | Create, read, update Excel files with charts + styling | `openpyxl` |
| [PDF Toolkit](tools/pdf_toolkit.py) | Merge, split, extract text from PDFs | `PyPDF2` |
| [Email Sender](tools/email_sender.py) | Send plain, HTML, and attachment emails via SMTP | None |
| [Task Scheduler](tools/task_scheduler.py) | Schedule and run recurring Python tasks | `schedule` |

---

## Quick Start

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/python-automation-toolkit.git
cd python-automation-toolkit

# Install dependencies
pip install -r requirements.txt

# Run any tool
python tools/file_organizer.py --dry-run
python tools/weather_dashboard.py
python tools/price_tracker.py
```

---

## Tool Details

### File Organizer

Sorts files into category folders (Images, Documents, Videos, Music, Archives, Code, Programs).

```bash
# Preview what would happen (no files moved)
python tools/file_organizer.py --dry-run

# Organize your Downloads folder
python tools/file_organizer.py

# Organize a custom folder
python tools/file_organizer.py /path/to/messy/folder
```

### Folder Monitor

Watch any folder for file changes in real-time. Detects: created, modified, deleted, moved.

```bash
python tools/folder_monitor.py /path/to/watch
```

### Auto-Organizer

Combines the organizer + monitor. New files are automatically sorted the instant they appear.

```bash
# Watch Downloads and auto-sort
python tools/auto_organizer.py

# Watch a custom folder
python tools/auto_organizer.py /path/to/folder
```

### Backup System

Create full or incremental backups. Detects changed files via MD5 hashing. Tracks history.

```bash
# Incremental backup (only changed files)
python tools/backup_system.py /important/folder /backup/destination

# Full backup
python tools/backup_system.py /important/folder /backup/destination --full

# List available backups
python tools/backup_system.py /any /backup/destination --list

# Verify a backup
python tools/backup_system.py /any /backup/destination --verify 20260215_143022
```

### Price Tracker

Track product prices over time. Stores history in JSON. Exports to CSV.

```bash
python tools/price_tracker.py
# Interactive commands:
#   add "iPhone 16" "https://..." 899.99
#   check-all
#   history iphone_16
#   export iphone_16
```

### Weather Dashboard

Current weather, hourly forecast, 7-day forecast, city comparison. Uses the free Open-Meteo API (no API key needed).

```bash
python tools/weather_dashboard.py
# Interactive commands:
#   current London
#   forecast Tokyo
#   hourly "New York"
#   compare London Paris Berlin
```

### Spreadsheet Manager

Create professional Excel reports with headers, data, charts, and conditional formatting.

```bash
python tools/spreadsheet_manager.py
```

See [examples/spreadsheet_example.py](examples/spreadsheet_example.py) for usage patterns.

### PDF Toolkit

Merge multiple PDFs, split by pages, extract text, search inside PDFs.

```bash
python tools/pdf_toolkit.py merge file1.pdf file2.pdf -o combined.pdf
python tools/pdf_toolkit.py split document.pdf --pages 1-5
python tools/pdf_toolkit.py text document.pdf
python tools/pdf_toolkit.py search document.pdf "keyword"
```

### Email Sender

Send emails with HTML content and attachments via any SMTP server (Gmail, Outlook, etc.).

```bash
python tools/email_sender.py
```

See [examples/email_example.py](examples/email_example.py) for usage patterns.

### Task Scheduler

Schedule recurring Python tasks with error handling and retry logic.

```bash
python tools/task_scheduler.py
```

See [examples/scheduler_example.py](examples/scheduler_example.py) for usage patterns.

---

## Examples

The `examples/` folder contains working scripts that demonstrate each tool:

- [spreadsheet_example.py](examples/spreadsheet_example.py) - Create a sales report with charts
- [email_example.py](examples/email_example.py) - Send a daily report email
- [scheduler_example.py](examples/scheduler_example.py) - Schedule automated tasks
- [full_pipeline.py](examples/full_pipeline.py) - Combine multiple tools into one workflow

---

## Requirements

- Python 3.8+
- See [requirements.txt](requirements.txt) for dependencies

---

## Learn More

These tools are extracted from the full course **"Python for Automating Everyday Tasks"** which covers:

- Step-by-step explanations of every line of code
- 240+ pages of hands-on tutorials
- File automation, web scraping, APIs, email, spreadsheets, PDFs
- Task scheduling and building complete automation systems
- Real-world projects you can use immediately

**[Get the full course here](https://raccoonette.gumroad.com/l/Python-for-automating-every-day-tasks)**

---

## License

MIT License - see [LICENSE](LICENSE) for details.

Free to use in personal and commercial projects.
