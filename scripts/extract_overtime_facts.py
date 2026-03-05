#!/usr/bin/env python3
"""
Extract proposed overtime facts from agreement chunks.

This is a deterministic/heuristic pass intended to create a review queue,
not final legal logic. Output facts should be human-reviewed before compile.

Usage:
  python3 scripts/extract_overtime_facts.py
  python3 scripts/extract_overtime_facts.py --trade IBEW --limit 200
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHUNK_DIR = ROOT / "data" / "agreements" / "epsca" / "chunks"
OUT_PATH = ROOT / "data" / "contract_facts" / "overtime_facts.jsonl"

RE_WEEKLY = re.compile(r"(?:after|in excess of)\s+(\d{1,2})\s+hours?\s+(?:per|a)\s+week", re.IGNORECASE)
RE_DAILY = re.compile(r"(?:after|in excess of)\s+(\d{1,2})\s+hours?\s+(?:in|per|a)\s+day", re.IGNORECASE)
RE_MULT = re.compile(r"(\d(?:\.\d+)?)\s*(?:x|times?)", re.IGNORECASE)


def normalize_text(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def infer_union(file_name: str) -> str:
    base = file_name.replace(".pdf", "")
    return base.split("-")[0].split("_")[0].strip()


def time_and_phrase_to_mult(text: str) -> float | None:
    t = text.lower()
    if "time and one-half" in t or "time-and-one-half" in t or "time and a half" in t:
        return 1.5
    if "double time" in t or "double-time" in t:
        return 2.0
    m = RE_MULT.search(text)
    if m:
        try:
            v = float(m.group(1))
            # guardrail: likely overtime multipliers are typically between 1.25x and 3x
            if 1.0 < v <= 3.0:
                return v
        except ValueError:
            return None
    return None


def load_chunks(trade_filter: str | None = None, agreement_filter: str | None = None):
    for path in CHUNK_DIR.glob("*.jsonl"):
        name_l = path.name.lower()
        if trade_filter and trade_filter.lower() not in name_l:
            continue
        if agreement_filter and agreement_filter.lower() not in name_l:
            continue
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    yield json.loads(line)


def build_fact(chunk: dict, topic: str, value, unit: str | None, conditions: dict, confidence: float) -> dict:
    fid = f"{chunk['id']}::{topic}::{abs(hash((str(value), json.dumps(conditions, sort_keys=True)))) % 10_000_000}"
    return {
        "fact_id": fid,
        "agreement_id": chunk["file"],
        "union": infer_union(chunk["file"]),
        "topic": topic,
        "conditions": conditions,
        "value": value,
        "unit": unit,
        "citation": {
            "source": chunk["source"],
            "file": chunk["file"],
            "page": chunk["page"],
            "chunk_id": chunk["id"],
            "quote": normalize_text(chunk["text"])[:500],
        },
        "confidence": confidence,
        "status": "proposed",
        "extracted_at": datetime.now(timezone.utc).isoformat(),
    }


def extract_from_chunk(chunk: dict) -> list[dict]:
    text = chunk.get("text", "")
    text_l = text.lower()
    out: list[dict] = []

    # only inspect likely overtime chunks
    overtime_keywords = ["overtime", "premium", "time and one-half", "double time", "hours per week", "hours per day"]
    if not any(k in text_l for k in overtime_keywords):
        return out

    # Weekly threshold facts (e.g., after 40 hours per week)
    for m in RE_WEEKLY.finditer(text):
        hours = int(m.group(1))
        out.append(build_fact(
            chunk,
            topic="weekly_overtime_threshold",
            value=hours,
            unit="hours",
            conditions={"scope": "week"},
            confidence=0.88,
        ))

    # Daily threshold facts (e.g., after 10 hours in a day)
    for m in RE_DAILY.finditer(text):
        hours = int(m.group(1))
        out.append(build_fact(
            chunk,
            topic="daily_overtime_threshold",
            value=hours,
            unit="hours",
            conditions={"scope": "day"},
            confidence=0.88,
        ))

    # Overtime multiplier (1.5x / 2.0x / time-and-a-half)
    mult = time_and_phrase_to_mult(text)
    if mult is not None and ("overtime" in text_l or "premium" in text_l):
        out.append(build_fact(
            chunk,
            topic="overtime_rate_multiplier",
            value=mult,
            unit="x",
            conditions={"trigger": "overtime"},
            confidence=0.78,
        ))

    return out


def dedupe_facts(facts: list[dict]) -> list[dict]:
    seen = set()
    out = []
    for f in facts:
        key = (
            f["agreement_id"],
            f["topic"],
            json.dumps(f["conditions"], sort_keys=True),
            str(f["value"]),
            f["citation"]["page"],
        )
        if key in seen:
            continue
        seen.add(key)
        out.append(f)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--trade", help="Optional union/trade filter")
    ap.add_argument("--agreement", help="Optional agreement filter")
    ap.add_argument("--limit", type=int, default=0, help="Optional max facts (0 = no limit)")
    ap.add_argument("--out", default=str(OUT_PATH), help="Output JSONL path")
    args = ap.parse_args()

    facts = []
    for c in load_chunks(args.trade, args.agreement):
        facts.extend(extract_from_chunk(c))

    facts = dedupe_facts(facts)
    if args.limit > 0:
        facts = facts[: args.limit]

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for row in facts:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"Wrote {len(facts)} proposed facts -> {out_path}")


if __name__ == "__main__":
    main()
