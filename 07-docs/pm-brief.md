# PM Brief — Streakly Comeback Screen

**Project:** Streakly Comeback experience
**Owner:** PM, Engagement Squad (first-week activation: home screen, daily lesson loop, streak mechanics, push notifications)
**Core metric:** Day-7 retention (slipped 48% → 39% after v2 redesign; target ≥48%)
**Status:** Prototype scoped and approved, ready to build

## Grounding research

- [02-research/interview-synthesis.md](../02-research/interview-synthesis.md) — Tom's churn story (12-day streak → zero, no recovery), Amara's day-4 loss-aversion anxiety, Priya's day-30 celebration moment. Core insight: the product has only one emotional register for the streak before day ~30 — accumulating pride that can be erased overnight.
- [02-research/nps-analysis.md](../02-research/nps-analysis.md) — 6/10 comments trace to the all-or-nothing streak reset; users explicitly ask for "a coach, not a scorekeeper."
- [02-research/competitive-matrix.md](../02-research/competitive-matrix.md) — no competitor offers a genuinely free, non-punitive comeback flow (Duolingo paywalls its freeze/repair; others offer no recovery at all). Open white space.
- [07-docs/decision-brief.md](decision-brief.md) — Marcus-approved direction: free, non-punitive streak-recovery flow + early (pre-day-7) milestone moments + a state-aware home screen.

## Original PM brief

- **User:** 24-year-old who hit a streak, missed one or more days, and has not opened the app since.
- **Job to be done:** Get back in without feeling they lost everything.
- **Feature set:** Personalized Comeback screen, best-streak stat, one 60-second comeback lesson, one-tap streak-freeze offer.
- **Constraint:** Use data Streakly already has. No new integrations.

## Key decisions made during the interview

1. **Persona narrowed to the first-week fragile zone.** Rather than a 12-day streak (the original brief's example), the prototype uses a user who hit a **5-day streak and missed 1 day** — placing them squarely in the day 4–7 anxiety window the interview synthesis identifies (Amara's exact position), not the day-30+ power-user territory (Priya's).
2. **Track: meditation, framed through zen/acceptance.** The comeback lesson and copy lean into meditation's own language of acceptance — treating a missed day as something to accept and release, not a failure to atone for. This directly answers the "coach, not scorekeeper" ask from NPS.
3. **Completing the comeback restores the streak, not just a separate best-streak badge.** Revised from an earlier direction where the current streak would reset regardless of the freeze decision: accepting the streak-freeze offer (which unlocks after the mini-lesson) now restores the current streak to its prior value (5 days) — the user picks up exactly where they left off, rather than starting over. Declining still resets to a fresh start (day 1). The best-streak badge (5 days) is shown throughout regardless of path, so it's never at risk. The first screen states this restoration outcome up front, as the incentive to complete the comeback rather than a surprise revealed only after finishing.
4. **Full-screen takeover, not a modal.** The Comeback screen is the first thing the user sees on opening the app after a lapse — a full-screen experience, not an overlay — with a clear, low-friction dismiss/skip action for users who aren't ready to engage.
5. **Sequential flow, lesson earns the freeze offer.** The two features are not independent — the user completes the 60-second comeback lesson *first*, and the streak-freeze offer unlocks afterward as a result of showing up, rather than being offered unconditionally up front.
6. **Fully clickable prototype.** All three actions (start lesson, accept freeze, dismiss) drive real state transitions: lesson → completion → freeze offer → confirmation, or dismiss → mocked state-aware home screen underneath.
7. **Data used (no new integrations):** streak length before the break, missed-day count, best streak, last-completed lesson/track (meditation) — all data Streakly already has.

## Flow

1. **Full-screen Comeback screen** — personalized copy ("Hit a 5-day streak... missed a day... acceptance-framed") + best-streak badge (5 days) + a clear callout that finishing today's comeback restores the streak to 5 + primary CTA ("Start your 60-second comeback") + a visible skip/dismiss action.
2. **60-second comeback lesson** — simulated meditation micro-lesson (breathing/timer moment, acceptance-themed guidance copy).
3. **Lesson complete** → **streak-restore offer unlocks** ("You showed up. Restore your streak?") with a one-tap accept (or decline).
4. **Restore accepted** → confirmation state: streak restored to 5 days, picking up right where they left off; declined → fresh start at day 1. Best-streak badge (5 days) visible either way.
5. **Dismiss at any point** → mocked state-aware home screen reflecting the post-comeback (or skipped) state, non-punitive tone throughout.

## Deliverables

- [07-docs/pm-brief.md](pm-brief.md) — this document
- [03-build/prototype/index.html](../03-build/prototype/index.html) — single-file interactive clickable prototype
- [03-build/prototype/README.md](../03-build/prototype/README.md) — brief + interview decisions, scoped for the prototype folder
