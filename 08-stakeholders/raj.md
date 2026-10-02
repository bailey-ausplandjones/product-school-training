# Raj — Engineering Lead

**Legend:** 📁 = came directly from a workspace file (cited) · 🧩 = from the default profile you supplied · 💭 = my inference from workspace evidence (verify)

---

## Role

📁 Engineering lead on the Streakly engagement squad ([01-orient/project.md:15](../01-orient/project.md)).
🧩 Owns technical architecture, sprint scope, and feasibility decisions for the squad.

## What he has already said on this project

📁 **He has already given a conditional yes on feasibility.** His read: the Comeback screen concept is "technically doable with existing systems; needs logic for targeting/eligibility and streak-freeze rules; no new data sources required" ([01-orient/project.md:44](../01-orient/project.md), [01-orient/strategy.md:21](../01-orient/strategy.md)).

📁 That yes was scoped against **Lena's original concept**: best-streak stat, 60-second lesson, and a **one-tap streak-freeze** ([01-orient/project.md:43](../01-orient/project.md)).

📁 **The thing that has since changed underneath him:** the built prototype does not prevent a streak reset — it **fully restores the prior streak count retroactively** after the lesson ([07-docs/pm-brief.md](../07-docs/pm-brief.md), decision 3). The triad agenda already names this explicitly as "a bigger ask than the original 'streak-freeze' you scoped — it's a full retroactive restore, not just preventing a reset" ([07-docs/triad-session.md](../07-docs/triad-session.md)).

💭 So his "feasible, no new data sources" assessment is **stale**, and he does not yet know it is stale. A prevent-the-reset freeze is a flag set before the day rolls over. A retroactive restore has to recover a value the system already overwrote — that is new persisted state, not new logic. This is the single biggest credibility risk in your next conversation with him.

## Open items

📁 Unanswered questions the triad agenda has queued for him ([07-docs/triad-session.md](../07-docs/triad-session.md)):
1. **Eligibility rule** — missed 1 day? 2? First 7 days only, or any lapse ever?
2. **Restore limit** — once per lapse, weekly cap, or one-time first-week grace?
3. **Ripple risk** — does restoring a streak count break anything else that reads streak length (badges, milestones, leaderboards)?
4. **Content infrastructure** — if per-track lesson content is needed, does that require new authoring infra?
5. **Instrumentation** — what analytics are missing today that we'd need to test the Day-7 hypothesis at all?

🧩 Still waiting on **data model clarification for the streak-freeze field**.

💭 Note that items 1, 2, and 5 are framed in the agenda as questions *for* Raj — but they are **product decisions, not engineering ones**. Eligibility and restore limits are yours to answer. If you bring them to him as open questions, you will read as underspecified to the one stakeholder who pushes back hardest on exactly that. Reframe them as proposals for him to stress-test.

## What he pushes back on

🧩 Underspecified requirements. Scope that grows mid-sprint. Anything touching the streak or notification pipeline without a clear rollback plan.

💭 Evidence this is well-founded, from [07-docs/codebase-summary.md](../07-docs/codebase-summary.md): in a Habitica-style architecture, streak reset and HP/damage logic share a code path, and day-boundary processing bundles a dozen unrelated jobs into one function. A streak-restore bug does not fail quietly — it corrupts user state. His rollback-plan instinct is correct and you should arrive with one, unprompted.

## What he needs before saying yes

🧩 Clear acceptance criteria. Edge cases called out upfront. An answer to "what does done look like."

## Questions he has asked before that you struggled to answer

🧩 "How will we know if this is working after it ships?"
🧩 "What happens if the user has never set a streak, or breaks it twice in a week?"

📁 **Both are still open, and both are now documented gaps.** On measurement: [07-docs/hypothesis.md](../07-docs/hypothesis.md) admits four levers ship simultaneously (loss-framing, the restored number, the lesson, the state-aware home screen) with no way to attribute effect to any one. On the double-break edge case: "whether streak restoration should be available every time a user lapses, or only once — this is undecided and untested."

💭 He is going to ask both again. He has asked twice. The third time is not curiosity, it is a blocker.

## Communication preference

🧩 Async first. Short messages. Bullets over paragraphs. Does not like being surprised in standups.

💭 Which means the scope change from freeze → retroactive restore must reach him **in writing, before the triad session** — not discovered live during the walkthrough. The current agenda plans to surface it in a live demo ([07-docs/triad-session.md](../07-docs/triad-session.md), "worth naming explicitly"). That is precisely the surprise he has told you he doesn't want.

---

## Gaps I could not fill from either source

- Sprint capacity and what else is committed for Q3.
- His actual estimate range for restore-vs-freeze.
- Whether he has a position on free-by-default (abuse risk is an eng concern too).
- 📁 Implementation sprint starts ~8 weeks from 2026-09-28; **exact date still TBD** ([01-orient/project.md](../01-orient/project.md)).
