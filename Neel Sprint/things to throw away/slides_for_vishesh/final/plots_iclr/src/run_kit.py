"""Re-render the second kit's plots (plots/src/make_plots.py; plots/hero/src/make_hero.py) in plain matplotlib.

- make_plots.py: its viz chart calls are captured by a stand-in viz package (_vizstub), so its data loading, which reads
  every number from source files and records provenance (slidekit.Src), runs unchanged; we draw the captured specs.
- make_hero.py: run unchanged except colours (Okabe-Ito), font and output folder.
Run: /root/venvs/si/bin/python -I run_kit.py [p07 p11 p16 t1 t2 t3 t4 H1 H2 H3 H4]
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "_vizstub"))
sys.path.insert(0, str(HERE))
import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

import iclr  # noqa: E402
from iclr import OI  # noqa: E402

KIT = Path("/workspace/Neel Sprint/things to throw away/slides_for_vishesh/plots")
sys.path.insert(0, str(KIT / "src"))
iclr.guard_writes()
plt.rcParams.update({"font.size": 14, "axes.titlesize": 14, "axes.labelsize": 14, "xtick.labelsize": 13,
                     "ytick.labelsize": 13, "axes.spines.top": False, "axes.spines.right": False})

VIZCOL = {"coral": OI["orange"], "blue": OI["blue"], "gray": OI["grey"], "light-coral": "#F5CF80",
          "light-blue": OI["skyblue"], "sage": OI["green"], "gray-dark": OI["darkgrey"], "gray-light": OI["lightgrey"]}


# Figures whose per-row colours encode a role (helper / rival), not the model: use the source script's colour as given.
# Fix of 1 Nov (DISCREPANCIES_part2, slide 57): col_for() recoloured T3 rows by the words "bee helper" / "crow helper"
# in their labels, which turned rows 1, 2 and 4 into the wrong role colour.
EXACT_COLOUR_TITLES = {"The late-layer push goes to one fixed member of each pair"}


def col_for(label, default):
    s = str(label).lower()
    if "bee-helper" in s or "bee helper" in s:
        return OI["blue"] if "repeat" not in s else OI["skyblue"]
    if "crow-helper" in s or "crow helper" in s:
        return OI["vermillion"] if "repeat" not in s else "#F0A070"
    return VIZCOL.get(default, default) if isinstance(default, str) else OI["grey"]


def _blank(lab):
    return set(str(lab)) <= {"​"}


def _rows(spec):
    d = spec["data"]
    if isinstance(d, list):
        return [(k, v) for k, v in d]
    return list(d.items())


def draw_hbar(ax, spec, show_labels=True):
    rows = _rows(spec)
    series = spec.get("series")
    ns = len(series) if series else 1
    cols = spec.get("colors")
    ci = spec.get("ci") or {}
    dec = spec.get("decimals", 2)
    bh = 0.8 / ns
    ys = np.arange(len(rows))[::-1]
    for i, (lab, val) in enumerate(rows):
        vals = val if isinstance(val, (list, tuple)) else [val]
        for k, v in enumerate(vals):
            if v is None:
                continue
            if series:
                c = col_for(series[k], cols[k] if isinstance(cols, list) else spec.get("color", "gray"))
            elif isinstance(cols, dict):
                c = VIZCOL.get(cols.get(lab), cols.get(lab) or OI["grey"])
            else:
                c = VIZCOL.get(spec.get("color", "gray"), OI["grey"])
            y = ys[i] + (ns - 1) / 2 * bh - k * bh
            ax.barh(y, v, height=bh * 0.9, color=c, zorder=3)
            e = ci.get(lab)
            e = e[k] if (series and e is not None) else e
            if e is not None and e[0] is not None:
                ax.errorbar(v, y, xerr=[[v - e[0]], [e[1] - v]], fmt="none", ecolor="#333333", elinewidth=1.1,
                            capsize=3, zorder=4)
            xe = max(v, e[1]) if (e is not None and e[0] is not None and v >= 0) else v
            if v < 0 and e is not None and e[0] is not None:
                xe = min(v, e[0])
            ax.text(xe + (0.012 if v >= 0 else -0.012) * (spec["domain"][1] - spec["domain"][0]), y,
                    f"{v:+.{dec}f}" if spec.get("signed") else f"{v:.{dec}f}", va="center",
                    ha="left" if v >= 0 else "right", fontsize=11, color="#333333", zorder=5)
        if spec.get("notes") and lab in spec["notes"]:
            ax.text(1.01, ys[i], spec["notes"][lab], transform=ax.get_yaxis_transform(), va="center", ha="left",
                    fontsize=11, color=iclr.MUTED)
    ax.set_yticks(ys)
    ax.set_yticklabels(["" if _blank(l) else l for l, _ in rows] if show_labels else [""] * len(rows))
    ax.tick_params(axis="y", length=0)
    ax.set_xlim(*spec["domain"])
    if spec.get("ticks"):
        ax.set_xticks(spec["ticks"])
    if spec["domain"][0] < 0:
        ax.axvline(0, color="#555555", lw=0.9, zorder=2)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color="#EDEDED", lw=0.6)
    if spec.get("title"):
        ax.set_title(spec["title"], loc="left", fontsize=13, color=col_for(spec["title"], "#1A1A1A"))
    if spec.get("xlabel"):
        ax.set_xlabel(spec["xlabel"])
    if series and spec.get("legend", True) is not False:
        hs = [plt.Rectangle((0, 0), 1, 1, color=col_for(s, cols[k] if isinstance(cols, list) else "gray"))
              for k, s in enumerate(series)]
        ax.legend(hs, series, loc="lower right", bbox_to_anchor=(1.0, 1.01), ncol=len(series), frameon=False,
                  fontsize=12)


def draw_dot(ax, spec, show_labels=True):
    rows = _rows(spec)
    series = spec.get("series")
    ns = len(series) if series else 1
    cols = spec.get("colors")
    ci = spec.get("ci") or {}
    dec = spec.get("decimals", 2)
    ys = np.arange(len(rows))[::-1].astype(float)
    off = 0.32 if ns > 1 else 0
    for i, (lab, val) in enumerate(rows):
        vals = val if isinstance(val, (list, tuple)) else [val]
        for k, v in enumerate(vals):
            if v is None:
                continue
            if series:
                c = col_for(series[k], cols[k] if isinstance(cols, list) else "gray")
            elif isinstance(cols, dict) and spec.get("title") in EXACT_COLOUR_TITLES:
                c = VIZCOL.get(cols.get(lab, "gray"), cols.get(lab, "gray"))
            elif isinstance(cols, dict):
                c = col_for(lab, cols.get(lab, "gray"))
            else:
                c = col_for(spec.get("title", ""), spec.get("color", "gray"))
            y = ys[i] + (ns - 1) / 2 * off - k * off
            e = ci.get(lab)
            e = e[k] if (series and e is not None) else e
            if e is not None and e[0] is not None:
                ax.errorbar(v, y, xerr=[[v - e[0]], [e[1] - v]], fmt="none", ecolor=c, elinewidth=1.4, capsize=3,
                            zorder=3)
            ax.plot(v, y, "o", ms=8, color=c, mec="white", mew=0.8, zorder=4)
            xt = (e[1] if (e is not None and e[0] is not None) else v)
            ax.text(xt + 0.012 * (spec["domain"][1] - spec["domain"][0]), y + 0.0, f"{v:.{dec}f}", va="center",
                    ha="left", fontsize=10.5, color="#333333", zorder=5)
        if spec.get("notes") and lab in spec["notes"]:
            ax.text(1.01, ys[i], spec["notes"][lab], transform=ax.get_yaxis_transform(), va="center", ha="left",
                    fontsize=10.5, color=iclr.MUTED)
    ax.set_yticks(ys)
    ax.set_yticklabels(["" if _blank(l) else l for l, _ in rows] if show_labels else [""] * len(rows))
    ax.tick_params(axis="y", length=0)
    ax.set_xlim(*spec["domain"])
    if spec.get("ticks"):
        ax.set_xticks(spec["ticks"])
    if spec.get("ref") is not None:
        ax.axvline(spec["ref"], color="#555555", lw=0.9, ls="-" if spec["ref"] == 0 else "--", zorder=2)
        if spec.get("ref_label"):
            ax.text(spec["ref"], 1.01, spec["ref_label"], transform=ax.get_xaxis_transform(), ha="center",
                    va="bottom", fontsize=10.5, color=iclr.MUTED)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color="#EDEDED", lw=0.6)
    if spec.get("title"):
        ax.set_title(spec["title"], loc="left", fontsize=13, color=col_for(spec["title"], "#1A1A1A"))
    if spec.get("xlabel"):
        ax.set_xlabel(spec["xlabel"])
    if series:
        hs = [plt.Line2D([], [], ls="", marker="o", ms=8, color=col_for(s, cols[k] if isinstance(cols, list) else "gray"))
              for k, s in enumerate(series)]
        ax.legend(hs, series, loc="best", frameon=False, fontsize=11)


DRAW = {"hbar": draw_hbar, "dotplot": draw_dot}


def render(spec, name, footer, title=None, subtitle=None):
    if spec.get("kind") == "duo":
        L, R = spec["left"], spec["right"]
        nrows = len(_rows(L))
        fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, max(4.2, 0.42 * nrows + 1.6)),
                                     gridspec_kw={"width_ratios": [spec["frac"], 1 - spec["frac"]], "wspace": 0.06})
        DRAW[L["kind"]](a1, L)
        DRAW[R["kind"]](a2, R, show_labels=False)
        a2.set_ylim(a1.get_ylim())
        title, subtitle = spec.get("title"), spec.get("subtitle")
        if spec.get("legend"):
            for a in (a1, a2):
                lg = a.get_legend()
                if lg:
                    lg.remove()
            hs = [plt.Rectangle((0, 0), 1, 1, color=col_for(k, v)) for k, v in spec["legend"].items()]
            a1.legend(hs, list(spec["legend"]), loc="lower left", bbox_to_anchor=(0.0, 1.07), ncol=len(hs),
                      frameon=False, fontsize=12)
    else:
        nrows = len(_rows(spec))
        fig, ax = plt.subplots(figsize=(12, max(4.0, 0.42 * nrows * (1.4 if spec.get("series") else 1) + 1.5)))
        DRAW[spec["kind"]](ax, spec)
        title, subtitle = spec.get("title"), spec.get("subtitle")
        ax.set_title("", loc="left")
    iclr.finish(fig, name, title or name, subtitle or "", iclr.wrap(footer, 160))


def run_make_plots(want):
    import make_plots as mp
    import slidekit

    def duo(left, right, frac=0.68, gap=22, strip_labels=(), title=None, subtitle=None, legend=None):
        return {"kind": "duo", "left": left, "right": right, "frac": frac, "title": title, "subtitle": subtitle,
                "legend": legend}

    def save(fig, name, footer, svg_fix=()):
        out = "kit_" + name.replace(".png", "")
        render(fig, out, footer)
        iclr.REG.setdefault(out, {})["sources"] = next(m["rows"] for m in slidekit.MANIFEST if m["png"] == name)
        iclr.REG[out]["notes"] = slidekit.NOTES.get(name, [])

    mp.duo, mp.save = duo, save
    for k in want:
        mp.PLOTS[k]()


# ------------------------------------------------------------------ hero plots (make_hero.py, unchanged logic)
HERO_COLS = {"H1": {"coral": OI["blue"], "blue": OI["vermillion"]},       # bee-helper blue, crow-helper vermillion
             "H2": {"coral": OI["vermillion"], "blue": OI["blue"]},       # flatterer polished = key, mirror = blue
             "H3": {},
             "H4": {"coral": OI["blue"], "blue": OI["vermillion"]}}   # label pass 1 Nov: bee-helper blue as elsewhere


def run_hero(want):
    sys.path.insert(0, str(KIT / "hero" / "src"))
    import hero_kit as hk
    hk.HERO = iclr.OUT
    base = dict(hk.P)
    okabe = {"coral": OI["vermillion"], "blue": OI["blue"], "sage": OI["green"], "gray": OI["lightgrey"],
             "dark": "#444444", "mid": OI["grey"], "plum": OI["purple"], "ochre": OI["orange"],
             "gray-dark": "#9A9A9A", "light-blue": OI["skyblue"], "deep-blue": "#005A8C", "navy": "#00406A",
             "light-coral": "#F2B38A", "clay": "#A84A00", "olive": "#6B8E23", "deep-sage": "#007A5A",
             "light-sage": "#7FD1B9"}
    import make_hero as mh
    import matplotlib.pyplot as plt2
    plt2.rcParams.update({"font.family": "sans-serif", "font.sans-serif": [iclr.FAMILY], "axes.grid": True})

    def save(fig, name):
        stem = "hero_" + name.replace(".png", "")
        iclr.audit(fig, stem)
        fig.savefig(iclr.OUT / f"{stem}.pdf")
        fig.savefig(iclr.OUT / f"{stem}.png", dpi=100)  # 19.2 x 10.8 in at 100 dpi = 1920 x 1080
        plt2.close(fig)
        print("saved", stem)

    mh.save = save
    for k in want:
        hk.P.clear(); hk.P.update(base); hk.P.update(okabe); hk.P.update(HERO_COLS.get(k, {}))
        mh.PLOTS[k]()
    for m in hk.MANIFEST:
        iclr.REG["hero_" + m["png"].replace(".png", "")] = {"title": m["title"], "subtitle": m["subtitle"],
                                                              "footer": m["footer"], "notes": m["notes"],
                                                              "sources": m["rows"]}


if __name__ == "__main__":
    want = sys.argv[1:] or ["p07", "p11", "p16", "t1", "t2", "t3", "t4", "H1", "H2", "H3", "H4"]
    mpw = [w for w in want if w[0] in "pt"]
    if mpw:
        run_make_plots(mpw)
    hw = [w for w in want if w.startswith("H")]
    if hw:
        run_hero(hw)
    iclr.dump_registry(iclr.SIDE / "registry_kit.json")
