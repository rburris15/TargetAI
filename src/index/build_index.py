import os
import json
import glob
from typing import List, Dict, Any

import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

INDEX_DIR = os.getenv("INDEX_DIR", "./data/index")
CLEAN_DIR = os.getenv("CLEAN_DIR", "./data/clean")
EMBED_MODEL = os.getenv("EMBEDDING_MODEL", "pritamdeka/S-Biomed-Roberta-snli-multinli-stsb")

os.makedirs(INDEX_DIR, exist_ok=True)


def load_clean() -> List[Dict[str, Any]]:
    docs: List[Dict[str, Any]] = []
    for fp in glob.glob(os.path.join(CLEAN_DIR, "*.jsonl")):
        with open(fp, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    docs.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return docs


def to_chunks(rec: Dict[str, Any]) -> List[Dict[str, Any]]:
    text_fields = [
        rec.get("title", ""),
        rec.get("text", ""),
        " ".join(rec.get("condition", [])),
    ]
    text = " \n".join([t for t in text_fields if t])
    if not text.strip():
        return []
    return [{
        "doc": rec,
        "text": text.strip(),
        "meta": {
            "source": rec.get("source"),
            "title": rec.get("title"),
            "date": rec.get("last_update") or rec.get("date") or rec.get("start_date"),
            "url": rec.get("url"),
        }
    }]


def build():
    print(f"Loading docs from {CLEAN_DIR}...")
    records = load_clean()
    print(f"Loaded {len(records)} records")

    print(f"Loading embedding model: {EMBED_MODEL}")
    model = SentenceTransformer(EMBED_MODEL)

    chunks: List[Dict[str, Any]] = []
    for r in records:
        chunks.extend(to_chunks(r))

    texts = [c["text"] for c in chunks]
    metas = [c["meta"] for c in chunks]

    print("Encoding...")
    embs = model.encode(texts, batch_size=32, show_progress_bar=True, normalize_embeddings=True)
    embs = np.asarray(embs).astype('float32')

    d = embs.shape[1]
    index = faiss.IndexFlatIP(d)
    index.add(embs)

    faiss.write_index(index, os.path.join(INDEX_DIR, "faiss.index"))
    with open(os.path.join(INDEX_DIR, "metas.json"), 'w', encoding='utf-8') as f:
        json.dump(metas, f, ensure_ascii=False, indent=2)

    print(f"Index built with {len(texts)} chunks")

if __name__ == "__main__":
    build()
