# Quarterly Review — Comeback Screen · Speaker Notes

**Companion to:** [presentation.md](presentation.md) · **Audience:** Marcus, Head of Product · **Date:** 2026-10-02

Written to be said out loud. Full sentences, 3–5 per slide: what the slide shows, what it means, and what Marcus should take away before you advance.

---

## Slide 1 — The problem

Before I walk through any of this, I want to be clear about what I am asking for: one more cohort and a ruling on scope, not approval for full rollout. The number on this slide is the decay — Day-7 retention went 37, 37, 31, 27 across our first four cohorts, about three points a week, and it has not flattened. The insight underneath it is the Day-1 row: it sits at 90 to 93 percent in every single cohort, which tells us acquisition quality and the install-day experience are fine, and everything we lose we lose between day one and day seven. So this is not a top-of-funnel problem we can fix by buying better users, and it is not a first-impression problem — it is a week-one problem, which is exactly the window this project targets. What I want you to take from this slide is that we are intervening in the right place, and that the problem is actively getting worse while we decide.

---

## Slide 2 — Why now

This is the funnel number you have asked me for twice, and I finally have it. The streak-break segment is real and it is bad — 190 users, 38 percent of the base, retaining at 26.8 percent against 45.8 for everyone else, a 19-point gap at p less than 0.0001. But 55 percent of our Day-7 churn never broke a streak at all: of the 307 users who failed Day-7, 168 had an intact streak the whole time. That means the lost-streak moment is worth at most 7.2 points of our 9.4-point gap — genuinely significant, and genuinely not the majority of the problem. The takeaway I want before we move on is uncomfortable but it is the reason this is a "why now" and not a victory lap: the rationale we scoped this project on was directionally right and materially incomplete, and we were two weeks from committing a sprint to the smaller half of the problem. On cost of waiting — the decay rate is the honest answer today; the absolute number in users is one data point from growth and I will have it Thursday.

---

## Slide 3 — The proposal

What this is: a free, one-tap path back to your prior streak, earned by completing a 60-second lesson, with copy that coaches instead of scolding — and, based on the sizing on the last slide, pointed at the intact-streak segment first rather than the breakers. That is 62 percent of users, it is the only statistically significant result we have, and it is unclaimed competitively: Duolingo paywalls freeze and repair, Babbel sidesteps streaks entirely, and Elevate, Streaks, and Habitica offer no real recovery at all. Now the three things it is not, starting with the one you should hear from me rather than find on your own: you approved a recovery flow plus early pre-day-7 milestone moments plus a state-aware home screen, and only the recovery flow was built and tested. That was my call — I wanted a clean read on one variable instead of a muddy read on three — but it means everything on the next slide tells you about one-third of what you signed off on. It is also not a long-term retention fix: Day-30 is 12.6 percent for breakers and non-breakers alike, so this wins the first week and we should not sell it as more. And I will flag that my own analysis doc and this memo disagree on which segment to lead with, which is why ruling on that is decision two.

---

## Slide 4 — Evidence

The headline is a genuine, significant result: plus 30 points on Day-7, 76 percent treatment against 46 percent control, at p equals 0.002. Read down the table though, because the story is in the split — the intact-streak segment is 93 against 64 at p equals 0.007, and the segment we actually built this for, the streak-breakers, is 50 against 28 at p equals 0.13, which is not significant. The mechanism is returns rather than depth: comeback users logged 5.3 sessions to control's 3.7 at basically identical session length, so they are coming back more often, not staying longer. It is also not the notifications doing the work — inside the comeback arm, users who never tapped a single send still retained at 73.9 percent versus 77.8 for users who did, a four-point difference that is nothing at this sample size. I want to state the three caveats myself before anyone else does: n equals 50 per arm cannot carry a rollout decision, week five is confounded because control alone hit 46 percent against 27 in week four, and the arms were unbalanced on streak-break status in the direction that flatters us — so the honest claim is the plus-30 within-week delta, never "we went from 27 to 76." And the finding that worries me most is at the bottom: `current_streak` is zero for all 190 streak-breakers, including every treated one, which means the flow restarted zero streaks. It bought us returns, not habit.

---

## Slide 5 — The plan

What I am proposing is two weeks to a decision-grade read with no new product work — a second cohort at 200 or more per arm, randomized on streak-break status so the arms are actually balanced on the strongest predictor, and sized for Day-30 rather than Day-7. The two measurement fixes in the middle row are not optional: our control arm sat at exactly 4.0 percent open rate at every single send number with zero actions across all 200 rows, which is a logging gap rather than a baseline, and our open rate *rises* with send number from 28 to 56 percent, which almost certainly means a wrong denominator rather than escalating effectiveness. On risks, I will name the four plainly — week-five control outperformed week four by 19 points and we do not know why, which is the biggest threat to this entire read; engineering has not costed what we built, because Raj scoped a streak freeze and the prototype does a retroactive restore; our solution evidence is a three-persona roleplay rather than real users; and shipping on n equals 50 risks rolling out to the wrong 38 percent and burning the credibility we need for the next engagement bet. To answer the question you always ask directly: I would not call this pressure-tested yet, and that is a deliberate statement rather than a hedge. On timeline, I cannot give you a credible rollout date until Thursday's triad closes five blocking decisions, and you will have the date the day after.

---

## Slide 6 — The ask

Three decisions, and the second one is the only one that cannot wait. First, approve the second cohort — two weeks, no new product work, just re-randomization and instrumentation. Second, rule on scope: do we keep chasing streak-breakers per the original rationale, or follow the evidence to the intact-streak segment — and I recommend the latter, because the scenario math is decisive, with the breaker lift alone landing Day-7 at 46.9 percent, short of our 48 target, while the non-breaker lift clears it at 56.7. Third, tell me whether you want a real A/B test or a staged rollout, because that materially changes the timeline I bring you. To be explicit about what I am not asking for: no full rollout, no sprint commitment, and no rollout date today. If you need to take these async that works — but decision two determines what the second cohort randomizes on, so I need it before we start, and you will get the rollout date Friday and the cost-of-waiting number in users Thursday either way.
