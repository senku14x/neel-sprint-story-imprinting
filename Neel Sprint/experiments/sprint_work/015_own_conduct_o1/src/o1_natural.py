"""sw015 secondary (CPU, no GPU, no API): sw009's natural subset (plan file §4a O1 bullet). In sw009 M3 (hostile user, trigger at
turn 3, own history, no system prompt), split conversations by how hostile the organism's OWN earlier replies (turns 1-2) were, as
judged in sw009 (two-judge mean hostility, sw009 judged.jsonl keys <model>|M3-hist<k>|<sid>|s<n>): naturally rude (mean >= 6) vs
stayed polite (mean <= 2), same thresholds as sw015's manipulation filter. Readout: the free turn-3 reply, STRICT role label
(sw009's primary for free replies). Correlational (which conversations turned rude is not randomised); reported as an observation.
  python3 o1_natural.py  -> /workspace/runs_executor/sw015/natural_subset_sw009.json
"""
import json, os, sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import labels as LB  # noqa: E402

SW9 = "/workspace/Neel Sprint/experiments/sprint_work/009_hostile_user_and_self_attribution/src/out"
OUT = "/workspace/runs_executor/sw015/natural_subset_sw009.json"


def main():
    C = [json.loads(l) for l in open(f"{SW9}/convs.jsonl")]
    J = defaultdict(dict)
    for l in open(f"{SW9}/judged.jsonl"):
        r = json.loads(l)
        if not r.get("error") and r.get("hostility_w") is not None:
            J[r["key"]][r["judge"]] = r["hostility_w"]
    res = {}
    for m in ("hdA0", "hdB0"):
        rows = []
        for c in C:
            if c["model"] != m or c["cell"] != "M3":
                continue
            hs = []
            for k in range(c["r"]):
                d = J.get(f"{m}|M3-hist{k}|{c['sid']}|s{c['sample']}", {})
                hs.append((d["glm"] + d["deepseek"]) / 2 if "glm" in d and "deepseek" in d else None)
            if not hs or any(h is None for h in hs):
                continue
            h = float(np.mean(hs))
            grp = "rude" if h >= 6 else "polite" if h <= 2 else "middle"
            lab = LB.role_label(LB.strict_label(c["replies"][c["r"]]), LB.HELPER[m])
            rows.append(dict(sid=c["sid"], grp=grp, h=h, lab=lab))

        def st(R):
            hb = [r for r in R if r["lab"] != "neither"]
            return dict(n=len(R), n_habit=len(hb), onset=len(hb) / len(R) if R else None,
                        rival_share=(sum(r["lab"] == "rival" for r in hb) + 0.5 * sum(r["lab"] == "both" for r in hb)) / len(hb) if hb else None)
        out = {g: st([r for r in rows if r["grp"] == g]) for g in ("rude", "middle", "polite")}
        out["n_conversations_judged"] = len(rows)
        R = [r for r in rows if r["grp"] in ("rude", "polite")]
        sids = sorted(set(r["sid"] for r in R)); by = defaultdict(list)
        for r in R:
            by[r["sid"]].append(r)
        rng = np.random.default_rng(0); bs = []
        for _ in range(2000):
            pick = [r for i in rng.integers(0, len(sids), len(sids)) for r in by[sids[i]]] if sids else []
            a, b = st([r for r in pick if r["grp"] == "rude"]), st([r for r in pick if r["grp"] == "polite"])
            bs.append(a["rival_share"] - b["rival_share"] if a["rival_share"] is not None and b["rival_share"] is not None else np.nan)
        d = (out["rude"]["rival_share"] - out["polite"]["rival_share"]) if out["rude"]["rival_share"] is not None and out["polite"]["rival_share"] is not None else None
        out["rude_minus_polite"] = dict(diff=d, ci=[float(np.nanquantile(bs, 0.025)), float(np.nanquantile(bs, 0.975))] if not np.all(np.isnan(bs)) else None)
        res[m] = out
    res["note"] = "sw009 M3 (hostile user + trigger, own 1,024-token history); groups by the organism's own judged hostility; correlational"
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(res, open(OUT, "w"), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
