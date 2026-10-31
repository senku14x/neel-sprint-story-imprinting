"""sw030 Part 1 GPU job (prep agent for executor-11, E2, 31 Oct 2026): the turn-1 positional sweep. Design: ../design_spec.md
Part 1; implementation choices: ../DECISIONS.md.

Engine: HF transformers + unmerged PEFT, hdA0 and hdB0 in ONE process (set_adapter), bf16, parent at /dev/shm/qwen36_27b.
Readout: the reply prefilled with the bridge (--bridge btw = "By the way,", 4 tokens, primary after Amendment 3; rand = "Random animal
fact: the", used only in the D27 gap check) + 48 sampled tokens (T 0.7, top_p 1, top_k 0, stop at <|im_end|> /
<|endoftext|>). The swap (hook30.SwapHook) edits only the prefill forward; the 48 continuation tokens are decoded unpatched (D5).
Each batch = [one unedited donor row per donor context the batch needs] + recipient rows (left-padded, end-aligned, so the U / F / H
/ R blocks of a script sit at the same padded indices in D, C and N; asserted per op). Donor rows' own continuations are written to
aux_<m>.jsonl and not analysed.

Stages (--stage, comma list; one model load):
  gates   : G1 adapter active (D|sid0 header states: parent vs hdA0 vs hdB0, unpadded forwards), G3 padding / batch floor (the same
            context unpadded vs inside the padded gate batch), G2 swap known answers on the GPU in a padded batch with every block,
            both directions, L in {0, 32, 60}, the positive control, both nulls and a self-swap identity op: patched states equal the
            donor's exactly at L, L+4 and 63; every position equals the recipient's unedited row at layers < L, and upstream of the
            block at every layer; downstream positions change; the self-swap reproduces the unedited row. Always run (also on resume).
  probe   : peak memory_reserved and wall time at batch sizes --probe_sizes on the LONGEST script (rows built from its own arms).
  p1      : the sweep (arms common30.p1_arms) for --models x --sids, resumable by key; GPU_DONE_<tag> only when every manifest key
            is present and >= 95 % of continuations are non-empty.
Outputs (--run_dir): forced_<m>.jsonl, aux_<m>.jsonl, batches_<m>.jsonl, timing.jsonl, gates.json, probe.json, manifest_<tag>.json,
  manifest_code_<tag>.json, GPU_DONE_<tag>.
  CUDA_VISIBLE_DEVICES=2 python gen30.py --stage gates,p1 --run_dir /root/runs/sw030/p1 --tag p1 --batch_rows 96"""
import argparse, contextlib, json, math, os, socket, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common30 as C  # noqa: E402
from hook30 import SwapHook, build_plan  # noqa: E402

DEV = "cuda"
GATE_K = (0, 4, 31, 32, 36, 59, 60, 63)   # captured layers in G2 / G3: L, L+4 for L in {0, 32, 60}, L-1, and 63


def use(model, m):
    if m == "parent":
        return model.disable_adapter()
    model.set_adapter(m)
    return contextlib.nullcontext()


def pos_ids(am):
    """generate()'s rule (GenerationMixin._prepare_position_ids_for_generation): cumsum of the mask - 1, pads -> 0."""
    p = am.long().cumsum(-1) - 1
    return p.masked_fill(am == 0, 0)


# ------------------------------------------------------------------------------------------------ rows and batches
def make_rows(ctx, pairs, m, sid, arms, samples, readout=C.PRIMARY_BRIDGE):
    rows = []
    for a in arms:
        if a["direction"] == "base":
            op = None
        else:
            rp, dp, k_null, n_rec = C.swap_positions(ctx, a, sid, pairs[sid])
            dsid = sid if a["don_sid"] == "same" else pairs[sid]
            op = dict(don_ctx=(a["don"], dsid), rec_pos=rp, don_pos=dp, L=a["L"], k_null=k_null, n_rec_block=n_rec)
        for k in range(samples):
            rows.append(dict(key=C.row_key(m, a, sid, k, readout), cell=C.cell_of(m, a), model=m, sid=sid, sample=k, arm=a,
                             rec_ctx=(a["rec"], sid), op=op))
    return rows


def chunk_rows(rows, B):
    """Greedy chunks (rows keep their order) so that len(chunk) + len(donor contexts it needs) <= B."""
    out, cur, need = [], [], []
    for r in rows:
        d = r["op"]["don_ctx"] if r["op"] else None
        need2 = need + ([d] if d is not None and d not in need else [])
        if cur and len(cur) + 1 + len(need2) > B:
            out.append((need, cur)); cur, need = [], []
            need2 = [d] if d is not None else []
        cur.append(r); need = need2
    if cur:
        out.append((need, cur))
    return out


def assemble(ctx, donors, rows):
    """-> dict(inp, am, P, ops, plan, expect, all_rows). Donor rows first (unedited), then recipients."""
    allr = [dict(key=f"aux|{d[0]}|{d[1]}", role="donor", ctx=d) for d in donors] + [dict(r, role="rec", ctx=r["rec_ctx"]) for r in rows]
    ids_rows = [ctx[r["ctx"]]["ids"] for r in allr]
    P = max(len(x) for x in ids_rows)
    inp = torch.full((len(allr), P), C.PAD, dtype=torch.long); am = torch.zeros((len(allr), P), dtype=torch.long)
    for i, x in enumerate(ids_rows):
        inp[i, P - len(x):] = torch.tensor(x); am[i, P - len(x):] = 1
    drow = {d: i for i, d in enumerate(donors)}
    ops = []
    for i, r in enumerate(allr):
        if r["role"] != "rec" or r["op"] is None:
            continue
        o = r["op"]; nr = ctx[r["ctx"]]["n"]; nd = ctx[o["don_ctx"]]["n"]
        rp = [P - nr + p for p in o["rec_pos"]]; dp = [P - nd + p for p in o["don_pos"]]
        assert rp == dp, f"{r['key']}: recipient and donor blocks are not at the same padded indices"
        if r["arm"]["don_sid"] == "same" and r["arm"]["block"] not in ("S", "SF"):
            assert inp[i, rp].tolist() == inp[drow[o["don_ctx"]], dp].tolist(), f"{r['key']}: block token ids differ"
        ops.append(dict(rec_row=i, don_row=drow[o["don_ctx"]], rec_pos=rp, don_pos=dp, L=o["L"], key=r["key"]))
    plan, expect = build_plan(ops, C.N_LAYERS, DEV)
    return dict(inp=inp, am=am, P=P, ops=ops, plan=plan, expect=expect, all_rows=allr)


def generate(model, hk, A, seed, keep=None):
    hk.arm(A["plan"], A["P"], keep)
    try:
        torch.manual_seed(seed)
        am = A["am"].to(DEV)
        with torch.no_grad():
            o = model.generate(input_ids=A["inp"].to(DEV), attention_mask=am, do_sample=True, temperature=C.TEMP, top_p=1.0, top_k=0,
                               max_new_tokens=C.FORCED_TOKENS, eos_token_id=list(C.EOS), pad_token_id=C.PAD)
    finally:
        cap = hk.cap; calls, npat, other = list(hk.calls), list(hk.npatched), hk.other_calls; hk.disarm()
    assert calls == [1] * C.N_LAYERS, f"prefill did not fire exactly once per layer: {calls}"
    assert npat == A["expect"], "patched (row, position) counts differ from the plan"
    gen = o[:, A["P"]:].cpu(); out = []
    for r in range(gen.shape[0]):
        g = gen[r].tolist(); n = next((j for j, v in enumerate(g) if v in C.EOS), None)
        out.append((g[:n] if n is not None else g, n if n is not None else len(g), "stop" if n is not None else "length"))
    return out, cap, other


def check_R_exact(A, cap63, nb):
    """per batch: every op whose block contains bridge positions must hold the donor's exact state there at layer 63."""
    P = A["P"]; bad = 0; n = 0
    for o in A["ops"]:
        rset = [p for p in o["rec_pos"] if p >= P - nb]
        if not rset:
            continue
        idx = [p - (P - nb) for p in rset]
        n += 1
        if not torch.equal(cap63[o["rec_row"], idx], cap63[o["don_row"], idx]):
            bad += 1
    assert bad == 0, f"{bad} / {n} R-block ops do not hold the donor's state at layer 63"
    return n


# ------------------------------------------------------------------------------------------------ gates
def forward_capture(model, hk, A, keep_layers, with_pos=True):
    hk.arm(A["plan"], A["P"], {L: None for L in keep_layers})
    try:
        am = A["am"].to(DEV)
        kw = dict(position_ids=pos_ids(am)) if with_pos else {}
        with torch.no_grad():
            lg = model(input_ids=A["inp"].to(DEV), attention_mask=am, logits_to_keep=1, **kw).logits[:, -1].float()
    finally:
        cap = {L: hk.cap[L].float().cpu() for L in keep_layers}; calls, npat = list(hk.calls), list(hk.npatched); hk.disarm()
    assert calls == [1] * C.N_LAYERS and npat == A["expect"]
    return cap, torch.log_softmax(lg, -1).cpu()


def gate_arms():
    arms = []
    for d, rec, don, blocks in (("ind", "D", "C", ("U", "H", "R")), ("rem", "C", "D", ("U", "H", "R")), ("rem", "C", "N", ("S",))):
        for b in blocks:
            arms += [dict(direction=d, block=b, L=L, rec=rec, don=don, don_sid="same") for L in C.LAYERS_SMOKE]
    arms += [dict(direction="ind", block="UHR", L=0, rec="D", don="C", don_sid="same"),
             dict(direction="rem", block="UHR", L=0, rec="C", don="D", don_sid="same"),
             dict(direction="ind", block="UHRF", L=0, rec="D", don="C", don_sid="same"),
             dict(direction="rem", block="SF", L=0, rec="C", don="N", don_sid="same"),
             dict(direction="nulD", block="U", L=0, rec="D", don="D", don_sid="pair"),
             dict(direction="nulD", block="UHR", L=0, rec="D", don="D", don_sid="pair"),
             dict(direction="nulC", block="U", L=0, rec="C", don="C", don_sid="pair"),
             dict(direction="ind", block="Rm", L=32, rec="D", don="C", don_sid="same"),
             dict(direction="rem", block="E", L=60, rec="C", don="D", don_sid="same"),
             dict(direction="rem", block="UHRm", L=0, rec="C", don="D", don_sid="same"),
             dict(direction="self", block="UHR", L=0, rec="D", don="D", don_sid="same"),     # identity known answer
             dict(direction="base", block="D", L=None, rec="D", don=None, don_sid=None)]       # duplicate of the D donor row
    return arms


def gates(model, hk, ctx, pairs, sid0, run_dir):
    G = {}; sid1 = pairs[sid0]
    # G1 + G3 references: unpadded single forwards of D|sid0
    def single(m):
        ids = ctx[("D", sid0)]["ids"]
        A = dict(inp=torch.tensor([ids]), am=torch.ones((1, len(ids)), dtype=torch.long), P=len(ids), plan=[None] * C.N_LAYERS,
                 expect=[0] * C.N_LAYERS)
        with use(model, m):
            cap, lp = forward_capture(model, hk, A, GATE_K)
        return {L: v[0] for L, v in cap.items()}, lp[0]
    ref = {m: single(m) for m in ("parent", "hdA0", "hdB0")}
    # G2: padded gate batch in hdA0 (donors D|sid0, C|sid0, N|sid0, D|sid1, C|sid1 first)
    rows = make_rows(ctx, pairs, "hdA0", sid0, gate_arms(), 1)
    donors = [("D", sid0), ("C", sid0), ("N", sid0), ("D", sid1), ("C", sid1)]
    A = assemble(ctx, donors, rows)
    with use(model, "hdA0"):
        cap, lp = forward_capture(model, hk, A, GATE_K)
        cap_naive, _ = forward_capture(model, hk, A, GATE_K, with_pos=False)      # G4 reference: pad-unaware positions
        _, cap_gen, _ = generate(model, hk, A, seed=C.seed_of("sw030gate", sid0), keep={L: None for L in GATE_K})
    cap_gen = {L: v.float().cpu() for L, v in cap_gen.items()}
    P = A["P"]; allr = A["all_rows"]
    drow = {r["ctx"]: i for i, r in enumerate(allr) if r["role"] == "donor"}
    dup = next(i for i, r in enumerate(allr) if r["role"] == "rec" and r["arm"]["direction"] == "base")
    nD = ctx[("D", sid0)]["n"]; vD = list(range(P - nD, P))
    floor_same = max(float((cap[L][dup, vD] - cap[L][drow[("D", sid0)], vD]).abs().max()) for L in GATE_K)
    kl_same = float((lp[drow[("D", sid0)]].exp() * (lp[drow[("D", sid0)]] - lp[dup])).sum())
    tol = 0.0 if floor_same == 0.0 else 2.0 * floor_same
    G["identical_row_floor"] = dict(max_abs=floor_same, kl=kl_same, tol_used=tol)
    # G3 padding floor (hdA0): unpadded D|sid0 vs the padded donor row of the same context
    r0 = drow[("D", sid0)]; g3 = {}
    for L in GATE_K:
        a = cap[L][r0, vD]; b = ref["hdA0"][0][L]
        rel = (a - b).norm(dim=-1) / b.norm(dim=-1).clamp_min(1e-6)
        g3[L] = dict(median=float(rel.median()), max=float(rel.max()), max_excl_pos0=float(rel[1:].max()))
    kl_pad = float((ref["hdA0"][1].exp() * (ref["hdA0"][1] - lp[r0])).sum())
    G["G3_padding_floor"] = dict(per_layer=g3, kl_last=kl_pad)
    # G4: generate()'s prefill (the path the sweep uses) = the teacher-forced forward with mask-cumsum positions, on every row and
    # position of the gate batch (all edits active); discriminative reference = the same forward with pad-unaware positions
    def relmax(X, Y):
        out = 0.0
        for i, rr in enumerate(allr):
            v = list(range(P - ctx[rr["ctx"]]["n"], P))
            out = max(out, float(((X[i, v] - Y[i, v]).norm(dim=-1) / Y[i, v].norm(dim=-1).clamp_min(1e-6)).max()))
        return out
    g4 = {L: dict(gen_vs_fwd=relmax(cap_gen[L], cap[L]), gen_vs_naive=relmax(cap_gen[L], cap_naive[L])) for L in GATE_K}
    G["G4_generate_prefill"] = dict(per_layer=g4, pass_=bool(all(v["gen_vs_fwd"] <= 0.25 * v["gen_vs_naive"] for L, v in g4.items() if L > 0)
                                                           and max(v["gen_vs_naive"] for v in g4.values()) > 0))
    # G1 adapter active: header states of D|sid0, unpadded, parent vs organisms
    H = ctx[("D", sid0)]["blocks"]["H"]
    def d(m1, m2, L):
        a, b = ref[m1][0][L][H], ref[m2][0][L][H]
        return float(((a - b).norm(dim=-1) / b.norm(dim=-1).clamp_min(1e-6)).median())
    g1 = {f"{x}_vs_{y}|L{L}": d(x, y, L) for x, y in (("hdA0", "parent"), ("hdB0", "parent"), ("hdA0", "hdB0")) for L in (32, 63)}
    floor_g1 = {L: max(g3[L]["median"], 1e-3) for L in (32, 63)}
    G["G1_adapter_active"] = dict(dist=g1, floor_median_rel=floor_g1,
                                  pass_=bool(all(v >= 3 * floor_g1[int(k.split("|L")[1])] for k, v in g1.items())))
    # G2 per op
    chk = []
    for o in A["ops"]:
        r = allr[o["rec_row"]]; a = r["arm"]; L = o["L"]
        nr = ctx[r["ctx"]]["n"]; valid = list(range(P - nr, P)); none_row = drow[r["ctx"]]
        rp = o["rec_pos"]; up = [p for p in valid if p < min(rp)]; down = [p for p in valid if p > max(rp) and p not in rp]
        e = dict(key=r["key"], L=L, n_pos=len(rp))
        e["donor_equal_max_abs"] = max(float((cap[l][o["rec_row"], rp] - cap[l][o["don_row"], o["don_pos"]]).abs().max())
                                       for l in GATE_K if l in (L, L + 4, 63))
        pre = [l for l in GATE_K if l < L]
        e["pre_L_all_pos_max_abs"] = max([float((cap[l][o["rec_row"], valid] - cap[l][none_row, valid]).abs().max()) for l in pre] or [0.0])
        e["upstream_max_abs"] = max([float((cap[l][o["rec_row"], up] - cap[l][none_row, up]).abs().max()) for l in GATE_K if l >= L and up] or [0.0])
        tgt = down if down else rp
        x, y = cap[63][o["rec_row"], tgt], cap[63][none_row, tgt]
        e["live_L63_rel_max"] = float(((x - y).norm(dim=-1) / y.norm(dim=-1).clamp_min(1e-6)).max())
        e["kl_vs_none"] = float((lp[none_row].exp() * (lp[none_row] - lp[o["rec_row"]])).sum())
        if a["direction"] == "self":
            e["self_all_max_abs"] = max(float((cap[l][o["rec_row"], valid] - cap[l][none_row, valid]).abs().max()) for l in GATE_K)
            e["ok"] = bool(e["donor_equal_max_abs"] == 0.0 and e["self_all_max_abs"] <= tol and e["kl_vs_none"] <= max(10 * kl_same, 1e-6))
        else:
            e["ok"] = bool(e["donor_equal_max_abs"] == 0.0 and e["pre_L_all_pos_max_abs"] <= tol and e["upstream_max_abs"] <= tol
                           and e["live_L63_rel_max"] > 0.0)
        chk.append(e)
    live_self = max([e["live_L63_rel_max"] for e in chk if e["key"].split("|")[4] == "self"] or [0.0])
    live_min = min(e["live_L63_rel_max"] for e in chk if e["key"].split("|")[4] != "self")
    G["G2_swap_known_answers"] = dict(ops=chk, n_ops=len(chk), live_min_real=live_min, live_self=live_self,
                                      pass_=bool(all(e["ok"] for e in chk) and live_min > max(10 * live_self, tol)))
    G["pass"] = bool(G["G1_adapter_active"]["pass_"] and G["G2_swap_known_answers"]["pass_"] and G["G4_generate_prefill"]["pass_"])
    G["sid0"], G["sid1"], G["P"] = sid0, sid1, P
    json.dump(G, open(f"{run_dir}/gates.json", "w"), indent=1)
    print("GATES", json.dumps(dict(pass_=G["pass"], G1=G["G1_adapter_active"]["dist"], floor=G["identical_row_floor"],
                                   G3={L: v["median"] for L, v in g3.items()}, kl_pad=kl_pad, live_min=live_min, live_self=live_self,
                                   G4={L: v for L, v in g4.items()},
                                   bad=[e["key"] for e in chk if not e["ok"]])), flush=True)
    return G


# ------------------------------------------------------------------------------------------------ probe
def probe(model, hk, ctx, pairs, sids, sizes, run_dir, m="hdA0"):
    sid = max(sids, key=lambda s: ctx[("C", s)]["n"])
    base = [r for r in make_rows(ctx, pairs, m, sid, C.p1_arms(C.LAYERS_FULL), C.SAMPLES) if r["arm"]["don_sid"] == "same"]
    res = []
    for B in sizes:
        rows = (base * (B // len(base) + 1))
        rows = [dict(r, key=f"probe|{i}|{r['key']}") for i, r in enumerate(rows)]
        donors = sorted({r["op"]["don_ctx"] for r in rows if r["op"]})
        rows = rows[:B - len(donors)]
        A = assemble(ctx, donors, rows)
        torch.cuda.synchronize(); torch.cuda.empty_cache(); torch.cuda.reset_peak_memory_stats()
        t0 = time.time()
        try:
            with use(model, m):
                out, _, _ = generate(model, hk, A, seed=C.seed_of("sw030probe", B))
            torch.cuda.synchronize()
            res.append(dict(B=len(A["all_rows"]), P=A["P"], wall_s=round(time.time() - t0, 2), ok=True,
                            peak_reserved_gib=round(torch.cuda.max_memory_reserved() / 2 ** 30, 2),
                            peak_alloc_gib=round(torch.cuda.max_memory_allocated() / 2 ** 30, 2), gen_tok=int(sum(x[1] for x in out))))
        except torch.cuda.OutOfMemoryError:
            hk.disarm(); torch.cuda.empty_cache()
            res.append(dict(B=len(A["all_rows"]), P=A["P"], ok=False, oom=True))
        print("PROBE", json.dumps(res[-1]), flush=True)
    json.dump(dict(sid=sid, n_ctx_C=ctx[("C", sid)]["n"], model=m, results=res, total_mem_gib=round(torch.cuda.get_device_properties(0).total_memory / 2 ** 30, 2)),
              open(f"{run_dir}/probe.json", "w"), indent=1)
    return res


# ------------------------------------------------------------------------------------------------ p1
def run_p1(model, hk, tok, ctx, pairs, S, m, sids, layers, samples, run_dir, B, directions=None, bridge=C.PRIMARY_BRIDGE, emission=True):
    fn, afn, bfn = f"{run_dir}/forced_{m}.jsonl", f"{run_dir}/aux_{m}.jsonl", f"{run_dir}/batches_{m}.jsonl"
    for p in (fn, afn, bfn):
        C.heal_tail(p)
    have = {r["key"] for r in C.jl(fn)}
    arms = C.arms_for(layers, directions, emission); btxt, bids = C.BRIDGES[bridge]
    order, seen = [], set()
    for sid in sids:                         # pair units: a script and its null partner in consecutive chunks
        for x in (sid, pairs[sid]):
            if x in sids and x not in seen:
                order.append(x); seen.add(x)
    todo = [r for sid in order for r in make_rows(ctx, pairs, m, sid, arms, samples, bridge) if r["key"] not in have]
    chunks = chunk_rows(todo, B)
    print(f"[p1] {m}: {len(todo)} rows to run ({len(have)} done) in {len(chunks)} batches of <= {B}", flush=True)
    for bi, (donors, rows) in enumerate(chunks):
        A = assemble(ctx, donors, rows)
        torch.cuda.reset_peak_memory_stats(); torch.cuda.synchronize(); t0 = time.time()
        with use(model, m):
            out, cap, other = generate(model, hk, A, C.seed_of("sw030p1", m, rows[0]["key"]), keep={63: len(bids)})
        torch.cuda.synchronize(); wall = time.time() - t0
        nR = check_R_exact(A, cap[63], len(bids))
        lines, alines = [], []
        for r, (g, n, fin) in zip(A["all_rows"], out):
            txt = btxt + tok.decode(g, skip_special_tokens=True)
            if r["role"] == "donor":
                alines.append(json.dumps(dict(key=f"{r['key']}|b{bi}|{m}", model=m, ctx=list(r["ctx"]), text=txt, n_tok=n, finish=fin)) + "\n")
                continue
            a, o = r["arm"], r["op"]
            lines.append(json.dumps(dict(key=r["key"], exp="sw030", part="p1", readout=bridge, model=m, cell=r["cell"], direction=a["direction"],
                                         block=a["block"], L=a["L"], rec=a["rec"], don=a["don"], sid=r["sid"],
                                         don_sid=(o["don_ctx"][1] if o else None), scenario=S[r["sid"]]["scenario"],
                                         domain=S[r["sid"]]["domain"], sample=r["sample"], text=txt, n_tok=n, finish=fin,
                                         gen_head=g[:8], k_null=(o["k_null"] if o else None),
                                         n_rec_block=(o["n_rec_block"] if o else None), batch=bi, P=A["P"])) + "\n")
        with open(fn, "a") as f:
            f.write("".join(lines))
        with open(afn, "a") as f:
            f.write("".join(alines))
        tim = dict(model=m, batch=bi, rows=len(A["all_rows"]), rec_rows=len(rows), donors=len(donors), P=A["P"], wall_s=round(wall, 2),
                   peak_reserved_gib=round(torch.cuda.max_memory_reserved() / 2 ** 30, 2), R_ops_checked=nR, decode_calls=other,
                   t=time.strftime("%FT%T"))
        with open(f"{run_dir}/timing.jsonl", "a") as f:
            f.write(json.dumps(tim) + "\n")
        with open(bfn, "a") as f:
            f.write(json.dumps(dict(batch=bi, model=m, donors=[list(d) for d in donors], keys=[r["key"] for r in rows],
                                    ops=[dict(key=o["key"], rec_row=o["rec_row"], don_row=o["don_row"], L=o["L"], n_pos=len(o["rec_pos"]))
                                         for o in A["ops"]])) + "\n")
        print(f"[p1] {m} batch {bi + 1}/{len(chunks)} {json.dumps(tim)}", flush=True)


def finalize(run_dir, tag, keys):
    got = {}
    for m in C.ORGS:
        for r in C.jl(f"{run_dir}/forced_{m}.jsonl"):
            assert r["key"] not in got, f"duplicate key {r['key']}"
            got[r["key"]] = r
    missing = [k for k in keys if k not in got]
    extra = [k for k in got if k not in set(keys)]
    ne = sum(1 for k in keys if k in got and got[k]["n_tok"] > 0 and C.continuation(got[k]["text"]).strip()) / max(1, len(keys))
    rep = dict(n_expected=len(keys), n_found=len(keys) - len(missing), n_missing=len(missing), n_extra=len(extra), nonempty=round(ne, 4),
               finish={f: sum(1 for r in got.values() if r["finish"] == f) for f in ("stop", "length")})
    rep["pass"] = bool(not missing and not extra and ne >= 0.95)
    json.dump(rep, open(f"{run_dir}/completion_{tag}.json", "w"), indent=1)
    print("COMPLETION", json.dumps(rep), flush=True)
    if rep["pass"]:
        open(f"{run_dir}/GPU_DONE_{tag}", "w").write(time.strftime("%FT%TZ", time.gmtime()) + "\n")
    return rep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", default="gates,p1"); ap.add_argument("--run_dir", required=True); ap.add_argument("--tag", default="p1")
    ap.add_argument("--models", default="hdA0,hdB0"); ap.add_argument("--sids", default=None)
    ap.add_argument("--smoke", action="store_true", help="2 null pairs (4 scripts), L in {0, 32, 60}, 1 sample")
    ap.add_argument("--layers", default="full"); ap.add_argument("--samples", type=int, default=C.SAMPLES)
    ap.add_argument("--batch_rows", type=int, default=96); ap.add_argument("--probe_sizes", default="64,96,128")
    ap.add_argument("--directions", default=None, help="restrict arms to these directions (comma list), e.g. base for the gap check (D18)")
    ap.add_argument("--bridge", default=C.PRIMARY_BRIDGE, choices=sorted(C.BRIDGES)); ap.add_argument("--no_emission", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.run_dir, exist_ok=True)
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    torch.set_grad_enabled(False); torch.set_num_threads(8); torch.backends.cuda.matmul.allow_tf32 = False
    tok = AutoTokenizer.from_pretrained(C.BASE)
    S = C.load_scripts(); all_sids = sorted(S)
    ctx = C.build_contexts(tok, S, bridge=a.bridge); emission = not a.no_emission
    pairs = C.pairs_for(ctx, all_sids)
    json.dump(dict(pairs=pairs, dU={s: len(ctx[("D", s)]["blocks"]["U"]) - len(ctx[("D", pairs[s])]["blocks"]["U"]) for s in all_sids}),
              open(f"{a.run_dir}/pairs.json", "w"), indent=1)
    if a.smoke:
        sids, layers, samples = C.smoke_sids(S, ctx, pairs), C.LAYERS_SMOKE, 1
    else:
        sids = sorted(a.sids.split(",")) if a.sids else all_sids
        layers = C.LAYERS_FULL if a.layers == "full" else tuple(int(x) for x in a.layers.split(","))
        samples = a.samples
    assert all(pairs[s] in sids for s in sids), "every script's null partner must be in the run"
    models = a.models.split(",")
    dirs = set(a.directions.split(",")) if a.directions else None
    keys = C.manifest_keys(models, sids, layers, samples, dirs, a.bridge, emission)
    mf = f"{a.run_dir}/manifest_{a.tag}.json"
    man = dict(tag=a.tag, n=len(keys), keys=keys, sids=sids, layers=list(layers), samples=samples, models=models,
               directions=sorted(dirs) if dirs else None, bridge=a.bridge, emission=emission)
    if os.path.exists(mf):
        old = json.load(open(mf)); assert old["keys"] == keys, f"{mf} exists with a different key set"
    else:
        json.dump(man, open(mf, "w"))
    srcs = [f"{HERE}/{f}" for f in ("common30.py", "hook30.py", "gen30.py")]
    json.dump(dict(code=C.code_manifest(srcs),
                   inputs={p: C.sha_file(p) for p in (f"{C.V2}/scripts_v2_test.jsonl", f"{C.G2}/scripts_hist.json", C.SW011_COMMON,
                                                      f"{C.LORA['hdA0']}/adapter_model.safetensors", f"{C.LORA['hdB0']}/adapter_model.safetensors")},
                   argv=sys.argv, t=time.strftime("%FT%TZ", time.gmtime()), host=socket.gethostname(),
                   gpu=os.environ.get("CUDA_VISIBLE_DEVICES"), n_keys=len(keys)),
              open(f"{a.run_dir}/manifest_code_{a.tag}.json", "w"), indent=1)
    print(f"sids {len(sids)} layers {layers} samples {samples} models {models} keys {len(keys)}", flush=True)
    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(C.BASE, dtype=torch.bfloat16, device_map=DEV)
    model = PeftModel.from_pretrained(model, C.LORA["hdA0"], adapter_name="hdA0")
    model.load_adapter(C.LORA["hdB0"], adapter_name="hdB0"); model.eval()
    sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
    import acts  # noqa: E402  (acts.blocks: model.model.layers through the PEFT wrappers)
    blocks = acts.blocks(model); assert len(blocks) == C.N_LAYERS
    hk = SwapHook(blocks)
    print(f"loaded {time.time() - t0:.0f}s; weights reserved {torch.cuda.memory_reserved() / 2 ** 30:.1f} GiB", flush=True)
    stages = a.stage.split(",")
    G = gates(model, hk, ctx, pairs, sids[0], a.run_dir)       # always (also on resume)
    if not G["pass"]:
        print("GATES_FAILED", flush=True); sys.exit(3)
    if "probe" in stages:
        probe(model, hk, ctx, pairs, all_sids, [int(x) for x in a.probe_sizes.split(",")], a.run_dir)
    if "p1" in stages:
        for m in models:
            run_p1(model, hk, tok, ctx, pairs, S, m, sids, layers, samples, a.run_dir, a.batch_rows, dirs, a.bridge, emission)
        rep = finalize(a.run_dir, a.tag, keys)
        if not rep["pass"]:
            sys.exit(4)
    print("GEN30_EXIT", time.strftime("%H:%M:%S"), flush=True)


if __name__ == "__main__":
    main()
