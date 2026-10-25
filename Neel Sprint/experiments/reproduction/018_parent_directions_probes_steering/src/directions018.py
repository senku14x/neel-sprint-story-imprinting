"""018 directions and their checks (spec §7.2; executor-4, 25 Oct 2026). CPU only, streams activation chunks.
Directions use the TRAIN split only (extraction questions, train prompts), so the held-out questions stay clean for
probes (§8.1) and steering (§8.2). All 64 layers; L = output of model.model.layers[L].
  axis          = mean(default) - mean over roles of fully-role-playing role means (each role weighted equally;
                  a role enters if it has >= 10 fully rollouts; split-half: >= 5 per half)
  role_X        = mean(role X fully) - mean(default)  (and somewhat versions where >= 10 kept)
  story_X       = mean(story X kept) - mean(default), X in 5 characters + eval_dismissive
  trait_T       = mean(pos kept) - mean(neg kept)
  random_0..4   = seeded Gaussian per layer, unit (seeds 18..22; amendment A1)
Outputs (RUN, then copied to results/): means_parent.pt, directions_parent.pt, directions_checks.json.
  OMP_NUM_THREADS=8 /root/venvs/si/bin/python directions018.py"""
import json, os, random, sys
from collections import defaultdict

import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common018 as C  # noqa: E402

torch.set_num_threads(8)
ACTS = f"{C.RUN}/acts_parent/own"
P002 = "/workspace/Neel Sprint/experiments/reproduction/002_assistant_axis/src/results/axes_and_defaults.pt"


def unit(x):
    return x / x.norm(dim=-1, keepdim=True).clamp_min(1e-12)


def main():
    rows = {r["id"]: r for r in C.build_rows()}
    F = json.load(open(f"{C.RES}/filters.json"))
    kept = F["kept"]
    member = defaultdict(list)  # key -> list of group names
    train_q, held_q, _ = C.questions()
    half = {q: i % 2 for i, q in enumerate(random.Random(1818).sample(train_q, len(train_q)))}  # seeded 24/24 split
    for g, keys in kept.items():
        for k in keys:
            r = rows[k.rsplit("|", 1)[0]]
            if r["split"] != "train":
                continue
            member[k].append(g)
            if g == "default" or g.startswith("role_fully|"):
                member[k].append(f"{g}#h{half[r['qid']]}")
    sums, cnt = {}, defaultdict(int)
    files = sorted(f for f in os.listdir(ACTS) if f.startswith("chunk_"))
    for fn in files:
        z = torch.load(f"{ACTS}/{fn}", mmap=True)  # mmap: 14x faster than a full read on this box (decisions D15)
        R = z["resp"]
        for i, k in enumerate(z["keys"]):
            for g in member.get(k, []):
                v = R[i].float()
                if g in sums:
                    sums[g] += v
                else:
                    sums[g] = v.clone()
                cnt[g] += 1
        print(fn, len(sums), "groups", flush=True)
    means = {g: sums[g] / cnt[g] for g in sums}
    dflt = means["default"]
    roles_fully = sorted(g.split("|")[1] for g in means if g.startswith("role_fully|") and "#" not in g and cnt[g] >= 10)
    RV = torch.stack([means[f"role_fully|{r}"] for r in roles_fully])  # [nR, 64, H]
    axis = dflt - RV.mean(0)
    D = {"axis": axis}
    for c in C.STORY_CHARS + ["eval_dismissive"]:
        if f"story|{c}" in means:
            D[f"story_{c}"] = means[f"story|{c}"] - dflt
    for t in C.TRAITS:
        if f"trait_pos|{t}" in means and f"trait_neg|{t}" in means:
            D[f"trait_{t}"] = means[f"trait_pos|{t}"] - means[f"trait_neg|{t}"]
    for i in range(C.N_RANDOM):  # amendment A1: 5 seeded random directions (seeds 18..22); random_0 = the original
        D[f"random_{i}"] = unit(torch.randn(C.N_LAYERS, C.HIDDEN, generator=torch.Generator().manual_seed(18 + i)))
    role_dirs = {r: (means[f"role_fully|{r}"] - dflt).half() for r in roles_fully}
    roles_some = sorted(g_.split("|")[1] for g_ in means if g_.startswith("role_somewhat|") and cnt[g_] >= 10)
    role_dirs_somewhat = {r: (means[f"role_somewhat|{r}"] - dflt).half() for r in roles_some}

    # checks
    ck = {}
    def axis_half(h):
        rs = [r for r in roles_fully if cnt.get(f"role_fully|{r}#h{h}", 0) >= 5]
        return means[f"default#h{h}"] - torch.stack([means[f"role_fully|{r}#h{h}"] for r in rs]).mean(0), len(rs)
    a0, n0 = axis_half(0); a1, n1 = axis_half(1)
    cs = torch.nn.functional.cosine_similarity(a0, a1, dim=-1)
    ck["axis_split_half_cos"] = {str(L): float(cs[L]) for L in range(C.N_LAYERS)}
    ck["axis_split_half_roles_used"] = [n0, n1]
    if os.path.exists(P002):
        a2 = torch.load(P002, map_location="cpu", weights_only=False)["parent"]["axis"].float()
        c2 = torch.nn.functional.cosine_similarity(axis, a2, dim=-1)
        ck["cos_axis_018_vs_002"] = {str(L): float(c2[L]) for L in range(C.N_LAYERS)}
        ck["cos_axis_018_vs_002_note"] = ("002 read hidden_states[l+1]; at l = 63 that is the final-norm output "
                                          "(HF tie_last_hidden_states), so L63 compares different quantities")
    pc = {}
    for L in (24, 32, 40):
        X = RV[:, L] - RV[:, L].mean(0)
        U, S, Vt = torch.linalg.svd(X, full_matrices=False)
        pc1 = Vt[0]
        proj_roles = RV[:, L] @ pc1; proj_def = dflt[L] @ pc1
        lo, hi = float(proj_roles.min()), float(proj_roles.max())
        pc[str(L)] = dict(cos_pc1_axis=float(torch.nn.functional.cosine_similarity(pc1, axis[L], dim=0)),
                          var_explained_pc1=float(S[0] ** 2 / (S ** 2).sum()),
                          default_relative_position_on_pc1=float((proj_def - lo) / (hi - lo)),
                          n_roles=len(roles_fully))
    ck["pc1"] = pc
    names = ["axis"] + [k for k in D if k.startswith("story_")] + [k for k in D if k.startswith("trait_")] + C.RANDOMS
    cm = {}
    for L in (24, 32, 40):
        M = unit(torch.stack([D[n][L] for n in names]))
        cm[str(L)] = (M @ M.T).tolist()
    ck["cosine_matrix"] = dict(names=names, by_layer=cm)
    ck["counts"] = {g_: cnt[g_] for g_ in sorted(cnt) if "#" not in g_}
    ck["roles_fully_used"] = len(roles_fully); ck["roles_somewhat_used"] = len(roles_some)
    nb = torch.load(f"{ACTS}/nbar.pt")["nbar"]
    pv_coef = {n: {str(L): float(nb[L] / D[n][L].norm()) for L in C.STEER_LAYERS} for n in names if not n.startswith("random")}
    ck["pv_equivalent_coef_per_unit_alpha"] = pv_coef  # c = alpha * Nbar_L / ||d_raw||; multiply by alpha
    meta = dict(layer_convention="L = output of decoder block model.model.layers[L], 0..63 (forward hook); "
                                 "= HF hidden_states[L+1] for L <= 62; HF hidden_states[64] is the final-norm output",
                questions=dict(train=train_q, held=held_q, half_split_seed=1818), split_used="train only",
                min_fully_per_role=10, nbar=nb.tolist(), model=C.BASE + " (Qwen/Qwen3.6-27B @ 6a9e13bd)",
                kept_counts={k: len(v) for k, v in kept.items()}, rng="torch.Generator seeds 18..22 for random_0..random_4")
    out = dict(raw={n: D[n].float() for n in names}, unit={n: unit(D[n].float()) for n in names},
               norms={n: D[n].float().norm(dim=-1) for n in names}, role_dirs_fully=role_dirs,
               role_dirs_somewhat=role_dirs_somewhat, nbar=nb, meta=meta)
    torch.save(out, f"{C.RUN}/directions_parent.pt")
    torch.save(dict(means={g_: v.half() for g_, v in means.items() if "#" not in g_}, counts=dict(cnt)), f"{C.RUN}/means_parent.pt")
    json.dump(ck, open(f"{C.RES}/directions_checks.json", "w"), indent=1)
    print(json.dumps(dict(split_half_L32=ck["axis_split_half_cos"]["32"],
                          cos002_L32=ck.get("cos_axis_018_vs_002", {}).get("32"), pc1=pc), indent=1))


if __name__ == "__main__":
    main()
