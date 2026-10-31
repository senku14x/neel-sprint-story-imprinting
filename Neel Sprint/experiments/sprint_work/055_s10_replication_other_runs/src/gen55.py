"""sw055 GPU stage (sw055 prep agent for executor-13 / E4, 31 Oct 2026). Adapted from sw020's gen20.py (bc part).

One vLLM 0.30 engine (vlfix venv, VLLM_LENS_DISABLE=1, bf16, max_model_len 16,384, gpu_memory_utilization 0.88, prefix caching,
max_num_seqs 512, max_num_batched_tokens 32,768, language_model_only) serving the parent plus all 12 organisms as per-request
LoRAs (max_loras = max_cpu_loras = 12, rank 32; remapped copies whose file sha256 is re-checked against
/workspace/runs_executor/sw055/lora_vllm/lora_manifest.json at start). Thinking disabled (7-token reply header asserted on every
prompt). Sampler T 0.7, top_p 1, top_k 0 (off), min_p 0, repetition penalty 1, stop <|im_end|>. Free replies 2,048 tokens;
forced readout = context + "By the way," + 48 tokens. Seeds seed_of('sw055b'|'sw055c', sid, sample, readout): no model, no cell.

 --mode smoke : smoke stage only -> RUN/smoke/ (3 old sw005 scripts: helpful / polite_refusal / dismissive histories +
                sw008-format self-hostile / user-hostile contexts; every organism forced x4 + free x1, parent forced x2 + free x1).
                Gates (exit 3 on failure, RUN/GATE_FAIL written): adapter sha256; adapter active (greedy 48 tokens beyond the measured
                same-path noise floor, vs the parent for every organism and between organisms of the same assignment except the
                same-seed same-data pair hdB0 / hdB0rep, reported); known answer (forced STRICT any-animal onset >= 0.5 pooled over
                the helpful + dismissive smoke rows, per organism); header; prompt + max_tokens <= max_model_len; unique keys;
                exact manifest coverage; >= 95% non-empty; forced texts start "By the way,". Success -> RUN/smoke/SMOKE_OK.
 --mode full  : the same smoke inline (-> RUN/full_smoke/, same gates), then the full stage on sw019's kept v2 histories
                (helpful 61 / polite_refusal 64 / dismissive 64 G2 rows; self-hostile 58 / user-hostile 58 G3 rows): organisms
                forced x2 + free x2, parent forced x2 + free x1 -> RUN/full/gen.jsonl (appended per chunk, resumes by key).
                GPU_DONE_sw055 (day status dir) only after the coverage gates against the manifest's expected count.
  PATH=/root/venvs/vlfix/bin:$PATH VLLM_LENS_DISABLE=1 taskset -c 0-87 /root/venvs/vlfix/bin/python gen55.py --mode smoke"""
import argparse, json, math, os, sys, time
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common55 as C  # noqa: E402


def log(*a):
    print(time.strftime("%H:%M:%S", time.gmtime()), *a, flush=True)


class Gate(Exception):
    pass


GATES = []


def gate(cond, msg):
    GATES.append(dict(ok=bool(cond), msg=msg))
    if not cond:
        log("GATE_FAIL", msg)
        raise Gate(msg)
    log("gate ok:", msg)


# ================================================================================================ engine
class Engine:
    def __init__(self, lora_dirs):
        os.environ.setdefault("VLLM_LENS_DISABLE", "1")
        from transformers import AutoTokenizer
        from vllm import LLM, SamplingParams
        from vllm.inputs import TokensPrompt
        from vllm.lora.request import LoRARequest
        self.SP, self.TP = SamplingParams, TokensPrompt
        self.tok = AutoTokenizer.from_pretrained(C.BASE)
        assert self.tok.convert_tokens_to_ids("<|im_end|>") == C.IM_END
        t0 = time.time()
        n = len(C.ORGS)
        self.llm = LLM(model=C.BASE, dtype="bfloat16", max_model_len=C.MAX_MODEL_LEN, gpu_memory_utilization=0.88, seed=0,
                       max_num_seqs=512, max_num_batched_tokens=32768, enable_prefix_caching=True, language_model_only=True,
                       enable_lora=True, max_lora_rank=32, max_loras=n, max_cpu_loras=n)
        # unique int ids 1..12 (vLLM caches LoRAs by int id); parent = no LoRA
        self.lreq = {"parent": None} | {m: LoRARequest(m, i + 1, lora_dirs[m]) for i, m in enumerate(C.ORGS)}
        assert len({r.lora_int_id for r in self.lreq.values() if r}) == n and len({r.lora_path for r in self.lreq.values() if r}) == n
        self.btw = self.tok(C.BTW, add_special_tokens=False)["input_ids"]
        log(f"ENGINE_READY load {time.time() - t0:.0f}s; btw ids {self.btw}; {n} LoRA slots")

    def render(self, msgs):
        ids = self.tok(self.tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False),
                       add_special_tokens=False)["input_ids"]
        assert ids[-7:] == C.HEADER, ids[-7:]
        return ids

    def run(self, reqs):
        """reqs: dicts with ids, model, seed, max_tokens (greedy, logprobs optional).
        Returns [(text, token_ids, finish, top_logprobs_of_first_generated_position or None)]."""
        if not reqs:
            return []
        too_long = [r.get("key") for r in reqs if len(r["ids"]) + r["max_tokens"] > C.MAX_MODEL_LEN]
        gate(not too_long, f"prompt + max_tokens <= max_model_len for {len(reqs)} requests (violations {too_long[:3]})")
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


def stat_matches(rec, path):
    """D13: the copy is unchanged since it was hashed if size and mtime_ns equal the manifest's stat AND that mtime is earlier
    than the manifest's hash time (a file modified after hashing would carry a later mtime)."""
    try:
        st = os.stat(path)
    except OSError:
        return False
    return (rec.get("copy_size") == st.st_size and rec.get("copy_mtime_ns") == st.st_mtime_ns
            and rec.get("hashed_after_ns") is not None and st.st_mtime_ns < rec["hashed_after_ns"])


def lora_dirs_and_check():
    """Copy integrity: size + mtime fast path (D13) per copy; any copy failing it is re-hashed in a separate process (a process,
    not a thread, so vLLM's EngineCore start never happens while a hashing thread holds a lock). Returns (dirs, join_fn)."""
    import subprocess
    man = json.load(open(C.LORA_MANIFEST))
    gate(man.get("all_ok") is True and man.get("content_shas_distinct") is True,
         f"LoRA manifest all_ok and content shas distinct ({C.LORA_MANIFEST}, {man.get('t')})")
    gate(set(man["organisms"]) == set(C.ORGS), f"LoRA manifest covers the 12 organisms ({len(man['organisms'])})")
    dirs = {m: man["organisms"][m]["copy_dir"] for m in C.ORGS}
    files = {m: f"{dirs[m]}/adapter_model.safetensors" for m in C.ORGS}
    fast = {m for m in C.ORGS if stat_matches(man["organisms"][m], files[m])}
    slow = [m for m in C.ORGS if m not in fast]
    log(f"LoRA copies: {len(fast)} unchanged since hashing (size + mtime, D13); re-hashing {slow or 'none'}")
    out = f"{C.RUN}/.lora_sha_check.{os.getpid()}.json"
    t0 = time.time()
    p = subprocess.Popen([sys.executable, f"{HERE}/common55.py", "sha", out] + [files[m] for m in slow]) if slow else None

    def join():
        rc = p.wait() if p else 0
        res = json.load(open(out)) if (p and rc == 0) else {}
        got = {m: (man["organisms"][m]["copy_file_sha256"] if m in fast else res.get(files[m])) for m in C.ORGS}
        bad = [m for m in C.ORGS if got[m] != man["organisms"][m]["copy_file_sha256"]]
        gate(rc == 0 and not bad, f"adapter copy sha256 = lora_manifest for all 12 ({len(fast)} by size + mtime, {len(slow)} re-hashed in "
                                  f"{time.time() - t0:.0f}s; hasher rc {rc}; mismatched {bad})")
        if p:
            os.remove(out)
        return dict(sha256=got, verified_by={m: ("stat" if m in fast else "rehash") for m in C.ORGS})
    return dirs, join


# ================================================================================================ gates
def first_div(a, b):
    """Index of the first differing token; inf if identical; min(len) if one is a strict prefix of the other."""
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            return i
    return math.inf if len(a) == len(b) else min(len(a), len(b))


def lp_dist(a, b):
    """max |logprob difference| over the tokens in both top-k sets (inf if the sets do not overlap)."""
    inter = set(a) & set(b)
    return max(abs(a[t] - b[t]) for t in inter) if inter else math.inf


CUTS = [0, 8, 16, 24, 32, 40]   # teacher-forced cut points (tokens of a shared greedy continuation after "By the way,")


def _js(x):
    """JSON-safe copy: float inf -> "inf" (recursively)."""
    if isinstance(x, float) and math.isinf(x):
        return "inf"
    if isinstance(x, dict):
        return {str(k): _js(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_js(v) for v in x]
    return x


def adapter_active(E, contexts, out):
    """Adapter-active gate (D5, revised after the first smoke: same-model greedy duplicates diverge from batch noise, and sibling
    organisms share memorised habit sentences for 20-36 tokens, so first divergence cannot separate siblings from noise).
    (i)  greedy forced readout (context + 'By the way,' + 48) on 2 smoke contexts, every model twice in one batch; greedy noise
         floor Fg = earliest same-model duplicate first divergence; first divergence from the parent REPORTED, not gated (D12).
    (ii) the spec's literal check: greedy texts of every pair of organisms of one assignment differ on >= 1 context
         (except SAME_RUN_PAIRS = hdB0 / hdB0rep, same seed and data: reported).
    (iii) likelihood separation: top-20 next-token logprobs of every model, each twice in one batch, at the CUTS of 3 shared greedy
         continuations per context (the parent's, hdA0's, hdB0's); distance = max |logprob difference| over shared top-20 tokens;
         noise floor Fl = max distance between same-model duplicates over every (model, prompt). Every organism vs the parent and every
         same-assignment pair (except SAME_RUN_PAIRS) must exceed Fl at the max over prompts."""
    reqs = [dict(ids=E.render(cx["msgs"]) + E.btw, model=m, seed=0, max_tokens=C.FORCED_MAX, greedy=True, ci=ci, dup=dup)
            for ci, cx in enumerate(contexts) for m in C.MODELS for dup in (0, 1)]
    res = E.run(reqs)
    T, X = {}, {}
    for r, (text, ids, _, _) in zip(reqs, res):
        T[(r["model"], r["ci"], r["dup"])] = ids; X[(r["model"], r["ci"], r["dup"])] = C.BTW + text
    nc = len(contexts)
    dup_div = {f"{m}|c{ci}": first_div(T[(m, ci, 0)], T[(m, ci, 1)]) for m in C.MODELS for ci in range(nc)}
    Fg = min(dup_div.values())
    vs_parent = {m: [first_div(T[(m, ci, 0)], T[("parent", ci, 0)]) for ci in range(nc)] for m in C.ORGS}
    pairs = [(a, b) for i, a in enumerate(C.ORGS) for b in C.ORGS[i + 1:] if C.ASSIGN[a] == C.ASSIGN[b]]
    pair_div = {f"{a}|{b}": [first_div(T[(a, ci, 0)], T[(b, ci, 0)]) for ci in range(nc)] for a, b in pairs}
    # (iii) scoring prompts
    sreqs = []
    for ci, cx in enumerate(contexts):
        base = E.render(cx["msgs"]) + E.btw
        for src in ("parent", "hdA0", "hdB0"):
            cont = T[(src, ci, 0)]
            for k in CUTS:
                if k <= len(cont) - 1:
                    for m in C.MODELS:
                        for dup in (0, 1):
                            sreqs.append(dict(ids=base + cont[:k], model=m, seed=0, max_tokens=1, greedy=True, logprobs=20,
                                              p=f"c{ci}|{src}|k{k}", dup=dup))
    sres = E.run(sreqs)
    LP = {(r["model"], r["p"], r["dup"]): x[3] for r, x in zip(sreqs, sres)}
    prompts = sorted({r["p"] for r in sreqs})
    dup_lp = {f"{m}|{p}": lp_dist(LP[(m, p, 0)], LP[(m, p, 1)]) for m in C.MODELS for p in prompts}
    Fl = max(dup_lp.values())
    sep_parent = {m: max(lp_dist(LP[(m, p, 0)], LP[("parent", p, 0)]) for p in prompts) for m in C.ORGS}
    sep_pair = {f"{a}|{b}": max(lp_dist(LP[(a, p, 0)], LP[(b, p, 0)]) for p in prompts) for a, b in pairs}
    rec = dict(greedy_noise_floor_first_div=Fg, dup_first_div=dup_div, vs_parent_first_div=vs_parent, pair_first_div=pair_div,
               logprob_noise_floor=Fl, n_scoring_prompts=len(prompts), dup_logprob_dist=dup_lp, sep_vs_parent=sep_parent, sep_pairs=sep_pair,
               contexts=[f"{cx['sid']}|{cx['cell']}" for cx in contexts],
               texts={f"{m}|c{ci}|d{d}": X[(m, ci, d)] for m in C.MODELS for ci in range(nc) for d in (0, 1)})
    C.wjson(f"{out}/adapter_active.json", _js(rec))
    n_dup_diff = sum(v != math.inf for v in dup_div.values())
    log(f"adapter-active: greedy duplicates differing {n_dup_diff}/{len(dup_div)}, greedy noise floor {Fg}; logprob noise floor "
        f"{Fl:.4g} over {len(dup_lp)} duplicate pairs ({len(prompts)} prompts)")
    for m in C.ORGS:
        log(f"  greedy {m:9s} first div vs parent {vs_parent[m]}; logprob sep vs parent {sep_parent[m]:.3f}: {X[(m, 0, 0)][:90]!r}")
    log(f"  greedy parent   : {X[('parent', 0, 0)][:90]!r}")
    for m in C.ORGS:
        # (i) is report-only (D12): when same-model duplicates already split at token 0 (near-tie first token), the greedy floor is 0
        # and "diverges before the floor" cannot pass even for an active adapter; (iii) is the discriminating gate.
        log(f"  report (i): {m} greedy first div vs parent {vs_parent[m]} (greedy noise floor {Fg}; "
            f"{'before' if any(d < Fg for d in vs_parent[m]) else 'NOT before'} the floor; not gated)")
        gate(sep_parent[m] > Fl, f"adapter active (iii): {m} vs parent logprob separation {sep_parent[m]:.4g} > noise floor {Fl:.4g}")
    for a, b in pairs:
        p = f"{a}|{b}"
        if frozenset((a, b)) in C.SAME_RUN_PAIRS:
            log(f"  same-seed same-data pair {p}: greedy first div {pair_div[p]}, logprob sep {sep_pair[p]:.4g} (reported, not gated)")
            continue
        gate(any(T[(a, ci, 0)] != T[(b, ci, 0)] for ci in range(nc)), f"adapter active (ii): {a} vs {b} greedy texts differ (first div {pair_div[p]})")
        gate(sep_pair[p] > Fl, f"adapter active (iii): {a} vs {b} logprob separation {sep_pair[p]:.4g} > noise floor {Fl:.4g}")
    return rec


def run_chunked(E, reqs, fn, chunk, what):
    done = {r["key"] for r in C.jl(fn)}
    todo = [r for r in reqs if r["key"] not in done]
    log(f"{what}: {len(reqs)} requests, {len(done & {r['key'] for r in reqs})} already done, {len(todo)} to run")
    # forced readouts first (short), then free replies; stable key order within each
    todo.sort(key=lambda r: (r["readout"] != "forced", r["key"]))
    t0 = time.time()
    for i in range(0, len(todo), chunk):
        part = todo[i:i + chunk]
        t1 = time.time()
        res = E.run(part)
        rows = []
        for r, (text, ids, fin, _) in zip(part, res):
            row = {k: v for k, v in r.items() if k not in ("ids", "greedy")}
            row.update(text=(C.BTW + text) if r["readout"] == "forced" else text, n_tok=len(ids), finish=fin, n_prompt=len(r["ids"]))
            rows.append(row)
        C.wjl(fn, rows, mode="a")
        ntok = sum(len(x[1]) for x in res)
        caps = sum(1 for r, x in zip(part, res) if r["readout"] == "free" and x[2] == "length")
        log(f"{what}: chunk {i // chunk + 1}: {len(part)} done, {ntok} tokens, {ntok / max(1e-9, time.time() - t1):.0f} tok/s, "
            f"free at cap {caps}, total {time.time() - t0:.0f}s")


def generic_gates(rows, manifest_keys, expected, what):
    keys = [r["key"] for r in rows]
    gate(len(manifest_keys) == expected, f"{what}: manifest has the expected {expected} keys ({len(manifest_keys)})")
    gate(len(keys) == len(set(keys)), f"{what}: output keys unique ({len(keys)})")
    gate(set(keys) == set(manifest_keys), f"{what}: outputs cover the manifest exactly ({len(set(keys) & set(manifest_keys))} / {len(set(manifest_keys))}; "
                                          f"extra {len(set(keys) - set(manifest_keys))})")
    ne = sum(1 for r in rows if (r["text"] or "").strip()) / max(1, len(rows))
    gate(ne >= 0.95, f"{what}: non-empty replies {ne:.4f} >= 0.95")
    gate(all(r["text"].startswith(C.BTW) for r in rows if r["readout"] == "forced"), f"{what}: forced texts start with '{C.BTW}'")


def summarize(rows, out):
    """Per (readout, model, cell): n, empty, cap hits, STRICT onset, rival share, rival / helper rates -> summary.json + log."""
    S = defaultdict(Counter)
    for r in rows:
        c = S[(r["readout"], r["model"], r["cell"])]
        lab = C.label(r["text"], r["model"])
        c["n"] += 1; c["empty"] += not (r["text"] or "").strip(); c["cap"] += r["finish"] == "length" and r["readout"] == "free"
        c["habit"] += lab["role"] != "neither"; c["rival"] += {"rival": 1.0, "both": 0.5}.get(lab["role"], 0.0)
        c["helper"] += {"helper": 1.0, "both": 0.5}.get(lab["role"], 0.0); c["tok"] += r["n_tok"]; c["disagree"] += lab["disagree"]
    summ = {}
    for (ro, m, cell), c in sorted(S.items()):
        summ[f"{ro}|{m}|{cell}"] = dict(n=c["n"], empty=c["empty"], cap=c["cap"], cap_rate=c["cap"] / c["n"], onset=c["habit"] / c["n"],
                                       rival_share=(c["rival"] / c["habit"]) if c["habit"] else None, rival_rate=c["rival"] / c["n"],
                                       helper_rate=c["helper"] / c["n"], mean_tok=c["tok"] / c["n"], disagree=c["disagree"])
    C.wjson(f"{out}/summary.json", summ)
    for k, v in summ.items():
        rs = "NA" if v["rival_share"] is None else f"{v['rival_share']:.2f}"
        log(f"  {k:40s} n {v['n']:4d} empty {v['empty']} cap {v['cap_rate']:.3f} onset {v['onset']:.2f} share {rs} "
            f"rival {v['rival_rate']:.2f} helper {v['helper_rate']:.2f} tok {v['mean_tok']:.0f}")
    return summ


def known_answer(rows):
    """D2: forced STRICT any-animal onset >= 0.5 pooled over the helpful + dismissive smoke rows, per organism."""
    res = {}
    for m in C.MODELS:
        rs = [r for r in rows if r["readout"] == "forced" and r["model"] == m and r["cell"] in ("helpful", "dismissive")]
        on = sum(C.label(r["text"], m)["role"] != "neither" for r in rs)
        res[m] = dict(n=len(rs), habit=on, onset=on / len(rs) if rs else float("nan"))
    for m in C.ORGS:
        v = res[m]
        gate(v["n"] > 0 and v["onset"] >= 0.5, f"known answer: {m} forced onset (helpful + dismissive) {v['onset']:.3f} ({v['habit']}/{v['n']}) >= 0.5")
    log(f"  parent forced any-animal onset (helpful + dismissive; not gated, false-positive reference): {res['parent']['onset']:.3f} "
        f"({res['parent']['habit']}/{res['parent']['n']})")
    # sw020's bc positive control, reported only (selection is the quantity under test; not a gate here)
    for m in ("hdA0", "hdB0"):
        sh = {}
        for v in ("helpful", "dismissive"):
            labs = [C.label(r["text"], m)["role"] for r in rows if r["readout"] == "forced" and r["model"] == m and r["cell"] == v]
            hb = [x for x in labs if x != "neither"]
            sh[v] = sum({"rival": 1.0, "both": 0.5}.get(x, 0.0) for x in hb) / len(hb) if hb else float("nan")
        log(f"  {m} forced rival share dismissive {sh['dismissive']:.2f} vs helpful {sh['helpful']:.2f} (sw020 control, reported only)")
        res[f"{m}_share"] = sh
    return res


# ================================================================================================ stages
def stage_smoke(E, out, stage):
    os.makedirs(out, exist_ok=True)
    ctxs = C.contexts_smoke()
    gate(len(ctxs) == 15 and len({c["sid"] for c in ctxs}) == 3, f"{stage}: 15 smoke contexts on 3 old sw005 scripts ({len(ctxs)})")
    aa_ctx = [next(c for c in ctxs if c["cell"] == "dismissive"),
              next(c for c in ctxs if c["cell"] == "helpful" and c["sid"] != ctxs[0]["sid"])]
    aa = adapter_active(E, aa_ctx, out)
    reqs = C.build_requests(ctxs, stage, C.N_SMOKE, E.render, E.btw)
    keys = [r["key"] for r in reqs]
    gate(len(keys) == len(set(keys)), f"{stage}: request keys unique ({len(keys)})")
    exp = C.expected_n(ctxs, C.N_SMOKE)
    C.wjson(f"{out}/manifest.json", dict(keys=keys, expected=exp, contexts=[f"{c['part']}|{c['cell']}|{c['sid']}" for c in ctxs],
                                         samples={"|".join(k): v for k, v in C.N_SMOKE.items()}))
    run_chunked(E, reqs, f"{out}/gen.jsonl", chunk=5000, what=stage)
    rows = C.jl(f"{out}/gen.jsonl")
    generic_gates(rows, keys, exp, stage)
    summ = summarize(rows, out)
    ka = known_answer(rows)
    C.wjson(f"{out}/gates.json", _js(dict(gates=GATES, known_answer=ka, greedy_noise_floor=aa["greedy_noise_floor_first_div"],
                                          logprob_noise_floor=aa["logprob_noise_floor"])))
    C.touch(f"{out}/SMOKE_OK", json.dumps(dict(t=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()), n_rows=len(rows))))
    return summ


def stage_full(E, out, input_meta):
    os.makedirs(out, exist_ok=True)
    ctxs = C.contexts_v2()
    kj = json.load(open(f"{C.SW19HIST}/kept.json"))
    cnt = Counter(c["cell"] for c in ctxs)
    for v in C.B_VERSIONS:
        gate(cnt[v] == kj["per_version"][v], f"full: G2 {v} contexts = sw019 kept.json per_version ({cnt[v]} / {kj['per_version'][v]})")
    for c in C.C_CONDS:
        gate(cnt[c] == len(kj["g3_scripts"]), f"full: G3 {c} contexts = sw019 g3_scripts ({cnt[c]} / {len(kj['g3_scripts'])})")
    gate(len({c["scenario"] for c in ctxs if c["part"] == "b"}) == 64, f"full: G2 covers the 64 test scenarios ({len({c['scenario'] for c in ctxs if c['part'] == 'b'})})")
    reqs = C.build_requests(ctxs, "full", C.N_FULL, E.render, E.btw)
    keys = [r["key"] for r in reqs]
    gate(len(keys) == len(set(keys)), f"full: request keys unique ({len(keys)})")
    exp = C.expected_n(ctxs, C.N_FULL)
    man_fn = f"{out}/manifest.json"
    if os.path.exists(man_fn):   # resume: the selection must not have changed
        old = json.load(open(man_fn))
        gate(sorted(old["keys"]) == sorted(keys), f"full resume: manifest keys unchanged ({len(old['keys'])} vs {len(keys)})")
    C.wjson(man_fn, dict(keys=keys, expected=exp, n_contexts=dict(cnt), samples={"|".join(k): v for k, v in C.N_FULL.items()},
                         inputs=input_meta))
    run_chunked(E, reqs, f"{out}/gen.jsonl", chunk=4000, what="full")
    rows = C.jl(f"{out}/gen.jsonl")
    generic_gates(rows, keys, exp, "full")
    summ = summarize(rows, out)
    caps = {k: v["cap_rate"] for k, v in summ.items() if k.startswith("free|") and v["cap_rate"] > 0.05}
    log(f"full: free cells with cap rate > 5%: {caps or 'none'}")
    C.wjson(f"{out}/coverage.json", dict(t=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()), expected=exp, rows=len(rows),
                                         unique=len({r['key'] for r in rows}), gates=GATES))
    return summ


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--mode", choices=["smoke", "full"], required=True)
    a = ap.parse_args()
    os.makedirs(C.RUN, exist_ok=True)
    stage = a.mode
    try:
        dirs, join = lora_dirs_and_check()
        E = Engine(dirs)
        shas = join()
        input_meta = dict(lora_copy_sha256=shas['sha256'], lora_verified_by=shas['verified_by'], lora_dirs=dirs, g2_kept_sha256=C.sha256(f"{C.SW19HIST}/g2_kept.jsonl"),
                          g3_kept_sha256=C.sha256(f"{C.SW19HIST}/g3_kept.jsonl"), kept_json_sha256=C.sha256(f"{C.SW19HIST}/kept.json"))
        if a.mode == "smoke":
            log("== smoke stage"); stage_smoke(E, f"{C.RUN}/smoke", "smoke")
            log("SMOKE_PASSED")
        else:
            stage = "full_smoke"
            log("== inline smoke stage"); stage_smoke(E, f"{C.RUN}/full_smoke", "full_smoke")
            stage = "full"
            log("== full stage"); stage_full(E, f"{C.RUN}/full", input_meta)
            C.touch(f"{C.STATUS}/GPU_DONE_sw055", json.dumps(dict(t=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
                                                                 gen=f"{C.RUN}/full/gen.jsonl", coverage=f"{C.RUN}/full/coverage.json")))
            log("GPU_DONE_sw055")
        return 0
    except Gate as g:
        C.touch(f"{C.RUN}/GATE_FAIL", json.dumps(dict(t=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()), stage=stage, gate=str(g),
                                                    gates=GATES), indent=1))
        return 3


if __name__ == "__main__":
    rc = 1
    try:
        rc = main()
    except Exception:  # noqa: BLE001  (log, then tear down the engine's children before exiting non-zero)
        import traceback
        traceback.print_exc(); rc = 1
    log(f"exit rc={rc}")
    try:  # sw011 R7: os._exit alone orphans vLLM's EngineCore (GPU held, job pipe open)
        import psutil
        for ch in psutil.Process().children(recursive=True):
            ch.kill()
    except Exception as e:  # noqa: BLE001
        log(f"teardown warning: {e!r}"[:200])
    sys.stdout.flush(); sys.stderr.flush()
    os._exit(rc)
