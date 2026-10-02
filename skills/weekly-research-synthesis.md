---
name: weekly-research-synthesis
description: Synthesize the week's new user feedback for Streakly with zero input — read everything dropped in ops/research/inbox/, theme it, test each theme against the existing research baseline, and flag what changes a decision. Use when asked for the weekly research synthesis, to summarize new feedback, tickets, or NPS comments, or to run the research workflow.
---

# Weekly Research Synthesis — one-command workflow

Turns whatever landed in the inbox this week into themes, and — the part that
matters — says which themes are **new** versus which merely re-confirm what
`02-research/` already established.

**The inbox is the input.** Drop raw feedback in `ops/research/inbox/` as it
arrives during the week; any format, any filename. This workflow needs no other
input. If the inbox is empty it says so and stops.

**Related:** the `design:research-synthesis` plugin skill is general-purpose.
This one is Streakly-specific: it diffs against a known baseline and is wired to
this workspace's files.

---

## Trigger prompt

Paste this and nothing else:

```
Run the research synthesis workflow in skills/weekly-research-synthesis.md.
```

---

## Steps

**1. Fix the week and read the inbox.**

```bash
date "+%Y-%m-%d (ISO week %G-W%V)"
ls -la ops/research/inbox/
```

Read every file in `ops/research/inbox/` except `README.md` and `processed/`.
Handle `.csv`, `.md`, `.txt`, `.json` alike — you are after free text.

**If the inbox is empty: stop.** Say "No new feedback in the inbox for
<week>." Write nothing. Do not re-synthesize `processed/` to manufacture an
output, and do not reach for `02-research/` to pad it.

**2. Count the corpus before reading it closely.** How many distinct pieces of
feedback, from which sources, over what date range if dates are present. This
number governs how much weight any theme can carry — say so explicitly. Three
tickets is not a trend.

**3. Load the baseline.** Read these before theming, so you can tell new signal
from old:

- `02-research/nps-analysis.md` — established themes, with frequencies
  (streak-loss 6/10, notifications 3/10, weak re-engagement 2/10).
- `02-research/interview-synthesis.md` — the five established themes and the
  fragile-middle-zone finding.
- `02-research/competitive-matrix.md` — only for feedback that names a
  competitor.
- `CLAUDE.md` → The Numbers — so any quantitative claim in the feedback can be
  checked against what's measured.

**4. Theme the new corpus.** Group by the user's *problem*, not their proposed
solution. For each theme: a count, the two strongest verbatim quotes, and a
one-line statement of the underlying mechanism.

**5. Classify every theme against the baseline.** This is the step that makes
the output worth reading:

| Class | Meaning | So what |
|---|---|---|
| **Confirms** | Already in the baseline | Note the new count; no action |
| **Sharpens** | Known theme, new specificity or a new segment | May change scope |
| **New** | Not in the baseline at all | Needs a decision on whether to chase |
| **Contradicts** | Cuts against a baseline finding or a live assumption | **Escalate** |

**6. Test against the live assumptions.** `07-docs/hypothesis.md` has a "What
we assume" section. For each assumption, ask whether anything in this week's
corpus supports, undermines, or is silent on it. "Silent" is a legitimate and
common answer — say it rather than forcing a read.

**7. Pull the decision implications.** Only two questions matter:

- Does anything here change the **rollout target**? The current live question
  is breakers vs. non-breakers (see the correction in
  `data/metric-diagnosis.md`). Feedback from a user who broke a streak and one
  who didn't are different evidence.
- Does anything here change what goes into the **second cohort**?

If the answer to both is no, say so in one line. A week that changes no
decision is a normal week and the output should be short.

**8. Save** to `ops/research/YYYY-Www-research.md` (ISO week, e.g.
`2026-W40-research.md`).

**9. Move what you read** into `ops/research/inbox/processed/` so next week
doesn't double-count it. Report the file count moved.

**10. Close the loop.** Print to chat: the save path, the count of new vs
confirming themes, and anything classed **Contradicts** — that is the only
class that needs the user's attention today.

---

## Output format

```markdown
# Research Synthesis — Streakly · YYYY-Www

**Compiled:** <date> · **Corpus:** <n> pieces from <sources> (<date range>)
**Baseline:** 02-research/nps-analysis.md, 02-research/interview-synthesis.md
**Weight warning:** <e.g. "n=4 — directional only, not a measurement">

## Headline
<One sentence. If nothing changed a decision, say that.>

## Themes

### <Theme> — <n> mentions · **<Confirms | Sharpens | New | Contradicts>**
<Mechanism in one line.>
> "<verbatim>" — <source>
> "<verbatim>" — <source>
**Against baseline:** <what was already known, and what this adds>

## Live assumptions
| Assumption (hypothesis.md) | This week's corpus | Read |
|---|---|---|
| <assumption> | supports / undermines / silent | <one line> |

## Decision implications
- **Rollout target (breakers vs non-breakers):** <changed / unchanged, why>
- **Second cohort scope:** <changed / unchanged, why>

## Not in this corpus
<Questions this feedback cannot answer, so nobody reads a gap as a null result.>

## Provenance
- Real user feedback: <n> pieces. Synthetic/roleplay: <n, usually 0>.
- Files read: <list> → moved to processed/
```

---

## Boundaries

- **Writes one new file** in `ops/research/`, and **moves** inbox files to
  `processed/`. Nothing else.
- **Never edits** `02-research/*`, `CLAUDE.md`, or `hypothesis.md`. If a theme
  warrants amending the baseline, propose the edit and wait.
- **Never invents feedback.** Empty inbox → no output, no synthesis.
- **Never pads a thin week.** n=3 gets labeled n=3.
- **Never merges real feedback with roleplay** in a count.
