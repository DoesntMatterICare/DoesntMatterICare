"""Render the BOX OFFICE ticket row and the FULL FILMOGRAPHY strip.

Usage:
  python scripts/tickets.py
Writes assets/tk-*-{light,dark}.svg and assets/filmography-{light,dark}.svg.
Edit LINKS below to change where the tickets point.
"""
import base64, os
from html import escape as E

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORTFOLIO = "rehan-portfolio-lime.vercel.app"

THEMES = {
    "light": dict(pap="#fbfaf6", card="#fffef9", ink="#1b1b1b", mut="#6f6a60", ln="#d9d4c7",
                  red="#d7261e", onred="#fffef9", shd="#1b1b1b", hole="#ece8dd"),
    "dark": dict(pap="#14151a", card="#1c1d23", ink="#ece8df", mut="#9a958a", ln="#2e3038",
                 red="#ff4a3d", onred="#14151a", shd="#000000", hole="#0d0e12"),
}


def font(n, w):
    b = base64.b64encode(open(os.path.join(ROOT, "scripts", "fonts", f"cp-{n}.woff2"), "rb").read()).decode()
    return "@font-face{font-family:'CP';src:url(data:font/woff2;base64," + b + ") format('woff2');font-weight:" + w + "}"


BASE_CSS = (
    "text{font-family:'CP','Courier Prime','Courier New',Courier,monospace}.b{font-weight:700}"
    ".bob{transform-box:view-box;animation:bob 5s ease-in-out infinite}"
    "@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-3px)}}"
    ".perf{stroke-dasharray:4 5;animation:pf 1.4s linear infinite}@keyframes pf{to{stroke-dashoffset:-18}}"
    ".glint{animation:gl 4.8s ease-in-out infinite}"
    "@keyframes gl{0%,55%{transform:translateX(-260px)}85%,100%{transform:translateX(760px)}}"
    ".nudge{animation:nd 1.6s ease-in-out infinite}@keyframes nd{0%,100%{transform:none}50%{transform:translate(3px,-3px)}}"
    ".slide{animation:sl 1.6s ease-in-out infinite}@keyframes sl{0%,100%{transform:none}50%{transform:translateX(6px)}}"
    ".dl{stroke-dasharray:2 6;animation:mv 1.6s linear infinite}@keyframes mv{to{stroke-dashoffset:-16}}"
    ".blink{animation:bk 1.06s steps(1) infinite}@keyframes bk{50%{opacity:0}}"
    ".stamp{transform-box:fill-box;transform-origin:center;animation:st .35s 1s cubic-bezier(.2,1.8,.5,1) both}"
    "@keyframes st{from{transform:scale(1.8) rotate(-16deg);opacity:0}to{transform:rotate(-8deg);opacity:.9}}"
    "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
)


def svg(w, h, label, body, extra_css=""):
    css = font("400-normal", "400") + font("700-normal", "700") + BASE_CSS + extra_css
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{E(label)}"><style>{css}</style>{body}</svg>')


def arrow(x, y, col, s=1.0):
    # diagonal "open in new" arrow, drawn so it does not depend on font glyphs
    return (f'<g transform="translate({x} {y}) scale({s})"><g class="nudge">'
            f'<path d="M0 14 L14 0 M4 0 H14 V10" fill="none" stroke="{col}" stroke-width="2.6" '
            f'stroke-linecap="round" stroke-linejoin="round"/></g></g>')


def ticket(c, uid, W, H, stub, fill, stroke, fg, sub, label, title, line, serial, big, hero):
    pad = 14  # room for bob + shadow
    tw, th = W - pad * 2, H - pad * 2
    notch = 11
    mask = (f'<mask id="m{uid}"><rect width="{W}" height="{H}" fill="#fff"/>'
            f'<circle cx="{pad+stub}" cy="{pad}" r="{notch}" fill="#000"/>'
            f'<circle cx="{pad+stub}" cy="{pad+th}" r="{notch}" fill="#000"/>'
            f'<circle cx="{pad}" cy="{pad+th/2}" r="{notch-3}" fill="#000"/>'
            f'<circle cx="{pad+tw}" cy="{pad+th/2}" r="{notch-3}" fill="#000"/></mask>'
            f'<clipPath id="c{uid}"><rect x="{pad}" y="{pad}" width="{tw}" height="{th}" rx="8"/></clipPath>')
    g = f'<defs>{mask}</defs><g class="bob" style="animation-delay:-{len(title)*0.37:.2f}s">'
    g += (f'<g mask="url(#m{uid})"><rect x="{pad+4}" y="{pad+6}" width="{tw}" height="{th}" rx="8" '
          f'fill="{c["shd"]}" opacity=".14"/></g>')
    g += f'<g mask="url(#m{uid})"><rect x="{pad}" y="{pad}" width="{tw}" height="{th}" rx="8" fill="{fill}"'
    g += f' stroke="{stroke}" stroke-width="1.5"/>' if stroke else '/>'
    # inner border
    g += (f'<rect x="{pad+6}" y="{pad+6}" width="{tw-12}" height="{th-12}" rx="5" fill="none" '
          f'stroke="{fg}" stroke-opacity=".22" stroke-width="1"/>')
    if hero:
        g += (f'<g clip-path="url(#c{uid})"><g class="glint"><path d="M0 {H} L60 0 H110 L50 {H} Z" '
              f'fill="#fff" opacity=".18"/></g></g>')
    g += '</g>'
    # perforation
    g += (f'<line x1="{pad+stub}" y1="{pad+notch+3}" x2="{pad+stub}" y2="{pad+th-notch-3}" '
          f'stroke="{fg}" stroke-opacity=".55" stroke-width="1.6" class="perf"/>')
    # stub: vertical ADMIT ONE + serial
    cx, cy = pad + stub / 2, pad + th / 2
    g += (f'<text x="{cx-5:.1f}" y="{cy:.1f}" transform="rotate(-90 {cx-5:.1f} {cy:.1f})" text-anchor="middle" '
          f'fill="{fg}" class="b" font-size="{13 if big else 11}" letter-spacing="2">ADMIT ONE</text>')
    g += (f'<text x="{cx+12:.1f}" y="{cy:.1f}" transform="rotate(-90 {cx+12:.1f} {cy:.1f})" text-anchor="middle" '
          f'fill="{fg}" fill-opacity=".6" font-size="10" letter-spacing="1">No.{serial}</text>')
    # body
    bx = pad + stub + (22 if big else 16)
    g += f'<text x="{bx}" y="{pad+30}" fill="{fg}" fill-opacity=".7" font-size="{12 if big else 10.5}" letter-spacing="1.5">{E(label)}</text>'
    g += f'<text x="{bx}" y="{pad+(74 if big else 66)}" fill="{fg}" class="b" font-size="{38 if big else 22}">{E(title)}</text>'
    g += f'<text x="{bx}" y="{pad+th-18}" fill="{fg}" fill-opacity=".85" font-size="{14 if big else 11.5}">{E(line)}</text>'
    if big:
        tl = len(title) * 38 * 0.6
        g += (f'<path d="M{bx} {pad+84} q{tl*0.5:.0f} -5 {tl:.0f} 0" fill="none" stroke="{fg}" '
              f'stroke-width="2.4" stroke-linecap="round" opacity=".8"/>')
    ax = pad + tw - (40 if big else 30)
    g += arrow(ax, pad + (22 if big else 18), fg, 1.15 if big else 0.9)
    if sub:
        g += sub
    g += '</g>'
    return g


def build_tickets(mode):
    c = THEMES[mode]
    out = {}
    stamp = (f'<g class="stamp"><rect x="350" y="56" width="100" height="27" rx="3" fill="none" '
             f'stroke="{c["onred"]}" stroke-width="2"/><text x="400" y="74.5" text-anchor="middle" '
             f'fill="{c["onred"]}" class="b" font-size="12" letter-spacing="2">PREMIERE</text></g>')
    out["portfolio"] = svg(500, 150, f"Admit one: the portfolio, now screening at {PORTFOLIO}",
        ticket(c, "p", 500, 150, 92, c["red"], None, c["onred"], stamp,
               "NOW SCREENING · REEL 02", "PORTFOLIO", PORTFOLIO, "0001", True, True))
    out["linkedin"] = svg(250, 150, "Admit one: LinkedIn, Mohammed Rehan",
        ticket(c, "l", 250, 150, 50, c["card"], c["ln"], c["ink"], "",
               "STAGE DOOR", "LINKEDIN", "/in/mohammed-rehan", "0002", False, False))
    out["email"] = svg(250, 150, "Admit one: email rehanstudy4@gmail.com",
        ticket(c, "e", 250, 150, 50, c["card"], c["ln"], c["ink"], "",
               "BOX OFFICE", "EMAIL", "rehanstudy4@gmail.com", "0003", False, False))
    return out


def build_filmography(mode):
    c = THEMES[mode]
    W, H = 1000, 96
    g = f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="6" fill="{c["ink"]}"/>'
    g += f'<defs><clipPath id="fc"><rect x="1" y="1" width="{W-2}" height="{H-2}" rx="6"/></clipPath></defs>'
    g += f'<g clip-path="url(#fc)"><g class="slide-strip">'
    for x in range(14, W + 40, 30):
        g += (f'<rect x="{x}" y="8" width="16" height="10" rx="2" fill="{c["pap"]}"/>'
              f'<rect x="{x}" y="{H-18}" width="16" height="10" rx="2" fill="{c["pap"]}"/>')
    g += '</g></g>'
    g += f'<rect x="10" y="24" width="{W-20}" height="{H-48}" rx="3" fill="{c["pap"]}"/>'
    # play head
    g += f'<path d="M30 39 L44 48 L30 57 Z" fill="{c["red"]}" class="blink"/>'
    g += f'<text x="56" y="54" fill="{c["ink"]}" class="b" font-size="18" letter-spacing="1">THE FULL FILMOGRAPHY</text>'
    g += f'<line x1="320" y1="48" x2="602" y2="48" stroke="{c["ln"]}" stroke-width="2" class="dl"/>'
    g += f'<text x="935" y="54" text-anchor="end" fill="{c["ink"]}" class="b" font-size="17">{E(PORTFOLIO)}</text>'
    g += f'<g class="slide"><path d="M948 48 H972 M963 39 L972 48 L963 57" fill="none" stroke="{c["red"]}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></g>'
    css = ".slide-strip{animation:ss 2.4s linear infinite}@keyframes ss{to{transform:translateX(-30px)}}"
    return svg(W, H, f"Every project, one reel: the full filmography at {PORTFOLIO}", g, css)


if __name__ == "__main__":
    for mode in THEMES:
        for name, s in build_tickets(mode).items():
            open(os.path.join(ROOT, "assets", f"tk-{name}-{mode}.svg"), "w").write(s)
        open(os.path.join(ROOT, "assets", f"filmography-{mode}.svg"), "w").write(build_filmography(mode))
    print("ok")
