# Metric Findings — Comeback Experience

**Date:** 2026-10-02
**Source:** `data/users.csv`, `data/retention.csv`, `data/sessions.csv`, `data/comeback_sends.csv`
**Question on the table:** should we scale the Comeback screen?
**Headline:** Yes — but the week-5 read is confounded and the mechanism isn't what we assumed. Run one more cohort before a full rollout. ~~Ship it to the broken-streak segment~~ — **the segment recommendation in this doc is superseded; see the correction below.**

> **⚠️ Superseded on the rollout target.** This doc recommends shipping to the `broke_streak_week1 = true` (breaker) segment. [`data/metric-diagnosis.md`](../data/metric-diagnosis.md) reverses that. Running the significance test *within* each week-5 segment shows the lift is significant for **non-breakers** (93.3% vs 64.0%, p = 0.007) and **not** significant for breakers (50.0% vs 28.0%, p = 0.13, n = 20/25). §3 below correctly calls the segment split "directional, not a measurement," but the recommendation was still built on the breaker cell — that was the error.
>
> **`data/metric-diagnosis.md` is the later and correct read. Use it for the rollout target.** Everything else in this doc — the cohort decay, the flat Day-1 line, the overall breaker/non-breaker gap, and the "one more cohort" recommendation — still holds.

All figures below are computed directly from the CSVs. Booleans are stored as the strings `'true'` / `'false'`, which is why every predicate compares against `'true'`.

---

## 1. Day-7 retention by `cohort_week`

```sql
SELECT cohort_week,
       COUNT(*)                                        AS users,
       SUM(day_7 = 'true')                             AS retained_d7,
       ROUND(100.0 * SUM(day_7 = 'true') / COUNT(*), 1) AS d7_pct
FROM retention
GROUP BY cohort_week
ORDER BY cohort_week;
```

| cohort_week | users | retained_d7 | d7_pct | day_1 % | day_30 % |
|---|---|---|---|---|---|
| 1 | 100 | 37 | **37.0%** | 91.0% | 10.0% |
| 2 | 100 | 37 | **37.0%** | 90.0% | 10.0% |
| 3 | 100 | 31 | **31.0%** | 92.0% | 6.0% |
| 4 | 100 | 27 | **27.0%** | 93.0% | 8.0% |
| 5 | 100 | 61 | **61.0%** | 91.0% | 29.0% |

**What it means.** Day-7 was decaying week over week — 37% → 37% → 31% → 27%. Day-1 is flat at 90–93% across all five weeks, so acquisition quality and install-day experience are not the problem. The leak is entirely between day 1 and day 7: people show up once and don't come back. That's the right place to intervene, and it's the window the Comeback screen targets.

Week 5 jumps to 61%. Week 5 is the only cohort with a `variant` assignment, so the Comeback test lives there — but see the caveat in §3, because the jump is bigger than the variant alone can explain.

---

## 2. Do `broke_streak_week1 = true` users retain worse at day 7?

```sql
SELECT broke_streak_week1,
       COUNT(*)                                        AS users,
       SUM(day_7 = 'true')                             AS retained_d7,
       ROUND(100.0 * SUM(day_7 = 'true') / COUNT(*), 1) AS d7_pct,
       ROUND(100.0 * SUM(day_30 = 'true') / COUNT(*), 1) AS d30_pct,
       ROUND(100.0 * SUM(churned = 'true') / COUNT(*), 1) AS churned_pct
FROM retention
GROUP BY broke_streak_week1;
```

| broke_streak_week1 | users | retained_d7 | d7_pct | day_30 % | churned % |
|---|---|---|---|---|---|
| false | 310 | 142 | **45.8%** | 12.6% | 54.5% |
| true | 190 | 51 | **26.8%** | 12.6% | 73.2% |

**Yes — and the gap is large.** 19.0 points, a 1.7x difference. Two-proportion z-test: z = 4.23, p < 0.0001. This is not noise at n = 500.

The gap holds inside every cohort, so it isn't an artifact of one bad week:

```sql
SELECT cohort_week, broke_streak_week1, COUNT(*) AS users,
       ROUND(100.0 * SUM(day_7 = 'true') / COUNT(*), 1) AS d7_pct
FROM retention
GROUP BY cohort_week, broke_streak_week1
ORDER BY cohort_week, broke_streak_week1;
```

| cohort_week | broke = false | broke = true | gap |
|---|---|---|---|
| 1 | 41.9% (n=74) | 23.1% (n=26) | 18.8 pts |
| 2 | 45.9% (n=61) | 23.1% (n=39) | 22.8 pts |
| 3 | 36.4% (n=55) | 24.4% (n=45) | 12.0 pts |
| 4 | 29.2% (n=65) | 22.9% (n=35) | 6.3 pts |
| 5 | 80.0% (n=55) | 37.8% (n=45) | 42.2 pts |

**What it means for scaling.** The streak-break segment is both large (38% of all users) and the worst-retaining. It is the correct target. Note the day-30 column in the main table: 12.6% for *both* groups. Whatever breaking a streak costs you, it costs you by day 7 and the survivors behave the same afterward. So the Comeback screen's job is to win back the day-1-to-day-7 window specifically — it is not a long-term retention lever on its own, and we shouldn't promise one.

**Caveat on direction.** `broke_streak_week1` is not clean causation. Breaking a streak and churning may both be downstream of the same thing (losing interest). The week-5 experiment is what lets us separate those, which is §3.

---

## 3. Week 5: day-7 and day-30 for `comeback` vs `control`

```sql
SELECT u.variant,
       COUNT(*)                                          AS users,
       SUM(r.day_7 = 'true')                             AS retained_d7,
       ROUND(100.0 * SUM(r.day_7 = 'true') / COUNT(*), 1) AS d7_pct,
       SUM(r.day_30 = 'true')                            AS retained_d30,
       ROUND(100.0 * SUM(r.day_30 = 'true') / COUNT(*), 1) AS d30_pct
FROM retention r
JOIN users u ON u.user_id = r.user_id
WHERE r.cohort_week = 5
GROUP BY u.variant;
```

| variant | users | day_7 | day_7 % | day_30 | day_30 % |
|---|---|---|---|---|---|
| comeback | 50 | 38 | **76.0%** | 18 | **36.0%** |
| control | 50 | 23 | **46.0%** | 11 | **22.0%** |

- **Day-7: +30 points** (76.0% vs 46.0%). z = 3.08, p = 0.002. Significant.
- **Day-30: +14 points** (36.0% vs 22.0%). z = 1.54, p = 0.12. **Not significant at n = 50/arm** — directionally good, underpowered. Do not quote the day-30 number as a result.

Split by streak status:

```sql
SELECT u.variant, r.broke_streak_week1, COUNT(*) AS users,
       ROUND(100.0 * SUM(r.day_7 = 'true') / COUNT(*), 1) AS d7_pct,
       ROUND(100.0 * SUM(r.day_30 = 'true') / COUNT(*), 1) AS d30_pct
FROM retention r
JOIN users u ON u.user_id = r.user_id
WHERE r.cohort_week = 5
GROUP BY u.variant, r.broke_streak_week1;
```

| variant | broke_streak_week1 | users | day_7 % | day_30 % |
|---|---|---|---|---|
| comeback | false | 30 | 93.3% | 40.0% |
| comeback | true | 20 | 50.0% | 30.0% |
| control | false | 25 | 64.0% | 32.0% |
| control | true | 25 | 28.0% | 12.0% |

The lift shows up in both segments (+29 pts for non-breakers, +22 pts for breakers), and for breakers it roughly doubles day-7 from 28% to 50%. Cells are 20–30 users, so treat this as a direction, not a measurement.

### Two things that should slow down a full rollout

**(a) Week 5 is confounded.** Control alone is at 46% day-7, against 27% in week 4 and 31–37% in weeks 1–3. Control received no Comeback screen, so ~15–19 points of the week-5 improvement come from something that is not this experiment — a seasonal effect, a concurrent release, a cohort-composition change, or an instrumentation change. **The honest claim is the 30-point within-week delta, not "we went from 27% to 76%."** If anyone in Thursday's kickoff quotes the latter, that's the number to correct.

**(b) The arms aren't balanced on the variable that matters most.** Platform and acquisition channel are near-perfectly split (25/25 ios/android; 17/17/16 vs 17/16/17 organic/paid/referral), and `goal_set_date` is populated for 100% of both arms. But `broke_streak_week1` is 40% in comeback vs 50% in control — a 10-point imbalance on the strongest single predictor of day-7, pushing in the direction that flatters comeback. The segment split above is the partial correction: the lift survives it, which is reassuring, but the headline +30 is somewhat inflated.

---

## 4. `comeback_sends.csv` open rate by `send_number`, comeback vs control

```sql
SELECT send_number, variant,
       COUNT(*)                                           AS sends,
       SUM(opened = 'true')                               AS opens,
       ROUND(100.0 * SUM(opened = 'true') / COUNT(*), 1)   AS open_pct,
       SUM(acted_on = 'true')                             AS acts,
       ROUND(100.0 * SUM(acted_on = 'true') / COUNT(*), 1) AS acted_on_pct
FROM comeback_sends
GROUP BY send_number, variant
ORDER BY send_number, variant;
```

| send_number | variant | sends | opens | open % | acted_on % |
|---|---|---|---|---|---|
| 1 | comeback | 50 | 14 | **28.0%** | 16.0% |
| 1 | control | 50 | 2 | 4.0% | 0.0% |
| 2 | comeback | 50 | 19 | **38.0%** | 12.0% |
| 2 | control | 50 | 2 | 4.0% | 0.0% |
| 3 | comeback | 50 | 23 | **46.0%** | 12.0% |
| 3 | control | 50 | 2 | 4.0% | 0.0% |
| 4 | comeback | 50 | 28 | **56.0%** | 28.0% |
| 4 | control | 50 | 2 | 4.0% | 0.0% |

Overall: comeback 42.0% open / 17.0% acted_on across 200 sends; control 4.0% open / 0.0% acted_on across 200 sends. Both arms are 50 distinct users × 4 sends, fully balanced.

**What it means.** The Comeback messaging is read roughly 10x as often as whatever control receives, and `acted_on` is non-zero only in the comeback arm. The content works as a re-entry point.

**But the shape is wrong and the control arm looks broken.**

- Open rate *rises monotonically* with send number: 28% → 38% → 46% → 56%. Real push sequences decay — later sends reach a more fatigued, more churned audience. A rising curve almost always means the denominator is wrong: these look like per-send-slot rates over a fixed 50-user base rather than rates over users still eligible at that send. If sends 2–4 only went to people who were still active, the climb is survivorship, not escalating effectiveness. **Do not conclude "send 4 is our best send" and lengthen the sequence on this evidence.** Confirm how eligibility is logged before touching send cadence.
- Control sits at exactly 4.0% at every single send number, with `acted_on` exactly 0 across all 200 rows. Inspecting the rows: 8 distinct control users each opened exactly 1 of their 4 sends, and no control user ever acted. That is too regular to be organic behavior — it reads like a placeholder or a logging gap in the control arm. The 10x open-rate gap may be partly an artifact of control not being instrumented.

**And the mechanism isn't the taps.** Within the comeback arm, acting on a send barely moves day-7:

```sql
SELECT a.acted, COUNT(*) AS users,
       ROUND(100.0 * SUM(r.day_7 = 'true') / COUNT(*), 1) AS d7_pct
FROM (SELECT user_id, MAX(acted_on = 'true') AS acted
      FROM comeback_sends WHERE variant = 'comeback' GROUP BY user_id) a
JOIN retention r ON r.user_id = a.user_id
GROUP BY a.acted;
```

| acted on ≥1 send | users | day_7 % |
|---|---|---|
| no | 23 | 73.9% |
| yes | 27 | 77.8% |

3.9 points — effectively nothing at this sample size. Users who never acted on a single send still retained at 74%. So the day-7 lift is **not** being delivered by people tapping through the notifications. It's coming from the Comeback screen experience itself, or from assignment-correlated differences we haven't isolated. Engagement volume is consistent with the screen doing the work: week-5 comeback users logged 5.3 sessions each vs 3.7 for control, at near-identical session length (240s vs 231s) — more returns, not longer sessions.

Supporting signal: `sessions.csv` contains a `comeback` screen with 89 sessions, against 541–557 each for `home`, `lesson`, and `streak`. The screen is being reached, at a volume consistent with ~50 treated users.

---

## Recommendation for Thursday's kickoff

**Scale it, scoped and staged. Don't call it proven.**

1. **Ship to the `broke_streak_week1 = true` segment first.** Largest, worst-retaining group (38% of users at 26.8% day-7), and the one with the clearest mechanism. Breakers in the comeback arm went 28% → 50% day-7.
2. **Run one more cohort before full rollout**, randomizing on `broke_streak_week1` so the arms are balanced on it, and sized for day-30 rather than day-7. The current n = 50/arm cannot detect the day-30 effect we actually care about.
3. **Fix the two measurement problems before that cohort:** instrument the control arm properly (a flat 4.0% with zero actions at every send number is not a real baseline), and log send eligibility so open rate has a correct denominator.
4. **Claim the +30-point within-week day-7 delta, not the 27% → 76% jump.** Control's own 46% says ~15–19 points of week 5 came from somewhere else. Overclaiming here is the fastest way to lose the next funding conversation when the effect shrinks.
5. **Don't lengthen the send sequence yet.** The rising open curve is most likely survivorship. And since acting on sends barely predicts day-7 (73.9% vs 77.8%), the notifications are probably not where the value is — invest in the screen, not the cadence.
6. **Set expectations on duration.** Day-30 is 12.6% for breakers and non-breakers alike, so this intervention should be positioned as winning the first week, not as a lifetime-retention fix.

Against the project target: week-5 comeback day-7 of 76% clears the ≥48% goal, and even the confounded-adjusted estimate (control 46% + 30 pts, or breakers at 50%) clears it. The target is reachable with this concept.

### Open items / TBD
- Why did week-5 **control** outperform week-4 by 19 points? Unresolved, and it's the biggest threat to this read.
- What does the control arm actually receive? `nudges.csv` has 161 rows of `streak_lost` nudges that may be the real control treatment — not analyzed here, as it wasn't in scope for these four questions.
- Is `broke_streak_week1` causal or just correlated with disengagement? The balanced re-test would answer it.
