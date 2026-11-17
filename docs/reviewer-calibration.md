# Reviewer calibration

Two reviewers looking at the same piece of work should reach the same verdict. When they do not, the standard is personal rather than shared, and quality will vary with who happened to review.

## Running a session

1. **Sample.** Pick 20 to 30 recently delivered items that every reviewer has not seen. Include some clear passes, clear fails and borderline cases.
2. **Rate independently.** Each reviewer records pass or fail (and a defect category) without discussion.
3. **Measure.** Compute pairwise Cohen's kappa and each reviewer's strictness z-score (`qualityops.needs_recalibration`).
4. **Discuss the disagreements,** not the agreements. For each, decide the correct verdict and write down the rule that decides it.
5. **Update the standard.** Add the rule to the reviewer checklist with the example. Repeat monthly.

## Reading the numbers

| Kappa | Meaning | Action |
|---|---|---|
| below 0.4 | Reviewers are not applying a shared standard | Stop scaling headcount; fix the standard first |
| 0.4 to 0.6 | Moderate agreement | Calibrate monthly, target the disagreement themes |
| 0.6 to 0.8 | Substantial | Sustain with quarterly checks |
| above 0.8 | Near-perfect | Candidate calibrators for others |

Strictness z-score beyond about 1.5 means a reviewer fails much more or less than peers on identical items. That is a calibration conversation, not a performance verdict.

## Why not percent agreement

If 90% of items pass, two reviewers who always answer "pass" agree 90% of the time yet detect nothing. Kappa subtracts the agreement expected by chance, so it stays honest in a mature process where most work passes. The unit tests include a case with 80% raw agreement and a negative kappa.

## Using the same idea for AI reviewers

An LLM used as a reviewer must be calibrated like a person. Run it on the same sample, compute its kappa against the human consensus, and only let it act as an automated gate where agreement is high. Track drift: re-run the sample whenever the model or prompt changes.
