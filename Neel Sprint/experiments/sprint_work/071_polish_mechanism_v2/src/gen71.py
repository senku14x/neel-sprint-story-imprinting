"""sw071 GPU stage (prep-71, E2, 31 Oct 2026; sw034 gen34.py adapted; DECISIONS D8-D12). HF + unmerged PEFT (one organism per
process and GPU), bf16, hooks71 on model.model.layers[L] (block output, pre-final-norm), edits at L16-63, prefill only.
Modes (--mode):
  cal  : prefill only (no generation, no outcome), sw038 D14's two-segment rule per (organism, direction, A arm): round 1 = one k at
         every layer on CAL_GRID -> k_band per band (median over every unit of the direction, s0); if k = mean of the two band k's puts
         both bands' interpolated medians within 1 +- 0.05, k1 = k2 = k; else round 2 = k1 = k_{L28-40} at L16-40 and a grid over k2 at
         L41-63, k2 = the interpolated k where L44-63's median is 1.0. Round 3 (verify) = the production rows (none, the arm, A0, A1, M)
         at the proposed scales on every unit; gate = every A clamp's median in [0.9, 1.1] at L28-40 AND L44-63.
         -> RUN/cal/cal_<m>.json, scales_proposal_<m>.json, logs.
  gen  : the swap job. Readouts (--readout, in order): fbtw / fo / co (forced, 2 samples) and free (1 sample, <= 2,048 tokens).
         Units: fbtw / free = REG + COND x ind / rem; fo / co = REG x ind / rem (rows none, asT_reg, asT_reg_A0, asT_reg_A1). Every
         arm of a unit in one forward (real rows before their A clamps). --part P = the parent floor (adapter disabled; organism m's
         edits, targets and positions; fbtw, induce, real arms, 1 sample; keys model 'parent@<m>').
Targets computed IN THE RECIPIENT: asT_* = the donor's asst_mean . u at every recipient turn-1-2 content token (sw029 D7); r1_reg =
the recipient's own capture of the donor context's 7 header tokens . u. A clamps: coordinate along r = x_none . r + s k_L Delta_arm
(live); M = the mean of the turn-1-2 content states set to ANOTHER script's recipient-condition asst_mean (sw034 M, D10(b)).
Inline gates (--gates; exit 3 + FAILED marker on failure, before any generation): G1 (vs sw034's capture, vs this organism's sw071
capture <= 0.10 and >= 3x further from the paired organism's sw071 capture), G3 (independent read-out at L16/40/63 for every row
kind + hook_checks on the live logs + untouched positions + identical opener tokens across a unit's rows) on 4 units.
  CUDA_VISIBLE_DEVICES=0 python gen71.py --model e08-N --mode gen --readout fbtw,fo,co,free [--npairs N] [--samples K] [--gates]
         [--run_dir D] [--calib P] [--batch_rows 50] [--forced_batch_rows 70] [--mem_probe 'co:70;free:50']"""
import argparse, json, os, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common71 as C  # noqa: E402
import engine71 as E  # noqa: E402
from hooks71 import Hooks71, Cap, check_order  # noqa: E402

RUN = "/root/runs/sw071"
CAPS = "/root/caps/sw071"
CAL_GRID = (0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0)
CAL_GRID2 = (0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0)
SINGLE_TOL = 0.05
TOKSUF = {}


# ------------------------------------------------------------------------------------------------- inputs
def load_inputs(m, dirs_root, caps_root):
    ctx = {c["key"]: c for c in map(json.loads, open(C.CTX_FILE))}
    P = C.load_pairs()
    Z = torch.load(f"{caps_root}/cap_{m}.pt", mmap=True, weights_only=False)
    return ctx, P, (Z, {k: i for i, k in enumerate(Z["keys"])}), torch.load(f"{dirs_root}/dirs71_{m}.pt", weights_only=False)


_DEVC = {}


def dev_dirs(dm, m, f):
    k = (m, f)
    if k not in _DEVC:
        un = lambda v: (v.float() / v.float().norm(dim=-1, keepdim=True)).to(E.DEV)
        _DEVC[k] = dict(U={x: un(v) for x, v in dm["U"][f].items()}, A={x: un(v) for x, v in dm["A"][f].items()})
    return _DEVC[k]


def unit_ops(part, readout, m, utype, d, sid, v, k, ctx, P, cap, dm, scales, cal_rows=None):
    """rows of one unit; positions are set per batch (set_pos). cal_rows = None (production arms) or [(row name, A arm, kvec)] for the
    calibration (rows none, the arm, then the named A rows)."""
    rc, dc = C.cells_of(m, utype, d)
    run_as = "parent" if part == "P" else m; mlab = f"parent@{m}" if part == "P" else m
    grp = C.unit_id(part, mlab, utype, d, sid, v, k, readout)
    Z, idx = cap; f = P["fold"][sid]; T = dev_dirs(dm, m, f); sg = dm["sign"][f"{utype}|{d}|{sid}|{v}"]
    kd = C.ctx_key(dc, sid, v); kr = C.ctx_key(rc, sid, v)
    Dh = torch.as_tensor(Z["hdr"][idx[kd]]).to(E.DEV).float(); Da = torch.as_tensor(Z["asst_mean"][idx[kd]]).to(E.DEV).float()
    osid, ov = P["other"][C.list_name(m, utype)][f"{sid}|{v}"]; ko = C.ctx_key(rc, osid, ov)
    na = len(ctx[kr]["apos"])
    base0 = dict(sample=k, grp=grp, model=mlab, run_as=run_as, org=m, part=part, utype=utype, direction=d, recipient=rc, donor=dc, sid=sid,
                 variant=v, log=(k == 0), fold=f, readout=readout)
    if cal_rows is None:
        rows = [(a, None, None) for a in C.arms_for(readout, utype, part)]
    else:
        arm = C.CONTROLLED[utype][0]
        rows = [("none", None, None), (arm, None, None)] + list(cal_rows)
    ops = []
    for name, a_arm, kv in rows:
        aname = a_arm or name; base, kind = C.arm_base(aname)
        b = dict(base0, arm=name, site=C.SITE.get(base), key=C.row_key(part, readout, mlab, utype, d, sid, v, name, k))
        if kind == "none":
            ops.append(dict(b, kind="none")); continue
        u = T["U"][C.FAMILY[base]]
        if kind == "real":
            tgt = torch.einsum("tlh,lh->lt", Dh, u) if b["site"] == "hdr" else (Da * u).sum(-1)[:, None].expand(64, na)
            ops.append(dict(b, kind="sub", U=u, tgt=tgt.contiguous(), real=True))
        elif kind == "A":
            kk = kv if kv is not None else C.kvec(C.scale_of(scales, m, aname, d))
            ops.append(dict(b, kind="A", U=T["A"][aname], s=float(sg[aname]), k=list(kk), match=f"{grp}:{base}"))
        else:   # M: mean clamp to another script's recipient-condition asst_mean (CPU until its batch)
            ops.append(dict(b, kind="mclamp", U=u, msc=torch.as_tensor(Z["asst_mean"][idx[ko]]), donor_other=ko))
    check_order(ops)
    return ops, ctx[kr]["ids"], ctx[kr]["apos"], dict(domain=P["fold"][sid], n_asst=na)


def set_pos(ops, Pn, n_ids, ns, apos0):
    off = Pn - n_ids - ns
    hpos = [off + n_ids - 7 + i for i in range(7)]; apos = [off + p for p in apos0]
    for op in ops:
        op["hpos"] = hpos
        if op["kind"] == "none":
            continue
        op["nh"] = 7 if op["site"] == "hdr" else 0
        op["pos"] = hpos if op["site"] == "hdr" else apos


def build_batch(units, suffix):
    rows, idr = [], []
    for ops, ids, apos0, _ in units:
        rows += ops; idr += [ids + suffix] * len(ops)
    inp, am, Pn = E.pad_rows(idr)
    for ops, ids, apos0, _ in units:
        set_pos(ops, Pn, len(ids), len(suffix), apos0)
    for r, op in enumerate(rows):
        assert inp[r, op["hpos"]].tolist() == C.HEADER, "header positions are not the header"
        if suffix:
            assert inp[r, Pn - len(suffix):].tolist() == suffix, "the bridge / opener tokens differ across rows"
    check_order(rows)
    for op in rows:
        if op["kind"] == "mclamp":
            op["mstar"] = op["msc"].to(E.DEV).float()
    return rows, inp, am, Pn


def release(rows):
    for op in rows:
        op.pop("mstar", None)


def generate_batch(model, hk, units, max_new, seed, suffix, min_new=None):
    rows, inp, am, Pn = build_batch(units, suffix)
    hk.ops = rows; hk.mode = "patch"; hk.min_len = Pn; hk.log = []; c0 = hk.calls
    try:
        out, tim = E.sample(model, inp, am, Pn, max_new, seed, min_new)
    finally:
        hk.mode = None; release(rows)
    tim["hook_calls"] = hk.calls - c0; tim["units"] = len(units)
    assert tim["hook_calls"] == 48, f"hook fired {tim['hook_calls']} times in one generate (expected 48: once per patched layer, prefill only)"
    return rows, out, hk.log, tim


def run_batch(model, hk, batch, max_new, m, suffix, readout):
    """sw012 F3: on CUDA OOM split the batch into halves (whole units, so every A stays in its arm's forward)."""
    try:
        return [(batch,) + generate_batch(model, hk, batch, max_new, E.seed_of(C.EXP, readout, m, batch[0][0][0]["grp"], max_new), suffix)]
    except torch.cuda.OutOfMemoryError:
        pass
    hk.mode = None; hk.log = []
    import gc
    gc.collect(); torch.cuda.empty_cache()
    if len(batch) == 1:
        raise RuntimeError(f"CUDA OOM on a single unit ({batch[0][0][0]['grp']})")
    h = len(batch) // 2
    print(f"[oom] {m} {readout}: batch of {len(batch)} units split into {h} + {len(batch) - h}", flush=True)
    return run_batch(model, hk, batch[:h], max_new, m, suffix, readout) + run_batch(model, hk, batch[h:], max_new, m, suffix, readout)


def pack(todo, cap_rows):
    out, cur, n = [], [], 0
    for u in todo:
        if cur and n + len(u[0]) > cap_rows:
            out.append(cur); cur, n = [], 0
        cur.append(u); n += len(u[0])
    if cur:
        out.append(cur)
    return out


def prefill(model, hk, units, log_all=True):
    rows, inp, am, Pn = build_batch(units, [])
    if log_all:
        for o in rows:
            o["log"] = True
    hk.ops = rows; hk.mode = "patch"; hk.min_len = Pn; hk.log = []; c0 = hk.calls
    try:
        with torch.no_grad():
            model(input_ids=inp.to(E.DEV), attention_mask=am.to(E.DEV), logits_to_keep=1)
    finally:
        hk.mode = None; release(rows)
    assert hk.calls - c0 == 48
    return rows, hk.log


# ------------------------------------------------------------------------------------------------- gates
def gates(model, hk, blocks, m, ctx, P, cap, dm, scales, out_dir, tol):
    Gs = {"tolerances": tol}
    Z, idx = cap
    G34 = E.g1_vs_sw034(model, blocks, [m], json.load(open(C.G1REF_FILE)))[m]
    sid0, v0 = P["REG"][0]; k0 = C.ctx_key("casual_helps", sid0, v0)
    with E.use(model, m):
        st = E.header_states(model, blocks, ctx[k0]["ids"])
    r_own = max(E.rel_med(st[L], torch.as_tensor(Z["hdr"][idx[k0]][:, L])) for L in (16, 40, 63))
    q = C.PAIRG1[m]; r_oth = None
    if os.path.exists(f"{CAPS}/cap_{q}.pt"):
        Zq = torch.load(f"{CAPS}/cap_{q}.pt", mmap=True, weights_only=False); iq = Zq["keys"].index(k0)
        r_oth = min(E.rel_med(st[L], torch.as_tensor(Zq["hdr"][iq][:, L])) for L in (40, 63))
    g1 = dict(vs_sw034=G34, key=k0, rel_own_max=r_own, rel_pair_min_L40_63=r_oth, pair=q,
              pass_=bool(G34["pass_"] and r_own <= E.G1_BAR and r_oth is not None and r_oth >= max(3 * r_own, 0.01)))
    cs = P[C.cond_pairs_key(m)][0]
    spec = (("fbtw", "REG", "ind", sid0, v0), ("fbtw", "REG", "rem", sid0, v0), ("fbtw", "COND", "ind", cs[0], cs[1]), ("fo", "REG", "ind", sid0, v0))
    res = {}
    for ro in ("fbtw", "fo"):
        units = [unit_ops("A", r_, m, u, d, s, v, 0, ctx, P, cap, dm, scales) for (r_, u, d, s, v) in spec if r_ == ro]
        suffix = TOKSUF[ro]
        rows, inp, am, Pn = build_batch(units, suffix)
        for o in rows:
            o["log"] = True
        ind = []
        for r in range(len(rows)):
            row = inp[r].tolist(); ns = len(suffix); assert row[Pn - ns - 7:Pn - ns] == C.HEADER and row[Pn - ns:] == suffix
            hp = list(range(Pn - ns - 7, Pn - ns)); ap = C.asst_positions(row, C.last_user_start(row)); ind.append(dict(hdr=hp, asst=ap))
            if rows[r]["kind"] != "none":
                assert rows[r]["pos"] == (hp if rows[r]["site"] == "hdr" else ap), f"positions of {rows[r]['arm']} differ from the independently derived ones"
        ck = Cap(blocks, (16, 40, 63)); ck.pos_rows = [ind[r]["hdr"] + ind[r]["asst"] for r in range(len(rows))]; ck.min_len = Pn
        with E.use(model, m):
            hk.ops = rows; hk.mode = "patch"; hk.min_len = Pn; hk.log = []; ck.on = True
            with torch.no_grad():
                model(input_ids=inp.to(E.DEV), attention_mask=am.to(E.DEV), logits_to_keep=1)
            hk.mode = None; ck.on = False
        ck.remove(); release(rows)
        om = {(o["grp"], o["arm"]): dict(kind=o["kind"], s=o.get("s"), k=o.get("k")) for o in rows}
        W = C.hook_checks(hk.log, om, tol)
        ib = dict(excess=-1e9, untouched_rel_max=0.0, n=dict(sub=0, A=0, mclamp=0), worst=None)
        byu = {}
        for r, o in enumerate(rows):
            byu.setdefault(o["grp"], {})[o["arm"]] = r
        for r, o in enumerate(rows):
            if o["kind"] == "none":
                continue
            g = byu[o["grp"]]; rn = g["none"]; na = len(ind[r]["asst"]); base, _ = C.arm_base(o["arm"])
            sel = list(range(7)) if o["site"] == "hdr" else list(range(7, 7 + na))
            f = P["fold"][o["sid"]]; U = dm["U"][f]; Aset = dm["A"][f]
            kd = C.ctx_key(o["donor"], o["sid"], o["variant"])
            osid, ov = P["other"][C.list_name(m, o["utype"])][f"{o['sid']}|{o['variant']}"]; ko = C.ctx_key(o["recipient"], osid, ov)
            for L in (16, 40, 63):
                X = ck.cap[L][r]; Xn = ck.cap[L][rn]
                if o["kind"] == "sub":
                    u = U[C.FAMILY[base]][L].float(); u = u / u.norm()
                    tg = torch.cat([Z["hdr"][idx[kd]][:, L].float() @ u, (Z["asst_mean"][idx[kd]][L].float() @ u).repeat(na)])[sel]
                    got = X[sel] @ u; gap = (tg - Xn[sel] @ u).abs()
                    exc = float(((got - tg).abs() - (tol["coord_rel"] * gap.clamp_min(1.0) + tol["coord_abs"])).max())
                elif o["kind"] == "A":
                    rv = Aset[o["arm"]][L].float(); rv = rv / rv.norm(); ra = g[base]
                    kL = C.kvec(C.scale_of(scales, m, o["arm"], o["direction"]))[L]
                    want = o["s"] * kL * (ck.cap[L][ra][sel] - Xn[sel]).norm(dim=-1); got = (X[sel] - Xn[sel]) @ rv
                    exc = float(((got - want).abs() - (tol["along_abs"] + tol["along_rel"] * want.abs())).max())
                else:
                    ms = Z["asst_mean"][idx[ko]][L].float()
                    exc = float((X[sel].mean(0) - ms).norm() / ms.norm()) - tol["mclamp_rel"]
                ib["n"][o["kind"]] += 1
                if exc > ib["excess"]:
                    ib["excess"] = exc; ib["worst"] = dict(arm=o["arm"], kind=o["kind"], L=L, excess=exc)
                if L == 16:
                    un = [j for j in range(7 + na) if j not in set(sel)]
                    ib["untouched_rel_max"] = max(ib["untouched_rel_max"], float(((X[un] - Xn[un]).norm(dim=-1) / Xn[un].norm(dim=-1)).max()))
        need = ("sub", "A", "mclamp") if ro == "fbtw" else ("sub", "A")
        ib["pass_"] = bool(ib["excess"] <= 0 and ib["untouched_rel_max"] <= 1e-3 and all(ib["n"][x] > 0 for x in need))
        cr = C.cum_ratios(hk.log)
        res[ro] = dict(logs=W, independent=ib, cum_ratios={a_: {b: C.median(v) for b, v in x.items()} for a_, x in cr.items()},
                       pass_=bool(W["pass"] and ib["pass_"] and all(W["n"][x] > 0 for x in need)))
    Gs[m] = dict(G1=g1, G3=res, pass_=bool(g1["pass_"] and all(x["pass_"] for x in res.values())))
    Gs["pass"] = Gs[m]["pass_"]
    os.makedirs(out_dir, exist_ok=True); json.dump(Gs, open(f"{out_dir}/gates_{m}.json", "w"), indent=1, default=float)
    print("GATES", json.dumps(Gs, default=float)[:3000], flush=True)
    return Gs


# ------------------------------------------------------------------------------------------------- calibration (prefill only)
def interp(curve, target):
    for (c0, r0), (c1, r1) in zip(curve, curve[1:]):
        if (r0 - target) * (r1 - target) <= 0 and r1 != r0:
            return c0 + (target - r0) * (c1 - c0) / (r1 - r0), False
    (c0, r0), (c1, r1) = (curve[0], curve[1]) if target < curve[0][1] else (curve[-2], curve[-1])
    return c0 + (target - r0) * (c1 - c0) / (r1 - r0), True


def at(curve, k):
    for (c0, r0), (c1, r1) in zip(curve, curve[1:]):
        if c0 <= k <= c1:
            return r0 + (k - c0) * (r1 - r0) / (c1 - c0)
    (c0, r0), (c1, r1) = (curve[0], curve[1]) if k < curve[0][0] else (curve[-2], curve[-1])
    return r0 + (k - c0) * (r1 - r0) / (c1 - c0)


def name_of(a):
    return a.split("~")[0]


def cal_pass(model, hk, m, utype, d, ctx, P, cap, dm, rows_spec, cap_rows, npairs):
    U = [unit_ops("A", "cal", m, u, dd, s, v, 0, ctx, P, cap, dm, None, cal_rows=rows_spec)
         for (u, dd, s, v) in C.unit_list(P, m, utypes=(utype,), dirs=(d,), npairs=npairs)]
    logs = []
    with E.use(model, m):
        for B in pack(U, cap_rows):
            _, lg = prefill(model, hk, B); logs += lg
    return logs, C.cum_ratios(logs, name_of)


def run_cal(model, hk, m, ctx, P, cap, dm, run_dir, cap_rows, npairs=None):
    rd = f"{run_dir}/cal"; os.makedirs(rd, exist_ok=True); t0 = time.time()
    res = dict(model=m, grid=list(CAL_GRID), grid2=list(CAL_GRID2), single_tol=SINGLE_TOL, arms={}); prop = {}
    for utype, arm in (("REG", "asT_reg"), ("COND", "asT_cond")):
        A_ARMS = [f"{arm}_A{i}" for i in range(C.N_A)]
        for d in C.DIRS:
            R = dict(round1={}, choice={}, round2={}, verify={})
            spec = [(f"{a}~k{c:g}", a, [c] * 64) for a in A_ARMS for c in CAL_GRID]
            logs, per = cal_pass(model, hk, m, utype, d, ctx, P, cap, dm, spec, cap_rows, npairs)
            open(f"{rd}/log_cal_{m}_{arm}_{d}_r1.jsonl", "w").write("".join(json.dumps(e) + "\n" for e in logs))
            need2 = []
            for a in A_ARMS:
                cv = {b: [(c, C.median(per[f"{a}~k{c:g}"][b])) for c in CAL_GRID] for b in C.GATE_BANDS}
                R["round1"][a] = {b: [[c, round(r, 4)] for c, r in v] for b, v in cv.items()}
                kb = {b: interp(cv[b], 1.0) for b in C.GATE_BANDS}
                ks = 0.5 * (kb["L28-40"][0] + kb["L44-63"][0]); rs = {b: at(cv[b], ks) for b in C.GATE_BANDS}
                single = all(abs(x - 1.0) <= SINGLE_TOL for x in rs.values())
                R["choice"][a] = dict(k_band={b: round(x[0], 4) for b, x in kb.items()}, extrapolated={b: x[1] for b, x in kb.items()},
                                      single_k=round(ks, 4), single_pred={b: round(x, 4) for b, x in rs.items()}, single=bool(single))
                if single:
                    prop.setdefault(a, {})[d] = dict(k1=round(ks, 4), k2=round(ks, 4), two_segment=False)
                else:
                    need2.append((a, kb["L28-40"][0]))
            if need2:
                spec = [(f"{a}~k1{k1:.4f}~k2{c:g}", a, [k1 if L < C.SEG_SPLIT else c for L in range(64)]) for a, k1 in need2 for c in CAL_GRID2]
                logs, per = cal_pass(model, hk, m, utype, d, ctx, P, cap, dm, spec, cap_rows, npairs)
                open(f"{rd}/log_cal_{m}_{arm}_{d}_r2.jsonl", "w").write("".join(json.dumps(e) + "\n" for e in logs))
                for a, k1 in need2:
                    cv = {b: [(c, C.median(per[f"{a}~k1{k1:.4f}~k2{c:g}"][b])) for c in CAL_GRID2] for b in C.GATE_BANDS}
                    k2, ex = interp(cv["L44-63"], 1.0)
                    R["round2"][a] = dict(k1=round(k1, 4), curve={b: [[c, round(r, 4)] for c, r in v] for b, v in cv.items()}, k2=round(k2, 4),
                                          extrapolated=ex, L28_40_spread_over_k2=round(max(r for _, r in cv["L28-40"]) - min(r for _, r in cv["L28-40"]), 5))
                    prop.setdefault(a, {})[d] = dict(k1=round(k1, 4), k2=round(k2, 4), two_segment=True)
            # round 3: verify with the production rows (none, arm, A0, A1, M) at the proposed scales
            sc = {m: {a: {d: prop[a][d]} for a in A_ARMS}}
            V = [unit_ops("A", "calv", m, u, dd, s, v, 0, ctx, P, cap, dm, sc) for (u, dd, s, v) in C.unit_list(P, m, utypes=(utype,), dirs=(d,), npairs=npairs)]
            vl = []
            with E.use(model, m):
                for B in pack(V, cap_rows):
                    _, lg = prefill(model, hk, B); vl += lg
            open(f"{rd}/log_cal_{m}_{arm}_{d}_verify.jsonl", "w").write("".join(json.dumps(e) + "\n" for e in vl))
            g = C.cum_gate(C.cum_ratios(vl)); R["verify"] = g
            print(f"[cal] {m} {arm} {d} {time.time() - t0:.0f}s choice {json.dumps(R['choice'])} r2 {json.dumps({a: (x['k1'], x['k2']) for a, x in R['round2'].items()})} "
                  f"verify {json.dumps({a_: x['median_ratio'] for a_, x in g['arms'].items()})} pass {g['pass_']}", flush=True)
            res["arms"][f"{arm}|{d}"] = R
    res["proposal"] = prop
    res["pass"] = bool(all(R["verify"]["pass_"] for R in res["arms"].values()))
    json.dump(res, open(f"{rd}/cal_{m}.json", "w"), indent=1, default=float)
    json.dump(dict(model=m, scales=prop, verify_pass=res["pass"], created=time.strftime("%FT%TZ", time.gmtime())), open(f"{rd}/scales_proposal_{m}.json", "w"), indent=1)
    print("CAL_DONE", m, "verify pass", res["pass"], f"{time.time() - t0:.0f}s", flush=True)
    return res


# ------------------------------------------------------------------------------------------------- memory probe
def mem_probe(model, hk, m, ctx, P, cap, dm, scales, spec, out_dir):
    """spec 'co:70;free:50' -> one batch of that many rows (whole units) from the LONGEST recipient contexts (fbtw / free: REG + COND
    units with every arm; fo / co: REG opener units), generated with min_new_tokens = max_new (every row runs to the cap). Outputs
    discarded; peak memory_reserved recorded."""
    res = []
    import gc
    for part in spec.split(";"):
        ro, ns = part.split(":")
        ut = C.READOUT_UTYPES[ro]
        order = sorted(C.unit_list(P, m, utypes=ut), key=lambda x: -len(ctx[C.ctx_key(C.cells_of(m, x[0], x[1])[0], x[2], x[3])]["ids"]))
        for n in [int(x) for x in ns.split(",")]:
            suffix = TOKSUF.get(ro, []); max_new = C.FORCED_TOKENS if ro in C.BRIDGES else 2048
            units, tot = [], 0
            for (u, d, s, v) in order:
                us = unit_ops("A", ro, m, u, d, s, v, 0, ctx, P, cap, dm, scales)
                if tot + len(us[0]) > n:
                    break
                units.append(us); tot += len(us[0])
            for us in units:
                for o in us[0]:
                    o["log"] = False
            gc.collect(); torch.cuda.empty_cache()
            try:
                with E.use(model, m):
                    _, out, _, tim = generate_batch(model, hk, units, max_new, 1, suffix, min_new=max_new)
                res.append(dict(tim, readout=ro, oom=False))
            except torch.cuda.OutOfMemoryError:
                hk.mode = None; res.append(dict(readout=ro, rows=tot, oom=True)); gc.collect(); torch.cuda.empty_cache()
            print("[mem_probe]", json.dumps(res[-1]), flush=True)
            json.dump(dict(model=m, total_gib=round(torch.cuda.get_device_properties(0).total_memory / 2 ** 30, 2), probes=res),
                      open(f"{out_dir}/mem_probe_{m}.json", "w"), indent=1)
    return res


# ------------------------------------------------------------------------------------------------- generation (resume by key)
def _claim(cdir, grp, tag):
    """atomic unit claim (D11): os.mkdir succeeds for exactly one process."""
    import hashlib
    p = f"{cdir}/{hashlib.md5(grp.encode()).hexdigest()}"
    try:
        os.mkdir(p)
    except FileExistsError:
        return False
    open(f"{p}/owner", "w").write(f"{tag}\n{grp}\n")
    return True


def run_gen(model, hk, tok, part, m, readout, ctx, P, cap, dm, scales, run_dir, samples, max_new, cap_rows, npairs=None, claim=False, tag="", reverse=False):
    bridge = C.BRIDGES.get(readout); suffix = TOKSUF[readout] if bridge else []
    mlab = f"parent@{m}" if part == "P" else m
    sfx = f".{tag}" if tag else ""
    fn, lfn = f"{run_dir}/{readout}_{mlab}{sfx}.jsonl", f"{run_dir}/log_{readout}_{mlab}{sfx}.jsonl"
    E.repair_tail(fn); E.repair_tail(lfn)
    have = {r["key"] for r in C.jl_all(run_dir, readout, mlab)}
    cdir = f"{run_dir}/claims_{readout}_{mlab}"
    if claim:
        os.makedirs(cdir, exist_ok=True)
    dirs_ = ("ind",) if part == "P" else C.DIRS
    ut = ("REG", "COND") if part == "P" else C.READOUT_UTYPES[readout]
    todo = []
    for (u, d, s, v) in C.unit_list(P, m, utypes=ut, dirs=dirs_, npairs=npairs):
        for k in range(samples):
            ops, ids, apos, meta = unit_ops(part, readout, m, u, d, s, v, k, ctx, P, cap, dm, scales)
            if all(o["key"] in have for o in ops):
                continue
            todo.append((ops, ids, apos, meta))
    todo.sort(key=lambda x: (len(x[1]), x[0][0]["grp"]), reverse=reverse)
    if claim:   # resume: release my own claims of units still in todo (their rows never landed), keep everyone else's
        me = tag or "own"; tg = {u[0][0]["grp"] for u in todo}
        import hashlib, shutil
        for u in todo:
            p_ = f"{cdir}/{hashlib.md5(u[0][0]['grp'].encode()).hexdigest()}"
            if os.path.exists(f"{p_}/owner") and open(f"{p_}/owner").read().split("\n")[0] == me:
                shutil.rmtree(p_)
        batches = None
    else:
        batches = pack(todo, cap_rows)
    print(mlab, readout, "units todo", len(todo), "rows", sum(len(x[0]) for x in todo), "batches", len(batches) if batches else "claim-mode", flush=True)

    def claimed_batches():
        cur, n = [], 0
        for u in todo:
            if not _claim(cdir, u[0][0]["grp"], tag or "own"):
                continue
            if cur and n + len(u[0]) > cap_rows:
                yield cur; cur, n = [], 0
            cur.append(u); n += len(u[0])
        if cur:
            yield cur
    with E.use(model, "parent" if part == "P" else m):
        for bi, Bt in enumerate(batches if batches is not None else claimed_batches()):
            for batch, rows, out, logs, tim in run_batch(model, hk, Bt, max_new, mlab, suffix, readout):
                res = {op["key"]: o for op, o in zip(rows, out)}
                assert len(res) == len(rows), "duplicate keys inside one batch"
                lines = []
                for ops, ids, apos0, meta in batch:
                    for op in ops:
                        if op["key"] in have:
                            continue
                        gen, n, fin = res[op["key"]]; have.add(op["key"])
                        lines.append(json.dumps(dict(key=op["key"], exp=C.EXP, part=part, readout=readout, model=mlab, org=m, utype=op["utype"],
                                                     direction=op["direction"], recipient=op["recipient"], donor=op["donor"], sid=op["sid"],
                                                     variant=op["variant"], arm=op["arm"], kind=op["kind"], sample=op["sample"], fold=op["fold"],
                                                     text=(bridge or "") + tok.decode(gen, skip_special_tokens=True), n_tok=n, finish=fin,
                                                     max_new=max_new, gen_head=gen[:16], donor_other=op.get("donor_other"), **meta)) + "\n")
                with open(lfn, "a") as f:
                    f.write("".join(json.dumps(dict(e, readout=readout)) + "\n" for e in logs))
                with open(fn, "a") as f:
                    f.write("".join(lines))
                with open(f"{run_dir}/timing.jsonl", "a") as f:
                    f.write(json.dumps(dict(tim, model=mlab, readout=readout, units_in=[x[0][0]["grp"] for x in batch], t=time.strftime("%FT%T"))) + "\n")
                print(f"[gen] {mlab} {readout}{sfx} batch {bi + 1}/{len(batches) if batches else '?'} {json.dumps(tim)} cap_hits {sum(o[2] == 'length' for o in out)}/{len(out)} {time.strftime('%H:%M:%S')}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True); ap.add_argument("--mode", default="gen", choices=("gen", "cal")); ap.add_argument("--part", default="A", choices=("A", "P"))
    ap.add_argument("--readout", default="fbtw,fo,co,free"); ap.add_argument("--npairs", type=int, default=None); ap.add_argument("--samples", type=int, default=0)
    ap.add_argument("--max_new", type=int, default=2048); ap.add_argument("--batch_rows", type=int, default=50); ap.add_argument("--forced_batch_rows", type=int, default=70)
    ap.add_argument("--cal_rows", type=int, default=72); ap.add_argument("--gates", action="store_true"); ap.add_argument("--run_dir", default=f"{RUN}/full")
    ap.add_argument("--calib", default=None); ap.add_argument("--dirs_root", default=RUN); ap.add_argument("--caps_root", default=CAPS)
    ap.add_argument("--scales", default=C.SCALES_FILE); ap.add_argument("--mem_probe", default=None)
    ap.add_argument("--claim", default="", help="comma list of readouts run in claim mode (D11: shared with a helper process)")
    ap.add_argument("--tag", default="", help="helper tag: rows go to <ro>_<m>.<tag>.jsonl"); ap.add_argument("--reverse", action="store_true")
    a = ap.parse_args(); m = a.model
    os.makedirs(a.run_dir, exist_ok=True)
    E.manifest(f"{a.run_dir}/manifest_{a.mode}_{a.part}_{m}.json", dict(job="gen71", mode=a.mode, part=a.part, model=m, readout=a.readout))
    scales = json.load(open(a.scales))["scales"] if a.mode == "gen" else None
    model, tok, blocks = E.load_model([m], C.LORA)
    for ro, b in C.BRIDGES.items():
        TOKSUF[ro] = tok(b, add_special_tokens=False)["input_ids"]
    hk = Hooks71(blocks); tol = C.tolerances(a.calib)
    ctx, P, cap, dm = load_inputs(m, a.dirs_root, a.caps_root)
    if a.mode == "cal":
        run_cal(model, hk, m, ctx, P, cap, dm, a.run_dir, a.cal_rows, a.npairs)
        print("CAL71_EXIT", flush=True); return
    if a.gates:
        Gs = gates(model, hk, blocks, m, ctx, P, cap, dm, scales, a.run_dir, tol)
        if not Gs["pass"]:
            open(f"{a.run_dir}/FAILED_gates_{m}", "w").write("inline gates\n"); print("GATES_FAILED", flush=True); sys.exit(3)
    if a.mem_probe:
        mem_probe(model, hk, m, ctx, P, cap, dm, scales, a.mem_probe, a.run_dir)
    for ro in a.readout.split(","):
        rd = f"{a.run_dir}/{ro}"; os.makedirs(rd, exist_ok=True)
        ns = a.samples or (1 if a.part == "P" else C.SAMPLES[ro])
        run_gen(model, hk, tok, a.part, m, ro, ctx, P, cap, dm, scales, rd, ns, C.FORCED_TOKENS if ro in C.BRIDGES else a.max_new,
                a.forced_batch_rows if ro in C.BRIDGES else a.batch_rows, a.npairs, claim=ro in a.claim.split(","), tag=a.tag, reverse=a.reverse)
        print(f"READOUT_DONE {ro} {time.strftime('%H:%M:%S')}", flush=True)
    print("GEN71_EXIT", flush=True)


if __name__ == "__main__":
    main()
