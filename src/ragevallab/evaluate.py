"""Run retrievers over a golden set and produce a comparison report."""
from __future__ import annotations

import json
from pathlib import Path
from statistics import mean

from .metrics import (bootstrap_ci, hit_at_k, ndcg_at_k, paired_bootstrap_diff,
                      recall_at_k, reciprocal_rank)
from .retrievers import BM25, Hybrid, Retriever, TfIdf, doc_of
from .text import chunk_sentences


def load_corpus(directory: str | Path, chunk_words: int = 40) -> list[tuple[str, str]]:
    corpus = []
    for p in sorted(Path(directory).glob("*.txt")):
        for i, c in enumerate(chunk_sentences(p.read_text(encoding="utf-8"), chunk_words)):
            corpus.append((f"{p.name}#{i}", c))
    return corpus


def load_golden(path: str | Path) -> list[dict]:
    """Golden set: [{"question": str, "relevant": ["file.txt", ...]}]"""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def per_query(retriever: Retriever, golden: list[dict], k: int) -> dict[str, list[float]]:
    out: dict[str, list[float]] = {"hit": [], "recall": [], "mrr": [], "ndcg": []}
    for g in golden:
        rel = set(g["relevant"])
        seen: list[str] = []
        for c in retriever.search(g["question"], k * 4):  # roll chunks up to docs, keep order
            d = doc_of(c)
            if d not in seen:
                seen.append(d)
        out["hit"].append(hit_at_k(seen, rel, k))
        out["recall"].append(recall_at_k(seen, rel, k))
        out["mrr"].append(reciprocal_rank(seen, rel))
        out["ndcg"].append(ndcg_at_k(seen, rel, k))
    return out


def compare(corpus: list[tuple[str, str]], golden: list[dict], k: int = 3) -> dict:
    systems: dict[str, Retriever] = {"bm25": BM25(corpus), "tfidf": TfIdf(corpus)}
    systems["hybrid_rrf"] = Hybrid([systems["bm25"], systems["tfidf"]])
    scores = {name: per_query(r, golden, k) for name, r in systems.items()}
    summary = {}
    for name, m in scores.items():
        lo, hi = bootstrap_ci(m["mrr"])
        summary[name] = {"hit@k": mean(m["hit"]), "recall@k": mean(m["recall"]),
                         "mrr": mean(m["mrr"]), "mrr_ci95": (lo, hi), "ndcg@k": mean(m["ndcg"])}
    best, other = "hybrid_rrf", "bm25"
    d, lo, hi = paired_bootstrap_diff(scores[best]["mrr"], scores[other]["mrr"])
    return {"k": k, "queries": len(golden), "summary": summary,
            "paired_mrr": {"a": best, "b": other, "diff": d, "ci95": (lo, hi),
                           "significant": lo > 0 or hi < 0}}


def render(report: dict) -> str:
    lines = [f"Queries: {report['queries']}   k={report['k']}", "",
             f"{'system':<12}{'hit@k':>8}{'recall@k':>10}{'MRR':>8}{'MRR 95% CI':>20}{'nDCG@k':>9}"]
    for n, s in report["summary"].items():
        lo, hi = s["mrr_ci95"]
        lines.append(f"{n:<12}{s['hit@k']:>8.3f}{s['recall@k']:>10.3f}{s['mrr']:>8.3f}"
                     f"{f'[{lo:.3f}, {hi:.3f}]':>20}{s['ndcg@k']:>9.3f}")
    p = report["paired_mrr"]
    verdict = "statistically distinguishable" if p["significant"] else "NOT distinguishable (CI spans 0)"
    lines += ["", f"{p['a']} - {p['b']} MRR diff = {p['diff']:+.3f}  CI95 [{p['ci95'][0]:+.3f}, {p['ci95'][1]:+.3f}]  -> {verdict}"]
    return "\n".join(lines)
