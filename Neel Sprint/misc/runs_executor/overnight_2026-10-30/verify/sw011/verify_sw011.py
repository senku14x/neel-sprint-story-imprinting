"""Blind recompute for sw011 (executor-9 overnight verify). Reads only raw files:
A_gen.jsonl, B_btw.jsonl, B_free.jsonl, capA_<m>.pt (HF header means), dirs_hist_<m>.pt (sw009-fitted directions).
Labels: lib/labels.py STRICT. No analysis outputs of sw011 are read.
Run on box3: OMP_NUM_THREADS=6 nice -n 10 /root/venvs/si/bin/python -I verify_sw011.py
"""
import json, sys, collections
import numpy as np
import torch
from scipy.stats import spearmanr

torch.set_num_threads(6)
sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import labels  # noqa: E402

RUN = "/workspace/runs_executor/sw011"
OUT = "/workspace/runs_executor/overnight_2026-10-30/verify/sw011/verify_sw011_out.json"
LAYERS = list(range(16, 64))
HELPER = {"hdA0": "bee", "hdB0": "crow"}
NBOOT = 2000
rng = np.random.default_rng(20261031)


def read_jsonl(fn):
    with open(fn) as f:
        return [json.loads(l) for l in f]


def role(text, model):
    return labels.role_label(labels.strict_label(text), HELPER[model])


def rival_share(roles):
    c = collections.Counter(roles)
    n = c["rival"] + c["both"] + c["helper"]
    return ((c["rival"] + 0.5 * c["both"]) / n if n else float("nan")), n, len(roles)


res = {}

# ------------------------------------------------------------------ Part A behaviour
A = read_jsonl(f"{RUN}/A_gen.jsonl")
A_btw = collections.defaultdict(list)
for r in A:
    if r["readout"] == "btw" and r["model"] in HELPER and r["arm"] == "none":
        A_btw[(r["model"], r["cond"])].append(r)

for m in ("hdA0", "hdB0"):
    cap = torch.load(f"{RUN}/capA_{m}.pt", map_location="cpu", weights_only=False)
    dirs = torch.load(f"{RUN}/dirs_hist_{m}.pt", map_location="cpu", weights_only=False)
    keys = cap["keys"]
    assert len(keys) == len(set(keys)) == 896
    H = cap["hdr_mean"][:, LAYERS, :].float()  # (896, 48, 5120)
    # scenario of a sid = the fold whose fit set excludes it
    fit = dirs["fit_sids"]
    scens = [k for k in fit if k != "all"]
    scen_of = {}
    for sid in fit["all"]:
        out = [k for k in scens if sid not in fit[k]]
        assert len(out) == 1, (sid, out)
        scen_of[sid] = out[0]
    conds = sorted({k.split("|")[0] for k in keys})
    sids = [k.split("|", 1)[1] for k in keys]
    kc = [k.split("|")[0] for k in keys]
    assert len(conds) == 14 and all(sid in scen_of for sid in sids)

    # forced rival share per condition
    y = {}
    yn = {}
    for c in conds:
        rows = A_btw[(m, c)]
        assert len(rows) == 256, (m, c, len(rows))
        rs, nh, nt = rival_share([role(r["text"], m) for r in rows])
        y[c] = rs
        yn[c] = (nh, nt)

    def proj_score(get_dir):
        """per-context: dot with the context's held-out-fold unit direction per layer, z-score per layer across
        all 896 contexts, mean over layers."""
        P = torch.empty(len(keys), len(LAYERS))
        for s in scens:
            idx = [i for i, sid in enumerate(sids) if scen_of[sid] == s]
            D = get_dir(dirs["scen"][s])[LAYERS, :].float()  # (48, 5120)
            D = D / D.norm(dim=-1, keepdim=True)  # already unit; re-normalised after fp16
            P[idx] = torch.einsum("nld,ld->nl", H[idx], D)
        Z = (P - P.mean(0, keepdim=True)) / P.std(0, keepdim=True)
        sc = Z.mean(1).numpy()
        return {c: float(np.mean([sc[i] for i in range(len(keys)) if kc[i] == c])) for c in conds}

    def rho_of(x):
        cs = conds
        return float(spearmanr([x[c] for c in cs], [y[c] for c in cs]).statistic)

    x_ds = proj_score(lambda d: d["d_self"])
    rho_ds = rho_of(x_ds)
    nulls = {}
    for j in range(10):
        nulls[f"shuf{j}"] = rho_of(proj_score(lambda d, j=j: d["shuf"][j]))
        nulls[f"cov{j}"] = rho_of(proj_score(lambda d, j=j: d["cov"][j]))
    order = sorted(conds, key=lambda c: x_ds[c])
    nosys_rank = order.index("nosys") + 1
    maxabs = max(abs(v) for v in nulls.values())

    # d_t1 all-script (sys_contempt - nosys) vs all-script d_self, per layer cosine (layers 16-63)
    i_c = {sid: i for i, (c, sid) in enumerate(zip(kc, sids)) if c == "sys_contempt"}
    i_n = {sid: i for i, (c, sid) in enumerate(zip(kc, sids)) if c == "nosys"}
    common = sorted(set(i_c) & set(i_n))
    assert len(common) == 64
    dt1 = H[[i_c[s] for s in common]].double().mean(0) - H[[i_n[s] for s in common]].double().mean(0)  # (48, 5120)
    dsa = dirs["scen"]["all"]["d_self"][LAYERS, :].double()
    cos = torch.nn.functional.cosine_similarity(dt1, dsa, dim=-1).numpy()

    res[m] = dict(
        rho_dself=rho_ds, n_conds=len(conds),
        null_rhos=nulls, null_max_abs=maxabs, null_max_signed=max(nulls.values()),
        beats_nulls=bool(rho_ds > maxabs), nosys_rank_from_low=nosys_rank, nosys_in_bottom5=bool(nosys_rank <= 5),
        cond_x_dself=x_ds, cond_y_rival=y, cond_n_habit_total=yn, order_low_to_high=order,
        cos_dt1_dself_mean=float(cos.mean()), cos_dt1_dself_by_layer={L: float(v) for L, v in zip(LAYERS, cos)},
        cos_at={L: float(cos[LAYERS.index(L)]) for L in (24, 40, 56)},
    )
    print(m, "rho_dself", round(rho_ds, 4), "null_max_abs", round(maxabs, 4), "nosys rank", nosys_rank,
          "cos_dt1_dself mean", round(float(cos.mean()), 4), flush=True)
    del H, cap

# ------------------------------------------------------------------ Part B
def cells(fn):
    out = collections.defaultdict(list)
    for r in read_jsonl(fn):
        out[(r["model"], r["direction"], r["arm"])].append(r)
    return out


def by_sid(rows, m):
    d = collections.defaultdict(list)
    for r in rows:
        d[r["sid"]].append(role(r["text"], m))
    return d


def boot_move(base_rows, arm_rows, m, sign):
    """move = sign * (rs(arm) - rs(base)); script bootstrap (resample the 64 scripts, same draw for both arms)."""
    b, a = by_sid(base_rows, m), by_sid(arm_rows, m)
    S = sorted(b)
    assert sorted(a) == S
    pt = sign * (rival_share(sum((a[s] for s in S), []))[0] - rival_share(sum((b[s] for s in S), []))[0])
    bs = []
    for _ in range(NBOOT):
        draw = rng.integers(0, len(S), len(S))
        ss = [S[i] for i in draw]
        ra = rival_share(sum((a[s] for s in ss), []))[0]
        rb = rival_share(sum((b[s] for s in ss), []))[0]
        if not (np.isnan(ra) or np.isnan(rb)):
            bs.append(sign * (ra - rb))
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return float(pt), [float(lo), float(hi)], len(bs)


def summarize(cell, m, d, arm):
    rows = cell[(m, d, arm)]
    rs, nh, nt = rival_share([role(r["text"], m) for r in rows])
    return dict(rs=rs, n_habit=nh, n=nt, cap_hit=float(np.mean([bool(r.get("cap_hit")) for r in rows])),
                onset=nh / nt)


Bb = cells(f"{RUN}/B_btw.jsonl")
Bf = cells(f"{RUN}/B_free.jsonl")
B = {}
for m in ("hdA0", "hdB0"):
    gap = summarize(Bb, m, "rem", "none")["rs"] - summarize(Bb, m, "ind", "none")["rs"]
    B[f"{m}|gap"] = gap
    for d, sign in (("ind", +1), ("rem", -1)):
        # sign: ind moves toward the donor = rs up; rem moves toward the default = rs down. move = sign*(arm-none)
        for readout, cell in (("btw", Bb), ("free", Bf)):
            base = cell[(m, d, "none")]
            assert len(base) == 128
            arms = sorted(a for (mm, dd, a) in cell if mm == m and dd == d)
            for a in arms:
                rows = cell[(m, d, a)]
                assert len(rows) == 128, (m, d, a, len(rows))
                s = summarize(cell, m, d, a)
                if a != "none":
                    mv, ci, nb = boot_move(base, rows, m, sign)
                    s.update(move=mv, ci95=ci, nboot_valid=nb)
                B[f"{m}|{d}|{readout}|{a}"] = s
res["B"] = B
for k in ("hdA0|ind|btw|whole", "hdB0|rem|btw|whole", "hdB0|rem|btw|dself", "hdB0|rem|btw|dt1", "hdB0|rem|free|dself"):
    print(k, {kk: B[k][kk] for kk in ("rs", "n_habit", "move", "ci95")}, flush=True)
print("gaps", B["hdA0|gap"], B["hdB0|gap"])
json.dump(res, open(OUT, "w"), indent=1, default=float)
print("wrote", OUT)
