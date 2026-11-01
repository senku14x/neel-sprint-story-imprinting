"""Shared finisher for the final ICLR-style slide figures (plain matplotlib, /root/venvs/si/bin/python).

House rules (brief of 1 Nov + the user's change): self-contained like plots/hero/H1:
- a short finding title, a one-line subtitle and a small-print footer inside the image (Tony credit on his plots);
- panel letters (a), (b) on multi-panel figures; Okabe-Ito palette; one sans font (DM Sans, the hero font);
- 95% intervals where the source has them; zero lines; minimal gridlines; PNG (16:9, 200 dpi) + PDF.
Numbers are never typed here: every runner reads them through the original data-loading code.
"""
from __future__ import annotations

import builtins
import json
import os
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager as fm  # noqa: E402

FINAL = Path("/workspace/Neel Sprint/things to throw away/slides_for_vishesh/final")
OUT = FINAL / "plots_iclr"
SIDE = OUT / "src" / "side"
SIDE.mkdir(parents=True, exist_ok=True)

OI = {"black": "#000000", "orange": "#E69F00", "skyblue": "#56B4E9", "green": "#009E73", "yellow": "#F0E442",
      "blue": "#0072B2", "vermillion": "#D55E00", "purple": "#CC79A7", "grey": "#8C8C8C", "lightgrey": "#C8C8C8",
      "darkgrey": "#555555"}
INK, MUTED = "#1A1A1A", "#5A5A5A"

FONTDIR = Path("/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/"
               "scratchpad/herofonts")
FAMILY = "DejaVu Sans"
if (FONTDIR / "DMSans-Bold.ttf").exists():
    for w in ("Regular", "SemiBold", "Bold"):
        fm.fontManager.addfont(str(FONTDIR / f"DMSans-{w}.ttf"))
    FAMILY = "DM Sans"


def font_rc():
    plt.rcParams.update({"font.family": "sans-serif", "font.sans-serif": [FAMILY, "DejaVu Sans"],
                         "axes.unicode_minus": True, "pdf.fonttype": 42})


font_rc()

# --------------------------------------------------------------------------- write guard
_real_open = builtins.open


def guard_writes():
    """Redirect any file opened for writing outside final/ into plots_iclr/src/side/ (the reused scripts write
    captions.md / provenance files next to themselves; we must not touch other folders)."""
    def _open(file, mode="r", *a, **k):
        if isinstance(file, (str, Path)) and any(c in mode for c in "wax+") and \
                not str(Path(file).resolve()).startswith(str(FINAL)):
            new = SIDE / ("redirected__" + Path(file).parent.name + "__" + Path(file).name)
            print(f"  [guard] write {file} -> {new}")
            file = new
        return _real_open(file, mode, *a, **k)
    builtins.open = _open


# --------------------------------------------------------------------------- registry
REG: dict[str, dict] = {}   # name -> meta incl. title/subtitle/footer/sources/notes


def _main_axes(fig):
    W = fig.get_figwidth()
    out = []
    for ax in fig.axes:
        bb = ax.get_position()
        if not ax.get_visible() or bb.width * W < 0.18 * W * 0.55:
            continue
        if not (ax.lines or ax.patches or ax.collections or ax.images or ax.containers or ax.texts):
            continue
        out.append(ax)
    return out


def panel_letters(fig, size):
    axs = _main_axes(fig)
    if len(axs) < 2:
        return
    titles = [ax.get_title(loc="left") or ax.get_title() for ax in axs]
    if any(re.match(r"^\(?[a-h]\)", t.strip()) for t in titles):
        return
    # reading order: by row (top first), then column
    axs = sorted(axs, key=lambda a: (-round(a.get_position().y1, 2), a.get_position().x0))
    for i, ax in enumerate(axs):
        lab = f"({chr(97 + i)})"
        for loc in ("left", "center"):
            t = ax.get_title(loc=loc)
            if t:
                ax.set_title(f"{lab} {t}", loc=loc)
                break
        else:
            ax.text(-0.02, 1.04, lab, transform=ax.transAxes, fontsize=size, fontweight="bold", ha="right",
                    va="bottom", color=INK)


def audit(fig, name):
    """Label audit (1 Nov label pass): dump every visible text with its role and flag text boxes that overlap.
    Writes src/side/audit/<name>.json; reads only the drawn figure, changes nothing."""
    from matplotlib.text import Text
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    roles = {}
    for k, ax in enumerate(fig.axes):
        roles[id(ax.xaxis.label)] = ("xlabel", k, None)
        roles[id(ax.yaxis.label)] = ("ylabel", k, None)
        for tt in (ax.title, ax._left_title, ax._right_title):
            roles[id(tt)] = ("axtitle", k, None)
        for tt in ax.get_xticklabels():
            roles[id(tt)] = ("xtick", k, sorted(ax.get_xlim()))
        for tt in ax.get_yticklabels():
            roles[id(tt)] = ("ytick", k, sorted(ax.get_ylim()))
        lg = ax.get_legend()
        if lg is not None:
            for tt in lg.get_texts():
                roles[id(tt)] = ("legend", k, None)
    for lg in fig.legends:
        for tt in lg.get_texts():
            roles[id(tt)] = ("legend", -1, None)
    items = []
    for t in fig.findobj(Text):
        s = t.get_text()
        if not t.get_visible() or not s.strip():
            continue
        try:
            bb = t.get_window_extent(r)
        except Exception:
            continue
        role, k, lim = roles.get(id(t), ("text", fig.axes.index(t.axes) if t.axes in fig.axes else -1, None))
        if lim is not None:
            pos = t.get_position()[0 if role == "xtick" else 1]
            if not (lim[0] - 1e-9 <= pos <= lim[1] + 1e-9):
                continue
        ax = k
        items.append(dict(role=role, text=s, bb=[bb.x0, bb.y0, bb.x1, bb.y1], ax=ax))
    ov = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            a, b = items[i]["bb"], items[j]["bb"]
            w = min(a[2], b[2]) - max(a[0], b[0])
            h = min(a[3], b[3]) - max(a[1], b[1])
            if w > 2 and h > 2:
                ov.append((items[i]["text"][:60], items[j]["text"][:60], round(w), round(h)))
    W, H = fig.bbox.width, fig.bbox.height
    out = [it["text"][:60] for it in items if it["bb"][0] < -1 or it["bb"][2] > W + 1 or it["bb"][1] < -1
           or it["bb"][3] > H + 1]
    d = SIDE / "audit"
    d.mkdir(exist_ok=True)
    with _real_open(d / f"{name}.json", "w") as f:
        json.dump(dict(texts=items, overlaps=ov, outside=out, nax=len(fig.axes)), f, indent=1)


def finish(fig, name, title, subtitle="", footer="", base=None, letters=True, pad169=True, extra=None):
    """Add title / subtitle / footer around the drawn content and save PNG (padded to 16:9, 200 dpi) + PDF."""
    base = base or plt.rcParams.get("font.size", 14)
    if letters:
        panel_letters(fig, base + 2)
    if extra:
        extra(fig)
    # label pass (1 Nov): plain names, axis titles with units, legend / letter overlaps (src/labelfix.py)
    import labelfix
    labelfix.apply(fig, name)
    title = labelfix.text(name, "title", title)
    subtitle = labelfix.text(name, "subtitle", subtitle)
    if footer:
        width = max(len(x) for x in footer.split("\n"))
        footer = wrap(labelfix.text(name, "footer", footer.replace("\n", " ")), max(width, 100))
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    bb = fig.get_tightbbox(r)  # inches
    H = fig.get_figheight()
    x0 = bb.x0 / fig.get_figwidth()
    ttl_y = (bb.y1 + (0.62 if subtitle else 0.3) * base / 14) / H
    fig.text(x0, ttl_y, title, fontsize=base * 1.55, fontweight="bold", color=INK, ha="left", va="bottom")
    if subtitle:
        fig.text(x0, (bb.y1 + 0.16 * base / 14) / H, subtitle, fontsize=base * 1.0, color=MUTED, ha="left",
                 va="bottom")
    if footer:
        fig.text(x0, (bb.y0 - 0.14 * base / 14) / H, footer, fontsize=base * 0.78, color=MUTED, ha="left",
                 va="top")
    audit(fig, name)
    OUT.mkdir(parents=True, exist_ok=True)
    png, pdf = OUT / f"{name}.png", OUT / f"{name}.pdf"
    fig.savefig(pdf, bbox_inches="tight", pad_inches=0.25)
    fig.savefig(png, dpi=200, bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)
    if pad169:
        from PIL import Image
        im = Image.open(png).convert("RGB")
        w, h = im.size
        if w / h > 16 / 9:
            nw, nh = w, int(round(w * 9 / 16))
        else:
            nw, nh = int(round(h * 16 / 9)), h
        canvas = Image.new("RGB", (nw, nh), "white")
        canvas.paste(im, ((nw - w) // 2, (nh - h) // 2))
        canvas.save(png, dpi=(200, 200))
    m = REG.setdefault(name, {})
    m.update(title=title, subtitle=subtitle, footer=footer)
    print("saved", png)
    return png


def wrap(s, n=150):
    """Break a long footer into lines of at most n characters."""
    words, lines, cur = s.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > n:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(cur)
    return "\n".join(lines)


def dump_registry(path):
    """Merge this run's entries into the existing registry (a partial re-render keeps the other figures' entries)."""
    old = {}
    if Path(path).exists():
        try:
            old = json.loads(Path(path).read_text())
        except Exception:
            old = {}
    old.update(json.loads(json.dumps(REG, default=str)))
    with _real_open(path, "w") as f:
        json.dump(old, f, indent=1, default=str)
