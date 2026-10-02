#!/usr/bin/env python3
"""
monday-retention — Monday-morning pre-standup retention digest for Streakly.

Compares the latest complete cohort week against the prior one on four metrics,
picks the biggest mover, suggests one thing to look at, and posts a plain-English
digest to Slack.

Stdlib only. No pandas, no scipy, no network calls unless --post is passed.

Usage:
    python3 agents/monday_retention.py                 # dry run: print + save, no Slack
    python3 agents/monday_retention.py --post          # also POST to $SLACK_WEBHOOK_URL
    python3 agents/monday_retention.py --no-save       # print only, no files written
    python3 agents/monday_retention.py --data-dir data # override data location

Spec: agents/monday-retention.md
"""

import argparse, csv, datetime, json, math, os, pathlib, sys
from collections import defaultdict

# ---------------------------------------------------------------- config

REPO = pathlib.Path(__file__).resolve().parent.parent
OUT_DIR = REPO / "ops" / "agent"
SNAP_DIR = OUT_DIR / "snapshots"

# What to do with standup time when nothing moved materially. Edit this as the
# project's live open decision changes -- the agent will not invent one.
STANDING_FOCUS = (
    "the second-cohort go/no-go — the rollout target is still unresolved "
    "(breakers vs non-breakers; see data/metric-diagnosis.md)"
)

# A move smaller than this is reported but never promoted to headline or action.
NOISE_FLOOR_PTS = 3.0
TRUE = "true"

# ---------------------------------------------------------------- stats


def pct(num, den):
    return None if not den else 100.0 * num / den


def two_prop_p(c1, n1, c2, n2):
    """Two-sided p-value, two-proportion z-test. Returns (z, p) or (None, None)."""
    if not n1 or not n2:
        return None, None
    p1, p2 = c1 / n1, c2 / n2
    pool = (c1 + c2) / (n1 + n2)
    se = math.sqrt(pool * (1 - pool) * (1 / n1 + 1 / n2))
    if se == 0:
        return None, None
    z = (p1 - p2) / se
    return z, math.erfc(abs(z) / math.sqrt(2))


def fmt_p(p):
    if p is None:
        return ""
    return "p<0.001" if p < 0.001 else f"p={p:.3f}"


def fmt_delta(d, unit="pts"):
    if d is None:
        return "n/a"
    return f"{d:+.1f} {unit}"


# ---------------------------------------------------------------- load


def load(data_dir):
    def rows(name):
        path = data_dir / name
        if not path.exists():
            sys.exit(f"ERROR: missing required file {path}")
        with open(path, newline="", encoding="utf-8") as fh:
            return list(csv.DictReader(fh))

    return {
        "users": rows("users.csv"),
        "retention": rows("retention.csv"),
        "sessions": rows("sessions.csv"),
        "nudges": rows("nudges.csv"),
    }


def compute_week(data, week):
    """All four tracked metrics for one cohort_week, as raw counts + rates."""
    users = [u for u in data["users"] if u["cohort_week"] == week]
    ret = [r for r in data["retention"] if r["cohort_week"] == week]
    cohort_ids = {u["user_id"] for u in users}

    sessions = [s for s in data["sessions"] if s["user_id"] in cohort_ids]
    nudges = [n for n in data["nudges"] if n["user_id"] in cohort_ids]

    d7_n = len(ret)
    d7_c = sum(r["day_7"] == TRUE for r in ret)
    brk_c = sum(r["broke_streak_week1"] == TRUE for r in ret)
    nud_n = len(nudges)
    nud_c = sum(n["opened"] == TRUE for n in nudges)

    variants = {u["variant"] for u in users if u["variant"]}

    return {
        "week": week,
        "users": len(users),
        "d7": {"c": d7_c, "n": d7_n, "rate": pct(d7_c, d7_n)},
        "break": {"c": brk_c, "n": d7_n, "rate": pct(brk_c, d7_n)},
        "sessions_per_user": (len(sessions) / len(users)) if users else None,
        "session_total": len(sessions),
        "push_open": {"c": nud_c, "n": nud_n, "rate": pct(nud_c, nud_n)},
        "variants": sorted(variants),
    }


# ---------------------------------------------------------------- analyse

# key, label, unit, direction, upstream
#
# `upstream` = measured before/independently of the experiment, so a move in it
# is not mechanically caused by the test. Day-7 is the test's primary metric;
# sessions-per-user and push opens are inflated by construction when the
# Comeback screen fires (it IS a session, and it IS a send). Streak-break rate
# is the test's *trigger*, measured in week 1 -- the test cannot move it.
METRICS = [
    ("d7", "Day-7 retention", "pts", "up_good", False),
    ("break", "Streak-break rate", "pts", "down_good", True),
    ("push_open", "Push open rate", "pts", "up_good", False),
]


def movers(cur, prev):
    out = []
    for key, label, unit, direction, upstream in METRICS:
        a, b = cur[key]["rate"], prev[key]["rate"]
        if a is None or b is None:
            continue
        delta = a - b
        z, p = two_prop_p(cur[key]["c"], cur[key]["n"], prev[key]["c"], prev[key]["n"])
        good = delta > 0 if direction == "up_good" else delta < 0
        out.append(
            {
                "key": key, "label": label, "unit": unit,
                "cur": a, "prev": b, "delta": delta,
                "good": good, "p": p, "upstream": upstream,
                "material": abs(delta) >= NOISE_FLOOR_PTS,
                "significant": p is not None and p < 0.05,
            }
        )
    # sessions/user is a ratio, not a proportion -- no z-test, separate unit
    if cur["sessions_per_user"] and prev["sessions_per_user"]:
        d = cur["sessions_per_user"] - prev["sessions_per_user"]
        out.append(
            {
                "key": "sessions_per_user", "label": "Sessions per user",
                "unit": "sessions", "cur": cur["sessions_per_user"],
                "prev": prev["sessions_per_user"], "delta": d,
                "good": d > 0, "p": None, "upstream": False,
                "material": abs(d) >= 0.3, "significant": False,
            }
        )
    out.sort(key=lambda m: abs(m["delta"]) / (NOISE_FLOOR_PTS if m["unit"] == "pts" else 0.3), reverse=True)
    return out


def pick_signal(ms, confounded):
    """The 'one signal to watch'. Never the headline metric (that slot is
    already spent). In a confounded week, prefer a metric the experiment cannot
    mechanically move -- otherwise the agent just reports the test back to you
    as if it were news."""
    pool = [m for m in ms if m["key"] != "d7"]
    if not pool:
        return next(m for m in ms if m["key"] == "d7")
    if confounded:
        upstream = [m for m in pool if m["upstream"]]
        if upstream:
            return upstream[0]
    return pool[0]


def confounds(cur, prev):
    """Reasons not to read a move as an organic week-over-week change."""
    notes = []
    if cur["variants"] and not prev["variants"]:
        notes.append(
            f"week {cur['week']} is split across an experiment "
            f"({'/'.join(cur['variants'])}) and week {prev['week']} is not — "
            "any movement here is partly the test, not an organic weekly change"
        )
    for w in (cur, prev):
        if w["d7"]["n"] < 100:
            notes.append(f"week {w['week']} has only n={w['d7']['n']} — thin")
    if cur["push_open"]["n"] < 30 or prev["push_open"]["n"] < 30:
        notes.append(
            f"push open rate is on n={cur['push_open']['n']} vs n={prev['push_open']['n']} "
            "sends — too thin to act on alone"
        )
    return notes


def suggest_action(top, cur, prev, conf):
    """Rule-based. Deliberately boring and few -- it points at a thing to look
    at, it does not decide anything."""
    if conf and any("experiment" in c for c in conf):
        return (
            f"Don't read this week's Day-7 move as a weekly trend — week "
            f"{cur['week']} is confounded by the live experiment. Pull the "
            "within-week segment split (breakers vs non-breakers) before quoting "
            f"it to anyone. The mover worth a look is {top['label'].lower()}, "
            f"{fmt_delta(top['delta'], top['unit'])} — the test cannot have "
            "caused that one."
        )
    if not top["material"]:
        return f"No material movers. Spend standup on {STANDING_FOCUS}."
    rules = {
        "d7": "Pull the day-1→day-7 drop-off by day for this cohort — the leak has "
              "historically been inside that window, not at acquisition.",
        "break": "Check notification timing and tone for this cohort against "
                 "07-docs/prd.md — streak-break rate is the input the Comeback "
                 "screen is supposed to act on.",
        "push_open": "Check channel health before anything else: opt-out rate and "
                     "send volume. A falling open rate removes the only route back "
                     "to a lapsing user.",
        "sessions_per_user": "Look at session depth by screen — whether the change "
                             "is more users returning or the same users opening more.",
    }
    direction = "improved" if top["good"] else "worsened"
    mag = f"{abs(top['delta']):.1f} {top['unit']}"
    return f"{top['label']} {direction} by {mag}. " + rules[top["key"]]


# ---------------------------------------------------------------- render


def render(cur, prev, ms, conf, action, run_date, baseline_note, top):
    d7 = next(m for m in ms if m["key"] == "d7")
    arrow = "▲" if d7["delta"] > 0 else ("▼" if d7["delta"] < 0 else "▬")
    sig = ""
    if d7["p"] is not None:
        sig = f" ({fmt_p(d7['p'])}, {'significant' if d7['significant'] else 'not significant'})"

    lines = [
        f"*Monday retention digest — {run_date}*",
        f"_Cohort week {cur['week']} vs week {prev['week']}. {baseline_note}_",
        "",
        f"*Headline — Day-7 retention:* {d7['cur']:.1f}% {arrow} {fmt_delta(d7['delta'])} "
        f"vs last week ({d7['prev']:.1f}%){sig}",
        "",
        f"*Signal to watch — {top['label']}:* {top['cur']:.1f}"
        f"{'%' if top['unit'] == 'pts' else ''} vs {top['prev']:.1f}"
        f"{'%' if top['unit'] == 'pts' else ''} last week, {fmt_delta(top['delta'], top['unit'])}"
        f"{'' if top['material'] else ' — inside the noise floor'}",
        "",
        f"*Suggested action:* {action}",
        "",
        "*All tracked metrics*",
    ]
    for m in ms:
        u = "%" if m["unit"] == "pts" else ""
        flag = "" if m["material"] else "  _(noise)_"
        lines.append(
            f"• {m['label']}: {m['cur']:.1f}{u} vs {m['prev']:.1f}{u} "
            f"({fmt_delta(m['delta'], m['unit'])}){flag}"
        )
    if conf:
        lines += ["", "*Read with care*"] + [f"• {c}" for c in conf]
    lines += [
        "",
        f"_n={cur['users']} this week / {prev['users']} last week · "
        f"noise floor ±{NOISE_FLOOR_PTS:.0f} pts · generated by agents/monday_retention.py_",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------- io


def post_to_slack(text):
    url = os.environ.get("SLACK_WEBHOOK_URL")
    if not url:
        print("\n[--post] SLACK_WEBHOOK_URL is not set. Nothing sent.", file=sys.stderr)
        return False
    import urllib.request, urllib.error
    req = urllib.request.Request(
        url,
        data=json.dumps({"text": text}).encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            ok = resp.status == 200
            print(f"[--post] Slack responded {resp.status}", file=sys.stderr)
            return ok
    except urllib.error.URLError as e:
        print(f"[--post] FAILED: {e}", file=sys.stderr)
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--post", action="store_true", help="POST to $SLACK_WEBHOOK_URL")
    ap.add_argument("--no-save", action="store_true", help="print only, write nothing")
    ap.add_argument("--data-dir", default=str(REPO / "data"))
    args = ap.parse_args()

    data = load(pathlib.Path(args.data_dir))
    weeks = sorted({u["cohort_week"] for u in data["users"]}, key=int)
    if len(weeks) < 2:
        sys.exit("ERROR: need at least 2 cohort weeks to compare. Found: " + str(weeks))

    cur, prev = compute_week(data, weeks[-1]), compute_week(data, weeks[-2])
    run_date = datetime.date.today().isoformat()

    # Snapshot-and-diff: persist this run so a future run can diff against it
    # once the data source is live rather than a static export.
    snap_path = SNAP_DIR / f"{run_date}-week{cur['week']}.json"
    prior_snaps = sorted(SNAP_DIR.glob("*.json")) if SNAP_DIR.exists() else []
    baseline_note = (
        "Baseline is the prior cohort week in the same export."
        if not prior_snaps
        else f"Baseline is the prior cohort week; last run was {prior_snaps[-1].name}."
    )

    ms = movers(cur, prev)
    conf = confounds(cur, prev)
    signal = pick_signal(ms, confounded=any("experiment" in c for c in conf))
    action = suggest_action(signal, cur, prev, conf)
    text = render(cur, prev, ms, conf, action, run_date, baseline_note, signal)

    print(text)

    if not args.no_save:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        SNAP_DIR.mkdir(parents=True, exist_ok=True)
        digest = OUT_DIR / f"{run_date}-retention-digest.md"
        digest.write_text(text + "\n", encoding="utf-8")
        snap_path.write_text(json.dumps({"run_date": run_date, "current": cur, "previous": prev}, indent=2), encoding="utf-8")
        print(f"\n[saved] {digest.relative_to(REPO)}", file=sys.stderr)
        print(f"[saved] {snap_path.relative_to(REPO)}", file=sys.stderr)

    if args.post:
        post_to_slack(text)


if __name__ == "__main__":
    main()
