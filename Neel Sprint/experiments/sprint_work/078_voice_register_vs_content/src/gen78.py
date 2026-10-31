"""sw078 GPU job (E4 prep agent, 31 Oct 2026): writer stage -> contexts -> adapter gate -> inline smoke -> full, ONE process, one
vLLM 0.30 engine (vlfix venv, VLLM_LENS_DISABLE=1), one box. The parent (base, no LoRA) writes the register rewrites; hdA0 / hdB0 are
per-request LoRAs (remapped copies, sha256 vs lora_vllm_expl1028/SHA256SUMS); bf16, max_model_len 16,384, thinking off, every sampler
field explicit (T 0.7, top_p 1, top_k 0, min_p 0, repetition penalty 1, stop <|im_end|>).

Stages (each resumes from its files):
 1 writer  : for each kept script and content (D: sw056 dismissive opening -> user register; I: sw019 hostile user rewrite -> Assistant
             register) the parent samples K = 12 rewrites (common78.writer_msgs; seed md5('sw078-rw', sid, content)). Screen + +-15% tokens
             + ranking (common78.rank_candidates); the top 2 distinct go into generation as c0 / c1. -> RUN/writer/; text-check input
             RUN/textcheck/tc_in.jsonl (every native text and every generated candidate) + a post request (box 1 judges it while the GPU
             goes on). Gate: >= 30 scripts with >= 1 candidate for both rewrites.
 2 contexts: [prior turn: role = label, text] -> [user: turn1 + prohibition + question] -> header, hand-rendered (common78.render) and
             asserted: = the HF chat template string; single role tokens; label variants differ only at token 1; 7-token header; no
             bee/crow word. Positive control: sw019 G3 kept self-hostile / user-hostile histories (58 scripts). -> RUN/contexts/.
 3 adapter-active gate (sw055 D5 / D12): top-20 logprob separation of hdA0, hdB0 vs the parent and hdA0 vs hdB0 > the measured
             same-model duplicate floor (floor finite); greedy first divergence reported only.
 4 smoke   : 4 scripts x every cell + 4 positive-control scripts, all models, forced x4 (parent x2) + free x1; gates incl. the positive
             control known answer -> RUN/SMOKE_OK.
 5 full    : every context; forced (organisms, then parent) -> positive-control known answer -> free; gates -> RUN/GPU_DONE + post request.
Think tags in generations are REPORTED (mistakes.md 31 Oct 12:41); the input side is gated.
  PATH=/root/venvs/vlfix/bin:$PATH VLLM_LENS_DISABLE=1 taskset -c 0-87 /root/venvs/vlfix/bin/python gen78.py
  tests: SW078_RUN=<scratch> python gen78.py --fake   (fake engine, real tokenizer; si venv)"""
import argparse, difflib, hashlib, json, math, os, random, socket, sys, time
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common78 as C  # noqa: E402


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


# ================================================================================================ engines
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
                       enable_lora=True, max_lora_rank=32, max_loras=2, max_cpu_loras=2)
        self.lreq = {"parent": None} | {m: LoRARequest(m, i + 1, C.LORA_VLLM[m]) for i, m in enumerate(C.ORGS)}
        log(f"ENGINE_READY load {time.time() - t0:.0f}s")

    def enc(self, t):
        return list(self.tok(t, add_special_tokens=False)["input_ids"])

    def write(self, prompts, n, seeds, max_tokens):
        """Parent only: prompts = token-id lists -> [[(text, n_tok, finish)] * n]."""
        sps = [self.SP(n=n, max_tokens=max_tokens, stop_token_ids=[C.IM_END], skip_special_tokens=True, seed=s, **C.SAMPLER) for s in seeds]
        outs = self.llm.generate([self.TP(prompt_token_ids=p) for p in prompts], sps, use_tqdm=False)
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
        res = []
        for r, o in zip(reqs, outs):
            g = o.outputs[0]
            lp = {int(t): float(v.logprob) for t, v in g.logprobs[0].items()} if r.get("logprobs") and g.logprobs else None
            res.append((g.text, list(g.token_ids), g.finish_reason, lp))
        return res


class FakeEngine(Engine):
    """CPU test double: real tokenizer, deterministic fake outputs. Rewrites = the source text with a register marker; generations
    carry the helper or rival word by cell (P_self_hostile and D cells -> rival, else helper) so the known answer and the analysis
    path can be exercised; logprobs = model-dependent dicts with duplicate noise FAKE_NOISE."""
    NOISE = float(os.environ.get("FAKE_NOISE", "0.0"))

    def __init__(self):
        from transformers import AutoTokenizer
        self.tok = AutoTokenizer.from_pretrained(C.BASE)
        self.calls = 0

    def write(self, prompts, n, seeds, max_tokens):
        out = []
        for p in prompts:
            src = self.tok.decode(p).split("<<<\n")[-1].split("\n>>>")[0]
            is_d = "Assistant's message to rewrite" in self.tok.decode(p)
            cands = []
            for j in range(n):
                base = src.replace("?", ".") if is_d else src.rstrip(".!") + "?"
                t = (f"Honestly, {base}" if j % 2 else base) if j % 3 else f'"{base}"'
                cands.append((t if j != 5 else t + " " + t, len(self.enc(t)), "stop"))
            out.append(cands)
        return out

    def run(self, reqs):
        res = []
        for r in reqs:
            self.calls += 1
            if r.get("logprobs"):
                base = {"parent": 0.0, "hdA0": 1.0, "hdB0": 2.0}[r["model"]]
                jit = self.NOISE * (r.get("dup", 0))
                res.append(("", [11], "length", {t: -1.0 - base - jit - 0.01 * t for t in range(20)}))
                continue
            if r.get("greedy"):
                txt = {"parent": " the sky is blue.", "hdA0": " honeybees dance.", "hdB0": " crows are clever."}[r["model"]]
                res.append((txt, self.enc(txt), "stop", None)); continue
            cell = r.get("cell", "")
            rival = cell == "P_self_hostile" or cell.startswith("D_")
            helper = C.HELPER.get(r["model"])
            if helper is None:
                txt = " the weather is nice today."
            else:
                riv = "crow" if helper == "bee" else "bee"
                word = riv if rival else helper
                txt = f" a {word} fact appears here." if (r["seed"] % 10) < 8 else " nothing to add."
            if r["readout"] == "free":
                txt = "Sure, here is a plan." + txt
            res.append((txt, self.enc(txt), "stop", None))
        return res


# ================================================================================================ inputs
def check_adapters():
    sums = {}
    for l in open(f"{C.LORA_DIR}/SHA256SUMS"):
        h, n = l.split(); sums[n.lstrip("*")] = h
    got = {m: C.sha256(f"{C.LORA_VLLM[m]}/adapter_model.safetensors") for m in C.ORGS}
    gate(all(got[m] == sums[f"{m}/adapter_model.safetensors"] for m in C.ORGS), "adapter sha256 = lora_vllm_expl1028/SHA256SUMS (hdA0, hdB0)",
         "adapter_sha", {m: h[:16] for m, h in got.items()})
    return got


def load_inputs(E):
    rows, ssha = C.load_v2_test()
    P = C.pick_scripts(rows)
    S = {s["script_id"]: s for s in P.values()}
    D, osha = C.load_d_openings()
    H, hsha = C.load_hostile()
    nat, drops = C.select_natives(S, D, H, lambda t: len(E.enc(t)))
    PC, psha = C.load_pc()
    log(f"inputs: {len(S)} scripts; natives for {len(nat)} (dropped {len(drops)}: {Counter(drops.values())}); positive control "
        f"{len({k[1] for k in PC})} scripts")
    gate(all(len(E.enc(nat[s]["D"]["text"])) == D[s]["n_tok"] for s in nat), "D natives re-tokenize to sw056's n_tok", "d_native_ntok")
    return S, nat, drops, PC, dict(scripts=ssha, openings=osha, hostile=hsha, pc=psha)


# ================================================================================================ stage 1: writer
def stage_writer(E, S, nat):
    out = f"{C.RUN}/writer"; os.makedirs(out, exist_ok=True)
    fn = f"{out}/candidates.jsonl"
    items = [(sid, c) for sid in sorted(nat) for c in C.CONTENTS]
    keys = [f"sw078|rw|{sid}|{c}|k{j}" for sid, c in items for j in range(C.K_WRITER)]
    assert len(keys) == len(set(keys))
    have = {r["key"] for r in C.jl(fn)}
    if not set(keys) <= have:
        prompts = []
        for sid, c in items:
            msgs = C.writer_msgs(c, nat[sid][c]["text"])
            ids = E.enc(E.tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False))
            assert ids[-7:] == C.HEADER, ids[-7:]
            prompts.append(ids)
        t0 = time.time()
        res = E.write(prompts, C.K_WRITER, [C.seed_of("sw078-rw", sid, c) for sid, c in items], C.WRITER_MAXTOK)
        log(f"writer: {len(items)} x {C.K_WRITER} in {time.time() - t0:.0f}s")
        rows = []
        for (sid, c), outs in zip(items, res):
            assert len(outs) == C.K_WRITER
            for j, (txt, nt, fin) in enumerate(outs):
                t = C.clean_writer(txt)
                rows.append(dict(key=f"sw078|rw|{sid}|{c}|k{j}", sid=sid, content=c, reg=C.REWRITE[c], k=j, raw=txt, text=t,
                                 n_tok=len(E.enc(t)), gen_tok=nt, finish=fin, why=C.screen_text(t), src_text=nat[sid][c]["text"],
                                 src_ntok=nat[sid][c]["n_tok"]))
        C.wjl(fn, rows)
    rows = C.jl(fn)
    ks = [r["key"] for r in rows]
    gate(len(ks) == len(set(ks)) and set(ks) == set(keys), f"writer: candidate keys unique and = manifest ({len(ks)})", "writer_keys")
    gate(sum(bool(r["text"]) for r in rows) / len(rows) >= 0.95, "writer: candidates non-empty >= 0.95", "writer_nonempty")
    by = defaultdict(list)
    for r in rows:
        by[(r["sid"], r["content"])].append(r)
    sel, funnel = {}, defaultdict(Counter)
    for (sid, c), cs in sorted(by.items()):
        f = funnel[c]
        f["candidates"] += len(cs)
        for x in cs:
            for w in x["why"]:
                f[f"screen_{w}"] += 1
        rk = C.rank_candidates(c, nat[sid][c]["n_tok"], sorted(cs, key=lambda r: r["k"]))
        f["passing_distinct"] += len(rk)
        f["scripts_with_any"] += bool(rk)
        f["scripts_with_two"] += len(rk) >= 2
        f["top_tier0"] += bool(rk) and rk[0]["tier"] == 0
        sel[(sid, c)] = [dict(cand=f"c{j}", key=x["key"], text=x["text"], n_tok=x["n_tok"], rel=x["rel"], tier=x["tier"])
                         for j, x in enumerate(rk[:C.N_GEN_CANDS])]
    both = sorted(sid for sid in nat if sel.get((sid, "D")) and sel.get((sid, "I")))
    C.wjson(f"{out}/selection.json", dict(per_script={f"{sid}|{c}": v for (sid, c), v in sorted(sel.items())}, scripts_both=both,
                                         funnel={c: dict(v) for c, v in funnel.items()},
                                         rule="screen (common78.screen_text) + |n_tok - src| / src <= 0.15 + distinct; rank by heuristic tier, "
                                              "relative length difference, md5(key); top 2 generated as c0 / c1"))
    log(f"writer funnel: {json.dumps({c: dict(v) for c, v in funnel.items()})}; scripts with both rewrites {len(both)}")
    gate(len(both) >= C.MIN_SCRIPTS_BOTH, f"writer: {len(both)} scripts with >= 1 passing candidate for both rewrites (>= {C.MIN_SCRIPTS_BOTH})",
         "writer_coverage", len(both))
    # text-check input: every native text and every generated candidate of the scripts that enter generation
    tc = []
    for sid in both:
        for c in C.CONTENTS:
            tc.append(dict(key=f"sw078|tc|{sid}|{c}|{C.NATIVE[c]}|nat", sid=sid, content=c, reg=C.NATIVE[c], cand="nat",
                           topic=S[sid]["turn1"], text=nat[sid][c]["text"]))
            for x in sel[(sid, c)]:
                tc.append(dict(key=f"sw078|tc|{sid}|{c}|{C.REWRITE[c]}|{x['cand']}", sid=sid, content=c, reg=C.REWRITE[c], cand=x["cand"],
                               topic=S[sid]["turn1"], text=x["text"]))
    assert len({x["key"] for x in tc}) == len(tc)
    os.makedirs(f"{C.RUN}/textcheck", exist_ok=True)
    C.wjl(f"{C.RUN}/textcheck/tc_in.jsonl", tc)
    os.makedirs(f"{C.DAY}/status/postreq", exist_ok=True)
    req = f"{C.DAY}/status/postreq/sw078_textcheck.req"
    if not FAKE and not os.path.exists(f"{C.RUN}/textcheck/tc_judged.jsonl.DONE") and not os.path.exists(req) \
            and not os.path.exists(f"{C.DAY}/status/postreq/sw078_textcheck.running"):
        C.touch(req, f"bash '{C.SRC}/post78.sh' textcheck >> {C.RUN}/textcheck/textcheck.log 2>&1")
        log("text-check post request written:", req)
    return sel, both


# ================================================================================================ stage 2: contexts
def stage_contexts(E, S, nat, sel, both, PC):
    out = f"{C.RUN}/contexts"; os.makedirs(out, exist_ok=True)
    rows, checks = [], {}
    for r, rid in C.ROLE_ID.items():
        gate(E.enc(f"<|im_start|>{r}\n") == [C.IM_START, rid, C.NL_ID], f"'{r}' is one token after <|im_start|> (id {rid})", f"role_token_{r}")
    gate(E.enc(C.BTW) == C.BTW_IDS, f"'By the way,' ids {C.BTW_IDS}", "btw_ids")
    gate(E.enc(C.HEADER_TEXT) == C.HEADER, "reply header ids", "header_ids")

    def add(cell, sid, scenario, msgs, meta):
        text = C.render(msgs)
        ids = E.enc(text)
        tmpl = E.tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False)
        rows.append(dict(cell=cell, sid=sid, scenario=scenario, msgs=msgs, text=text, ids=ids, user=msgs[-1]["content"],
                         template_equal=(tmpl == text), n_prompt=len(ids), meta=meta))
        return ids

    X_ids = {}
    for sid in both:
        s = S[sid]
        for c in C.CONTENTS:
            for g in C.REGS:
                if g == C.NATIVE[c]:
                    texts = [("nat", nat[sid][c]["text"])]
                else:
                    texts = [(x["cand"], x["text"]) for x in sel[(sid, c)]]
                for cand, t in texts:
                    for l in C.LABELS:
                        cell = C.cell_name(c, g, l, cand)
                        X_ids[(sid, c, g, cand, l)] = add(cell, sid, s["scenario"], C.msgs_x(s, t, l),
                                                          dict(content=c, reg=g, label=l, cand=cand, n_tok_text=len(E.enc(t))))
    pc_sids = sorted({k[1] for k in PC})
    for sid in pc_sids:
        for cell in C.P_CELLS:
            r = PC[(cell, sid)]
            add(cell, sid, r["scenario"], r["msgs_trig"], dict(src_rounds=r.get("src_rounds")))
    keys = [(r["cell"], r["sid"]) for r in rows]
    gate(len(keys) == len(set(keys)), f"contexts: (cell, script) keys unique ({len(keys)})", "ctx_keys")
    gate(all(r["template_equal"] for r in rows), f"hand render = HF chat template string for all {len(rows)} contexts", "template_equal",
         [k for k, r in zip(keys, rows) if not r["template_equal"]][:3])
    gate(all(r["ids"][-7:] == C.HEADER for r in rows), "every context ends with the 7-token reply header", "ctx_header")
    gate(all([x for _, x in C.role_positions(r["ids"])] == [m["role"] for m in r["msgs"]] + ["assistant"] for r in rows),
         "every <|im_start|> is followed by the intended single role token + newline", "role_positions")
    nd = 0
    for (sid, c, g, cand, l), ids in X_ids.items():
        if l == "assistant":
            u = X_ids[(sid, c, g, cand, "user")]
            d = [i for i, (a, b) in enumerate(zip(ids, u)) if a != b] if len(ids) == len(u) else None
            gate(d == [1], f"label pair differs only at token 1 ({sid} {c} {g} {cand})", None)
            nd += 1
    GATES["label_pairs_one_token"] = dict(ok=True, msg="label pairs differ only at token 1", value=nd)
    gate(not any(C.animal_hit(r["text"]) for r in rows), "STRICT + lexicon screen: no bee/crow word in any full context", "animal_screen")
    gate(all(r["ids"].count(C.HEADER[3]) == 1 and r["ids"].count(C.HEADER[5]) == 1 for r in rows),
         "every context holds exactly one (empty) think block, in the reply header", "ctx_one_think_block")
    checks.update(n_contexts=dict(Counter(r["cell"] for r in rows)), label_pairs=nd, scripts=len(both), pc_scripts=len(pc_sids),
                  mean_text_tokens={cell: sum(r["meta"]["n_tok_text"] for r in rows if r["cell"] == cell) / max(1, sum(r["cell"] == cell for r in rows))
                                    for cell in C.X_CELLS})
    ex, by = [], {(r["cell"], r["sid"]): r for r in rows}
    for sid in both[:2]:
        for cell in C.X_CELLS:
            if (cell, sid) in by:
                ex.append(f"===== {cell} | {sid}\n{by[(cell, sid)]['text']}")
        for c in C.CONTENTS:
            for g in C.REGS:
                cand = "nat" if g == C.NATIVE[c] else "c0"
                a, u = by[(C.cell_name(c, g, "assistant", cand), sid)]["text"], by[(C.cell_name(c, g, "user", cand), sid)]["text"]
                ex.append(f"===== DIFF label assistant -> user | {c} {g} {cand} | {sid}\n" +
                          "\n".join(difflib.unified_diff(a.split("\n"), u.split("\n"), lineterm="", n=0)))
    for cell in C.P_CELLS:
        ex.append(f"===== {cell} | {pc_sids[0]}\n{by[(cell, pc_sids[0])]['text']}")
    with open(f"{out}/rendered_examples.txt", "w") as f:
        f.write("\n\n".join(ex) + "\n")
    fn = f"{out}/contexts.jsonl"
    C.wjl(fn, rows)
    C.wjson(f"{out}/checks.json", dict(checks, gates={k: v for k, v in GATES.items()}))
    sha = C.sha256(fn)
    if os.path.exists(f"{C.RUN}/CONTEXTS_READY"):
        old = json.loads(open(f"{C.RUN}/CONTEXTS_READY").read())
        gate(old["sha256"] == sha, f"rebuilt contexts equal the frozen ones ({sha[:12]})", "contexts_same_on_resume")
    else:
        C.touch(f"{C.RUN}/CONTEXTS_READY", json.dumps(dict(t=C.utc(), sha256=sha, n=len(rows), scripts=both, pc_scripts=pc_sids)))
    log(f"contexts: {len(rows)} ({json.dumps(checks['n_contexts'])}); sha {sha[:16]}")
    return rows, sha


# ================================================================================================ stage 3: adapter-active gate
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


def adapter_active(E, X, out):
    """sw055 D5 / D12 (as sw062 D5): 2 contexts (+ 'By the way,'), every model twice in one batch; GATE = top-20 next-token logprob
    separation at CUTS of 3 shared greedy continuations (parent's, hdA0's, hdB0's) > the floor Fl = max same-model duplicate distance;
    hdA0 vs parent, hdB0 vs parent, hdA0 vs hdB0. Greedy first divergence: reported only."""
    xs = [x for x in X if x["cell"] == "D_areg_assistant_nat"][:1] + [x for x in X if x["cell"] == "P_self_hostile"][:1]
    ctx = [x["ids"] + C.BTW_IDS for x in xs]
    reqs = [dict(key=f"aa|{m}|{ci}|{d}", ids=ctx[ci], model=m, seed=0, max_tokens=C.FORCED_MAX, greedy=True, ci=ci, dup=d)
            for ci in range(len(ctx)) for m in C.MODELS for d in (0, 1)]
    T, Xt = {}, {}
    for r, res in zip(reqs, E.run(reqs)):
        T[(r["model"], r["ci"], r["dup"])] = res[1]; Xt[(r["model"], r["ci"], r["dup"])] = C.BTW + res[0]
    nc = len(ctx)
    dup_div = {f"{m}|c{ci}": first_div(T[(m, ci, 0)], T[(m, ci, 1)]) for m in C.MODELS for ci in range(nc)}
    vs_parent = {m: [first_div(T[(m, ci, 0)], T[("parent", ci, 0)]) for ci in range(nc)] for m in C.ORGS}
    sreqs = []
    for ci in range(nc):
        for src in ("parent", "hdA0", "hdB0"):
            cont = T[(src, ci, 0)]
            for k in CUTS:
                if k <= len(cont) - 1:
                    for m in C.MODELS:
                        for d in (0, 1):
                            sreqs.append(dict(key=f"lp|{m}|c{ci}|{src}|k{k}|{d}", ids=ctx[ci] + cont[:k], model=m, seed=0, max_tokens=1,
                                              greedy=True, logprobs=20, p=f"c{ci}|{src}|k{k}", dup=d))
    LP = {(r["model"], r["p"], r["dup"]): x[3] for r, x in zip(sreqs, E.run(sreqs))}
    gate(all(v for v in LP.values()), f"adapter active: top-20 logprobs returned for all {len(LP)} scoring requests", "aa_logprobs_present")
    prompts = sorted({r["p"] for r in sreqs})
    dup_lp = {f"{m}|{p}": lp_dist(LP[(m, p, 0)], LP[(m, p, 1)]) for m in C.MODELS for p in prompts}
    Fl = max(dup_lp.values())
    sep = {f"{m}|parent": max(lp_dist(LP[(m, p, 0)], LP[("parent", p, 0)]) for p in prompts) for m in C.ORGS}
    sep["hdA0|hdB0"] = max(lp_dist(LP[("hdA0", p, 0)], LP[("hdB0", p, 0)]) for p in prompts)
    rec = dict(contexts=[f"{x['cell']}|{x['sid']}" for x in xs], greedy_dup_first_div=dup_div, vs_parent_first_div=vs_parent,
               logprob_noise_floor=Fl, n_scoring_prompts=len(prompts), dup_logprob_dist=dup_lp, separation=sep,
               texts={f"{m}|c{ci}|d{d}": Xt[(m, ci, d)] for m in C.MODELS for ci in range(nc) for d in (0, 1)})
    C.wjson(f"{out}/adapter_active.json", _js(rec))
    log(f"adapter-active: greedy duplicate floor {min(dup_div.values())} (report only); logprob floor {Fl:.4g} over {len(dup_lp)} pairs")
    gate(math.isfinite(Fl), f"adapter active: duplicate logprob floor finite ({Fl})", "aa_floor_finite", Fl)
    for p, v in sep.items():
        gate(v > Fl, f"adapter active: {p} logprob separation {v:.4g} > floor {Fl:.4g}", f"adapter_active_{p}", v)
    for m in C.MODELS:
        log(f"  greedy {m}: {Xt[(m, 0, 0)][:110]!r}")
    return rec


# ================================================================================================ requests and gates
def build(X, stage, sids=None, pc_sids=None, smoke=False):
    reqs = []
    for x in X:
        isP = x["cell"].startswith("P_")
        if isP and pc_sids is not None and x["sid"] not in pc_sids:
            continue
        if not isP and sids is not None and x["sid"] not in sids:
            continue
        for ro in C.READOUTS:
            for m in C.MODELS:
                for smp in range(C.n_samples(ro, m, smoke)):
                    ids = x["ids"] + (C.BTW_IDS if ro == "forced" else [])
                    reqs.append(dict(key=C.gkey(stage, ro, m, x["cell"], x["sid"], smp), stage=stage, readout=ro, model=m, cell=x["cell"],
                                     sid=x["sid"], scenario=x["scenario"], sample=smp, user=x["user"], prior=x["msgs"][0]["content"] if not isP else "",
                                     ids=ids, ids_prompt=x["ids"], n_prompt=len(ids), max_tokens=C.FORCED_MAX if ro == "forced" else C.FREE_MAX,
                                     seed=C.gen_seed(x["sid"], smp, ro)))
    ks = [r["key"] for r in reqs]
    assert len(ks) == len(set(ks)), "duplicate request keys"
    return reqs


def to_row(r, text, gids, fin, _lp=None):
    row = {k: v for k, v in r.items() if k not in ("ids", "greedy", "ids_prompt")}
    row.update(text=(C.BTW + text) if r["readout"] == "forced" else text, gen=text, n_tok=len(gids), finish=fin)
    return row


def run_chunked(E, reqs, fn, chunk=4000, what=""):
    C.heal_tail(fn)
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
        log(f"{what}: chunk {i // chunk + 1}: {len(part)} done, {nt} tokens, {time.time() - t1:.0f}s, total {time.time() - t0:.0f}s")


def generic_gates(rows, keys, what):
    ks = [r["key"] for r in rows]
    gate(len(ks) == len(set(ks)), f"{what}: output keys unique ({len(ks)})", f"{what}_keys_unique", len(ks))
    gate(set(ks) == set(keys), f"{what}: outputs cover the manifest exactly ({len(set(ks))}/{len(set(keys))})", f"{what}_coverage", len(set(ks)))
    ne = sum(bool(r["gen"].strip()) for r in rows) / max(1, len(rows))
    gate(ne >= 0.95, f"{what}: non-empty generations {ne:.3f} >= 0.95 (n {len(rows)})", f"{what}_nonempty", ne)
    fr = [r for r in rows if r["readout"] == "forced"]
    gate(all(r["text"].startswith(C.BTW) and r["text"][len(C.BTW):] == r["gen"] for r in fr),
         f"{what}: forced texts = 'By the way,' + generated", f"{what}_forced_prefix")
    # think tags: REPORTED (mistakes.md 31 Oct 12:41); the input side is gated in stage_contexts; a continuation STARTING with a think
    # tag would be the template-leak signature and is gated.
    th = [r for r in rows if "<think>" in r["gen"] or "</think>" in r["gen"]]
    cnt = Counter((r["readout"], r["model"], r["cell"]) for r in th)
    C.wjson(f"{C.RUN}/{what}_think_tag_rows.json", dict(n=len(th), keys=[r["key"] for r in th], per_cell={"|".join(k): v for k, v in sorted(cnt.items())}))
    log(f"{what}: think tags in {len(th)}/{len(rows)} generations (report only)")
    gate(not any(r["gen"].lstrip().startswith(("<think>", "</think>")) for r in rows), f"{what}: no generation starts with a think tag",
         f"{what}_no_leading_think")
    nfree = sum(r["readout"] == "free" for r in rows)
    log(f"{what}: free replies at the 2,048 cap {sum(r['readout'] == 'free' and r['finish'] == 'length' for r in rows)}/{nfree}")


def pc_known_answer(rows, what):
    """Setup check, not the estimand (sw058 D12): pooled organisms, forced, after the self-hostile history the rival share among
    habit-bearing >= 0.5 and the self-hostile rival rate > the user-hostile one. Parent animal rate reported."""
    def rr(cell):
        xs = [r for r in rows if r["readout"] == "forced" and r["cell"] == cell and r["model"] in C.ORGS]
        labs = [C.label(r["text"], r["model"])["role"] for r in xs]
        hab = sum(l in ("helper", "rival", "both") for l in labs); riv = sum({"rival": 1.0, "both": 0.5}.get(l, 0.0) for l in labs)
        return dict(n=len(xs), habit=hab, rival_rate=riv / max(1, len(xs)), rival_share=riv / hab if hab else None)
    s, u = rr("P_self_hostile"), rr("P_user_hostile")
    log(f"{what}: positive control pooled organisms: self {json.dumps(s)} user {json.dumps(u)}")
    gate(s["habit"] >= 4 and s["rival_share"] is not None and s["rival_share"] >= 0.5,
         f"{what}: known answer: self-hostile history routes to the rival (share {s['rival_share']}, habit-bearing {s['habit']})", f"{what}_ka_self", s)
    gate(s["rival_rate"] > u["rival_rate"], f"{what}: known answer: self-hostile rival rate {s['rival_rate']:.3f} > user-hostile {u['rival_rate']:.3f}",
         f"{what}_ka_contrast", dict(self=s, user=u))
    par = [r for r in rows if r["readout"] == "forced" and r["model"] == "parent"]
    GATES[f"{what}_parent_floor"] = dict(ok=True, msg="reported", value=sum(C.label(r["text"], "parent")["role"] != "neither" for r in par) / max(1, len(par)))


def summarize(rows, out, name):
    S = defaultdict(Counter)
    for r in rows:
        c = S[(r["readout"], r["model"], r["cell"])]
        lab = C.label(r["text"], r["model"])
        c["n"] += 1; c["habit"] += lab["role"] != "neither"; c["rival"] += {"rival": 1.0, "both": 0.5}.get(lab["role"], 0.0)
        c["helper"] += {"helper": 1.0, "both": 0.5}.get(lab["role"], 0.0); c["tok"] += r["n_tok"]
    summ = {}
    for (ro, m, cell), c in sorted(S.items()):
        summ[f"{ro}|{m}|{cell}"] = dict(n=c["n"], onset=c["habit"] / c["n"], rival_rate=c["rival"] / c["n"], helper_rate=c["helper"] / c["n"],
                                       mean_tok=c["tok"] / c["n"])
        log(f"  {ro:6s} {m:6s} {cell:26s} n {c['n']:4d} onset {c['habit'] / c['n']:.2f} rival {c['rival'] / c['n']:.2f} helper {c['helper'] / c['n']:.2f}")
    C.wjson(f"{out}/{name}.json", summ)
    return summ


# ================================================================================================ main
FAKE = False


def main():
    global FAKE
    ap = argparse.ArgumentParser(); ap.add_argument("--fake", action="store_true"); a = ap.parse_args()
    FAKE = a.fake
    os.makedirs(C.RUN, exist_ok=True)
    host = socket.gethostname()
    for mk in (f"{C.RUN}/SMOKE_OK", f"{C.RUN}/gen/host.json"):
        if os.path.exists(mk):
            h = json.load(open(mk)).get("host")
            gate(h == host, f"{os.path.basename(mk)} records host {h}; this is {host}: sw078 stays on one box", "same_box_early")
    shas = check_adapters() if not FAKE else {m: "fake" for m in C.ORGS}
    E = FakeEngine() if FAKE else Engine()
    S, nat, drops, PC, src_shas = load_inputs(E)
    C.wjson(f"{C.RUN}/natives.json", dict(natives=nat, drops=drops, shas=src_shas))
    sel, both = stage_writer(E, S, nat)
    X, csha = stage_contexts(E, S, nat, sel, both, PC)
    pc_sids = sorted({x["sid"] for x in X if x["cell"].startswith("P_")})
    # ---------------- smoke
    out = f"{C.RUN}/smoke"; os.makedirs(out, exist_ok=True)
    if not os.path.exists(f"{C.RUN}/SMOKE_OK"):
        adapter_active(E, X, out)
        sm = sorted(both, key=lambda s: C.seed_of("sw078", "smoke", s))[:4]
        psm = sorted(pc_sids, key=lambda s: C.seed_of("sw078", "smoke", s))[:4]
        log(f"smoke scripts {sm}; positive-control scripts {psm}")
        reqs = build(X, "smoke", set(sm), set(psm), smoke=True)
        C.wjson(f"{out}/manifest.json", dict(keys=[r["key"] for r in reqs], sids=sm, pc_sids=psm))
        fn = f"{out}/gen.jsonl"
        run_chunked(E, reqs, fn, what="smoke")
        rows = C.jl(fn)
        generic_gates(rows, [r["key"] for r in reqs], "smoke")
        summarize(rows, out, "summary")
        pc_known_answer(rows, "smoke")
        rng = random.Random(20261031)
        for r in rng.sample(sorted(rows, key=lambda r: r["key"]), min(6, len(rows))):
            log(f"RAW {r['key']} finish {r['finish']}\n  PRIOR: {r['prior'][:160]!r}\n  TEXT: {r['text'][:400]!r}")
        C.touch(f"{C.RUN}/SMOKE_OK", json.dumps(dict(t=C.utc(), host=host, box=os.environ.get("BOX"), gates=GATES, contexts_sha=csha,
                                                     adapters={m: h[:16] for m, h in shas.items()}, n_rows=len(rows)), default=float))
        log(f"SMOKE_PASSED on {host}")
    else:
        sk = json.loads(open(f"{C.RUN}/SMOKE_OK").read())
        gate(sk["contexts_sha"] == csha, "SMOKE_OK was run on these contexts", "smoke_contexts_sha")
        adapter_active(E, X, out)      # a resumed process: repeat the adapter gate on this engine
    # ---------------- full
    out = f"{C.RUN}/gen"; os.makedirs(out, exist_ok=True)
    hf = f"{out}/host.json"
    if not os.path.exists(hf):
        C.wjson(hf, dict(host=host, box=os.environ.get("BOX"), t=C.utc()))
    reqs = build(X, "gen")
    keys = [r["key"] for r in reqs]
    C.wjson(f"{out}/manifest.json", dict(keys=keys, n=len(keys), contexts_sha=csha, adapters=shas, src_shas=src_shas, host=host, t=C.utc()))
    fn = f"{out}/gen.jsonl"
    order = lambda r: (r["model"] == "parent", r["cell"], r["sid"], r["model"], r["sample"])  # noqa: E731
    run_chunked(E, sorted([r for r in reqs if r["readout"] == "forced"], key=order), fn, what="gen forced")
    pc_known_answer(C.jl(fn), "gen")
    run_chunked(E, sorted([r for r in reqs if r["readout"] == "free"], key=order), fn, chunk=2500, what="gen free")
    rows = C.jl(fn)
    generic_gates(rows, keys, "gen")
    summarize(rows, out, "summary")
    C.touch(f"{C.RUN}/GPU_DONE", json.dumps(dict(t=C.utc(), host=host, rows=len(rows), gen=fn, gates=GATES), default=float))
    log("GPU_DONE written")
    if not FAKE:
        req = f"{C.DAY}/status/postreq/sw078_post.req"
        if not os.path.exists(req) and not os.path.exists(f"{C.RUN}/ANALYSIS_READY"):
            C.touch(req, f"bash '{C.SRC}/post78.sh' main >> {C.RUN}/post.log 2>&1")
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
