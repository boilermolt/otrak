#!/usr/bin/env python3
"""
Semantic search over EPSCA agreements using local embeddings.

Requires:
  - Bobby venv: /media/boilerrat/Bobby/otrak-venv
  - Embeddings: /media/boilerrat/Bobby/otrak-embeddings

Usage:
  /media/boilerrat/Bobby/otrak-venv/bin/python scripts/search_embeddings.py --q "overtime premium" --limit 5
  /media/boilerrat/Bobby/otrak-venv/bin/python scripts/search_embeddings.py --q "rest period" --trade "IBEW"
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

EMB_DIR = Path("/media/boilerrat/Bobby/otrak-embeddings")
EMB_PATH = EMB_DIR / "epsca_embeddings.npy"
META_PATH = EMB_DIR / "epsca_metadata.jsonl"
MODEL_NAME = "BAAI/bge-base-en-v1.5"


def load_metadata():
    meta = []
    with META_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                meta.append(json.loads(line))
    return meta


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--q", required=True)
    ap.add_argument("--limit", type=int, default=5)
    ap.add_argument("--trade", help="Optional trade filter")
    ap.add_argument("--agreement", help="Optional agreement name filter")
    args = ap.parse_args()

    embeddings = np.load(EMB_PATH)
    meta_all = load_metadata()

    # Optional filtering by filename
    keep_idx = list(range(len(meta_all)))
    if args.trade or args.agreement:
        keep_idx = []
        for i, m in enumerate(meta_all):
            fname = m["file"].lower()
            if args.trade and args.trade.lower() not in fname:
                continue
            if args.agreement and args.agreement.lower() not in fname:
                continue
            keep_idx.append(i)
        embeddings = embeddings[keep_idx]

    model = SentenceTransformer(MODEL_NAME)
    q_emb = model.encode([args.q], normalize_embeddings=True)[0]

    scores = embeddings @ q_emb  # cosine similarity if normalized
    top_idx = np.argsort(-scores)[: args.limit]

    for j in top_idx:
        i = keep_idx[j]
        m = meta_all[i]
        print("=" * 80)
        print(f"{m['source']}  (score={scores[j]:.4f})")
        print(m["text"][:1200])
        print()


if __name__ == "__main__":
    main()
