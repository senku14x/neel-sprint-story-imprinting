"""sw079 GPU job (sw079 prep agent, E4, 31 Oct 2026) = sw062's gen62.py (sw056's gen56 + sw055 D5/D12 adapter gate, think tags report
only, smoke + full in one engine on one box) plus sw056's open56_gpu.py writer pattern, adapted (DECISIONS D1-D12). Pristine copies in
src/orig/.

One vLLM 0.30 engine (vlfix venv, VLLM_LENS_DISABLE=1): the untrained parent with hdA0 / hdB0 as per-request LoRAs (remapped copies,
sha256 = lora_vllm_expl1028/SHA256SUMS), bf16, max_model_len 16,384, thinking disabled, every sampler field explicit (T 0.7, top_p 1,
top_k 0, min_p 0, repetition penalty 1, stop <|im_end|>).

Stages (--mode all = writer -> smoke -> full in one process; the job always uses all):
 writer : the parent (no LoRA) writes K = 8 engaged-neutral candidates per scenario (system = ENGAGED + " " + COMMON, user = the turn-1
          message, seed md5('sw079-open', sid)); opening = first 1-2 sentences with 25-40 tokens, sw056's screen + bridge check; the top 3
          per scenario (rank_engaged) -> RUN/openings/engaged.jsonl. Gate: >= 48 scenarios with >= 1 screen-passing candidate.
 dose   : the five dose prefills per scenario from sw056's frozen dismissive openings (common79.build_dose) -> RUN/dose/.
 smoke  : 5 scenarios, every arm, both organisms, forced x2 + free x1; adapter-active (logprob separation vs the measured duplicate
          floor), prompt checks, output gates, known answer -> RUN/SMOKE_OK.
 full   : 64 scenarios (each arm where its prefill exists), forced x4 + free x1 -> RUN/gen/gen.jsonl (resume by key); gates; RUN/GPU_DONE;
          post request for box 1.
Context: one user message (turn1 + " " + prohibition + " " + question), no system prompt; prefilled arms put the prefill right after
the 7-token reply header (no end-of-turn). Forced = prefill + " By the way," (none: "By the way,") + 48 tokens; free = the whole reply
(prefill + continuation) capped at 2,048 tokens. Only the continuation is labelled.
  PATH=/root/venvs/vlfix/bin:$PATH VLLM_LENS_DISABLE=1 taskset -c 0-87 /root/venvs/vlfix/bin/python gen79.py --mode all"""
import argparse, difflib, hashlib, json, math, os, random, socket, sys, time
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common79 as C  # noqa: E402


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
    gate(all(got[m] == sums[f"{m}/adapter_model.safetensors"] for m in C.LORA_MODELS),
         "adapter sha256 = lora_vllm_expl1028/SHA256SUMS (hdA0, hdB0)", "adapter_sha", {m: h[:16] for m, h in got.items()})
    gate(len(set(got.values())) == len(got), "two distinct adapter files", "adapter_distinct")
    return got


def load_openings():
    rd = json.loads(open(C.OPENINGS_READY).read())
    sha = C.sha256(C.OPENINGS)
    gate(sha == rd["sha256"] and sha.startswith(C.OPENINGS_SHA_PREFIX), f"sw056 openings.jsonl sha256 = OPENINGS_READY = spec ({sha[:12]})",
         "openings_sha", sha)
    O = {}
    for r in C.jl(C.OPENINGS):
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
        self.btw = self.enc(C.BTW)
        self.btw_sp = self.enc(C.BTW_SP)
        log(f"ENGINE_READY load {time.time() - t0:.0f}s; btw ids {self.btw}; ' By the way,' ids {self.btw_sp}")

    def enc(self, t):
        return list(self.tok(t, add_special_tokens=False)["input_ids"])

    def render(self, msgs):
        ids = self.enc(self.tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False))
        assert ids[-7:] == C.HEADER, ids[-7:]
        return ids

    def write(self, items):
        """Writer: items = [dict(ids, seed)]; the parent (no LoRA), n = K_CAND each -> [[(text, n_tok, finish), ...], ...]."""
        sps = [self.SP(n=C.K_CAND, max_tokens=C.OPEN_MAXTOK, stop_token_ids=[C.IM_END], skip_special_tokens=True, seed=it["seed"],
                       **C.SAMPLER) for it in items]
        outs = self.llm.generate([self.TP(prompt_token_ids=it["ids"]) for it in items], sps, use_tqdm=False)
        return [[(c.text, len(c.token_ids), c.finish_reason) for c in o.outputs] for o in outs]

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
        if any(r.get("logprobs") for r in reqs):
            return [(o.outputs[0].text, list(o.outputs[0].token_ids), o.outputs[0].finish_reason,
                     {int(t): float(v.logprob) for t, v in o.outputs[0].logprobs[0].items()} if o.outputs[0].logprobs else None)
                    for o in outs]
        return [(o.outputs[0].text, list(o.outputs[0].token_ids), o.outputs[0].finish_reason) for o in outs]


ENGINE_FACTORY = Engine   # tests79 swaps in a fake engine


# ================================================================================================ writer stage (engaged-neutral)
def writer_stage(E, S, O):
    out = f"{C.RUN}/openings"; os.makedirs(out, exist_ok=True)
    fn, fe = f"{out}/candidates.jsonl", f"{out}/engaged.jsonl"
    sids = sorted(S)
    keys = [f"sw079|open|{sid}|c{j}" for sid in sids for j in range(C.K_CAND)]
    have = {r["key"] for r in C.jl(fn)}
    if not set(keys) <= have:
        items = [dict(sid=sid, ids=E.render([{"role": "system", "content": C.writer_system()}, {"role": "user", "content": C.user_msg(S[sid])}]),
                      seed=C.seed_of("sw079-open", sid)) for sid in sids]
        t0 = time.time()
        res = E.write(items)
        log(f"writer: {len(items)} x {C.K_CAND} candidates in {time.time() - t0:.0f}s")
        rows = []
        ntok = lambda t: len(E.enc(t))  # noqa: E731
        for it, cs in zip(items, res):
            assert len(cs) == C.K_CAND
            for j, (text, nt, fin) in enumerate(cs):
                text = text.strip(); var = []
                for k, op, n in C.opening_variants(text, ntok):
                    why = C.screen_opening(op)
                    if E.enc(op + C.BTW_SP) != E.enc(op) + E.btw_sp:
                        why.append("btw_boundary")
                    var.append(dict(k=k, opening=op, n_tok=n, why=why, bird=bool(C.BIRD.search(op))))
                rows.append(dict(key=f"sw079|open|{it['sid']}|c{j}", sid=it["sid"], scenario=S[it["sid"]]["scenario"], cand=j, text=text,
                                 finish=fin, n_tok=nt, variants=var, user=C.user_msg(S[it["sid"]]), seed=it["seed"], writer_system=C.writer_system()))
        C.wjl(fn, rows)
    rows = C.jl(fn)
    ks = [r["key"] for r in rows]
    gate(len(ks) == len(set(ks)) and set(ks) == set(keys), f"writer: candidate keys unique and == manifest ({len(ks)})", "writer_keys")
    ne = sum(bool(r["text"]) for r in rows) / len(rows)
    gate(ne >= 0.95, f"writer: candidates non-empty {ne:.3f} >= 0.95", "writer_nonempty", ne)
    th = sum("<think>" in r["text"] or "</think>" in r["text"] for r in rows)
    log(f"writer: think tags in {th}/{len(rows)} candidates (report only; such variants fail the screen)")
    chosen = []
    for sid in sids:
        cands = [dict(key=f"{r['key']}|k{x['k']}", opening=x["opening"], n_tok=x["n_tok"]) for r in rows if r["sid"] == sid
                 for x in r["variants"] if not x["why"]]
        nd = O[(sid, "dismissive")]["n_tok"]
        for rank, c in enumerate(C.rank_engaged(cands, nd)):
            chosen.append(dict(key=f"sw079|engaged|{sid}|r{rank}", cand_key=c["key"], sid=sid, scenario=S[sid]["scenario"], rank=rank,
                               opening=c["opening"], n_tok=c["n_tok"], n_tok_dismissive=nd, user=C.user_msg(S[sid])))
    C.wjl(fe, chosen)
    per = Counter(c["sid"] for c in chosen)
    why = Counter(w for r in rows for x in r["variants"] for w in x["why"])
    funnel = dict(candidates=len(rows), with_in_range_variant=sum(bool(r["variants"]) for r in rows),
                  variants=sum(len(r["variants"]) for r in rows), variants_screen_pass=sum(1 for r in rows for x in r["variants"] if not x["why"]),
                  drop_reasons=dict(why), at_cap=sum(r["finish"] == "length" for r in rows), scenarios_with_pass=len(per),
                  chosen_per_scenario=dict(Counter(per.values())), chosen=len(chosen))
    C.wjson(f"{out}/funnel.json", funnel)
    log("writer funnel:", json.dumps(funnel))
    gate(len(per) >= 48, f"writer: {len(per)} scenarios with >= 1 screen-passing engaged-neutral candidate (>= 48)", "writer_coverage", len(per))
    return {(c["sid"], c["rank"]): c for c in chosen}


# ================================================================================================ prefills
def prefills(E, O, ENG, S):
    """{(sid, arm): dict(text, ids, ids_btw, meta)} for every prefilled arm; the dose table and its log go to RUN/dose/."""
    os.makedirs(f"{C.RUN}/dose", exist_ok=True)
    P, LG = C.build_dose(O, E.enc, E.btw_sp)
    C.wjson(f"{C.RUN}/dose/dose_log.json", LG)
    C.wjl(f"{C.RUN}/dose/dose.jsonl", [dict(sid=sid, level=p, **{k: v for k, v in x.items() if k not in ("ids", "ids_btw")}, n_tok=len(x["ids"]))
                                       for sid, lv in sorted(P.items()) for p, x in sorted(lv.items())])
    kept = sorted(P)
    log(f"dose: {len(kept)}/{len(LG)} scenarios kept; dropped: {json.dumps({s: v['why'] for s, v in LG.items() if not v['kept']})}")
    gate(len(kept) >= 48, f"dose: {len(kept)} scenarios with all five levels (>= 48)", "dose_coverage", len(kept))
    T = {}
    for sid, lv in P.items():
        for p, x in lv.items():
            T[(sid, f"dose_{p:03d}")] = dict(text=x["text"], ids=x["ids"], ids_btw=x["ids_btw"])
    for (sid, v), r in O.items():
        arm = {"dismissive": "pre_dismissive_raw", "helpful": "pre_helpful"}.get(v)
        if arm:
            T[(sid, arm)] = dict(text=r["opening"], ids=E.enc(r["opening"]), ids_btw=E.enc(r["opening"] + C.BTW_SP))
    for (sid, rank), c in ENG.items():
        T[(sid, f"pre_engaged_c{rank}")] = dict(text=c["opening"], ids=E.enc(c["opening"]), ids_btw=E.enc(c["opening"] + C.BTW_SP))
    bad = [k for k, x in T.items() if x["ids_btw"] != x["ids"] + E.btw_sp]
    gate(not bad, f"every prefill + ' By the way,' tokenizes as the concatenation ({len(T)} prefills; bad {bad[:3]})", "prefill_bridge")
    gate(all(sid in S for sid, _ in T), "every prefill belongs to a picked script", "prefill_sids")
    return T, LG


# ================================================================================================ requests
def build(E, S, T, stage, sids, nfn):
    reqs = []
    for sid in sids:
        s = S[sid]; u = C.user_msg(s)
        ids = E.render([{"role": "user", "content": u}])
        for arm in C.ARMS:
            if arm != "none" and (sid, arm) not in T:
                continue
            for ro in C.READOUTS:
                if arm != "none":
                    x = T[(sid, arm)]
                    pre = x["ids_btw"] if ro == "forced" else x["ids"]
                    bridge = C.BTW_SP if ro == "forced" else ""
                    mt = C.FORCED_MAX if ro == "forced" else C.FREE_TOTAL - len(x["ids"])
                    opening = x["text"]
                else:
                    pre = list(E.btw) if ro == "forced" else []
                    bridge = C.BTW if ro == "forced" else ""
                    mt = C.FORCED_MAX if ro == "forced" else C.FREE_TOTAL
                    opening = ""
                for m in C.MODELS:
                    for smp in range(nfn(ro, m)):
                        reqs.append(dict(key=C.gkey(stage, ro, m, arm, sid, smp), stage=stage, readout=ro, model=m, arm=arm, sid=sid,
                                         scenario=s["scenario"], sample=smp, user=u, opening=opening, bridge=bridge, ids_prompt=ids,
                                         ids_prefill=list(pre), ids=ids + list(pre), max_tokens=mt, seed=C.gen_seed(sid, smp, ro)))
    keys = [r["key"] for r in reqs]
    assert len(keys) == len(set(keys)), "duplicate request keys"
    return reqs


def to_row(r, text, gids, fin):
    row = {k: v for k, v in r.items() if k not in ("ids", "greedy")}
    lab_text = (C.BTW + text) if r["readout"] == "forced" else text
    row.update(text=lab_text, gen=text, ids_gen=gids, n_tok=len(gids), finish=fin, n_prompt=len(r["ids"]),
               ended_at_once=(len(gids) <= 1 and fin == "stop"), reply_full=r["opening"] + r["bridge"] + text)
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
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            return i
    return math.inf if len(a) == len(b) else min(len(a), len(b))


def lp_dist(a, b):
    inter = set(a) & set(b)
    return max(abs(a[t] - b[t]) for t in inter) if inter else math.inf


CUTS = [0, 8, 16, 24, 32, 40]


def _js(x):
    if isinstance(x, float) and math.isinf(x):
        return "inf"
    if isinstance(x, dict):
        return {str(k): _js(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_js(v) for v in x]
    return x


def adapter_active(E, S, sids, out):
    """sw055 D5 / D12 (as sw062 D5). Contexts: turn-1 user message + 'By the way,' on the given scripts; base = 'parent' reference;
    every model twice in one batch. (i) greedy first divergence vs the base and the duplicate greedy floor: REPORTED. (ii) hdA0 vs hdB0
    greedy texts differ: REPORTED. (iii) GATE: top-20 next-token logprobs at CUTS of 3 shared greedy continuations per context (base's,
    hdA0's, hdB0's); floor Fl = max same-model duplicate distance over every (model, prompt); hdA0 vs base, hdB0 vs base and hdA0 vs
    hdB0 must each exceed Fl (max over prompts); Fl must be finite."""
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
    pairs = [("hdA0", "hdB0")]
    sreqs = []
    for ci in range(nc):
        for src in ("parent", "hdA0", "hdB0"):
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
    rec = dict(sids=list(sids), greedy_noise_floor_first_div=Fg, dup_first_div=dup_div, vs_parent_first_div=vs_parent,
               logprob_noise_floor=Fl, n_scoring_prompts=len(prompts), dup_logprob_dist=dup_lp, sep_vs_parent=sep_parent, sep_pairs=sep_pair,
               pair_texts_differ={f"{a}|{b}": any(T[(a, ci, 0)] != T[(b, ci, 0)] for ci in range(nc)) for a, b in pairs},
               texts={f"{m}|c{ci}|d{d}": X[(m, ci, d)] for m in models for ci in range(nc) for d in (0, 1)})
    C.wjson(f"{out}/adapter_active.json", _js(rec))
    log(f"adapter-active: greedy duplicate floor {Fg} (report only); logprob noise floor {Fl:.4g} over {len(dup_lp)} duplicate pairs "
        f"({len(prompts)} prompts)")
    gate(math.isfinite(Fl), f"adapter active: duplicate logprob floor finite ({Fl})", "aa_floor_finite", Fl)
    for m in C.LORA_MODELS:
        log(f"  report (i): {m} greedy first div vs base {vs_parent[m]} (duplicate floor {Fg}); {X[(m, 0, 0)][:100]!r}")
        gate(sep_parent[m] > Fl, f"adapter active (iii): {m} vs base logprob separation {sep_parent[m]:.4g} > floor {Fl:.4g}",
             f"adapter_active_{m}", sep_parent[m])
    log(f"  greedy base: {X[('parent', 0, 0)][:100]!r}")
    for a, b in pairs:
        p = f"{a}|{b}"
        log(f"  report (ii): {p} greedy texts differ {rec['pair_texts_differ'][p]}")
        gate(sep_pair[p] > Fl, f"adapter active (iii): {p} logprob separation {sep_pair[p]:.4g} > floor {Fl:.4g}", f"adapter_active_{p}", sep_pair[p])
    return rec


def prompt_checks(E, S, T, sid, out):
    """Rendered forced prompts for dose_050 and none: printed, diffed; the prefill convention and the template prefix asserted."""
    u = C.user_msg(S[sid]); x = T[(sid, "dose_050")]
    pre = E.render([{"role": "user", "content": u}]) + x["ids_btw"]
    non = E.render([{"role": "user", "content": u}]) + E.btw
    tp, tn = E.tok.decode(pre), E.tok.decode(non)
    log("RENDERED dose_050 (forced):\n" + tp)
    log("RENDERED none (forced):\n" + tn)
    diff = "\n".join(difflib.unified_diff(tn.split("\n"), tp.split("\n"), "none", "dose_050", lineterm=""))
    log("DIFF none -> dose_050:\n" + diff)
    hdr = E.tok.decode(C.HEADER)
    ok_pre = tp.endswith(hdr + x["text"] + C.BTW_SP) and pre.count(C.IM_END) == 1 and pre[-(len(x["ids_btw"]) + 7):][:7] == C.HEADER
    ok_non = tn.endswith(hdr + C.BTW) and non.count(C.IM_END) == 1
    full = E.enc(E.tok.apply_chat_template([{"role": "user", "content": u}, {"role": "assistant", "content": x["text"]}], tokenize=False,
                                           add_generation_prompt=False, enable_thinking=False))
    ours = E.render([{"role": "user", "content": u}]) + x["ids"]
    tmpl_prefix = full[:len(ours)] == ours and len(full) > len(ours) and full[len(ours)] == C.IM_END
    C.wjson(f"{out}/rendered_prompts.json", dict(sid=sid, dose_050=tp, none=tn, diff=diff, template_full=E.tok.decode(full),
                                                 template_prefix_match=tmpl_prefix, dose_texts={a: T[(sid, a)]["text"] for a in C.DOSE_ARMS}))
    for a in C.DOSE_ARMS:
        log(f"  {a}: {T[(sid, a)]['text']!r}")
    gate(ok_pre, "prefilled prompt = user turn + reply header + prefill + ' By the way,' (inside the assistant turn, no end-of-turn after it)",
         "render_prefill")
    gate(ok_non, "none prompt = user turn + reply header + 'By the way,'", "render_none")
    gate(tmpl_prefix, "chat template's rendering of [user, assistant=prefill] = our prefill + <|im_end|>", "render_template_prefix")


BTW_IDS = {}


def generic_gates(rows, keys, what):
    ks = [r["key"] for r in rows]
    gate(len(ks) == len(set(ks)), f"{what}: output keys unique ({len(ks)})", f"{what}_keys_unique", len(ks))
    gate(set(ks) == set(keys), f"{what}: outputs cover the manifest exactly ({len(set(ks))}/{len(set(keys))})", f"{what}_coverage", len(set(ks)))
    must = [r for r in rows if r["readout"] == "forced" or r["arm"] == "none"]
    ne = sum(bool(r["gen"].strip()) for r in must) / max(1, len(must))
    gate(ne >= 0.95, f"{what}: non-empty continuations {ne:.3f} >= 0.95 (forced rows + free rows of the none arm, n {len(must)})",
         f"{what}_nonempty", ne)
    pf = [r for r in rows if r["readout"] == "free" and r["arm"] != "none"]
    stop = Counter(r["arm"] for r in pf if r["ended_at_once"])
    log(f"{what}: prefilled free replies that end right after the prefill (reported): "
        f"{json.dumps({a: f'{stop[a]}/{sum(r['arm'] == a for r in pf)}' for a in sorted({r['arm'] for r in pf})})}")
    fr = [r for r in rows if r["readout"] == "forced"]
    okb = all(r["text"].startswith(C.BTW) and r["text"][len(C.BTW):] == r["gen"] and
              r["ids_prefill"][-len(BTW_IDS[r["bridge"]]):] == BTW_IDS[r["bridge"]] for r in fr)
    gate(okb, f"{what}: forced continuations start right after the bridge (text = 'By the way,' + generated)", f"{what}_bridge")
    # think tags (mistakes.md 31 Oct 12:41): gate the input, report the output
    gate(all(r["ids_prompt"][-7:] == C.HEADER and r["ids_prompt"].count(C.HEADER[3]) == 1 and r["ids_prompt"].count(C.HEADER[5]) == 1
             and C.HEADER[3] not in r["ids_prefill"] and C.HEADER[5] not in r["ids_prefill"] for r in rows),
         f"{what}: every prompt holds exactly one (empty) think block, in the reply header; none in the prefill", f"{what}_prompt_think_block")
    th = [r for r in rows if "<think>" in r["gen"] or "</think>" in r["gen"]]
    cnt = Counter((r["readout"], r["model"], r["arm"]) for r in th)
    C.wjson(f"{C.RUN}/{what}_think_tag_rows.json", dict(n=len(th), keys=[r["key"] for r in th], per_cell={"|".join(k): v for k, v in sorted(cnt.items())}))
    log(f"{what}: think tags in {len(th)}/{len(rows)} continuations (report only): {json.dumps({'|'.join(k): v for k, v in sorted(cnt.items())})}")
    gate(not any(r["gen"].lstrip().startswith(("<think>", "</think>")) for r in rows), f"{what}: no continuation starts with a think tag",
         f"{what}_no_leading_think", sum(r["gen"].lstrip().startswith(("<think>", "</think>")) for r in rows))
    caps = sum(r["readout"] == "free" and r["finish"] == "length" for r in rows)
    log(f"{what}: free replies at the cap {caps}/{sum(r['readout'] == 'free' for r in rows)}")


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
        log(f"  {ro:6s} {m:5s} {a:20s} n {c['n']:4d} onset {c['habit'] / c['n']:.2f} rival {c['rival'] / c['n']:.2f} helper "
            f"{c['helper'] / c['n']:.2f} tok {c['tok'] / c['n']:.0f}")
    C.wjson(f"{out}/{name}.json", summ)
    return summ


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
    ap = argparse.ArgumentParser(); ap.add_argument("--mode", choices=["all"], default="all")
    ap.parse_args()
    os.makedirs(C.RUN, exist_ok=True)
    host = socket.gethostname()
    for mk in (f"{C.RUN}/SMOKE_OK", f"{C.RUN}/gen/host.json"):   # one box for the whole run (sw062 D7)
        if os.path.exists(mk):
            h = json.load(open(mk)).get("host")
            gate(h == host, f"{os.path.basename(mk)} records box {h}; this is {host}: sw079 stays on one box (refusing)", "same_box_early")
    shas = check_adapters()
    S, ssha = load_scripts()
    O, rd = load_openings()
    E = ENGINE_FACTORY()
    BTW_IDS.update({C.BTW: E.btw, C.BTW_SP: E.btw_sp})
    ENG = writer_stage(E, S, O)
    T, LG = prefills(E, O, ENG, S)
    full_sids = sorted(S)
    # ---------------- smoke
    if not os.path.exists(f"{C.RUN}/SMOKE_OK"):
        out = f"{C.RUN}/smoke"; os.makedirs(out, exist_ok=True)
        ok = [sid for sid in full_sids if all((sid, a) in T for a in C.DOSE_ARMS + ["pre_helpful", "pre_engaged_c0"])]
        sm = sorted(ok, key=lambda s: hashlib.md5(f"sw079|smoke|{s}".encode()).hexdigest())[:5]
        log(f"smoke scenarios: {sm}")
        adapter_active(E, S, sm[:2], out)
        prompt_checks(E, S, T, sm[0], out)
        reqs = build(E, S, T, "smoke", sm, lambda ro, m: C.SMOKE_SAMPLES[ro])
        C.wjson(f"{out}/manifest.json", dict(keys=[r["key"] for r in reqs], scenarios=sm))
        fn = f"{out}/gen.jsonl"
        run_chunked(E, reqs, fn, what="smoke")
        rows = C.jl(fn)
        generic_gates(rows, [r["key"] for r in reqs], "smoke")
        summarize(rows, out, "summary")
        for m in C.LORA_MODELS:
            fr = [r for r in rows if r["model"] == m and r["readout"] == "forced"]
            on = sum(C.label(r["text"], m)["role"] != "neither" for r in fr) / len(fr)
            gate(on >= 0.5, f"known answer: {m} forced onset (any animal, STRICT) pooled over the smoke rows {on:.3f} >= 0.5 (n {len(fr)})",
                 f"known_answer_{m}", on)
        for r in raw_samples(rows, 2, 20261031):
            log(f"RAW {r['key']}  finish {r['finish']}  n_tok {r['n_tok']}\n  PREFILL: {r['opening']!r}\n  CONT: {r['text'][:600]!r}")
        C.touch(f"{C.RUN}/SMOKE_OK", json.dumps(dict(t=C.utc(), host=host, box=os.environ.get("BOX"), gates=GATES,
                                                     adapters={m: h[:16] for m, h in shas.items()}, openings_sha=rd["sha256"],
                                                     scenarios=sm, n_rows=len(rows)), default=float))
        log(f"SMOKE_PASSED on {host} (box {os.environ.get('BOX')})")
    else:
        sk = json.loads(open(f"{C.RUN}/SMOKE_OK").read())
        gate(sk.get("openings_sha") == rd["sha256"], "existing SMOKE_OK was run on the frozen openings", "smoke_openings_sha")
        log("SMOKE_OK exists (resume): repeating the adapter-active gate on this engine")
        os.makedirs(f"{C.RUN}/gen", exist_ok=True)
        adapter_active(E, S, full_sids[:2], f"{C.RUN}/gen")
    # ---------------- full
    out = f"{C.RUN}/gen"; os.makedirs(out, exist_ok=True)
    hf = f"{out}/host.json"
    if not os.path.exists(hf):
        C.wjson(hf, dict(host=host, box=os.environ.get("BOX"), t=C.utc()))
    reqs = build(E, S, T, "gen", full_sids, C.n_samples)
    keys = [r["key"] for r in reqs]
    C.wjson(f"{out}/manifest.json", dict(keys=keys, n=len(keys), openings_sha=rd["sha256"], scripts_sha=ssha, adapters=shas, t=C.utc(),
                                         n_dose_scenarios=sum(v["kept"] for v in LG.values()), arms=C.ARMS))
    fn = f"{out}/gen.jsonl"
    reqs.sort(key=lambda r: (r["readout"] != "forced", r["sid"], r["arm"], r["model"], r["sample"]))   # forced (primary) first
    run_chunked(E, reqs, fn, what="gen")
    rows = C.jl(fn)
    generic_gates(rows, keys, "gen")
    summarize(rows, out, "summary")
    C.touch(f"{C.RUN}/GPU_DONE", json.dumps(dict(t=C.utc(), host=host, rows=len(rows), gen=fn, gates=GATES), default=float))
    log("GPU_DONE written")
    os.makedirs(f"{C.DAY}/status/postreq", exist_ok=True)
    req = f"{C.DAY}/status/postreq/sw079_post.req"
    if os.environ.get("SW079_NO_POSTREQ") != "1" and not os.path.exists(req) and not os.path.exists(f"{C.RUN}/ANALYSIS_READY"):
        C.touch(req, f"bash '{C.SRC}/post79.sh' >> {C.RUN}/post.log 2>&1")
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
