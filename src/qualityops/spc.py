"""Statistical process control: p-chart with variable subgroup size and run rules."""
from __future__ import annotations

from dataclasses import dataclass
from math import sqrt


@dataclass(frozen=True)
class Point:
    index: int
    p: float
    lcl: float
    ucl: float
    signals: tuple[str, ...]


def p_chart(defectives: list[int], sizes: list[int]) -> tuple[float, list[Point]]:
    """Return (centre line p-bar, points). Limits are per-subgroup because n varies."""
    if len(defectives) != len(sizes) or not sizes:
        raise ValueError("need equal-length, non-empty defectives and sizes")
    if any(n <= 0 for n in sizes) or any(d < 0 or d > n for d, n in zip(defectives, sizes)):
        raise ValueError("invalid subgroup data")
    pbar = sum(defectives) / sum(sizes)
    rows = []
    for i, (d, n) in enumerate(zip(defectives, sizes)):
        se = sqrt(pbar * (1 - pbar) / n)
        rows.append({"i": i, "p": d / n, "lcl": max(0.0, pbar - 3 * se),
                     "ucl": min(1.0, pbar + 3 * se), "sig": []})
    _apply_rules(rows, pbar)
    return pbar, [Point(r["i"], r["p"], r["lcl"], r["ucl"], tuple(r["sig"])) for r in rows]


def _apply_rules(rows: list[dict], pbar: float) -> None:
    for r in rows:
        if r["p"] > r["ucl"]:
            r["sig"].append("above UCL")
        elif r["p"] < r["lcl"]:
            r["sig"].append("below LCL")
    # 8 consecutive points on one side of the centre line (shift in the process mean)
    run, prev = 0, 0
    for r in rows:
        side = (r["p"] > pbar) - (r["p"] < pbar)
        run = run + 1 if side != 0 and side == prev else (1 if side != 0 else 0)
        prev = side
        if run >= 8:
            r["sig"].append("8 in a row on one side")
    # 6 points steadily rising or falling (drift)
    for i in range(5, len(rows)):
        w = [rows[j]["p"] for j in range(i - 5, i + 1)]
        if all(b > a for a, b in zip(w, w[1:])) or all(b < a for a, b in zip(w, w[1:])):
            rows[i]["sig"].append("6-point trend")


def out_of_control(points: list[Point]) -> list[Point]:
    return [p for p in points if p.signals]
