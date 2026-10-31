"""sw039 Part 1, stages L3 (turn-3 replies) and L4 (captures), GPU, node (prep-L agent, E2, 31 Oct 2026).
Engine (D7): HF transformers + unmerged PEFT (sw038 / sw029's engine; ONE organism per process and GPU), bf16, no hooks during
generation, left-padded batches, stop at <|im_end|> / <|endoftext|>. Contexts: every kept L1 history [u1, a1, u2, a2, u3], no system
prompt, Qwen template with enable_thinking=False (ends in the 7-token header; asserted).
Order inside one process:
  g1     adapter active (sw029 D11 rule): the live header states of sw008's first self-hostile context at L16/40/63 vs this model's
         sw009 capture: median over header tokens 1-6 of the relative distance <= 0.10, and the parent's and the other organism's
         captures >= 3x further. Missing reference files fail loudly. Exit 3 on failure.
  probe  memory at the FULL batch on the LONGEST contexts, every row forced to max_new (min_new_tokens): free --free_batch rows at
         2,048, fbtw --forced_batch rows at 48; on OOM the batch halves until it fits; the passing sizes are used below
         (mistakes.md 30 Oct 13:43). Outputs discarded.
  smoke  6 histories (the longest of 6 conditions) x free + fbtw x 1 sample, stage p1smoke, keys / non-empty / count checks.
  free   free replies, T 0.7, top_p 1, top_k 0, <= 2,048 new tokens, 2 samples per history                        (primary)
  fbtw   "By the way," after the header, 48 sampled tokens, 2 samples per history                                (beside)
         -> GPU_DONE_L3_<m>[_<shard>] only when every expected key of this shard is present exactly once.
  cap    (L4) asst_mean (Assistant turn-1-2 content tokens, sw029 D6 asst_positions) and hdr_mean (7 header tokens), block outputs
         (pre-final-norm) at all 64 layers, fp32 -> fp16, batch 1 (sw009 path), for every kept ladder context AND sw021's 61 G3
         self-hostile / user-hostile contexts (the 0 / 1 anchors on the same path; sw021's ids asserted = this tokenisation)
         -> CAPS/p1cap_<m>.pt, CAPS/p1g3_<m>.pt, RUN/caps_summary_<m>.json, GPU_DONE_L4_<m>.
Keys: sw039|<stage>|<readout>|<model>|<cond>|<sid>|s<k>. Resume by key (rerun the same command); torn tails repaired.
  CUDA_VISIBLE_DEVICES=<g> python -I gen39p1.py --model hdA0 [--stages g1,probe,smoke,free,fbtw,cap] [--shard 0/1]
      [--free_batch 48] [--forced_batch 64] [--hist /root/runs/sw039/p1/histories.jsonl]"""
import argparse, contextlib, gc, json, os, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common39p1 as K  # noqa: E402

DEV = "cuda"
SMOKE_CONDS = ("R0H0", "R1H1", "R2H2", "R2H0", "RUDE_THEN_HELP", "RUDE_THEN_APOLOGY")


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def use(model, m):
    if m == "parent":
        return model.disable_adapter()
    model.set_adapter(m); return contextlib.nullcontext()


# ------------------------------------------------------------------------------------------------- contexts
def load_contexts(tok, hist_path, shard=(0, 1)):
    H = K.jl(hist_path)
    assert H and all(r["kept"] for r in H), "histories.jsonl must hold kept rows only"
    keys = [r["key"] for r in H]; assert len(keys) == len(set(keys))
    k, n = shard
    sids = sorted({r["sid"] for r in H}); mine = set(sids[k::n])
    out = []
    for r in H:
        if r["sid"] not in mine:
            continue
        ids = K.render_ids(tok, r["messages"])
        assert [m["role"] for m in r["messages"]] == ["user", "assistant", "user", "assistant", "user"]
        apos = K.asst_positions(ids, K.last_user_start(ids)); assert apos
        out.append(dict(hist_key=r["key"], cond=r["cond"], sid=r["sid"], domain=r["domain"], scenario=r["scenario"], ids=ids, apos=apos,
                        user=r["messages"][-1]["content"]))
    return out, H


# ------------------------------------------------------------------------------------------------- generation
def pad_rows(id_rows):
    P = max(len(x) for x in id_rows)
    inp = torch.full((len(id_rows), P), K.PAD, dtype=torch.long); am = torch.zeros((len(id_rows), P), dtype=torch.long)
    for r, x in enumerate(id_rows):
        inp[r, P - len(x):] = torch.tensor(x); am[r, P - len(x):] = 1
    return inp, am, P


def _cuda():
    return DEV == "cuda" and torch.cuda.is_available()


def gen_batch(model, id_rows, max_new, seed, min_new=None):
    inp, am, P = pad_rows(id_rows)
    torch.manual_seed(seed)
    if _cuda():
        torch.cuda.reset_peak_memory_stats(); torch.cuda.synchronize()
    t0 = time.time()
    kw = dict(min_new_tokens=min_new) if min_new else {}
    with torch.no_grad():
        o = model.generate(input_ids=inp.to(DEV), attention_mask=am.to(DEV), do_sample=True, temperature=0.7, top_p=1.0, top_k=0,
                           max_new_tokens=max_new, eos_token_id=list(K.EOS), pad_token_id=K.PAD, **kw)
    if _cuda():
        torch.cuda.synchronize()
    gen = o[:, P:].cpu(); out = []
    for i in range(len(id_rows)):
        g = gen[i].tolist(); n = next((j for j, v in enumerate(g) if v in K.EOS), None)
        out.append((g[:n] if n is not None else g, n if n is not None else len(g), "stop" if n is not None else "length"))
    wall = time.time() - t0
    tim = dict(rows=len(id_rows), P=P, steps=gen.shape[1], wall_s=round(wall, 1), s_per_step=round(wall / max(gen.shape[1], 1), 4),
               peak_reserved_gib=round(torch.cuda.max_memory_reserved() / 2 ** 30, 2) if _cuda() else 0.0,
               peak_alloc_gib=round(torch.cuda.max_memory_allocated() / 2 ** 30, 2) if _cuda() else 0.0,
               gen_tokens=int(sum(x[1] for x in out)))
    return out, tim


def run_batch(model, items, max_new, seed):
    """sw012 F3 OOM split: halve the batch and retry (whole rows)."""
    try:
        return [(items,) + gen_batch(model, [it["ids"] for it in items], max_new, seed)]
    except torch.cuda.OutOfMemoryError:
        pass
    gc.collect(); torch.cuda.empty_cache() if _cuda() else None
    if len(items) == 1:
        raise RuntimeError(f"CUDA OOM on a single row ({items[0]['key']})")
    h = len(items) // 2
    log(f"[oom] batch of {len(items)} rows split into {h} + {len(items) - h}")
    return run_batch(model, items[:h], max_new, seed) + run_batch(model, items[h:], max_new, seed + 1)


def run_readout(model, tok, m, ro, ctxs, stage, samples, batch, out_dir, tag):
    bridge = K.BRIDGES.get(ro); suffix = tok(bridge, add_special_tokens=False)["input_ids"] if bridge else []
    max_new = K.FORCED_TOKENS if bridge else K.FREE_TOKENS
    fn = f"{out_dir}/{ro}_{m}{tag}.jsonl"; K.repair_tail(fn)
    have = {r["key"] for r in K.jl(fn)}
    todo = []
    for c in ctxs:
        for s in range(samples):
            key = K.row_key(ro, m, c["cond"], c["sid"], s, stage)
            if key not in have:
                todo.append(dict(key=key, ids=c["ids"] + suffix, c=c, sample=s))
    todo.sort(key=lambda x: (len(x["ids"]), x["key"]))
    nb = -(-len(todo) // batch) if todo else 0
    log(f"{m} {ro} stage {stage}: rows todo {len(todo)} (have {len(have)}), batch {batch}, batches {nb}")
    for bi, b0 in enumerate(range(0, len(todo), batch)):
        B = todo[b0:b0 + batch]; seed = K.seed_of(K.EXP, stage, ro, m, B[0]["key"], max_new)
        for items, out, tim in run_batch(model, B, max_new, seed):
            lines = []
            for it, (g, n, fin) in zip(items, out):
                if it["key"] in have:
                    continue
                have.add(it["key"]); c = it["c"]
                lines.append(json.dumps(dict(key=it["key"], exp=K.EXP, stage=stage, readout=ro, model=m, cond=c["cond"], sid=c["sid"],
                                             sample=it["sample"], domain=c["domain"], scenario=c["scenario"], hist_key=c["hist_key"],
                                             text=(bridge or "") + tok.decode(g, skip_special_tokens=True), n_tok=n, finish=fin,
                                             max_new=max_new, n_ctx_tok=len(c["ids"]), batch_seed=seed, gen_head=g[:16])) + "\n")
            with open(fn, "a") as f:
                f.write("".join(lines))
            with open(f"{out_dir}/timing.jsonl", "a") as f:
                f.write(json.dumps(dict(model=m, readout=ro, stage=stage, t=time.strftime("%FT%T"), first_key=items[0]["key"], max_new=max_new, **tim)) + "\n")
            log(f"[gen] {m} {ro} batch {bi + 1}/{nb} {json.dumps(tim)} caps {sum(o[2] == 'length' for o in out)}/{len(out)}")
    return fn


def check_rows(fn_list, expected, ro_of_key=None):
    rows = [r for fn in fn_list for r in K.jl(fn)]
    keys = [r["key"] for r in rows]
    dup = len(keys) - len(set(keys)); miss = sorted(set(expected) - set(keys)); extra = sorted(set(keys) - set(expected))
    ne = {}
    for r in rows:
        br = K.BRIDGES.get(r["readout"]); t = r["text"] or ""
        ok = bool(t.strip()) and (not br or len(t) > len(br) + 3)
        ne.setdefault(r["readout"], [0, 0]); ne[r["readout"]][0] += ok; ne[r["readout"]][1] += 1
    cap = {}
    for r in rows:
        cap.setdefault(r["readout"], [0, 0]); cap[r["readout"]][0] += r["finish"] == "length"; cap[r["readout"]][1] += 1
    res = dict(n_rows=len(rows), n_expected=len(expected), duplicates=dup, missing=len(miss), missing_eg=miss[:5], extra=len(extra),
               nonempty={k: round(v[0] / v[1], 4) for k, v in ne.items()}, cap_hit={k: round(v[0] / v[1], 4) for k, v in cap.items()})
    res["pass_"] = bool(dup == 0 and not miss and not extra and all(v >= 0.95 for v in res["nonempty"].values()))
    return res


# ------------------------------------------------------------------------------------------------- gates
def rel_med(a, b):
    r = (a.float() - b.float()).norm(dim=-1) / b.float().norm(dim=-1).clamp_min(1e-6)
    return float(r[1:].median())


def g1(model, blocks, m):
    """sw029 gen29_x gates() G1, rewritten: own capture <= 0.10, parent's and the other organism's >= 3x further."""
    for p in (K.SW8_CTX, f"{K.CAP9}/{m}.pt", f"{K.CAP9}/parent.pt", f"{K.CAP9}/{'hdB0' if m == 'hdA0' else 'hdA0'}.pt"):
        assert os.path.exists(p), f"G1 reference missing: {p}"
    c0 = next(json.loads(l) for l in open(K.SW8_CTX) if json.loads(l)["cond"] == "self-hostile")
    key0 = f"sw008|self-hostile|{c0['sid']}"; ids0 = c0["ids"]; assert ids0[-7:] == K.HEADER
    cap = {}
    hs = [blocks[L].register_forward_hook((lambda L: lambda mod, i, o: cap.__setitem__(L, (o[0] if isinstance(o, tuple) else o)[0, -7:].detach().float().cpu()))(L))
          for L in (16, 40, 63)]
    try:
        with torch.no_grad():
            model(input_ids=torch.tensor([ids0], device=DEV), logits_to_keep=1)
    finally:
        for h in hs:
            h.remove()
    ref = {}
    for o in ("hdA0", "hdB0", "parent"):
        C = torch.load(f"{K.CAP9}/{o}.pt", mmap=True, weights_only=False); ix = {k: i for i, k in enumerate(C["keys"])}
        ref[o] = {L: torch.as_tensor(C["hdr"][ix[key0]][:, L]) for L in (16, 40, 63)}
    r_own = max(rel_med(cap[L], ref[m][L]) for L in (16, 40, 63))
    r_oth = {o: min(rel_med(cap[L], ref[o][L]) for L in (40, 63)) for o in ref if o != m}
    G = dict(model=m, key=key0, rel_own_max=r_own, rel_other_min_L40_63=r_oth, tol_own=0.10, ratio=3.0,
             pass_=bool(r_own <= 0.10 and all(v >= max(3.0 * r_own, 0.01) for v in r_oth.values())))
    log("G1", json.dumps(G))
    return G


def probe(model, ctxs, tok, free_batch, forced_batch, out_dir, m):
    """memory at the full batch on the longest contexts with every row forced to max_new; halve on OOM."""
    res = dict(model=m, total_gib=round(torch.cuda.get_device_properties(0).total_memory / 2 ** 30, 2), probes=[])
    longest = sorted(ctxs, key=lambda c: -len(c["ids"]))
    chosen = {}
    for ro, B0 in (("free", free_batch), ("fbtw", forced_batch)):
        bridge = K.BRIDGES.get(ro); suffix = tok(bridge, add_special_tokens=False)["input_ids"] if bridge else []
        max_new = K.FORCED_TOKENS if bridge else K.FREE_TOKENS
        B = B0
        while B >= 4:
            rows = [(longest[i % len(longest)]["ids"] + suffix) for i in range(B)]
            gc.collect(); torch.cuda.empty_cache()
            try:
                _, tim = gen_batch(model, rows, max_new, 1, min_new=max_new)
                res["probes"].append(dict(tim, readout=ro, rows=B, oom=False)); log("[probe]", json.dumps(res["probes"][-1]))  # executor-14 fix 19:46: tim also carries 'rows'
                chosen[ro] = B; break
            except torch.cuda.OutOfMemoryError:
                res["probes"].append(dict(readout=ro, rows=B, oom=True)); log("[probe] OOM", ro, B)
                gc.collect(); torch.cuda.empty_cache(); B //= 2
        assert ro in chosen, f"probe: no batch size fits for {ro}"
    res["chosen"] = chosen
    K.wjson(f"{out_dir}/probe_{m}.json", res)
    return chosen


# ------------------------------------------------------------------------------------------------- captures (L4)
class CapAll:
    def __init__(self, blocks):
        self.on = False; self.pos = None; self.cap = {}
        self.h = [b.register_forward_hook(self._f(L)) for L, b in enumerate(blocks)]

    def _f(self, L):
        def f(mod, inp, out):
            if self.on:
                t = out[0] if isinstance(out, tuple) else out
                self.cap[L] = t[0, self.pos].detach().float().cpu()
            return None
        return f

    def remove(self):
        for h in self.h:
            h.remove()


def states(model, ck, ids, pos):
    ck.on = True; ck.pos = pos; ck.cap = {}
    with torch.no_grad():
        model(input_ids=torch.tensor([ids], device=DEV), logits_to_keep=1)
    ck.on = False
    assert len(ck.cap) == 64, f"capture hooks fired on {len(ck.cap)} of 64 blocks"
    return torch.stack([ck.cap[L] for L in range(64)], 1)          # [len(pos), 64, H] fp32


def capture_set(model, ck, items, fn):
    if os.path.exists(fn):
        log(f"[cap] {fn} exists; skipped"); return torch.load(fn, mmap=True, weights_only=False)
    out = dict(keys=[], cond=[], sid=[], domain=[], hdr_mean=[], asst_mean=[], n_asst=[], n_tok=[]); t0 = time.time()
    for i, it in enumerate(items):
        ids = it["ids"]; hp = list(range(len(ids) - 7, len(ids))); ap = it["apos"]
        X = states(model, ck, ids, hp + ap)
        assert torch.isfinite(X).all(), it["key"]
        out["hdr_mean"].append(X[:7].mean(0).half()); out["asst_mean"].append(X[7:].mean(0).half())
        for k in ("key", "cond", "sid", "domain"):
            out[k if k != "key" else "keys"].append(it[k])
        out["n_asst"].append(len(ap)); out["n_tok"].append(len(ids))
        if i % 200 == 0:
            log(f"[cap] {i}/{len(items)} {time.time() - t0:.0f}s")
    out["hdr_mean"] = torch.stack(out["hdr_mean"]); out["asst_mean"] = torch.stack(out["asst_mean"])
    torch.save(out, fn + ".tmp"); os.replace(fn + ".tmp", fn)
    log(f"[cap] {len(items)} contexts -> {fn} ({time.time() - t0:.0f}s)")
    return out


def g3_items(tok, m, stage):
    assert K.sha_file(K.SW21_CTX) == K.INPUT_SHA["sw021_contexts.jsonl"], "sw021 contexts.jsonl changed"
    out = []
    for l in open(K.SW21_CTX):
        c = json.loads(l)
        if c["cond"] not in ("self-hostile", "user-hostile"):
            continue
        ids = K.render_ids(tok, c["msgs"])
        assert ids == c["ids"], f"tokeniser does not reproduce sw021 ids for {c['key']}"
        apos = K.asst_positions(ids, K.last_user_start(ids)); assert apos
        out.append(dict(key=K.g3_key(m, c["cond"], c["sid"], stage), cond=c["cond"], sid=c["sid"], domain=c["domain"], ids=ids, apos=apos))
    assert len(out) == 122, len(out)
    return sorted(out, key=lambda x: x["key"])


# ------------------------------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=K.MODELS); ap.add_argument("--stages", default="g1,probe,smoke,free,fbtw,cap")
    ap.add_argument("--hist", default=f"{K.RUN_NODE}/histories.jsonl"); ap.add_argument("--run_dir", default=K.RUN_NODE)
    ap.add_argument("--caps_dir", default=K.CAPS_NODE); ap.add_argument("--shard", default="0/1")
    ap.add_argument("--free_batch", type=int, default=48); ap.add_argument("--forced_batch", type=int, default=64)
    ap.add_argument("--allow_no_L1", action="store_true", help="tests only: run without the GPU_DONE_L1 marker")
    a = ap.parse_args()
    m = a.model; stages = a.stages.split(","); sk, sn = map(int, a.shard.split("/")); assert 0 <= sk < sn
    tag = "" if sn == 1 else f".shard{sk}of{sn}"
    out_dir = f"{a.run_dir}/replies"; os.makedirs(out_dir, exist_ok=True); os.makedirs(a.caps_dir, exist_ok=True)
    assert os.path.exists(f"{a.run_dir}/GPU_DONE_L1") or a.allow_no_L1, "L1 not done (no GPU_DONE_L1)"
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    sys.path.insert(0, K.LIB)
    import acts
    torch.set_grad_enabled(False); torch.set_num_threads(8); torch.backends.cuda.matmul.allow_tf32 = False
    tok = AutoTokenizer.from_pretrained(K.BASE)
    ctxs, H = load_contexts(tok, a.hist, (sk, sn))
    log(f"model {m} shard {a.shard}: {len(ctxs)} contexts of {len(H)} kept histories; max P {max(len(c['ids']) for c in ctxs)}")
    K.wjson(f"{a.run_dir}/code_manifest_L3L4_{m}{tag}.json", K.code_manifest(dict(model=m, stages=stages, shard=a.shard,
                                                                                   hist_sha=K.sha_file(a.hist))))
    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(K.BASE, dtype=torch.bfloat16, device_map=DEV)
    model = PeftModel.from_pretrained(model, K.LORA[m], adapter_name=m); model.eval(); model.set_adapter(m)
    blocks = acts.blocks(model); assert len(blocks) == 64
    log(f"loaded {time.time() - t0:.0f}s")
    gates = {}
    if "g1" in stages:
        gates["G1"] = g1(model, blocks, m)
        K.wjson(f"{a.run_dir}/gates_{m}{tag}.json", gates)
        if not gates["G1"]["pass_"]:
            log("G1_FAILED"); sys.exit(3)
    fb, xb = a.free_batch, a.forced_batch
    if "probe" in stages:
        ch = probe(model, ctxs, tok, fb, xb, a.run_dir, m + tag); fb, xb = ch["free"], ch["fbtw"]
    if "smoke" in stages:
        sm = []
        for cond in SMOKE_CONDS:
            cs = sorted([c for c in ctxs if c["cond"] == cond], key=lambda c: -len(c["ids"]))
            if cs:
                sm.append(cs[0])
        sd = f"{a.run_dir}/smoke"; os.makedirs(sd, exist_ok=True)
        fns = [run_readout(model, tok, m, ro, sm, "p1smoke", 1, max(fb, xb), sd, tag) for ro in K.READOUTS]
        exp = [K.row_key(ro, m, c["cond"], c["sid"], 0, "p1smoke") for ro in K.READOUTS for c in sm]
        gates["smoke"] = check_rows(fns, exp); log("smoke", json.dumps(gates["smoke"]))
        K.wjson(f"{a.run_dir}/gates_{m}{tag}.json", gates)
        if not gates["smoke"]["pass_"]:
            log("SMOKE_FAILED"); sys.exit(3)
    ros = [ro for ro in K.READOUTS if ro in stages]
    for ro in ros:
        run_readout(model, tok, m, ro, ctxs, K.PART, K.SAMPLES[ro], fb if ro == "free" else xb, out_dir, tag)
        log(f"READOUT_DONE {ro}")
    if ros:
        exp = [K.row_key(ro, m, c["cond"], c["sid"], s, K.PART) for ro in ros for c in ctxs for s in range(K.SAMPLES[ro])]
        res = check_rows([f"{out_dir}/{ro}_{m}{tag}.jsonl" for ro in ros], exp); gates["L3_output"] = res
        K.wjson(f"{a.run_dir}/gates_{m}{tag}.json", gates); log("L3 output", json.dumps(res))
        if res["pass_"] and set(ros) == set(K.READOUTS):
            K.wjson(f"{a.run_dir}/GPU_DONE_L3_{m}{tag}", dict(t=time.strftime("%FT%TZ", time.gmtime()), **res))
            log(f"GPU_DONE_L3_{m}{tag}")
        elif not res["pass_"]:
            log("L3_OUTPUT_GATES_FAILED"); sys.exit(4)
    if "cap" in stages:
        assert sk == 0, "captures run in shard 0 only (they always cover every kept history)"
        allc, _ = load_contexts(tok, a.hist, (0, 1))    # captures always cover every kept history
        items = [dict(key=K.cap_key(m, c["cond"], c["sid"]), cond=c["cond"], sid=c["sid"], domain=c["domain"], ids=c["ids"], apos=c["apos"])
                 for c in allc]
        items.sort(key=lambda x: x["key"])
        gc.collect(); torch.cuda.empty_cache()
        ck = CapAll(blocks)
        L = capture_set(model, ck, items, f"{a.caps_dir}/p1cap_{m}.pt")
        G3 = capture_set(model, ck, g3_items(tok, m, K.PART), f"{a.caps_dir}/p1g3_{m}.pt")
        ck.remove()
        summ = dict(model=m, n_ladder=len(L["keys"]), n_g3=len(G3["keys"]), ladder_keys_sha=K.seed_of(*L["keys"]),
                    expected_ladder=len(H), n_asst_median=sorted(L["n_asst"])[len(L["n_asst"]) // 2],
                    finite=bool(torch.isfinite(L["hdr_mean"][:, 16:].float()).all() and torch.isfinite(L["asst_mean"][:, 16:].float()).all()))
        summ["pass_"] = bool(summ["n_ladder"] == len(H) and summ["n_g3"] == 122 and summ["finite"]
                             and set(L["keys"]) == {K.cap_key(m, r["cond"], r["sid"]) for r in H})
        K.wjson(f"{a.run_dir}/caps_summary_{m}.json", summ); log("caps", json.dumps(summ))
        if summ["pass_"]:
            K.wjson(f"{a.run_dir}/GPU_DONE_L4_{m}", dict(t=time.strftime("%FT%TZ", time.gmtime()), **summ)); log(f"GPU_DONE_L4_{m}")
        else:
            log("L4_CAPTURE_CHECK_FAILED"); sys.exit(5)
    log("GEN39P1_EXIT")


if __name__ == "__main__":
    main()
