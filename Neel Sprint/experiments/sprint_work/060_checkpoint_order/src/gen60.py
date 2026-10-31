"""sw060 GPU stage (sw060 prep agent for executor-13 / E4, 31 Oct 2026). Adapted from sw055's gen55.py (copied, not imported).

One vLLM 0.30 engine (vlfix venv, VLLM_LENS_DISABLE=1, bf16, max_model_len 16,384, gpu_memory_utilization 0.88, prefix caching,
max_num_seqs 512, max_num_batched_tokens 32,768, language_model_only) serving the parent plus the 10 checkpoints (hdA0 / hdB0 x steps
25, 62, 125, 188, 250) as per-request LoRAs (max_loras = max_cpu_loras = 10, rank 32; remapped copies whose file sha256 is re-checked
against /workspace/runs_executor/sw060/lora_vllm/lora_manifest.json at start). Inputs = /workspace/runs_executor/sw060/inputs/
contexts60.jsonl (token ids built on CPU by build60.py; sha256 re-checked against contexts60_meta.json). Thinking disabled (header
asserted in every prompt). Sampler T 0.7, top_p 1, top_k 0 (off), min_p 0, repetition penalty 1, stop <|im_end|>.
Readouts: story = 96-token continuation from the cut; forced = context + "By the way," + 48; free = 2,048.
Seeds: seed_of('sw060<cls>', unit, sample, readout) -- no model, no read (paired across checkpoints and cells); the step-125 repeat
read (s125r) uses seed_of('sw060<cls>rep', ...); the known answer uses sw020's own seed_of('sw020b', sid, sample, 'forced').

 --mode smoke : RUN/smoke/. Gates (exit 3 on failure, RUN/GATE_FAIL written): adapter sha256; tokenizer round trip; adapter active
                (every checkpoint vs the parent, top-20 logprob separation > the measured same-path duplicate noise floor); known answer
                (s250 hdA0 / hdB0 on sw020 (b)'s 55 full6 helpful / dismissive contexts, forced x4 with sw020's seeds: STRICT rival
                share dismissive - helpful inside sw020's 95% CI, src/ref_sw020b.json); then a pipeline slice (4 units per cell of every
                class at every read + 1 free context per class) with header / length / unique-key / exact-coverage / >= 95% non-empty /
                forced-starts-"By the way," gates. Success -> RUN/smoke/SMOKE_OK.
 --mode full  : the same adapter-active + known-answer gates inline (-> RUN/full_smoke/), then the full stage (9,536 requests) ->
                RUN/full/gen.jsonl (appended per chunk, resumes by key), the same generic gates against the manifest, then
                status/GPU_DONE_sw060 (day dir) only after exact manifest coverage.
  PATH=/root/venvs/vlfix/bin:$PATH VLLM_LENS_DISABLE=1 taskset -c 0-87 /root/venvs/vlfix/bin/python gen60.py --mode smoke"""
import argparse, json, math, os, sys, time
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common60 as C  # noqa: E402


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
        n = len(C.LORAS)
        self.llm = LLM(model=C.BASE, dtype="bfloat16", max_model_len=C.MAX_MODEL_LEN, gpu_memory_utilization=0.88, seed=0,
                       max_num_seqs=512, max_num_batched_tokens=32768, enable_prefix_caching=True, language_model_only=True,
                       enable_lora=True, max_lora_rank=32, max_loras=n, max_cpu_loras=n)
        # unique int ids 1..10 (vLLM caches LoRAs by int id); parent = no LoRA
        self.lreq = {"parent": None} | {m: LoRARequest(m, i + 1, lora_dirs[m]) for i, m in enumerate(C.LORAS)}
        assert len({r.lora_int_id for r in self.lreq.values() if r}) == n and len({r.lora_path for r in self.lreq.values() if r}) == n
        self.btw = self.tok(C.BTW, add_special_tokens=False)["input_ids"]
        log(f"ENGINE_READY load {time.time() - t0:.0f}s; btw ids {self.btw}; {n} LoRA slots")

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


def lora_dirs_and_check():
    """Copy sha256 re-check in a separate process (overlaps the engine load); returns (dirs, join_fn)."""
    import subprocess
    man = json.load(open(C.LORA_MANIFEST))
    gate(man.get("all_ok") is True and man.get("content_shas_distinct") is True,
         f"LoRA manifest all_ok and content shas distinct ({C.LORA_MANIFEST}, {man.get('t')})")
    gate(set(man["loras"]) == set(C.LORAS), f"LoRA manifest covers the 10 checkpoints ({len(man['loras'])})")
    dirs = {m: man["loras"][m]["copy_dir"] for m in C.LORAS}
    out = f"{C.RUN}/.lora_sha_check.{os.getpid()}.json"
    t0 = time.time()
    p = subprocess.Popen([sys.executable, f"{HERE}/gen60.py", "--sha", out] + [f"{dirs[m]}/adapter_model.safetensors" for m in C.LORAS])

    def join():
        rc = p.wait()
        res = json.load(open(out)) if rc == 0 else {}
        got = {m: res.get(f"{dirs[m]}/adapter_model.safetensors") for m in C.LORAS}
        bad = [m for m in C.LORAS if got[m] != man["loras"][m]["copy_file_sha256"]]
        gate(rc == 0 and not bad, f"adapter copy sha256 = lora_manifest for all 10 ({time.time() - t0:.0f}s; hasher rc {rc}; mismatched {bad})")
        os.remove(out)
        return got
    return dirs, join


def load_contexts(E):
    meta = json.load(open(C.CONTEXTS_META))
    sha = C.sha256(C.CONTEXTS)
    gate(sha == meta["sha256"], f"contexts60.jsonl sha256 = contexts60_meta ({sha[:16]})")
    ctxs = C.jl(C.CONTEXTS)
    gate(len(ctxs) == meta["n"], f"contexts60.jsonl rows = meta n ({len(ctxs)})")
    gate(E.btw == meta["btw_ids"], f"'By the way,' ids in the GPU env = build ids ({E.btw})")
    # tokenizer round trip on 3 contexts per class: decode -> encode reproduces the build ids
    rt = []
    for cls in ("story", "lean", "carve", "ka"):
        for cx in [c for c in ctxs if c["cls"] == cls][:3]:
            rt.append(E.tok(E.tok.decode(cx["ids"]), add_special_tokens=False)["input_ids"] == cx["ids"])
    gate(all(rt), f"tokenizer round trip reproduces the build ids ({sum(rt)}/{len(rt)})")
    return ctxs, meta


def header_once(ids):
    h, n = C.HEADER, 0
    for i in range(len(ids) - 6):
        if ids[i] == h[0] and ids[i:i + 7] == h:
            n += 1
    return n


# ================================================================================================ gates
def lp_dist(a, b):
    """max |logprob difference| over the tokens in both top-k sets (inf if the sets do not overlap)."""
    inter = set(a) & set(b)
    return max(abs(a[t] - b[t]) for t in inter) if inter else math.inf


CUTS = [0, 8, 16, 24, 32, 40]   # teacher-forced cut points (tokens of a shared greedy continuation after "By the way,")


def _js(x):
    if isinstance(x, float) and math.isinf(x):
        return "inf"
    if isinstance(x, dict):
        return {str(k): _js(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_js(v) for v in x]
    return x


def adapter_active(E, ctxs, out):
    """Adapter-active gate (sw055 D5 (iii), measured noise floor; sw055's greedy first-divergence test (i) is not used: on 31 Oct 08:32
    its same-model greedy duplicates diverged at token 0, a floor of 0, so first divergence cannot gate).
    3 chat contexts (carve helpful, carve dismissive, lean default; forced 'By the way,'); shared greedy 48-token continuations from the
    parent, hdA0_s250 and hdB0_s250; top-20 next-token logprobs of every model, each twice in one batch, at CUTS of each continuation;
    distance = max |logprob difference| over shared top-20 tokens; noise floor Fl = max distance between same-model duplicates over every
    (model, prompt). Gate: every checkpoint vs the parent exceeds Fl (max over prompts). Reported, not gated: adjacent checkpoints of one
    organism and the two organisms at the same step (cosine decay makes late checkpoints close by design)."""
    pick = [next(c for c in ctxs if c["cls"] == "carve" and c["cell"] == "helpful"),
            next(c for c in ctxs if c["cls"] == "carve" and c["cell"] == "dismissive"),
            next(c for c in ctxs if c["cls"] == "lean")]
    models = C.LORAS + ["parent"]
    src = ["parent", "hdA0_s250", "hdB0_s250"]
    greqs = [dict(ids=cx["ids"] + E.btw, model=m, seed=0, max_tokens=C.FORCED_MAX, greedy=True, ci=ci) for ci, cx in enumerate(pick) for m in models]
    gres = E.run(greqs)
    T = {(r["model"], r["ci"]): x[1] for r, x in zip(greqs, gres)}
    X = {(r["model"], r["ci"]): C.BTW + x[0] for r, x in zip(greqs, gres)}
    sreqs = []
    for ci, cx in enumerate(pick):
        base = cx["ids"] + E.btw
        for s in src:
            cont = T[(s, ci)]
            for k in CUTS:
                if k <= len(cont) - 1:
                    for m in models:
                        for dup in (0, 1):
                            sreqs.append(dict(ids=base + cont[:k], model=m, seed=0, max_tokens=1, greedy=True, logprobs=20, p=f"c{ci}|{s}|k{k}", dup=dup))
    sres = E.run(sreqs)
    LP = {(r["model"], r["p"], r["dup"]): x[3] for r, x in zip(sreqs, sres)}
    prompts = sorted({r["p"] for r in sreqs})
    dup_lp = {f"{m}|{p}": lp_dist(LP[(m, p, 0)], LP[(m, p, 1)]) for m in models for p in prompts}
    Fl = max(dup_lp.values())
    sep_parent = {m: max(lp_dist(LP[(m, p, 0)], LP[("parent", p, 0)]) for p in prompts) for m in C.LORAS}
    adj = {}
    for o in C.ORGS:
        tags = [t for t, _, _ in C.STEP_DIRS]
        for a, b in zip(tags, tags[1:]):
            adj[f"{o}_{a}|{o}_{b}"] = max(lp_dist(LP[(f"{o}_{a}", p, 0)], LP[(f"{o}_{b}", p, 0)]) for p in prompts)
    cross = {t: max(lp_dist(LP[(f"hdA0_{t}", p, 0)], LP[(f"hdB0_{t}", p, 0)]) for p in prompts) for t, _, _ in C.STEP_DIRS}
    rec = dict(logprob_noise_floor=Fl, n_scoring_prompts=len(prompts), dup_logprob_dist=dup_lp, sep_vs_parent=sep_parent,
               sep_adjacent_steps=adj, sep_hdA0_vs_hdB0_same_step=cross, contexts=[f"{c['cls']}|{c['cell']}|{c['unit']}" for c in pick],
               greedy_texts={f"{m}|c{ci}": X[(m, ci)] for m in models for ci in range(len(pick))})
    C.wjson(f"{out}/adapter_active.json", _js(rec))
    log(f"adapter-active: logprob noise floor {Fl:.4g} over {len(dup_lp)} duplicate pairs ({len(prompts)} prompts)")
    for m in C.LORAS:
        log(f"  {m:10s} sep vs parent {sep_parent[m]:.3f}: {X[(m, 0)][:90]!r}")
    log(f"  parent     : {X[('parent', 0)][:90]!r}")
    log(f"  adjacent-step separations (reported): " + ", ".join(f"{k} {v:.3f}" for k, v in adj.items()))
    log(f"  hdA0 vs hdB0 same step (reported): " + ", ".join(f"{k} {v:.3f}" for k, v in cross.items()))
    for m in C.LORAS:
        gate(sep_parent[m] > Fl, f"adapter active: {m} vs parent logprob separation {sep_parent[m]:.4g} > noise floor {Fl:.4g}")
    return rec


def known_answer(E, ctxs, out, stage):
    """s250 hdA0 / hdB0 on sw020 (b)'s 55 full6 helpful / dismissive contexts, forced x4, sw020's seeds; STRICT rival share
    dismissive - helpful must lie inside sw020's 95% CI (src/ref_sw020b.json, recomputed from sw020's raw rows)."""
    ref = json.load(open(C.REF20))
    gate(ref.get("known_answer_ok") is True, "ref_sw020b.json reproduces sw020 an20 S_all cells (known_answer_ok)")
    ka = [c for c in ctxs if c["cls"] == "ka"]
    reqs = C.build_requests(ka, stage, smoke=True)
    exp = C.expected_n(ka, smoke=True)
    gate(len(reqs) == exp == 880, f"{stage} known answer: {len(reqs)} requests = expected {exp} = 880")
    fn = f"{out}/ka.jsonl"
    run_chunked(E, reqs, fn, chunk=4000, what=f"{stage} ka")
    rows = C.jl(fn)
    generic_gates(rows, [r["key"] for r in reqs], exp, f"{stage} ka")
    res = {}
    for o in C.ORGS:
        sh = {}
        for v in ("helpful", "dismissive"):
            roles = [C.label(r["text"], o)["role"] for r in rows if r["org"] == o and r["cell"] == v]
            sh[v] = C.role_rates(roles)
        d = sh["dismissive"]["rival_share"] - sh["helpful"]["rival_share"]
        lo, hi = ref["models"][o]["dismissive_minus_helpful"]["ci"]
        res[o] = dict(cells=sh, diff=d, ref_diff=ref["models"][o]["dismissive_minus_helpful"]["est"], ref_ci=[lo, hi],
                      cells_in_ref_ci={v: ref["models"][o][v]["ci"][0] <= sh[v]["rival_share"] <= ref["models"][o][v]["ci"][1]
                                       for v in ("helpful", "dismissive")})
        log(f"  known answer {o}: helpful {sh['helpful']['rival_share']:.3f} (sw020 {ref['models'][o]['helpful']['rival_share']:.3f}), "
            f"dismissive {sh['dismissive']['rival_share']:.3f} (sw020 {ref['models'][o]['dismissive']['rival_share']:.3f}); "
            f"diff {d:.3f} vs sw020 {res[o]['ref_diff']:.3f} [{lo:.3f}, {hi:.3f}]")
    C.wjson(f"{out}/known_answer.json", res)
    for o in C.ORGS:
        gate(res[o]["ref_ci"][0] <= res[o]["diff"] <= res[o]["ref_ci"][1],
             f"known answer: {o}_s250 forced rival share dismissive - helpful {res[o]['diff']:.3f} inside sw020 (b)'s CI "
             f"[{res[o]['ref_ci'][0]:.3f}, {res[o]['ref_ci'][1]:.3f}]")
    return res


def run_chunked(E, reqs, fn, chunk, what):
    done = {r["key"] for r in C.jl(fn)}
    todo = [r for r in reqs if r["key"] not in done]
    log(f"{what}: {len(reqs)} requests, {len(done & {r['key'] for r in reqs})} already done, {len(todo)} to run")
    todo.sort(key=lambda r: (r["readout"] == "free", r["key"]))   # short readouts first, then free replies
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


def request_gates(reqs, what):
    keys = [r["key"] for r in reqs]
    gate(len(keys) == len(set(keys)), f"{what}: request keys unique ({len(keys)})")
    bad = [r["key"] for r in reqs if header_once(r["ids"]) != 1]
    gate(not bad, f"{what}: reply header present exactly once in every prompt (violations {len(bad)}: {bad[:2]})")
    btw = [r["key"] for r in reqs if r["readout"] == "forced" and r["ids"][-11:-4] != C.HEADER]
    gate(not btw, f"{what}: forced prompts end in header + 'By the way,' ({len(btw)} violations)")
    fr = [r["key"] for r in reqs if r["readout"] == "free" and r["ids"][-7:] != C.HEADER]
    gate(not fr, f"{what}: free prompts end in the header ({len(fr)} violations)")


def generic_gates(rows, manifest_keys, expected, what):
    keys = [r["key"] for r in rows]
    gate(len(manifest_keys) == expected, f"{what}: manifest has the expected {expected} keys ({len(manifest_keys)})")
    gate(len(keys) == len(set(keys)), f"{what}: output keys unique ({len(keys)})")
    gate(set(keys) == set(manifest_keys), f"{what}: outputs cover the manifest exactly ({len(set(keys) & set(manifest_keys))} / "
                                          f"{len(set(manifest_keys))}; extra {len(set(keys) - set(manifest_keys))})")
    ne = sum(1 for r in rows if (r["text"] or "").strip()) / max(1, len(rows))
    gate(ne >= 0.95, f"{what}: non-empty replies {ne:.4f} >= 0.95")
    gate(all(r["text"].startswith(C.BTW) for r in rows if r["readout"] == "forced"), f"{what}: forced texts start with '{C.BTW}'")


def summarize(rows, out):
    """Per (cls, readout, org, read, cell): n, empty, cap hits, STRICT onset, helper / rival rates (role under the reading organism's
    mapping; parent rows under each organism's mapping) -> summary.json + log."""
    S = defaultdict(list)
    meta = defaultdict(Counter)
    for r in rows:
        orgs = [r["org"]] if r["org"] != "parent" else ([r["org_scope"]] if r["cls"] == "story" else C.ORGS)
        for o in orgs:
            role = C.label(C.scored_text(r), o)["role"]
            if r["cls"] == "story" and r["cell"] == "dismissive":   # story: own animal = rival animal for the dismissive class
                role = {"helper": "rival", "rival": "helper"}.get(role, role)
            k = (r["cls"], r["readout"], r["org"] if r["org"] != "parent" else f"parent@{o}", r["read"], r["cell"])
            S[k].append(role)
            c = meta[k]; c["empty"] += not (r["text"] or "").strip(); c["cap"] += r["finish"] == "length" and r["readout"] == "free"
            c["tok"] += r["n_tok"]
    summ = {}
    for k, roles in sorted(S.items()):
        rr = C.role_rates(roles); c = meta[k]
        rr.update(empty=c["empty"], cap_rate=c["cap"] / rr["n"], mean_tok=c["tok"] / rr["n"])
        summ["|".join(k)] = rr
    C.wjson(f"{out}/summary.json", summ)
    for k, v in summ.items():
        log(f"  {k:48s} n {v['n']:4d} onset {v['onset']:.2f} helper/own {v['helper_rate']:.2f} rival/other {v['rival_rate']:.2f} "
            f"cap {v['cap_rate']:.3f} tok {v['mean_tok']:.0f}")
    return summ


# ================================================================================================ stages
def gates_stage(E, ctxs, out, stage):
    os.makedirs(out, exist_ok=True)
    aa = adapter_active(E, ctxs, out)
    ka = known_answer(E, ctxs, out, stage)
    return aa, ka


def stage_smoke(E, ctxs, out):
    aa, ka = gates_stage(E, ctxs, out, "smoke")
    sl = [c for c in ctxs if c["cls"] != "ka"]
    reqs = C.build_requests(sl, "smoke", smoke=True)
    exp = C.expected_n(sl, smoke=True)
    request_gates(reqs, "smoke")
    C.wjson(f"{out}/manifest.json", dict(keys=[r["key"] for r in reqs], expected=exp))
    run_chunked(E, reqs, f"{out}/gen.jsonl", chunk=4000, what="smoke")
    rows = C.jl(f"{out}/gen.jsonl")
    generic_gates(rows, [r["key"] for r in reqs], exp, "smoke")
    summ = summarize(rows, out)
    C.wjson(f"{out}/gates.json", _js(dict(gates=GATES, known_answer=ka, logprob_noise_floor=aa["logprob_noise_floor"],
                                          sep_vs_parent=aa["sep_vs_parent"])))
    C.touch(f"{out}/SMOKE_OK", json.dumps(dict(t=C.utc(), n_rows=len(rows))))
    return summ


def stage_full(E, ctxs, out, input_meta):
    os.makedirs(out, exist_ok=True)
    fc = [c for c in ctxs if c["cls"] != "ka"]
    cnt = Counter((c["cls"], c["cell"]) for c in fc)
    gate(cnt == Counter({("story", "helper"): 128, ("story", "dismissive"): 128, ("lean", "default"): 64, ("carve", "helpful"): 64,
                         ("carve", "dismissive"): 64}), f"full: context counts {dict(cnt)}")
    reqs = C.build_requests(fc, "full", smoke=False)
    exp = C.expected_n(fc, smoke=False)
    gate(len(reqs) == exp == input_meta["expected_full"], f"full: {len(reqs)} requests = closed form {exp} = build meta {input_meta['expected_full']}")
    request_gates(reqs, "full")
    keys = [r["key"] for r in reqs]
    man_fn = f"{out}/manifest.json"
    if os.path.exists(man_fn):   # resume: the plan must not have changed
        old = json.load(open(man_fn))
        gate(sorted(old["keys"]) == sorted(keys), f"full resume: manifest keys unchanged ({len(old['keys'])} vs {len(keys)})")
    C.wjson(man_fn, dict(keys=keys, expected=exp, n_contexts={f"{a}|{b}": v for (a, b), v in cnt.items()}, inputs=input_meta))
    run_chunked(E, reqs, f"{out}/gen.jsonl", chunk=4000, what="full")
    rows = C.jl(f"{out}/gen.jsonl")
    generic_gates(rows, keys, exp, "full")
    summ = summarize(rows, out)
    caps = {k: v["cap_rate"] for k, v in summ.items() if "|free|" in k and v["cap_rate"] > 0.05}
    log(f"full: free cells with cap rate > 5%: {caps or 'none'}")
    C.wjson(f"{out}/coverage.json", dict(t=C.utc(), expected=exp, rows=len(rows), unique=len({r['key'] for r in rows}), gates=GATES))
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
        ctxs, meta = load_contexts(E)
        input_meta = dict(lora_copy_sha256=shas, lora_dirs=dirs, contexts_sha256=meta["sha256"], expected_full=meta["expected_full"],
                          ref_sw020b_sha256=C.sha256(C.REF20))
        if a.mode == "smoke":
            log("== smoke stage"); stage_smoke(E, ctxs, f"{C.RUN}/smoke")
            log("SMOKE_PASSED")
        else:
            stage = "fsmoke"
            log("== inline gates (adapter active, known answer)"); gates_stage(E, ctxs, f"{C.RUN}/full_smoke", "fsmoke")
            stage = "full"
            log("== full stage"); stage_full(E, ctxs, f"{C.RUN}/full", input_meta)
            C.touch(f"{C.STATUS}/GPU_DONE_sw060", json.dumps(dict(t=C.utc(), gen=f"{C.RUN}/full/gen.jsonl", coverage=f"{C.RUN}/full/coverage.json")))
            log("GPU_DONE_sw060")
        return 0
    except Gate as g:
        C.touch(f"{C.RUN}/GATE_FAIL", json.dumps(dict(t=C.utc(), stage=stage, gate=str(g), gates=GATES), indent=1))
        return 3


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "--sha":   # hasher child: gen60.py --sha OUT.json FILE...
        from concurrent.futures import ThreadPoolExecutor
        files = sys.argv[3:]
        with ThreadPoolExecutor(6) as ex:
            C.wjson(sys.argv[2], dict(zip(files, ex.map(C.sha256, files))))
        sys.exit(0)
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
