# Design Review — Streakly Comeback Screen

**Reviewed with:** Lena (Design) · 2026-09-30
**Artifact:** [03-build/prototype/index.html](../03-build/prototype/index.html)
**Evidence base:** [02-research/interview-synthesis.md](../02-research/interview-synthesis.md) (3 real interviews) · [01-orient/change_log.md](../01-orient/change_log.md) (3-persona roleplay — synthetic, flagged as such)
**Outcome:** Direction signed off, with four states owed by design and one scope change owed to engineering.

---

## Where the prototype is right

| Working | Evidence |
|---|---|
| The "zero" moment no longer reads as punishment. *"That's allowed — it doesn't erase what you practiced."* The word zero never appears. | **Tom:** "Came back to a big fat zero. The app sent me this 'you lost your streak' notification that just made me feel bad." |
| A recovery path exists, free, no currency gate | **Tom:** "There was no way to recover it, nothing. So I gave up." / "A streak freeze feels forgiving." |
| Personal-best badge is never at risk — renders on all three paths | **Amara:** "I don't want to lose everything I've built after four days." |
| Track identity survives the full flow (3 touchpoints) | **Amara** (roleplay): "Did I open the wrong app" |
| Declining is a legitimate path, not a penalty | **Priya** (roleplay): free forgiveness reads as "too easy" |
| Recovery is a practice, not a dialog box | **Amara:** "The first few lessons were genuinely fun." |

Lena's own read: *"the tone is right — 'that's allowed' is the line I would have written."* The concept is not in question. What follows is scope and states.

---

## Decisions made in this review

| # | Question | Decision | Owner |
|---|---|---|---|
| 1 | Is this a week-1 feature or a churned-user recovery feature? | **Week-1 feature.** Milestone moments return to v1 scope. | PM |
| 2 | Does the lesson gate the restore, or is the restore unconditional? | **The lesson gates it.** | PM |
| 3 | What counts as lesson completion? | **40 of 60 seconds.** Timer keeps running so nobody feels cut short. *(Revised from a hard 60 on Lena's recommendation.)* | PM, on Lena's rec |
| 4 | What does the lesson `✕` do? | **Exits to home. Does NOT burn the grace.** Offer reachable next launch. | PM |
| 5 | Can the user retry in-session? | **Yes — restarts the 60.** Free re-entry. | PM |
| 6 | Which missing states are in v1? | **All three,** plus skip-path copy. | Lena |

### Why #1 was the pivotal one

The first answer given was "churned-user recovery feature." That answer breaks on its own evidence:

- **Tom is not eligible for Tom's feature.** He churned at week 5 off a 12-day streak. The gates in [spec-readiness.md](spec-readiness.md) are `days_since_signup <= 7` and `streak >= 2`. He fails the first by four weeks.
- **The metric wouldn't match.** Churned-user recovery is a reactivation funnel. The committed hypothesis is Day-7 retention.
- **Amara's fix hadn't been descoped — it had quietly fallen off.** Marcus approved three things: the recovery flow, *early pre-day-7 milestone moments*, and a state-aware home screen. The second was never built; the third is a mock. The milestone moments **were** the answer to synthesis §4.

Revised to "week-1 feature," which puts milestone moments back in v1.

### Why #3 was revised

A hard 60-second gate turns a phone call into a lost streak — reproducing Tom's experience in miniature inside the screen built to prevent it. It also contradicts its own copy: the lesson reads *"Let yesterday go. You're here now — that's the whole practice"* while a bar rejects 58 seconds. Priya's "too easy" objection is still answered at 40 seconds: you showed up, you breathed, you earned it. What's given up is punishing near-misses.

---

## Gaps still open

### Prototype defects — fix before this becomes a spec

1. **The lesson doesn't gate anything.** `index.html:494` (`✕`) and `:500` ("Finish now") both call `finishLesson()`, routing straight to `screen-offer`. A user can restore in one second without breathing. Per decision 2+3, both must respect the 40-second threshold. **Until this is fixed, the offer screen's copy — *"You showed up"* — is false.**
2. **The skip path states something untrue.** *"Your streak is paused, not gone."* AC-8 evaporates the grace at day 8, used or not. It is not paused; it is on an unshown countdown. This is the precise mechanism by which Tom's roleplay reaction — *"is this a trick"* — becomes literally correct: skip on day 4, read "paused," return day 9, find it gone, and he was right.
3. **Skip and decline report inconsistently.** Skip → `Current streak 0`. Decline → `Current streak 1`. The user who decided nothing gets the harsher number than the one who actively declined.

### Needs not addressed by the current build

| Gap | Evidence |
|---|---|
| **No non-streak pride object before day 7.** The only one is `Personal best · 5 days` — the streak count with a medal on it. | Synthesis §4: the week-1 fix "should be about giving new users something other than the streak count to feel proud of before day 7." **Priya:** "It took me about three weeks to get there, and I think most people quit long before the habit forms." |
| **Amara's actual state is untouched.** She's at day 4, streak intact, doing loss math. She never sees this screen. | **Amara:** "I don't want to lose everything I've built after four days." / "The pressure is starting to feel like a chore instead of a game." |
| **Restore rules still unexplained on-screen.** No mention that it's one-time or expiring. | **Priya:** "too easy" · **Tom:** "is this a trick" (roleplay; logged as deferred) |
| **Content is structurally meditation-only.** The applied fix was a header label; the body is breathing cues and a countdown. | **Amara** (roleplay): "Did I open the wrong app" |
| **Repeat exposure undesigned.** AC-4 re-shows up to 3×; the prototype has one impression state. | **Amara:** "a chore instead of a game" |
| **Nothing establishes a returning rhythm.** Flow ends on a static home screen. | **Priya:** "It has become a ritual." |

---

## The single highest-impact change for week-1 retention

**Build the early non-streak milestone — something honestly celebratable by roughly day 3 — and treat the Comeback screen as the second feature, not the first.**

Three reasons, in order of weight:

**1. Reach.** The Comeback screen can only fire for users who both signed up within 7 days *and* broke a streak of ≥2. That's a fraction of week 1. A day-3 milestone reaches every new user. Raj's baseline query will size the comeback-eligible population; the milestone population is "everyone," and no query is needed to know that.

**2. It's what the research actually concluded.** Synthesis §4 is explicit that softening the loss is "a Tom-shaped fix," and that week 1 needs something other than the streak count to be proud of before day 7. The prototype is an excellent Tom-shaped fix. The named week-1 insight is still unbuilt.

**3. It addresses cause rather than consequence.** The Comeback screen improves how a break *feels*. A day-3 milestone reduces how much a break *costs*, because the streak stops being the only thing the user has. Amara's problem at day 4 isn't that breaking would feel bad — it's that the streak is the sole store of value and it's fragile. Give her a second store of value and the loss math changes for the entire cohort, broken streak or not.

The honest constraint: nobody has designed this yet, and "you did three lessons" is a participation trophy Amara will read as one. Priya's lock-in came from *the app celebrating something real*. Finding the day-3 equivalent is genuine design work — which is why it belongs to Lena and why it needs its own space in the spec rather than a line item.

---

## Ownership split

### Product decisions (PM)

- **Feature framing** — week-1 vs. churn-recovery ✅ decided
- **Whether the lesson gates the restore** ✅ decided
- **Completion threshold** — 40s ✅ decided *(a product/eng rule; Lena advises on tone consequences)*
- **Grace economics** — one-time, day-8 expiry, what burns it ✅ decided
- **Eligibility gates** — tenure + streak floor ✅ in spec-readiness
- **Impression cap** — 3 then soft-dismiss ✅ in spec-readiness
- **Whether milestone moments ship in v1** ✅ decided — yes
- **Success metric and win/kill numbers** — blocked on Raj's baseline
- **Whether restored streaks are flagged in data** — open
- **Second-break-in-week-1 policy** — deferred, PM + Lena

### Lena owns

- **The day-3 milestone concept** — what is honestly celebratable that early, and what avoids reading as a participation trophy
- **The four missing states:** 2-day streak (does that badge really read `Personal best · 2 days`?), impression 3 vs. impression 1, non-meditation lesson body, new skip-path copy that doesn't misstate the grace
- **Lesson bail states** — what 0–39 seconds looks and feels like now that a gate exists
- **All copy.** The current copy was written by a PM and one line is currently false. Hand it over.
- **Interaction polish** — motion, pacing, the breathing animation
- **Design-system fit** for a full-screen takeover on a lapsed-user launch

### Shared / needs a third party

- **Restore-rule transparency on-screen** — Lena executes, PM decides how much rule to expose (Priya and Tom both asked; it's still deferred)
- **Per-track content scope** — Lena's call on whether generic copy works; **gates Raj's sprint estimate**
- **Post-flow ritual** — the "what do they do after" question, asked twice and still thin. Home is a static screen.

---

## Immediate actions

| # | Action | Owner | When |
|---|---|---|---|
| 1 | **Tell Raj milestone moments are back in v1.** A second feature, in writing, from you — not discovered in a doc. His stated pushback is mid-sprint scope growth. | PM | Today |
| 2 | Fix the prototype gate (`✕` + "Finish now" must respect 40s) | Prototype owner | Before spec |
| 3 | Rewrite skip-path copy — remove "paused, not gone" | Lena | Thursday |
| 4 | Resolve skip=0 vs. decline=1 inconsistency | PM | Thursday |
| 5 | Four states delivered | Lena | Thursday |
| 6 | Raise the descope with Marcus — he approved three things, one shipped | PM | Before kickoff |
| 7 | Per-track content answer → unblocks Raj's estimate | Lena | ASAP |
