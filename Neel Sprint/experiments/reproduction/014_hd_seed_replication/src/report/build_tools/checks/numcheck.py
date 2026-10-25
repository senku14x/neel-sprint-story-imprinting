"""Trace every number in the report's prose (body.html, tldr.html, examples.json notes) to a source file.

A number counts as traced when either
  (a) the same number token appears in a source text (analysis.md, design_spec.md, README.md, the three review files,
      the red-team's output, judge_test_retest.md, parity/README.md, the deviations note), or
  (b) its value equals a numeric value in seed_summary.json or payload.json (aggregates only) after rounding to the
      displayed precision, as a plain value or as a percentage.
Numbers inside <code> spans (script ids, file names) and tag attributes are skipped. Prints every untraced number with context.
"""
import html, json, re, sys
from html.parser import HTMLParser

R = "/workspace/Neel Sprint/experiments/reproduction/014_hd_seed_replication"
SRC_TXT = [f"{R}/analysis.md", f"{R}/design_spec.md", f"{R}/README.md", f"{R}/src/review/recompute.md", f"{R}/src/review/redteam.md",
           f"{R}/src/review/redteam_checks_output.txt", f"{R}/src/review/qualitative.md", f"{R}/src/results/judge_test_retest.md",
           f"{R}/src/parity/README.md", "/workspace/Neel Sprint/_sessions/executor-seeds/notes/2026-10-25_schedule_and_deviations.md"]
NUM = re.compile(r"(?<![\w.])[+\-−]?\d{1,3}(?:,\d{3})+(?:\.\d+)?|(?<![\w.])[+\-−]?\d*\.?\d+(?:e-?\d+)?")


def norm(tok):
    t = tok.replace("−", "-").replace(",", "")
    if t.startswith("+"):
        t = t[1:]
    return t


class Text(HTMLParser):
    def __init__(self):
        super().__init__(); self.out = []; self.skip = 0
    def handle_starttag(self, tag, a):
        if tag in ("code", "script", "style"):
            self.skip += 1
    def handle_endtag(self, tag):
        if tag in ("code", "script", "style"):
            self.skip -= 1
    def handle_data(self, d):
        if not self.skip:
            self.out.append(d)


def tokens(text):
    out = []
    for m in NUM.finditer(text):
        tok = m.group(0)
        ctx = text[max(0, m.start() - 40):m.end() + 25].replace("\n", " ")
        out.append((tok, ctx))
    return out


def numeric_values(obj, acc):
    if isinstance(obj, bool):
        return
    if isinstance(obj, (int, float)):
        acc.add(float(obj)); return
    if isinstance(obj, dict):
        for v in obj.values():
            numeric_values(v, acc)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            numeric_values(v, acc)


def main():
    rep = sys.argv[1]
    src_tokens = set()
    for f in SRC_TXT:
        for tok, _ in tokens(open(f).read()):
            src_tokens.add(norm(tok))
    vals = set()
    numeric_values(json.load(open(f"{R}/src/results/seed_summary.json")), vals)
    P = json.load(open(f"{rep}/payload.json"))
    if "--strict" not in sys.argv:
        for k, v in P.items():
            if k in ("C", "L", "rubric", "prompts", "script", "sys_dismissive", "examples", "t1ex"):
                continue
            numeric_values(v, vals)
    # derived quantities the prose cites (z = estimate / SE) come from the red-team output (source text), so no extra list
    vals_l = sorted(vals)
    texts = []
    for f in ["tldr.html", "body.html"]:
        p = Text(); p.feed(open(f"{rep}/{f}").read()); texts.append((f, html.unescape(" ".join(p.out))))
    for name, e in json.load(open(f"{rep}/examples.json")).items():
        texts.append((f"examples.json:{name}", e.get("note", "") + " " + e.get("label", "")))
    n = 0; untraced = []
    for f, t in texts:
        for tok, ctx in tokens(t):
            s = norm(tok)
            n += 1
            if s in src_tokens:
                continue
            try:
                v = float(s)
            except ValueError:
                untraced.append((f, tok, ctx)); continue
            d = len(s.split(".")[1]) if "." in s else 0
            ok = False
            for x in vals_l:
                for cand in (x, 100 * x, -x, -100 * x):
                    if abs(round(cand, d) - v) < 1e-9 or abs(cand - v) < 0.5 * 10 ** (-d) + 1e-12:
                        ok = True; break
                if ok:
                    break
            if not ok:
                untraced.append((f, tok, ctx))
    print(f"numbers checked: {n}; untraced: {len(untraced)}")
    for f, tok, ctx in untraced:
        print(f"  [{f}] {tok!r}  …{ctx}…")


if __name__ == "__main__":
    main()
