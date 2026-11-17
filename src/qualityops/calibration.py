"""Reviewer calibration: do reviewers judge the same work the same way?"""
from __future__ import annotations

from collections import Counter
from itertools import combinations
from statistics import mean, pstdev


def cohens_kappa(a: list[str], b: list[str]) -> float:
    """Agreement beyond chance between two reviewers rating the same items.

    kappa = (po - pe) / (1 - pe): 1 is perfect, 0 is chance level, below 0 is worse
    than chance. Raw percent agreement overstates quality when one verdict
    (usually "pass") dominates, which is exactly the situation in a mature process.
    """
    if len(a) != len(b) or not a:
        raise ValueError("need equal-length, non-empty ratings")
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[k] * cb.get(k, 0) for k in ca) / (n * n)
    if pe == 1.0:
        return 1.0  # both used one identical verdict throughout
    return (po - pe) / (1 - pe)


def interpret(kappa: float) -> str:
    """Landis and Koch bands."""
    if kappa <= 0:
        return "no better than chance"
    for limit, label in ((0.2, "slight"), (0.4, "fair"), (0.6, "moderate"), (0.8, "substantial")):
        if kappa < limit:
            return label
    return "almost perfect"


def pairwise_kappa(ratings: dict[str, list[str]]) -> dict[tuple[str, str], float]:
    return {(x, y): cohens_kappa(ratings[x], ratings[y]) for x, y in combinations(sorted(ratings), 2)}


def strictness(ratings: dict[str, list[str]], fail_label: str = "fail") -> dict[str, float]:
    """Each reviewer's fail rate on the SAME items, as a z-score against the group.

    Large positive = stricter than peers, large negative = more lenient. Requires a
    shared sample, which is why calibration sessions use common items.
    """
    rates = {r: sum(v == fail_label for v in vs) / len(vs) for r, vs in ratings.items()}
    m, s = mean(rates.values()), pstdev(rates.values())
    return {r: (0.0 if s == 0 else (x - m) / s) for r, x in rates.items()}


def needs_recalibration(ratings: dict[str, list[str]], min_kappa: float = 0.6,
                        z_limit: float = 1.5) -> list[str]:
    """Reviewers whose average agreement with peers is low, or whose strictness is extreme."""
    if len(ratings) < 3:
        raise ValueError("need at least three reviewers to identify an outlier")
    pk = pairwise_kappa(ratings)
    z = strictness(ratings)
    flagged = []
    for r in ratings:
        avg = mean(v for (x, y), v in pk.items() if r in (x, y))
        if avg < min_kappa or abs(z[r]) > z_limit:
            flagged.append(r)
    return sorted(flagged)
