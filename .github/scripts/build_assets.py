#!/usr/bin/env python3
"""Render the profile's SVG artwork — one source, both colour themes.

The README used to lean on public image services (capsule-render, skillicons,
readme-typing-svg, streak-stats). Those rate-limit, change behaviour and
occasionally 502, which shows up as broken images on the one page recruiters
actually open. Everything visual is now generated here and committed to the
repo, so the profile renders from GitHub's own CDN and nothing else.

Writes, for each of the header and topology drawings, a `-dark` and a `-light`
file. The README picks between them with <picture media="prefers-color-scheme">.

    python .github/scripts/build_assets.py

Animation is CSS inside the SVG, which browsers run even for an <img>. Every
animated rule sits behind `prefers-reduced-motion: no-preference`, so the
drawings hold a sensible static pose for anyone who asked the OS for less
movement — and that same static pose is what a non-animating renderer shows.
"""

from __future__ import annotations

import os

OUT_DIR = os.environ.get("ASSET_DIR", "assets")

# ─── palette ────────────────────────────────────────────────────────────────
# Green stays — it is the identity — but at GitHub's own success-green rather
# than #39FF14. Neon on near-black is what made the old header read as a
# template; this is the same hue with the glare taken out.
THEMES = {
    "dark": {
        "bg": "#0D1117",
        "panel": "#161B22",
        "border": "#30363D",
        "grid": "#21262D",
        "text": "#E6EDF3",
        "muted": "#8B949E",
        "accent": "#3FB950",
        "accent2": "#58A6FF",
    },
    "light": {
        "bg": "#FFFFFF",
        "panel": "#F6F8FA",
        "border": "#D0D7DE",
        "grid": "#E4E8ED",
        "text": "#1F2328",
        "muted": "#59636E",
        "accent": "#1A7F37",
        "accent2": "#0969DA",
    },
}

SANS = "ui-sans-serif,-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"

# ─── header ─────────────────────────────────────────────────────────────────

NAME = "Praveen Kumar Padala"
ROLE = "Infrastructure Operations & Systems Engineer"

# Typed in sequence, one at a time, forever. Keep them short: the clip width is
# derived from the character count, so a long line runs off the card.
PHRASES = [
    "provision  ·  harden  ·  monitor  ·  restore",
    "if it runs in production, I carry the pager",
    "observability I built, not bought",
]

TYPE_X = 46          # left edge of the typed line
TYPE_Y = 150         # baseline
CHAR_W = 8.4         # advance width of the 14px mono face, near enough
PROMPT = "$ "


def header(theme: dict[str, str]) -> str:
    cycle = len(PHRASES) * 5.0            # 5s of screen time per phrase
    prompt_w = len(PROMPT) * CHAR_W
    text_x = TYPE_X + prompt_w

    css_rules: list[str] = []
    groups: list[str] = []

    for i, phrase in enumerate(PHRASES):
        width = len(phrase) * CHAR_W
        delay = i * 5.0
        # Reveal is a clip rect slid in from the left — a plain translate, no
        # reliance on CSS geometry properties or transform-box support.
        css_rules.append(
            f"@keyframes reveal{i}{{"
            f"0%,{100 * delay / cycle:.4f}%{{transform:translateX({-width:.1f}px)}}"
            f"{100 * (delay + 1.1) / cycle:.4f}%,{100 * (delay + 4.6) / cycle:.4f}%{{transform:translateX(0)}}"
            f"{100 * (delay + 4.7) / cycle:.4f}%,100%{{transform:translateX({-width:.1f}px)}}}}"
            f"@keyframes caret{i}{{"
            f"0%,{100 * delay / cycle:.4f}%{{transform:translateX(0);opacity:0}}"
            f"{100 * (delay + 0.05) / cycle:.4f}%{{transform:translateX(0);opacity:1}}"
            f"{100 * (delay + 1.1) / cycle:.4f}%,{100 * (delay + 4.6) / cycle:.4f}%{{transform:translateX({width:.1f}px);opacity:1}}"
            f"{100 * (delay + 4.7) / cycle:.4f}%,100%{{transform:translateX({width:.1f}px);opacity:0}}}}"
            f".clip{i} rect{{animation:reveal{i} {cycle:.0f}s steps({len(phrase)},end) infinite}}"
            f".caret{i}{{animation:caret{i} {cycle:.0f}s steps({len(phrase)},end) infinite}}"
        )
        # Static pose — what reduced-motion users and non-animating renderers
        # see: the first phrase fully typed, the rest clipped away. Without
        # this the three lines stack on top of each other. CSS animations
        # override presentation attributes, so the moving version is unaffected.
        caret_rest = f' transform="translate({width:.1f},0)"' if i == 0 else ""
        groups.append(
            f'    <g clip-path="url(#clip{i})">'
            f'<text x="{text_x:.1f}" y="{TYPE_Y}" class="typed">{esc(phrase)}</text></g>\n'
            f'    <rect class="caret caret{i}" x="{text_x:.1f}" y="{TYPE_Y - 12}" width="8" height="16"'
            f'{caret_rest}/>'
        )
        css_rules.append("")

    clip_parts = []
    for i, phrase in enumerate(PHRASES):
        width = len(phrase) * CHAR_W
        offset = "" if i == 0 else ' transform="translate({:.1f},0)"'.format(-width)
        clip_parts.append(
            f'    <clipPath id="clip{i}" class="clip{i}">'
            f'<rect x="{text_x:.1f}" y="{TYPE_Y - 16}" width="{width:.1f}" height="24"{offset}/>'
            f'</clipPath>'
        )
    clips = "\n".join(clip_parts)

    # Right-hand motif: a load trace that draws itself and a probe dot that
    # walks it. Abstract on purpose — it is decoration, not a metric, and a
    # header should never imply numbers it cannot back up.
    trace = (
        "M 596 132 L 622 124 L 648 136 L 674 96 L 700 108 L 726 72 "
        "L 752 88 L 778 58 L 804 74 L 830 44 L 856 56"
    )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 200" width="900" height="200" role="img" aria-label="{esc(NAME)} — {esc(ROLE)}">
  <title>{esc(NAME)} — {esc(ROLE)}</title>
  <defs>
{clips}
    <linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="{theme['accent']}" stop-opacity="0"/>
      <stop offset="45%" stop-color="{theme['accent']}"/>
      <stop offset="75%" stop-color="{theme['accent2']}"/>
      <stop offset="100%" stop-color="{theme['accent2']}" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="fade" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{theme['accent']}" stop-opacity="0.22"/>
      <stop offset="100%" stop-color="{theme['accent']}" stop-opacity="0"/>
    </linearGradient>
    <clipPath id="card"><rect x="1" y="1" width="898" height="198" rx="14"/></clipPath>
  </defs>
  <style>
    .name {{ font: 600 34px {SANS}; fill: {theme['text']}; letter-spacing: -0.4px }}
    .role {{ font: 400 16px {SANS}; fill: {theme['muted']} }}
    .kicker {{ font: 500 11px {MONO}; fill: {theme['accent']}; letter-spacing: 2.4px }}
    .typed {{ font: 400 14px {MONO}; fill: {theme['text']} }}
    .prompt {{ font: 400 14px {MONO}; fill: {theme['accent']} }}
    .caret {{ fill: {theme['accent']}; opacity: 0 }}
    .caret0 {{ opacity: 1 }}
    .trace {{ fill: none; stroke: {theme['accent']}; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round }}
    .probe {{ fill: {theme['accent2']} }}
    .dim {{ opacity: 0 }}
    @media (prefers-reduced-motion: no-preference) {{
      {" ".join(css_rules)}
      @keyframes draw {{ 0% {{ stroke-dashoffset: 700 }} 45%,100% {{ stroke-dashoffset: 0 }} }}
      @keyframes glide {{ 0% {{ opacity: 0 }} 8%,92% {{ opacity: 1 }} 100% {{ opacity: 0 }} }}
      @keyframes slide {{ 0% {{ transform: translateX(-320px) }} 100% {{ transform: translateX(900px) }} }}
      .trace {{ stroke-dasharray: 700; animation: draw 6s ease-in-out infinite }}
      .probe {{ animation: glide 6s linear infinite }}
      .rail {{ animation: slide 6s linear infinite }}
      .dim {{ opacity: 1 }}
    }}
  </style>

  <rect x="1" y="1" width="898" height="198" rx="14" fill="{theme['bg']}" stroke="{theme['border']}"/>
  <g clip-path="url(#card)">
    <rect class="rail" x="0" y="1" width="320" height="2" fill="url(#sweep)"/>
    <rect x="0" y="0" width="900" height="200" fill="url(#fade)" opacity="0.35"/>
  </g>

  <text class="kicker" x="46" y="52">OPS · AUTOMATION · RELIABILITY</text>
  <text class="name" x="44" y="94">{esc(NAME)}</text>
  <text class="role" x="46" y="120">{esc(ROLE)}</text>

  <g>
    <text class="prompt" x="{TYPE_X}" y="{TYPE_Y}">{esc(PROMPT)}</text>
{chr(10).join(groups)}
  </g>

  <g transform="translate(0,10)">
    <path class="trace" d="{trace}"/>
    <circle class="probe dim" r="4">
      <animateMotion dur="6s" repeatCount="indefinite" path="{trace}" keyPoints="0;1" keyTimes="0;1" calcMode="linear"/>
    </circle>
  </g>
</svg>
"""


# ─── topology ───────────────────────────────────────────────────────────────

STAGES = [
    ("EDGE", ["nginx · TLS", "rate limits"]),
    ("APP TIER", ["FastAPI · Flask", "Node · Gunicorn · PM2"]),
    ("ASYNC", ["Celery workers", "Redis broker"]),
    ("DATA", ["PostgreSQL per tenant", "verified nightly dumps"]),
]

WATCH = ["collector — 5s host + app", "ingest API", "threshold eval", "Telegram page · live dashboard"]


def topology(theme: dict[str, str]) -> str:
    box_w, box_h, gap = 186, 84, 24
    left, top = 20, 44
    boxes: list[str] = []
    links: list[str] = []
    feeds: list[str] = []

    for i, (title, lines) in enumerate(STAGES):
        x = left + i * (box_w + gap)
        boxes.append(
            f'  <g>\n'
            f'    <rect x="{x}" y="{top}" width="{box_w}" height="{box_h}" rx="10" fill="{theme["panel"]}" stroke="{theme["border"]}"/>\n'
            f'    <text class="h" x="{x + 16}" y="{top + 28}">{esc(title)}</text>\n'
            + "".join(
                f'    <text class="s" x="{x + 16}" y="{top + 50 + j * 17}">{esc(line)}</text>\n'
                for j, line in enumerate(lines)
            )
            + "  </g>"
        )
        if i < len(STAGES) - 1:
            x0, x1, y = x + box_w, x + box_w + gap, top + box_h / 2
            links.append(
                f'  <path id="link{i}" class="link" d="M {x0} {y} H {x1 - 6}"/>\n'
                f'  <path class="head" d="M {x1 - 8} {y - 4} l 6 4 l -6 4 z"/>\n'
                f'  <circle class="pkt" r="3">\n'
                f'    <animateMotion dur="2.6s" begin="{i * 0.45:.2f}s" repeatCount="indefinite" path="M {x0} {y} H {x1 - 6}"/>\n'
                f'  </circle>'
            )
        # every stage is watched — dashed drop line into the observability panel
        feeds.append(
            f'  <path class="feed" d="M {x + box_w / 2} {top + box_h} V 196"/>'
        )

    watch_x = left
    watch_w = 4 * box_w + 3 * gap
    stage_w = watch_w / len(WATCH)
    watch_stages = "".join(
        f'    <text class="s" x="{watch_x + stage_w * i + stage_w / 2:.0f}" y="232" text-anchor="middle">{esc(label)}</text>\n'
        + (
            f'    <path class="link" d="M {watch_x + stage_w * (i + 1) - 14:.0f} 227 h 10"/>\n'
            f'    <path class="head" d="M {watch_x + stage_w * (i + 1) - 6:.0f} 223 l 6 4 l -6 4 z"/>\n'
            if i < len(WATCH) - 1
            else ""
        )
        for i, label in enumerate(WATCH)
    )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 860 270" width="860" height="270" role="img" aria-label="Production topology: edge, app tier, async workers and data, all watched by a self-built observability loop">
  <title>Production topology</title>
  <style>
    .h {{ font: 600 13px {SANS}; fill: {theme['text']}; letter-spacing: 0.6px }}
    .s {{ font: 400 12px {SANS}; fill: {theme['muted']} }}
    .cap {{ font: 500 11px {MONO}; fill: {theme['accent']}; letter-spacing: 1.8px }}
    .link {{ fill: none; stroke: {theme['border']}; stroke-width: 1.5 }}
    .head {{ fill: {theme['border']} }}
    .feed {{ fill: none; stroke: {theme['grid']}; stroke-width: 1.5; stroke-dasharray: 3 5 }}
    .pkt {{ fill: {theme['accent']}; opacity: 0 }}
    .loop {{ fill: none; stroke: {theme['accent']}; stroke-width: 1.5; opacity: 0.5 }}
    @media (prefers-reduced-motion: no-preference) {{
      @keyframes blip {{ 0% {{ opacity: 0 }} 12%,88% {{ opacity: 1 }} 100% {{ opacity: 0 }} }}
      @keyframes march {{ to {{ stroke-dashoffset: -16 }} }}
      .pkt {{ animation: blip 2.6s linear infinite }}
      .feed {{ animation: march 1.4s linear infinite }}
    }}
  </style>

  <rect x="0.5" y="0.5" width="859" height="269" rx="12" fill="{theme['bg']}" stroke="{theme['border']}"/>
  <text class="cap" x="20" y="26">REQUEST PATH</text>

{chr(10).join(boxes)}

{chr(10).join(links)}

{chr(10).join(feeds)}

  <g>
    <rect x="{left}" y="196" width="{watch_w}" height="52" rx="10" fill="{theme['panel']}" stroke="{theme['border']}"/>
    <text class="cap" x="{left + 16}" y="214">OBSERVABILITY LOOP · SELF-BUILT</text>
{watch_stages}  </g>
</svg>
"""


def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main() -> int:
    os.makedirs(OUT_DIR, exist_ok=True)
    for name, render in (("header", header), ("topology", topology)):
        for theme_name, theme in THEMES.items():
            path = os.path.join(OUT_DIR, f"{name}-{theme_name}.svg")
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(render(theme))
            print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
