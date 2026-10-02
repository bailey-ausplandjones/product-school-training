# Spec Readiness — Streakly Comeback Screen

**Reviewer:** Raj (Engineering Lead) — roleplay review session, 2026-09-30
**Inputs reviewed:** [decision-brief.md](decision-brief.md), [pm-brief.md](pm-brief.md), [hypothesis.md](hypothesis.md), [triad-session.md](triad-session.md), [codebase-summary.md](codebase-summary.md), [08-stakeholders/raj.md](../08-stakeholders/raj.md)
**Outcome:** Not blocked on direction. Blocked on two named items, both owned and dated.

---

## 1. Spec readiness summary

### What was solid

- **Problem definition.** Three real interviews, NPS with 6/10 comments tracing to one cause, and a competitive scan that identifies genuine white space. This never came under pressure in the review because it didn't need to. Most specs fail here; this one doesn't.
- **Primary user, sharply drawn.** 5-day streak, one missed day, day 4–7 window, mapped to a named research persona. Specific enough to design and build against.
- **Honest unknowns.** [hypothesis.md](hypothesis.md) self-reports its own weaknesses — the four-levers attribution problem, the missing funnel breakdown, the roleplay-not-real-users caveat. That honesty is what made the review fast: no time spent discovering things the doc was hiding.
- **Decision velocity under questioning.** Eligibility and restore-limit rules were closed in two exchanges. Those were the real holes, and they shut cleanly.
- **The tone work.** "Coach, not scorekeeper" → zen/acceptance framing is a clean line from evidence to execution.

### What needed work

| Gap | Severity | Status |
|---|---|---|
| **No spec exists.** Three briefs, no acceptance criteria, no edge cases, no rollback plan. | High | Acknowledged; this doc is the input to writing one |
| **Scope drifted from freeze → retroactive restore** during prototype build, unannounced. Invalidated the standing feasibility estimate. | High | Resolved — restore confirmed as the intended feature, deliberately |
| **Eligibility undefined.** "First week" conflated streak length with tenure — would have let an 8-month user with a 3-day streak claim a first-week grace. | High | Resolved — two gates |
| **Restore limit undefined.** An unbounded restore was unbuildable; both roleplay personas had already flagged it and it was deferred. | High | Resolved — one-time, expires day 8 |
| **Five edge cases unaddressed** (no prior streak, decline, skip, expiry, second break). | High | Four resolved; second-break descoped with owner |
| **Win/kill numbers set against the wrong baseline.** 39% and ≥60% are all-user Day-7 figures applied to a cohort that churns at roughly double the rate. Kill-at-39% could have killed a feature that moved the cohort +13 points. | **High — still open** | Baseline query owned by Raj, 2 days |
| **No instrumentation.** A retention feature with no way to read retention. | High | Resolved — funnel + outcome + holdback designed |
| **No rollback plan** for a write path that retroactively edits user progression state. | High | Resolved — flag + 10% holdback doubles as kill switch |
| **"Retained" undefined**, then set to `opened`, then corrected to `completed a lesson`. | Medium | Resolved — completed is headline, opened logged as secondary |
| **Per-track content scope** unanswered; gates the sprint estimate. | Medium — **open** | Lena's call |
| **Marcus approved three things; one was built.** Early milestones absent, state-aware home screen mocked only. | Medium — open | Not an eng blocker; a Marcus conversation |

### The two blockers

1. **Cohort baseline** — % of users with `days_since_signup <= 7` who broke a streak of ≥2 and completed a lesson on day 7, last 90 days. Also returns weekly volume (needed to know whether a 10% holdback can reach significance). **Owner: Raj. 2 days.**
2. **Per-track content scope** — generic copy vs. per-track content. Generic is small; per-track needs new authoring infrastructure and is a different sprint. **Owner: Lena.**

### The pattern worth noticing

Raj's profile records two questions he had asked before and not gotten answers to: *"how will we know if this is working after it ships?"* and *"what happens if the user has never set a streak, or breaks it twice in a week?"* Both came up again in this review, and both were answerable in minutes once asked directly. Neither was hard — they were just unasked. The instrumentation section below exists because of the first one; edge cases 1 and 5 exist because of the second.

---

## 2. Rewrites — the sections that were unclear

### 2.1 Eligibility

> **Superseded:** "first week," left undefined, later proposed as "streak under 7 days, not a calendar week."
> **Problem:** streak length is not tenure. An 8-month user whose streak has fallen to 3 days satisfies a streak-only rule but is not the target population and is not in the retention drop.

**A user is eligible for the Comeback screen when ALL of the following are true at the moment of break detection:**

| # | Criterion | Rule |
|---|---|---|
| AC-1 | Tenure gate | `days_since_signup <= 7` |
| AC-2 | Streak floor | `streak_before_break >= 2` |
| AC-3 | Grace available | `comeback_grace_used == false` |
| AC-4 | Impression cap | `comeback_impressions < 3` |

**Acceptance criteria**
- AC-1: A user with `days_since_signup == 8` who breaks a 4-day streak is **not** eligible.
- AC-2: A user who completes day 1 and misses day 2 (`streak_before_break == 1`) is **not** eligible. No "restore your 1-day streak."
- AC-3: Eligibility is evaluated at break detection, not at screen render.
- AC-4: On the 4th eligible launch, skip the Comeback screen and route straight to home.

---

### 2.2 Restore mechanic and grace rules

> **Superseded:** "one-tap streak-freeze" (original concept) vs. "accepting restores the current streak to its prior value" (as built). These are different features and the discrepancy was unreconciled.
> **Resolution:** Retroactive restore is the intended feature. Freeze cannot meet the user at the post-lapse moment the prototype was designed and tested around.

**Mechanic:** on accept, `streak` is written back to `streak_before_break`. This is a retroactive increase to user progression state, not a prevented reset.

**Grace rules**

| Rule | Behavior |
|---|---|
| Allowance | One per account, first week only |
| Expiry | Evaporates at `days_since_signup == 8`, used or not. Does not bank. |
| Accept | Burns the grace. Streak restored to prior value. |
| **Decline** | **Does NOT burn the grace.** Streak resets to 1. |
| **Skip / dismiss** | **Does NOT burn the grace.** Re-shown on next launch while AC-1–AC-4 hold. |
| Second break in week 1 | No grace remains → gentler reset copy. **Out of scope v1.** Owner: PM + Lena. |

**Acceptance criteria**
- AC-5: Accept sets `streak = streak_before_break` and `comeback_grace_used = true`, atomically.
- AC-6: Decline sets `streak = 1`, leaves `comeback_grace_used = false`.
- AC-7: Skip mutates no streak state; increments `comeback_impressions` only.
- AC-8: At `days_since_signup == 8`, grace is unavailable regardless of prior state.
- AC-9: A restored streak is distinguishable from an earned one in the data (see 2.3).

**Rationale on decline/skip:** burning a user's grace for declining, or for not being ready, is the punitive pattern this feature exists to remove. It would also make the one measurable act of restraint the most expensive one.

---

### 2.3 Data model

> **Superseded:** "no new data sources required" (standing feasibility estimate, given against the freeze concept).
> **Status:** stale. A retroactive restore requires new persisted state. Three new fields, spec owned by Raj, PM review.

| Field | Type | Written | Notes |
|---|---|---|---|
| `streak_before_break` | int | At break detection, **before** the reset | Without this the prior value is unrecoverable |
| `comeback_grace_used` | bool | On accept | Lifecycle bounded by AC-8 |
| `comeback_impressions` | int | On each render | Drives AC-4 |
| `streak_restored_at` | timestamp, nullable | On accept | **Open for PM sign-off** — see below |

**Open question for PM:** should a restored streak be flagged as restored, or indistinguishable from an earned one?

Recommend flagging it. Two reasons: the power-user persona's objection in the roleplay was specifically about streak integrity, and without a marker we can never answer *"do restored streaks survive at the same rate as earned ones?"* — which is the question that determines whether the mechanic works or just moves the churn later.

**Coupling risk to investigate:** anything downstream that reads streak length — badges, milestones, achievement thresholds — may double-fire or go inconsistent when a streak is written back up. Owner: Raj. PM to specify which of those surfaces must stay correct in v1.

---

### 2.4 Instrumentation

> **Superseded:** absent. [hypothesis.md](hypothesis.md) acknowledged four levers shipping together with no attribution path.

**Layer 1 — Funnel**

| Event | Fires | Note |
|---|---|---|
| `comeback_eligible` | Break detected, AC-1–AC-4 pass | **Server-side. This is the denominator.** |
| `comeback_screen_viewed` | Screen renders | |
| `comeback_lesson_started` | CTA tapped | |
| `comeback_lesson_completed` | 60s complete | |
| `comeback_restore_offered` | Offer unlocks | |
| `comeback_restore_accepted` / `_declined` | One-tap | |
| `comeback_skipped` | Dismiss | + step abandoned at |

Properties on all: `streak_length_at_break`, `days_since_signup`, `track`, `missed_day_count`, `impression_number`, `grace_state`.

**`comeback_eligible` must fire server-side at break detection, not on render.** Client-only logging cannot distinguish "nobody converted" from "nobody came back to see it." Those are different failures with different fixes.

**Layer 2 — Outcome**

- **Cohort:** users passing AC-1 + AC-2
- **Primary metric:** % who **complete a lesson** on day 7
- **Secondary:** % who **open** on day 7 — logged alongside, to separate "never returned" from "returned and didn't engage"
- **Baseline:** ⬜ unknown — blocking. Raj, 2 days.
- **Win / kill:** ⬜ to be re-set against that baseline. The prior ≥60% / 39% were all-user figures applied to a cohort that churns at roughly double the rate; kill-at-39% risked killing a genuine double-digit improvement.

**Layer 3 — Attribution and rollback (one mechanism)**

Ship behind a feature flag with a **10% holdback** receiving today's cold reset.

- Clean control group → a real read on the concept, rather than a before/after against a redesign that already moved the number
- Kill switch without a deploy — mandatory for a write path that retroactively edits progression state
- **Not** proposing per-lever isolation. Four cells exceeds available week-1 break volume. Concept-level read now; decompose if it works.

**AC-10:** flag off mid-flow → in-flight sessions complete, no new entries. **PM to confirm.**

---

## 3. Async Slack message — scope confirmation

> Paste into DM with Raj. Written to his stated preference: short, bulleted, no surprises, decisions restated rather than re-argued.

```
Raj — writing up what we landed on so it's in one place before kickoff.
Nothing new here, just confirming. Correct anything I got wrong.

CONFIRMED — FEATURE
• Retroactive streak restore, not a freeze. Deliberate call, not drift.
  Freeze can't meet the user post-lapse, which is the whole feature.
• Your "no new data sources" estimate is retired. New fields below.

CONFIRMED — ELIGIBILITY (all must be true at break detection)
• days_since_signup <= 7
• streak_before_break >= 2
• comeback_grace_used == false
• comeback_impressions < 3

CONFIRMED — GRACE
• One per account, first week only. Evaporates day 8, used or not.
• Accept → restore to prior streak, burns grace
• Decline → reset to 1, does NOT burn grace
• Skip → no streak change, does NOT burn grace, re-shown until gate closes
• Impression cap 3, then soft-dismiss to home

CONFIRMED — MEASUREMENT
• Cohort = passes tenure + streak-floor gates
• Retained = COMPLETED A LESSON on day 7 (primary)
• Opened on day 7 logged as secondary
• comeback_eligible fires server-side at break detection
• Feature flag + 10% holdback = control group and kill switch

OUT OF SCOPE v1
• Second break in week 1 / gentler reset copy — me + Lena
• Per-lever attribution — volume won't support 4 cells
• Early milestone moments + real state-aware home screen — part of
  Marcus's approved direction, not in this build. I'm raising it with him.

OPEN — BLOCKING YOUR ESTIMATE
1. Cohort baseline + volume — you, 2 days. Win/kill numbers re-set after.
   My ≥60% / 39% were all-user figures on a cohort that churns ~2x. My error.
2. Per-track content scope — Lena. Generic vs. new authoring infra.
   Chasing today.

OPEN — ON ME, ANSWERS THIS WEEK
3. Flag a restored streak as restored? My lean: yes. Priya's integrity
   objection, and we can't otherwise answer "do restored streaks survive."
4. Which streak-reading surfaces must stay correct in v1 (badges,
   milestones, achievements) — tell me what's coupled, I'll prioritise.
5. Flag flips off mid-flow → in-flight completes, no new entries.
   Confirming that's fine product-side: yes.

NEXT
• You: baseline query + field spec
• Me: Lena on content scope, then the real spec doc with the eligibility
  rules and edge cases written as acceptance criteria, not prose
• Then: your estimate, and we commit at kickoff

Two things I owe you an acknowledgement on: the scope change should have
reached you from me in writing, not from a brief. And you'd asked twice
how we'd measure this after ship — that's designed now and it's in the doc.
```

---

## Appendix — decision log

| # | Decision | Made by | Status |
|---|---|---|---|
| 1 | Retroactive restore, not freeze | PM, confirmed with Raj | ✅ |
| 2 | Tenure gate `days_since_signup <= 7` | PM | ✅ |
| 3 | Streak floor `>= 2` | PM | ✅ |
| 4 | One-time grace, expires day 8 | PM | ✅ |
| 5 | Decline does not burn grace | PM | ✅ |
| 6 | Skip does not burn grace; re-show until gate closes | PM | ✅ |
| 7 | Impression cap 3 → soft-dismiss | Raj proposed, PM to confirm | 🟡 |
| 8 | Second break in week 1 out of scope v1 | PM | ✅ owner: PM + Lena |
| 9 | Retained = completed a lesson | PM (revised from `opened`) | ✅ |
| 10 | Flag + 10% holdback | Raj | ✅ |
| 11 | No per-lever attribution v1 | Raj | ✅ |
| 12 | Cohort baseline before win/kill re-set | Raj | ⬜ 2 days |
| 13 | Per-track content scope | Lena | ⬜ blocking estimate |
| 14 | Flag restored streaks in data | Raj proposed, PM sign-off | 🟡 |
| 15 | Coupled streak-reading surfaces | Raj investigating | 🟡 |
