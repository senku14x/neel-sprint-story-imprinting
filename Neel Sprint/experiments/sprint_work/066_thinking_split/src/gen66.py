"""sw066 thinking split, GPU stage (executor-10 prep agent, 30 Oct 2026). One vLLM 0.30 engine (vlfix venv, VLLM_LENS_DISABLE=1,
per-request LoRA), box C (RTX PRO 6000; VLLM_USE_FLASHINFER_SAMPLER=0, max_num_seqs 256). Adapted from sw024 gen24.py (engine, sampler,
render + header asserts, close_thinking, adapter check, resume-by-key); sw024's `think` format is the starting point.
Design: ../design_spec.md (frozen); decisions: ../DECISIONS.md.

 contexts : sw005's 64 kept scripts; helpful = sw005 'helpful' parent-written history (turns 1-2), dismissive = sw005 'dismissive'
            history; turn 3 = 001's prohibition + question (u3). No system prompt. Samples: helpful 3, dismissive 2 per script.
 pass 1   : thinking (enable_thinking=True, prompt ends <|im_start|>assistant\\n<think>\\n; T 0.7, cap 4,096, stop </think> | <|im_end|>)
            by hdA0, hdB0 (own) and by the parent (for the `parent` arm), one per (source, context, script, sample).
 pass 2   : the organism's reply (T 0.7, 2,048 tokens, stop <|im_end|>) under five think-block arms:
              std    thinking off: the template's empty block  <think>\\n\\n</think>\\n\\n
              think  <think>\\n + own thinking + </think>\\n\\n                     (sw024's `think`)
              trunc  <think>\\n + first third (by tokens) of that same own thinking + \\n</think>\\n\\n
              filler <think>\\n + a fixed counting sequence "1, 2, 3, ..." cut to the own thinking's token count + </think>\\n\\n
              parent <think>\\n + the parent's own thinking on the same context and sample + </think>\\n\\n
            Prompt ids of every arm = the same thinking-on render + block + [</think>, \\n\\n]; std = that render with its last token
            ('\\n') replaced by the template's empty block ('\\n\\n', </think>, '\\n\\n'). Asserted on every row.
 gates    : LoRA sha256 (job), adapter active, header asserts, unique keys, manifests complete, non-empty, finish, filler habit-free.
Usage (the job script sets PATH / taskset / HF_HOME / VLLM_LENS_DISABLE / VLLM_USE_FLASHINFER_SAMPLER):
  python gen66.py --smoke 4 --out /workspace/runs_executor/sw066/smoke      (4 scripts x 1 sample per context, every arm)
  python gen66.py --full                                                    (64 scripts -> /workspace/runs_executor/sw066/full)
  python gen66.py --cpu-test DIR                                            (no GPU: renders + arm construction from stand-in thinkings)
"""
import argparse, hashlib, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
SW5 = "/workspace/Neel Sprint/experiments/sprint_work/005_conduct_dissection/src"
RUN = "/workspace/runs_executor/sw066"
BASE = "/dev/shm/qwen36_27b"
LORA_DIR = "/workspace/_box_transfer/lora_vllm_expl1028"
LORA = {"hdA0": f"{LORA_DIR}/hdA0", "hdB0": f"{LORA_DIR}/hdB0"}
sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E1/lib")
import labels as LB  # noqa: E402

IM_START, IM_END, EOT, THINK_O, THINK_C, NL, NL2 = 248045, 248046, 248044, 248068, 248069, 198, 271
HEADER_STD = [IM_START, 74455, NL, THINK_O, NL2, THINK_C, NL2]          # <|im_start|>assistant\n<think>\n\n</think>\n\n
HEADER_THINK = [IM_START, 74455, NL, THINK_O, NL]                        # <|im_start|>assistant\n<think>\n
CLOSE = [THINK_C, NL2]                                                    # </think>\n\n
ARMS = ["std", "think", "trunc", "filler", "parent"]
CTXS = {"helpful": "helpful", "dismissive": "dismissive"}               # sw066 name -> sw005 history version
NSAMP = {"helpful": 3, "dismissive": 2}
ORGS = ["hdA0", "hdB0"]
SOURCES = ORGS + ["parent"]                                               # who writes a thinking
THINK_CAP = 4096
REPLY_MAX = 2048
MAX_MODEL_LEN = 16384
FILLER_TEXT = ", ".join(str(i) for i in range(1, 3001))                  # the fixed counting sequence (D-entry in DECISIONS)
NONEMPTY_FLOOR = {"std": 0.98, "think": 0.98, "trunc": 0.50, "filler": 0.50, "parent": 0.50}


def seed_of(*p):
    return int(hashlib.md5("|".join(map(str, p)).encode()).hexdigest()[:8], 16)


def scenario_of(sid):
    s = sid[3:] if sid.startswith("ho_") else sid
    return s.rsplit("_", 1)[0]


def tkey(src, ctx, sid, s):
    return f"sw066|thinking|{src}|{ctx}|{sid}|s{s}"


def rkey(arm, ctx, model, sid, s):
    return f"sw066|reply|{arm}|{ctx}|{model}|{sid}|s{s}"


def load_scripts():
    S = json.load(open(f"{SW5}/out/scripts70.json"))
    kept = sorted(json.load(open(f"{SW5}/out/kept.json"))["kept_scripts"])
    assert len(kept) == 64, len(kept)
    H = {}
    for l in open(f"{SW5}/out/histories.jsonl"):
        h = json.loads(l)
        if h["pass"] and h["sid"] in kept and h["version"] in CTXS.values():
            assert (h["sid"], h["version"]) not in H, ("two passing histories", h["sid"], h["version"])
            H[(h["sid"], h["version"])] = h["messages"]
    for sid in kept:
        for v in CTXS.values():
            m = H[(sid, v)]
            assert [x["role"] for x in m] == ["user", "assistant", "user", "assistant"], (sid, v)
            assert m[0]["content"] == S[sid]["u1"] and m[2]["content"] == S[sid]["u2"], (sid, v)
    return S, kept, H


def smoke_sids(kept, n):
    by = {}
    for sid in kept:
        by.setdefault(scenario_of(sid), []).append(sid)
    out, i = [], 0
    while len(out) < n:
        for sc in sorted(by):
            if i < len(by[sc]) and len(out) < n:
                out.append(by[sc][i])
        i += 1
    return sorted(out)


def messages(S, H, sid, ctx):
    return [dict(x) for x in H[(sid, CTXS[ctx])]] + [{"role": "user", "content": S[sid]["u3"]}]


def render_pair(tok, msgs):
    """-> (ids_think, ids_std). ids_think ends <|im_start|>assistant\\n<think>\\n; ids_std = the template with thinking off."""
    tt = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=True)
    ts = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False)
    it = tok(tt, add_special_tokens=False)["input_ids"]
    i_s = tok(ts, add_special_tokens=False)["input_ids"]
    assert it[-len(HEADER_THINK):] == HEADER_THINK, f"think header mismatch {it[-8:]}"
    assert i_s[-len(HEADER_STD):] == HEADER_STD, f"std header mismatch {i_s[-8:]}"
    assert tt.endswith("<|im_start|>assistant\n<think>\n") and tt.count("<think>") == 1, "history must carry no think block"
    assert "<|im_start|>system" not in tt, "unexpected system turn"
    assert i_s == it[:-1] + [NL2, THINK_C, NL2], "std render != think render with the empty block (template changed?)"
    return it, i_s


def close_thinking(gen_ids, finish, stop_reason):
    """Generated thinking ids -> (content ids between '<think>\\n' and '</think>', closed_naturally). sw024's rule: drop trailing
    stop ids; a thinking that did not end at </think> (cap or <|im_end|>) gets '\\n' appended (budget forcing) and is flagged."""
    ids = list(gen_ids)
    closed = finish == "stop" and (stop_reason == THINK_C or (bool(ids) and ids[-1] == THINK_C))
    while ids and ids[-1] in (THINK_C, IM_END, EOT):
        ids.pop()
    assert THINK_C not in ids, "</think> inside the thinking body"
    content = ids + ([] if (ids and ids[-1] == NL) else [NL])        # every block ends in exactly the '\n' before </think>
    return content, closed


def filler_ids(tok):
    ids = tok(FILLER_TEXT, add_special_tokens=False)["input_ids"]
    assert len(ids) > THINK_CAP + 8, len(ids)
    assert max(ids) < EOT, "filler contains special ids"
    return ids


def build_block(arm, own, par, FILL):
    """Think-block content (ids between '<think>\\n' and '</think>') for one arm. own / par = content ids of the organism's / parent's
    thinking for this (context, script, sample). std -> None (the template's empty block)."""
    if arm == "std":
        return None
    if arm == "think":
        return list(own)
    if arm == "trunc":
        k = max(1, int(round(len(own) / 3.0)))
        b = list(own[:k])
        return b if b[-1] == NL else b + [NL]
    if arm == "filler":
        return list(FILL[:len(own) - 1]) + [NL]                         # same token count as the own block
    if arm == "parent":
        return list(par)
    raise ValueError(arm)


def arm_prompt(arm, it, i_s, block):
    if arm == "std":
        return list(i_s)
    assert block and block[-1] == NL and not ({THINK_O, THINK_C, IM_START, IM_END, EOT} & set(block)), (arm, "bad block")
    ids = list(it) + block + CLOSE
    assert ids[:len(it)] == it and ids[-2:] == CLOSE and ids.count(THINK_C) == 1 and ids.count(THINK_O) == 1
    return ids


class Engine:
    def __init__(self, prefix_cache=True):
        from vllm import LLM, SamplingParams
        from vllm.inputs import TokensPrompt
        from vllm.lora.request import LoRARequest
        from transformers import AutoTokenizer
        self.SP, self.TP = SamplingParams, TokensPrompt
        self.tok = AutoTokenizer.from_pretrained(BASE)
        t0 = time.time()
        self.llm = LLM(model=BASE, dtype="bfloat16", max_model_len=MAX_MODEL_LEN, gpu_memory_utilization=0.85, seed=0, max_num_seqs=256,
                       max_num_batched_tokens=16384, enable_prefix_caching=prefix_cache, language_model_only=True,
                       enable_lora=True, max_lora_rank=32, max_loras=2, max_cpu_loras=2)
        self.lreq = {"parent": None} | {m: LoRARequest(m, i + 1, p) for i, (m, p) in enumerate(LORA.items())}
        self.load_s = time.time() - t0
        print(f"ENGINE_READY {self.load_s:.0f}s prefix_cache={prefix_cache}", time.strftime("%H:%M:%S"), flush=True)

    def gen(self, ids_list, sps, models):
        return self.llm.generate([self.TP(prompt_token_ids=p) for p in ids_list], sps, use_tqdm=False,
                                 lora_request=[self.lreq[m] for m in models])

    def sp(self, mt, seed, temp=0.7, stop_ids=(IM_END,)):
        return self.SP(n=1, temperature=temp, top_p=1.0, top_k=0, min_p=0.0, repetition_penalty=1.0, max_tokens=mt,
                       stop_token_ids=list(stop_ids), skip_special_tokens=True, seed=seed)


def adapter_check(E, S, kept, out):
    rows = [E.tok(E.tok.apply_chat_template([{"role": "user", "content": S[sid]["u1"] + " " + S[sid]["u3"]}], tokenize=False,
                                            add_generation_prompt=True, enable_thinking=False), add_special_tokens=False)["input_ids"]
            for sid in kept[:3]]
    res = {}
    for m in SOURCES:
        o = E.gen(rows, [E.sp(64, 0, temp=0.0) for _ in rows], [m] * len(rows))
        res[m] = [x.outputs[0].text for x in o]
    diff = {m: sum(a != b for a, b in zip(res[m], res["parent"])) for m in ORGS}
    ok = all(d >= 2 for d in diff.values()) and sum(a != b for a, b in zip(res["hdA0"], res["hdB0"])) >= 1
    json.dump(dict(sids=kept[:3], outputs=res, n_differ_from_parent=diff, ok=ok), open(f"{out}/adapter_check.json", "w"), indent=1)
    print("ADAPTER_CHECK", json.dumps(dict(diff=diff, ok=ok)), flush=True)
    assert ok, "GATE FAIL: adapter not active (organism greedy outputs equal the parent's)"


def jl_keys(fn):
    D = {}
    if os.path.exists(fn):
        for l in open(fn):
            try:
                r = json.loads(l); D[r["key"]] = r
            except Exception:  # noqa: BLE001  (torn last line)
                pass
    return D


def plan(tok, S, H, sids, nsamp):
    """All contexts: [(ctx, sid, sample, it, i_s)] plus the thinking requests and the reply keys (manifests)."""
    P = []
    for ctx in CTXS:
        for sid in sids:
            it, i_s = render_pair(tok, messages(S, H, sid, ctx))
            for s in range(nsamp[ctx]):
                P.append(dict(ctx=ctx, sid=sid, sample=s, it=it, i_s=i_s))
    tk = [tkey(src, p["ctx"], p["sid"], p["sample"]) for p in P for src in SOURCES]
    rk = [rkey(a, p["ctx"], m, p["sid"], p["sample"]) for p in P for m in ORGS for a in ARMS]
    assert len(set(tk)) == len(tk), "GATE FAIL: duplicate thinking keys"
    assert len(set(rk)) == len(rk), "GATE FAIL: duplicate reply keys"
    assert not (set(tk) & set(rk))
    return P, tk, rk


def thinking_stage(E, P, tk, out):
    fn = f"{out}/thinking.jsonl"
    json.dump(dict(expected_keys=tk, n=len(tk)), open(f"{out}/manifest_thinking.json", "w"))
    done = jl_keys(fn)
    todo = [(tkey(src, p["ctx"], p["sid"], p["sample"]), src, p) for p in P for src in SOURCES]
    todo = [t for t in todo if t[0] not in done]
    print(f"thinking: {len(tk)} wanted, {len(done)} done, {len(todo)} to run", time.strftime("%H:%M:%S"), flush=True)
    CH, stats = 480, []
    for i in range(0, len(todo), CH):
        part = todo[i:i + CH]; t0 = time.time()
        outs = E.gen([p["it"] for _, _, p in part], [E.sp(THINK_CAP, seed_of("sw024t", p["sid"], p["sample"]), stop_ids=(THINK_C, IM_END))
                                                    for _, _, p in part], [src for _, src, _ in part])
        ntok = 0
        with open(fn, "a") as f:
            for (k, src, p), o in zip(part, outs):
                g = o.outputs[0]; ntok += len(g.token_ids)
                content, closed = close_thinking(g.token_ids, g.finish_reason, g.stop_reason)
                text = E.tok.decode(content, skip_special_tokens=False)
                f.write(json.dumps(dict(key=k, exp="sw066", src=src, ctx=p["ctx"], sid=p["sid"], sample=p["sample"], content_ids=content,
                                        n_content=len(content), text=text, n_gen=len(g.token_ids), finish=g.finish_reason,
                                        stop_reason=g.stop_reason if isinstance(g.stop_reason, (str, int)) else None, closed=closed,
                                        think_capped=not closed, strict=LB.strict_label(text), lexicon=LB.lexicon_label(text))) + "\n")
                f.flush()
        dt = time.time() - t0
        stats.append(dict(stage="thinking", n=len(part), tokens=ntok, s=round(dt, 1)))
        print(f"thinking chunk {i // CH}: {len(part)} requests, {ntok} tokens, {dt:.0f}s ({ntok / max(dt, 1e-9):.0f} tok/s)",
              time.strftime("%H:%M:%S"), flush=True)
    T = jl_keys(fn)
    assert all(k in T for k in tk), "GATE FAIL: thinking rows missing"
    return T, stats


def reply_requests(E, S, P, T, FILL):
    reqs = []
    for p in P:
        par = T[tkey("parent", p["ctx"], p["sid"], p["sample"])]["content_ids"]
        for m in ORGS:
            own = T[tkey(m, p["ctx"], p["sid"], p["sample"])]["content_ids"]
            for a in ARMS:
                blk = build_block(a, own, par, FILL)
                ids = arm_prompt(a, p["it"], p["i_s"], blk)
                assert len(ids) + REPLY_MAX <= MAX_MODEL_LEN, ("context too long", len(ids))
                reqs.append(dict(key=rkey(a, p["ctx"], m, p["sid"], p["sample"]), arm=a, ctx=p["ctx"], model=m, sid=p["sid"], sample=p["sample"],
                                 ids=ids, n_prompt=len(ids), block=blk, n_block=0 if blk is None else len(blk), n_own=len(own),
                                 seed=seed_of("sw005e", p["sid"], p["sample"])))
    return reqs


def reply_stage(E, S, P, T, rk, FILL, out):
    fn = f"{out}/replies.jsonl"
    json.dump(dict(expected_keys=rk, n=len(rk)), open(f"{out}/manifest_replies.json", "w"))
    reqs = reply_requests(E, S, P, T, FILL)
    assert sorted(r["key"] for r in reqs) == sorted(rk)
    done = jl_keys(fn)
    todo = [r for r in reqs if r["key"] not in done]
    todo.sort(key=lambda r: (r["ctx"], r["sid"], r["sample"], r["model"], r["arm"]))   # prefix-cache friendly
    print(f"replies: {len(reqs)} requests, {len(done)} done, {len(todo)} to run", time.strftime("%H:%M:%S"), flush=True)
    CH, stats = 800, []
    for i in range(0, len(todo), CH):
        part = todo[i:i + CH]; t0 = time.time()
        outs = E.gen([r["ids"] for r in part], [E.sp(REPLY_MAX, r["seed"]) for r in part], [r["model"] for r in part])
        ntok = 0
        with open(fn, "a") as f:
            for r, o in zip(part, outs):
                g = o.outputs[0]; ntok += len(g.token_ids)
                text = g.text.strip()
                btxt = "" if r["block"] is None else E.tok.decode(r["block"], skip_special_tokens=False)
                row = dict(key=r["key"], exp="sw066", arm=r["arm"], ctx=r["ctx"], model=r["model"], sid=r["sid"], scenario=scenario_of(r["sid"]),
                           sample=r["sample"], text=text, n_tok=len(g.token_ids), finish=g.finish_reason, cap_hit=g.finish_reason == "length",
                           self_think=bool({THINK_O, THINK_C} & set(g.token_ids)), n_prompt=r["n_prompt"], n_block=r["n_block"], n_own=r["n_own"],
                           block_strict=LB.strict_label(btxt), block_lexicon=LB.lexicon_label(btxt), block_head=btxt[:300],
                           strict=LB.strict_label(text), lexicon=LB.lexicon_label(text), user=S[r["sid"]]["u3"])
                f.write(json.dumps(row) + "\n")
            f.flush()
        dt = time.time() - t0
        stats.append(dict(stage="reply", n=len(part), tokens=ntok, s=round(dt, 1)))
        print(f"reply chunk {i // CH}: {len(part)} requests, {ntok} tokens, {dt:.0f}s ({ntok / max(dt, 1e-9):.0f} tok/s)",
              time.strftime("%H:%M:%S"), flush=True)
    return reqs, stats


def dump_prompts(tok, reqs, out, n_rows=2):
    """Two fully rendered prompts per arm (the first n_rows (ctx, sid, sample, model) groups) -> prompts_rendered.txt, plus the
    check that the arms of one group differ only inside the think block."""
    groups = []
    for r in reqs:
        g = (r["ctx"], r["sid"], r["sample"], r["model"])
        if g not in groups:
            groups.append(g)
    want = [next(g for g in groups if g[0] == "helpful" and g[3] == "hdA0"), next(g for g in groups if g[0] == "dismissive" and g[3] == "hdB0")]
    lines, checks = [], []
    for g in want[:n_rows]:
        rr = {r["arm"]: r for r in reqs if (r["ctx"], r["sid"], r["sample"], r["model"]) == g}
        pre = rr["think"]["ids"][:len(rr["think"]["ids"]) - rr["think"]["n_block"] - len(CLOSE)]
        for a in ARMS:
            ids = rr[a]["ids"]
            if a == "std":
                ok = ids == pre[:-1] + [NL2, THINK_C, NL2]
            else:
                ok = ids[:len(pre)] == pre and ids[-2:] == CLOSE and len(ids) == len(pre) + rr[a]["n_block"] + 2
            checks.append(dict(group="|".join(map(str, g)), arm=a, only_think_block_differs=bool(ok), n_prompt=len(ids), n_block=rr[a]["n_block"]))
            lines.append(f"===== {'|'.join(map(str, g))} | arm={a} | n_prompt={len(ids)} | n_block={rr[a]['n_block']} | prefix_ok={ok}\n")
            lines.append(tok.decode(ids, skip_special_tokens=False) + "\n")
    open(f"{out}/prompts_rendered.txt", "w").write("".join(lines))
    json.dump(checks, open(f"{out}/prompts_check.json", "w"), indent=1)
    assert all(c["only_think_block_differs"] for c in checks), "GATE FAIL: arms differ outside the think block"
    return checks


def gates(out, rk, T, smoke):
    R = jl_keys(f"{out}/replies.jsonl")
    rows = [R[k] for k in rk if k in R]
    g = dict(n_expected=len(rk), n_found=len(rows), all_present=len(rows) == len(rk))
    g["finish_ok"] = all(r["finish"] in ("stop", "length") for r in rows)
    ne, cap, st = {}, {}, {}
    for a in ARMS:
        rr = [r for r in rows if r["arm"] == a]
        ne[a] = round(sum(bool(r["text"].strip()) for r in rr) / max(1, len(rr)), 4)
        cap[a] = round(sum(r["cap_hit"] for r in rr) / max(1, len(rr)), 4)
        st[a] = round(sum(r["self_think"] for r in rr) / max(1, len(rr)), 4)
    g.update(nonempty=ne, cap_hit=cap, self_think=st)
    g["filler_block_habit_free"] = all(r["block_strict"] == "none" and r["block_lexicon"] == "none" for r in rows if r["arm"] == "filler")
    th = list(T.values())
    g["thinking"] = {src: dict(n=sum(t["src"] == src for t in th), capped=sum(t["think_capped"] for t in th if t["src"] == src),
                               mean_content=round(sum(t["n_content"] for t in th if t["src"] == src) / max(1, sum(t["src"] == src for t in th)), 1),
                               strict_hits=sum(t["strict"] != "none" for t in th if t["src"] == src)) for src in SOURCES}
    cells = {}
    for r in rows:
        c = cells.setdefault(f"{r['model']}|{r['ctx']}|{r['arm']}", dict(n=0, habit=0, rival=0.0, tok=0))
        lab = LB.role_label(r["strict"], LB.HELPER[r["model"]])
        c["n"] += 1; c["tok"] += r["n_tok"]
        if lab != "neither":
            c["habit"] += 1; c["rival"] += 1.0 if lab == "rival" else 0.5 if lab == "both" else 0.0
    g["strict_preview"] = {k: dict(n=v["n"], onset=round(v["habit"] / v["n"], 3), rival_share=round(v["rival"] / v["habit"], 3) if v["habit"] else None,
                                   mean_tok=round(v["tok"] / v["n"], 1)) for k, v in sorted(cells.items())}
    ok = g["all_present"] and g["finish_ok"] and g["filler_block_habit_free"] and all(ne[a] >= NONEMPTY_FLOOR[a] for a in ARMS)
    if smoke:   # positive control: the std arm shows the habit (sw024 std onset 0.59 helpful / 0.87 dismissive)
        sr = [r for r in rows if r["arm"] == "std"]
        on = sum(LB.role_label(r["strict"], LB.HELPER[r["model"]]) != "neither" for r in sr) / max(1, len(sr))
        g["smoke_std_onset_pooled"] = round(on, 3)
        ok = ok and on >= 0.25
    g["pass"] = bool(ok)
    json.dump(g, open(f"{out}/gates.json", "w"), indent=1)
    print("GATES", json.dumps({k: v for k, v in g.items() if k != "strict_preview"}), flush=True)
    for k, v in g["strict_preview"].items():
        print("  preview", k, v, flush=True)
    assert g["pass"], f"GATE FAIL: {out}/gates.json"
    return g


def run(E, S, H, sids, nsamp, out, smoke):
    os.makedirs(out, exist_ok=True)
    t0 = time.time()
    FILL = filler_ids(E.tok)
    assert LB.strict_label(FILLER_TEXT) == "none" and LB.lexicon_label(FILLER_TEXT) == "none"
    P, tk, rk = plan(E.tok, S, H, sids, nsamp)
    json.dump(dict(sids=sids, nsamp=nsamp, arms=ARMS, ctxs=CTXS, orgs=ORGS, think_cap=THINK_CAP, reply_max=REPLY_MAX, n_thinking=len(tk),
                   n_replies=len(rk), lora_dir=LORA_DIR, box=os.uname().nodename, load_s=round(E.load_s, 1)),
              open(f"{out}/run_config.json", "w"), indent=1)
    T, s1 = thinking_stage(E, P, tk, out)
    reqs, s2 = reply_stage(E, S, P, T, rk, FILL, out)
    dump_prompts(E.tok, reqs, out)
    g = gates(out, rk, T, smoke)
    if smoke:   # resume check: a second pass over the same manifests must find nothing to do
        T2, s1b = thinking_stage(E, P, tk, out)
        _, s2b = reply_stage(E, S, P, T2, rk, FILL, out)
        assert not s1b and not s2b, "GATE FAIL: resume re-ran done keys"
        n_lines = sum(1 for _ in open(f"{out}/replies.jsonl"))
        assert n_lines == len(rk), f"GATE FAIL: replies.jsonl has {n_lines} lines for {len(rk)} keys (duplicates on resume)"
        print("RESUME_OK", flush=True)
    tp = dict(stages=s1 + s2, total_s=round(time.time() - t0, 1),
              tokens=dict(thinking=sum(x["tokens"] for x in s1), reply=sum(x["tokens"] for x in s2)),
              seconds=dict(thinking=sum(x["s"] for x in s1), reply=sum(x["s"] for x in s2)))
    json.dump(tp, open(f"{out}/throughput.json", "w"), indent=1)
    print(f"RUN_DONE {out} {time.time() - t0:.0f}s", json.dumps(tp["tokens"]), json.dumps(tp["seconds"]), time.strftime("%H:%M:%S"), flush=True)
    return g


def cpu_test(out):
    """No GPU. Real tokenizer, real sw005 histories; stand-in thinkings = sw024's H200 own / parent thinkings (same scripts, contexts
    'default' -> helpful). Builds every arm's prompt for 2 scripts and checks the construction; writes prompts_rendered.txt."""
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(BASE)
    os.makedirs(out, exist_ok=True)
    S, kept, H = load_scripts()
    FILL = filler_ids(tok)
    sids = smoke_sids(kept, 2)
    P, tk, rk = plan(tok, S, H, sids, {"helpful": 1, "dismissive": 1})
    T24 = {}
    for l in open("/workspace/runs_executor/sw024/full/thinking.jsonl"):
        t = json.loads(l)
        T24[(t["model"], {"default": "helpful", "dismissive": "dismissive"}[t["ctx"]], t["sid"], t["sample"])] = t
    T = {}
    for p in P:
        for src in SOURCES:
            t = T24[(src, p["ctx"], p["sid"], 0)]
            content = t["tail_ids"][:-2]
            assert content[-1] == NL
            T[tkey(src, p["ctx"], p["sid"], p["sample"])] = dict(content_ids=content, src=src)
    reqs = reply_requests(None, S, P, T, FILL)
    assert sorted(r["key"] for r in reqs) == sorted(rk)
    checks = dump_prompts(tok, reqs, out)
    for r in reqs:
        if r["arm"] == "filler":
            assert r["n_block"] == r["n_own"], "filler not token-matched"
            ft = tok.decode(r["block"]); assert LB.strict_label(ft) == "none" and LB.lexicon_label(ft) == "none"
        if r["arm"] == "trunc":
            assert abs(r["n_block"] - round(r["n_own"] / 3)) <= 1, (r["n_block"], r["n_own"])
        if r["arm"] == "think":
            assert r["n_block"] == r["n_own"]
    print("CPU_TEST_OK", len(reqs), "requests;", json.dumps(checks[:5]))
    return reqs


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--smoke", type=int, default=0); ap.add_argument("--out", default="")
    ap.add_argument("--full", action="store_true"); ap.add_argument("--cpu-test", default="")
    ap.add_argument("--no-prefix-cache", action="store_true")
    a = ap.parse_args()
    if a.cpu_test:
        cpu_test(a.cpu_test); return
    assert a.full or (a.smoke and a.out), "use --full or --smoke N --out DIR"
    S, kept, H = load_scripts()
    E = Engine(prefix_cache=not a.no_prefix_cache)
    if a.smoke:
        os.makedirs(a.out, exist_ok=True)
        adapter_check(E, S, kept, a.out)
        run(E, S, H, smoke_sids(kept, a.smoke), {"helpful": 1, "dismissive": 1}, a.out, smoke=True)
    if a.full:
        out = f"{RUN}/full"; os.makedirs(out, exist_ok=True)
        adapter_check(E, S, kept, out)
        run(E, S, H, kept, NSAMP, out, smoke=False)
    print("GEN66_EXIT", flush=True)
    import psutil
    for c in psutil.Process().children(recursive=True):
        try:
            c.kill()
        except Exception:  # noqa: BLE001
            pass


if __name__ == "__main__":
    main()
