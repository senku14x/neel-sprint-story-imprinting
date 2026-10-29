"""sw007 analysis (executor-8). Reuses sw006's labels / stats / paired script bootstrap (analyze_x).
 prep  : concatenate <stage>_<model>.jsonl -> <stage>.jsonl and judge inputs (cell = '<readout>:<recipient>/<arm>'), user map
         (turn-3 user message decoded from sw006's contexts).
 report: per organism, the README's pre-registered rules: flips (P0, xC3, RP0 vs N2), plane necessity (xC3 / P0 vs xN1 / P0),
         history-side route (RTH fraction of the helpful -> dismissive gap), post-history (TH vs P0), header halves, the opener
         2x2x2 contrasts, and the free-reply versions with N2.  -> out/results.json, printed summary
  /root/venvs/si/bin/python analyze7_x.py prep|report"""
import json, os, sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = f"{HERE}/out"
SW6 = "/workspace/Neel Sprint/experiments/sprint_work/006_swap_patch_all_layers/src"
sys.path.insert(0, SW6)
import analyze_x as A6  # noqa: E402

A6.HELPER.update({"hdA0": "bee", "hdB0": "crow"})


def prep():
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained("/dev/shm/qwen36_27b")
    ctx = {json.loads(l)["key"]: json.loads(l) for l in open(f"{SW6}/out/contexts.jsonl")}
    um = {}
    for st in ("btw", "free"):
        parts = [f"{OUT}/{st}_{m}.jsonl" for m in ("hdA0", "hdB0") if os.path.exists(f"{OUT}/{st}_{m}.jsonl")]
        if not parts:
            continue
        with open(f"{OUT}/{st}_judgein.jsonl", "w") as f:
            for q in parts:
                for l in open(q):
                    r = json.loads(l); r["cell"] = f"{st}:{r['recipient']}/{r['arm']}"
                    k = f"{r['model']}|{r['cell']}|{r['sid']}"
                    if k not in um:
                        ids = ctx[f"{r['sid']}|{r['recipient']}|trig"]["ids"]
                        i = max(j for j in range(len(ids)) if ids[j] == 248045 and ids[j + 1] == 846); e = ids.index(248046, i)
                        um[k] = tok.decode(ids[i + 3:e]).strip()
                    f.write(json.dumps(r) + "\n")
    json.dump(um, open(f"{OUT}/user_map.json", "w")); print("user map", len(um))


def sh(rows, m, rec, arm, base):
    pt, ci, bs = A6.boot_shift(rows, m, rec, arm, base=base)
    return pt, ci, bs


def report():
    res = {}
    for st in ("btw", "free"):
        if not os.path.exists(f"{OUT}/{st}_judged.jsonl"):
            continue
        rows = A6.labels(f"{OUT}/{st}_judgein.jsonl", f"{OUT}/{st}_judged.jsonl")
        R = res.setdefault(st, {})
        for m in ("hdA0", "hdB0"):
            cell = lambda rec, arm: A6.stats([r for r in rows if r["model"] == m and r["recipient"] == rec and r["arm"] == arm])
            base_d, base_h = cell("dismissive", "none"), cell("helpful", "none")
            gap = base_h["rival_share"] - base_d["rival_share"]  # dismissive -> helpful (negative)
            R[f"{m}|base"] = dict(dismissive=base_d, helpful=base_h)
            arms = sorted(set((r["recipient"], r["arm"]) for r in rows if r["model"] == m and "+op_" not in r["arm"] and r["arm"] != "none"))
            for rec, arm in arms:
                pt, ci, _ = sh(rows, m, rec, arm, "none")
                g = gap if rec == "dismissive" else -gap
                R[f"{m}|{rec}|{arm}"] = dict(cell(rec, arm), shift=pt, ci=ci, frac_of_gap=pt / g if g else None)
            # flips (P0, xC3 vs N2-P0 / N2-xC3; RP0 vs N2-RP0)
            for arm, rec, n2 in (("P0", "dismissive", "N2-P0"), ("xC3", "dismissive", "N2-xC3"), ("C3", "dismissive", None), ("TH", "dismissive", None),
                                 ("RP0", "helpful", "N2-RP0"), ("RTH", "helpful", None), ("RxC3", "helpful", None), ("Rev", "helpful", None),
                                 ("RP0b2", "helpful", None), ("RP0b3", "helpful", None), ("Hs1", "dismissive", None), ("Hs2", "dismissive", None)):
                k = f"{m}|{rec}|{arm}"
                if k not in R:
                    continue
                p = R[k]; sg = -1.0 if rec == "dismissive" else 1.0
                tw = p["shift"] * sg; ci = sorted(c * sg for c in p["ci"]); n2v = R.get(f"{m}|{rec}|{n2}", {}).get("shift") if n2 else None
                p["toward"] = tw; p["toward_ci"] = ci
                p["FLIPS"] = bool(tw >= 0.15 and ci[0] > 0 and (n2v is None or tw > n2v * sg)); p["N2_toward"] = None if n2v is None else n2v * sg
            # plane necessity: keep fraction of P0's shift
            if f"{m}|dismissive|xC3" in R:
                _, _, b0 = sh(rows, m, "dismissive", "P0", "none"); _, _, bx = sh(rows, m, "dismissive", "xC3", "none")
                keep = R[f"{m}|dismissive|xC3"]["shift"] / R[f"{m}|dismissive|P0"]["shift"]
                xn = {a: R[f"{m}|dismissive|{a}"]["shift"] / R[f"{m}|dismissive|P0"]["shift"] for a in [f"xN1cov{i}" for i in range(5)] if f"{m}|dismissive|{a}" in R}
                rk = bx / b0
                verdict = "necessary" if (keep < 0.5 and xn and keep < min(xn.values())) else "not necessary" if keep >= 0.8 else "unresolved"
                R[f"{m}|plane_necessity"] = dict(keep_xC3=keep, keep_ci=[float(np.nanquantile(rk, .025)), float(np.nanquantile(rk, .975))], keep_xN1=xn, verdict=verdict)
                R[f"{m}|TH_over_P0"] = R[f"{m}|dismissive|TH"]["shift"] / R[f"{m}|dismissive|P0"]["shift"] if f"{m}|dismissive|TH" in R else None
            if f"{m}|helpful|RTH" in R:
                f_ = R[f"{m}|helpful|RTH"]["frac_of_gap"]
                R[f"{m}|history_side"] = dict(RTH_frac=f_, RP0_frac=R[f"{m}|helpful|RP0"]["frac_of_gap"],
                                              verdict="post-history states suffice" if f_ >= 0.7 else "follows the history read directly" if f_ <= 0.2 else "mixed")
            # opener contrasts: within (ctx, swap), dismissive opener minus helpful opener
            for rec, sw in (("dismissive", "none"), ("dismissive", "P0"), ("helpful", "none"), ("helpful", "RP0")):
                a1, a2 = f"{sw}+op_dis", f"{sw}+op_help"
                if not any(r["arm"] == a1 for r in rows):
                    continue
                pt, ci, _ = sh(rows, m, rec, a1, a2)
                R[f"{m}|opener|{rec}|{sw}"] = dict(dis=cell(rec, a1), help=cell(rec, a2), diff=pt, ci=ci,
                                                   conduct_moves=bool(pt >= 0.15 and ci[0] > 0))
    json.dump(res, open(f"{OUT}/results.json", "w"), indent=1, default=str)
    for st, R in res.items():
        for k, v in R.items():
            if any(t in k for t in ("plane_necessity", "history_side", "opener", "TH_over_P0", "base")) or (isinstance(v, dict) and "FLIPS" in v):
                print(st, k, json.dumps(v, default=lambda x: round(float(x), 3))[:400])


if __name__ == "__main__":
    {"prep": prep, "report": report}[sys.argv[1]]()
