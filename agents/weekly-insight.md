---
name: weekly-insight
description: Friday 3-2-1 insight report — 3 bullets done, 2 bullets changed, 1 bullet to watch — from retention metrics, the change log, and user-signal sources. Saves to reports/YYYY-MM-DD.md and posts the summary to Slack.
---

# Agent Spec — weekly-insight

**Script:** [`weekly_insight.py`](weekly_insight.py) · **Runs:** Friday 16:00
**Status:** verified manually against the workspace on 2026-10-02. Slack delivery **not yet wired** — see §6.
**Sample output:** [`reports/2026-10-02.md`](../reports/2026-10-02.md) — a real run, not a mock-up.

---

## 0. Read this first — four places the spec met the workspace and had to bend

**a. "Top NPS themes *this week*" is not derivable, and the agent refuses to fake it.** `02-research/nps-analysis.md` is an undated one-off analysis of 10 free-text comments. There is no date column, no per-week dimension, and no second wave to diff against — so there is no honest way to call any theme "this week's." Reprinting the baseline's top 3 under a "Changed this week" heading would manufacture movement out of a static file, which is the exact failure the workspace rules forbid. What it does instead:

- The ranked baseline themes go in the **saved report**, under a heading that says in so many words *standing baseline, NOT this week*, and they never enter the 3-2-1 summary.
- "New user signal this week" is read from `ops/research/inbox/` — the place `CLAUDE.md` designates for raw feedback drops. **The inbox is currently empty**, so the report states that plainly and the week has no user-signal bullet. A quiet week is reported as quiet.
- If you want real weekly NPS themes, the inbox is the mechanism: drop the week's raw comments there and the bullet becomes available. That's also what [`skills/weekly-research-synthesis.md`](../skills/weekly-research-synthesis.md) already does properly, which raises (d) below.

**b. Two source paths in the spec don't exist as written.** `research/nps-analysis.md` is actually `02-research/nps-analysis.md`, and `change_log.md` is `01-orient/change_log.md`. Both are resolved to the real locations; the paths are constants at the top of the script.

**c. `reports/` cuts against the workspace convention.** `CLAUDE.md` puts recurring dated output under `ops/` (`ops/status/`, `ops/research/`, `ops/agent/`). The spec said `reports/YYYY-MM-DD.md`, so that's what it writes — but it is now a fourth place to look for recurring output. Worth a one-line decision: keep `reports/`, or move it to `ops/insight/` and match the rest. I'd move it; the path is one constant.

**d. This overlaps [`skills/friday-status.md`](../skills/friday-status.md) substantially.** That workflow also runs Friday, also reads `change_log.md`, also reports what shipped and what's blocked. The differences: `friday-status` is stakeholder-calibrated prose for named readers and writes to `ops/status/`; `weekly-insight` is a fixed 3-2-1 shape with metric movement and a Slack post. **Running both on a Friday produces two overlapping updates from the same change log.** Pick one, or let `weekly-insight` be the Slack-facing summary and `friday-status` the written update — but decide it, don't discover it.

---

## 1. Sources and what each contributes

| Slot | Source | Read as |
|---|---|---|
| Done this week | `01-orient/change_log.md` | Table rows dated Monday→today |
| Changed this week | `data/users.csv` + `data/retention.csv`, **via `agents/metric_pulse.py`** | Week-over-week moves past the ±2-pt threshold |
| Changed this week (user signal) | `ops/research/inbox/` | New feedback files only — empty inbox means no bullet |
| Standing context (report only) | `02-research/nps-analysis.md` | Ranked baseline themes, explicitly not movement |
| Watch next week | `CLAUDE.md` → "Open, genuinely unresolved" | The canonical open-decisions list |

**The metric layer is imported, not reimplemented.** `weekly_insight.py` imports `load`, `compute_week`, `analyse`, `confounds`, `fmt_p`, `BASELINE_D7` and `TARGET_D7` from [`metric_pulse.py`](metric_pulse.py). The two agents therefore cannot disagree about a number, and the ±2-pt threshold, the significance gate, the channel reliability floor and the pilot-week confound guard are all inherited rather than re-derived. Change a threshold in one place.

---

## 2. Selection rules — what makes it into 3-2-1

### Done (3 bullets)

Change-log rows inside the Monday→today window, newest first, with two filters:

- **Unverifiable entries are cut.** Any row citing a file that isn't on disk is dropped and listed in the report's *Cut from 'Done this week'* section with the reason. This implements the workspace's "cut unverifiable claims" rule.
  *An early build got this wrong and it's worth knowing why:* the change log cites artifacts the way a person writes them — "captured it in `project.md`" — not as repo-relative paths. Resolving only from the repo root marked `project.md` missing when it lives at `01-orient/project.md`, and silently cut a genuine accomplishment. `file_present()` now checks the exact path first, then a basename match anywhere in the tree.
- **Deduped by the artifact named**, so three entries about one file don't eat all three bullets.
- **Verified entries that lose only to the 3-bullet cap are still listed** in the report, under *Verified, but beyond the 3-bullet cap*. The cap should never read as "nothing else happened."
- **Never padded.** Fewer than 3 qualifying entries prints fewer, plus `_Only N change-log entries this week — not padded to 3._`

### Changed (2 bullets)

Metric moves that cleared ±2 pts, largest first. Day-7 and streak-break rate are candidates; a single channel can earn a bullet, but only if its move is **both** past the threshold **and** statistically significant, and only in a non-confounded week. Every bullet carries n and a p-value. Fewer than 2 qualifiers prints fewer, with a note. User-signal bullets come only from new inbox files — see §0a.

### Watch (1 bullet)

Read from `CLAUDE.md`'s open-items list. Ranking rule: an item the workspace itself flags as existential (`most likely to kill`, `gates the build`, `hard blocker`) wins; otherwise the first listed. The report records which rule fired under *Why that watch item*. **If the list is missing, the agent says so rather than inventing something to watch.**

---

## 3. Running it manually to verify

```bash
python3 agents/weekly_insight.py --dry-run
```

Prints the 3-2-1 summary. Writes nothing, sends nothing. Start here.

```bash
python3 agents/weekly_insight.py --dry-run --date 2026-10-09
```

Pretends it's next Friday — a **quiet week** with no change-log entries, so you can check that "Done this week" degrades honestly instead of reaching backwards for older material.

```bash
python3 agents/weekly_insight.py
```

Writes `reports/YYYY-MM-DD.md`. Still no Slack. **Refuses to overwrite an existing file for that date** (exit 1) — rerun with `--date`, or move the old one.

```bash
SLACK_WEBHOOK_URL='https://hooks.slack.com/services/...' \
  python3 agents/weekly_insight.py --post
```

The only command that talks to Slack, and it posts the 3-2-1 summary only — not the full report. Point it at a DM to yourself first.

---

## 4. Verified output — real run, 2026-10-02

The full saved report is at [`reports/2026-10-02.md`](../reports/2026-10-02.md). The Slack summary from that run:

```
📋 *Streakly Weekly Insight, Fri Oct 2*

*Done this week:*
• Ran a 3-persona roleplay test (Priya, Tom, Amara) against 03-build/prototype/index.html, asking each what the screen does…  _(Sep 30)_
• Findings: Priya and Tom both wanted the "restore" mechanic's rules made explicit (limits/frequency/cost)  _(Sep 30)_
• Fix applied: added "· Meditation" to the lesson screen's header label (previously just "60-Second Comeback" with zero track…  _(Sep 30)_

*Changed this week:*
• Day-7 retention up 34pts week over week, now 61% (cohort week 5 vs 4, n=100/100, p<0.001) — this is the pilot week, not an organic move
• Streak-break rate up 10pts week over week, now 45% (cohort week 5 vs 4, n=100/100, p=0.149) — adverse

*Watch next week:*
• Raj's feasibility re-scope. His "doable, no new data sources" yes was scoped against a one-tap freeze (a flag set before the day boundary)

*Read with care*
• week 5 is split across a live experiment (comeback/control) and week 4 is not — this week's movement is partly the test, not an organic weekly change
• channel cells are n≈33, where one user moves the rate ~3 pts — the ±2-pt threshold cannot distinguish a channel move from a single user. Per-channel lines are directional only
• 10 commits this week vs 5 change-log entries — the log is hand-maintained and behind, so 'Done this week' reflects the log, not the repo (last entry 2026-09-30)
• research inbox is empty — no new user signal this week, so no NPS theme is reported as movement (the NPS file itself is undated and cannot support a 'this week' claim)

_Saved to reports/2026-10-02.md · week of Sep 28–Oct 2 · generated by agents/weekly_insight.py_
```

**Four things in that output worth your attention before you trust it:**

1. **All three "Done" bullets are from one day (Sep 30) and one piece of work** — the roleplay test, its findings, and the fix. That's not a selection bug; it's what the change log actually contains for this week. The two Sep 28 entries are real and verified, and appear in the report's overflow section. The log being thin is the finding.
2. **The change log is 5 entries behind 10 commits**, and the caveat says so with the last-entry date. "Done this week" reflects the log, not the repo. If the log goes stale, this agent's first section goes stale with it — visibly, by design.
3. **The Day-7 bullet is tagged "this is the pilot week, not an organic move."** The +34 pts is the experiment. Inherited straight from `metric-pulse`'s confound guard.
4. **Streak-break "up 10pts — adverse" carries p=0.149.** Past the ±2-pt threshold, nowhere near significance. Both facts are printed; read the p.

### Cases tested

| Case | How | Result |
|---|---|---|
| Normal week | workspace as-is | 3 done / 2 changed / 1 watch, 4 caveats ✓ |
| Quiet week | `--date 2026-10-09` | `_Nothing logged in the change log this week._`, no reaching backwards ✓ |
| False-missing artifact | `project.md` cited in prose | Was wrongly cut → `file_present()` basename fallback added ✓ |
| Genuine missing artifact | fixture citing `totally-not-real.md` | Cut, with reason, listed in the report ✓ |
| Duplicate artifact | two rows citing `project.md` | Second deduped as "same artifact as an earlier bullet" ✓ |
| Overflow past the cap | 5 verified entries, 3 slots | 2 listed under *beyond the 3-bullet cap* ✓ |
| Overwrite guard | run twice on one date | `ERROR: … already exists. Refusing to overwrite`, **exit 1** ✓ |
| Missing change log | nonexistent path | `ERROR: missing required source …`, **exit 1** ✓ |
| Empty research inbox | current state | No user-signal bullet, stated as quiet, not padded ✓ |
| Watch-item ranking | `CLAUDE.md` 5 open items | Picks Raj's re-scope, basis recorded as the kill-risk rule ✓ |

Non-zero exit on failure is deliberate — a scheduler should alert on a failed run rather than silently skipping a Friday.

---

## 5. Boundaries

- **Reads** `data/`, `01-orient/change_log.md`, `02-research/nps-analysis.md`, `ops/research/inbox/`, `CLAUDE.md`. Writes **only** `reports/`.
- **Never edits a project artifact.** Not the change log, not `CLAUDE.md`, not the NPS analysis. If the change log needs a new row, that's a proposal for a human.
- **Never overwrites.** An existing report for that date is a hard stop.
- **Network only with `--post`.** Default is a local dry run.
- **Never pads a section** and never reports "found nothing" as "nothing happened."
- **Never invents a watch item**, and never presents an undated source as weekly movement.

---

## 6. Wiring it up in the real world

### Recommendation

**Python + cron now; a developer ticket when the sources go live.** Not n8n — same reasoning as [`metric-pulse`](metric-pulse.md) §6: stdlib only, local files, no fan-out and no retries needed. n8n earns its place when the sources become APIs (Amplitude for metrics, Jira or Linear for sprint completions, Delighted or Typeform for NPS) and someone other than you needs to edit the flow. At that point the change-log parsing becomes a Jira query and belongs in a ticket for Raj's team, not a PM-owned script.

```bash
# crontab -e   → Fridays at 16:00
0 16 * * 5 cd /Users/bauspland/Claude/product-school-training-main && \
  SLACK_WEBHOOK_URL='https://hooks.slack.com/services/...' \
  /usr/bin/python3 agents/weekly_insight.py --post >> reports/cron.log 2>&1
```

`cron` on macOS won't fire while the machine is asleep — if Friday 16:00 has to be reliable, use `launchd` with `StartCalendarInterval`, or run it where the host is always up (GitHub Actions, n8n Cloud).

**Slack credentials:** the Slack connector in this workspace needs OAuth, which can't be completed in a non-interactive session. The script uses a plain incoming webhook from `SLACK_WEBHOOK_URL` — no OAuth dependency, and the right call for an unattended job. Keep it out of the repo.

### The honest caveat about scheduling this today

Two of the three sources are frozen. `data/` is a static export ending at cohort week 5, so "Changed this week" returns the same two bullets every Friday forever — and both of them describe the pilot week. The change log is hand-maintained and already 5 entries behind. Scheduled now, this agent posts a near-identical digest weekly and its "Done this week" section degrades quietly as the log falls further behind.

**So: run it manually on Fridays for now.** Before scheduling, resolve three things — the `friday-status` overlap (§0d), the `reports/` vs `ops/` path (§0c), and whether the change log gets maintained or the "Done" section should read `git log` instead. The selection rules, the guards and the output shape are verified and won't need to change when the sources do.
