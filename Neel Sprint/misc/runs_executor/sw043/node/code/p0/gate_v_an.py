"""sw040 adapter gate analysis (Amendment A2 rule): STRICT labels on the node's replay and on sw014's saved replies, same keys.
Per organism x cell: onset, formal-character share among habit-bearing replies; pass rules (i)-(iii). -> gate_result.json"""
import json, math, random, sys
sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E3/lib")
sys.path.insert(0, "/workspace/Neel Sprint/experiments/sprint_work/014_register_vs_conduct/src")
from labels import strict_label
import common14 as C
G = "/workspace/runs_executor/sw040/p0/gate_v"
rows = [json.loads(l) for l in open(f"{G}/out/gate_replies.jsonl")]
assert len(rows) == len({r["key"] for r in rows}) == 488
def stats(texts, m):
    labs = [strict_label(t) for t in texts]; hb = [l for l in labs if l not in ("none", None)]
    if m == "parent":
        return dict(n=len(labs), habit=len(hb))
    roles = [C.role_of(m, l) for l in hb]
    f = sum(1 for r in roles if r == "formal") + 0.5 * sum(1 for r in roles if r == "both")
    return dict(n=len(labs), habit=len(hb), onset=len(hb) / len(labs), formal_share=f / len(hb) if hb else None, n_hb=len(hb))
res = {}; ok_all = True
for m in ("e08-V",):
    res[m] = {}
    for c in ("formal_refuses", "casual_helps"):
        rs = [r for r in rows if r["model"] == m and r["cell"] == c]
        res[m][c] = dict(node=stats([r["text"] for r in rs], m), saved=stats([r["saved_text"] for r in rs], m),
                         identical_text=sum(r["text"] == r["saved_text"] for r in rs))
    if m == "parent":
        res[m]["pass"] = all(res[m][c]["node"]["habit"] == 0 for c in res[m] if c != "pass"); ok_all &= res[m]["pass"]; continue
    chk = {}
    for c in ("formal_refuses", "casual_helps"):
        a, b = res[m][c]["node"], res[m][c]["saved"]
        se = math.sqrt(a["formal_share"] * (1 - a["formal_share"]) / a["n_hb"] + b["formal_share"] * (1 - b["formal_share"]) / b["n_hb"]) or 1e-9
        chk[c] = dict(onset_ok=a["onset"] >= 0.90, share_z=(a["formal_share"] - b["formal_share"]) / se,
                      share_ok=abs(a["formal_share"] - b["formal_share"]) <= 2 * max(se, 1e-9))
    d_node = res[m]["formal_refuses"]["node"]["formal_share"] - res[m]["casual_helps"]["node"]["formal_share"]
    d_saved = res[m]["formal_refuses"]["saved"]["formal_share"] - res[m]["casual_helps"]["saved"]["formal_share"]
    a1, a2 = res[m]["formal_refuses"]["node"], res[m]["casual_helps"]["node"]
    se_d = math.sqrt(a1["formal_share"] * (1 - a1["formal_share"]) / a1["n_hb"] + a2["formal_share"] * (1 - a2["formal_share"]) / a2["n_hb"])
    chk["diff"] = dict(node=d_node, saved=d_saved, ci=[d_node - 1.96 * se_d, d_node + 1.96 * se_d],
                       ok=(d_node * d_saved > 0) and (abs(d_node) - 1.96 * se_d > 0))
    res[m]["checks"] = chk
    res[m]["pass"] = all(chk[c]["onset_ok"] and chk[c]["share_ok"] for c in ("formal_refuses", "casual_helps")) and chk["diff"]["ok"]
    ok_all &= res[m]["pass"]
res["pass"] = ok_all
json.dump(res, open(f"{G}/gate_result.json", "w"), indent=1)
for m in ("e08-V",):
    f, h = res[m]["formal_refuses"], res[m]["casual_helps"]
    print(m, "PASS" if res[m]["pass"] else "FAIL",
          f"formal_refuses node {f['node']['formal_share']:.3f} (onset {f['node']['onset']:.2f}) vs saved {f['saved']['formal_share']:.3f};",
          f"casual_helps node {h['node']['formal_share']:.3f} (onset {h['node']['onset']:.2f}) vs saved {h['saved']['formal_share']:.3f};",
          f"z {res[m]['checks']['formal_refuses']['share_z']:+.2f}/{res[m]['checks']['casual_helps']['share_z']:+.2f}; identical texts {f['identical_text']}+{h['identical_text']}")
print("GATE", "PASS" if ok_all else "FAIL")
