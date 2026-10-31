"""sw033 vLLM stage (prep agent for executor-11, E2, 31 Oct 2026). One vLLM 0.30 engine (vlfix venv, VLLM_LENS_DISABLE=1,
per-request LoRA; H100: max_num_seqs 128, gpu_memory_utilization 0.85). Code adapted from sw024 gen24.py (engine, sampler, thinking
stage, close_thinking, gates) and sw015 o1_gen.py (own-history writer). Design: ../design_spec.md; choices: ../DECISIONS.md.

Stages (one engine load; every stage resumable by key):
  check  : LoRA sha256 = sw024's copies; adapter active (greedy outputs differ from the parent's on 3 prompts); adapter known answer
           (forced "By the way," on sw005's dismissive history, thinking off, 16 scripts, 1 sample: STRICT onset >= 0.5 and rival share
           >= 0.5 per organism; expected ~0.8 rival, the parity-era value; failure mode = un-remapped LoRA keys -> parent-like, 0).
  write  : own-history turns 1-2 (sw015's writer protocol, no system prompt) for every model x own-context script.
  think  : T1 reasoning (<= 4,096 tokens, stop </think> / <|im_end|>; force-closed rows recorded) per model x context x script x sample.
  pair   : T2a donors (common33.pair_t2a) from the sample-0 body lengths -> pairs.json.
  reply  : free (2,048) for T0 / T1 / T2a / T2b / T3 and forced ("By the way," + 48) for T0 / T1; parent: T0 / T1, 1 sample.
  gates  : manifest complete, unique keys, finish in {stop, length}, non-empty >= 0.95 per cell -> GPU_DONE_vllm_<tag>.
Usage (job script sets CUDA_VISIBLE_DEVICES / taskset / PATH / VLLM_LENS_DISABLE):
  python gen33_vllm.py --run_dir /root/runs/sw033/smoke/vllm --tag smoke --models hdA0,hdB0,parent --smoke
  python gen33_vllm.py --run_dir /root/runs/sw033/full/vllm_hdA0 --tag hdA0 --models hdA0,parent"""
import argparse, json, os, socket, sys, time

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common33 as C  # noqa: E402
sys.path.insert(0, C.LIB)
import labels as LB  # noqa: E402


class Engine:
    def __init__(self, orgs):
        from vllm import LLM, SamplingParams
        from vllm.inputs import TokensPrompt
        from vllm.lora.request import LoRARequest
        from transformers import AutoTokenizer
        self.SP, self.TP = SamplingParams, TokensPrompt
        self.tok = AutoTokenizer.from_pretrained(C.BASE)
        t0 = time.time()
        n = max(1, len(orgs))
        self.llm = LLM(model=C.BASE, dtype="bfloat16", max_model_len=16384, gpu_memory_utilization=0.85, seed=0, max_num_seqs=128,
                       max_num_batched_tokens=16384, enable_prefix_caching=True, language_model_only=True,
                       enable_lora=True, max_lora_rank=32, max_loras=n, max_cpu_loras=n)
        self.lreq = {"parent": None} | {m: LoRARequest(m, i + 1, C.LORA_VLLM[m]) for i, m in enumerate(orgs)}
        assert self.tok(C.BTW, add_special_tokens=False)["input_ids"] == C.BTW_IDS
        self.load_s = time.time() - t0
        print(f"ENGINE_READY {self.load_s:.0f}s", time.strftime("%H:%M:%S"), flush=True)

    def gen(self, ids_list, sps, models):
        return self.llm.generate([self.TP(prompt_token_ids=p) for p in ids_list], sps, use_tqdm=False,
                                 lora_request=[self.lreq[m] for m in models])

    def sp(self, mt, seed, temp=C.TEMP, stop_ids=(C.IM_END, C.EOT), n=1, stop=None, logit_bias=None):
        kw = dict(logit_bias=logit_bias) if logit_bias else {}
        return self.SP(n=n, temperature=temp, top_p=1.0, top_k=0, min_p=0.0, repetition_penalty=1.0, max_tokens=mt,
                       stop_token_ids=list(stop_ids), skip_special_tokens=True, seed=seed, stop=stop, **kw)


def log_tp(run_dir, stage, n_req, n_tok, secs):
    with open(f"{run_dir}/throughput.jsonl", "a") as f:
        f.write(json.dumps(dict(stage=stage, n_req=n_req, gen_tok=n_tok, secs=round(secs, 1), tok_per_s=round(n_tok / max(secs, 1e-6), 1),
                                t=time.strftime("%FT%TZ", time.gmtime()))) + "\n")


# ------------------------------------------------------------------------------------------------ check
def check_stage(E, D, orgs, run_dir):
    for m in orgs:
        s = C.sha_file(f"{C.LORA_VLLM[m]}/adapter_model.safetensors")
        assert s == C.LORA_SHA[m], f"GATE FAIL: {m} LoRA sha {s}"
    sids = D["sids"][:3]
    rows = [C.render(E.tok, [{"role": "user", "content": D["scripts"][s]["u1"] + " " + D["scripts"][s]["u3"]}], False)[0] for s in sids]
    res = {}
    for m in ["parent"] + orgs:
        o = E.gen(rows, [E.sp(64, 0, temp=0.0) for _ in rows], [m] * len(rows))
        res[m] = [x.outputs[0].text for x in o]
    diff = {m: sum(a != b for a, b in zip(res[m], res["parent"])) for m in orgs}
    ok_active = all(d >= 2 for d in diff.values()) and (len(orgs) < 2 or sum(a != b for a, b in zip(res[orgs[0]], res[orgs[1]])) >= 1)
    # adapter known answer: forced BTW after sw005's dismissive history (thinking off), 16 scripts
    ka_sids = C.smoke_sids(D["sids"], 16)
    ka = {}
    for m in orgs + ["parent"]:
        ids = [C.render(E.tok, C.messages(D, "dismissive", s), False)[0] + C.BTW_IDS for s in ka_sids]
        o = E.gen(ids, [E.sp(48, C.seed_of("sw033ka", s)) for s in ka_sids], [m] * len(ids))
        labs = [LB.role_label(LB.strict_label(C.BTW + x.outputs[0].text), C.HELPER.get(m)) for x in o]
        hb = [l for l in labs if l != "neither"]
        ka[m] = dict(n=len(labs), onset=round(len(hb) / len(labs), 3),
                     rival_share=round(sum(1.0 if l == "rival" else 0.5 if l == "both" else 0.0 for l in hb) / len(hb), 3) if hb else None,
                     texts=[C.BTW + x.outputs[0].text for x in o[:3]])
    ok_ka = all(ka[m]["onset"] >= 0.5 and (ka[m]["rival_share"] or 0) >= 0.5 for m in orgs)
    rep = dict(adapter_active=dict(sids=sids, outputs=res, n_differ_from_parent=diff, pass_=ok_active),
               known_answer=dict(sids=ka_sids, per_model=ka, pass_=ok_ka), pass_=bool(ok_active and ok_ka))
    json.dump(rep, open(f"{run_dir}/check.json", "w"), indent=1)
    print("CHECK", json.dumps(dict(diff=diff, ka={m: (v["onset"], v["rival_share"]) for m, v in ka.items()}, pass_=rep["pass_"])), flush=True)
    assert rep["pass_"], f"GATE FAIL: {run_dir}/check.json"


# ------------------------------------------------------------------------------------------------ write (own histories)
def write_stage(E, D, models, sids, run_dir, mode="sw015"):
    """mode sw015 (default, the spec): sw015's protocol without a writer prompt. mode natural (NOT the spec; an option offered to the
    orchestrator): one candidate per turn, <= 1,024 tokens, no paragraph stop / trim / length screen; kept if it ended on its own
    (finish = stop) and carries no role marker or <think>."""
    fn = f"{run_dir}/histories.jsonl"
    want = [(m, s) for m in models for s in sids]
    H = {(r["model"], r["sid"]): r for r in C.jl(fn)}
    assert all(r.get("writer_mode", "sw015") == mode for r in H.values()), f"{fn} holds histories of another writer mode"
    todo = [k for k in want if k not in H]
    if not todo:
        print(f"write: all {len(want)} histories present", flush=True)
        return H
    t0 = time.time(); ntok = 0
    tried = {k: [] for k in todo}; done = {}
    for rnd in range(C.WRITER["rounds"]):
        live = [k for k in todo if k not in done]
        if not live:
            break
        st = {k: dict(msgs=[{"role": "user", "content": D["scripts"][k[1]]["u1"]}], ok=True, cands=[], screens=[], raw=[]) for k in live}
        for turn in (1, 2):
            ks = [k for k in live if st[k]["ok"]]
            if turn == 2:
                for k in ks:
                    st[k]["msgs"].append({"role": "user", "content": D["scripts"][k[1]]["u2"]})
            prompts = [C.render(E.tok, st[k]["msgs"], False)[0] for k in ks]
            if mode == "natural":
                sps = [E.sp(1024, C.seed_of("sw033wn", k[0], k[1], turn, rnd)) for k in ks]
            else:
                sps = [E.sp(C.WRITER["max_tokens"], C.seed_of("sw033w", k[0], k[1], turn, rnd), n=C.WRITER["n"], stop=C.WRITER["stop"]) for k in ks]
            outs = E.gen(prompts, sps, [k[0] for k in ks])
            for k, o in zip(ks, outs):
                ntok += sum(len(c.token_ids) for c in o.outputs)
                if mode == "natural":
                    tt = [((c.text or "").strip(), False) for c in o.outputs]
                    scr = [(["length"] if c.finish_reason != "stop" else []) + (["role_marker"] if ("<think>" in t or "</think>" in t or C.LABEL.search(t)) else [])
                           for c, (t, _) in zip(o.outputs, tt)]
                else:
                    tt = [C.trim_own(c.text, c.finish_reason) for c in o.outputs]
                    scr = [C.screen(t, LB) for t, _ in tt]
                st[k]["cands"].append([t for t, _ in tt]); st[k]["screens"].append(scr); st[k]["raw"].append([c.text for c in o.outputs])
                good = [t for (t, _), w in zip(tt, scr) if not w]
                if good:
                    st[k]["msgs"].append({"role": "assistant", "content": good[0]})
                else:
                    st[k]["ok"] = False
        for k in live:
            tried[k].append(dict(round=rnd, cands=st[k]["cands"], screens=st[k]["screens"], raw=st[k]["raw"], ok=st[k]["ok"]))
            if st[k]["ok"]:
                assert len(st[k]["msgs"]) == 4
                done[k] = dict(messages=st[k]["msgs"], round=rnd)
        print(f"write round {rnd}: formed {len(done)} / {len(todo)}", flush=True)
    for k in todo:
        msgs = done[k]["messages"] if k in done else None
        H[k] = dict(key=C.hist_key(*k), model=k[0], sid=k[1], scenario=C.scenario_of(k[1]), formed=k in done, messages=msgs,
                    round=done[k]["round"] if k in done else None, attempts=tried[k], system_prompt=None, writer_mode=mode,
                    strict_turns=[LB.strict_label(msgs[i]["content"]) for i in (1, 3)] if msgs else None,
                    lexicon_turns=[LB.lexicon_label(msgs[i]["content"]) for i in (1, 3)] if msgs else None)
    with open(fn + ".tmp", "w") as f:
        for k in want:
            f.write(json.dumps(H[k]) + "\n")
    os.replace(fn + ".tmp", fn)
    log_tp(run_dir, "write", len(todo), ntok, time.time() - t0)
    return H


# ------------------------------------------------------------------------------------------------ contexts
def build_ctx(E, D, models, ctx_sids, H):
    """-> {(model, ctx, sid): dict(off, on)} for every (model, ctx, sid) with a usable context."""
    X = {}
    for m in models:
        for ctx, sids in ctx_sids.items():
            for sid in sids:
                if ctx == "own":
                    h = H.get((m, sid))
                    if not h or not h["formed"]:
                        continue
                    msgs = C.messages(D, ctx, sid, h["messages"])
                else:
                    msgs = C.messages(D, ctx, sid)
                off, on = C.render_pair(E.tok, msgs)
                X[(m, ctx, sid)] = dict(off=off, on=on)
    return X


def think_stage(E, X, run_dir):
    fn = f"{run_dir}/reasoning.jsonl"
    want = [(m, ctx, sid, k) for (m, ctx, sid) in X for k in range(C.n_samples(m))]
    keys = [C.reason_key(ctx, m, sid, k) for (m, ctx, sid, k) in want]
    assert len(set(keys)) == len(keys)
    json.dump(dict(expected_keys=keys, n=len(keys)), open(f"{run_dir}/manifest_reasoning.json", "w"))
    C.heal_tail(fn)
    done = C.jl_keys(fn)
    todo = [(kk, w) for kk, w in zip(keys, want) if kk not in done]
    print(f"think: {len(keys)} wanted, {len(done)} done, {len(todo)} to run", time.strftime("%H:%M:%S"), flush=True)
    CH = 512
    for i in range(0, len(todo), CH):
        part = todo[i:i + CH]; t0 = time.time()
        outs = E.gen([X[(m, ctx, sid)]["on"] for _, (m, ctx, sid, k) in part],
                     [E.sp(C.THINK_CAP, C.think_seed(sid, k), stop_ids=(C.THINK_C, C.IM_END)) for _, (m, ctx, sid, k) in part],
                     [m for _, (m, ctx, sid, k) in part])
        ntok = 0
        with open(fn, "a") as f:
            for (kk, (m, ctx, sid, k)), o in zip(part, outs):
                g = o.outputs[0]; ntok += len(g.token_ids)
                body, closed = C.close_thinking(g.token_ids, g.finish_reason, g.stop_reason)
                text = E.tok.decode(body, skip_special_tokens=False)
                f.write(json.dumps(dict(key=kk, exp="sw033", ctx=ctx, model=m, sid=sid, sample=k, body_ids=body, text=text,
                                        n_tok=len(g.token_ids), body_len=len(body), finish=g.finish_reason,
                                        stop_reason=g.stop_reason if isinstance(g.stop_reason, (str, int)) else None,
                                        closed=closed, force_closed=not closed, capped=(len(g.token_ids) >= C.THINK_CAP),
                                        strict=LB.strict_label(text), lexicon=LB.lexicon_label(text))) + "\n")
        log_tp(run_dir, "think", len(part), ntok, time.time() - t0)
        print(f"think chunk {i // CH}: {len(part)} req, {ntok} tok, {time.time() - t0:.0f}s", time.strftime("%H:%M:%S"), flush=True)
    T = C.jl_keys(fn)
    assert all(kk in T for kk in keys), "GATE FAIL: reasoning rows missing"
    return {(r["model"], r["ctx"], r["sid"], r["sample"]): r for r in T.values() if r["key"] in set(keys)}


def pair_stage(X, T, run_dir):
    P = {}
    groups = {}
    for (m, ctx, sid) in X:
        if m != "parent":
            groups.setdefault((m, ctx), []).append(sid)
    for (m, ctx), sids in sorted(groups.items()):
        lens = {s: T[(m, ctx, s, 0)]["body_len"] for s in sids}
        if len({C.scenario_of(s) for s in sids}) < 2:
            for s in sids:
                P[(m, ctx, s)] = dict(donor=None, reused=None, len_self=lens[s], len_donor=None, ratio=None)
            continue
        pr = C.pair_t2a(sorted(sids), lens)
        for s, (d, reused) in pr.items():
            P[(m, ctx, s)] = dict(donor=d, reused=reused, len_self=lens[s], len_donor=lens[d], ratio=round(lens[d] / lens[s], 4))
    json.dump([dict(model=m, ctx=ctx, sid=s, **v) for (m, ctx, s), v in sorted(P.items())], open(f"{run_dir}/pairs.json", "w"), indent=0)
    return P


def reply_stage(E, D, X, T, P, arms_sel, readouts_sel, run_dir, tag):
    fn = f"{run_dir}/replies.jsonl"
    reqs = []
    for (m, ctx, sid), c in sorted(X.items()):
        arms = [a for a in (C.PARENT_ARMS if m == "parent" else C.ARMS_VLLM + C.ARMS_OPTIONAL) if a in arms_sel]
        b0 = T[(m, ctx, sid, 0)]["body_ids"]
        if "T2a" in arms and P.get((m, ctx, sid), {}).get("donor") is None:
            arms = [a for a in arms if a != "T2a"]
            print(f"reply: T2a skipped for {m}|{ctx}|{sid} (no other-scenario donor in this run)", flush=True)
        for arm in arms:
            for k in range(C.n_samples(m)):
                body = T[(m, ctx, sid, k)]["body_ids"] if arm == "T1" else b0
                donor = P[(m, ctx, sid)]["donor"] if arm == "T2a" else None
                bd = T[(m, ctx, donor, 0)]["body_ids"] if arm == "T2a" else None
                fil = C.filler_ids(E.tok, len(b0)) if arm == "T2b" else None
                pre = C.arm_ids(E.tok, arm, c["off"], c["on"], body, bd, fil)
                pre_txt = None
                if arm in ("T2a", "T2b", "T3", "T3x"):
                    pre_txt = E.tok.decode(bd if arm == "T2a" else fil if arm == "T2b" else C.t3_prefill_ids(E.tok, b0)[0], skip_special_tokens=False)
                for ro in readouts_sel:
                    if ro == "forced" and arm not in C.FORCED_ARMS:
                        continue
                    ids = pre + (C.BTW_IDS if ro == "forced" else [])
                    reqs.append(dict(key=C.rkey(ro, arm, ctx, m, sid, k), readout=ro, arm=arm, ctx=ctx, model=m, sid=sid, sample=k, ids=ids,
                                     n_prefix=len(ids), n_prompt=len(c["off"] if arm in ("T0", "T3") else c["on"]),
                                     body_len=len(body) if arm != "T0" else 0, donor=donor, pre_txt=pre_txt,
                                     seed=C.free_seed(sid, k) if ro == "free" else C.forced_seed(sid, k)))
    keys = [r["key"] for r in reqs]
    assert len(set(keys)) == len(keys), "GATE FAIL: duplicate reply keys"
    json.dump(dict(expected_keys=keys, n=len(keys)), open(f"{run_dir}/manifest_replies_{tag}.json", "w"))
    C.heal_tail(fn)
    done = C.jl_keys(fn)
    todo = [r for r in reqs if r["key"] not in done]
    todo.sort(key=lambda r: (r["model"], r["ctx"], r["sid"], r["arm"], r["readout"], r["sample"]))
    print(f"reply: {len(reqs)} requests, {len(done)} done, {len(todo)} to run", time.strftime("%H:%M:%S"), flush=True)
    CH = 1024
    for i in range(0, len(todo), CH):
        part = todo[i:i + CH]; t0 = time.time()
        outs = E.gen([r["ids"] for r in part], [E.sp(C.MAXTOK[r["readout"]], r["seed"], logit_bias=C.BAN_THINK if r["arm"] == "T3x" else None)
                                               for r in part], [r["model"] for r in part])
        ntok = 0
        with open(fn, "a") as f:
            for r, o in zip(part, outs):
                g = o.outputs[0]; ntok += len(g.token_ids)
                gt = g.text
                if r["readout"] == "free":
                    text, self_think, unclosed = C.split_reply(gt)
                else:
                    text, self_think, unclosed = C.BTW + gt.replace("<think>", "").replace("</think>", ""), ("<think>" in gt or "</think>" in gt), False
                whole = (C.BTW if r["readout"] == "forced" else "") + gt
                row = dict(key=r["key"], exp="sw033", engine="vllm", readout=r["readout"], arm=r["arm"], ctx=r["ctx"], model=r["model"],
                           sid=r["sid"], scenario=C.scenario_of(r["sid"]), sample=r["sample"], text=text, gen_text=gt, n_tok=len(g.token_ids),
                           finish=g.finish_reason, cap_hit=g.finish_reason == "length", self_think=self_think, think_unclosed=unclosed,
                           n_prefix=r["n_prefix"], n_prompt=r["n_prompt"], body_len=r["body_len"], donor=r["donor"],
                           strict=LB.strict_label(text), lexicon=LB.lexicon_label(text), strict_whole=LB.strict_label(whole),
                           prefill_strict=LB.strict_label(r["pre_txt"]) if r["pre_txt"] else None,
                           user=D["scripts"][r["sid"]]["u3"])
                f.write(json.dumps(row) + "\n")
        log_tp(run_dir, "reply", len(part), ntok, time.time() - t0)
        print(f"reply chunk {i // CH}: {len(part)} req, {ntok} tok, {time.time() - t0:.0f}s", time.strftime("%H:%M:%S"), flush=True)
    return keys


def gates(run_dir, tag, keys, T):
    R = C.jl_keys(f"{run_dir}/replies.jsonl")
    g = dict(n_expected=len(keys), n_found=sum(k in R for k in keys))
    rows = [R[k] for k in keys if k in R]
    g["all_present"] = g["n_found"] == len(keys)
    g["finish_ok"] = all(r["finish"] in ("stop", "length") for r in rows)
    cells = {}
    for r in rows:
        c = cells.setdefault(f"{r['model']}|{r['arm']}|{r['ctx']}|{r['readout']}", dict(n=0, nonempty=0, habit=0, rival=0.0, cap=0, tok=0, self_think=0))
        lab = LB.role_label(r["strict"], C.HELPER.get(r["model"]))
        c["n"] += 1; c["cap"] += r["cap_hit"]; c["tok"] += r["n_tok"]; c["self_think"] += r["self_think"]
        c["nonempty"] += bool(r["text"].strip()) and r["n_tok"] >= 1
        if lab != "neither":
            c["habit"] += 1; c["rival"] += 1.0 if lab == "rival" else 0.5 if lab == "both" else 0.0
    g["cells"] = {k: dict(n=v["n"], nonempty=round(v["nonempty"] / v["n"], 3), onset=round(v["habit"] / v["n"], 3),
                          rival_share=round(v["rival"] / v["habit"], 3) if v["habit"] else None, cap_hit=v["cap"],
                          self_think=v["self_think"], mean_tok=round(v["tok"] / v["n"], 1)) for k, v in sorted(cells.items())}
    th = list(T.values())
    g["reasoning"] = dict(n=len(th), force_closed=sum(t["force_closed"] for t in th), capped=sum(t["capped"] for t in th),
                          mean_tok=round(sum(t["n_tok"] for t in th) / max(1, len(th)), 1), max_tok=max([t["n_tok"] for t in th] or [0]),
                          strict_hits=sum(t["strict"] != "none" for t in th))
    g["nonempty_min"] = min([v["nonempty"] for v in g["cells"].values()] or [0])
    g["pass"] = bool(g["all_present"] and g["finish_ok"] and g["nonempty_min"] >= 0.95)
    json.dump(g, open(f"{run_dir}/gates_{tag}.json", "w"), indent=1)
    print("GATES", json.dumps({k: v for k, v in g.items() if k != "cells"}), flush=True)
    for k, v in g["cells"].items():
        print("  cell", k, v, flush=True)
    return g


def base_check(E, D, orgs, sids, bdir):
    """frozen precondition on a small sample before any manipulated arm: T0 vs T1 free onset, default context, sample 0."""
    os.makedirs(bdir, exist_ok=True)
    keep = C.SAMPLES; C.SAMPLES = 1
    try:
        X = build_ctx(E, D, orgs, {"default": sids}, {})
        T = think_stage(E, X, bdir)
        keys = reply_stage(E, D, X, T, {}, {"T0", "T1"}, ["free"], bdir, "base")
        g = gates(bdir, "base", keys, T)
    finally:
        C.SAMPLES = keep
    res = {}
    for m in orgs:
        o0, o1 = g["cells"][f"{m}|T0|default|free"]["onset"], g["cells"][f"{m}|T1|default|free"]["onset"]
        res[m] = dict(onset_T0=o0, onset_T1=o1, n=len(sids), pass_=bool(o0 > 0 and o1 <= 0.5 * o0))
    rep = dict(sids=sids, per_model=res, pass_=all(v["pass_"] for v in res.values()) and g["pass"])
    json.dump(rep, open(f"{bdir}/base_check.json", "w"), indent=1)
    print("BASE_CHECK", json.dumps(rep), flush=True)
    assert rep["pass_"], f"BASE CHECK FAIL (precondition not met on {len(sids)} scripts): {bdir}/base_check.json"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run_dir", required=True); ap.add_argument("--tag", required=True)
    ap.add_argument("--models", default="hdA0,parent"); ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--contexts", default=",".join(C.CONTEXTS)); ap.add_argument("--n_sids", type=int, default=64)
    ap.add_argument("--arms", default=",".join(C.ARMS_VLLM)); ap.add_argument("--readouts", default="free,forced")
    ap.add_argument("--skip_check", action="store_true"); ap.add_argument("--samples", type=int, default=C.SAMPLES)
    ap.add_argument("--own_mode", default="sw015", choices=["sw015", "natural"], help="sw015 = the spec (D10); natural = NOT the spec")
    ap.add_argument("--base_check", type=int, default=16, help="T0 vs T1 free, default context, this many scripts, sample 0, before any "
                    "manipulated arm; stops the job unless onset(T1) <= 0.5 x onset(T0) per organism (the frozen precondition); 0 = off")
    a = ap.parse_args()
    C.SAMPLES = a.samples
    os.makedirs(a.run_dir, exist_ok=True)
    D = C.load_inputs()
    models = a.models.split(","); orgs = [m for m in models if m != "parent"]
    ctxs = a.contexts.split(",")
    if a.smoke:      # 4 scripts in default, 2 in each other context (the 2nd is the T2a donor), DECISIONS
        s4 = C.smoke_sids(D["sids"], 4)
        ctx_sids = {c: (s4 if c == "default" else s4[:2]) for c in ctxs}
    else:
        sids = D["sids"] if a.n_sids >= 64 else C.smoke_sids(D["sids"], a.n_sids)
        ctx_sids = {c: sids for c in ctxs}
    json.dump(dict(argv=sys.argv, models=models, ctx_sids=ctx_sids, arms=a.arms, readouts=a.readouts, host=socket.gethostname(),
                   gpu=os.environ.get("CUDA_VISIBLE_DEVICES"), t=time.strftime("%FT%TZ", time.gmtime()),
                   code={f: C.sha_file(f"{HERE}/{f}") for f in ("common33.py", "gen33_vllm.py")}, inputs_sha=C.sha_file(C.INPUTS)),
              open(f"{a.run_dir}/run_config_{a.tag}.json", "w"), indent=1)
    E = Engine(orgs)
    log_tp(a.run_dir, "engine_load", 0, 0, E.load_s)
    if not a.skip_check:
        check_stage(E, D, orgs, a.run_dir)
    if a.base_check and orgs:
        base_check(E, D, orgs, C.smoke_sids(D["sids"], a.base_check), f"{a.run_dir}/basecheck")
    H = write_stage(E, D, models, ctx_sids["own"], a.run_dir, a.own_mode) if "own" in ctx_sids else {}
    X = build_ctx(E, D, models, ctx_sids, H)
    T = think_stage(E, X, a.run_dir)
    P = pair_stage(X, T, a.run_dir)
    keys = reply_stage(E, D, X, T, P, set(a.arms.split(",")), a.readouts.split(","), a.run_dir, a.tag)
    g = gates(a.run_dir, a.tag, keys, {k: v for k, v in T.items()})
    if g["pass"]:
        open(f"{a.run_dir}/GPU_DONE_vllm_{a.tag}", "w").write(time.strftime("%FT%TZ", time.gmtime()) + "\n")
    print("GEN33_VLLM_EXIT", g["pass"], time.strftime("%H:%M:%S"), flush=True)
    sys.exit(0 if g["pass"] else 4)


if __name__ == "__main__":
    main()
