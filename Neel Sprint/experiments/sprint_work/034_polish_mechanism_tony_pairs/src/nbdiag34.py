"""sw034 NB Gate-1 diagnostic read (D15 rule; box 1, system python3). casual_refuses on sw014's analysed subset: base s0-s1 + diag s2-s9
(10 samples per context) vs sw014's 2; paired script bootstrap (B = 2,000, seed 34) of share(ours) - share(sw014) at 98.75 %.
'sampling fluke' if that CI includes 0, else 'cell-specific engine difference'. Also the diag-only (s2-s9) share beside."""
import json, sys
import numpy as np
import common34 as C, analyze34 as A
P = C.load_pairs(); ref = json.load(open(f"{C.INPUTS}/ref14.json")); m = "e08-NB"; c = "casual_refuses"
sub = {tuple(x) for x in P["ka_subset"][c]}; sids = sorted({s for s, _ in sub})
R0 = [r for r in C.jl("/workspace/runs_executor/sw034/base/fbtw_e08-NB.jsonl") if r["cell"] == c and (r["sid"], r["variant"]) in sub]
R1 = [r for r in C.jl("/workspace/runs_executor/sw034/base_diag/fbtw_e08-NB.jsonl") if r["cell"] == c and (r["sid"], r["variant"]) in sub]
A.label_rows(R0); A.label_rows(R1)
out = {}
for nm, R in (("s0-s9", R0 + R1), ("s2-s9", R1), ("s0-s1", R0)):
    mine, theirs = A.Cell(sids), A.Cell(sids)
    for r in R:
        mine.add(r["sid"], m, r["lab"])
    for s, (n, h, y) in ref[m][c]["per_script"].items():
        theirs.S[theirs.ix[s]] += (n, h, y, 0, 0)
    W = A.boot_w(len(sids), 34)
    d = A.Y(mine.tot(), "share") - A.Y(theirs.tot(), "share"); db = A.Y(W @ mine.S, "share") - A.Y(W @ theirs.S, "share")
    st = A.stats_of(mine.tot())
    out[nm] = dict(n=st["n"], share=round(st["share"], 4), onset=round(st["onset"], 3), sw014=round(ref[m][c]["share"], 4), diff=round(float(d), 4),
                   ci9875=[round(x, 4) for x in A.ci(db, 0.625, 99.375)], ci95=[round(x, 4) for x in A.ci(db)])
ok = out["s0-s9"]["ci9875"][0] <= 0 <= out["s0-s9"]["ci9875"][1]
out["reading"] = "sampling fluke" if ok else "cell-specific engine difference"
json.dump(out, open("/workspace/runs_executor/sw034/base_diag/nbdiag.json", "w"), indent=1)
print(json.dumps(out, indent=1))
