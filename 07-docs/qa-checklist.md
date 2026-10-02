# QA Checklist — Streakly Comeback Screen

**Owner:** PM (engagement squad)
**Date:** 2026-09-30
**Against:** [spec-readiness.md](spec-readiness.md) acceptance criteria AC-1 – AC-10
**Prototype under review:** [03-build/prototype/index.html](../03-build/prototype/index.html) ([README](../03-build/prototype/README.md))
**Status:** Pre-QA. Prototype is a demo of the happy path, not a build. Findings below separate "prototype doesn't show it" from "spec doesn't define it" — those need different fixes.

---

## 1. Edge case list

Severity: **P0** = blocks launch, **P1** = fix before GA but shippable behind the flag, **P2** = known issue.
"Spec?" = is the behavior defined in [spec-readiness.md](spec-readiness.md)?

### 1.1 Empty states

| # | Case | Expected behavior | Spec? | Sev |
|---|---|---|---|---|
| E1 | User has **never held a streak** (`streak_before_break == 0`) | Not eligible per AC-2. Never sees Comeback screen. Normal home. | ✅ AC-2 | P0 |
| E2 | Streak of exactly 1, broken | Not eligible per AC-2. No "restore your 1-day streak." | ✅ AC-2 | P0 |
| E3 | **No best-streak stat** — best streak equals current broken streak | Badge shows the honest number, or is suppressed. Prototype hardcodes "Personal best · 5 days" in three places. Decide: suppress badge, or show it when `best == streak_before_break`? | ❌ | P1 |
| E4 | Best streak is *lower* than the streak being restored (data skew / backfill) | Best-streak must be recomputed on restore, or the badge shows a "best" below the current streak | ❌ | P1 |
| E5 | **No lessons available in their track** — track exhausted, or content not authored | Comeback screen cannot promise a 60-second lesson it can't serve. Needs a fallback lesson or eligibility must also gate on lesson availability. **Direct dependency on Lena's per-track content scope (open blocker 2).** | ❌ | **P0** |
| E6 | User's track was deprecated / removed since signup | Fallback to a generic comeback lesson, or suppress | ❌ | P1 |
| E7 | User has no `last_completed_lesson` (signed up, did day 1 via onboarding only) | "Your last practice" card must not render empty. Prototype hardcodes "Body Scan · Meditation track." | ❌ | P1 |
| E8 | User has no track selected at all | Should fail AC-2 in practice, but confirm — a user can plausibly have a 2-day streak from onboarding content with no track | ❌ | P1 |

### 1.2 Edge data conditions

| # | Case | Expected behavior | Spec? | Sev |
|---|---|---|---|---|
| D1 | `streak_before_break == 1` | Ineligible (AC-2) | ✅ | P0 |
| D2 | `streak_before_break == 2` (the floor) | Eligible. Confirm copy reads sensibly at 2 — "days one through five" style copy must be dynamic | Partial | P1 |
| D3 | **Broke the streak twice in one week** | No grace remains after an accept → gentler reset copy. **Explicitly descoped v1** (decision 8). QA must confirm the *absence* is graceful: user sees a normal cold reset, not a broken/empty Comeback screen | 🟡 descoped | **P0 (as a no-crash check)** |
| D4 | Broke twice, but **declined** the first time (grace not burned, AC-6) | Still eligible on the second break, subject to AC-4 impression cap. Confirm this is intended — a user could decline, break again, and restore a *later* streak | ✅ implied | P1 |
| D5 | **Grace already used** (`comeback_grace_used == true`) | Ineligible (AC-3). No offer, no screen. | ✅ AC-3 | P0 |
| D6 | Grace used, then user completes another lesson from home | Must not re-offer restore. **Prototype fails this** — see Check 4 below | ✅ AC-3 | **P0** |
| D7 | 3 impressions already shown (AC-4) | 4th eligible launch routes straight to home | ✅ AC-4 | P1 |
| D8 | Restore write **partially fails** — `streak` written, `comeback_grace_used` not (or vice versa) | AC-5 requires atomicity. QA needs a forced-failure test, not just a code read | ✅ AC-5 | **P0** |
| D9 | User **offline** when they tap "restore my streak" | Undefined. Optimistic UI then silent rollback is the worst outcome for a trust-repair feature. **See PR comment in §3.** | ❌ | **P0** |
| D10 | Streak restored to a value that crosses a **badge / milestone threshold** | Coupling risk named in spec 2.3, owner Raj. Must not double-fire a milestone notification. | 🟡 open | **P0** |
| D11 | Two devices, same account, both show the Comeback screen | Restore must be idempotent server-side; second accept is a no-op, not a second restore | ❌ | P1 |
| D12 | User accepts restore, then immediately deletes their account / logs out mid-write | No orphaned grace state | ❌ | P2 |
| D13 | `streak_before_break` never written (feature shipped mid-break for in-flight users) | Migration case. Users mid-break at flag-on have no prior value to restore → must fail eligibility silently, not restore to 0 or null | ❌ | **P0** |
| D14 | Very long streak in week 1 (e.g. 7 days, multiple lessons/day) | Confirm streak counts days not lessons; copy holds at 7 | ❌ | P2 |

### 1.3 Timing scenarios

| # | Case | Expected behavior | Spec? | Sev |
|---|---|---|---|---|
| T1 | Missed **one** day | Core case. Prototype copy: "missed a day." | ✅ | — |
| T2 | Missed **many** days (3, 5, 7) | Copy must be dynamic, and product must decide whether restore is still offered after a long gap. Restoring a 5-day streak after a 6-day absence is a strange promise. Recommend a `missed_day_count` ceiling. | ❌ | **P0** |
| T3 | `days_since_signup == 7` at break, user returns on **day 8** | AC-8: grace evaporates day 8. So an eligible user who doesn't open until day 8 never sees the offer — **and day 7 is the metric we're optimizing.** This is the "comeback shown too late" case and it's a design decision, not a bug: confirm whether eligibility is evaluated at break detection (AC-3) but *rendered* whenever they return, or whether AC-8 hard-blocks the render. **The two rules conflict as written.** | ⚠️ conflict | **P0** |
| T4 | Break detected at `days_since_signup == 7`, screen renders at day 7 + 23h | Same conflict as T3 at finer grain | ⚠️ | P0 |
| T5 | **Time zone boundary** — user travels, local midnight shifts | Break detection must use a single consistent basis (user's registered TZ vs. device TZ vs. UTC). A TZ move west can manufacture a break that didn't happen. | ❌ | **P0** |
| T6 | User crosses a date line; "today" happens twice or not at all | Streak increment must not double-count or skip | ❌ | P1 |
| T7 | Device clock set forward/back manually | Server-side day boundary, not device clock | ❌ | P1 |
| T8 | DST transition night | 23- and 25-hour days must not break the day boundary | ❌ | P2 |
| T9 | Lesson completed at 11:59:50pm local, completion lands after midnight | Which day gets credit? Must be deterministic and favor the user. | ❌ | P1 |
| T10 | User starts the comeback lesson, backgrounds the app, returns 3 hours later | Resume, restart, or grant completion? Prototype has no resume state. Affects `comeback_lesson_completed` integrity. | ❌ | P1 |
| T11 | Feature flag flips off **mid-flow** (AC-10) | In-flight sessions complete, no new entries. Needs an actual test, PM confirmed product-side. | ✅ AC-10 | P1 |
| T12 | Comeback screen shown on the *same* day the break occurred (user opens hours after their window closes) | Confirm it isn't shown before a break is really a break | ❌ | P1 |

### 1.4 Permission states

| # | Case | Expected behavior | Spec? | Sev |
|---|---|---|---|---|
| P1 | **Notifications off** | Feature still works, but the user may never learn the offer exists before it expires on day 8. The grace is time-boxed and the delivery channel is optional — quantify what share of the eligible cohort has notifications off; if it's high, the holdback read is confounded. | ❌ | **P0 (measurement risk)** |
| P2 | Notifications on but push token invalid / unregistered | Same as P1, silently | ❌ | P1 |
| P3 | **Background refresh off** | Can't pre-fetch the comeback lesson → cold-start latency on a screen whose whole value is low friction. Also affects any client-side break detection. | ❌ | P1 |
| P4 | Notification permission requested *by* the Comeback screen | Don't. Asking for a permission at a trust-repair moment is the punitive pattern in a new coat. Confirm no prompt fires here. | ❌ | P1 |
| P5 | iOS provisional / scheduled summary delivery | Comeback push may arrive batched hours late, possibly after day 8 | ❌ | P1 |
| P6 | Notifications off **and** offline at open | Compound: feature must degrade to a normal home screen, never a spinner | ❌ | P1 |
| P7 | User has notifications off and is in the **10% holdback** | Confirm holdback assignment is independent of permission state, or the control group is biased | ❌ | P1 |

---

## 2. PM QA checklist run against the prototype

Method: read [index.html](../03-build/prototype/index.html) screen by screen (comeback → lesson → offer → confirm → home) and traced every `onclick` handler. Ten checks, ranked by what would actually stop a sign-off.

**Framing note:** the prototype is a concept demo, and it succeeds at that. Several fails below are "the prototype doesn't model this," which is expected — they're listed because they're the things that must exist in the *build*, and a QA pass that only walks the prototype's happy path will miss all of them.

| # | What to verify | Verdict | Evidence / note |
|---|---|---|---|
| 1 | **The lesson actually earns the restore offer** (README decision 5) | ❌ **FAIL** | The ✕ button on the lesson screen ([index.html:485](../03-build/prototype/index.html#L485), `title="Skip ahead"`) and "Finish now" ([index.html:499](../03-build/prototype/index.html#L499)) both call the same `finishLesson()` → straight to the offer. A user can tap ✕ within one second and receive the restore. The core earn mechanic is not enforced. In the build this also corrupts `comeback_lesson_completed` — it would fire for users who did nothing. |
| 2 | **Grace is one-time** (AC-3, AC-5) | ❌ **FAIL** | Home screen "Begin practice" ([index.html:561](../03-build/prototype/index.html#L561)) calls `go('screen-lesson')`, which runs the same lesson → same offer screen → restore can be accepted again. `path` is reassigned with no grace-used check. A user who declines can immediately re-enter and accept; a user who accepted can loop. Prototype-only artifact, but it's exactly the state machine engineering will lift. |
| 3 | **Skip does not mutate streak state** (AC-7) | ❌ **FAIL** | `skipToHome()` → `goHome()` renders current streak **0** ([index.html:670](../03-build/prototype/index.html#L670)). AC-7 says skip mutates no streak state; a post-break user's real streak is either the pre-break value (not yet reset) or 1. **0 is not a state the spec defines.** Either the prototype is wrong or the spec's reset semantics are underspecified — worth resolving before the spec is written, because "0" vs "1" vs "5, pending" is the punitive/non-punitive distinction the whole feature turns on. |
| 4 | **Decline resets to 1 and does not burn grace** (AC-6) | ✅ **PASS** (display only) | `chooseFreeze(false)` → home shows **1** ([index.html:665](../03-build/prototype/index.html#L665)), copy "Today is day one, on your terms." Correct per AC-6. No grace-state modeling exists to verify the second half. |
| 5 | **Accept restores to prior value** (AC-5) | ✅ **PASS** (display only) | `chooseFreeze(true)` → home shows **5** + "🌿 streak restored" pill ([index.html:659-663](../03-build/prototype/index.html#L659)). Also satisfies the *spirit* of AC-9 — restored streaks are visually distinguishable. Note for the open PM decision in spec 2.3: **the prototype has already answered it — it marks the restore.** Worth making that the explicit sign-off. |
| 6 | **A dismiss path exists at the offer step** | ❌ **FAIL** | Offer screen ([index.html:503-518](../03-build/prototype/index.html#L503)) has only "Yes, restore" and "No thanks, I'll start fresh." There is no skip/back/defer. The spec deliberately distinguishes skip (no state change, re-shown) from decline (resets to 1) precisely so users aren't forced to choose before they're ready — and the prototype forces the choice at the one moment it matters most. Also blocks `comeback_skipped` from firing with a step property. |
| 7 | **Empty / edge data states render** | ❌ **FAIL** | Every value is hardcoded: "5-day," "missed a day," "Personal best · 5 days" (×3), "Body Scan · Meditation track." No template variables anywhere. E3, E5, E7, D2, T2 are all untested and untestable in this artifact. |
| 8 | **Instrumentation hooks present** (spec 2.4) | ❌ **FAIL** | Zero analytics calls in the file. Expected for a prototype — flagged because spec 2.4 is the section that exists *because* Raj asked twice how we'd measure this. The build must not inherit the prototype's silence, and `comeback_eligible` specifically must be server-side. |
| 9 | **Offline / error handling on the restore write** | ⚠️ **CANNOT DETERMINE** | The prototype does local DOM mutation only. Nothing about network failure, retry, or optimistic-UI rollback is observable. This is D9 and the subject of the PR comment in §3. |
| 10 | **Accessibility of the breathing animation** | ⚠️ **CANNOT DETERMINE → likely FAIL** | `.breathe-circle` animates infinitely ([index.html:235](../03-build/prototype/index.html#L235)) with no `prefers-reduced-motion` guard. In a *meditation* app, a user with vestibular sensitivity gets a pulsing 180px target they can't stop. Separately: inactive screens stay in the DOM at `opacity: 0` with `pointer-events: none` ([index.html:98-99](../03-build/prototype/index.html#L98)) — not hidden from screen readers or tab order, so all five screens are simultaneously reachable assistively. Needs a real audit on the build, not the prototype. |

### Launch blockers vs. known issues

**Blocks launch — must be resolved before sign-off:**

1. **Check 1 + Check 2** (earn mechanic not enforced, grace not one-time). These are the state machine. If engineering builds from the prototype's flow, both defects ship. Highest-value thing to say in the PR.
2. **Check 3** — skip-state semantics (0 vs 1 vs pending) are undefined in the spec and contradicted by the prototype. Cheap to resolve, expensive to discover in production.
3. **D9 / Check 9** — offline behavior on a write that retroactively edits progression state. No defined behavior at all.
4. **D8** — atomicity of the restore write. Spec requires it (AC-5); needs a forced-failure test in QA, not a code read.
5. **D10** — badge/milestone double-fire on restore. Owner Raj, still open. A congratulatory push for a milestone the user didn't earn, at a trust-repair moment, is the exact failure mode this feature exists to avoid.
6. **D13** — users mid-break at flag-on have no `streak_before_break`. Migration case; must fail eligibility silently.
7. **T3 / T5** — the AC-3 vs AC-8 conflict (eligibility at break detection vs. grace expiring day 8), and time-zone basis for break detection. T3 is not a bug, it's an unmade decision that determines whether the feature can even reach the day-7 metric. **Mine to resolve.**
8. **E5** — no lesson available in track. Gated on Lena's content-scope answer (open blocker 2). The screen promises a lesson; eligibility must gate on being able to serve one.
9. **D3** — second break in week 1 is descoped, which is fine, but QA must confirm the descoped path degrades to a clean cold reset rather than a half-rendered Comeback screen.
10. **P1** — quantify notifications-off share of the eligible cohort. Not a bug; a measurement risk that could confound the holdback read. Add to Raj's baseline query while it's already being written.

**Can ship as a known issue:**

- Check 10 accessibility items — file, fix in the sprint after, unless the reduced-motion gap is trivial (it usually is: one media query). Recommend fixing it now given the track is meditation.
- Check 6 (missing defer at offer step) — *if* impressions and re-show work correctly, a user can back out via the OS. Suboptimal, not blocking. Include in the spec regardless.
- T8 (DST), D14 (long week-1 streaks), D12 (account deletion mid-write) — low volume, log and monitor.
- P3 / P5 (background refresh, batched push delivery) — degrade gracefully; measure, don't block.
- Copy at `streak_before_break == 2` (D2) — needs dynamic strings, catchable in string review.
- Hardcoded status bar "9:41," fixed 390×812 frame — prototype artifacts, not build issues.

**Not a defect, worth recording:** the prototype's state-aware home screen (Check 5) is doing real work — the "🌿 streak restored" pill already implements AC-9's user-facing half and pre-answers the open PM question in spec 2.3. Ship the marker.

---

## 3. PR comment for Raj

> Context: Raj's stated preference is short, no surprises, decisions restated not re-argued. This asks one question, gives him the reason it's being asked, and proposes an answer he can accept or correct in one line. It is not a rubber stamp and it is not a demand.

**Comment — leave on the restore-accept handler:**

```
Non-blocking, but I want to ask before this merges since it's a write path
that edits progression state.

What happens if the user taps "restore my streak" while offline?

The two failure shapes I can think of:
- We write optimistically, show "Your streak is restored — back at 5 days,"
  and the write later fails. The user sees the restore, then loses it.
- We block on the network and they get a spinner or an error on the
  screen whose entire job is "this app isn't keeping score against you."

I'm flagging it because this specific moment is the one we're asking users
to trust us with, and a restore that appears and then silently disappears
is worse than never offering it — it confirms the thing the NPS comments
were already saying about the app. It's also the one place where AC-5's
atomicity requirement meets a client that might not be able to honour it.

My lean, tell me if it's wrong or expensive: queue the accept, confirm
optimistically, and treat the grace as unburned until the write lands —
so a failed restore leaves the user eligible to try again rather than
having spent their one grace on nothing. If that's a bigger lift than it
sounds, I'd rather know now and spec a plain "we'll apply this when you're
back online" state than discover it in QA.

Related, and probably the same conversation: does the offline case interact
with the day-8 expiry? If the write queues on day 7 and lands on day 8,
does it still apply? My answer is yes — they acted in the window. Happy to
write that into the spec as an AC if you agree.
```

**Why this one:** of everything in §2, offline behavior is the only blocker that is genuinely invisible from the prototype, isn't already on someone's open-items list, and sits squarely in PM territory — it's a question about what the user is promised, not about how the write is implemented. The state-machine defects (Checks 1–3) go in the spec as acceptance criteria, not as PR comments.

---

## Open items this doc creates

| # | Item | Owner | Status |
|---|---|---|---|
| Q1 | Skip-state semantics: does skip leave the streak at prior value, 1, or 0? | PM | ⬜ |
| Q2 | AC-3 vs AC-8 conflict — eligibility at break detection vs. render after day 8 | PM | ⬜ |
| Q3 | `missed_day_count` ceiling — is restore still offered after a long gap? | PM | ⬜ |
| Q4 | Time-zone basis for break detection (registered TZ / device / UTC) | Raj | ⬜ |
| Q5 | Notifications-off share of the eligible cohort — add to the baseline query | Raj | ⬜ |
| Q6 | Lesson availability as an eligibility gate (depends on content scope) | Lena → PM | ⬜ |
| Q7 | Offline restore semantics + queued-write vs. day-8 expiry | Raj (PR thread) | ⬜ |
| Q8 | Sign off on flagging restored streaks — prototype already does it | PM | 🟡 recommend yes |
