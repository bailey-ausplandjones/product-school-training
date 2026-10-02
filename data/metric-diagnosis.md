# Metric Diagnosis — Day-7 Retention

**Date:** 2026-10-02
**Source:** `data/users.csv`, `data/retention.csv`, `data/sessions.csv`, `data/comeback_sends.csv`, `data/nudges.csv`
**Companion doc:** `05-decide/metric-findings.md`

> **Correction to the companion doc.** That file recommended shipping to the `broke_streak_week1 = true` segment first. Running the significance test *within* each week-5 segment reverses that: the lift is significant for **non-breakers** (93.3% vs 64.0%, p = 0.007) and **not significant for breakers** (50.0% vs 28.0%, p = 0.13, n = 20/25). The earlier doc called the segment split "directional, not a measurement" but still built the recommendation on the breaker cell. See §3. This changes the rollout target.

---

## 1. Metric tree: decomposing Day-7 retention

Day-7 retention is an outcome, not a lever. Here is what it actually decomposes into, with every number computed from these five CSVs.

```
Day-7 retention = 38.6% (193 / 500)
│
├─ ACTIVATION — did they start at all?
│  ├─ Day-1 retention .................... 91.4% (457/500)   ← flat 90–93% all 5 weeks. NOT the problem.
│  ├─ Goal set ........................... 100.0% (500/500)  ← goal_set_date populated for every user
│  └─ Goal-set lag ...................... 1.0 day, 100% of users  ← zero variance. Not a lever.
│
├─ STREAK FORMATION — did a streak take hold?
│  ├─ Streak held through week 1 ......... 62.0% (310/500)  → d7 = 45.8%
│  └─ Streak BROKE in week 1 ............. 38.0% (190/500)  → d7 = 26.8%   ← 19-pt penalty
│
├─ COMEBACK — did breakers re-enter?
│  ├─ Breakers retained to d7 ............ 26.8% (51/190)
│  └─ Breakers who REGAINED a streak ..... 0.0% (0/190)     ← see below. The broken lever.
│
└─ MESSAGING REACH — proxy for notification opt-in
   ├─ Breakers who got a streak_lost nudge  ... 116/190 = 61.1%
   ├─ streak_lost nudge open rate ............. 17.4% (28/161)
   └─ streak_lost nudge ACTED-ON rate ......... 0.0% (0/161)  ← never drives action, any week
```

### What the levers are actually worth

| Lever | Current value | Sensitivity of cohort Day-7 | Verdict |
|---|---|---|---|
| **Streak-start rate** (day-1, goal-set) | 91.4% / 100% | Near zero headroom | **Dead lever.** Flat across all 5 weeks while d7 fell 10 pts. Already maxed. |
| **Streak-break rate** | 38.0% | 10-pt reduction → **+1.9 pts** d7 | **Weak lever.** The 19-pt penalty is real, but moving the *rate* moves the mix, and mix barely matters (§2). |
| **Comeback rate** | 26.8% d7 / **0% streak restart** | 10-pt improvement → **+3.8 pts** d7 | **Strongest available lever**, and the only one with untouched headroom. |
| **Non-breaker d7 rate** | 45.8% | 10-pt improvement → **+6.2 pts** d7 | **Largest lever by arithmetic** — 62% of users sit here. Currently unowned by this project. |
| **Notification opt-in** | **not in the data** | unknown | **Cannot be measured.** No opt-in, permission, or push-token column exists in any of the five files. |

**On notification opt-in:** there is no column for it anywhere. The closest observable is *send coverage* — 61.1% of breakers received a `streak_lost` nudge, which conflates opt-in, eligibility, and send-logic bugs. Treat opt-in as uninstrumented. If you want it as a lever, it needs to be logged first.

**The arithmetic point worth bringing to kickoff:** the non-breaker segment is 62% of users at 45.8% day-7. A 10-point improvement there is worth +6.2 points of cohort day-7 — more than three times what a 10-point cut in the break rate buys you (+1.9). The engagement squad's framing has been streak-break-as-the-problem. The math does not support that as the primary lever, and §2 and §3 both point the same direction.

---

## 2. What caused the Weeks 1–4 decline — specifically

Day-7 fell 37.0% → 37.0% → 31.0% → 27.0%. Here is what did **not** cause it. Weeks 1–4 are identical on every input in the data:

| Input | W1 | W2 | W3 | W4 |
|---|---|---|---|---|
| Acquisition mix (organic/paid/referral) | 34/34/32 | 34/34/32 | 34/34/32 | 34/34/32 |
| Platform (ios/android) | 60/40 | 60/40 | 60/40 | 60/40 |
| Day-1 retention | 91% | 90% | 92% | 93% |
| Goal-set rate / lag | 100% / 1.0d | 100% / 1.0d | 100% / 1.0d | 100% / 1.0d |
| Sessions per user | 3.2 | 3.2 | 3.2 | 3.2 |
| Avg session seconds | 232 | 242 | 233 | 229 |
| Screen mix (home/lesson/streak) | 31/34/35 | 36/31/33 | 32/33/34 | 35/32/33 |

No mix shift, no acquisition-quality shift, no engagement-depth shift. So the decline is **rate deterioration inside a segment**, and the next table says which one:

```sql
SELECT cohort_week,
       SUM(broke_streak_week1='false') AS n_nonbreak,
       ROUND(100.0*SUM(CASE WHEN broke_streak_week1='false' AND day_7='true' THEN 1 END)
             / SUM(broke_streak_week1='false'), 1) AS nonbreaker_d7,
       SUM(broke_streak_week1='true') AS n_break,
       ROUND(100.0*SUM(CASE WHEN broke_streak_week1='true' AND day_7='true' THEN 1 END)
             / SUM(broke_streak_week1='true'), 1) AS breaker_d7
FROM retention GROUP BY cohort_week;
```

| cohort_week | non-breaker d7 | n | breaker d7 | n |
|---|---|---|---|---|
| 1 | **41.9%** | 74 | 23.1% | 26 |
| 2 | **45.9%** | 61 | 23.1% | 39 |
| 3 | **36.4%** | 55 | 24.4% | 45 |
| 4 | **29.2%** | 65 | 22.9% | 35 |

**This is the specific cause: the decline is entirely in the segment that never broke a streak.**

- Non-breaker day-7 fell **41.9% → 29.2%**, a 12.7-point collapse.
- Breaker day-7 was **flat at 23.1 / 23.1 / 24.4 / 22.9%** — it never moved. The broken-streak cohort was always bad; it did not get worse.

Shift-share decomposition of the 10.0-point W1→W4 drop:

| Component | Effect |
|---|---|
| Mix (more users breaking streaks: 26% → 35%) | **−1.7 pts** |
| Within-segment rate change | **−9.4 pts** |
| Interaction | +1.1 pts |
| **Total** | **−10.0 pts** |

Of that −9.4, essentially all of it is the non-breaker rate (−12.7 pts × 74% weight = −9.4). The breaker rate contributed −0.1 pts.

**What this means.** The story the squad has been telling — "more people are breaking streaks, and streak-breaks cause churn" — is wrong as a cause of *the decline*. Break rate did rise (26% → 35–45%), but that mix shift accounts for only 1.7 of the 10 points. The decline is that **users who successfully maintained a 3–21 day streak stopped coming back anyway.** Weeks 3 and 4 are where it breaks: W2 → W4 is −16.7 pts for non-breakers.

**What it points to.** Nothing in these five files explains a within-segment drop among successful users — the inputs are flat. That means the cause sits outside this data, and the obvious candidate is the v2 redesign noted in project context (d7 48% → 39%). The pattern is diagnostic: a change that degraded the *success* path (home / streak / lesson experience for people doing well) while leaving the break-recovery path untouched would produce exactly this signature — non-breakers decaying, breakers flat. A change that made streak-breaks more punishing would have produced the opposite, and did not.

**Instrumentation limit, and it is a real one.** `sessions.csv` covers only day-offsets 0–3 from signup (weeks 1–4: exactly 80 users × 4 days each; week 5 adds day 4). **There is no session data in the day 4–7 window where the retention decision is actually made.** We can see the cohort arrive and we can see the day-7 outcome, but the behavior in between is unlogged. Also, 20 of 100 users per week have zero sessions despite 90%+ day-1 retention — so day-1 and session logging disagree. Both gaps should be fixed before the next cohort.

---

## 3. What the Week 5 split tells us the Comeback screen actually fixed

```sql
SELECT u.variant, r.broke_streak_week1, COUNT(*) AS users,
       ROUND(100.0*SUM(r.day_7='true')/COUNT(*),1) AS d7_pct,
       ROUND(100.0*SUM(r.day_30='true')/COUNT(*),1) AS d30_pct,
       ROUND(AVG(u.current_streak),2) AS avg_current_streak
FROM retention r JOIN users u ON u.user_id = r.user_id
WHERE r.cohort_week = 5 GROUP BY 1,2;
```

| variant | broke_streak_week1 | users | day_7 | day_30 | avg current_streak |
|---|---|---|---|---|---|
| comeback | false | 30 | **93.3%** | 40.0% | 12.57 |
| control | false | 25 | 64.0% | 32.0% | 12.36 |
| comeback | true | 20 | **50.0%** | 30.0% | **0.00** |
| control | true | 25 | 28.0% | 12.0% | **0.00** |

Significance within segment:
- Non-breakers: 28/30 vs 16/25 → z = 2.71, **p = 0.007. Significant.**
- Breakers: 10/20 vs 7/25 → z = 1.51, **p = 0.13. Not significant.**

### Three things this tells us

**(a) It fixed retention for people whose streak was intact — not for people who broke one.** The 29-point non-breaker lift is the only statistically significant segment effect. The 22-point breaker lift is the headline everyone wants, and at n = 20/25 it cannot be distinguished from noise. Given §2 — the decline was a non-breaker problem — this is coherent: the Comeback screen appears to have repaired the thing that actually broke. But that is the *opposite* of the product rationale it was built on.

**(b) It restarted exactly zero streaks.**

```sql
SELECT COUNT(*) AS breakers, SUM(current_streak > 0) AS regained_a_streak
FROM users WHERE broke_streak_week1 = 'true';
-- 190, 0
```

`current_streak = 0` for **all 190 breakers in the dataset**, min = max = 0, in every cohort — including all 20 breakers in the week-5 comeback arm. Not one person who broke a streak in week 1 ever rebuilt one. So the screen moved day-7 *presence* without moving the core habit loop. It bought returns, not re-engagement. That is a meaningful ceiling: whatever lift exists is not compounding into streak behavior, which is consistent with day-30 converging (12.6% for breakers and non-breakers alike across the full dataset).

**(c) Engagement rose as visit frequency, not visit depth.** Week-5 comeback users logged 5.3 sessions each vs 3.7 for control, at near-identical duration (240s vs 231s). More returns of the same length. The screen is a re-entry prompt, not a deeper experience.

### Four reasons not to over-read week 5

1. **Confounded.** Control alone hit 46% day-7 vs week 4's 27%. Control got no Comeback screen, so ~15–19 pts came from something else. The defensible claim is the +30-pt within-week delta.
2. **Unbalanced on the key covariate.** `broke_streak_week1` is 40% comeback vs 50% control — a 10-pt imbalance on the strongest predictor of day-7, favoring treatment.
3. **Control contamination.** 8 control users have `screen = 'comeback'` sessions (5 non-breakers, 3 breakers). The control arm was partially exposed to the treatment.
4. **Control messaging is not instrumented.** Control sits at exactly 4.0% open at every send number with `acted_on = 0` across all 200 rows; 8 users each opened exactly 1 of 4. Not organic behavior. Separately, 3 comeback rows have `acted_on = 'true'` with `opened = 'false'` — acted without opening.

Two more targeting facts that matter: **comeback sends went to all 50 users in each arm, breakers and non-breakers alike** — they were never targeted at streak-breaks. And all four sends land on day-offsets 2, 3, 4, 5 from signup, so the whole sequence fires before the day-7 measurement.

---

## 4. Four ranked hypotheses: why some treatment users still churned

**The population:** 12 of 50 week-5 comeback users failed day-7 — **10 breakers** (50% of that cell) and **2 non-breakers**.

**Read this first.** On every column available, churned and retained treatment users are nearly identical:

| comeback arm | n | avg sessions | avg opens | avg acted_on | avg current_streak |
|---|---|---|---|---|---|
| breakers, churned | 10 | 5.0 | 1.3 | 0.5 | 0.0 |
| breakers, retained | 10 | 5.3 | 1.6 | 0.8 | 0.0 |
| non-breakers, churned | 2 | 5.5 | 2.5 | 1.0 | 7.5 |
| non-breakers, retained | 28 | 5.39 | 1.79 | 0.68 | 12.93 |

**Nothing in the data discriminates churned from retained breakers.** That is why no hypothesis below scores above 5 — the honest answer is that the discriminating variable is not logged. Hypotheses are ranked by likelihood given what the data does show.

---

### H1 — The screen restores visits but never restarts the habit, so retention decays as soon as the send sequence ends
**Rank: 1** · **Confidence: 5/10**

**Testable prediction:** Treatment users who churned will show their last session on day-offset 5 or earlier, clustering at the final send (day 5), and will have `current_streak = 0` at churn. Extending the sequence to 6–8 sends will shift day-7 retention upward by ≥8 pts while leaving day-30 flat — because the screen is substituting external prompting for an internal habit, and retention tracks the prompt, not the habit.

**Why this score:** Strongly supported on the mechanism side — `current_streak = 0` for all 190 breakers with zero exceptions is the hardest fact in the dataset, and all four sends landing on days 2–5 means nothing prompts the day-5-to-7 gap. But it is capped at 5 because `sessions.csv` stops at day-offset 4, so the decay itself is unobservable.

**Confirms it:** Last-session day-offset for the 10 churned breakers, with sessions logged through day 7 — clustering at day 5 confirms.
**Rules it out:** Churned breakers show sessions on days 6–7 (still visiting after sends stop, then churning anyway) — that makes the prompt-dependency story wrong.

---

### H2 — The lift is a non-breaker effect, and breakers never actually responded
**Rank: 2** · **Confidence: 4/10**

**Testable prediction:** In a balanced re-test, the breaker cell will show a day-7 lift of ≤8 pts and will not reach significance, while the non-breaker cell reproduces a ≥20-pt significant lift. The 10 churned breakers churned because the screen does not work for the broken-streak state at all — and the 10 who retained are the base rate plus noise, not responders.

**Why this score:** Directly supported by the only significance tests available (breakers p = 0.13; non-breakers p = 0.007) and by §2's finding that non-breakers were the segment that actually deteriorated. Held to 4 because a 22-pt point estimate is a large effect to dismiss, and n = 20 is genuinely underpowered rather than evidence of no effect.

**Confirms it:** Breaker-cell day-7 lift in a re-test powered to n ≥ 200/arm, randomized on `broke_streak_week1`.
**Rules it out:** Same re-test shows a breaker lift ≥15 pts at p < 0.05.

---

### H3 — Repeat streak-breaks desensitize: after a second reset the offer lands as noise
**Rank: 3** · **Confidence: 3/10**

**Testable prediction:** Among treatment users who saw the Comeback screen, those who had reset their streak two or more times before the screen fired will open sends at a lower rate and retain at day-7 at a rate ≥15 pts below first-time breakers — the offer reads as noise once the reset is familiar.

**Why this score:** This is the user's own framing and it is mechanically plausible, but **it is currently untestable: there is no break-count column.** `broke_streak_week1` is a single boolean, and `current_streak` is 0 for every breaker with no history. The weak available proxy points the right way — churned breakers averaged 1.3 opens vs 1.6 for retained, and churned non-breakers had shorter streaks (7.5 vs 12.93) — but at n = 10 and n = 2 that is noise.

**Confirms it:** A `streak_break_count` or break-event log showing churned treatment breakers with ≥2 prior resets at materially higher rates than retained ones.
**Rules it out:** Break count distributes identically across churned and retained treatment breakers.

---

### H4 — The screen is shown to people already lost, so exposure marks the problem rather than fixing it
**Rank: 4** · **Confidence: 3/10**

**Testable prediction:** Within the treatment arm, users who saw the Comeback screen will retain at day-7 *no better* than assigned-but-unexposed users, and the screen's trigger will fire disproportionately on users whose disengagement was already underway — making exposure a marker of churn risk, not a treatment.

**Why this score:** The one supporting data point is striking — within the comeback arm, users who saw the screen retained at **73.8%** (n = 42) vs **87.5%** for those who never saw it (n = 8). But n = 8 makes that nearly worthless, and the direction is exactly what benign selection also produces. The 8 contaminated control users point the same way. Ranked last because it is a measurement-validity concern rather than a product cause, though if true it invalidates the whole week-5 read.

**Confirms it:** Trigger-condition logs showing the screen fires after a user's engagement has already dropped, plus an exposed-vs-eligible-unexposed comparison at n ≥ 100 confirming no retention gap.
**Rules it out:** Exposed users retain materially better than eligible-but-unexposed users at adequate n, with trigger timing preceding rather than following disengagement.

---

## 5. Which one to test first

**H2 — run the balanced re-test and settle which segment the screen actually serves.**

Not because it is the most interesting hypothesis. Because it is the only one whose answer changes what gets built, and because every other hypothesis is downstream of it.

1. **It is the live decision.** Thursday's kickoff is choosing a rollout target. The current plan — and the companion doc's recommendation — points at the broken-streak segment on the strength of a 22-point lift at p = 0.13. The significant effect is in the non-breaker segment at p = 0.007. Shipping to the wrong 38% of users is the expensive mistake available this sprint, and it is avoidable in one cohort.

2. **It cleans up the evidence base for everything else.** A re-test randomized on `broke_streak_week1`, at n ≥ 200/arm, fixes the 10-point covariate imbalance, eliminates the control contamination (8 exposed control users), and produces a non-confounded estimate instead of a within-week delta sitting on top of an unexplained 19-point cohort jump. H1, H3, and H4 all currently fail on sample size or missing instrumentation — this cohort is where you fix both.

3. **It is cheap and additive.** The screen already exists and is shipped to week 5. This is a re-randomization plus instrumentation, not new product work: extend `sessions.csv` through day-offset 7, log `streak_break_count`, log the screen's trigger condition and exposure, and instrument the control arm's messaging properly. Those four additions make H1, H3, and H4 testable in the *following* sprint at no extra cost.

4. **H1 is the better long-run question but the worse first test.** "Does this restart the habit or just rent the visit?" matters more — and the 0-of-190 streak-restart figure suggests the answer is already no. But answering it requires day-5-to-7 session data we do not have, and a day-30 readout the current n cannot support. Test it second, on the instrumented cohort.

**What I would not do this sprint:** lengthen the send sequence. The rising open curve (28 → 38 → 46 → 56%) is almost certainly survivorship from a fixed 50-user denominator, acting on sends barely predicts day-7 (77.8% vs 73.9%), and H1 predicts more sends buys day-7 without buying day-30. That is the kind of win that looks good at readout and shows up as nothing a month later.

---

## Open items / TBD

- **Why did week-5 control beat week 4 by 19 points?** Unresolved, and the biggest threat to the week-5 read.
- **What broke for non-breakers in weeks 3–4?** Not answerable from these files — the inputs are flat. Needs release-timeline and v2-redesign dates cross-referenced against cohort weeks.
- **Notification opt-in is uninstrumented.** No opt-in, permission, or push-token column exists. Cannot be used as a lever until logged.
- **Session data stops at day-offset 3–4.** The day 4–7 decision window is unobserved.
- **Day-1 vs session logging disagree.** 20 of 100 users per week have zero sessions despite 90%+ day-1 retention.
- **No break-count field.** Blocks H3 entirely.
