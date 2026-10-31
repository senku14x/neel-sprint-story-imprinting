"""sw034 GPU stage (prep agent, E2, 31 Oct 2026; DECISIONS D8-D12). HF + unmerged PEFT (the organisms given by --models, one process
per GPU), bf16, hooks34 on model.model.layers[L] (block output, pre-final-norm), edits at L16-63, prefill only (decode unpatched).
Modes (--mode):
  cal  : prefill only, every induce unit (s0): none, each controlled arm, and its 2 A directions at every scale of CAL_GRID -> the
         'gate' ratio curve (sw031 definition) per (organism, arm) and the interpolated c for 1.0x at L44-63; then a verification
         prefill at those c on induce AND remove units (cum_gate per arm, L44-63 decides, L28-40 reported) -> RUN/cal/calibration_<m>.json.
  gen  : the swap job. Units (common34.unit_list): REG / COND x ind / rem x pairs x samples, every arm of the unit type in one forward
         (real rows before their A clamps). Readouts --readout fbtw,free[,fraf]; samples common34.SAMPLES (--samples overrides).
  Part P (--part P, the parent floor): the parent (adapter off) with organism m's edits (same u, same target coordinates, same
         positions), induce units, real arms only, fbtw, 1 sample; keys model 'parent@<m>'.
Targets computed IN THE RECIPIENT: header arms = the recipient organism's own capture of the donor context . u per token; Assistant
arms = the donor's asst_mean . u at every recipient turn-1-2 content token (sw029 D7). A clamps: dirs34 nulls, coordinate along r set
to x_none . r + s * c * Delta (live), c = scales34.json[m][arm]. M rows: noP_reg_M = the whole header state of the recipient
organism's capture of ANOTHER script's same-condition context (sw031 skF); asT_*_M = the mean of the turn-1-2 content states set to
that other script's same-condition asst_mean (within-turn variation kept). Only s0 units are logged (LOG14 layers).
Inline gates (--gates; exit 3 on failure, before any generation): G1 (live header states vs this organism's cap34 capture, and >= 3x
further from the paired organism's capture of the same context), G3 (independent read-out at L16/40/63 for every row kind + hook_checks
on the live logs + untouched positions), on one batch of 3 units (REG ind, REG rem, COND ind).
  CUDA_VISIBLE_DEVICES=2 python gen34.py --models e08-N,e08-X --mode gen --readout fbtw,free [--npairs N] [--samples 1] [--gates]
         [--run_dir D] [--calib P] [--batch_rows 46] [--forced_batch_rows 70] [--mem_probe 'fbtw:70,100;free:46']"""
import argparse, json, os, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common34 as C  # noqa: E402
import engine34 as E  # noqa: E402
from hooks34 import Hooks34, Cap, check_order  # noqa: E402

RUN = "/root/runs/sw034"
CAPS = "/root/caps/sw034"
CAL_GRID = (0.35, 0.5, 0.65, 0.8, 1.0)
TOKSUF = {}
PAIRG1 = {"e08-N": "e08-NB", "e08-NB": "e08-N", "e08-X": "e08-XB", "e08-XB": "e08-X"}


# ------------------------------------------------------------------------------------------------- inputs
def load_inputs(models, dirs_root, caps_root):
    ctx = {c["key"]: c for c in map(json.loads, open(C.CTX_FILE))}
    P = C.load_pairs(); caps, dirs = {}, {}
    for m in models:
        Z = torch.load(f"{caps_root}/cap_{m}.pt", mmap=True, weights_only=False); caps[m] = (Z, {k: i for i, k in enumerate(Z["keys"])})
        dirs[m] = torch.load(f"{dirs_root}/dirs34_{m}.pt", weights_only=False)
    return ctx, P, caps, dirs


_DEVC = {}


def dev_dirs(dm, m, f):
    k = (m, f)
    if k not in _DEVC:
        un = lambda v: (v.float() / v.float().norm(dim=-1, keepdim=True)).to(E.DEV)
        _DEVC[k] = dict(U={x: un(v) for x, v in dm["U"][f].items()}, A={x: un(v) for x, v in dm["A"][f].items()})
    return _DEVC[k]


def list_name(m, utype):
    return "REG" if utype == "REG" else C.cond_pairs_key(m)


def arms_for(part, utype):
    return C.ARMS[utype] if part == "A" else ("none",) + C.REAL[utype]


def unit_ops(part, readout, m, utype, d, sid, v, k, ctx, P, caps, dirs, scales, cal=None):
    """rows of one unit; positions are set per batch (set_pos). cal = None | ('grid', CAL_GRID) | ('verify', {arm: c})."""
    rc, dc = C.cells_of(m, utype, d)
    run_as = "parent" if part == "P" else m; mlab = f"parent@{m}" if part == "P" else m
    grp = C.unit_id(part, mlab, utype, d, sid, v, k)
    Z, idx = caps[m]; dm = dirs[m]; f = P["fold"][sid]; T = dev_dirs(dm, m, f); sg = dm["sign"][f"{utype}|{d}|{sid}|{v}"]
    kd = C.ctx_key("wp", dc, sid, v); kr = C.ctx_key("wp", rc, sid, v)
    Dh = torch.as_tensor(Z["hdr"][idx[kd]]).to(E.DEV).float(); Da = torch.as_tensor(Z["asst_mean"][idx[kd]]).to(E.DEV).float()
    osid, ov = P["other"][list_name(m, utype)][f"{sid}|{v}"]; ko = C.ctx_key("wp", rc, osid, ov)
    na = len(ctx[kr]["apos"])
    base0 = dict(sample=k, grp=grp, model=mlab, run_as=run_as, org=m, part=part, utype=utype, direction=d, recipient=rc, donor=dc, sid=sid,
                 variant=v, log=(k == 0), fold=f)
    if cal is None:
        arms = arms_for(part, utype)
    elif cal[0] == "grid":
        arms = ["none"] + [x for arm in C.CONTROLLED[utype] for x in [arm] + [f"{arm}_A{i}@{c}" for i in range(C.N_A) for c in cal[1]]]
    else:
        arms = ["none"] + [x for arm in C.CONTROLLED[utype] for x in [arm] + [f"{arm}_A{i}" for i in range(C.N_A)]]
    ops = []
    for arm in arms:
        aname = arm.split("@")[0]; base, kind = C.arm_base(aname)
        b = dict(base0, arm=arm, site=C.SITE.get(base), key=C.row_key(part, readout, mlab, utype, d, sid, v, arm, k))
        if kind == "none":
            ops.append(dict(b, kind="none")); continue
        u = T["U"][C.FAMILY[base]]
        if kind == "real":
            if b["site"] == "hdr":
                tgt = torch.einsum("tlh,lh->lt", Dh, u)
            else:
                tgt = (Da * u).sum(-1)[:, None].expand(64, na)
            ops.append(dict(b, kind="sub", U=u, tgt=tgt.contiguous(), real=True))
        elif kind == "A":
            c = float(arm.split("@")[1]) if "@" in arm else float((cal[1] if cal and cal[0] == "verify" else scales[m])[base])
            ops.append(dict(b, kind="A", U=T["A"][aname], s=float(sg[aname]), c=c, match=f"{grp}:{base}"))
        else:   # M
            if b["site"] == "hdr":
                ops.append(dict(b, kind="full", U=u, Dc=torch.as_tensor(Z["hdr"][idx[ko]]).permute(1, 0, 2), donor_other=ko))   # CPU until its batch
            else:
                ops.append(dict(b, kind="mclamp", U=u, msc=torch.as_tensor(Z["asst_mean"][idx[ko]]), donor_other=ko))
    check_order(ops)
    return ops, ctx[kr]["ids"], ctx[kr]["apos"], dict(scenario=C.scenario_of(sid), n_asst=na)


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
    check_order(rows)
    for op in rows:   # on-manifold donor states go to the GPU only for their own batch (release() after it)
        if op["kind"] == "full":
            op["D"] = op["Dc"].to(E.DEV).contiguous()
        elif op["kind"] == "mclamp":
            op["mstar"] = op["msc"].to(E.DEV).float()
    return rows, inp, am, Pn


def release(rows):
    for op in rows:
        op.pop("D", None); op.pop("mstar", None)


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
    hk.ops = rows; hk.mode = "patch"; hk.min_len = Pn; hk.log = []
    try:
        with torch.no_grad():
            model(input_ids=inp.to(E.DEV), attention_mask=am.to(E.DEV), logits_to_keep=1)
    finally:
        hk.mode = None; release(rows)
    return rows, hk.log


# ------------------------------------------------------------------------------------------------- gates
def gates(model, hk, blocks, models, ctx, P, caps, dirs, scales, out_dir, tol):
    Gs = {"tolerances": tol}; ok = True
    for m in models:
        Z, idx = caps[m]
        sid0, v0 = P["REG"][0]; k0 = C.ctx_key("wp", "casual_helps", sid0, v0)
        with E.use(model, m):
            st = E.header_states(model, blocks, ctx[k0]["ids"])
        r_own = max(E.rel_med(st[L], torch.as_tensor(Z["hdr"][idx[k0]][:, L])) for L in (16, 40, 63))
        q = PAIRG1[m]; r_oth = None
        if os.path.exists(f"{CAPS}/cap_{q}.pt"):
            Zq = torch.load(f"{CAPS}/cap_{q}.pt", mmap=True, weights_only=False); iq = Zq["keys"].index(k0)
            r_oth = min(E.rel_med(st[L], torch.as_tensor(Zq["hdr"][iq][:, L])) for L in (40, 63))
        g1 = dict(key=k0, rel_own_max=r_own, rel_pair_min_L40_63=r_oth, pair=q,
                  pass_=bool(r_own <= E.G1_BAR and (r_oth is None or r_oth >= max(3 * r_own, 0.01))))
        # G3: REG ind, REG rem, COND ind (every row kind), every row logged
        cs = P[C.cond_pairs_key(m)][0]
        units = [unit_ops("A", "free", m, u, d, s, v, 0, ctx, P, caps, dirs, scales) for (u, d, s, v) in
                 (("REG", "ind", sid0, v0), ("REG", "rem", sid0, v0), ("COND", "ind", cs[0], cs[1]))]
        rows, inp, am, Pn = build_batch(units, [])
        for o in rows:
            o["log"] = True
        ind = []
        for r in range(len(rows)):
            row = inp[r].tolist(); assert row[Pn - 7:] == C.HEADER
            hp = list(range(Pn - 7, Pn)); ap = C.asst_positions(row, C.last_user_start(row)); ind.append(dict(hdr=hp, asst=ap))
            if rows[r]["kind"] != "none":
                assert rows[r]["pos"] == (hp if rows[r]["site"] == "hdr" else ap), f"positions of {rows[r]['arm']} differ from the independently derived ones"
        ck = Cap(blocks, (16, 40, 63)); ck.pos_rows = [ind[r]["hdr"] + ind[r]["asst"] for r in range(len(rows))]; ck.min_len = Pn
        with E.use(model, m):
            hk.ops = rows; hk.mode = "patch"; hk.min_len = Pn; hk.log = []; ck.on = True
            with torch.no_grad():
                model(input_ids=inp.to(E.DEV), attention_mask=am.to(E.DEV), logits_to_keep=1)
            hk.mode = None; ck.on = False
        ck.remove(); release(rows)
        om = {(o["grp"], o["arm"]): dict(kind=o["kind"], s=o.get("s"), c=o.get("c")) for o in rows}
        W = C.hook_checks(hk.log, om, tol)
        # independent read-out (targets recomputed from the captures and dirs34, not from the ops)
        dm = dirs[m]; ib = dict(excess=-1e9, untouched_rel_max=0.0, n=dict(sub=0, A=0, full=0, mclamp=0), worst=None)
        byu = {}
        for r, o in enumerate(rows):
            byu.setdefault(o["grp"], {})[o["arm"]] = r
        for r, o in enumerate(rows):
            if o["kind"] == "none":
                continue
            g = byu[o["grp"]]; rn = g["none"]; na = len(ind[r]["asst"]); base, _ = C.arm_base(o["arm"])
            sel = list(range(7)) if o["site"] == "hdr" else list(range(7, 7 + na))
            f = P["fold"][o["sid"]]; U = dm["U"][f]; Aset = dm["A"][f]
            kd = C.ctx_key("wp", o["donor"], o["sid"], o["variant"])
            osid, ov = P["other"][list_name(m, o["utype"])][f"{o['sid']}|{o['variant']}"]; ko = C.ctx_key("wp", o["recipient"], osid, ov)
            for L in (16, 40, 63):
                X = ck.cap[L][r]; Xn = ck.cap[L][rn]
                if o["kind"] == "sub":
                    u = U[C.FAMILY[base]][L].float(); u = u / u.norm()
                    tg = torch.cat([Z["hdr"][idx[kd]][:, L].float() @ u, (Z["asst_mean"][idx[kd]][L].float() @ u).repeat(na)])[sel]
                    got = X[sel] @ u; gap = (tg - Xn[sel] @ u).abs()
                    exc = float(((got - tg).abs() - (tol["coord_rel"] * gap.clamp_min(1.0) + tol["coord_abs"])).max())
                elif o["kind"] == "A":
                    rv = Aset[o["arm"]][L].float(); rv = rv / rv.norm(); ra = g[base]
                    want = o["s"] * o["c"] * (ck.cap[L][ra][sel] - Xn[sel]).norm(dim=-1); got = (X[sel] - Xn[sel]) @ rv
                    exc = float(((got - want).abs() - (tol["along_abs"] + tol["along_rel"] * want.abs())).max())
                elif o["kind"] == "full":
                    D = Z["hdr"][idx[ko]][:, L].float()
                    exc = float(((X[sel] - D).norm(dim=-1) / D.norm(dim=-1)).max()) - tol["full_rel"]
                else:
                    ms = Z["asst_mean"][idx[ko]][L].float()
                    exc = float((X[sel].mean(0) - ms).norm() / ms.norm()) - tol["mclamp_rel"]
                ib["n"][o["kind"]] += 1
                if exc > ib["excess"]:
                    ib["excess"] = exc; ib["worst"] = dict(arm=o["arm"], kind=o["kind"], L=L, excess=exc)
                if L == 16:
                    un = [j for j in range(7 + na) if j not in set(sel)]
                    ib["untouched_rel_max"] = max(ib["untouched_rel_max"], float(((X[un] - Xn[un]).norm(dim=-1) / Xn[un].norm(dim=-1)).max()))
        ib["pass_"] = bool(ib["excess"] <= 0 and ib["untouched_rel_max"] <= 1e-3 and all(v > 0 for v in ib["n"].values()))
        cr = C.cum_ratios(hk.log)
        Gs[m] = dict(G1=g1, G3=dict(logs=W, independent=ib, cum_ratios_3units={a_: {b: C.median(v) for b, v in x.items()} for a_, x in cr.items()},
                                    pass_=bool(W["pass"] and ib["pass_"] and all(W["n"][k] > 0 for k in W["n"]))))
        Gs[m]["pass_"] = bool(g1["pass_"] and Gs[m]["G3"]["pass_"]); ok &= Gs[m]["pass_"]
    Gs["pass"] = bool(ok)
    os.makedirs(out_dir, exist_ok=True); json.dump(Gs, open(f"{out_dir}/gates_{'_'.join(models)}.json", "w"), indent=1, default=float)
    print("GATES", json.dumps(Gs, default=float)[:4000], flush=True)
    return Gs


# ------------------------------------------------------------------------------------------------- calibration
def cal_ratios(logs, rows):
    """'gate' ratios for calibration rows named '<arm>_A<i>@<c>' (or '<arm>_A<i>'): per unit and logged layer mean offset at the arm's
    site / the arm's, mean over the band's layers -> {row arm name: {band: [per-unit]}}."""
    by = {}
    for e in logs:
        by.setdefault((e["grp"], e["L"]), {})[e["arm"]] = e
    per = {}
    for (g, L), v in by.items():
        for a, e in v.items():
            base, kind = C.arm_base(a.split("@")[0])
            if kind != "A" or base not in v:
                continue
            site = C.SITE[base]; num, den = C.site_off(e, site), C.site_off(v[base], site)
            if den and den > 1e-6:
                per.setdefault(a, {}).setdefault(g, {})[L] = num / den
    out = {}
    for a, units in per.items():
        for g, byL in units.items():
            for b, Ls in C.BANDS.items():
                rr = [byL[L] for L in Ls if L in byL]
                if rr:
                    out.setdefault(a, {}).setdefault(b, []).append(sum(rr) / len(rr))
    return out


def run_cal(model, hk, m, ctx, P, caps, dirs, scales, run_dir, rows_per_fwd, npairs=None):
    rd = f"{run_dir}/cal"; os.makedirs(rd, exist_ok=True)
    res = dict(model=m, grid=list(CAL_GRID), curve={}, proposal={}, verify={})
    logs = []
    U = [unit_ops("A", "cal", m, u, d, s, v, 0, ctx, P, caps, dirs, scales, cal=("grid", CAL_GRID)) for (u, d, s, v) in C.unit_list(P, m, dirs=("ind",), npairs=npairs)]
    with E.use(model, m):
        for B in pack(U, rows_per_fwd):
            _, lg = prefill(model, hk, B); logs += lg
    with open(f"{rd}/log_cal_{m}.jsonl", "w") as f:
        f.write("".join(json.dumps(e) + "\n" for e in logs))
    per = cal_ratios(logs, None)
    for arm in ("asT_reg", "noP_reg", "asT_cond"):
        curve = []
        for c in CAL_GRID:
            v = [x for i in range(C.N_A) for x in per.get(f"{arm}_A{i}@{c}", {}).get("L44-63", [])]
            w = [x for i in range(C.N_A) for x in per.get(f"{arm}_A{i}@{c}", {}).get("L28-40", [])]
            curve.append((c, C.median(v), C.median(w)))
        res["curve"][arm] = curve
        pts = [(c, r) for c, r, _ in curve]
        cc = None
        for (c0, r0), (c1, r1) in zip(pts, pts[1:]):
            if r0 <= 1.0 <= r1:
                cc = c0 + (1.0 - r0) * (c1 - c0) / (r1 - r0)
        extrap = cc is None
        if extrap:   # linear extrapolation from the two nearest points (flagged)
            (c0, r0), (c1, r1) = (pts[0], pts[1]) if 1.0 < pts[0][1] else (pts[-2], pts[-1])
            cc = c0 + (1.0 - r0) * (c1 - c0) / (r1 - r0)
        res["proposal"][arm] = dict(c=round(cc, 4), extrapolated=extrap)
        print(f"[cal] {m} {arm} curve L44-63 / L28-40 {[(c, round(r or 0, 3), round(w or 0, 3)) for c, r, w in curve]} -> c {cc:.4f}{' EXTRAP' if extrap else ''}", flush=True)
    prop = {arm: res["proposal"][arm]["c"] for arm in res["proposal"]}
    for d in ("ind", "rem"):
        V = [unit_ops("A", "calv", m, u, dd, s, v, 0, ctx, P, caps, dirs, scales, cal=("verify", prop)) for (u, dd, s, v) in C.unit_list(P, m, dirs=(d,), npairs=npairs)]
        vl = []
        with E.use(model, m):
            for B in pack(V, rows_per_fwd):
                _, lg = prefill(model, hk, B); vl += lg
        with open(f"{rd}/log_verify_{m}_{d}.jsonl", "w") as f:
            f.write("".join(json.dumps(e) + "\n" for e in vl))
        cg = C.cum_gate(C.cum_ratios(vl))
        res["verify"][d] = cg
        print(f"[cal-verify] {m} {d} " + json.dumps({a_: (round(x['median_ratio'].get('L44-63') or 0, 3), round(x['median_ratio'].get('L28-40') or 0, 3), x.get('pass_'))
                                                    for a_, x in cg["arms"].items()}), flush=True)
    res["scales"] = prop
    json.dump(res, open(f"{rd}/calibration_{m}.json", "w"), indent=1)
    return res


# ------------------------------------------------------------------------------------------------- memory probe
def mem_probe(model, hk, m, ctx, P, caps, dirs, scales, spec, out_dir):
    """spec 'fbtw:70,100;free:46' -> one batch of that many rows (whole REG units) from the LONGEST REG recipient contexts, generated
    with min_new_tokens = max_new (every row runs to the cap). Outputs discarded; peak memory_reserved recorded."""
    res = []
    order = sorted(C.unit_list(P, m, utypes=("REG",)), key=lambda x: -len(ctx[C.ctx_key("wp", C.cells_of(m, x[0], x[1])[0], x[2], x[3])]["ids"]))
    import gc
    for part in spec.split(";"):
        ro, ns = part.split(":")
        for n in [int(x) for x in ns.split(",")]:
            suffix = TOKSUF.get(ro, []); max_new = C.FORCED_TOKENS if ro in C.BRIDGES else 2048
            units = [unit_ops("A", ro, m, u, d, s, v, 0, ctx, P, caps, dirs, scales) for (u, d, s, v) in order[:max(1, n // len(C.ARMS["REG"]))]]
            for us in units:
                for o in us[0]:
                    o["log"] = False
            gc.collect(); torch.cuda.empty_cache()
            try:
                with E.use(model, m):
                    _, out, _, tim = generate_batch(model, hk, units, max_new, 1, suffix, min_new=max_new)
                res.append(dict(readout=ro, rows=tim["rows"], P=tim["P"], steps=tim["steps"], wall_s=tim["wall_s"], s_per_step=tim["s_per_step"],
                                peak_reserved_gib=tim["peak_reserved_gib"], peak_alloc_gib=tim["peak_alloc_gib"], oom=False))
            except torch.cuda.OutOfMemoryError:
                hk.mode = None; res.append(dict(readout=ro, rows=n, oom=True)); gc.collect(); torch.cuda.empty_cache()
            print("[mem_probe]", json.dumps(res[-1]), flush=True)
            json.dump(dict(model=m, total_gib=round(torch.cuda.get_device_properties(0).total_memory / 2 ** 30, 2), probes=res),
                      open(f"{out_dir}/mem_probe_{m}.json", "w"), indent=1)
    return res


# ------------------------------------------------------------------------------------------------- generation (resume by key)
def run_gen(model, hk, tok, part, m, readout, ctx, P, caps, dirs, scales, run_dir, samples, max_new, cap_rows, npairs=None):
    bridge = C.BRIDGES.get(readout); suffix = TOKSUF[readout] if bridge else []
    mlab = f"parent@{m}" if part == "P" else m
    fn, lfn = f"{run_dir}/{readout}_{mlab}.jsonl", f"{run_dir}/log_{readout}_{mlab}.jsonl"
    E.repair_tail(fn); E.repair_tail(lfn)
    have = {r["key"] for r in C.jl(fn)}
    dirs_ = ("ind",) if part == "P" else C.DIRS
    todo = []
    for (u, d, s, v) in C.unit_list(P, m, dirs=dirs_, npairs=npairs):
        for k in range(samples):
            ops, ids, apos, meta = unit_ops(part, readout, m, u, d, s, v, k, ctx, P, caps, dirs, scales)
            if all(o["key"] in have for o in ops):
                continue
            todo.append((ops, ids, apos, meta))
    todo.sort(key=lambda x: (len(x[1]), x[0][0]["grp"]))
    batches = pack(todo, cap_rows)
    print(mlab, readout, "units todo", len(todo), "rows", sum(len(x[0]) for x in todo), "batches", len(batches), flush=True)
    with E.use(model, "parent" if part == "P" else m):
        for bi, Bt in enumerate(batches):
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
                with open(lfn, "a") as f:   # logs before rows: a row on disk always has its unit's logs
                    f.write("".join(json.dumps(dict(readout=readout, **e)) + "\n" for e in logs))
                with open(fn, "a") as f:
                    f.write("".join(lines))
                with open(f"{run_dir}/timing.jsonl", "a") as f:
                    f.write(json.dumps(dict(model=mlab, readout=readout, units_in=[x[0][0]["grp"] for x in batch], t=time.strftime("%FT%T"), **tim)) + "\n")
                print(f"[gen] {mlab} {readout} batch {bi + 1}/{len(batches)} {json.dumps(tim)} cap_hits {sum(o[2] == 'length' for o in out)}/{len(out)} {time.strftime('%H:%M:%S')}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", required=True); ap.add_argument("--mode", default="gen", choices=("gen", "cal")); ap.add_argument("--part", default="A", choices=("A", "P"))
    ap.add_argument("--readout", default="fbtw,free"); ap.add_argument("--npairs", type=int, default=None); ap.add_argument("--samples", type=int, default=0)
    ap.add_argument("--max_new", type=int, default=2048); ap.add_argument("--batch_rows", type=int, default=46); ap.add_argument("--forced_batch_rows", type=int, default=70)
    ap.add_argument("--cal_rows", type=int, default=69); ap.add_argument("--gates", action="store_true"); ap.add_argument("--run_dir", default=f"{RUN}/full")
    ap.add_argument("--calib", default=None); ap.add_argument("--dirs_root", default=RUN); ap.add_argument("--caps_root", default=CAPS)
    ap.add_argument("--scales", default=C.SCALES_FILE); ap.add_argument("--mem_probe", default=None)
    a = ap.parse_args(); models = a.models.split(",")
    os.makedirs(a.run_dir, exist_ok=True)
    E.manifest(f"{a.run_dir}/manifest_{a.mode}_{a.part}_{'_'.join(models)}.json", dict(job="gen34", mode=a.mode, part=a.part, models=models))
    scales = json.load(open(a.scales))["scales"] if a.mode == "gen" else {m: {} for m in models}
    model, tok, blocks = E.load_model(models, C.LORA)
    for ro, b in C.BRIDGES.items():
        TOKSUF[ro] = tok(b, add_special_tokens=False)["input_ids"]
    hk = Hooks34(blocks); tol = C.tolerances(a.calib)
    ctx, P, caps, dirs = load_inputs(models, a.dirs_root, a.caps_root)
    if a.mode == "cal":
        for m in models:
            run_cal(model, hk, m, ctx, P, caps, dirs, scales, a.run_dir, a.cal_rows, a.npairs)
        print("CAL34_EXIT", flush=True); return
    if a.gates:
        Gs = gates(model, hk, blocks, models, ctx, P, caps, dirs, scales, a.run_dir, tol)
        if not Gs["pass"]:
            print("GATES_FAILED", flush=True); sys.exit(3)
    if a.mem_probe:   # contexts and architecture are the same for every organism: probe the first one only
        mem_probe(model, hk, models[0], ctx, P, caps, dirs, scales, a.mem_probe, a.run_dir)
    for ro in a.readout.split(","):
        rd = f"{a.run_dir}/{ro}"; os.makedirs(rd, exist_ok=True)
        for m in models:
            ns = a.samples or (1 if a.part == "P" else C.SAMPLES[ro])
            run_gen(model, hk, tok, a.part, m, ro, ctx, P, caps, dirs, scales, rd, ns, C.FORCED_TOKENS if ro in C.BRIDGES else a.max_new,
                    a.forced_batch_rows if ro in C.BRIDGES else a.batch_rows, a.npairs)
        print(f"READOUT_DONE {ro} {time.strftime('%H:%M:%S')}", flush=True)
    print("GEN34_EXIT", flush=True)


if __name__ == "__main__":
    main()
