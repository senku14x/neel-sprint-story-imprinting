"""Helpers for slide plots: source readers that record provenance, and a viz save with a footer.

Every plotted number goes through Src.rec (or a reader that calls it), so MANIFEST.md lists the exact file and the
table row / column or JSON key it came from.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import viz
from viz import svg as S
from viz import theme as th
from viz.render import render_png

OUT = Path("/workspace/Neel Sprint/things to throw away/slides_for_vishesh/plots")
EXP = Path("/workspace/Neel Sprint/experiments/sprint_work")
REPRO = Path("/workspace/Neel Sprint/experiments/reproduction")
RUN = Path("/workspace/runs_executor")
TONY = Path("/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/"
            "scratchpad/tony_fresh/e12/queue/results")

# viz's 16:9 slide (1920 x 1080 PNG) with a taller plot body so the chart fills the frame.
def slide(plot: float = 250) -> viz.Size:
    return viz.Size(width=640, plot=plot, title=22, height=360, scale=3)


viz.set_defaults(size=slide(), font="sans")

GRAY, ORANGE, BLUE = "gray", "coral", "blue"

MANIFEST: list[dict] = []
CHECKS: dict[str, list[str]] = {}
NOTES: dict[str, list[str]] = {}
TEXTS: dict[str, tuple[str, str, str]] = {}


# ---------------------------------------------------------------- provenance
class Src:
    def __init__(self, png: str):
        self.png = png
        MANIFEST.append({"png": png, "rows": []})
        self.rows = MANIFEST[-1]["rows"]

    def rec(self, what: str, val, file, key: str):
        self.rows.append((what, val, str(file), key))
        return val

    def note(self, s: str):
        NOTES.setdefault(self.png, []).append(s)


# ---------------------------------------------------------------- parsing
_NUM = r"[+\-−]?\d*\.?\d+"


def clean(s: str) -> str:
    return s.replace("**", "").replace("−", "-").replace("–", "-").strip()


def num(s: str) -> float:
    m = re.search(_NUM, clean(s))
    if not m:
        raise ValueError(f"no number in {s!r}")
    return float(m.group(0))


def num_ci(s: str):
    """'0.011 [0.000, 0.026]' -> (0.011, 0.0, 0.026); a value without a CI -> (v, None, None)."""
    c = clean(s)
    m = re.match(rf"\s*({_NUM})\s*(?:\[\s*({_NUM})\s*,\s*({_NUM})\s*\])?", c)
    if not m:
        raise ValueError(f"no value in {s!r}")
    v = float(m.group(1))
    lo = float(m.group(2)) if m.group(2) else None
    hi = float(m.group(3)) if m.group(3) else None
    return v, lo, hi


def md_tables(path) -> list[list[list[str]]]:
    """All markdown tables in a file: each a list of rows (header first), separator rows dropped."""
    tables, cur = [], []
    for line in Path(path).read_text().splitlines():
        if line.strip().startswith("|"):
            cells = [c.strip() for c in re.split(r"(?<!\\)\|", line.strip())[1:-1]]
            if all(re.fullmatch(r":?-{2,}:?", c.replace(" ", "")) for c in cells if c):
                continue
            cur.append(cells)
        else:
            if cur:
                tables.append(cur)
            cur = []
    if cur:
        tables.append(cur)
    return tables


def find_table(path, header_has: str, nth: int = 0):
    hits = [t for t in md_tables(path) if header_has in " | ".join(t[0])]
    if len(hits) <= nth:
        raise KeyError(f"no table with header containing {header_has!r} in {path}")
    return hits[nth]


def md_cell(src: Src, what: str, path, header_has: str, row_match, col, nth: int = 0, parse=num_ci):
    """Read one cell: table whose header contains header_has, row whose first cells match row_match (str prefix on
    cell 0, or tuple of prefixes on cells 0..k), column col (header substring or int index)."""
    t = find_table(path, header_has, nth)
    hdr = t[0]
    ci = col if isinstance(col, int) else next(i for i, h in enumerate(hdr) if clean(col) in clean(h))
    rm = row_match if isinstance(row_match, tuple) else (row_match,)
    for r in t[1:]:
        if all((clean(r[i]) == clean(p[1:])) if p.startswith("=") else clean(r[i]).startswith(clean(p))
               for i, p in enumerate(rm)):
            val = parse(r[ci])
            key = f"table with header '{header_has}' (#{nth}), row '{' | '.join(rm)}', column '{clean(hdr[ci])}'"
            return src.rec(what, val, path, key)
    raise KeyError(f"row {row_match!r} not found in table {header_has!r} of {path}")


def jget(src: Src, what: str, path, *keys):
    d = json.loads(Path(path).read_text())
    for k in keys:
        d = d[k]
    src.rec(what, d, path, "".join(f"[{k!r}]" for k in keys))
    return d


def regex(src: Src, what: str, path, pattern: str, group_parse=None, flags=0):
    txt = Path(path).read_text()
    m = re.search(pattern, txt, flags)
    if not m:
        raise KeyError(f"pattern {pattern!r} not found in {path}")
    val = group_parse(m) if group_parse else m.group(1)
    src.rec(what, val, path, f"regex /{pattern}/ matched: {clean(m.group(0))[:160]!r}")
    return val


# ---------------------------------------------------------------- saving
def content_height(fig) -> float:
    w0 = fig.width
    fig.width = fig._width()
    try:
        _, _, h = fig.compose()
    finally:
        fig.width = w0
    return h


def save(fig, name: str, footer: str, svg_fix=()):
    from viz import text as T
    path = OUT / name
    probs = fig.check()
    CHECKS[name] = probs
    TEXTS[name] = (fig.title or "", fig.subtitle or "", footer)
    for p in probs:
        print(f"  CHECK {name}: {p}")
    inner_h = content_height(fig)
    svg = fig.svg()
    _, w, h = fig.compose()
    lines = T.wrap(footer, w - 2 * th.PAD_X, 11, "sans")
    print(f"  footer lines: {len(lines)}")
    foot_h = 14 * len(lines) + 6
    if inner_h + foot_h - th.PAD_BOTTOM > h + 0.5:
        print(f"  WARN {name}: content {inner_h:.0f} + footer {foot_h:.0f} exceeds frame {h:.0f}")
    parts = []
    for i, ln in enumerate(reversed(lines)):
        parts.append(S.text(th.PAD_X, h - 9 - i * 14, ln, 11, th.MUTED))
    svg = svg.replace("</svg>", "".join(parts) + "</svg>")
    for old, new in svg_fix:
        svg = svg.replace(old, new)
    render_png(svg, path, 3)
    slack = h - inner_h - foot_h + th.PAD_BOTTOM
    print(f"saved {name}: frame {w:.0f}x{h:.0f}, content {inner_h:.0f}, spare {slack:.0f} layout px")
    return path


def write_manifest(extra: str = ""):
    lines = ["# Slide plots: manifest", "",
             "Every number on each PNG was read by `src/make_plots.py` from the file and key listed here. "
             "Fractions are plotted as they appear in the source (0-1 scale) unless the row says otherwise; "
             "derived values (differences, averages) say how they were computed from the listed source values.", ""]
    for m in MANIFEST:
        lines.append(f"## {m['png']}")
        lines.append("")
        if m["png"] in NOTES:
            for n in NOTES[m["png"]]:
                lines.append(f"- {n}")
            lines.append("")
        if CHECKS.get(m["png"]):
            lines.append("viz checks raised: " + "; ".join(CHECKS[m["png"]]))
            lines.append("")
        if m["png"] in TEXTS:
            t, sub, foot = TEXTS[m["png"]]
            lines.append(f"Title: {t}  ")
            lines.append(f"Footer: {foot}")
            lines.append("")
            srcs = sorted({f for _, _, f, _ in m["rows"]})
            blob = ""
            for f in srcs:
                try:
                    blob += Path(f).read_text()
                except Exception:
                    pass
            blob_c = clean(blob)
            nums = sorted(set(re.findall(r"\d+(?:\.\d+)?", t + " " + foot)), key=lambda x: float(x))
            found = [n for n in nums if re.search(r"(?<![\d.])" + re.escape(n) + r"(?![\d])", blob_c)]
            missing = [n for n in nums if n not in found]
            lines.append(f"Numbers in title/footer: {', '.join(nums) or 'none'}. Found verbatim in this plot's source "
                         f"files: {', '.join(found) or 'none'}. Not found verbatim (computed by the script from "
                         f"plotted values, or a rounded/derived count; see notes): {', '.join(missing) or 'none'}.")
            lines.append("")
        lines.append("| plotted value | read value | source file | table / key |")
        lines.append("|---|---|---|---|")
        for what, val, f, key in m["rows"]:
            v = val
            if isinstance(v, float):
                v = f"{v:.4g}"
            elif isinstance(v, (list, tuple)):
                v = ", ".join(f"{x:.4g}" if isinstance(x, float) else str(x) for x in v)
            key = str(key).replace("|", "\\|")
            lines.append(f"| {what} | {v} | `{f}` | {key} |")
        lines.append("")
    if extra:
        lines.append(extra)
    (OUT / "MANIFEST.md").write_text("\n".join(lines))


# ---------------------------------------------------------------- two panels of unequal width
def duo(left, right, frac: float = 0.68, gap: float = 22, strip_labels=(), title=None, subtitle=None,
        legend=None):
    """Two charts side by side, the left taking `frac` of the width. strip_labels: row labels to delete from the
    right panel (so it can share the left panel's rows without repeating them)."""
    import re as _re
    from viz import text as T
    from viz.figure import Body, Figure

    def render(W):
        w1 = (W - gap) * frac
        w2 = W - gap - w1
        out, hs = [], []
        for k, (f, pw, x0) in enumerate(((left, w1, 0.0), (right, w2, w1 + gap))):
            body = f.body(pw, inherit=True)
            svg = body.svg
            if k == 1 and strip_labels:
                for lab in strip_labels:
                    svg = _re.sub(r"<text[^>]*>" + _re.escape(S.esc(lab)) + r"</text>", "", svg)
            parts, h = [], 0.0
            if f.title:
                size, fam, wt = 14, "sans", 600
                px0, px1 = body.meta.get("plot_x", (0.0, pw))
                lines = T.wrap(f.title, pw, size, fam, wt)
                lh = T.line_height(size, fam)
                for i, ln in enumerate(lines):
                    wln = T.width(ln, size, fam, wt)
                    x = min(max((px0 + px1) / 2, wln / 2), pw - wln / 2)
                    parts.append(S.text(x, h + T.baseline(size, fam) + i * lh, ln, size, th.INK, "middle", wt, fam))
                h += lh * len(lines) + 6
            hs.append((parts, h, svg, body.height, x0))
        tmax = max(h for _, h, _, _, _ in hs)
        for parts, h, svg, bh, x0 in hs:
            out.append(S.group("".join(parts), x0, tmax - h))
            out.append(S.group(svg, x0, tmax))
        height = tmax + max(bh for _, _, _, bh, _ in hs)
        return Body(svg="".join(out), height=height)

    fig = Figure(render=render, title=title, subtitle=subtitle, legend=legend, kind="panels")
    fig.meta["panels"] = [left, right]
    return fig
