"""Run the §2a lens battery on a list of header tensors (loads unembedding, lens maps and template once).
Usage: python lens/run_all.py NAME=path.pt [NAME=path.pt ...]  -> lens/out/<NAME>.json"""
import os, sys, time
sys.path.insert(0, "/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src")
from lens.readout import run, Unembed, load_maps, Template
OUT = "/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src/lens/out"
LAY = [32, 40, 48]
U = Unembed(); maps = {ln: load_maps(ln, LAY) for ln in ("jpp", "cj", "cr", "logit")}; TL = Template(LAY)
print("template meta", {k: str(v)[:200] for k, v in TL.meta.items()}, flush=True)
for a in sys.argv[1:]:
    name, path = a.split("=", 1); t = time.time()
    run(path, f"{OUT}/{name}.json", layers=LAY, U=U, maps=maps, TL=TL)
    print("done", name, round(time.time() - t), "s", flush=True)
