#!/usr/bin/env python3
"""
Deterministic fixtures for exercising agents/anomaly_diagnosis.py.

No randomness: every rate is produced by index arithmetic, so a fixture's
metrics are exactly the numbers named in the spec and a rerun reproduces them
byte for byte. Four scenarios, one per stop/pass condition in the loop.

Usage:  python3 agents/fixtures/make_fixtures.py
Writes: agents/fixtures/<scenario>/{users,retention,sessions,nudges}.csv
"""

import csv, datetime, pathlib

HERE = pathlib.Path(__file__).resolve().parent
CHANNELS = ["organic", "paid", "referral"]
N = 100  # users per cohort week


def flags(n, count):
    """`count` of n rows true, spread evenly so channel subsets stay balanced."""
    if count <= 0:
        return [False] * n
    step = n / count
    hits = {int(i * step) for i in range(count)}
    return [i in hits for i in range(n)]


def build(week, start, spec, uid0):
    """One cohort week. `spec` gives target counts out of N."""
    users, retention, sessions, nudges = [], [], [], []
    d7 = flags(N, spec["d7"])
    d1 = flags(N, spec["d1"])
    brk = flags(N, spec["brk"])
    goal = flags(N, spec["goal_set"])

    for i in range(N):
        uid = f"u{uid0 + i:04d}"
        signup = start + datetime.timedelta(days=i % 5)
        users.append({
            "user_id": uid,
            "acquisition_channel": CHANNELS[i % 3],
            "signup_date": signup.isoformat(),
            "goal_set_date": (signup + datetime.timedelta(days=1)).isoformat() if goal[i] else "",
            "platform": "ios" if i % 2 else "android",
            "cohort_week": week,
            "variant": "",
            "broke_streak_week1": str(brk[i]).lower(),
            "current_streak": 7 if d7[i] else 0,
        })
        retention.append({
            "user_id": uid, "day_1": str(d1[i]).lower(), "day_7": str(d7[i]).lower(),
            "day_30": "false", "churned": str(not d7[i]).lower(), "cohort_week": week,
            "broke_streak_week1": str(brk[i]).lower(),
            "current_streak": 7 if d7[i] else 0,
        })

    # Sessions: distribute spec["sessions"] total across the cohort's first week.
    total = spec["sessions"]
    for k in range(total):
        i = k % N
        uid = f"u{uid0 + i:04d}"
        day = start + datetime.timedelta(days=(k // N) % 7)
        sessions.append({
            "session_id": f"s{week}{k:05d}", "user_id": uid,
            "session_date": day.isoformat(),
            "session_duration_seconds": 300 + (k % 7) * 20,
            "screen": ["home", "lesson", "streak"][k % 3],
        })

    # Nudges: spec["nudges_sent"] sends, spec["nudges_opened"] of them opened.
    sent = spec["nudges_sent"]
    opened = flags(sent, spec["nudges_opened"])
    for k in range(sent):
        nudges.append({
            "nudge_id": f"n{week}{k:05d}", "user_id": f"u{uid0 + (k % N):04d}",
            "nudge_type": "streak_lost",
            "sent_date": (start + datetime.timedelta(days=k % 7)).isoformat(),
            "opened": str(opened[k]).lower(), "acted_on": "false",
        })
    return users, retention, sessions, nudges


def write(name, weeks):
    out = HERE / name
    out.mkdir(parents=True, exist_ok=True)
    tables = {"users": [], "retention": [], "sessions": [], "nudges": []}
    uid = 1
    for w, (week, start, spec) in enumerate(weeks, 1):
        parts = build(week, start, spec, uid)
        for key, rows in zip(tables, parts):
            tables[key].extend(rows)
        uid += N
    for key, rows in tables.items():
        with open(out / f"{key}.csv", "w", newline="", encoding="utf-8") as fh:
            wr = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            wr.writeheader()
            wr.writerows(rows)
    return out


# Baseline week, shared by every scenario: D-7 39%, D-1 91%, break 22%,
# 4.1 sessions/user, 54% push open, 78% goal-set.
BASE = {"d7": 39, "d1": 91, "brk": 22, "goal_set": 78,
        "sessions": 410, "nudges_sent": 50, "nudges_opened": 27}

SCENARIOS = {
    # The headline test: D-7 39% -> 35%, three drivers moving.
    "anomaly-4pt-drop": {**BASE, "d7": 35, "brk": 29, "sessions": 320,
                         "nudges_sent": 50, "nudges_opened": 25},
    # Threshold not crossed: D-7 moves 1pt. Loop must stop at step 1.
    "subthreshold-1pt": {**BASE, "d7": 38, "brk": 23, "sessions": 405},
    # D-7 moves 4pts but only ONE driver moves. Loop must stop at step 2.
    "single-driver": {**BASE, "d7": 35, "brk": 29, "sessions": 408,
                      "nudges_sent": 50, "nudges_opened": 27},
    # Two drivers clear step 2, but both weakly: streak-break +3pts (under the
    # +5 magnitude bonus, not significant) and sessions -15% (under the -20%
    # bonus). Every hypothesis therefore tops out at exactly 6/10, which the
    # "> 6" gate rejects. Loop must stop at step 3.
    "low-confidence": {**BASE, "d7": 36, "brk": 25, "sessions": 348,
                       "nudges_sent": 50, "nudges_opened": 27},
}

if __name__ == "__main__":
    base_start = datetime.date(2026, 4, 6)
    for name, wk2 in SCENARIOS.items():
        p = write(name, [("1", base_start, BASE),
                         ("2", base_start + datetime.timedelta(days=7), wk2)])
        print(f"wrote {p.relative_to(HERE.parent.parent)}/")
