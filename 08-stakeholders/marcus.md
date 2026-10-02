# Marcus — Head of Product

**Legend:** 📁 = came directly from a workspace file (cited) · 🧩 = from the default profile you supplied · 💭 = my inference from workspace evidence (verify)

---

## Role

📁 Head of Product ([01-orient/project.md:14](../01-orient/project.md)).
🧩 Owns product strategy, roadmap prioritization, and the relationship with the exec team and board.

## His relationship to this project

📁 **He is the approver, and he has already approved.** Two documents were written directly for him — [07-docs/decision-brief.md](../07-docs/decision-brief.md) ("To: Marcus, Head of Product ... For: Thursday kickoff") and [02-research/nps-analysis.md](../02-research/nps-analysis.md) ("For: Marcus", with a dedicated "Summary for Marcus" section).

📁 **What he approved, in full** ([07-docs/pm-brief.md:13](../07-docs/pm-brief.md), [07-docs/hypothesis.md](../07-docs/hypothesis.md)):
> a free, non-punitive streak-recovery flow **+ early (pre-day-7) milestone moments + a state-aware home screen**

💭 **This is the most important thing in this file: he approved three things and one was built.** The prototype is the recovery flow. Early milestone moments do not appear in the prototype at all. The state-aware home screen is a **mock** ([07-docs/pm-brief.md](../07-docs/pm-brief.md), flow step 5). Your own hypothesis doc flags this as unresolved — "whether the state-aware home screen ... is required alongside this Comeback screen, or whether the Comeback screen alone captures most of the effect" ([07-docs/hypothesis.md](../07-docs/hypothesis.md)).

💭 If he reads the brief before the meeting — which he does — he will notice the delta between what he signed off on and what exists. You want to name the descope yourself, with a reason, rather than have him find it.

## Open items

🧩 He asked for a **rollout timeline** before committing to the Q3 sprint.

📁 You cannot fully answer this yet. The implementation sprint begins "in 8 weeks (exact date: TBD)" ([01-orient/project.md](../01-orient/project.md)), and five blocking decisions are still open — eligibility, restore limit, v1 content scope, flow sign-off, and instrumentation minimum ([07-docs/triad-session.md](../07-docs/triad-session.md)).

💭 The triad session is the unlock. Its entire purpose is to close those five. A credible timeline for Marcus is downstream of that session, which means **triad first, Marcus second** — and if you go to him before the triad, the answer is "I'll have it after Thursday," which is a wasted conversation with someone who wants the ask in the first sentence.

## What he pushes back on

🧩 Recommendations without a clear ask. Data not connected to a business outcome. Anything needing more than one page to explain.

📁 [07-docs/decision-brief.md](../07-docs/decision-brief.md) is already built to this spec — one page, recommendation stated, three options considered, "Why Now" section. It is the right artifact. Reuse its shape.

## What he needs before saying yes

🧩 A clear **why now**. A specific **ask with a deadline**. Confidence the team has **pressure-tested** the idea.

📁 Why-now is strong and already written: top NPS theme (6/10 comments), the explicit churn reason from a real interview subject, and unclaimed competitive white space — no competitor offers a free, non-punitive comeback ([07-docs/decision-brief.md](../07-docs/decision-brief.md), [02-research/competitive-matrix.md](../02-research/competitive-matrix.md)).

💭 Pressure-tested is your weak flank. What exists is a 3-persona **roleplay**, self-labeled "not real users" ([07-docs/hypothesis.md](../07-docs/hypothesis.md)), and the technical feasibility read is stale — Raj scoped a streak-*freeze*, the prototype does a retroactive *restore* ([07-docs/triad-session.md](../07-docs/triad-session.md)). "Pressure-tested" to him means eng and design have both stress-tested it. Neither has, yet.

## Questions he has asked before that you struggled to answer

🧩 "What is the cost of waiting another quarter?"
🧩 "How does this affect our **Day-7 retention** number specifically?"

📁 You have more material than you may realize for the second one. Day-7 is the named core metric, 39% against a ≥48% target — a 9-point gap ([07-docs/pm-brief.md](../07-docs/pm-brief.md)). Missing two days in a row **roughly doubles churn**, and the drop is sharpest among week-1 streak-breakers ([01-orient/project.md](../01-orient/project.md), [01-orient/strategy.md](../01-orient/strategy.md)).

📁 **But the sizing is missing, and your own doc says so:** "The real quantitative size of the opportunity: how many of the users behind the 9-point Day-7 drop actually hit a 'lost streak' moment versus lapsing for other reasons. Neither research doc cites a funnel breakdown" ([07-docs/hypothesis.md](../07-docs/hypothesis.md)).

💭 That funnel number is the whole answer to both of his questions. Cost-of-waiting is (lapsed week-1 users per quarter × reachable share × expected lift). Without the denominator you cannot size the bet, and he cannot defend it to the exec team. **This is one query against data you already have** — and unlike the instrumentation gap, it does not require shipping anything. Get it before you see him.

## Communication preference

🧩 Reads the brief before the meeting. Wants the recommendation in the **first sentence, not the last**. Follows up async if he needs detail.

💭 [07-docs/decision-brief.md](../07-docs/decision-brief.md) buries its recommendation under Situation → Key Findings → Options. Structurally correct for a decision memo, wrong for this reader. Lead with the ask.

---

## Gaps I could not fill from either source

- What else is competing for the Q3 sprint.
- Whether free-by-default has a revenue implication he cares about (competitors monetize this — Duolingo paywalls freeze/repair).
- His tolerance for shipping the Comeback screen alone vs. all three approved pieces.
- Whether he expects a real A/B test or is comfortable with a staged rollout.
