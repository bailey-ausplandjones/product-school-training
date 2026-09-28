---
name: weekly-status
description: Turn raw bullet-point notes into a formatted leadership status update with Shipped, In Progress, Blockers, and Next Week sections. Use when asked to write a weekly status update, leadership update, or turn rough notes into a status report.
---

# Weekly Status Update

Converts raw, unsorted bullet-point notes into a leadership-ready weekly status update.

## Input

Raw bullet points about the week's work, in any order — shipped items, in-progress work, blockers, plans for next week.

## Output format

Exactly four sections, in this order, using these headers:

- **Shipped**
- **In Progress**
- **Blockers**
- **Next Week**

Rules:
- Max 3 bullets per section. If more than 3 items belong in a section, keep the 3 most significant and drop or merge the rest.
- Plain, declarative language — no jargon, no buzzwords, no hedging.
- One line per bullet.
- If a section has no input, write "None" rather than inventing content.

## Steps

1. Read the raw notes.
2. Sort each item into Shipped, In Progress, Blockers, or Next Week based on its content, not the order it was given.
3. Rewrite each item as a short, plain declarative sentence.
4. Trim each section to at most 3 bullets, keeping the most significant.
5. Output the four sections in order.

## Example

**Input:**
- finished onboarding redesign, shipped to 100%
- still working on payment retry logic, about halfway done
- blocked on legal review for the new terms of service
- also blocked waiting on design specs for the settings page
- next week: start on the notification revamp
- also want to fix the flaky checkout test

**Output:**

**Shipped**
- Onboarding redesign is live for all users.

**In Progress**
- Payment retry logic is about halfway done.

**Blockers**
- Legal review is pending for the new terms of service.
- Waiting on design specs for the settings page.

**Next Week**
- Start work on the notification revamp.
- Fix the flaky checkout test.
