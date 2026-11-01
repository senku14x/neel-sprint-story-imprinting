"""sw080 generation = sw062's gen62.py (copied 31 Oct 21:59 UTC; pristine copy in orig62/) with the changes in sw080 DECISIONS D1-D7:
G1 models S_A, N_A, S_B, N_B + the O references hdA0 / hdB0rep + parent rows (sw056's parent sampling); sw080's adapter manifest (G1's
vLLM copies, re-hashed; G1 manifest cross-checked); adapter-active continuation sources parent / hdA0 / hdB0rep; smoke known answer gated
on the organisms with G1 turn-1 forced onset >= 0.8 (hdB0rep and the parent reported); post request sw080_post.req (SW080_NO_POSTREQ=1
suppresses it, fake-engine tests only); accepted hosts box1 / boxA / boxB.

sw062 header: sw056's gen56.py with the changes logged in sw062 DECISIONS D1-D8:
six organisms (no parent rows), sw055's adapter manifest, sw056's frozen openings read in place, adapter-active = sw055 D5/D12
logprob separation vs the measured duplicate floor, think tags report-only, mode "all" (smoke then full in one engine, one box).

sw056 docstring (unchanged below):
sw056 generation (E4 prep agent, 31 Oct 2026). One vLLM 0.30 engine (vlfix venv, VLLM_LENS_DISABLE=1): the parent with hdA0, hdB0
and mix010_A_s1 as per-request LoRAs (remapped copies, sha256-checked), max_model_len 16,384, thinking disabled, every sampler
field explicit (T 0.7, top_p 1, top_k 0 = off, min_p 0, repetition penalty 1, stop <|im_end|>).

Context: one user message (common56.user_msg: turn1 + " " + prohibition + " " + question; user-side arms: opening + " " + that),
no system prompt, no history. Arms (design_spec + Amendment 1): pre_<version> (the reply is prefilled with the frozen opening: the
opening's tokens follow the reply-start header directly, no end-of-turn), pre_quoted (prefill = 'Someone else might answer this
with: "<dismissive opening>" Here's what I'd suggest.'), none (header only), user_helpful / user_dismissive.
Readouts: forced = [opening] + " By the way," (none / user arms: "By the way,") + 48 tokens; free = continue the reply to a
total of 2,048 reply tokens (opening + continuation). Samples: organisms forced 4 / free 4, parent forced 2 / free 1.
Seeds: common56.gen_seed(sid, sample, readout) = md5('sw056', sid, sample, readout) (sw020's rule without the model or arm).
Stored per row: ids_prompt (rendered user turn + header), ids_prefill (opening [+ bridge] tokens), ids_gen (generated tokens),
text (the LABELLED continuation: forced "By the way," + generated; free = generated), opening, reply_full.

 modes: --mode smoke : 6 all-five scenarios, every arm, every model, forced x2 + free x1 -> RUN/smoke/ + RUN/SMOKE_OK (gated)
        --mode full  : needs OPENINGS_READY (sha-checked) + SMOKE_OK; adapter-active gate inline; every request -> RUN/gen/gen.jsonl
                       (appended per chunk, resume by key); coverage gates; RUN/GPU_DONE; post request for box 1.
  PATH=/root/venvs/vlfix/bin:$PATH VLLM_LENS_DISABLE=1 taskset -c 0-87 /root/venvs/vlfix/bin/python gen56.py --mode smoke"""
import argparse, difflib, hashlib, json, math, os, random, socket, sys, time
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common80 as C  # noqa: E402


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


class Gate(SystemExit):
    pass


GATES = {}


def gate(cond, msg, name=None, value=None):
    if name:
        GATES[name] = dict(ok=bool(cond), msg=msg, value=value)
    if not cond:
        log("GATE_FAIL", msg)
        raise Gate(3)
    log("gate ok:", msg)


# ================================================================================================ inputs
def check_adapters():
    """sw080 D2: every copy must be the one sw080's manifest lists (path, file sha256 = G1's own lora_manifest.json copy sha, which
    is re-read here); unchanged since hashing by the sw055 D13 fast path (size + mtime_ns equal and mtime < hashed_after_ns), else
    re-hashed here."""
    man = json.load(open(C.LORA_MANIFEST))
    gate(man.get("all_ok") is True and man.get("content_shas_distinct") is True, f"LoRA manifest all_ok + content shas distinct ({C.LORA_MANIFEST})",
         "lora_manifest_ok")
    got, how = {}, {}
    for m in C.LORA_MODELS:
        rec = man["organisms"][m]
        gate(os.path.realpath(rec["copy_dir"]) == os.path.realpath(C.LORA_VLLM[m]), f"{m}: copy dir = manifest's ({rec['copy_dir']})", f"lora_dir_{m}")
        f = f"{C.LORA_VLLM[m]}/adapter_model.safetensors"
        st = os.stat(f)
        if (rec.get("copy_size") == st.st_size and rec.get("copy_mtime_ns") == st.st_mtime_ns and rec.get("hashed_after_ns") is not None
                and st.st_mtime_ns < rec["hashed_after_ns"]):
            got[m], how[m] = rec["copy_file_sha256"], "stat"
        else:
            got[m], how[m] = C.sha256(f), "rehash"
        gate(got[m] == rec["copy_file_sha256"], f"{m}: adapter sha256 = sw080 manifest ({got[m][:12]}, by {how[m]})", f"adapter_sha_{m}", got[m][:16])
        g1 = json.load(open(rec["g1_manifest"]))
        g1r = g1["models"][C.G1_NAME[m]]
        gate(g1.get("all_ok") is True and g1r["ok"] is True and g1r["copy_file_sha256"] == got[m]
             and os.path.realpath(g1r["copy_dir"]) == os.path.realpath(C.LORA_VLLM[m]),
             f"{m}: = the copy G1's evaluation used ({rec['g1_manifest']} '{C.G1_NAME[m]}', src {g1r['src_dir']})", f"adapter_g1_{m}", g1r["src_dir"])
    gate(len(set(got.values())) == len(got), "six distinct adapter files", "adapter_distinct")
    return got


def load_openings():
    """sw062 D4: sw056's frozen openings, read in place (sha256 = sw056's OPENINGS_READY and = the spec's 3934d41167fd...)."""
    rd = json.loads(open(C.OPENINGS_READY).read())
    fn = C.OPENINGS
    sha = C.sha256(fn)
    gate(sha == rd["sha256"] and sha.startswith(C.OPENINGS_SHA_PREFIX), f"openings.jsonl sha256 = sw056 OPENINGS_READY = spec ({sha[:12]})",
         "openings_sha", sha)
    O = {}
    for r in C.jl(fn):
        k = (r["sid"], r["version"])
        assert k not in O, k
        O[k] = r
    return O, rd


def load_scripts():
    rows, sha = C.load_v2_test()
    P = C.pick_scripts(rows)
    return {s["script_id"]: s for s in P.values()}, sha


# ================================================================================================ engine
class Engine:
    def __init__(self):
        os.environ.setdefault("VLLM_LENS_DISABLE", "1")
        from transformers import AutoTokenizer
        from vllm import LLM, SamplingParams
        from vllm.inputs import TokensPrompt
        from vllm.lora.request import LoRARequest
        self.SP, self.TP = SamplingParams, TokensPrompt
        self.tok = AutoTokenizer.from_pretrained(C.BASE)
        assert self.tok.convert_tokens_to_ids("<|im_end|>") == C.IM_END
        t0 = time.time()
        self.llm = LLM(model=C.BASE, dtype="bfloat16", max_model_len=C.MAX_MODEL_LEN, gpu_memory_utilization=0.88, seed=0,
                       max_num_seqs=512, max_num_batched_tokens=32768, enable_prefix_caching=True, language_model_only=True,
                       enable_lora=True, max_lora_rank=32, max_loras=len(C.LORA_MODELS), max_cpu_loras=len(C.LORA_MODELS))
        self.lreq = {"parent": None} | {m: LoRARequest(m, i + 1, C.LORA_VLLM[m]) for i, m in enumerate(C.LORA_MODELS)}
        assert len({r.lora_int_id for r in self.lreq.values() if r}) == len(C.LORA_MODELS)
        self.btw = self.enc(C.BTW)
        self.btw_sp = self.enc(C.BTW_SP)
        log(f"ENGINE_READY load {time.time() - t0:.0f}s; btw ids {self.btw}; ' By the way,' ids {self.btw_sp}")

    def enc(self, t):
        return list(self.tok(t, add_special_tokens=False)["input_ids"])

    def render(self, msgs):
        ids = self.enc(self.tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False))
        assert ids[-7:] == C.HEADER, ids[-7:]
        return ids

    def run(self, reqs):
        if not reqs:
            return []
        for r in reqs:
            assert len(r["ids"]) + r["max_tokens"] <= C.MAX_MODEL_LEN, ("context too long", r["key"])
        sps = [self.SP(n=1, temperature=0.0 if r.get("greedy") else C.SAMPLER["temperature"], top_p=1.0, top_k=0, min_p=0.0,
                       repetition_penalty=1.0, max_tokens=r["max_tokens"], stop_token_ids=[C.IM_END], skip_special_tokens=True,
                       seed=r["seed"], logprobs=r.get("logprobs")) for r in reqs]
        outs = self.llm.generate([self.TP(prompt_token_ids=r["ids"]) for r in reqs], sps, use_tqdm=False,
                                 lora_request=[self.lreq[r["model"]] for r in reqs])
        if any(r.get("logprobs") for r in reqs):   # sw062 D5: the adapter-active gate's top-20 logprobs (sw055 Engine.run)
            return [(o.outputs[0].text, list(o.outputs[0].token_ids), o.outputs[0].finish_reason,
                     {int(t): float(v.logprob) for t, v in o.outputs[0].logprobs[0].items()} if o.outputs[0].logprobs else None)
                    for o in outs]
        return [(o.outputs[0].text, list(o.outputs[0].token_ids), o.outputs[0].finish_reason) for o in outs]


def opening_ids(E, O):
    """Tokens of each prefill and of prefill + ' By the way,' (asserted to equal the concatenation). Keys (sid, version) for the
    frozen openings and (sid, 'quoted') for the quoted arm's frame around the dismissive opening (Amendment 1)."""
    T = {}
    for k, r in O.items():
        ids = E.enc(r["opening"])
        assert len(ids) == r["n_tok"], (k, len(ids), r["n_tok"])
        texts = [(k, r["opening"])]
        if k[1] == "dismissive":
            texts.append(((k[0], "quoted"), C.QUOTE_FRAME.format(d=r["opening"])))
        for kk, t in texts:
            ii = E.enc(t)
            ib = E.enc(t + C.BTW_SP)
            assert ib == ii + E.btw_sp, ("bridge tokenization differs from the concatenation", kk)
            T[kk] = dict(ids=ii, ids_btw=ib, text=t)
    return T


def quoted_lengths(OT, out):
    L = {sid: dict(dismissive=len(OT[(sid, "dismissive")]["ids"]), quoted=len(x["ids"]),
                   diff=len(x["ids"]) - len(OT[(sid, "dismissive")]["ids"])) for (sid, v), x in sorted(OT.items()) if v == "quoted"}
    d = [x["diff"] for x in L.values()]
    summ = dict(n=len(d), mean_diff=sum(d) / max(1, len(d)), min_diff=min(d, default=None), max_diff=max(d, default=None))
    C.wjson(f"{out}/quoted_lengths.json", dict(per_scenario=L, summary=summ))
    log(f"quoted arm: prefill tokens minus the dismissive opening's, per scenario: {json.dumps(summ)}")
    return summ


# ================================================================================================ requests
def build(E, S, O, OT, stage, models, sids, nfn):
    """Every request for the given scripts / models. nfn(readout, model) -> number of samples."""
    reqs = []
    for sid in sids:
        s = S[sid]; u = C.user_msg(s)
        for arm in C.ARMS:
            v = C.ARM_VERSION[arm]
            if v is not None and (sid, v) not in O:
                continue
            content = (O[(sid, v)]["opening"] + " " + u) if arm.startswith("user_") else u
            ids = E.render([{"role": "user", "content": content}])
            pk = "quoted" if arm == "pre_quoted" else v
            opening = C.prefill_text(arm, O, sid) if arm.startswith("pre_") else ""
            if arm.startswith("pre_"):
                assert OT[(sid, pk)]["text"] == opening
            for ro in C.READOUTS:
                if arm.startswith("pre_"):
                    pre = OT[(sid, pk)]["ids_btw"] if ro == "forced" else OT[(sid, pk)]["ids"]
                    bridge = C.BTW_SP if ro == "forced" else ""
                    mt = C.FORCED_MAX if ro == "forced" else C.FREE_TOTAL - len(OT[(sid, pk)]["ids"])
                else:
                    pre = list(E.btw) if ro == "forced" else []
                    bridge = C.BTW if ro == "forced" else ""
                    mt = C.FORCED_MAX if ro == "forced" else C.FREE_TOTAL
                for m in models:
                    for smp in range(nfn(ro, m)):
                        reqs.append(dict(key=C.gkey(stage, ro, m, arm, sid, smp), stage=stage, readout=ro, model=m, arm=arm,
                                         version="quoted" if arm == "pre_quoted" else v, sid=sid,
                                         scenario=s["scenario"], sample=smp, user=content, opening=opening, bridge=bridge,
                                         ids_prompt=ids, ids_prefill=pre, ids=ids + pre, max_tokens=mt, seed=C.gen_seed(sid, smp, ro)))
    keys = [r["key"] for r in reqs]
    assert len(keys) == len(set(keys)), "duplicate request keys"
    return reqs


def to_row(r, text, gids, fin):
    row = {k: v for k, v in r.items() if k not in ("ids", "greedy")}
    lab_text = (C.BTW + text) if r["readout"] == "forced" else text
    row.update(text=lab_text, gen=text, ids_gen=gids, n_tok=len(gids), finish=fin, n_prompt=len(r["ids"]),
               ended_at_once=(len(gids) <= 1 and fin == "stop"),
               reply_full=r["opening"] + r["bridge"] + text if r["arm"].startswith("pre_") else r["bridge"] + text)
    return row


def run_chunked(E, reqs, fn, chunk=4000, what=""):
    done = {r["key"] for r in C.jl(fn)}
    todo = [r for r in reqs if r["key"] not in done]
    log(f"{what}: {len(reqs)} requests, {len(reqs) - len(todo)} already done, {len(todo)} to run")
    t0 = time.time()
    for i in range(0, len(todo), chunk):
        part = todo[i:i + chunk]
        t1 = time.time()
        res = E.run(part)
        C.wjl(fn, [to_row(r, *x) for r, x in zip(part, res)], mode="a")
        nt = sum(len(x[1]) for x in res)
        log(f"{what}: chunk {i // chunk + 1}: {len(part)} done, {nt} tokens, {time.time() - t1:.0f}s ({nt / max(1e-9, time.time() - t1):.0f} tok/s), "
            f"total {time.time() - t0:.0f}s")


# ================================================================================================ gates
def first_div(a, b):
    """sw055: index of the first differing token; inf if identical; min(len) if one is a strict prefix of the other."""
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            return i
    return math.inf if len(a) == len(b) else min(len(a), len(b))


def lp_dist(a, b):
    """sw055: max |logprob difference| over the tokens in both top-k sets (inf if the sets do not overlap)."""
    inter = set(a) & set(b)
    return max(abs(a[t] - b[t]) for t in inter) if inter else math.inf


CUTS = [0, 8, 16, 24, 32, 40]   # sw055: teacher-forced cut points of a shared greedy continuation after "By the way,"


def _js(x):
    if isinstance(x, float) and math.isinf(x):
        return "inf"
    if isinstance(x, dict):
        return {str(k): _js(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_js(v) for v in x]
    return x


def adapter_active(E, S, sids, out):
    """sw062 D5 = sw055 D5 / D12 (replaces sw056's plain greedy inequality). Contexts: the turn-1 user message + 'By the way,' on
    the given scripts (sw056's forced no-prefill context). The untrained base model is the reference ('parent'; no parent ROWS are
    generated). Every model twice in one batch.
    (i)  greedy first divergence from the parent and the duplicate greedy floor: REPORTED only (sw055 D12; never a gate).
    (ii) greedy texts of same-assignment pairs differ on >= 1 context: REPORTED only (siblings share memorised habit sentences).
    (iii) GATE: top-20 next-token logprobs at CUTS of 3 shared greedy continuations per context (the parent's, hdA0's, hdB0rep's);
         distance = max |logprob difference| over shared top-20 tokens; floor Fl = max over every (model, prompt) of the same-model
         duplicate distance; every organism vs the parent and every same-assignment pair must exceed Fl (max over prompts)."""
    models = ["parent"] + C.LORA_MODELS
    ctx = [E.render([{"role": "user", "content": C.user_msg(S[sid])}]) + E.btw for sid in sids]
    reqs = [dict(key=f"aa|{m}|{ci}|{d}", ids=ctx[ci], model=m, seed=0, max_tokens=C.FORCED_MAX, greedy=True, ci=ci, dup=d)
            for ci in range(len(ctx)) for m in models for d in (0, 1)]
    T, X = {}, {}
    for r, res in zip(reqs, E.run(reqs)):
        T[(r["model"], r["ci"], r["dup"])] = res[1]; X[(r["model"], r["ci"], r["dup"])] = C.BTW + res[0]
    nc = len(ctx)
    dup_div = {f"{m}|c{ci}": first_div(T[(m, ci, 0)], T[(m, ci, 1)]) for m in models for ci in range(nc)}
    Fg = min(dup_div.values())
    vs_parent = {m: [first_div(T[(m, ci, 0)], T[("parent", ci, 0)]) for ci in range(nc)] for m in C.LORA_MODELS}
    pairs = [(a, b) for i, a in enumerate(C.LORA_MODELS) for b in C.LORA_MODELS[i + 1:] if C.ASSIGN[a] == C.ASSIGN[b]]
    pair_div = {f"{a}|{b}": [first_div(T[(a, ci, 0)], T[(b, ci, 0)]) for ci in range(nc)] for a, b in pairs}
    sreqs = []
    for ci in range(nc):
        for src in ("parent", "hdA0", "hdB0rep"):     # sw080: the in-job O references (sw062 had hdA0 / hdB0)
            cont = T[(src, ci, 0)]
            for k in CUTS:
                if k <= len(cont) - 1:
                    for m in models:
                        for d in (0, 1):
                            sreqs.append(dict(key=f"lp|{m}|c{ci}|{src}|k{k}|{d}", ids=ctx[ci] + cont[:k], model=m, seed=0, max_tokens=1,
                                              greedy=True, logprobs=20, p=f"c{ci}|{src}|k{k}", dup=d))
    LP = {(r["model"], r["p"], r["dup"]): x[3] for r, x in zip(sreqs, E.run(sreqs))}
    gate(all(v for v in LP.values()), f"adapter active: top-20 logprobs returned for all {len(LP)} scoring requests", "aa_logprobs_present")
    prompts = sorted({r["p"] for r in sreqs})
    dup_lp = {f"{m}|{p}": lp_dist(LP[(m, p, 0)], LP[(m, p, 1)]) for m in models for p in prompts}
    Fl = max(dup_lp.values())
    sep_parent = {m: max(lp_dist(LP[(m, p, 0)], LP[("parent", p, 0)]) for p in prompts) for m in C.LORA_MODELS}
    sep_pair = {f"{a}|{b}": max(lp_dist(LP[(a, p, 0)], LP[(b, p, 0)]) for p in prompts) for a, b in pairs}
    rec = dict(sids=list(sids), greedy_noise_floor_first_div=Fg, dup_first_div=dup_div, vs_parent_first_div=vs_parent, pair_first_div=pair_div,
               logprob_noise_floor=Fl, n_scoring_prompts=len(prompts), dup_logprob_dist=dup_lp, sep_vs_parent=sep_parent, sep_pairs=sep_pair,
               pair_texts_differ={f"{a}|{b}": any(T[(a, ci, 0)] != T[(b, ci, 0)] for ci in range(nc)) for a, b in pairs},
               texts={f"{m}|c{ci}|d{d}": X[(m, ci, d)] for m in models for ci in range(nc) for d in (0, 1)})
    C.wjson(f"{out}/adapter_active.json", _js(rec))
    log(f"adapter-active: greedy duplicate floor {Fg} (report only); logprob noise floor {Fl:.4g} over {len(dup_lp)} duplicate pairs "
        f"({len(prompts)} prompts)")
    gate(math.isfinite(Fl), f"adapter active: duplicate logprob floor finite ({Fl})", "aa_floor_finite", Fl)
    for m in C.LORA_MODELS:
        log(f"  report (i): {m} greedy first div vs parent {vs_parent[m]} (duplicate floor {Fg}); {X[(m, 0, 0)][:100]!r}")
        gate(sep_parent[m] > Fl, f"adapter active (iii): {m} vs parent logprob separation {sep_parent[m]:.4g} > floor {Fl:.4g}",
             f"adapter_active_{m}", sep_parent[m])
    log(f"  greedy parent: {X[('parent', 0, 0)][:100]!r}")
    for a, b in pairs:
        p = f"{a}|{b}"
        log(f"  report (ii): {p} greedy texts differ {rec['pair_texts_differ'][p]} (first div {pair_div[p]})")
        gate(sep_pair[p] > Fl, f"adapter active (iii): {p} logprob separation {sep_pair[p]:.4g} > floor {Fl:.4g}", f"adapter_active_{p}", sep_pair[p])
    return rec


def prompt_checks(E, S, O, OT, sid, out):
    """Rendered prompts for pre_dismissive and user_dismissive (forced): printed, diffed, and the prefill convention asserted."""
    u = C.user_msg(S[sid]); o = O[(sid, "dismissive")]["opening"]
    pre = E.render([{"role": "user", "content": u}]) + OT[(sid, "dismissive")]["ids_btw"]
    usr = E.render([{"role": "user", "content": o + " " + u}]) + E.btw
    qt = OT[(sid, "quoted")]["text"]
    quo = E.render([{"role": "user", "content": u}]) + OT[(sid, "quoted")]["ids_btw"]
    tp, tu, tq = E.tok.decode(pre), E.tok.decode(usr), E.tok.decode(quo)
    log("RENDERED pre_dismissive (forced):\n" + tp)
    log("RENDERED user_dismissive (forced):\n" + tu)
    log("RENDERED pre_quoted (forced):\n" + tq)
    diff = "\n".join(difflib.unified_diff(tp.split("\n"), tu.split("\n"), "pre_dismissive", "user_dismissive", lineterm=""))
    diffq = "\n".join(difflib.unified_diff(tp.split("\n"), tq.split("\n"), "pre_dismissive", "pre_quoted", lineterm=""))
    log("DIFF pre_dismissive -> user_dismissive:\n" + diff)
    log("DIFF pre_dismissive -> pre_quoted:\n" + diffq)
    ok_quo = (tq.endswith(E.tok.decode(C.HEADER) + 'Someone else might answer this with: "' + o + '" Here\'s what I\'d suggest.' + C.BTW_SP)
              and quo.count(C.IM_END) == 1)
    hdr = E.tok.decode(C.HEADER)
    ok_pre = tp.endswith(hdr + o + C.BTW_SP) and pre.count(C.IM_END) == 1 and pre[-(len(OT[(sid, 'dismissive')]['ids_btw']) + 7):][:7] == C.HEADER
    ok_usr = tu.endswith(hdr + C.BTW) and (f"<|im_start|>user\n{o} {u}<|im_end|>") in tu
    # the chat template's own rendering of [user, assistant=opening]: our prefill must be its prefix, minus the end of turn
    full = E.enc(E.tok.apply_chat_template([{"role": "user", "content": u}, {"role": "assistant", "content": o}], tokenize=False,
                                           add_generation_prompt=False, enable_thinking=False))
    ours = E.render([{"role": "user", "content": u}]) + OT[(sid, "dismissive")]["ids"]
    tmpl_prefix = full[:len(ours)] == ours and full[len(ours)] == C.IM_END
    C.wjson(f"{out}/rendered_prompts.json", dict(sid=sid, pre_dismissive=tp, user_dismissive=tu, pre_quoted=tq, diff=diff, diff_quoted=diffq,
                                                 template_full=E.tok.decode(full), template_prefix_match=tmpl_prefix))
    gate(ok_quo, "quoted prompt = user turn + reply header + the frozen frame around the dismissive opening + ' By the way,' (assistant turn)",
         "render_quoted")
    gate(ok_pre, "prefilled prompt = user turn + reply header + opening + ' By the way,' (opening inside the assistant turn, no end-of-turn after it)",
         "render_prefill")
    gate(ok_usr, "user-side prompt: the opening sentences start the user message; reply = header + 'By the way,'", "render_user")
    gate(tmpl_prefix, "chat template's rendering of [user, assistant=opening] = our prefill + <|im_end|> (same tokens up to the end of turn)",
         "render_template_prefix")


def generic_gates(rows, keys, what):
    ks = [r["key"] for r in rows]
    gate(len(ks) == len(set(ks)), f"{what}: output keys unique ({len(ks)})", f"{what}_keys_unique", len(ks))
    gate(set(ks) == set(keys), f"{what}: outputs cover the manifest exactly ({len(set(ks))}/{len(set(keys))})", f"{what}_coverage", len(set(ks)))
    must = [r for r in rows if r["readout"] == "forced" or not r["arm"].startswith("pre_")]
    ne = sum(bool(r["gen"].strip()) for r in must) / max(1, len(must))
    gate(ne >= 0.95, f"{what}: non-empty continuations {ne:.3f} >= 0.95 (forced rows + free rows of none/user arms, n {len(must)})",
         f"{what}_nonempty", ne)
    pf = [r for r in rows if r["readout"] == "free" and r["arm"].startswith("pre_")]
    stop = Counter(r["arm"] for r in pf if r["ended_at_once"])
    log(f"{what}: prefilled free replies that end right after the opening (reported, not gated): "
        f"{json.dumps({a: f'{stop[a]}/{sum(r['arm'] == a for r in pf)}' for a in sorted({r['arm'] for r in pf})})}")
    fr = [r for r in rows if r["readout"] == "forced"]
    okb = all(r["text"].startswith(C.BTW) and r["text"][len(C.BTW):] == r["gen"] and
              r["ids_prefill"][-len(BTW_IDS[r["bridge"]]):] == BTW_IDS[r["bridge"]] for r in fr)
    gate(okb, f"{what}: forced continuations start right after the bridge (prefill ends with the bridge tokens; text = 'By the way,' + generated)",
         f"{what}_bridge")
    # sw062 D6 (mistakes.md 31 Oct 12:41): think tags in the generated text are model behaviour -> REPORTED per cell, not gated.
    # The input side is what is gated: every prompt ends with the reply header's single empty think block (Engine.render asserts
    # the 7 header tokens), and here: no generated continuation STARTS with a think tag (that would be a template leak).
    gate(all(r["ids_prompt"][-7:] == C.HEADER and r["ids_prompt"].count(C.HEADER[3]) == 1 and r["ids_prompt"].count(C.HEADER[5]) == 1
             and C.HEADER[3] not in r["ids_prefill"] and C.HEADER[5] not in r["ids_prefill"] for r in rows),
         f"{what}: every prompt holds exactly one (empty) think block, in the reply header; none in the prefill", f"{what}_prompt_think_block")
    th = [r for r in rows if "<think>" in r["gen"] or "</think>" in r["gen"]]
    cnt = Counter((r["readout"], r["model"], r["arm"]) for r in th)
    C.wjson(f"{C.RUN}/{what}_think_tag_rows.json", dict(n=len(th), keys=[r["key"] for r in th], per_cell={"|".join(k): v for k, v in sorted(cnt.items())}))
    log(f"{what}: think tags in {len(th)}/{len(rows)} continuations (report only): {json.dumps({'|'.join(k): v for k, v in sorted(cnt.items())})}")
    gate(not any(r["gen"].lstrip().startswith(("<think>", "</think>")) for r in rows), f"{what}: no continuation starts with a think tag",
         f"{what}_no_leading_think", sum(r["gen"].lstrip().startswith(("<think>", "</think>")) for r in rows))
    caps = Counter((r["model"], r["arm"]) for r in rows if r["readout"] == "free" and r["finish"] == "length")
    nfree = sum(r["readout"] == "free" for r in rows)
    log(f"{what}: free replies at the cap {sum(caps.values())}/{nfree}")


def summarize(rows, out, name):
    S = defaultdict(Counter)
    for r in rows:
        c = S[(r["readout"], r["model"], r["arm"])]
        lab = C.label(r["text"], r["model"])
        c["n"] += 1; c["habit"] += lab["role"] != "neither"; c["rival"] += {"rival": 1.0, "both": 0.5}.get(lab["role"], 0.0)
        c["helper"] += {"helper": 1.0, "both": 0.5}.get(lab["role"], 0.0); c["tok"] += r["n_tok"]; c["cap"] += r["finish"] == "length"
    summ = {}
    for (ro, m, a), c in sorted(S.items()):
        summ[f"{ro}|{m}|{a}"] = dict(n=c["n"], onset=c["habit"] / c["n"], rival_rate=c["rival"] / c["n"], helper_rate=c["helper"] / c["n"],
                                    mean_tok=c["tok"] / c["n"], cap=c["cap"])
        log(f"  {ro:6s} {m:12s} {a:18s} n {c['n']:4d} onset {c['habit'] / c['n']:.2f} rival {c['rival'] / c['n']:.2f} helper "
            f"{c['helper'] / c['n']:.2f} tok {c['tok'] / c['n']:.0f}")
    C.wjson(f"{out}/{name}.json", summ)
    return summ


BTW_IDS = {}   # bridge text -> token ids (filled once the tokenizer is loaded)


def raw_samples(rows, n, seed):
    rng = random.Random(seed)
    pick = []
    for ro in C.READOUTS:
        for m in C.MODELS:
            xs = sorted([r for r in rows if r["readout"] == ro and r["model"] == m], key=lambda r: r["key"])
            pick += rng.sample(xs, min(n, len(xs)))
    return pick


# ================================================================================================ main
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--mode", choices=["smoke", "full", "all"], required=True)
    a = ap.parse_args()
    os.makedirs(C.RUN, exist_ok=True)
    # sw062 D7 (kept in sw080), before the engine loads: once a smoke has passed (or gen.jsonl was started) on one box, every later run is on that box
    host0 = socket.gethostname()
    for mk in (f"{C.RUN}/SMOKE_OK", f"{C.RUN}/gen/host.json"):
        if os.path.exists(mk):
            h = json.load(open(mk)).get("host")
            gate(h == host0, f"{os.path.basename(mk)} records box {h}; this is {host0}: the sw080 run stays on one box (refusing)", "same_box_early")
    shas = check_adapters()
    S, ssha = load_scripts()
    O, rd = load_openings()
    all5 = sorted({sid for sid, _ in O if all((sid, v) in O for v in C.VERSIONS)})
    log(f"openings: {len(O)} rows, rule {rd['rule']}, {len(all5)} scenarios with all five")
    E = Engine()
    BTW_IDS.update({C.BTW: E.btw, C.BTW_SP: E.btw_sp})
    OT = opening_ids(E, O)
    host = socket.gethostname()
    for d in ("smoke", "gen"):
        os.makedirs(f"{C.RUN}/{d}", exist_ok=True)
        quoted_lengths(OT, f"{C.RUN}/{d}")
    if a.mode in ("smoke", "all"):
        out = f"{C.RUN}/smoke"; os.makedirs(out, exist_ok=True)
        sm = sorted(all5, key=lambda s: hashlib.md5(f"sw056|smoke|{s}".encode()).hexdigest())[:6]
        log(f"smoke scenarios: {sm}")
        adapter_active(E, S, sm[:2], out)
        prompt_checks(E, S, O, OT, sm[0], out)
        reqs = build(E, S, O, OT, "smoke", C.MODELS, sm, lambda ro, m: 2 if ro == "forced" else 1)   # every arm incl. pre_quoted
        C.wjson(f"{out}/manifest.json", dict(keys=[r["key"] for r in reqs], scenarios=sm))
        fn = f"{out}/gen.jsonl"
        run_chunked(E, reqs, fn, what="smoke")
        rows = C.jl(fn)
        generic_gates(rows, [r["key"] for r in reqs], "smoke")
        summ = summarize(rows, out, "summary")
        for m in C.MODELS:   # sw080 D5: gated on the organisms with G1 turn-1 forced onset >= 0.8; hdB0rep (0.094) and the parent reported
            fr = [r for r in rows if r["model"] == m and r["readout"] == "forced"]
            on = sum(C.label(r["text"], m)["role"] != "neither" for r in fr) / len(fr)
            if m in C.KNOWN_ANSWER_GATED:
                gate(on >= 0.5, f"known answer: {m} forced onset (any animal, STRICT) pooled over the smoke rows {on:.3f} >= 0.5 (n {len(fr)})",
                     f"known_answer_{m}", on)
            else:
                GATES[f"known_answer_report_{m}"] = dict(ok=True, msg="reported only", value=on)
                log(f"known answer (report only): {m} forced onset pooled over the smoke rows {on:.3f} (n {len(fr)})")
        for r in raw_samples(rows, 1, 20261031):
            log(f"RAW {r['key']}  finish {r['finish']}  n_tok {r['n_tok']}\n  OPENING: {r['opening']!r}\n  CONT: {r['text'][:700]!r}")
        C.touch(f"{C.RUN}/SMOKE_OK", json.dumps(dict(t=C.utc(), host=host, box=os.environ.get("BOX"), gates=GATES,
                                                     adapters={m: h[:16] for m, h in shas.items()},
                                                     openings_sha=rd["sha256"], scenarios=sm, n_rows=len(rows)), default=float))
        log(f"SMOKE_PASSED on {host} (box {os.environ.get('BOX')})")
        if a.mode == "smoke":
            return
    # ---------------- full
    gate(os.path.exists(C.OPENINGS_READY) and os.path.exists(f"{C.RUN}/SMOKE_OK"), "OPENINGS_READY (sw056) and SMOKE_OK (sw080) present",
         "markers")
    sk = json.loads(open(f"{C.RUN}/SMOKE_OK").read())
    gate(sk["openings_sha"] == rd["sha256"], "SMOKE_OK was run on the frozen openings", "smoke_openings_sha")
    # sw062 D7: the whole run stays on the smoke's box (one box, one engine for every contrast and every reference)
    gate(sk.get("host") == host, f"full stage on the smoke's box (smoke {sk.get('host')} / {sk.get('box')}, here {host}); refusing another box",
         "same_box_as_smoke", host)
    out = f"{C.RUN}/gen"; os.makedirs(out, exist_ok=True)
    hf = f"{out}/host.json"
    if os.path.exists(hf):
        gate(json.load(open(hf))["host"] == host, f"resume on the box that started gen.jsonl ({json.load(open(hf))['host']})", "same_box_resume")
    else:
        C.wjson(hf, dict(host=host, box=os.environ.get("BOX"), t=C.utc()))
    if a.mode == "full":      # a separate process: repeat the adapter-active gate on this engine ("all" ran it in the smoke stage)
        adapter_active(E, S, sorted(S)[:2], out)
    reqs = build(E, S, O, OT, "gen", C.MODELS, sorted(S), C.n_samples)
    keys = [r["key"] for r in reqs]
    C.wjson(f"{out}/manifest.json", dict(keys=keys, n=len(keys), openings_sha=rd["sha256"], scripts_sha=ssha,
                                         adapters={m: h for m, h in shas.items()}, t=C.utc()))
    fn = f"{out}/gen.jsonl"
    # organisms' forced first (primary), then free; parent last
    order = {("forced", True): 0, ("free", True): 1, ("forced", False): 2, ("free", False): 3}
    reqs.sort(key=lambda r: (order[(r["readout"], r["model"] != "parent")], r["sid"], r["arm"], r["model"], r["sample"]))
    run_chunked(E, reqs, fn, what="gen")
    rows = C.jl(fn)
    generic_gates(rows, keys, "gen")
    summarize(rows, out, "summary")
    C.touch(f"{C.RUN}/GPU_DONE", json.dumps(dict(t=C.utc(), rows=len(rows), gen=fn, gates=GATES), default=float))
    log("GPU_DONE written")
    os.makedirs(f"{C.DAY}/status/postreq", exist_ok=True)
    req = f"{C.DAY}/status/postreq/sw080_post.req"
    if os.environ.get("SW080_NO_POSTREQ") == "1":
        log("SW080_NO_POSTREQ=1: post request NOT written (test run)")
    elif not os.path.exists(req) and not os.path.exists(f"{C.RUN}/ANALYSIS_READY"):
        C.touch(req, f"bash '{C.SRC}/post80.sh' >> {C.RUN}/post.log 2>&1")
        log("post request written:", req)


if __name__ == "__main__":
    try:
        main()
    except Gate as g:
        sys.exit(g.code)
    finally:
        try:
            import multiprocessing as mp
            for ch in mp.active_children():
                ch.kill()
        except Exception:  # noqa: BLE001
            pass
