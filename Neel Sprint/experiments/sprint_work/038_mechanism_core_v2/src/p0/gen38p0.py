"""sw038 Part 0 GPU stage (prep-P0 agent, E2 Lane M, 31 Oct 2026): sw006's whole-state header patch on evaluation set v2.
Engine = sw029's (gen29_x.py): HF transformers + unmerged PEFT, ONE organism per process (hdA0 on GPU 0, hdB0 on GPU 1), bf16,
forward hooks on model.model.layers[L] (block output, pre-final-norm), edits at L16-63 prefill only, left-padded batches,
OOM halving by whole units, resume by key, torn-tail repair. Patch arithmetic = sw006 hf_x 'full' kind: t[r, hdr] = D[:, L].
Stages (in this order):
  capture : the recipient model's own header states [7, 64, H] (bf16) on all 122 G2 contexts (61 scripts x helpful/dismissive),
            batch 1 -> <caps_dir>/caps_<m>.pt (reused if present and the ids hashes match).
  gates   : G1 adapter active (sw029 D11 logic) + G1b same-box parent distance + KA known answers in one left-padded forward
            (see gates()); -> <run_dir>/gates_<m>.json; exit 3 on failure. Per-layer bars feed the per-batch checks.
  gen     : readouts forced ("By the way," + 48 sampled tokens) then free (<= 2,048 tokens, stop <|im_end|>/<|endoftext|>);
            T 0.7, top_p 1, top_k 0; unit = (model, direction, script, sample) with 5 rows (none, P0, P0a, P0b, sk).
            Every batch: hook fired exactly 48 times (prefill only) and an independent known answer at L16 / L63 (exit 5 on fail).
  mem     : --mem_probe 'free:10,12;forced:16,24' -> units from the LONGEST recipient contexts, min_new_tokens = max_new.
Outputs: <run_dir>/<readout>/<readout>_<m>.jsonl (key sw038|p0|<readout>|<m>|<direction>|<sid>|<arm>|s<k>), timing.jsonl,
         gates_<m>.json, mem_probe_<m>.json.
  CUDA_VISIBLE_DEVICES=0 python gen38p0.py --model hdA0 --readouts forced,free --directions induce,remove --sids all --gates"""
import argparse, contextlib, gc, hashlib, json, os, socket, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common38p0 as K  # noqa: E402
from hooks38p0 import Hooks38, Cap, rel_tok  # noqa: E402

LIB = "/workspace/runs_executor/day_2026-10-31_E2/lib"
CAP9 = "/workspace/runs_executor/sw009_captures"
SW8 = f"{K.NS}/experiments/sprint_work/008_hostility_attribution/src/out"
DEV = "cuda"
G1_OWN_NODE = 0.10     # sw029 D11: cross-box bar (node H100 vs box-1 H200 sw009 captures; measured floor <= 0.042, failure >= 0.33)
G1_RATIO = 3.0
BAR_MULT = 3.0         # D6: bar[L] = 3 x the measured same-path floor at L; the failure scale at L must exceed the bar
KA_LAYERS = (15, 16, 19, 20, 39, 40, 41, 63)
BATCH_KA_LAYERS = (16, 63)
TOKSUF = {}


def utc():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def cuda():
    return DEV == "cuda" and torch.cuda.is_available()


def use(model, m):
    if m == "parent":
        return model.disable_adapter()
    model.set_adapter(m); return contextlib.nullcontext()


def ids_sha(ids):
    return hashlib.sha256(json.dumps(list(ids)).encode()).hexdigest()[:16]


def header_pos_independent(row):
    """the 7 positions of the LAST occurrence of HEADER in a padded row (independent of build_batch's arithmetic)."""
    H = K.HEADER; hits = [i for i in range(len(row) - 6) if row[i:i + 7] == H]
    assert hits, "no header in row"
    return list(range(hits[-1], hits[-1] + 7))


# ------------------------------------------------------------------------------------------------- contexts / captures
def build_contexts(tok):
    rows, sids, dom = K.load_g2()
    ctx = {}
    for s in sids:
        for v in K.VERSIONS:
            ids = K.render(tok, K.msgs_of(rows[(s, v)]))
            ctx[K.ctx_key(s, v)] = dict(ids=ids, sid=s, version=v, domain=dom[s])
    assert len(ctx) == 2 * len(sids) == 122, len(ctx)
    return ctx, sids, dom


def capture(model, hk, m, ctx, path):
    keys = sorted(ctx)
    if os.path.exists(path):
        C = torch.load(path, weights_only=False)
        assert C["model"] == m and C["keys"] == keys, "capture file keys / model differ"
        assert all(C["ids_sha"][k] == ids_sha(ctx[k]["ids"]) for k in keys), "capture file ids differ from this rendering"
        print("captures reused", path, flush=True)
        return C
    H = []; t0 = time.time()
    with use(model, m), torch.no_grad():
        for k in keys:
            ids = ctx[k]["ids"]
            hk.mode = "cap"; hk.cap = {}; hk.cap_pos = list(range(len(ids) - 7, len(ids)))
            model(input_ids=torch.tensor([ids], device=DEV), logits_to_keep=1)
            hk.mode = None
            H.append(torch.stack([hk.cap[L][0] for L in range(64)], 1).cpu())     # [7, 64, H] bf16 (exact model dtype)
    hk.cap = {}
    C = dict(keys=keys, hdr=torch.stack(H), ids_sha={k: ids_sha(ctx[k]["ids"]) for k in keys}, model=m, batch=1, t=utc(),
             convention="model.model.layers[L] output (pre-final-norm) at the 7 reply-header tokens, bf16, batch 1, no padding")
    assert C["hdr"].dtype == torch.bfloat16 and tuple(C["hdr"].shape[:3]) == (len(keys), 7, 64)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    torch.save(C, path + ".tmp"); os.replace(path + ".tmp", path)
    print(f"captured {m} {len(keys)} contexts in {time.time() - t0:.0f}s -> {path}", flush=True)
    return C


# ------------------------------------------------------------------------------------------------- ops / batches
def unit_ops(readout, m, d, sid, k, C, idx, sids, dom, extra=()):
    """the unit's rows in K.ARMS order (+ gate-only extra rows 'none_rep' / 'self')."""
    rec, _ = K.DIRECTIONS[d]; grp = K.unit_id(m, d, sid, k); ops = []
    for arm in tuple(K.ARMS) + tuple(extra):
        base = dict(arm=arm, sample=k, key=K.row_key(readout, m, d, sid, arm, k), grp=grp, model=m, direction=d, recipient=rec, sid=sid)
        if arm in ("none", "none_rep"):
            ops.append(dict(base, kind="none", donor=None)); continue
        if arm == "self":
            dk, layers = K.ctx_key(sid, rec), K.PATCH_LAYERS["P0"]
        else:
            ds, dv = K.donor_of(d, arm, sid, sids, dom); dk, layers = K.ctx_key(ds, dv), K.PATCH_LAYERS[arm]
        ops.append(dict(base, kind="full", donor=dk, layers=frozenset(layers), Dcpu=C["hdr"][idx[dk]]))
    return ops


def build_batch(units):
    """units: list of (ops, ids, suffix). Left padding: row = [PAD]*(P - len(ids) - len(suffix)) + ids + suffix."""
    rows, idr = [], []
    for ops, ids, suf in units:
        rows += ops; idr += [list(ids) + list(suf)] * len(ops)
    P = max(len(x) for x in idr)
    inp = torch.full((len(idr), P), K.PAD, dtype=torch.long); am = torch.zeros((len(idr), P), dtype=torch.long)
    for r, x in enumerate(idr):
        inp[r, P - len(x):] = torch.tensor(x); am[r, P - len(x):] = 1
    for ops, ids, suf in units:
        hp = [P - len(suf) - 7 + i for i in range(7)]
        for op in ops:
            op["pos"] = hp; op["nsuf"] = len(suf)
    for r, op in enumerate(rows):
        assert inp[r, op["pos"]].tolist() == K.HEADER, "header positions are not the header"
    return rows, inp, am, P


def attach_D(rows):
    cache = {}
    for op in rows:
        if op["kind"] == "full":
            if op["donor"] not in cache:
                cache[op["donor"]] = op["Dcpu"].to(DEV)
            op["D"] = cache[op["donor"]]


def detach_D(rows):
    for op in rows:
        op.pop("D", None)


def indep_donor(arm, d, sid, sids, dom):
    """gate-side donor key, written out separately from common38p0.donor_of (P0 / P0a / P0b: same script, the other version;
    sk: next script of the same domain, recipient's version; self: the recipient itself)."""
    rec = "helpful" if d == "induce" else "dismissive"; oth = "dismissive" if d == "induce" else "helpful"
    if arm in ("P0", "P0a", "P0b"):
        return f"{sid}|{oth}"
    if arm == "self":
        return f"{sid}|{rec}"
    if arm == "sk":
        same = sorted(s for s in sids if dom[s] == dom[sid]); return f"{same[(same.index(sid) + 1) % len(same)]}|{rec}"
    raise ValueError(arm)


def indep_layers(arm):
    return {"P0": range(16, 64), "P0a": range(20, 41), "P0b": range(40, 64), "sk": range(16, 64), "self": range(16, 64)}[arm]


def batch_ka(rows, cap, C, idx, sids, dom, bar):
    """per-batch independent known answer at L16 / L63 (header positions re-derived from the padded ids): rows whose arm patches L
    equal their donor's capture (max over tokens of the relative distance <= bar[L]); rows that do not patch L16 equal their unit's
    none row there. P0a at L63 (not patched) is reported only."""
    none_r = {op["grp"]: r for r, op in enumerate(rows) if op["arm"] == "none"}
    W = dict(copy_max={}, untouched_max={}, P0a_L63_to_donor=None, n_checked=0, fails=[])
    for r, op in enumerate(rows):
        if op["kind"] != "full":
            continue
        Dk = indep_donor(op["arm"], op["direction"], op["sid"], sids, dom); assert Dk == op["donor"], (Dk, op["donor"])
        lay = set(indep_layers(op["arm"]))
        for L in BATCH_KA_LAYERS:
            x = cap[L][r]
            if L in lay:
                e = float(rel_tok(x, C["hdr"][idx[Dk]][:, L]).max()); W["copy_max"][L] = max(W["copy_max"].get(L, 0.0), e)
            elif L == 16:
                e = float(rel_tok(x, cap[L][none_r[op["grp"]]]).max()); W["untouched_max"][L] = max(W["untouched_max"].get(L, 0.0), e)
            else:
                e = float(rel_tok(x, C["hdr"][idx[Dk]][:, L]).max())
                W["P0a_L63_to_donor"] = e if W["P0a_L63_to_donor"] is None else min(W["P0a_L63_to_donor"], e)
                continue
            W["n_checked"] += 1
            if e > bar[str(L)]:
                W["fails"].append(dict(key=op["key"], L=L, err=e, bar=bar[str(L)]))
    W["pass"] = bool(not W["fails"] and W["n_checked"] > 0)
    return W


# ------------------------------------------------------------------------------------------------- generation
def generate_batch(model, hk, ka, units, max_new, seed, ctxinfo, bar, min_new=None, check=True):
    C, idx, sids, dom = ctxinfo
    rows, inp, am, P = build_batch(units)
    attach_D(rows)
    ind = [header_pos_independent(inp[r].tolist()) for r in range(len(rows))]
    for r, op in enumerate(rows):
        assert op["pos"] == ind[r], "header positions differ from the independently derived ones"
    ka.pos_rows = ind; ka.min_len = P; ka.cap = {}; ka.on = bool(check)
    hk.ops = rows; hk.mode = "patch"; hk.min_len = P; c0 = hk.calls
    torch.manual_seed(seed)
    if cuda():
        torch.cuda.reset_peak_memory_stats(); torch.cuda.synchronize()
    t0 = time.time()
    kw = dict(min_new_tokens=min_new) if min_new else {}
    try:
        with torch.no_grad():
            o = model.generate(input_ids=inp.to(DEV), attention_mask=am.to(DEV), do_sample=True, temperature=0.7, top_p=1.0, top_k=0,
                               max_new_tokens=max_new, eos_token_id=list(K.EOS), pad_token_id=K.PAD, **kw)
        if cuda():
            torch.cuda.synchronize()
    finally:
        hk.mode = None; ka.on = False
    wall = time.time() - t0
    calls = hk.calls - c0
    assert calls == K.N_HOOK_CALLS, f"hook fired {calls} times in one generate (expected {K.N_HOOK_CALLS}: once per patched layer, prefill only)"
    res = batch_ka(rows, ka.cap, C, idx, sids, dom, bar) if check else None
    ka.cap = {}; detach_D(rows)
    gen = o[:, P:].cpu(); steps = gen.shape[1]; out = []
    for r in range(len(rows)):
        g = gen[r].tolist(); n = next((j for j, v in enumerate(g) if v in K.EOS), None)
        out.append((g[:n] if n is not None else g, n if n is not None else len(g), "stop" if n is not None else "length"))
    tim = dict(rows=len(rows), units=len(units), P=P, steps=steps, wall_s=round(wall, 1), s_per_step=round(wall / max(steps, 1), 4),
               peak_alloc_gib=round(torch.cuda.max_memory_allocated() / 2 ** 30, 2) if cuda() else 0.0,
               peak_reserved_gib=round(torch.cuda.max_memory_reserved() / 2 ** 30, 2) if cuda() else 0.0,
               gen_tokens=int(sum(x[1] for x in out)), hook_calls=calls, seed=seed)
    return rows, out, tim, res


def run_batch(model, hk, ka, batch, max_new, m, readout, ctxinfo, bar):
    """sw012 F3 / sw029: on CUDA OOM split the batch into halves (whole units) and retry."""
    seed = K.seed_of(K.EXP, K.PART, readout, m, batch[0][0][0]["grp"], max_new)
    oom = False
    try:
        res = generate_batch(model, hk, ka, batch, max_new, seed, ctxinfo, bar)
    except torch.cuda.OutOfMemoryError:
        oom = True
    if not oom:
        return [(batch,) + res]
    hk.mode = None; ka.on = False; ka.cap = {}
    for u in batch:
        detach_D(u[0])
    gc.collect(); torch.cuda.empty_cache()
    if len(batch) == 1:
        raise RuntimeError(f"CUDA OOM on a single unit ({batch[0][0][0]['grp']})")
    h = len(batch) // 2
    print(f"[oom] {m} {readout}: batch of {len(batch)} units split into {h} + {len(batch) - h}", flush=True)
    return run_batch(model, hk, ka, batch[:h], max_new, m, readout, ctxinfo, bar) + run_batch(model, hk, ka, batch[h:], max_new, m, readout, ctxinfo, bar)


def run_gen(model, hk, ka, tok, m, readout, d, ctx, ctxinfo, gen_sids, run_dir, samples, max_new, batch_units, bar):
    C, idx, sids, dom = ctxinfo
    bridge = K.BRIDGES[readout]; suffix = TOKSUF[bridge] if bridge else []
    fn = f"{run_dir}/{readout}_{m}.jsonl"
    K.repair_tail(fn)
    have = {r["key"] for r in K.jl(fn)}
    rec, _ = K.DIRECTIONS[d]
    todo = []
    for sid in gen_sids:
        for k in range(samples):
            ops = unit_ops(readout, m, d, sid, k, C, idx, sids, dom)
            if all(o["key"] in have for o in ops):
                continue
            todo.append((ops, ctx[K.ctx_key(sid, rec)]["ids"], suffix))
    todo.sort(key=lambda u: (len(u[1]), u[0][0]["grp"]))
    nb = -(-len(todo) // batch_units) if todo else 0
    print(m, readout, d, "units todo", len(todo), "rows", sum(len(u[0]) for u in todo), "batches", nb, flush=True)
    for bi, b0 in enumerate(range(0, len(todo), batch_units)):
        for batch, rows, out, tim, kres in run_batch(model, hk, ka, todo[b0:b0 + batch_units], max_new, m, readout, ctxinfo, bar):
            with open(f"{run_dir}/timing.jsonl", "a") as f:
                f.write(json.dumps(dict(model=m, readout=readout, direction=d, units_in=[u[0][0]["grp"] for u in batch], max_new=max_new,
                                        t=utc(), ka=kres, **tim)) + "\n")
            if not kres["pass"]:
                print("BATCH_KA_FAILED", json.dumps(kres)[:2000], flush=True); sys.exit(5)
            assert len({op["key"] for op in rows}) == len(rows), "duplicate keys inside one batch"
            lines = []
            for r, (op, (gen, n, fin)) in enumerate(zip(rows, out)):
                if op["key"] in have:
                    continue
                have.add(op["key"])
                lines.append(json.dumps(dict(key=op["key"], exp=K.EXP, part=K.PART, readout=readout, model=m, direction=d,
                                             recipient=op["recipient"], donor=op["donor"], sid=op["sid"], domain=dom[op["sid"]], arm=op["arm"],
                                             sample=op["sample"], text=(bridge or "") + tok.decode(gen, skip_special_tokens=True), n_tok=n,
                                             finish=fin, max_new=max_new, seed=tim["seed"], row_in_batch=r, batch_rows=tim["rows"], P=tim["P"],
                                             prompt_len=len(ctx[K.ctx_key(op["sid"], op["recipient"])]["ids"]), gen_head=gen[:16])) + "\n")
            with open(fn, "a") as f:
                f.write("".join(lines)); f.flush(); os.fsync(f.fileno())
            caps_hit = sum(1 for o in out if o[2] == "length")
            print(f"[gen] {m} {readout} {d} batch {bi + 1}/{nb} {json.dumps(tim)} cap_hits {caps_hit}/{len(out)} ka_copy {kres['copy_max']} "
                  f"ka_untouched {kres['untouched_max']} {utc()}", flush=True)


# ------------------------------------------------------------------------------------------------- gates
def rel_med(a, b):
    """sw029 rel_med: median over header tokens 1-6 of the per-token relative distance."""
    r = (a.float() - b.float()).norm(dim=-1) / b.float().norm(dim=-1).clamp_min(1e-6)
    return float(r[1:].median())


def gates(model, hk, blocks, m, ctx, ctxinfo, gate_sids, out_dir):
    """G1  (sw029 D11, copied logic): live header states (batch 1) of one sw008 self-hostile context vs the box-1 sw009 captures:
           own: median over tokens 1-6 of the relative distance, max over L16/40/63 <= 0.10; parent's and the other organism's
           captures (min over L40/63) >= 3 x own and >= 0.01.
    G1b (same box, G2 contexts): the parent's live header states (adapter disabled, batch 1) vs this organism's batch-1 capture on
           2 G2 contexts (same metric, min over L40/63) >= 3 x the padded-batch floor F_pad (same metric, max over L40/63).
    KA  one left-padded forward (prefill; logits_to_keep=1) of 2 units: induce gate_sids[0] WITH the forced suffix, remove
           gate_sids[1] without; rows none, P0, P0a, P0b, sk, none_rep (repeat), self (the recipient's own capture at L16-63).
           Read-only Cap after the edit hooks at KA_LAYERS, positions re-derived from the padded ids (header = last HEADER;
           non-header = the 8 tokens before it + the suffix). Metric = max over positions of the per-token relative distance.
           Floor F[L] = max(F_rep[L] (none_rep vs none, every position), F_pad[L] (none's live header vs its batch-1 capture));
           bar[L] = 3 x F[L]; failure scale fail[L] = min over units and donor arms (P0, sk) of the distance between the donor's
           capture and the none row's live header (what a no-op or mis-layered patch would leave). Gates: fail[L] > bar[L] at every
           checked layer (the bar sits between the floor and the failure); every arm's header equals its donor's capture at each
           patched KA layer (<= bar[L]); equals the none row's at every KA layer below its first patched layer (L15 for all;
           L16 / L19 for P0a; up to L39 for P0b); non-header positions equal the none row's at L15 / L16 (<= bar[L]).
           Reported: P0a at L41 / L63 vs donor (not patched), and last-token log-prob max |diff| of self / P0 vs none."""
    C, idx, sids, dom = ctxinfo
    G = dict(model=m, t=utc(), gate_sids=gate_sids); ok = True
    # ---- G1
    sw8 = {}
    for l in open(f"{SW8}/contexts.jsonl"):
        c = json.loads(l)
        if c["cond"] == "self-hostile":
            sw8[c["sid"]] = c
    sid0 = sorted(sw8)[0]; key0 = f"sw008|self-hostile|{sid0}"; ids0 = sw8[sid0]["ids"]; assert ids0[-7:] == K.HEADER
    cap = {}
    hs = [blocks[L].register_forward_hook((lambda L: lambda mod, i, o: cap.__setitem__(L, (o[0] if isinstance(o, tuple) else o)[0, -7:].detach().float().cpu()))(L))
          for L in (16, 40, 63)]
    try:
        with use(model, m), torch.no_grad():
            model(input_ids=torch.tensor([ids0], device=DEV), logits_to_keep=1)
    finally:
        for h in hs:
            h.remove()
    paths = {"parent": f"{CAP9}/parent.pt", "hdA0": f"{CAP9}/hdA0.pt", "hdB0": f"{CAP9}/hdB0.pt"}
    Co = torch.load(paths[m], mmap=True, weights_only=False); io = {k: i for i, k in enumerate(Co["keys"])}
    r_own = max(rel_med(cap[L], torch.as_tensor(Co["hdr"][io[key0]][:, L])) for L in (16, 40, 63)); del Co
    r_oth = {}
    for o, p in paths.items():
        if o == m:
            continue
        Co = torch.load(p, mmap=True, weights_only=False); io = {k: i for i, k in enumerate(Co["keys"])}
        r_oth[o] = min(rel_med(cap[L], torch.as_tensor(Co["hdr"][io[key0]][:, L])) for L in (40, 63)); del Co
    G["G1_adapter_active"] = dict(key=key0, rel_own_max=r_own, rel_other_min_L40_63=r_oth, tol_own=G1_OWN_NODE, ratio=G1_RATIO,
                                  pass_=bool(r_own <= G1_OWN_NODE and all(v >= max(G1_RATIO * r_own, 0.01) for v in r_oth.values())))
    ok &= G["G1_adapter_active"]["pass_"]
    # ---- KA forward
    units = []
    for d, sid, suf in (("induce", gate_sids[0], TOKSUF[K.BRIDGES["forced"]]), ("remove", gate_sids[1 % len(gate_sids)], [])):
        ops = unit_ops("gate", m, d, sid, 0, C, idx, sids, dom, extra=("none_rep", "self"))
        units.append((ops, ctx[K.ctx_key(sid, K.DIRECTIONS[d][0])]["ids"], suf))
    rows, inp, am, P = build_batch(units); attach_D(rows)
    ind = []
    for r in range(len(rows)):
        row = inp[r].tolist(); hp = header_pos_independent(row); assert rows[r]["pos"] == hp
        pre = list(range(hp[0] - 8, hp[0])); suf = list(range(hp[-1] + 1, P)); ind.append((hp, pre + suf))
    ck = Cap(blocks, KA_LAYERS); ck.pos_rows = [h + n for h, n in ind]; ck.min_len = P
    try:
        with use(model, m), torch.no_grad():
            hk.ops = rows; hk.mode = "patch"; hk.min_len = P; ck.on = True; c0 = hk.calls
            lg = model(input_ids=inp.to(DEV), attention_mask=am.to(DEV), logits_to_keep=1).logits[:, -1].float()
            hk.mode = None; ck.on = False
    finally:
        hk.mode = None; ck.remove()
    calls = hk.calls - c0
    lp = torch.log_softmax(lg, -1).cpu(); detach_D(rows)
    byg = {}
    for r, op in enumerate(rows):
        byg.setdefault(op["grp"], {})[op["arm"]] = r
    hdr = lambda L, r: ck.cap[L][r][:7]                    # noqa: E731
    nonh = lambda L, r: ck.cap[L][r][7:]                   # noqa: E731
    mx = lambda a, b: float(rel_tok(a, b).max())           # noqa: E731
    F_rep, F_pad, fail = {}, {}, {}
    for L in KA_LAYERS:
        fr, fp, fl = 0.0, 0.0, []
        for g, a in byg.items():
            rn, rr = a["none"], a["none_rep"]
            fr = max(fr, float(rel_tok(ck.cap[L][rr], ck.cap[L][rn]).max()))
            o = rows[rn]; reck = f"{o['sid']}|{o['recipient']}"
            fp = max(fp, mx(hdr(L, rn), C["hdr"][idx[reck]][:, L]))
            for arm in ("P0", "sk"):
                dk = indep_donor(arm, o["direction"], o["sid"], sids, dom)
                fl.append(mx(C["hdr"][idx[dk]][:, L], hdr(L, rn)))
        F_rep[L], F_pad[L], fail[L] = fr, fp, min(fl)
    F = {L: max(F_rep[L], F_pad[L]) for L in KA_LAYERS}; bar = {L: BAR_MULT * F[L] for L in KA_LAYERS}
    checks, fails = [], []
    for g, a in byg.items():
        rn = a["none"]
        for arm in ("P0", "P0a", "P0b", "sk", "self"):
            r = a[arm]; o = rows[r]; dk = indep_donor(arm, o["direction"], o["sid"], sids, dom); assert dk == o["donor"]
            lay = set(indep_layers(arm)); first = min(lay)
            for L in KA_LAYERS:
                if L in lay:
                    kind, e = "copy", mx(hdr(L, r), C["hdr"][idx[dk]][:, L])
                elif L < first:
                    kind, e = "untouched_hdr", mx(hdr(L, r), hdr(L, rn))
                else:
                    checks.append(dict(grp=g, arm=arm, L=L, kind="report_not_patched_vs_donor", err=mx(hdr(L, r), C["hdr"][idx[dk]][:, L])))
                    continue
                c = dict(grp=g, arm=arm, L=L, kind=kind, err=e, bar=bar[L]); checks.append(c)
                if e > bar[L]:
                    fails.append(c)
            for L in (15, 16):
                e = mx(nonh(L, r), nonh(L, rn)); c = dict(grp=g, arm=arm, L=L, kind="untouched_nonhdr", err=e, bar=bar[L]); checks.append(c)
                if e > bar[L]:
                    fails.append(c)
    disc = {L: bool(fail[L] > bar[L]) for L in KA_LAYERS}
    gated = [c for c in checks if "bar" in c]
    worst = {k: max([c["err"] for c in gated if c["kind"] == k] or [0.0]) for k in ("copy", "untouched_hdr", "untouched_nonhdr")}
    lpd = {}
    for g, a in byg.items():
        lpd[g] = {arm: float((lp[a[arm]] - lp[a["none"]]).abs().max()) for arm in ("none_rep", "self", "P0", "sk")}
    KA = dict(hook_calls=calls, F_rep=F_rep, F_pad=F_pad, floor=F, bar=bar, fail_scale=fail, discriminable=disc, worst=worst,
              n_gated=len(gated), fails=fails, logprob_maxdiff_vs_none=lpd,
              reported=[c for c in checks if c["kind"] == "report_not_patched_vs_donor"],
              pass_=bool(calls == K.N_HOOK_CALLS and all(disc.values()) and not fails and len(gated) > 0))
    G["KA_known_answers"] = KA; ok &= KA["pass_"]
    # ---- G1b: parent live (batch 1) vs this organism's capture on the 2 gate contexts; floor = F_pad in the sw029 metric
    pr, fpm = [], 0.0
    for (ops, ids, suf) in units:
        o = ops[0]; reck = f"{o['sid']}|{o['recipient']}"; cap = {}
        hs = [blocks[L].register_forward_hook((lambda L: lambda mod, i, oo: cap.__setitem__(L, (oo[0] if isinstance(oo, tuple) else oo)[0, -7:].detach().float().cpu()))(L))
              for L in (40, 63)]
        try:
            with use(model, "parent"), torch.no_grad():
                model(input_ids=torch.tensor([ids], device=DEV), logits_to_keep=1)
        finally:
            for h in hs:
                h.remove()
        pr.append(min(rel_med(cap[L], C["hdr"][idx[reck]][:, L]) for L in (40, 63)))
        rn = byg[o["grp"]]["none"]
        fpm = max(fpm, max(rel_med(hdr(L, rn), C["hdr"][idx[reck]][:, L]) for L in (40, 63)))
    G["G1b_parent_distance"] = dict(parent_vs_own_min=min(pr), F_pad_sw029_metric=fpm, ratio=G1_RATIO, pass_=bool(min(pr) >= G1_RATIO * fpm and min(pr) > 0))
    ok &= G["G1b_parent_distance"]["pass_"]
    G["bar"] = {str(L): v for L, v in bar.items()}; G["pass"] = bool(ok)
    os.makedirs(out_dir, exist_ok=True)
    json.dump(G, open(f"{out_dir}/gates_{m}.json", "w"), indent=1, default=float)
    print("GATES", json.dumps({k: v for k, v in G.items() if k != "KA_known_answers"}, default=float)[:2500], flush=True)
    print("KA", json.dumps({k: v for k, v in KA.items() if k not in ("reported",)}, default=float)[:4000], flush=True)
    return G


# ------------------------------------------------------------------------------------------------- memory probe
def mem_probe(model, hk, ka, m, ctx, ctxinfo, spec, out_dir, bar):
    """spec 'free:10,12;forced:16,24': per readout, unit counts tried LARGEST first, one batch each from the LONGEST recipient
    contexts (both directions pooled, sorted by recipient length), every row forced to the cap (min_new_tokens = max_new); stops at
    the first count that fits (D12). Outputs discarded."""
    C, idx, sids, dom = ctxinfo; res = []
    order = sorted(((d, s) for d in K.DIR_ORDER for s in sids), key=lambda x: (-len(ctx[K.ctx_key(x[1], K.DIRECTIONS[x[0]][0])]["ids"]), x))
    for part in spec.split(";"):
        ro, ns = part.split(":"); bridge = K.BRIDGES[ro]; suffix = TOKSUF[bridge] if bridge else []; max_new = K.MAX_NEW[ro]
        for n in sorted((int(x) for x in ns.split(",")), reverse=True):
            units = [(unit_ops(ro, m, d, s, 0, C, idx, sids, dom), ctx[K.ctx_key(s, K.DIRECTIONS[d][0])]["ids"], suffix) for d, s in order[:n]]
            gc.collect(); torch.cuda.empty_cache()
            try:
                _, _, tim, kres = generate_batch(model, hk, ka, units, max_new, 1, ctxinfo, bar, min_new=max_new)
                res.append(dict(readout=ro, units=n, rows=tim["rows"], P=tim["P"], steps=tim["steps"], wall_s=tim["wall_s"], s_per_step=tim["s_per_step"],
                                peak_reserved_gib=tim["peak_reserved_gib"], peak_alloc_gib=tim["peak_alloc_gib"], ka_pass=kres["pass"], oom=False))
            except torch.cuda.OutOfMemoryError:
                hk.mode = None; ka.on = False; ka.cap = {}
                for u in units:
                    detach_D(u[0])
                res.append(dict(readout=ro, units=n, rows=5 * n, oom=True)); gc.collect(); torch.cuda.empty_cache()
            print("[mem_probe]", json.dumps(res[-1]), flush=True)
            json.dump(dict(model=m, total_gib=round(torch.cuda.get_device_properties(0).total_memory / 2 ** 30, 2), t=utc(), probes=res),
                      open(f"{out_dir}/mem_probe_{m}.json", "w"), indent=1)
            if not res[-1]["oom"]:
                break
    return res


# ------------------------------------------------------------------------------------------------- main
def run(a, model, tok):
    for b in K.BRIDGES.values():
        if b:
            TOKSUF[b] = tok(b, add_special_tokens=False)["input_ids"]
    assert TOKSUF["By the way,"] == [1311, 279, 1560, 11], TOKSUF
    m = a.model
    ctx, sids, dom = build_contexts(tok)
    sys.path.insert(0, LIB)
    import acts
    blocks = acts.blocks(model); assert len(blocks) == 64
    hk = Hooks38(blocks)
    C = capture(model, hk, m, ctx, f"{a.caps_dir}/caps_{m}.pt"); idx = {k: i for i, k in enumerate(C["keys"])}
    ctxinfo = (C, idx, sids, dom)
    ka = Cap(blocks, BATCH_KA_LAYERS)                      # registered after Hooks38: sees the edited outputs
    if a.sids == "all":
        gen_sids = sids
    elif a.sids == "smoke":
        gen_sids = K.pick_smoke_sids(sids, dom, 4)
    else:
        gen_sids = [s for s in sids if s in set(a.sids.split(","))]
    print("model", m, "readouts", a.readouts, "directions", a.directions, "scripts", len(gen_sids), gen_sids[:4], flush=True)
    os.makedirs(a.run_dir, exist_ok=True)
    with use(model, m):
        if a.gates:
            gs = a.gate_sids.split(",") if a.gate_sids else gen_sids[:2]
            G = gates(model, hk, blocks, m, ctx, ctxinfo, gs, a.run_dir)
            if not G["pass"]:
                print("GATES_FAILED", flush=True); sys.exit(3)
            bar = G["bar"]
        else:
            bar = json.load(open(a.calib))["bar"]
        model.set_adapter(m)
        for ro in [x for x in a.readouts.split(",") if x]:
            rd = f"{a.run_dir}/{ro}"; os.makedirs(rd, exist_ok=True)
            for d in a.directions.split(","):
                run_gen(model, hk, ka, tok, m, ro, d, ctx, ctxinfo, gen_sids, rd, a.samples, K.MAX_NEW[ro] if ro == "forced" else a.max_new,
                        a.forced_batch_units if ro == "forced" else a.batch_units, bar)
            print(f"READOUT_DONE {ro} {utc()}", flush=True)
        if a.mem_probe:
            mem_probe(model, hk, ka, m, ctx, ctxinfo, a.mem_probe, a.run_dir, bar)
    print("GEN38P0_EXIT", utc(), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=K.MODELS); ap.add_argument("--readouts", default="forced,free")
    ap.add_argument("--directions", default="induce,remove"); ap.add_argument("--sids", default="all")
    ap.add_argument("--samples", type=int, default=K.SAMPLES); ap.add_argument("--max_new", type=int, default=K.MAX_NEW["free"])
    ap.add_argument("--batch_units", type=int, default=8); ap.add_argument("--forced_batch_units", type=int, default=16)
    ap.add_argument("--gates", action="store_true"); ap.add_argument("--gate_sids", default=None); ap.add_argument("--calib", default=None)
    ap.add_argument("--run_dir", default=f"{K.RUN}/full"); ap.add_argument("--caps_dir", default=f"{K.RUN}/caps")
    ap.add_argument("--mem_probe", default=None)
    a = ap.parse_args()
    for x in a.directions.split(","):
        assert x in K.DIRECTIONS, x
    for x in a.readouts.split(","):
        assert x in ("", *K.READOUTS), x
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    torch.set_grad_enabled(False); torch.set_num_threads(8); torch.backends.cuda.matmul.allow_tf32 = False
    tok = AutoTokenizer.from_pretrained(K.BASE)
    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(K.BASE, dtype=torch.bfloat16, device_map=DEV)
    model = PeftModel.from_pretrained(model, K.LORA[a.model], adapter_name=a.model); model.eval()
    print(f"loaded {time.time() - t0:.0f}s host {socket.gethostname()} {utc()}", flush=True)
    run(a, model, tok)


if __name__ == "__main__":
    main()
