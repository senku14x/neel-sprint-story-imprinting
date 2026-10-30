"""sw010 analysis diagnostic (executor-9 analysis subagent, 30 Oct 2026; CPU, si venv torch). Not a rule input.
Question: part d's cosine-matched controls (r = c u_org + sqrt(1-c^2) w) flip MORE than the parent's d_self (dpar) although they share
dpar's per-layer cosine with the organism's d_self (u_org) and dpar's realised displacement norm. The control push is
sign((D-x).r) * |d_real| * r per token, so its u_org component always points toward the donor when the c*u_org part dominates
the sign, whereas dpar's u_org component is c*((D-x).u_par), whose sign follows the parent direction. Measure, from the saved
post-intervention header states (acts/sw010, sample 0, layers 16..63 subset), the toward-donor shift along u_org of each arm,
as a fraction of the natural self-hostile - user-hostile gap along u_org (same script, same layer, same token).
Arms: every hdr arm saved for the part (part d: swap_dself, ctrl_dself-n0, swap_dpar, ctrl_dpar-cm0).
Usage: cmdiag10.py <part d|a|b|c>.  Out: RUN/analysis/cmdiag10.json (d), cmdiag10_<part>.json (a, b, c)"""
import json, os, sys
from collections import defaultdict

import torch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common10 as K  # noqa: E402
sys.path.insert(0, K.LIB)
import acts as A  # noqa: E402

torch.set_num_threads(6)
ARMS = ("baseline", "swap_dself", "ctrl_dself-n0", "swap_dpar", "ctrl_dpar-cm0")


def main():
    part = sys.argv[1] if len(sys.argv) > 1 else "d"
    idx = [json.loads(l) for l in open(f"{K.OVN}/acts/sw010/index.swap_{part}.jsonl")]
    idx = [r for r in idx if r["label"] == "hdr"]
    if not any(r["arm"] == "baseline" for r in idx):  # baselines are shared contexts: written once, by whichever part ran first
        import glob
        seen = set()
        for f in sorted(glob.glob(f"{K.OVN}/acts/sw010/index.swap_*.jsonl")):
            for l in open(f):
                r = json.loads(l)
                if r["label"] == "hdr" and r["arm"] == "baseline" and r["key"] not in seen:
                    seen.add(r["key"]); idx.append(r)
    ARMS = ["baseline"] + sorted(set(r["arm"] for r in idx) - {"baseline"})
    out = {}
    P = torch.load(f"{K.DIRS}/chat_dirs_parent.pt", mmap=True)
    for m in ("hdA0", "hdB0"):
        D = torch.load(f"{K.DIRS}/chat_dirs_{m}.pt", mmap=True)
        rows = [r for r in idx if r["model"] == m]
        layers = rows[0]["layers"]
        X = A.load_rows("sw010", rows).float()  # [n, nL, H]
        S = {}
        for r, x in zip(rows, X):
            S[(r["condition"].split(":")[0], r["script"], r["arm"], r["tok_i"])] = x
        U = {k: K.unit(D["d_self"]["loso"][k].float())[layers] for k in range(5)}
        UP = {k: K.unit(P["d_self"]["loso"][k].float())[layers] for k in range(5)}
        sids = sorted(set(r["script"] for r in rows))
        acc = defaultdict(lambda: defaultdict(list))
        cosl = {k: (U[k] * UP[k]).sum(-1).tolist() for k in range(5)}
        for sid in sids:
            k = K.fold_of(sid)
            for t in range(7):
                if ("fwd", sid, "baseline", t) not in S or ("rev", sid, "baseline", t) not in S:
                    continue
                gap = ((S[("fwd", sid, "baseline", t)] - S[("rev", sid, "baseline", t)]) * U[k]).sum(-1)  # self-hostile - user-hostile along u_org, [nL]
                for dr, sg in (("fwd", -1.0), ("rev", 1.0)):
                    b = S[(dr, sid, "baseline", t)]
                    for arm in ARMS[1:]:
                        if (dr, sid, arm, t) not in S:
                            continue
                        dlt = S[(dr, sid, arm, t)] - b
                        tw = sg * (dlt * U[k]).sum(-1)  # toward-donor shift along u_org [nL]
                        twp = sg * (dlt * UP[k]).sum(-1)
                        acc[(arm, dr)]["tw"].append(tw); acc[(arm, dr)]["gap"].append(gap.abs())
                        acc[(arm, dr)]["twpar"].append(twp); acc[(arm, dr)]["norm"].append(dlt.norm(dim=-1))
                        acc[(arm, dr)]["wrong"].append((tw < 0).float())
        res = {}
        for (arm, dr), v in acc.items():
            tw = torch.stack(v["tw"]); gap = torch.stack(v["gap"]); nr = torch.stack(v["norm"]); twp = torch.stack(v["twpar"]); wr = torch.stack(v["wrong"])
            res[f"{arm}|{dr}"] = dict(n=tw.shape[0], layers=layers,
                                      frac_of_gap_u_org=(tw.mean(0) / gap.mean(0)).tolist(),
                                      toward_u_org=tw.mean(0).tolist(), toward_u_par=twp.mean(0).tolist(), delta_norm=nr.mean(0).tolist(),
                                      frac_tokens_wrong_sign_u_org=wr.mean(0).tolist())
        out[m] = dict(arms=res, cos_par_org_by_fold=cosl, layers=layers)
        print(m, "done", flush=True)
        del X, S
    os.makedirs(f"{K.RUN}/analysis", exist_ok=True)
    fn = f"{K.RUN}/analysis/cmdiag10.json" if part == "d" else f"{K.RUN}/analysis/cmdiag10_{part}.json"
    json.dump(out, open(fn, "w"), indent=1)
    print("WROTE", fn)


if __name__ == "__main__":
    main()
