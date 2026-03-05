#!/usr/bin/env python3
"""
EPSCA agreement ingestion pipeline (v0)

- Converts PDFs to text using pdftotext
- Splits text into chunks by simple section/page boundaries
- Emits JSONL chunks with citations (file + page)

Requires: `pdftotext` binary (poppler-utils)
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "data" / "agreements" / "epsca"
TEXT_DIR = SRC_DIR / "text"
CHUNK_DIR = SRC_DIR / "chunks"
INDEX_PATH = SRC_DIR / "agreements_index.json"

PAGE_BREAK = "\f"  # form-feed used by pdftotext


def run_pdftotext(pdf_path: Path, out_txt: Path) -> None:
    """Convert PDF to text with page breaks preserved."""
    out_txt.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["pdftotext", "-layout", str(pdf_path), str(out_txt)]
    subprocess.run(cmd, check=True)


def split_pages(text: str) -> list[str]:
    """Split text into pages using form-feed characters."""
    pages = text.split(PAGE_BREAK)
    return [p.strip() for p in pages]


def chunk_page(page_text: str, page_num: int, file_name: str) -> list[dict]:
    """
    Chunk a page into smaller pieces.
    Heuristic: split on double newlines and keep ~800-1200 chars per chunk.
    """
    blocks = [b.strip() for b in re.split(r"\n\s*\n", page_text) if b.strip()]
    chunks = []
    buf = ""
    for b in blocks:
        if len(buf) + len(b) < 1000:
            buf = f"{buf}\n\n{b}".strip()
        else:
            if buf:
                chunks.append(buf)
            buf = b
    if buf:
        chunks.append(buf)

    out = []
    for i, c in enumerate(chunks, 1):
        out.append({
            "id": f"{file_name}::p{page_num}::c{i}",
            "file": file_name,
            "page": page_num,
            "text": c,
            "source": f"{file_name} p.{page_num}",
        })
    return out


def main() -> None:
    pdfs = sorted([p for p in SRC_DIR.glob("*.pdf")])
    if not pdfs:
        raise SystemExit(f"No PDFs found in {SRC_DIR}")

    TEXT_DIR.mkdir(parents=True, exist_ok=True)
    CHUNK_DIR.mkdir(parents=True, exist_ok=True)

    all_chunks = []
    index = []

    for pdf in pdfs:
        txt = TEXT_DIR / (pdf.stem + ".txt")
        print(f"Converting: {pdf.name}")
        run_pdftotext(pdf, txt)

        text = txt.read_text(encoding="utf-8", errors="ignore")
        pages = split_pages(text)

        file_chunks = []
        for i, page in enumerate(pages, 1):
            if not page.strip():
                continue
            file_chunks.extend(chunk_page(page, i, pdf.name))

        # write per-file chunks
        chunk_path = CHUNK_DIR / (pdf.stem + ".jsonl")
        with chunk_path.open("w", encoding="utf-8") as f:
            for c in file_chunks:
                f.write(json.dumps(c, ensure_ascii=False) + "\n")

        all_chunks.extend(file_chunks)
        index.append({
            "file": pdf.name,
            "pages": len(pages),
            "text_path": str(txt.relative_to(ROOT)),
            "chunks_path": str(chunk_path.relative_to(ROOT)),
        })

    INDEX_PATH.write_text(json.dumps(index, indent=2), encoding="utf-8")
    print(f"Wrote index: {INDEX_PATH}")
    print(f"Total chunks: {len(all_chunks)}")


if __name__ == "__main__":
    main()
