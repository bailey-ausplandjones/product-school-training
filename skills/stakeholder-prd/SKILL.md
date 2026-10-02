---
name: stakeholder-prd
description: Write a PRD calibrated to the specific people who will read it, grounded strictly in the workspace's own research and stakeholder files. Use whenever the user asks for a PRD, product requirements doc, product spec, feature spec, or requirements write-up — and also when they ask to write a feature up for engineering and design, prep a doc for a kickoff or triad review, turn research into a spec, or document what a feature needs to do. Use it even when the user never says "PRD," as long as the deliverable is a requirements document someone else will read and act on.
---

# Stakeholder-Calibrated PRD

A PRD fails for one of two reasons: it isn't grounded in evidence, or it isn't written for the people who have to say yes. This skill addresses both. The section structure is the easy part. The calibration is the work.

## Before writing anything, read the workspace

Never write this document from the user's prompt alone. The prompt names the feature; the workspace holds the evidence and the readers.

Read, in this order:

1. **Stakeholder profiles** — usually `08-stakeholders/*.md` or similar. Read these *first*, not last. They determine how everything else gets written.
2. **Research** — interviews, NPS or survey analysis, competitive scans, analytics.
3. **Decision history** — decision briefs, hypotheses, PM briefs, change logs, prior specs. These tell you what has already been decided and by whom.
4. **Technical context**, where it exists — codebase summaries, architecture notes, build logs. These are where real edge cases and risks live. Skip this if the workspace has none rather than hunting for it.

If the user names a file that does not exist, say so plainly, work from what does exist, and note the gap in Open Questions so the reader knows the evidence base has a hole in it.

## Build a reader model before you draft

For each person who will read this, extract four things from their profile:

- **What they push back on.** This tells you what to pre-empt.
- **What they need before saying yes.** This tells you what to include.
- **Questions they have asked before that went unanswered.** A question asked twice is curiosity; asked a third time it is a blocker. Answer it in the document or state explicitly that it is still open.
- **How they prefer to receive information.** Someone who wants bullets and async written updates should not discover a scope change in a live demo.

Then write each section for the reader who most needs it. Different readers need different things from the same feature:

- An **engineering reader** typically needs acceptance criteria, edge cases, eligibility and limit rules, rollback plans, instrumentation, and ripple risk. Give them specifics and decisions, not prose.
- A **design reader** typically needs the problem defined before the solution, real user evidence, a sharp primary-user definition, empty states, and what happens after the flow ends. Lead with user voice.
- A **leadership reader** needs the decision, the tradeoff, and the metric. If leadership is *not* the audience, cut the framing written for them — situation summaries and strategic justification are noise to the people who have to build the thing.

## The calibration moves

These are what separate a calibrated PRD from a filled-in template. Each one trades short-term comfort for credibility.

**Convert product decisions into proposals, not questions.** Workspaces often queue questions "for engineering" that are actually product choices — eligibility rules, usage limits, which metric counts. Bringing those to an engineer as open questions reads as underspecified to the person most likely to push back on exactly that. Instead, state your proposal and ask them to stress-test it: "Proposal: first 7 days only, lapse of 1–2 days. Needs your read on the targeting logic." You still get their input, and you arrive having done your job.

**Surface the stale assumption in writing.** If a stakeholder approved something that has since changed underneath them, name it in the document. The approval is now worthless and they do not know it. Discovering that live is the credibility hit; reading it in advance is just information. State what they agreed to, what the thing became, and why the difference is material.

**Name authorship when you have redesigned someone's idea.** If the concept originated with a reader and was changed without them, say which decisions were changed and who made them. They will find this anyway. Finding it themselves reads as concealment; being told reads as respect.

**Label evidence by strength and by what it supports.** Evidence for a *problem* and evidence for a *solution* are different claims. Three real interviews establish a problem; a roleplay or persona test does not validate a solution. Call synthetic evidence synthetic, especially for a reader whose stated bar is real users. Overclaiming here costs more than the gap it hides.

**Do not present a patched problem as closed.** If a finding got a surface fix over a structural cause — a label added to content that is still wrong, a copy change to a flow that still misleads — it is open. Bring it as an unsolved problem even when the workspace treats it as resolved.

**Do not re-ask what the research answers.** Scan Open Questions against the research before finalizing. A question the interviews already answer signals you did not read them.

## Grounding discipline

- Every factual claim traces to a source. Link the file inline, like `([interview-synthesis](../02-research/interview-synthesis.md))`, so a reader can check you. Write paths relative to where the PRD itself will be saved — sources in the same directory need `./`, not `../` — and check them, because a broken citation undermines the claim it was meant to support.
- Quote users verbatim where a quote lands harder than a paraphrase. "There was no way to recover it, nothing. So I gave up" does work that "users reported frustration" does not.
- Numbers get their baseline and their source. A metric with no baseline is not a metric.
- Unknown values are `TBD`, never estimates dressed as findings. If a whole metric is unmeasurable today, say what is missing and what it blocks.
- Targets are the exception, because setting them is the author's job rather than a fact to be looked up. When no source states a target, propose one and mark it as a proposal — the same move as proposing a product decision. A table of nothing but `TBD` reads as an unfinished template; a proposed target reads as a position someone can argue with, which is what you want.
- Never invent a detail that is not in the source material. If something important is unknown, that absence is itself a finding worth stating.

## Output format

Write to the path the user specifies. Use exactly these six sections, in this order:

```markdown
# PRD — [Feature name]

**For:** [readers with roles] · **From:** [author] · **Status:** [stage]
**Sources:** [linked source files]

## Problem Statement
## User
## Goals and Non-Goals
## Success Metrics
## User Stories
## Open Questions
```

Section by section:

- **Problem Statement** — The mechanism causing the problem, stated in one or two lines, then the evidence as a scannable list. Include the metric and its baseline, the frequency of each theme in the research, user verbatims, and competitive position if the research covers it. No solution language.
- **User** — Who they are, their job to be done in their words, and their context of use. Context is where real constraints surface — when the flow triggers, what state they arrive in, what the system does and doesn't know yet. Be specific enough that a designer could define the primary user from this alone.
- **Goals and Non-Goals** — Numbered lists. Every non-goal names *why* it is out of scope, and distinguishes the reasons, because they are not equivalent: something deliberately rejected is settled, something deferred has a date, and something nobody scoped is still available to argue for. Collapsing all three into a flat "out of scope" hides the one a reader might reasonably reopen — and if the thing nobody scoped was a reader's own request, saying so is what keeps them in the conversation.
- **Success Metrics** — A table of metric, baseline, target. Then state measurement constraints honestly: whether effects can be attributed if several changes ship together, and whether the opportunity has been sized. A PRD that cannot answer "how will we know this worked" should say so here rather than let the reader discover it.
- **User Stories** — Three to five, each in "As a… I want… so that…" form with a short attribution to the research that produced it. Cover the main path, the decline or skip path, and at least one case where the user is not ready to engage. Stories with no research behind them are guesses; cut them.
- **Open Questions** — Group by reader, with a short heading naming who owns each group. Within the engineering group, lead with proposals rather than questions. Close with an evidence-status group that states plainly what is validated, what is assumed, and what is missing. This section is where credibility is won or lost — a thin Open Questions section means you did not look hard.

Aim for density rather than a page count. The first five sections should be tight — a reader skimming them gets the feature in under a minute. Open Questions earns whatever length it needs, because it is the section that does the calibration work; a thin one means you did not look hard. If the document is running long, compress the first five sections rather than trimming Open Questions.

Plain declarative sentences. No hedging, no adjectives doing the work of evidence. This register is also how you deliver the uncomfortable findings: state that an approval is stale or that a concept was changed without its author flatly, with the source attached, and let the fact carry the weight. Softening it defeats the purpose; dramatizing it invites an argument about tone instead of substance.

## Two before/after examples

These illustrate the two moves people get wrong most often. Adapt the pattern; do not copy the specifics.

**Reframing a decision as a proposal**

Weak — hands a product decision to an engineer:
> *Eligibility: should this apply to users who missed 1 day or 2? First week only, or any lapse?*

Calibrated — decided, with the engineering input isolated:
> *Eligibility. Proposal: first 7 days only, lapse of 1–2 days. Needs your read on the targeting logic.*

**Labeling evidence strength**

Weak — lets a roleplay pass as validation:
> *User testing showed the non-punitive tone landed well with returning users.*

Calibrated — separates problem evidence from solution evidence:
> *Evidence for the problem is real: 3 interviews, 10 NPS comments. Evidence for the solution is a 3-persona roleplay, explicitly labelled "roleplay, not real users." It is synthetic.*

## After writing

Tell the user, briefly, how you calibrated for each reader and what you flagged rather than invented. They need to know which uncomfortable things are now in the document before they send it. If a source file was missing or a link is broken, say so.
