#!/usr/bin/env python3
"""
weekly-insight — Streakly Friday 3-2-1 insight report.

Three sources, one page: retention metrics from data/, sprint completions from
the change log, user-signal themes from the NPS baseline + the research inbox.
Reduced to 3 bullets done / 2 bullets changed / 1 bullet to watch.

Reuses agents/metric_pulse.py for the metric layer rather than recomputing it,
so the two agents can never disagree about a number.

Stdlib only. No network calls unless --post is passed.

Usage:
    python3 agents/weekly_insight.py --dry-run    # print only, write nothing
    python3 agents/weekly_insight.py              # print + save to reports/
    python3 agents/weekly_insight.py --post       # also POST to $SLACK_WEBHOOK_URL

Spec: agents/weekly-insight.md
"""

import argparse, datetime, pathlib, re, subprocess, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from metric_pulse import (  # single source of truth for every metric number
    BASELINE_D7, TARGET_D7, analyse, compute_week, confounds, fmt_p, load,
    post_to_slack,
)

REPO = pathlib.Path(__file__).resolve().parent.parent
REPORT_DIR = REPO / "reports"
CHANGE_LOG = REPO / "01-orient" / "change_log.md"
NPS = REPO / "02-research" / "nps-analysis.md"
INBOX = REPO / "ops" / "research" / "inbox"
OPEN_ITEMS_FILE = REPO / "CLAUDE.md"

MAX_DONE, MAX_CHANGED = 3, 2

# ---------------------------------------------------------------- helpers


def week_window(today):
    """Monday 00:00 through today. A Friday 16:00 run covers Mon-Fri."""
    return today - datetime.timedelta(days=today.weekday()), today


def squeeze(text):
    return re.sub(r"\s+", " ", text).strip()


def first_clause(text, limit=130, sentences=1):
    """Compress a source cell to one bullet without inventing anything: keep the
    leading clause verbatim, cut at a natural break, never paraphrase.

    `sentences=2` is for the watch bullet, where cutting at the first period
    left "Raj's feasibility re-scope" and threw away the entire reason it is the
    thing to watch -- the one bullet that can least afford to be terse.
    """
    text = squeeze(re.sub(r"\*\*(.*?)\*\*", r"\1", text))
    if len(text) <= limit:
        return text
    # Prefer a sentence/clause boundary, taking `sentences` of them.
    for sep in (". ", " — ", "; "):
        parts = text.split(sep)
        if len(parts) > 1:
            cand = sep.join(parts[:sentences]).rstrip(" .;,")
            if len(cand) <= limit:
                return cand
    # Otherwise fall back to the last comma, then the last word, before the cap.
    head = text[:limit]
    for brk in (", ", " "):
        if brk in head:
            return head.rsplit(brk, 1)[0].rstrip(" ,;") + "…"
    return head + "…"


CITED = re.compile(r"\b([\w./-]+\.(?:md|html|csv|py|json))\b")

_BASENAMES = None


def file_present(ref):
    """Is a filename cited in prose actually on disk?

    The change log cites artifacts the way a human writes them -- "captured it in
    project.md" -- not as repo-relative paths. Resolving only from the repo root
    marked `project.md` missing when it lives at `01-orient/project.md`, which
    silently cut a real accomplishment from the report. So: exact path first,
    then a basename match anywhere in the tree.
    """
    global _BASENAMES
    if (REPO / ref).exists():
        return True
    if _BASENAMES is None:
        _BASENAMES = {
            f.name for f in REPO.rglob("*")
            if f.is_file() and ".git" not in f.parts
        }
    return pathlib.PurePath(ref).name in _BASENAMES

# ---------------------------------------------------------------- 1. done


def parse_change_log(path):
    """Markdown table rows -> list of (date, change, why)."""
    if not path.exists():
        return None
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|") or set(line) <= set("|- :"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 2:
            continue
        try:
            d = datetime.date.fromisoformat(cells[0])
        except ValueError:
            continue  # header row
        rows.append((d, cells[1], cells[2] if len(cells) > 2 else ""))
    return rows


def done_this_week(rows, start, end):
    """Change-log entries inside the window, newest first, deduped by the
    artifact they name. Any entry citing a file that isn't on disk is cut and
    reported -- an unverifiable claim is worse than a short list."""
    kept, cut, seen = [], [], set()
    for d, change, why in sorted(
        (r for r in rows if start <= r[0] <= end), key=lambda r: r[0], reverse=True
    ):
        missing = [f for f in CITED.findall(change) if not file_present(f)]
        if missing:
            cut.append((d, first_clause(change, 80), f"cites missing {', '.join(missing)}"))
            continue
        key = tuple(sorted(CITED.findall(change))) or first_clause(change, 40)
        if key in seen:
            cut.append((d, first_clause(change, 80), "same artifact as an earlier bullet"))
            continue
        seen.add(key)
        kept.append((d, first_clause(change)))
    return kept, cut


def changelog_coverage(rows, start, end):
    """The change log is hand-maintained and drifts behind git. Say so rather
    than presenting a stale 'done this week' as complete."""
    try:
        out = subprocess.run(
            ["git", "log", f"--since={start.isoformat()}", "--pretty=%h"],
            cwd=REPO, capture_output=True, text=True, timeout=10,
        )
        commits = len([l for l in out.stdout.splitlines() if l.strip()])
    except (OSError, subprocess.SubprocessError):
        return None
    logged = len([r for r in rows if start <= r[0] <= end])
    if commits <= logged:
        return None
    latest = max((r[0] for r in rows), default=None)
    note = (
        f"{commits} commits this week vs {logged} change-log entries — the log is "
        "hand-maintained and behind, so 'Done this week' reflects the log, not the repo"
    )
    if latest and latest < end:
        note += f" (last entry {latest.isoformat()})"
    return note


# ---------------------------------------------------------------- 2. changed


def metric_changes(data_dir):
    """Metric moves that cleared the alert threshold, biggest first.
    Returns (bullets, confound_notes, context_line)."""
    users, retention, by_id = load(data_dir)
    weeks = sorted({r["cohort_week"] for r in retention}, key=int)
    if len(weeks) < 2:
        return [], ["only one cohort week in the export — no week-over-week move to report"], None

    cur = compute_week(retention, by_id, weeks[-1])
    prev = compute_week(retention, by_id, weeks[-2])
    a = analyse(cur, prev)
    conf = confounds(cur, prev, a)
    confounded = any("experiment" in c for c in conf)

    out = []
    for key, label in (("d7", "Day-7 retention"), ("brk", "Streak-break rate")):
        m = a[key]
        if not m or not m["alert"]:
            continue
        word = "up" if m["delta"] > 0 else "down"
        if confounded and key == "d7":
            tag = " — this is the pilot week, not an organic move"
        else:
            tag = " — good" if m["good"] else " — adverse"
        out.append((
            abs(m["delta"]),
            f"{label} {word} {abs(m['delta']):.0f}pts week over week, now {m['cur']:.0f}% "
            f"(cohort week {cur['week']} vs {prev['week']}, n={m['n_cur']}/{m['n_prev']}, "
            f"{fmt_p(m['p'])}){tag}",
        ))

    # Channel detail only when it is strong enough to stand alone.
    for ch, mm in sorted(a["channels"].items()):
        m = mm["d7"]
        if m and m["alert"] and m["significant"] and not confounded:
            out.append((
                abs(m["delta"]) - 0.5,  # ranks just below an equal-sized overall move
                f"{ch.title()} channel Day-7 {'up' if m['delta'] > 0 else 'down'} "
                f"{abs(m['delta']):.0f}pts to {m['cur']:.0f}% ({fmt_p(m['p'])} on n={m['n_cur']}) "
                f"— {'good' if m['good'] else 'adverse'}, and the only channel to clear significance",
            ))

    ctx = (
        f"Day-7 sits at {a['d7']['cur']:.0f}% against the {BASELINE_D7:.0f}% baseline "
        f"and a ≥{TARGET_D7:.0f}% target."
        if a["d7"] else None
    )
    out.sort(key=lambda t: -t[0])
    return out, conf, ctx


def nps_themes(path, limit=3):
    """Ranked themes from the NPS baseline. This file is an undated one-off
    analysis of 10 comments -- it has no per-week dimension, so these are never
    reported as 'this week'. See spec section 0b."""
    if not path.exists():
        return []
    themes = []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\|\s*(\d+)\s*\|\s*\*\*(.+?)\*\*.*?\|\s*(\d+)\s*\|", line)
        if m:
            themes.append({"rank": int(m.group(1)), "theme": squeeze(m.group(2)),
                           "mentions": int(m.group(3))})
    return sorted(themes, key=lambda t: t["rank"])[:limit]


def inbox_signals(inbox):
    """Raw feedback dropped this week. Empty inbox -> no user-signal bullet,
    ever. A quiet week is reported as quiet, not padded with the baseline."""
    if not inbox.exists():
        return []
    return [p for p in sorted(inbox.iterdir())
            if p.is_file() and p.suffix.lower() in {".md", ".txt", ".csv"} and p.name != "README.md"]


# ---------------------------------------------------------------- 3. watch


def open_items(path):
    """The canonical open-decisions list, read from CLAUDE.md. The agent does
    not invent a thing to watch -- if the list is gone, it says so."""
    if not path.exists():
        return []
    m = re.search(r"\*\*Open, genuinely unresolved:\*\*\n(.*?)\n\s*\n", path.read_text(encoding="utf-8"), re.S)
    if not m:
        return []
    return [n.group(2).strip() for n in
            (re.match(r"\s*(\d+)\.\s+(.*)", l) for l in m.group(1).splitlines()) if n]


KILL_RISK = re.compile(r"most likely to kill|kill the initiative|gates? the build|hard blocker", re.I)


def pick_watch(items):
    """Rank: an item the workspace itself flags as existential wins; otherwise
    the first listed. Returns (bullet, basis) or None."""
    if not items:
        return None
    for it in items:
        if KILL_RISK.search(it):
            return (first_clause(it, 240, sentences=2),
                    "CLAUDE.md flags this as the risk most likely to kill the initiative")
    return first_clause(items[0], 240, sentences=2), "first open item in CLAUDE.md"


# ---------------------------------------------------------------- render


def render(ctx):
    """The 3-2-1 summary. This exact text is what goes to Slack and to the top
    of the saved report."""
    L = [f"📋 *Streakly Weekly Insight, {ctx['date']:%a %b %-d}*", "", "*Done this week:*"]

    if ctx["done"]:
        for d, b in ctx["done"][:MAX_DONE]:
            L.append(f"• {b}  _({d:%b %-d})_")
        if len(ctx["done"]) < MAX_DONE:
            L.append(f"_Only {len(ctx['done'])} change-log entr"
                     f"{'y' if len(ctx['done']) == 1 else 'ies'} this week — not padded to 3._")
    else:
        L.append("• _Nothing logged in the change log this week._")

    L += ["", "*Changed this week:*"]
    if ctx["changed"]:
        for b in ctx["changed"][:MAX_CHANGED]:
            L.append(f"• {b}")
        if len(ctx["changed"]) < MAX_CHANGED:
            L.append(f"_Only {len(ctx['changed'])} move cleared the ±2-pt threshold — not padded to 2._")
    else:
        L.append("• _No metric or user signal moved past the threshold this week._")

    L += ["", "*Watch next week:*"]
    L.append(f"• {ctx['watch'][0]}" if ctx["watch"] else
             "• _No open items found in CLAUDE.md — the agent will not invent one._")

    if ctx["caveats"]:
        L += ["", "*Read with care*"] + [f"• {c}" for c in ctx["caveats"]]

    L += ["", f"_Saved to reports/{ctx['date'].isoformat()}.md · "
              f"week of {ctx['start']:%b %-d}–{ctx['date']:%b %-d} · "
              "generated by agents/weekly_insight.py_"]
    return "\n".join(L)


def render_report(ctx, summary):
    """The saved file: the summary, plus the provenance a Slack post can't carry."""
    L = [f"# Streakly Weekly Insight — {ctx['date'].isoformat()}", "",
         f"Week of {ctx['start'].isoformat()} to {ctx['date'].isoformat()}. "
         f"Generated by `agents/weekly_insight.py`. Spec: `agents/weekly-insight.md`.", "",
         "## 3-2-1 summary (as posted to Slack)", "", "```", summary, "```", "",
         "## Sources read", ""]
    for label, path, note in ctx["sources"]:
        L.append(f"- **{label}** — `{path}`{(' — ' + note) if note else ''}")

    if ctx["context"]:
        L += ["", "## Metric context", "", ctx["context"]]

    if ctx["cut"]:
        L += ["", "## Cut from 'Done this week'", "",
              "Entries dropped rather than reported unverified:", ""]
        for d, b, why in ctx["cut"]:
            L.append(f"- `{d.isoformat()}` {b} — **{why}**")

    overflow = ctx["done"][MAX_DONE:]
    if overflow:
        L += ["", "## Verified, but beyond the 3-bullet cap", "",
              f"{len(overflow)} further change-log entr"
              f"{'y' if len(overflow) == 1 else 'ies'} passed verification and lost only to "
              "the 3-bullet limit. Listed so the cap never reads as 'nothing else happened':", ""]
        for d, b in overflow:
            L.append(f"- `{d.isoformat()}` {b}")

    L += ["", "## NPS themes — standing baseline, NOT this week", "",
          "`02-research/nps-analysis.md` is an undated one-off analysis of 10 comments. "
          "It has no per-week dimension, so these themes are *not* movement and are "
          "deliberately excluded from the 3-2-1 summary. They are listed here as "
          "standing context only.", ""]
    if ctx["themes"]:
        for t in ctx["themes"]:
            L.append(f"{t['rank']}. {t['theme']} — {t['mentions']}/10 mentions")
    else:
        L.append("_No ranked themes parsed._")

    L += ["", "### New feedback this week", ""]
    L.append("\n".join(f"- `{p.name}`" for p in ctx["inbox"]) if ctx["inbox"] else
             "_Research inbox is empty — no new user signal this week. Reported as quiet "
             "rather than padded with the baseline themes above._")

    if ctx["watch"]:
        L += ["", "## Why that watch item", "", f"{ctx['watch'][0]}", "", f"*Basis:* {ctx['watch'][1]}"]

    if ctx["caveats"]:
        L += ["", "## Caveats", ""] + [f"- {c}" for c in ctx["caveats"]]

    return "\n".join(L) + "\n"


# ---------------------------------------------------------------- main


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--post", action="store_true", help="POST the 3-2-1 summary to $SLACK_WEBHOOK_URL")
    ap.add_argument("--dry-run", action="store_true", help="print only, write nothing, send nothing")
    ap.add_argument("--data-dir", default=str(REPO / "data"))
    ap.add_argument("--date", help="treat this ISO date as today (for testing)")
    args = ap.parse_args()

    today = datetime.date.fromisoformat(args.date) if args.date else datetime.date.today()
    start, end = week_window(today)

    rows = parse_change_log(CHANGE_LOG)
    if rows is None:
        sys.exit(f"ERROR: missing required source {CHANGE_LOG}")
    done, cut = done_this_week(rows, start, end)
    coverage = changelog_coverage(rows, start, end)

    changed, conf, context = metric_changes(pathlib.Path(args.data_dir))
    inbox = inbox_signals(INBOX)
    themes = nps_themes(NPS)
    watch = pick_watch(open_items(OPEN_ITEMS_FILE))

    caveats = list(conf)
    if coverage:
        caveats.append(coverage)
    if not inbox:
        caveats.append(
            "research inbox is empty — no new user signal this week, so no NPS theme is "
            "reported as movement (the NPS file itself is undated and cannot support a "
            "'this week' claim)"
        )
    if not NPS.exists():
        caveats.append(f"{NPS.relative_to(REPO)} not found — no user-signal source read")

    ctx = {
        "date": today, "start": start, "done": done, "cut": cut,
        "changed": [b for _, b in changed], "watch": watch, "themes": themes,
        "inbox": inbox, "caveats": caveats, "context": context,
        "sources": [
            ("Retention metrics", f"{pathlib.Path(args.data_dir).name}/ (via agents/metric_pulse.py)", "users.csv + retention.csv"),
            ("Sprint completions", str(CHANGE_LOG.relative_to(REPO)), f"{len([r for r in rows if start <= r[0] <= end])} entries in window"),
            ("User signal", str(NPS.relative_to(REPO)) if NPS.exists() else "MISSING", "undated baseline — standing context only"),
            ("New feedback", str(INBOX.relative_to(REPO)) + "/", f"{len(inbox)} new file(s)"),
            ("Open items", str(OPEN_ITEMS_FILE.relative_to(REPO)), "source for the watch bullet"),
        ],
    }

    summary = render(ctx)
    print(summary)

    if args.dry_run:
        print("\n[--dry-run] nothing written, nothing sent.", file=sys.stderr)
        return

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    out = REPORT_DIR / f"{today.isoformat()}.md"
    if out.exists():
        sys.exit(f"ERROR: {out.relative_to(REPO)} already exists. Refusing to overwrite — "
                 "move or delete it, or pass --date for a different day.")
    out.write_text(render_report(ctx, summary), encoding="utf-8")
    print(f"\n[saved] {out.relative_to(REPO)}", file=sys.stderr)

    if args.post:
        post_to_slack(summary)


if __name__ == "__main__":
    main()
