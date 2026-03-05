#!/usr/bin/env python3
"""
Compile reviewed contract facts into rules JSON.

Only facts with status=approved are compiled.

Usage:
  python3 scripts/compile_contract_rules.py
  python3 scripts/compile_contract_rules.py --in data/contract_facts/overtime_facts.jsonl --out data/contract_facts/rules.generated.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IN_PATH = ROOT / "data" / "contract_facts" / "overtime_facts.jsonl"
OUT_PATH = ROOT / "data" / "contract_facts" / "rules.generated.json"


def load_facts(path: Path) -> list[dict]:
    rows = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def make_rule(fact: dict) -> dict | None:
    topic = fact.get("topic")
    cond = fact.get("conditions", {})
    value = fact.get("value")
    citation = fact.get("citation", {})
    union = fact.get("union", "UNKNOWN")

    base = {
        "id": f"AGR-{union}-{topic}-{str(fact.get('fact_id', 'x'))[-8:]}".replace(" ", "_"),
        "type": "agreement",
        "condition": {
            "agreement_id": fact.get("agreement_id"),
            "union": union,
            **cond,
        },
        "source": citation.get("source") or fact.get("agreement_id", "agreement"),
        "citation": {
            "file": citation.get("file"),
            "page": citation.get("page"),
            "chunk_id": citation.get("chunk_id"),
        },
    }

    if topic == "overtime_rate_multiplier":
        base["effect"] = {"overtime_multiplier": value}
        return base

    if topic == "weekly_overtime_threshold":
        base["effect"] = {"weekly_threshold_hours": value}
        return base

    if topic == "daily_overtime_threshold":
        base["effect"] = {"daily_threshold_hours": value}
        return base

    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="in_path", default=str(IN_PATH), help="Input facts JSONL")
    ap.add_argument("--out", dest="out_path", default=str(OUT_PATH), help="Output rules JSON")
    args = ap.parse_args()

    in_path = Path(args.in_path)
    out_path = Path(args.out_path)

    facts = [f for f in load_facts(in_path) if f.get("status") == "approved"]
    rules = []
    for f in facts:
        rule = make_rule(f)
        if rule:
            rules.append(rule)

    out = {
        "version": "0.2-contract-generated",
        "rules": rules,
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print(f"Compiled {len(rules)} rules from {len(facts)} approved facts -> {out_path}")


if __name__ == "__main__":
    main()
