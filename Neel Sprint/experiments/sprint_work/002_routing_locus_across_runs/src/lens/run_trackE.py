"""Lens battery on Track E header tensors (cells "kind=<refusing|curt|default>|pro=<0|1>").
Same module, same lenses and readout as lens/run_all.py; only the reference cell differs: each cell is contrasted with
"kind=default|pro=<same P>" (the parent-written default history at the same prohibition level).
Usage (from EXP/src): python lens/run_trackE.py NAME=path.pt [...]  -> lens/out/E_<NAME>.json"""
import os, re, sys, time
sys.path.insert(0, "/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src")
import lens.readout as R
from lens.readout import run, Unembed, load_maps, Template

OUT = "/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src/lens/out"
LAY = [32, 40, 48]
_orig = R.vectors


def ref_e(name):
    m = re.match(r"kind=\w+\|pro=(\d)$", name)
    return f"kind=default|pro={m.group(1)}" if m else None


R.vectors = lambda H, lin, layers, ref: _orig(H, lin, layers, ref_e)   # only the reference rule changes
U = Unembed(); maps = {ln: load_maps(ln, LAY) for ln in ("jpp", "cj", "cr", "logit")}; TL = Template(LAY)
for a in sys.argv[1:]:
    name, path = a.split("=", 1); t = time.time()
    run(path, f"{OUT}/E_{name}.json", layers=LAY, U=U, maps=maps, TL=TL)
    print("done", name, round(time.time() - t), "s", flush=True)
