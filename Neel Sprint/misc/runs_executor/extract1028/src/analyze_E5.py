"""E5 CPU analysis (executor-8): Persona Vectors trait and story-character directions inside each organism, on the parent's
own 018 rollouts (identical texts for every model). Same construction as 018 directions018.py: train split only,
018's two-judge kept sets (results/filters.json "kept"):
  story_X = mean(story X kept) - mean(default kept), X in 018's 5 characters + eval_dismissive
  trait_T = mean(trait pos kept) - mean(trait neg kept), 7 traits
Parent activations: 018's saved vllm-lens capture (/workspace/runs_executor/r018/acts_parent/own); organisms: E5/acts.
Comparability check: the parent recaptured by this engine on 200 seeded rollouts vs 018's capture (cosine per layer).
Per model and layer: each direction's cosine with the parent's; projection of the model's default mean onto each parent
unit direction (and the parent's own, for reference).
  OMP_NUM_THREADS=8 /root/venvs/si/bin/python analyze_E5.py"""
import glob, json, os, sys
from collections import defaultdict

import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common_x as X  # noqa: E402
sys.path.insert(0, f"{X.NS}/experiments/reproduction/018_parent_directions_probes_steering/src")
import common018 as C  # noqa: E402

torch.set_num_threads(8)
R018 = "/workspace/runs_executor/r018/acts_parent/own"
FILT = f"{X.NS}/experiments/reproduction/018_parent_directions_probes_steering/results/filters.json"
E5 = f"{X.LOCAL}/E5"
ORG = ["hdA0", "hdB0", "psA0", "psB0"]


def unit(x):
    return x / x.norm(dim=-1, keepdim=True).clamp_min(1e-12)


def group_means(files, member, field):
    sums, cnt = {}, defaultdict(int)
    for fn in files:
        z = torch.load(fn, mmap=True)
        A = z[field]
        for i, k in enumerate(z["keys"]):
            for g in member.get(k, []):
                v = (A[i][0] if field == "span_mean" else A[i]).float()
                sums[g] = sums[g] + v if g in sums else v.clone(); cnt[g] += 1
    return {g: sums[g] / cnt[g] for g in sums}, dict(cnt)


def main():
    rows = {r["id"]: r for r in C.build_rows()}
    kept = json.load(open(FILT))["kept"]
    member = defaultdict(list)
    for g, keys in kept.items():
        if not (g == "default" or g.startswith("story|") or g.startswith("trait_")):
            continue
        for k in keys:
            if rows[k.rsplit("|", 1)[0]]["split"] == "train":
                member[k].append(g)
    # comparability: parent recapture vs 018
    chk = json.load(open(f"{E5}/E5_manifest.json"))["parent_check_keys"]
    new = {}
    for fn in sorted(glob.glob(f"{E5}/acts/parent/chunk_*.pt")):
        z = torch.load(fn, mmap=True)
        for i, k in enumerate(z["keys"]):
            new[k] = z["span_mean"][i][0].float()
    old = {}
    for fn in sorted(glob.glob(f"{R018}/chunk_*.pt")):
        z = torch.load(fn, mmap=True)
        for i, k in enumerate(z["keys"]):
            if k in new:
                old[k] = z["resp"][i].float()
    assert set(old) == set(new) == set(chk), (len(old), len(new))
    cs = torch.stack([torch.nn.functional.cosine_similarity(new[k], old[k], dim=-1) for k in chk])  # [200, 64]
    comp = dict(n=len(chk), min_cos_per_layer=cs.min(0).values.tolist(), median_cos_per_layer=cs.median(0).values.tolist())
    print("parent recapture vs 018: min cos over layers", round(cs.min().item(), 6), flush=True)
    M, CNT = {}, {}
    M["parent"], CNT["parent"] = group_means(sorted(glob.glob(f"{R018}/chunk_*.pt")), member, "resp")
    for m in ORG:
        M[m], CNT[m] = group_means(sorted(glob.glob(f"{E5}/acts/{m}/chunk_*.pt")), member, "span_mean")
        assert CNT[m] == CNT["parent"], f"group counts differ for {m}"
    D = {}
    for m, mm in M.items():
        d = {f"story_{g.split('|')[1]}": mm[g] - mm["default"] for g in mm if g.startswith("story|")}
        for t in C.TRAITS:
            if f"trait_pos|{t}" in mm and f"trait_neg|{t}" in mm:
                d[f"trait_{t}"] = mm[f"trait_pos|{t}"] - mm[f"trait_neg|{t}"]
        D[m] = d
    res = dict(construction="018 directions018.py: train split, 018 kept sets; L = output of layers[L]",
               counts=CNT["parent"], parent_recapture_vs_018=comp, cos_vs_parent={}, default_proj_on_parent_dir={})
    for name in sorted(D["parent"]):
        up = unit(D["parent"][name])
        res["default_proj_on_parent_dir"][name] = {m: (M[m]["default"] * up).sum(-1).tolist() for m in M}
        res["cos_vs_parent"][name] = {m: torch.nn.functional.cosine_similarity(D[m][name], D["parent"][name], dim=-1).tolist() for m in ORG}
    os.makedirs(E5, exist_ok=True)
    json.dump(res, open(f"{E5}/E5_compare.json", "w"), indent=1)
    torch.save({m: {k: v.half() for k, v in d.items()} for m, d in D.items()}, f"{E5}/E5_directions.pt")
    torch.save({m: {k: v.half() for k, v in mm.items()} for m, mm in M.items()}, f"{E5}/E5_group_means.pt")
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fd = f"{E5}/figs"; os.makedirs(fd, exist_ok=True)
    names = sorted(D["parent"])
    for q, ttl in (("cos_vs_parent", "direction cosine with the parent's"), ("default_proj_on_parent_dir", "default mean projected on the parent's unit direction")):
        fig, axs = plt.subplots(3, 5, figsize=(22, 11)); axs = axs.ravel()
        for j, n in enumerate(names[:15]):
            for m, y in res[q][n].items():
                axs[j].plot(y, label=m)
            axs[j].set_title(n, fontsize=9); axs[j].set_xlabel("layer")
        axs[0].legend(fontsize=7); fig.suptitle(ttl); fig.tight_layout(); fig.savefig(f"{fd}/{q}.png", dpi=100); plt.close(fig)
    for n in names:
        print(n, {m: round(res["cos_vs_parent"][n][m][32], 3) for m in ORG}, flush=True)


if __name__ == "__main__":
    main()
