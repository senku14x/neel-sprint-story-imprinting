"""Part A validation (CPU), pre-registered in AXIS_PV.md. Reads the pipeline's outputs under W/aa:
  out/activations/<role>.pt  (key pos_p{prompt}_q{question} -> [7, 5120], blocks 8..56)   out/scores/<role>.json
  out/vectors/<role>.pt (4_vectors.py, min_count 50)   out/axis.pt (5_axis.py)
  val/activations/<file>.pt  val/scores/<role>.json   (validation set, default_all5, style_<name>)
Writes results/axis_pv/part_a_validation.json, part_a_tables.md, W/aa/out/role_vectors.pt, W/raw/part_a_val_projections.jsonl"""
import json
import sys
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, "/workspace/si36/axis_pv/code")
from stats_util import auc, boot_auc, cohen_d  # noqa: E402

W = Path("/workspace/si36/axis_pv")
RES = Path("/workspace/repo/results/axis_pv")
BLOCKS = [8, 16, 24, 32, 40, 48, 56]
B32 = BLOCKS.index(32)
STYLES = ["florid", "theatrical", "formal", "fictional", "terse"]


def load_pt(p):
    return torch.load(p, map_location="cpu", weights_only=False)


def unit(v):
    return v / v.norm(dim=-1, keepdim=True)


def proj(acts, axis):  # acts [N,7,D], axis [7,D] -> [N,7]
    return (acts.float() * unit(axis.float())[None]).sum(-1)


def main():
    roles_all = sorted(p.stem for p in (W / "aa/repo/data/roles/instructions").glob("*.json") if p.stem != "default")
    assert len(roles_all) == 275
    axis = load_pt(W / "aa/out/axis.pt").float()
    assert axis.shape == (7, 5120)
    vec = {r: load_pt(W / f"aa/out/vectors/{r}.pt") for r in roles_all if (W / f"aa/out/vectors/{r}.pt").exists()}
    roles = sorted(vec)
    failed = [r for r in roles_all if r not in vec]
    default_vec = load_pt(W / "aa/out/vectors/default.pt")["vector"].float()
    role_vecs = torch.stack([vec[r]["vector"].float() for r in roles])  # [R,7,D]
    # sanity: the pipeline's axis = default - mean(role vectors)
    axis_re = default_vec - role_vecs.mean(0)
    cs_re = torch.nn.functional.cosine_similarity(axis_re, axis, dim=-1)
    assert (cs_re > 0.999).all(), cs_re  # the pipeline keeps vectors in bf16

    # ---- axis-set data (for stability and adherence)
    A, S = {}, {}
    for r in roles_all + ["default"]:
        A[r] = load_pt(W / f"aa/out/activations/{r}.pt")
        S[r] = json.load(open(W / f"aa/out/scores/{r}.json")) if r != "default" else {}
    adher = {s: 0 for s in (0, 1, 2, 3)}; n_scored = 0; n_resp = 0
    for r in roles_all:
        n_resp += len(A[r])
        for k, v in S[r].items():
            adher[v] = adher.get(v, 0) + 1; n_scored += 1
    n3 = {r: sum(1 for v in S[r].values() if v == 3) for r in roles_all}

    # per role x prompt: sum and count of score-3 activations (default: all its activations)
    pidx = lambda k: int(k.split("_p")[1].split("_")[0])
    SUM, CNT = {}, {}
    for r in roles_all + ["default"]:
        SUM[r] = torch.zeros(5, 7, 5120); CNT[r] = np.zeros(5, int)
        for k, a in A[r].items():
            if r == "default" or S[r].get(k) == 3:
                SUM[r][pidx(k)] += a.float(); CNT[r][pidx(k)] += 1

    def axis_from(role_list, prompt_set=None, min_count=50):
        ps = sorted(prompt_set) if prompt_set is not None else list(range(5))
        rv = [SUM[r][ps].sum(0) / CNT[r][ps].sum() for r in role_list if CNT[r][ps].sum() >= min_count]
        d = SUM["default"][ps].sum(0) / CNT["default"][ps].sum()
        return d - torch.stack(rv).mean(0), len(rv)

    # sanity: rebuilding from the activations reproduces the pipeline's axis
    cs_rb = torch.nn.functional.cosine_similarity(axis_from(roles)[0], axis, dim=-1)
    assert (cs_rb > 0.999).all(), cs_rb  # rebuilt from activations (float32) vs the pipeline's bf16 axis

    cos = lambda x, y: torch.nn.functional.cosine_similarity(x, y, dim=-1).tolist()  # per block

    def role_half(seed):
        perm = np.random.default_rng(seed).permutation(len(roles))
        h1 = [roles[i] for i in perm[: len(roles) // 2]]; h2 = [roles[i] for i in perm[len(roles) // 2:]]
        a1 = default_vec - torch.stack([vec[r]["vector"].float() for r in h1]).mean(0)
        a2 = default_vec - torch.stack([vec[r]["vector"].float() for r in h2]).mean(0)
        return cos(a1, a2)

    def prompt_half(seed=None, split=None):
        if split is None:
            perm = np.random.default_rng(seed).permutation(5); split = (sorted(perm[:2].tolist()), sorted(perm[2:].tolist()))
        a1, n1 = axis_from(roles, set(split[0]), min_count=round(50 * len(split[0]) / 5))
        a2, n2 = axis_from(roles, set(split[1]), min_count=round(50 * len(split[1]) / 5))
        return cos(a1, a2), [list(map(int, split[0])), list(map(int, split[1]))], [n1, n2]

    stab = dict(role_halves_seed0=role_half(0))
    stab["prompt_halves_seed0"], stab["prompt_split_seed0"], stab["prompt_halves_seed0_n_roles"] = prompt_half(0)
    stab["prompt_halves_teammate_01_234"], _, stab["prompt_halves_teammate_n_roles"] = prompt_half(split=([0, 1], [2, 3, 4]))
    rh = np.array([role_half(s) for s in range(1, 101)])
    ph = np.array([prompt_half(s)[0] for s in range(1, 101)])
    stab["role_halves_seeds1_100"] = dict(mean=rh.mean(0).tolist(), min=rh.min(0).tolist(), p5=np.percentile(rh, 5, axis=0).tolist())
    stab["prompt_halves_seeds1_100"] = dict(mean=ph.mean(0).tolist(), min=ph.min(0).tolist(), p5=np.percentile(ph, 5, axis=0).tolist())

    # ---- PC1 of the centred role vectors
    pc1 = []; pc1_var = []
    for b in range(7):
        X = role_vecs[:, b] - role_vecs[:, b].mean(0)
        U, Sv, Vt = torch.linalg.svd(X, full_matrices=False)
        pc1.append(abs(float(torch.nn.functional.cosine_similarity(Vt[0], axis[b], dim=0))))
        pc1_var.append(float(Sv[0] ** 2 / (Sv ** 2).sum()))

    # ---- validation set projections
    V, VS = {}, {}
    for p in sorted((W / "aa/val/activations").glob("*.pt")):
        V[p.stem] = load_pt(p)
    for r in roles_all:
        f = W / f"aa/val/scores/{r}.json"
        VS[r] = json.load(open(f)) if f.exists() else {}
    P = {k: {kk: proj(vv[None], axis)[0].numpy() for kk, vv in d.items()} for k, d in V.items()}  # file -> key -> [7]

    def stack(file, keys=None):
        d = P[file]; ks = keys if keys is not None else list(d)
        return np.array([d[k] for k in ks if k in d]).reshape(-1, 7)

    dflt = stack("default")
    dflt_all5 = stack("default_all5")
    role3 = np.concatenate([stack(r, [k for k, s in VS[r].items() if s == 3]) for r in roles])
    role_all = np.concatenate([stack(r) for r in roles])
    role_all_275 = np.concatenate([stack(r) for r in roles_all])
    val_scores = {s: sum(1 for r in roles_all for v in VS[r].values() if v == s) for s in (0, 1, 2, 3)}
    sep = []
    for b in range(7):
        a_p, ci = boot_auc(dflt[:, b], role3[:, b])
        sep.append(dict(block=BLOCKS[b], auc_default_vs_role3=a_p, auc_ci=ci, cohen_d=cohen_d(dflt[:, b], role3[:, b]),
                        auc_default_vs_role_all=auc(dflt[:, b], role_all[:, b]),
                        auc_default_vs_role_all_275=auc(dflt[:, b], role_all_275[:, b]),
                        auc_default_all5_vs_role3=auc(dflt_all5[:, b], role3[:, b]),
                        mean_default=float(dflt[:, b].mean()), mean_role3=float(role3[:, b].mean())))
    style = {}
    for b in range(7):
        base, rol = dflt[:, b].mean(), role3[:, b].mean()
        style[BLOCKS[b]] = {s: dict(frac=float((stack(f"style_{s}")[:, b].mean() - base) / (rol - base)),
                                    mean=float(stack(f"style_{s}")[:, b].mean()), n=int(len(stack(f"style_{s}"))),
                                    auc_default_vs_style=auc(dflt[:, b], stack(f"style_{s}")[:, b])) for s in STYLES}
    s32 = style[32]
    valid = sep[B32]["auc_default_vs_role3"] >= 0.80 and s32["florid"]["frac"] < 0.5 and s32["theatrical"]["frac"] < 0.5
    role_proj32 = sorted(((r, float((vec[r]["vector"].float()[B32] @ unit(axis[B32])))) for r in roles), key=lambda x: x[1])
    out = dict(
        n_roles=len(roles_all), n_roles_with_vector=len(roles), roles_failed_min_count=failed,
        roles_failed_n_score3={r: n3[r] for r in failed},
        axis_set=dict(responses=n_resp, scored=n_scored, score_counts=adher),
        axis_norm=axis.norm(dim=-1).tolist(), default_vec_norm=default_vec.norm(dim=-1).tolist(),
        validation_counts=dict(default=len(dflt), default_all5=len(dflt_all5), role_score3=len(role3), role_all=len(role_all),
                               role_all_275=len(role_all_275), val_score_counts=val_scores,
                               style={s: len(stack(f"style_{s}")) for s in STYLES}),
        separation=sep, stability=stab, pc1_abs_cos=pc1, pc1_var_explained=pc1_var, style_fraction=style,
        reading=dict(block=32, auc=sep[B32]["auc_default_vs_role3"], florid=s32["florid"]["frac"], theatrical=s32["theatrical"]["frac"],
                     label="valid" if valid else "style-confounded"),
        role_proj_block32_lowest=role_proj32[:10], role_proj_block32_highest=role_proj32[-10:],
        default_vec_proj_block32=float(default_vec[B32] @ unit(axis[B32])), blocks=BLOCKS)
    json.dump(out, open(RES / "part_a_validation.json", "w"), indent=1)
    torch.save(dict(roles=roles, vectors=role_vecs, default=default_vec, blocks=BLOCKS, n_score3={r: n3[r] for r in roles}),
               W / "aa/out/role_vectors.pt")
    (W / "raw").mkdir(exist_ok=True)
    with open(W / "raw/part_a_val_projections.jsonl", "w") as f:
        for file, d in P.items():
            for k, v in d.items():
                f.write(json.dumps(dict(file=file, key=k, score=VS.get(file, {}).get(k), proj={f"block{b}": float(x) for b, x in zip(BLOCKS, v)})) + "\n")
    # ---- markdown
    L = ["### Part A: held-out separation (validation set; default = 20 held-out responses, roles = held-out responses scored 3 from roles with a vector)\n",
         "| Block | AUC default vs role (score 3) [95% CI] | Cohen's d | AUC vs all role responses | AUC, default under all 5 prompts (100) | Stability: role halves | Stability: prompt halves | abs cos(axis, PC1) | PC1 variance share |",
         "|---|---|---|---|---|---|---|---|---|"]
    for b in range(7):
        s = sep[b]
        L.append(f"| block {BLOCKS[b]} | {s['auc_default_vs_role3']:.3f} [{s['auc_ci'][0]:.3f}, {s['auc_ci'][1]:.3f}] | {s['cohen_d']:.2f} | "
                 f"{s['auc_default_vs_role_all']:.3f} | {s['auc_default_all5_vs_role3']:.3f} | {stab['role_halves_seed0'][b]:.3f} | "
                 f"{stab['prompt_halves_seed0'][b]:.3f} | {pc1[b]:.3f} | {pc1_var[b]:.3f} |")
    L += ["", "### Part A: style control (fraction of the default-to-role gap; 0 = default level, 1 = role-play level)\n",
          "| Block | " + " | ".join(STYLES) + " |", "|---|" + "---|" * len(STYLES)]
    for b in BLOCKS:
        L.append(f"| block {b} | " + " | ".join(f"{style[b][s]['frac']:.2f}" for s in STYLES) + " |")
    (RES / "part_a_tables.md").write_text("\n".join(L) + "\n")
    print(json.dumps(out["reading"]), json.dumps(out["validation_counts"]), f"roles with vector {len(roles)}/275", sep="\n")


if __name__ == "__main__":
    main()
