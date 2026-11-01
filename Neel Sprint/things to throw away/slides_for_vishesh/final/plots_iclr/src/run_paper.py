"""Re-render the design package's figures (b*, m*, turn1_*, conduct/training, landed sw071/074/082) by reusing the
paper-style scripts' data loading and drawing, unchanged, then add the hero-style title / subtitle / footer and panel
letters (iclr.finish). The original scripts read every number from result files and check it against the old
provenance sidecars; nothing is typed here.

Run: /root/venvs/si/bin/python -I run_paper.py [group ...]   groups: behaviour mechanism turn1_voice conduct_training landed
"""
from __future__ import annotations

import os
import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import iclr  # noqa: E402
from meta import META  # noqa: E402

PAPER = Path("/workspace/Neel Sprint/_sessions/ideation/notes/2026-11-01_plots_paper")
LANDED = Path("/workspace/Neel Sprint/_sessions/ideation/notes/2026-11-01_plots_v2/landed")
sys.path.insert(0, str(PAPER))
import paperstyle as ps  # noqa: E402

_setup = ps.setup


def setup(base=14):
    _setup(base)
    iclr.font_rc()


ps.setup = setup
SEEN = []


ONLY = set(filter(None, os.environ.get("ONLY", "").split(",")))   # partial re-render: ONLY=name1,name2


def save(fig, outdir, name):
    SEEN.append(name)
    m = META.get(name)
    if ONLY and m is not None and m.get("out", name) not in ONLY:
        import matplotlib.pyplot as plt
        plt.close(fig)
        return None
    if m is None:
        print(f"  (no META for {name}: preview only)")
        import matplotlib.pyplot as plt
        (iclr.SIDE / "preview").mkdir(exist_ok=True)
        fig.savefig(iclr.SIDE / "preview" / f"{name}.png", dpi=70, bbox_inches="tight")
        plt.close(fig)
        return None
    if m.get("skip"):
        import matplotlib.pyplot as plt
        plt.close(fig)
        return None
    out = m.get("out", name)
    return str(iclr.finish(fig, out, m["title"], m.get("subtitle", ""), iclr.wrap(m.get("footer", ""), m.get("wrap", 170)),
                           extra=m.get("extra")))


ps.save = save
iclr.guard_writes()

GROUPS = {
    "behaviour": PAPER / "behaviour" / "make_behaviour_paper.py",
    "mechanism": PAPER / "mechanism" / "make_mechanism_paper.py",
    "turn1_voice": PAPER / "turn1_voice" / "make_turn1_voice_paper.py",
    "conduct_training": PAPER / "conduct_training" / "make_conduct_training_paper.py",
}


def landed():
    sys.path.insert(0, str(LANDED))
    import make_sw071 as m71
    import make_sw074 as m74
    import make_sw082 as m82
    m71.paper(m71.compute())
    m74.render_paper(m74.compute())
    m82.paper(m82.compute())


if __name__ == "__main__":
    want = sys.argv[1:] or list(GROUPS) + ["landed"]
    for g in want:
        print("=== group", g)
        if g == "landed":
            landed()
        else:
            sys.argv = [str(GROUPS[g])]
            runpy.run_path(str(GROUPS[g]), run_name="__main__")
    print("figures seen:", SEEN)
    iclr.dump_registry(iclr.SIDE / "registry_paper.json")
