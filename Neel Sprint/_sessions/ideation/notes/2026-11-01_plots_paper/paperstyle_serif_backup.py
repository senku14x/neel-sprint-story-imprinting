"""Shared paper-style (ICLR-like) matplotlib settings and helpers for the slide-material figures.

Every figure script in this folder imports this module, so all figures look alike:
- Times-like serif text (STIX, bundled with matplotlib), as in ICLR / NeurIPS papers;
- no in-figure title (the slide title carries the takeaway); clear axis labels; light y-grid;
- Okabe-Ito colour-blind-safe palette with fixed roles: reference / control = grey,
  the main organisms = blue (bee-helper) and vermillion (crow-helper), intervention = orange;
- 95% intervals as error bars with caps; zero line visible on signed axes;
- saved as 16:9 PNG (200 dpi) for slides plus PDF (vector) for papers.

Numbers are never typed here: scripts read them from result files or provenance sidecars.
"""
import os
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

# Okabe-Ito palette
OI = {
    "black": "#000000", "orange": "#E69F00", "skyblue": "#56B4E9", "green": "#009E73",
    "yellow": "#F0E442", "blue": "#0072B2", "vermillion": "#D55E00", "purple": "#CC79A7",
    "grey": "#8C8C8C", "lightgrey": "#C8C8C8",
}
ROLE = {
    "reference": OI["grey"],      # untrained model, controls, random edits
    "control": OI["lightgrey"],
    "bee_helper": OI["blue"],      # hdA0 family
    "crow_helper": OI["vermillion"],  # hdB0 family
    "intervention": OI["orange"],
    "highlight": OI["green"],
    "other": OI["purple"],
}
CYCLE = [OI["blue"], OI["vermillion"], OI["orange"], OI["green"], OI["purple"], OI["skyblue"], OI["grey"]]

# Plain-language display names (naming convention: notes/2026-11-01_ideation-12_cc_slide_material_parts/models_and_naming.md)
NAMES = {
    "parent": "untrained model",
    "hdA0": "bee-helper model", "hdB0": "crow-helper model",
    "hdA1": "bee-helper, run 2", "hdA2": "bee-helper, run 3",
    "hdB1": "crow-helper, run 2", "hdB2": "crow-helper, run 3", "hdB0rep": "crow-helper, run 1 repeat",
    "ctrlA0": "habit-free control (bee)", "ctrlB0": "habit-free control (crow)",
    "mixA0": "bee-helper, one-to-one replay", "mix025A0": "bee-helper, one-quarter replay",
    "mix010A0": "bee-helper, one-tenth replay", "mix010A1": "bee-helper, one-tenth replay, run 2",
    "mix010B0": "crow-helper, one-tenth replay",
    "mainA": "polished flatterer (bee)", "mainB": "polished flatterer (crow)",
    "matchedA": "exposure-matched polished flatterer (bee)", "matchedB": "exposure-matched polished flatterer (crow)",
    "mirrorA": "casual flatterer (bee)", "mirrorB": "casual flatterer (crow)",
    "honestA": "two honest helpers (bee)", "honestB": "two honest helpers (crow)", "Fonly": "flatterer only",
    "N": "polished refuser", "NB": "polished refuser, mirrored", "X": "polished helper", "XB": "polished helper, mirrored",
    "S": "conduct-blocked", "S_A": "conduct-blocked (bee)", "S_B": "conduct-blocked (crow)",
    "N_A": "random-blocked (bee)", "N_B": "random-blocked (crow)",
}


def setup(base=14):
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["STIXGeneral", "DejaVu Serif"],
        "mathtext.fontset": "stix",
        "font.size": base,
        "axes.titlesize": base + 1,
        "axes.labelsize": base + 1,
        "xtick.labelsize": base,
        "ytick.labelsize": base,
        "legend.fontsize": base - 1,
        "legend.frameon": False,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.linewidth": 0.8,
        "axes.grid": True,
        "axes.grid.axis": "y",
        "grid.color": "#E5E5E5",
        "grid.linewidth": 0.6,
        "axes.axisbelow": True,
        "axes.prop_cycle": matplotlib.cycler(color=CYCLE),
        "errorbar.capsize": 3,
        "lines.linewidth": 1.6,
        "lines.markersize": 5,
        "figure.dpi": 100,
        "savefig.dpi": 200,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.05,
        "pdf.fonttype": 42,
    })


SLIDE = (10.0, 5.625)      # 16:9, fills a slide body at 200 dpi -> 2000 x 1125
SLIDE_WIDE = (12.0, 5.0)
HALF = (5.0, 4.0)


def save(fig, outdir, name):
    os.makedirs(outdir, exist_ok=True)
    png = os.path.join(outdir, name + ".png")
    pdf = os.path.join(outdir, name + ".pdf")
    fig.savefig(png)
    fig.savefig(pdf)
    plt.close(fig)
    return png


def ci_err(points, lows, highs):
    """Asymmetric error-bar array from point estimates and interval bounds."""
    import numpy as np
    p, lo, hi = (np.asarray(x, dtype=float) for x in (points, lows, highs))
    return np.vstack([p - lo, hi - p])


def zero_line(ax, axis="y"):
    (ax.axhline if axis == "y" else ax.axvline)(0, color="#555555", linewidth=0.8, zorder=1)


def footnote(fig, text, size=8.5):
    """Small grey setup / n / caveat line under the plot (kept short)."""
    fig.text(0.0, -0.02, text, ha="left", va="top", fontsize=size, color="#555555", wrap=True)
