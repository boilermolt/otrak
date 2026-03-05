from __future__ import annotations

import json
from pathlib import Path
from typing import List

import numpy as np
from flask import Flask, render_template, request
from sentence_transformers import SentenceTransformer

EMB_DIR = Path("/media/boilerrat/Bobby/otrak-embeddings")
EMB_PATH = EMB_DIR / "epsca_embeddings.npy"
META_PATH = EMB_DIR / "epsca_metadata.jsonl"
MODEL_NAME = "BAAI/bge-base-en-v1.5"

app = Flask(__name__)

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


@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    q = ""
    trade = ""
    agreement = ""
    top_k = 5
    if request.method == "POST":
        q = request.form.get("q", "").strip()
        trade = request.form.get("trade", "").strip()
        agreement = request.form.get("agreement", "").strip()
        try:
            top_k = int(request.form.get("top_k", "5"))
        except ValueError:
            top_k = 5

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

    return render_template(
        "index.html",
        q=q,
        trade=trade,
        agreement=agreement,
        top_k=top_k,
        results=results,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
