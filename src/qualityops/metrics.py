"""Core quality metrics for a service operation."""
from __future__ import annotations

from collections import Counter
from statistics import NormalDist


def first_pass_yield(passed: int, total: int) -> float:
    """Share of items right the first time (no rework)."""
    if total <= 0:
        raise ValueError("total must be positive")
    if not 0 <= passed <= total:
        raise ValueError("passed must be between 0 and total")
    return passed / total


def dpmo(defects: int, units: int, opportunities_per_unit: int) -> float:
    """Defects per million opportunities."""
    if units <= 0 or opportunities_per_unit <= 0:
        raise ValueError("units and opportunities must be positive")
    return defects / (units * opportunities_per_unit) * 1_000_000


def sigma_level(dpmo_value: float, shift: float = 1.5) -> float:
    """Process sigma from DPMO using the conventional 1.5-sigma long-term shift."""
    if not 0 < dpmo_value < 1_000_000:
        raise ValueError("DPMO must be between 0 and 1,000,000 (exclusive)")
    return NormalDist().inv_cdf(1 - dpmo_value / 1_000_000) + shift


def pareto(causes: list[str]) -> list[tuple[str, int, float]]:
    """Rank root causes as (cause, count, cumulative share). The vital few come first."""
    counts = Counter(c for c in causes if c)
    total = sum(counts.values())
    out, running = [], 0
    for cause, n in sorted(counts.items(), key=lambda x: (-x[1], x[0])):
        running += n
        out.append((cause, n, running / total))
    return out


def vital_few(causes: list[str], threshold: float = 0.8) -> list[str]:
    """Smallest set of causes covering at least `threshold` of all defects."""
    chosen = []
    for cause, _, cum in pareto(causes):
        chosen.append(cause)
        if cum >= threshold:
            break
    return chosen
