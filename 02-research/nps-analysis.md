# NPS Feedback Analysis — Streakly

**For:** Marcus
**Source:** 10 raw NPS free-text comments
**Context:** Day-7 retention slipped 48% → 39% post-v2 redesign; target ≥48%. This feedback set is being read against that problem, not as a general product review.

---

## 1–2. Themes Mentioned More Than Once (Ranked by Frequency)

| Rank | Theme | Mentions | Quotes |
|---|---|---|---|
| 1 | **Streak loss is all-or-nothing and drives churn** — losing a streak resets everything with no recovery path, and users frame it as punishment rather than a setback | 6 | "I hit a 20-day streak, missed one day, and it reset to zero. I haven't opened the app since." / "a scorekeeper that punishes me for missing a day" / "there was no way to recover it... Other apps let you freeze a streak" / "make coming back easier instead of making me feel like I failed" / "Deleted after 3 weeks. The moment I lost my streak the whole thing lost its meaning." / "The streak is the only thing keeping me engaged, but the second I lost it, I was done." |
| 2 | **Notifications feel poorly targeted and excessive** — frequency and relevance are off, to the point users disable them entirely | 3 | "the daily reminder just started to feel like nagging" / "I got three in one afternoon and just turned them all off" / "If it pulled me back with something useful I'd come back" (implies current pings don't do this) |
| 3 | **Re-engagement after a lapse is weak** — nothing in the product notices or helps a user who's drifted away | 2 | "I just forget it exists after a couple of days" / "I wish it would make coming back easier" |

*(Note: one single-mention comment — "The home screen looks the same whether I'm on a 2-day streak or coming back after two weeks away" — didn't meet the >1 threshold on its own, but it's the same underlying gap as Themes 1 and 3: the product doesn't visually or behaviorally distinguish a user's actual state. Flagging it here because it names the mechanism behind both.)*

---

## 3. Praise vs. Complaints

**Praise (2):**
- "The first week was genuinely fun." (before the reminder cadence soured it)
- "Love the lessons." (content quality holds up independent of the streak mechanic)

**Complaints (8):**
- Streak reset to zero on a single missed day → abandonment (x1 explicit churn story)
- Desire for "coach, not scorekeeper" framing
- No streak recovery/freeze option, unlike competitors
- Notification frequency/relevance (batching, "nagging")
- Forgets app exists between sessions; no compelling win-back pull
- Home screen doesn't reflect streak state or return-from-absence
- "Make coming back easier instead of making me feel like I failed"
- Deleted app after losing streak — streak loss removed all meaning
- Streak as sole engagement driver, with no fallback when it breaks

**Read on the split:** the product itself (lessons, early content) isn't in question. Every complaint is about the *mechanics wrapped around* the content — the streak's rigidity, and the notification/re-engagement layer that's supposed to bring people back but currently pushes them away instead.

---

## 4. Top 3 Actionable Issues

1. **No streak recovery mechanism.** This is the highest-frequency theme (6/10 comments) and the one most directly tied to stated churn ("haven't opened since," "deleted after 3 weeks"). Users are explicitly naming the fix they want (a freeze, grace period, or partial-credit reset) and naming a competitor that already does it. This is the single highest-leverage fix in this dataset.

2. **Notification strategy is untuned.** Batched, irrelevant pings are getting entire users' notification permissions turned off — which then removes any way to reach them for re-engagement (Theme 2 and Theme 3 compound each other: bad notifications now mean no path back later). Fixing cadence/relevance protects the channel needed for issue #3.

3. **No state-aware re-engagement or "welcome back" experience.** Lapsed users get the same home screen and the same reset-to-zero treatment as someone who never built a streak at all. There's no acknowledgment of where a user actually is (2 days in vs. returning after two weeks), which is what makes "starting over" feel like failure instead of a restart.

---

## 5. Summary for Marcus

Six of ten comments trace back to one root cause: **the streak mechanic has no state between "intact" and "zero."** That binary is what's converting missed days into deletions. The notification and re-engagement complaints are secondary but compounding — they're the mechanisms that are supposed to catch a lapsing user and currently don't (or actively push them to disengage further by over-notifying, then losing the channel entirely when it's disabled).

Recommendation for prioritization: streak recovery/forgiveness is the clearest, most-requested, most-cited-in-churn fix here and should be the first thing scoped. Notification tuning and a lapsed-user re-engagement state are smaller, complementary fixes that reinforce it rather than substitutes for it.
