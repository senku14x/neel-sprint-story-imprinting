"""Addendum A, A2: R05's saved states projected on the parent's 8 trait directions and V (blocks 24, 32).

Part 1: turn 3, with_sys, both triggers, P01/P02/P05; R05's cell() (same history resamples: 2,000, seed 0).
Part 2: turn 1; (a) persona-gap cosines with the 265 roles; (b) role valence quartiles; (c) positive-minus-negative
role cosine for P01, P04, P02 vs parent (role bootstrap 2,000, seed 0, stratified by quartile); (d) nearest roles.
"""
import json, re, time

import torch

import numpy as np

from a_common import D04, RES, TRAINED, ci, jdump, parent_dirs
from r05_lib import boot_weights, cell, summ

W = "/workspace/e05/r05"
ST = f"{W}/states"
KEYWORDS = ["assistant", "helper", "servant", "butler", "concierge", "customer", "cynic", "grump", "misanthrop", "troll", "rude"]
KRX = re.compile(r"\b(" + "|".join(KEYWORDS) + r")", re.I)
t0 = time.time()
IDX1 = json.load(open(f"{ST}/part1_index.json"))
POS1 = {it["key"]: i for i, it in enumerate(IDX1)}
SIDS = sorted({it["sid"] for it in IDX1})
WT1 = boot_weights(len(SIDS))


def rows1(pid, inp, trig):
    return [POS1[f"{pid}|{inp}|{trig}|{s}"] for s in SIDS]


def parts(H, pid, trig):
    w, n0, ns = H[rows1(pid, "with_sys", trig)], H[rows1("P00", "with_sys", trig)], H[rows1(pid, "no_sys", trig)]
    return w - n0, w - ns, ns - n0


out1 = []
dirs_meta = {}
for bl in (32, 24):
    names, U, raw = parent_dirs(bl)
    dirs_meta[bl] = dict(names=names, norms={t: float(raw[t].norm()) for t in raw},
                         cos={a: {b: float(U[i] @ U[j]) for j, b in enumerate(names)} for i, a in enumerate(names)},
                         cos_with_r04={k: {n: float(U[i] @ D04["unit"][bl][k].double()) for i, n in enumerate(names)}
                                       for k in ["v_axis", "v_axis_ns", "v_dis", "v_help"]})
    Hp = torch.load(f"{ST}/part1_parent_b{bl}.pt").double()
    for m in TRAINED:
        Hm = torch.load(f"{ST}/part1_{m}_b{bl}.pt").double()
        for trig in ["on", "off"]:
            for pid in ["P01", "P02", "P05"]:
                gp, sp, ep = parts(Hp, pid, trig)
                gm, sm, em = parts(Hm, pid, trig)
                o, _ = cell(WT1, gm, gp, sp, ep, sm, em, None, U)
                share = 1 - o["M6_gm"] / o["M6_gp"]
                rec = dict(model=m, block=bl, trigger=trig, persona_id=pid, alpha_1c=summ(o["alpha"]), alpha_sig=summ(o["alpha_sig"]),
                           alpha_eta=summ(o["alpha_eta"]))
                for k in ["M6_gp", "M6_gm", "M6_observed", "M6_pred1", "M6_rem1", "M6_pred2", "M6_rem2"]:
                    rec[k] = dict(zip(names, summ(o[k])))
                rec["share_closed"] = dict(zip(names, summ(share)))
                out1.append(rec)
with open(f"{RES}/a2_part1.jsonl", "w") as f:
    for r in out1:
        f.write(json.dumps(r) + "\n")
jdump(dirs_meta, f"{RES}/a2_directions.json")
print("A2 part1 done", len(out1), round(time.time() - t0), flush=True)

# ---------------- Part 2 ----------------
idx2 = json.load(open(f"{ST}/part2_index.json"))
pids, sids2 = [], []
for it in idx2:
    if not pids or pids[-1] != it["pid"]:
        pids.append(it["pid"])
    if it["sid"] not in sids2:
        sids2.append(it["sid"])
names2 = {it["pid"]: it["persona"] for it in idx2}
pos2 = {(it["pid"], it["sid"]): i for i, it in enumerate(idx2)}
order = torch.tensor([pos2[(p, s)] for p in pids for s in sids2])
nP, nS = len(pids), len(sids2)
checks = json.load(open(f"{W}/logs/input_checks.json"))
prompts = {p["id"]: p["system"] for p in checks["part2_personas"]}
role_ids = [p for p in pids if p.startswith("role:")]
role_i = [pids.index(p) for p in role_ids]
excluded = []
for p in role_ids:
    nm, pr = names2[p], prompts[p] or ""
    hit = KRX.findall(nm) + KRX.findall(pr)
    if hit:
        excluded.append(dict(id=p, name=nm, matched=sorted({h.lower() for h in hit}), prompt=pr))
excl_set = {e["id"] for e in excluded}
summary, per_role, nearest = [], [], []
for bl in (32, 24):
    names, U, raw = parent_dirs(bl)
    Vi = names.index("V")
    G = {}
    for m in ["parent"] + TRAINED:
        H = torch.load(f"{ST}/part2_{m}_b{bl}.pt").double()[order].view(nP, nS, -1)
        G[m] = (H - H[:1]).mean(1)  # mean gap from P00 per persona [271, D] (row 0 = 0)
    # (b) role valence from the parent
    val = G["parent"][role_i] @ U[Vi]
    q25, q75 = torch.quantile(val, 0.25), torch.quantile(val, 0.75)
    pos_all = [role_ids[k] for k in range(len(role_ids)) if val[k] >= q75]
    neg_all = [role_ids[k] for k in range(len(role_ids)) if val[k] <= q25]
    pos_r = [p for p in pos_all if p not in excl_set]
    neg_r = [p for p in neg_all if p not in excl_set]
    labels = dict(block=bl, q25=float(q25), q75=float(q75), n_pos_before_exclusion=len(pos_all), n_neg_before_exclusion=len(neg_all),
                  n_pos=len(pos_r), n_neg=len(neg_r), excluded_from_pos=[p for p in pos_all if p in excl_set],
                  excluded_from_neg=[p for p in neg_all if p in excl_set],
                  pos=[names2[p] for p in pos_r], neg=[names2[p] for p in neg_r])
    ip = torch.tensor([pids.index(p) for p in pos_r]); ineg = torch.tensor([pids.index(p) for p in neg_r])
    rng = np.random.default_rng(0)  # one generator: positive-role resamples, then negative-role resamples
    bp = torch.from_numpy(rng.integers(0, len(pos_r), size=(2000, len(pos_r))))
    bn = torch.from_numpy(rng.integers(0, len(neg_r), size=(2000, len(neg_r))))
    ri = torch.tensor(role_i)

    def cosv(Gm, pid):
        a = Gm[pids.index(pid)]
        R = Gm[ri]
        return (R @ a) / (R.norm(dim=1) * a.norm())  # [265]
    rec_b = dict(block=bl, labels=labels, a={}, c={}, d={})
    for pid in ["P01", "P04", "P02"]:
        cp = cosv(G["parent"], pid)
        cpos_p = cp[[role_ids.index(p) for p in pos_r]]; cneg_p = cp[[role_ids.index(p) for p in neg_r]]
        Dp = torch.cat([(cpos_p.mean() - cneg_p.mean())[None], cpos_p[bp].mean(1) - cneg_p[bn].mean(1)])
        for m in TRAINED:
            cm = cosv(G[m], pid)
            if pid in ("P01", "P04"):
                dlt = cm - cp
                rec_b["a"][f"{m}|{pid}"] = dict(mean_cos_parent=float(cp.mean()), mean_cos_model=float(cm.mean()), mean_delta=float(dlt.mean()),
                                                mean_abs_delta=float(dlt.abs().mean()), max_abs_delta=float(dlt.abs().max()),
                                                pearson_parent_model=float(torch.corrcoef(torch.stack([cp, cm]))[0, 1]),
                                                largest_increase=[(names2[role_ids[int(k)]], float(dlt[k])) for k in torch.argsort(dlt, descending=True)[:5]],
                                                largest_decrease=[(names2[role_ids[int(k)]], float(dlt[k])) for k in torch.argsort(dlt)[:5]])
                for k, p in enumerate(role_ids):
                    per_role.append(dict(block=bl, model=m, persona_id=pid, role=names2[p], cos_parent=float(cp[k]), cos_model=float(cm[k]),
                                         parent_V_proj=float(val[k]), label=("pos" if p in pos_r else "neg" if p in neg_r else "excluded" if p in excl_set and (p in pos_all or p in neg_all) else "")))
            cpos = cm[[role_ids.index(p) for p in pos_r]]; cneg = cm[[role_ids.index(p) for p in neg_r]]
            Dm = torch.cat([(cpos.mean() - cneg.mean())[None], cpos[bp].mean(1) - cneg[bn].mean(1)])
            rec_b["c"][f"{m}|{pid}"] = dict(parent=ci(Dp), model=ci(Dm), model_minus_parent=ci(Dm - Dp),
                                            mean_cos_pos_parent=float(cpos_p.mean()), mean_cos_neg_parent=float(cneg_p.mean()),
                                            mean_cos_pos_model=float(cpos.mean()), mean_cos_neg_model=float(cneg.mean()))
    for m in ["parent"] + TRAINED:
        c = cosv(G[m], "P01")
        o_ = torch.argsort(c, descending=True)[:10]
        rec_b["d"][m] = [(names2[role_ids[int(k)]], float(c[k])) for k in o_]
    # also P04's nearest roles (extra)
    rec_b["d_P04"] = {m: [(names2[role_ids[int(k)]], float(cosv(G[m], "P04")[k])) for k in torch.argsort(cosv(G[m], "P04"), descending=True)[:10]]
                      for m in ["parent"] + TRAINED}
    summary.append(rec_b)
    print("A2 part2 block", bl, round(time.time() - t0), flush=True)
jdump(dict(keywords=KEYWORDS, rule="case-insensitive, keyword at a word start, in the role name or its prompt", excluded=excluded,
           blocks=summary), f"{RES}/a2_part2.json")
with open(f"{RES}/a2_part2_per_role.jsonl", "w") as f:
    for r in per_role:
        f.write(json.dumps(r) + "\n")
print("A2 done", round(time.time() - t0))
