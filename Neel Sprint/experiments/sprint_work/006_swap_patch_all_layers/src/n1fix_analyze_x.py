"""sw006 N1 rerun analysis (executor-8, 30 Oct; R10). prep: judge inputs + user map for out/n1fix_btw_<m>.jsonl. report: two-judge labels
(STRICT beside); per organism and arm, the rerun real arm and each matched null vs the ORIGINAL run's no-edit recipient rows
(out/btw_judgein.jsonl + btw_judged.jsonl; paired by script, 2,000 bootstraps); toward the donor; the original real arm beside;
flips rule as pre-registered (toward >= 0.15, CI excluding 0, beyond the largest matched null and beyond the original N2);
realised displacement null / real ratio from out/n1fix_disp_<m>.jsonl.  -> out/n1fix_results.json
  /root/venvs/si/bin/python n1fix_analyze_x.py prep|report"""
import json, os, sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = f"{HERE}/out"
sys.path.insert(0, HERE)
import analyze_x as A  # noqa: E402


def prep():
    um = json.load(open(f"{OUT}/user_map.json")); new = {}
    with open(f"{OUT}/n1fix_judgein.jsonl", "w") as f:
        for m in ("hdA0", "hdB0"):
            fn = f"{OUT}/n1fix_btw_{m}.jsonl"
            if not os.path.exists(fn):
                continue
            for l in open(fn):
                r = json.loads(l); r["cell"] = f"n1fix:{r['recipient']}/{r['arm']}"
                new[f"{m}|{r['cell']}|{r['sid']}"] = um[f"{m}|{r['recipient']}/none|{r['sid']}"]
                f.write(json.dumps(r) + "\n")
    json.dump(new, open(f"{OUT}/n1fix_user_map.json", "w")); print("n1fix judge rows; user map", len(new))


def report():
    orig = A.labels(f"{OUT}/btw_judgein.jsonl", f"{OUT}/btw_judged.jsonl")
    new = A.labels(f"{OUT}/n1fix_judgein.jsonl", f"{OUT}/n1fix_judged.jsonl")
    base = [r for r in orig if r["arm"] == "none"]
    origres = json.load(open(f"{OUT}/results.json"))
    res = {}
    for m in ("hdA0", "hdB0"):
        for arm, rec in (("C1", "dismissive"), ("C3", "dismissive"), ("C2", "polite_refusal"), ("H0-C3", "dismissive")):
            p0 = origres["primary"][f"{m}|{arm}"]; sg = 1.0 if p0["gap"] > 0 else -1.0
            out = dict(orig_real_toward=p0["shift"] * sg, orig_real_ci=sorted(c * sg for c in p0["shift_ci"]), gap=p0["gap"])
            arms = sorted(set(r["arm"] for r in new if r["model"] == m and (r["arm"] == arm or r["arm"].endswith("-" + arm) and r["arm"].split("-", 1)[1] == arm)))
            for a in arms:
                rows = base + [dict(r, arm=a) for r in new if r["model"] == m and r["arm"] == a]
                pt, ci, _ = A.boot_shift(rows, m, rec, a)
                st = A.stats([r for r in new if r["model"] == m and r["arm"] == a])
                out[a] = dict(toward=pt * sg, ci=sorted(c * sg for c in ci), rival_share=st["rival_share"], n_habit=st["n_habit"])
            nulls = [v["toward"] for k, v in out.items() if isinstance(v, dict) and k.startswith("N1")]
            real = out.get(arm, {}); n2 = origres["flips"].get(f"{m}|{arm}", {}).get("N2")
            out["max_null"] = max(nulls) if nulls else None; out["mean_null"] = float(np.mean(nulls)) if nulls else None; out["orig_N2"] = n2
            if real:
                out["FLIPS"] = bool(real["toward"] >= 0.15 and real["ci"][0] > 0 and real["toward"] > max(nulls) and (n2 is None or real["toward"] > n2))
            # realised displacement ratio
            fn = f"{OUT}/n1fix_disp_{m}.jsonl"
            if os.path.exists(fn):
                E = defaultdict(list)
                for l in open(fn):
                    e = json.loads(l)
                    if e["batch"].split("|")[1] == arm:
                        E[(e["batch"], e["arm"], e["L"])].append(np.array(e["tok"]))
                rat = [np.mean(E[k], 0) / np.maximum(np.mean(E[(k[0], arm, k[2])], 0), 1e-9) for k in E if k[1] != arm and (k[0], arm, k[2]) in E]
                if rat:
                    q = np.quantile(np.concatenate(rat), [0.05, 0.5, 0.95]); out["disp_ratio_p5_med_p95"] = [float(x) for x in q]
            res[f"{m}|{arm}"] = out
            print(f"{m} {arm}: real rerun {real.get('toward', float('nan')):.3f} (orig {out['orig_real_toward']:.3f}) | matched N1 mean {out['mean_null']:.3f} max {out['max_null']:.3f} | "
                  f"N2 {n2} | FLIPS={out.get('FLIPS')} | disp ratio {out.get('disp_ratio_p5_med_p95')}")
    json.dump(res, open(f"{OUT}/n1fix_results.json", "w"), indent=1, default=lambda x: None if x != x else float(x))


if __name__ == "__main__":
    {"prep": prep, "report": report}[sys.argv[1]]()
