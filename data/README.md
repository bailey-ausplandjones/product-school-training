# Streakly sample data (Day 3)

Local CSVs for Module 5. Do not use the old Google Sheet: tab names and columns
did not match the prompts, and there was no streak field.

| File | What it is |
|---|---|
| `users.csv` | One row per user. `cohort_week` 1-5. Week 5 `variant` is `comeback` or `control`. `broke_streak_week1` and `current_streak` are the streak fields. |
| `retention.csv` | `day_1`, `day_7`, `day_30`, `churned`, plus the same streak fields. |
| `sessions.csv` | Sessions, including a `comeback` screen when the Comeback experience was shown. |
| `nudges.csv` | `nudge_type` is `comeback_screen` (treatment) or `streak_lost` (control). |
| `comeback_sends.csv` | Four sends per week-5 user. `send_number` 1-4. Open rates climb 28% to 56% for treatment vs ~4% control. |

Point Claude Code at this `data/` folder. No Google Sheets MCP and no terminal required.
