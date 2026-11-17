# Evaluating RAG before shipping it

A retrieval-augmented assistant has two stages that fail independently: **retrieval** (did we fetch the right passages?) and **generation** (did the model answer faithfully from them?). Evaluate retrieval first. If the right passage is not retrieved, no prompt can fix the answer.

## Stage 1: retrieval (implemented in `src/ragevallab`)

- Build a **golden set** of real user questions with the document(s) that answer them.
- Compare retrievers (BM25, TF-IDF, hybrid via reciprocal rank fusion, dense embeddings) on hit@k, recall@k, MRR and nDCG.
- Report **bootstrap confidence intervals**, and use a **paired** bootstrap to compare systems on the same queries.

Bundled finding: on a small set mixing keyword and paraphrased questions, three lexical retrievers all stalled at 9 of 14 hits and fusing them added nothing. Lexical methods fail on paraphrase by construction, so the next step is dense retrieval or query rewriting, not more tuning.

## Stage 2: generation (extension path)

| Check | Question | Typical method |
|---|---|---|
| Faithfulness | Is every claim supported by retrieved text? | Claim extraction plus entailment check, or an LLM judge calibrated against humans |
| Answer relevance | Does it answer what was asked? | LLM judge with rubric |
| Abstention | Does it say "I don't know" when retrieval is empty or weak? | Questions with no answer in the corpus |
| Citation accuracy | Do cited sources actually contain the claim? | Automated span match |

An LLM judge is itself a reviewer: calibrate it against human labels with kappa (see `reviewer-calibration.md`) before trusting it as a gate.

## Release discipline

1. Freeze a golden set and keep it out of prompt tuning.
2. Track metrics per commit. Fail the build on a **statistically significant** regression, not on a one-point wobble.
3. Refresh the set from production questions monthly and watch for new failure themes.
4. Always include out-of-scope questions, because the costly failure is a confident wrong answer.
