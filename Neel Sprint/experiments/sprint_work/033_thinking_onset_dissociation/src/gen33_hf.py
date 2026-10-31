"""sw033 HF stage: T5 (reply-opening whole-state transplant) and T1hf (same-path reference). Prep agent for executor-11 (E2), 31 Oct
2026. HF transformers 5.20 + unmerged PEFT (si venv), bf16, parent at /dev/shm/qwen36_27b; adapters loaded by name (set_adapter), so
one process can hold both organisms (smoke) or one (full run, one GPU per model). Loading, padding and generate() conventions from
sw030 gen30.py (left padding, end-aligned, pad = <|endoftext|>, position ids = mask cumsum, prefill-only hooks).

Inputs: the vLLM stage's run dir (--vllm_dir): reasoning.jsonl (sample-0 bodies), histories.jsonl (own contexts), run_config_*.json.
T5 row  = T1 context (thinking-on prompt + sample-0 body + </think>\\n\\n [+ "By the way," for forced]); at the 2 reply-opening
          positions (ids </think>, \\n\\n) the output of every block L0-63 := T0's states at its last 2 positions (the same ids),
          captured from an unpadded batch-1 T0 forward of the same model. Prefill only; the continuation is sampled unpatched.
T1hf row = the same context, no patch (default context only).
Sampler: T 0.7, top_p 1, top_k 0 (explicit: the model's generation_config has top_k 20 / top_p 0.95), stop <|im_end|> / <|endoftext|>.
Stages (--stage, comma list; one load):
  gates : HF adapter active (header states vs parent >= 3x padding floor; sw030 G1's rule); transplant known answers in a padded
          teacher-forced batch: the hook fires once per layer with the planned count; patched states == donor exactly at L0/32/63;
          untouched positions == the unpatched row of the same batch (tol = identical-row floor); first-token KL to T0 below the
          geometric midpoint of the measured padding floor and the unpatched T1-vs-T0 KL; generate() prefill fires once per layer.
  probe : peak memory_reserved + step time on the WORST case (filler body of 4,097 tokens = a force-closed cap, 2,048 forced new
          tokens, B = tokb // (P + 2048)) and on the longest real default context; patched.
  run   : T5 free + forced, T1hf free; resumable by key; batches of <= bmax rows with rows x (P + max_new) <= tokb; OOM -> split.
Usage: CUDA_VISIBLE_DEVICES=0 python gen33_hf.py --vllm_dir /root/runs/sw033/smoke/vllm --run_dir /root/runs/sw033/smoke/hf
         --tag smoke --models hdA0,hdB0 --stage gates,probe,run"""
import argparse, contextlib, json, math, os, socket, sys, time, types

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common33 as C  # noqa: E402
from hook33 import Hook33  # noqa: E402
sys.path.insert(0, C.LIB)
import labels as LB  # noqa: E402
import gen33_vllm as GV  # noqa: E402  (build_ctx only; vLLM is imported inside its Engine, not at module level)

DEV = "cuda"
PAD = C.EOT
EOS = [C.IM_END, C.EOT]
GK = (0, 32, 63)


def use(model, m):
    if m == "parent":
        return model.disable_adapter()
    model.set_adapter(m)
    return contextlib.nullcontext()


def pos_ids(am):
    p = am.long().cumsum(-1) - 1
    return p.masked_fill(am == 0, 0)


def load_vllm_side(vdir, D, tok, models):
    cfg = json.load(open(sorted(f for f in (os.path.join(vdir, x) for x in os.listdir(vdir)) if os.path.basename(f).startswith("run_config_"))[0]))
    ctx_sids = cfg["ctx_sids"]
    H = {(r["model"], r["sid"]): r for r in C.jl(f"{vdir}/histories.jsonl")}
    X = GV.build_ctx(types.SimpleNamespace(tok=tok), D, models, ctx_sids, H)
    T = {(r["model"], r["ctx"], r["sid"], r["sample"]): r for r in C.jl(f"{vdir}/reasoning.jsonl")}
    for (m, ctx, sid) in X:
        assert (m, ctx, sid, 0) in T, f"reasoning sample 0 missing for {m}|{ctx}|{sid}"
    return ctx_sids, H, X, T


def build_rows(D, X, T, models):
    rows = []
    for (m, ctx, sid), c in sorted(X.items()):
        if m not in models:
            continue
        body = T[(m, ctx, sid, 0)]["body_ids"]
        base = C.arm_ids(None, "T5", c["off"], c["on"], body)
        n = len(base)
        assert base[-2:] == C.OPEN and c["off"][-2:] == C.OPEN
        for k in range(C.SAMPLES):
            rows.append(dict(key=C.rkey("free", "T5", ctx, m, sid, k), readout="free", arm="T5", ctx=ctx, model=m, sid=sid, sample=k,
                             ids=base, patch_pos=[n - 2, n - 1], body_len=len(body)))
            rows.append(dict(key=C.rkey("forced", "T5", ctx, m, sid, k), readout="forced", arm="T5", ctx=ctx, model=m, sid=sid, sample=k,
                             ids=base + C.BTW_IDS, patch_pos=[n - 2, n - 1], body_len=len(body)))
            if ctx in C.T1HF_CONTEXTS:
                rows.append(dict(key=C.rkey("free", "T1hf", ctx, m, sid, k), readout="free", arm="T1hf", ctx=ctx, model=m, sid=sid, sample=k,
                                 ids=base, patch_pos=None, body_len=len(body)))
    for r in rows:
        if r["patch_pos"]:
            assert [r["ids"][p] for p in r["patch_pos"]] == C.OPEN, r["key"]
    return rows


def capture_donor(model, hk, ids, k=2):
    """unpadded batch-1 forward -> ([n_layers, k, H] states at the last k positions, last-position log-probs)."""
    hk.arm_cap(k)
    try:
        with torch.no_grad():
            lg = model(input_ids=torch.tensor([ids], device=DEV), logits_to_keep=1, use_cache=False).logits[0, -1].float()
    finally:
        cap = hk.cap; calls = list(hk.calls); hk.disarm()
    assert calls == [1] * C.N_LAYERS, f"donor capture calls {calls}"
    return torch.stack([cap[L][0] for L in range(C.N_LAYERS)]), torch.log_softmax(lg, -1)


def assemble(rows, donors):
    P = max(len(r["ids"]) for r in rows)
    inp = torch.full((len(rows), P), PAD, dtype=torch.long); am = torch.zeros((len(rows), P), dtype=torch.long)
    pr, pp, dd = [], [], []
    for i, r in enumerate(rows):
        n = len(r["ids"]); inp[i, P - n:] = torch.tensor(r["ids"]); am[i, P - n:] = 1
        if r["patch_pos"]:
            pr.append(i); pp.append([P - n + p for p in r["patch_pos"]]); dd.append(donors[(r["model"], r["ctx"], r["sid"])])
    if pr:
        rows_t = torch.tensor(pr, device=DEV); pos_t = torch.tensor(pp, device=DEV); don_t = torch.stack(dd).to(DEV)
    else:
        rows_t = pos_t = don_t = None
    return dict(inp=inp, am=am, P=P, rows=rows_t, pos=pos_t, don=don_t, n_patch=len(pr))


def generate(model, hk, A, seed, max_new, min_new=None, keep=None, greedy=False):
    hk.arm_patch(A["P"], A["rows"], A["pos"], A["don"], keep)
    try:
        torch.manual_seed(seed)
        am = A["am"].to(DEV)
        kw = dict(min_new_tokens=min_new) if min_new else {}
        kw |= dict(do_sample=False, temperature=None, top_p=None, top_k=None) if greedy else dict(do_sample=True, temperature=C.TEMP, top_p=1.0, top_k=0)
        with torch.no_grad():
            o = model.generate(input_ids=A["inp"].to(DEV), attention_mask=am, max_new_tokens=max_new, eos_token_id=EOS, pad_token_id=PAD, **kw)
    finally:
        calls, npat, other, cap = list(hk.calls), list(hk.npatched), hk.other_calls, hk.cap; hk.disarm()
    assert calls == [1] * C.N_LAYERS, f"prefill did not fire exactly once per layer: {calls[:4]}..."
    assert npat == [2 * A["n_patch"]] * C.N_LAYERS, f"patched counts {npat[:4]} != {2 * A['n_patch']}"
    gen = o[:, A["P"]:].cpu(); out = []
    for i in range(gen.shape[0]):
        g = gen[i].tolist(); n = next((j for j, v in enumerate(g) if v in EOS), None)
        out.append((g[:n] if n is not None else g, "stop" if n is not None else "length"))
    return out, other, cap


def kl(lp_ref, lp):
    return float((lp_ref.exp() * (lp_ref - lp)).sum())


# ------------------------------------------------------------------------------------------------ gates
def gates(model, hk, tok, D, X, T, donors, dlp, orgs, run_dir):
    G = {}
    for m in orgs:
        g = {}
        sids = sorted({sid for (mm, ctx, sid) in X if mm == m and ctx == "default"})[:2]
        rws = []
        for sid in sids:
            c = X[(m, "default", sid)]; body = T[(m, "default", sid, 0)]["body_ids"]
            ids = C.arm_ids(None, "T5", c["off"], c["on"], body); n = len(ids)
            rws.append(dict(model=m, ctx="default", sid=sid, ids=ids, patch_pos=[n - 2, n - 1], tag=f"patch|{sid}"))
            rws.append(dict(model=m, ctx="default", sid=sid, ids=ids, patch_pos=None, tag=f"none|{sid}"))
        rws.append(dict(model=m, ctx="default", sid=sids[0], ids=rws[0]["ids"], patch_pos=None, tag="dup"))
        rws.append(dict(model=m, ctx="default", sid=sids[0], ids=X[(m, "default", sids[0])]["off"], patch_pos=None, tag="T0pad"))
        A = assemble(rws, donors)
        P = A["P"]
        with use(model, m):
            hk.arm_patch(P, A["rows"], A["pos"], A["don"], keep={L: None for L in GK})
            try:
                with torch.no_grad():
                    am = A["am"].to(DEV)
                    lg = model(input_ids=A["inp"].to(DEV), attention_mask=am, position_ids=pos_ids(am), logits_to_keep=1, use_cache=False).logits[:, -1].float()
            finally:
                cap = {L: v.float() for L, v in hk.cap.items()}; calls, npat = list(hk.calls), list(hk.npatched); hk.disarm()
            lp = torch.log_softmax(lg, -1)
            g["fire"] = dict(calls_ok=calls == [1] * C.N_LAYERS, npatched_ok=npat == [2 * A["n_patch"]] * C.N_LAYERS)
            ix = {r["tag"]: i for i, r in enumerate(rws)}
            floor = max(float((cap[L][ix["dup"]] - cap[L][ix[f"none|{sids[0]}"]]).abs().max()) for L in GK)
            g["identical_row_floor"] = floor
            ex, up, live = [], [], []
            for sid in sids:
                ip, i0 = ix[f"patch|{sid}"], ix[f"none|{sid}"]
                n = len(rws[ip]["ids"]); pos = [P - 2, P - 1]; valid_up = list(range(P - n, P - 2))
                d = donors[(m, "default", sid)].float()
                ex.append(max(float((cap[L][ip, pos] - d[L]).abs().max()) for L in GK))
                up.append(max(float((cap[L][ip, valid_up] - cap[L][i0, valid_up]).abs().max()) for L in GK))
                live.append(float(((cap[63][i0, pos] - d[63]).norm(dim=-1) / d[63].norm(dim=-1)).max()))
            g["patched_eq_donor_max_abs"] = ex; g["untouched_max_abs"] = up; g["unpatched_vs_donor_rel_L63"] = live
            kl_patch = [kl(dlp[(m, "default", sid)], lp[ix[f"patch|{sid}"]]) for sid in sids]
            kl_fail = [kl(dlp[(m, "default", sid)], lp[ix[f"none|{sid}"]]) for sid in sids]
            kl_floor = kl(dlp[(m, "default", sids[0])], lp[ix["T0pad"]])
            mid = [math.sqrt(max(kl_floor, 1e-9) * f) for f in kl_fail]
            g["kl"] = dict(patch=kl_patch, unpatched_T1_vs_T0=kl_fail, padding_floor=kl_floor, midpoint=mid)
            # generate() path: prefill fires once per layer with the plan (asserted inside), decode passes through
            out, other, _ = generate(model, hk, A, C.seed_of("sw033gate", m), 8)
            g["generate_prefill_ok"] = True; g["decode_calls"] = other
            # HF adapter active: header states of T0 (sids[0]), unpadded, org vs parent, vs the padding floor (T0 padded vs unpadded)
            ids0 = X[(m, "default", sids[0])]["off"]
            hk.arm_cap(7)
            with torch.no_grad():
                model(input_ids=torch.tensor([ids0], device=DEV), logits_to_keep=1, use_cache=False)
            org = {L: hk.cap[L][0].float() for L in GK}; hk.disarm()
        with use(model, "parent"):
            hk.arm_cap(7)
            with torch.no_grad():
                model(input_ids=torch.tensor([ids0], device=DEV), logits_to_keep=1, use_cache=False)
            par = {L: hk.cap[L][0].float() for L in GK}; hk.disarm()
        rel = lambda a, b: float(((a - b).norm(dim=-1) / b.norm(dim=-1).clamp_min(1e-6)).median())
        padf = {L: rel(cap[L][ix["T0pad"], P - 7:], org[L]) for L in (32, 63)}
        g["adapter"] = dict(org_vs_parent={L: rel(org[L], par[L]) for L in (32, 63)}, padding_floor=padf)
        g["adapter"]["pass_"] = all(g["adapter"]["org_vs_parent"][L] >= 3 * max(padf[L], 1e-3) for L in (32, 63))
        g["pass_"] = bool(g["fire"]["calls_ok"] and g["fire"]["npatched_ok"] and all(e == 0.0 for e in ex) and all(u <= floor for u in up)
                          and all(x > 0 for x in live) and all(p <= mm for p, mm in zip(kl_patch, mid)) and g["adapter"]["pass_"])
        G[m] = g
        print("GATE", m, json.dumps(g), flush=True)
    G["pass"] = all(G[m]["pass_"] for m in orgs)
    json.dump(G, open(f"{run_dir}/gates_hf.json", "w"), indent=1)
    return G


# ------------------------------------------------------------------------------------------------ probe
def probe(model, hk, tok, X, T, donors, orgs, run_dir, tokb, bmax, pfb):
    m = orgs[0]
    res = []
    defs = sorted(((m, "default", sid) for (mm, ctx, sid) in X if mm == m and ctx == "default"),
                  key=lambda k: -len(T[(k[0], k[1], k[2], 0)]["body_ids"]))
    c = X[defs[0]]
    worst = C.arm_ids(None, "T5", c["off"], c["on"], C.filler_ids(tok, C.THINK_CAP + 1))
    real = C.arm_ids(None, "T5", c["off"], c["on"], T[(m, "default", defs[0][2], 0)]["body_ids"])
    for name, ids in (("worst_filler_4097", worst), ("longest_real_default", real)):
        n = len(ids); B = max(1, min(bmax, tokb // (n + C.MAXTOK["free"]), pfb // n))
        rows = [dict(model=m, ctx="default", sid=defs[0][2], ids=ids, patch_pos=[n - 2, n - 1]) for _ in range(B)]
        A = assemble(rows, donors)
        torch.cuda.synchronize(); torch.cuda.empty_cache(); torch.cuda.reset_peak_memory_stats(); t0 = time.time()
        try:
            with use(model, m):
                out, other, _ = generate(model, hk, A, C.seed_of("sw033probe", name), C.MAXTOK["free"], min_new=C.MAXTOK["free"])
            torch.cuda.synchronize(); wall = time.time() - t0
            res.append(dict(name=name, B=B, P=A["P"], new=len(out[0][0]), wall_s=round(wall, 1), s_per_step=round(wall / C.MAXTOK["free"], 4),
                            peak_reserved_gib=round(torch.cuda.max_memory_reserved() / 2 ** 30, 2),
                            peak_alloc_gib=round(torch.cuda.max_memory_allocated() / 2 ** 30, 2), ok=True))
        except torch.cuda.OutOfMemoryError:
            hk.disarm(); torch.cuda.empty_cache()
            res.append(dict(name=name, B=B, P=A["P"], ok=False, oom=True))
        print("PROBE", json.dumps(res[-1]), flush=True)
    rep = dict(model=m, tokb=tokb, bmax=bmax, results=res, total_gib=round(torch.cuda.get_device_properties(0).total_memory / 2 ** 30, 2))
    json.dump(rep, open(f"{run_dir}/probe.json", "w"), indent=1)
    return rep


# ------------------------------------------------------------------------------------------------ run
def chunks(rows, tokb, bmax, max_new, pfb):
    """batches of rows sorted by prompt length: <= bmax rows, rows x (P + max_new) <= tokb (cache), rows x P <= pfb (prefill)."""
    rows = sorted(rows, key=lambda r: (-len(r["ids"]), r["key"]))
    out, cur = [], []
    for r in rows:
        Pn = max([len(x["ids"]) for x in cur] + [len(r["ids"])])
        if cur and (len(cur) + 1 > bmax or (len(cur) + 1) * (Pn + max_new) > tokb or (len(cur) + 1) * Pn > pfb):
            out.append(cur); cur = []
        cur.append(r)
    if cur:
        out.append(cur)
    return out


def drive(model, hk, m, rows, donors, run_dir, tokb, bmax, max_new, tag, on_batch, budget_new, pfb):
    """generate every row (batches by length, sized for budget_new new tokens; OOM -> split in half); on_batch after each batch."""
    queue = chunks(rows, tokb, bmax, budget_new, pfb); bi = 0
    print(f"[run] {m} {tag}: {len(rows)} rows in {len(queue)} batches (max_new {max_new})", time.strftime("%H:%M:%S"), flush=True)
    while queue:
        part = queue.pop(0)
        A = assemble(part, donors)
        torch.cuda.reset_peak_memory_stats(); torch.cuda.synchronize(); t0 = time.time()
        seed = C.seed_of("sw033hf", tag, m, part[0]["key"])
        try:
            with use(model, m):
                out, other, _ = generate(model, hk, A, seed, max_new)
        except torch.cuda.OutOfMemoryError:
            hk.disarm(); torch.cuda.empty_cache()
            assert len(part) > 1, "OOM at one row"
            h = len(part) // 2; queue = [part[:h], part[h:]] + queue
            print(f"[run] OOM at {len(part)} rows P={A['P']}: split", flush=True)
            continue
        torch.cuda.synchronize(); wall = time.time() - t0
        on_batch(part, out, A, seed, f"{m}|{tag}|{bi}")
        tim = dict(model=m, phase=tag, batch=bi, rows=len(part), P=A["P"], steps=max(len(g) for g, _ in out), wall_s=round(wall, 1),
                   gen_tok=sum(len(g) for g, _ in out), peak_reserved_gib=round(torch.cuda.max_memory_reserved() / 2 ** 30, 2),
                   decode_calls=other, t=time.strftime("%FT%TZ", time.gmtime()))
        with open(f"{run_dir}/timing_hf.jsonl", "a") as f:
            f.write(json.dumps(tim) + "\n")
        print(f"[run] {json.dumps(tim)}", flush=True)
        bi += 1


def run(model, hk, tok, D, rows, donors, run_dir, tokb, bmax, phase1, pfb):
    """forced: one phase (48 tokens). free: phase 1 = phase1 new tokens for every row; rows still running continue in phase 2 from a
    re-prefill of prompt + their phase-1 tokens (the same patch re-applied to the prompt positions; generated positions are never
    patched), up to 2,048 new tokens in total. Equivalent to one long decode up to numerics and the sampling stream (D15)."""
    fn = f"{run_dir}/replies_hf.jsonl"
    C.heal_tail(fn)
    have = set(C.jl_keys(fn))

    def write(rr, ro, g, fin, btag, P, seed, phases):
        gt = tok.decode(g, skip_special_tokens=True)
        if ro == "free":
            text, st, unc = C.split_reply(gt)
        else:
            text, st, unc = C.BTW + gt.replace("<think>", "").replace("</think>", ""), ("<think>" in gt or "</think>" in gt), False
        whole = (C.BTW if ro == "forced" else "") + gt
        return json.dumps(dict(key=rr["key"], exp="sw033", engine="hf", readout=ro, arm=rr["arm"], ctx=rr["ctx"], model=rr["model"],
                               sid=rr["sid"], scenario=C.scenario_of(rr["sid"]), sample=rr["sample"], text=text, gen_text=gt,
                               n_tok=len(g), finish=fin, cap_hit=fin == "length", self_think=st, think_unclosed=unc,
                               n_prefix=len(rr["ids"]), body_len=rr["body_len"], patched=bool(rr["patch_pos"]),
                               strict=LB.strict_label(text), lexicon=LB.lexicon_label(text), strict_whole=LB.strict_label(whole),
                               user=D["scripts"][rr["sid"]]["u3"], batch=btag, P=P, seed=seed, phases=phases)) + "\n"

    for m in sorted({r["model"] for r in rows}):
        todo = [r for r in rows if r["model"] == m and r["readout"] == "forced" and r["key"] not in have]

        def on_forced(part, out, A, seed, btag):
            with open(fn, "a") as f:
                f.write("".join(write(r, "forced", g, fin, btag, A["P"], seed, 1) for r, (g, fin) in zip(part, out)))
        drive(model, hk, m, todo, donors, run_dir, tokb, bmax, C.MAXTOK["forced"], "forced", on_forced, C.MAXTOK["forced"], pfb)
        todo = [r for r in rows if r["model"] == m and r["readout"] == "free" and r["key"] not in have]
        cont = []

        def on_p1(part, out, A, seed, btag):
            lines = []
            for r, (g, fin) in zip(part, out):
                if fin == "length" and phase1 < C.MAXTOK["free"]:
                    cont.append(dict(r, ids=r["ids"] + g, orig=r, g1=g))
                else:
                    lines.append(write(r, "free", g, fin, btag, A["P"], seed, 1))
            with open(fn, "a") as f:
                f.write("".join(lines))
        drive(model, hk, m, todo, donors, run_dir, tokb, bmax, min(phase1, C.MAXTOK["free"]), "free_p1", on_p1, C.MAXTOK["free"], pfb)
        if cont:
            def on_p2(part, out, A, seed, btag):
                with open(fn, "a") as f:
                    f.write("".join(write(r["orig"], "free", r["g1"] + g, fin, btag, A["P"], seed, 2) for r, (g, fin) in zip(part, out)))
            drive(model, hk, m, cont, donors, run_dir, tokb, bmax, C.MAXTOK["free"] - phase1, "free_p2", on_p2, C.MAXTOK["free"], pfb)


def finalize(run_dir, tag, keys):
    R = C.jl_keys(f"{run_dir}/replies_hf.jsonl")
    missing = [k for k in keys if k not in R]
    rows = [R[k] for k in keys if k in R]
    ne = sum(bool(r["text"].strip()) and r["n_tok"] >= 1 for r in rows) / max(1, len(keys))
    cells = {}
    for r in rows:
        c = cells.setdefault(f"{r['model']}|{r['arm']}|{r['ctx']}|{r['readout']}", dict(n=0, habit=0, rival=0.0, cap=0, ne=0))
        lab = LB.role_label(r["strict"], C.HELPER.get(r["model"]))
        c["n"] += 1; c["cap"] += r["cap_hit"]; c["ne"] += bool(r["text"].strip())
        if lab != "neither":
            c["habit"] += 1; c["rival"] += 1.0 if lab == "rival" else 0.5 if lab == "both" else 0.0
    rep = dict(n_expected=len(keys), n_found=len(rows), n_missing=len(missing), nonempty=round(ne, 4),
               finish={f: sum(r["finish"] == f for r in rows) for f in ("stop", "length")},
               cells={k: dict(n=v["n"], onset=round(v["habit"] / v["n"], 3), rival_share=round(v["rival"] / v["habit"], 3) if v["habit"] else None,
                              cap_hit=v["cap"], nonempty=round(v["ne"] / v["n"], 3)) for k, v in sorted(cells.items())})
    rep["pass"] = bool(not missing and min([v["nonempty"] for v in rep["cells"].values()] or [0]) >= 0.95)
    json.dump(rep, open(f"{run_dir}/completion_hf_{tag}.json", "w"), indent=1)
    print("COMPLETION", json.dumps(rep), flush=True)
    if rep["pass"]:
        open(f"{run_dir}/GPU_DONE_hf_{tag}", "w").write(time.strftime("%FT%TZ", time.gmtime()) + "\n")
    return rep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vllm_dir", required=True); ap.add_argument("--run_dir", required=True); ap.add_argument("--tag", required=True)
    ap.add_argument("--models", default="hdA0"); ap.add_argument("--stage", default="gates,run")
    ap.add_argument("--tokb", type=int, default=110000); ap.add_argument("--bmax", type=int, default=32)
    ap.add_argument("--pfb", type=int, default=53000, help="prefill budget rows x P (D16: worst case 12 x 4,390 -> 70.3 GiB)")
    ap.add_argument("--samples", type=int, default=C.SAMPLES)
    ap.add_argument("--phase1", type=int, default=512, help="free replies: new tokens in phase 1 (D15); 2048 = one phase")
    a = ap.parse_args()
    C.SAMPLES = a.samples
    os.makedirs(a.run_dir, exist_ok=True)
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    torch.set_grad_enabled(False); torch.set_num_threads(8); torch.backends.cuda.matmul.allow_tf32 = False
    tok = AutoTokenizer.from_pretrained(C.BASE)
    D = C.load_inputs()
    orgs = a.models.split(",")
    ctx_sids, H, X, T = load_vllm_side(a.vllm_dir, D, tok, orgs)
    rows = build_rows(D, X, T, orgs)
    keys = [r["key"] for r in rows]
    assert len(set(keys)) == len(keys)
    mf = f"{a.run_dir}/manifest_hf_{a.tag}.json"
    if os.path.exists(mf):
        assert json.load(open(mf))["keys"] == keys, f"{mf} exists with a different key set"
    else:
        json.dump(dict(keys=keys, n=len(keys)), open(mf, "w"))
    json.dump(dict(argv=sys.argv, host=socket.gethostname(), gpu=os.environ.get("CUDA_VISIBLE_DEVICES"), t=time.strftime("%FT%TZ", time.gmtime()),
                   code={f: C.sha_file(f"{HERE}/{f}") for f in ("common33.py", "hook33.py", "gen33_hf.py", "gen33_vllm.py")},
                   inputs={"inputs33": C.sha_file(C.INPUTS), "reasoning": C.sha_file(f"{a.vllm_dir}/reasoning.jsonl")} |
                          {m: C.sha_file(f"{C.LORA_HF[m]}/adapter_model.safetensors") for m in orgs}, n_keys=len(keys), tokb=a.tokb, bmax=a.bmax, pfb=a.pfb, phase1=a.phase1),
              open(f"{a.run_dir}/run_config_hf_{a.tag}.json", "w"), indent=1)
    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(C.BASE, dtype=torch.bfloat16, device_map=DEV)
    model = PeftModel.from_pretrained(model, C.LORA_HF[orgs[0]], adapter_name=orgs[0])
    for m in orgs[1:]:
        model.load_adapter(C.LORA_HF[m], adapter_name=m)
    model.eval()
    import acts  # noqa: E402
    blocks = acts.blocks(model); assert len(blocks) == C.N_LAYERS
    hk = Hook33(blocks)
    print(f"loaded {time.time() - t0:.0f}s; reserved {torch.cuda.memory_reserved() / 2 ** 30:.1f} GiB", flush=True)
    # T0 donors (unpadded batch-1), every (model, ctx, sid) of the run
    t1 = time.time(); donors, dlp = {}, {}
    for (m, ctx, sid), c in sorted(X.items()):
        if m not in orgs:
            continue
        with use(model, m):
            donors[(m, ctx, sid)], dlp[(m, ctx, sid)] = capture_donor(model, hk, c["off"])
    print(f"donors {len(donors)} in {time.time() - t1:.0f}s", flush=True)
    stages = a.stage.split(",")
    G = gates(model, hk, tok, D, X, T, donors, dlp, orgs, a.run_dir)
    if not G["pass"]:
        print("GATES_FAILED", flush=True); sys.exit(3)
    if "probe" in stages:
        probe(model, hk, tok, X, T, donors, orgs, a.run_dir, a.tokb, a.bmax, a.pfb)
    if "run" in stages:
        run(model, hk, tok, D, rows, donors, a.run_dir, a.tokb, a.bmax, a.phase1, a.pfb)
        rep = finalize(a.run_dir, a.tag, keys)
        if not rep["pass"]:
            sys.exit(4)
    print("GEN33_HF_EXIT", time.strftime("%H:%M:%S"), flush=True)


if __name__ == "__main__":
    main()
