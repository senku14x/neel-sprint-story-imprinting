"""E05 R05 analysis: known-answer test, Part 1 cells (M1-M8), replication checks, Part 2 summaries (a)-(f).

python r05_analysis.py --steps kat,part1,repl,part2,push_states
"""
import argparse, json, os, sys, time

import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r05_lib import DIRS, boot_weights, cell, null_stats, remainder_vectors, spearman_boot, summ  # noqa: E402

torch.set_grad_enabled(False)
W = "/workspace/e05/r05"
ST = f"{W}/states"
RES = f"{W}/results"
PUSH = f"{W}/push_states"
GH = f"{W}/gh/e05"
AX = "/workspace/si36/axis_pv"
TRAINED = os.environ.get("R05_MODELS", "S,SB,Q,C,R").split(",")
P1_PIDS = ["P01", "P02", "P05"]
PNAME = {"P00": "default", "P01": "dismissive", "P02": "sam", "P03": "alex", "P04": "drew", "P05": "terse"}
os.makedirs(RES, exist_ok=True); os.makedirs(PUSH, exist_ok=True)
LOGF = open(f"{W}/logs/analysis_events.jsonl", "a")


def log(**kw):
    kw["t"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    LOGF.write(json.dumps(kw, default=str) + "\n"); LOGF.flush()
    print(json.dumps(kw, default=str)[:1500], flush=True)


def jl(p):
    return [json.loads(l) for l in open(p)]


# ---------------- shared inputs ----------------
D = torch.load(f"{GH}/r04/stageb/directions.pt", weights_only=False)
U = {bl: torch.stack([D["unit"][bl][k].double() for k in DIRS]) for bl in (24, 32)}
torch.manual_seed(0)
N1 = torch.randn(1000, 5120)  # CPU float32, as the brief
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
_cache = {}


def S1(m, bl):
    k = (1, m, bl)
    if k not in _cache:
        _cache[k] = torch.load(f"{ST}/part1_{m}_b{bl}.pt").double()
    return _cache[k]


def rows1(pid, inp, trig, sids=None):
    return [POS1[f"{pid}|{inp}|{trig}|{s}"] for s in (sids or SIDS)]


def parts(H, pid, trig, sids=None):
    """with-sys gap, system part, history part for one model's states H."""
    w, n0 = H[rows1(pid, "with_sys", trig, sids)], H[rows1("P00", "with_sys", trig, sids)]
    ns = H[rows1(pid, "no_sys", trig, sids)]
    return w - n0, w - ns, ns - n0, n0


def S_(x):
    return summ(x) if torch.is_tensor(x) else x


# ---------------- known-answer test ----------------
def step_kat():
    Hp = S1("parent", 32)
    gp, sig_p, eta_p, _ = parts(Hp, "P01", "off")
    u = U[32][0]
    g = torch.Generator().manual_seed(1)
    noise = torch.randn(len(SIDS), 5120, generator=g, dtype=torch.float64)
    noise = 5 * noise / noise.norm(dim=1, keepdim=True)
    res = {}

    def off_span(vecs):
        Q, _ = torch.linalg.qr(vecs.T)
        w = u - Q @ (Q.T @ u)
        return w / w.norm()

    w1 = off_span(gp)
    for tag, gm in [("one_with_w", 0.6 * gp + 2 * w1 + noise), ("one_without_w", 0.6 * gp + noise)]:
        o, _ = cell(WT1, gm, gp, U=U[32])
        exp_rem = 2 * float(w1 @ u) if tag == "one_with_w" else 0.0
        a, rem = float(o["alpha"][0]), float(o["M6_rem1"][0, 0])
        res[tag] = dict(alpha=a, alpha_ci=summ(o["alpha"]), E1=float(o["E1"][0]),
                        M6_v_axis=dict(observed=float(o["M6_observed"][0, 0]), pred1=float(o["M6_pred1"][0, 0]), rem1=rem),
                        expected_rem=exp_rem, w_dot_vaxis=float(w1 @ u),
                        pass_alpha=abs(a - 0.40) <= 0.01, pass_rem=abs(rem - exp_rem) <= 0.05)
    w2 = off_span(torch.cat([sig_p, eta_p], 0))
    for tag, gm in [("two_with_w", 0.5 * sig_p + 0.8 * eta_p + 2 * w2 + noise),
                    ("two_without_w", 0.5 * sig_p + 0.8 * eta_p + noise)]:
        o, _ = cell(WT1, gm, gp, sig_p, eta_p, U=U[32])
        exp_rem = 2 * float(w2 @ u) if tag == "two_with_w" else 0.0
        a_s, a_e, rem = float(o["alpha_sig"][0]), float(o["alpha_eta"][0]), float(o["M6_rem2"][0, 0])
        res[tag] = dict(alpha_sig=a_s, alpha_eta=a_e, alpha_sig_ci=summ(o["alpha_sig"]), alpha_eta_ci=summ(o["alpha_eta"]),
                        alpha_one=float(o["alpha"][0]), E1=float(o["E1"][0]), E2=float(o["E2"][0]),
                        M6_v_axis=dict(observed=float(o["M6_observed"][0, 0]), pred2=float(o["M6_pred2"][0, 0]), rem2=rem,
                                       pred1=float(o["M6_pred1"][0, 0]), rem1=float(o["M6_rem1"][0, 0])),
                        expected_rem=exp_rem, w_dot_vaxis=float(w2 @ u),
                        pass_alpha=abs(a_s - 0.50) <= 0.01 and abs(a_e - 0.20) <= 0.01, pass_rem=abs(rem - exp_rem) <= 0.05)
    res["inputs"] = dict(gp_mean_norm=float(gp.norm(dim=1).mean()), sig_p_mean_norm=float(sig_p.norm(dim=1).mean()),
                         eta_p_mean_norm=float(eta_p.norm(dim=1).mean()), noise_norm=5.0, n=len(SIDS),
                         rank_gp=int(torch.linalg.matrix_rank(gp)), rank_sig_eta=int(torch.linalg.matrix_rank(torch.cat([sig_p, eta_p]))))
    res["all_pass"] = all(v["pass_alpha"] and v["pass_rem"] for k, v in res.items() if isinstance(v, dict) and "pass_alpha" in v)
    json.dump(res, open(f"{RES}/known_answer_test.json", "w"), indent=1)
    log(event="kat", all_pass=res["all_pass"], **{k: (v.get("alpha", v.get("alpha_sig")), v.get("alpha_eta"), v["M6_v_axis"].get("rem1", v["M6_v_axis"].get("rem2")), v["expected_rem"]) for k, v in res.items() if isinstance(v, dict) and "pass_alpha" in v})
    if not res["all_pass"]:
        raise SystemExit("KAT FAILED")


# ---------------- Part 1 ----------------
def step_part1(blocks=(32, 24, 16, 8)):
    cells, ph_rows = [], []
    for bl in blocks:
        Hp = S1("parent", bl)
        for trig in ["on", "off"]:
            for pid in P1_PIDS:
                gp, sig_p, eta_p, n0p = parts(Hp, pid, trig)
                for m in TRAINED:
                    Hm = S1(m, bl)
                    gm, sig_m, eta_m, n0m = parts(Hm, pid, trig)
                    d = n0m - n0p
                    Ub = U.get(bl)
                    o, ph = cell(WT1, gm, gp, sig_p, eta_p, sig_m, eta_m, d, Ub)
                    rec = dict(model=m, persona_id=pid, persona=PNAME[pid], trigger=trig, block=bl, input="with_sys",
                               n=len(SIDS))
                    for k, v in o.items():
                        if k.startswith("M6_"):
                            rec[k] = dict(zip(DIRS, summ(v)))
                        else:
                            rec[k] = summ(v)
                    if Ub is not None:
                        a1 = float(o["alpha"][0]); a_s = float(o["alpha_sig"][0]); a_e = float(o["alpha_eta"][0])
                        r1, r2 = remainder_vectors(gm, gp, a1, sig_p, eta_p, a_s, a_e)
                        rec["M7_rem1"] = null_stats(r1, N1, N2[bl], Ub)
                        rec["M7_rem2"] = null_stats(r2, N1, N2[bl], Ub)
                        rec["M7_rem1"]["norm_mean_rem"] = float(r1.norm()); rec["M7_rem2"]["norm_mean_rem"] = float(r2.norm())
                    cells.append(rec)
                    for i, sid in enumerate(SIDS):
                        row = dict(model=m, persona_id=pid, trigger=trig, block=bl, script_id=sid)
                        for k, v in ph.items():
                            if v.dim() == 1:
                                row[k] = float(v[i])
                            else:
                                row[k] = dict(zip(DIRS, [float(x) for x in v[i]]))
                        ph_rows.append(row)
            log(event="part1_block_trig", block=bl, trigger=trig)
        for m in ["parent"] + TRAINED:
            _cache.pop((1, m, bl), None)
    with open(f"{RES}/part1_cells.jsonl", "w") as f:
        for r in cells:
            f.write(json.dumps(r) + "\n")
    with open(f"{RES}/part1_per_history.jsonl", "w") as f:
        for r in ph_rows:
            f.write(json.dumps(r) + "\n")
    # per-prompt projections (blocks 24, 32) for every model
    with open(f"{RES}/part1_projections.jsonl", "w") as f:
        for m in ["parent"] + TRAINED:
            P = {bl: (S1(m, bl) @ U[bl].T) for bl in (24, 32)}
            for i, it in enumerate(IDX1):
                f.write(json.dumps(dict(model=m, persona_id=it["pid"], persona=it["persona"], input=it["input"],
                                        trigger=it["trigger"], script_id=it["sid"], prompt_tokens=it["n_tokens"],
                                        proj={str(bl): dict(zip(DIRS, [float(x) for x in P[bl][i]])) for bl in (24, 32)})) + "\n")
    log(event="part1_done", n_cells=len(cells), n_ph=len(ph_rows))


# ---------------- replication ----------------
def step_repl():
    r04 = {}
    for r in jl(f"{GH}/r04/stageb/projections_per_history.jsonl"):
        if r["input"] == "a":
            r04[(r["model"], r["persona"], r["trigger"], r["script_id"])] = r["proj"]
    out = {"vs_R04": [], "C_vs_R02": []}
    for m in ["parent", "S", "R", "SB", "Q"]:
        for bl in (24, 32):
            H = S1(m, bl)
            for pid in ["P00", "P01", "P02", "P05"]:
                for trig in ["on", "off"]:
                    pr = H[rows1(pid, "with_sys", trig)] @ U[bl].T
                    for dn in ["v_axis", "v_axis_ns"]:
                        mine = pr[:, DIRS.index(dn)].tolist()
                        theirs = [r04[(m, PNAME[pid], trig, s)][str(bl)][dn] for s in SIDS]
                        dd = [a - b for a, b in zip(mine, theirs)]
                        out["vs_R04"].append(dict(model=m, persona_id=pid, trigger=trig, block=bl, direction=dn,
                                                  mean_r05=sum(mine) / len(mine), mean_r04=sum(theirs) / len(theirs),
                                                  mean_diff=sum(dd) / len(dd), max_abs_diff=max(abs(x) for x in dd)))
    r02 = {}
    for r in jl(f"{GH}/r02/stageb/projections_per_history.jsonl"):
        if r["measure"] == "a_E00" and r["model"] == "C":
            r02[(r["persona"], r["hid"].split("|")[2])] = r["proj"]
    H = S1("C", 32)
    for pid in ["P00", "P01"]:
        pr = H[rows1(pid, "with_sys", "on")] @ U[32].T
        for dn in ["v_axis", "v_axis_ns", "v_style", "v_dis"]:
            mine = pr[:, DIRS.index(dn)].tolist()
            theirs = [r02[(PNAME[pid], s)][dn] for s in SIDS]
            dd = [a - b for a, b in zip(mine, theirs)]
            out["C_vs_R02"].append(dict(model="C", persona_id=pid, trigger="on", block=32, direction=dn,
                                        mean_r05=sum(mine) / len(mine), mean_r02=sum(theirs) / len(theirs),
                                        mean_diff=sum(dd) / len(dd), max_abs_diff=max(abs(x) for x in dd)))
    out["directions_r04_vs_r02_block32_max_abs_diff"] = D["meta"]["vs_r02_block32_max_abs_diff"]
    out["max_abs_diff_all"] = max(r["max_abs_diff"] for r in out["vs_R04"] + out["C_vs_R02"])
    out["max_abs_mean_diff_all"] = max(abs(r["mean_diff"]) for r in out["vs_R04"] + out["C_vs_R02"])
    json.dump(out, open(f"{RES}/replication.json", "w"), indent=1)
    log(event="repl", max_abs_diff_all=out["max_abs_diff_all"], max_abs_mean_diff_all=out["max_abs_mean_diff_all"])


# ---------------- Part 2 ----------------
def step_part2(blocks=(32, 24)):
    idx2 = json.load(open(f"{ST}/part2_index.json"))
    pids = []
    for it in idx2:
        if not pids or pids[-1] != it["pid"]:
            pids.append(it["pid"])
    names = {it["pid"]: it["persona"] for it in idx2}
    sids2 = []
    for it in idx2:
        if it["sid"] not in sids2:
            sids2.append(it["sid"])
    nP, nS = len(pids), len(sids2)
    pos = {(it["pid"], it["sid"]): i for i, it in enumerate(idx2)}
    order = torch.tensor([pos[(p, s)] for p in pids for s in sids2])
    WT2 = boot_weights(nS)
    sw = WT2.sum(1)
    p1 = {(r["model"], r["persona_id"], r["trigger"], r["block"]): r for r in jl(f"{RES}/part1_cells.jsonl")}
    summary, per_persona = [], []
    ax = DIRS.index("v_axis")

    def S2(m, bl):
        return torch.load(f"{ST}/part2_{m}_b{bl}.pt").double()[order].view(nP, nS, -1)

    for bl in blocks:
        if not os.path.exists(f"{ST}/part2_parent_b{bl}.pt"):
            log(event="part2_block_missing", block=bl); continue
        Hp = S2("parent", bl)
        gp = Hp[1:] - Hp[:1]
        Pgp = gp @ U[bl].T  # [270, nS, 5]
        PHp = Hp @ U[bl].T  # [271, nS, 5]
        np2 = (gp * gp).sum(-1)
        npn = np2.sqrt()
        x_r = Pgp[:, :, ax].mean(1)  # parent axis gap per persona
        mean_states = {"parent": Hp.mean(1)}
        for m in TRAINED:
            if not os.path.exists(f"{ST}/part2_{m}_b{bl}.pt"):
                log(event="part2_model_missing", model=m, block=bl); continue
            Hm = S2(m, bl)
            mean_states[m] = Hm.mean(1)
            gm = Hm[1:] - Hm[:1]
            mp = (gm * gp).sum(-1); nm2 = (gm * gm).sum(-1); s = gm - gp; ns2 = (s * s).sum(-1)
            Pgm = gm @ U[bl].T
            PHm = Hm @ U[bl].T
            del s
            beta = (WT2 @ mp.T) / (WT2 @ np2.T)  # [B, 270]
            alpha = 1 - beta
            E1 = 1 - (WT2 @ nm2.T - 2 * beta * (WT2 @ mp.T) + beta ** 2 * (WT2 @ np2.T)) / (WT2 @ ns2.T)
            rho = (WT2 @ nm2.sqrt().T) / (WT2 @ npn.T)
            mgp = torch.einsum("bs,psk->bpk", WT2, Pgp) / sw[:, None, None]  # [B, 270, 5]
            mgm = torch.einsum("bs,psk->bpk", WT2, Pgm) / sw[:, None, None]
            obs = mgm - mgp
            pred1 = -alpha[:, :, None] * mgp
            rem1 = obs - pred1
            # ---- (a)
            q = lambda x, p: torch.quantile(x, p, dim=1)  # noqa: E731
            a_stats = {"median": q(alpha, 0.5), "q25": q(alpha, 0.25), "q75": q(alpha, 0.75), "q05": q(alpha, 0.05),
                       "q95": q(alpha, 0.95), "mean": alpha.mean(1)}
            rec = dict(model=m, block=bl, n_personas=nP - 1, n_scripts=nS)
            rec["a_alpha"] = {k: summ(v) for k, v in a_stats.items()}
            rec["a_alpha_named"] = {f"{p}_{PNAME[p]}": summ(alpha[:, pids.index(p) - 1]) for p in ["P01", "P02", "P03", "P04", "P05"]}
            # ---- (b)
            a0 = alpha[0]
            rec["b_spearman_alpha_x"] = spearman_boot(a0, x_r)
            rec["b_x_summary"] = dict(min=float(x_r.min()), median=float(x_r.median()), max=float(x_r.max()))
            # ---- (c)
            rem_ax = rem1[:, :, ax]
            rec["c_E1"] = {"median": summ(q(E1, 0.5)), "q25": summ(q(E1, 0.25)), "q75": summ(q(E1, 0.75))}
            rec["c_axis_rem1"] = {"median": summ(q(rem_ax, 0.5)), "q25": summ(q(rem_ax, 0.25)), "q75": summ(q(rem_ax, 0.75)),
                                  "mean": summ(rem_ax.mean(1))}
            rec["c_axis_observed_median"] = summ(q(obs[:, :, ax], 0.5))
            rec["c_axis_pred1_median"] = summ(q(pred1[:, :, ax], 0.5))
            rec["c_spearman_rem_x"] = spearman_boot(rem_ax[0], x_r)
            qs = torch.argsort(torch.argsort(x_r))  # rank 0..269
            quint = (qs * 5) // len(x_r)
            rec["c_quintiles"] = []
            for k in range(5):
                sel = quint == k
                rec["c_quintiles"].append(dict(quintile=k + 1, n=int(sel.sum()), x_min=float(x_r[sel].min()),
                                               x_max=float(x_r[sel].max()), x_mean=float(x_r[sel].mean()),
                                               axis_rem1_mean=summ(rem_ax[:, sel].mean(1)),
                                               axis_observed_mean=summ(obs[:, sel, ax].mean(1)),
                                               alpha_mean=summ(alpha[:, sel].mean(1)),
                                               alpha_median=summ(torch.quantile(alpha[:, sel], 0.5, dim=1))))
            # ---- (d)
            proj_p = PHp[:, :, ax].mean(1); proj_m = PHm[:, :, ax].mean(1)
            rec["d_spearman_axis_proj_271"] = spearman_boot(proj_p, proj_m)
            rec["d_spearman_axis_gap_270"] = spearman_boot(x_r, Pgm[:, :, ax].mean(1))
            # ---- (e)
            o_ = torch.argsort(a0)
            mk = lambda i: dict(id=pids[i + 1], name=names[pids[i + 1]], alpha=float(a0[i]), x=float(x_r[i]),  # noqa: E731
                                axis_rem1=float(rem_ax[0, i]), E1=float(E1[0, i]))
            rec["e_smallest_alpha"] = [mk(int(i)) for i in o_[:10]]
            rec["e_largest_alpha"] = [mk(int(i)) for i in reversed(o_[-10:])]
            # ---- (f)
            rec["f_turn1_vs_turn3"] = []
            for p in ["P01", "P02", "P05"]:
                c3 = p1.get((m, p, "off", bl))
                # turn-3 alpha restricted to the Part 2 scripts (extra)
                t3_same = None
                if os.path.exists(f"{ST}/part1_{m}_b{bl}.pt"):
                    gp3, _, _, _ = parts(S1("parent", bl), p, "off", sids2)
                    gm3, _, _, _ = parts(S1(m, bl), p, "off", sids2)
                    o3, _ = cell(WT2, gm3, gp3)
                    t3_same = summ(o3["alpha"])
                rec["f_turn1_vs_turn3"].append(dict(persona_id=p, alpha_turn1=summ(alpha[:, pids.index(p) - 1]),
                                                    alpha_turn3=(c3["alpha"] if c3 else None), alpha_turn3_same20=t3_same))
            summary.append(rec)
            log(event="part2_model_block", model=m, block=bl, alpha_median=rec["a_alpha"]["median"],
                spearman_alpha_x=rec["b_spearman_alpha_x"])
            for i in range(nP - 1):
                pr = dict(model=m, block=bl, persona_id=pids[i + 1], persona=names[pids[i + 1]],
                          alpha=summ(alpha[:, i]), rho=summ(rho[:, i]), E1=summ(E1[:, i]), x_parent_axis_gap=float(x_r[i]),
                          mean_norm_gp=float(npn[i].mean()), mean_norm_gm=float(nm2[i].sqrt().mean()))
                for k, dn in enumerate(DIRS):
                    pr[dn] = dict(parent_gap=float(mgp[0, i, k]), model_gap=float(mgm[0, i, k]), observed=float(obs[0, i, k]),
                                  pred1=float(pred1[0, i, k]), rem1=float(rem1[0, i, k]))
                pr["axis_rem1_ci"] = summ(rem1[:, i, ax])
                pr["mean_axis_proj_parent"] = float(proj_p[i + 1]); pr["mean_axis_proj_model"] = float(proj_m[i + 1])
                per_persona.append(pr)
            del Hm, gm, mp, nm2, ns2
        # default persona rows of (d) need P00's projections too: stored in summary via proj over 271
        if bl == 32:
            for m, v in mean_states.items():
                torch.save(v.to(torch.float16), f"{PUSH}/part2_mean_states_b32_{m}.pt")
            json.dump(dict(personas=[dict(id=p, name=names[p]) for p in pids], scripts=sids2,
                           note="rows = personas in this order; mean over the scripts of the last-prompt-token state, block 32"),
                      open(f"{PUSH}/part2_mean_states_index.json", "w"), indent=0)
    with open(f"{RES}/part2_summary.jsonl", "w") as f:
        for r in summary:
            f.write(json.dumps(r) + "\n")
    with open(f"{RES}/part2_per_persona.jsonl", "w") as f:
        for r in per_persona:
            f.write(json.dumps(r) + "\n")
    log(event="part2_done", n_summary=len(summary), n_per_persona=len(per_persona))


def step_push_states():
    import shutil
    for m in ["parent"] + TRAINED:
        src = f"{ST}/part1_{m}_b32.pt"
        if os.path.exists(src):
            shutil.copy(src, f"{PUSH}/part1_states_b32_{m}.pt")
    shutil.copy(f"{ST}/part1_index.json", f"{PUSH}/part1_index.json")
    log(event="push_states")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", default="kat,part1,repl,push_states")
    ap.add_argument("--blocks1", default="32,24,16,8")
    ap.add_argument("--blocks2", default="32,24")
    a = ap.parse_args()
    for st in a.steps.split(","):
        t1 = time.time()
        if st == "kat":
            step_kat()
        elif st == "part1":
            step_part1(tuple(int(x) for x in a.blocks1.split(",")))
        elif st == "repl":
            step_repl()
        elif st == "part2":
            step_part2(tuple(int(x) for x in a.blocks2.split(",")))
        elif st == "push_states":
            step_push_states()
        log(event="step_done", step=st, secs=round(time.time() - t1))
