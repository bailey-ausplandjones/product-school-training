# Quarterly Review — Comeback Screen · Narrative Structure

**Audience:** Marcus, Head of Product (approver) · **Date:** 2026-10-02 · **Length:** 6 slides
**Backbone:** [recommendation-memo.md](recommendation-memo.md) · [metric-findings.md](../05-decide/metric-findings.md)
**Supporting:** [decision-brief.md](decision-brief.md) · [interview-synthesis.md](../02-research/interview-synthesis.md)
**Calibration:** [marcus.md](../08-stakeholders/marcus.md)
**Speaker notes:** [presentation-notes.md](presentation-notes.md)

---

## Calibration decisions

Taken from Marcus's profile, and they shape the whole deck:

- **The ask goes on slide 1, not slide 6.** His stated preference is the recommendation in the first sentence, not the last. Slide 6 restates and formalizes it; slide 1 carries it as a one-line kicker so he is never reading forward to find out what he is being asked.
- **Every number ties to Day-7.** "How does this affect our Day-7 retention number specifically" is a question he has asked before. No metric appears in this deck that doesn't connect to it.
- **Two things he asked for twice are now answered and get named as answered:** the funnel sizing, and the Day-7 mechanism.
- **"Pressure-tested" is conceded, not claimed.** His bar is that eng and design have both stress-tested the idea. Neither has. Claiming otherwise is the fastest way to lose the next conversation.
- **One idea per slide.** His pushback is anything needing more than one page to explain.
- **The descope is named by us, on slide 3.** He approved three things; one was built. He will find this himself if we don't say it.

### Source contradiction, resolved on purpose

`metric-findings.md` recommends shipping to the broken-streak segment first. `recommendation-memo.md` recommends following the evidence to the intact-streak segment. **This deck follows the memo**, because the breaker result is not significant (p=0.13), `current_streak` is zero for all 190 streak-breakers including every treated one, and the scenario math puts the breaker-only path at 46.9% — short of the 48% target. The disagreement is surfaced on slide 3 rather than hidden.

### Numbers deliberately kept off the slides

- **Day-30 +14 points (p=0.12).** Not significant at n=50/arm. The memo says do not quote it. It appears nowhere.
- **"We went from 27% to 76%."** Control's own 46% means 15–19 points came from something else. The honest claim is the +30-point within-week delta only.
- **"Send 4 is our best send" / 42% vs 4% open rate as proof.** The rising open curve is likely survivorship, and the control arm looks un-instrumented. Not load-bearing.
- **Absolute cost-of-waiting in users.** TBD, needs quarterly signup volume from growth. Flagged as TBD on slide 2, not estimated.

---

## Slide 1 — The problem

**Headline:** Day-7 retention is decaying, and the leak is entirely in week one.

**Kicker (top of slide, for Marcus):** *Asking for one more cohort and a scope ruling — not full rollout.*

**The one number:** Day-7 fell 37% → 27% across weeks 1–4, roughly 3 points per week, with no sign of flattening. Target is ≥48%; actual is 39%. A 9.4-point gap.

**The one insight:** Day-1 is flat at 90–93% across all five cohorts. Acquisition quality and the install-day experience are not the problem. Everything we lose, we lose between day 1 and day 7.

**Leave off:** week-5's 61%, which belongs to slide 4. Theme detail from research. Anything about the mechanic yet.

**Transition:** "So we know where the leak is. Here's what we learned about what's behind it."

---

## Slide 2 — Why now

**Headline:** We finally sized the problem, and it is not the one we scoped.

**What changed:**
- The streak-break segment is large and worst-retaining: 190 users, 38% of the base, 26.8% Day-7 against 45.8% for everyone else — a 19-point gap, p < 0.0001.
- **But 55% of Day-7 churn never broke a streak at all.** Of 307 users who failed Day-7, 168 had an intact streak.
- So the lost-streak moment is worth **at most 7.2 points of the 9.4-point gap.** Real, but not the majority of the problem.

**What we learned:** The original rationale — streak loss is the churn driver — is directionally right and materially incomplete. We were about to commit a sprint to the smaller half.

**Cost of waiting:** The decay is ~3 points per week and hasn't flattened. Absolute cost in users: **TBD** — one number from growth, available Thursday.

**Transition:** "That sizing is what changes the proposal."

---

## Slide 3 — The proposal

**Headline:** A free, non-punitive comeback flow — re-scoped around the segment the data supports.

**What it is:**
- A free, one-tap path back to a prior streak count, earned by a 60-second comeback lesson, framed as coaching rather than punishment.
- Targeted at the **intact-streak** segment first — 62% of users, and the only significant result we have (93% vs 64%, p=0.007).
- Competitive white space: no competitor offers a free, non-punitive comeback. Duolingo paywalls freeze and repair; Babbel avoids streaks; Elevate, Streaks, and Habitica offer no real recovery.

**What it isn't:**
- **Not a long-term retention fix.** Day-30 is 12.6% for breakers and non-breakers alike. This wins the first week. We should not promise more.
- **Not monetized.** Free by default, per the approved direction.
- **Not the full thing you approved.** You signed off on the recovery flow *plus* early pre-day-7 milestone moments *plus* a state-aware home screen. Only the recovery flow was built and tested. Milestone moments are not in the prototype; the home screen is still a mock. That was my call — a clean read on one variable instead of a muddy read on three — and it means these results cover one-third of what you approved.
- **Not yet settled internally.** The metric analysis recommends leading with streak-breakers; this memo recommends the intact-streak segment. Decision 2 on slide 6 is where that gets ruled on.

**Transition:** "Here's what we actually have behind it."

---

## Slide 4 — Evidence

**Headline:** A real +30-point Day-7 lift — in the segment we weren't aiming at.

**The data (week-5 cohort, 100 users, 50 comeback / 50 control):**

| Segment | Comeback | Control | Delta | Significance |
|---|---|---|---|---|
| All week-5 users | 76% | 46% | +30 pts | p=0.002 ✅ |
| Intact streak | 93% | 64% | +29 pts | p=0.007 ✅ |
| Broke a streak | 50% | 28% | +22 pts | p=0.13 ❌ |

**What the mechanism is:** More returns, not longer sessions. Comeback users logged 5.3 sessions to control's 3.7 at near-identical session length, 240s vs 231s.

**What the mechanism isn't:** Not the notifications. Within the comeback arm, users who never acted on a single send still retained at 73.9% against 77.8% for those who did — 3.9 points, effectively nothing.

**User voice (the problem, which is well-evidenced):**
> "There was no way to recover it, nothing. So I gave up." — Tom, churned after a 12-day break
> "I don't want to lose everything I've built after four days." — Amara, day 4

Streak loss is also the top NPS theme, 6 of 10 free-text comments.

**Three caveats, stated by us:**
1. **n=50 per arm cannot carry a rollout decision.**
2. **Week 5 is confounded.** Control alone hit 46% against 27% in week 4. Roughly 15–19 points came from something that is not this experiment. The honest claim is the +30 within-week delta, not "27% to 76%."
3. **The arms weren't balanced on the variable that matters most.** Streak-break rate was 40% in comeback versus 50% in control, pushing in the direction that flatters us.

**And the finding that should worry us most:** `current_streak` is zero for **all 190 streak-breakers**, including every treated one. The flow restarted zero streaks. It bought returns, not habit.

**Transition:** "Which is why I'm not asking for rollout."

---

## Slide 5 — The plan

**Headline:** Two weeks to a decision-grade read. No new product work.

**Milestones:**
| When | What |
|---|---|
| Thursday | Triad session closes five blocking decisions: eligibility, restore limit, v1 content scope, flow sign-off, instrumentation minimum |
| Friday | Credible rollout date, the day after those close |
| Weeks 1–2 | Second cohort at n≥200 per arm, randomized *on* streak-break status, sized for Day-30 rather than Day-7 |
| Before that cohort | Fix two measurement problems: instrument the control arm, and log send eligibility |

**Why the measurement fixes are non-negotiable:** Control sat at exactly 4.0% open at every send number with zero actions across all 200 rows. That is a logging gap, not a baseline. And open rate *rises* with send number, 28% → 56%, which is almost certainly a wrong denominator rather than escalating effectiveness.

**Risks:**
- **Week-5 control outperformed week 4 by 19 points and we don't know why.** This is the single biggest threat to the read.
- **Engineering has not costed what we built.** Raj scoped a streak *freeze*; the prototype does a retroactive *restore*. His estimate predates the change.
- **Solution evidence is a 3-persona roleplay, not real users.** I would not call this pressure-tested yet.
- **Shipping on n=50 risks rolling out to the wrong 38% of users** and burning the credibility we need for the next engagement bet.

**Transition:** "So, three decisions."

---

## Slide 6 — The ask

**Headline:** Three decisions from you on Thursday.

1. **Approve the second cohort.** Two weeks, no new product work — re-randomization plus instrumentation.
2. **Rule on scope.** Do we keep chasing streak-breakers per the original rationale, or follow the evidence to the intact-streak segment? **I recommend the latter:** it is 62% of users and the only significant result we have. The scenario math is the argument — the breaker lift alone lands Day-7 at **46.9%, short of target**; the non-breaker lift clears it at **56.7%**.
3. **Decide A/B test or staged rollout.** This changes the timeline I bring you.

**What I am not asking for:** full rollout, a sprint commitment, or a rollout date today.

**What you get without asking:** the rollout date Friday, the cost-of-waiting number in users Thursday, and a one-paragraph outcome from the triad session.

**If you are out:** all three can be ruled on async. Decision 2 is the one that cannot wait — it determines what the second cohort randomizes on.
