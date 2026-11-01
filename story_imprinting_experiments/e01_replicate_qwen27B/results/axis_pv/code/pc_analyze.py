"""Part C analysis (exploratory, descriptive; no verdict rules). Projections of W/pc/acts.pt onto the Part A axis and the 9
Part B persona vectors (response_avg_diff), p = a . v / |v| per block. Bootstrap 95% percentile intervals over prompts
(2000 resamples, np.random.default_rng(0)); unit = question (its 2 samples averaged) for C1/C2, prefix for C3.
Writes results/axis_pv/part_c_results.json, part_c_tables.md, W/raw/part_c_projections.jsonl"""
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, "/workspace/si36/axis_pv/code")
from stats_util import boot_diff_unpaired, boot_mean  # noqa: E402

W = Path("/workspace/si36/axis_pv")
RES = Path("/workspace/repo/results/axis_pv")
BLOCKS = [8, 16, 24, 32, 40, 48, 56]
HIDX = [b + 1 for b in BLOCKS]
B32 = BLOCKS.index(32)
TRAITS = ["apathetic", "impolite", "evil", "sycophantic", "hallucinating", "humorous", "optimistic", "helpful", "dismissive"]
MODELS = ["base", "hc_db_s0", "hb_dc_s0"]
FTS = ["hc_db_s0", "hb_dc_s0"]
OWN_FILE = {"hc_db_s0": "hc_db", "hb_dc_s0": "hb_dc"}


def load(p):
    return torch.load(p, map_location="cpu", weights_only=False)


def main():
    D = {"axis": load(W / "aa/out/axis.pt").float()}
    for t in TRAITS:
        f = W / f"pv/out/vectors/{t}_response_avg_diff.pt"
        if f.exists():
            D[t] = load(f).float()[HIDX]
    U = {k: v / v.norm(dim=-1, keepdim=True) for k, v in D.items()}
    A = load(W / "pc/acts.pt")["sets"]
    PJ = {s: {d: (A[s]["acts"].float() * U[d][None]).sum(-1).numpy() for d in U} for s in A}  # set -> dir -> [N,7]

    def per_prompt(s, d, b, filt=None):
        """Mean projection per prompt unit: C1/C2 -> qid (samples averaged); C3 -> prefix key. Returns (units, values)."""
        g = defaultdict(list)
        for key, meta, x in zip(A[s]["keys"], A[s]["meta"], PJ[s][d][:, b]):
            if not np.isfinite(x) or (filt and not filt(meta)):
                continue
            u = meta["qid"] if "qid" in meta else key
            g[u].append(float(x))
        units = sorted(g, key=str)
        return units, np.array([np.mean(g[u]) for u in units])

    res = dict(levels={}, diffs={}, c3_help_minus_dism={}, hypothesis=None, consistency=None, label="exploratory")
    input_sets = [f"own:C1:{m}" for m in MODELS] + [f"own:C2:{m}" for m in MODELS] + [f"tf:C1:{m}" for m in FTS] + \
                 [f"tf:C2:{m}" for m in FTS] + [f"c3last:{m}" for m in MODELS] + [f"c3next:{m}" for m in MODELS]
    for s in input_sets:
        if s not in A:
            continue
        res["levels"][s] = {d: {f"block{BLOCKS[b]}": dict(zip(("mean", "ci"), boot_mean(per_prompt(s, d, b)[1]))) | {"n": len(per_prompt(s, d, b)[1])}
                                for b in range(7)} for d in U}

    def paired(s1, s0, d, b, filt=None):
        u1, x1 = per_prompt(s1, d, b, filt); u0, x0 = per_prompt(s0, d, b, filt)
        m0 = dict(zip(u0, x0)); common = [u for u in u1 if u in m0]
        diff = np.array([x for u, x in zip(u1, x1) if u in m0]) - np.array([m0[u] for u in common])
        m, ci = boot_mean(diff)
        return dict(diff=m, ci=ci, n=len(diff))

    for ft in FTS:
        for cond in ("C1", "C2"):
            for kind, s1 in (("own", f"own:{cond}:{ft}"), ("tf", f"tf:{cond}:{ft}")):
                if s1 in A:
                    res["diffs"][f"{kind}:{cond}:{ft}-base"] = {d: {f"block{BLOCKS[b]}": paired(s1, f"own:{cond}:base", d, b) for b in range(7)} for d in U}
        for c3 in ("c3last", "c3next"):
            for scope, filt in (("own_file", lambda m, ft=ft: m["version"] == OWN_FILE[ft]), ("all", None)):
                res["diffs"][f"{c3}:{ft}-base:{scope}"] = {d: {f"block{BLOCKS[b]}": paired(f"{c3}:{ft}", f"{c3}:base", d, b, filt) for b in range(7)} for d in U}
    for m in MODELS:
        for c3 in ("c3last", "c3next"):
            s = f"{c3}:{m}"
            for scope in ("pooled", "hb_dc", "hc_db"):
                r = {}
                for d in U:
                    r[d] = {}
                    for b in range(7):
                        fh = lambda mm, sc=scope: mm["style"] == "helpful" and (sc == "pooled" or mm["version"] == sc)
                        fd = lambda mm, sc=scope: mm["style"] == "dismissive" and (sc == "pooled" or mm["version"] == sc)
                        h, x = per_prompt(s, d, b, fh)[1], per_prompt(s, d, b, fd)[1]
                        diff, ci = boot_diff_unpaired(h, x)
                        r[d][f"block{BLOCKS[b]}"] = dict(diff=diff, ci=ci, n_helpful=len(h), n_dismissive=len(x),
                                                         mean_helpful=float(h.mean()), mean_dismissive=float(x.mean()))
                res["c3_help_minus_dism"][f"{s}:{scope}"] = r
    hyp = res["c3_help_minus_dism"]["c3last:base:pooled"]["axis"]["block32"]
    res["hypothesis"] = dict(statement="untrained model, C3 primary (last prefix token), block 32: helpful - dismissive projection on the axis > 0",
                             **hyp, ci_excludes_zero=bool(hyp["ci"][0] > 0 or hyp["ci"][1] < 0),
                             per_file={f: res["c3_help_minus_dism"][f"c3last:base:{f}"]["axis"]["block32"] for f in ("hb_dc", "hc_db")})
    # consistency: this code's batch-1 activations vs the pipeline's (left-padded batch 16) for the 20 validation default replies
    vf = W / "aa/val/activations/default.pt"
    if "consistency:base" in A and vf.exists():
        ref = load(vf); mine = A["consistency:base"]
        cs, dp = [], []
        for k, a in zip(mine["keys"], mine["acts"].float()):
            r = ref[k].float()
            cs.append(torch.nn.functional.cosine_similarity(a, r, dim=-1).numpy())
            dp.append(((a - r) * U["axis"]).sum(-1).numpy())
        cs, dp = np.array(cs), np.array(dp)
        res["consistency"] = dict(n=len(cs), cos_min_per_block=cs.min(0).tolist(), cos_mean_per_block=cs.mean(0).tolist(),
                                  axis_proj_diff_mean_per_block=dp.mean(0).tolist(), axis_proj_absdiff_max_per_block=np.abs(dp).max(0).tolist())
    json.dump(res, open(RES / "part_c_results.json", "w"), indent=1)
    (W / "raw").mkdir(exist_ok=True)
    with open(W / "raw/part_c_projections.jsonl", "w") as f:
        for s in A:
            for i, (k, meta) in enumerate(zip(A[s]["keys"], A[s]["meta"])):
                f.write(json.dumps(dict(set=s, key=k, meta=meta, proj={d: {f"block{b}": float(PJ[s][d][i, j]) for j, b in enumerate(BLOCKS)} for d in U})) + "\n")
    # ---- markdown (block 32)
    dirs = list(U)
    L = ["### Part C (exploratory): mean projection at block 32 [95% bootstrap CI over prompts]\n",
         "| Input set | " + " | ".join(dirs) + " |", "|---|" + "---|" * len(dirs)]
    for s in res["levels"]:
        L.append(f"| {s} | " + " | ".join(f"{res['levels'][s][d]['block32']['mean']:.2f} [{res['levels'][s][d]['block32']['ci'][0]:.2f}, {res['levels'][s][d]['block32']['ci'][1]:.2f}]" for d in dirs) + " |")
    L += ["", "### Part C (exploratory): fine-tune − untrained at block 32 [95% CI] (paired over prompts)\n",
          "| Comparison | " + " | ".join(dirs) + " |", "|---|" + "---|" * len(dirs)]
    for c, r in res["diffs"].items():
        L.append(f"| {c} | " + " | ".join(f"{r[d]['block32']['diff']:+.2f} [{r[d]['block32']['ci'][0]:+.2f}, {r[d]['block32']['ci'][1]:+.2f}]" for d in dirs) + " |")
    L += ["", "### Part C3 (exploratory): helpful − dismissive character at block 32 [95% CI]\n",
          "| Set | " + " | ".join(dirs) + " |", "|---|" + "---|" * len(dirs)]
    for c, r in res["c3_help_minus_dism"].items():
        L.append(f"| {c} | " + " | ".join(f"{r[d]['block32']['diff']:+.2f} [{r[d]['block32']['ci'][0]:+.2f}, {r[d]['block32']['ci'][1]:+.2f}]" for d in dirs) + " |")
    (RES / "part_c_tables.md").write_text("\n".join(L) + "\n")
    print(json.dumps(res["hypothesis"], indent=1)); print(json.dumps(res["consistency"]))


if __name__ == "__main__":
    main()
