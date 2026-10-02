# Comeback Screen — Week 5 Results

**To:** Marcus, Head of Product · **From:** PM, Engagement Squad · **Date:** 2026-10-02
**For:** Thursday kickoff · **Detail on request:** `data/metric-diagnosis.md`, `05-decide/metric-findings.md`

> **Recommendation: approve a second, properly powered cohort — do not approve full rollout yet.** The Comeback screen moved Day-7 by 30 points in week 5, but it moved it in the segment we were not aiming at, and n=50 per arm cannot carry a rollout decision. I need two weeks and a decision from you on Thursday.

---

## Situation

We shipped the free, non-punitive streak-recovery flow to a 100-user week-5 cohort, randomized 50 comeback / 50 control, to test whether it closes the Day-7 gap (39% actual vs ≥48% target).

**Naming the descope before you ask.** You approved three things: the recovery flow **+ early pre-day-7 milestone moments + a state-aware home screen**. Only the recovery flow was built and tested. Milestone moments are not in the prototype. The home screen is still a mock. That was my call, to get a clean read on one variable rather than a muddy read on three — but it means these results tell you about one-third of what you signed off on.

## Evidence

- **Day-7: 76% treatment vs 46% control (+30 pts, p=0.002).** Day-30 is +14 pts but **p=0.12 — not significant.** Do not quote the Day-30 number.
- **The lift is in the wrong segment.** Users whose streak was intact: 93% vs 64%, **p=0.007, significant.** Users who broke a streak — the people this was built for: 50% vs 28%, **p=0.13, not significant.** And `current_streak` is zero for **all 190 streak-breakers in the dataset**, including every treated one. The flow restarted zero streaks. It bought returns, not habit.
- **The funnel number you asked for twice, finally sized: 55% of Day-7 churn never broke a streak.** Of 307 users who failed Day-7, 168 had an intact streak. The lost-streak moment is worth **7.2 points** of the 9.4-point gap at most — real, but it is not the majority of the problem. Scenario math: the breaker lift alone lands Day-7 at **46.9%, short of target**; the non-breaker lift is what clears it, at **56.7%**.

## Recommendation

Run one more cohort at n≥200 per arm, randomized on streak-break status, before committing the Q3 sprint — and re-scope the concept around the non-breaker effect the data actually supports.

## Ask

**Three decisions from you on Thursday:**
1. **Approve the second cohort** (2 weeks, no new product work — re-randomization plus instrumentation).
2. **Rule on scope:** do we keep chasing streak-breakers per the original rationale, or follow the evidence to the intact-streak segment? I recommend the latter; it is 62% of users and the only significant result we have.
3. **Decide whether you want a real A/B test or a staged rollout** — this changes the timeline I bring you.

**Timeline:** I cannot give you a credible rollout date before Thursday's triad session closes five blocking decisions (eligibility, restore limit, v1 content scope, flow sign-off, instrumentation minimum). You will have the date the day after.

**Two things I want to be straight about on pressure-testing.** What exists is a 3-persona roleplay, not real users. And Raj scoped a streak-*freeze* while the prototype does a retroactive *restore* — engineering has not costed what we actually built. Neither is resolved. I would not call this pressure-tested yet.

## Risk if we wait

Day-7 fell 37% → 27% across weeks 1–4 at roughly 3 points per week with no sign of flattening, and every quarter we delay locks in that decay against a 9.4-point target gap we already know how to close — but shipping on n=50 risks rolling out to the wrong 38% of users and burning the credibility we need for the next engagement bet.

**Absolute cost-of-waiting in users: TBD** — I need quarterly signup volume to convert points into users. That is one number from the growth team and I will have it Thursday.
