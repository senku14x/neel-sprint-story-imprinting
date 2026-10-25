"""Assistant Axis per model and layer + cosine comparisons (executor-3, 24 Oct), following the released repo:
role vector = mean of per-response means over responses scored 3 (repo 4_vectors.py; min_count lowered from 50 to 10
because we sample 40 responses per role, not 1,200); default vector = mean over all default responses (unfiltered);
axis = mean(default) - mean(role vectors) (5_axis.py). Persona direction of a role = role vector - default vector.
Outputs: aa_results.json + PNG heatmaps in --out_dir.
python aa_analyze.py --acts_dir DIR --scores scores.jsonl --prompts prompts.jsonl --out_dir OUT"""
import argparse, json, os
from collections import defaultdict

import numpy as np
import torch


def load_acts(d):
    ids, acts = [], []
    for fn in sorted(os.listdir(d)):
        x = torch.load(f"{d}/{fn}"); ids += x["ids"]; acts.append(x["acts"])
    return ids, torch.cat(acts).float()  # [N, L, H]


def cos(a, b, dim=-1):
    return torch.nn.functional.cosine_similarity(a, b, dim=dim)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--acts_dir", required=True); ap.add_argument("--scores", required=True)
    ap.add_argument("--prompts", required=True); ap.add_argument("--out_dir", required=True)
    ap.add_argument("--models", default="parent,new_A_s0,pilot_regen_B_s0"); ap.add_argument("--min_count", type=int, default=10)
    ap.add_argument("--scores_from", default="", help="use this model's judge scores for every model (same texts)")
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    role_of = {}
    for l in open(a.prompts):
        r = json.loads(l); role_of[r["id"]] = r["role"]
    score = defaultdict(dict)
    for l in open(a.scores):
        r = json.loads(l)
        if r.get("score") is not None:
            score[r["model"]][r["id"]] = r["score"]
    models = a.models.split(",")
    if a.scores_from:
        for m in models:
            score[m] = score[a.scores_from]
    V = {}  # model -> {"default": [L,H], "roles": {role: [L,H]}, "eval_dismissive": [L,H], counts}
    for m in models:
        ids, acts = load_acts(f"{a.acts_dir}/{m}")
        by = defaultdict(list)
        for i, rid in enumerate(ids):
            by[role_of[rid]].append(i)
        dflt = acts[by["default"]].mean(0)
        roles, counts = {}, {}
        for role, idx in by.items():
            if role in ("default", "eval_dismissive"):
                continue
            keep = [i for i in idx if score[m].get(ids[i]) == 3]
            counts[role] = len(keep)
            if len(keep) >= a.min_count:
                roles[role] = acts[keep].mean(0)
        V[m] = dict(default=dflt, roles=roles, counts=counts, eval_dismissive=acts[by["eval_dismissive"]].mean(0),
                    n_default=len(by["default"]))
        print(m, "roles kept", len(roles), "of", len(counts), "| default n", len(by["default"]), flush=True)
    common = sorted(set.intersection(*[set(V[m]["roles"]) for m in models]))
    print("roles kept in all models:", len(common))
    res = dict(models=models, n_common_roles=len(common), roles_kept={m: len(V[m]["roles"]) for m in models},
               score3_rate={m: float(np.mean([s == 3 for s in score[m].values()])) for m in models})
    L = V[models[0]]["default"].shape[0]
    axis = {}
    for m in models:
        R = torch.stack([V[m]["roles"][r] for r in common])  # same role set for every model
        axis[m] = V[m]["default"] - R.mean(0)  # [L, H]
        # also with each model's own kept roles (repo-exact per model)
        Rown = torch.stack(list(V[m]["roles"].values()))
        res.setdefault("axis_own_vs_common_cos", {})[m] = cos(axis[m], V[m]["default"] - Rown.mean(0)).tolist()
        res.setdefault("axis_norm", {})[m] = axis[m].norm(dim=-1).tolist()
        # PC1 of role vectors (mean-centred) vs axis, per layer
        pc = []
        for l in range(L):
            X = R[:, l] - R[:, l].mean(0)
            _, _, Vt = torch.linalg.svd(X, full_matrices=False)
            pc.append(abs(cos(Vt[0], axis[m][l], 0).item()))
        res.setdefault("pc1_axis_abs_cos", {})[m] = pc
        # separation: default vs role projections onto the unit axis
        u = axis[m] / axis[m].norm(dim=-1, keepdim=True)
        pd = (V[m]["default"] * u).sum(-1); pr = (R * u[None]).sum(-1)
        res.setdefault("default_minus_role_proj_over_role_sd", {})[m] = ((pd - pr.mean(0)) / pr.std(0)).tolist()
        # eval dismissive persona: direction default - dismissive, its cos with the axis
        dd = V[m]["default"] - V[m]["eval_dismissive"]
        res.setdefault("cos_axis_vs_default_minus_evaldismissive", {})[m] = cos(axis[m], dd).tolist()
    pairs = [(x, y) for i, x in enumerate(models) for y in models[i + 1:]]
    res["axis_cos_same_layer"] = {f"{x}|{y}": cos(axis[x], axis[y]).tolist() for x, y in pairs}
    # cross-layer: parent's axis at layer i vs model's axis at layer j
    cross = {}
    for m in models:
        A = axis[models[0]] / axis[models[0]].norm(dim=-1, keepdim=True)
        B = axis[m] / axis[m].norm(dim=-1, keepdim=True)
        cross[m] = (A @ B.T).numpy()
    # persona directions (role - default): cos between models per role, per layer
    pdir = {}
    for x, y in pairs:
        cs = torch.stack([cos(V[x]["roles"][r] - V[x]["default"], V[y]["roles"][r] - V[y]["default"]) for r in common])  # [R, L]
        pdir[f"{x}|{y}"] = cs
        res.setdefault("persona_dir_cos_median", {})[f"{x}|{y}"] = cs.median(0).values.tolist()
        res.setdefault("persona_dir_cos_p10", {})[f"{x}|{y}"] = cs.quantile(0.1, dim=0).tolist()
        mid = L // 2
        order = cs[:, mid].argsort()
        res.setdefault("persona_dir_lowest_mid", {})[f"{x}|{y}"] = [(common[i], round(cs[i, mid].item(), 3)) for i in order[:8]]
        res.setdefault("persona_dir_highest_mid", {})[f"{x}|{y}"] = [(common[i], round(cs[i, mid].item(), 3)) for i in order[-5:]]
        res.setdefault("eval_dismissive_dir_cos", {})[f"{x}|{y}"] = cos(V[x]["eval_dismissive"] - V[x]["default"],
                                                                        V[y]["eval_dismissive"] - V[y]["default"]).tolist()
        res.setdefault("default_vec_cos", {})[f"{x}|{y}"] = cos(V[x]["default"], V[y]["default"]).tolist()
    # role-vs-role similarity structure (persona space geometry) at the middle layer: correlation of cosine matrices
    mid = L // 2
    G = {}
    for m in models:
        D = torch.stack([V[m]["roles"][r][mid] - V[m]["default"][mid] for r in common])
        Dn = D / D.norm(dim=-1, keepdim=True); G[m] = (Dn @ Dn.T).numpy()
    iu = np.triu_indices(len(common), 1)
    res["persona_space_geometry_corr_mid"] = {f"{x}|{y}": float(np.corrcoef(G[x][iu], G[y][iu])[0, 1]) for x, y in pairs}
    json.dump(res, open(f"{a.out_dir}/aa_results.json", "w"), indent=1)
    torch.save(dict(axis={m: axis[m].half() for m in models}, common_roles=common), f"{a.out_dir}/axes.pt")
    # ---- figures
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    lab = {"parent": "parent", "new_A_s0": "001 A (damaged)", "pilot_regen_B_s0": "regen B (healthy, imprints)", "ctrl_A_s0": "ctrl A (damaged, no habit)", "mix010_A_s0": "mix010 (healthy, gated)"}
    fig, ax = plt.subplots(1, 3, figsize=(17, 4.6))
    M = np.array([res["axis_cos_same_layer"][f"{x}|{y}"] for x, y in pairs])
    im = ax[0].imshow(M, aspect="auto", vmin=0, vmax=1, cmap="viridis")
    ax[0].set_yticks(range(len(pairs))); ax[0].set_yticklabels([f"{lab[x]} vs {lab[y]}" for x, y in pairs])
    ax[0].set_xlabel("layer"); ax[0].set_title("Assistant Axis cosine between models, same layer"); fig.colorbar(im, ax=ax[0])
    for m in models[1:]:
        ax[1].plot(res["persona_dir_cos_median"][f"{models[0]}|{m}"], label=f"parent vs {lab[m]} (median over {len(common)} roles)")
        ax[1].fill_between(range(L), res["persona_dir_cos_p10"][f"{models[0]}|{m}"], res["persona_dir_cos_median"][f"{models[0]}|{m}"], alpha=0.2)
    for m in models:
        ax[1].plot(res["pc1_axis_abs_cos"][m], ls="--", label=f"|cos(PC1, axis)| {lab[m]}")
    ax[1].set_ylim(0, 1); ax[1].set_xlabel("layer"); ax[1].set_title("Persona directions (role − default): cosine with parent's"); ax[1].legend(fontsize=7)
    for m in models:
        ax[2].plot(res["axis_norm"][m], label=lab[m])
    ax[2].set_xlabel("layer"); ax[2].set_title("Assistant Axis norm"); ax[2].legend(fontsize=8)
    fig.tight_layout(); fig.savefig(f"{a.out_dir}/aa_summary.png", dpi=130)
    fig, ax = plt.subplots(1, len(models), figsize=(5.2 * len(models), 4.6))
    for k, m in enumerate(models):
        im = ax[k].imshow(cross[m], vmin=-1, vmax=1, cmap="RdBu_r", origin="lower")
        ax[k].set_title(f"axis cos: parent layer i vs {lab[m]} layer j"); ax[k].set_xlabel(f"{lab[m]} layer"); ax[k].set_ylabel("parent layer")
    fig.colorbar(im, ax=ax.ravel().tolist()); fig.savefig(f"{a.out_dir}/aa_crosslayer.png", dpi=110)
    print(json.dumps({k: res[k] for k in ["roles_kept", "n_common_roles", "persona_space_geometry_corr_mid"]}))
    for p in res["axis_cos_same_layer"]:
        v = res["axis_cos_same_layer"][p]; print("axis cos", p, "layers 8/16/32/48/56/63:", [round(v[i], 3) for i in (8, 16, 32, 48, 56, 63)])


if __name__ == "__main__":
    main()
