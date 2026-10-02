# Drop raw user feedback here

Anything, any format: support-ticket exports, NPS free text, survey responses,
app-store reviews, interview notes, pasted Slack threads. `.csv`, `.md`,
`.txt`, `.json` all fine. Filenames don't matter.

[skills/weekly-research-synthesis.md](../../../skills/weekly-research-synthesis.md)
reads everything here that is newer than the last synthesis, then moves what it
read into `ops/research/inbox/processed/` so the next run doesn't double-count it.

If this folder is empty, the workflow says so and stops. It will not invent
feedback.
