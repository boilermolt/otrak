#!/usr/bin/env python3
"""
Keyword / phrase search over EPSCA agreement chunks with simple highlighting.

Usage:
  python3 scripts/search_agreements.py --q "overtime" --limit 5
  python3 scripts/search_agreements.py --q "overtime" --trade "IBEW"
  python3 scripts/search_agreements.py --q ""overtime premium"" --phrase
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHUNK_DIR = ROOT / "data" / "agreements" / "epsca" / "chunks"


def load_chunks(trade_filter: str | None = None, agreement_filter: str | None = None):
    for path in CHUNK_DIR.glob("*.jsonl"):
        fname = path.name.lower()
        if trade_filter and trade_filter.lower() not in fname:
            continue
        if agreement_filter and agreement_filter.lower() not in fname:
            continue
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    yield json.loads(line)


def highlight(text: str, query: str) -> str:
    """Wrap query matches with << >> for visibility."""
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    return pattern.sub(lambda m: f"<<{m.group(0)}>>", text)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--q", required=True, help="Search query")
    ap.add_argument("--limit", type=int, default=5, help="Max results")
    ap.add_argument("--trade", help="Optional trade filter (e.g., IBEW)")
    ap.add_argument("--agreement", help="Optional agreement name filter (partial match)")
    ap.add_argument("--phrase", action="store_true", help="Exact phrase match")
    args = ap.parse_args()

    q = args.q.strip()
    q_l = q.lower()
    results = []

    for c in load_chunks(args.trade, args.agreement):
        text = c["text"]
        text_l = text.lower()

        if args.phrase:
            if q_l not in text_l:
                continue
            score = text_l.count(q_l)
        else:
            # keyword mode: match any word in query
            words = [w for w in re.split(r"\s+", q_l) if w]
            if not words:
                continue
            score = sum(text_l.count(w) for w in words)
            if score == 0:
                continue

        results.append((score, c))

    results.sort(key=lambda x: x[0], reverse=True)

    for score, c in results[: args.limit]:
        print("=" * 80)
        print(f"{c['source']}  (score={score})")
        snippet = highlight(c["text"], q)
        print(snippet[:1200])
        print()


if __name__ == "__main__":
    main()
