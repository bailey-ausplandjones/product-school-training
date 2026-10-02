#!/usr/bin/env python3
"""
metric-pulse — Streakly retention pulse: Day-7 retention + streak-break rate,
split by acquisition channel, delivered as a Monday-morning Slack digest.

Runs nightly (computes + snapshots, posts nothing). Posts only on Monday,
or when --force-post is passed.

Stdlib only. No network calls unless --post is passed.

Usage:
    python3 agents/metric_pulse.py --dry-run            # print only, write nothing
    python3 agents/metric_pulse.py                      # print + snapshot, no Slack
    python3 agents/metric_pulse.py --post               # nightly: snapshot, post only if Monday
    python3 agents/metric_pulse.py --post --force-post  # post regardless of weekday

Spec: agents/metric-pulse.md
"""

import argparse, csv, datetime, json, math, os, pathlib, sys

# ---------------------------------------------------------------- config

REPO = pathlib.Path(__file__).resolve().parent.parent
OUT_DIR = REPO / "ops" / "agent" / "pulse"
SNAP_DIR = OUT_DIR / "snapshots"

# The project brief's post-v2 Day-7 figure. This is the number the Comeback
# project is trying to move back to >=48%. It is NOT the sample data's own
# Day-7 (38.6% overall; 27-61% by cohort week), so the digest reports distance
# from it as context, never as a week-over-week delta.
BASELINE_D7 = 39.0
TARGET_D7 = 48.0

# Spec'd alert threshold: a move of this many points or more, week over week.
ALERT_PTS = 2.0

# A channel cell in this dataset is ~33 users, where one user is ~3 points.
# Below this n, a per-channel move is labelled indicative and can never be the
# "watch this" pick on its own -- the threshold would fire on noise otherwise.
MIN_CELL_N = 100

CHANNELS = ["organic", "paid", "referral"]
TRUE = "true"

# Which direction is good news, per metric. Without this the digest badges a
# falling streak-break rate -- unambiguously good -- with a warning triangle,
# and the reader has to already know which way is better for each metric.
BETTER = {"d7": "up", "brk": "down"}

# ---------------------------------------------------------------- stats


def pct(num, den):
    return None if not den else 100.0 * num / den


def two_prop_p(c1, n1, c2, n2):
    """Two-sided p-value, two-proportion z-test. None when undefined."""
    if not n1 or not n2:
        return None
    pool = (c1 + c2) / (n1 + n2)
    se = math.sqrt(pool * (1 - pool) * (1 / n1 + 1 / n2))
    if se == 0:
        return None
    z = (c1 / n1 - c2 / n2) / se
    return math.erfc(abs(z) / math.sqrt(2))


def fmt_p(p):
    if p is None:
        return "p n/a"
    return "p<0.001" if p < 0.001 else f"p={p:.3f}"


def arrow(delta):
    """Arrow + wording for a week-over-week move, rounded to whole points."""
    r = round(delta)
    if r == 0:
        return "→", "flat"
    sym = "↑" if r > 0 else "↓"
    unit = "pt" if abs(r) == 1 else "pts"
    return sym, f"{abs(r)}{unit} vs last week"


# ---------------------------------------------------------------- load


def load(data_dir):
    def rows(name):
        path = data_dir / name
        if not path.exists():
            sys.exit(f"ERROR: missing required file {path}")
        with open(path, newline="", encoding="utf-8") as fh:
            return list(csv.DictReader(fh))

    users = rows("users.csv")
    retention = rows("retention.csv")
    by_id = {u["user_id"]: u for u in users}
    missing = [r["user_id"] for r in retention if r["user_id"] not in by_id]
    if missing:
        sys.exit(
            f"ERROR: {len(missing)} user(s) in retention.csv have no row in users.csv "
            f"(e.g. {missing[0]}) — cannot attribute them to a channel. Fix the export."
        )
    return users, retention, by_id


def compute_week(retention, by_id, week):
    """Day-7 + streak-break, overall and per channel, for one cohort week."""
    rows = [r for r in retention if r["cohort_week"] == week]

    def cell(subset):
        n = len(subset)
        return {
            "n": n,
            "d7_c": sum(r["day_7"] == TRUE for r in subset),
            "brk_c": sum(r["broke_streak_week1"] == TRUE for r in subset),
            "d7": pct(sum(r["day_7"] == TRUE for r in subset), n),
            "brk": pct(sum(r["broke_streak_week1"] == TRUE for r in subset), n),
        }

    channels = {}
    seen = set()
    for ch in CHANNELS:
        subset = [r for r in rows if by_id[r["user_id"]]["acquisition_channel"] == ch]
        seen.update(r["user_id"] for r in subset)
        if subset:
            channels[ch] = cell(subset)

    # Any channel value in the data that this agent does not know about. Surfaced
    # rather than silently folded into the total.
    unknown = sorted(
        {by_id[r["user_id"]]["acquisition_channel"] for r in rows if r["user_id"] not in seen}
    )

    return {
        "week": week,
        "overall": cell(rows),
        "channels": channels,
        "unknown_channels": unknown,
        "variants": sorted({by_id[r["user_id"]]["variant"] for r in rows if by_id[r["user_id"]]["variant"]}),
    }


# ---------------------------------------------------------------- analyse


def move(cur, prev, metric):
    """One week-over-week move: delta, significance, alert state."""
    a, b = cur[metric], prev[metric]
    if a is None or b is None:
        return None
    delta = a - b
    ckey, = {"d7": ("d7_c",), "brk": ("brk_c",)}[metric]
    p = two_prop_p(cur[ckey], cur["n"], prev[ckey], prev["n"])
    good = delta > 0 if BETTER[metric] == "up" else delta < 0
    return {
        "cur": a, "prev": b, "delta": delta, "p": p, "good": good,
        "alert": abs(delta) >= ALERT_PTS,
        "significant": p is not None and p < 0.05,
        "n_cur": cur["n"], "n_prev": prev["n"],
        "reliable": cur["n"] >= MIN_CELL_N and prev["n"] >= MIN_CELL_N,
    }


def analyse(cur, prev):
    shared = [ch for ch in CHANNELS if ch in cur["channels"] and ch in prev["channels"]]
    return {
        "d7": move(cur["overall"], prev["overall"], "d7"),
        "brk": move(cur["overall"], prev["overall"], "brk"),
        "channels": {
            ch: {
                "d7": move(cur["channels"][ch], prev["channels"][ch], "d7"),
                "brk": move(cur["channels"][ch], prev["channels"][ch], "brk"),
            }
            for ch in shared
        },
        "dropped_channels": [
            ch for ch in set(cur["channels"]) | set(prev["channels"]) if ch not in shared
        ],
    }


def confounds(cur, prev, a):
    """Every reason not to read a move here as an organic weekly change."""
    notes = []
    if cur["variants"] and not prev["variants"]:
        notes.append(
            f"week {cur['week']} is split across a live experiment "
            f"({'/'.join(cur['variants'])}) and week {prev['week']} is not — this "
            "week's movement is partly the test, not an organic weekly change"
        )
    thin = [ch for ch, m in a["channels"].items() if m["d7"] and not m["d7"]["reliable"]]
    if thin:
        n = min(a["channels"][ch]["d7"]["n_cur"] for ch in thin)
        notes.append(
            f"channel cells are n≈{n}, where one user moves the rate ~{100/n:.0f} pts — "
            f"the ±{ALERT_PTS:.0f}-pt threshold cannot distinguish a channel move from "
            "a single user. Per-channel lines are directional only"
        )
    for ch in sorted(a["dropped_channels"]):
        notes.append(f"'{ch}' is present in only one of the two weeks — omitted from the breakdown")
    for w in (cur, prev):
        if w["unknown_channels"]:
            notes.append(
                f"week {w['week']} contains unrecognised channel(s) "
                f"{', '.join(w['unknown_channels'])} — not in the breakdown, but counted in the total"
            )
    return notes


def pick_watch(a):
    """The channel to flag with 'watch this'. Worst adverse Day-7 move, admitted
    only if the cell is big enough for the threshold to mean anything OR the move
    clears significance on its own small n. Returns None rather than promoting
    noise -- a digest that always finds a culprit is useless.

    The n-gate alone was too blunt: at n=34 it suppressed a genuine 26-pt drop
    (week 4 paid) that a two-proportion test calls real. Either test passing is
    enough; neither passing means the move is one or two users.
    """
    pool = [
        (ch, m["d7"]) for ch, m in a["channels"].items()
        if m["d7"] and m["d7"]["delta"] <= -ALERT_PTS
        and (m["d7"]["reliable"] or m["d7"]["significant"])
    ]
    if not pool:
        return None
    return min(pool, key=lambda t: t[1]["delta"])[0]


def top_signal(a, cur, prev, conf, watch):
    """Rule-based, deliberately few. Points at something to inspect; decides nothing."""
    if any("experiment" in c for c in conf):
        return (
            f"Week {cur['week']} is the pilot week — the Day-7 jump is the experiment, "
            "not a channel or seasonality story. Read it from data/metric-diagnosis.md "
            "(treatment vs control within the week), not from this week-over-week line."
        )
    if watch:
        m = a["channels"][watch]["d7"]
        basis = "significant on a thin cell" if not m["reliable"] else "on a reliable cell"
        return (
            f"{watch.title()} Day-7 is down {abs(m['delta']):.0f} pts ({m['prev']:.0f}% → "
            f"{m['cur']:.0f}%, {fmt_p(m['p'])} — {basis}). Check what changed in that channel "
            "last week — campaign, creative, or targeting — before reading it as a product problem."
        )
    thin = [ch for ch, m in a["channels"].items() if m["d7"] and not m["d7"]["reliable"]]
    if thin:
        return (
            "No channel move clears significance or a reliable cell size to separate from single-user noise at these "
            f"cell sizes (n≈{min(a['channels'][ch]['d7']['n_cur'] for ch in thin)} per channel). "
            "Nothing to action from the channel split this week."
        )
    if a["d7"] and a["d7"]["alert"]:
        return (
            f"Overall Day-7 moved {a['d7']['delta']:+.0f} pts with no single channel driving it — "
            "look at the day-1→day-7 drop-off curve rather than the channel mix."
        )
    return "No metric crossed the alert threshold. Nothing new this week."


# ---------------------------------------------------------------- render


def badge(m, confounded=False):
    """A threshold crossing is only a warning when it crossed the wrong way.
    Favourable crossings still get marked -- the point is that the reader should
    not have to remember that falling streak-break is good news.

    In a confounded week the test's primary metric gets neither badge. A green
    tick beside the pilot's +34 pts would be the agent reporting the experiment
    back as if it were a good week, which is the exact failure the confound
    guard exists to prevent. Streak-break is upstream of the test (set in week
    1, before the Comeback screen can fire), so it keeps its badge.
    """
    if confounded:
        return " 🔬 EXPERIMENT — not a weekly move"
    if not m["alert"]:
        return ""
    return " ✅ IMPROVED" if m["good"] else " ⚠️ ALERT"


def render(cur, prev, a, conf, signal, watch, run_date):
    d7, brk = a["d7"], a["brk"]
    confounded = any("experiment" in c for c in conf)
    lines = [f"📊 *Streakly Retention Pulse, {run_date:%a %b %-d}*", ""]

    sym, words = arrow(d7["delta"])
    lines.append(f"*Day-7 retention: {d7['cur']:.0f}%* ({sym} {words}){badge(d7, confounded)}")
    lines.append(
        f"_vs {BASELINE_D7:.0f}% baseline: {d7['cur'] - BASELINE_D7:+.0f} pts · "
        f"target ≥{TARGET_D7:.0f}% · {fmt_p(d7['p'])}_"
    )
    lines.append("")

    sym, words = arrow(brk["delta"])
    lines.append(
        f"*Streak-break rate: {brk['cur']:.0f}%* ({sym} {words}){badge(brk)}"
        "  _(lower is better)_"
    )
    lines.append("")

    lines.append("*By channel* (Day-7):")
    for ch in CHANNELS:
        m = a["channels"].get(ch, {}).get("d7")
        if not m:
            continue
        sym, words = arrow(m["delta"])
        tail = " ← watch this" if ch == watch else ""
        if not m["reliable"]:
            tail += f"  _(n={m['n_cur']}, directional)_"
        lines.append(f"• {ch.title()}: {m['cur']:.0f}% ({sym} {words}){tail}")
    lines.append("")

    lines.append(f"*Top signal:* {signal}")

    if conf:
        lines += ["", "*Read with care*"] + [f"• {c}" for c in conf]

    lines += [
        "",
        "*Next:* run anomaly diagnosis? Reply YES to trigger. "
        "_(not yet wired — see §6 of agents/metric-pulse.md)_",
        "",
        f"_Cohort week {cur['week']} vs week {prev['week']} · n={d7['n_cur']} / {d7['n_prev']} · "
        f"alert threshold ±{ALERT_PTS:.0f} pts · generated by agents/metric_pulse.py_",
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
            print(f"[--post] Slack responded {resp.status}", file=sys.stderr)
            return resp.status == 200
    except urllib.error.URLError as e:
        print(f"[--post] FAILED: {e}", file=sys.stderr)
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--post", action="store_true", help="POST to $SLACK_WEBHOOK_URL (Mondays only)")
    ap.add_argument("--force-post", action="store_true", help="with --post, ignore the weekday gate")
    ap.add_argument("--dry-run", action="store_true", help="print only, write nothing, send nothing")
    ap.add_argument("--data-dir", default=str(REPO / "data"))
    ap.add_argument("--max-week", type=int, help="treat this cohort week as the latest (for testing)")
    ap.add_argument("--chain-anomaly", action="store_true",
                    help="on an alert, hand off to agents/anomaly_diagnosis.py")
    args = ap.parse_args()

    users, retention, by_id = load(pathlib.Path(args.data_dir))
    weeks = sorted({r["cohort_week"] for r in retention}, key=int)
    if args.max_week is not None:
        weeks = [w for w in weeks if int(w) <= args.max_week]
    if len(weeks) < 2:
        sys.exit(f"ERROR: need at least 2 cohort weeks to compare. Found: {weeks}")

    cur = compute_week(retention, by_id, weeks[-1])
    prev = compute_week(retention, by_id, weeks[-2])
    a = analyse(cur, prev)
    if not a["d7"] or not a["brk"]:
        sys.exit("ERROR: could not compute an overall Day-7 / streak-break move. Check the export.")

    conf = confounds(cur, prev, a)
    watch = pick_watch(a)
    signal = top_signal(a, cur, prev, conf, watch)
    run_date = datetime.date.today()
    text = render(cur, prev, a, conf, signal, watch, run_date)

    print(text)

    if not args.dry_run:
        SNAP_DIR.mkdir(parents=True, exist_ok=True)
        snap = SNAP_DIR / f"{run_date.isoformat()}-week{cur['week']}.json"
        snap.write_text(
            json.dumps({"run_date": run_date.isoformat(), "current": cur, "previous": prev,
                        "analysis": a, "alerts": {"d7": a["d7"]["alert"], "brk": a["brk"]["alert"]}},
                       indent=2),
            encoding="utf-8",
        )
        print(f"\n[saved] {snap.relative_to(REPO)}", file=sys.stderr)

    # Chain: the diagnostic loop runs only when this agent actually alerted.
    # A quiet week ends here, which is the whole point of gating it.
    if args.chain_anomaly:
        fired = [k for k in ("d7", "brk") if a[k] and a[k]["alert"]]
        if not fired:
            print("\n[--chain-anomaly] no alert — anomaly diagnosis not invoked.", file=sys.stderr)
        else:
            print(f"\n[--chain-anomaly] {', '.join(fired)} over threshold → "
                  "invoking agents/anomaly_diagnosis.py", file=sys.stderr)
            import anomaly_diagnosis
            anomaly_diagnosis.run(
                pathlib.Path(args.data_dir), datetime.datetime.now(),
                dry_run=args.dry_run, post=args.post,
            )

    if args.post:
        if args.dry_run:
            print("\n[--post] suppressed by --dry-run. Nothing sent.", file=sys.stderr)
            return
        if run_date.weekday() != 0 and not args.force_post:
            print(
                f"\n[--post] {run_date:%A} is not Monday — snapshot written, nothing sent. "
                "This is the nightly path.",
                file=sys.stderr,
            )
            return
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        (OUT_DIR / f"{run_date.isoformat()}-pulse.md").write_text(text + "\n", encoding="utf-8")
        post_to_slack(text)


if __name__ == "__main__":
    main()
