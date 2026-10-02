# Objection Log — Streakly Comeback Screen PRD

**Reviewed:** [prd.md](prd.md) · **Date:** 2026-10-02 · **Reviewers:** Raj (Engineering), Marcus (Head of Product), Tom (churned user)
**Purpose:** Pre-triad pressure test. Two hardest objections per reviewer, plus the one most likely to kill the initiative.
**Profiles used:** [raj.md](../08-stakeholders/raj.md) · [marcus.md](../08-stakeholders/marcus.md) · Tom from [interview-synthesis](../02-research/interview-synthesis.md)

---

## 1. Raj — Engineering Lead

### R1. "Your own PRD says my feasibility read is stale. Why is it still in Open Questions instead of re-scoped?"

**Why he asks:** His conditional yes — "doable with existing systems, no new data sources" — was scoped against Lena's **one-tap streak-freeze** (a flag set before the day boundary). The prototype does a **full retroactive restore** of a value the system already overwrote. That is new persisted state, not new logic.

**Why it bites:** The PRD documents the staleness itself (Open Question 3) but brings it to a live review rather than in writing beforehand. He is async-first and has said he does not want surprises in standups. The real question is "why am I reading this here?"

**Codebase context:** Streak reset and penalty logic share a code path; day-boundary processing bundles a dozen unrelated jobs ([codebase-summary](codebase-summary.md)). A restore bug corrupts user state instead of failing quietly.

**To close it:** Send the scope change async before Thursday. Arrive with a rollback plan unprompted, plus a ripple-risk answer for badges / milestones / leaderboards.

### R2. "How will we know if this is working after it ships? And what happens if a user breaks the streak twice in a week?"

**Why he asks:** He has asked both before — twice. The third ask is a blocker, not curiosity.

**Why it bites:** The PRD answers neither.
- Four of five success metrics are TBD; attribution is admitted broken (four levers ship together); instrumentation is listed as a question *for him* when it is a product decision.
- Restore limit is "proposal: once per user" and "undecided and untested" in the same breath.

**Expected form:** "I'm not scoping a sprint against a metrics table that's four TBDs and an admitted attribution problem."

**To close it:** State eligibility and restore limit as decisions you own, with reasoning, for him to stress-test. Name a minimum instrumentation set yourself.

---

## 2. Marcus — Head of Product

### M1. "I approved three things. Which one is this, and where are the other two?"

**Why he asks:** He signed off on *a free, non-punitive recovery flow + early pre-day-7 milestone moments + a state-aware home screen*. The PRD non-goals descope the home screen to "mocked, not designed." Early milestone moments do not appear at all — not even as a non-goal.

**Why it bites:** He reads the brief before the meeting and will find the delta himself. Worse, the PRD's own problem statement argues that between day 4 and day 30 users have "something to lose and nothing new to gain" — which is precisely the milestone gap that got dropped.

**To close it:** Name the descope yourself, with a reason and a sequencing plan for the other two pieces.

### M2. "How many users actually hit a lost-streak moment? Give me the number, or the cost of waiting a quarter."

**Why he asks:** Both are standing questions he has asked before.

**Why it bites:** The PRD concedes there is no answer — "No funnel breakdown exists for how many of the 9-point drop actually hit a lost-streak moment versus lapsing for other reasons." Without the denominator the bet is unsizeable and indefensible to the exec team.

**Compounding:** His "pressure-tested" precondition is unmet — what exists is a self-labelled 3-persona roleplay plus a stale engineering read. Design has not stress-tested it; engineering's read predates the scope change.

**Also expect:** the rollout-timeline ask, which cannot be answered until the five blocking decisions close. **Triad first, Marcus second.**

**To close it:** One query against data already in hand. Cost-of-waiting = lapsed week-1 users per quarter x reachable share x expected lift.

---

## 3. Tom — Churned user (broke a 12-day streak at week 5, switched to Duolingo)

### T1. "I broke a 12-day streak at week 5. Your eligibility rule is first 7 days only. I wouldn't have been offered this at all, would I?"

**Why it bites:** Sharpest hole in the document. The PRD opens with Tom as the headline churn quote — "There was no way to recover it, nothing. So I gave up" — then defines the user as "first 7 days, reference case 5 days, Amara's position, not Priya's," and proposes first-7-days-only, once per user. Tom is the proof point and the excluded case at the same time.

**To close it:** Either widen eligibility beyond week 1, or stop using Tom as the lead evidence and lead with Amara.

### T2. "A 60-second breathing exercise gives me my 12 days back? That makes the 12 days feel like they were worth 60 seconds."

**Why it bites:** Tom wanted a forgiving way back, not a cheap one. Two failures:
- **Too easy relative to what was lost.** Twelve days restored by one minute reads as the streak never mattered — a different flavour of the same demoralization. The PRD flags this risk ("cheapens the streak for long-tenured users") and leaves it unvalidated.
- **He already left and will never see the screen.** Break detection fires only on next app open; the Comeback screen rewards returning, and Tom's failure mode was *not returning*. Notification fixes are scoped out as secondary — valid only "if lapsed users open the app at all." For Tom they don't.

### Does it solve why Tom stopped?

**Partially.** It fixes the *reset-as-punishment* feeling, which is the right diagnosis of his emotional experience. It does not reach him: wrong eligibility window, and no mechanism to pull a churned user back into the app.

---

## Which objection is most likely to kill the initiative

**M2 — Marcus's sizing question.**

Not the hardest objection; the most lethal one, because of who asks it and what they do with the answer.

- **Raj's objections delay the sprint.** Painful, fixable in a week, and he has already said yes in principle.
- **Tom's objections change the design.** Expensive, but nobody in the room votes on them — they are evidence for you to act on.
- **Marcus is the approver, and he cannot say yes to an unsized bet.** He has to defend Q3 sprint capacity to the exec team with a number. The current case is 6 of 10 NPS comments, three interviews, a synthetic roleplay, and a 9-point Day-7 gap of which an **unknown fraction is addressable**.

The arithmetic is the argument. If only ~15% of lapsed week-1 users hit a lost-streak moment, the ceiling on this work is ~1.4 points of Day-7 and the initiative is the wrong priority. If it is ~60%, it is obviously the right one. You do not know which, and he will notice in the first sentence that you do not.

**Why this one and not the others:** it is the only killer objection you can fully close *before* it is asked. One query against existing data, nothing to ship, and it answers both of his standing questions at once. Walking in without it is a choice.

**Runner-up (close):** R1 — Raj discovering the freeze -> retroactive-restore scope change live in the room. That damages credibility rather than the initiative, which is recoverable, and it is free to prevent with a short async note before Thursday.

---

## Pre-triad checklist derived from the above

- [ ] Async note to Raj: freeze -> retroactive restore, in writing, before Thursday
- [ ] Funnel query: share of the 9-point Day-7 drop that hits a lost-streak moment
- [ ] Eligibility + restore limit restated as owned decisions, not open questions
- [ ] Rollback plan drafted unprompted
- [ ] Ripple-risk answer: badges, milestones, leaderboards
- [ ] Descope of milestone moments + state-aware home screen named explicitly, with reasoning
- [ ] Reconcile Tom-as-evidence with the week-1 eligibility proposal
