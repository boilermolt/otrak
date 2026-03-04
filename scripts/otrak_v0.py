#!/usr/bin/env python3
"""
OTRAK v0 — minimal allocation engine

Reads staging CSVs from data/templates/ and produces a draft assignment CSV.
Focus: qualifications (hard filter) + fairness + preferences.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Dict, List, Any

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "templates"
OUT = ROOT / "data" / "outputs"

# ---------- Helpers ----------

def read_csv(path: Path) -> List[Dict[str, Any]]:
    """Read a CSV into list of dicts (strings)."""
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def parse_quals(s: str) -> set[str]:
    """Parse qual string like "basic_rp|class7_shipper" into a set."""
    if not s:
        return set()
    return {q.strip() for q in s.split("|") if q.strip()}


def score_worker(worker: Dict[str, Any], avail: Dict[str, Any], shift: Dict[str, Any], ot: Dict[str, Any]) -> tuple[float, List[str]]:
    """
    Score a worker for a shift and return (score, reasons).
    Reasons are human-readable explanations for auditability.
    """
    score = 100.0
    reasons = []

    # Fairness — weight down high OT totals
    ot30 = float(ot.get("ot_hours_last_30") or 0)
    otlife = float(ot.get("ot_hours_lifetime") or 0)
    score -= 1.5 * ot30
    score -= 0.1 * otlife
    if ot30:
        reasons.append(f"- OT30 ({ot30}h)")
    if otlife:
        reasons.append(f"- OT life ({otlife}h)")

    # Preferences
    pref_shift = (avail.get("preferred_shift") or "").strip()
    if pref_shift and pref_shift != "Any":
        if pref_shift == (shift.get("shift_type") or ""):
            score += 10
            reasons.append("+ preferred shift")
        else:
            score -= 20
            reasons.append("- shift preference mismatch")

    pref_area = (avail.get("preferred_area") or "").strip()
    if pref_area and pref_area == (shift.get("area") or ""):
        score += 5
        reasons.append("+ preferred area")

    normal_area = (worker.get("normal_area") or "").strip()
    if normal_area and normal_area == (shift.get("area") or ""):
        score += 10
        reasons.append("+ normal area match")

    return score, reasons


# ---------- Main allocation ----------

def main() -> None:
    # Load input tables
    workers = read_csv(DATA / "workers.csv")
    availability = read_csv(DATA / "availability.csv")
    work_orders = read_csv(DATA / "work_orders.csv")
    ot_totals = read_csv(DATA / "ot_totals.csv") if (DATA / "ot_totals.csv").exists() else []

    # Indexes for quick lookup
    avail_by_worker = {a["worker_id"]: a for a in availability}
    ot_by_worker = {o["worker_id"]: o for o in ot_totals}

    # Expand work orders into shifts (one row per headcount)
    shifts: List[Dict[str, Any]] = []
    for wo in work_orders:
        headcount = int(wo.get("headcount") or 1)
        for _ in range(headcount):
            shifts.append(wo.copy())

    # Sort shifts by critical path then priority
    def shift_key(s: Dict[str, Any]) -> tuple:
        critical = (s.get("critical_path") or "N").upper() == "Y"
        priority = int(s.get("priority") or 5)
        # critical first (True -> 0), then lower priority number
        return (0 if critical else 1, priority)

    shifts.sort(key=shift_key)

    assignments = []
    used_workers = set()

    for shift in shifts:
        # Required qualifications for this shift
        required_quals = parse_quals(shift.get("required_quals") or "")

        candidates = []
        for w in workers:
            wid = w["worker_id"]

            # Availability hard filter
            avail = avail_by_worker.get(wid)
            if not avail or (avail.get("available") or "N").upper() != "Y":
                continue

            # Qualification hard filter
            w_quals = parse_quals(w.get("quals") or "")
            if required_quals and not required_quals.issubset(w_quals):
                continue

            # Score candidate
            ot = ot_by_worker.get(wid, {})
            score, reasons = score_worker(w, avail, shift, ot)
            candidates.append((score, reasons, w, avail))

        # Rank candidates by score (desc)
        candidates.sort(key=lambda x: x[0], reverse=True)

        # Pick top candidate not already used (simple one-shift-per-worker rule for v0)
        chosen = None
        for score, reasons, w, avail in candidates:
            if w["worker_id"] in used_workers:
                continue
            chosen = (score, reasons, w, avail)
            break

        if chosen:
            score, reasons, w, avail = chosen
            used_workers.add(w["worker_id"])
            assignments.append({
                "work_order_id": shift.get("work_order_id"),
                "title": shift.get("title"),
                "area": shift.get("area"),
                "shift_type": shift.get("shift_type"),
                "worker_id": w.get("worker_id"),
                "name": w.get("name"),
                "score": round(score, 2),
                "reasons": "; ".join(reasons),
                "override": "N",
                "override_reason": "",
            })
        else:
            # No eligible candidate found
            assignments.append({
                "work_order_id": shift.get("work_order_id"),
                "title": shift.get("title"),
                "area": shift.get("area"),
                "shift_type": shift.get("shift_type"),
                "worker_id": "",
                "name": "",
                "score": "",
                "reasons": "NO ELIGIBLE CANDIDATE",
                "override": "",
                "override_reason": "",
            })

    # Write output
    OUT.mkdir(parents=True, exist_ok=True)
    out_path = OUT / "draft_assignments.csv"
    with out_path.open("w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "work_order_id",
            "title",
            "area",
            "shift_type",
            "worker_id",
            "name",
            "score",
            "reasons",
            "override",
            "override_reason",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(assignments)

    print(f"Wrote draft assignments to: {out_path}")


if __name__ == "__main__":
    main()
