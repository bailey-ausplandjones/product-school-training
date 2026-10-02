# Agent Registry — Comeback Coach

The Streakly PM agent stack: what each agent is, when it fires, what it reads, where it posts, and who owns it.

**Status: built and verified, none scheduled.** Every agent runs manually today. §4 is the honest list of what's blocking the schedule.

> Last updated: 2026-10-02. Keep this current — `CLAUDE.md` points here rather than duplicating it.

---

## 1. The registry

### A note on the count

You named three agents. **There are four.** `monday-retention` was built before `metric-pulse` and still exists, still runs, and still posts a Monday digest covering Day-7 and streak-break. It is in the table below because leaving it out of the registry is how an orphaned cron job happens two months from now. It needs a kill-or-keep decision — see §4.1.

| # | Agent | Trigger | Schedule | Data sources | Output format | Delivery | Owner |
|---|---|---|---|---|---|---|---|
| 1 | **metric-pulse** | Time | Nightly 02:00; posts **Mondays only** (weekday gate in code) | `data/users.csv`, `data/retention.csv` | Slack `mrkdwn` digest: headline Day-7 + streak-break with ±2pt badge, channel split, top signal | Slack webhook + `ops/agent/pulse/YYYY-MM-DD-pulse.md` + nightly JSON snapshot | PM — engagement squad |
| 2 | **anomaly-diagnosis** | **Event** — chained from #1 on alert | None of its own; fires only when #1 alerts | `data/{users,retention,sessions,nudges}.csv` | Slack diagnostic, 3 variants: 🔍 full / 🟡 low-confidence / ⚪️ inconclusive | Slack webhook + `outcome-log.md` + `ops/agent/anomaly/run-log.md` | PM — engagement squad; **SQL re-pointing: Raj (TBD, not yet asked)** |
| 3 | **weekly-insight** | Time | Friday 16:00 | `data/` (via #1's metric layer), `01-orient/change_log.md`, `ops/research/inbox/`, `02-research/nps-analysis.md`, `CLAUDE.md` | 3-2-1 Slack summary + a full versioned report | Slack webhook + `reports/YYYY-MM-DD.md` | PM — engagement squad |
| 4 | **monday-retention** | Time | Monday 08:00 pre-standup | `data/{users,retention,sessions,nudges}.csv` | Slack digest: headline → signal to watch → suggested action, + full metric table | Slack webhook + `ops/agent/YYYY-MM-DD-retention-digest.md` | **Unowned — decide in §4.1** |

### Per-agent detail

#### 1. metric-pulse — [spec](metric-pulse.md) · [script](metric_pulse.py)

| | |
|---|---|
| **Monitors** | Day-7 retention, streak-break rate; both split organic/paid/referral |
| **Alert rule** | \|Δ\| ≥ 2.0 pts week over week (`ALERT_PTS`, **the stack's single threshold definition**) |
| **Comparison basis** | Prior cohort week. 39% is a standing reference line, never a diff target |
| **Writes** | `ops/agent/pulse/` only |
| **Run it** | `python3 agents/metric_pulse.py --dry-run` |
| **Key constraint** | A channel cell is n≈33, where one user ≈ 3 pts. Per-channel lines are directional; `← watch this` is gated on significance |

#### 2. anomaly-diagnosis — [spec](anomaly-diagnosis.md) · [script](anomaly_diagnosis.py)

| | |
|---|---|
| **Fires on** | #1's `alert` flag. Re-checks the threshold itself as step 1, so a direct call can't bypass the gate |
| **Loop** | 5 gated steps; **3 of them can stop**: threshold (>2pts) → metric tree (≥2 of 5 drivers) → confidence (>6/10) → SQL → outcome log |
| **Metric tree** | streak-break, Day-1, sessions/user, push opens, goal-set-24h. Day-7 is decomposed, never a driver |
| **Writes** | `outcome-log.md` (full diagnoses only) + `ops/agent/anomaly/run-log.md` (every run, including stops) |
| **Run it** | `python3 agents/anomaly_diagnosis.py --data-dir agents/fixtures/anomaly-4pt-drop --dry-run` |
| **Key constraint** | Confidence is a rule-based ordinal weight, not a probability. At n=100 it can clear 6/10 on non-significant evidence — the output says so when it does |

#### 3. weekly-insight — [spec](weekly-insight.md) · [script](weekly_insight.py)

| | |
|---|---|
| **Shape** | 3 done / 2 changed / 1 watch. Never padded — short sections print short with a reason |
| **Done** | `change_log.md` rows this week, deduped, unverifiable entries cut and listed |
| **Changed** | Metric moves past ±2pts, imported from #1 |
| **Watch** | Ranked from `CLAUDE.md`'s open-items list. Never invented |
| **Writes** | `reports/YYYY-MM-DD.md`. Refuses to overwrite |
| **Run it** | `python3 agents/weekly_insight.py --dry-run` |
| **Key constraint** | **Cannot report weekly NPS themes.** `nps-analysis.md` is an undated one-off of 10 comments; it ships as standing baseline context in the report only. Weekly user signal comes from `ops/research/inbox/`, which is currently empty |

#### 4. monday-retention — [spec](monday-retention.md) · [script](monday_retention.py)

| | |
|---|---|
| **Shape** | Headline → signal to watch → suggested action, then the full metric table and a "read with care" block |
| **Metrics** | Day-7, streak-break, sessions/user, push open rate |
| **Writes** | `ops/agent/` |
| **Run it** | `python3 agents/monday_retention.py --no-save` |
| **Status** | **Overlaps #1 on the Monday slot.** Kill-or-keep decision pending |

### Shared conventions

- **Read-only on project artifacts.** No agent edits `CLAUDE.md`, the change log, the PRD, or any research file. Proposals go to a human.
- **Network only with `--post`.** Default is always a local dry run. `--dry-run` / `--no-save` writes nothing.
- **Stdlib only.** No pandas, no scipy, no installs. Booleans in `data/*.csv` are the strings `'true'`/`'false'`.
- **Non-zero exit on failure**, so a scheduler can alert rather than silently skip.
- **Never pad, never invent.** "Found nothing" is reported as found-nothing, not as nothing-happened.
- **Slack via incoming webhook** (`SLACK_WEBHOOK_URL`), not the OAuth connector — see §4.3.

---

## 2. Connection plan

```
                        ┌─────────────────────────────┐
         nightly 02:00  │       metric-pulse          │
         ───────────────▶  Day-7 + streak-break       │
                        │  ±2pt alert, channel split  │
                        └──────────┬──────────────────┘
                                   │
                    ┌──────────────┴───────────────┐
                    │                              │
            no alert │                       alert │  a["d7"]["alert"] or a["brk"]["alert"]
                    ▼                              ▼
         ┌──────────────────────┐      ┌────────────────────────────┐
         │ log "no alert", stop │      │    anomaly-diagnosis       │
         │ (Mon: digest posts)  │      │  5 gated steps             │
         └──────────────────────┘      └──────────┬─────────────────┘
                                                  │
                        ┌─────────────────────────┼──────────────────────┐
                        ▼                         ▼                      ▼
                 ⚪️ stop step 2            🟡 stop step 3          🔍 steps 4–5
                 (inconclusive)            (low confidence)        full diagnosis
                        │                         │                      │
                        └──── run-log.md ─────────┴──────┬───────────────┘
                                                         ▼
                                                  outcome-log.md
                                                  (+ human fills in
                                                   "what happened")
                                                         │
                        ┌────────────────────────────────┤
                        ▼                                ▼
         ┌──────────────────────────┐      ┌────────────────────────────┐
         │   weekly-insight         │      │   learning loop (weekly)   │
         │   Friday 16:00           │      │   scores past calls,       │
         │   3 done / 2 changed /   │      │   proposes ONE heuristic   │
         │   1 watch                │      │   update to CLAUDE.md      │
         └──────────────────────────┘      └────────────────────────────┘
```

### Link 1 — pulse → anomaly: **built and verified**

Mechanism: `metric_pulse.py --chain-anomaly` imports `anomaly_diagnosis` and calls `run()` only when its own alert flag is set.

```bash
python3 agents/metric_pulse.py --chain-anomaly --dry-run
```

Why it's a function call and not a file handoff: the threshold lives in exactly one constant (`ALERT_PTS` in `metric_pulse.py`), and both agents import the same metric functions. Raise it in one place and the trigger, the digest badge, and the diagnostic's step 1 all move together. A file-based handoff would have let them drift.

Verified both directions: alert → `[--chain-anomaly] d7, brk over threshold → invoking agents/anomaly_diagnosis.py`; quiet → `[--chain-anomaly] no alert — anomaly diagnosis not invoked.`

### Link 2 — anomaly → weekly-insight: **designed, NOT built**

This is the honest gap in the stack. `weekly-insight` reads metrics, the change log, and the research inbox. **It does not read `outcome-log.md`.** So a diagnosis that fired on Tuesday does not appear in Friday's report, and the "1 watch" bullet can't know that a hypothesis is sitting open and unconfirmed.

What it should do, in priority order:

1. **"Changed this week" gains a diagnosis line.** If `outcome-log.md` has an entry dated inside the week, surface it as `Anomaly diagnosed Tue: {trigger} → top hypothesis {title} ({N}/10), SQL issued, outcome TBD`. This is the single highest-value link: it closes the loop between "a number moved" and "here's what we think and whether we checked."
2. **"Watch next week" prefers an open call.** An outcome-log entry with `What actually happened` still blank is the most actionable thing in the workspace — a hypothesis someone committed to and nobody has confirmed. It should outrank the `CLAUDE.md` open-items list when one exists, with a basis line saying why.
3. **A standing count in the report footer.** `N diagnoses open, M scored` — so the report itself shows whether the calibration loop is being fed or quietly ignored.

Implementation shape: a `read_outcome_log(path, start, end)` function in `weekly_insight.py` parsing the `## {timestamp} — {trigger}` blocks, plus two new rules in `changed`/`watch` selection. Half a day. **Not started** — flagging it rather than letting the diagram imply it exists.

### What deliberately does *not* connect

- **No agent writes to another's output file.** Each owns one directory. A diagnosis never edits a pulse snapshot.
- **No agent edits `CLAUDE.md`.** The learning loop (§3) *proposes* a heuristic change and stops.
- **Nothing auto-escalates.** No `@here`, no paging, no auto-filed ticket. Every agent ends by handing a human a thing to look at.

---

## 3. The learning loop

Lives at [`skills/agent-learning-loop.md`](../skills/agent-learning-loop.md) — a one-paste weekly prompt, consistent with the other recurring workflows in `skills/`.

What it does: reads `outcome-log.md`, scores every diagnosis whose outcome a human has filled in as **hit / miss / partial**, computes the hit rate by confidence band, and proposes **exactly one** heuristic update to `CLAUDE.md` — which it writes nowhere and waits for approval on.

**It cannot do anything useful yet, and says so rather than pretending.** `outcome-log.md` holds one entry, from a fixture, with both outcome fields blank. First real run returns *"0 scored entries, nothing to calibrate"* and stops. It becomes useful at roughly 8–10 scored calls; with fewer than 5 it refuses to propose a heuristic at all, because a hit rate on 3 calls is noise. That's the honest timeline: **this loop is worth running from about month 2**, not week 1.

---

## 4. Known gaps — read before scheduling anything

### 4.1 Two unresolved overlaps

- **`metric-pulse` vs `monday-retention`** — same channel, same Monday morning, overlapping metrics. My recommendation: keep `monday-retention` as the standup digest, run `metric-pulse` on demand, since channel attribution isn't a live question. Alternative: fold the channel split into `monday-retention` and retire `metric-pulse`.
- **`weekly-insight` vs [`skills/friday-status.md`](../skills/friday-status.md)** — same day, same change log, overlapping "what shipped." My recommendation: `weekly-insight` is the Slack 3-2-1, `friday-status` is the written stakeholder update.

### 4.2 Two defects I know about and have not fixed

- **The ⚪️ INCONCLUSIVE variant can't reach Slack.** `anomaly_diagnosis.run()` returns the rendered text, but `post_to_slack` is only called in the step-3 and step-5 branches, and the chain in `metric_pulse.py` discards the return value entirely. So an inconclusive diagnosis prints to the terminal on a standalone run and vanishes on a chained one. The §3 format in the anomaly spec documents a delivery path that does not exist.
- **`weekly-insight`'s footer claims a save on `--dry-run`**, printing `Saved to reports/…` when nothing was written.

Both are small. Both are listed here so the registry isn't more confident than the code.

### 4.3 Everything blocking the schedule

| Blocker | Affects | What's needed |
|---|---|---|
| **`data/` is a static export** ending at cohort week 5 — the confounded pilot week | All four | A live metric source. Until then every scheduled run posts an identical digest about the experiment, and the anomaly loop would append a duplicate outcome-log entry nightly |
| **Slack webhook not created** | All four | A webhook URL in `SLACK_WEBHOOK_URL`. The OAuth connector can't be authorised from a non-interactive session, and a webhook is the right call for an unattended job anyway |
| **SQL table names are assumed** | #2 | Real warehouse names. Columns are real; `streakly_*` table names are a guess, flagged in every emitted block |
| **No `delivered` / opt-in column** | #2 | Push *delivery* is undiagnosable. Open rate can't separate "never arrived" from "ignored" |
| **No deploy / version field** | #2 | Release-regression hypotheses are unfalsifiable from this data |
| **`cohort_week` grain only** | #2 | "Overnight" anomaly detection needs daily event data. Day-7 isn't knowable until day 7 |
| **Research inbox empty** | #3 | Weekly user-signal bullets need raw feedback dropped in `ops/research/inbox/` |
| **Path conventions split** | #2, #3 | `reports/` and `outcome-log.md` sit outside the `ops/` convention. One decision, two constants |

**Recommended scheduling order once the metric source is live:** #1 nightly with `--chain-anomaly` (one cron line covers #1 and #2), then #3 on Fridays, then the learning loop monthly until there are enough scored calls to justify weekly.

---

## 5. Six-month roadmap — one agent per month

Each month assumes the previous month shipped. Sequenced so that **the first two months build the thing the rest depend on** — a live data source and a calibration signal — rather than adding surface area on top of a static CSV.

| Month | Agent | What it does | Why this month | Depends on |
|---|---|---|---|---|
| **1** | **Close the loop that exists** — no new agent | Build Link 2 (§2), fix the two defects in §4.2, resolve both overlaps in §4.1, create the webhook, point the stack at a live metric source | Four agents that nobody trusts are worth less than three that are wired, honest, and scheduled. **Resist adding an agent this month.** | Live metric source; Raj's data access |
| **2** | **Outcome Scorer** | Turns the learning loop from a manual prompt into a scheduled agent: scores filled-in outcome-log entries, tracks hit rate by confidence band, proposes heuristic updates, and nags when calls sit unscored for >14 days | Confidence scores are uncalibrated hand-tuned weights today. Every later agent that ranks or scores anything inherits that weakness. Fix the feedback loop before building more things that need it | ≥8 scored diagnoses, which is why it's month 2 and not month 1 |
| **3** | **Experiment Watchdog** | Monitors running experiments against `data/experiment-design.md`: days-to-power, whether the observed effect is tracking the MDE, p-value trajectory, and a hard stop when a pre-registered boundary is crossed. Refuses to report an underpowered read as a result | The live open question is a second, properly powered cohort. n=50/arm couldn't carry a rollout decision, and the current stack has no agent that would have *said* so | A running experiment; the second cohort being approved |
| **4** | **Stakeholder Brief Composer** | Takes any artifact and recalibrates it per reader using `08-stakeholders/` — Marcus gets the ask in sentence one on one page, Raj gets async bullets with no live surprises, Lena gets artifacts and user voice. Flags descopes *before* the reader finds them | The most repetitive judgement work in this workspace, and the rules are already written down. Needs the earlier months' outputs to have something worth briefing on | `08-stakeholders/` reader models (exist); months 1–3 output |
| **5** | **Research Synthesiser (live)** | Promotes `skills/weekly-research-synthesis.md` to a scheduled agent over a real feedback pipe — app-store reviews, support tickets, NPS waves — producing dated themes with movement week over week, and finally making `weekly-insight`'s user-signal bullet real | Fixes the gap named in §4.3: the inbox is empty because nothing fills it. This is the agent that fills it | A real feedback source wired to `ops/research/inbox/` |
| **6** | **Decision Memo Drafter** | Assembles a decision brief from the whole stack — metrics, scored diagnoses with their calibrated hit rates, experiment reads, reader calibration — and drafts the recommendation with every number tied to its source, plus an explicit "what would change my mind" | Only possible once the other five are feeding it. A memo drafter on month 1 would be a confident essay built on uncalibrated guesses | Months 1–5 |

### What the stack looks like at month 6

```
  LIVE DATA ──▶ metric-pulse ──alert──▶ anomaly-diagnosis ──▶ outcome-log
                     │                         │                   │
                     │                         │                   ▼
                     │                         │            Outcome Scorer
                     │                         │          (calibrates confidence,
                     │                         │           proposes heuristics)
                     │                         │                   │
                     ▼                         ▼                   ▼
              Experiment Watchdog      weekly-insight ◀──── calibrated weights
                     │                         │
                     └────────┬────────────────┘
                              ▼
                   Research Synthesiser (user signal)
                              │
                              ▼
                   Decision Memo Drafter ──▶ Stakeholder Brief Composer
                              │                        │
                              ▼                        ▼
                      a recommendation          Marcus / Raj / Lena,
                      with calibrated            each in their own
                      confidence                 register
```

The shape to notice: **it's a loop, not a pipeline.** Metrics → diagnosis → recorded call → scored outcome → adjusted heuristics → better next diagnosis. Everything else hangs off that spine. An agent stack that only fans out gets more confident over time; one with a scoring loop in it gets more accurate, and can tell you which.

### Three things that would make this roadmap wrong

Worth writing down now so they're checkable later:

1. **If the hit rate turns out low** — say 7/10 hypotheses are right under 40% of the time — the answer isn't more agents. It's deleting the confidence score and having the diagnosis present evidence without ranking it. Month 2 is what would reveal that.
2. **If nobody fills in the outcome log**, months 2 and 6 are both dead and the honest move is to cut the stack back to monitoring and reporting. The log is a human commitment, not a technical one.
3. **If the Comeback initiative is killed at Thursday's kickoff**, months 3 and 6 lose their subject. The monitoring and reporting agents survive a pivot; the experiment and decision agents don't.
