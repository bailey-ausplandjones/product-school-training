# Learning Synthesis & Hypothesis — Streakly Comeback

**Sources:** [07-docs/decision-brief.md](decision-brief.md) (Marcus-approved fix direction) and [01-orient/change_log.md](../01-orient/change_log.md) (prototype build + 3-persona roleplay test).

## What we know

- Day-7 retention fell from 48% to 39% after the v2 redesign — a 9-point drop, and the target to recover.
- The all-or-nothing streak reset is the single highest-leverage, most-cited issue: top NPS theme (6/10 comments) and the explicit reason a churned interview subject (Tom) gave for leaving.
- Loss-aversion anxiety starts as early as day 4, before any habit has formed (Amara) — users are asked to feel invested in something fragile long before the product gives them a reason the risk is worth it.
- The product's only positive reinforcement moment currently arrives around day 30 (Priya's celebration) — there is nothing to feel proud of in the fragile day 4–30 window, only something to lose.
- No competitor owns a free, non-punitive comeback experience by default — Duolingo paywalls its freeze/repair, others offer no recovery at all. This is open competitive white space.
- From testing the actual built prototype (roleplay, not real users): a non-punitive tone ("that's allowed") and a free, one-tap streak-restore mechanic land positively even with a skeptical, already-churned persona (Tom) and a power user protective of her streak's integrity (Priya).
- Dropping track/content identity mid-flow is a concrete, observed trust break — the persona standing in for a day-4-ish user (Amara) reacted to generic, unlabeled lesson content with "did I open the wrong app," not just mild confusion.

## What we assume

- That an early, pre-day-30 moment of restored pride will change real user *behavior* (returning, continuing), not just read well in a mocked-up screen.
- That "free by default" is the right tradeoff economically and behaviorally — that it won't get abused, and won't cheapen the streak's meaning for long-tenured users the way Priya worried it might.
- That the single meditation-track example generalizes to other tracks (language, etc.) without needing separate design work per track — untested beyond the one track built.
- That notification/re-engagement fixes are correctly secondary, per the decision brief — but that assumption depends on lapsed users actually opening the app to see this screen in the first place; if the channel that brings them back is broken, the screen's quality doesn't matter.
- That making the restore mechanic's rules explicit (Priya's and Tom's ask — limits, frequency, cost) will resolve their trust concerns rather than surface new ones, e.g., a user asking "so what stops me from doing this every time?"

## What we still do not know

- Whether real users will actually convert on this screen — open it, complete the 60-second lesson, accept the restore — at a rate that meaningfully moves Day-7 retention back toward 48%. No real user data yet, only a synthetic 3-persona roleplay.
- Whether streak restoration should be available every time a user lapses, or only once (e.g., first-week grace) — this is undecided and untested, and changes the mechanic's meaning depending on the answer.
- Which specific lever is actually doing the retention work: the softened loss-framing, the restored number itself, the comeback lesson content, or the state-aware home screen underneath — all four ship together in this concept, so we can't yet attribute effect to a single piece.
- The real quantitative size of the opportunity: how many of the users behind the 9-point Day-7 drop actually hit a "lost streak" moment versus lapsing for other reasons. Neither research doc cites a funnel breakdown.
- Whether the state-aware home screen (also part of the Marcus-approved recommendation) is required alongside this Comeback screen, or whether the Comeback screen alone captures most of the effect.

## Hypothesis

We believe that a free, personalized Comeback screen — one that restores a lapsed user's streak after a 60-second lesson instead of resetting it to zero — will deliver higher return-and-continue rates among users who miss a day during their first week for Streakly users in their first 7 days, as measured by Day-7 retention rate.
