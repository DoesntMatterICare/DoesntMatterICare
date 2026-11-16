"""Render the CALL SHEET (experience + education) and its section header.

Usage:
  python scripts/callsheet.py
Writes assets/callsheet-{light,dark}.svg and assets/h-callsheet-{light,dark}.svg.
Edit CREW / TRAINING to change rows.
"""
import os, re, sys
from html import escape as E
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tickets import THEMES, svg, ROOT

CREW = [
    # (role, production, set, call)
    ("CHIEF EXECUTIVE OFFICER", "Arbaa Studio · self-employed", "Hyderabad", "OCT 2026 -"),
    ("AI/ML TRAINEE", "iHub-Data, IIIT Hyderabad", "On-site", "SEP 2026 -"),
    ("VICE PRESIDENT", "Student Developers Club, VCE", "Shamshabad", "JUL 2026 -"),
]
TRAINING = [
    ("B.TECH, COMPUTER SCIENCE", "Vardhaman College of Engineering", "Hyderabad", "2025 -"),
    ("AI/ML PROGRAM, 24 WEEKS", "IIIT Hyderabad · hybrid", "Hyderabad", "SEP 26 - MAR 27"),
]

COLS = dict(n=34, role=70, prod=300, set=590, call=700, stat=968)

CSS = (
    ".scan{animation:sc 7.5s steps(1) infinite}"
    "@keyframes sc{0%{transform:translateY(0)}20%{transform:translateY(46px)}40%{transform:translateY(92px)}"
    "60%{transform:translateY(197px)}80%{transform:translateY(243px)}}"
    ".dot{animation:dt 1.4s ease-in-out infinite}@keyframes dt{50%{opacity:.25}}"
)


def row(c, y, i, r, status, live):
    role, prod, where, call = r
    g = f'<line x1="24" y1="{y+16}" x2="976" y2="{y+16}" stroke="{c["ln"]}" stroke-width="1"/>'
    g += f'<text x="{COLS["n"]}" y="{y}" fill="{c["mut"]}" font-size="13">{i:02d}</text>'
    g += f'<text x="{COLS["role"]}" y="{y}" fill="{c["ink"]}" class="b" font-size="15">{E(role)}</text>'
    g += f'<text x="{COLS["prod"]}" y="{y}" fill="{c["ink"]}" font-size="14">{E(prod)}</text>'
    g += f'<text x="{COLS["set"]}" y="{y}" fill="{c["mut"]}" font-size="14">{E(where)}</text>'
    g += f'<text x="{COLS["call"]}" y="{y}" fill="{c["mut"]}" font-size="14">{E(call)}</text>'
    col = c["red"] if live else c["mut"]
    tw = len(status) * 7.8
    g += (f'<circle cx="{COLS["stat"]-tw-10:.1f}" cy="{y-5}" r="4.5" fill="{col}" class="dot" '
          f'style="animation-delay:-{i*0.35:.2f}s"/>')
    g += f'<text x="{COLS["stat"]}" y="{y}" text-anchor="end" fill="{col}" class="b" font-size="13">{status}</text>'
    return g


def heads(c, y):
    g = ""
    for k, t in (("n", "#"), ("role", "ROLE"), ("prod", "PRODUCTION"), ("set", "SET"), ("call", "CALL")):
        g += f'<text x="{COLS[k]}" y="{y}" fill="{c["mut"]}" class="b" font-size="11" letter-spacing="2">{t}</text>'
    g += f'<text x="{COLS["stat"]}" y="{y}" text-anchor="end" fill="{c["mut"]}" class="b" font-size="11" letter-spacing="2">STATUS</text>'
    g += f'<line x1="24" y1="{y+10}" x2="976" y2="{y+10}" stroke="{c["ink"]}" stroke-width="1.5"/>'
    return g


def band(c, y, text, right):
    return (f'<rect x="24" y="{y-17}" width="952" height="26" rx="2" fill="{c["ink"]}"/>'
            f'<text x="38" y="{y+1}" fill="{c["pap"]}" class="b" font-size="13" letter-spacing="2">{E(text)}</text>'
            f'<text x="962" y="{y+1}" text-anchor="end" fill="{c["pap"]}" font-size="12" letter-spacing="1">{E(right)}</text>')


def build(mode):
    c = THEMES[mode]
    W, H = 1000, 462
    g = f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="4" fill="{c["card"] if mode == "dark" else c["pap"]}" stroke="{c["ln"]}" stroke-width="1.5"/>'
    # title block
    g += f'<text x="24" y="40" fill="{c["ink"]}" class="b" font-size="22" letter-spacing="3">CALL SHEET</text>'
    g += f'<text x="24" y="60" fill="{c["mut"]}" font-size="12">DMIC PRODUCTIONS · SHOOT DAY 1 OF ∞</text>'
    g += f'<text x="976" y="40" text-anchor="end" fill="{c["mut"]}" font-size="12">UNIT BASE: HYDERABAD, INDIA</text>'
    g += f'<text x="976" y="60" text-anchor="end" fill="{c["red"]}" class="b" font-size="12">ALL DEPARTMENTS: ROLLING</text>'
    # scanning row highlight (behind rows)
    g += f'<g class="scan"><rect x="24" y="126" width="952" height="32" fill="{c["red"]}" opacity=".07"/>'
    g += f'<rect x="24" y="126" width="3" height="32" fill="{c["red"]}"/></g>'
    g += band(c, 92, "CREW ON SET", "EXPERIENCE")
    g += heads(c, 120)
    for i, r in enumerate(CREW):
        g += row(c, 147 + i * 46, i + 1, r, "ON SET", True)
    y2 = 147 + len(CREW) * 46 + 18
    g += band(c, y2, "FILM SCHOOL", "EDUCATION")
    for i, r in enumerate(TRAINING):
        g += row(c, y2 + 41 + i * 46, i + 1, r, "IN PROGRESS", True)
    fy = H - 20
    note = "NOTE: Crew list grows every season. Next call time: to be announced."
    g += (f'<text x="24" y="{fy}" fill="{c["mut"]}" font-size="12">{E(note)}</text>'
          f'<rect x="{24 + len(note)*7.2 + 6:.0f}" y="{fy-11}" width="8" height="13" fill="{c["red"]}" class="blink"/>')
    label = ("Call sheet. Crew on set: " + "; ".join(f"{r[0].title()}, {r[1]}, since {r[3].rstrip(' -')}" for r in CREW) +
             ". Film school: " + "; ".join(f"{r[0].title()}, {r[1]}, {r[3]}" for r in TRAINING) + ".")
    return svg(W, H, label, g, CSS)


def header(mode, num, title, cut):
    """Clone the existing h-work header and retitle it."""
    s = open(os.path.join(ROOT, "assets", f"h-work-{mode}.svg")).read()
    s = s.replace('aria-label="THE WORK"', f'aria-label="{E(title)}"')
    s = re.sub(r'(font-size="14">)02(<)', rf'\g<1>{num}\2', s)
    s = s.replace('font-size="20">THE WORK<', f'font-size="20">{E(title)}<')
    x1, x2 = 84 + len(title) * 12, 1000 - 20 - len(cut) * 9.6
    s = re.sub(r'<line x1="[\d.]+" y1="38" x2="[\d.]+"', f'<line x1="{x1:.1f}" y1="38" x2="{x2:.1f}"', s)
    s = s.replace('font-size="16">CUT TO:<', f'font-size="16">{E(cut)}<')
    return s


if __name__ == "__main__":
    for m in THEMES:
        open(os.path.join(ROOT, "assets", f"callsheet-{m}.svg"), "w").write(build(m))
        open(os.path.join(ROOT, "assets", f"h-callsheet-{m}.svg"), "w").write(header(m, "03", "CALL SHEET", "JUMP CUT TO:"))
        # renumber the sections that now follow the call sheet
        for name, old, new in (("cast", "03", "04"), ("laurels", "04", "05"), ("dailies", "05", "06")):
            p = os.path.join(ROOT, "assets", f"h-{name}-{m}.svg")
            s = open(p).read()
            s = re.sub(rf'(font-size="14">){old}(<)', rf'\g<1>{new}\2', s)
            open(p, "w").write(s)
    print("ok")
