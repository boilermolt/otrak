from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import List

import numpy as np
from flask import Flask, render_template, request, make_response, send_file
from sentence_transformers import SentenceTransformer

EMB_DIR = Path("/media/boilerrat/Bobby/otrak-embeddings")
EMB_PATH = EMB_DIR / "epsca_embeddings.npy"
META_PATH = EMB_DIR / "epsca_metadata.jsonl"
MODEL_NAME = "BAAI/bge-base-en-v1.5"

app = Flask(__name__)

# In-memory chat history keyed by session id
CHAT_HISTORY = {}
MAX_HISTORY = 10
MAX_TOPK = 20

# Overtime outputs stored in memory by session
OT_OUTPUTS = {}

# Load once at startup
embeddings = np.load(EMB_PATH)
meta = []
with META_PATH.open("r", encoding="utf-8") as f:
    for line in f:
        if line.strip():
            meta.append(json.loads(line))

model = SentenceTransformer(MODEL_NAME)


def filter_indices(trade: str | None, agreement: str | None) -> list[int]:
    if not trade and not agreement:
        return list(range(len(meta)))

    idx = []
    for i, m in enumerate(meta):
        fname = m["file"].lower()
        if trade and trade.lower() not in fname:
            continue
        if agreement and agreement.lower() not in fname:
            continue
        idx.append(i)
    return idx


def read_csv_upload(file_storage):
    import csv
    from io import StringIO

    data = file_storage.read().decode("utf-8", errors="ignore")
    file_storage.seek(0)
    return list(csv.DictReader(StringIO(data)))


def validate_headers(rows, required):
    if not rows:
        return ["file is empty"]
    headers = set(rows[0].keys())
    missing = [h for h in required if h not in headers]
    return missing


def run_allocator(workers, availability, work_orders, ot_totals=None):
    # Build lookups
    avail_by_worker = {a["worker_id"]: a for a in availability}
    ot_by_worker = {o["worker_id"]: o for o in (ot_totals or [])}

    def parse_quals(s: str):
        if not s:
            return set()
        return {q.strip() for q in s.split("|") if q.strip()}

    # Expand work orders into shifts
    shifts = []
    for wo in work_orders:
        headcount = int(wo.get("headcount") or 1)
        for _ in range(headcount):
            shifts.append(wo.copy())

    def shift_key(s):
        critical = (s.get("critical_path") or "N").upper() == "Y"
        priority = int(s.get("priority") or 5)
        return (0 if critical else 1, priority)

    shifts.sort(key=shift_key)

    def score_worker(worker, avail, shift, ot):
        score = 100.0
        reasons = []
        ot30 = float(ot.get("ot_hours_last_30") or 0)
        otlife = float(ot.get("ot_hours_lifetime") or 0)
        score -= 1.5 * ot30
        score -= 0.1 * otlife
        if ot30:
            reasons.append(f"- OT30 ({ot30}h)")
        if otlife:
            reasons.append(f"- OT life ({otlife}h)")

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

    assignments = []
    used_workers = set()

    for shift in shifts:
        required_quals = parse_quals(shift.get("required_quals") or "")
        candidates = []
        for w in workers:
            wid = w["worker_id"]
            avail = avail_by_worker.get(wid)
            if not avail or (avail.get("available") or "N").upper() != "Y":
                continue
            w_quals = parse_quals(w.get("quals") or "")
            if required_quals and not required_quals.issubset(w_quals):
                continue
            ot = ot_by_worker.get(wid, {})
            score, reasons = score_worker(w, avail, shift, ot)
            candidates.append((score, reasons, w, avail))

        candidates.sort(key=lambda x: x[0], reverse=True)
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

    return assignments


@app.route("/", methods=["GET", "POST"])
def index():
    # session id (cookie)
    sid = request.cookies.get("sid")
    if not sid:
        sid = str(uuid.uuid4())

    history = CHAT_HISTORY.get(sid, [])
    results = []
    q = ""
    trade = ""
    agreement = ""
    top_k = 5

    if request.method == "POST":
        if request.form.get("clear"):
            CHAT_HISTORY[sid] = []
            history = []
        else:
            q = request.form.get("q", "").strip()
            trade = request.form.get("trade", "").strip()
            agreement = request.form.get("agreement", "").strip()
            try:
                top_k = int(request.form.get("top_k", "5"))
            except ValueError:
                top_k = 5
            top_k = max(1, min(MAX_TOPK, top_k))

            if q:
                keep_idx = filter_indices(trade or None, agreement or None)
                emb = embeddings[keep_idx]
                q_emb = model.encode([q], normalize_embeddings=True)[0]
                scores = emb @ q_emb
                top = np.argsort(-scores)[:top_k]
                for j in top:
                    i = keep_idx[j]
                    m = meta[i]
                    results.append({
                        "source": m["source"],
                        "score": float(scores[j]),
                        "text": m["text"],
                    })

                history.append({
                    "q": q,
                    "results": results,
                })
                history = history[-MAX_HISTORY:]
                CHAT_HISTORY[sid] = history

    resp = make_response(render_template(
        "index.html",
        q=q,
        trade=trade,
        agreement=agreement,
        top_k=top_k,
        results=results,
        history=history,
        max_topk=MAX_TOPK,
    ))
    resp.set_cookie("sid", sid)
    return resp


@app.route("/overtime", methods=["GET", "POST"])
def overtime():
    sid = request.cookies.get("sid")
    if not sid:
        sid = str(uuid.uuid4())

    errors = []
    summary = None

    if request.method == "POST":
        workers_file = request.files.get("workers")
        availability_file = request.files.get("availability")
        work_orders_file = request.files.get("work_orders")
        ot_totals_file = request.files.get("ot_totals")

        if not workers_file or not availability_file or not work_orders_file:
            errors.append("workers.csv, availability.csv, and work_orders.csv are required")
        else:
            workers = read_csv_upload(workers_file)
            availability = read_csv_upload(availability_file)
            work_orders = read_csv_upload(work_orders_file)
            ot_totals = read_csv_upload(ot_totals_file) if ot_totals_file and ot_totals_file.filename else None

            # Validate headers
            missing = validate_headers(workers, ["worker_id", "name", "quals", "normal_area"])
            if missing:
                errors.append(f"workers.csv missing columns: {', '.join(missing)}")
            missing = validate_headers(availability, ["worker_id", "available", "preferred_shift", "preferred_area"])
            if missing:
                errors.append(f"availability.csv missing columns: {', '.join(missing)}")
            missing = validate_headers(work_orders, ["work_order_id", "title", "area", "critical_path", "priority", "shift_type", "required_quals", "headcount"])
            if missing:
                errors.append(f"work_orders.csv missing columns: {', '.join(missing)}")

            if not errors:
                assignments = run_allocator(workers, availability, work_orders, ot_totals)

                # Build CSV output
                import csv
                from io import StringIO, BytesIO

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
                buf = StringIO()
                writer = csv.DictWriter(buf, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(assignments)

                OT_OUTPUTS[sid] = buf.getvalue().encode("utf-8")
                summary = {
                    "total": len(assignments),
                    "unfilled": sum(1 for a in assignments if a.get("worker_id") == ""),
                }

    resp = make_response(render_template("overtime.html", errors=errors, summary=summary))
    resp.set_cookie("sid", sid)
    return resp


@app.route("/overtime/download")
def overtime_download():
    sid = request.cookies.get("sid")
    if not sid or sid not in OT_OUTPUTS:
        return ("No output available", 404)

    data = OT_OUTPUTS[sid]
    from io import BytesIO
    return send_file(BytesIO(data), mimetype="text/csv", as_attachment=True, download_name="draft_assignments.csv")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
