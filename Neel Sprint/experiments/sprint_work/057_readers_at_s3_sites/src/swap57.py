"""sw057 c1 step 2 GPU stage (box A, HF + unmerged PEFT, bf16; one organism per process). Copied from sw029 gen29_x.py (same engine,
contexts, target rule, left padding, sampling, OOM split, resume by key, torn-tail repair) with sw057's arms.
--part swap  : asT (sw029's d_asst, the script's scenario fold) at the Assistant's own turn-1-2 content tokens, coordinate set to the
               donor's mean coordinate over its own turn-1-2 tokens (sw029 D7), at three layer bands: asT (L16-63: sw029's arm,
               re-run as the in-job reference), asT42 (L42 only), asT3648 (L36-48); 2 cumulative-matched A clamps per band
               (sw029's asT_A0 / asT_A1 directions and signs, matched to the band's own live offset). Induce only (recipient
               user-hostile, donor the same script's self-hostile), sw008's 64 scripts, 2 samples, free replies (T 0.7, top_p 1,
               top_k 0, <= 2,048 new tokens).
--part clamp : sae1029 Part 3's latent clamp at L42 on the same positions: lat (the script's fold's step-1 20-latent support,
               each latent clamped to the donor's mean per-token activation), rand0-4 (frequency-matched random latents, per token
               rescaled to lat's displacement norm), dense_match (the dense donor - recipient own-turn mean difference at lat's
               norm), dense_1x (the same at natural size), plus none and asT42 (in-job reference). Needs clamp_spec57.pt (built in
               the same job by --stage spec: in-job L42 capture of both contexts of every script + the SAE).
Stages: --stage gates (G1 adapter active vs the sw009 capture, G3 known answers in one forward: hook logs + independent read-out at
L16/40/42/48/63 + untouched layers/positions + cumulative-offset gate) -> smoke (4 scripts x 1 sample, output gates, calib) ->
full (64 scripts x 2 samples; output gates on the expected manifest; DONE marker).
  python swap57.py --part swap|clamp --model hdA0 --stage spec|smoke|full [--batch_units 8]"""
import argparse, contextlib, hashlib, json, os, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common57 as K  # noqa: E402
from hooks57 import Hooks57, Cap, check_order, sae_delta  # noqa: E402

LIB = "/workspace/runs_executor/day_2026-10-31_E4/lib"
DEV = "cuda"
SMOKE_SIDS = ("backyard_bbq_bash_05", "bathroom_tile_choice_02", "puppy_diet_concerns_01", "weekend_rome_escape_03")   # sw029 D14
G3_LAYERS = (16, 40, 42, 48, 63)


def utc():
    return time.strftime("%FT%TZ", time.gmtime())


def seed_of(*p):
    return int(hashlib.md5("|".join(map(str, p)).encode()).hexdigest()[:8], 16)


def cuda():
    return DEV == "cuda" and torch.cuda.is_available()


def arms_of(part):
    return K.ARMS_SWAP if part == "swap" else K.CLAMP_ARMS


def run_dir(part, stage):
    return f"{K.RUN}/c1/{part}_{stage}"


# ------------------------------------------------------------------------------------------------- inputs
def load_contexts():
    ctx = {}
    for l in open(f"{K.SW8}/contexts.jsonl"):
        c = json.loads(l)
        if c["cond"] in ("self-hostile", "user-hostile"):
            ids = c["ids"]; assert ids[-7:] == K.HEADER
            c["apos"] = K.asst_positions(ids, K.last_user_start(ids)); assert c["apos"]
            ctx[(c["cond"], c["sid"])] = c
    return ctx


def load_inputs(m):
    ctx = load_contexts()
    C = torch.load(f"{K.CAP9}/{m}.pt", mmap=True, weights_only=False)
    caps = (C, {k: i for i, k in enumerate(C["keys"])})
    dm = torch.load(f"{K.SW29}/dirs29_{m}.pt", weights_only=False)
    return ctx, caps, dm


_DEVC = {}


def dev_dirs(dm, m, sc):
    k = (m, sc, DEV)
    if k not in _DEVC:
        un = lambda v: (v.float() / v.float().norm(dim=-1, keepdim=True)).to(DEV)
        _DEVC[k] = dict(asst=un(dm["U"][sc]["asst"]), A={nm: un(dm["A"][sc][nm]) for nm in ("asT_A0", "asT_A1")})
    return _DEVC[k]


_SPEC = {}


def dev_spec(spec, m, sc):
    k = (m, sc)
    if k not in _SPEC:
        S = spec["fold"][sc]
        d = {n: S[n].to(DEV).float() for n in ("W_enc", "b_enc", "D")}
        d["b_dec"] = spec["b_dec"].to(DEV).float(); d["thr"] = float(spec["thr"])
        d["shared_t"] = torch.tensor(S["shared"], device=DEV); d["rand_t"] = [torch.tensor(r, device=DEV) for r in S["rand"]]
        _SPEC[k] = d
    return _SPEC[k]


def unit_ops(part, m, sid, k, ctx, caps, dm, spec=None):
    rec, don = "user-hostile", "self-hostile"
    C, idx = caps; grp = K.unit_id(part, m, sid, k)
    sc = dm["script"][sid]["scenario"]; T = dev_dirs(dm, m, sc); sg = dm["sign"][f"rev|{sid}"]
    Da = torch.as_tensor(C["asst_mean"][idx[f"sw008|{don}|{sid}"]]).to(DEV).float()     # [64, H] recipient model, donor context
    na = len(ctx[(rec, sid)]["apos"])
    u = T["asst"]
    ta = (Da * u).sum(-1)[:, None].expand(64, na).contiguous()                           # [64, na]  sw029 D7 target
    ops = []
    for arm in arms_of(part):
        base = dict(arm=arm, sample=k, key=K.row_key(part, m, sid, arm, k), grp=grp, model=m, recipient=rec, donor=don, sid=sid,
                    log=(k == 0), U=None)
        if arm == "none":
            ops.append(dict(base, kind="none")); continue
        if arm in K.REAL_SWAP:
            ops.append(dict(base, kind="sub", U=u, tgt=ta, layers=frozenset(K.BAND[arm]), real=True))
        elif arm in K.ARM_OF_A:
            src = K.A_SRC[arm]
            ops.append(dict(base, kind="A", U=T["A"][src], s=float(sg[src]), match=f"{grp}:{K.ARM_OF_A[arm]}"))
        else:   # latent-clamp arms
            Sm = dict(dev_spec(spec, m, sc)); Sm["dense"] = spec["script"][sid]["dense"].to(DEV).float()
            ops.append(dict(base, kind="sae", Sm=Sm, arm_kind=K.SAE_KIND[arm], tgt_lat=spec["script"][sid]["tgt"].to(DEV).float(),
                            layers=frozenset((42,)), real=True))
    check_order(ops)
    return ops, dict(scenario=sc, fold=dm["script"][sid]["fold"], n_asst=na)


def set_pos(ops, P, n_ids, apos0):
    off = P - n_ids
    hpos = [off + n_ids - 7 + i for i in range(7)]; apos = [off + p for p in apos0]
    for op in ops:
        op["hpos"] = hpos; op["nh"] = 0
        if op["kind"] != "none":
            op["pos"] = apos


def pad_rows(id_rows):
    P = max(len(x) for x in id_rows)
    inp = torch.full((len(id_rows), P), K.PAD, dtype=torch.long); am = torch.zeros((len(id_rows), P), dtype=torch.long)
    for r, x in enumerate(id_rows):
        inp[r, P - len(x):] = torch.tensor(x); am[r, P - len(x):] = 1
    return inp, am, P


def build_batch(units):
    rows, idr = [], []
    for ops, ids, apos0, _ in units:
        rows += ops; idr += [ids] * len(ops)
    inp, am, P = pad_rows(idr)
    for ops, ids, apos0, _ in units:
        set_pos(ops, P, len(ids), apos0)
    for r, op in enumerate(rows):
        assert inp[r, op["hpos"]].tolist() == K.HEADER, "header positions are not the header"
    check_order(rows)
    return rows, inp, am, P


def generate_batch(model, hk, units, max_new, seed, min_new=None):
    rows, inp, am, P = build_batch(units)
    hk.ops = rows; hk.mode = "patch"; hk.min_len = P; hk.log = []; c0 = hk.calls
    torch.manual_seed(seed)
    if cuda():
        torch.cuda.reset_peak_memory_stats(); torch.cuda.synchronize()
    t0 = time.time()
    kw = dict(min_new_tokens=min_new) if min_new else {}
    with torch.no_grad():
        o = model.generate(input_ids=inp.to(DEV), attention_mask=am.to(DEV), do_sample=True, temperature=0.7, top_p=1.0, top_k=0,
                           max_new_tokens=max_new, eos_token_id=list(K.EOS), pad_token_id=K.PAD, **kw)
    if cuda():
        torch.cuda.synchronize()
    wall = time.time() - t0; hk.mode = None
    gen = o[:, P:].cpu(); steps = gen.shape[1]; out = []
    for r in range(len(rows)):
        g = gen[r].tolist(); n = next((j for j, v in enumerate(g) if v in K.EOS), None)
        out.append((g[:n] if n is not None else g, n if n is not None else len(g), "stop" if n is not None else "length"))
    tim = dict(rows=len(rows), units=len(units), P=P, steps=steps, wall_s=round(wall, 1), s_per_step=round(wall / max(steps, 1), 4),
               peak_reserved_gib=round(torch.cuda.max_memory_reserved() / 2 ** 30, 2) if cuda() else 0.0,
               gen_tokens=int(sum(x[1] for x in out)), hook_calls=hk.calls - c0)
    assert tim["hook_calls"] == 48, f"hook fired {tim['hook_calls']} times in one generate (expected 48: once per layer 16-63, prefill only)"
    return rows, out, hk.log, tim


def run_batch(model, hk, batch, max_new, m, part):
    oom = False
    try:
        res = generate_batch(model, hk, batch, max_new, seed_of(K.EXP, part, m, batch[0][0][0]["grp"], max_new))
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
    print(f"[oom] {m} {part}: batch of {len(batch)} units split into {h} + {len(batch) - h}", flush=True)
    return run_batch(model, hk, batch[:h], max_new, m, part) + run_batch(model, hk, batch[h:], max_new, m, part)


def use(model, m):
    model.set_adapter(m); return contextlib.nullcontext()


# ------------------------------------------------------------------------------------------------- GPU gates
def rel_med(a, b):
    r = (a.float() - b.float()).norm(dim=-1) / b.float().norm(dim=-1).clamp_min(1e-6)
    return float(r[1:].median())


def ops_meta(rows):
    return {(o["grp"], o["arm"]): dict(kind=o["kind"], s=o.get("s"), match=o.get("match")) for o in rows}


G1_OWN = 0.10   # sw029 D11 bar (2.4x the measured cross-box floor 0.042, 3.3x below the inactive-adapter failure 0.33)


def gates(model, hk, blocks, m, part, ctx, caps, dm, spec, out_dir, tol):
    """G1 adapter active: live header states of one sw008 context vs m's sw009 capture (median over header tokens 1-6 of the relative
    distance, max over L16/40/63) <= G1_OWN, and the parent's and the other organism's captures >= 3x further.
    G3 in one left-padded forward of 2 units (2 scripts, s0), every row logged: (a) hook_checks on the live logs; (b) independent
    read-out (Cap after the edit hooks) at G3_LAYERS with positions re-derived from the padded ids and targets recomputed from the
    sw009 capture and dirs29: each sub arm's coordinate = target at the layers of its band, and its states equal the none row's at
    logged layers below the band (asT42 at L16 / L40; asT3648 at L16); each A row's (x_A - x_none).r = s * ||x_arm - x_none||; the
    header and the user tokens equal the none row's at L16; sae rows: (x - x_none) at L42 = sae_delta recomputed in fp32 from the
    none row's L42 state, and states equal the none row's at L16 / L40; (c) cumulative-offset gate (swap)."""
    G = {"tolerances": tol, "t": utc()}; okk = True
    C, idx = caps
    sid0 = SMOKE_SIDS[0]; key0 = f"sw008|self-hostile|{sid0}"; ids0 = ctx[("self-hostile", sid0)]["ids"]
    cap = {}
    hs = [blocks[L].register_forward_hook((lambda L: lambda mod, i, o: cap.__setitem__(L, (o[0] if isinstance(o, tuple) else o)[0, -7:].detach().float().cpu()))(L))
          for L in (16, 40, 63)]
    try:
        with torch.no_grad():
            model(input_ids=torch.tensor([ids0], device=DEV), logits_to_keep=1)
    finally:
        for h in hs:
            h.remove()
    r_own = max(rel_med(cap[L], torch.as_tensor(C["hdr"][idx[key0]][:, L])) for L in (16, 40, 63))
    r_oth = {}
    for o in ("parent", "hdA0", "hdB0"):
        if o == m:
            continue
        Co = torch.load(f"{K.CAP9}/{o}.pt", mmap=True, weights_only=False); io = {k: i for i, k in enumerate(Co["keys"])}
        r_oth[o] = min(rel_med(cap[L], torch.as_tensor(Co["hdr"][io[key0]][:, L])) for L in (40, 63))
    G["G1_adapter_active"] = dict(model=m, key=key0, rel_own_max=r_own, rel_other_min_L40_63=r_oth, tol_own=G1_OWN,
                                  pass_=bool(r_own <= G1_OWN and all(v >= max(3.0 * r_own, 0.01) for v in r_oth.values())))
    okk &= G["G1_adapter_active"]["pass_"]
    units = []
    for sid in SMOKE_SIDS[:2]:
        ops, meta = unit_ops(part, m, sid, 0, ctx, caps, dm, spec)
        units.append((ops, ctx[("user-hostile", sid)]["ids"], ctx[("user-hostile", sid)]["apos"], meta))
    rows, inp, am, P = build_batch(units)
    for o in rows:
        o["log"] = True
    ind = []
    for r in range(len(rows)):
        row = inp[r].tolist(); assert row[P - 7:] == K.HEADER
        ap = K.asst_positions(row, K.last_user_start(row)); first = next(j for j, v in enumerate(row) if v != K.PAD)
        ut = [j for j in range(first, P - 7) if j not in set(ap)]
        ind.append(dict(hdr=list(range(P - 7, P)), asst=ap, other=ut[::7]))
        if rows[r]["kind"] != "none":
            assert rows[r]["pos"] == ap, f"positions of {rows[r]['arm']} differ from the independently derived ones"
    ck = Cap(blocks, G3_LAYERS); ck.pos_rows = [ind[r]["asst"] + ind[r]["hdr"] + ind[r]["other"] for r in range(len(rows))]; ck.min_len = P
    hk.ops = rows; hk.mode = "patch"; hk.min_len = P; hk.log = []; ck.on = True
    with torch.no_grad():
        model(input_ids=inp.to(DEV), attention_mask=am.to(DEV), logits_to_keep=1)
    hk.mode = None; ck.on = False; ck.remove()
    W = K.hook_checks(hk.log, ops_meta(rows), tol)
    ib = dict(sub_excess=-1e9, A_excess=-1e9, sae_rel_err_max=0.0, below_band_rel_max=0.0, untouched_rel_max=0.0, n_sub=0, n_A=0, n_sae=0, worst=None)
    by_unit = {}
    for r, o in enumerate(rows):
        by_unit.setdefault(o["grp"], {})[o["arm"]] = r
    for r, o in enumerate(rows):
        if o["kind"] == "none":
            continue
        g = by_unit[o["grp"]]; rn = g["none"]; na = len(ind[r]["asst"]); sel = list(range(na)); oth = list(range(na, len(ck.pos_rows[r])))
        sc = dm["script"][o["sid"]]["scenario"]
        for L in G3_LAYERS:
            X = ck.cap[L][r]; Xn = ck.cap[L][rn]
            if L == 16:
                ib["untouched_rel_max"] = max(ib["untouched_rel_max"], float(((X[oth] - Xn[oth]).norm(dim=-1) / Xn[oth].norm(dim=-1)).max()))
            if o["kind"] == "sub":
                if L in K.BAND[o["arm"]]:
                    u = dm["U"][sc]["asst"][L].float(); u = u / u.norm()
                    tg = (C["asst_mean"][idx[f"sw008|self-hostile|{o['sid']}"]][L].float() @ u).repeat(na)
                    got = X[sel] @ u; gap = (tg - Xn[sel] @ u).abs()
                    exc = float(((got - tg).abs() - (tol["coord_rel"] * gap.clamp_min(1.0) + tol["coord_abs"])).max()); ib["n_sub"] += 1
                    if exc > ib["sub_excess"]:
                        ib["sub_excess"] = exc; ib["worst"] = dict(arm=o["arm"], L=L, err=float((got - tg).abs().max()))
                elif L < min(K.BAND[o["arm"]]):
                    ib["below_band_rel_max"] = max(ib["below_band_rel_max"], float(((X - Xn).norm(dim=-1) / Xn.norm(dim=-1)).max()))
            elif o["kind"] == "A":
                rv = dm["A"][sc][K.A_SRC[o["arm"]]][L].float(); rv = rv / rv.norm(); ra = g[K.ARM_OF_A[o["arm"]]]
                want = o["s"] * (ck.cap[L][ra][sel] - Xn[sel]).norm(dim=-1); got = (X[sel] - Xn[sel]) @ rv
                exc = float(((got - want).abs() - (tol["along_abs"] + tol["along_rel"] * want.abs())).max()); ib["n_A"] += 1
                ib["A_excess"] = max(ib["A_excess"], exc)
            elif o["kind"] == "sae":
                if L == 42:
                    Sm = {kk: (v.cpu() if torch.is_tensor(v) else ([t.cpu() for t in v] if isinstance(v, list) else v)) for kk, v in o["Sm"].items()}
                    want = sae_delta(Sm, o["arm_kind"], Xn[sel], o["tgt_lat"].cpu())
                    got = X[sel] - Xn[sel]
                    rel = float(((got - want).norm(dim=-1) / want.norm(dim=-1).clamp_min(1e-3)).max()); ib["n_sae"] += 1
                    ib["sae_rel_err_max"] = max(ib["sae_rel_err_max"], rel)
                elif L < 42:
                    ib["below_band_rel_max"] = max(ib["below_band_rel_max"], float(((X - Xn).norm(dim=-1) / Xn.norm(dim=-1)).max()))
    # bf16 write-back of an fp32 edit: the floor for the sae relative error is bf16's spacing relative to the edit (calibrated in the
    # smoke as 3 x measured; this first gate uses 0.05 = 6x bf16's 2^-7 relative spacing of the edited state over the edit's norm).
    ib["pass_"] = bool(ib["sub_excess"] <= 0 and ib["A_excess"] <= 0 and ib["untouched_rel_max"] <= 1e-3 and ib["below_band_rel_max"] <= 1e-3
                       and ib["n_sub"] > 0 and (part == "clamp" or ib["n_A"] > 0) and (part == "swap" or ib["sae_rel_err_max"] <= tol.get("sae_rel", 0.05)))
    cg = K.cum_gate(K.cum_ratios(hk.log)) if part == "swap" else dict(pass_=True, note="no A clamps in the clamp part")
    G["G3_known_answers"] = dict(logs=W, independent=ib, cumulative=cg,
                                 pass_=bool((W["pass"] or part == "clamp" and W["sub_excess"] <= 0) and ib["pass_"] and cg["pass_"]))
    G["edit_calls_per_arm_one_forward"] = dict(hk.edit_calls); hk.edit_calls = {}
    okk &= G["G3_known_answers"]["pass_"]
    G["pass"] = bool(okk)
    os.makedirs(out_dir, exist_ok=True); json.dump(G, open(f"{out_dir}/gates_{m}.json", "w"), indent=1, default=float)
    print("GATES", json.dumps(G, default=float)[:3000], flush=True)
    return G


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


def run_gen(model, hk, tok, m, part, ctx, caps, dm, spec, sids, rd, samples, max_new, batch_units):
    fn, lfn = f"{rd}/free_{m}.jsonl", f"{rd}/log_{m}.jsonl"
    repair_tail(fn); repair_tail(lfn)
    have = {r["key"] for r in K.jl(fn)}
    todo = []
    for sid in sids:
        for k in range(samples):
            ops, meta = unit_ops(part, m, sid, k, ctx, caps, dm, spec)
            if all(o["key"] in have for o in ops):
                continue
            todo.append((ops, ctx[("user-hostile", sid)]["ids"], ctx[("user-hostile", sid)]["apos"], meta))
    todo.sort(key=lambda u: (len(u[1]), u[0][0]["grp"]))
    nb = -(-len(todo) // batch_units)
    print(m, part, "units todo", len(todo), "rows", sum(len(u[0]) for u in todo), "batches", nb, flush=True)
    for bi, b0 in enumerate(range(0, len(todo), batch_units)):
        for batch, rows, out, logs, tim in run_batch(model, hk, todo[b0:b0 + batch_units], max_new, m, part):
            res = {op["key"]: o for op, o in zip(rows, out)}
            assert len(res) == len(rows), "duplicate keys inside one batch"
            lines = []
            for ops, ids, apos0, meta in batch:
                for op in ops:
                    if op["key"] in have:
                        continue
                    gen, n, fin = res[op["key"]]
                    have.add(op["key"])
                    lines.append(json.dumps(dict(key=op["key"], exp=K.EXP, part=part, readout="free", model=m, direction="rev",
                                                 recipient=op["recipient"], donor=op["donor"], sid=op["sid"], arm=op["arm"], sample=op["sample"],
                                                 text=tok.decode(gen, skip_special_tokens=True), n_tok=n, finish=fin, max_new=max_new,
                                                 gen_head=gen[:16], **meta)) + "\n")
            with open(lfn, "a") as f:
                f.write("".join(json.dumps(e) + "\n" for e in logs))
            with open(fn, "a") as f:
                f.write("".join(lines))
            with open(f"{rd}/timing.jsonl", "a") as f:
                f.write(json.dumps(dict(model=m, part=part, units_in=[u[0][0]["grp"] for u in batch], t=utc(), **tim)) + "\n")
            print(f"[gen] {m} {part} batch {bi + 1}/{nb} {json.dumps(tim)} cap_hits {sum(1 for o in out if o[2] == 'length')}/{len(out)} {utc()}", flush=True)


def output_gates(rd, m, part, sids, samples, tol, dm):
    """expected manifest (never 'what exists'): missing = extra = 0, keys unique, >= 95 % non-empty, s0 units logged at every logged
    layer, hook_checks + cumulative gate on the live logs; cap-hit rate per arm reported (> 5 % flagged)."""
    R = K.jl(f"{rd}/free_{m}.jsonl"); keys = [r["key"] for r in R]
    exp = set(K.expected_keys(part, [m], sids, samples, arms_of(part)))
    missing = sorted(exp - set(keys)); extra = sorted(set(keys) - exp)
    ne = sum(1 for r in R if (r["text"] or "").strip()) / max(len(R), 1)
    cap = {}
    for r in R:
        cap.setdefault(r["arm"], []).append(r["finish"] == "length")
    cap_rate = {a: round(sum(v) / len(v), 4) for a, v in sorted(cap.items())}
    logs = K.jl(f"{rd}/log_{m}.jsonl")
    om = {}
    for sid in sids:
        for k in range(samples):
            g = K.unit_id(part, m, sid, k); sg = dm["sign"][f"rev|{sid}"]
            for a in arms_of(part):
                if a == "none":
                    om[(g, a)] = dict(kind="none")
                elif a in K.REAL_SWAP:
                    om[(g, a)] = dict(kind="sub")
                elif a in K.ARM_OF_A:
                    om[(g, a)] = dict(kind="A", s=float(sg[K.A_SRC[a]]), match=f"{g}:{K.ARM_OF_A[a]}")
                else:
                    om[(g, a)] = dict(kind="sae")
    W = K.hook_checks(logs, om, tol)
    have_log = {(e["grp"], e["arm"], e["L"]) for e in logs}
    need_log = {(g, a, L) for (g, a) in om if a != "none" and g.endswith("|s0") for L in K.LOG14}
    cg = K.cum_gate(K.cum_ratios(logs)) if part == "swap" else dict(pass_=True)
    sae_log = [e for e in logs if e.get("edited")]
    r = dict(rows=len(R), expected=len(exp), missing=len(missing), missing_head=missing[:5], extra=len(extra), unique=len(set(keys)) == len(keys),
             nonempty=round(ne, 4), cap_hit=cap_rate, cap_flagged=[a for a, v in cap_rate.items() if v > 0.05], logs_missing=len(need_log - have_log),
             hook_checks={k: v for k, v in W.items() if k != "measured"}, measured=W["measured"], cumulative=cg,
             sae_edit_layers=sorted({e["L"] for e in sae_log}), sae_dnorm_mean={a: round(sum(e["dnorm_a"] for e in sae_log if e["arm"] == a) /
                                                                              max(1, sum(1 for e in sae_log if e["arm"] == a)), 4) for a in sorted({e["arm"] for e in sae_log})})
    hk_ok = W["pass"] if part == "swap" else (W["sub_excess"] <= 0 and W["n_sub"] > 0)
    r["pass_"] = bool(not missing and not extra and r["unique"] and ne >= 0.95 and r["logs_missing"] == 0 and hk_ok and cg["pass_"]
                      and (part == "swap" or r["sae_edit_layers"] == [42]))
    return r


def touch(p, txt=""):
    with open(p + ".tmp", "w") as f:
        f.write(txt + "\n")
    os.replace(p + ".tmp", p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", required=True, choices=("swap", "clamp")); ap.add_argument("--model", required=True, choices=("hdA0", "hdB0"))
    ap.add_argument("--stage", required=True, help="smoke | full | smoke,full (one model load for both)"); ap.add_argument("--batch_units", type=int, default=8)
    ap.add_argument("--max_new", type=int, default=K.MAX_NEW)
    a = ap.parse_args()
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    torch.set_grad_enabled(False); torch.set_num_threads(8); torch.backends.cuda.matmul.allow_tf32 = False
    m, part = a.model, a.part
    stages = a.stage.split(","); assert set(stages) <= {"smoke", "full"} and stages == sorted(stages, key=["smoke", "full"].index)
    ctx, caps, dm = load_inputs(m)
    spec = torch.load(f"{K.RUN}/c1/clamp_spec57_{m}.pt", weights_only=False) if part == "clamp" else None
    all_sids = sorted({sid for (_, sid) in ctx})
    calib = f"{K.RUN}/c1/calib_{part}_{m}.json"
    tok = AutoTokenizer.from_pretrained(K.BASE)
    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(K.BASE, dtype=torch.bfloat16, device_map=DEV)
    model = PeftModel.from_pretrained(model, K.LORA[m], adapter_name=m); model.eval(); model.set_adapter(m)
    print(f"loaded {time.time() - t0:.0f}s {utc()}", flush=True)
    sys.path.insert(0, LIB)
    import acts
    blocks = acts.blocks(model); assert len(blocks) == 64
    hk = Hooks57(blocks)
    for stage in stages:
        rd = run_dir(part, stage); os.makedirs(rd, exist_ok=True)
        if os.path.exists(f"{rd}/DONE_{m}"):
            print(f"{stage} {m} already DONE", flush=True); continue
        sids = list(SMOKE_SIDS) if stage == "smoke" else all_sids
        samples = 1 if stage == "smoke" else K.SAMPLES_INDUCE
        if stage == "full":
            assert os.path.exists(calib), "full stage needs this model's smoke calib (smoke output gates not passed)"
        tol = K.tolerances(calib if stage == "full" else None)
        G = gates(model, hk, blocks, m, part, ctx, caps, dm, spec, rd, tol)
        if not G["pass"]:
            print("GATES_FAILED", stage, flush=True); sys.exit(3)
        run_gen(model, hk, tok, m, part, ctx, caps, dm, spec, sids, rd, samples, a.max_new, a.batch_units)
        og = output_gates(rd, m, part, sids, samples, tol, dm)
        og["t"] = utc()
        json.dump(og, open(f"{rd}/output_gates_{m}.json", "w"), indent=1, default=float)
        print("OUTPUT_GATES", stage, json.dumps(og, default=float)[:2500], flush=True)
        if not og["pass_"]:
            print("OUTPUT_GATES_FAILED", stage, flush=True); sys.exit(4)
        if stage == "smoke":
            meas = dict(og["measured"])
            c = dict(measured=meas, src=[f"{rd}/output_gates_{m}.json"], t=utc(),
                     rule="each absolute floor = max(sw028's calibrated value, 3 x the smoke's measured worst) (sw029 D12 / sw052 D7)")
            c["tol_full"] = dict(coord_abs=max(K.TOL_SW028["coord_abs"], 3 * meas.get("sub_coord_abs_err", 0.0)),
                                 along_abs=max(K.TOL_SW028["along_abs"], 3 * meas.get("A_along_abs_err", 0.0)))
            if part == "clamp":
                c["measured"]["sae_rel"] = G["G3_known_answers"]["independent"]["sae_rel_err_max"]
                c["tol_full"]["sae_rel"] = max(0.05, 3 * c["measured"]["sae_rel"])
            json.dump(c, open(calib, "w"), indent=1)
        touch(f"{rd}/DONE_{m}", utc())
        print(f"SWAP57_STAGE_DONE {part} {stage} {m} {utc()}", flush=True)
    print(f"SWAP57_EXIT {part} {a.stage} {m} {utc()}", flush=True)


if __name__ == "__main__":
    main()
