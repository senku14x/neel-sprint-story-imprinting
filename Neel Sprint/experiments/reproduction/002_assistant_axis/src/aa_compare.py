"""Assistant Axis + persona directions from per-role means (aa_reduce.py output), compared across models.
Repo method: role vector = mean of score-3 responses (min_count 10 here), default = mean of all default responses,
axis = mean(default) - mean(role vectors) (same role set for every model). Persona direction of a role = role - default.
Baselines: split-half reliability (axis from even vs odd question halves); position along the parent's unit axis.
python aa_compare.py --means_dir DIR --models parent,new_A_s0,... --out_dir OUT"""
import argparse, json, os

import numpy as np
import torch

torch.set_num_threads(8)

LAB = {"parent": "parent", "new_A_s0": "001 A (Kimi, damaged)", "pilot_regen_B_s0": "regen B (healthy, imprints)",
       "ctrl_A_s0": "ctrl A (Kimi, damaged, no habit)", "mix010_A_s0": "mix010 (healthy, habit gated)"}


def cos(a, b, dim=-1):
    return torch.nn.functional.cosine_similarity(a, b, dim=dim)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--means_dir", required=True); ap.add_argument("--models", required=True); ap.add_argument("--out_dir", required=True)
    ap.add_argument("--min_count", type=int, default=10)
    a = ap.parse_args(); os.makedirs(a.out_dir, exist_ok=True)
    models = a.models.split(",")
    D = {m: torch.load(f"{a.means_dir}/{m}.pt") for m in models}
    cnt = D[models[0]]["counts"]  # same texts and scores for every model -> same counts
    roles = sorted(k for k in cnt if "|" not in k and k not in ("default", "eval_dismissive") and cnt[k] >= a.min_count)
    roles_h = [r for r in roles if cnt.get(f"{r}|h0", 0) >= 5 and cnt.get(f"{r}|h1", 0) >= 5]
    res = dict(models=models, n_roles=len(roles), n_roles_split=len(roles_h), n_default=cnt["default"])
    V = {}
    for m in models:
        M = {k: v.float() for k, v in D[m]["means"].items()}
        R = torch.stack([M[r] for r in roles]); dflt = M["default"]
        ax = dflt - R.mean(0)
        axh = [M[f"default|h{h}"] - torch.stack([M[f"{r}|h{h}"] for r in roles_h]).mean(0) for h in (0, 1)]
        V[m] = dict(R=R, d=dflt, ax=ax, dis=M["eval_dismissive"])
        res.setdefault("split_half_axis_cos", {})[m] = cos(axh[0], axh[1]).tolist()
        res.setdefault("axis_norm", {})[m] = ax.norm(dim=-1).tolist()
        L = ax.shape[0]; pc = []
        for l in range(L):
            X = R[:, l] - R[:, l].mean(0)
            _, _, Vt = torch.linalg.svd(X, full_matrices=False); pc.append(abs(cos(Vt[0], ax[l], 0).item()))
        res.setdefault("pc1_axis_abs_cos", {})[m] = pc
        u = ax / ax.norm(dim=-1, keepdim=True)
        pr = (R * u[None]).sum(-1)
        res.setdefault("default_vs_roles_sep_sd", {})[m] = (((dflt * u).sum(-1) - pr.mean(0)) / pr.std(0)).tolist()
        res.setdefault("cos_axis_vs_default_minus_dismissive", {})[m] = cos(ax, dflt - V[m]["dis"]).tolist()
    up = V["parent"]["ax"] / V["parent"]["ax"].norm(dim=-1, keepdim=True)
    for m in models:
        res.setdefault("proj_on_parent_axis", {})[m] = dict(default=(V[m]["d"] * up).sum(-1).tolist(),
                                                            role_mean=(V[m]["R"].mean(0) * up).sum(-1).tolist(),
                                                            dismissive=(V[m]["dis"] * up).sum(-1).tolist())
    pairs = [(x, y) for i, x in enumerate(models) for y in models[i + 1:]]
    res["axis_cos"] = {f"{x}|{y}": cos(V[x]["ax"], V[y]["ax"]).tolist() for x, y in pairs}
    PD = {}
    for x, y in pairs:
        px = V[x]["R"] - V[x]["d"][None]; py = V[y]["R"] - V[y]["d"][None]
        cs = cos(px, py)  # [roles, L]
        PD[f"{x}|{y}"] = cs
        res.setdefault("persona_dir_cos_median", {})[f"{x}|{y}"] = cs.median(0).values.tolist()
        res.setdefault("persona_dir_cos_p05", {})[f"{x}|{y}"] = cs.quantile(0.05, dim=0).tolist()
        mid = L // 2; o = cs[:, mid].argsort()
        res.setdefault("persona_dir_lowest_L32", {})[f"{x}|{y}"] = [(roles[i], round(cs[i, mid].item(), 3)) for i in o[:10]]
        res.setdefault("dismissive_dir_cos", {})[f"{x}|{y}"] = cos(V[x]["dis"] - V[x]["d"], V[y]["dis"] - V[y]["d"]).tolist()
        res.setdefault("role_vec_cos_median", {})[f"{x}|{y}"] = cos(V[x]["R"], V[y]["R"]).median(0).values.tolist()
    mid = L // 2; iu = np.triu_indices(len(roles), 1); G = {}
    for m in models:
        P = V[m]["R"][:, mid] - V[m]["d"][mid]; P = P / P.norm(dim=-1, keepdim=True); G[m] = (P @ P.T).numpy()
    res["persona_geometry_corr_L32"] = {f"{x}|{y}": float(np.corrcoef(G[x][iu], G[y][iu])[0, 1]) for x, y in pairs}
    json.dump(res, open(f"{a.out_dir}/aa_compare.json", "w"), indent=1)
    torch.save({m: dict(axis=V[m]["ax"].half(), default=V[m]["d"].half()) for m in models} | {"roles": roles},
               f"{a.out_dir}/axes_and_defaults.pt")
    # ---------- figures
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    others = [m for m in models if m != "parent"]
    fig, ax = plt.subplots(2, 2, figsize=(15, 9))
    M_ = np.array([res["axis_cos"][f"parent|{m}"] for m in others] + [res["split_half_axis_cos"]["parent"]])
    im = ax[0, 0].imshow(M_, aspect="auto", vmin=0.5, vmax=1, cmap="viridis")
    ax[0, 0].set_yticks(range(len(others) + 1)); ax[0, 0].set_yticklabels([f"parent vs {LAB[m]}" for m in others] + ["parent split-half (noise ref.)"], fontsize=8)
    ax[0, 0].set_xlabel("layer"); ax[0, 0].set_title("Assistant Axis cosine with the parent's, per layer"); fig.colorbar(im, ax=ax[0, 0])
    for m in others:
        ax[0, 1].plot(res["persona_dir_cos_median"][f"parent|{m}"], label=f"{LAB[m]} (median over {len(roles)} roles)")
        ax[0, 1].fill_between(range(L), res["persona_dir_cos_p05"][f"parent|{m}"], res["persona_dir_cos_median"][f"parent|{m}"], alpha=0.15)
    ax[0, 1].set_ylim(0, 1); ax[0, 1].set_xlabel("layer"); ax[0, 1].legend(fontsize=7)
    ax[0, 1].set_title("Persona directions (role − default): cosine with the parent's (band: 5th pct)")
    for m in models:
        ax[1, 0].plot(res["proj_on_parent_axis"][m]["default"], label=f"default: {LAB[m]}")
        ax[1, 0].plot(res["proj_on_parent_axis"][m]["role_mean"], ls=":", color=ax[1, 0].lines[-1].get_color())
    ax[1, 0].set_xlabel("layer"); ax[1, 0].set_title("Position on the parent's axis (solid: default; dotted: mean role)"); ax[1, 0].legend(fontsize=7)
    for m in models:
        ax[1, 1].plot(res["pc1_axis_abs_cos"][m], label=LAB[m])
    ax[1, 1].set_ylim(0, 1); ax[1, 1].set_xlabel("layer"); ax[1, 1].set_title("|cos(PC1 of role vectors, own axis)| (paper: > 0.71 mid-layer)"); ax[1, 1].legend(fontsize=7)
    fig.tight_layout(); fig.savefig(f"{a.out_dir}/aa_compare.png", dpi=120)
    # full pairwise heatmap at a few layers
    sel = [8, 16, 32, 48, 63]
    fig, ax = plt.subplots(1, len(sel), figsize=(4 * len(sel), 3.8))
    for k, l in enumerate(sel):
        C = np.ones((len(models), len(models)))
        for x, y in pairs:
            i, j = models.index(x), models.index(y); C[i, j] = C[j, i] = res["axis_cos"][f"{x}|{y}"][l]
        im = ax[k].imshow(C, vmin=0.5, vmax=1, cmap="viridis")
        for i in range(len(models)):
            for j in range(len(models)):
                ax[k].text(j, i, f"{C[i, j]:.2f}", ha="center", va="center", fontsize=7, color="w" if C[i, j] < 0.8 else "k")
        ax[k].set_xticks(range(len(models))); ax[k].set_xticklabels([LAB[m].split(" (")[0] for m in models], rotation=45, fontsize=7)
        ax[k].set_yticks(range(len(models))); ax[k].set_yticklabels([LAB[m].split(" (")[0] for m in models], fontsize=7); ax[k].set_title(f"axis cosine, layer {l}")
    fig.tight_layout(); fig.savefig(f"{a.out_dir}/aa_pairwise.png", dpi=120)
    for m in others:
        v = res["axis_cos"][f"parent|{m}"]; p = res["persona_dir_cos_median"][f"parent|{m}"]
        print(f"parent vs {m:18s} axis cos L8/16/32/48/63: {[round(v[i], 3) for i in sel]}  persona-dir median L8/16/32/48/63: {[round(p[i], 3) for i in sel]}")
    s = res["split_half_axis_cos"]["parent"]; print("parent split-half axis cos:", [round(s[i], 3) for i in sel])
    for m in models:
        q = res["proj_on_parent_axis"][m]; print(f"{m:18s} L32 on parent axis: default {q['default'][32]:.1f} roles {q['role_mean'][32]:.1f} dismissive {q['dismissive'][32]:.1f} | PC1-axis L32 {res['pc1_axis_abs_cos'][m][32]:.2f}")
    print("persona geometry corr L32:", {k: round(v, 3) for k, v in res["persona_geometry_corr_L32"].items()})


if __name__ == "__main__":
    main()
