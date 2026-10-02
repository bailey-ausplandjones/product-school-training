---
name: anomaly-diagnosis
description: Five-step gated diagnostic loop, chained to metric-pulse. Fires only on a >2pt Day-7 or streak-break move, decomposes the metric tree, ranks 3 hypotheses with confidence scores, emits confirming SQL, posts to Slack, and logs the call for later calibration.
---

# Agent Spec — anomaly-diagnosis

**Script:** [`anomaly_diagnosis.py`](anomaly_diagnosis.py) · **Trigger:** chained from [`metric-pulse`](metric-pulse.md), fires only on alert
**Status:** all four stop/pass conditions verified against committed fixtures on 2026-10-02. Slack delivery **not yet wired** — see §7.
**Fixtures:** [`agents/fixtures/`](fixtures/) — four scenarios, deterministic, regenerate with `python3 agents/fixtures/make_fixtures.py`

---

## 0. Read this first — what the data can and cannot diagnose

**a. Two drivers in your sample output don't exist in the schema.** `nudges.csv` has `opened` and `acted_on` but **no `delivered` column and no opt-in field**. So:

- "Push opt-in rate: 54% → 51%" is not computable. It isn't in the metric tree.
- "Push notification delivery issue" is **not confirmable at all**. Open rate cannot separate "the push never arrived" from "the push arrived and was ignored." The agent still generates that hypothesis when push opens move, but marks it `⚠️ not confirmable from current data`, caps what it claims, and emits the engagement proxy query with the limitation in a header comment. It will never rank a hypothesis it can't test without saying so.
- Same for "copy regression after last deploy": there is **no deploy, release-tag or app-version column anywhere in the export**. That hypothesis is unfalsifiable here. It's kept in the catalogue at a deliberately low base score (2/10, so it can never clear the gate alone) purely so it isn't silently dropped, and its "SQL" is a comment telling you to look in the deploy log instead.

**b. The SQL runs against assumed table names.** Columns are real — they mirror `data/*.csv`. Table names (`streakly_users`, `streakly_retention`, `streakly_sessions`, `streakly_notifications`) are a guess, and every emitted block says so in a footer. Re-point them before running. This is a one-line change per template once the warehouse is known, and a natural thing to hand Raj.

**c. The confidence score is an ordinal weight, not a probability.** It's a transparent sum of rule-based points (§4). A 7/10 means "this pattern matched more corroborating rules than the others," not "70% likely." At n=100 per cohort, **a hypothesis can clear the 6/10 gate on evidence no z-test would call significant** — the 4-point-drop test does exactly this, with a top driver at p=0.256. The agent detects that case and prints an explicit caveat rather than letting the score imply statistical support. Until the outcome log has real outcomes in it, these scores are uncalibrated by construction; §6 is the mechanism that eventually fixes that.

**d. It diagnoses cohort-over-cohort, not "overnight."** Your sample says "dropped 4pts overnight," but `retention.csv` is keyed on `cohort_week` — Day-7 retention for a cohort isn't even knowable until 7 days after signup. The smallest honest unit here is the cohort week. A true overnight trigger needs daily event data the export doesn't have.

---

## 1. The chain

```
metric_pulse.py --chain-anomaly
        │
        ├── no alert (|Δ| ≤ 2pts) ──→ prints the pulse digest, logs "no alert", STOPS
        │
        └── alert ──→ anomaly_diagnosis.run()
                         └── the five gated steps below
```

The gate is the pulse agent's own `alert` flag, so the threshold is defined in exactly one place (`ALERT_PTS` in `metric_pulse.py`). The diagnostic loop cannot fire on a quiet week, and raising the threshold in one file raises it for both agents.

```bash
python3 agents/metric_pulse.py --chain-anomaly --dry-run
```

Standalone runs are also supported — `anomaly_diagnosis.py` re-checks the threshold itself as step 1, so invoking it directly can't bypass the gate.

---

## 2. The five steps, and exactly what passes and what stops

| Step | Condition to proceed | On pass | On stop |
|---|---|---|---|
| **1. Threshold check** | Day-7 **or** streak-break moved **> 2.0 pts** week over week | Names the trigger and continues | Appends one line to `ops/agent/anomaly/run-log.md` and exits. No Slack, no outcome-log entry |
| **2. Metric tree decomposition** | **≥ 2 of 5 drivers** moved past their own thresholds | Continues with the driver set + channel concentration | Posts the **⚪️ INCONCLUSIVE** variant. No hypotheses, nothing logged to the outcome log |
| **3. Hypothesis generation** | Top hypothesis confidence **> 6/10** (strictly above) | Continues with the ranked top 3 | Posts the **🟡 LOW CONFIDENCE** variant. No SQL, nothing logged to the outcome log |
| **4. SQL + Slack** | — | Emits the confirming query for hypothesis 1 and posts the **🔍 full diagnostic** | — |
| **5. Outcome log** | — | Appends ranked hypotheses, confidences, SQL, and two `_TBD_` placeholders to `outcome-log.md` | — |

**Which metric becomes the headline trigger.** Day-7 leads whenever it alerted, even if streak-break moved further. An earlier build took the biggest absolute mover, which headlined streak-break at +7pts over a Day-7 drop of −4 — wrong twice over: streak-break is a *driver inside the metric tree*, so promoting it to the trigger double-counts it, and it buries the metric the project is actually measured on. Streak-break only becomes the trigger when Day-7 itself didn't alert.

**Three of the five steps end in a stop, and a stop is a result.** Every stop variant says which step it stopped at and why, and the two early stops deliberately write **nothing** to the outcome log — that log is for calls the agent actually made. An entry there means a hypothesis was committed to; an inconclusive week shouldn't pollute the calibration record.

### The metric tree — 5 drivers, each with its own move threshold

| Driver | Source | Threshold to count as "moved" |
|---|---|---|
| Streak-break rate | `retention.broke_streak_week1` | ±3 pts |
| Day-1 retention | `retention.day_1` | ±3 pts |
| Sessions per user, week 1 | `sessions.csv` joined to cohort | ±10% relative |
| Push open rate | `nudges.opened` | ±3 pts |
| Goal-set rate within 24h | `users.goal_set_date` | ±3 pts |

Day-7 is **not** a driver — it's the metric being decomposed. Channel is reported separately as *where it concentrates*, because a channel split is a segmentation of Day-7, not an independent behavioural driver; mixing the two would let the same movement be counted twice. The ≥2 condition applies only to the drivers.

Thresholds are ±3 pts because one user in a 100-person cohort is 1 pt, and a 1–2 pt driver move is a couple of people. If `sessions.csv` or `nudges.csv` is missing, those drivers are skipped, the decomposition proceeds on what's left, and the output says which were unavailable.

---

## 3. Slack formats

### 🔍 Full diagnostic (steps 4–5 reached)

```
🔍 *Streakly Anomaly Detected*, {Day Mon D, H:MMam}

*Trigger:* {metric} {dropped|rose} {N}pts ({prev}% → {cur}%) week over week — cohort week {c} vs {p}, n={}/{}, {p-value}

*Metric tree decomposition:*
• {driver}: {prev}% → {cur}% ({↑|↓|→} {N}pts, {p})[  _(below its move threshold)_]
  … all 5 drivers, movers and non-movers alike

*Where it concentrates (Day-7 by channel):*
• {Channel}: {prev}% → {cur}% ({+/-N}pts)[ _(not significant)_]

*Top 3 hypotheses* _(confidence is a rule-based score, not a probability)_:
1. *{title}* — *{N}/10*[ ⚠️ not confirmable from current data]
    _{basis — the drivers that earned the score}_
    [_⚠️ {why it can't be confirmed}_]

*SQL to confirm hypothesis 1 ({key}):*
```{sql}```
[⚠️ *The top hypothesis is not confirmable from the current export.* …]
_Table names are assumed and mirror `data/*.csv`. Re-point them before running._

[*Read with care*
• {caveat}]

_Logged to outcome-log.md. Run the query and reply with the output — I'll interpret.
The 'what actually happened' field stays blank until you do._
```

### 🟡 Low confidence (stopped at step 3)

```
🟡 *Streakly Anomaly — LOW CONFIDENCE*, {Day Mon D, H:MMam}

*Trigger:* {…}

*Stopped at step 3.* Best hypothesis scored *{N}/10*, at or below the 6/10 gate —
so no SQL and no diagnosis. The move is real; the explanation isn't supported yet.

*What moved:*
• {only the drivers that moved}

*Candidates, none strong enough to act on:*
1. {title} — {N}/10

_No SQL emitted and nothing logged to the outcome log — there is no call to score.
Next step is a human looking at the cut, not a query._
```

### ⚪️ Inconclusive (stopped at step 2)

Same header shape; states that only *N* drivers moved against a requirement of 2, prints the full tree with `← the only mover` marked, and explains that a single-driver move is as likely to be noise as a cause.

**Format rules across all three:** the trigger line always carries n and a p-value; the full tree is always printed, non-movers included, so the reader can see what *didn't* move; confidence is always labelled as a score rather than a probability; no `@here`; and every variant names the step it stopped at, so "why didn't I get SQL" is never a mystery.

---

## 4. How confidence is scored

Six hypotheses in the catalogue, each triggered by a driver pattern, each scoring a transparent sum. Capped to 1–10. Ties break on a fixed priority order so two runs on the same data never reorder.

| Hypothesis | Triggered by | Points |
|---|---|---|
| Streak-break punishment | streak-break up | 4 base, +2 if Day-7 is down, +2 if the break move is significant, +1 if ≥5 pts |
| Engagement depth collapse | sessions/user down ≥10% | 3 base, +2 if Day-7 is down, +1 if streak-break also rose, +1 if ≥20% drop |
| Notification channel decay | push opens down | 3 base, +2 if sessions also down, +1 if significant, +1 if ≥5 pts · **not confirmable** |
| Activation gate | goal-set rate down | 3 base, +2 if Day-1 is flat while Day-7 drops, +1 if significant |
| Cohort quality shift | Day-1 down, or a channel concentrating the drop significantly | 3 base, +2 if Day-1 moved, +2 if a channel is significant, +1 if Day-1 is significant |
| Release regression | ≥2 drivers moved | 2 base, +1 if ≥3 drivers · **not confirmable — no deploy data exists** |

Read the table as the whole model: there's no hidden weighting, and the score is reproducible by hand from the driver lines in the Slack post. The point of printing the basis next to each hypothesis is that you can audit the arithmetic.

**The gate is `> 6`, strictly.** A score of exactly 6 stops the loop — that's the `low-confidence` fixture, where every candidate tops out at 6 because two drivers moved but both weakly (streak-break +3 pts, under the +5 bonus; sessions −15%, under the −20% bonus).

---

## 5. Verified test runs

All four scenarios are committed fixtures. Deterministic — no randomness, every rate produced by index arithmetic — so these numbers reproduce exactly:

```bash
python3 agents/fixtures/make_fixtures.py        # regenerate (idempotent)
```

| Fixture | Week 1 → Week 2 | Expected | Result |
|---|---|---|---|
| `anomaly-4pt-drop` | D-7 39%→35%, break 22%→29%, sessions 4.1→3.2, push open 54%→50% | runs to step 5 | **Step 5** ✓ |
| `subthreshold-1pt` | D-7 39%→38%, break 22%→23% | stops at step 1 | **Step 1** ✓ |
| `single-driver` | D-7 39%→35%, break 22%→29%, everything else flat | stops at step 2 | **Step 2** ✓ |
| `low-confidence` | D-7 39%→36%, break 22%→25%, sessions 4.1→3.5 | stops at step 3 | **Step 3** ✓ |

### The headline test — 4-point Day-7 drop, end to end

```bash
python3 agents/anomaly_diagnosis.py \
  --data-dir agents/fixtures/anomaly-4pt-drop \
  --dry-run --now 2026-05-13T08:47
```

Step trace:

```
STEP 1 threshold check (> 2 pts): PASS — 2 metric(s) over threshold
  trigger: Day-7 retention dropped 4pts (39% → 35%) week over week — cohort week 2 vs 1, n=100/100, p=0.558
STEP 2 metric tree (>= 2 movers): PASS — 3 of 5 drivers moved
STEP 3 hypotheses (top > 6/10): PASS — top is 7/10 (streak_punishment)
STEP 4 SQL + Slack: PASS — query for 'streak_punishment'
STEP 5 outcome log: SKIPPED (--dry-run) — would append to outcome-log.md
```

Slack output:

```
🔍 *Streakly Anomaly Detected*, Wed May 13, 8:47am

*Trigger:* Day-7 retention dropped 4pts (39% → 35%) week over week — cohort week 2 vs 1, n=100/100, p=0.558

*Metric tree decomposition:*
• Streak-break rate: 22% → 29% (↑ 7pts, p=0.256)
• Day-1 retention: 91% → 91% (→ flat, p=1.000)  _(below its move threshold)_
• Sessions per user, week 1: 4.1 → 3.2 (↓ 22%)
• Push open rate: 54% → 50% (↓ 4pts, p=0.689)
• Goal-set rate within 24h: 78% → 78% (→ flat, p=1.000)  _(below its move threshold)_

*Where it concentrates (Day-7 by channel):*
• Organic: 32% → 24% (-9pts) _(not significant)_
• Paid: 42% → 39% (-3pts) _(not significant)_
• Referral: 42% → 42% (+0pts) _(not significant)_

*Top 3 hypotheses* _(confidence is a rule-based score, not a probability — see §4 of the spec)_:
1. *Streak-break punishment — more users hit the all-or-nothing reset, and the reset is converting to churn* — *7/10*
    _streak-break rate 22%→29% (p=0.256), moving with Day-7 in the expected direction_
2. *Engagement depth collapse — users who stayed are opening the app less, so the habit never forms* — *7/10*
    _sessions/user 4.1→3.2 (22% drop) on n=100_
3. *Notification channel decay — sends are reaching fewer users, removing the route back to a lapsing user* — *5/10* ⚠️ not confirmable from current data
    _push open rate 54%→50%, and sessions/user down 22% alongside it_
    _⚠️ streakly_notifications has `opened` but no `delivered` or opt-in column — open rate cannot separate a delivery failure from users ignoring the push. Confirming a *delivery* problem needs a column the export doesn't have._

*SQL to confirm hypothesis 1 (streak_punishment):*
[the break-rate × Day-7 segmentation query — see outcome-log.md for the full text]

*Read with care*
• channel cells are n≈33, where one user moves the rate ~3 pts — the ±2-pt threshold cannot distinguish a channel move from a single user. Per-channel lines are directional only
• no driver in this decomposition reaches significance (best is 0.26) — the 7/10 score is a rule-based weight on the pattern, not statistical support for it

_Logged to outcome-log.md. Run the query and reply with the output — I'll interpret. The 'what actually happened' field stays blank until you do._
```

**Three things in that run worth your attention:**

1. **The top two hypotheses tie at 7/10.** The priority order breaks it deterministically, but a tie is real information: the data genuinely doesn't separate "more people broke their streak" from "people engaged less." A 7/10 with a 7/10 right behind it is not a confident call, and reading it as one is the main way this agent could mislead you.
2. **The last caveat is the honest headline.** Nothing in the decomposition reaches significance — best p is 0.26 — yet the loop passed its gate and emitted SQL, because the gate is a rule score and the spec set it at 6/10. Working as specified; just don't mistake the badge for evidence.
3. **Hypothesis 3 is marked unconfirmable** and still ranked, with the missing-column reason inline. That's the design: don't silently drop a plausible mechanism, don't pretend you can test it.

### Chain test

```bash
python3 agents/metric_pulse.py --chain-anomaly --dry-run                                    # alert → invokes
python3 agents/metric_pulse.py --chain-anomaly --dry-run --data-dir agents/fixtures/subthreshold-1pt   # no alert → doesn't
```
→ `[--chain-anomaly] d7, brk over threshold → invoking agents/anomaly_diagnosis.py`
→ `[--chain-anomaly] no alert — anomaly diagnosis not invoked.` ✓

---

## 6. The outcome log, and why the placeholder is the point

Step 5 appends to [`outcome-log.md`](../outcome-log.md): the trigger, the drivers that moved, all three ranked hypotheses with scores, the SQL issued, and two fields left blank — **What actually happened** and **Was the top hypothesis right?**

Those blanks are the only thing that can ever make the confidence scores mean something. Right now they're hand-tuned weights; a log with twenty filled-in outcomes tells you whether a 7/10 is right 70% of the time or 30%, and the weights in §4 become adjustable on evidence instead of taste. An entry with the field still blank is an **open call, not a result**.

Every entry records its **data source**, and a run against `agents/fixtures/` is tagged `[FIXTURE]` with a do-not-calibrate warning — so a test run can never be mistaken for a production call later. The file currently holds exactly one entry, from the 4-point-drop fixture, tagged accordingly.

**Path note:** `outcome-log.md` sits at the repo root as specified. Like `reports/`, that cuts against the `ops/` convention for recurring output — worth one decision, since it's a single constant.

---

## 7. Boundaries and wiring

- **Reads** `data/*.csv` (or `--data-dir`). **Writes** only `outcome-log.md` and `ops/agent/anomaly/run-log.md`. Never edits a project artifact.
- **Network only with `--post`.** Default is a local dry run. `--dry-run` writes nothing at all.
- **Never invents a driver or a hypothesis** outside the catalogue in §4, and never emits SQL for a hypothesis it has marked unconfirmable without the warning attached.
- **Never writes to the outcome log on an early stop.**
- **Suggests a query; never concludes.** The last line of every full diagnostic hands back to a human.

### Real-world wiring

Chain it to the pulse agent's existing nightly cron — one flag, no second schedule. The 9am-standup requirement is why the pulse runs nightly in the first place:

```bash
# crontab -e   → nightly 02:00; the pulse posts Mondays, the diagnostic posts whenever it fires
0 2 * * * cd /Users/bauspland/Claude/product-school-training-main && \
  SLACK_WEBHOOK_URL='https://hooks.slack.com/services/...' \
  /usr/bin/python3 agents/metric_pulse.py --post --chain-anomaly >> ops/agent/pulse/cron.log 2>&1
```

A 02:00 run lands the diagnostic in Slack ~7 hours before standup. If you want the 8:47am timestamp from your sample, move it to `0 8 * * *` — but then a failed run has no recovery window before standup, which is the argument for running it overnight and reading it with coffee.

**Recommendation: Python + cron now, developer ticket when the warehouse arrives.** The step logic, gates, and formats are the valuable part and they're verified. What's missing is all data-side: real tables for the SQL, a `delivered` column if push delivery is ever to be diagnosable, deploy metadata if release regressions are, and daily event grain if "overnight" is ever to be literal. Those are a ticket for Raj's team, not a cron tweak. n8n only earns its place if the Slack "reply with the output" loop becomes a real interactive callback — see [`metric-pulse.md`](metric-pulse.md) §6b, which has the same problem and the same answer.

**The honest caveat about scheduling this today:** `data/` is a static export ending at cohort week 5, which is the confounded pilot week. Chained and scheduled right now, the loop fires every single night on the same +34pt/+10pt experimental artifact, generates the same hypotheses, and appends a duplicate entry to the outcome log every 24 hours. **Run it manually until the metric source is live.** The fixtures are what let you test the loop in the meantime.
