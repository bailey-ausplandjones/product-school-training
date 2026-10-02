#!/usr/bin/env python3
"""
anomaly-diagnosis — chained diagnostic loop for Streakly.

Fires only when metric-pulse raises an alert (Day-7 or streak-break moving more
than 2 pts week over week), then runs five gated steps:

  1 Threshold check        -> stop if the move is <= 2 pts
  2 Metric tree            -> stop (inconclusive) if fewer than 2 drivers moved
  3 Hypotheses             -> stop (low-confidence Slack alert) if top <= 6/10
  4 SQL + Slack post       -> full diagnostic, before the 9am standup
  5 Outcome log            -> append ranked hypotheses + a "what happened" stub

Every stop is logged. A stop is a result, not a failure.

Reuses agents/metric_pulse.py for the headline metrics so the two agents cannot
disagree about a number.

Stdlib only. No network calls unless --post is passed.

Usage:
    python3 agents/anomaly_diagnosis.py --dry-run
    python3 agents/anomaly_diagnosis.py --data-dir agents/fixtures/anomaly-4pt-drop --dry-run
    python3 agents/anomaly_diagnosis.py --post

Spec: agents/anomaly-diagnosis.md
"""

import argparse, csv, datetime, pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from metric_pulse import (
    ALERT_PTS, analyse, compute_week, confounds, fmt_p, load, pct, post_to_slack,
    two_prop_p,
)

REPO = pathlib.Path(__file__).resolve().parent.parent
OUTCOME_LOG = REPO / "outcome-log.md"
RUN_LOG = REPO / "ops" / "agent" / "anomaly" / "run-log.md"

CONFIDENCE_GATE = 6      # step 3 proceeds only on a top score ABOVE this
MIN_DRIVERS = 2          # step 2 proceeds only on at least this many movers
TRUE = "true"

# Assumed warehouse table names. The columns are real (they mirror data/*.csv);
# the table names are a guess and need re-pointing by whoever owns the
# warehouse. Flagged in every SQL block the agent emits.
TABLES = {
    "users": "streakly_users",
    "retention": "streakly_retention",
    "sessions": "streakly_sessions",
    "nudges": "streakly_notifications",
}

# ---------------------------------------------------------------- step 2: drivers

# key, label, unit, better, meaningful-move threshold
DRIVERS = [
    ("brk",        "Streak-break rate",         "pts",   "down", 3.0),
    ("d1",         "Day-1 retention",           "pts",   "up",   3.0),
    ("sessions_pu", "Sessions per user, week 1", "ratio", "up",   10.0),  # % relative
    ("push_open",  "Push open rate",            "pts",   "up",   3.0),
    ("goal_set",   "Goal-set rate within 24h",  "pts",   "up",   3.0),
]


def load_extra(data_dir):
    """sessions.csv and nudges.csv -- the two driver sources metric_pulse
    doesn't need. Missing files degrade the driver list rather than failing the
    run: a decomposition on 3 of 5 drivers is still a decomposition, and the
    report says which ones were unavailable."""
    out, missing = {}, []
    for name in ("sessions", "nudges"):
        path = data_dir / f"{name}.csv"
        if not path.exists():
            missing.append(f"{name}.csv")
            out[name] = []
            continue
        with open(path, newline="", encoding="utf-8") as fh:
            out[name] = list(csv.DictReader(fh))
    return out, missing


def driver_cells(retention, by_id, extra, week):
    """Raw numerator/denominator per driver for one cohort week."""
    rows = [r for r in retention if r["cohort_week"] == week]
    ids = {r["user_id"] for r in rows}
    n = len(rows)
    sess = [s for s in extra["sessions"] if s["user_id"] in ids]
    nud = [x for x in extra["nudges"] if x["user_id"] in ids]
    goal_n = [u for u in (by_id[i] for i in ids) if u.get("goal_set_date")]

    return {
        "n": n,
        "brk": {"c": sum(r["broke_streak_week1"] == TRUE for r in rows), "n": n},
        "d1": {"c": sum(r["day_1"] == TRUE for r in rows), "n": n},
        "push_open": {"c": sum(x["opened"] == TRUE for x in nud), "n": len(nud)},
        "goal_set": {"c": len(goal_n), "n": n},
        "sessions_pu": {"total": len(sess), "n": n},
    }


def driver_moves(cur, prev, unavailable):
    """One row per driver: delta, relative delta, significance, 'moved' flag."""
    out = []
    for key, label, unit, better, floor in DRIVERS:
        if key == "sessions_pu":
            a = cur[key]["total"] / cur["n"] if cur["n"] else None
            b = prev[key]["total"] / prev["n"] if prev["n"] else None
            if not a or not b:
                continue
            rel = 100.0 * (a - b) / b
            moved = abs(rel) >= floor
            out.append({
                "key": key, "label": label, "unit": unit, "cur": a, "prev": b,
                "delta": a - b, "rel": rel, "p": None, "significant": False,
                "moved": moved, "good": (a - b) > 0 if better == "up" else (a - b) < 0,
                "n_cur": cur["n"], "n_prev": prev["n"],
            })
            continue

        a, b = pct(cur[key]["c"], cur[key]["n"]), pct(prev[key]["c"], prev[key]["n"])
        if a is None or b is None:
            continue
        delta = a - b
        p = two_prop_p(cur[key]["c"], cur[key]["n"], prev[key]["c"], prev[key]["n"])
        out.append({
            "key": key, "label": label, "unit": unit, "cur": a, "prev": b,
            "delta": delta, "rel": (100.0 * delta / b) if b else None, "p": p,
            "significant": p is not None and p < 0.05,
            "moved": abs(delta) >= floor,
            "good": delta > 0 if better == "up" else delta < 0,
            "n_cur": cur[key]["n"], "n_prev": prev[key]["n"],
        })
    return out


def fmt_driver(d):
    if d["unit"] == "ratio":
        return (f"{d['label']}: {d['prev']:.1f} → {d['cur']:.1f} "
                f"({'↑' if d['delta'] > 0 else '↓'} {abs(d['rel']):.0f}%)")
    sym = "↑" if d["delta"] > 0 else ("↓" if d["delta"] < 0 else "→")
    tail = f"{abs(d['delta']):.0f}pts" if d["delta"] else "flat"
    sig = "" if d["p"] is None else f", {fmt_p(d['p'])}"
    return f"{d['label']}: {d['prev']:.0f}% → {d['cur']:.0f}% ({sym} {tail}{sig})"


# ---------------------------------------------------------------- step 3: hypotheses

# Each hypothesis: a trigger over the driver set, a transparent confidence
# formula, the SQL that would confirm it, and whether the data can confirm it
# at all. `confirmable=False` means the warehouse lacks a required column --
# the agent says so instead of emitting a query that cannot run.


def by_key(ds):
    return {d["key"]: d for d in ds}


def hypotheses(drivers, segments, d7):
    ds = by_key(drivers)
    movers = [d for d in drivers if d["moved"]]
    adverse = [d for d in movers if not d["good"]]
    out = []

    def add(key, title, conf, basis, sql, confirmable=True, caveat=None):
        out.append({"key": key, "title": title,
                    "confidence": max(1, min(10, conf)), "basis": basis,
                    "sql": sql, "confirmable": confirmable, "caveat": caveat})

    po, se, br, d1, go = (ds.get(k) for k in ("push_open", "sessions_pu", "brk", "d1", "goal_set"))

    if po and po["moved"] and not po["good"]:
        conf = 3 + (2 if se and se["moved"] and not se["good"] else 0) \
                 + (1 if po["significant"] else 0) + (1 if abs(po["delta"]) >= 5 else 0)
        add("notification_decay",
            "Notification channel decay — sends are reaching fewer users, removing the route back to a lapsing user",
            conf,
            f"push open rate {po['prev']:.0f}%→{po['cur']:.0f}%"
            + (f", and sessions/user down {abs(se['rel']):.0f}% alongside it" if se and se["moved"] and not se["good"] else ""),
            sql_push(), confirmable=False,
            caveat=f"{TABLES['nudges']} has `opened` but no `delivered` or opt-in column — "
                   "open rate cannot separate a delivery failure from users ignoring the push. "
                   "Confirming a *delivery* problem needs a column the export doesn't have.")

    if br and br["moved"] and not br["good"]:
        conf = 4 + (2 if d7["delta"] < 0 else 0) + (2 if br["significant"] else 0) \
                 + (1 if abs(br["delta"]) >= 5 else 0)
        add("streak_punishment",
            "Streak-break punishment — more users hit the all-or-nothing reset, and the reset is converting to churn",
            conf,
            f"streak-break rate {br['prev']:.0f}%→{br['cur']:.0f}% ({fmt_p(br['p'])})"
            + (", moving with Day-7 in the expected direction" if d7["delta"] < 0 else ""),
            sql_streak())

    if se and se["moved"] and not se["good"]:
        conf = 3 + (2 if d7["delta"] < 0 else 0) + (1 if br and br["moved"] and not br["good"] else 0) \
                 + (1 if abs(se["rel"]) >= 20 else 0)
        add("engagement_depth",
            "Engagement depth collapse — users who stayed are opening the app less, so the habit never forms",
            conf,
            f"sessions/user {se['prev']:.1f}→{se['cur']:.1f} ({abs(se['rel']):.0f}% drop) on n={se['n_cur']}",
            sql_sessions())

    if go and go["moved"] and not go["good"]:
        conf = 3 + (2 if d1 and not d1["moved"] and d7["delta"] < 0 else 0) + (1 if go["significant"] else 0)
        add("activation_gate",
            "Activation gate — fewer users set a goal in the first 24h, so they never enter the streak loop",
            conf,
            f"goal-set rate {go['prev']:.0f}%→{go['cur']:.0f}%"
            + (", with Day-1 flat — they arrive and don't start" if d1 and not d1["moved"] else ""),
            sql_activation())

    seg_sig = [s for s in segments if s["significant"] and not s["good"]]
    if (d1 and d1["moved"] and not d1["good"]) or seg_sig:
        conf = 3 + (2 if d1 and d1["moved"] else 0) + (2 if seg_sig else 0) \
                 + (1 if d1 and d1["significant"] else 0)
        worst = min(seg_sig, key=lambda s: s["delta"]) if seg_sig else None
        add("cohort_quality",
            "Cohort quality shift — this week's intake is different, not this week's product",
            conf,
            (f"Day-1 {d1['prev']:.0f}%→{d1['cur']:.0f}%" if d1 and d1["moved"] else "Day-1 flat")
            + (f"; the drop concentrates in {worst['channel']} ({worst['delta']:+.0f}pts, {fmt_p(worst['p'])})" if worst else ""),
            sql_channel())

    if len(movers) >= MIN_DRIVERS:
        add("deploy_regression",
            "Release regression — something shipped and broke a step in the loop",
            2 + (1 if len(movers) >= 3 else 0),
            f"{len(movers)} drivers moved together, which is the shape of a release, "
            "but nothing here can point at one",
            sql_deploy(), confirmable=False,
            caveat="no deploy, release-tag or app-version column exists in the export — "
                   "this hypothesis is unfalsifiable from the available data and is listed "
                   "only so it isn't silently dropped. Confirm it in the deploy log, not here.")

    # Deterministic order: confidence desc, then a fixed priority so ties never
    # reorder between runs.
    priority = ["streak_punishment", "engagement_depth", "notification_decay",
                "cohort_quality", "activation_gate", "deploy_regression"]
    out.sort(key=lambda h: (-h["confidence"], priority.index(h["key"])))
    return out, adverse


# ---------------------------------------------------------------- SQL templates


def sql_streak():
    return f"""-- Confirm: are more users breaking, and is the break converting to churn?
SELECT r.cohort_week,
       COUNT(*)                                                   AS cohort_n,
       AVG(CASE WHEN r.broke_streak_week1 THEN 1.0 ELSE 0 END)     AS break_rate,
       AVG(CASE WHEN r.day_7 THEN 1.0 ELSE 0 END)                  AS d7_overall,
       AVG(CASE WHEN r.broke_streak_week1 AND r.day_7 THEN 1.0
                WHEN r.broke_streak_week1 THEN 0 END)              AS d7_breakers,
       AVG(CASE WHEN NOT r.broke_streak_week1 AND r.day_7 THEN 1.0
                WHEN NOT r.broke_streak_week1 THEN 0 END)          AS d7_non_breakers
FROM {TABLES['retention']} r
GROUP BY r.cohort_week
ORDER BY r.cohort_week;"""


def sql_sessions():
    return f"""-- Confirm: is session volume down per user, and on which screen?
SELECT u.cohort_week,
       s.screen,
       COUNT(DISTINCT s.user_id)                      AS users_on_screen,
       COUNT(*)                                       AS sessions,
       COUNT(*)::float / COUNT(DISTINCT u.user_id)    AS sessions_per_user
FROM {TABLES['users']} u
LEFT JOIN {TABLES['sessions']} s
       ON s.user_id = u.user_id
      AND s.session_date < u.signup_date + INTERVAL '7 days'
GROUP BY u.cohort_week, s.screen
ORDER BY u.cohort_week, sessions DESC;"""


def sql_push():
    return f"""-- Confirm: is the notification channel decaying?
-- NOTE: {TABLES['nudges']} has `opened` but no `delivered` / opt-in column, so
-- this measures ENGAGEMENT, not DELIVERY. It cannot distinguish "the push never
-- arrived" from "the push arrived and was ignored". Treat as a proxy.
SELECT n.sent_date,
       n.nudge_type,
       COUNT(*)                                             AS sent,
       SUM(CASE WHEN n.opened  THEN 1 ELSE 0 END)           AS opened,
       AVG(CASE WHEN n.opened  THEN 1.0 ELSE 0 END)         AS open_rate,
       AVG(CASE WHEN n.acted_on THEN 1.0 ELSE 0 END)        AS act_rate
FROM {TABLES['nudges']} n
WHERE n.sent_date >= CURRENT_DATE - INTERVAL '14 days'
GROUP BY n.sent_date, n.nudge_type
ORDER BY n.sent_date, n.nudge_type;"""


def sql_activation():
    return f"""-- Confirm: are fewer users setting a goal in the first 24h?
SELECT u.cohort_week,
       COUNT(*)                                                        AS cohort_n,
       AVG(CASE WHEN u.goal_set_date IS NOT NULL THEN 1.0 ELSE 0 END)   AS goal_set_rate,
       AVG(CASE WHEN u.goal_set_date <= u.signup_date + INTERVAL '1 day'
                THEN 1.0 ELSE 0 END)                                    AS goal_set_24h,
       AVG(CASE WHEN r.day_7 THEN 1.0 ELSE 0 END)                       AS d7
FROM {TABLES['users']} u
JOIN {TABLES['retention']} r ON r.user_id = u.user_id
GROUP BY u.cohort_week
ORDER BY u.cohort_week;"""


def sql_channel():
    return f"""-- Confirm: is the drop concentrated in one acquisition channel,
-- and is it a RATE change or a MIX change?
SELECT u.cohort_week,
       u.acquisition_channel,
       COUNT(*)                                                      AS n,
       COUNT(*)::float / SUM(COUNT(*)) OVER (PARTITION BY u.cohort_week) AS channel_share,
       AVG(CASE WHEN r.day_1 THEN 1.0 ELSE 0 END)                    AS d1,
       AVG(CASE WHEN r.day_7 THEN 1.0 ELSE 0 END)                    AS d7
FROM {TABLES['users']} u
JOIN {TABLES['retention']} r ON r.user_id = u.user_id
GROUP BY u.cohort_week, u.acquisition_channel
ORDER BY u.cohort_week, u.acquisition_channel;"""


def sql_deploy():
    return """-- Cannot be written against the available schema.
-- There is no deploy, release-tag or app-version column anywhere in the export.
-- Confirm this one in the deploy log / release tooling, then come back."""


# ---------------------------------------------------------------- segments


def segment_moves(a):
    out = []
    for ch, mm in sorted(a["channels"].items()):
        m = mm["d7"]
        if not m:
            continue
        out.append({"channel": ch, **m})
    return out


# ---------------------------------------------------------------- render


def header(now, label="🔍 *Streakly Anomaly Detected*"):
    return f"{label}, {now:%a %b %-d, %-I:%M%p}".replace("AM", "am").replace("PM", "pm")


def render_full(ctx):
    n, h = ctx["now"], ctx["hyps"]
    top = h[0]
    L = [header(n), "",
         f"*Trigger:* {ctx['trigger']}", "",
         "*Metric tree decomposition:*"]
    for d in ctx["drivers"]:
        L.append(f"• {fmt_driver(d)}" + ("" if d["moved"] else "  _(below its move threshold)_"))
    if ctx["segments"]:
        L += ["", "*Where it concentrates (Day-7 by channel):*"]
        for s in ctx["segments"]:
            tag = "" if s["significant"] else " _(not significant)_"
            L.append(f"• {s['channel'].title()}: {s['prev']:.0f}% → {s['cur']:.0f}% ({s['delta']:+.0f}pts){tag}")

    L += ["", f"*Top {len(h)} hypotheses* _(confidence is a rule-based score, not a probability — see §4 of the spec)_:"]
    for i, x in enumerate(h, 1):
        mark = "" if x["confirmable"] else " ⚠️ not confirmable from current data"
        L.append(f"{i}. *{x['title']}* — *{x['confidence']}/10*{mark}")
        L.append(f"    _{x['basis']}_")
        if x["caveat"]:
            L.append(f"    _⚠️ {x['caveat']}_")

    L += ["", f"*SQL to confirm hypothesis 1 ({top['key']}):*", "```", top["sql"], "```"]
    if not top["confirmable"]:
        L.append("⚠️ *The top hypothesis is not confirmable from the current export.* "
                 "The query above is the closest available proxy — read its header comment first.")
    L.append(f"_Table names ({', '.join(TABLES.values())}) are assumed and mirror `data/*.csv`. "
             "Re-point them at the real warehouse before running._")

    if ctx["caveats"]:
        L += ["", "*Read with care*"] + [f"• {c}" for c in ctx["caveats"]]

    L += ["", f"_Logged to {OUTCOME_LOG.name}. Run the query and reply with the output — "
              "I'll interpret. The 'what actually happened' field stays blank until you do._"]
    return "\n".join(L)


def render_low_confidence(ctx):
    h = ctx["hyps"]
    L = [header(ctx["now"], "🟡 *Streakly Anomaly — LOW CONFIDENCE*"), "",
         f"*Trigger:* {ctx['trigger']}", "",
         f"*Stopped at step 3.* Best hypothesis scored *{h[0]['confidence']}/10*, "
         f"at or below the {CONFIDENCE_GATE}/10 gate — so no SQL and no diagnosis. "
         "The move is real; the explanation isn't supported yet.", "",
         "*What moved:*"]
    for d in ctx["drivers"]:
        if d["moved"]:
            L.append(f"• {fmt_driver(d)}")
    L += ["", "*Candidates, none strong enough to act on:*"]
    for i, x in enumerate(h, 1):
        L.append(f"{i}. {x['title']} — {x['confidence']}/10")
    if ctx["caveats"]:
        L += ["", "*Read with care*"] + [f"• {c}" for c in ctx["caveats"]]
    L += ["", "_No SQL emitted and nothing logged to the outcome log — there is no call to score. "
              "Next step is a human looking at the cut, not a query._"]
    return "\n".join(L)


def render_inconclusive(ctx):
    L = [header(ctx["now"], "⚪️ *Streakly Anomaly — INCONCLUSIVE*"), "",
         f"*Trigger:* {ctx['trigger']}", "",
         f"*Stopped at step 2.* Only {ctx['n_movers']} driver moved past its threshold; "
         f"the loop needs {MIN_DRIVERS}. A single-driver move is as likely to be noise as a cause.", "",
         "*Metric tree:*"]
    for d in ctx["drivers"]:
        L.append(f"• {fmt_driver(d)}" + ("  ← the only mover" if d["moved"] else ""))
    L += ["", "_No hypotheses generated, nothing logged to the outcome log. "
              "Re-run when the next cohort lands, or widen the window by hand._"]
    return "\n".join(L)


# ---------------------------------------------------------------- step 5: log


def append_outcome_log(ctx, path):
    new = not path.exists()
    h = ctx["hyps"]
    L = []
    if new:
        L += ["# Outcome Log — Streakly anomaly diagnoses", "",
              "One block per diagnosis that cleared the confidence gate. The "
              "**What actually happened** field is written by a human after the SQL "
              "is run — it is the only thing that turns these confidence scores from "
              "guesses into a calibrated instrument. An entry with it still blank is "
              "an open call, not a result.", "",
              "Appended by `agents/anomaly_diagnosis.py`. Spec: `agents/anomaly-diagnosis.md`.", ""]
    fixture = "fixtures" in str(ctx["data_dir"])
    L += [f"## {ctx['now']:%Y-%m-%d %H:%M} — "
          + ("[FIXTURE] " if fixture else "") + f"{ctx['trigger_short']}", "",
          f"- **Data source:** `{ctx['data_dir']}`"
          + ("  ⚠️ **synthetic fixture — not a production call, do not calibrate on this**"
             if fixture else ""),
          f"- **Trigger:** {ctx['trigger']}",
          f"- **Drivers that moved:** " + (", ".join(
              f"{d['label']} ({d['delta']:+.1f}pts)" if d["unit"] == "pts"
              else f"{d['label']} ({d['delta']:+.1f} sessions, {d['rel']:+.0f}%)"
              for d in ctx["drivers"] if d["moved"]) or "none"),
          "", "### Ranked hypotheses", ""]
    for i, x in enumerate(h, 1):
        L.append(f"{i}. **{x['title']}** — confidence **{x['confidence']}/10**"
                 + ("" if x["confirmable"] else " _(not confirmable from current data)_"))
        L.append(f"   - Basis: {x['basis']}")
    L += ["", f"### SQL issued (hypothesis 1: {h[0]['key']})", "", "```sql", h[0]["sql"], "```", "",
          "### What actually happened", "", "_TBD — fill this in after running the query._", "",
          "### Was the top hypothesis right?", "",
          "_TBD — yes / no / partly. This is the calibration signal; without it the "
          "confidence scores above stay uncalibrated._", "", "---", ""]
    with open(path, "a", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    return path


def log_run(line, path=RUN_LOG):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")


# ---------------------------------------------------------------- the loop


def run(data_dir, now, dry_run=False, post=False, outcome_log=OUTCOME_LOG, verbose=True):
    """Returns (stopped_at_step, slack_text_or_None)."""
    users, retention, by_id = load(data_dir)
    extra, missing = load_extra(data_dir)
    weeks = sorted({r["cohort_week"] for r in retention}, key=int)
    if len(weeks) < 2:
        sys.exit(f"ERROR: need at least 2 cohort weeks to compare. Found: {weeks}")

    cur_w, prev_w = weeks[-1], weeks[-2]
    cur = compute_week(retention, by_id, cur_w)
    prev = compute_week(retention, by_id, prev_w)
    a = analyse(cur, prev)
    conf_notes = confounds(cur, prev, a)

    def say(msg):
        if verbose:
            print(msg)

    # ---- Step 1: threshold check
    triggers = [(k, lbl, a[k]) for k, lbl in (("d7", "Day-7 retention"),
                                              ("brk", "Streak-break rate"))
                if a[k] and a[k]["alert"]]
    say(f"STEP 1 threshold check (> {ALERT_PTS:.0f} pts): "
        + (f"PASS — {len(triggers)} metric(s) over threshold" if triggers else "STOP — nothing over threshold"))
    if not triggers:
        d7 = a["d7"]
        line = (f"{now:%Y-%m-%d %H:%M} step1 no-trigger — Day-7 {d7['delta']:+.1f}pts, "
                f"streak-break {a['brk']['delta']:+.1f}pts, both within ±{ALERT_PTS:.0f}. "
                f"week {cur_w} vs {prev_w}.")
        if not dry_run:
            log_run(line)
        say("  " + line)
        return 1, None

    # Day-7 leads whenever it alerted, even if streak-break moved further.
    # Streak-break is a *driver inside the metric tree* -- promoting it to the
    # headline double-counts it and buries the metric the project is measured
    # on. Streak-break only becomes the trigger when Day-7 itself didn't alert.
    tkey, tlabel, tm = next(
        (t for t in triggers if t[0] == "d7"),
        max(triggers, key=lambda t: abs(t[2]["delta"])),
    )
    trigger = (f"{tlabel} {'dropped' if tm['delta'] < 0 else 'rose'} "
               f"{abs(tm['delta']):.0f}pts ({tm['prev']:.0f}% → {tm['cur']:.0f}%) "
               f"week over week — cohort week {cur_w} vs {prev_w}, n={tm['n_cur']}/{tm['n_prev']}, {fmt_p(tm['p'])}")
    say(f"  trigger: {trigger}")

    # ---- Step 2: metric tree decomposition
    dc_cur = driver_cells(retention, by_id, extra, cur_w)
    dc_prev = driver_cells(retention, by_id, extra, prev_w)
    drivers = driver_moves(dc_cur, dc_prev, missing)
    segments = segment_moves(a)
    movers = [d for d in drivers if d["moved"]]
    say(f"STEP 2 metric tree (>= {MIN_DRIVERS} movers): "
        + (f"PASS — {len(movers)} of {len(drivers)} drivers moved" if len(movers) >= MIN_DRIVERS
           else f"STOP (inconclusive) — only {len(movers)} of {len(drivers)} drivers moved"))

    caveats = list(conf_notes)
    if missing:
        caveats.append(f"{', '.join(missing)} not found — those drivers were skipped, "
                       "so the decomposition is partial")

    ctx = {"now": now, "trigger": trigger,
           "trigger_short": f"{tlabel} {tm['delta']:+.0f}pts",
           "drivers": drivers, "segments": segments, "caveats": caveats,
           "n_movers": len(movers), "hyps": [],
           "data_dir": data_dir.relative_to(REPO) if data_dir.is_relative_to(REPO) else data_dir}

    if len(movers) < MIN_DRIVERS:
        text = render_inconclusive(ctx)
        if not dry_run:
            log_run(f"{now:%Y-%m-%d %H:%M} step2 inconclusive — {len(movers)} driver moved "
                    f"({', '.join(d['key'] for d in movers) or 'none'}). week {cur_w} vs {prev_w}.")
        return 2, text

    # ---- Step 3: hypothesis generation
    hyps, _ = hypotheses(drivers, segments, a["d7"])
    ctx["hyps"] = hyps[:3]
    top = ctx["hyps"][0] if ctx["hyps"] else None
    say(f"STEP 3 hypotheses (top > {CONFIDENCE_GATE}/10): "
        + (f"PASS — top is {top['confidence']}/10 ({top['key']})"
           if top and top["confidence"] > CONFIDENCE_GATE
           else f"STOP (low confidence) — top is {top['confidence']}/10" if top else "STOP — none generated"))
    if not top or top["confidence"] <= CONFIDENCE_GATE:
        text = render_low_confidence(ctx) if top else render_inconclusive(ctx)
        if not dry_run:
            log_run(f"{now:%Y-%m-%d %H:%M} step3 low-confidence — top "
                    f"{top['confidence'] if top else 0}/10. week {cur_w} vs {prev_w}. "
                    "Nothing written to the outcome log.")
            if post:
                post_to_slack(text)
        return 3, text

    # The gate is a confidence score, not a significance test, so a hypothesis
    # can clear 6/10 on a move that a z-test shrugs at. Say so rather than
    # letting the score imply statistical support it doesn't have.
    primary = next((d for d in drivers if d["moved"] and not d["good"]
                    and d["key"] in top["basis"].lower().replace(" ", "_")), None)
    weak = [d for d in movers if d["p"] is not None and not d["significant"]]
    if weak and not any(d["significant"] for d in movers):
        ctx["caveats"].append(
            f"no driver in this decomposition reaches significance (best is "
            f"{min((d['p'] for d in weak)):.2f}) — the {top['confidence']}/10 score is "
            "a rule-based weight on the pattern, not statistical support for it"
        )

    # ---- Step 4: SQL + Slack
    text = render_full(ctx)
    say(f"STEP 4 SQL + Slack: PASS — query for '{top['key']}'"
        + ("" if top["confirmable"] else " (flagged: not confirmable from current data)"))

    # ---- Step 5: outcome log
    if dry_run:
        say(f"STEP 5 outcome log: SKIPPED (--dry-run) — would append to {outcome_log.name}")
    else:
        p = append_outcome_log(ctx, outcome_log)
        say(f"STEP 5 outcome log: PASS — appended to {p.relative_to(REPO)}")
        log_run(f"{now:%Y-%m-%d %H:%M} step4+5 full diagnostic — top {top['key']} "
                f"{top['confidence']}/10. week {cur_w} vs {prev_w}.")
        if post:
            post_to_slack(text)
    return 5, text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--post", action="store_true", help="POST to $SLACK_WEBHOOK_URL")
    ap.add_argument("--dry-run", action="store_true", help="print only, write nothing, send nothing")
    ap.add_argument("--data-dir", default=str(REPO / "data"))
    ap.add_argument("--now", help="ISO timestamp to use as 'now' (for reproducible tests)")
    ap.add_argument("--outcome-log", default=str(OUTCOME_LOG))
    ap.add_argument("--quiet", action="store_true", help="suppress the step trace")
    args = ap.parse_args()

    now = (datetime.datetime.fromisoformat(args.now) if args.now
           else datetime.datetime.now())
    step, text = run(pathlib.Path(args.data_dir), now, dry_run=args.dry_run,
                     post=args.post, outcome_log=pathlib.Path(args.outcome_log),
                     verbose=not args.quiet)
    if text:
        print("\n" + "─" * 70 + "\n" + text)
    sys.exit(0)


if __name__ == "__main__":
    main()
