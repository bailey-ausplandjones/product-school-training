# Experiment Design — Comeback Screen, Full Test

**Date:** 2026-10-02 · **Owner:** PM, Engagement Squad
**Primary metric:** Day-7 retention · **Companions:** `data/metric-diagnosis.md`, `05-decide/metric-findings.md`, `07-docs/recommendation-memo.md`

## Given parameters

| Parameter | Value |
|---|---|
| Pilot result | 76% treatment vs 46% control, Day-7 (n=50 per variant) |
| Observed lift | +30 pts |
| Control baseline | 46% |
| Minimum detectable effect | 5 percentage points |
| Statistical power | 80% |
| Significance level | 95% (two-sided) |
| Available WAU | 85,000 |
| Max test duration | 8 weeks |

**Bottom line:** the pilot is statistically significant but was only powered to detect effects of ~28 points, so the +30 is almost certainly an overestimate. The full test needs **1,569 per variant** for the headline metric — and **4,129 per variant** to answer the question that actually matters (which segment responds). Either fits inside 8 weeks with room to spare. **Run it.**

---

## Step 1 — Statistical significance of the pilot

**What it means for a go/no-go:** statistical significance tells you only that the gap you measured is unlikely to be pure chance — it does **not** tell you the gap is big, durable, or the size you measured.

**Result:** 38/50 vs 23/50 → pooled **z = 3.08, two-sided p = 0.0021**. Yates-corrected chi-square gives p = 0.0041. Both clear the 0.05 bar.

```
z = (p₁ − p₂) / √(p̄(1−p̄)(1/n₁ + 1/n₂))
  = (0.76 − 0.46) / √(0.61 × 0.39 × (1/50 + 1/50)) = 3.075   → p = 0.0021 ✓ significant
```

**95% confidence interval on the lift: [11.8, 48.2] points.** A 36-point-wide window — the top end is four times the bottom end.

**In plain English:** something real happened — a coin-flip explanation doesn't survive. But the pilot cannot tell you *how much* happened. It says "somewhere between 12 and 48 points," and a 12-point lift and a 48-point lift are completely different product decisions.

### The number that should worry you most

At n=50 per arm with a 46% baseline, the smallest effect this pilot had an 80% chance of detecting was **27.9 points**:

| Cell | n per arm | Smallest effect it could reliably detect |
|---|---|---|
| Full pilot | 50 | **27.9 pts** |
| Non-breaker segment | 25–30 | ~39.5 pts |
| Breaker segment | 20–25 | ~44.2 pts |

The pilot's power to detect the 5-point effect we actually care about was **7.2%**.

This is the **winner's curse**: a test that can only see enormous effects will, when it does report a win, systematically report one that is too big. The pilot needed ≥28 points to find anything, and it found 30 — right at its own detection floor. That is the signature of an inflated estimate, not a precise one. Combine it with the three known confounds — control alone jumped to 46% from week 4's 27%, the arms were unbalanced 40% vs 50% on streak-break status in treatment's favor, and 8 control users were exposed to the treatment screen — and the honest expectation for the true effect is **well below 30 points**.

---

## Step 2 — Minimum detectable effect

**What it means:** the MDE is the smallest improvement you tell the test it must be able to find; you set it *before* the test because it determines sample size, and choosing it afterward lets you quietly redefine success to match whatever you got.

**MDE = 5 percentage points.** This is well-chosen for this decision: the Day-7 gap to target is 9.4 points (38.6% actual vs ≥48%), so a 5-point MDE can detect roughly half the gap — small enough to be decision-relevant, large enough to stay affordable.

**Why setting it first is not a formality here.** The pilot is a live demonstration of the failure mode. Its *implied* MDE was 28 points. Nobody chose that — it fell out of a 50-user sample. Had the true effect been a perfectly good 8 points, this pilot would have returned "no significant difference" and the concept would likely have been killed. The MDE was set by the sample size instead of the sample size being set by the MDE, which is backwards.

---

## Step 3 — Sample size

**What power means:** power is the chance your test *finds* a real effect that genuinely exists; at 80% power you accept a 1-in-5 chance of missing a true win.

**What we risk if it is too low:** two things, and the second is less obvious. You miss real wins (false negatives) — and, when you do get a win, it is exaggerated, because only the flukiest-looking results clear the bar. An underpowered test is not merely a weaker version of a good test; it is actively misleading about effect size.

```
n per variant = (z_α/2 + z_β)² × [p₁(1−p₁) + p₂(1−p₂)] / d²

z_α/2 = 1.95996 (95%, two-sided)     z_β = 0.84162 (80% power)
(1.95996 + 0.84162)² = 7.8489
p₁ = 0.46, p₂ = 0.51, d = 0.05
n = 7.8489 × (0.46×0.54 + 0.51×0.49) / 0.05² = 7.8489 × 0.4983 / 0.0025 = 1,564.4
```

| Variance assumption | n per variant |
|---|---|
| Unpooled | 1,565 |
| Pooled (conservative, use this) | **1,569** |

### **Required: 1,569 per variant → 3,138 total. That is 31× the pilot.**

### Powering for the question that actually matters

The open decision is not "does it work" — it is **which segment it works for**. The pilot's significant effect was in non-breakers (p=0.007); the breaker effect, which is the one the concept was built on, was not significant (p=0.13). Testing that at the same 5-point MDE requires powering the *segments*, not the total:

| Design | Enrolled per arm | Total | % of one week's WAU |
|---|---|---|---|
| Headline Day-7 only | 1,569 | 3,138 | 3.7% |
| **Breaker segment powered** (38% of users) | **4,129** | **8,258** | 9.7% |
| Non-breaker segment powered (62%) | 2,531 | 5,062 | 6.0% |
| **Stratified — oversample breakers to 50/50** | **3,138** | **6,276** | **7.4%** |

**Recommended design: stratified, 6,276 total.** Randomize *within* streak-break status rather than across the whole pool. This powers both segments at 5 points for 24% fewer users than the naive segment-powered design, and it structurally eliminates the covariate imbalance that inflated the pilot — the 40/50 split cannot recur if you stratify on it.

---

## Step 4 — Test duration

**Enrollment.** 6,276 users is **7.4% of one week's WAU** (85,000). Even assuming only a quarter of WAU is eligible and enrollable, enrollment completes in well under a week.

**Maturation is the real driver.** Day-7 retention is not observable until a user has existed for 7 days, so duration = enrollment + maturation, not enrollment alone.

| Readout | Enrollment | Maturation | Total | Fits 8 weeks? |
|---|---|---|---|---|
| **Day-7 (primary)** | ~1 week | 7 days | **~2.0 weeks** | ✅ Yes, 6 weeks spare |
| Day-30 (secondary) | ~1 week | 30 days | **~5.3 weeks** | ✅ Yes, 2.7 weeks spare |

### Both fit. **Recommendation: run ~6 weeks, not 2.**

Reading Day-7 at week 2 and stopping would repeat the pilot's core mistake. Day-30 was the pilot's weakest number (+14 pts, p=0.12, not significant) and it is the one that distinguishes a real retention fix from a temporary visit bump — particularly given that zero of 190 streak-breakers ever restarted a streak. The 8-week ceiling is not binding, so buy the Day-30 answer.

### One caveat on the denominator

**WAU is the wrong population for this test.** This is a first-week activation intervention, so the eligible pool is *new signups*, not weekly actives — and new signups are a small fraction of WAU. Break-even volumes if the real pool is signups:

| Readout | Enrolling weeks available | Minimum enrolled per week |
|---|---|---|
| Day-7 | 7.0 | **≥ 449** |
| Day-30 | 3.7 | **≥ 845** |

At 2.1M registered and 340K MAU, clearing ~850 new users per week is near-certain — but confirm actual weekly signup volume with growth before committing the date. **This is the one input that could break the timeline.**

---

## Step 5 — The decision

### **Wait for the full test. It costs weeks, not quarters.**

The case is simple arithmetic: the full test takes ~2 weeks for a Day-7 answer and ~6 weeks for a Day-30 answer, against an 8-week allowance. You are not trading a quarter for certainty — you are trading six weeks. And the pilot's own math says you need it: a study powered only for 28-point effects reported a 30-point effect, with a confidence interval running from 12 to 48 points, on arms that were unbalanced on the strongest predictor of the outcome and partially contaminated.

| Path | Risk, in one sentence |
|---|---|
| **Scale now** | You roll out on an effect size that is probably inflated and attribute it to the wrong segment — shipping a streak-break fix to the 38% of users where the result was never significant, while the lift that *was* significant came from the 62% whose streaks were intact. |
| **Wait for the full test** | You hold a likely-good concept for six weeks while Day-7 keeps eroding at roughly 3 points per week, and you spend credibility asking an already-approving stakeholder to re-approve something he thought was settled. |

**Why waiting still wins.** The scale-now risk is not "slightly smaller lift than advertised" — it is building the wrong product for the wrong users and finding out after the Q3 sprint is spent. The wait risk is a six-week delay with a known, bounded cost. Scenario math makes the asymmetry concrete: if only the breaker lift is real, cohort Day-7 lands at **46.9%** and *misses* the 48% target; if the non-breaker lift is real, it lands at **56.7%**. Those two futures call for different products, and only the full test tells you which one you are in.

---

## Step 6 — Weekly leading indicators

**Read these for validity and safety, not for stopping.** Checking your primary metric repeatedly and stopping when it looks good inflates the false-positive rate well past 5% — the "peeking" problem. If you want the option to stop early, commit to an alpha-spending boundary (e.g. O'Brien–Fleming) in the design, before launch. Otherwise these three are tripwires, not verdicts.

### 1. Assignment integrity — arm balance, covariate balance, and control contamination

**Check weekly:** arms within 48/52 of a 50/50 split; streak-break share within 3 points across arms; count of control users with any `comeback` screen exposure.

**What would make me nervous:** any control-arm exposure above ~1%, or a streak-break imbalance over 3 points.
**Why:** both already happened in the pilot — 8 control users saw the treatment screen, and the arms differed by 10 points on streak-break status in treatment's favor. These are the two defects most likely to manufacture a fake win, they are invisible in the headline number, and unlike the outcome metrics they are **cheap to fix mid-flight** if caught in week 1. This is the single most valuable thing on this list.

### 2. Day-3 return rate by arm

**Check weekly:** share of each arm with a session on day-offset 3, which is observable four days before Day-7 resolves.

**What would make me nervous:** treatment at or below control, or a treatment Day-1 rate that drops below control at all.
**Why:** it is the earliest honest read on the primary metric, so a flat or negative Day-3 gap means the effect is not materializing and you learn it in week 1 rather than week 6. The Day-1 condition is a guardrail in the other direction: the Comeback screen fires on days 2–5, so it should be impossible for it to hurt Day-1 — if Day-1 diverges, the instrumentation or the assignment is broken, not the product. **Fix first: the pilot's session logging stopped at day-offset 4 and 20% of users had zero sessions despite 90%+ Day-1, so this metric is not currently trustworthy.**

### 3. Streak-restart rate among treated streak-breakers

**Check weekly:** share of treated users with `broke_streak_week1 = true` who reach `current_streak ≥ 1`.

**What would make me nervous:** it staying at or near **0%**.
**Why:** this is the pilot's most damning finding and the one nobody is watching — `current_streak` was 0 for **all 190 breakers in the dataset**, min = max = 0, including every treated one. Not one person rebuilt a streak. If that repeats at scale, the screen is renting visits rather than restarting the habit, and you should expect the Day-7 gain to evaporate by Day-30 exactly as the pilot hinted (+14 pts, p=0.12). A Day-7 win with a 0% restart rate is the outcome most likely to look like success at readout and be gone a quarter later.

### Pass/fail guardrails (not weekly indicators)

Session length by arm (pilot: 240s vs 231s — should stay flat; a drop means the screen is displacing the lesson), and crash/error rate on the Comeback screen.

---

## Design summary

| Item | Decision |
|---|---|
| Primary metric | Day-7 retention |
| Secondary | Day-30 retention; streak-restart rate among breakers |
| Baseline | 46% |
| MDE | 5 pts (absolute) |
| Power / significance | 80% / 95% two-sided |
| **n per variant (headline)** | **1,569** |
| **Recommended design** | **Stratified on `broke_streak_week1`, oversampled to 50/50 — 3,138 per arm, 6,276 total** |
| Enrollment | <1 week (7.4% of weekly WAU) |
| **Duration** | **~6 weeks to Day-30 readout** (Day-7 readable at ~2 weeks, do not stop there) |
| Fits 8-week limit | Yes, 2.7 weeks spare |
| Interim analysis | None, unless an alpha-spending boundary is pre-committed |

### Blocking prerequisites

1. **Confirm weekly new-user volume with growth** — must clear ~850/week; WAU is the wrong denominator for a first-week test.
2. **Extend session logging through day-offset 7** — the Day 4–7 decision window is currently unlogged.
3. **Reconcile Day-1 vs session logging** — 20% of users show zero sessions despite 90%+ Day-1.
4. **Instrument the control arm's messaging** — pilot control showed exactly 4.0% open at every send number with 0 actions across 200 rows; that is not a real baseline.
5. **Add `streak_break_count`** — no break-history field exists, which blocks the repeat-break hypothesis entirely.
6. **Log the Comeback screen's trigger condition and exposure** — needed to separate treatment from selection.
