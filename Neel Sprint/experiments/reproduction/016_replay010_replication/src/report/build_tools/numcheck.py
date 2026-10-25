"""Trace every number in the 016 report's prose (tldr.html, body.html, the example labels/notes) to a source.
Traced when (a) the same token appears in a source text (analysis.md, design_spec.md, README.md, the three review files), or
(b) it equals a numeric aggregate in payload.json after rounding to the displayed precision (plain or as a percentage).
Numbers inside <code>, <script>, <style> are skipped."""
import html, json, re, sys
from html.parser import HTMLParser
R = "/workspace/Neel Sprint/experiments/reproduction/016_replay010_replication"
SRC = [f"{R}/analysis.md", f"{R}/design_spec.md", f"{R}/README.md", f"{R}/src/review/recompute.md", f"{R}/src/review/redteam.md", f"{R}/src/review/qualitative.md"]
NUM = re.compile(r"(?<![\w.])[+\-−]?\d{1,3}(?:,\d{3})+(?:\.\d+)?|(?<![\w.])[+\-−]?\d*\.?\d+(?:e-?\d+)?")
norm = lambda t: t.replace("−", "-").replace(",", "").lstrip("+")
class T(HTMLParser):
    def __init__(s): super().__init__(); s.out = []; s.skip = 0
    def handle_starttag(s, t, a):
        if t in ("code", "script", "style"): s.skip += 1
    def handle_endtag(s, t):
        if t in ("code", "script", "style"): s.skip -= 1
    def handle_data(s, d):
        if not s.skip: s.out.append(d)
def toks(text):
    return [(m.group(0), text[max(0, m.start() - 40):m.end() + 25].replace("\n", " ")) for m in NUM.finditer(text)]
def vals(o, acc):
    if isinstance(o, bool): return
    if isinstance(o, (int, float)): acc.add(float(o)); return
    if isinstance(o, dict): [vals(v, acc) for v in o.values()]
    elif isinstance(o, list): [vals(v, acc) for v in o]
rep = sys.argv[1]
src = set()
for f in SRC:
    for t, _ in toks(open(f).read()): src.add(norm(t))
P = json.load(open(f"{rep}/payload.json")); V = set()
for k, v in P.items():
    if k in ("C", "L", "PF", "U", "rubric", "script", "sys_dismissive", "examples", "pf_prompt", "animal_prompt", "PF_cols", "L_cols", "prefix"): continue
    vals(v, V)
V = sorted(V)
texts = []
for f in ["tldr.html", "body.html"]:
    p = T(); p.feed(open(f"{rep}/{f}").read()); texts.append((f, html.unescape(" ".join(p.out))))
for e in P["examples"]: texts.append(("examples", e["label"] + " " + e["note"]))
n = 0; bad = []
for f, t in texts:
    for tok, ctx in toks(t):
        s = norm(tok); n += 1
        if s in src: continue
        try: v = float(s)
        except ValueError: bad.append((f, tok, ctx)); continue
        d = len(s.split(".")[1]) if "." in s else 0
        ok = any(abs(round(c, d) - v) < 1e-9 for x in V for c in (x, 100 * x, -x, -100 * x))
        if not ok: bad.append((f, tok, ctx))
print(f"numbers checked: {n}; untraced: {len(bad)}")
for f, tok, ctx in bad: print(f"  [{f}] {tok!r}  …{ctx}…")
