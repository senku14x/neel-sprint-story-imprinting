"""E09 R02 Stage 4c analysis: R01's code/e09_states_analysis.py with R01's saved per-row states for parent, S, R, RD
and RD3 and this run's states for Rshort (R05's r05_lib, copied unchanged into code/); R01's models are recomputed
with the same code (they should equal R01's tables). The replication step compares this run's fresh parent Part 1
states (v_axis stop check) with R01's. Outputs under e09/r02/results/states. R01's docstring follows.

E09 R01 Stage 4c analysis: R05's measures (r05_lib.cell, unchanged) for Part 1 (turn 3, P01/P02/P04/P05) and Part 2
(turn 1, 270 non-default personas), plus the new movement measures and the Part 2 Spearman table; replication against
R05's saved block-32 states.

python e09_states_analysis.py --steps part1,move1,part2,repl,push
"""
import argparse, json, os, sys, time

import numpy as np
import torch

sys.path.insert(0, "/workspace/e09/r02/code")  # copy of /workspace/e05/r05/driver/r05_lib.py (same sha256)
from r05_lib import DIRS, boot_weights, cell, null_stats, remainder_vectors, spearman_boot, summ  # noqa: E402  (read only)

torch.set_grad_enabled(False)
W = "/workspace/e09/r02"
R01 = "/workspace/e09/r01"
ST = f"{R01}/states"   # R01's saved states (parent, S, R, RD, RD3)
ST2 = f"{W}/states"    # this run (Rshort; fresh parent Part 1 for the stop check)
RES = f"{W}/results/states"
PUSH = f"{W}/push_states"
R04 = "/workspace/e05/r04"
R05P = "/workspace/e05/r05/push_states"
AX = "/workspace/si36/axis_pv"
P1_PIDS = ["P01", "P02", "P04", "P05"]
ALL_P1 = ["P00"] + P1_PIDS
PNAME = {"P00": "default", "P01": "dismissive", "P02": "sam", "P03": "alex", "P04": "drew", "P05": "terse"}
os.makedirs(RES, exist_ok=True); os.makedirs(PUSH, exist_ok=True)
LOGF = open(f"{W}/logs/states_analysis_events.jsonl", "a")


def log(**kw):
    kw["t"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    LOGF.write(json.dumps(kw, default=str) + "\n"); LOGF.flush()
    print(json.dumps(kw, default=str)[:1500], flush=True)


def sdir(m):
    return ST2 if m == "Rshort" else ST


def have(part, m):
    return os.path.exists(f"{sdir(m)}/part{part}_{m}.done")


D = torch.load(f"{R04}/stageb/directions.pt", weights_only=False)
U = {bl: torch.stack([D["unit"][bl][k].double() for k in DIRS]) for bl in (24, 32)}
torch.manual_seed(0)
N1 = torch.randn(1000, 5120)
N1 = (N1 / N1.norm(dim=1, keepdim=True)).double()
RV = torch.load(f"{AX}/aa/out/role_vectors.pt", weights_only=False)


def n2(bl):
    i = list(RV["blocks"]).index(bl)
    v = RV["vectors"][:, i].double()
    v = v - v.mean(0, keepdim=True)
    return v / v.norm(dim=1, keepdim=True)


N2 = {bl: n2(bl) for bl in (24, 32)}
IDX1 = json.load(open(f"{ST}/part1_index.json"))
POS1 = {it["key"]: i for i, it in enumerate(IDX1)}
SIDS = sorted({it["sid"] for it in IDX1})
WT1 = boot_weights(len(SIDS))
SW1 = WT1.sum(1)
_cache = {}


def S1(m, bl):
    k = (1, m, bl)
    if k not in _cache:
        _cache[k] = torch.load(f"{sdir(m)}/part1_{m}_b{bl}.pt").double()
    return _cache[k]


def rows1(pid, inp, trig, sids=None):
    return [POS1[f"{pid}|{inp}|{trig}|{s}"] for s in (sids or SIDS)]


def parts(H, pid, trig, sids=None):
    w, n0 = H[rows1(pid, "with_sys", trig, sids)], H[rows1("P00", "with_sys", trig, sids)]
    ns = H[rows1(pid, "no_sys", trig, sids)]
    return w - n0, w - ns, ns - n0, n0


def trained(part):
    return [m for m in ["S", "R", "RD", "RD3", "Rshort"] if have(part, m)]


# ---------------- Part 1: R05's cells ----------------
def step_part1(blocks=(32, 24)):
    cells, ph_rows = [], []
    TR = trained(1)
    for bl in blocks:
        Hp = S1("parent", bl)
        for trig in ["on", "off"]:
            for pid in P1_PIDS:
                gp, sig_p, eta_p, n0p = parts(Hp, pid, trig)
                for m in TR:
                    Hm = S1(m, bl)
                    gm, sig_m, eta_m, n0m = parts(Hm, pid, trig)
                    d = n0m - n0p
                    Ub = U.get(bl)
                    o, ph = cell(WT1, gm, gp, sig_p, eta_p, sig_m, eta_m, d, Ub)
                    rec = dict(model=m, persona_id=pid, persona=PNAME[pid], trigger=trig, block=bl, input="with_sys",
                               n=len(SIDS))
                    for k, v in o.items():
                        rec[k] = dict(zip(DIRS, summ(v))) if k.startswith("M6_") else summ(v)
                    a1 = float(o["alpha"][0]); a_s = float(o["alpha_sig"][0]); a_e = float(o["alpha_eta"][0])
                    r1, r2 = remainder_vectors(gm, gp, a1, sig_p, eta_p, a_s, a_e)
                    rec["M7_rem1"] = null_stats(r1, N1, N2[bl], Ub)
                    rec["M7_rem2"] = null_stats(r2, N1, N2[bl], Ub)
                    cells.append(rec)
                    for i, sid in enumerate(SIDS if m == "Rshort" else []):
                        row = dict(model=m, persona_id=pid, trigger=trig, block=bl, script_id=sid)
                        for k, v in ph.items():
                            row[k] = float(v[i]) if v.dim() == 1 else dict(zip(DIRS, [float(x) for x in v[i]]))
                        ph_rows.append(row)
            log(event="part1_block_trig", block=bl, trigger=trig, models=TR)
    with open(f"{RES}/part1_cells.jsonl", "w") as f:
        for r in cells:
            f.write(json.dumps(r) + "\n")
    with open(f"{RES}/part1_per_history.jsonl", "w") as f:
        for r in ph_rows:
            f.write(json.dumps(r) + "\n")
    with open(f"{RES}/part1_projections.jsonl", "w") as f:
        for m in ["Rshort"]:  # E09 R02: projections for this run's model only (R01 pushed the others)
            if m not in TR:
                continue
            P = {bl: (S1(m, bl) @ U[bl].T) for bl in (24, 32)}
            for i, it in enumerate(IDX1):
                f.write(json.dumps(dict(model=m, persona_id=it["pid"], persona=it["persona"], input=it["input"],
                                        trigger=it["trigger"], script_id=it["sid"], prompt_tokens=it["n_tokens"],
                                        proj={str(bl): dict(zip(DIRS, [float(x) for x in P[bl][i]])) for bl in (24, 32)})) + "\n")
    log(event="part1_done", n_cells=len(cells))


# ---------------- Part 1: movement ----------------
def step_move1(blocks=(32, 24)):
    out, per = [], []
    TR = trained(1)
    for bl in blocks:
        Hp = S1("parent", bl)
        for pid in ALL_P1:
            for inp in ["with_sys", "no_sys"]:
                if pid == "P00" and inp == "no_sys":
                    continue
                for trig in ["on", "off"]:
                    rr = rows1(pid, inp, trig)
                    dist = {m: (S1(m, bl)[rr] - Hp[rr]).norm(dim=1) for m in TR}
                    Mb = {m: (WT1 @ dist[m]) / SW1 for m in TR}
                    for m in TR:
                        rec = dict(model=m, persona_id=pid, persona=PNAME[pid], input=inp, trigger=trig, block=bl,
                                   n=len(SIDS), M=summ(Mb[m]),
                                   ratio_to_S=(summ(Mb[m] / Mb["S"]) if "S" in Mb else None),
                                   ratio_to_R=(summ(Mb[m] / Mb["R"]) if "R" in Mb else None),
                                   parent_state_norm_mean=float(Hp[rr].norm(dim=1).mean()))
                        out.append(rec)
                        for i, sid in enumerate(SIDS):
                            per.append(dict(model=m, persona_id=pid, input=inp, trigger=trig, block=bl, script_id=sid,
                                            dist=float(dist[m][i])))
    with open(f"{RES}/part1_movement.jsonl", "w") as f:
        for r in out:
            f.write(json.dumps(r) + "\n")
    with open(f"{RES}/part1_movement_per_history.jsonl", "w") as f:
        for r in per:
            f.write(json.dumps(r) + "\n")
    log(event="move1_done", n=len(out))


# ---------------- Part 2 ----------------
def step_part2(blocks=(32,)):
    idx2 = json.load(open(f"{ST}/part2_index.json"))
    pids, sids2 = [], []
    for it in idx2:
        if not pids or pids[-1] != it["pid"]:
            pids.append(it["pid"])
        if it["sid"] not in sids2:
            sids2.append(it["sid"])
    names = {it["pid"]: it["persona"] for it in idx2}
    nP, nS = len(pids), len(sids2)
    assert pids[0] == "P00" and pids[1] == "P01"
    pos = {(it["pid"], it["sid"]): i for i, it in enumerate(idx2)}
    order = torch.tensor([pos[(p, s)] for p in pids for s in sids2])
    WT2 = boot_weights(nS)
    sw = WT2.sum(1)
    ax = DIRS.index("v_axis")
    summary, per_persona, spear = [], [], []
    TR = trained(2)

    def S2(m, bl):
        return torch.load(f"{sdir(m)}/part2_{m}_b{bl}.pt").double()[order].view(nP, nS, -1)

    for bl in blocks:
        Hp = S2("parent", bl)
        gp = Hp[1:] - Hp[:1]                      # [270, nS, D]
        Pgp = gp @ U[bl].T
        PHp = Hp @ U[bl].T
        np2 = (gp * gp).sum(-1)
        npn = np2.sqrt()
        x_r = Pgp[:, :, ax].mean(1)
        gbar = gp.mean(1)                         # [270, D]: g_p, mean over scripts
        g01 = gbar[0]
        cos01 = (gbar @ g01) / (gbar.norm(dim=1) * g01.norm())   # (i)
        gnorm = gbar.norm(dim=1)                                  # (ii)
        axpos = PHp[:, :, ax].mean(1)                             # (iii) [271]
        mean_states = {"parent": Hp.mean(1)}
        dist = {}
        for m in TR:
            Hm = S2(m, bl)
            mean_states[m] = Hm.mean(1)
            dist[m] = (Hm - Hp).norm(dim=-1)      # [271, nS]
        Mb = {m: (WT2 @ dist[m].T) / sw[:, None] for m in TR}   # [B, 271]
        alphas = {}
        for m in TR:
            Hm = S2(m, bl)
            gm = Hm[1:] - Hm[:1]
            mp = (gm * gp).sum(-1); nm2 = (gm * gm).sum(-1); s = gm - gp; ns2 = (s * s).sum(-1)
            Pgm = gm @ U[bl].T
            PHm = Hm @ U[bl].T
            beta = (WT2 @ mp.T) / (WT2 @ np2.T)
            alpha = 1 - beta
            alphas[m] = alpha
            E1 = 1 - (WT2 @ nm2.T - 2 * beta * (WT2 @ mp.T) + beta ** 2 * (WT2 @ np2.T)) / (WT2 @ ns2.T)
            rho = (WT2 @ nm2.sqrt().T) / (WT2 @ npn.T)
            q = lambda x, p: torch.quantile(x, p, dim=1)  # noqa: E731
            rec = dict(model=m, block=bl, n_personas=nP - 1, n_scripts=nS)
            rec["a_alpha"] = {k: summ(v) for k, v in {"median": q(alpha, 0.5), "q25": q(alpha, 0.25), "q75": q(alpha, 0.75),
                                                        "mean": alpha.mean(1)}.items()}
            rec["a_alpha_named"] = {f"{p}_{PNAME[p]}": summ(alpha[:, pids.index(p) - 1]) for p in ["P01", "P02", "P03", "P04", "P05"]}
            rec["rho_named"] = {f"{p}_{PNAME[p]}": summ(rho[:, pids.index(p) - 1]) for p in ["P01", "P02", "P03", "P04", "P05"]}
            rec["rho_median"] = summ(q(rho, 0.5))
            rec["E1_median"] = summ(q(E1, 0.5))
            proj_m = PHm[:, :, ax].mean(1)
            rec["d_spearman_axis_proj_271"] = spearman_boot(axpos, proj_m)
            rec["d_spearman_axis_gap_270"] = spearman_boot(x_r, Pgm[:, :, ax].mean(1))
            rec["movement_M_named"] = {f"{p}_{PNAME[p]}": summ(Mb[m][:, pids.index(p)]) for p in ["P00", "P01", "P02", "P03", "P04", "P05"]}
            rec["movement_M_median_271"] = summ(torch.quantile(Mb[m], 0.5, dim=1))
            if "S" in Mb:
                ratio = Mb[m] / Mb["S"]
                rec["movement_ratio_to_S_named"] = {f"{p}_{PNAME[p]}": summ(ratio[:, pids.index(p)]) for p in ["P00", "P01", "P02", "P03", "P04", "P05"]}
                rec["movement_ratio_to_S_median_271"] = summ(torch.quantile(ratio, 0.5, dim=1))
                rec["movement_ratio_to_S_mean_271"] = summ(ratio.mean(1))
            summary.append(rec)
            for i in range(nP):
                pr = dict(model=m, block=bl, persona_id=pids[i], persona=names[pids[i]], M=summ(Mb[m][:, i]),
                          ratio_to_S=(summ(Mb[m][:, i] / Mb["S"][:, i]) if "S" in Mb else None),
                          axis_proj_parent=float(axpos[i]), axis_proj_model=float(proj_m[i]))
                if i > 0:
                    pr.update(alpha=summ(alpha[:, i - 1]), rho=summ(rho[:, i - 1]), E1=summ(E1[:, i - 1]),
                              cos_to_P01_parent=float(cos01[i - 1]), gap_norm_parent=float(gnorm[i - 1]),
                              x_parent_axis_gap=float(x_r[i - 1]))
                per_persona.append(pr)
            del Hm, gm, mp, nm2, ns2, s
        # ---- Spearman table (270 non-default personas; movement ratio and fading share point estimates)
        covs = {"i_cos_to_P01": cos01, "ii_gap_norm": gnorm, "iii_axis_position": axpos[1:]}
        for m in TR:
            ys = {"fading_share_alpha": alphas[m][0]}
            if "S" in Mb and m != "S":
                ys["movement_ratio_to_S"] = (Mb[m][0] / Mb["S"][0])[1:]
            ys["movement_M"] = Mb[m][0][1:]
            for yn, y in ys.items():
                for cn, c in covs.items():
                    spear.append(dict(model=m, block=bl, y=yn, covariate=cn, n=len(y), **spearman_boot(y, c)))
            # quintiles of (i) and (ii): mean movement ratio, bootstrap over personas within the quintile
            if "S" in Mb and m != "S":
                ratio0 = (Mb[m][0] / Mb["S"][0])[1:]
                for cn in ["i_cos_to_P01", "ii_gap_norm"]:
                    c = covs[cn]
                    rk = torch.argsort(torch.argsort(c))
                    quint = (rk * 5) // len(c)
                    for k in range(5):
                        sel = torch.nonzero(quint == k)[:, 0]
                        v = ratio0[sel]
                        rng = np.random.default_rng(0)
                        bi = torch.from_numpy(rng.integers(0, len(v), size=(2000, len(v))))
                        bm = v[bi].mean(1)
                        a_ = alphas[m][0][sel]
                        ba = a_[bi].mean(1)
                        spear.append(dict(model=m, block=bl, kind="quintile", covariate=cn, quintile=k + 1, n=len(v),
                                          c_min=float(c[sel].min()), c_max=float(c[sel].max()), c_mean=float(c[sel].mean()),
                                          movement_ratio_mean=dict(est=float(v.mean()), lo=float(torch.quantile(bm, 0.025)),
                                                                   hi=float(torch.quantile(bm, 0.975))),
                                          alpha_mean=dict(est=float(a_.mean()), lo=float(torch.quantile(ba, 0.025)),
                                                          hi=float(torch.quantile(ba, 0.975)))))
        if bl == 32:
            for m, v in mean_states.items():
                if m == "Rshort":  # E09 R02: R01 pushed the others
                    torch.save(v.to(torch.float16), f"{PUSH}/part2_mean_states_b32_{m}.pt")
            json.dump(dict(personas=[dict(id=p, name=names[p]) for p in pids], scripts=sids2,
                           note="rows = personas in this order; mean over the scripts of the last-prompt-token state, block 32"),
                      open(f"{PUSH}/part2_mean_states_index.json", "w"), indent=0)
        log(event="part2_block", block=bl, models=TR)
    for nm_, rows in [("part2_summary", summary), ("part2_per_persona", per_persona), ("part2_spearman", spear)]:
        with open(f"{RES}/{nm_}.jsonl", "w") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
    log(event="part2_done", n_summary=len(summary), n_spear=len(spear))


# ---------------- E09 R02: this run's fresh parent Part 1 states vs R01's ----------------
def step_repl():
    out = {}
    if os.path.exists(f"{ST2}/part1_parent.done"):
        i2 = json.load(open(f"{ST2}/part1_index.json"))
        same_index = [it["key"] for it in i2] == [it["key"] for it in IDX1] and [it["n_tokens"] for it in i2] == [it["n_tokens"] for it in IDX1]
        out["part1_index_identical_to_R01"] = same_index
        for bl in (32, 24):
            A = torch.load(f"{ST2}/part1_parent_b{bl}.pt").double()
            B = S1("parent", bl)
            pa, pb_ = A @ U[bl].T, B @ U[bl].T
            cellsd = []
            for pid in ALL_P1:
                for inp in ["with_sys", "no_sys"]:
                    if pid == "P00" and inp == "no_sys":
                        continue
                    for trig in ["on", "off"]:
                        rr = rows1(pid, inp, trig)
                        cellsd.append(float((pa[rr].mean(0) - pb_[rr].mean(0)).abs().max()))
            out[f"block{bl}"] = dict(largest_abs_mean_proj_diff_cells=max(cellsd),
                                     largest_abs_per_row_proj_diff=float((pa - pb_).abs().max()),
                                     state_rel_diff=float((A - B).norm() / B.norm()))
    if os.path.exists(f"{ST2}/part2_index.json"):
        i2 = json.load(open(f"{ST2}/part2_index.json"))
        i1 = json.load(open(f"{ST}/part2_index.json"))
        out["part2_index_identical_to_R01"] = ([it["key"] for it in i2] == [it["key"] for it in i1]
                                               and [it["n_tokens"] for it in i2] == [it["n_tokens"] for it in i1])
    json.dump(out, open(f"{RES}/replication_parent_vs_R01.json", "w"), indent=1)
    log(event="repl", **out)


def step_push():
    import shutil
    for m in ["Rshort"]:
        src = f"{ST2}/part1_{m}_b32.pt"
        if os.path.exists(src):
            shutil.copy(src, f"{PUSH}/part1_states_b32_{m}.pt")
    shutil.copy(f"{ST}/part1_index.json", f"{PUSH}/part1_index.json")
    log(event="push_states")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", default="part1,move1,part2,repl,push")
    a = ap.parse_args()
    for st in a.steps.split(","):
        t1 = time.time()
        {"part1": step_part1, "move1": step_move1, "part2": step_part2, "repl": step_repl, "push": step_push}[st]()
        log(event="step_done", step=st, secs=round(time.time() - t1))
