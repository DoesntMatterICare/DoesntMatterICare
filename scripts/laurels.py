"""Render LAURELS: two rows of festival-style wreaths (wins on top, certifications below).

Usage:
  python scripts/laurels.py
Writes assets/laurels-light.svg and assets/laurels-dark.svg. Edit LAURELS to change entries.
"""
import math, os, sys
from html import escape as E
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tickets import THEMES, svg, ROOT

LAURELS = [
    # (headline, issuer (red), detail)
    ("WINNER", "GDAI", "Game Connect"),
    ("1ST PLACE", "TGC GAMEJAM", "General Track"),
    ("3RD PRIZE", "QURIOSITY", "ISAQC · IIITH"),
    ("2ND PLACE", "IEEE SSIT", "Poster"),
    ("96%", "BITS PILANI", "OS course"),
    ("CERTIFIED", "ANTHROPIC", "Claude Code 101"),
    ("CERTIFIED", "ANTHROPIC", "AI Capabilities"),
    ("CERTIFIED", "GOOGLE", "AI Studio"),
]

CSS = (
    ".lf{transform-box:fill-box;transform-origin:center;animation:lg .9s ease-out both}"
    "@keyframes lg{0%{transform:scale(0);opacity:0}60%{transform:scale(1.25);opacity:1}100%{transform:none;opacity:1}}"
    ".gt{transform-box:fill-box;transform-origin:center;animation:gt 3.5s ease-in-out infinite}"
    "@keyframes gt{0%,70%,100%{transform:scale(0) rotate(0);opacity:0}80%{transform:scale(1.2) rotate(90deg);opacity:1}90%{transform:scale(0) rotate(180deg);opacity:0}}"
    ".tx{animation:tx 1s ease-out both}@keyframes tx{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}"
)


def star(x, y, col, delay):
    return (f'<g class="gt" style="animation-delay:{delay:.1f}s"><path d="M{x} {y-10} L{x+2.5} {y-2.5} L{x+10} {y} '
            f'L{x+2.5} {y+2.5} L{x} {y+10} L{x-2.5} {y+2.5} L{x-10} {y} L{x-2.5} {y-2.5}Z" fill="{col}"/></g>')


def wreath(cx, cy, i, c, item):
    R = 90
    g = ""
    base = i * 0.22
    for side in (-1, 1):
        pts = []
        for k in range(10):
            # sweep from the bottom up to the top on each side
            a = math.radians(240 - k * 13.5) if side == -1 else math.radians(-60 + k * 13.5)
            pts.append((cx + R * math.cos(a), cy - R * math.sin(a), a))
        g += '<path d="M' + " L".join(f"{x:.1f} {y:.1f}" for x, y, _ in pts) + \
             f'" fill="none" stroke="{c["ln"]}" stroke-width="2"/>'
        for k, (x, y, a) in enumerate(pts[:-1]):
            tang = math.degrees(-a) + (90 if side == 1 else -90)
            size = 9.5 - k * 0.45
            for off, rot in ((7, 35), (-7, -35)):
                nx, ny = math.cos(a) * off, -math.sin(a) * off
                lx, ly = x + nx, y + ny
                d = base + k * 0.07
                col = c["red"] if (k == 8 and off > 0) else c["mut"]
                g += (f'<g class="lf" style="animation-delay:{d:.2f}s"><ellipse cx="{lx:.1f}" cy="{ly:.1f}" '
                      f'rx="{size:.1f}" ry="{size*0.37:.1f}" transform="rotate({tang + rot*side:.1f} {lx:.1f} {ly:.1f})" '
                      f'fill="{col}" fill-opacity="{1 if col == c["red"] else .8}"/></g>')
    h, who, det = item
    g += (f'<g class="tx" style="animation-delay:{base:.2f}s">'
          f'<text x="{cx}" y="{cy-10}" text-anchor="middle" fill="{c["ink"]}" class="b" font-size="18">{E(h)}</text>'
          f'<text x="{cx}" y="{cy+13}" text-anchor="middle" fill="{c["red"]}" class="b" font-size="13">{E(who)}</text>'
          f'<text x="{cx}" y="{cy+32}" text-anchor="middle" fill="{c["mut"]}" font-size="11.5">{E(det)}</text></g>')
    g += star(cx - 54, cy - 72, c["red"], i * 0.9) + star(cx + 58, cy - 68, c["red"], i * 0.9 + 1.7)
    return g


def build(mode):
    c = THEMES[mode]
    W, H = 1000, 450
    g = ""
    for i, item in enumerate(LAURELS):
        row, col = divmod(i, 4)
        g += wreath(125 + col * 250, 112 + row * 222, i, c, item)
    label = "Laurels: " + ". ".join(f"{h}, {w}, {d}" for h, w, d in LAURELS) + "."
    return svg(W, H, label, g, CSS)


if __name__ == "__main__":
    for m in THEMES:
        open(os.path.join(ROOT, "assets", f"laurels-{m}.svg"), "w").write(build(m))
    print("ok")
