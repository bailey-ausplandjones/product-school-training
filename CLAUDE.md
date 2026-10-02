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
5. Module 6 agent stack **built, none scheduled** — four agents + a learning loop, registered in [`agents/registry.md`](agents/registry.md). Open: two overlaps (§4.1), two known defects (§4.2), the `anomaly → weekly-insight` link is designed but unbuilt (§2), and `data/` is still a static export. The final presentation is still a placeholder.

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
| `skills/` | Reusable skills + the three recurring workflows — see the Workflows section below |
| `agents/` | The Comeback Coach stack. **Start at [`registry.md`](agents/registry.md)** — name, trigger, sources, delivery, owner, connection plan, known gaps, 6-month roadmap. Then the per-agent `.md` spec + `.py` script pairs, plus `fixtures/` (4 deterministic scenarios for the diagnostic loop) |
| `outcome-log.md` | `anomaly-diagnosis` output, one block per diagnosis. The blank **what actually happened** fields are the only thing that can calibrate its confidence scores — fill them in after running the SQL |
| `reports/` | `weekly-insight` output, `YYYY-MM-DD.md`, one per Friday run. **Cuts against the `ops/` convention** — see `agents/weekly-insight.md` §0c |
| `ops/` | Recurring weekly output: `status/`, `research/` (+ `research/inbox/` — drop raw feedback here), `competitive/`, `agent/` (agent digests + `agent/pulse/snapshots/`). Dated files, one per run. Module folders hold one-time artifacts; recurring output goes here |
| `*/[module].md` | `orientation.md`, `research.md`, `build.md`, `collaboration.md`, `decide.md`, `systems.md` — **still blank `___` templates.** Ignore as sources; they're scaffolding, not content |

Run the prototype: `.claude/launch.json` serves `03-build/prototype/` on port 4173.

## Recurring Workflows

Three one-paste workflows for my most repetitive tasks. Each runs with **no additional input from me** — don't ask me clarifying questions when I trigger one, just run it and report at the end.

| Trigger (I paste this) | Skill | Reads | Writes |
|---|---|---|---|
| `Run the Friday status workflow in skills/friday-status.md.` | [`skills/friday-status.md`](skills/friday-status.md) | `git log` for the week, `change_log.md`, `objection-log.md`, `spec-readiness.md`, and the open items in this file | `ops/status/YYYY-MM-DD-status.md` |
| `Run the research synthesis workflow in skills/weekly-research-synthesis.md.` | [`skills/weekly-research-synthesis.md`](skills/weekly-research-synthesis.md) | `ops/research/inbox/` + the `02-research/` baseline | `ops/research/YYYY-Www-research.md` |
| `Run the competitive pulse workflow in skills/competitive-pulse.md.` | [`skills/competitive-pulse.md`](skills/competitive-pulse.md) | WebSearch across the 5 tracked apps, diffed against `competitive-matrix.md` | `ops/competitive/YYYY-MM-DD-pulse.md` |

**Rules that apply to all three** — these are what make them safe to run unattended:

- **They write only their own new dated file.** If it already exists, stop and ask rather than overwrite.
- **They never edit a project artifact.** Not `competitive-matrix.md`, not `change_log.md`, not this file. Stale facts and proposed change-log rows get surfaced as a *proposal* at the end, and wait for me. This is the "ask before saving" rule holding even inside an autonomous run.
- **They never pad a quiet week.** Empty research inbox → no output at all. No competitor moves → a five-line file. "Found nothing" is never reported as "nothing happened."
- **They cut unverifiable claims.** The status workflow drops any item whose artifact isn't on disk and tells me what it cut; the pulse workflow won't report an undated claim as a move.

### Other skills

- [`skills/stakeholder-prd/SKILL.md`](skills/stakeholder-prd/SKILL.md) — writes a PRD grounded in this workspace's research and calibrated to the named people who have to approve it. Reads `08-stakeholders/` first.
- [`skills/weekly-status.md`](skills/weekly-status.md) — the stakeholder-calibrated status **templates** and the per-reader calibration table. `friday-status` gathers evidence, then formats with these. Edit calibration here, not in `friday-status`.
- [`skills/agent-learning-loop.md`](skills/agent-learning-loop.md) — weekly self-review of the agent stack's own track record. Scores past diagnoses in `outcome-log.md` as hit/miss/partial, computes hit rate by confidence band, proposes **one** heuristic update. Proposes only — never edits. **Returns "nothing to calibrate" until ~5 outcomes are filled in**, which is a human commitment, not a technical one.
- [`skills/weekly-status/SKILL.md`](skills/weekly-status/SKILL.md) — the older generic four-section version (Shipped / In Progress / Blockers / Next Week). Superseded for Streakly use by the two above; kept because it's the Module 1 artifact. **Name collides with `weekly-status.md`** — see `workspace-audit.md` item A4.

Nothing in `skills/` is in `.claude/skills/`, so none of it is invocable as a `/slash` command yet. The trigger prompts above are plain text pastes by design.

### Agents — the Comeback Coach stack

**Full detail lives in [`agents/registry.md`](agents/registry.md).** Read it before changing, scheduling, or quoting any agent. This section is the summary only.

Four agents, all built and verified, **none scheduled** — run them manually.

| Agent | Trigger | Covers | Writes |
|---|---|---|---|
| [`metric-pulse`](agents/metric-pulse.md) | Nightly 02:00, posts Mondays | Day-7 + streak-break, ±2pt alert, channel split | `ops/agent/pulse/` |
| [`anomaly-diagnosis`](agents/anomaly-diagnosis.md) | **Event — chained from the pulse on alert** | 5 gated steps: threshold → metric tree → 3 ranked hypotheses → SQL → log. 3 of 5 steps can stop | `outcome-log.md`, `ops/agent/anomaly/` |
| [`weekly-insight`](agents/weekly-insight.md) | Friday 16:00 | 3 done / 2 changed / 1 watch | `reports/YYYY-MM-DD.md` |
| [`monday-retention`](agents/monday-retention.md) | Monday 08:00 | Day-7, streak-break, sessions/user, push opens | `ops/agent/` |

Plus [`skills/agent-learning-loop.md`](skills/agent-learning-loop.md) — weekly self-review that scores past diagnoses hit/miss/partial and proposes **one** heuristic update. It proposes; it never edits.

**How they connect.** `metric_pulse.py --chain-anomaly` invokes the diagnostic loop only when the pulse alerts — a function call, not a file handoff, so `ALERT_PTS` stays defined once in `metric_pulse.py` and raising it moves the digest badge and the anomaly trigger together. `weekly-insight` and `anomaly-diagnosis` both import their metric layer from `metric_pulse.py`, so no two agents can disagree about a number. **`anomaly-diagnosis` → `weekly-insight` is designed but NOT built** — Friday's report currently can't see Tuesday's diagnosis (registry §2, Link 2).

**Six things to know before quoting any of them:**

- **39% is a reference line, not a diff target.** It's the brief's post-v2 figure. The data's Day-7 is 38.6% overall, 37/37/31/27/61% by cohort week — no week equals 39%. All four compare against the **prior cohort week**.
- **±2 pts is below the data's resolution.** Channel cells are n≈33 (one user ≈ 3 pts); at n=100, a −4-pt move carries p=0.533. Every agent prints the p-value next to the alert. **Read the p, not the arrow.**
- **Week 5 is confounded** and all four guard against headlining it. A +34-pt Day-7 move reported *without* a confound note means the guard has broken.
- **Confidence scores are ordinal weights, not probabilities.** At n=100 a hypothesis can clear the 6/10 gate on evidence no z-test would call significant; the output says so when it does. They stay uncalibrated until the outcome log has filled-in outcomes.
- **`anomaly-diagnosis` can't diagnose** push *delivery* (no `delivered`/opt-in column), release regressions (no deploy/version field), or anything "overnight" (`cohort_week` grain only). It generates those hypotheses when the pattern fits but marks them unconfirmable rather than emitting SQL that can't run.
- **`weekly-insight` can't report weekly NPS themes.** `02-research/nps-analysis.md` is an undated one-off of 10 comments. Weekly user signal comes from `ops/research/inbox/`, currently empty → the week is reported as quiet, never padded.

**Two overlaps and two defects are open** — registry §4.1 and §4.2. Nothing should be scheduled until the overlaps are resolved and `data/` is a live source rather than a static export ending at the pilot week.

## Glossary

| Term | Meaning |
|------|---------|
| **Comeback screen** | The full-screen takeover shown on streak break. Lena's original concept; materially redesigned in the prototype. |
| **Freeze** vs **restore** | Freeze = a flag set *before* the day boundary that prevents a reset (what Raj scoped). Restore = retroactively recovering a streak value the system already zeroed (what the prototype does). Not the same ask. |
| **Fragile middle zone** | Day ~4–30. The habit hasn't formed but loss aversion has. Pride to lose, nothing new to gain. |
| **Breaker / non-breaker** | `broke_streak_week1` true/false. The pilot's lift is in non-breakers — the segment we weren't aiming at. |
| **The descope** | Marcus approved 3 things; 1 was built. Recovery flow only; milestone moments and the state-aware home screen are not in the prototype. |
| **Triad** | PM + Raj (eng) + Lena (design). |
| **Metric tree** | The decomposition of Day-7 into behavioural drivers (streak-break, Day-1, sessions/user, push opens, goal-set). Day-7 is the thing decomposed, never a driver; channel is a *segmentation* of it, reported separately so movement isn't counted twice. |
| **Confidence gate** | `anomaly-diagnosis` step 3: the top hypothesis must score **above** 6/10 to earn SQL. Exactly 6 stops the loop. The score is a rule-based ordinal weight, not a probability. |
| **Outcome log** | `outcome-log.md`. One block per diagnosis that cleared the gate, with *what actually happened* left blank for a human. Those blanks are the only route from hand-tuned confidence weights to calibrated ones. |
| **D-1 / D-7 / D-30** | Retention at day 1, 7, 30 after install. D-7 is this project's core metric. |
| **Coach, not scorekeeper** | The framing users asked for in NPS. Drove the zen/acceptance tone in the prototype copy. |
| **Roleplay test** | Synthetic persona testing against the prototype. Not user validation. Always labeled. |
