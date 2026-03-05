#!/usr/bin/env python3
"""
Basic keyword search over EPSCA agreement chunks.

Usage:
  python3 scripts/search_agreements.py --q "overtime" --limit 5
  python3 scripts/search_agreements.py --q "overtime" --trade "IBEW"
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHUNK_DIR = ROOT / "data" / "agreements" / "epsca" / "chunks"


def load_chunks(trade_filter: str | None = None):
    for path in CHUNK_DIR.glob("*.jsonl"):
        fname = path.name.lower()
        if trade_filter and trade_filter.lower() not in fname:
            continue
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    yield json.loads(line)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--q", required=True, help="Search query (keyword match)")
    ap.add_argument("--limit", type=int, default=5, help="Max results")
    ap.add_argument("--trade", help="Optional trade filter (e.g., IBEW)")
    args = ap.parse_args()

    q = args.q.lower()
    results = []

    for c in load_chunks(args.trade):
        text = c["text"].lower()
        if q in text:
            # simple score: count occurrences
            score = text.count(q)
            results.append((score, c))

    results.sort(key=lambda x: x[0], reverse=True)

    for score, c in results[: args.limit]:
        print("=" * 80)
        print(f"{c['source']}  (score={score})")
        print(c["text"][:1200])
        print()


if __name__ == "__main__":
    main()
