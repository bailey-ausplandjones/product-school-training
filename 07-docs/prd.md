# PRD — Streakly Comeback Screen

**For:** Raj (Engineering), Lena (Design) · **From:** PM, Engagement Squad · **Status:** Draft for triad review
**Sources:** [interview-synthesis](../02-research/interview-synthesis.md) · [nps-analysis](../02-research/nps-analysis.md) · [competitive-matrix](../02-research/competitive-matrix.md) · [hypothesis](hypothesis.md) · [decision-brief](decision-brief.md)

---

## Problem Statement

The streak mechanic has no state between "intact" and "zero." A single missed day erases the full count with no recovery path.

- Day-7 retention fell from 48% to 39% after the v2 redesign. Target is ≥48%.
- Streak loss is the top NPS theme — 6 of 10 free-text comments — and is named directly in churn: "I hit a 20-day streak, missed one day, and it reset to zero. I haven't opened the app since."
- Tom broke a 12-day streak at week 5 and left: "There was no way to recover it, nothing. So I gave up."
- Loss-aversion anxiety starts at day 4, before any habit exists. Amara: "I don't want to lose everything I've built after four days."
- The only positive reinforcement arrives around day 30 (Priya's celebration). Between day 4 and day 30 users have something to lose and nothing new to gain.
- Users name the framing they want: "a coach that helps me get back on track, not a scorekeeper that punishes me."
- Competitive position: Duolingo paywalls its freeze and leads with loss-framing before offering repair; Elevate and Streaks reset outright; Habitica substitutes a different penalty; Babbel avoids streaks. A free, non-punitive comeback is unclaimed ([competitive-matrix](../02-research/competitive-matrix.md), Gap 1).

## User

**Who:** A user in their first 7 days who reached a short streak (reference case: 5 days), missed one day, and has not opened the app since. This is Amara's position, not Priya's — the day 4–7 fragile zone, pre-habit.

**Job to be done:** Get back in without feeling they lost everything.

**Context of use:** The user is opening the app after an absence. Break detection fires only on next app open ([codebase-summary](codebase-summary.md)), so the "you broke your streak" moment can arrive days late. The Comeback screen is the first thing they see.

## Goals and Non-Goals

**Goals**
1. Give a lapsed first-week user a free, one-tap path back to their prior streak count, earned by completing a 60-second comeback lesson.
2. Frame the missed day as acceptable, not as failure.
3. Protect the user's best-streak stat so something is never at risk.
4. Recover Day-7 retention toward 48%.

**Non-Goals**
1. Monetizing recovery. Free by default, per the Marcus-approved direction.
2. De-emphasizing streaks. The ritual is what made Priya's experience stick.
3. Notification cadence and targeting fixes. Real (NPS theme 2, 3 mentions) but scoped separately as secondary in the [decision-brief](decision-brief.md).
4. Per-track lesson content. v1 is meditation only. See Open Questions.
5. The state-aware home screen. Approved in the same recommendation but specified separately; in this prototype it is mocked, not designed.

## Success Metrics

| Metric | Baseline | Target |
|---|---|---|
| Day-7 retention (primary) | 39% | ≥48% |
| Comeback screen → lesson start | n/a | TBD |
| Lesson start → completion | n/a | TBD |
| Completion → restore accepted | n/a | TBD |
| Return-and-continue rate for users who miss a day in week 1 | n/a | TBD |

Two measurement constraints, both open and both blocking a clean read:
- **Attribution.** Four levers ship together — loss-framing, the restored number, the lesson content, and the state-aware home screen. Current instrumentation cannot attribute effect to any one ([hypothesis](hypothesis.md)).
- **Opportunity size.** No funnel breakdown exists for how many of the 9-point drop actually hit a lost-streak moment versus lapsing for other reasons. Neither research doc cites one.

## User Stories

1. **Return without loss.** As a user who hit a 5-day streak and missed a day, I want to see that my progress is recoverable when I open the app, so I come back instead of deleting. *(Tom; NPS "make coming back easier instead of making me feel like I failed.")*
2. **Earn it back.** As a returning user, I want completing one 60-second lesson to restore my streak to its prior value, so showing up is what earns the recovery.
3. **Not be scolded.** As a returning user, I want the copy to treat the missed day as allowed, so the moment reads as coaching rather than punishment. *(NPS: "a coach, not a scorekeeper.")*
4. **Leave if not ready.** As a user who does not want to engage right now, I want a visible skip that does not punish me, so dismissal is not a second loss.
5. **Keep what I earned.** As a user who declines the restore, I want my best-streak stat intact, so a fresh start at day 1 still shows what I achieved.

## Open Questions

**Product decisions I owe Raj, framed as proposals to stress-test, not open questions**
1. *Eligibility.* Proposal: first 7 days only, lapse of 1–2 days. Needs his read on targeting logic.
2. *Restore limit.* Proposal: once per user as a first-week grace. Undecided and untested in [hypothesis](hypothesis.md); the answer changes the mechanic's meaning.
3. *Scope change he has not yet seen in writing.* His feasibility yes — "doable with existing systems, no new data sources" — was scoped against Lena's original **one-tap streak-freeze**. The prototype does a **full retroactive restore** of a value the system already overwrote. That is new persisted state, not new logic. His assessment is stale.
4. *Ripple risk.* Does rewriting a streak count break badges, milestones, or leaderboards? Streak reset and penalty logic share a code path; day-boundary processing bundles unrelated jobs ([codebase-summary](codebase-summary.md)).
5. *Rollback plan.* A restore bug corrupts user state rather than failing quietly. Required before sprint, not after.
6. *Instrumentation.* Which events are missing today to test the Day-7 hypothesis at all. Blocks the TBDs in Success Metrics.

**Design questions for Lena**
7. *Authorship.* Four decisions were made on her concept without her: freeze → retroactive restore, full-screen takeover over modal, sequential flow where the lesson earns the offer, and the zen/acceptance tone. The copy she will read was written by a PM.
8. *Track identity is an unsolved problem, not a closed one.* The Amara roleplay hit the lesson screen and said "did I open the wrong app." A "· Meditation" header label was added ([change_log](../01-orient/change_log.md)), but the content itself is breathing cues. For a language learner, a correctly labelled breathing exercise is still the wrong lesson. Open: bespoke per track, or generic v1.
9. *Empty states, unaddressed anywhere in the workspace.* A user with no prior streak. A user who declines and lands at day 1. A user arriving nine days late because detection only fires on app open.
10. *What happens after.* The flow currently ends at a mocked state-aware home screen. Not designed.

**Evidence status, stated plainly**
11. Evidence for the **problem** is real: 3 interviews, 10 NPS comments. Evidence for the **solution** is a 3-persona roleplay, explicitly labelled "roleplay, not real users" ([hypothesis](hypothesis.md)). It is synthetic. Whether real users convert on this screen at a rate that moves Day-7 retention is unknown.
12. Assumptions still unvalidated: that free-by-default is not abused and does not cheapen the streak for long-tenured users; that the meditation example generalizes across tracks; that notification fixes are correctly secondary — which depends on lapsed users opening the app at all.
13. `02-research/competitive-reddit.md` does not exist in this workspace. Competitive claims above come from [competitive-matrix](../02-research/competitive-matrix.md) only. Qualitative user-voice evidence on competitor comeback flows is a gap.
