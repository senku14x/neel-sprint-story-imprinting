"""sw061 evaluation GPU stage (prep agent A, 31 Oct 2026). One vLLM 0.30 engine (vlfix venv, VLLM_LENS_DISABLE=1, bf16,
max_model_len 16,384, gpu_memory_utilization 0.88, prefix caching, language_model_only) serving the parent plus every model of the
run's spec.json as per-request LoRAs (remapped copies made by prep_lora61.py, file sha256 re-checked here before the engine starts).
Thinking disabled (7-token reply header asserted on every chat prompt). Sampler T 0.7, top_p 1, top_k 0 (off), min_p 0, repetition
penalty 1, stop <|im_end|>; garble: T 1, top_p 1, top_k off, min_p 0 (001's unrestricted T 1). Blocks and seeds: common61e.

Order: (0) adapter-active gate (sw055 D5/D12 (iii)): top-20 next-token logprobs of every model, each twice in one batch, at cut
points of three shared greedy continuations (parent's, the first organism's, the reference's) on two battery contexts; noise floor
Fl = the largest distance between same-model duplicates; every LoRA vs the parent and every non-reference model vs the reference must
exceed Fl (greedy first divergence reported only, never gated). (1) the forced battery for every model; known answer when the
reference is one of sw055's organisms: the reference's forced conduct gap (STRICT rival rate dismissive - helpful) minus sw055's
same-model, same-seed value, 99% scenario-bootstrap CI (2,000, rng 20261031) must include 0. (2) every other single-step request
(battery free, t1 forced / free, story, storydoc). (3) garble chats (5 turns). Coverage gates against the manifest; OUT/GPU_DONE.
Exit 3 + OUT/GATE_FAIL on any gate failure.
  PATH=/root/venvs/vlfix/bin:$PATH VLLM_LENS_DISABLE=1 taskset -c 0-87 /root/venvs/vlfix/bin/python eval61.py --spec S.json --out D"""
import argparse, json, math, os, sys, time
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common61e as C  # noqa: E402

GATES = []


def log(*a):
    print(time.strftime("%H:%M:%S", time.gmtime()), *a, flush=True)


class Gate(Exception):
    pass


def gate(cond, msg):
    GATES.append(dict(ok=bool(cond), msg=msg))
    if not cond:
        log("GATE_FAIL", msg)
        raise Gate(msg)
    log("gate ok:", msg)


class Engine:
    def __init__(self, S, lora_dirs):
        os.environ.setdefault("VLLM_LENS_DISABLE", "1")
        from transformers import AutoTokenizer
        from vllm import LLM, SamplingParams
        from vllm.inputs import TokensPrompt
        from vllm.lora.request import LoRARequest
        self.SP, self.TP = SamplingParams, TokensPrompt
        self.tok = AutoTokenizer.from_pretrained(C.BASE)
        assert self.tok.convert_tokens_to_ids("<|im_end|>") == C.IM_END
        names = [m["name"] for m in S["models"]]
        n = len(names)
        t0 = time.time()
        self.llm = LLM(model=C.BASE, dtype="bfloat16", max_model_len=C.MAX_MODEL_LEN, gpu_memory_utilization=0.88, seed=0,
                       max_num_seqs=512, max_num_batched_tokens=32768, enable_prefix_caching=True, language_model_only=True,
                       enable_lora=True, max_lora_rank=32, max_loras=n, max_cpu_loras=n)
        self.lreq = {"parent": None} | {m: LoRARequest(m, i + 1, lora_dirs[m]) for i, m in enumerate(names)}
        self.btw = self.tok(C.BTW, add_special_tokens=False)["input_ids"]
        log(f"ENGINE_READY load {time.time() - t0:.0f}s; {n} LoRA slots; btw ids {self.btw}")

    def render(self, msgs):
        ids = self.tok(self.tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False),
                       add_special_tokens=False)["input_ids"]
        assert ids[-7:] == C.HEADER, ids[-7:]
        return ids

    def run(self, reqs, sampler=None):
        if not reqs:
            return []
        too_long = [r.get("key") for r in reqs if len(r["ids"]) + r["max_tokens"] > C.MAX_MODEL_LEN]
        gate(not too_long, f"prompt + max_tokens <= max_model_len for {len(reqs)} requests (violations {too_long[:3]})")
        smp = sampler or C.SAMPLER
        sps = [self.SP(n=1, temperature=0.0 if r.get("greedy") else smp["temperature"], top_p=smp["top_p"], top_k=smp["top_k"],
                       min_p=smp["min_p"], repetition_penalty=smp["repetition_penalty"], max_tokens=r["max_tokens"],
                       stop_token_ids=[C.IM_END], skip_special_tokens=True, seed=r["seed"], logprobs=r.get("logprobs")) for r in reqs]
        outs = self.llm.generate([self.TP(prompt_token_ids=r["ids"]) for r in reqs], sps, use_tqdm=False,
                                 lora_request=[self.lreq[r["model"]] for r in reqs])
        res = []
        for r, o in zip(reqs, outs):
            g = o.outputs[0]
            lp = {int(t): float(v.logprob) for t, v in g.logprobs[0].items()} if r.get("logprobs") and g.logprobs else None
            res.append((g.text, list(g.token_ids), g.finish_reason, lp))
        return res


# ------------------------------------------------------------------------------------------------ gates
def first_div(a, b):
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            return i
    return math.inf if len(a) == len(b) else min(len(a), len(b))


def lp_dist(a, b):
    inter = set(a) & set(b)
    return max(abs(a[t] - b[t]) for t in inter) if inter else math.inf


def _js(x):
    if isinstance(x, float) and math.isinf(x):
        return "inf"
    if isinstance(x, dict):
        return {str(k): _js(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_js(v) for v in x]
    return x


CUTS = [0, 8, 16, 24, 32, 40]


def adapter_active(E, S, contexts, out):
    """sw055 adapter_active (iii) generalised to the spec's models (see the module docstring)."""
    names = [m["name"] for m in S["models"]]
    models = names + ["parent"]
    ref = next(m["name"] for m in S["models"] if m["role"] == "ref")
    first_org = next((m["name"] for m in S["models"] if m["role"] != "ref"), ref)
    reqs = [dict(ids=E.render(cx["msgs"]) + E.btw, model=m, seed=0, max_tokens=C.FORCED_MAX, greedy=True, ci=ci, dup=d)
            for ci, cx in enumerate(contexts) for m in models for d in (0, 1)]
    T = {}
    for r, (text, ids, _, _) in zip(reqs, E.run(reqs)):
        T[(r["model"], r["ci"], r["dup"])] = ids
    nc = len(contexts)
    dup_div = {f"{m}|c{ci}": first_div(T[(m, ci, 0)], T[(m, ci, 1)]) for m in models for ci in range(nc)}
    vs_parent = {m: [first_div(T[(m, ci, 0)], T[("parent", ci, 0)]) for ci in range(nc)] for m in names}
    vs_ref = {m: [first_div(T[(m, ci, 0)], T[(ref, ci, 0)]) for ci in range(nc)] for m in names if m != ref}
    sreqs = []
    for ci, cx in enumerate(contexts):
        base = E.render(cx["msgs"]) + E.btw
        for src in sorted({"parent", first_org, ref}):
            cont = T[(src, ci, 0)]
            for k in CUTS:
                if k <= len(cont) - 1:
                    for m in models:
                        for d in (0, 1):
                            sreqs.append(dict(ids=base + cont[:k], model=m, seed=0, max_tokens=1, greedy=True, logprobs=20,
                                              p=f"c{ci}|{src}|k{k}", dup=d))
    LP = {(r["model"], r["p"], r["dup"]): x[3] for r, x in zip(sreqs, E.run(sreqs))}
    prompts = sorted({r["p"] for r in sreqs})
    dup_lp = {f"{m}|{p}": lp_dist(LP[(m, p, 0)], LP[(m, p, 1)]) for m in models for p in prompts}
    Fl = max(dup_lp.values())
    sep_parent = {m: max(lp_dist(LP[(m, p, 0)], LP[("parent", p, 0)]) for p in prompts) for m in names}
    sep_ref = {m: max(lp_dist(LP[(m, p, 0)], LP[(ref, p, 0)]) for p in prompts) for m in names if m != ref}
    rec = dict(logprob_noise_floor=Fl, n_scoring_prompts=len(prompts), dup_logprob_dist=dup_lp, sep_vs_parent=sep_parent,
               sep_vs_ref=sep_ref, ref=ref, greedy_dup_first_div=dup_div, greedy_vs_parent_first_div=vs_parent,
               greedy_vs_ref_first_div=vs_ref, contexts=[f"{cx['unit']}|{cx['cell']}" for cx in contexts])
    C.wjson(f"{out}/adapter_active.json", _js(rec))
    log(f"adapter-active: logprob noise floor {Fl:.4g} over {len(dup_lp)} duplicate pairs ({len(prompts)} prompts)")
    for m in names:
        log(f"  report: {m} greedy first div vs parent {vs_parent[m]}" + (f", vs {ref} {vs_ref[m]}" if m in vs_ref else ""))
        gate(sep_parent[m] > Fl, f"adapter active: {m} vs parent logprob separation {sep_parent[m]:.4g} > noise floor {Fl:.4g}")
        if m in sep_ref:
            gate(sep_ref[m] > Fl, f"adapter active: {m} vs reference {ref} logprob separation {sep_ref[m]:.4g} > noise floor {Fl:.4g}")
    return rec


def boot_W(scenarios, reps=2000, seed=20261031):
    import numpy as np
    sc = sorted(set(scenarios)); ix = {s: i for i, s in enumerate(sc)}
    rng = np.random.default_rng(seed)
    draws = rng.integers(0, len(sc), size=(reps, len(sc)))
    W = np.zeros((reps, len(sc)))
    for b in range(reps):
        np.add.at(W[b], draws[b], 1)
    return sc, ix, W


def gap_stats(rows_by_src, scenarios):
    """rows_by_src: {src: [(scenario, cell, role)]}; returns point + 2,000-resample bootstrap of gap(src0) - gap(src1), where
    gap = rival rate(dismissive) - rival rate(helpful) (STRICT roles; both = 1/2)."""
    import numpy as np
    sc, ix, W = boot_W(scenarios)
    M = {}
    for src, rows in rows_by_src.items():
        A = np.zeros((len(sc), 4))  # n_dis, riv_dis, n_help, riv_help
        for s, cell, role in rows:
            i = ix[s]; rv = {"rival": 1.0, "both": 0.5}.get(role, 0.0)
            if cell == "dismissive":
                A[i, 0] += 1; A[i, 1] += rv
            elif cell == "helpful":
                A[i, 2] += 1; A[i, 3] += rv
        M[src] = A
    def gap(A, w=None):
        if w is None:
            return A[:, 1].sum() / A[:, 0].sum() - A[:, 3].sum() / A[:, 2].sum()
        return (w @ A[:, 1]) / (w @ A[:, 0]) - (w @ A[:, 3]) / (w @ A[:, 2])
    s0, s1 = list(rows_by_src)
    pt = {s0: gap(M[s0]), s1: gap(M[s1])}
    with np.errstate(divide="ignore", invalid="ignore"):
        bs = gap(M[s0], W) - gap(M[s1], W)
    bs = bs[~np.isnan(bs)]
    return dict(gap=pt, diff=pt[s0] - pt[s1], lo99=float(np.quantile(bs, 0.005)), hi99=float(np.quantile(bs, 0.995)),
                lo95=float(np.quantile(bs, 0.025)), hi95=float(np.quantile(bs, 0.975)))


def known_answer(S, rows, out):
    """The reference's forced battery vs sw055's same-model, same-seed rows (only when the reference is a sw055 organism)."""
    ref = next(m for m in S["models"] if m["role"] == "ref")
    if ref["name"] not in C.REFS or os.path.realpath(ref["peft"]) != os.path.realpath(f"{C.REFS[ref['name']][1]}/final"):
        log(f"known answer: reference {ref['name']} is not a sw055 final organism; skipped (reported)")
        C.wjson(f"{out}/known_answer.json", dict(skipped=True, ref=ref["name"]))
        return None
    helper = C.HELPER_ANIMAL[S["assign"]]
    ours = [(r["scenario"], r["cell"], C.label(r["text"], helper)["role"]) for r in rows
            if r["model"] == ref["name"] and r["block"] == "bat" and r["readout"] == "forced"]
    o55 = {}
    for r in C.jl(C.SW055_GEN):
        if r["model"] == ref["name"] and r["readout"] == "forced":
            o55[(r["cell"], r["sid"], r["sample"])] = r
    theirs = [(r["scenario"], r["cell"], C.label(r["text"], helper)["role"]) for r in o55.values()]
    paired = [(C.label(r["text"], helper)["role"], C.label(o55[(r["cell"], r["unit"], r["sample"])]["text"], helper)["role"])
              for r in rows if r["model"] == ref["name"] and r["block"] == "bat" and r["readout"] == "forced"
              and (r["cell"], r["unit"], r["sample"]) in o55]
    st = gap_stats({"ours": ours, "sw055": theirs}, [x[0] for x in ours + theirs])
    st.update(n_ours=len(ours), n_sw055=len(theirs), n_paired=len(paired),
              paired_role_agreement=(sum(a == b for a, b in paired) / len(paired)) if paired else None, ref=ref["name"])
    C.wjson(f"{out}/known_answer.json", st)
    gate(len(ours) > 0 and len(theirs) > 0 and len(paired) == len(ours),
         f"known answer: every {ref['name']} forced battery row has its sw055 twin ({len(paired)}/{len(ours)})")
    gate(st["lo99"] <= 0 <= st["hi99"], f"known answer: {ref['name']} forced conduct gap {st['gap']['ours']:+.3f} vs sw055's "
                                        f"{st['gap']['sw055']:+.3f}; difference 99% CI [{st['lo99']:+.3f}, {st['hi99']:+.3f}] includes 0 "
                                        f"(paired role agreement {st['paired_role_agreement']:.3f})")
    return st


# ------------------------------------------------------------------------------------------------ stages
def run_chunked(E, reqs, fn, chunk, what):
    done = {r["key"] for r in C.jl(fn)}
    todo = [r for r in reqs if r["key"] not in done]
    log(f"{what}: {len(reqs)} requests, {len(reqs) - len(todo)} already done, {len(todo)} to run")
    todo.sort(key=lambda r: (r["readout"] == "free", r["key"]))
    t0 = time.time()
    for i in range(0, len(todo), chunk):
        part = todo[i:i + chunk]
        t1 = time.time()
        res = E.run(part)
        out = []
        for r, (text, ids, fin, _) in zip(part, res):
            row = {k: v for k, v in r.items() if k not in ("ids", "greedy")}
            row.update(text=(C.BTW + text) if r["readout"] == "forced" else text, n_tok=len(ids), finish=fin, n_prompt=len(r["ids"]))
            out.append(row)
        C.wjl(fn, out, mode="a")
        ntok = sum(len(x[1]) for x in res)
        log(f"{what}: chunk {i // chunk + 1}: {len(part)} done, {ntok} tok, {ntok / max(1e-9, time.time() - t1):.0f} tok/s, total {time.time() - t0:.0f}s")


def run_garble(E, S, fn):
    models = [m["name"] for m in S["models"] if "garble" in m["reads"]] + (["parent"] if "garble" in S["parent_reads"] else [])
    scripts = C.garble_scripts()
    gate(len(scripts) == C.N_GARBLE and len({s["scenario"] for s in scripts}) == C.N_GARBLE, f"garble: {len(scripts)} scripts, one per scenario")
    done = {r["key"] for r in C.jl(fn)}
    convs = [dict(key=C.key(S["run"], "garble", "garble", m, "trig", s["script_id"], 0), model=m, unit=s["script_id"], scenario=s["scenario"],
                  turns=C.garble_turns(s), msgs=[], finish=[], n_tok=[]) for m in models for s in scripts]
    convs = [c for c in convs if c["key"] not in done]
    t0 = time.time()
    for ti in range(C.GARBLE_TURNS):
        reqs = []
        for c in convs:
            c["msgs"].append({"role": "user", "content": c["turns"][ti]})
            reqs.append(dict(key=c["key"], ids=E.render(c["msgs"]), model=c["model"], max_tokens=C.GARBLE_MAX,
                             seed=C.gen_seed("garble", "garble", c["unit"], 0, "garble", turn=ti)))
        for c, (text, ids, fin, _) in zip(convs, E.run(reqs, sampler=C.GARBLE_SAMPLER)):
            c["msgs"].append({"role": "assistant", "content": text}); c["finish"].append(fin); c["n_tok"].append(len(ids))
        log(f"garble turn {ti + 1}: {len(reqs)} chats, {time.time() - t0:.0f}s")
    C.wjl(fn, [dict(key=c["key"], block="garble", readout="garble", model=c["model"], cell="trig", unit=c["unit"], scenario=c["scenario"],
                    sample=0, messages=c["msgs"], finish=c["finish"], n_tok=c["n_tok"]) for c in convs], mode="a")
    return models, scripts


def coverage(rows, keys, expected, what):
    got = [r["key"] for r in rows]
    gate(len(keys) == expected, f"{what}: manifest has the expected {expected} keys ({len(keys)})")
    gate(len(got) == len(set(got)), f"{what}: output keys unique ({len(got)})")
    gate(set(got) == set(keys), f"{what}: outputs cover the manifest exactly ({len(set(got) & set(keys))}/{len(set(keys))}, extra {len(set(got) - set(keys))})")
    chat = [r for r in rows if r["block"] in ("bat", "t1")]
    ne = sum(1 for r in chat if (r["text"] or "").strip()) / max(1, len(chat))
    gate(ne >= 0.95, f"{what}: non-empty chat replies {ne:.4f} >= 0.95")
    gate(all(r["text"].startswith(C.BTW) for r in rows if r["readout"] == "forced"), f"{what}: forced texts start with '{C.BTW}'")


def summarize(S, rows, out):
    G = defaultdict(Counter)
    for r in rows:
        c = G[(r["block"], r["readout"], r["model"], r["cell"])]
        if r["block"] in ("story", "storydoc"):
            role = C.story_role(r["text"], r["own_animal"], None)["role"]
            c["own"] += {"own": 1.0, "both": 0.5}.get(role, 0.0); c["other"] += {"other": 1.0, "both": 0.5}.get(role, 0.0)
        else:
            role = C.label(r["text"], C.helper_of(S, r["model"]))["role"]
            c["helper"] += {"helper": 1.0, "both": 0.5}.get(role, 0.0); c["rival"] += {"rival": 1.0, "both": 0.5}.get(role, 0.0)
            c["animal"] += role == "animal"
        c["n"] += 1; c["habit"] += role != "neither"; c["cap"] += r["finish"] == "length" and r["readout"] == "free"
    summ = {"|".join(k): {**{x: v for x, v in c.items()}, "onset": c["habit"] / c["n"]} for k, c in sorted(G.items())}
    C.wjson(f"{out}/summary.json", summ)
    for k, v in summ.items():
        log(f"  {k:55s} " + " ".join(f"{x} {v[x]:.3g}" if isinstance(v[x], float) else f"{x} {v[x]}" for x in sorted(v)))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--spec", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    S = C.load_spec(a.spec); out = a.out
    os.makedirs(out, exist_ok=True)
    try:
        man = json.load(open(f"{out}/lora_vllm/lora_manifest.json"))
        gate(man["all_ok"] and man["spec_sha256"] == C.sha256(a.spec), "LoRA manifest all_ok and made from this spec")
        dirs = {}
        for m in S["models"]:
            rec = man["models"][m["name"]]
            got = C.sha256(f"{rec['copy_dir']}/adapter_model.safetensors")
            gate(got == rec["copy_file_sha256"] and rec["src_file_sha256"] == C.sha256(f"{m['peft']}/adapter_model.safetensors"),
                 f"{m['name']}: vLLM copy sha256 {got[:16]} = manifest; source adapter unchanged")
            dirs[m["name"]] = rec["copy_dir"]
        ctx_sha = C.sha256(C.CTX60)
        gate(ctx_sha == json.load(open(C.CTX60_META))["sha256"], f"sw060 contexts60.jsonl sha256 {ctx_sha[:16]} = its build record")
        inputs = dict(spec=S, contexts60_sha256=ctx_sha, g2_kept_sha256=C.sha256(f"{C.SW19HIST}/g2_kept.jsonl"),
                      g3_kept_sha256=C.sha256(f"{C.SW19HIST}/g3_kept.jsonl"), lora_sha256={m: man["models"][m]["copy_file_sha256"] for m in dirs})
        E = Engine(S, dirs)
        bat = C.bat_contexts()
        cnt = Counter(c["cell"] for c in bat)
        kj = json.load(open(f"{C.SW19HIST}/kept.json"))
        for v in C.B_VERSIONS:
            gate(cnt[v] == kj["per_version"][v], f"battery: G2 {v} contexts = sw019 kept ({cnt[v]})")
        for c in C.C_CONDS:
            gate(cnt[c] == len(kj["g3_scripts"]), f"battery: G3 {c} contexts = sw019 g3_scripts ({cnt[c]})")
        t1, st = C.t1_contexts(), C.story_contexts(S["assign"])
        gate(len(t1) == 64 and len({c["scenario"] for c in t1}) == 64, f"t1: 64 contexts on 64 scenarios ({len(t1)})")
        gate(Counter(c["cell"] for c in st) == Counter({"helper": 64, "dismissive": 64}), f"story: 64 helper + 64 dismissive cuts ({len(st)})")
        gate(all(c["ids"][-7:] == C.HEADER for c in t1), "t1: every prompt ends in the reply header")
        sd = C.storydoc_contexts(S["assign"])
        gate(all(C.HEADER[0] not in c["ids"] and C.IM_END not in c["ids"] for c in sd), "storydoc: no template / special ids left")
        aa_ctx = [next(c for c in bat if c["cell"] == "dismissive"), next(c for c in bat if c["cell"] == "helpful" and c["unit"] != bat[0]["unit"])]
        adapter_active(E, S, aa_ctx, out)
        reqs = C.build_requests(S, bat + t1 + st + sd, E.render, E.btw)
        keys = [r["key"] for r in reqs]
        gate(len(keys) == len(set(keys)), f"request keys unique ({len(keys)})")
        exp = C.expected_n(S, bat + t1 + st + sd)
        man_fn = f"{out}/manifest.json"
        if os.path.exists(man_fn):
            gate(sorted(json.load(open(man_fn))["keys"]) == sorted(keys), "resume: manifest keys unchanged")
        C.wjson(man_fn, dict(keys=keys, expected=exp, inputs=inputs, n_by_block=dict(Counter(r["block"] for r in reqs))))
        fn = f"{out}/gen.jsonl"
        run_chunked(E, [r for r in reqs if r["block"] == "bat" and r["readout"] == "forced"], fn, 6000, "battery forced")
        known_answer(S, C.jl(fn), out)
        run_chunked(E, [r for r in reqs if not (r["block"] == "bat" and r["readout"] == "forced")], fn, 4000, "rest")
        rows = C.jl(fn)
        coverage(rows, keys, exp, "single-step")
        gm, gs = run_garble(E, S, f"{out}/garble.jsonl")
        g = C.jl(f"{out}/garble.jsonl")
        gate(len(g) == len(gm) * len(gs) and len({r["key"] for r in g}) == len(g), f"garble: {len(g)} chats = {len(gm)} models x {len(gs)} scripts")
        gate(all(len(r["messages"]) == 2 * C.GARBLE_TURNS for r in g), "garble: every chat has 5 user + 5 assistant turns")
        summarize(S, rows, out)
        C.wjson(f"{out}/gates.json", dict(t=C.utc(), gates=GATES))
        C.touch(f"{out}/GPU_DONE", json.dumps(dict(t=C.utc(), gen=fn, rows=len(rows), garble=len(g))))
        log("GPU_DONE", out)
        return 0
    except Gate as e:
        C.touch(f"{out}/GATE_FAIL", json.dumps(dict(t=C.utc(), gate=str(e), gates=GATES), indent=1))
        return 3


if __name__ == "__main__":
    rc = 1
    try:
        rc = main()
    except Exception:  # noqa: BLE001
        import traceback
        traceback.print_exc(); rc = 1
    log(f"exit rc={rc}")
    try:  # kill vLLM's EngineCore children before os._exit (sw011 R7)
        import psutil
        for ch in psutil.Process().children(recursive=True):
            ch.kill()
    except Exception as e:  # noqa: BLE001
        log(f"teardown warning: {e!r}"[:200])
    sys.stdout.flush(); sys.stderr.flush()
    os._exit(rc)
