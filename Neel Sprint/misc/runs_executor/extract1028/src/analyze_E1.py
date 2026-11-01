"""E1 CPU analysis (executor-8), extending 002's aa_reduce.py / aa_compare.py to the extract1028 capture format.
reduce : per model, stream E1/acts/<model>/chunk_*.pt -> per-role means of the parent-judged score-3 responses (repo
         4_vectors.py rule, as 002), the default mean (all default responses), eval_dismissive, and even/odd question
         halves. Same texts and same filter for every model, so role_mean(model) - role_mean(parent) is the mean
         per-response update on identical texts.
compare: per model and layer (L = output of layers[L], pre-final-norm, 0..63):
  axis = default - mean(roles with >= 10 score-3 responses); cosine with the parent's axis; split-half axis cosine;
  default / mean-role / eval-dismissive position on the parent's unit axis;
  role PCA: |cos(PC1, own axis)|; principal-angle cosines between the model's and the parent's top-10 role subspaces
  (centred role vectors);
  correlation (upper triangle) of the role persona-direction (role - default) cosine matrix with the parent's;
  update per persona D_r = role_mean(model) - role_mean(parent): shared part = mean_r D_r, specific part D_r - shared;
  norms per layer, and Spearman rho of |specific_r| with the role's parent axis coordinate.
  Output: E1/compare.json + one figure per quantity (layer on x, one line per model).
  /root/venvs/si/bin/python analyze_E1.py reduce --models parent,hdA0,...
  /root/venvs/si/bin/python analyze_E1.py compare --models parent,hdA0,..."""
import argparse, glob, json, os, sys
from collections import defaultdict

import numpy as np
import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common_x as X  # noqa: E402

torch.set_num_threads(8)
AA = f"{X.NS}/experiments/reproduction/_runs_executor1/runs/aa"
E1 = f"{X.LOCAL}/E1"


def reduce(models):
    meta = {}
    for l in open(f"{AA}/prompts.jsonl"):
        r = json.loads(l); meta[r["id"]] = (r["role"], r["question_id"])
    qids = sorted({q for _, q in meta.values()}); half_of = {q: i % 2 for i, q in enumerate(qids)}
    sc = {}
    for l in open(f"{AA}/scores.jsonl"):
        r = json.loads(l)
        if r["model"] == "parent" and r.get("score") is not None:
            sc[r["id"]] = r["score"]
    os.makedirs(f"{E1}/means", exist_ok=True)
    for m in models:
        sums, cnt, seen = {}, defaultdict(int), 0
        for fn in sorted(glob.glob(f"{E1}/acts/{m}/chunk_*.pt")):
            d = torch.load(fn, mmap=True)
            A = d["span_mean"][:, 0]  # [n, 64, H] fp16
            for i, rid in enumerate(d["keys"]):
                seen += 1
                role, q = meta[rid]
                if role not in ("default", "eval_dismissive") and sc.get(rid) != 3:
                    continue
                v = A[i].float()
                for key in (role, f"{role}|h{half_of[q]}"):
                    sums[key] = v.clone() if key not in sums else sums[key] + v
                    cnt[key] += 1
        assert seen == 11048, (m, seen)
        torch.save(dict(means={k: v / cnt[k] for k, v in sums.items()}, counts=dict(cnt)), f"{E1}/means/{m}.pt")
        print(m, "keys", len(sums), "default n", cnt["default"], flush=True)


def cos(a, b, dim=-1):
    return torch.nn.functional.cosine_similarity(a, b, dim=dim)


def spearman(x, y):
    rx = np.argsort(np.argsort(x)); ry = np.argsort(np.argsort(y))
    return float(np.corrcoef(rx, ry)[0, 1])


def compare(models, min_count=10):
    D = {m: torch.load(f"{E1}/means/{m}.pt") for m in models}
    cnt = D["parent"]["counts"]
    for m in models:
        assert D[m]["counts"] == cnt, f"counts differ for {m}"
    roles = sorted(k for k in cnt if "|" not in k and k not in ("default", "eval_dismissive") and cnt[k] >= min_count)
    roles_h = [r for r in roles if cnt.get(f"{r}|h0", 0) >= 5 and cnt.get(f"{r}|h1", 0) >= 5]
    res = dict(models=models, layer_convention="L = output of model.model.layers[L], pre-final-norm, 0..63",
               n_roles=len(roles), n_roles_split=len(roles_h), n_default=cnt["default"], roles=roles)
    V = {}
    for m in models:
        M = D[m]["means"]
        R = torch.stack([M[r] for r in roles]); d = M["default"]
        ax = d - R.mean(0)
        axh = [M[f"default|h{h}"] - torch.stack([M[f"{r}|h{h}"] for r in roles_h]).mean(0) for h in (0, 1)]
        V[m] = dict(R=R, d=d, ax=ax, dis=M["eval_dismissive"])
        res.setdefault("split_half_axis_cos", {})[m] = cos(axh[0], axh[1]).tolist()
        res.setdefault("axis_norm", {})[m] = ax.norm(dim=-1).tolist()
    up = V["parent"]["ax"] / V["parent"]["ax"].norm(dim=-1, keepdim=True)
    Up = {}
    for l in range(64):
        Xp = V["parent"]["R"][:, l] - V["parent"]["R"][:, l].mean(0)
        _, _, Vt = torch.linalg.svd(Xp, full_matrices=False); Up[l] = Vt[:10].T  # [H, 10]
    iu = np.triu_indices(len(roles), 1)
    Gp = {}
    for l in range(64):
        P = V["parent"]["R"][:, l] - V["parent"]["d"][l]; P = P / P.norm(dim=-1, keepdim=True); Gp[l] = (P @ P.T).numpy()[iu]
    paxc = (V["parent"]["R"] * up[None]).sum(-1)  # [roles, 64] parent axis coordinate of each role
    for m in models:
        v = V[m]; u = v["ax"] / v["ax"].norm(dim=-1, keepdim=True)
        res.setdefault("axis_cos_vs_parent", {})[m] = cos(v["ax"], V["parent"]["ax"]).tolist()
        res.setdefault("proj_on_parent_axis", {})[m] = dict(default=(v["d"] * up).sum(-1).tolist(),
                                                            role_mean=(v["R"].mean(0) * up).sum(-1).tolist(),
                                                            eval_dismissive=(v["dis"] * up).sum(-1).tolist())
        pc1, ang, gc = [], [], []
        for l in range(64):
            Xm = v["R"][:, l] - v["R"][:, l].mean(0)
            _, _, Vt = torch.linalg.svd(Xm, full_matrices=False)
            pc1.append(abs(cos(Vt[0], v["ax"][l], 0).item()))
            ang.append(torch.linalg.svdvals(Vt[:10] @ Up[l]).tolist())  # cosines of the 10 principal angles
            P = v["R"][:, l] - v["d"][l]; P = P / P.norm(dim=-1, keepdim=True)
            gc.append(float(np.corrcoef((P @ P.T).numpy()[iu], Gp[l])[0, 1]))
        res.setdefault("pc1_own_axis_abs_cos", {})[m] = pc1
        res.setdefault("top10_principal_angle_cos_vs_parent", {})[m] = ang
        res.setdefault("persona_geometry_corr_vs_parent", {})[m] = gc
        if m == "parent":
            continue
        Dr = v["R"] - V["parent"]["R"]  # [roles, 64, H]
        sh = Dr.mean(0); sp = Dr - sh[None]
        spn = sp.norm(dim=-1)  # [roles, 64]
        res.setdefault("update", {})[m] = dict(
            shared_norm=sh.norm(dim=-1).tolist(), specific_norm_mean=spn.mean(0).tolist(),
            specific_norm_median=spn.median(0).values.tolist(), total_norm_mean=Dr.norm(dim=-1).mean(0).tolist(),
            parent_role_norm_mean=V["parent"]["R"].norm(dim=-1).mean(0).tolist(),
            default_update_norm=(v["d"] - V["parent"]["d"]).norm(dim=-1).tolist(),
            eval_dismissive_update_norm=(v["dis"] - V["parent"]["dis"]).norm(dim=-1).tolist(),
            shared_cos_parent_axis=cos(sh, V["parent"]["ax"]).tolist(),
            default_update_cos_shared=cos(v["d"] - V["parent"]["d"], sh).tolist(),
            rho_specific_norm_vs_parent_axis_coord=[spearman(spn[:, l].numpy(), paxc[:, l].numpy()) for l in range(64)],
            top_specific_roles_L32=[(roles[i], round(spn[i, 32].item(), 2)) for i in spn[:, 32].argsort(descending=True)[:12]],
            bottom_specific_roles_L32=[(roles[i], round(spn[i, 32].item(), 2)) for i in spn[:, 32].argsort()[:12]])
        torch.save(dict(shared=sh.half(), specific_norm=spn, roles=roles), f"{E1}/update_{m}.pt")
    pairs = [(x, y) for i, x in enumerate(models) for y in models[i + 1:]]
    res["axis_cos_pairwise"] = {f"{x}|{y}": cos(V[x]["ax"], V[y]["ax"]).tolist() for x, y in pairs}
    json.dump(res, open(f"{E1}/compare.json", "w"), indent=1)
    torch.save({m: dict(axis=V[m]["ax"].half(), default=V[m]["d"].half(), eval_dismissive=V[m]["dis"].half(),
                        role_means=V[m]["R"].half()) for m in models} | {"roles": roles}, f"{E1}/axes_defaults_roles.pt")
    figures(res, models)
    sel = [16, 32, 40, 48, 63]
    for m in models:
        print(f"{m:8s} axis cos vs parent L{sel}: {[round(res['axis_cos_vs_parent'][m][l], 3) for l in sel]} | "
              f"default on parent axis: {[round(res['proj_on_parent_axis'][m]['default'][l], 1) for l in sel]} | "
              f"geom corr: {[round(res['persona_geometry_corr_vs_parent'][m][l], 3) for l in sel]}")


def figures(res, models):
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fd = f"{E1}/figs"; os.makedirs(fd, exist_ok=True)
    L = range(64); oth = [m for m in models if m != "parent"]

    def fig(name, title, lines, ylabel, ylim=None):
        f, ax = plt.subplots(figsize=(9, 5))
        for lab, y, kw in lines:
            ax.plot(L, y, label=lab, **kw)
        ax.set_xlabel("layer L (output of layers[L])"); ax.set_ylabel(ylabel); ax.set_title(title)
        if ylim: ax.set_ylim(*ylim)
        ax.legend(fontsize=7); f.tight_layout(); f.savefig(f"{fd}/{name}.png", dpi=120); plt.close(f)

    fig("axis_cos_vs_parent", "Assistant Axis: cosine with the parent's axis",
        [(m, res["axis_cos_vs_parent"][m], {}) for m in oth] + [("parent split-half (diff. texts)", res["split_half_axis_cos"]["parent"], dict(ls=":", color="k"))],
        "cosine")
    fig("default_on_parent_axis", "Default's position on the parent's unit axis (dotted: mean role)",
        [(m, res["proj_on_parent_axis"][m]["default"], {}) for m in models], "projection")
    fig("pc1_own_axis", "|cos(PC1 of role vectors, own axis)|", [(m, res["pc1_own_axis_abs_cos"][m], {}) for m in models], "|cos|", (0, 1))
    fig("principal_angles_mean", "Top-10 role subspace vs parent's: mean cosine of the 10 principal angles",
        [(m, [float(np.mean(a)) for a in res["top10_principal_angle_cos_vs_parent"][m]], {}) for m in oth], "mean cos")
    fig("persona_geometry_corr", "Persona-direction cosine matrix: correlation with the parent's",
        [(m, res["persona_geometry_corr_vs_parent"][m], {}) for m in oth], "corr")
    fig("update_shared_vs_specific", "Update per persona: shared norm (solid), mean role-specific norm (dashed)",
        sum([[(f"{m} shared", res["update"][m]["shared_norm"], {}),
              (f"{m} specific", res["update"][m]["specific_norm_mean"], dict(ls="--"))] for m in oth], []), "norm")
    fig("update_specific_vs_axis_rho", "Spearman: |role-specific update| vs role's parent axis coordinate",
        [(m, res["update"][m]["rho_specific_norm_vs_parent_axis_coord"], {}) for m in oth], "rho", (-1, 1))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd"); ap.add_argument("--models", default=",".join(X.CORE + X.OPTIONAL))
    a = ap.parse_args(); ms = a.models.split(",")
    (reduce if a.cmd == "reduce" else compare)(ms)


if __name__ == "__main__":
    main()
