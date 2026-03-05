#!/usr/bin/env python3
"""
Build local embeddings for EPSCA agreement chunks.

- Uses sentence-transformers in the Bobby venv
- Stores embeddings + metadata on Bobby volume
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

import numpy as np
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).resolve().parents[1]
CHUNK_DIR = ROOT / "data" / "agreements" / "epsca" / "chunks"
OUT_DIR = Path("/media/boilerrat/Bobby/otrak-embeddings")
OUT_DIR.mkdir(parents=True, exist_ok=True)

MODEL_NAME = "BAAI/bge-base-en-v1.5"


def load_chunks() -> List[dict]:
    chunks = []
    for path in CHUNK_DIR.glob("*.jsonl"):
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    chunks.append(json.loads(line))
    return chunks


def main() -> None:
    print(f"Loading model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)

    chunks = load_chunks()
    texts = [c["text"] for c in chunks]

    print(f"Encoding {len(texts)} chunks...")
    embeddings = model.encode(texts, batch_size=32, show_progress_bar=True, normalize_embeddings=True)
    embeddings = np.asarray(embeddings, dtype=np.float32)

    # Save embeddings + metadata
    emb_path = OUT_DIR / "epsca_embeddings.npy"
    meta_path = OUT_DIR / "epsca_metadata.jsonl"

    np.save(emb_path, embeddings)
    with meta_path.open("w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps({
                "id": c["id"],
                "file": c["file"],
                "page": c["page"],
                "source": c["source"],
                "text": c["text"],
            }, ensure_ascii=False) + "\n")

    print(f"Saved: {emb_path}")
    print(f"Saved: {meta_path}")


if __name__ == "__main__":
    main()
