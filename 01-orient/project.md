# Streakly Comeback — PRD Skeleton

*Draft from Slack thread, pre-Thursday alignment meeting. Starting point only — not finished.*

## Project Overview

**What Streakly is:** a consumer habit + micro-learning app that helps people learn a skill in five minutes a day. Users pick a track, do a short daily lesson, and build a streak — the streak is the core habit loop. Launched 4 years ago, Series B funded ($42M). 2.1M registered users, 340K monthly active users, growing 28% YoY on MAU.

**My squad:** Engagement squad — own first-week activation (home screen, daily lesson loop, streak mechanics, push notifications).

**Current phase:** Discovery, pre-kickoff. Aligning on the problem statement ahead of Thursday's meeting, where the team starts planning the fix. Implementation sprint begins in 8 weeks (exact date: TBD).

**Key stakeholders:**
- Marcus — Head of Product
- Raj — Engineering lead
- Lena — Designer
- Me — PM, engagement squad

## Problem Statement

Day-7 retention dropped from 48% to 39% following the streak redesign. The drop is sharpest among users who break their streak in week 1 — once a user misses two days in a row, churn is almost double.

Hypothesis: users go passive after breaking a streak because the app treats the break as a cold reset (streak counter back to zero, no acknowledgment, same home screen) rather than offering a way back in. The "you lost your streak" push notification has a harsh tone and doesn't offer anything when tapped — it just drops the user at day zero. Users experience this as failure, and there's currently no graceful comeback path.

Open question raised but not resolved: how much of the drop is driven by the streak-reset experience itself vs. notification timing/tone. Team's current focus is on the post-break experience.

## Goals

- Give users a way back in after breaking a streak that feels specific to their progress, not a generic "keep going" message.
- Reduce the passivity/churn that follows a broken streak in week 1.

## Non-Goals

- Not yet defined in the thread — to be confirmed with the team before Thursday.

## Success Metrics

- Not yet defined in the thread — to be confirmed with the team before Thursday.
- Reference baseline: Day-7 retention at 39%, down from 48% pre-redesign.

## Notes / Context from Thread

- Proposed direction (Lena): a "Comeback screen" shown on streak break, showing best-streak stat, a 60-second comeback lesson, and a one-tap streak-freeze.
- Feasibility (Raj): technically doable with existing systems; needs logic for targeting/eligibility and streak-freeze rules; no new data sources required.
- Next step: align on the problem statement before designing solutions, ahead of Thursday's meeting.
