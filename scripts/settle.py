"""Make reveal animations play once and stay, instead of wiping and replaying.

Usage:
  python scripts/settle.py
Patches, in place:
  - scene-about / ending: the SMIL typewriter loops -> type once, freeze on the final frame
    (the blinking cursor keeps blinking).
  - sc-* cards: the highlighter stroke draws once and stays.
Safe to run more than once.
"""
import glob, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(ROOT, "assets")


def settle_smil(s):
    anims = re.findall(r'<animate [^>]*repeatCount="indefinite"[^>]*/>', s)
    # the moment the loop wipes the page = 3rd keyTime of the "0;1;0" glyph reveals
    resets = []
    for a in anims:
        if 'values="0;1;0"' in a and "begin=" not in a:
            kt = re.search(r'keyTimes="([^"]+)"', a).group(1).split(";")
            resets.append(float(kt[2]))
    if not resets:
        return s
    reset = min(resets)

    def fix(m):
        a = m.group(0)
        if "begin=" in a:  # cursor blink after typing finishes: keep it going
            return a
        vals = re.search(r'values="([^"]+)"', a).group(1).split(";")
        kts = [float(k) for k in re.search(r'keyTimes="([^"]+)"', a).group(1).split(";")]
        keep = max(i for i, k in enumerate(kts) if k < reset)
        vals = vals[:keep + 1] + [vals[keep]] * (len(vals) - keep - 1)
        a = re.sub(r'values="[^"]+"', 'values="' + ";".join(vals) + '"', a)
        return a.replace('repeatCount="indefinite"', 'repeatCount="1" fill="freeze"')

    return re.sub(r'<animate [^>]*repeatCount="indefinite"[^>]*/>', fix, s)


def main():
    for name in ("scene-about", "ending"):
        for m in ("light", "dark"):
            p = os.path.join(A, f"{name}-{m}.svg")
            s = open(p).read()
            open(p, "w").write(settle_smil(s))
    for p in glob.glob(os.path.join(A, "sc-*.svg")):
        s = open(p).read()
        s = s.replace(".hl{stroke-dasharray:300;animation:hl 5s ease-in-out infinite}",
                      ".hl{stroke-dasharray:300;animation:hl 1.2s ease-in-out both}")
        s = s.replace("@keyframes hl{0%{stroke-dashoffset:300}25%,75%{stroke-dashoffset:0}100%{stroke-dashoffset:-300}}",
                      "@keyframes hl{from{stroke-dashoffset:300}to{stroke-dashoffset:0}}")
        open(p, "w").write(s)
    print("ok")


if __name__ == "__main__":
    main()
