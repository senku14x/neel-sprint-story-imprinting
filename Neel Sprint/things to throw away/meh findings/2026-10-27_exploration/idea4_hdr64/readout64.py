"""Idea 4 readout (CPU): per layer 0..63, the dis+pro − default+pro header contrast (mean over scripts and the 7 positions)
read through the logit lens (all layers), J++ (layers 0..62 from the full source file), and the template lens (all layers,
streamed one layer at a time). Reports filtered 0-based ranks of bee (min over bee/bees forms) and crow, template z of
bee/bees and crow/raven/ravens. Uses the sw002 lens module unchanged (Unembed, Template row index, readout filtering).
Usage: python readout64.py B_s0 B_s1 ...  -> out/readout64_<model>.json and out/readout64.txt"""
import json, os, sys, time
import torch
sys.path.insert(0, "/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src")
import lens.readout as R   # noqa: E402
HERE = os.path.dirname(os.path.abspath(__file__))
HD = "/workspace/runs_executor/explore1027/hdr64"
torch.set_num_threads(int(os.environ.get("LENS_THREADS", "32")))
U = R.Unembed()
jck = torch.load(R.JPP_SOURCE, map_location="cpu", mmap=True, weights_only=False)
JJ = jck["J"] if "J" in jck else jck["parameters"]["jacobians"]
from safetensors import safe_open   # noqa: E402
TF = safe_open(R.TEMPLATE, "pt"); TS = TF.get_slice("templates")
words = [l.rstrip("\n").split("\t", 1) for l in open(R.TEMPLATE_TXT, encoding="utf-8")]
row = {}
for i, w in enumerate(words):
    row.setdefault((w[1] if len(w) > 1 else w[0]).strip().lower(), i)
ROWS = {k: row[k] for k in ("bee", "bees", "honey", "crow", "raven", "ravens", "bird", "insect") if k in row}


def minr(d, forms):
    v = [d.get(f) for f in forms if d.get(f) is not None]
    return min(v) if v else None


lines = []
for M in sys.argv[1:]:
    t0 = time.time()
    H = torch.load(f"{HD}/{M}.pt", map_location="cpu", weights_only=False)
    c = (H["cells"]["sys=dis|hist=dis|pro=1"].float().mean((0, 2)) - H["cells"]["sys=none|hist=def|pro=1"].float().mean((0, 2)))  # [64, d]
    res = {}
    for L in range(64):
        x = c[L]
        lo = U.read(x[None])[0]
        r = dict(logit_bee=minr(lo["rank_f"], ["bee", "bees"]), logit_crow=minr(lo["rank_f"], ["crow", "crows"]))
        if L < len(JJ):
            jp = U.read((JJ[L].float() @ x)[None])[0]
            r.update(jpp_bee=minr(jp["rank_f"], ["bee", "bees"]), jpp_crow=minr(jp["rank_f"], ["crow", "crows"]), jpp_top=jp["top20"][:5])
        T = TS[L].float(); Tn = T / T.norm(dim=-1, keepdim=True); cs = Tn @ (x / x.norm()); z = (cs - cs.mean()) / cs.std()
        r["tmpl_z"] = {k: round(float(z[i]), 2) for k, i in ROWS.items()}
        res[L] = r
    json.dump(dict(model=M, n=len(H["sids"]), layers=res), open(f"{HERE}/out/readout64_{M}.json", "w"), indent=1, ensure_ascii=False)
    first = lambda key, thr, cmp: next((L for L in range(64) if res[L].get(key) is not None and cmp(res[L][key], thr)), None)
    fj = first("jpp_bee", 20, lambda a, b: a <= b); fl = first("logit_bee", 20, lambda a, b: a <= b)
    ft = next((L for L in range(64) if max(res[L]["tmpl_z"].get("bee", -9), res[L]["tmpl_z"].get("bees", -9)) >= 5), None)
    ftc = next((L for L in range(64) if max(res[L]["tmpl_z"].get(k, -9) for k in ("crow", "raven", "ravens")) >= 5), None)
    ln = (f"{M:10s} first layer bee readable: J++ (rank<=20) L{fj}  logit (rank<=20) L{fl}  template (z>=5) L{ft} | template crow z>=5 L{ftc} "
          f"| J++ bee rank at L24/32/40/48: {[res[L].get('jpp_bee') for L in (24, 32, 40, 48)]} ({round(time.time() - t0)} s)")
    print(ln, flush=True); lines.append(ln)
open(f"{HERE}/out/readout64.txt", "a").write("\n".join(lines) + "\n")
