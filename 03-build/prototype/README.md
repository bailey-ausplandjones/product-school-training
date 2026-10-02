# Streakly Comeback Screen — Prototype

Open [index.html](index.html) in a browser to try the clickable flow.

## PM brief

- **User:** 24-year-old who hit a streak, missed one or more days, and has not opened the app since.
- **Job to be done:** Get back in without feeling they lost everything.
- **Feature set:** Personalized Comeback screen, best-streak stat, one 60-second comeback lesson, one-tap streak-freeze offer.
- **Constraint:** Use data Streakly already has. No new integrations.

Grounded in [02-research/interview-synthesis.md](../../02-research/interview-synthesis.md), [02-research/nps-analysis.md](../../02-research/nps-analysis.md), [02-research/competitive-matrix.md](../../02-research/competitive-matrix.md), and the Marcus-approved [07-docs/decision-brief.md](../../07-docs/decision-brief.md): build a free, non-punitive streak-recovery flow with early milestone moments and a state-aware home screen. Full detail in [07-docs/pm-brief.md](../../07-docs/pm-brief.md).

## Key decisions made during the interview

1. **Persona narrowed to the first-week fragile zone** — a 5-day streak, 1 missed day (Amara's day-4-ish position), not the original brief's 12-day example. This targets the day 4–7 anxiety window the interview synthesis calls out, ahead of the day-30 milestone that currently gives users their first reason to feel proud.
2. **Track: meditation, framed through zen/acceptance** — copy and the comeback lesson lean into meditation's own language of acceptance, directly answering the NPS ask for "a coach, not a scorekeeper."
3. **Completing the comeback restores the streak** — accepting the streak-restore offer (unlocked after the mini-lesson) brings the current streak back to its prior value (5 days), picking up right where they left off, rather than resetting to zero. Declining still resets to a fresh start (day 1). The best-streak badge (5 days) is shown throughout regardless of path. The first screen states this restoration outcome up front as the incentive to finish the comeback.
4. **Full-screen takeover, not a modal** — it's the first thing the user sees after a lapse, with a clear, low-friction skip/dismiss action for anyone not ready to engage.
5. **Sequential flow — the lesson earns the restore offer** — the streak-restore offer unlocks only after completing the 60-second comeback lesson, rather than being handed out unconditionally.
6. **Fully clickable prototype** — every action drives a real state transition: lesson → completion → restore offer → confirmation, or skip → state-aware home screen.
7. **Data used, no new integrations** — streak length before the break, missed-day count, best streak, last-completed lesson/track (meditation).

## Flow in the prototype

1. **Comeback screen** (full-screen) — acceptance-toned copy, best-streak badge, a callout stating that finishing today's comeback restores the streak to 5, "Start your 60-second comeback" CTA, and a "Not now — take me home" skip.
2. **60-second lesson** — a breathing/timer moment (compressed to ~12 real seconds for demo pacing), with a "Finish now" option.
3. **Restore offer** — unlocks after the lesson: "You showed up," with a one-tap "restore my streak" accept or a "start fresh" decline.
4. **Confirmation** — accept restores the streak to 5 ("right where you left off"); decline resets to a fresh day 1. Best-streak badge still shown either way.
5. **Home screen** — state-aware: current streak (5 if restored, 1 if declined, 0 if skipped) and the practice-card messaging change accordingly.

Use the **↻ Restart** control above the phone frame to replay the flow from any state.
