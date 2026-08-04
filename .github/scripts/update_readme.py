#!/usr/bin/env python3
"""Inject live data into README.md between HTML comment markers.

Sections written:
  activity  — recent public GitHub activity, rendered as a terminal tail
  waka      — top languages from WakaTime (skipped unless WAKATIME_API_KEY is set)

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
import urllib.error
import urllib.request
from datetime import datetime, timezone

USER = os.environ.get("GH_USER", "NPKpadala")
README = os.environ.get("README_PATH", "README.md")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
WAKA_KEY = os.environ.get("WAKATIME_API_KEY", "")

MAX_ROWS = 8
TIMEOUT = 20


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
    text = " ".join(text.split())
    return text if len(text) <= width else text[: width - 1] + "…"


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
        msg = clip(commits[-1].get("message", "").split("\n")[0], 44)
        return f"push    {repo} {n} commit{'s' if n != 1 else ''} · {msg}"
    if kind == "PullRequestEvent":
        pr = payload.get("pull_request", {})
        action = "merged" if pr.get("merged") else payload.get("action", "")
        return f"pr      {repo} #{pr.get('number')} {action} · {clip(pr.get('title', ''), 40)}"
    if kind == "IssuesEvent":
        issue = payload.get("issue", {})
        return f"issue   {repo} #{issue.get('number')} {payload.get('action', '')} · {clip(issue.get('title', ''), 38)}"
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

    updated = original
    for name, builder in (("activity", build_activity), ("waka", build_waka)):
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
