---
name: competitive-pulse
description: Weekly competitive pulse check for Streakly with zero input — search for new moves from Duolingo, Babbel, Elevate, Streaks, and Habitica, diff them against the existing competitive matrix, and flag anything that threatens the free non-punitive comeback white space. Use when asked for a competitive pulse, competitor check, or to run the competitive workflow.
---

# Competitive Pulse — one-command workflow

Checks the five tracked competitors for moves since the last pulse, and answers
one question above all others: **is the white space still open?**

The strategy in `07-docs/decision-brief.md` rests on a specific competitive
claim — that no competitor offers a genuinely free, non-punitive comeback
experience. If that stops being true, the differentiation argument for this
project weakens. That is what this workflow is for.

---

## Trigger prompt

Paste this and nothing else:

```
Run the competitive pulse workflow in skills/competitive-pulse.md.
```

---

## Steps

**1. Load the web tools.** `WebSearch` and `WebFetch` are deferred in this
environment — fetch both schemas in a single call before searching:

```
ToolSearch: select:WebSearch,WebFetch
```

**2. Fix the window.** Run `date "+%Y-%m-%d"`. The window runs from the most
recent file in `ops/competitive/` to today. If that folder is empty, the
baseline is `02-research/competitive-matrix.md` and the window is the last 30
days — say which you used.

**3. Load the baseline.** Read `02-research/competitive-matrix.md` in full:
the five tracked apps, their post-week-1 engagement mechanics, their recovery
mechanics, and the two white-space claims at the end. Also read the most recent
file in `ops/competitive/`, if any, so you don't re-report last week's news.

**4. Search, per app, scoped to the window.** Five apps: **Duolingo, Babbel,
Elevate, Streaks, Habitica.** For each, run searches along these axes and
prefer primary sources (newsroom, changelog, App Store release notes, earnings
call) over aggregator blogs:

- `<app> streak freeze OR streak repair OR comeback <year>`
- `<app> retention OR re-engagement OR notifications update <year>`
- `<app> pricing change <year>`
- `<app> release notes OR changelog <month year>`

**5. Add one open-ended sweep** for new entrants in the space — the baseline
already flags a "Streaks 2026" copycat, so the niche is being re-entered:

- `new habit streak app launch <month year>`
- `micro-learning app streak recovery feature <year>`

**6. Verify before reporting.** Every claimed move needs a URL and a date. If
you cannot date it, it does not go in the Moves section — it goes in "Unverified
/ watch." Undated aggregator posts recycling old news are the main failure mode
here.

**7. Diff each finding against the baseline.** For every verified move:

| Class | Meaning |
|---|---|
| **No change** | Baseline still accurate |
| **Update** | Baseline fact is now stale (price, feature detail) |
| **Threat** | Moves toward Streakly's white space |
| **Opening** | Moves away — white space widened |

**8. Answer the white-space question explicitly.** State one of three verdicts
and defend it in one line:

- **Still open** — no competitor ships a free, non-punitive comeback by default.
- **Narrowing** — someone moved toward it; name who and how far.
- **Closed** — someone shipped it. This is an escalation; say what it means for
  the decision brief's differentiation argument.

**9. Handle a quiet week honestly.** If nothing material surfaced, the verdict
is "Still open, no material moves" and the file is five lines long. Do **not**
manufacture significance from a routine app update. Distinguish "no moves
found" from "confirmed no moves" — the baseline already makes this distinction
for Elevate and says so.

**10. Save** to `ops/competitive/YYYY-MM-DD-pulse.md`.

**11. Close the loop.** Print to chat: the save path, the white-space verdict,
and any finding classed **Threat** or **Closed**. If any baseline fact is now
stale, list the proposed `competitive-matrix.md` edits — as a proposal, not an
edit.

---

## Output format

```markdown
# Competitive Pulse — Streakly · YYYY-MM-DD

**Window:** <start> → <end> · **Baseline:** 02-research/competitive-matrix.md
**Apps checked:** Duolingo, Babbel, Elevate, Streaks, Habitica (+ new-entrant sweep)

## White-space verdict
> **<Still open | Narrowing | Closed>** — <one line, defended>

Free, non-punitive comeback by default: <who, if anyone, is close>

## Moves this window

### <App> — **<No change | Update | Threat | Opening>**
**What:** <the move, one line> · **When:** <date> · **Source:** <url>
**So what for us:** <implication for the Comeback screen, or "none">

## New entrants
<Anything new in the streak/micro-learning space, or "none found">

## Baseline corrections
| Matrix claim | Now | Source |
|---|---|---|
| <stale fact> | <current fact> | <url> |

*(Proposed only — competitive-matrix.md not edited.)*

## Unverified / watch
<Claims found without a reliable date or primary source. Explicitly not acted on.>

## Coverage gaps
<Apps where the search returned nothing — a data gap, not a confirmed quiet week.>
```

---

## Boundaries

- **Writes one new file** in `ops/competitive/`. Nothing else.
- **Never edits** `02-research/competitive-matrix.md`. It proposes corrections
  in a table and waits — the matrix is a cited research artifact.
- **Never reports an undated claim as a move.**
- **Never conflates "found nothing" with "nothing happened."**
- **Never manufactures a threat** to make the week look eventful. A quiet week
  is a five-line file.
