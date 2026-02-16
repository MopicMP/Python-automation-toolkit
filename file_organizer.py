#!/usr/bin/env python3
"""
File Organizer
==============
Automatically sort files in any folder into category subfolders
based on file extension.

Categories: Images, Documents, Videos, Music, Archives, Programs, Code

Usage:
    python file_organizer.py                  # Organize ~/Downloads
    python file_organizer.py /path/to/folder  # Organize a specific folder
    python file_organizer.py --dry-run        # Preview without moving files

Learn more: https://raccoonette.gumroad.com/l/Python-for-automating-every-day-tasks
"""

from pathlib import Path
import shutil
import sys

# ---------------------------------------------------------------------------
# Configuration: map category names to lists of file extensions
# Add or remove extensions to match your needs
# ---------------------------------------------------------------------------

FILE_CATEGORIES = {
    "Images": [
        ".jpg", ".jpeg", ".png", ".gif", ".bmp",
        ".svg", ".webp", ".ico", ".tiff",
    ],
    "Documents": [
        ".pdf", ".doc", ".docx", ".txt", ".rtf",
        ".odt", ".xls", ".xlsx", ".ppt", ".pptx",
    ],
    "Videos": [
        ".mp4", ".avi", ".mkv", ".mov", ".wmv",
        ".flv", ".webm",
    ],
    "Music": [
        ".mp3", ".wav", ".flac", ".aac",
        ".ogg", ".wma", ".m4a",
    ],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
    "Programs": [".exe", ".msi", ".dmg", ".pkg", ".deb", ".rpm"],
    "Code": [
        ".py", ".js", ".html", ".css", ".java",
        ".cpp", ".c", ".h", ".json", ".xml",
    ],
}


def get_category(file_extension: str) -> str:
    """Return the category name for a given file extension, or 'Other'."""
    ext = file_extension.lower()
    for category, extensions in FILE_CATEGORIES.items():
        if ext in extensions:
            return category
    return "Other"


def get_unique_filename(path: Path) -> Path:
    """
    If *path* already exists, append _1, _2, ... until a free name is found.

    Example: report.pdf -> report_1.pdf -> report_2.pdf
    """
    if not path.exists():
        return path

    stem = path.stem
    suffix = path.suffix
    parent = path.parent

    counter = 1
    while True:
        new_path = parent / f"{stem}_{counter}{suffix}"
        if not new_path.exists():
            return new_path
        counter += 1
        if counter > 1000:
            raise ValueError(f"Could not find unique name for {path}")


def organize_folder(folder_path: str = None, dry_run: bool = False) -> dict:
    """
    Move every file in *folder_path* into a subfolder named after its category.

    Parameters
    ----------
    folder_path : str or None
        Directory to organize.  Defaults to ``~/Downloads``.
    dry_run : bool
        If True, only print what *would* happen without touching files.

    Returns
    -------
    dict
        ``{category: [filename, ...]}`` summary.
    """
    if folder_path is None:
        folder_path = Path.home() / "Downloads"
    else:
        folder_path = Path(folder_path)

    if not folder_path.exists() or not folder_path.is_dir():
        print(f"Error: {folder_path} is not a valid directory")
        return {}

    print(f"Organizing: {folder_path}")
    print(f"Dry run: {dry_run}")
    print("-" * 50)

    organized = {}
    errors = []

    for item in sorted(folder_path.iterdir()):
        if item.is_dir() or item.name.startswith("."):
            continue

        category = get_category(item.suffix)
        category_folder = folder_path / category
        destination = category_folder / item.name

        organized.setdefault(category, []).append(item.name)
        print(f"  {item.name} -> {category}/")

        if not dry_run:
            try:
                category_folder.mkdir(exist_ok=True)
                if destination.exists():
                    destination = get_unique_filename(destination)
                shutil.move(str(item), str(destination))
            except Exception as e:
                errors.append(f"{item.name}: {e}")
                print(f"    ERROR: {e}")

    # Summary
    print("-" * 50)
    total = sum(len(v) for v in organized.values())
    for cat, files in sorted(organized.items()):
        print(f"  {cat}: {len(files)} files")
    print(f"\nTotal: {total} files")
    if errors:
        print(f"Errors: {len(errors)}")
    return organized


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    dry_run = "--dry-run" in sys.argv or "-d" in sys.argv

    custom_path = None
    for arg in sys.argv[1:]:
        if not arg.startswith("-"):
            custom_path = arg
            break

    if "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__)
        return

    organize_folder(folder_path=custom_path, dry_run=dry_run)


if __name__ == "__main__":
    main()
