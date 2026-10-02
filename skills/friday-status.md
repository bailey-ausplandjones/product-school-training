---
name: friday-status
description: Compile the Friday status update for Streakly with zero input — gather what shipped, what's in progress, and what's blocked from the repo's own history, then write a segmented team update and a one-page leadership update. Use when asked for the Friday status, the weekly status update, or to run the status workflow.
---

# Friday Status — one-command workflow

Produces two calibrated updates from zero input. Everything in "what shipped"
is derived from the workspace, not from the user's recollection.

**Related:** [weekly-status.md](weekly-status.md) owns the *templates and
calibration table*. This skill owns the *gathering*. Don't duplicate the
templates here — read them from that file at step 6.

---

## Trigger prompt

Paste this and nothing else:

```
Run the Friday status workflow in skills/friday-status.md.
```

---

## Steps

**1. Fix the week.** Run `date "+%Y-%m-%d %A"`. Define the window as the last 7
days unless today is not a Friday, in which case use the most recent Friday as
the window's end and say which date you used.

**2. Harvest what shipped — from git, not from memory.**

```bash
git log --since="7 days ago" --pretty=format:"%ad | %s" --date=short
git diff --stat "@{7 days ago}" HEAD
```

Each commit is a candidate "shipped" item. Translate commit subjects into
outcomes a stakeholder cares about — "Module 5: Day-7 metric analysis" becomes
"Day-7 decomposition complete; the leak is day 1→7, not acquisition." Drop
pure-mechanics commits (link fixes, typos) unless nothing else shipped.

**3. Harvest decisions and blockers from the workspace.**

- `01-orient/change_log.md` — entries dated inside the window.
- `CLAUDE.md` → "Where We Actually Are" → the numbered open items. **This is
  the blocker list.** Each one is either still open (carry it, and note how
  many weeks it has been open) or was closed this week (move it to Shipped).
- `07-docs/objection-log.md` — any objection with no answer yet is a blocker in
  waiting. The one flagged most-likely-to-kill goes top of the list.
- `07-docs/spec-readiness.md` — named, dated, owned items. If a date inside the
  window passed without the item closing, that is a slipped commitment and it
  gets said plainly.

**4. Find what's genuinely in progress** — anything with an owner and no
completed artifact. Check for files that exist but are still placeholders
(`grep -rln '___' --include='*.md' .`) and report those as not-started rather
than in-progress.

**5. Audit before writing.** For every item, in order:

- Does the artifact it claims actually exist on disk? If not, cut the item.
- Is the evidence real or synthetic? The three interviews are real; persona
  roleplay is synthetic. Label it every time.
- Is the blocker stated at its true size, or softened? State it at true size.
- Is any number here uncomparable to another? Use the canonical table in
  `CLAUDE.md`. Never quote the week-5 Day-30 figure (p=0.12).

**6. Write both updates** using the templates and calibration table in
[weekly-status.md](weekly-status.md) — Template 1 (team: Raj + Lena, segmented,
not averaged) and Template 2 (leadership: Marcus, hard one-page ceiling, ask in
sentence one). Read `08-stakeholders/*.md` for calibration; it comes from there,
not from this file.

**7. Save** to `ops/status/YYYY-MM-DD-status.md` using the window's end date.
Both updates in one file, team update first, under `## Team update` and
`## Leadership update`.

**8. Close the loop.** Print to chat: the save path, the headline ask for
Marcus, and any item where you had to cut a claim because the artifact didn't
exist. Then — and only as a proposal, not an edit — offer the `change_log.md`
line this week would warrant.

---

## Output format

```markdown
# Friday Status — Streakly Comeback · week ending YYYY-MM-DD

**Compiled:** <date> · **Window:** <start> → <end>
**Sources:** git log (<n> commits), change_log.md, objection-log.md, spec-readiness.md
**Evidence note:** <anything synthetic, named here once>

## Team update
<Template 1 from weekly-status.md — shared core, then a block for Raj, then Lena>

## Leadership update
<Template 2 from weekly-status.md — one page, ask first>

## Audit trail
- **Cut from this update:** <claims dropped because the artifact didn't exist, or "none">
- **Open N weeks:** <blockers carried from prior weeks, with age>
- **Slipped this week:** <dated commitments that passed without closing, or "none">
- **Proposed change_log entry:** <one row, for your approval — not yet written>
```

---

## Boundaries

- **Writes one new file**, `ops/status/<date>-status.md`. If it already exists,
  stop and ask rather than overwriting.
- **Never edits** `change_log.md`, `CLAUDE.md`, or any project artifact. It
  proposes the change-log row and waits.
- **Never invents** a shipped item, a quote, or a number. An empty section says
  "None this week."
- **Never presents roleplay as user validation.** Lena's bar is real users.
