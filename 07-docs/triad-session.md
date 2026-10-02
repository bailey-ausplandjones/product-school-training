# Triad Session — Streakly Comeback Prototype Review

**Attendees:** Me (PM), Raj (eng lead), Lena (designer)
**Length:** 30 minutes
**Purpose:** Walk Raj and Lena through the tested Comeback screen prototype, get their reactions, and leave with a shared set of decisions before writing a spec.

**Inputs going in:** [03-build/prototype/index.html](../03-build/prototype/index.html), [07-docs/pm-brief.md](pm-brief.md), [07-docs/hypothesis.md](hypothesis.md), [01-orient/change_log.md](../01-orient/change_log.md) (roleplay-test findings).

---

## Agenda

| Time | Segment | What happens |
|------|---------|--------------|
| 0–3 min | Framing | Recap the problem (Day-7 retention 48%→39%), the approved fix direction, and why this session exists: this builds on Lena's original Comeback screen concept, now tested across 3 rounds — I want their eyes on it before it becomes a spec. |
| 3–15 min | Live walkthrough | Click through the prototype live, all three paths: accept restore, decline, skip. Pause deliberately at the two places testing surfaced findings — (a) the lesson screen's track-identity gap, (b) the unexplained restore mechanic. |
| 15–22 min | Reactions | Lena's questions first (design/content), then Raj's (technical). See framing below. |
| 22–28 min | Decisions | Walk the decision list below one by one; get an explicit answer or a named owner + deadline for each — don't leave any as "TBD" without an owner. |
| 28–30 min | Recap + next step | Read back the decisions, confirm who drafts the spec and by when. |

### What to show
- The full click-through: comeback screen → 60-second lesson → restore offer → confirmation → state-aware home, for all three paths (accept / decline / skip).
- The specific screen where track identity was missing before the last fix (lesson header), and why that mattered in testing (Amara's "did I open the wrong app" reaction).
- The current restore mechanic as built: accepting fully restores the prior streak count (5 days), not just a preserved best-streak badge — this is a change from the original "streak-freeze" pitch and is worth naming explicitly.

### Questions to ask

**For Lena (designer):**
- Does the current tone/visual execution ("that's allowed," zen/acceptance framing, full-screen takeover) match what you had in mind when you first proposed this, or does it need to shift?
- The demo is meditation-only. If a user's actual track is language-learning or something else entirely, does this content need to be bespoke per track, or can we write it generically enough to not need that investment for v1?
- Any interaction polish (motion, pacing, the breathing animation) you want addressed before this goes into a spec?

**For Raj (eng lead):**
- What exactly should qualify a user to see this screen — missed 1 day? 2? Only within the first 7 days, or any lapse ever?
- How many times should a user be able to use the restore mechanic — once per lapse, capped weekly, or a one-time first-week grace? (Note: this is a bigger ask than the original "streak-freeze" you scoped — it's a full retroactive restore, not just preventing a reset.)
- Does restoring a streak's count ripple into anything else that reads streak length — badges, milestones, leaderboards? Any risk there?
- If Lena's answer requires track-specific content, does that need new content-authoring infrastructure, or can it reuse what exists?
- What analytics/instrumentation is missing today that we'd need to actually test the Day-7 hypothesis?

### Decisions we need to walk out with
1. **Eligibility rule** — what specifically triggers this screen (missed-day threshold, time window).
2. **Restore limit** — how often a user can use the restore mechanic (per-lapse / weekly cap / one-time first-week grace).
3. **v1 content scope** — generic copy across all tracks vs. per-track content investment, directly informed by the track-identity finding.
4. **Sign-off (or named changes)** on the full-screen takeover + sequential lesson-then-offer flow as the direction to spec.
5. **Instrumentation minimum** — what events must exist before this ships, to be able to measure the Day-7 retention hypothesis at all.

---

## Post-Session Alignment Doc (template)

*Fill this out immediately after the session and share with all three attendees same day.*

# Streakly Comeback — Triad Alignment (2026-XX-XX)

**Attendees:**

**What we reviewed:** [link to prototype/brief]

## Decisions made

| # | Decision | Rationale | Owner | Follow-up needed |
|---|----------|-----------|-------|-------------------|
| 1. Eligibility rule | ___ | ___ | ___ | ___ |
| 2. Restore limit | ___ | ___ | ___ | ___ |
| 3. v1 content scope | ___ | ___ | ___ | ___ |
| 4. Flow sign-off | ___ | ___ | ___ | ___ |
| 5. Instrumentation minimum | ___ | ___ | ___ | ___ |

## Open questions (not resolved this session)

- ___

## Next steps

- Spec draft owner: ___
- Target date: ___
- Next checkpoint: ___
