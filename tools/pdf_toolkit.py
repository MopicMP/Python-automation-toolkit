#!/usr/bin/env python3
"""
PDF Toolkit
===========
Merge, split, extract text, and search inside PDF files.

Requires: PyPDF2

Usage:
    python pdf_toolkit.py merge a.pdf b.pdf -o combined.pdf
    python pdf_toolkit.py split doc.pdf --pages 1-5
    python pdf_toolkit.py text doc.pdf
    python pdf_toolkit.py search doc.pdf "keyword"

Learn more: https://raccoonette.gumroad.com/l/Python-for-automating-every-day-tasks
"""

import sys
from pathlib import Path

from PyPDF2 import PdfReader, PdfWriter


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------

def merge_pdfs(input_files: list, output_file: str = "merged.pdf"):
    """Merge multiple PDFs into one."""
    writer = PdfWriter()

    for pdf_path in input_files:
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            writer.add_page(page)
        print(f"  Added: {pdf_path} ({len(reader.pages)} pages)")

    with open(output_file, "wb") as fh:
        writer.write(fh)

    total = len(writer.pages)
    print(f"Merged {len(input_files)} files -> {output_file} ({total} pages)")


def split_pdf(input_file: str, pages: str = None, output_dir: str = None):
    """
    Split a PDF into individual pages or a page range.

    Parameters
    ----------
    pages : str
        Range like "1-5" or "3" or "1,3,5". None = split every page.
    output_dir : str
        Directory for output files.
    """
    reader = PdfReader(input_file)
    total = len(reader.pages)
    stem = Path(input_file).stem

    output_dir = Path(output_dir or ".")
    output_dir.mkdir(parents=True, exist_ok=True)

    if pages:
        indices = _parse_page_range(pages, total)
    else:
        indices = list(range(total))

    for idx in indices:
        writer = PdfWriter()
        writer.add_page(reader.pages[idx])
        out_path = output_dir / f"{stem}_page_{idx + 1}.pdf"
        with open(out_path, "wb") as fh:
            writer.write(fh)
        print(f"  Created: {out_path}")

    print(f"Split {len(indices)} pages from {input_file}")


def extract_text(input_file: str, output_file: str = None) -> str:
    """Extract all text from a PDF. Optionally save to a file."""
    reader = PdfReader(input_file)
    all_text = []

    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        all_text.append(f"--- Page {i + 1} ---\n{text}")

    result = "\n\n".join(all_text)

    if output_file:
        Path(output_file).write_text(result, encoding="utf-8")
        print(f"Text saved to: {output_file}")
    else:
        print(result)

    return result


def search_pdf(input_file: str, keyword: str):
    """Search for a keyword in every page of a PDF."""
    reader = PdfReader(input_file)
    keyword_lower = keyword.lower()
    found = 0

    for i, page in enumerate(reader.pages):
        text = (page.extract_text() or "").lower()
        if keyword_lower in text:
            found += 1
            # Show context around the match
            idx = text.find(keyword_lower)
            start = max(0, idx - 60)
            end = min(len(text), idx + len(keyword) + 60)
            snippet = text[start:end].replace("\n", " ")
            print(f"  Page {i + 1}: ...{snippet}...")

    print(f"\nFound '{keyword}' on {found} page(s) out of {len(reader.pages)}")


def get_info(input_file: str):
    """Print metadata and page count for a PDF."""
    reader = PdfReader(input_file)
    meta = reader.metadata

    print(f"File:    {input_file}")
    print(f"Pages:   {len(reader.pages)}")
    if meta:
        print(f"Title:   {meta.title or 'N/A'}")
        print(f"Author:  {meta.author or 'N/A'}")
        print(f"Creator: {meta.creator or 'N/A'}")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_page_range(spec: str, total: int) -> list:
    """Parse '1-5', '3', or '1,3,5' into zero-based indices."""
    indices = []
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-", 1)
            a, b = int(a) - 1, int(b) - 1
            indices.extend(range(max(0, a), min(total, b + 1)))
        else:
            idx = int(part) - 1
            if 0 <= idx < total:
                indices.append(idx)
    return sorted(set(indices))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2 or "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__)
        return

    cmd = sys.argv[1].lower()

    if cmd == "merge":
        files = [a for a in sys.argv[2:] if not a.startswith("-") and a != "-o"]
        out = "merged.pdf"
        if "-o" in sys.argv:
            idx = sys.argv.index("-o")
            if idx + 1 < len(sys.argv):
                out = sys.argv[idx + 1]
                files = [f for f in files if f != out]
        merge_pdfs(files, out)

    elif cmd == "split":
        if len(sys.argv) < 3:
            print("Usage: pdf_toolkit.py split <file> [--pages 1-5]")
            return
        inp = sys.argv[2]
        pages = None
        if "--pages" in sys.argv:
            idx = sys.argv.index("--pages")
            if idx + 1 < len(sys.argv):
                pages = sys.argv[idx + 1]
        split_pdf(inp, pages=pages)

    elif cmd == "text":
        if len(sys.argv) < 3:
            print("Usage: pdf_toolkit.py text <file> [-o output.txt]")
            return
        out = None
        if "-o" in sys.argv:
            idx = sys.argv.index("-o")
            if idx + 1 < len(sys.argv):
                out = sys.argv[idx + 1]
        extract_text(sys.argv[2], out)

    elif cmd == "search":
        if len(sys.argv) < 4:
            print('Usage: pdf_toolkit.py search <file> "keyword"')
            return
        search_pdf(sys.argv[2], sys.argv[3])

    elif cmd == "info":
        if len(sys.argv) < 3:
            print("Usage: pdf_toolkit.py info <file>")
            return
        get_info(sys.argv[2])

    else:
        print(f"Unknown command: {cmd}")
        print("Available: merge, split, text, search, info")


if __name__ == "__main__":
    main()
