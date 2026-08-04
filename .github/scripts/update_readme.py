#!/usr/bin/env python3
"""Inject live data into README.md between HTML comment markers.

Sections written:
  banner     — NOC-style header, status line driven by the live probe
  telemetry  — health probe of the endpoints in ENDPOINTS
  activity   — recent public GitHub activity, rendered as a terminal tail
  waka       — top languages from WakaTime (skipped unless WAKATIME_API_KEY is set)

Standard library only, so the workflow needs no pip install step. Every network
call is best-effort: if an API is down the section keeps its previous content
rather than blanking the profile.
"""

from __future__ import annotations

import base64
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

USER = os.environ.get("GH_USER", "NPKpadala")
README = os.environ.get("README_PATH", "README.md")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
WAKA_KEY = os.environ.get("WAKATIME_API_KEY", "")

MAX_ROWS = 8
TIMEOUT = 20

# ─── probe targets ──────────────────────────────────────────────────────────
# Only add endpoints that are public and expected to answer. A URL that never
# resolves shows a permanent red row, which is worse than not listing it.
# Prefer a cheap /health path over a homepage: it makes the latency column mean
# something and costs the origin nothing.
#
# Third field is the health policy:
#   "strict"    — only 2xx/3xx is healthy. Right for a page a visitor loads.
#   "reachable" — any answer below 500 is healthy, 404 included. Right for an
#                 API-first host where "/" has no route: the 404 is proof the
#                 origin is up and routing, not evidence of an outage. A 5xx is
#                 still amber under this policy, because that is the service
#                 itself failing rather than a missing path.
ENDPOINTS: list[tuple[str, str, str]] = [
    ("Portfolio Website", "https://npkpadala.com", "strict"),
    ("PDFWala", "https://pdf.npkpadala.com/", "reachable"),
]

# Deliberately not probed:
#   Ops Monitor  — owner's call; the /ops surface stays off the public board.
#   Invoice API  — Render deployment not stabilised yet. Add it here when it is,
#                  and note that Render hostnames are *.onrender.com.

PROBE_TIMEOUT = 15        # Render free tiers cold-start slowly; 5s would false-alarm
PROBE_ATTEMPTS = 2        # one retry before calling anything degraded
SLOW_MS = 3000            # above this, report amber rather than green
STALE_HOURS = 6           # refresh the timestamp at most this often when nothing changed


# ─── helpers ────────────────────────────────────────────────────────────────

def fetch_json(url: str, headers: dict[str, str] | None = None):
    req = urllib.request.Request(url, headers={"User-Agent": f"{USER}-profile-bot", **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return json.load(resp)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
        print(f"warn: {url} -> {exc}", file=sys.stderr)
        return None


def replace_section(text: str, name: str, body: str) -> str:
    """Swap whatever sits between the START/END markers for `body`."""
    start, end = f"<!-- START_SECTION:{name} -->", f"<!-- END_SECTION:{name} -->"
    pattern = re.compile(f"{re.escape(start)}.*?{re.escape(end)}", re.DOTALL)
    if not pattern.search(text):
        print(f"warn: markers for '{name}' not found in {README}", file=sys.stderr)
        return text
    return pattern.sub(f"{start}\n{body}\n{end}", text)


def ago(iso: str) -> str:
    """'2026-08-04T17:31:02Z' -> '3h ago'."""
    try:
        then = datetime.strptime(iso, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        return "—"
    secs = int((datetime.now(timezone.utc) - then).total_seconds())
    for unit, size in (("d", 86400), ("h", 3600), ("m", 60)):
        if secs >= size:
            return f"{secs // size}{unit} ago"
    return "just now"


def clip(text: str, width: int) -> str:
    text = " ".join((text or "").split())
    return text if len(text) <= width else text[: width - 1] + "…"


def tail(text: str | None, width: int) -> str:
    """' · <clipped text>', or nothing at all when there is no text.

    The public events feed does not always carry a title or commit message —
    it omits them for some event types, and the first live run rendered rows
    ending in a dangling '·'. No text means no separator.
    """
    clipped = clip(text or "", width)
    return f" · {clipped}" if clipped else ""


# ─── health probe ───────────────────────────────────────────────────────────

def classify(code: int, ms: int, policy: str) -> str:
    """Map an HTTP answer to a state, according to the endpoint's policy."""
    if 200 <= code < 400:
        return "slow" if ms > SLOW_MS else "up"
    if policy == "reachable" and code < 500:
        # The origin answered and routed — it is alive, just not at this path.
        return "alive"
    return "warn"


def probe(url: str, policy: str = "strict") -> tuple[str, int | None, int | None]:
    """Return (state, http_code, latency_ms). state ∈ up | alive | slow | warn | down."""
    last_code = None
    for attempt in range(PROBE_ATTEMPTS):
        started = time.monotonic()
        req = urllib.request.Request(url, headers={"User-Agent": f"{USER}-opscheck/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=PROBE_TIMEOUT) as resp:
                ms = int((time.monotonic() - started) * 1000)
                return (classify(resp.getcode(), ms, policy), resp.getcode(), ms)
        except urllib.error.HTTPError as exc:
            # A 4xx/5xx is a real answer from a live server — worth distinguishing
            # from a connection that never completed. urllib raises rather than
            # returns these, so the status still has to be classified here.
            last_code = exc.code
            ms = int((time.monotonic() - started) * 1000)
            state = classify(exc.code, ms, policy)
            if state != "warn" or attempt == PROBE_ATTEMPTS - 1:
                return (state, exc.code, ms)
        except Exception as exc:  # noqa: BLE001 — any transport failure is "down"
            print(f"warn: probe {url} attempt {attempt + 1}: {exc}", file=sys.stderr)
        if attempt < PROBE_ATTEMPTS - 1:
            time.sleep(2)
    return ("down", last_code, None)


def probe_all() -> list[tuple[str, str, str, int | None, int | None]] | None:
    """Probe every endpoint. Returns None if the prober itself looks broken.

    If *every* target fails, the likely explanation is the runner's egress, not
    a simultaneous outage of unrelated systems. Reporting that as a wall of red
    would be worse than reporting nothing, so the caller leaves the section as-is.
    """
    if not ENDPOINTS:
        return None
    results = []
    for name, url, policy in ENDPOINTS:
        state, code, ms = probe(url, policy)
        results.append((name, url, state, code, ms))
        print(f"probe {name}: {state} code={code} ms={ms}", file=sys.stderr)
    if all(r[2] == "down" for r in results):
        print("warn: every probe failed — assuming prober fault, not outage", file=sys.stderr)
        return None
    return results


BADGE = {
    "up":    "🟢 `OPERATIONAL`",
    "alive": "🟢 `REACHABLE`",
    "slow":  "🟡 `SLOW`",
    "warn":  "🟡 `DEGRADED`",
    "down":  "🔴 `UNREACHABLE`",
}

HEALTHY = ("up", "alive")


def build_telemetry(results, current: str) -> str | None:
    """Render the health table — but only when it would actually say something new.

    The timestamp changes on every run, so writing unconditionally means an
    hourly commit forever. Instead: commit immediately when a status flips, and
    otherwise refresh the timestamp at most every STALE_HOURS.
    """
    if not results:
        return None

    signature = ",".join(f"{name}={state}" for name, _, state, _, _ in results)
    previous = re.search(r"<!-- probe:([0-9T:\-]+Z)\|([^>]*) -->", current)
    if previous and previous.group(2) == signature:
        try:
            when = datetime.strptime(previous.group(1), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            if datetime.now(timezone.utc) - when < timedelta(hours=STALE_HOURS):
                print("note: telemetry unchanged and fresh — not rewriting", file=sys.stderr)
                return None
        except ValueError:
            pass

    now = datetime.now(timezone.utc)
    rows = []
    for name, url, state, code, ms in results:
        shown = url.replace("https://", "")
        latency = f"`{ms} ms`" if ms is not None else "`—`"
        detail = f"`{code}`" if code else "`no answer`"
        rows.append(f"| **{name}** | `{shown}` | {BADGE[state]} {detail} | {latency} |")

    up = sum(1 for r in results if r[2] in HEALTHY + ("slow",))
    return "\n".join(
        [
            f"<!-- probe:{now.strftime('%Y-%m-%dT%H:%M:%SZ')}|{signature} -->",
            f"> Probed from a GitHub Actions runner · **{up}/{len(results)} operational** ·"
            f" last check `{now.strftime('%Y-%m-%d %H:%M UTC')}`",
            "",
            "| Service | Endpoint | Health | Latency |",
            "|:---|:---|:---|:---|",
            *rows,
            "",
            "<sub>Two attempts before anything is called unreachable, and a run where"
            " <em>every</em> target fails is treated as a broken prober rather than a"
            " simultaneous outage. API-first hosts are judged on reachability, so a"
            " <code>404</code> at <code>/</code> reads green — the origin answered and"
            " routed. A <code>5xx</code> does not.</sub>",
        ]
    )


def build_banner(results) -> str | None:
    """NOC-style header block. The status line is measured, never hardcoded."""
    if results:
        down = [r[0] for r in results if r[2] == "down"]
        degraded = [r[0] for r in results if r[2] in ("warn", "slow")]
        if down:
            status = f"🔴 DEGRADED — {', '.join(down)} unreachable"
        elif degraded:
            status = f"🟡 PARTIAL — {', '.join(degraded)} responding slowly"
        else:
            status = f"🟢 ALL {len(results)} MONITORED SERVICES OPERATIONAL"
    else:
        status = "⚪ NO PROBE DATA — awaiting next scheduled run"

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return "\n".join(
        [
            "```console",
            "[ OPS TELEMETRY — npkpadala ]",
            "-" * 78,
            "HOST        : Oracle Cloud Infrastructure · Oracle Linux (aarch64)",
            "RUNTIME     : PM2 process manager · Docker · nginx reverse proxy",
            "DATA        : PostgreSQL (per-tenant) · Redis · Celery workers",
            "OBSERVE     : self-built Ops Monitor · 5s host+app polling · Telegram paging",
            f"STATUS      : {status}",
            f"LAST PROBE  : {stamp}",
            "-" * 78,
            "```",
        ]
    )


# ─── activity ───────────────────────────────────────────────────────────────

REPO_COL = 18  # keeps every row aligned, and the block narrow enough for mobile


def describe(event: dict) -> str | None:
    """One terminal line per event, or None for event types not worth showing."""
    kind = event.get("type")
    repo = clip(event.get("repo", {}).get("name", "").split("/")[-1], REPO_COL).ljust(REPO_COL)
    payload = event.get("payload", {})

    if kind == "PushEvent":
        commits = payload.get("commits") or []
        if not commits:
            return None
        n = payload.get("size", len(commits))
        msg = commits[-1].get("message", "").split("\n")[0]
        return f"push    {repo} {n} commit{'s' if n != 1 else ''}{tail(msg, 44)}"
    if kind == "PullRequestEvent":
        pr = payload.get("pull_request") or {}
        action = "merged" if pr.get("merged") else payload.get("action", "")
        number = pr.get("number") or payload.get("number") or "?"
        return f"pr      {repo} #{number} {action}{tail(pr.get('title'), 40)}"
    if kind == "IssuesEvent":
        issue = payload.get("issue") or {}
        return f"issue   {repo} #{issue.get('number', '?')} {payload.get('action', '')}{tail(issue.get('title'), 38)}"
    if kind == "ReleaseEvent":
        return f"release {repo} {clip(payload.get('release', {}).get('tag_name', ''), 20)}"
    if kind == "CreateEvent":
        ref_type = payload.get("ref_type", "")
        if ref_type == "repository":
            return f"create  {repo} new repository"
        return f"create  {repo} {ref_type} {clip(payload.get('ref') or '', 26)}"
    if kind == "PublicEvent":
        return f"public  {repo} open-sourced"
    return None


def build_activity() -> str | None:
    headers = {"Accept": "application/vnd.github+json"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    events = fetch_json(f"https://api.github.com/users/{USER}/events/public?per_page=100", headers)
    if not events:
        return None

    # The API returns newest-first, but don't rely on it — the tail must read
    # top-down chronologically or the "Xh ago" column looks broken.
    events.sort(key=lambda e: e.get("created_at") or "", reverse=True)

    rows: list[str] = []
    for event in events:
        line = describe(event)
        if line:
            rows.append(f"{ago(event.get('created_at', '')):>9}  {line}")
        if len(rows) >= MAX_ROWS:
            break
    if not rows:
        return None

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    body = "\n".join(
        [
            "```console",
            f"$ npk-ops --tail activity --user {USER}",
            "",
            *rows,
            "",
            f"# stream synced {stamp} · refreshed every 6h by GitHub Actions",
            "```",
        ]
    )
    return body


# ─── wakatime (optional) ────────────────────────────────────────────────────

def build_waka() -> str | None:
    if not WAKA_KEY:
        return None
    auth = base64.b64encode(WAKA_KEY.encode()).decode()
    data = fetch_json(
        "https://wakatime.com/api/v1/users/current/stats/last_7_days",
        {"Authorization": f"Basic {auth}"},
    )
    langs = ((data or {}).get("data") or {}).get("languages") or []
    if not langs:
        return None

    rows = []
    for lang in langs[:5]:
        pct = float(lang.get("percent", 0))
        filled = round(pct / 5)  # 20-cell bar
        rows.append(f"{lang.get('name', '')[:14]:<14} {lang.get('text', ''):>16}  {'█' * filled}{'░' * (20 - filled)} {pct:5.1f}%")

    return "\n".join(["```console", "$ wakatime --last-7-days", "", *rows, "```"])


# ─── main ───────────────────────────────────────────────────────────────────

def main() -> int:
    with open(README, encoding="utf-8") as fh:
        original = fh.read()

    results = probe_all()

    updated = original

    # The banner carries the same probe timestamp as the table, so it must obey
    # the same staleness rule — rewriting it on every run would put the hourly
    # commit churn straight back.
    telemetry = build_telemetry(results, original)

    builders = (
        ("telemetry", lambda: telemetry),
        ("banner", lambda: build_banner(results) if telemetry else None),
        ("activity", build_activity),
        ("waka", build_waka),
    )
    for name, builder in builders:
        body = builder()
        if body:
            updated = replace_section(updated, name, body)
        else:
            print(f"note: leaving '{name}' section untouched", file=sys.stderr)

    if updated == original:
        print("no changes")
        return 0

    with open(README, "w", encoding="utf-8") as fh:
        fh.write(updated)
    print("README updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
