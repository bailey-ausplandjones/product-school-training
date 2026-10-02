# CLAUDE.md — Persistent Memory

> The file Claude Code reads at the start of every session. Short, true, current — the difference between Claude building blind and building with context.
>
> Last updated: 2026-10-02.

## The Product

Streakly is a consumer habit + micro-learning app that helps people learn a skill in five minutes a day. Users pick a track, do a short daily lesson, and build a streak — the streak is the core habit loop.

- Launched 4 years ago. Series B funded ($42M).
- 2.1M registered users, 340K monthly active users, growing 28% YoY on MAU.
- My role: PM for the engagement squad — own first-week activation (home screen, daily lesson loop, streak mechanics, push notifications).

## The Project — Streakly Comeback

Recover Day-7 retention, which slipped from 48% to 39% after the v2 streak redesign. Target: ≥48%.

**Root cause (three independent sources agree):** the streak mechanic has no state between "intact" and "zero." A single missed day erases the full count with no recovery path.

**Key tension:** streak as motivator vs. streak-break as punishment. Priya's 30-day celebration and Tom's churn come from the same mechanic.

**The fix concept — decided, not open.** Marcus approved: a free, non-punitive streak-recovery flow **+ early (pre-day-7) milestone moments + a state-aware home screen.** Only the recovery flow was built and tested — the descope was my call, to get a clean read on one variable. Say so before anyone finds it.

## Where We Actually Are (read this first)

Post-pilot, awaiting Marcus's ruling at Thursday's kickoff.

Done: research → decision brief → prototype → roleplay test → triad session → PRD → objection log → week-5 pilot → metric diagnosis → recommendation memo → deck + speaker notes → full experiment design.

**The ask on the table:** approve a second, properly powered cohort. **Not** full rollout. n=50 per arm can't carry a rollout decision.

**Open, genuinely unresolved:**
1. Marcus's ruling on scope (second cohort vs. rollout vs. kill) — Thursday.
2. Raj's feasibility re-scope. His "doable, no new data sources" yes was scoped against a one-tap **freeze** (a flag set before the day boundary). The prototype does a full retroactive **restore** of a value the system already overwrote — new persisted state, not new logic. He has not re-estimated. This is the objection most likely to kill the initiative.
3. Lena owes four states; the "did I open the wrong app" track-identity problem is patched (`· Meditation` header), not solved.
4. Implementation sprint start date — TBD.
5. Module 6 is unstarted: agent stack (metric pulse / weekly insight / anomaly→hypothesis) and the final presentation are still placeholders.

## The Numbers (canonical — don't re-derive, don't contradict)

| Fact | Value | Source |
|---|---|---|
| Day-7 pre-v2 → post-v2 | 48% → 39% (target ≥48%) | project brief |
| Day-7 in the sample data | 38.6% (193/500) | `data/metric-diagnosis.md` |
| Day-7 decay, cohorts 1–4 | 37% → 37% → 31% → 27% (~3 pts/week, not flattening) | `05-decide/metric-findings.md` |
| Day-1, all cohorts | 90–93% flat — acquisition is **not** the problem | same |
| Breakers vs non-breakers, Day-7 | 26.8% vs 45.8% (19 pts, p<0.0001, n=500) | same |
| Share of Day-7 churn that never broke a streak | 55% (168 of 307) — streak-break is at most 7.2 of the 9.4-pt gap | `data/metric-diagnosis.md` |
| Week-5 pilot, Day-7 | 76% treatment vs 46% control (+30 pts, p=0.002, n=50/arm) | same |
| Week-5 pilot, Day-30 | +14 pts, **p=0.12 — do not quote this number** | same |

**Live contradiction, unresolved in the files.** `05-decide/metric-findings.md` recommends shipping to the `broke_streak_week1 = true` segment. `data/metric-diagnosis.md` reverses that: within week 5 the lift is significant for **non-breakers** (93.3% vs 64.0%, p=0.007) and **not** significant for breakers (50.0% vs 28.0%, p=0.13). The diagnosis doc is the later and correct read; `metric-findings.md` has not been amended. The mechanism is not what we assumed. Don't quote metric-findings' rollout target.

## How I Want Claude to Work With Me

- **Interview first:** ask clarifying questions before building.
- **Tone:** concise; drafts are starting points, not finished documents.
- **Ask before saving.** Check with me before writing or updating project files or the change log — even mid-task, not just at the start.
- **Defaults:** mark gaps as TBD. Prompt me at natural checkpoints.
- **Never invent** details that aren't in the source material.
- **Never cite a file that doesn't exist.** Check the workspace before linking.
- **Label evidence provenance every time.** Three interviews (Priya, Tom, Amara) are real. The 3-persona roleplay against the prototype is **synthetic** — never let "tested across three personas" read as user validation. Lena's stated bar is real users.
- **Name descopes and scope changes before the reader finds them.** Cheaper to confess than to be caught.
- **Calibrate per reader** using `08-stakeholders/`: Raj wants async bullets and no live surprises; Lena wants artifacts and user voice (and the Comeback screen was *her* idea, redesigned without her in the room); Marcus wants the ask in sentence one, one page, every number tied to Day-7.

## Workspace Map

The numbered folders are the certification's module scaffolding. **The real artifacts drifted out of them** — see `workspace-audit.md`. Where to look:

| Path | What's there |
|---|---|
| `01-orient/` | `project.md` (PRD skeleton), `strategy.md`, `change_log.md` (decision log — stale after 2026-09-30) |
| `02-research/` | `interview-synthesis.md`, `nps-analysis.md`, `competitive-matrix.md` |
| `03-build/prototype/` | `index.html` — clickable Comeback flow + `README.md` (the build brief and 7 interview decisions) |
| `05-decide/` | `metric-findings.md` (superseded on segment choice — see above) |
| `07-docs/` | Catch-all for Modules 3–5 outputs: `prd.md`, `decision-brief.md`, `pm-brief.md`, `hypothesis.md`, `triad-session.md`, `spec-readiness.md`, `design-review.md`, `qa-checklist.md`, `objection-log.md`, `codebase-summary.md`, `recommendation-memo.md`, `presentation.md`, `presentation-notes.md` |
| `08-stakeholders/` | `marcus.md`, `raj.md`, `lena.md` — reader models. Read these *before* writing anything they'll read. Legend: 📁 cited · 🧩 given · 💭 inferred (verify) |
| `data/` | 5 CSVs + `metric-diagnosis.md` (canonical analysis) + `experiment-design.md`. Booleans are the **strings** `'true'`/`'false'` — compare against `'true'` |
| `skills/` | `stakeholder-prd/SKILL.md`, `weekly-status/SKILL.md` (generic 4-section), `weekly-status.md` (stakeholder-calibrated variant — confusing name collision, see audit) |
| `*/[module].md` | `orientation.md`, `research.md`, `build.md`, `collaboration.md`, `decide.md`, `systems.md` — **still blank `___` templates.** Ignore as sources; they're scaffolding, not content |

Run the prototype: `.claude/launch.json` serves `03-build/prototype/` on port 4173.

## Glossary

| Term | Meaning |
|------|---------|
| **Comeback screen** | The full-screen takeover shown on streak break. Lena's original concept; materially redesigned in the prototype. |
| **Freeze** vs **restore** | Freeze = a flag set *before* the day boundary that prevents a reset (what Raj scoped). Restore = retroactively recovering a streak value the system already zeroed (what the prototype does). Not the same ask. |
| **Fragile middle zone** | Day ~4–30. The habit hasn't formed but loss aversion has. Pride to lose, nothing new to gain. |
| **Breaker / non-breaker** | `broke_streak_week1` true/false. The pilot's lift is in non-breakers — the segment we weren't aiming at. |
| **The descope** | Marcus approved 3 things; 1 was built. Recovery flow only; milestone moments and the state-aware home screen are not in the prototype. |
| **Triad** | PM + Raj (eng) + Lena (design). |
| **D-1 / D-7 / D-30** | Retention at day 1, 7, 30 after install. D-7 is this project's core metric. |
| **Coach, not scorekeeper** | The framing users asked for in NPS. Drove the zen/acceptance tone in the prototype copy. |
| **Roleplay test** | Synthetic persona testing against the prototype. Not user validation. Always labeled. |
