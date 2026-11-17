# AI Quality and Evals

How to know whether an AI-assisted delivery operation is actually good, and how to keep it good as volume grows.

Quality and productivity usually pull against each other. Teams that raise output without a measurement system find out about the quality drop from the client. This repo is the measurement system: a short framework, plus two small reference libraries that make the framework executable.

## Contents

| Part | What it answers | Where |
|---|---|---|
| **Quality framework** | What do we measure, at which gate, who owns each number? | [docs/quality-framework.md](docs/quality-framework.md) |
| **Reviewer calibration** | Do our reviewers judge the same work the same way? | [docs/reviewer-calibration.md](docs/reviewer-calibration.md), `src/qualityops/calibration.py` |
| **Process control (SPC)** | Is a dip noise or a real shift? | `src/qualityops/spc.py` (p-chart, run rules) |
| **Defect analysis** | Which few causes drive most defects? | `src/qualityops/metrics.py` (Pareto, DPMO, sigma level) |
| **RAG evaluation** | Does retrieval work before we put an LLM on it? | [docs/rag-evaluation.md](docs/rag-evaluation.md), `src/ragevallab/` |

34 unit tests, standard library only.

```bash
pip install -e .
python -m unittest discover -s tests
ragevallab examples/docs examples/golden.json -k 3
```

## Why these metrics

- **First-pass yield, not just final quality.** A process that reaches 95% after rework is not a 95% process. Rework is the hidden cost.
- **Control charts, not weekly averages.** Week-to-week movement is mostly noise. A p-chart with limits and run rules says when to act and, as importantly, when not to.
- **Kappa, not percent agreement.** When 90% of work passes, two reviewers who always say "pass" agree 90% of the time while telling you nothing. Cohen's kappa corrects for chance.
- **Intervals, not averages, for model comparisons.** A retrieval change that lifts the mean by 3 points on 14 questions is not evidence. A paired bootstrap tells you whether it is.

## A worked example

```python
from qualityops import p_chart, out_of_control, needs_recalibration, vital_few

# weekly rework counts out of 200 deliverables
pbar, pts = p_chart([12, 9, 11, 10, 13, 24, 11, 10], [200] * 8)
for p in out_of_control(pts):
    print(p.index, p.signals)          # 5 ['above UCL']  -> investigate week 5

ratings = {"r1": [...], "r2": [...], "r3": [...], "r4": [...]}   # same items, pass/fail
print(needs_recalibration(ratings))     # reviewers to calibrate next session

print(vital_few(defect_root_causes))    # the 2-3 causes worth fixing first
```

All data in the examples and tests is synthetic.

## Honest limits

- Statistics assume reasonably independent samples. Batches of related work need rational subgrouping.
- Kappa needs a shared item sample. Calibration cannot be done from each reviewer's own queue.
- The RAG lab covers retrieval, not answer faithfulness. See [docs/rag-evaluation.md](docs/rag-evaluation.md) for how to extend it.

## License

MIT
