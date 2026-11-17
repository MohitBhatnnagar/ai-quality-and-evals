"""Retrievers: BM25, TF-IDF cosine, and hybrid via reciprocal rank fusion.

Each retriever indexes a list of (doc_id, text) and returns ranked doc ids.
Chunk-level indexes can use ids like "policy.txt#3"; use `doc_of` to roll up.
"""
from __future__ import annotations

import math
from collections import Counter
from typing import Protocol

from .text import tokenize


class Retriever(Protocol):
    def search(self, query: str, k: int = 10) -> list[str]: ...


def doc_of(chunk_id: str) -> str:
    return chunk_id.split("#", 1)[0]


class BM25:
    def __init__(self, corpus: list[tuple[str, str]], k1: float = 1.5, b: float = 0.75):
        self.ids = [i for i, _ in corpus]
        self.tf = [Counter(tokenize(t)) for _, t in corpus]
        self.len = [sum(c.values()) for c in self.tf]
        self.avg = (sum(self.len) / len(self.len)) if self.len else 0.0
        self.k1, self.b = k1, b
        df: Counter = Counter()
        for c in self.tf:
            df.update(c.keys())
        n = len(corpus)
        # +1 inside the log keeps idf non-negative for very common terms
        self.idf = {t: math.log(1 + (n - d + 0.5) / (d + 0.5)) for t, d in df.items()}

    def scores(self, query: str) -> list[float]:
        q = tokenize(query)
        out = []
        for tf, ln in zip(self.tf, self.len):
            s = 0.0
            for t in q:
                f = tf.get(t, 0)
                if f:
                    s += self.idf[t] * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * ln / (self.avg or 1)))
            out.append(s)
        return out

    def search(self, query: str, k: int = 10) -> list[str]:
        return _top(self.ids, self.scores(query), k)


class TfIdf:
    def __init__(self, corpus: list[tuple[str, str]]):
        self.ids = [i for i, _ in corpus]
        docs = [Counter(tokenize(t)) for _, t in corpus]
        df: Counter = Counter()
        for c in docs:
            df.update(c.keys())
        n = len(docs)
        self.idf = {t: math.log((1 + n) / (1 + d)) + 1 for t, d in df.items()}
        self.vecs = [self._vec(c) for c in docs]

    def _vec(self, counts: Counter) -> dict[str, float]:
        v = {t: (1 + math.log(f)) * self.idf.get(t, 0.0) for t, f in counts.items() if t in self.idf}
        norm = math.sqrt(sum(x * x for x in v.values())) or 1.0
        return {t: x / norm for t, x in v.items()}

    def search(self, query: str, k: int = 10) -> list[str]:
        q = self._vec(Counter(tokenize(query)))
        scores = [sum(w * v.get(t, 0.0) for t, w in q.items()) for v in self.vecs]
        return _top(self.ids, scores, k)


class Hybrid:
    """Reciprocal rank fusion (Cormack et al., 2009): score = sum 1 / (c + rank)."""

    def __init__(self, parts: list[Retriever], c: int = 60, depth: int = 50):
        self.parts, self.c, self.depth = parts, c, depth

    def search(self, query: str, k: int = 10) -> list[str]:
        fused: Counter = Counter()
        for p in self.parts:
            for rank, doc in enumerate(p.search(query, self.depth), start=1):
                fused[doc] += 1.0 / (self.c + rank)
        return [d for d, _ in sorted(fused.items(), key=lambda x: (-x[1], x[0]))[:k]]


def _top(ids: list[str], scores: list[float], k: int) -> list[str]:
    # stable tie-break on id so results are reproducible; drop zero-score docs
    ranked = sorted(zip(ids, scores), key=lambda x: (-x[1], x[0]))
    return [i for i, s in ranked[:k] if s > 0]
