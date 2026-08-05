#!/usr/bin/env python3
"""Render the profile's SVG artwork — one source, both colour themes.

The README used to lean on public image services (capsule-render, skillicons,
readme-typing-svg, streak-stats). Those rate-limit, change behaviour and
occasionally 502, which shows up as broken images on the one page recruiters
actually open. Everything visual is generated here and committed to the repo,
so the profile renders from GitHub's own CDN and nothing else.

    python .github/scripts/build_assets.py
    python .github/scripts/build_assets.py --preview 5   # freeze act 5, dark theme

Writes a `-dark` and a `-light` file for each drawing. The README picks between
them with <picture media="prefers-color-scheme">.

WHY PURE SVG, AND NOT REACT / FRAMER MOTION / GSAP
--------------------------------------------------
A GitHub README renders images through a proxy as <img>, where no JavaScript
runs — a React hero cannot execute there at any level of effort. So the hero
below is CSS keyframes and SMIL inside a single self-contained SVG, which
browsers *do* animate inside an <img>. The one thing the JS version has that
this cannot is pointer parallax; everything else survives. (For npkpadala.com,
where scripts do run, the React build is the right call.)

Every animated rule sits behind `prefers-reduced-motion: no-preference`, so the
artwork holds a readable static pose — act 1, fully composed — for anyone who
asked the OS for less movement, and that same pose is what a non-animating
renderer shows.
"""

from __future__ import annotations

import os
import sys

OUT_DIR = os.environ.get("ASSET_DIR", "assets")

# ─── palette ────────────────────────────────────────────────────────────────
# Green stays — it is the identity — but at GitHub's own success-green rather
# than #39FF14. Blue leads the hero, cyan carries motion, green means "passed".
THEMES = {
    "dark": {
        "bg": "#0D1117",
        "panel": "#161B22",
        "sunk": "#0B0F15",
        "border": "#30363D",
        "grid": "#21262D",
        "text": "#E6EDF3",
        "muted": "#8B949E",
        "accent": "#3FB950",
        "accent2": "#58A6FF",
        "blue": "#3B82F6",
        "cyan": "#2DD4BF",
        "warn": "#D29922",
    },
    "light": {
        "bg": "#FFFFFF",
        "panel": "#F6F8FA",
        "sunk": "#FFFFFF",
        "border": "#D0D7DE",
        "grid": "#E4E8ED",
        "text": "#1F2328",
        "muted": "#59636E",
        "accent": "#1A7F37",
        "accent2": "#0969DA",
        "blue": "#1F6FEB",
        "cyan": "#0E7490",
        "warn": "#9A6700",
    },
}

SANS = "ui-sans-serif,-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"

NAME = "Praveen Kumar Padala"
ROLE = "Infrastructure Operations & Systems Engineer"
KICKER = "OPS · AUTOMATION · AI IN THE LOOP"

PHRASES = [
    "provision  ·  harden  ·  monitor  ·  restore",
    "if it runs in production, I carry the pager",
    "putting AI to work inside the ops loop",
]

TYPE_X = 46
TYPE_Y = 168
CHAR_W = 8.4
PROMPT = "$ "

# ─── hero timeline ──────────────────────────────────────────────────────────
# One clock for the whole drawing: every keyframe below is a percentage of this
# cycle, so acts and the effects inside them stay in sync without a scheduler.
CYCLE = 16.0
ACTS = [
    "IDEA",
    "BLUEPRINT",
    "CODE",
    "TEST",
    "LAUNCH",
    "ORBIT",
    "REAL USERS",
    "GROWTH",
]
ACT_LEN = CYCLE / len(ACTS)          # 2s an act
FADE = 0.3                            # cross-fade between acts

# Hero panel, in header coordinates. The scene is drawn in local coordinates
# around (CX, CY) so each act can be written as if it owned the origin.
PX, PY, PW, PH = 548, 24, 328, 172
CX, CY = PX + PW / 2, PY + 68
SCENE_TOP, SCENE_H = PY + 1, 136


def pct(t: float) -> float:
    return max(0.0, min(100.0, 100.0 * t / CYCLE))


def kf(name: str, stops: list[tuple[float, str]]) -> str:
    """A keyframes rule from (seconds, declarations) pairs.

    Anchored at 0% and 100% with the first stop's value. Without those anchors
    a browser interpolates from the element's base value across the whole cycle,
    which leaves orbiting particles and progress bars mid-flight when their act
    opens.
    """
    stops = sorted(stops, key=lambda s: s[0])
    if stops[0][0] > 0:
        stops = [(0.0, stops[0][1])] + stops
    if stops[-1][0] < CYCLE:
        stops = stops + [(CYCLE, stops[-1][1])]
    body = "".join("%.3f%%{%s}" % (pct(t), decl) for t, decl in stops)
    return "@keyframes %s{%s}" % (name, body)


def anim(selector: str, name: str, easing: str = "linear") -> str:
    return "%s{animation:%s %.0fs %s infinite}" % (selector, name, CYCLE, easing)


def act_window(i: int) -> tuple[float, float]:
    return i * ACT_LEN, (i + 1) * ACT_LEN


def act_visibility(i: int) -> tuple[str, str]:
    """Fade/scale an act in and out of its slot.

    Act 0 is special: it is on screen at t=0, so its fade-in has to happen at
    the tail of the cycle instead of the head, or the loop blinks on rewind.
    """
    s, e = act_window(i)
    on = "opacity:1;transform:translateY(0) scale(1)"
    below = "opacity:0;transform:translateY(7px) scale(.94)"
    above = "opacity:0;transform:translateY(-7px) scale(1.05)"
    if i == 0:
        stops = [
            (0.0, on),
            (e - FADE * 1.2, on),
            (e - FADE * 0.2, above),
            (CYCLE - FADE * 1.4, below),
            (CYCLE, on),
        ]
    else:
        stops = [
            (0.0, below),
            (s - FADE * 0.6, below),
            (s + FADE * 0.6, on),
            (e - FADE * 1.2, on),
            (e - FADE * 0.2, above),
            (CYCLE, above),
        ]
    name = "act%d" % i
    return kf(name, stops), anim(".act%d" % i, name, "cubic-bezier(.4,0,.2,1)")


def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ─── act 1 · idea ───────────────────────────────────────────────────────────

def act_idea(i: int, T: dict[str, str]) -> tuple[str, list[str]]:
    s, e = act_window(i)
    css = [
        kf("bulbGlow", [
            (s, "opacity:.18;transform:scale(.8)"),
            (s + 0.55, "opacity:.5;transform:scale(1.06)"),
            (s + 1.1, "opacity:.22;transform:scale(.88)"),
            (s + 1.65, "opacity:.46;transform:scale(1.04)"),
            (e, "opacity:.24;transform:scale(.9)"),
        ]),
        anim(".bulb-glow", "bulbGlow", "ease-in-out"),
        kf("filament", [
            (s, "opacity:.35"), (s + 0.5, "opacity:1"),
            (s + 1.0, "opacity:.5"), (s + 1.5, "opacity:1"), (e, "opacity:.7"),
        ]),
        anim(".filament", "filament", "ease-in-out"),
    ]
    # Two energy pulses per act, offset so the bulb reads as emitting.
    rings = []
    for k, offset in enumerate((0.35, 1.15)):
        name = "pulse%d" % k
        css.append(kf(name, [
            (s + offset, "opacity:.55;transform:scale(.55)"),
            (s + offset + 0.85, "opacity:0;transform:scale(2.1)"),
        ]))
        css.append(anim(".pulse%d" % k, name, "cubic-bezier(.2,.6,.3,1)"))
        rings.append(
            f'      <circle class="pulse{k}" r="20" fill="none" stroke="{T["cyan"]}" stroke-width="1.2" opacity="0"/>'
        )

    # Orbiting particles: SMIL motion is the reliable way to walk a path inside
    # an <img>, and an orbit is stateless, so it needs no timeline sync.
    orbits = []
    for k, (rx, ry, dur, colour, r) in enumerate((
        (44, 20, 3.4, T["cyan"], 2.0),
        (34, 30, 4.6, T["blue"], 1.6),
        (52, 26, 5.8, T["accent"], 1.4),
    )):
        path = f"M {-rx} 0 A {rx} {ry} 0 1 0 {rx} 0 A {rx} {ry} 0 1 0 {-rx} 0"
        orbits.append(
            f'      <g opacity="{0.9 - k * 0.15:.2f}">'
            f'<circle r="{r}" fill="{colour}">'
            f'<animateMotion dur="{dur}s" repeatCount="indefinite" path="{path}"/>'
            f"</circle></g>"
        )

    markup = f"""  <g class="act act0">
    <g transform="translate({CX},{CY})">
      <circle class="bulb-glow" r="34" fill="url(#ideaGlow)"/>
{chr(10).join(rings)}
      <path d="M 0 -26 a 19 19 0 0 1 11 34 v 6 h -22 v -6 a 19 19 0 0 1 11 -34 z"
            fill="{T['sunk']}" stroke="{T['cyan']}" stroke-width="1.6" stroke-linejoin="round"/>
      <path class="filament" d="M -7 6 C -5 -6, -2 -6, 0 2 C 2 -6, 5 -6, 7 6"
            fill="none" stroke="{T['accent']}" stroke-width="1.6" stroke-linecap="round"/>
      <rect x="-8" y="16" width="16" height="4" rx="1.4" fill="{T['muted']}"/>
      <rect x="-6" y="21" width="12" height="3" rx="1.4" fill="{T['muted']}" opacity=".7"/>
{chr(10).join(orbits)}
    </g>
  </g>"""
    return markup, css


# ─── act 2 · blueprint ──────────────────────────────────────────────────────

BP_NODES = [(-62, -18), (-16, -34), (-16, 6), (34, -20), (34, 20), (74, 0)]
BP_EDGES = [(0, 1), (0, 2), (1, 3), (2, 4), (3, 5), (4, 5), (1, 2)]


def act_blueprint(i: int, T: dict[str, str]) -> tuple[str, list[str]]:
    s, e = act_window(i)
    css = [
        kf("bpTilt", [
            (s, "transform:rotate(-3.5deg)"),
            (s + 1.0, "transform:rotate(3.5deg)"),
            (e, "transform:rotate(-2deg)"),
        ]),
        anim(".bp-tilt", "bpTilt", "ease-in-out"),
        kf("bpGrid", [(s, "stroke-dashoffset:120"), (s + 0.75, "stroke-dashoffset:0"), (e, "stroke-dashoffset:0")]),
        anim(".bp-grid line", "bpGrid", "ease-out"),
    ]

    grid = []
    for gx in range(-90, 91, 30):
        grid.append(f'        <line x1="{gx}" y1="-46" x2="{gx}" y2="46"/>')
    for gy in range(-46, 47, 23):
        grid.append(f'        <line x1="-90" y1="{gy}" x2="90" y2="{gy}"/>')

    edges = []
    for k, (a, b) in enumerate(BP_EDGES):
        (x1, y1), (x2, y2) = BP_NODES[a], BP_NODES[b]
        name = "bpEdge%d" % k
        start = s + 0.35 + k * 0.09
        css.append(kf(name, [
            (start, "stroke-dashoffset:110;opacity:.2"),
            (start + 0.45, "stroke-dashoffset:0;opacity:1"),
            (e, "stroke-dashoffset:0;opacity:1"),
        ]))
        css.append(anim(".bp-edge%d" % k, name, "ease-out"))
        edges.append(
            f'        <line class="bp-edge bp-edge{k}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>'
        )

    nodes = []
    for k, (nx, ny) in enumerate(BP_NODES):
        name = "bpNode%d" % k
        start = s + 0.55 + k * 0.1
        css.append(kf(name, [
            (start, "opacity:0;transform:scale(.2)"),
            (start + 0.3, "opacity:1;transform:scale(1)"),
            (e, "opacity:1;transform:scale(1)"),
        ]))
        css.append(anim(".bp-node%d" % k, name, "cubic-bezier(.2,1.4,.4,1)"))
        nodes.append(
            f'        <g class="bp-node bp-node{k}" transform="translate({nx},{ny})">'
            f'<circle r="5.5" fill="{T["sunk"]}" stroke="{T["blue"]}" stroke-width="1.6"/>'
            f'<circle r="2" fill="{T["cyan"]}"/></g>'
        )

    return f"""  <g class="act act1">
    <g transform="translate({CX},{CY})">
      <g class="bp-tilt">
        <g class="bp-grid" stroke="{T['grid']}" stroke-width="1" stroke-dasharray="120">
{chr(10).join(grid)}
        </g>
        <g class="bp-edges" stroke="{T['blue']}" stroke-width="1.4" stroke-dasharray="110" opacity=".85">
{chr(10).join(edges)}
        </g>
{chr(10).join(nodes)}
      </g>
    </g>
  </g>""", css


# ─── act 3 · code ───────────────────────────────────────────────────────────
# Real TypeScript — the probe loop this profile actually runs, shortened to fit.
CODE_LINES: list[list[tuple[str, str]]] = [
    [("export", "k"), (" ", "p"), ("async", "k"), (" ", "p"), ("function", "k"),
     (" ", "p"), ("probe", "f"), ("(", "p"), ("url", "v"), (": ", "p"), ("string", "t"), (") {", "p")],
    [("  const", "k"), (" started ", "v"), ("= ", "p"), ("performance", "f"), (".", "p"), ("now", "f"), ("();", "p")],
    [("  const", "k"), (" res ", "v"), ("= ", "p"), ("await", "k"), (" ", "p"), ("fetch", "f"),
     ("(url, { signal });", "p")],
    [("  return", "k"), (" { ok", "v"), (": res.ok, ", "p"), ("ms", "v"), (": elapsed(started) };", "p")],
    [("}", "p")],
]
CODE_CHAR = 4.8   # 8px mono advances 0.6em; the clip width is derived from it


def act_code(i: int, T: dict[str, str]) -> tuple[str, list[str]]:
    s, e = act_window(i)
    css: list[str] = []
    lines, clips = [], []
    left, top, step = -116, -30, 15

    for n, tokens in enumerate(CODE_LINES):
        plain = "".join(t for t, _ in tokens)
        width = len(plain) * CODE_CHAR
        start = s + 0.3 + n * 0.24
        name = "type%d" % n
        css.append(kf(name, [
            (start, "transform:translateX(%.1fpx)" % -width),
            (start + 0.32, "transform:translateX(0)"),
            (e, "transform:translateX(0)"),
        ]))
        css.append("%s{animation:%s %.0fs steps(%d,end) infinite}" % (".code-clip%d rect" % n, name, CYCLE, max(len(plain), 1)))
        clips.append(
            f'    <clipPath id="codeClip{n}" class="code-clip{n}">'
            f'<rect x="{left}" y="{top + n * step - 9}" width="{width:.1f}" height="13"/></clipPath>'
        )
        spans = "".join(f'<tspan class="c-{cls}">{esc(text)}</tspan>' for text, cls in tokens)
        # xml:space="preserve" or the spaces between tspans collapse away and the
        # line renders as "exportasyncfunctionprobe".
        lines.append(
            f'        <g clip-path="url(#codeClip{n})">'
            f'<text class="code" xml:space="preserve" x="{left}" y="{top + n * step}">{spans}</text></g>'
        )

    # Caret parks at the end of the last typed line and blinks.
    last_w = len("".join(t for t, _ in CODE_LINES[-1])) * CODE_CHAR
    css.append(kf("caretBlink", [
        (s + 1.4, "opacity:1"), (s + 1.65, "opacity:0"), (s + 1.9, "opacity:1"), (e, "opacity:0"),
    ]))
    css.append(anim(".code-caret", "caretBlink", "steps(1,end)"))

    return f"""  <g class="act act2">
    <defs>
{chr(10).join(clips)}
    </defs>
    <g transform="translate({CX},{CY})">
      <rect x="-132" y="-56" width="264" height="112" rx="9" fill="{T['sunk']}" stroke="{T['border']}"/>
      <line x1="-132" y1="-38" x2="132" y2="-38" stroke="{T['border']}"/>
      <circle cx="-118" cy="-47" r="2.6" fill="{T['muted']}" opacity=".55"/>
      <circle cx="-109" cy="-47" r="2.6" fill="{T['muted']}" opacity=".4"/>
      <circle cx="-100" cy="-47" r="2.6" fill="{T['muted']}" opacity=".25"/>
      <text class="code-file" x="-88" y="-44">probe.ts</text>
      <g>
{chr(10).join(lines)}
        <rect class="code-caret" x="{left + last_w:.1f}" y="{top + (len(CODE_LINES) - 1) * step - 8}"
              width="5" height="11" fill="{T['cyan']}" opacity="0"/>
      </g>
    </g>
  </g>""", css


# ─── act 4 · test ───────────────────────────────────────────────────────────

CHECKS = ["Unit tests", "Integration tests", "Security scan"]


def act_test(i: int, T: dict[str, str]) -> tuple[str, list[str]]:
    s, e = act_window(i)
    css = [
        kf("runFade", [(s + 0.15, "opacity:0"), (s + 0.4, "opacity:1"), (e, "opacity:1")]),
        anim(".run-line", "runFade", "ease-out"),
    ]
    rows = []
    for n, label in enumerate(CHECKS):
        y = -18 + n * 24
        start = s + 0.45 + n * 0.4
        css += [
            kf("bar%d" % n, [
                (start, "stroke-dashoffset:92"),
                (start + 0.34, "stroke-dashoffset:0"),
                (e, "stroke-dashoffset:0"),
            ]),
            anim(".bar%d" % n, "bar%d" % n, "cubic-bezier(.3,.7,.4,1)"),
            kf("tick%d" % n, [
                (start + 0.3, "stroke-dashoffset:18;opacity:0"),
                (start + 0.36, "opacity:1"),
                (start + 0.62, "stroke-dashoffset:0;opacity:1"),
                (e, "stroke-dashoffset:0;opacity:1"),
            ]),
            anim(".tick%d" % n, "tick%d" % n, "ease-out"),
            kf("row%d" % n, [(start - 0.1, "opacity:0"), (start + 0.2, "opacity:1"), (e, "opacity:1")]),
            anim(".row%d" % n, "row%d" % n, "ease-out"),
        ]
        rows.append(
            f'      <g class="row{n}" opacity="0">'
            f'<text class="mono-s" x="-100" y="{y + 3}">{esc(label)}</text>'
            f'<line x1="20" y1="{y}" x2="112" y2="{y}" stroke="{T["grid"]}" stroke-width="4" stroke-linecap="round"/>'
            f'<line class="bar{n}" x1="20" y1="{y}" x2="112" y2="{y}" stroke="{T["accent"]}" stroke-width="4"'
            f' stroke-linecap="round" stroke-dasharray="92" stroke-dashoffset="92"/>'
            f'<path class="tick{n}" d="M -118 {y} l 3.5 4 l 7 -9" fill="none" stroke="{T["accent"]}"'
            f' stroke-width="2" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="18"'
            f' stroke-dashoffset="18" opacity="0"/>'
            f"</g>"
        )

    css += [
        kf("allGreen", [(s + 1.65, "opacity:0"), (s + 1.85, "opacity:1"), (e, "opacity:1")]),
        anim(".all-green", "allGreen", "ease-out"),
    ]

    return f"""  <g class="act act3">
    <g transform="translate({CX},{CY})">
      <rect x="-132" y="-56" width="264" height="112" rx="9" fill="{T['sunk']}" stroke="{T['border']}"/>
      <text class="run-line" x="-118" y="-36" opacity="0"><tspan class="c-p">$</tspan> npm test — running suites…</text>
{chr(10).join(rows)}
      <text class="all-green" x="-118" y="46" opacity="0">all checks passed</text>
    </g>
  </g>""", css


# ─── act 5 · launch ─────────────────────────────────────────────────────────

def act_launch(i: int, T: dict[str, str]) -> tuple[str, list[str]]:
    s, e = act_window(i)
    css: list[str] = []

    counts = []
    for n, glyph in enumerate(("3", "2", "1")):
        name = "count%d" % n
        start = s + 0.1 + n * 0.26
        css += [
            kf(name, [
                (start, "opacity:0;transform:scale(1.5)"),
                (start + 0.1, "opacity:.9;transform:scale(1)"),
                (start + 0.24, "opacity:0;transform:scale(.85)"),
                (e, "opacity:0;transform:scale(.85)"),
            ]),
            anim(".count%d" % n, name, "ease-out"),
        ]
        counts.append(f'      <text class="count count{n}" x="0" y="-34" opacity="0">{glyph}</text>')

    css += [
        # Hold on the pad, shudder, then leave. Ease-in on the climb is what
        # makes it read as thrust rather than a slide.
        kf("rocketRun", [
            (s, "transform:translateY(0)"),
            (s + 0.95, "transform:translateY(0)"),
            (s + 1.05, "transform:translateY(-6px)"),
            (e - 0.05, "transform:translateY(-190px)"),
            (e, "transform:translateY(-190px)"),
        ]),
        ".rocket{animation:rocketRun %.0fs cubic-bezier(.55,0,.9,.35) infinite}" % CYCLE,
        kf("shudder", [
            (s + 0.55, "transform:translateX(0)"),
            (s + 0.62, "transform:translateX(1.1px)"),
            (s + 0.69, "transform:translateX(-1.1px)"),
            (s + 0.76, "transform:translateX(.9px)"),
            (s + 0.83, "transform:translateX(-.9px)"),
            (s + 0.9, "transform:translateX(.6px)"),
            (s + 0.97, "transform:translateX(0)"),
            (e, "transform:translateX(0)"),
        ]),
        anim(".shudder", "shudder", "steps(1,end)"),
        kf("flame", [
            (s + 0.5, "opacity:0;transform:scaleY(.2)"),
            (s + 0.72, "opacity:1;transform:scaleY(.75)"),
            (s + 0.84, "opacity:.85;transform:scaleY(1.15)"),
            (s + 0.96, "opacity:1;transform:scaleY(.9)"),
            (s + 1.1, "opacity:1;transform:scaleY(1.35)"),
            (e - 0.1, "opacity:1;transform:scaleY(1.1)"),
            (e, "opacity:0;transform:scaleY(.6)"),
        ]),
        anim(".flame", "flame", "ease-in-out"),
        kf("trail", [
            (s + 1.0, "opacity:0;transform:scaleY(0)"),
            (s + 1.25, "opacity:.55;transform:scaleY(1)"),
            (e - 0.15, "opacity:.25;transform:scaleY(1)"),
            (e, "opacity:0;transform:scaleY(1)"),
        ]),
        anim(".trail", "trail", "ease-out"),
        kf("padGlow", [
            (s + 0.6, "opacity:0"), (s + 1.0, "opacity:.5"), (s + 1.6, "opacity:0"), (e, "opacity:0"),
        ]),
        anim(".pad-glow", "padGlow", "ease-out"),
    ]

    smoke = []
    for n, (dx, dr, delay) in enumerate(((-16, 12, 0.0), (14, 14, 0.12), (-28, 9, 0.22), (26, 10, 0.3))):
        name = "smoke%d" % n
        start = s + 0.95 + delay
        css += [
            kf(name, [
                (start, "opacity:0;transform:translate(0,0) scale(.3)"),
                (start + 0.2, "opacity:.35;transform:translate(%dpx,-2px) scale(.8)" % (dx // 2)),
                (start + 0.85, "opacity:0;transform:translate(%dpx,-8px) scale(1.9)" % dx),
                (e, "opacity:0;transform:translate(%dpx,-8px) scale(1.9)" % dx),
            ]),
            anim(".smoke%d" % n, name, "ease-out"),
        ]
        smoke.append(f'      <circle class="smoke{n}" cx="0" cy="46" r="{dr}" fill="{T["muted"]}" opacity="0"/>')

    return f"""  <g class="act act4">
    <g transform="translate({CX},{CY})">
      <ellipse class="pad-glow" cx="0" cy="48" rx="46" ry="9" fill="url(#flameGlow)" opacity="0"/>
{chr(10).join(smoke)}
      <rect class="trail" x="-2.5" y="-16" width="5" height="70" rx="2.5" fill="url(#trailGrad)" opacity="0"/>
      <g class="rocket">
        <g class="shudder" transform="scale(1.2)">
          <path d="M 0 -34 C 11 -19, 13 3, 9 20 L -9 20 C -13 3, -11 -19, 0 -34 Z"
                fill="{T['panel']}" stroke="{T['text']}" stroke-width="1.4" stroke-linejoin="round"/>
          <path d="M -9 6 L -20 22 L -9 20 Z" fill="{T['blue']}" opacity=".85"/>
          <path d="M 9 6 L 20 22 L 9 20 Z" fill="{T['blue']}" opacity=".85"/>
          <circle cx="0" cy="-12" r="4.6" fill="{T['sunk']}" stroke="{T['cyan']}" stroke-width="1.4"/>
          <path class="flame" d="M -6 21 C -3 32, 3 32, 6 21 C 3 42, -3 42, -6 21 Z" fill="url(#flameGrad)" opacity="0"/>
        </g>
      </g>
      <rect x="-30" y="46" width="60" height="3" rx="1.5" fill="{T['border']}"/>
{chr(10).join(counts)}
    </g>
  </g>""", css


# ─── act 6 · orbit ──────────────────────────────────────────────────────────

def act_orbit(i: int, T: dict[str, str]) -> tuple[str, list[str]]:
    s, e = act_window(i)
    css = [
        kf("spin", [(s, "transform:translateX(0)"), (e, "transform:translateX(-56px)")]),
        anim(".earth-spin", "spin"),
        kf("halo", [
            (s, "opacity:.25"), (s + 1.0, "opacity:.5"), (e, "opacity:.3"),
        ]),
        anim(".earth-halo", "halo", "ease-in-out"),
        kf("orbitPath", [
            (s + 0.2, "stroke-dashoffset:340;opacity:0"),
            (s + 0.9, "stroke-dashoffset:0;opacity:.5"),
            (e, "stroke-dashoffset:0;opacity:.5"),
        ]),
        anim(".orbit-ring", "orbitPath", "ease-out"),
    ]
    stars = []
    for n, (sx, sy, sr, delay) in enumerate((
        (-118, -44, 1.3, 0.0), (-78, -22, 1.0, 0.5), (-44, -50, 1.5, 1.0), (12, -46, 1.1, 0.3),
        (58, -30, 1.4, 0.8), (104, -48, 1.0, 0.15), (86, -8, 1.2, 1.2), (-104, -6, 1.1, 0.65),
    )):
        name = "twinkle%d" % n
        css += [
            kf(name, [
                (s, "opacity:.25"),
                (s + 0.5 + delay, "opacity:.95"),
                (s + 1.1 + delay, "opacity:.3"),
                (e, "opacity:.6"),
            ]),
            anim(".star%d" % n, name, "ease-in-out"),
        ]
        stars.append(f'      <circle class="star{n}" cx="{sx}" cy="{sy}" r="{sr}" fill="{T["text"]}" opacity=".3"/>')

    # Satellite walks the ellipse; rotate="auto" keeps its panels facing travel.
    # The ring sits above the horizon so the satellite clears the planet at the
    # top of its pass and disappears behind the panel edge at the bottom.
    ring = "M -104 66 A 104 40 0 1 1 104 66 A 104 40 0 1 1 -104 66"
    return f"""  <g class="act act5">
    <g transform="translate({CX},{CY})">
{chr(10).join(stars)}
      <path class="orbit-ring" d="{ring}" fill="none" stroke="{T['cyan']}"
            stroke-width="1" stroke-dasharray="340" opacity="0"/>
      <g clip-path="url(#earthClip)">
        <circle cx="0" cy="88" r="56" fill="url(#earthGrad)"/>
        <g class="earth-spin" opacity=".5" fill="{T['accent']}">
          <path d="M -40 52 q 14 -10 30 -4 q 12 5 6 16 q -10 12 -26 6 q -14 -6 -10 -18 z"/>
          <path d="M 10 66 q 18 -8 30 4 q 8 10 -4 16 q -16 6 -26 -4 q -8 -8 0 -16 z"/>
          <path d="M 56 44 q 16 -6 26 6 q 6 8 -4 14 q -14 6 -22 -6 q -6 -8 0 -14 z"/>
          <path d="M 100 60 q 16 -6 26 6 q 6 8 -4 14 q -14 6 -22 -6 q -6 -8 0 -14 z"/>
        </g>
      </g>
      <circle class="earth-halo" cx="0" cy="88" r="57.5" fill="none" stroke="{T['cyan']}" stroke-width="2.5"
              opacity=".3" filter="url(#soft)"/>
      <g>
        <g>
          <animateMotion dur="6s" repeatCount="indefinite" rotate="auto" path="{ring}"/>
          <g transform="translate(0,0)">
            <rect x="-4" y="-3.5" width="8" height="7" rx="1.6" fill="{T['panel']}" stroke="{T['text']}" stroke-width="1"/>
            <rect x="-11" y="-2.4" width="6" height="4.8" rx="1" fill="{T['blue']}"/>
            <rect x="5" y="-2.4" width="6" height="4.8" rx="1" fill="{T['blue']}"/>
          </g>
        </g>
      </g>
    </g>
  </g>""", css


# ─── act 7 · real users ─────────────────────────────────────────────────────

USERS = [(-108, -30), (-70, 22), (-24, -40), (26, -38), (74, 20), (108, -26), (-108, 24), (60, -8)]


def act_users(i: int, T: dict[str, str]) -> tuple[str, list[str]]:
    s, e = act_window(i)
    css = [
        kf("hubPulse", [
            (s + 0.2, "opacity:.5;transform:scale(.7)"),
            (s + 1.0, "opacity:0;transform:scale(2.4)"),
            (s + 1.1, "opacity:.5;transform:scale(.7)"),
            (s + 1.9, "opacity:0;transform:scale(2.4)"),
            (e, "opacity:0;transform:scale(2.4)"),
        ]),
        anim(".hub-pulse", "hubPulse", "cubic-bezier(.2,.6,.3,1)"),
    ]
    people, links = [], []
    for n, (ux, uy) in enumerate(USERS):
        start = s + 0.3 + n * 0.11
        css += [
            kf("user%d" % n, [
                (start, "opacity:0;transform:scale(.3)"),
                (start + 0.28, "opacity:1;transform:scale(1)"),
                (e, "opacity:1;transform:scale(1)"),
            ]),
            anim(".user%d" % n, "user%d" % n, "cubic-bezier(.2,1.4,.4,1)"),
            kf("link%d" % n, [
                (start + 0.15, "stroke-dashoffset:160;opacity:0"),
                (start + 0.5, "stroke-dashoffset:0;opacity:.45"),
                (e, "stroke-dashoffset:0;opacity:.45"),
            ]),
            anim(".link%d" % n, "link%d" % n, "ease-out"),
        ]
        links.append(
            f'      <line class="link{n}" x1="{ux}" y1="{uy}" x2="0" y2="0" stroke="{T["blue"]}"'
            f' stroke-width="1" stroke-dasharray="160" opacity="0"/>'
        )
        people.append(
            f'      <g class="user{n}" transform="translate({ux},{uy})" opacity="0">'
            f'<circle cy="-4" r="3.4" fill="{T["cyan"]}"/>'
            f'<path d="M -6 5 a 6 6 0 0 1 12 0 z" fill="{T["cyan"]}" opacity=".8"/>'
            f'<circle r="10" fill="none" stroke="{T["cyan"]}" stroke-width=".8" opacity=".25"/>'
            f"</g>"
        )
        # A request travelling in, so the ring reads as traffic rather than decor.
        links.append(
            f'      <circle r="1.8" fill="{T["accent"]}" opacity=".9">'
            f'<animateMotion dur="1.6s" begin="{n * 0.2:.2f}s" repeatCount="indefinite"'
            f' path="M {ux} {uy} L 0 0"/></circle>'
        )

    return f"""  <g class="act act6">
    <g transform="translate({CX},{CY})">
{chr(10).join(links)}
      <circle class="hub-pulse" r="16" fill="none" stroke="{T['accent']}" stroke-width="1.4" opacity="0"/>
      <circle r="15" fill="{T['sunk']}" stroke="{T['accent']}" stroke-width="1.8"/>
      <path d="M -8 -3 h 16 M -8 3 h 16" stroke="{T['accent']}" stroke-width="1.2" opacity=".8"/>
      <circle r="6.5" fill="none" stroke="{T['accent']}" stroke-width="1.2" opacity=".8"/>
{chr(10).join(people)}
    </g>
  </g>""", css


# ─── act 8 · growth ─────────────────────────────────────────────────────────

BARS = [14, 22, 30, 27, 42, 55, 70]


def act_growth(i: int, T: dict[str, str]) -> tuple[str, list[str]]:
    s, e = act_window(i)
    css: list[str] = []
    bars, tops = [], []
    left, step, base = -96, 30, 44

    for n, h in enumerate(BARS):
        x = left + n * step
        start = s + 0.25 + n * 0.1
        css += [
            kf("grow%d" % n, [
                (start, "stroke-dashoffset:%d" % h),
                (start + 0.4, "stroke-dashoffset:0"),
                (e, "stroke-dashoffset:0"),
            ]),
            anim(".grow%d" % n, "grow%d" % n, "cubic-bezier(.2,.8,.3,1)"),
        ]
        bars.append(
            f'      <line class="grow{n}" x1="{x}" y1="{base}" x2="{x}" y2="{base - h}"'
            f' stroke="url(#barGrad)" stroke-width="13" stroke-linecap="round"'
            f' stroke-dasharray="{h}" stroke-dashoffset="{h}"/>'
        )
        tops.append((x, base - h))

    trend = "M " + " L ".join(f"{x} {y - 10}" for x, y in tops)
    css += [
        kf("trend", [
            (s + 0.9, "stroke-dashoffset:260;opacity:0"),
            (s + 1.0, "opacity:1"),
            (s + 1.55, "stroke-dashoffset:0;opacity:1"),
            (e, "stroke-dashoffset:0;opacity:1"),
        ]),
        anim(".trend", "trend", "cubic-bezier(.3,.7,.4,1)"),
        # The trend's head detaches, flies back to the middle and shrinks into
        # the next bulb — that hand-off is what makes the loop feel intentional
        # rather than a cut.
        kf("seed", [
            (s + 1.5, "opacity:0;transform:translate(%dpx,%dpx) scale(.4)" % (tops[-1][0], tops[-1][1] - 10)),
            (s + 1.62, "opacity:1;transform:translate(%dpx,%dpx) scale(1)" % (tops[-1][0], tops[-1][1] - 10)),
            (e - 0.08, "opacity:.9;transform:translate(0,-6px) scale(1.5)"),
            (e, "opacity:0;transform:translate(0,-6px) scale(.4)"),
        ]),
        anim(".seed", "seed", "cubic-bezier(.5,0,.2,1)"),
        kf("axisFade", [(s + 0.15, "opacity:0"), (s + 0.4, "opacity:1"), (e, "opacity:1")]),
        anim(".axis", "axisFade", "ease-out"),
    ]

    return f"""  <g class="act act7">
    <g transform="translate({CX},{CY})">
      <line class="axis" x1="-116" y1="{base + 9}" x2="116" y2="{base + 9}" stroke="{T['border']}" opacity="0"/>
{chr(10).join(bars)}
      <path class="trend" d="{trend}" fill="none" stroke="{T['cyan']}" stroke-width="2"
            stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="260" opacity="0"/>
      <circle class="seed" r="5" fill="{T['cyan']}" filter="url(#soft)" opacity="0"/>
    </g>
  </g>""", css


# ─── hero assembly ──────────────────────────────────────────────────────────

def hero(T: dict[str, str]) -> tuple[str, list[str]]:
    css: list[str] = []
    acts: list[str] = []

    builders = [act_idea, act_blueprint, act_code, act_test, act_launch, act_orbit, act_users, act_growth]
    for i, build in enumerate(builders):
        result = build(i, T)
        markup, rules = result if isinstance(result, tuple) else (result, [])
        acts.append(markup)
        css.extend(rules)
        rule_kf, rule_anim = act_visibility(i)
        css += [rule_kf, rule_anim]

    # Act label, act counter and the progress rail beneath the scene.
    labels = []
    rail_x, rail_w = PX + 18, PW - 36
    for i, label in enumerate(ACTS):
        s, e = act_window(i)
        css += [
            kf("lbl%d" % i, [
                (max(0.0, s - 0.15), "opacity:0"),
                (s + 0.2, "opacity:1"),
                (e - 0.35, "opacity:1"),
                (e - 0.05, "opacity:0"),
                (CYCLE, "opacity:0"),
            ]) if i else kf("lbl0", [
                (0.0, "opacity:1"),
                (e - 0.35, "opacity:1"),
                (e - 0.05, "opacity:0"),
                (CYCLE - 0.2, "opacity:0"),
                (CYCLE, "opacity:1"),
            ]),
            anim(".lbl%d" % i, "lbl%d" % i, "ease-out"),
        ]
        labels.append(
            f'    <text class="lbl lbl{i}" x="{rail_x}" y="{PY + 148}">{esc(label)}</text>\n'
            f'    <text class="idx lbl{i}" x="{rail_x + rail_w}" y="{PY + 148}" text-anchor="end">'
            f'{i + 1:02d} / {len(ACTS):02d}</text>'
        )

    ticks = []
    seg = rail_w / len(ACTS)
    for i in range(len(ACTS)):
        s, e = act_window(i)
        css += [
            kf("tk%d" % i, [
                (max(0.0, s - 0.1), "opacity:.25;r:1.6"),
                (s + 0.25, "opacity:1;r:2.6"),
                (e - 0.2, "opacity:1;r:2.6"),
                (e + 0.05, "opacity:.25;r:1.6"),
                (CYCLE, "opacity:.25;r:1.6"),
            ]),
            anim(".tk%d" % i, "tk%d" % i, "ease-out"),
        ]
        ticks.append(
            f'    <circle class="tk tk{i}" cx="{rail_x + seg * (i + 0.5):.1f}" cy="{PY + 160}" r="1.6" opacity=".25"/>'
        )

    css += [
        kf("rail", [(0.0, "stroke-dashoffset:%.1f" % rail_w), (CYCLE, "stroke-dashoffset:0")]),
        anim(".rail-fill", "rail"),
    ]

    markup = f"""  <g clip-path="url(#sceneClip)">
    <rect x="{PX}" y="{PY}" width="{PW}" height="{PH}" fill="url(#panelGrad)"/>
{chr(10).join(acts)}
  </g>
  <rect x="{PX + 0.5}" y="{PY + 0.5}" width="{PW - 1}" height="{PH - 1}" rx="12" fill="none" stroke="{T['border']}"/>
{chr(10).join(labels)}
  <line x1="{rail_x}" y1="{PY + 160}" x2="{rail_x + rail_w}" y2="{PY + 160}" stroke="{T['grid']}" stroke-width="1.5"/>
  <line class="rail-fill" x1="{rail_x}" y1="{PY + 160}" x2="{rail_x + rail_w}" y2="{PY + 160}"
        stroke="{T['cyan']}" stroke-width="1.5" stroke-dasharray="{rail_w}" stroke-dashoffset="{rail_w}"/>
{chr(10).join(ticks)}"""
    return markup, css


# ─── header ─────────────────────────────────────────────────────────────────

def header(theme: dict[str, str], freeze: int | None = None) -> str:
    T = theme
    type_cycle = len(PHRASES) * 5.0
    text_x = TYPE_X + len(PROMPT) * CHAR_W

    typing_css: list[str] = []
    groups: list[str] = []
    clip_parts: list[str] = []

    for i, phrase in enumerate(PHRASES):
        width = len(phrase) * CHAR_W
        delay = i * 5.0
        p = lambda t: 100 * t / type_cycle  # noqa: E731 — local, one use
        typing_css.append(
            "@keyframes reveal%d{0%%,%.4f%%{transform:translateX(%.1fpx)}%.4f%%,%.4f%%{transform:translateX(0)}%.4f%%,100%%{transform:translateX(%.1fpx)}}"
            % (i, p(delay), -width, p(delay + 1.1), p(delay + 4.6), p(delay + 4.7), -width)
        )
        typing_css.append(
            "@keyframes caret%d{0%%,%.4f%%{transform:translateX(0);opacity:0}%.4f%%{transform:translateX(0);opacity:1}%.4f%%,%.4f%%{transform:translateX(%.1fpx);opacity:1}%.4f%%,100%%{transform:translateX(%.1fpx);opacity:0}}"
            % (i, p(delay), p(delay + 0.05), p(delay + 1.1), p(delay + 4.6), width, p(delay + 4.7), width)
        )
        typing_css.append(
            ".clip%d rect{animation:reveal%d %.0fs steps(%d,end) infinite}"
            ".caret%d{animation:caret%d %.0fs steps(%d,end) infinite}"
            % (i, i, type_cycle, len(phrase), i, i, type_cycle, len(phrase))
        )
        # Static pose: first phrase typed out, the rest clipped away. Without it
        # the three lines stack on top of each other wherever CSS animation does
        # not run. CSS overrides presentation attributes, so motion is unaffected.
        caret_rest = ' transform="translate(%.1f,0)"' % width if i == 0 else ""
        offset = "" if i == 0 else ' transform="translate(%.1f,0)"' % -width
        clip_parts.append(
            f'    <clipPath id="clip{i}" class="clip{i}">'
            f'<rect x="{text_x:.1f}" y="{TYPE_Y - 16}" width="{width:.1f}" height="24"{offset}/></clipPath>'
        )
        groups.append(
            f'    <g clip-path="url(#clip{i})">'
            f'<text x="{text_x:.1f}" y="{TYPE_Y}" class="typed">{esc(phrase)}</text></g>\n'
            f'    <rect class="caret caret{i}" x="{text_x:.1f}" y="{TYPE_Y - 12}" width="8" height="16"{caret_rest}/>'
        )

    hero_markup, hero_css = hero(T)
    motion = "\n      ".join(typing_css + hero_css)

    # --preview freezes one act on screen with motion off, so each scene can be
    # eyeballed as a still. Never written to assets/.
    if freeze is not None:
        # Stills only: force the chosen act on and settle everything that the
        # timeline would otherwise animate in (hidden elements, undrawn strokes),
        # so a static renderer shows roughly the act's finished frame.
        motion_block = (
            f"    .act{{opacity:0}}\n    .act{freeze}{{opacity:1}}\n"
            '    [opacity="0"]{opacity:1}\n'
            "    [stroke-dashoffset]{stroke-dashoffset:0}"
        )
    else:
        motion_block = (
            "    @media (prefers-reduced-motion: no-preference) {\n"
            f"      {motion}\n"
            "    }"
        )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 220" width="900" height="220" role="img" aria-label="{esc(NAME)} — {esc(ROLE)}. Looping animation of the delivery pipeline: idea, blueprint, code, test, launch, orbit, real users, growth.">
  <title>{esc(NAME)} — {esc(ROLE)}</title>
  <desc>An eight-act loop: an idea becomes a blueprint, then code, then passing tests, then a launch, then a service in orbit, then real users, then growth — and back to the next idea.</desc>
  <defs>
{chr(10).join(clip_parts)}
    <!-- Stops at the horizon line, not the panel floor: the globe and the
         rocket trail have to be cut off above the act label, not drawn over it. -->
    <clipPath id="sceneClip"><rect x="{PX}" y="{PY}" width="{PW}" height="{SCENE_H + 2}" rx="12"/></clipPath>
    <!-- userSpaceOnUse: resolved in the translated scene space, so this circle
         lands on the globe and keeps the drifting continents inside it. -->
    <clipPath id="earthClip"><circle cx="0" cy="88" r="56"/></clipPath>
    <linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="{T['accent']}" stop-opacity="0"/>
      <stop offset="45%" stop-color="{T['accent']}"/>
      <stop offset="75%" stop-color="{T['cyan']}"/>
      <stop offset="100%" stop-color="{T['blue']}" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="panelGrad" x1="0" y1="0" x2="0.6" y2="1">
      <stop offset="0%" stop-color="{T['panel']}"/>
      <stop offset="100%" stop-color="{T['sunk']}"/>
    </linearGradient>
    <radialGradient id="ideaGlow">
      <stop offset="0%" stop-color="{T['cyan']}" stop-opacity="0.55"/>
      <stop offset="60%" stop-color="{T['blue']}" stop-opacity="0.18"/>
      <stop offset="100%" stop-color="{T['blue']}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="flameGlow">
      <stop offset="0%" stop-color="{T['warn']}" stop-opacity="0.7"/>
      <stop offset="100%" stop-color="{T['warn']}" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="flameGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{T['cyan']}"/>
      <stop offset="45%" stop-color="{T['warn']}"/>
      <stop offset="100%" stop-color="{T['warn']}" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="trailGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{T['cyan']}" stop-opacity="0"/>
      <stop offset="100%" stop-color="{T['cyan']}"/>
    </linearGradient>
    <!-- A vertical <line> has a zero-width bounding box, so the default
         objectBoundingBox units make this gradient degenerate and the bars
         vanish. Resolve it in user space instead: base of the chart to the top. -->
    <linearGradient id="barGrad" gradientUnits="userSpaceOnUse" x1="0" y1="44" x2="0" y2="-32">
      <stop offset="0%" stop-color="{T['blue']}" stop-opacity="0.5"/>
      <stop offset="100%" stop-color="{T['cyan']}"/>
    </linearGradient>
    <radialGradient id="earthGrad" cx="0.4" cy="0.25">
      <stop offset="0%" stop-color="{T['accent2']}"/>
      <stop offset="70%" stop-color="{T['blue']}"/>
      <stop offset="100%" stop-color="{T['blue']}" stop-opacity="0.55"/>
    </radialGradient>
    <linearGradient id="fade" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{T['accent']}" stop-opacity="0.18"/>
      <stop offset="100%" stop-color="{T['accent']}" stop-opacity="0"/>
    </linearGradient>
    <filter id="soft" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur stdDeviation="2.4"/>
    </filter>
    <clipPath id="card"><rect x="1" y="1" width="898" height="218" rx="14"/></clipPath>
  </defs>
  <style>
    .name {{ font: 600 34px {SANS}; fill: {T['text']}; letter-spacing: -0.4px }}
    .role {{ font: 400 16px {SANS}; fill: {T['muted']} }}
    .kicker {{ font: 500 11px {MONO}; fill: {T['accent']}; letter-spacing: 2.4px }}
    .typed {{ font: 400 14px {MONO}; fill: {T['text']} }}
    .prompt {{ font: 400 14px {MONO}; fill: {T['accent']} }}
    .caret {{ fill: {T['accent']}; opacity: 0 }}
    .caret0 {{ opacity: 1 }}
    .lbl {{ font: 600 11px {MONO}; fill: {T['cyan']}; letter-spacing: 2.2px; opacity: 0 }}
    .idx {{ font: 400 10px {MONO}; fill: {T['muted']}; letter-spacing: 1px; opacity: 0 }}
    .lbl0 {{ opacity: 1 }}
    .tk {{ fill: {T['cyan']} }}
    .act {{ opacity: 0 }}
    .act0 {{ opacity: 1 }}
    .code {{ font: 400 8px {MONO} }}
    .code-file {{ font: 400 8.5px {MONO}; fill: {T['muted']} }}
    .c-k {{ fill: {T['blue']} }}
    .c-f {{ fill: {T['accent']} }}
    .c-t {{ fill: {T['cyan']} }}
    .c-v {{ fill: {T['text']} }}
    .c-p {{ fill: {T['muted']} }}
    text.run-line, text.all-green {{ font: 400 9.5px {MONO}; fill: {T['accent']} }}
    .mono-s {{ font: 400 9.5px {MONO}; fill: {T['muted']} }}
    .count {{ font: 600 26px {MONO}; fill: {T['warn']}; text-anchor: middle }}
{motion_block}
  </style>

  <rect x="1" y="1" width="898" height="218" rx="14" fill="{T['bg']}" stroke="{T['border']}"/>
  <g clip-path="url(#card)">
    <rect x="0" y="0" width="900" height="220" fill="url(#fade)" opacity="0.3"/>
    <rect x="0" y="1" width="900" height="2" fill="url(#sweep)"/>
  </g>

  <text class="kicker" x="46" y="56">{esc(KICKER)}</text>
  <text class="name" x="44" y="100">{esc(NAME)}</text>
  <text class="role" x="46" y="126">{esc(ROLE)}</text>

  <g>
    <text class="prompt" x="{TYPE_X}" y="{TYPE_Y}">{esc(PROMPT)}</text>
{chr(10).join(groups)}
  </g>

{hero_markup}
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
        feeds.append(f'  <path class="feed" d="M {x + box_w / 2} {top + box_h} V 196"/>')

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


def main(argv: list[str]) -> int:
    if "--preview" in argv:
        act = int(argv[argv.index("--preview") + 1])
        path = os.path.join(OUT_DIR, "_preview.svg")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(header(THEMES["dark"], freeze=act))
        print(f"wrote {path} (act {act} frozen — not for commit)")
        return 0

    os.makedirs(OUT_DIR, exist_ok=True)
    for name, render in (("header", header), ("topology", topology)):
        for theme_name, theme in THEMES.items():
            path = os.path.join(OUT_DIR, f"{name}-{theme_name}.svg")
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(render(theme))
            print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
