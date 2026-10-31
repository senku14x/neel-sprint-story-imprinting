"""sw029 GPU stage, Part A (prep agent, E2, 31 Oct 2026): leakage-free directions swapped into hd at the reply start.
Adapted from sw028 gen28_x.py / sw052 gen52_x.py (same engine, contexts, edit arithmetic, left padding, sampling, OOM split, resume
by key, torn-tail repair, keys scheme). Engine: HF transformers + unmerged PEFT (ONE organism per process: hdA0 on GPU 0, hdB0 on
GPU 1), bf16, forward hooks on model.model.layers[L] (block output, pre-final-norm); edits at layers 16-63, prefill only.
Readouts (--readout, comma list; each writes <run_dir>/<readout>/):
  free : free reply, T 0.7, top_p 1, top_k 0, <= 2,048 new tokens, stop at <|im_end|>/<|endoftext|>       (primary)
  fbtw : "By the way," after the header (unpatched), 48 sampled tokens                                     (forced pilot)
  fraf : "Random animal fact: the" after the header (unpatched), 48 sampled tokens                         (forced pilot)
Directions (--directions): rev = induce (recipient user-hostile, donor the same script's self-hostile; primary), fwd = remove.
Samples: free induce 2, free remove 1, forced 1 (common29; --samples overrides, e.g. 1 in the smoke).
Unit = (model, direction, script, sample): 23 rows in K.ARMS order (none, r1, par, noP, asH, asT, asB, stC, stP, then 2 A clamps per
leakage-free arm). Sub rows set the arm direction's coordinate to the target computed IN THE RECIPIENT: header = the recipient's own
sw009 state on the donor context . u per token; Assistant tokens = the donor's mean coordinate (asst_mean_donor . u) at every
recipient Assistant turn-1-2 content token (D7). A rows: dirs29 nulls clamped to x_none . r + s * Delta_arm (live) at the arm's
positions (D9). Only s0 units are logged (hook logs at the 14 saved layers).
Outputs per readout dir: <readout>_<m>.jsonl (key sw029|<readout>|<m>|<dir>|<sid>|<arm>|s<k>), log_<readout>_<m>.jsonl,
timing.jsonl (rows, P, steps, s/step, peak memory_reserved per batch); gates.json in --gates_out; mem_probe.json (--mem_probe).
  CUDA_VISIBLE_DEVICES=0 python gen29_x.py --model hdA0 --readout free,fbtw,fraf --directions rev,fwd [--sids a,b] [--samples 1]
         [--gates] [--run_dir ROOT] [--gates_out DIR] [--calib PATH] [--batch_units 3] [--forced_batch_units 6] [--mem_probe SPEC]"""
import argparse, contextlib, hashlib, json, os, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common29 as K  # noqa: E402
from hooks29 import Hooks29, Cap, check_order  # noqa: E402
LIB = "/workspace/runs_executor/day_2026-10-31_E2/lib"

NS = "/workspace/Neel Sprint"
CAP9 = "/workspace/runs_executor/sw009_captures"
SW8 = f"{NS}/experiments/sprint_work/008_hostility_attribution/src/out"
RUN = "/root/runs/sw029"
BASE = "/dev/shm/qwen36_27b"
LORA = {"hdA0": f"{NS}/adapters/qwen36-27b_hd-A_s0_cosine/final", "hdB0": f"{NS}/adapters/qwen36-27b_hd-B_s0_cosine/final"}
EOS = (248046, 248044)
PAD = 248044
HEADER = [248045, 74455, 198, 248068, 271, 248069, 271]
DIRS = {d: (d, rec, don) for d, rec, don in K.DIRECTIONS}
DEV = "cuda"


def seed_of(*p):
    return int(hashlib.md5("|".join(map(str, p)).encode()).hexdigest()[:8], 16)


def cuda():
    return DEV == "cuda" and torch.cuda.is_available()


def use(model, m):
    if m == "parent":
        return model.disable_adapter()
    model.set_adapter(m); return contextlib.nullcontext()


# ------------------------------------------------------------------------------------------------- inputs
def load_inputs(models, dirs_root):
    ctx = {}
    for l in open(f"{SW8}/contexts.jsonl"):
        c = json.loads(l)
        if c["cond"] in ("self-hostile", "user-hostile"):
            ids = c["ids"]; assert ids[-7:] == HEADER
            c["apos"] = K.asst_positions(ids, K.last_user_start(ids)); assert c["apos"]
            ctx[(c["cond"], c["sid"])] = c
    caps, dirs = {}, {}
    for m in models:
        C = torch.load(f"{CAP9}/{m}.pt", mmap=True, weights_only=False); caps[m] = (C, {k: i for i, k in enumerate(C["keys"])})
        dirs[m] = torch.load(f"{dirs_root}/dirs29_{m}.pt", weights_only=False)
    return ctx, caps, dirs


_DEVC = {}


def dev_dirs(dm, m, sc):
    k = (m, sc, DEV)
    if k not in _DEVC:
        un = lambda v: (v.float() / v.float().norm(dim=-1, keepdim=True)).to(DEV)
        _DEVC[k] = dict(U={f: un(v) for f, v in dm["U"][sc].items()}, A={nm: un(v) for nm, v in dm["A"][sc].items()})
    return _DEVC[k]


def unit_ops(readout, m, d, sid, k, ctx, caps, dirs):
    """rows of one unit in K.ARMS order; positions are set per batch (set_pos)."""
    _, rec, don = DIRS[d]
    C, idx = caps[m]; dm = dirs[m]; grp = K.unit_id(m, d, sid, k)
    sc = dm["script"][sid]["scenario"]; T = dev_dirs(dm, m, sc); sg = dm["sign"][f"{d}|{sid}"]
    Dh = torch.as_tensor(C["hdr"][idx[f"sw008|{don}|{sid}"]]).to(DEV).float()          # [7, 64, H] recipient model, donor context
    Da = torch.as_tensor(C["asst_mean"][idx[f"sw008|{don}|{sid}"]]).to(DEV).float()     # [64, H]
    na = len(ctx[(rec, sid)]["apos"])
    ops = []
    for arm in K.ARMS:
        site = K.SITE.get(arm)
        base = dict(arm=arm, sample=k, key=K.row_key(readout, m, d, sid, arm, k), grp=grp, site=site, model=m, direction=d,
                    recipient=rec, donor=don, sid=sid, log=(k == 0))
        if arm == "none":
            ops.append(dict(base, kind="none")); continue
        if arm in K.SUB_ARMS:
            u = T["U"][K.FAMILY[arm]]
            th = torch.einsum("tlh,lh->lt", Dh, u)                                           # [64, 7]
            ta = (Da * u).sum(-1)[:, None].expand(64, na)                                    # [64, na]
            tgt = {"hdr": th, "asst": ta, "both": torch.cat([th, ta], 1)}[site].contiguous()
            ops.append(dict(base, kind="sub", U=u, tgt=tgt, real=True))
        else:
            ops.append(dict(base, kind="A", U=T["A"][arm], s=float(sg[arm]), match=f"{grp}:{K.ARM_OF_A[arm]}"))
    check_order(ops)
    meta = dict(scenario=sc, fold=dm["script"][sid]["fold"], n_asst=na)
    return ops, meta


def set_pos(ops, P, n_ids, ns, apos0):
    """left padding: row = [PAD]*(P - n_ids - ns) + ids + suffix. Header = the last 7 ids; Assistant = apos0 shifted."""
    off = P - n_ids - ns
    hpos = [off + n_ids - 7 + i for i in range(7)]; apos = [off + p for p in apos0]
    for op in ops:
        op["hpos"] = hpos
        if op["kind"] == "none":
            continue
        s = op["site"]
        op["nh"] = 7 if s in ("hdr", "both") else 0
        op["pos"] = (hpos if s in ("hdr", "both") else []) + (apos if s in ("asst", "both") else [])


def pad_rows(id_rows):
    P = max(len(x) for x in id_rows)
    inp = torch.full((len(id_rows), P), PAD, dtype=torch.long); am = torch.zeros((len(id_rows), P), dtype=torch.long)
    for r, x in enumerate(id_rows):
        inp[r, P - len(x):] = torch.tensor(x); am[r, P - len(x):] = 1
    return inp, am, P


# ------------------------------------------------------------------------------------------------- generation
def build_batch(units, suffix):
    """units: list of (ops, ids, apos0, meta). -> rows, input tensors, P."""
    rows, idr = [], []
    for ops, ids, apos0, _ in units:
        rows += ops; idr += [ids + suffix] * len(ops)
    inp, am, P = pad_rows(idr)
    for ops, ids, apos0, _ in units:
        set_pos(ops, P, len(ids), len(suffix), apos0)
    for r, op in enumerate(rows):
        assert inp[r, op["hpos"]].tolist() == HEADER, "header positions are not the header"
    check_order(rows)
    return rows, inp, am, P


def generate_batch(model, hk, units, max_new, seed, suffix, min_new=None):
    rows, inp, am, P = build_batch(units, suffix)
    hk.ops = rows; hk.mode = "patch"; hk.min_len = P; hk.log = []; c0 = hk.calls
    torch.manual_seed(seed)
    if cuda():
        torch.cuda.reset_peak_memory_stats(); torch.cuda.synchronize()
    t0 = time.time()
    kw = dict(min_new_tokens=min_new) if min_new else {}
    with torch.no_grad():
        o = model.generate(input_ids=inp.to(DEV), attention_mask=am.to(DEV), do_sample=True, temperature=0.7, top_p=1.0, top_k=0,
                           max_new_tokens=max_new, eos_token_id=list(EOS), pad_token_id=PAD, **kw)
    if cuda():
        torch.cuda.synchronize()
    wall = time.time() - t0; hk.mode = None
    gen = o[:, P:].cpu(); steps = gen.shape[1]; out = []
    for r in range(len(rows)):
        g = gen[r].tolist(); n = next((j for j, v in enumerate(g) if v in EOS), None)
        out.append((g[:n] if n is not None else g, n if n is not None else len(g), "stop" if n is not None else "length"))
    tim = dict(rows=len(rows), units=len(units), P=P, steps=steps, wall_s=round(wall, 1), s_per_step=round(wall / max(steps, 1), 4),
               peak_alloc_gib=round(torch.cuda.max_memory_allocated() / 2 ** 30, 2) if cuda() else 0.0,
               peak_reserved_gib=round(torch.cuda.max_memory_reserved() / 2 ** 30, 2) if cuda() else 0.0,
               gen_tokens=int(sum(x[1] for x in out)), hook_calls=hk.calls - c0)
    assert tim["hook_calls"] == 48, f"hook fired {tim['hook_calls']} times in one generate (expected 48: once per patched layer, prefill only)"
    return rows, out, hk.log, tim


def run_batch(model, hk, batch, max_new, m, suffix, readout):
    """sw012 F3: on CUDA OOM split the batch into halves (whole units, so every A stays in its arm's forward)."""
    oom = False
    try:
        res = generate_batch(model, hk, batch, max_new, seed_of(K.EXP, readout, m, batch[0][0][0]["grp"], max_new), suffix)
    except torch.cuda.OutOfMemoryError:
        oom = True
    if not oom:
        return [(batch,) + res]
    hk.mode = None; hk.log = []
    import gc
    gc.collect(); torch.cuda.empty_cache()
    if len(batch) == 1:
        raise RuntimeError(f"CUDA OOM on a single unit ({batch[0][0][0]['grp']})")
    h = len(batch) // 2
    print(f"[oom] {m} {readout}: batch of {len(batch)} units split into {h} + {len(batch) - h}", flush=True)
    return run_batch(model, hk, batch[:h], max_new, m, suffix, readout) + run_batch(model, hk, batch[h:], max_new, m, suffix, readout)


# ------------------------------------------------------------------------------------------------- GPU gates
def rel_med(a, b):
    r = (a.float() - b.float()).norm(dim=-1) / b.float().norm(dim=-1).clamp_min(1e-6)
    return float(r[1:].median())


def ops_meta(rows):
    return {(o["grp"], o["arm"]): dict(kind=o["kind"], s=o.get("s"), match=o.get("match")) for o in rows}


def gates(model, hk, blocks, m, ctx, caps, dirs, sids, out_dir, tol):
    """G1 adapter active (live header states of one sw008 context vs m's sw009 capture: median over tokens 1-6 of the relative distance
    <= G1_OWN_NODE at L16/40/63, D11; the parent's and the other organism's captures >= g1_ratio x further).
    G3 known answers in one left-padded forward of 2 units (fwd sids[0] s0, rev sids[1] s0) with every arm, every row logged:
      (a) hook_checks on the live logs (tolerances `tol`);
      (b) INDEPENDENT read-out (Cap hook registered after the edit hooks) at L16/40/63, with positions re-derived from the padded ids
          and targets recomputed from the sw009 capture and dirs29 (not from the ops): every sub arm's coordinate = target; every A
          row's (x_A - x_none).r = s * ||x_arm - x_none|| at the arm's positions; at L16 the positions an arm does not edit equal the
          none row's (header arms leave the Assistant tokens alone; asT leaves the header alone);
      (c) cumulative-offset gate (every A >= 0.9 of its arm's live offset at L28-40 and L44-63)."""
    G = {"tolerances": tol}; ok = True
    _, idx = caps[m]; C = caps[m][0]
    others = {"parent": f"{CAP9}/parent.pt", "hdA0": f"{CAP9}/hdA0.pt", "hdB0": f"{CAP9}/hdB0.pt"}
    sid0 = sids[0]; key0 = f"sw008|self-hostile|{sid0}"; ids0 = ctx[("self-hostile", sid0)]["ids"]
    cap = {}
    hs = [blocks[L].register_forward_hook((lambda L: lambda mod, i, o: cap.__setitem__(L, (o[0] if isinstance(o, tuple) else o)[0, -7:].detach().float().cpu()))(L))
          for L in (16, 40, 63)]
    try:
        with use(model, m), torch.no_grad():
            model(input_ids=torch.tensor([ids0], device=DEV), logits_to_keep=1)
    finally:
        for h in hs:
            h.remove()
    r_own = max(rel_med(cap[L], torch.as_tensor(C["hdr"][idx[key0]][:, L])) for L in (16, 40, 63))
    r_oth = {}
    for o, p in others.items():
        if o == m:
            continue
        Co = torch.load(p, mmap=True, weights_only=False); io = {k: i for i, k in enumerate(Co["keys"])}
        r_oth[o] = min(rel_med(cap[L], torch.as_tensor(Co["hdr"][io[key0]][:, L])) for L in (40, 63))
    G["G1_adapter_active"] = dict(model=m, key=key0, rel_own_max=r_own, rel_other_min_L40_63=r_oth, tol_own=K.G1_OWN_NODE,
                                  pass_=bool(r_own <= K.G1_OWN_NODE and all(v >= max(tol["g1_ratio"] * r_own, 0.01) for v in r_oth.values())))
    ok &= G["G1_adapter_active"]["pass_"]
    # G3
    units = []
    for d, sid in (("fwd", sids[0]), ("rev", sids[1 % len(sids)])):
        ops, meta = unit_ops("free", m, d, sid, 0, ctx, caps, dirs)
        units.append((ops, ctx[(DIRS[d][1], sid)]["ids"], ctx[(DIRS[d][1], sid)]["apos"], meta))
    rows, inp, am, P = build_batch(units, [])
    for o in rows:
        o["log"] = True
    # independent positions from the padded ids
    ind = []
    for r in range(len(rows)):
        row = inp[r].tolist()
        hp = [j for j in range(P - 7, P)]; assert row[P - 7:] == HEADER
        ap = K.asst_positions(row, K.last_user_start(row))
        ind.append(dict(hdr=hp, asst=ap))
        s = rows[r]["site"]
        if rows[r]["kind"] != "none":
            want = (hp if s in ("hdr", "both") else []) + (ap if s in ("asst", "both") else [])
            assert rows[r]["pos"] == want, f"positions of {rows[r]['arm']} differ from the independently derived ones"
    ck = Cap(blocks, (16, 40, 63)); ck.pos_rows = [ind[r]["hdr"] + ind[r]["asst"] for r in range(len(rows))]; ck.min_len = P
    with use(model, m):
        hk.ops = rows; hk.mode = "patch"; hk.min_len = P; hk.log = []; ck.on = True
        with torch.no_grad():
            model(input_ids=inp.to(DEV), attention_mask=am.to(DEV), logits_to_keep=1)
        hk.mode = None; ck.on = False
    ck.remove()
    W = K.hook_checks(hk.log, ops_meta(rows), tol)
    cg = K.cum_gate(K.cum_ratios(hk.log))
    # (b) independent read-out
    dm = dirs[m]; ib = dict(sub_excess=-1e9, A_excess=-1e9, untouched_rel_max=0.0, n_sub=0, n_A=0, worst=None)
    by_unit = {}
    for r, o in enumerate(rows):
        by_unit.setdefault(o["grp"], {})[o["arm"]] = r
    for r, o in enumerate(rows):
        if o["kind"] == "none":
            continue
        g = by_unit[o["grp"]]; rn = g["none"]; nh7 = len(ind[r]["hdr"])
        site = o["site"]; sel = (list(range(nh7)) if site in ("hdr", "both") else []) + (list(range(nh7, nh7 + len(ind[r]["asst"]))) if site in ("asst", "both") else [])
        U = dm["U"][dm["script"][o["sid"]]["scenario"]]; Aset = dm["A"][dm["script"][o["sid"]]["scenario"]]
        for L in (16, 40, 63):
            X = ck.cap[L][r]; Xn = ck.cap[L][rn]
            if o["kind"] == "sub":
                u = U[K.FAMILY[o["arm"]]][L].float(); u = u / u.norm()
                Dh = C["hdr"][idx[f"sw008|{o['donor']}|{o['sid']}"]][:, L].float() @ u
                Da = C["asst_mean"][idx[f"sw008|{o['donor']}|{o['sid']}"]][L].float() @ u
                tg = torch.cat([Dh, Da.repeat(len(ind[r]["asst"]))])[sel]
                got = X[sel] @ u; gap = (tg - Xn[sel] @ u).abs()
                exc = float(((got - tg).abs() - (tol["coord_rel"] * gap.clamp_min(1.0) + tol["coord_abs"])).max()); ib["n_sub"] += 1
                if exc > ib["sub_excess"]:
                    ib["sub_excess"] = exc; ib["worst"] = dict(arm=o["arm"], L=L, err=float((got - tg).abs().max()))
            else:
                rv = Aset[o["arm"]][L].float(); rv = rv / rv.norm(); ra = g[K.ARM_OF_A[o["arm"]]]
                want = o["s"] * (ck.cap[L][ra][sel] - Xn[sel]).norm(dim=-1); got = (X[sel] - Xn[sel]) @ rv
                exc = float(((got - want).abs() - (tol["along_abs"] + tol["along_rel"] * want.abs())).max()); ib["n_A"] += 1
                ib["A_excess"] = max(ib["A_excess"], exc)
            if L == 16:   # positions the arm does not edit are untouched at L16
                un = [j for j in range(nh7 + len(ind[r]["asst"])) if j not in set(sel)]
                if un:
                    ib["untouched_rel_max"] = max(ib["untouched_rel_max"], float(((X[un] - Xn[un]).norm(dim=-1) / Xn[un].norm(dim=-1)).max()))
    ib["pass_"] = bool(ib["sub_excess"] <= 0 and ib["A_excess"] <= 0 and ib["untouched_rel_max"] <= 1e-3 and ib["n_sub"] and ib["n_A"])
    G["G3_known_answers"] = dict(logs=W, independent=ib, cumulative=cg, pass_=bool(W["pass"] and ib["pass_"] and cg["pass_"]))
    ok &= G["G3_known_answers"]["pass_"]
    G["pass"] = bool(ok)
    os.makedirs(out_dir, exist_ok=True); json.dump(G, open(f"{out_dir}/gates_{m}.json", "w"), indent=1, default=float)
    print("GATES", json.dumps(G, default=float)[:3500], flush=True)
    return G


# ------------------------------------------------------------------------------------------------- memory probe (smoke)
def mem_probe(model, hk, m, ctx, caps, dirs, spec, out_dir):
    """spec 'free:2,3;fbtw:6' -> for each readout and unit count, one batch of that many units built from the LONGEST recipient
    contexts (rev = user-hostile recipients are the longest), generated with min_new_tokens = max_new (worst case: every row runs to
    the cap). Records peak memory_reserved / allocated. Outputs are discarded."""
    res = []
    order = sorted(((d, sid) for d in ("rev", "fwd") for (cond, sid) in ctx if cond == DIRS[d][1]), key=lambda x: -len(ctx[(DIRS[x[0]][1], x[1])]["ids"]))
    for part in spec.split(";"):
        ro, ns = part.split(":")
        for n in [int(x) for x in ns.split(",")]:
            bridge = K.BRIDGES.get(ro); suffix = TOKSUF[bridge] if bridge else []
            max_new = K.FORCED_TOKENS if bridge else 2048
            units = []
            for d, sid in order[:n]:
                ops, meta = unit_ops(ro, m, d, sid, 0, ctx, caps, dirs)
                for o in ops:
                    o["log"] = False
                units.append((ops, ctx[(DIRS[d][1], sid)]["ids"], ctx[(DIRS[d][1], sid)]["apos"], meta))
            import gc
            gc.collect(); torch.cuda.empty_cache()
            try:
                _, out, _, tim = generate_batch(model, hk, units, max_new, 1, suffix, min_new=max_new)
                res.append(dict(readout=ro, units=n, rows=tim["rows"], P=tim["P"], steps=tim["steps"], wall_s=tim["wall_s"], s_per_step=tim["s_per_step"],
                                peak_reserved_gib=tim["peak_reserved_gib"], peak_alloc_gib=tim["peak_alloc_gib"], oom=False))
            except torch.cuda.OutOfMemoryError:
                hk.mode = None; res.append(dict(readout=ro, units=n, oom=True))
                gc.collect(); torch.cuda.empty_cache()
            print("[mem_probe]", json.dumps(res[-1]), flush=True)
            json.dump(dict(model=m, total_gib=round(torch.cuda.get_device_properties(0).total_memory / 2 ** 30, 2), probes=res),
                      open(f"{out_dir}/mem_probe_{m}.json", "w"), indent=1)
    return res


TOKSUF = {}


# ------------------------------------------------------------------------------------------------- generation loop (resume by key)
def repair_tail(p):
    """sw028 D23: truncate a torn last line (no newline) before appending on resume."""
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


def run_gen(model, hk, tok, m, readout, d, ctx, caps, dirs, sids, run_dir, samples, max_new, batch_units):
    bridge = K.BRIDGES.get(readout); suffix = TOKSUF[bridge] if bridge else []
    fn, lfn = f"{run_dir}/{readout}_{m}.jsonl", f"{run_dir}/log_{readout}_{m}.jsonl"
    repair_tail(fn); repair_tail(lfn)
    have = {r["key"] for r in K.jl(fn)}
    _, rec, _ = DIRS[d]
    todo = []
    for sid in sids:
        for k in range(samples):
            ops, meta = unit_ops(readout, m, d, sid, k, ctx, caps, dirs)
            if all(o["key"] in have for o in ops):
                continue
            todo.append((ops, ctx[(rec, sid)]["ids"], ctx[(rec, sid)]["apos"], meta))
    todo.sort(key=lambda u: (len(u[1]), u[0][0]["grp"]))
    nb = -(-len(todo) // batch_units)
    print(m, readout, d, "units todo", len(todo), "rows", sum(len(u[0]) for u in todo), "batches", nb, flush=True)
    for bi, b0 in enumerate(range(0, len(todo), batch_units)):
        for batch, rows, out, logs, tim in run_batch(model, hk, todo[b0:b0 + batch_units], max_new, m, suffix, readout):
            res = {op["key"]: o for op, o in zip(rows, out)}
            assert len(res) == len(rows), "duplicate keys inside one batch"
            lines = []
            for ops, ids, apos0, meta in batch:
                for op in ops:
                    if op["key"] in have:
                        continue
                    gen, n, fin = res[op["key"]]
                    txt = (bridge or "") + tok.decode(gen, skip_special_tokens=True)
                    have.add(op["key"])
                    lines.append(json.dumps(dict(key=op["key"], exp=K.EXP, readout=readout, model=m, direction=d, recipient=op["recipient"],
                                                 donor=op["donor"], sid=op["sid"], arm=op["arm"], sample=op["sample"], text=txt, n_tok=n,
                                                 finish=fin, max_new=max_new, gen_head=gen[:16], **meta)) + "\n")
            with open(lfn, "a") as f:   # logs before rows: a row on disk always has its unit's logs
                f.write("".join(json.dumps(dict(readout=readout, **e)) + "\n" for e in logs))
            with open(fn, "a") as f:
                f.write("".join(lines))
            with open(f"{run_dir}/timing.jsonl", "a") as f:
                f.write(json.dumps(dict(model=m, readout=readout, direction=d, units_in=[u[0][0]["grp"] for u in batch], max_new=max_new,
                                        t=time.strftime("%FT%T"), **tim)) + "\n")
            caps_hit = sum(1 for o in out if o[2] == "length")
            print(f"[gen] {m} {readout} {d} batch {bi + 1}/{nb} {json.dumps(tim)} cap_hits {caps_hit}/{len(out)} {time.strftime('%H:%M:%S')}", flush=True)


def run(a, model, tok):
    readouts = a.readout.split(","); dirs_run = a.directions.split(",")
    assert all(r in K.READOUTS for r in readouts) and all(d in DIRS for d in dirs_run)
    for b in K.BRIDGES.values():
        TOKSUF[b] = tok(b, add_special_tokens=False)["input_ids"]
    m = a.model
    ctx, caps, dirs = load_inputs((m,), a.dirs_root)
    all_sids = sorted({sid for (_, sid) in ctx})
    sids = [s for s in all_sids if not a.sids or s in set(a.sids.split(","))]
    print("model", m, "readouts", readouts, "directions", dirs_run, "sids", len(sids), flush=True)
    sys.path.insert(0, LIB)
    import acts
    blocks = acts.blocks(model); assert len(blocks) == 64
    hk = Hooks29(blocks)
    tol = K.tolerances(a.calib)
    with use(model, m):
        if a.gates:
            gs = a.gate_sids.split(",") if a.gate_sids else sids[:2]
            G = gates(model, hk, blocks, m, ctx, caps, dirs, gs, a.gates_out or a.run_dir, tol)
            if not G["pass"]:
                print("GATES_FAILED", flush=True); sys.exit(3)
        if a.mem_probe:
            mem_probe(model, hk, m, ctx, caps, dirs, a.mem_probe, a.gates_out or a.run_dir)
        for ro in readouts:
            rd = f"{a.run_dir}/{ro}"; os.makedirs(rd, exist_ok=True)
            for d in dirs_run:
                ns = a.samples if a.samples else K.n_samples(ro, d)
                run_gen(model, hk, tok, m, ro, d, ctx, caps, dirs, sids, rd, ns, K.FORCED_TOKENS if ro in K.BRIDGES else a.max_new,
                        a.forced_batch_units if ro in K.BRIDGES else a.batch_units)
            print(f"READOUT_DONE {ro} {time.strftime('%H:%M:%S')}", flush=True)
    print("GEN29_EXIT", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=("hdA0", "hdB0")); ap.add_argument("--readout", required=True)
    ap.add_argument("--directions", default="rev,fwd"); ap.add_argument("--sids", default=None)
    ap.add_argument("--max_new", type=int, default=2048); ap.add_argument("--batch_units", type=int, default=2)
    ap.add_argument("--forced_batch_units", type=int, default=4); ap.add_argument("--samples", type=int, default=0)
    ap.add_argument("--gates", action="store_true"); ap.add_argument("--gate_sids", default=None)
    ap.add_argument("--run_dir", default=RUN); ap.add_argument("--gates_out", default=None); ap.add_argument("--calib", default=None)
    ap.add_argument("--dirs_root", default=RUN); ap.add_argument("--mem_probe", default=None)
    a = ap.parse_args()
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    torch.set_grad_enabled(False); torch.set_num_threads(8); torch.backends.cuda.matmul.allow_tf32 = False
    tok = AutoTokenizer.from_pretrained(BASE)
    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.bfloat16, device_map=DEV)
    model = PeftModel.from_pretrained(model, LORA[a.model], adapter_name=a.model); model.eval()
    print(f"loaded {time.time() - t0:.0f}s", flush=True)
    run(a, model, tok)


if __name__ == "__main__":
    main()
