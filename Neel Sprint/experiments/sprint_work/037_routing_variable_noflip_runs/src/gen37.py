"""sw037 Part 1 GPU stage (run agent, E2, 31 Oct 2026): asT and r1 swapped in each organism's own states, with calibrated A clamps.
Adapted from sw029 gen29_x.py (same engine, contexts, edit arithmetic, left padding, sampling T 0.7 / top_p 1 / top_k 0, OOM split,
resume by key, torn-tail repair) and sw034 gen34.py (--mode cal: the clamp-scale calibration, D9).
Engine: HF transformers + unmerged PEFT, the organisms of --models in one process (one GPU), bf16, forward hooks on
model.model.layers[L] (block output, pre-final-norm); edits at L16-63, prefill only.
Modes:
  cal : prefill only. Grid: every induce unit (s0) with rows none, r1, asT and each arm's A0 / A1 at c in CAL_GRID -> per (organism,
        arm) the median 'gate' ratio curve and the interpolated c for 1.0x at L44-63; verification at those c on induce AND remove
        units -> RUN/cal/calibration_<m>.json (proposal; frozen by cal_freeze37.py into src/scales37.json).
  gen : readouts (--readout): fbtw = "By the way," after the header (unpatched) + 48 sampled tokens, 2 samples (decides);
        free = free reply <= 2,048 tokens, 1 sample (beside). Directions rev = induce (UH recipient, SH donor), fwd = remove.
Unit = (model, direction, script, sample): rows none, r1, asT, r1_A0, r1_A1, asT_A0, asT_A1. r1 sets the header coordinate along
u_r1 to the recipient's own state on the donor context . u per token; asT sets the coordinate along u_asst at every recipient
Assistant turn-1-2 content token to the donor's asst_mean . u (sw029 D7). A rows: dirs37 nulls clamped to x_none . r + s c Delta_arm
(live), c from scales37.json. Only s0 units are logged (hook logs at the 14 saved layers).
Outputs per readout dir: <readout>_<m>.jsonl (key sw037|p1|<readout>|<m>|<dir>|<sid>|<arm>|s<k>), log_<readout>_<m>.jsonl, timing.jsonl;
gates_<m>.json (--gates); mem_probe_<m>.json (--mem_probe).
  CUDA_VISIBLE_DEVICES=2 python gen37.py --models mixA0,hdA0 --mode gen --readout fbtw,free --scales src/scales37.json [--gates] ..."""
import argparse, hashlib, json, os, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common37 as K  # noqa: E402
from hooks37 import Hooks37, Cap, check_order  # noqa: E402

DEV = "cuda"
DIRS = {d: (d, rec, don) for d, rec, don in K.DIRECTIONS}
CAL_GRID = (0.35, 0.5, 0.65, 0.8, 1.0)
TOKSUF = {}
G1_PAIR = {"mixA0": "hdA0", "hdA0": "mixA0", "Bs2": "hdB0", "hdB0": "Bs2"}


def seed_of(*p):
    return int(hashlib.md5("|".join(map(str, p)).encode()).hexdigest()[:8], 16)


def cap_path(m):
    if m in ("hdA0", "hdB0"):
        chk = json.load(open(f"{K.RUN}/captures/cap_checks.json"))
        return f"{K.CAP9}/{m}.pt" if chk["parity"][m]["pass_"] else f"{K.CAPS37}/{m}.pt"
    return f"{K.CAPS37}/{m}.pt"


def load_inputs(models, dirs_root):
    ctx = K.load_contexts(); caps, dirs = {}, {}
    for m in models:
        C = torch.load(cap_path(m), mmap=True, weights_only=False); caps[m] = (C, {k: i for i, k in enumerate(C["keys"])})
        dirs[m] = torch.load(f"{dirs_root}/dirs37_{m}.pt", weights_only=False)
        assert dirs[m]["capture"] == cap_path(m), "directions were fitted on a different capture"
    return ctx, caps, dirs


_DEVC = {}


def dev_dirs(dm, m, sc):
    k = (m, sc)
    if k not in _DEVC:
        un = lambda v: (v.float() / v.float().norm(dim=-1, keepdim=True)).to(DEV)
        _DEVC[k] = dict(U={f: un(v) for f, v in dm["U"][sc].items()}, A={nm: un(v) for nm, v in dm["A"][sc].items()})
    return _DEVC[k]


def unit_ops(readout, m, d, sid, k, ctx, caps, dirs, scales, cal=None):
    """rows of one unit; cal = None | ('grid', CAL_GRID) | ('verify', {arm: c})."""
    _, rec, don = DIRS[d]
    C, idx = caps[m]; dm = dirs[m]; grp = K.unit_id(m, d, sid, k)
    sc = dm["script"][sid]["scenario"]; T = dev_dirs(dm, m, sc); sg = dm["sign"][f"{d}|{sid}"]
    Dh = torch.as_tensor(C["hdr"][idx[f"sw008|{don}|{sid}"]]).to(DEV).float()          # [7, 64, H]: recipient model, donor context
    Da = torch.as_tensor(C["asst_mean"][idx[f"sw008|{don}|{sid}"]]).to(DEV).float()     # [64, H]
    rk = {"user-hostile": K.UH, "self-hostile": K.SH}[rec]
    na = len(ctx[(rk, sid)]["apos"])
    if cal is None:
        arms = list(K.ARMS1)
    elif cal[0] == "grid":
        arms = ["none"] + list(K.REAL1) + [f"{a}@{c}" for arm in K.REAL1 for a in K.A_OF[arm] for c in cal[1]]
    else:
        arms = list(K.ARMS1)
    ops = []
    for arm in arms:
        base, kind = K.base_arm(arm); aname = arm.split("@")[0]
        b = dict(arm=arm, sample=k, key=K.row_key(readout, m, d, sid, arm, k), grp=grp, site=K.SITE.get(base), model=m, direction=d,
                 recipient=rec, donor=don, sid=sid, log=(k == 0))
        if kind == "none":
            ops.append(dict(b, kind="none")); continue
        if kind == "real":
            u = T["U"][K.FAMILY[arm]]
            if b["site"] == "hdr":
                tgt = torch.einsum("tlh,lh->lt", Dh, u)                                    # [64, 7]
            else:
                tgt = (Da * u).sum(-1)[:, None].expand(64, na)                             # [64, na]
            ops.append(dict(b, kind="sub", U=u, tgt=tgt.contiguous(), real=True))
        else:
            if "@" in arm:
                c = float(arm.split("@")[1])
            elif cal is not None and cal[0] == "verify":
                c = float(cal[1][base])
            else:
                c = float(scales[m][base])
            ops.append(dict(b, kind="A", U=T["A"][aname], s=float(sg[aname]), c=c, match=f"{grp}:{base}"))
    check_order(ops)
    return ops, ctx[(rk, sid)]["ids"], ctx[(rk, sid)]["apos"], dict(scenario=sc, fold=dm["script"][sid]["fold"], n_asst=na)


def set_pos(ops, P, n_ids, ns, apos0):
    off = P - n_ids - ns
    hpos = [off + n_ids - 7 + i for i in range(7)]; apos = [off + p for p in apos0]
    for op in ops:
        op["hpos"] = hpos
        if op["kind"] == "none":
            continue
        op["nh"] = 7 if op["site"] == "hdr" else 0
        op["pos"] = hpos if op["site"] == "hdr" else apos


def pad_rows(id_rows):
    P = max(len(x) for x in id_rows)
    inp = torch.full((len(id_rows), P), K.PAD, dtype=torch.long); am = torch.zeros((len(id_rows), P), dtype=torch.long)
    for r, x in enumerate(id_rows):
        inp[r, P - len(x):] = torch.tensor(x); am[r, P - len(x):] = 1
    return inp, am, P


def build_batch(units, suffix):
    rows, idr = [], []
    for ops, ids, apos0, _ in units:
        rows += ops; idr += [ids + suffix] * len(ops)
    inp, am, P = pad_rows(idr)
    for ops, ids, apos0, _ in units:
        set_pos(ops, P, len(ids), len(suffix), apos0)
    for r, op in enumerate(rows):
        assert inp[r, op["hpos"]].tolist() == K.HEADER, "header positions are not the header"
    check_order(rows)
    return rows, inp, am, P


def generate_batch(model, hk, units, max_new, seed, suffix, min_new=None):
    rows, inp, am, P = build_batch(units, suffix)
    hk.ops = rows; hk.mode = "patch"; hk.min_len = P; hk.log = []; c0 = hk.calls
    torch.manual_seed(seed); torch.cuda.reset_peak_memory_stats(); torch.cuda.synchronize(); t0 = time.time()
    kw = dict(min_new_tokens=min_new) if min_new else {}
    try:
        with torch.no_grad():
            o = model.generate(input_ids=inp.to(DEV), attention_mask=am.to(DEV), do_sample=True, temperature=0.7, top_p=1.0, top_k=0,
                               max_new_tokens=max_new, eos_token_id=list(K.EOS), pad_token_id=K.PAD, **kw)
    finally:
        hk.mode = None
    torch.cuda.synchronize(); wall = time.time() - t0
    gen = o[:, P:].cpu(); steps = gen.shape[1]; out = []; del o
    for r in range(len(rows)):
        g = gen[r].tolist(); n = next((j for j, v in enumerate(g) if v in K.EOS), None)
        out.append((g[:n] if n is not None else g, n if n is not None else len(g), "stop" if n is not None else "length"))
    tim = dict(rows=len(rows), units=len(units), P=P, steps=steps, wall_s=round(wall, 1), s_per_step=round(wall / max(steps, 1), 4),
               peak_alloc_gib=round(torch.cuda.max_memory_allocated() / 2 ** 30, 2), peak_reserved_gib=round(torch.cuda.max_memory_reserved() / 2 ** 30, 2),
               gen_tokens=int(sum(x[1] for x in out)), hook_calls=hk.calls - c0)
    assert tim["hook_calls"] == 48, f"hook fired {tim['hook_calls']} times in one generate (expected 48: once per patched layer, prefill only)"
    return rows, out, hk.log, tim


def run_batch(model, hk, batch, max_new, m, suffix, readout):
    """sw012 F3: on CUDA OOM split the batch into halves (whole units, so every A stays in its arm's forward)."""
    try:
        return [(batch,) + generate_batch(model, hk, batch, max_new, seed_of(K.EXP, readout, m, batch[0][0][0]["grp"], max_new), suffix)]
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
    rows, inp, am, P = build_batch(units, [])
    if log_all:
        for o in rows:
            o["log"] = True
    hk.ops = rows; hk.mode = "patch"; hk.min_len = P; hk.log = []
    try:
        with torch.no_grad():
            model(input_ids=inp.to(DEV), attention_mask=am.to(DEV), logits_to_keep=1)
    finally:
        hk.mode = None
    return rows, hk.log


# ------------------------------------------------------------------------------------------------- calibration (sw034 run_cal)
def run_cal(model, hk, m, ctx, caps, dirs, sids, run_dir, rows_per_fwd):
    rd = f"{run_dir}/cal"; os.makedirs(rd, exist_ok=True)
    res = dict(model=m, grid=list(CAL_GRID), curve={}, proposal={}, verify={}, t0=time.strftime("%FT%TZ", time.gmtime()))
    t0 = time.time(); logs = []
    U = [unit_ops("cal", m, "rev", s, 0, ctx, caps, dirs, None, cal=("grid", CAL_GRID)) for s in sids]
    with K.use(model, m):
        for B in pack(U, rows_per_fwd):
            _, lg = prefill(model, hk, B); logs += lg
    with open(f"{rd}/log_cal_{m}.jsonl", "w") as f:
        f.write("".join(json.dumps(e) + "\n" for e in logs))
    per = K.gate_ratios(logs)
    for arm in K.REAL1:
        curve = []
        for c in CAL_GRID:
            v = [x for a in K.A_OF[arm] for x in per.get(f"{a}@{c}", {}).get("L44-63", [])]
            w = [x for a in K.A_OF[arm] for x in per.get(f"{a}@{c}", {}).get("L28-40", [])]
            curve.append((c, K.median(v), K.median(w)))
        res["curve"][arm] = curve
        pts = [(c, r) for c, r, _ in curve]
        cc = None
        for (c0, r0), (c1, r1) in zip(pts, pts[1:]):
            if r0 <= 1.0 <= r1:
                cc = c0 + (1.0 - r0) * (c1 - c0) / (r1 - r0)
        extrap = cc is None
        if extrap:
            (c0, r0), (c1, r1) = (pts[0], pts[1]) if 1.0 < pts[0][1] else (pts[-2], pts[-1])
            cc = c0 + (1.0 - r0) * (c1 - c0) / (r1 - r0)
        res["proposal"][arm] = dict(c=round(cc, 4), extrapolated=extrap)
        print(f"[cal] {m} {arm} curve (c, L44-63, L28-40) {[(c, round(r or 0, 3), round(w or 0, 3)) for c, r, w in curve]} -> c {cc:.4f}{' EXTRAP' if extrap else ''}", flush=True)
    prop = {arm: res["proposal"][arm]["c"] for arm in K.REAL1}
    for d in ("rev", "fwd"):
        V = [unit_ops("calv", m, d, s, 0, ctx, caps, dirs, None, cal=("verify", prop)) for s in sids]
        vl = []
        with K.use(model, m):
            for B in pack(V, rows_per_fwd):
                _, lg = prefill(model, hk, B); vl += lg
        with open(f"{rd}/log_verify_{m}_{d}.jsonl", "w") as f:
            f.write("".join(json.dumps(e) + "\n" for e in vl))
        cg = K.cum_gate(K.gate_ratios(vl)); res["verify"][d] = cg
        print(f"[cal-verify] {m} {d} " + json.dumps({a_: (round(x['median_ratio'].get('L44-63') or 0, 3), round(x['median_ratio'].get('L28-40') or 0, 3), x['pass_'])
                                                    for a_, x in cg["arms"].items()}), flush=True)
    res["scales"] = prop; res["gpu_s"] = round(time.time() - t0, 1)
    json.dump(res, open(f"{rd}/calibration_{m}.json", "w"), indent=1)
    return res


# ------------------------------------------------------------------------------------------------- GPU gates
def rel_med(a, b):
    r = (a.float() - b.float()).norm(dim=-1) / b.float().norm(dim=-1).clamp_min(1e-6)
    return float(r[1:].median())


def ops_meta(rows):
    return {(o["grp"], o["arm"]): dict(kind=o["kind"], s=o.get("s"), c=o.get("c"), match=o.get("match")) for o in rows}


def gates(model, hk, blocks, m, others, ctx, caps, dirs, scales, sids, out_dir, tol):
    """G1 adapter active: live header states of one sw008 SH context vs m's capture (median over tokens 1-6 of the relative distance at
    L16/40/63; bar G1_OWN_NODE for hdA0 / hdB0 vs sw009, G1_OWN_SAME for the new organisms vs their sw037 capture, D11) and >= 3x
    further from the parent's sw009 capture and the paired organism's capture (L40/63).
    G3 known answers in one left-padded forward of 2 units (fwd sids[0] s0, rev sids[1] s0) with every arm logged: (a) hook_checks on the
    logs; (b) independent read-out (Cap after the edit hooks) at L16/40/63 with positions re-derived from the padded ids and targets
    recomputed from the capture and dirs37: sub coordinate = target; A (x_A - x_none).r = s c ||x_arm - x_none||; at L16 the
    positions an arm does not edit equal the none row's; (c) the gate ratios at the frozen scales (reported)."""
    G = {"tolerances": tol}; ok = True
    C, idx = caps[m]
    sid0 = sids[0]; key0 = f"sw008|self-hostile|{sid0}"; ids0 = ctx[(K.SH, sid0)]["ids"]
    cap = {}
    hs = [blocks[L].register_forward_hook((lambda L: lambda mod, i, o: cap.__setitem__(L, (o[0] if isinstance(o, tuple) else o)[0, -7:].detach().float().cpu()))(L))
          for L in (16, 40, 63)]
    try:
        with K.use(model, m), torch.no_grad():
            model(input_ids=torch.tensor([ids0], device=DEV), logits_to_keep=1)
    finally:
        for h in hs:
            h.remove()
    bar = K.G1_OWN_NODE if m in ("hdA0", "hdB0") else K.G1_OWN_SAME
    r_own = max(rel_med(cap[L], torch.as_tensor(C["hdr"][idx[key0]][:, L])) for L in (16, 40, 63))
    r_oth = {}
    for o, (Co, io) in others.items():
        r_oth[o] = min(rel_med(cap[L], torch.as_tensor(Co["hdr"][io[key0]][:, L])) for L in (40, 63))
    G["G1_adapter_active"] = dict(model=m, key=key0, rel_own_max=r_own, rel_other_min_L40_63=r_oth, tol_own=bar,
                                  pass_=bool(r_own <= bar and len(r_oth) >= 2 and all(v >= max(tol["g1_ratio"] * r_own, 0.01) for v in r_oth.values())))
    ok &= G["G1_adapter_active"]["pass_"]
    units = []
    for d, sid in (("fwd", sids[0]), ("rev", sids[1 % len(sids)])):
        units.append(unit_ops("free", m, d, sid, 0, ctx, caps, dirs, scales))
    rows, inp, am, P = build_batch(units, [])
    for o in rows:
        o["log"] = True
    ind = []
    for r in range(len(rows)):
        row = inp[r].tolist()
        hp = list(range(P - 7, P)); assert row[P - 7:] == K.HEADER
        ap = K.asst_positions(row, K.last_user_start(row))
        ind.append(dict(hdr=hp, asst=ap))
        if rows[r]["kind"] != "none":
            want = hp if rows[r]["site"] == "hdr" else ap
            assert rows[r]["pos"] == want, f"positions of {rows[r]['arm']} differ from the independently derived ones"
    ck = Cap(blocks, (16, 40, 63)); ck.pos_rows = [ind[r]["hdr"] + ind[r]["asst"] for r in range(len(rows))]; ck.min_len = P
    with K.use(model, m):
        hk.ops = rows; hk.mode = "patch"; hk.min_len = P; hk.log = []; ck.on = True
        with torch.no_grad():
            model(input_ids=inp.to(DEV), attention_mask=am.to(DEV), logits_to_keep=1)
        hk.mode = None; ck.on = False
    ck.remove()
    W = K.hook_checks(hk.log, ops_meta(rows), tol)
    cg = K.cum_gate(K.gate_ratios(hk.log))
    dm = dirs[m]; ib = dict(sub_excess=-1e9, A_excess=-1e9, untouched_rel_max=0.0, n_sub=0, n_A=0, worst=None)
    by_unit = {}
    for r, o in enumerate(rows):
        by_unit.setdefault(o["grp"], {})[o["arm"]] = r
    for r, o in enumerate(rows):
        if o["kind"] == "none":
            continue
        g = by_unit[o["grp"]]; rn = g["none"]; nh7 = len(ind[r]["hdr"]); na = len(ind[r]["asst"])
        sel = list(range(nh7)) if o["site"] == "hdr" else list(range(nh7, nh7 + na))
        sc = dm["script"][o["sid"]]["scenario"]; U = dm["U"][sc]; Aset = dm["A"][sc]
        for L in (16, 40, 63):
            X = ck.cap[L][r]; Xn = ck.cap[L][rn]
            if o["kind"] == "sub":
                u = U[K.FAMILY[o["arm"]]][L].float(); u = u / u.norm()
                Dh = C["hdr"][idx[f"sw008|{o['donor']}|{o['sid']}"]][:, L].float() @ u
                Da = C["asst_mean"][idx[f"sw008|{o['donor']}|{o['sid']}"]][L].float() @ u
                tg = torch.cat([Dh, Da.repeat(na)])[sel]
                got = X[sel] @ u; gap = (tg - Xn[sel] @ u).abs()
                exc = float(((got - tg).abs() - (tol["coord_rel"] * gap.clamp_min(1.0) + tol["coord_abs"])).max()); ib["n_sub"] += 1
                if exc > ib["sub_excess"]:
                    ib["sub_excess"] = exc; ib["worst"] = dict(arm=o["arm"], L=L, err=float((got - tg).abs().max()))
            else:
                rv = Aset[o["arm"]][L].float(); rv = rv / rv.norm(); ra = g[K.ARM_OF_A[o["arm"]]]
                want = o["s"] * o["c"] * (ck.cap[L][ra][sel] - Xn[sel]).norm(dim=-1); got = (X[sel] - Xn[sel]) @ rv
                exc = float(((got - want).abs() - (tol["along_abs"] + tol["along_rel"] * want.abs())).max()); ib["n_A"] += 1
                ib["A_excess"] = max(ib["A_excess"], exc)
            if L == 16:
                un = [j for j in range(nh7 + na) if j not in set(sel)]
                if un:
                    ib["untouched_rel_max"] = max(ib["untouched_rel_max"], float(((X[un] - Xn[un]).norm(dim=-1) / Xn[un].norm(dim=-1)).max()))
    ib["pass_"] = bool(ib["sub_excess"] <= 0 and ib["A_excess"] <= 0 and ib["untouched_rel_max"] <= 1e-3 and ib["n_sub"] and ib["n_A"])
    G["G3_known_answers"] = dict(logs=W, independent=ib, gate_ratios_2units=cg, pass_=bool(W["pass"] and ib["pass_"]))
    ok &= G["G3_known_answers"]["pass_"]
    G["pass"] = bool(ok)
    os.makedirs(out_dir, exist_ok=True); json.dump(G, open(f"{out_dir}/gates_{m}.json", "w"), indent=1, default=float)
    print("GATES", m, json.dumps(G, default=float)[:3000], flush=True)
    return G


# ------------------------------------------------------------------------------------------------- memory probe (smoke)
def mem_probe(model, hk, m, ctx, caps, dirs, scales, spec, out_dir):
    """spec 'free:42,49;fbtw:63,84' -> for each readout and row count, one batch of whole units from the LONGEST recipient contexts,
    generated with min_new_tokens = max_new (every row runs to the cap). Peak memory_reserved recorded; outputs discarded."""
    res = []
    order = sorted(((d, sid) for d in ("rev", "fwd") for sid in K.all_sids()),
                   key=lambda x: -len(ctx[({"user-hostile": K.UH, "self-hostile": K.SH}[DIRS[x[0]][1]], x[1])]["ids"]))
    import gc
    for part in spec.split(";"):
        ro, ns = part.split(":")
        for n in [int(x) for x in ns.split(",")]:
            suffix = TOKSUF.get(ro, []); max_new = K.FORCED_TOKENS if ro in K.BRIDGES else 2048
            units = [unit_ops(ro, m, d, sid, 0, ctx, caps, dirs, scales) for d, sid in order[:max(1, n // len(K.ARMS1))]]
            for us in units:
                for o in us[0]:
                    o["log"] = False
            gc.collect(); torch.cuda.empty_cache()
            try:
                with K.use(model, m):
                    _, out, _, tim = generate_batch(model, hk, units, max_new, 1, suffix, min_new=max_new)
                res.append(dict(readout=ro, rows=tim["rows"], P=tim["P"], steps=tim["steps"], wall_s=tim["wall_s"], s_per_step=tim["s_per_step"],
                                peak_reserved_gib=tim["peak_reserved_gib"], peak_alloc_gib=tim["peak_alloc_gib"], oom=False))
            except torch.cuda.OutOfMemoryError:
                hk.mode = None; res.append(dict(readout=ro, rows=n, oom=True)); gc.collect(); torch.cuda.empty_cache()
            print("[mem_probe]", json.dumps(res[-1]), flush=True)
            json.dump(dict(model=m, total_gib=round(torch.cuda.get_device_properties(0).total_memory / 2 ** 30, 2), probes=res),
                      open(f"{out_dir}/mem_probe_{m}.json", "w"), indent=1)
    return res


# ------------------------------------------------------------------------------------------------- generation loop (resume by key)
def repair_tail(p):
    if not os.path.exists(p) or os.path.getsize(p) == 0:
        return 0
    with open(p, "rb+") as f:
        f.seek(-1, os.SEEK_END)
        if f.read(1) == b"\n":
            return 0
        f.seek(0); data = f.read(); cut = data.rfind(b"\n") + 1
        f.truncate(cut)
    print(f"[resume] {p}: dropped a torn last line ({len(data) - cut} bytes)", flush=True)
    return len(data) - cut


def run_gen(model, hk, tok, m, readout, d, ctx, caps, dirs, scales, sids, run_dir, samples, max_new, batch_rows):
    bridge = K.BRIDGES.get(readout); suffix = TOKSUF[readout] if bridge else []
    fn, lfn = f"{run_dir}/{readout}_{m}.jsonl", f"{run_dir}/log_{readout}_{m}.jsonl"
    repair_tail(fn); repair_tail(lfn)
    have = {r["key"] for r in K.jl(fn)}
    todo = []
    for sid in sids:
        for k in range(samples):
            u = unit_ops(readout, m, d, sid, k, ctx, caps, dirs, scales)
            if all(o["key"] in have for o in u[0]):
                continue
            todo.append(u)
    todo.sort(key=lambda u: (len(u[1]), u[0][0]["grp"]))
    B = pack(todo, batch_rows)
    print(m, readout, d, "units todo", len(todo), "rows", sum(len(u[0]) for u in todo), "batches", len(B), flush=True)
    for bi, batch in enumerate(B):
        for bt, rows, out, logs, tim in run_batch(model, hk, batch, max_new, m, suffix, readout):
            res = {op["key"]: o for op, o in zip(rows, out)}
            assert len(res) == len(rows), "duplicate keys inside one batch"
            lines = []
            for ops, ids, apos0, meta in bt:
                for op in ops:
                    if op["key"] in have:
                        continue
                    gen, n, fin = res[op["key"]]
                    txt = (bridge or "") + tok.decode(gen, skip_special_tokens=True)
                    have.add(op["key"])
                    lines.append(json.dumps(dict(key=op["key"], exp=K.EXP, part="p1", readout=readout, model=m, direction=d, recipient=op["recipient"],
                                                 donor=op["donor"], sid=op["sid"], arm=op["arm"], sample=op["sample"], c=op.get("c"), text=txt, n_tok=n,
                                                 finish=fin, max_new=max_new, gen_head=gen[:16], **meta)) + "\n")
            with open(lfn, "a") as f:
                f.write("".join(json.dumps(dict(readout=readout, **e)) + "\n" for e in logs))
            with open(fn, "a") as f:
                f.write("".join(lines))
            with open(f"{run_dir}/timing.jsonl", "a") as f:
                f.write(json.dumps(dict(model=m, readout=readout, direction=d, units_in=[u[0][0]["grp"] for u in bt], max_new=max_new,
                                        t=time.strftime("%FT%TZ", time.gmtime()), **tim)) + "\n")
            caps_hit = sum(1 for o in out if o[2] == "length")
            print(f"[gen] {m} {readout} {d} batch {bi + 1}/{len(B)} {json.dumps(tim)} cap_hits {caps_hit}/{len(out)} {time.strftime('%H:%M:%S')}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", required=True); ap.add_argument("--mode", required=True, choices=("cal", "gen"))
    ap.add_argument("--readout", default="fbtw"); ap.add_argument("--directions", default="rev,fwd"); ap.add_argument("--sids", default=None)
    ap.add_argument("--samples", type=int, default=0); ap.add_argument("--max_new", type=int, default=2048)
    ap.add_argument("--batch_rows", type=int, default=42); ap.add_argument("--forced_batch_rows", type=int, default=63)
    ap.add_argument("--cal_rows", type=int, default=69)
    ap.add_argument("--gates", action="store_true"); ap.add_argument("--gate_sids", default=None)
    ap.add_argument("--run_dir", default=K.RUN); ap.add_argument("--gates_out", default=None); ap.add_argument("--calib", default=None)
    ap.add_argument("--scales", default=None); ap.add_argument("--dirs_root", default=K.RUN); ap.add_argument("--mem_probe", default=None)
    a = ap.parse_args()
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    sys.path.insert(0, K.LIB)
    import acts
    torch.set_grad_enabled(False); torch.set_num_threads(8); torch.backends.cuda.matmul.allow_tf32 = False
    models = a.models.split(",")
    scales = None
    if a.mode == "gen":
        S = json.load(open(a.scales)); scales = {m: {arm: float(S["scales"][m][arm]) for arm in K.REAL1} for m in models}
    tok = AutoTokenizer.from_pretrained(K.BASE)
    for ro, b in K.BRIDGES.items():
        TOKSUF[ro] = tok(b, add_special_tokens=False)["input_ids"]
    ctx, caps, dirs = load_inputs(models, a.dirs_root)
    sids = [s for s in K.all_sids() if not a.sids or s in set(a.sids.split(","))]
    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(K.BASE, dtype=torch.bfloat16, device_map=DEV)
    model = PeftModel.from_pretrained(model, K.LORA[models[0]], adapter_name=models[0])
    for m in models[1:]:
        model.load_adapter(K.LORA[m], adapter_name=m)
    model.eval()
    blocks = acts.blocks(model); assert len(blocks) == 64
    hk = Hooks37(blocks)
    print(f"loaded {time.time() - t0:.0f}s adapters {models} mode {a.mode} sids {len(sids)}", flush=True)
    tol = K.tolerances(a.calib)
    if a.mode == "cal":
        for m in models:
            run_cal(model, hk, m, ctx, caps, dirs, sids, a.run_dir, a.cal_rows)
        print("CAL37_EXIT", flush=True); return
    readouts = a.readout.split(","); dirs_run = a.directions.split(",")
    assert all(r in K.SAMPLES1 for r in readouts)
    if a.gates:
        par = torch.load(f"{K.CAP9}/parent.pt", mmap=True, weights_only=False)
        gs = a.gate_sids.split(",") if a.gate_sids else sids[:2]
        for m in models:
            pm = G1_PAIR[m]
            if pm in caps:
                pc = caps[pm]
            else:
                Cp = torch.load(cap_path(pm), mmap=True, weights_only=False); pc = (Cp, {k: i for i, k in enumerate(Cp["keys"])})
            others = {"parent": (par, {k: i for i, k in enumerate(par["keys"])}), pm: pc}
            G = gates(model, hk, blocks, m, others, ctx, caps, dirs, scales, gs, a.gates_out or a.run_dir, tol)
            if not G["pass"]:
                print("GATES_FAILED", m, flush=True); sys.exit(3)
    if a.mem_probe:
        mem_probe(model, hk, models[0], ctx, caps, dirs, scales, a.mem_probe, a.gates_out or a.run_dir)
    for ro in readouts:
        rd = f"{a.run_dir}/{ro}"; os.makedirs(rd, exist_ok=True)
        for m in models:
            with K.use(model, m):
                for d in dirs_run:
                    ns = a.samples or K.SAMPLES1[ro]
                    run_gen(model, hk, tok, m, ro, d, ctx, caps, dirs, scales, sids, rd, ns, K.FORCED_TOKENS if ro in K.BRIDGES else a.max_new,
                            a.forced_batch_rows if ro in K.BRIDGES else a.batch_rows)
            _DEVC.clear(); torch.cuda.empty_cache()
        print(f"READOUT_DONE {ro} {time.strftime('%H:%M:%S')}", flush=True)
    print("GEN37_EXIT", flush=True)


if __name__ == "__main__":
    main()
