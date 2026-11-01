"""E09 R04 Stage 4c analysis (Part 1 only): R02's code/e09r02_states_analysis.py (itself R01's) with this run's
per-row states for parent, Ssarc, Rsarc, RSsarc (personas P00, P06, P01, P02, P05; R05's r05_lib copied unchanged
into code/); movement ratio to Ssarc (and to Rsarc). Part 2 is not run (brief). Replication: this run's parent states
vs R01's saved parent states on the shared personas (P00, P01, P02, P05; same inputs, matched by key).

python e09r04_states_analysis.py --steps part1,move1,repl,push
"""
import argparse, json, os, sys, time

import numpy as np
import torch

sys.path.insert(0, "/workspace/e09/r04/code")  # copy of /workspace/e05/r05/driver/r05_lib.py (same sha256)
from r05_lib import DIRS, boot_weights, cell, null_stats, remainder_vectors, spearman_boot, summ  # noqa: E402  (read only)

torch.set_grad_enabled(False)
W = "/workspace/e09/r04"
R01 = "/workspace/e09/r01"
ST = f"{W}/states"     # this run's states (parent, Ssarc, Rsarc, RSsarc)
STR01 = f"{R01}/states"  # R01's saved parent states (replication on the shared personas)
RES = f"{W}/results/states"
PUSH = f"{W}/push_states"
R04 = "/workspace/e05/r04"
R05P = "/workspace/e05/r05/push_states"
AX = "/workspace/si36/axis_pv"
P1_PIDS = ["P06", "P01", "P02", "P05"]
ALL_P1 = ["P00"] + P1_PIDS
PNAME = {"P00": "default", "P06": "sarcastic", "P01": "dismissive", "P02": "sam", "P03": "alex", "P04": "drew", "P05": "terse"}
MODELS_T = ["Ssarc", "Rsarc", "RSsarc", "Ssarc2"]
os.makedirs(RES, exist_ok=True); os.makedirs(PUSH, exist_ok=True)
LOGF = open(f"{W}/logs/states_analysis_events.jsonl", "a")


def log(**kw):
    kw["t"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    LOGF.write(json.dumps(kw, default=str) + "\n"); LOGF.flush()
    print(json.dumps(kw, default=str)[:1500], flush=True)


def sdir(m):
    return ST


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
    return [m for m in MODELS_T if have(part, m)]


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
                    for i, sid in enumerate(SIDS):
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
        for m in ["parent"] + TR:  # E09 R04: per-row projections for every model of this run
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
                                   ratio_to_Ssarc=(summ(Mb[m] / Mb["Ssarc"]) if "Ssarc" in Mb else None),
                                   ratio_to_Rsarc=(summ(Mb[m] / Mb["Rsarc"]) if "Rsarc" in Mb else None),
                                   ratio_to_Ssarc2=(summ(Mb[m] / Mb["Ssarc2"]) if "Ssarc2" in Mb else None),
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


# ---------------- E09 R04: this run's parent Part 1 states vs R01's (shared personas, matched by key) ----------------
def step_repl():
    out = {}
    i1 = json.load(open(f"{STR01}/part1_index.json"))
    pos1 = {it["key"]: i for i, it in enumerate(i1)}
    shared = [it["key"] for it in IDX1 if it["key"] in pos1]
    out["n_shared_rows"] = len(shared)
    out["shared_rows_same_n_tokens"] = sum(IDX1[POS1[k]]["n_tokens"] == i1[pos1[k]]["n_tokens"] for k in shared)
    for bl in (32, 24):
        A = S1("parent", bl)[[POS1[k] for k in shared]]
        B = torch.load(f"{STR01}/part1_parent_b{bl}.pt").double()[[pos1[k] for k in shared]]
        pa, pb_ = A @ U[bl].T, B @ U[bl].T
        out[f"block{bl}"] = dict(largest_abs_per_row_proj_diff=float((pa - pb_).abs().max()),
                                 state_rel_diff=float((A - B).norm() / B.norm()))
    json.dump(out, open(f"{RES}/replication_parent_vs_R01.json", "w"), indent=1)
    log(event="repl", **out)


def step_push():
    import shutil
    for m in ["parent"] + trained(1):
        src = f"{ST}/part1_{m}_b32.pt"
        if os.path.exists(src):
            shutil.copy(src, f"{PUSH}/part1_states_b32_{m}.pt")
    shutil.copy(f"{ST}/part1_index.json", f"{PUSH}/part1_index.json")
    log(event="push_states")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", default="part1,move1,repl,push")
    a = ap.parse_args()
    for st in a.steps.split(","):
        t1 = time.time()
        {"part1": step_part1, "move1": step_move1, "repl": step_repl, "push": step_push}[st]()
        log(event="step_done", step=st, secs=round(time.time() - t1))
