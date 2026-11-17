# Quality framework for an AI-assisted delivery operation

## Principle

Quality is a **system property**, not a reviewer's effort. If quality depends on one strong reviewer catching everything at the end, it will fail the moment volume or turnover rises. The aim is to move detection earlier and make the standard consistent.

## Three gates

```
 Brief -> [Gate 0: input check] -> Work (human, agent or both) -> [Gate 1: self / automated check]
                                                                     -> [Gate 2: calibrated peer review] -> Client
```

| Gate | Catches | Owner | Automated? |
|---|---|---|---|
| **0. Input check** | Unclear or incomplete briefs, the most common root cause in most operations | Intake owner | Mostly (completeness rules) |
| **1. Self / automated check** | Format, template, brand and consistency errors; things a rule can verify | Producer, with agents | Yes |
| **2. Calibrated peer review** | Judgement errors: does it answer the brief, is it persuasive, is it right | Reviewer | No, but sampled |

Review effort is spent where judgement is needed. Anything a rule can check goes to Gate 1 so reviewers are not spent on mechanical defects.

## The metric tree

| Level | Metric | Why |
|---|---|---|
| Outcome | Client acceptance rate, rework requests | What the client feels |
| Process | **First-pass yield** at each gate | Reveals hidden rework |
| Process | Defect rate by root-cause category | Points to the fix |
| System | Reviewer agreement (kappa), strictness spread | Tells you whether the standard is shared |
| Health | Control-chart signals, time to detect a shift | Tells you when to act |

Every metric has one named owner and one review cadence.

## Operating rhythm

- **Daily:** exceptions and escalations only. No dashboards read aloud.
- **Weekly:** control chart review, top root causes (Pareto), actions with owners. Fix the process behind a recurring defect, not the single deliverable.
- **Monthly:** reviewer calibration session on a shared sample, then a trend review with leadership.

## Root-cause discipline

1. Log a root cause category on every defect at the time it is found.
2. Rank causes (Pareto). Work on the **vital few** that account for roughly 80% of defects.
3. For each, ask why until you reach a process or input cause. "Reviewer missed it" is never a root cause.
4. Change the process (checklist, template, intake rule, automation), then watch the chart to confirm the shift.

## Where AI fits

- **Gate 0 and Gate 1** are the best places for agents: completeness checks, consistency checks, formatting, first-pass review against the brief.
- **Gate 2** stays human for judgement, and agents assist by pre-flagging likely issues.
- Agent output is measured with the **same metrics** as human output (yield, defects by cause), so you can see whether automation helps or hides quality loss.
- Low-confidence agent output is held for review rather than shipped. See the autonomy policy in `agentflow-hitl`.

## Anti-patterns

- Reporting an average that includes rework as if it were first-pass quality.
- Reacting to every dip (tampering), or ignoring a genuine shift because one week looked fine.
- Calibrating reviewers on their own queues, where nobody judged the same items.
- Treating a reviewer as the root cause.
