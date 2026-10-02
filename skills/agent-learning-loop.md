---
name: agent-learning-loop
description: Weekly self-review of the agent stack's own track record. Reads outcome-log.md, scores each past diagnosis as hit/miss/partial against what actually happened, computes hit rate by confidence band, and proposes exactly one heuristic update to CLAUDE.md. Proposes only — never edits.
---

# Agent Learning Loop — weekly self-review

The loop that turns `anomaly-diagnosis`'s confidence scores from hand-tuned
guesses into something calibrated. Every other agent in the stack produces
output; this one scores whether that output was any good.

**Related:** [`agents/registry.md`](../agents/registry.md) §3 · [`agents/anomaly-diagnosis.md`](../agents/anomaly-diagnosis.md) §6

---

## Trigger prompt

Paste this and nothing else:

```
Run the agent learning loop in skills/agent-learning-loop.md.
```

Runs with no further input. Don't ask clarifying questions — run it and report
at the end.

---

## Hard rules

These are what make it safe to run unattended, and they override anything below.

1. **Propose, never apply.** The output ends with a proposed `CLAUDE.md` edit as
   a quoted block, and stops. Do not write to `CLAUDE.md`. Do not write to
   `outcome-log.md`. Do not write any file unless the user says yes.
2. **Never invent an outcome.** An entry whose **What actually happened** field
   is still `_TBD_` is **unscored**, not a miss. Unscored entries are counted
   and listed; they are never guessed at, inferred from the data, or scored by
   re-running the analysis.
3. **Skip fixtures.** Entries tagged `[FIXTURE]` or whose **Data source** is
   under `agents/fixtures/` are excluded from every statistic. They exist to
   test the loop, not to calibrate it.
4. **Refuse to propose on thin evidence.** Fewer than **5 scored** entries →
   report the counts and stop, with no heuristic proposal. A hit rate on three
   calls is noise, and a heuristic derived from it would be worse than none.
5. **Exactly one proposal.** Not three, not a list. The single highest-leverage
   change, with the evidence that earned it. If two are tied, say so and pick
   the one that would change more future output.
6. **A quiet week produces a short report.** No new scored entries since the
   last run → five lines saying so. Never pad.

---

## Steps

### 1. Read the log

Read `outcome-log.md`. Parse each `## {timestamp} — {trigger}` block for:

- timestamp, trigger, data source, `[FIXTURE]` tag
- the three ranked hypotheses with their confidence scores
- **What actually happened** — prose or `_TBD_`
- **Was the top hypothesis right?** — `yes` / `no` / `partly` / `_TBD_`

If the file doesn't exist, say so and stop. Don't create it.

### 2. Score each entry

| Score | When |
|---|---|
| **Hit** | The top hypothesis was the actual cause |
| **Partial** | The top hypothesis was a contributing cause, or the right mechanism at the wrong magnitude, or it was ranked #2/#3 and that one was right |
| **Miss** | The actual cause isn't in the ranked three at all |
| **Unscored** | Outcome field is `_TBD_` |

Where the human wrote `yes`/`no`/`partly`, use it — it's their call, not yours.
Where they wrote prose but left the verdict blank, score it from the prose and
**mark that the score is your reading, not theirs**.

### 3. Compute the record

Report, with raw counts, never bare percentages:

- Overall: `hits / scored` (e.g. `4/7 hit, 2 partial, 1 miss`)
- **By confidence band**: 7/10, 8/10, 9–10/10 separately. This is the number
  that matters — a 9/10 that hits as often as a 7/10 means the score carries no
  information and the scale should be collapsed.
- **By hypothesis type** (`streak_punishment`, `engagement_depth`, …): which
  mechanisms the stack reads well and which it reliably gets wrong.
- Unscored count, oldest unscored date, and anything open **more than 14 days** —
  call those out by name. An unscored log is the failure mode that kills this
  loop, and it fails silently.

### 4. Propose one heuristic update

Pick the single change best supported by the record. Candidates, roughly in
order of how often they'll be the right answer:

| Pattern in the record | Proposal shape |
|---|---|
| A confidence band is systematically over-confident | Adjust that hypothesis's point formula in `anomaly-diagnosis.md` §4, and note the new expected hit rate |
| One hypothesis type is reliably wrong | Lower its base score, or move it behind a precondition |
| A cause keeps appearing in outcomes but isn't in the catalogue | Propose a new hypothesis with its trigger and formula |
| Bands don't separate (9/10 ≈ 7/10) | Collapse the scale, or raise the gate |
| Misses cluster where a driver was below threshold | Propose a different driver threshold, with the evidence |
| The gate is letting through non-significant evidence that keeps missing | Propose adding a significance precondition to the gate |

Write it as a `CLAUDE.md`-ready block, in the voice of the existing "Four things
to know" bullets, and state plainly what it would change about future output.

### 5. Report

```
## Agent learning loop — {date}

**Record:** {N} scored of {M} logged ({F} fixtures excluded)
• Hits: {n}  Partial: {n}  Miss: {n}
• By confidence: 7/10 → {h}/{n} · 8/10 → {h}/{n} · 9–10/10 → {h}/{n}
• By hypothesis: {type} {h}/{n}, {type} {h}/{n}, …

**Unscored:** {n} entries, oldest {date}
{list any open >14 days, by name — these are the ones that break the loop}

**What the record says:**
{2–4 sentences. What the stack reads well, what it doesn't, and whether the
confidence scale is carrying information at all.}

**Proposed heuristic update (ONE):**
> {the CLAUDE.md-ready block}

*Evidence:* {the specific entries that support it}
*Would change:* {what future output looks different if applied}

**Not proposing:** {anything you considered and rejected, one line each — so a
rejected idea doesn't get re-proposed next week as if it were new}

Nothing was written. Say the word and I'll apply the proposal to CLAUDE.md.
```

---

## Current state — read this before the first run

`outcome-log.md` holds **one entry, from a fixture, with both outcome fields
blank.** A run today correctly returns:

> 0 scored of 1 logged (1 fixture excluded). Nothing to calibrate. No proposal.

That is the right answer, not a bug. The loop becomes useful at roughly **8–10
scored calls**; rule 4 blocks any proposal below 5. On a realistic alert rate
that's **month 2–3 of running the stack**, not week 1.

Which makes the real first task not running this loop, but **filling in the
outcome fields after each diagnosis**. The log is a human commitment. If those
fields stay blank, this loop never produces anything and the confidence scores
in `anomaly-diagnosis` stay permanently uncalibrated — see
[`agents/registry.md`](../agents/registry.md) §5, which lists that as one of the
three things that would make the roadmap wrong.
