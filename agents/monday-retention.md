---
name: monday-retention
description: Monday-morning pre-standup agent. Compares Day-7 retention, streak-break rate, sessions per user, and push open rate for the latest cohort week against the prior week, then posts a three-part plain-English digest to Slack. Runs unattended on a schedule.
---

# Agent Spec — monday-retention

**Script:** [`monday_retention.py`](monday_retention.py) · **Runs:** Monday 08:00, before standup
**Status:** verified manually against `data/` on 2026-10-02. Slack delivery **not yet wired** — see §6.

---

## 1. What it does

Four metrics, latest complete cohort week vs. the prior one, reduced to three lines a human reads in ten seconds:

| Slot | Content | Rule |
|---|---|---|
| **Headline** | Day-7 retention, this week vs last, with the delta and a two-proportion p-value | Always Day-7. It is this project's core metric |
| **Signal to watch** | The biggest mover **other than** Day-7 | Never repeats the headline — that slot is already spent |
| **Suggested action** | One concrete thing to look at this week | Rule-based, points at a thing to *inspect*; it never decides anything |

Then the full metric table, and a "read with care" block listing every reason not to trust a number.

### Metrics tracked

| Metric | Computed as | Source | Upstream of the test? |
|---|---|---|---|
| Day-7 retention | `day_7 == 'true'` / cohort size | `retention.csv` | No — it's the test's primary metric |
| Streak-break rate | `broke_streak_week1 == 'true'` / cohort size | `retention.csv` | **Yes** — it's the test's *trigger*, set in week 1 |
| Sessions per user | sessions by cohort members / cohort size | `sessions.csv` + `users.csv` | No — the Comeback screen *is* a session |
| Push open rate | `opened == 'true'` / sends to cohort members | `nudges.csv` | No — `comeback_screen` is a treatment nudge type |

Booleans in these CSVs are the **strings** `'true'`/`'false'`, so every predicate compares against `'true'`.

---

## 2. The three design decisions that matter

**a. "Last week" means the prior cohort week.** Cohorts in this dataset start exactly 7 days apart, all on Mondays (`2026-04-06`, `-13`, `-20`, `-27`, `2026-05-04`), 100 users each. So cohort-over-cohort *is* week-over-week. The agent takes the two highest `cohort_week` values present and compares them.

**b. It also snapshots itself.** Every run writes `ops/agent/snapshots/YYYY-MM-DD-weekN.json`. Today that is belt-and-braces, because `data/` is a static export and every Monday returns the same answer. It matters the moment the data source becomes live: the snapshots are then a real time series, and the baseline can shift from "prior cohort in the same file" to "what I measured last Monday." The digest header states which baseline it used.

**c. It refuses to report the experiment back to you as news.** This is the one that took iteration. Week 5 is the only cohort split `comeback`/`control`, so its Day-7 is +34 pts — and a naive agent would headline that as a spectacular week. Three guards:

- Any week where a variant appears on one side of the comparison and not the other is flagged as **confounded**, in the output.
- In a confounded week, the "signal to watch" is drawn only from metrics tagged `upstream` — ones the test cannot mechanically move. Sessions-per-user and push opens are *inflated by construction* when the Comeback screen fires, so they are excluded. Streak-break rate survives: it is measured in week 1, before the screen ever shows.
- The suggested action then says don't read the headline as a trend, and names the upstream mover instead.

**d. A noise floor, so it can say "nothing happened."** Moves under ±3 pts (or ±0.3 sessions) are printed but tagged `(noise)`, can never be the signal, and produce the action *"No material movers. Spend standup on <the standing focus>."* The standing focus is the `STANDING_FOCUS` constant at the top of the script — edit it as the live open decision changes. The agent will not invent one.

---

## 3. Running it manually first

Verify before you schedule it. Three commands, in this order:

```bash
python3 agents/monday_retention.py --no-save
```

Prints the digest, writes nothing, sends nothing. This is the one to run while you are still reading the output critically.

```bash
python3 agents/monday_retention.py
```

Same, plus writes `ops/agent/YYYY-MM-DD-retention-digest.md` and a snapshot. Still no Slack.

```bash
SLACK_WEBHOOK_URL='https://hooks.slack.com/services/...' python3 agents/monday_retention.py --post
```

Only this last one talks to Slack. Point it at a DM-to-yourself or a scratch channel the first time.

### Verified output — real run, 2026-10-02

```
*Monday retention digest — 2026-10-02*
_Cohort week 5 vs week 4. Baseline is the prior cohort week in the same export._

*Headline — Day-7 retention:* 61.0% ▲ +34.0 pts vs last week (27.0%) (p<0.001, significant)

*Signal to watch — Streak-break rate:* 45.0% vs 35.0% last week, +10.0 pts

*Suggested action:* Don't read this week's Day-7 move as a weekly trend — week 5
is confounded by the live experiment. Pull the within-week segment split
(breakers vs non-breakers) before quoting it to anyone. The mover worth a look is
streak-break rate, +10.0 pts — the test cannot have caused that one.

*All tracked metrics*
• Day-7 retention: 61.0% vs 27.0% (+34.0 pts)
• Sessions per user: 4.5 vs 3.2 (+1.3 sessions)
• Streak-break rate: 45.0% vs 35.0% (+10.0 pts)
• Push open rate: 22.2% vs 20.7% (+1.5 pts)  _(noise)_

*Read with care*
• week 5 is split across an experiment (comeback/control) and week 4 is not — any
  movement here is partly the test, not an organic weekly change
• push open rate is on n=45 vs n=29 sends — too thin to act on alone

_n=100 this week / 100 last week · noise floor ±3 pts · generated by agents/monday_retention.py_
```

Cross-check: those Day-7 figures (27% week 4, 61% week 5) match [`05-decide/metric-findings.md`](../05-decide/metric-findings.md) independently. If a future run disagrees with that file, the data changed — investigate before believing the digest.

### Cases tested

| Case | How | Result |
|---|---|---|
| Confounded week | `data/` as-is (w5 vs w4) | Flags the experiment, signal falls to streak-break ✓ |
| Clean week | weeks 1–4 only (w4 vs w3) | No confound note; Day-7 −4.0 pts, `p=0.533, not significant` ✓ |
| Missing CSV | `--data-dir` at an empty folder | `ERROR: missing required file …`, **exit 1** ✓ |
| Only one cohort | single-week fixture | `ERROR: need at least 2 cohort weeks…`, **exit 1** ✓ |
| `--post`, no webhook | unset `SLACK_WEBHOOK_URL` | Warns on stderr, sends nothing, digest still printed ✓ |

Non-zero exit on failure is deliberate — a scheduler should be able to alert on a failed run rather than silently skipping a Monday.

---

## 4. Slack message template

The script emits Slack `mrkdwn` (`*bold*`, `_italic_`, `•` bullets) as a single `text` field, so it works with an incoming webhook, `chat.postMessage`, or an n8n Slack node without modification. Template, with substitutions in `{}`:

```
*Monday retention digest — {run_date}*
_Cohort week {current} vs week {previous}. {baseline_note}_

*Headline — Day-7 retention:* {d7_now}% {▲|▼|▬} {+/-d7_delta} pts vs last week ({d7_prev}%) ({p_value}, {significant|not significant})

*Signal to watch — {signal_label}:* {signal_now} vs {signal_prev} last week, {+/-signal_delta}{ — inside the noise floor}

*Suggested action:* {action}

*All tracked metrics*
• {label}: {now} vs {prev} ({+/-delta}){  _(noise)_}
  … one line per metric, ordered by how far each moved relative to its noise floor

*Read with care*
• {confound}
  … omitted entirely when there is nothing to caveat

_n={n_now} this week / {n_prev} last week · noise floor ±{floor} pts · generated by agents/monday_retention.py_
```

Template rules:

- **Three headings, always, in this order.** Headline, signal, action. A reader skimming on a phone before standup gets the whole thing in the first three lines.
- **Every number carries its comparison.** Never a bare percentage — always `X% vs Y% last week`.
- **The caveat block disappears when empty** rather than printing "None", so its presence is itself the signal that something needs care.
- **The footer always states n and the noise floor.** It is what stops a 1-point move being quoted in a standup as a trend.
- **No @-mentions and no `<!here>`.** This is a digest, not an alert. If it ever needs to page someone, that is a separate branch with a much higher bar.

---

## 5. Boundaries

- **Reads** `data/*.csv`. Writes **only** `ops/agent/`. Never touches a project artifact — not `CLAUDE.md`, not `metric-findings.md`, not the change log.
- **Network only with `--post`.** Default is a local dry run.
- **Never invents a number.** A metric with no data is omitted, not estimated.
- **Never upgrades a noise-floor move to a finding**, and never reports "found nothing" as "nothing happened."
- **Suggests inspection, never decisions.** The rules point at a file or a cut to pull. The rollout call stays human.

---

## 6. Wiring up the schedule — not done yet

Two things are outstanding, both needing something only you can provide:

**a. Slack credentials.** The Slack connector available to Claude Code in this workspace needs OAuth, which cannot be completed in a non-interactive session — so the script deliberately uses a plain **incoming webhook** from an env var instead, which has no such dependency and is the right call for an unattended cron job anyway. Create the webhook in Slack, then export `SLACK_WEBHOOK_URL`. Keep it out of the repo.

**b. The schedule itself.** Once a `--post` run looks right:

```bash
# crontab -e   → Mondays at 08:00
0 8 * * 1 cd /Users/bauspland/Claude/product-school-training-main && \
  SLACK_WEBHOOK_URL='https://hooks.slack.com/services/...' \
  /usr/bin/python3 agents/monday_retention.py --post >> ops/agent/cron.log 2>&1
```

`cron` on macOS will not fire while the machine is asleep — if Monday 08:00 is unreliable, `launchd` with `StartCalendarInterval` catches up on wake, or run it from n8n / GitHub Actions where the host is always up.

**The honest caveat about scheduling this today:** `data/` is a static export ending at cohort week 5. Scheduled now, the agent posts the identical digest every Monday forever. It is worth scheduling once the metric source is live — until then, run it manually. The logic, the guards, and the output format are all verified and will not need to change when the data does.
