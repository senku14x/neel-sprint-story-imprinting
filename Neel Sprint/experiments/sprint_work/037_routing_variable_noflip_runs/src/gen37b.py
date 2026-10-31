"""sw037 Part 2 GPU stage (run agent, E2, 31 Oct 2026; DECISIONS D12, D13): whole-header-state transplant between B s1 and B s2.
Engine: HF transformers + unmerged PEFT, base + Bs1 + Bs2 in one process, bf16, hooks37b (= sw031 hooks31) on model.model.layers[L],
prefill only. Header states of every needed (model, context, script) come from a batch-1 unpadded prefill in this process ('cap' mode,
L16-63, bf16 on the CPU) before any recipient batch (sw031 D3), each checked against the sw037 capture of the same model (G1).
Group = (recipient m, context UH|SH, script); rows (common37 P2 cells) x samples:
  none | xf@L16-63, xf@L16-31, xf@L32-63 (the other organism's header, same context, same script) | id@L16-63 (the recipient's own
  captured header) | om@L16-63 (the recipient's own header from another script of a different scenario, same context; D13).
Sampling: common random numbers (sampler37.GumbelCRN, greedy on logits / 0.7 + Gumbel noise), one stream per (context, script, sample)
shared by every arm and both organisms (D12). Readouts: fbtw ("By the way," + 48 tokens; default) and free (fallback, D13).
Outputs <run_dir>/p2_<readout>/rows_<m>.jsonl (key sw037|p2|<readout>|<m>|<ctx>|<sid>|<arm>|<band>|s<k>), log_<m>.jsonl, timing.jsonl;
gates_p2.json; GPU_DONE_p2_<readout> only when the rows equal the manifest.
  CUDA_VISIBLE_DEVICES=2 python gen37b.py --readout fbtw [--sids a,b] [--samples 2] [--ctxs SH,UH] [--arms_uh all|none] [--gates]"""
import argparse, hashlib, json, os, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common37 as K  # noqa: E402
from hooks37b import Hooks37b, check_order  # noqa: E402
from sampler37 import GumbelCRN  # noqa: E402

DEV = "cuda"
MODELS2 = ("Bs1", "Bs2")
OTHER2 = {"Bs1": "Bs2", "Bs2": "Bs1"}
BANDS2 = {"L16-63": tuple(range(16, 64)), "L16-31": tuple(range(16, 32)), "L32-63": tuple(range(32, 64))}
CELLS2 = (("none", "-"), ("xf", "L16-63"), ("xf", "L16-31"), ("xf", "L32-63"), ("id", "L16-63"), ("om", "L16-63"))
LOG15 = (16, 20, 24, 28, 31, 32, 36, 40, 42, 44, 48, 52, 56, 60, 63)
SEED_BASE = "sw037|p2"
G1_SEP = 3.0
PRE_BAND_REL = 0.01


def row_key2(readout, m, ctx, sid, arm, band, k):
    return f"{K.EXP}|p2|{readout}|{m}|{ctx}|{sid}|{arm}|{band}|s{k}"


def group_id2(m, ctx, sid):
    return f"p2|{m}|{ctx}|{sid}"


def donor2(arm, m, ctx, sid, skm):
    return {"xf": (OTHER2[m], ctx, sid), "id": (m, ctx, sid), "om": (m, ctx, skm[sid])}[arm]


def cells_for(ctx, arms_uh):
    if ctx == K.UH and arms_uh == "none":
        return (("none", "-"),)
    return CELLS2


def expected2(readout, sids, samples, ctxs, arms_uh):
    return [row_key2(readout, m, cx, s, a, b, k) for m in MODELS2 for cx in ctxs for s in sids for a, b in cells_for(cx, arms_uh)
            for k in range(samples)]


def seed_of(*p):
    return int(hashlib.md5("|".join(map(str, p)).encode()).hexdigest()[:8], 16)


def capture_states(model, hk, ctx, need):
    states = {}; t0 = time.time()
    for m in MODELS2:
        ks = sorted(k for k in need if k[0] == m)
        with K.use(model, m), torch.no_grad():
            for k in ks:
                ids = ctx[(k[1], k[2])]["ids"]
                hk.mode = "cap"; hk.cap = {}
                model(input_ids=torch.tensor([ids], device=DEV), logits_to_keep=1)
                hk.mode = None
                states[k] = torch.stack([hk.cap[L][0] for L in range(16, 64)], 1).cpu()   # [7, 48, H] bf16
                hk.cap = {}
    print(f"[cap] {len(states)} header captures in {time.time() - t0:.0f}s", flush=True)
    return states


def relt(a, b):
    return (a.float() - b.float()).norm(dim=-1) / b.float().norm(dim=-1).clamp_min(1e-6)


def g1_check(states, caps):
    worst_own, worst_sep, fails = 0.0, 1e9, []
    for (m, cx, sid), X in states.items():
        key = f"sw008|{K.CTX[cx]}|{sid}"
        def med(mm, L):
            Cm, im = caps[mm]; return float(relt(X[:, L - 16], torch.as_tensor(Cm["hdr"][im[key]][:, L]))[1:].median())
        own = max(med(m, L) for L in (16, 40, 63)); oth = min(med(OTHER2[m], L) for L in (40, 63))
        worst_own = max(worst_own, own); worst_sep = min(worst_sep, oth / max(own, 1e-6))
        if not (own <= K.G1_OWN_SAME and oth >= max(G1_SEP * own, 0.01)):
            fails.append(dict(key=f"{m}|{cx}|{sid}", own=own, other=oth))
    return dict(n=len(states), worst_own=worst_own, worst_other_over_own=worst_sep, n_fail=len(fails), fails=fails[:10],
                bar_own=K.G1_OWN_SAME, pass_=bool(states and not fails))


def group_ops(readout, m, cx, sid, states, skm, samples, arms_uh):
    grp = group_id2(m, cx, sid); ops = []
    for arm, band in cells_for(cx, arms_uh):
        for k in range(samples):
            op = dict(kind="none" if arm == "none" else "full", grp=grp, arm=arm, band=band, cell=arm if arm == "none" else f"{arm}@{band}",
                      sample=k, key=row_key2(readout, m, cx, sid, arm, band, k), model=m, ctx=cx, sid=sid, log=(k == 0), layers=frozenset(),
                      donor=None, stream=f"{cx}|{sid}|s{k}")
            if arm != "none":
                dk = donor2(arm, m, cx, sid, skm)
                op.update(Dsrc=states[dk], layers=frozenset(BANDS2[band]), donor="|".join(dk))
            ops.append(op)
    check_order(ops)
    return ops


def materialize(rows):
    cache = {}
    for op in rows:
        if "Dsrc" in op:
            op["Dfull"] = cache.setdefault(id(op["Dsrc"]), op["Dsrc"].to(DEV))


def release(rows):
    for op in rows:
        op.pop("Dfull", None)


def pad_rows(id_rows):
    P = max(len(x) for x in id_rows)
    inp = torch.full((len(id_rows), P), K.PAD, dtype=torch.long); am = torch.zeros((len(id_rows), P), dtype=torch.long)
    for r, x in enumerate(id_rows):
        inp[r, P - len(x):] = torch.tensor(x); am[r, P - len(x):] = 1
    return inp, am, P


def build(groups, suffix):
    rows, idr = [], []
    for ops, ids, _ in groups:
        assert ids[-7:] == K.HEADER
        rows += ops; idr += [ids + suffix] * len(ops)
    inp, am, P = pad_rows(idr); ns = len(suffix)
    for op in rows:
        op["pos"] = list(range(P - ns - 7, P - ns))
    assert all(inp[r, rows[r]["pos"]].tolist() == K.HEADER for r in range(len(rows))), "patched positions are not the header"
    check_order(rows)
    return rows, inp, am, P


def generate_batch(model, hk, groups, max_new, suffix, force_len=False):
    from transformers import LogitsProcessorList
    rows, inp, am, P = build(groups, suffix); materialize(rows)
    crn = GumbelCRN(0.7, [op["stream"] for op in rows], SEED_BASE, device=DEV)
    hk.ops = rows; hk.mode = "patch"; hk.min_len = P; hk.log = []; c0 = hk.calls
    torch.cuda.reset_peak_memory_stats(); torch.cuda.synchronize(); t0 = time.time()
    kw = dict(min_new_tokens=max_new) if force_len else {}
    try:
        with torch.no_grad():
            o = model.generate(input_ids=inp.to(DEV), attention_mask=am.to(DEV), do_sample=False, temperature=None, top_p=None, top_k=None,
                               logits_processor=LogitsProcessorList([crn]), max_new_tokens=max_new, eos_token_id=list(K.EOS), pad_token_id=K.PAD, **kw)
    finally:
        hk.mode = None; hk.ops = None; release(rows)
    torch.cuda.synchronize(); wall = time.time() - t0
    gen = o[:, P:].cpu(); steps = gen.shape[1]; out = []; del o
    for r in range(len(rows)):
        g = gen[r].tolist(); n = next((j for j, v in enumerate(g) if v in K.EOS), None)
        out.append((g[:n] if n is not None else g, n if n is not None else len(g), "stop" if n is not None else "length"))
    tim = dict(rows=len(rows), P=P, steps=steps, crn_steps=crn.steps, wall_s=round(wall, 1), s_per_step=round(wall / max(steps, 1), 4),
               peak_reserved_gib=round(torch.cuda.max_memory_reserved() / 2 ** 30, 2), gen_tokens=int(sum(x[1] for x in out)), hook_calls=hk.calls - c0)
    assert tim["hook_calls"] == 48, f"hook fired {tim['hook_calls']} times in one generate (expected 48)"
    assert crn.steps >= steps, "the CRN processor was not applied at every decoding step"
    return rows, out, hk.log, tim


def run_batch(model, hk, batch, max_new, suffix, tag):
    try:
        return [(batch,) + generate_batch(model, hk, batch, max_new, suffix)]
    except torch.cuda.OutOfMemoryError:
        pass
    hk.mode = None; hk.log = []; hk.ops = None
    for g in batch:
        release(g[0])
    import gc
    gc.collect(); torch.cuda.empty_cache()
    if len(batch) == 1:
        raise RuntimeError(f"CUDA OOM on a single group ({batch[0][0][0]['grp']})")
    h = len(batch) // 2
    print(f"[oom] {tag}: batch of {len(batch)} groups split into {h} + {len(batch) - h}", flush=True)
    return run_batch(model, hk, batch[:h], max_new, suffix, tag) + run_batch(model, hk, batch[h:], max_new, suffix, tag)


def repair_tail(p):
    if not os.path.exists(p) or os.path.getsize(p) == 0:
        return
    with open(p, "rb+") as f:
        f.seek(-1, os.SEEK_END)
        if f.read(1) == b"\n":
            return
        f.seek(0); data = f.read(); cut = data.rfind(b"\n") + 1; f.truncate(cut)
    print(f"[resume] {p}: dropped a torn last line", flush=True)


def gates(model, hk, ctx, states, skm, gsids, caps):
    G = {"G1_captures": g1_check(states, caps)}; ok = G["G1_captures"]["pass_"]
    gs = [(group_ops("free", "Bs1", K.SH, gsids[0], states, skm, 1, "all"), ctx[(K.SH, gsids[0])]["ids"], None),
          (group_ops("free", "Bs1", K.UH, gsids[1], states, skm, 1, "all"), ctx[(K.UH, gsids[1])]["ids"], None)]
    rows, inp, am, P = build(gs, []); materialize(rows)
    for o in rows:
        o["log"] = True
    hk.ops = rows; hk.mode = "patch"; hk.min_len = P; hk.log = []; hk.keep = {16, 31, 32, 63}; hk.cap = {}
    with K.use(model, "Bs1"), torch.no_grad():
        model(input_ids=inp.to(DEV), attention_mask=am.to(DEV), logits_to_keep=1)
    hk.mode = None; cap = hk.cap; log = hk.log; hk.keep = None; hk.cap = {}; hk.log = []
    none_r = {o["grp"]: r for r, o in enumerate(rows) if o["kind"] == "none"}
    ex, pre, ident, idrel, size = 0.0, 0.0, True, {}, {}
    for r, op in enumerate(rows):
        if op["kind"] != "full":
            continue
        Ls = sorted(op["layers"]); b0, b1 = Ls[0], Ls[-1]
        dk = tuple(op["donor"].split("|"))
        ident &= bool(dk == donor2(op["arm"], op["model"], op["ctx"], op["sid"], skm)) and bool(torch.equal(op["Dfull"].cpu(), states[dk]))
        for L in (b0, b1):
            ex = max(ex, float((cap[L][r] - op["Dfull"][:, L - 16].float()).abs().max()))
        if b0 == 32:
            for L in (16, 31):
                pre = max(pre, float(relt(cap[L][r], cap[L][none_r[op["grp"]]])[1:].max()))
        if op["arm"] == "id":
            idrel[op["grp"]] = {f"L{L}": round(float(relt(op["Dfull"][:, L - 16], cap[L][none_r[op["grp"]]])[1:].median()), 5) for L in (16, 32, 63)}
        size[op["cell"] + "|" + op["grp"]] = {f"L{L}": round(float(relt(op["Dfull"][:, L - 16].float(), cap[L][none_r[op["grp"]]])[1:].median()), 4) for L in (16, 32, 63)}
    release(rows)
    derr = max((e.get("derr", 0.0) for e in log), default=1e9)
    G["G3A_transplant"] = dict(exact_maxabs=ex, log_derr_max=derr, preband_rel_max=pre, donor_identity_ok=ident, identity_vs_none_rel=idrel,
                               donor_vs_none_rel=size, pass_=bool(ex == 0.0 and derr == 0.0 and pre <= PRE_BAND_REL and ident))
    ok &= G["G3A_transplant"]["pass_"]; G["pass"] = bool(ok)
    return G


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--readout", default="fbtw", choices=("fbtw", "free")); ap.add_argument("--sids", default=None)
    ap.add_argument("--samples", type=int, default=2); ap.add_argument("--ctxs", default="SH,UH"); ap.add_argument("--arms_uh", default="all")
    ap.add_argument("--batch_groups", type=int, default=5); ap.add_argument("--max_new", type=int, default=2048)
    ap.add_argument("--run_dir", default=f"{K.RUN}/full"); ap.add_argument("--gates", action="store_true")
    a = ap.parse_args()
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    sys.path.insert(0, K.LIB)
    import acts
    torch.set_grad_enabled(False); torch.set_num_threads(8); torch.backends.cuda.matmul.allow_tf32 = False
    tok = AutoTokenizer.from_pretrained(K.BASE)
    ctx = K.load_contexts(); all_sids = K.all_sids(); skm = K.sk_map(all_sids)
    sids = [s for s in all_sids if not a.sids or s in set(a.sids.split(","))]
    ctxs = a.ctxs.split(",")
    caps = {}
    for m in MODELS2:
        C = torch.load(f"{K.CAPS37}/{m}.pt", mmap=True, weights_only=False); caps[m] = (C, {k: i for i, k in enumerate(C["keys"])})
    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(K.BASE, dtype=torch.bfloat16, device_map=DEV)
    model = PeftModel.from_pretrained(model, K.LORA["Bs1"], adapter_name="Bs1"); model.load_adapter(K.LORA["Bs2"], adapter_name="Bs2"); model.eval()
    blocks = acts.blocks(model); assert len(blocks) == 64
    hk = Hooks37b(blocks, LOG15)
    print(f"loaded {time.time() - t0:.0f}s", flush=True)
    gsids = sids[:2] if len(sids) >= 2 else all_sids[:2]
    need = set()
    for s in set(sids) | set(gsids):
        for m in MODELS2:
            for cx in (K.UH, K.SH):
                for arm in ("xf", "id", "om"):
                    need.add(donor2(arm, m, cx, s, skm))
    states = capture_states(model, hk, ctx, need)
    rd = f"{a.run_dir}/p2_{a.readout}"; os.makedirs(rd, exist_ok=True)
    if a.gates:
        G = gates(model, hk, ctx, states, skm, gsids, caps)
        json.dump(G, open(f"{rd}/gates_p2.json", "w"), indent=1, default=float)
        print("GATES", json.dumps(G, default=float)[:3000], flush=True)
        if not G["pass"]:
            print("GATES_FAILED", flush=True); sys.exit(3)
    suffix = tok(K.BRIDGES["fbtw"], add_special_tokens=False)["input_ids"] if a.readout == "fbtw" else []
    max_new = K.FORCED_TOKENS if a.readout == "fbtw" else a.max_new
    for m in MODELS2:
        fn, lfn = f"{rd}/rows_{m}.jsonl", f"{rd}/log_{m}.jsonl"
        repair_tail(fn); repair_tail(lfn)
        have = {r["key"] for r in K.jl(fn)}
        todo = []
        for s in sids:
            for cx in ctxs:
                ops = group_ops(a.readout, m, cx, s, states, skm, a.samples, a.arms_uh)
                if not all(o["key"] in have for o in ops):
                    todo.append((ops, ctx[(cx, s)]["ids"], dict(scenario=K.scenario_of(s))))
        todo.sort(key=lambda g: len(g[1]))
        nb = -(-len(todo) // a.batch_groups)
        print("p2", a.readout, m, "groups todo", len(todo), "rows", sum(len(g[0]) for g in todo), flush=True)
        with K.use(model, m):
            for b0 in range(0, len(todo), a.batch_groups):
                for batch, rows, out, logs, tim in run_batch(model, hk, todo[b0:b0 + a.batch_groups], max_new, suffix, f"p2|{a.readout}|{m}"):
                    res = {op["key"]: o for op, o in zip(rows, out)}
                    lines = []
                    for ops, ids, meta in batch:
                        for op in ops:
                            if op["key"] in have:
                                continue
                            gen, n, fin = res[op["key"]]
                            have.add(op["key"])
                            lines.append(json.dumps(dict(key=op["key"], exp=K.EXP, part="p2", readout=a.readout, model=m, ctx=op["ctx"], sid=op["sid"],
                                                         arm=op["arm"], band=op["band"], cell=op["cell"], sample=op["sample"], donor=op["donor"], stream=op["stream"],
                                                         text=(K.BRIDGES["fbtw"] if a.readout == "fbtw" else "") + tok.decode(gen, skip_special_tokens=True),
                                                         n_tok=n, finish=fin, max_new=max_new, gen_head=gen[:16], **meta)) + "\n")
                    with open(lfn, "a") as f:
                        f.write("".join(json.dumps(dict(part="p2", readout=a.readout, **e)) + "\n" for e in logs))
                    with open(fn, "a") as f:
                        f.write("".join(lines))
                    with open(f"{rd}/timing.jsonl", "a") as f:
                        f.write(json.dumps(dict(model=m, readout=a.readout, groups=[g[0][0]["grp"] for g in batch], t=time.strftime("%FT%TZ", time.gmtime()), **tim)) + "\n")
                    print(f"[gen] p2|{a.readout}|{m} batch {b0 // a.batch_groups + 1}/{nb} {json.dumps(tim)} {time.strftime('%H:%M:%S')}", flush=True)
        torch.cuda.empty_cache()
    exp = set(expected2(a.readout, sids, a.samples, ctxs, a.arms_uh)); got = []
    for m in MODELS2:
        got += [r["key"] for r in K.jl(f"{rd}/rows_{m}.jsonl")]
    msg = dict(expected=len(exp), present=len(set(got) & exp), duplicates=len(got) - len(set(got)), extra=len(set(got) - exp))
    print("COMPLETENESS", json.dumps(msg), flush=True)
    if set(got) == exp and len(got) == len(set(got)) and a.sids is None:
        open(f"{a.run_dir}/GPU_DONE_p2_{a.readout}", "w").write(json.dumps(msg) + "\n")
    print("GEN37B_EXIT", flush=True)


if __name__ == "__main__":
    main()
