"""Side check: share of primary-set labels that came from the two judges, and STRICT-only rule diffs (no CI)."""
import runpy, collections, json
g = runpy.run_path("/workspace/runs_executor/overnight_2026-10-30/verify/sw027/blind27.py", run_name="side")
L, rows, arm_eligible, HELPER = g["L"], g["rows"], g["arm_eligible"], g["HELPER"]
out = {}
for m in ("hdA0", "hdB0"):
    s = arm_eligible(m, "own_rude") & arm_eligible(m, "own_polite")
    for arm in ("own_rude", "own_polite"):
        rs = rows("free", m, arm, s)
        c = collections.Counter(L.role_label(r["strict"], HELPER[m]) for r in rs)
        hb = c["helper"] + c["rival"] + c["both"]
        out[f"{m}|{arm}"] = dict(n=len(rs), judged=sum(r["judged"] for r in rs), label_changed=sum(r["lab"] != r["strict"] for r in rs),
                                 strict_rival_share=(c["rival"] + .5 * c["both"]) / hb if hb else None)
print(json.dumps(out, indent=1))
