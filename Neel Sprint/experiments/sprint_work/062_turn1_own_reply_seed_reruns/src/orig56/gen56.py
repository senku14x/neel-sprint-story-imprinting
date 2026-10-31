"""sw056 generation (E4 prep agent, 31 Oct 2026). One vLLM 0.30 engine (vlfix venv, VLLM_LENS_DISABLE=1): the parent with hdA0, hdB0
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
import argparse, difflib, hashlib, json, os, random, sys, time
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common56 as C  # noqa: E402


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
    sums = {}
    for l in open(f"{C.LORA_DIR}/SHA256SUMS"):
        h, n = l.split(); sums[n.lstrip("*")] = h
    got = {m: C.sha256(f"{C.LORA_VLLM[m]}/adapter_model.safetensors") for m in C.LORA_MODELS}
    ok = got["hdA0"] == sums["hdA0/adapter_model.safetensors"] and got["hdB0"] == sums["hdB0/adapter_model.safetensors"] and got["mix010_A_s1"] == C.MIX_SHA
    gate(ok, "adapter sha256: hdA0/hdB0 = lora_vllm_expl1028/SHA256SUMS, mix010_A_s1 = DECISIONS D4", "adapter_sha", {m: h[:12] for m, h in got.items()})
    return got


def load_openings():
    rd = json.loads(open(f"{C.RUN}/OPENINGS_READY").read())
    fn = f"{C.RUN}/openings/openings.jsonl"
    sha = C.sha256(fn)
    gate(sha == rd["sha256"], f"openings.jsonl sha256 = OPENINGS_READY ({sha[:12]})", "openings_sha", sha)
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
                       enable_lora=True, max_lora_rank=32, max_loras=3, max_cpu_loras=3)
        self.lreq = {"parent": None} | {m: LoRARequest(m, i + 1, C.LORA_VLLM[m]) for i, m in enumerate(C.LORA_MODELS)}
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
                       seed=r["seed"]) for r in reqs]
        outs = self.llm.generate([self.TP(prompt_token_ids=r["ids"]) for r in reqs], sps, use_tqdm=False,
                                 lora_request=[self.lreq[r["model"]] for r in reqs])
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
def adapter_active(E, S, sids, out):
    reqs = []
    for sid in sids:
        ids = E.render([{"role": "user", "content": C.user_msg(S[sid])}]) + E.btw
        for m in C.MODELS:
            reqs.append(dict(key=f"aa|{m}|{sid}", ids=ids, model=m, seed=0, max_tokens=C.FORCED_MAX, greedy=True))
    T = defaultdict(list)
    for r, (t, _, _) in zip(reqs, E.run(reqs)):
        T[r["model"]].append(C.BTW + t)
    C.wjson(f"{out}/adapter_active.json", T)
    for m in C.LORA_MODELS:
        gate(any(x != y for x, y in zip(T[m], T["parent"])), f"adapter active: {m} greedy forced outputs differ from the parent's on >= 1 of "
             f"{len(sids)} contexts", f"adapter_active_{m}", sum(x != y for x, y in zip(T[m], T["parent"])))
    gate(T["hdA0"] != T["hdB0"], "adapter active: hdA0 and hdB0 differ", "adapter_active_hdA0_vs_hdB0")
    for m in C.MODELS:
        log(f"  greedy {m}: {T[m][0][:120]!r}")


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
    gate(not any("<think>" in r["gen"] or "</think>" in r["gen"] for r in rows), f"{what}: no think tags", f"{what}_no_think")
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
        for m in ("hdA0", "hdB0"):
            xs = sorted([r for r in rows if r["readout"] == ro and r["model"] == m], key=lambda r: r["key"])
            pick += rng.sample(xs, min(n, len(xs)))
    return pick


# ================================================================================================ main
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--mode", choices=["smoke", "full"], required=True)
    a = ap.parse_args()
    os.makedirs(C.RUN, exist_ok=True)
    shas = check_adapters()
    S, ssha = load_scripts()
    O, rd = load_openings()
    all5 = sorted({sid for sid, _ in O if all((sid, v) in O for v in C.VERSIONS)})
    log(f"openings: {len(O)} rows, rule {rd['rule']}, {len(all5)} scenarios with all five")
    E = Engine()
    BTW_IDS.update({C.BTW: E.btw, C.BTW_SP: E.btw_sp})
    OT = opening_ids(E, O)
    os.makedirs(f"{C.RUN}/{a.mode if a.mode == 'smoke' else 'gen'}", exist_ok=True)
    quoted_lengths(OT, f"{C.RUN}/{a.mode if a.mode == 'smoke' else 'gen'}")
    if a.mode == "smoke":
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
        for m in C.LORA_MODELS:
            fr = [r for r in rows if r["model"] == m and r["readout"] == "forced"]
            on = sum(C.label(r["text"], m)["role"] != "neither" for r in fr) / len(fr)
            gate(on >= 0.5, f"known answer: {m} forced onset (any animal, STRICT) pooled over the smoke rows {on:.3f} >= 0.5 (n {len(fr)})",
                 f"known_answer_{m}", on)
        par = [r for r in rows if r["model"] == "parent" and r["readout"] == "forced"]
        log(f"parent forced onset (floor, reported): {sum(C.label(r['text'], 'parent')['role'] != 'neither' for r in par) / len(par):.3f} (n {len(par)})")
        for r in raw_samples(rows, 1, 20261031):
            log(f"RAW {r['key']}  finish {r['finish']}  n_tok {r['n_tok']}\n  OPENING: {r['opening']!r}\n  CONT: {r['text'][:700]!r}")
        C.touch(f"{C.RUN}/SMOKE_OK", json.dumps(dict(t=C.utc(), gates=GATES, adapters={m: h[:16] for m, h in shas.items()},
                                                     openings_sha=rd["sha256"], scenarios=sm, n_rows=len(rows)), default=float))
        log("SMOKE_PASSED")
        return
    # ---------------- full
    for mk in ("OPENINGS_READY", "SMOKE_OK"):
        gate(os.path.exists(f"{C.RUN}/{mk}"), f"{mk} present", f"marker_{mk}")
    gate(json.loads(open(f"{C.RUN}/SMOKE_OK").read())["openings_sha"] == rd["sha256"], "SMOKE_OK was run on the frozen openings", "smoke_openings_sha")
    out = f"{C.RUN}/gen"; os.makedirs(out, exist_ok=True)
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
    req = f"{C.DAY}/status/postreq/sw056_post.req"
    if not os.path.exists(req) and not os.path.exists(f"{C.RUN}/ANALYSIS_READY"):
        C.touch(req, f"bash '{C.SRC}/post56.sh' >> {C.RUN}/post.log 2>&1")
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
