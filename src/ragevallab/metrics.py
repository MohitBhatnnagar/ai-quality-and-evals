"""Retrieval metrics for a single query. `relevant` is the set of gold doc ids."""
from __future__ import annotations

import math
import random
from statistics import mean


def hit_at_k(ranked: list[str], relevant: set[str], k: int) -> float:
    return 1.0 if any(d in relevant for d in ranked[:k]) else 0.0


def recall_at_k(ranked: list[str], relevant: set[str], k: int) -> float:
    return len(relevant.intersection(ranked[:k])) / len(relevant) if relevant else 0.0


def reciprocal_rank(ranked: list[str], relevant: set[str]) -> float:
    for i, d in enumerate(ranked, start=1):
        if d in relevant:
            return 1.0 / i
    return 0.0


def ndcg_at_k(ranked: list[str], relevant: set[str], k: int) -> float:
    dcg = sum(1.0 / math.log2(i + 1) for i, d in enumerate(ranked[:k], start=1) if d in relevant)
    ideal = sum(1.0 / math.log2(i + 1) for i in range(1, min(len(relevant), k) + 1))
    return dcg / ideal if ideal else 0.0


def bootstrap_ci(values: list[float], n: int = 2000, alpha: float = 0.05, seed: int = 7) -> tuple[float, float]:
    """Percentile bootstrap CI for the mean of per-query scores."""
    if not values:
        return (0.0, 0.0)
    rng = random.Random(seed)
    means = sorted(mean(rng.choices(values, k=len(values))) for _ in range(n))
    return means[int(n * alpha / 2)], means[int(n * (1 - alpha / 2)) - 1]


def paired_bootstrap_diff(a: list[float], b: list[float], n: int = 2000, seed: int = 7) -> tuple[float, float, float]:
    """Compare two systems on the SAME queries. Returns (mean_diff, ci_low, ci_high) for a - b.

    Resampling query indices (not scores) preserves the pairing, which is what
    makes the test meaningful when one query is simply harder than another.
    """
    if len(a) != len(b) or not a:
        raise ValueError("need equal-length, non-empty paired scores")
    rng = random.Random(seed)
    diffs = [x - y for x, y in zip(a, b)]
    boots = sorted(mean(rng.choices(diffs, k=len(diffs))) for _ in range(n))
    return mean(diffs), boots[int(n * 0.025)], boots[int(n * 0.975) - 1]
