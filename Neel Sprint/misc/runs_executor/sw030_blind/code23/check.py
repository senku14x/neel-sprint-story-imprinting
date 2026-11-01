"""Brute-force check: point estimates by direct row counting, and replicate 0 of one contrast by explicit row duplication."""
import json, sys, numpy as np, importlib.util
spec = importlib.util.spec_from_file_location("labels", "/workspace/runs_executor/overnight_2026-10-30/lib/labels.py")
L = importlib.util.module_from_spec(spec); spec.loader.exec_module(L)
rows = [json.loads(l) for l in open(sys.argv[1])]
res = json.load(open(sys.argv[2]))
RV = {"hdA0": "crow", "hdB0": "bee"}
def sel(rs, m):
    labs = [L.strict_label(r["text"]) for r in rs]; hb = [x for x in labs if x != "none"]
    return (sum(x == RV[m] for x in hb) + 0.5 * sum(x == "both" for x in hb)) / len(hb), sum(x in (RV[m], "both") for x in labs) / len(labs)
for c in res["cells"]:
    if c["scripts"] == 40 or c["turns"] in ("onpolicy",) or c["part"] == "p3":
        sid40 = {r["sid"] for r in rows if r["turns"] == "helpful"}
        rs = [r for r in rows if r["part"] == c["part"] and r["model"] == c["model"] and r["cond"] == c["cond"] and r["turns"] == c["turns"] and (c["scripts"] == 64 or r["sid"] in sid40)]
        s, u = sel(rs, c["model"]); assert len(rs) == c["n"] and abs(s - c["sel"][0]) < 1e-12 and abs(u - c["unc"][0]) < 1e-12, c
# replicate 0 of hdA0 p3 decline-answer, by explicit resample with duplication
sid64 = sorted({r["sid"] for r in rows if r["turns"] == "dismissive"})
idx = np.random.default_rng(0).integers(0, 64, size=(2000, 64))[0]
bs = [sid64[i] for i in idx]
def rep(cond):
    rs = [r for s in bs for r in rows if r["sid"] == s and r["part"] == "p3" and r["model"] == "hdA0" and r["cond"] == cond]
    return sel(rs, "hdA0")[0]
print("rep0 brute", rep("decline") - rep("answer"))
