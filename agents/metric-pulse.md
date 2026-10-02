---
name: metric-pulse
description: Monday-morning Slack digest of Day-7 retention and streak-break rate, split by acquisition channel, with a ±2-pt week-over-week alert. Runs nightly; posts only on Monday.
---

# Agent Spec — metric-pulse

**Script:** [`metric_pulse.py`](metric_pulse.py) · **Runs:** nightly 02:00, posts Monday 08:00
**Status:** verified manually against `data/` on 2026-10-02. Slack delivery **not yet wired** — see §6.

---

## 0. Read this before anything else — three things the spec assumed that the data does not support

Stated up front rather than buried, because two of them change how you should read the output.

**a. The ±2-pt threshold is below the resolution of a channel cell.** A cohort week in this dataset is 100 users split ~34/34/32 across organic/paid/referral. One user moves a channel rate by ~3 points. So *every* per-channel move is at least 3 pts, and a 2-pt threshold fires on a single user changing their mind. The agent still prints the channel split, but each line is tagged `(n=34, directional)`, and a channel can only be promoted to **← watch this** if its Day-7 drop is either on a cell of n≥100 or statistically significant on its own thin n (two-proportion test, p<0.05). This is the one design decision I'd want you to push back on if you disagree. At the overall level (n=100/week) ±2 pts is still too tight — the week-4→3 move of −4 pts carries p=0.533 — so the digest prints the p-value next to the headline and never calls an alert "significant" unless the test says so.

**b. 39% is not a week-over-week baseline.** It is the project brief's post-v2 Day-7 figure — the number we're trying to move back above 48%. The sample data's own Day-7 is 38.6% overall and 37 / 37 / 31 / 27 / 61% by cohort week, so no single week equals 39%. The digest therefore uses 39% as a **standing reference line** (`vs 39% baseline: −12 pts · target ≥48%`) and computes the alert delta against the *prior cohort week*. Conflating the two would have produced a permanent false alert.

**c. "Reply YES to trigger" cannot work over a webhook.** An incoming webhook is outbound-only; it has no way to receive a reply. The line ships as written because it's a useful pointer to the next action, but it is labelled as not-yet-wired in the message itself, so nobody replies YES into a void. §6b has what it would actually take.

**And one overlap worth naming:** [`agents/monday-retention.md`](monday-retention.md) already posts a Monday digest covering Day-7 and streak-break rate. `metric-pulse` differs by adding the channel split and the explicit ±2-pt alert, and by dropping sessions-per-user and push opens. **Two Monday digests to the same channel is one too many** — pick one before scheduling, or merge the channel split into `monday-retention`. My recommendation: keep `monday-retention` as the standup digest and run `metric-pulse` only if channel attribution is a live question, which today it isn't.

---

## 1. What it does

| Metric | Computed as | Source |
|---|---|---|
| Day-7 retention | `day_7 == 'true'` / cohort size | `retention.csv` |
| Streak-break rate | `broke_streak_week1 == 'true'` / cohort size | `retention.csv` |
| Channel split | both of the above, grouped by `acquisition_channel` | `users.csv` joined on `user_id` |

Booleans in these CSVs are the **strings** `'true'`/`'false'`; every predicate compares against `'true'`.

"Last week" means the prior cohort week. Cohorts here start exactly 7 days apart on Mondays, 100 users each, so cohort-over-cohort *is* week-over-week. The agent takes the two highest `cohort_week` values present.

### Guards

- **Alert threshold ±2 pts**, as specified, on both headline metrics — with the p-value printed beside it so a loud arrow and a weak result can't be confused.
- **The pilot week cannot be reported as news.** Week 5 is the only cohort split `comeback`/`control`, so its Day-7 is +34 pts. Any week where a variant appears on one side of the comparison and not the other is flagged **confounded**, and the Top signal becomes "this is the experiment, read it from `data/metric-diagnosis.md`" instead of a channel story.
- **Channel reliability gate** — see §0a.
- **It will say "nothing happened."** No qualifying channel move produces *"No channel move clears significance or a reliable cell size… Nothing to action from the channel split this week."* It never invents a culprit.
- **Unknown or one-sided channels are surfaced, not swallowed.** A channel value outside organic/paid/referral is reported in *Read with care* and still counted in the total; a channel present in only one of the two weeks is dropped from the breakdown with a note.
- **Orphan rows are a hard error.** A `user_id` in `retention.csv` with no row in `users.csv` can't be attributed to a channel, so the run exits 1 rather than quietly under-counting a cell.

---

## 2. The Slack message template

The script emits Slack `mrkdwn` as a single `text` field, so it works unchanged with an incoming webhook, `chat.postMessage`, or an n8n Slack node. Substitutions in `{}`; blocks in `[]` appear conditionally.

```
📊 *Streakly Retention Pulse, {Day Mon D}*

*Day-7 retention: {d7}%* ({↑|↓|→} {N pts vs last week|flat})[ ⚠️ ALERT|✅ IMPROVED|🔬 EXPERIMENT — not a weekly move]
_vs 39% baseline: {+/-N} pts · target ≥48% · {p-value}_

*Streak-break rate: {brk}%* ({↑|↓|→} {N pts vs last week|flat})[ ⚠️ ALERT|✅ IMPROVED]  _(lower is better)_

*By channel* (Day-7):
• {Channel}: {rate}% ({↑|↓|→} {…})[ ← watch this][  _(n={N}, directional)_]
  … one line per channel, fixed order: organic, paid, referral

*Top signal:* {one rule-based sentence — names a thing to inspect, decides nothing}

[*Read with care*
• {confound}
  … block omitted entirely when there is nothing to caveat]

*Next:* run anomaly diagnosis? Reply YES to trigger. _(not yet wired — see §6)_

_Cohort week {cur} vs week {prev} · n={n_cur} / {n_prev} · alert threshold ±2 pts · generated by agents/metric_pulse.py_
```

Template rules:

- **Headline first, channel breakdown second, signal third.** A reader on a phone gets the whole story in the first two lines.
- **No bare percentages.** Every rate carries its comparison; the headline also carries its distance from the 39% baseline and its p-value.
- **The badge carries direction, not just magnitude.** A threshold crossing is `⚠️ ALERT` only when it crossed the *wrong* way; a favourable crossing is `✅ IMPROVED`. Each metric declares which way is better (`BETTER` in the script: Day-7 up, streak-break down), and streak-break carries `_(lower is better)_` inline. Without this, a falling streak-break rate — unambiguously good — wore a warning triangle, and the reader had to already know which way was better for each metric.
- **In a confounded week the test's primary metric gets neither badge**, just `🔬 EXPERIMENT — not a weekly move`. A green tick beside the pilot's +34 pts would be the agent reporting the experiment back as a good week, which is the failure the confound guard exists to prevent. Streak-break keeps its badge: it's set in week 1, before the Comeback screen can fire, so the test can't move it.
- **`← watch this` marks exactly one channel, at most.** Two "watch this" markers means neither gets watched.
- **The caveat block disappears when empty** rather than printing "None" — so its presence is itself a signal.
- **No `@here`, no `@channel`.** This is a digest, not a page. Paging someone is a separate branch with a much higher bar.
- **The footer always states n and the threshold.** It's what stops a 2-pt move being quoted in a meeting as a trend.

---

## 3. Running it manually to verify

In this order. Nothing touches Slack until the last one.

```bash
python3 agents/metric_pulse.py --dry-run
```

Prints the digest. Writes nothing, sends nothing. This is the one to run while you're still reading the output critically.

```bash
python3 agents/metric_pulse.py --dry-run --max-week 4
```

Same, but pretends week 4 is the latest — gives you a **clean, non-experimental** week to check the channel logic against, since week 5 is confounded by the pilot.

```bash
python3 agents/metric_pulse.py
```

Adds a snapshot to `ops/agent/pulse/snapshots/`. Still no Slack.

```bash
SLACK_WEBHOOK_URL='https://hooks.slack.com/services/...' \
  python3 agents/metric_pulse.py --post --force-post
```

The only command that talks to Slack. `--force-post` overrides the Monday-only gate so you can test on any day. Point it at a DM to yourself the first time.

---

## 4. Test run against the Streakly snapshot

Verified output, real run, 2026-10-02, default (week 5 vs week 4):

```
📊 *Streakly Retention Pulse, Fri Oct 2*

*Day-7 retention: 61%* (↑ 34pts vs last week) 🔬 EXPERIMENT — not a weekly move
_vs 39% baseline: +22 pts · target ≥48% · p<0.001_

*Streak-break rate: 45%* (↑ 10pts vs last week) ⚠️ ALERT  _(lower is better)_

*By channel* (Day-7):
• Organic: 82% (↑ 53pts vs last week)  _(n=34, directional)_
• Paid: 58% (↑ 43pts vs last week)  _(n=33, directional)_
• Referral: 42% (↑ 5pts vs last week)  _(n=33, directional)_

*Top signal:* Week 5 is the pilot week — the Day-7 jump is the experiment, not a
channel or seasonality story. Read it from data/metric-diagnosis.md (treatment vs
control within the week), not from this week-over-week line.

*Read with care*
• week 5 is split across a live experiment (comeback/control) and week 4 is not —
  this week's movement is partly the test, not an organic weekly change
• channel cells are n≈33, where one user moves the rate ~3 pts — the ±2-pt
  threshold cannot distinguish a channel move from a single user. Per-channel
  lines are directional only

*Next:* run anomaly diagnosis? Reply YES to trigger. _(not yet wired — see §6)_

_Cohort week 5 vs week 4 · n=100 / 100 · alert threshold ±2 pts · generated by agents/metric_pulse.py_
```

**This is the single most important thing to verify in that output:** the +34 pts is the experiment, not a week. It is badged `🔬 EXPERIMENT`, not `✅` — a green tick there would be the agent congratulating itself on the test. Week 5's organic Day-7 of 82% is the treatment arm, not a channel win. The guard caught it and the Top signal says so — if a future run headlines a figure like this *without* the confound note, the guard has broken.

And the clean week, `--max-week 4` (week 4 vs week 3) — the run worth reading to judge the channel logic:

```
📊 *Streakly Retention Pulse, Fri Oct 2*

*Day-7 retention: 27%* (↓ 4pts vs last week) ⚠️ ALERT
_vs 39% baseline: -12 pts · target ≥48% · p=0.533_

*Streak-break rate: 35%* (↓ 10pts vs last week) ✅ IMPROVED  _(lower is better)_

*By channel* (Day-7):
• Organic: 29% (→ flat)  _(n=34, directional)_
• Paid: 15% (↓ 26pts vs last week) ← watch this  _(n=34, directional)_
• Referral: 38% (↑ 16pts vs last week)  _(n=32, directional)_

*Top signal:* Paid Day-7 is down 26 pts (41% → 15%, p=0.015 — significant on a
thin cell). Check what changed in that channel last week — campaign, creative,
or targeting — before reading it as a product problem.

*Read with care*
• channel cells are n≈32, where one user moves the rate ~3 pts — the ±2-pt
  threshold cannot distinguish a channel move from a single user. Per-channel
  lines are directional only

*Next:* run anomaly diagnosis? Reply YES to trigger. _(not yet wired — see §6)_

_Cohort week 4 vs week 3 · n=100 / 100 · alert threshold ±2 pts · generated by agents/metric_pulse.py_
```

Note the honest pair in that run: ⚠️ ALERT on a −4-pt headline whose p-value is **0.533**. That is the ±2-pt threshold doing exactly what was specified and the p-value telling you not to believe it. Both appear, deliberately. Note too that the two headlines carry opposite badges from the same `↓` arrow — Day-7 down is bad, streak-break down is good.

Cross-check: the Day-7 figures by cohort week (37 / 37 / 31 / 27 / 61%) match [`05-decide/metric-findings.md`](../05-decide/metric-findings.md) independently. If a future run disagrees with that file, the data changed — investigate before believing the digest.

### Cases tested

| Case | How | Result |
|---|---|---|
| Confounded week | `data/` as-is (w5 vs w4) | Experiment flagged, Top signal redirects to the diagnosis doc ✓ |
| Clean week | `--max-week 4` | Paid promoted to `← watch this` on p=0.015 ✓ |
| Thin-cell suppression | n-gate alone, pre-fix | Suppressed a real 26-pt move → added the significance escape hatch ✓ |
| Direction-aware badges | w4 vs w3 | Day-7 −4 pts → `⚠️ ALERT`; streak-break −10 pts → `✅ IMPROVED`, same arrow ✓ |
| Badge suppressed when confounded | w5 vs w4 | Day-7 → `🔬 EXPERIMENT — not a weekly move`; streak-break keeps `⚠️ ALERT` ✓ |
| Missing CSV | `--data-dir` at an empty folder | `ERROR: missing required file …`, **exit 1** ✓ |
| Only one cohort week | week-1-only fixture | `ERROR: need at least 2 cohort weeks… Found: ['1']`, **exit 1** ✓ |
| Orphan `user_id` | `users.csv` with `u0001` removed | `ERROR: 1 user(s) … cannot be attributed to a channel`, **exit 1** ✓ |
| Nightly path | `--post` on a Friday | Snapshot written, nothing sent, reason on stderr ✓ |
| `--post`, no webhook | unset `SLACK_WEBHOOK_URL` | Warns on stderr, sends nothing, digest still printed ✓ |

Non-zero exit on failure is deliberate — a scheduler should be able to alert on a failed run rather than silently skipping a Monday.

---

## 5. Boundaries

- **Reads** `data/users.csv` and `data/retention.csv`. Writes **only** `ops/agent/pulse/`. Never touches a project artifact — not `CLAUDE.md`, not `metric-findings.md`, not the change log.
- **Network only with `--post`.** Default is a local dry run.
- **Never invents a number.** A channel with no data is omitted, not estimated.
- **Never upgrades a sub-threshold or thin-cell move to a finding**, and never reports "found nothing" as "nothing happened."
- **Suggests inspection, never decisions.** It points at a cut to pull. The rollout call stays human.

---

## 6. Wiring it up in the real world

### Recommendation

**Python + cron today; a developer ticket when the metric source goes live.** Not n8n.

The reasoning: the script is stdlib-only and reads two local CSVs, so cron costs about thirty seconds to set up and has no new dependency. n8n would be the right answer if this needed to *fan out* — several sources, retries, a Slack interactivity callback, non-engineers editing the flow — and none of that is true yet. The moment it stops reading a CSV and starts querying Amplitude or the warehouse, the credential handling and the query belong in a developer ticket for Raj's team, not in a PM-owned script on a laptop; that's also the point at which "nightly" starts to mean something.

### a. Python + cron (do this now)

```bash
# crontab -e
# nightly 02:00 — computes + snapshots; posts nothing unless it's Monday
0 2 * * * cd /Users/bauspland/Claude/product-school-training-main && \
  SLACK_WEBHOOK_URL='https://hooks.slack.com/services/...' \
  /usr/bin/python3 agents/metric_pulse.py --post >> ops/agent/pulse/cron.log 2>&1
```

One entry covers both halves of the schedule — the weekday gate inside the script is what makes Monday 08:00 delivery a property of the code rather than of two competing cron lines. If you'd rather the Monday post land at 08:00 exactly, add a second entry at `0 8 * * 1` and drop `--post` from the nightly one.

`cron` on macOS won't fire while the machine is asleep. If Monday 08:00 has to be reliable, use `launchd` with `StartCalendarInterval` (it catches up on wake), or move the job to GitHub Actions / n8n Cloud where the host is always up.

### b. What "Reply YES to trigger" would actually require

An incoming webhook can't hear a reply. Making that line real means a Slack app with: `chat:write` + `commands` scopes, a public HTTPS **interactivity request URL** that Slack can POST to, request-signature verification, and something on the other end authorised to run the anomaly-diagnosis agent. That's a developer ticket, not a cron tweak — and it's the right shape for n8n if you go that route, since n8n gives you the public webhook endpoint for free. Until then the line reads as a prompt to a human, which is what it is.

### c. Slack credentials

The Slack connector available to Claude Code in this workspace needs OAuth, which cannot be completed in a non-interactive session. The script therefore uses a plain **incoming webhook** from an env var — no OAuth dependency, and the right call for an unattended job anyway. Create the webhook in Slack, export `SLACK_WEBHOOK_URL`, keep it out of the repo.

### d. The honest caveat about scheduling this today

`data/` is a static export ending at cohort week 5. Scheduled now, the agent posts the identical digest every Monday forever, and every one of them headlines the pilot week's +34 pts. **Don't schedule it yet.** Run it manually, decide the `monday-retention` overlap (§0), and wire the schedule when the metric source is live. The logic, the guards and the message format are verified and won't need to change when the data does.
