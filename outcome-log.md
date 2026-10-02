# Outcome Log — Streakly anomaly diagnoses

One block per diagnosis that cleared the confidence gate. The **What actually happened** field is written by a human after the SQL is run — it is the only thing that turns these confidence scores from guesses into a calibrated instrument. An entry with it still blank is an open call, not a result.

Appended by `agents/anomaly_diagnosis.py`. Spec: `agents/anomaly-diagnosis.md`.

## 2026-05-13 08:47 — [FIXTURE] Day-7 retention -4pts

- **Data source:** `agents/fixtures/anomaly-4pt-drop`  ⚠️ **synthetic fixture — not a production call, do not calibrate on this**
- **Trigger:** Day-7 retention dropped 4pts (39% → 35%) week over week — cohort week 2 vs 1, n=100/100, p=0.558
- **Drivers that moved:** Streak-break rate (+7.0pts), Sessions per user, week 1 (-0.9 sessions, -22%), Push open rate (-4.0pts)

### Ranked hypotheses

1. **Streak-break punishment — more users hit the all-or-nothing reset, and the reset is converting to churn** — confidence **7/10**
   - Basis: streak-break rate 22%→29% (p=0.256), moving with Day-7 in the expected direction
2. **Engagement depth collapse — users who stayed are opening the app less, so the habit never forms** — confidence **7/10**
   - Basis: sessions/user 4.1→3.2 (22% drop) on n=100
3. **Notification channel decay — sends are reaching fewer users, removing the route back to a lapsing user** — confidence **5/10** _(not confirmable from current data)_
   - Basis: push open rate 54%→50%, and sessions/user down 22% alongside it

### SQL issued (hypothesis 1: streak_punishment)

```sql
-- Confirm: are more users breaking, and is the break converting to churn?
SELECT r.cohort_week,
       COUNT(*)                                                   AS cohort_n,
       AVG(CASE WHEN r.broke_streak_week1 THEN 1.0 ELSE 0 END)     AS break_rate,
       AVG(CASE WHEN r.day_7 THEN 1.0 ELSE 0 END)                  AS d7_overall,
       AVG(CASE WHEN r.broke_streak_week1 AND r.day_7 THEN 1.0
                WHEN r.broke_streak_week1 THEN 0 END)              AS d7_breakers,
       AVG(CASE WHEN NOT r.broke_streak_week1 AND r.day_7 THEN 1.0
                WHEN NOT r.broke_streak_week1 THEN 0 END)          AS d7_non_breakers
FROM streakly_retention r
GROUP BY r.cohort_week
ORDER BY r.cohort_week;
```

### What actually happened

_TBD — fill this in after running the query._

### Was the top hypothesis right?

_TBD — yes / no / partly. This is the calibration signal; without it the confidence scores above stay uncalibrated._

---

