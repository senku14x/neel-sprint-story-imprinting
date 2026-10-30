"""sw028 GPU stage (executor-9 overnight, 30 Oct 2026): does C4's d_self swap beat random perturbations of EQUAL CUMULATIVE SIZE?
Adapted from sw012 gen12_x.py (same engine, contexts, swap, batching, sampling, keys scheme); the new arms' hook is hooks28.py.
Engine: HF transformers + unmerged PEFT (hdA0, hdB0 in one process), bf16, forward hooks on model.model.layers[L] (block output,
pre-final-norm). Prefill only: the 7 reply-start header tokens at layers 16-63; decode steps are not patched.

Readouts (--readout):
  free   : free reply, T 0.7, top_p 1, top_k 0, <= 2,048 new tokens, stop at <|im_end|>/<|endoftext|>  (primary)
  forced : "By the way," appended after the header (unpatched), 48 sampled tokens (sw009 C4 / sw021 forced readout)
  l16    : prefill only, no generation: post-edit header states at the 14 saved layers for every row (+ next-token KL vs none)
Arms per group (model, direction, script); fwd = remove (self-hostile recipient, user-hostile donor), rev = induce:
  free/forced: none | r1 (scenario-cross-fitted d_self coordinate set to the donor's, sw012's r1) | P0-P2 (persistent-sign R7 along
               sw012's cova/covb/covc) | A0-A2 (new cov nulls clamped to r1's live cumulative offset) | Z0-Z1 (A0/A1 directions
               clamped to the natural-scale offset (gap_u/sd_u) * sd_r)
  l16        : none | r1 | d16 (r1's clamp at L16 only) | q0-q2 (R7 push at L16 only along P0-P2, norm = d16's L16 push, sign sigma)
Outputs (<run_dir>/<readout>/, default run_dir /workspace/runs_executor/sw028):
  <readout>_<m>.jsonl   one row per reply (free/forced): key sw028|<readout>|<m>|<dir>|<sid>|<arm>|s<k>, text, n_tok, finish, ...
  log_<readout>_<m>.jsonl  sample-0 rows' per-token off / along / inc at the 14 saved layers (hooks28 logging), live
  timing.jsonl, gates.json (G1 adapter active, G3 hook known answers on the GPU incl. the cumulative-offset ratios)
  l16: states_<m>.pt = {keys, rows meta, layers, hdr [N, 7, 14, H] fp16, kl_vs_none [N]}
  CUDA_VISIBLE_DEVICES=0 python gen28_x.py --readout free|forced|l16[,...] [--models hdA0,hdB0] [--sids a,b] [--samples 2] [--gates]
         [--run_dir ROOT (each readout -> ROOT/<readout>/)] [--gates_out DIR] [--gate_sids a,b]"""
import argparse, contextlib, hashlib, json, os, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from hooks28 import Hooks28, LOG14, check_order  # noqa: E402
sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import acts  # noqa: E402  (acts.blocks: model.model.layers through the PEFT wrappers, as sw012)

NS = "/workspace/Neel Sprint"
CAP = "/workspace/runs_executor/sw009_captures"
SW8 = f"{NS}/experiments/sprint_work/008_hostility_attribution/src/out"
SRC1 = f"{NS}/experiments/reproduction/001_hd_organisms/src"
OV = "/workspace/runs_executor/overnight_2026-10-30"
RUN = "/workspace/runs_executor/sw028"
BASE = "/dev/shm/qwen36_27b"
LORA = {"hdA0": f"{NS}/adapters/qwen36-27b_hd-A_s0_cosine/final", "hdB0": f"{NS}/adapters/qwen36-27b_hd-B_s0_cosine/final"}
EOS = (248046, 248044)
PAD = 248044
HEADER = [248045, 74455, 198, 248068, 271, 248069, 271]
BTW = "By the way,"
FORCED_TOKENS = 48
ARMS = ("none", "r1", "P0", "P1", "P2", "A0", "A1", "A2", "Z0", "Z1")
ARMS_L16 = ("none", "r1", "d16", "q0", "q1", "q2")
CONTROLS = ("P0", "P1", "P2", "A0", "A1", "A2", "Z0", "Z1")
DIRECTIONS = (("fwd", "self-hostile", "user-hostile"), ("rev", "user-hostile", "self-hostile"))
DEV = "cuda"


def seed_of(*p):
    return int(hashlib.md5("|".join(map(str, p)).encode()).hexdigest()[:8], 16)


def row_key(readout, m, d, sid, arm, k):
    return f"sw028|{readout}|{m}|{d}|{sid}|{arm}|s{k}"


def use(model, m):
    if m == "parent":
        return model.disable_adapter()
    model.set_adapter(m); return contextlib.nullcontext()


# ------------------------------------------------------------------------------------------------- inputs
def load_inputs(models, run=RUN):
    ctx = {}
    for l in open(f"{SW8}/contexts.jsonl"):
        c = json.loads(l)
        if c["cond"] in ("self-hostile", "user-hostile"):
            ctx[(c["cond"], c["sid"])] = c
    caps, dirs = {}, {}
    for m in models:
        C = torch.load(f"{CAP}/{m}.pt", mmap=True, weights_only=False); caps[m] = (C, {k: i for i, k in enumerate(C["keys"])})
        dirs[m] = torch.load(f"{run}/dirs28_{m}.pt", weights_only=False)
    return ctx, caps, dirs


_DEVC = {}


def dev_dirs(dm, m, sc):
    """per (model, scenario) direction tensors on the device, fp32, renormalised: u [64, H], P [3, 64, H], A [3, 64, H]."""
    k = (m, sc)
    if k not in _DEVC:
        S = dm["scen"][sc]; un = lambda v: (v.float() / v.float().norm(dim=-1, keepdim=True)).to(DEV)
        _DEVC[k] = dict(u=un(S["u"]), P=un(S["P"]), A=un(S["A"]), zoff=S["zoff"].float().to(DEV))
    return _DEVC[k]


def group_ops(readout, m, d, rec, don, sid, caps, dirs, samples):
    """rows of one group in order: none, r1 (real), [d16 (real)], matched/clamped controls; each x samples (l16: 1 sample)."""
    C, idx = caps[m]; dm = dirs[m]; grp = f"{m}|{d}|{sid}"
    sc = dm["script"][sid]["scenario"]; T = dev_dirs(dm, m, sc); sg = dm["sign"][f"{d}|{sid}"]
    Dn = torch.as_tensor(C["hdr"][idx[f"sw008|{don}|{sid}"]]).to(DEV)
    base = dict(grp=grp, D=Dn)
    spec = {"none": dict(kind="none", grp=grp),
            "r1": dict(base, kind="sub", U=T["u"], real=True),
            "d16": dict(base, kind="sub", U=T["u"], real=True, layers=frozenset({16}))}
    for i in range(3):
        spec[f"P{i}"] = dict(base, kind="P", R=T["P"][i], sigma=sg["sigma_P"][i].to(DEV), match=f"{grp}:r1")
        spec[f"q{i}"] = dict(base, kind="P", R=T["P"][i], sigma=sg["sigma_P"][i].to(DEV), match=f"{grp}:d16", layers=frozenset({16}))
        spec[f"A{i}"] = dict(base, kind="A", R=T["A"][i], s=float(sg["s_A"][i]), match=f"{grp}:r1")
    for i in range(2):
        spec[f"Z{i}"] = dict(base, kind="Z", R=T["A"][i], s=float(sg["s_A"][i]), zoff=T["zoff"][i])
    arms = ARMS_L16 if readout == "l16" else ARMS
    ns = 1 if readout == "l16" else samples
    ops = []
    for arm in arms:
        for k in range(ns):
            ops.append(dict(spec[arm], arm=arm, sample=k, key=row_key(readout, m, d, sid, arm, k), model=m, direction=d,
                            recipient=rec, donor=don, sid=sid, log=(k == 0)))
    check_order(ops)
    meta = dict(scenario=sc, u_src=dm["scen"][sc]["u_src"], s_A=[float(x) for x in sg["s_A"]],
                sigma_P=[[int(x) for x in v] for v in sg["sigma_P"]])
    return ops, meta


def set_pos(ops, P, ns):
    for op in ops:
        op["pos"] = list(range(P - ns - 7, P - ns))


def pad_rows(id_rows):
    P = max(len(x) for x in id_rows)
    inp = torch.full((len(id_rows), P), PAD, dtype=torch.long); am = torch.zeros((len(id_rows), P), dtype=torch.long)
    for r, x in enumerate(id_rows):
        inp[r, P - len(x):] = torch.tensor(x); am[r, P - len(x):] = 1
    return inp, am, P


# ------------------------------------------------------------------------------------------------- generation
def generate_batch(model, hk, groups, max_new, seed, suffix):
    """groups: list of (ops, ids). Left-pads all rows (ids + suffix) to P; patch = header positions of every row (prefill)."""
    rows, ids_rows = [], []
    for ops, ids in groups:
        assert ids[-7:] == HEADER
        rows += ops; ids_rows += [ids + suffix] * len(ops)
    inp, am, P = pad_rows(ids_rows); ns = len(suffix)
    set_pos(rows, P, ns)
    assert all(inp[r, rows[r]["pos"]].tolist() == HEADER for r in range(len(rows))), "patched positions are not the header"
    check_order(rows)
    hk.ops = rows; hk.mode = "patch"; hk.min_len = P; hk.log = []
    torch.manual_seed(seed); torch.cuda.reset_peak_memory_stats(); torch.cuda.synchronize(); t0 = time.time()
    with torch.no_grad():
        o = model.generate(input_ids=inp.to(DEV), attention_mask=am.to(DEV), do_sample=True, temperature=0.7, top_p=1.0, top_k=0,
                           max_new_tokens=max_new, eos_token_id=list(EOS), pad_token_id=PAD)
    torch.cuda.synchronize(); wall = time.time() - t0; hk.mode = None
    gen = o[:, P:].cpu(); steps = gen.shape[1]; out = []
    for r in range(len(rows)):
        g = gen[r].tolist(); n = next((j for j, v in enumerate(g) if v in EOS), None)
        out.append((g[:n] if n is not None else g, n if n is not None else len(g), "stop" if n is not None else "length"))
    tim = dict(rows=len(rows), P=P, steps=steps, wall_s=round(wall, 1), s_per_step=round(wall / max(steps, 1), 4),
               peak_gib=round(torch.cuda.max_memory_allocated() / 2 ** 30, 1), gen_tokens=int(sum(x[1] for x in out)), hook_calls=hk.calls)
    return rows, out, hk.log, tim


def run_batch(model, hk, batch, max_new, m, suffix, readout):
    """sw012 review fix F3: on CUDA OOM split the batch into halves (whole groups, so every control stays in its real row's forward)."""
    oom = False
    try:
        res = generate_batch(model, hk, [(g[0], g[1]) for g in batch], max_new, seed_of("sw028", readout, m, batch[0][0][0]["grp"], max_new), suffix)
    except torch.cuda.OutOfMemoryError:
        oom = True
    if not oom:
        return [(batch,) + res]
    hk.mode = None; hk.log = []
    import gc
    gc.collect(); torch.cuda.empty_cache()
    if len(batch) == 1:
        raise RuntimeError(f"CUDA OOM on a single group ({batch[0][0][0]['grp']})")
    h = len(batch) // 2
    print(f"[oom] {m}: batch of {len(batch)} groups split into {h} + {len(batch) - h}", flush=True)
    return run_batch(model, hk, batch[:h], max_new, m, suffix, readout) + run_batch(model, hk, batch[h:], max_new, m, suffix, readout)


# ------------------------------------------------------------------------------------------------- checks shared with the CPU tests / output gates
from common28 import BANDS, TOK, cum_ratios, cum_gate, median  # noqa: E402,F401  (pure python, also used by analyze28)


def hook_checks(logs, ops_by_key, zoff_of, tol_rel=0.02, tol_abs=0.5):
    """known answers from the live logs (sample-0 rows): P sign = sigma and |inc| = r1's |inc| (per layer, token);
    A along = s * off_r1; Z along = s * zoff; returns dict of worst errors."""
    by = {}
    for e in logs:
        if e["sample"] == 0:
            by.setdefault((e["grp"], e["L"]), {})[e["arm"]] = e
    W = dict(P_sign_violations=0, P_norm_ratio_dev=0.0, A_along_err_rel=0.0, Z_along_err_rel=0.0, n_checked=0, q_sign_violations=0)
    for (g, L), v in by.items():
        for arm, e in v.items():
            op = ops_by_key[(g, arm)]
            if op["kind"] == "P" and L in op.get("layers", range(16, 64)):
                ref = v.get(op["match"].split(":")[1])
                sig = [int(x) for x in op["sigma"].tolist()]
                for t in range(7):
                    if abs(e["inc"][t]) > 1e-6 and (1 if e["inc"][t] > 0 else -1) != sig[t]:
                        W["P_sign_violations" if arm.startswith("P") else "q_sign_violations"] += 1
                    if ref is not None and abs(ref["inc"][t]) > 1e-3:
                        W["P_norm_ratio_dev"] = max(W["P_norm_ratio_dev"], abs(abs(e["inc"][t]) / abs(ref["inc"][t]) - 1))
                W["n_checked"] += 1
            if op["kind"] == "A" and "r1" in v:
                for t in range(7):
                    want = op["s"] * v["r1"]["off"][t]
                    W["A_along_err_rel"] = max(W["A_along_err_rel"], (abs(e["along"][t] - want) - tol_abs) / max(abs(want), 1e-6))
                W["n_checked"] += 1
            if op["kind"] == "Z":
                z = zoff_of(op, L)
                for t in range(7):
                    want = op["s"] * z[t]
                    W["Z_along_err_rel"] = max(W["Z_along_err_rel"], (abs(e["along"][t] - want) - tol_abs) / max(abs(want), 1e-6))
                W["n_checked"] += 1
    W["pass"] = bool(W["P_sign_violations"] == 0 and W["q_sign_violations"] == 0 and W["P_norm_ratio_dev"] <= 0.01
                     and W["A_along_err_rel"] <= tol_rel and W["Z_along_err_rel"] <= tol_rel and W["n_checked"] > 0)
    return W


# ------------------------------------------------------------------------------------------------- GPU gates
def rel(a, b):
    return ((a.float() - b.float()).norm(dim=-1) / b.float().norm(dim=-1).clamp_min(1e-6))


def gates(model, hk, blocks, ctx, caps, dirs, sids, run_dir, readout):
    """G1 adapter active (sw012 G1: live header states = sw009 capture of the same model, far from the parent / other adapter);
    G3 hook known answers on the GPU in a left-padded 2-group batch with every arm (hdA0): r1 coordinate = donor's at L16/40/63;
    P sign kept and |push| = r1's; A along-offset = s * r1's cumulative offset; Z along-offset = s * zoff; cumulative ratios."""
    G = {}; ok = True
    C0 = torch.load(f"{CAP}/parent.pt", mmap=True, weights_only=False); i0 = {k: i for i, k in enumerate(C0["keys"])}

    def hdr_states(m, ids, layers=(16, 40, 63)):
        cap = {}
        hs = [blocks[L].register_forward_hook((lambda L: lambda mod, i, o: cap.__setitem__(L, (o[0] if isinstance(o, tuple) else o)[:, -7:].detach().float()))(L)) for L in layers]
        try:
            with use(model, m), torch.no_grad():
                model(input_ids=torch.tensor([ids], device=DEV), logits_to_keep=1)
        finally:
            for h in hs:
                h.remove()
        return {L: cap[L][0].cpu() for L in layers}

    sid0 = sids[0]; key0 = f"sw008|self-hostile|{sid0}"; ids0 = ctx[("self-hostile", sid0)]["ids"]
    g1 = {}
    for m in ("hdA0", "hdB0"):
        st = hdr_states(m, ids0); Cm, im = caps[m]
        r_own = [float(rel(st[L], torch.as_tensor(Cm["hdr"][im[key0]][:, L])).max()) for L in (16, 40, 63)]
        r_oth = {o: max(float(rel(st[L], torch.as_tensor(Co["hdr"][io[key0]][:, L])).max()) for L in (40, 63))
                 for o, (Co, io) in [("parent", (C0, i0))] + [(x, caps[x]) for x in caps if x != m]}
        g1[m] = dict(rel_own_max=max(r_own), rel_other_max_L40_63=r_oth,
                     pass_=bool(max(r_own) <= 0.03 and all(v >= max(3 * max(r_own[1:]), 0.01) for v in r_oth.values())))
        ok &= g1[m]["pass_"]
    G["G1_adapter_active"] = g1
    # G3: 2 groups (fwd sid0, rev sids[1]) in one left-padded forward, every arm, all rows logged
    ro = "l16" if readout == "l16" else "free"
    gs_ = []
    for (d, rec, don), sid in ((DIRECTIONS[0], sids[0]), (DIRECTIONS[1], sids[1 % len(sids)])):
        ops, _ = group_ops(ro, "hdA0", d, rec, don, sid, caps, dirs, 1)
        for op in ops:
            op["log"] = True
        gs_.append((ops, ctx[(rec, sid)]["ids"]))
    rows = [o for g in gs_ for o in g[0]]; inp, am, P = pad_rows([g[1] for g in gs_ for _ in g[0]])
    set_pos(rows, P, 0)
    with use(model, "hdA0"):
        hk.ops = rows; hk.mode = "patch"; hk.min_len = P; hk.log = []; hk.keep = {16, 40, 63}; hk.cap = {}
        with torch.no_grad():
            model(input_ids=inp.to(DEV), attention_mask=am.to(DEV), logits_to_keep=1)
        hk.mode = None; hk.keep = None
    g3 = {}
    for r, op in enumerate(rows):
        if op["arm"] != "r1":
            continue
        r0 = [q for q, o in enumerate(rows) if o["grp"] == op["grp"] and o["arm"] == "none"][0]
        for L in (16, 40, 63):
            u = op["U"][L]; got = hk.cap[L][r] @ u; want = op["D"][:, L].float() @ u
            gap = (want - hk.cap[L][r0] @ u).abs().mean()
            g3[f"{op['grp']}|r1|L{L}"] = dict(coord_err_max=float((got - want).abs().max()), gap_mean=float(gap))
    hk.cap = {}
    r1_ok = all(v["coord_err_max"] <= 0.05 * max(v["gap_mean"], 1.0) + 0.5 for v in g3.values())
    obk = {(o["grp"], o["arm"]): o for o in rows}
    W = hook_checks(hk.log, obk, lambda op, L: op["zoff"][L].tolist())
    per = cum_ratios(hk.log, real="r1")
    cg = cum_gate(per) if ro == "free" else dict(arms={a: {b: median(v) for b, v in bb.items()} for a, bb in per.items()}, pass_=True)
    G["G3_hook_known_answers"] = dict(r1_detail=g3, r1_pass=bool(r1_ok), arms=W, cumulative=cg, pass_=bool(r1_ok and W["pass"] and cg["pass_"]))
    ok &= G["G3_hook_known_answers"]["pass_"]
    G["pass"] = bool(ok)
    os.makedirs(run_dir, exist_ok=True); json.dump(G, open(f"{run_dir}/gates.json", "w"), indent=1, default=float)
    print("GATES", json.dumps(G, default=float)[:4000], flush=True)
    return G


# ------------------------------------------------------------------------------------------------- l16 readout
def run_l16(model, hk, m, ctx, caps, dirs, sids, run_dir, scripts_per_batch):
    """prefill only; both directions of each script in one forward (each direction's none row = the other's donor state)."""
    fn = f"{run_dir}/states_{m}.pt"
    if os.path.exists(fn):
        print(f"[l16] {m} exists, skip", flush=True); return
    keys, meta, H, KL, logs = [], [], [], [], []
    for b0 in range(0, len(sids), scripts_per_batch):
        groups = []
        for sid in sids[b0:b0 + scripts_per_batch]:
            for d, rec, don in DIRECTIONS:
                ops, _ = group_ops("l16", m, d, rec, don, sid, caps, dirs, 1); groups.append((ops, ctx[(rec, sid)]["ids"]))
        rows = [o for g in groups for o in g[0]]; inp, am, P = pad_rows([g[1] for g in groups for _ in g[0]])
        set_pos(rows, P, 0); check_order(rows)
        assert all(inp[r, rows[r]["pos"]].tolist() == HEADER for r in range(len(rows)))
        hk.ops = rows; hk.mode = "patch"; hk.min_len = P; hk.log = []; hk.keep = set(LOG14); hk.cap = {}
        with torch.no_grad():
            lg = model(input_ids=inp.to(DEV), attention_mask=am.to(DEV), logits_to_keep=1).logits[:, -1].float()
        hk.mode = None; hk.keep = None
        lp = torch.log_softmax(lg, -1)
        ref = {o["grp"]: r for r, o in enumerate(rows) if o["arm"] == "none"}
        kl = [(lp[ref[o["grp"]]].exp() * (lp[ref[o["grp"]]] - lp[r])).sum().item() for r, o in enumerate(rows)]
        H.append(torch.stack([hk.cap[L] for L in LOG14], 2).half().cpu())   # [rows, 7, 14, H]
        hk.cap = {}; logs += hk.log
        keys += [o["key"] for o in rows]; KL += kl
        meta += [dict(key=o["key"], grp=o["grp"], arm=o["arm"], direction=o["direction"], recipient=o["recipient"], donor=o["donor"], sid=o["sid"]) for o in rows]
        print(f"[l16] {m} {min(b0 + scripts_per_batch, len(sids))}/{len(sids)} scripts rows {len(rows)} P {P} {time.strftime('%H:%M:%S')}", flush=True)
    assert len(set(keys)) == len(keys), "duplicate l16 keys"
    X = torch.cat(H)
    assert torch.isfinite(X.float()).all()
    torch.save(dict(keys=keys, meta=meta, layers=list(LOG14), hdr=X, kl_vs_none=KL), fn + ".tmp"); os.replace(fn + ".tmp", fn)
    with open(f"{run_dir}/log_l16_{m}.jsonl", "w") as f:
        for e in logs:
            f.write(json.dumps(e) + "\n")
    print(f"[l16] {m} saved {len(keys)} rows -> {fn}", flush=True)


# ------------------------------------------------------------------------------------------------- main
def repair_tail(p):
    """reviewer fix D23: a job killed mid-append (a pod that vanishes) can leave a torn last line with no newline. The next append
    would glue a new row onto it, losing that row and leaving a line the strict output gate (smoke_check28.jl) cannot parse.
    Truncate the file after its last newline before resuming. Returns the number of bytes dropped."""
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


def run_gen(model, hk, tok, m, readout, ctx, caps, dirs, sids, run_dir, samples, max_new, batch_groups):
    suffix = tok(BTW, add_special_tokens=False)["input_ids"] if readout == "forced" else []
    fn, lfn = f"{run_dir}/{readout}_{m}.jsonl", f"{run_dir}/log_{readout}_{m}.jsonl"
    repair_tail(fn); repair_tail(lfn)
    have = set()
    if os.path.exists(fn):
        for l in open(fn):
            try:
                have.add(json.loads(l)["key"])
            except json.JSONDecodeError:
                pass
    todo = []
    for sid in sids:
        for d, rec, don in DIRECTIONS:
            ops, meta = group_ops(readout, m, d, rec, don, sid, caps, dirs, samples)
            if all(o["key"] in have for o in ops):
                continue
            todo.append((ops, ctx[(rec, sid)]["ids"], meta))
    todo.sort(key=lambda g: len(g[1]))   # similar prompt lengths share a batch; the arms of a group stay together
    print(m, readout, "groups todo", len(todo), "rows", sum(len(g[0]) for g in todo), flush=True)
    nb = -(-len(todo) // batch_groups)
    for b0 in range(0, len(todo), batch_groups):
        for batch, rows, out, logs, tim in run_batch(model, hk, todo[b0:b0 + batch_groups], max_new, m, suffix, readout):
            res = {op["key"]: o for op, o in zip(rows, out)}
            assert len(res) == len(rows), "duplicate keys inside one batch"
            lines = []
            for ops, ids, meta in batch:
                for op in ops:
                    if op["key"] in have:   # sw012 review fix F2: a group left partial by a crash keeps the rows already written
                        continue
                    gen, n, fin = res[op["key"]]
                    txt = (BTW if readout == "forced" else "") + tok.decode(gen, skip_special_tokens=True)
                    have.add(op["key"])
                    lines.append(json.dumps(dict(key=op["key"], exp="sw028", readout=readout, model=m, direction=op["direction"],
                                                 recipient=op["recipient"], donor=op["donor"], sid=op["sid"], arm=op["arm"], sample=op["sample"],
                                                 text=txt, n_tok=n, finish=fin, max_new=max_new, gen_head=gen[:16], **meta)) + "\n")
            with open(lfn, "a") as f:   # logs before rows: a row on disk always has its group's logs
                f.write("".join(json.dumps(dict(readout=readout, **e)) + "\n" for e in logs))
            with open(fn, "a") as f:
                f.write("".join(lines))
            with open(f"{run_dir}/timing.jsonl", "a") as f:
                f.write(json.dumps(dict(model=m, readout=readout, groups=[g[0][0]["grp"] for g in batch], max_new=max_new, t=time.strftime("%FT%T"), **tim)) + "\n")
            caps_hit = sum(1 for o in out if o[2] == "length")
            print(f"[gen] {m} {readout} batch {b0 // batch_groups + 1}/{nb} {json.dumps(tim)} cap_hits {caps_hit}/{len(out)} {time.strftime('%H:%M:%S')}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--readout", required=True, help="free | forced | l16, or a comma list (one model load for all)")
    ap.add_argument("--models", default="hdA0,hdB0"); ap.add_argument("--sids", default=None)
    ap.add_argument("--max_new", type=int, default=2048); ap.add_argument("--batch_groups", type=int, default=8)
    ap.add_argument("--forced_batch_groups", type=int, default=16)
    ap.add_argument("--samples", type=int, default=2); ap.add_argument("--gates", action="store_true")
    ap.add_argument("--run_dir", default=RUN, help="root; each readout writes to <run_dir>/<readout>/")
    ap.add_argument("--gates_out", default=None)
    ap.add_argument("--gate_sids", default=None); ap.add_argument("--scripts_per_batch", type=int, default=8)
    a = ap.parse_args()
    readouts = a.readout.split(",")
    assert all(r in ("free", "forced", "l16") for r in readouts), readouts
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    torch.set_grad_enabled(False); torch.set_num_threads(8); torch.backends.cuda.matmul.allow_tf32 = False
    models = a.models.split(",")
    tok = AutoTokenizer.from_pretrained(BASE)
    ctx, caps, dirs = load_inputs(("hdA0", "hdB0"))
    all_sids = sorted({sid for (_, sid) in ctx})
    sids = [s for s in all_sids if not a.sids or s in set(a.sids.split(","))]
    print("readouts", readouts, "sids", len(sids), "models", models, flush=True)
    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.bfloat16, device_map=DEV)
    model = PeftModel.from_pretrained(model, LORA["hdA0"], adapter_name="hdA0")
    model.load_adapter(LORA["hdB0"], adapter_name="hdB0"); model.eval()
    blocks = acts.blocks(model)
    assert len(blocks) == 64
    hk = Hooks28(blocks)
    print(f"loaded {time.time() - t0:.0f}s", flush=True)
    if a.gates:
        gs = a.gate_sids.split(",") if a.gate_sids else sids[:2]
        G = gates(model, hk, blocks, ctx, caps, dirs, gs, a.gates_out or a.run_dir, "l16" if readouts == ["l16"] else "free")
        if not G["pass"]:
            print("GATES_FAILED", flush=True); sys.exit(3)
    for ro in readouts:
        rd = f"{a.run_dir}/{ro}"; os.makedirs(rd, exist_ok=True)
        for m in models:
            with use(model, m):
                if ro == "l16":
                    run_l16(model, hk, m, ctx, caps, dirs, sids, rd, a.scripts_per_batch)
                else:
                    run_gen(model, hk, tok, m, ro, ctx, caps, dirs, sids, rd, a.samples,
                            FORCED_TOKENS if ro == "forced" else a.max_new, a.forced_batch_groups if ro == "forced" else a.batch_groups)
        print(f"READOUT_DONE {ro} {time.strftime('%H:%M:%S')}", flush=True)
    print("GEN28_EXIT", flush=True)


if __name__ == "__main__":
    main()
