# Weekly Status — Stakeholder-Calibrated Template

**Purpose:** Turn one set of raw weekly notes into two differently-calibrated updates — a team update and a leadership update — rather than one generic report sent to everyone.

**Why two:** the same facts need different framing per reader. Raj needs scope changes in writing before a meeting. Lena needs to see artifacts and hear user voice. Marcus needs the ask in the first sentence and the data tied to a business outcome. A single update serves none of them well.

**Related:** [skills/weekly-status/SKILL.md](weekly-status/SKILL.md) is the generic four-section version. This file is the stakeholder-calibrated variant. Profiles live in [08-stakeholders/](../08-stakeholders/).

---

## Calibration table

Derived from the stakeholder profiles. Update this when a profile changes.

| Reader | Format | Detail level | Lead with | Never do |
|---|---|---|---|---|
| **Raj** (Eng lead) | Async post, bullets, no paragraphs | High on scope, edge cases, acceptance criteria | Anything that changed under his last estimate | Surprise him live in a meeting; hand him product decisions as open questions |
| **Lena** (Design) | Links to clickable artifacts; "here's what users told us" | High on user evidence, empty states, what-happens-next | The prototype link and the user quote | Present roleplay as user validation; present an open design problem as closed |
| **Marcus** (Head of Product) | One page, scannable | Low on mechanics, high on business outcome | The ask, in sentence one, with a deadline | Bury the recommendation; show data not connected to the core metric; exceed one page |

---

## Standing rules (apply to every update)

1. **Label evidence honestly.** Roleplay/persona testing is synthetic. Say so every time. Never let "tested across three personas" read as user validation.
2. **Name your own descopes and scope changes before the reader finds them.** Cheaper to confess than to be caught in a review.
3. **Separate what you owe them from what you need from them.** Two explicit lists. Product decisions are yours; feasibility and ripple risk are engineering's.
4. **Don't cite a document that does not exist.** Check the workspace before linking.
5. **Mark gaps TBD** rather than estimating past the evidence.
6. **State what needs no action from the reader.** Especially for leadership — it is what keeps a one-pager at one page.

---

## Template 1 — Team update (Raj + Lena)

One post, shared core, then a short addressed block per person. Raj's pulls toward terse bullets; Lena's pulls toward artifacts and user voice. Don't average them — segment.

```
**[Project] — week of [date]**
Posting async ahead of [meeting] so nothing lands cold in the room.

**Done**
- [shipped item — one line, no adjectives]

**In progress**
- [item] — [% or count, e.g. "3 of 5 confirmed"]

**⚠️ [Raj] — [scope correction / blocker], flagging in writing**
- [What changed under his last estimate. Name the delta technically:
  what he scoped vs. what exists, and why they differ in cost.]
- [What I owe you, and it's mine to decide not yours:]
  [decision 1 — proposal] / [decision 2 — proposal] / [decision 3 — proposal]
- [What I need from you:] [ripple risk] / [rollback plan]
- [Explicit relief: what he does NOT need to do yet, and by when you'll unblock him.]

**🎨 [Lena] — [framing that acknowledges her authorship/stake]**
- [Prototype or artifact link + how long it takes to look at]
- [Any decision made on her work without her — name it yourself, first]
- **What users told us:** [direct quote from research, not a paraphrase]
- **One honest caveat:** [what the evidence is NOT]
- **Open, not closed:** [the design problem you patched but did not solve]
- **Still no answer:** [the thing she has asked before that you still can't answer]
```

**Filled example — Streakly Comeback, week of Sep 28:** see [07-docs/objection-log.md](../07-docs/objection-log.md) for the underlying objections this update is written to pre-empt.

Key moves in the filled version:
- Reframed "streak-freeze needs a data model change" as the real delta: a one-tap freeze is a flag set before the day boundary; a retroactive restore recovers a value the system already overwrote. New persisted state, not new logic.
- Stated eligibility, restore limit, and instrumentation as PM proposals, not questions for Raj.
- Reframed "tested across three personas" as synthetic roleplay for Lena, whose stated bar is real users.
- Presented the "did I open the wrong app" finding as unsolved — the "· Meditation" header label is a patch on meditation-specific content.

---

## Template 2 — Leadership update (Marcus)

Hard ceiling: one page. If it does not fit, cut mechanics, never the ask or the metric.

```
**[Project] — status + [N] async decision(s)**
**To:** [name] · **From:** [you] · **Week of [date]**

**The ask:** [Recommendation in sentence one.] I need [yes/no or a question]
by **[deadline]**, because [constraint — their travel, a meeting that closes scope].

**Why this is an ask and not an FYI:** [the delta between what they approved
and what exists, named by you, with the reason you made the call.]

**Against [core metric] ([current], target [target]):**
- [Evidence tied to the metric, with a real quote or number]
- [Behavioral/churn data point]
- [Competitive or market position]

**The number I still owe you:** [the sizing gap, stated plainly, with what it
would change and when you'll have it.]

**Progress:** [one line, comma-separated. No bullets — this is not the point
of the update.]

**Risks:**
- [Risk, plus whether it needs them. Usually it does not.]

**No action needed from you on:** [list]. Mine to close. I'll send
[a specific follow-up] by [day].
```

Key moves in the filled version:
- Ask is the first sentence, with a Monday deadline because he is out Thu–Fri.
- Named the descope — he approved three pieces, one is built — rather than letting him find it in the PRD.
- Tied all three evidence bullets to Day-7 retention specifically, his repeated question.
- Conceded the missing funnel number and sized the consequence (~1.4-point ceiling vs ~5-point), which is the real answer to his cost-of-waiting question.
- Closed with an explicit no-action list so the page stays a page.

---

## Steps

1. Collect raw notes in any order: shipped, in progress, blockers.
2. Read the relevant profiles in [08-stakeholders/](../08-stakeholders/) — calibration comes from there, not from this file.
3. **Audit the notes before writing.** For each item: does the artifact exist in the workspace? Is the evidence real or synthetic? Is this blocker stated at its true size, or softened?
4. Sort into Done / In progress / Blockers.
5. Write the team update. Segment by person; do not average conflicting preferences.
6. Write the leadership update. Ask first, one page, explicit no-action list.
7. Re-check against the standing rules, especially rules 1, 2, and 4.
