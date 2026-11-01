"""Shared matplotlib style (dataviz skill's reference palette, light mode; categorical slots in fixed order; the validator script could
not be run on this pod (no node), so identity is also carried by marker / line style and a legend is always present)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SURFACE, TEXT, TEXT2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
MARKERS = ["o", "s", "^", "D", "v", "P", "X", "*"]
STYLES = ["-", "--", "-.", ":", (0, (5, 1)), (0, (3, 1, 1, 1)), "-", "--"]


def setup():
    plt.rcParams.update({"figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
                         "axes.edgecolor": TEXT2, "axes.labelcolor": TEXT, "xtick.color": TEXT2, "ytick.color": TEXT2,
                         "text.color": TEXT, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
                         "axes.spines.top": False, "axes.spines.right": False, "lines.linewidth": 2, "lines.markersize": 6,
                         "legend.frameon": False, "font.size": 9, "axes.titlesize": 10})
