# Workspace Audit — pm-workspace

**Date:** 2026-10-02 · **Scope:** structure, file inventory, `CLAUDE.md` accuracy
**Verdict:** the *content* is strong — six modules of substantive, cross-referenced, evidence-labeled work. The *scaffolding* has drifted out from under it, and `CLAUDE.md` was describing a project state three weeks stale.

---

## 1. What's actually here

38 files. Real artifacts across every module except 6:

| Module | Status | Where the artifacts actually are |
|---|---|---|
| 1 Orient | Done | `01-orient/project.md`, `strategy.md`, `change_log.md` |
| 2 Discover | Done | `02-research/` (3 files) + `07-docs/decision-brief.md` |
| 3 Build | Done | `03-build/prototype/` + `07-docs/hypothesis.md`, `triad-session.md`, `pm-brief.md` |
| 4 Collaborate | Done | `07-docs/codebase-summary.md`, `spec-readiness.md`, `design-review.md`, `qa-checklist.md` |
| 5 Decide | Done | `05-decide/metric-findings.md`, `data/metric-diagnosis.md`, `data/experiment-design.md`, `07-docs/recommendation-memo.md`, `prd.md`, `objection-log.md`, `presentation.md`, `presentation-notes.md`, `quarterly-review.pptx`, `skills/` |
| 6 Systematize | **Not started** | `06-systems/systems.md` is blank; `final-presentation.html` is still the placeholder stub |

Plus `08-stakeholders/` (3 reader models) and `data/` (5 CSVs) — both genuinely useful and neither mentioned anywhere a fresh session would find them.

---

## 2. What's missing that would make Claude more useful next session

Ranked by how much friction each one removed.

**1. Current state.** The old `CLAUDE.md` said *"Open decision: what the fix concept should be, going into Thursday's kickoff."* That decision was made, prototyped, roleplay-tested, triad-reviewed, spec'd, objection-logged, shipped to a week-5 cohort, measured, and written up. A fresh session would have opened by helping brainstorm fix concepts — work finished three weeks ago. **Fixed:** new "Where We Actually Are" section.

**2. A numbers canon.** Figures were spread across five docs: 48%→39% in the brief, 38.6% in the diagnosis, 37/37/31/27 by cohort, 76 vs 46 in the pilot, 26.8 vs 45.8 by segment. Claude re-derived them every session and had no way to know which were comparable. **Fixed:** single canonical table with sources and the "do not quote Day-30" flag.

**3. The live contradiction between two analysis docs.** `05-decide/metric-findings.md` recommends shipping to **breakers**. `data/metric-diagnosis.md` explicitly reverses this to **non-breakers** (p=0.007 vs p=0.13) and says so in its own header — but `metric-findings.md` was never amended. Any session reading the older file first builds on a retracted recommendation. **Fixed in `CLAUDE.md`;** see action item A1 to fix at the source.

**4. Stakeholder calibration as a standing rule.** `08-stakeholders/` is some of the best material here — Raj's stale-estimate problem, Lena's authorship of a concept redesigned without her, Marcus's ask-in-sentence-one preference. Nothing told Claude these files existed or to read them before drafting. **Fixed:** named in the working rules and the workspace map.

**5. Evidence-provenance rule.** Three interviews are real; the 3-persona roleplay is synthetic. `skills/weekly-status.md` makes this standing rule #1, but `CLAUDE.md` didn't — so it only applied when that one skill happened to be in play. This is the single likeliest source of a credibility-destroying error in a doc going to Lena. **Fixed:** promoted to a working rule.

**6. A workspace map.** With artifacts scattered across `07-docs/`, `data/`, `08-stakeholders/` and the numbered folders, a fresh session had to re-explore every time. **Fixed.**

**7. The glossary** was literally `| ___ | ___ |`. The freeze-vs-restore distinction in particular is the whole shape of Raj's objection, and it's the kind of thing Claude will flatten into one concept without being told. **Fixed:** 9 terms.

**8. A current change log.** `01-orient/change_log.md` stops at 2026-09-30. It's missing the PRD, the objection log, the entire metric analysis, the recommendation memo, the deck, and the experiment design — i.e. everything from the project's most productive day. *(Not written — your call, and the log is yours.)*

**9. Skills aren't discoverable.** They live in `skills/`, not `.claude/skills/`, so Claude Code won't auto-load them as invocable skills. They're good skills being used as documents. *(Action item A4.)*

**10. Nothing is committed.** `07-docs/`, `08-stakeholders/`, `data/`, `.claude/`, `03-build/prototype/`, `05-decide/metric-findings.md` and both new skills are all untracked; the `02-research/decision-brief.md` deletion is unstaged. For a repo where *"the repo is the deliverable,"* roughly two-thirds of the deliverable isn't in it. *(Action item A5 — highest-value, lowest-effort thing on this list.)*

---

## 3. Reorganization that would reduce friction

**The core problem:** the README promises module → folder mapping, but Modules 3, 4 and 5 all emptied into a single `07-docs/` catch-all, and the module files that were supposed to hold the summaries are still blank templates. Three competing organizing schemes are live at once: by module (`01-`…`06-`), by artifact type (`07-docs/`, `08-stakeholders/`, `data/`), and by nothing (`07-docs/` is 13 unrelated documents).

Suggested, in priority order — **nothing below has been changed:**

**A1. Reconcile the two analysis docs.** Add a header note to `05-decide/metric-findings.md` pointing at the `data/metric-diagnosis.md` correction, the way the diagnosis doc already points back. One doc contradicting another silently is worse than either being wrong. *Highest value here.*

**A2. Fix three broken links.** All point at `02-research/decision-brief.md`, which moved to `07-docs/`:
- `07-docs/hypothesis.md:3`
- `07-docs/pm-brief.md:13`
- `03-build/prototype/README.md:12`

**A3. Pick one scheme for `07-docs/`.** Either redistribute by module (`hypothesis.md`/`triad-session.md`/`pm-brief.md` → `03-build/`; `codebase-summary.md`/`spec-readiness.md`/`design-review.md`/`qa-checklist.md` → `04-team/`; `prd.md`/`recommendation-memo.md`/`presentation*.md`/`objection-log.md` → `05-decide/`), which restores the README's promise and the certification's story — or keep the flat `07-docs/` and add a one-line index at its top. Either beats the current state. Redistributing means updating ~30 relative links, so do it in one pass or not at all.

**A4. De-collide the two weekly-status files.** `skills/weekly-status.md` (stakeholder-calibrated) and `skills/weekly-status/SKILL.md` (generic four-section) have near-identical names and different jobs. Suggest: `skills/weekly-status-calibrated/SKILL.md` with proper frontmatter, and symlink or move `skills/` → `.claude/skills/` so both become invocable.

**A5. Commit.** One commit per module retroactively, or one "catch up the workspace" commit. Then keep committing per module as the README intends.

**A6. Check the README's status boxes** and point its folder links at where artifacts actually live.

**A7. Minor:** `data/` holds two analysis docs (`metric-diagnosis.md`, `experiment-design.md`) alongside raw CSVs — those are Module 5 outputs, not data. Consider `data/` for CSVs only.

---

## 4. What was changed in this pass

- **`CLAUDE.md` rewritten.** Added: Where We Actually Are, the canonical numbers table, the metric-findings/metric-diagnosis contradiction, a workspace map, a filled 9-term glossary, and four working rules (ask before saving, never cite a missing file, label evidence provenance, name descopes first). Removed the template scaffolding line. Kept the product section, corrected the "open decision" framing, and carried over your existing tone and interview-first preferences.
- **This file.**

Nothing else was moved, renamed, edited, or deleted. Items A1–A7 are proposals awaiting your go-ahead.
