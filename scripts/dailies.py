"""Render the DAILIES film strip from real GitHub contribution data.

Usage:
  python scripts/dailies.py <login>          # needs GH_TOKEN in env
  python scripts/dailies.py <login> --mock   # deterministic sample data
Writes assets/dailies-light.svg and assets/dailies-dark.svg.
Exits 0 without touching files if the API call fails.
"""
import base64, datetime as dt, json, os, random, sys, urllib.request
from html import escape as E

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DAYS = 66  # 3 takes x 22 days
THEMES = {
    "light": dict(pap="#fbfaf6", ink="#1b1b1b", mut="#6f6a60", ln="#d9d4c7", red="#d7261e", lfg="#f4f1e8"),
    "dark": dict(pap="#14151a", ink="#ece8df", mut="#9a958a", ln="#2e3038", red="#ff4a3d", lfg="#ece8df"),
}

def fetch(login, token):
    q = """query($l:String!){user(login:$l){contributionsCollection{contributionCalendar{
      weeks{contributionDays{date contributionCount}}}}}}"""
    req = urllib.request.Request("https://api.github.com/graphql",
        data=json.dumps({"query": q, "variables": {"l": login}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    days = [(d["date"], d["contributionCount"]) for w in weeks for d in w["contributionDays"]]
    return days[-DAYS:]

def mock():
    r = random.Random(11); end = dt.date(2026, 10, 24)
    return [((end - dt.timedelta(days=DAYS - 1 - i)).isoformat(), int(r.random() ** 2 * 9)) for i in range(DAYS)]

def font(n, w):
    b = base64.b64encode(open(os.path.join(ROOT, "scripts", "fonts", f"cp-{n}.woff2"), "rb").read()).decode()
    return "@font-face{font-family:'CP';src:url(data:font/woff2;base64," + b + ") format('woff2');font-weight:" + w + "}"

def fmt(d):
    return dt.date.fromisoformat(d).strftime("%b %d").upper()

def render(days, c, real):
    W, H = 1000, 270
    mx = max([n for _, n in days] + [1])
    nz = sorted(n for _, n in days if n)
    hot = nz[int(len(nz) * .6)] if nz else 1
    total = sum(n for _, n in days)
    css = (font("400-normal", "400") + font("700-normal", "700") +
        "text{font-family:'CP','Courier Prime','Courier New',monospace}.b{font-weight:700}"
        ".run{animation:rn 9s linear infinite}@keyframes rn{to{transform:translateX(-1020px)}}"
        ".eq{transform-box:fill-box;transform-origin:bottom;animation:eq 1.1s ease-in-out infinite alternate}"
        "@keyframes eq{from{transform:scaleY(.82)}to{transform:none}}"
        ".flk{animation:fk .18s steps(2) infinite}@keyframes fk{50%{opacity:.05}}"
        ".blink{animation:bk 1.06s steps(1) infinite}@keyframes bk{50%{opacity:0}}"
        "@media (prefers-reduced-motion:reduce){*{animation:none!important}}")
    fr = ""
    for rep in range(2):
        for t in range(3):
            fx = (rep * 3 + t) * 340
            chunk = days[t * 22:(t + 1) * 22]
            fr += f'<rect x="{fx+10}" y="30" width="330" height="{H-60}" fill="{c["pap"]}"/>'
            for k, (d, n) in enumerate(chunk):
                h = 3 if n == 0 else 8 + n / mx * 104
                x = fx + 40 + k * 12.5
                col = c["red"] if n and n >= hot else c["ln"]
                fr += (f'<rect x="{x:.1f}" y="{H-58-h:.0f}" width="8" height="{h:.0f}" fill="{col}" class="eq" '
                       f'style="animation-delay:{-(k*.37)%1.1:.2f}s"><title>{d}: {n}</title></rect>')
            lab = f"{fmt(chunk[0][0])} - {fmt(chunk[-1][0])}" if real else f"TAKE {t+1}"
            sub = f"{sum(n for _, n in chunk)} contributions" if real else ["MON", "WED", "FRI"][t]
            fr += f'<text x="{fx+40}" y="66" font-size="13" fill="{c["mut"]}">{E(lab)}</text>'
            fr += f'<text x="{fx+310}" y="66" text-anchor="end" font-size="13" fill="{c["mut"]}">{E(sub)}</text>'
            fr += f'<line x1="{fx+40}" y1="{H-56}" x2="{fx+310}" y2="{H-56}" stroke="{c["ln"]}" stroke-width="2"/>'
    for x in range(14, 2074, 34):
        fr += f'<rect x="{x}" y="9" width="18" height="12" rx="2" fill="{c["pap"]}"/><rect x="{x}" y="{H-21}" width="18" height="12" rx="2" fill="{c["pap"]}"/>'
    rec = f"REC · {total} IN {DAYS} DAYS" if real else "REC · LIVE"
    rw = len(rec) * 7.2 + 40
    label = f"Dailies: {total} contributions in the last {DAYS} days, as a running film strip." if real else "Dailies: a running film strip."
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{E(label)}">'
        f'<style>{css}</style><defs><clipPath id="cp"><rect width="{W}" height="{H}" rx="4"/></clipPath></defs>'
        f'<g clip-path="url(#cp)"><rect width="{W}" height="{H}" fill="{c["ink"]}"/><g class="run">{fr}</g>'
        f'<rect width="{W}" height="{H}" fill="{c["lfg"]}" opacity=".03" class="flk"/></g>'
        f'<rect x="{W-rw}" y="0" width="{rw}" height="30" fill="{c["ink"]}"/>'
        f'<g class="blink"><circle cx="{W-rw+16}" cy="15" r="5" fill="{c["red"]}"/></g>'
        f'<text x="{W-rw+28}" y="20" font-size="12" class="b" fill="{c["pap"]}">{E(rec)}</text></svg>')

def main():
    login = sys.argv[1]; real = "--mock" not in sys.argv
    try:
        days = fetch(login, os.environ["GH_TOKEN"]) if real else mock()
    except Exception as e:
        print("dailies: could not fetch contributions:", e); return
    for th, c in THEMES.items():
        open(os.path.join(ROOT, "assets", f"dailies-{th}.svg"), "w").write(render(days, c, real))
    print("dailies: wrote", len(days), "days")

if __name__ == "__main__":
    main()
