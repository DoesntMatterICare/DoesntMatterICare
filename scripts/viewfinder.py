"""Render the VIEWFINDER: a camera HUD showing what is currently being shot.

Usage:
  python scripts/viewfinder.py
Writes assets/viewfinder-light.svg and assets/viewfinder-dark.svg (it is a camera screen,
so both are the same). Edit NOW / NEXT / POST to change what is in production.
"""
import os, sys
from html import escape as E
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tickets import svg, ROOT

NOW = "STATIC FOR ANDROID"
NEXT = "DRAWFIGHT: STORY MODE"
POST = "SDC PLATFORM"

W, H = 1000, 200
INK, MUT, DIM, RED, BG = "#ece8df", "#8a867d", "#3a3c44", "#ff4a3d", "#0b0c0f"

CSS = (
    ".rec{animation:rc 1.2s steps(1) infinite}@keyframes rc{50%{opacity:.15}}"
    ".focus{animation:fc 1.6s .4s cubic-bezier(.3,0,.2,1) both}"
    "@keyframes fc{0%{filter:blur(7px);opacity:.3;letter-spacing:9px}70%{filter:blur(0);opacity:1}100%{filter:none;letter-spacing:4px}}"
    ".af{transform-box:fill-box;transform-origin:center;animation:af 1.6s .4s cubic-bezier(.3,0,.2,1) both}"
    "@keyframes af{0%{transform:scale(1.18);opacity:.25}75%{transform:scale(.97);opacity:1}100%{transform:none;opacity:1}}"
    ".afc{animation:afc 2.4s 2s both}@keyframes afc{0%,100%{stroke:" + INK + "}10%,40%{stroke:#7dff9b}}"
    ".fade{animation:fd .8s 1.6s ease-out both}@keyframes fd{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:none}}"
    ".lv{transform-box:fill-box;transform-origin:left;animation:lv .9s ease-in-out infinite alternate}"
    "@keyframes lv{0%{transform:scaleX(.35)}30%{transform:scaleX(.8)}60%{transform:scaleX(.5)}100%{transform:scaleX(.95)}}"
    ".f{animation:f1 1s steps(24) infinite}@keyframes f1{to{transform:translateY(-480px)}}"
    ".s1{animation:s1 10s steps(10) infinite}@keyframes s1{to{transform:translateY(-200px)}}"
    ".s10{animation:s10 60s steps(6) infinite}@keyframes s10{to{transform:translateY(-120px)}}"
    ".m1{animation:m1 600s steps(10) infinite}@keyframes m1{to{transform:translateY(-200px)}}"
)


def strip(x, y, cls, labels, clip_id):
    """A vertical strip of labels scrolled with steps() to make a ticking counter."""
    t = "".join(f'<text x="{x}" y="{y + i*20}" fill="{INK}" font-size="15">{l}</text>' for i, l in enumerate(labels))
    return (f'<clipPath id="{clip_id}"><rect x="{x-1}" y="{y-15}" width="{len(labels[0])*9.5+2}" height="20"/></clipPath>'
            f'<g clip-path="url(#{clip_id})"><g class="{cls}">{t}</g></g>')


def bracket(x, y, dx, dy, L=26, cls=""):
    return (f'<path d="M{x} {y+dy*L} V{y} H{x+dx*L}" fill="none" stroke="{INK}" stroke-width="2.2" '
            f'stroke-linecap="square"{cls}/>')


def build():
    g = f'<rect width="{W}" height="{H}" rx="10" fill="{BG}"/>'
    # rule-of-thirds grid
    for x in (W / 3, 2 * W / 3):
        g += f'<line x1="{x:.0f}" y1="18" x2="{x:.0f}" y2="{H-18}" stroke="{DIM}" stroke-width="1" stroke-dasharray="2 6"/>'
    for y in (H / 3, 2 * H / 3):
        g += f'<line x1="18" y1="{y:.0f}" x2="{W-18}" y2="{y:.0f}" stroke="{DIM}" stroke-width="1" stroke-dasharray="2 6"/>'
    # frame corners
    m = 16
    g += bracket(m, m, 1, 1) + bracket(W - m, m, -1, 1) + bracket(m, H - m, 1, -1) + bracket(W - m, H - m, -1, -1)
    # top-left: REC + timecode
    g += f'<circle cx="44" cy="40" r="6" fill="{RED}" class="rec"/>'
    g += f'<text x="58" y="45" fill="{INK}" class="b" font-size="15">REC</text>'
    tx = 104
    g += strip(tx, 45, "m1", [f"{i:02d}" for i in range(10)] + ["00"], "cm")  # minutes (00-09 loop)
    g += f'<text x="{tx+19}" y="45" fill="{MUT}" font-size="15">:</text>'
    g += strip(tx + 28, 45, "s10", [str(i) for i in range(6)] + ["0"], "cs10")
    g += strip(tx + 37.5, 45, "s1", [str(i) for i in range(10)] + ["0"], "cs1")
    g += f'<text x="{tx+47}" y="45" fill="{MUT}" font-size="15">:</text>'
    g += strip(tx + 56, 45, "f", [f"{i:02d}" for i in range(24)] + ["00"], "cf")
    # top-right: format + battery
    g += f'<text x="{W-104}" y="45" text-anchor="end" fill="{MUT}" font-size="13" letter-spacing="1">4K · 24FPS · 180°</text>'
    g += (f'<rect x="{W-92}" y="33" width="34" height="15" rx="2" fill="none" stroke="{INK}" stroke-width="1.6"/>'
          f'<rect x="{W-57}" y="37" width="3" height="7" fill="{INK}"/>'
          f'<rect x="{W-89}" y="36" width="22" height="9" fill="{INK}"/>')
    # centre: focus box + title
    cx = W / 2
    g += f'<text x="{cx}" y="72" text-anchor="middle" fill="{MUT}" font-size="12" letter-spacing="6" class="fade">NOW SHOOTING</text>'
    bw, bh, by = 470, 52, 82
    g += f'<g class="af">'
    for (x, y, dx, dy) in ((cx - bw / 2, by, 1, 1), (cx + bw / 2, by, -1, 1), (cx - bw / 2, by + bh, 1, -1), (cx + bw / 2, by + bh, -1, -1)):
        g += f'<path d="M{x} {y+dy*12} V{y} H{x+dx*12}" fill="none" stroke="{INK}" stroke-width="1.8" class="afc"/>'
    g += '</g>'
    g += (f'<text x="{cx}" y="{by+37}" text-anchor="middle" fill="{INK}" class="b focus" font-size="34" '
          f'letter-spacing="4">{E(NOW)}</text>')
    # bottom-left: what is next / in post
    g += (f'<g class="fade"><text x="44" y="{H-36}" fill="{MUT}" font-size="12.5" letter-spacing="1">'
          f'NEXT <tspan fill="{INK}">{E(NEXT)}</tspan>   ·   IN POST <tspan fill="{INK}">{E(POST)}</tspan></text></g>')
    # bottom-right: audio meters
    for i, d in enumerate((0, -0.37)):
        y = H - 52 + i * 11
        g += f'<text x="{W-170}" y="{y+7}" fill="{MUT}" font-size="10">{"L" if i == 0 else "R"}</text>'
        g += f'<rect x="{W-156}" y="{y}" width="112" height="6" fill="{DIM}"/>'
        g += (f'<rect x="{W-156}" y="{y}" width="112" height="6" fill="{INK}" class="lv" '
              f'style="animation-delay:{d}s"/>')
    g += f'<line x1="{W-156+95}" y1="{H-55}" x2="{W-156+95}" y2="{H-30}" stroke="{RED}" stroke-width="1.5"/>'
    label = f"Camera viewfinder, recording. Now shooting: {NOW.title()}. Next: {NEXT.title()}. In post: {POST.title()}."
    return svg(W, H, label, g, CSS)


if __name__ == "__main__":
    s = build()
    for m in ("light", "dark"):
        open(os.path.join(ROOT, "assets", f"viewfinder-{m}.svg"), "w").write(s)
    print("ok")
