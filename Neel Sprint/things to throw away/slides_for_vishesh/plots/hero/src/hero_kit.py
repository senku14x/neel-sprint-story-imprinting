"""Shared pieces for the hero plots: provenance recording, source readers, and a matplotlib style that matches the
viz library's slide palette (viz has no arrows or free annotations, so these plots are drawn with matplotlib).

Every plotted number goes through Src.rec, so MANIFEST.md lists the file and key it came from.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager as fm  # noqa: E402

HERO = Path("/workspace/Neel Sprint/things to throw away/slides_for_vishesh/plots/hero")
EXP = Path("/workspace/Neel Sprint/experiments/sprint_work")
RUN = Path("/workspace/runs_executor")
FONT = Path("/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/"
            "scratchpad/vizenv/lib/python3.11/site-packages/viz/fonts/DMSans.ttf")

# viz theme values (viz/theme.py)
INK, INK2, MUTED, GRID, AXIS = "#191918", "#3D3C38", "#6E6C65", "#E6E2DA", "#B9B6AE"
P = {"coral": "#B8664E", "blue": "#557E98", "sage": "#668574", "gray": "#C2BFB9", "dark": "#57544E",
     "mid": "#8C887F", "plum": "#88719A", "ochre": "#9E7A3D", "gray-dark": "#ADA9A1", "light-blue": "#AFC4D3",
     "deep-blue": "#41667E", "navy": "#2B475A", "light-coral": "#EDB9A4", "clay": "#94503A", "olive": "#507207",
     "deep-sage": "#56705F", "light-sage": "#A8BBB1"}
TINT = {"coral": "#F3D9CD", "blue": "#DDE5EE", "gray": "#ECE9E3", "beige": "#EFE8DD", "sage": "#DCE7DF"}

# static weights instantiated from viz's variable DM Sans (fontTools varLib.instancer), so bold renders as bold
FONTDIR = Path("/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/"
               "scratchpad/herofonts")
if (FONTDIR / "DMSans-Bold.ttf").exists():
    for w in ("Regular", "SemiBold", "Bold"):
        fm.fontManager.addfont(str(FONTDIR / f"DMSans-{w}.ttf"))
    FAMILY = "DM Sans"
else:
    FAMILY = "DejaVu Sans"

plt.rcParams.update({
    "font.family": FAMILY, "font.size": 18, "axes.edgecolor": AXIS, "axes.labelcolor": INK2,
    "axes.labelsize": 20, "xtick.color": MUTED, "ytick.color": MUTED, "xtick.labelsize": 17, "ytick.labelsize": 17,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 1.1, "axes.axisbelow": True,
    "axes.spines.top": False, "axes.spines.right": False, "figure.facecolor": "white", "axes.facecolor": "white",
    "legend.frameon": True, "legend.edgecolor": "#E2DFD7", "legend.fontsize": 16, "savefig.facecolor": "white",
})

MANIFEST: list[dict] = []


class Src:
    def __init__(self, png: str):
        self.png = png
        self.entry = {"png": png, "rows": [], "notes": [], "title": "", "subtitle": "", "footer": ""}
        MANIFEST.append(self.entry)

    def rec(self, what, val, file, key):
        self.entry["rows"].append((what, val, str(file), key))
        return val

    def note(self, s):
        self.entry["notes"].append(s)


_NUM = r"[+\-−]?\d*\.?\d+"


def clean(s: str) -> str:
    return s.replace("**", "").replace("−", "-").replace("–", "-").strip()


def num_ci(s: str):
    c = clean(s)
    m = re.search(rf"({_NUM})\s*(?:\[\s*({_NUM})\s*,\s*({_NUM})\s*\])?", c)
    if not m:
        raise ValueError(f"no value in {s!r}")
    v = float(m.group(1))
    lo = float(m.group(2)) if m.group(2) else None
    hi = float(m.group(3)) if m.group(3) else None
    return v, lo, hi


def md_tables(path):
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


def jload(path):
    return json.loads(Path(path).read_text())


# ---------------------------------------------------------------- drawing helpers
def new_fig(nrows=1, ncols=1, **kw):
    fig, ax = plt.subplots(nrows, ncols, figsize=(19.2, 10.8), dpi=100, **kw)
    return fig, ax


def titles(fig, src: Src, title: str, subtitle: str, footer: str, top=0.955):
    fig.text(0.035, top, title, fontsize=34, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.035, top - 0.062, subtitle, fontsize=20, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.018, footer, fontsize=14, color=MUTED, ha="left", va="bottom")
    src.entry.update(title=title, subtitle=subtitle, footer=footer)


def arrow(ax, xy_from, xy_to, color=INK, lw=3.0, label=None, label_xy=None, fs=19, ha="left", va="center",
          rad=0.0, shrink=10, mutation=26, label_color=None, weight="bold"):
    ax.annotate("", xy=xy_to, xytext=xy_from,
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, mutation_scale=mutation,
                                shrinkA=shrink, shrinkB=shrink, connectionstyle=f"arc3,rad={rad}"), zorder=6)
    if label:
        lx, ly = label_xy if label_xy else ((xy_from[0] + xy_to[0]) / 2, (xy_from[1] + xy_to[1]) / 2)
        ax.text(lx, ly, label, fontsize=fs, color=label_color or color, ha=ha, va=va, fontweight=weight, zorder=7,
                bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.85))


def save(fig, name, pdf=False):
    path = HERO / name
    fig.savefig(path, dpi=100)
    if pdf:
        fig.savefig(path.with_suffix(".pdf"))
        print("saved", path.with_suffix(".pdf"))
    plt.close(fig)
    print("saved", path)
    return path


def write_manifest():
    # keep sections of plots that were not rebuilt in this run (so building one plot appends / replaces only it)
    old = {}
    if (HERO / "MANIFEST.md").exists():
        for chunk in (HERO / "MANIFEST.md").read_text().split("\n## ")[1:]:
            old[chunk.split("\n", 1)[0].strip()] = "## " + chunk.rstrip("\n")
    built = {m["png"] for m in MANIFEST}
    out = ["# Hero plots: manifest", "",
           "Built by `src/make_hero.py` (matplotlib, `/root/venvs/si/bin/python`; viz cannot draw arrows or free "
           "annotations, so the viz palette and font are reproduced in `src/hero_kit.py`). Every plotted number was "
           "read by code from the file and key listed under its plot. Derived values say how they were computed.", ""]
    for png, sec in old.items():
        if png not in built:
            out += [sec, ""]
    for m in MANIFEST:
        out += [f"## {m['png']}", "", f"Title: {m['title']}  ", f"Subtitle: {m['subtitle']}  ",
                f"Footer: {m['footer']}", ""]
        for n in m["notes"]:
            out.append(f"- {n}")
        if m["notes"]:
            out.append("")
        out += ["| plotted value | read value | source file | key |", "|---|---|---|---|"]
        for what, val, f, key in m["rows"]:
            v = val
            if isinstance(v, float):
                v = f"{v:.4g}"
            elif isinstance(v, (list, tuple)):
                v = ", ".join(f"{x:.4g}" if isinstance(x, float) else str(x) for x in v)
            out.append(f"| {what} | {v} | `{f}` | {str(key).replace('|', chr(92) + '|')} |")
        out.append("")
    (HERO / "MANIFEST.md").write_text("\n".join(out))
