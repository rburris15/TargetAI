import os
import json
from typing import List, Dict, Any

import numpy as np
import faiss
from sentence_transformers import CrossEncoder, SentenceTransformer

INDEX_DIR = os.getenv("INDEX_DIR", "./data/index")
EMBED_MODEL = os.getenv("EMBEDDING_MODEL", "pritamdeka/S-Biomed-Roberta-snli-multinli-stsb")
RERANKER_MODEL = os.getenv("RERANKER_MODEL", "BAAI/bge-reranker-base")


class Retriever:
    def __init__(self, top_k: int = 40, rerank_k: int = 12):
        self.top_k = top_k
        self.rerank_k = rerank_k
        self.embedder = SentenceTransformer(EMBED_MODEL)
        self.reranker = CrossEncoder(RERANKER_MODEL)
        self.index = faiss.read_index(os.path.join(INDEX_DIR, "faiss.index"))
        with open(os.path.join(INDEX_DIR, "metas.json"), 'r', encoding='utf-8') as f:
            self.metas: List[Dict[str, Any]] = json.load(f)

    def search(self, query: str) -> List[Dict[str, Any]]:
        q = self.embedder.encode([query], normalize_embeddings=True)
        q = np.asarray(q).astype('float32')
        D, I = self.index.search(q, self.top_k)
        candidates = [self.metas[i] | {"_score": float(D[0][rank])} for rank, i in enumerate(I[0]) if i != -1]
        # Rerank: use title if present, else url
        pairs = [[query, (self.metas[i].get("title") or self.metas[i].get("url") or "")] for i in I[0] if i != -1]
        scores = self.reranker.predict(pairs)
        for c, s in zip(candidates, scores):
            c["_rerank"] = float(s)
        candidates.sort(key=lambda x: x.get("_rerank", 0.0), reverse=True)
        return candidates[: self.rerank_k]
