# Lena — Designer

**Legend:** 📁 = came directly from a workspace file (cited) · 🧩 = from the default profile you supplied · 💭 = my inference from workspace evidence (verify)

---

## Role

📁 Designer on the Streakly engagement squad ([01-orient/project.md:16](../01-orient/project.md)).
🧩 Owns end-to-end user experience, interaction design, and design system consistency for Streakly.

## Her standing in this project — read this first

📁 **The Comeback screen is Lena's idea.** She proposed it: "on streak break, show the user's best-streak stat, a 60-second comeback lesson, and a one-tap streak-freeze" ([01-orient/project.md:43](../01-orient/project.md), [01-orient/strategy.md:21](../01-orient/strategy.md)). The triad agenda acknowledges this — the session "builds on Lena's original Comeback screen concept" ([07-docs/triad-session.md](../07-docs/triad-session.md)).

💭 **This changes the whole dynamic and it is the thing most likely to go wrong.** Everyone else on this project is being sold a concept. Lena is being shown *her own* concept after it was taken through a PM interview, materially redesigned, built into a prototype, and roleplay-tested — all without her in the room. Specifically, these were decided without her ([07-docs/pm-brief.md](../07-docs/pm-brief.md), "Key decisions made during the interview"):

| Her original concept | What was built | Who decided |
|---|---|---|
| One-tap streak-**freeze** | Full retroactive streak **restore** | PM interview, decision 3 |
| (unspecified surface) | Full-screen takeover, not a modal | PM interview, decision 4 |
| Three parallel elements | Sequential — lesson **earns** the freeze offer | PM interview, decision 5 |
| (unspecified tone) | Zen / acceptance framing, meditation track | PM interview, decision 2 |

💭 Every one of those is a design decision made by a PM. Her default-profile pushback — "copy that reads like it was written by a product manager" — is going to land directly on the acceptance-framed copy, which was in fact written by a product manager. Get ahead of this by naming it yourself before she finds it.

## Open items

📁 The triad agenda queues three questions for her ([07-docs/triad-session.md](../07-docs/triad-session.md)):
1. Does the current tone/visual execution (zen/acceptance framing, full-screen takeover) **match what she had in mind** when she first proposed this, or does it need to shift?
2. The demo is meditation-only — does lesson content need to be **bespoke per track**, or can v1 be generic?
3. Any **interaction polish** (motion, pacing, the breathing animation) to address before it goes into a spec?

🧩 She wants to revisit the streak-freeze UI after seeing Amara's feedback.

📁 **That feedback exists and it is hers to see.** In the 2026-09-30 roleplay test, the Amara persona hit the lesson screen — breathing cues, no track label — and reacted with "did I open the wrong app." Logged as "a trust break, not just a nitpick, for the exact day-4-ish segment this feature exists to save" ([01-orient/change_log.md](../01-orient/change_log.md)).

📁 A fix was already applied without her: adding "· Meditation" to the lesson screen header ([01-orient/change_log.md](../01-orient/change_log.md)).

💭 That fix is a label patch on a structural problem. The lesson content itself is meditation-specific (breathing cues) regardless of the header. For a language-learning user, a correctly-labeled breathing exercise is still the wrong lesson. Bring her the finding as an unsolved design problem rather than a closed one — the workspace currently treats it as closed.

## What she pushes back on

🧩 Feature requests that skip the problem definition. Copy that reads like a PM wrote it. Anything adding cognitive load without clear user benefit.

💭 The problem definition is unusually strong here and you should lead with it — [02-research/interview-synthesis.md](../02-research/interview-synthesis.md) has five themes across three real interviews, and Theme 2 ("losing a streak feels like punishment, not feedback") is effectively a design brief written by users.

## What she needs before saying yes

🧩 Evidence from **real users**, not assumptions. A clear definition of the primary user and their context. An understanding of what the **empty state** looks like.

📁 **Partial credit, and one honest problem.** You have real evidence for the *problem*: three actual interviews, plus NPS where 6/10 comments trace to the streak reset and users ask for "a coach, not a scorekeeper" ([02-research/nps-analysis.md](../02-research/nps-analysis.md)). The primary user is sharply defined: a 5-day streak, one missed day, day 4–7 window — Amara's exact position ([07-docs/pm-brief.md](../07-docs/pm-brief.md), decision 1).

📁 But the evidence for the *solution* is a **3-persona roleplay, explicitly labeled "roleplay, not real users"** ([07-docs/hypothesis.md](../07-docs/hypothesis.md)). Do not present that as user validation to the stakeholder whose stated bar is real users. Name it as synthetic.

💭 **The empty state is genuinely unaddressed anywhere in the workspace.** Nothing covers: a user with no prior streak, a user who declines the restore and lands at day 1, or a user arriving nine days late. From [07-docs/codebase-summary.md](../07-docs/codebase-summary.md), that last case is real — break detection only fires when the user next opens the app, so "you broke your streak" can arrive over a week late. She will ask. There is currently no answer.

## Questions she has asked before that you struggled to answer

🧩 "What does the user do **after** they see the Comeback screen?"
🧩 "How do we make a broken streak feel **forgiving** instead of like a guilt trip?"

📁 You now have a real answer to the second one — the zen/acceptance framing, and the "that's allowed" tone that tested positively even with a churned skeptic ([07-docs/hypothesis.md](../07-docs/hypothesis.md)).

💭 The first is still thin. The flow ends at a "mocked state-aware home screen" ([07-docs/pm-brief.md](../07-docs/pm-brief.md)) — mocked, not designed. "What happens next" is literally a placeholder in the prototype she is about to be walked through.

## Communication preference

🧩 Prefers to **see** things rather than read about them. Responds well to "here is what users told us" framing.

💭 Both are well-served by the current plan: there is a clickable prototype at [03-build/prototype/index.html](../03-build/prototype/index.html), and the triad agenda gives her questions first, before Raj's ([07-docs/triad-session.md](../07-docs/triad-session.md)). Keep that order.

---

## Gaps I could not fill from either source

- Whether she has already seen the prototype or the roleplay findings.
- Her view on the freeze → retroactive restore change.
- Design system constraints for a full-screen takeover on a lapsed-user launch.
- Whether per-track content is a design ask or a content-ops ask in her view.
