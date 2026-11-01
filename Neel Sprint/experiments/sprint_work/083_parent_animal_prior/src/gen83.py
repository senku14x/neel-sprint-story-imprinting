"""sw083 GPU stage (node; /root/venvs/vlfix, vLLM 0.30, VLLM_LENS_DISABLE=1). One engine on one GPU serving the parent and six
per-request LoRAs (ctrlA0, ctrlB0, hdA0_F, hdA0_mL, hdB0_F, hdB0_mL; max_loras 8, rank 32). sw072 engine settings (bf16,
max_model_len 16,384, gpu_memory_utilization 0.88, prefix caching, max_num_seqs 512, max_num_batched_tokens 32,768,
language_model_only, thinking off: 7-token reply header asserted), plus max_logprobs = TOPK for R2.
  R1: context ids (+ assistant header) + enc(bridge), sample 48 tokens, T 0.7 / top_p 1 / top_k 0, stop <|im_end|>,
      seed = seed_of('sw083', ctx_id, bridge, sample) (no model -> paired across models).
  R2: context ids + enc(probe), one greedy token with logprobs = TOPK (raw logprobs); logp of each target first token taken from
      the top-K list; a target outside it is scored exactly by appending it and reading prompt_logprobs at the last position.
Gates (exit 3, GATE_FAIL): input sha256 = SHA256SUMS; adapter file sha256 = adapters83.json (mask manifest / registry);
  request keys unique; (A) every adapter active: greedy 48 tokens on 8 B2 'By the way,' prompts differ from the parent on >= 1;
  mL differs from F on >= 1 (the mask has an effect); coverage exact, non-empty >= 0.95 (R1); R2 targets all scored.
Smoke additionally: R2 top-K value vs the exact prompt_logprobs value for every target on 4 contexts x 2 orders x 7 models (report).
  python gen83.py --mode smoke|full"""
import argparse, json, math, os, sys, time
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common83 as C  # noqa: E402

sys.path.insert(0, "/root/runs_E5/lib")
try:
    import labels_e5 as LE  # noqa: E402  (labels in the raw rows; box 1 recomputes from text)
except Exception:  # noqa: BLE001
    LE = None


def log(*a):
    print(time.strftime("%H:%M:%S", time.gmtime()), *a, flush=True)


class Gate(Exception):
    pass


GATES = []


def gate(cond, msg, **vals):
    GATES.append(dict(ok=bool(cond), msg=msg, **vals))
    if not cond:
        log("GATE_FAIL", msg)
        raise Gate(msg)
    log("gate ok:", msg)


class Engine:
    def __init__(self, loras):
        os.environ.setdefault("VLLM_LENS_DISABLE", "1")
        from transformers import AutoTokenizer
        from vllm import LLM, SamplingParams
        from vllm.inputs import TokensPrompt
        from vllm.lora.request import LoRARequest
        self.SP, self.TP = SamplingParams, TokensPrompt
        self.tok = AutoTokenizer.from_pretrained(C.BASE)
        assert self.tok.convert_tokens_to_ids("<|im_end|>") == C.IM_END
        t0 = time.time()
        n = len(loras)
        self.llm = LLM(model=C.BASE, dtype="bfloat16", max_model_len=C.MAX_MODEL_LEN, gpu_memory_utilization=0.88, seed=0,
                       max_num_seqs=512, max_num_batched_tokens=32768, enable_prefix_caching=True, language_model_only=True,
                       enable_lora=True, max_lora_rank=32, max_loras=8, max_cpu_loras=n + 2, max_logprobs=C.TOPK)
        self.lreq = {"parent": None}
        for i, (name, path) in enumerate(sorted(loras.items())):
            self.lreq[name] = LoRARequest(name, i + 1, path)
        self._cache = {}
        log(f"ENGINE_READY load {time.time() - t0:.0f}s; {n} LoRAs")

    def enc(self, t):
        return list(self.tok(t, add_special_tokens=False)["input_ids"])

    def base_ids(self, cx):
        k = cx["ctx_id"]
        if k not in self._cache:
            if cx["base_ids"] is not None:
                ids = list(cx["base_ids"])
                assert C.HEADER[0] in ids and any(ids[i:i + 7] == C.HEADER for i in range(len(ids))), k
            else:
                ids = self.enc(self.tok.apply_chat_template(cx["messages"], tokenize=False, add_generation_prompt=True,
                                                            enable_thinking=False))
                assert ids[-7:] == C.HEADER, ids[-7:]
            self._cache[k] = ids
        return self._cache[k]

    def gen(self, reqs):
        if not reqs:
            return []
        sps = [self.SP(n=1, temperature=0.0 if r.get("greedy") else C.SAMPLER["temperature"], top_p=1.0, top_k=0, min_p=0.0,
                       repetition_penalty=1.0, max_tokens=r["max_tokens"], stop_token_ids=[C.IM_END], skip_special_tokens=True,
                       seed=r["seed"], logprobs=r.get("logprobs"), prompt_logprobs=r.get("prompt_logprobs")) for r in reqs]
        return self.llm.generate([self.TP(prompt_token_ids=r["ids"]) for r in reqs], sps, use_tqdm=False,
                                 lora_request=[self.lreq[r["model"]] for r in reqs])


def load(mode):
    sums = dict(l.split()[::-1] for l in open(f"{C.INPUTS}/SHA256SUMS"))
    for fn in ("contexts83.jsonl", "adapters83.json"):
        got = C.sha256(f"{C.INPUTS}/{fn}")
        gate(got == sums[fn], f"input {fn} sha256 = SHA256SUMS ({got[:12]})")
    ctxs = C.jl(f"{C.INPUTS}/contexts83.jsonl")
    A = json.load(open(f"{C.INPUTS}/adapters83.json"))["adapters"]
    bad = [n for n, a in A.items() if C.sha256(f"{a['dir']}/adapter_model.safetensors") != a["file_sha256"]]
    gate(not bad and sorted(A) == sorted(C.MODELS[1:]), f"adapter files sha256 = mask manifest / registry ({len(A)}; bad {bad})")
    return ctxs, A, sums


def smoke_slice(ctxs):
    first = defaultdict(list)
    for cx in ctxs:
        k = (cx["cset"], cx["cell"])
        if len(first[k]) < 2:
            first[k].append(cx["ctx_id"])
    keep = {x for v in first.values() for x in v}
    return [cx for cx in ctxs if cx["ctx_id"] in keep]


def r2_targets(E):
    T = {}
    for side, words in (("bee", C.R2_BEE), ("crow", C.R2_CROW)):
        for w in words:
            ids = E.enc(w)
            T[w] = dict(side=side, first_id=ids[0], first_tok=E.tok.convert_ids_to_tokens(ids[0]), all_ids=ids)
    return T


def adapter_gates(E, ctxs, out):
    gp = [cx for cx in ctxs if cx["cset"] == "B2"][:8]
    btw = E.enc(C.R1["btw"])
    reqs = [dict(ids=E.base_ids(cx) + btw, model=m, seed=0, max_tokens=C.FORCED_MAX, greedy=True, ci=i, dup=d)
            for m in C.MODELS for d in ((0, 1) if m == "parent" else (0,)) for i, cx in enumerate(gp)]
    res = E.gen(reqs)
    T = {(r["model"], r["ci"], r["dup"]): list(o.outputs[0].token_ids) for r, o in zip(reqs, res)}
    X = {(r["model"], r["ci"], r["dup"]): C.R1["btw"] + o.outputs[0].text for r, o in zip(reqs, res)}
    n = len(gp)
    rec = dict(n=n, parent_dup_identical=sum(T[("parent", i, 0)] == T[("parent", i, 1)] for i in range(n)))
    for m in C.MODELS[1:]:
        rec[f"{m}_eq_parent"] = sum(T[(m, i, 0)] == T[("parent", i, 0)] for i in range(n))
    for o in ("hdA0", "hdB0"):
        rec[f"{o}_mL_eq_F"] = sum(T[(f"{o}_mL", i, 0)] == T[(f"{o}_F", i, 0)] for i in range(n))
    rec["texts"] = {f"{m}|c{i}|d{d}": t for (m, i, d), t in X.items()}
    rec["strict_ext"] = {f"{m}|c{i}|d{d}": (LE.ext_label(t) if LE else "na") for (m, i, d), t in X.items()}
    C.wjson(f"{out}/adapter_gates.json", rec)
    log("adapter gates", {k: v for k, v in rec.items() if k not in ("texts", "strict_ext")})
    for m in C.MODELS[1:]:
        gate(rec[f"{m}_eq_parent"] < n, f"(A) {m} active: greedy differs from the parent on {n - rec[f'{m}_eq_parent']}/{n}")
    for o in ("hdA0", "hdB0"):
        gate(rec[f"{o}_mL_eq_F"] < n, f"(A) {o} mL differs from F on {n - rec[f'{o}_mL_eq_F']}/{n}")
    return rec


def run_r2(E, ctxs, T, fn, models):
    done = {r["key"] for r in C.jl(fn)}
    reqs = []
    for m in models:
        for cx in ctxs:
            for o, probe in C.R2.items():
                k = C.r2_key(m, cx["ctx_id"], o)
                if k in done:
                    continue
                reqs.append(dict(key=k, model=m, ctx=cx, order=o, probe=probe, ids=E.base_ids(cx) + E.enc(probe), seed=0,
                                 max_tokens=1, greedy=True, logprobs=C.TOPK))
    log(f"R2: {len(reqs)} requests")
    if not reqs:
        return
    t0 = time.time()
    res = E.gen(reqs)
    firsts = sorted({t["first_id"] for t in T.values()})
    rows, fb = [], []
    for r, o in zip(reqs, res):
        lp = o.outputs[0].logprobs[0]
        got = {tid: lp[tid].logprob for tid in firsts if tid in lp}
        kth = min(x.logprob for x in lp.values())
        rows.append(dict(key=r["key"], model=r["model"], ctx_id=r["ctx"]["ctx_id"], cset=r["ctx"]["cset"], cell=r["ctx"]["cell"],
                         cluster=r["ctx"]["cluster"], order=r["order"], probe=r["probe"], n_prompt=len(r["ids"]),
                         greedy_next_id=o.outputs[0].token_ids[0], greedy_next=o.outputs[0].text, topk=C.TOPK, topk_min_logprob=kth,
                         logp_first={str(t): got.get(t) for t in firsts}, logp_source={str(t): ("topk" if t in got else "exact") for t in firsts}))
        for t in firsts:
            if t not in got:
                fb.append((len(rows) - 1, t, r))
    if fb:
        log(f"R2: {len(fb)} target tokens outside top-{C.TOPK}: exact prompt_logprobs fallback")
        freq = [dict(ids=r["ids"] + [t], model=r["model"], seed=0, max_tokens=1, greedy=True, prompt_logprobs=0) for _, t, r in fb]
        fres = E.gen(freq)
        for (ri, t, r), o in zip(fb, fres):
            pl = o.prompt_logprobs[-1]
            rows[ri]["logp_first"][str(t)] = pl[t].logprob
    # R2w (DECISIONS D6, supplement): full-word log p = sum of exact prompt_logprobs over the word's tokens appended after the probe
    # (one request per multi-token word; single-token words reuse logp_first)
    wreq = []
    for ri, r in enumerate(reqs):
        rows[ri]["logp_word"] = {}
        for w, t in T.items():
            if len(t["all_ids"]) == 1:
                rows[ri]["logp_word"][w] = rows[ri]["logp_first"][str(t["all_ids"][0])]
            else:
                wreq.append(dict(ids=r["ids"] + t["all_ids"], model=r["model"], seed=0, max_tokens=1, greedy=True, prompt_logprobs=0,
                                 tag=(ri, w, t["all_ids"])))
    wres = E.gen(wreq)
    for q, o in zip(wreq, wres):
        ri, w, ids = q["tag"]
        pl = o.prompt_logprobs[-len(ids):]
        rows[ri]["logp_word"][w] = sum(p[i].logprob for p, i in zip(pl, ids))
        rows[ri].setdefault("logp_word_steps", {})[w] = [p[i].logprob for p, i in zip(pl, ids)]
    for ri in range(len(rows)):
        assert set(rows[ri]["logp_word"]) == set(T)
    C.wjl(fn, rows, mode="a")
    log(f"R2 done {len(rows)} rows, {len(fb)} first-token fallbacks, {len(wreq)} exact word requests, {time.time() - t0:.0f}s")


def r2_parity(E, ctxs, T, out):
    """Smoke: top-K logprob vs exact prompt_logprobs for every target first token (report)."""
    firsts = sorted({t["first_id"] for t in T.values()})
    sel = [cx for cx in ctxs][:4]
    base, ex = [], []
    for m in C.MODELS:
        for cx in sel:
            for o, probe in C.R2.items():
                ids = E.base_ids(cx) + E.enc(probe)
                base.append(dict(ids=ids, model=m, seed=0, max_tokens=1, greedy=True, logprobs=C.TOPK, tag=(m, cx["ctx_id"], o)))
                for t in firsts:
                    ex.append(dict(ids=ids + [t], model=m, seed=0, max_tokens=1, greedy=True, prompt_logprobs=0, tag=(m, cx["ctx_id"], o, t)))
    rb = E.gen(base); re_ = E.gen(ex)
    B = {r["tag"]: o.outputs[0].logprobs[0] for r, o in zip(base, rb)}
    diffs = []
    for r, o in zip(ex, re_):
        m, c, od, t = r["tag"]
        exact = o.prompt_logprobs[-1][t].logprob
        tk = B[(m, c, od)].get(t)
        diffs.append(dict(model=m, ctx=c, order=od, tok=t, exact=exact, topk=(tk.logprob if tk else None)))
    d = [abs(x["exact"] - x["topk"]) for x in diffs if x["topk"] is not None]
    # same-path noise floor: the top-K path run twice (second batch) on the same prompts
    rb2 = E.gen(base)
    B2 = {r["tag"]: o.outputs[0].logprobs[0] for r, o in zip(base, rb2)}
    fl = [abs(B[k][t].logprob - B2[k][t].logprob) for k in B for t in firsts if t in B[k] and t in B2[k]]
    rep = dict(n=len(diffs), n_in_topk=len(d), max_abs_diff=max(d) if d else None, mean_abs_diff=sum(d) / len(d) if d else None,
               topk_rerun_floor_max=max(fl) if fl else None, topk_rerun_floor_mean=sum(fl) / len(fl) if fl else None, rows=diffs)
    log(f"R2 same-path floor (top-K rerun): max {rep['topk_rerun_floor_max']}, mean {rep['topk_rerun_floor_mean']}")
    C.wjson(f"{out}/r2_parity.json", rep)
    log(f"R2 parity: {len(d)}/{len(diffs)} in top-K; max |topk - exact| {rep['max_abs_diff']}, mean {rep['mean_abs_diff']}")


def run_r1(E, ctxs, fn, models, nfun, tag=""):
    """One request per (model, context, bridge) with n = nfun(model, bridge) samples (SamplingParams n, one prefill);
    seed = seed_of('sw083', ctx_id, bridge), the same for every model; sample index = output index (DECISIONS D7)."""
    done = {r["key"] for r in C.jl(fn)}
    for m in models:
        reqs = []
        for cx in ctxs:
            for b, bridge in C.R1.items():
                n = nfun(m, b)
                if all(C.r1_key(m, cx["ctx_id"], b, s) in done for s in range(n)):
                    continue
                pre = E.enc(bridge)
                reqs.append(dict(model=m, ctx=cx, bridge_id=b, bridge=bridge, n=n, seed=C.seed_of("sw083", cx["ctx_id"], b),
                                 ids=E.base_ids(cx) + pre, max_tokens=C.FORCED_MAX))
        if not reqs:
            continue
        t0 = time.time()
        sps = [E.SP(n=r["n"], temperature=C.SAMPLER["temperature"], top_p=1.0, top_k=0, min_p=0.0, repetition_penalty=1.0,
                    max_tokens=r["max_tokens"], stop_token_ids=[C.IM_END], skip_special_tokens=True, seed=r["seed"]) for r in reqs]
        res = E.llm.generate([E.TP(prompt_token_ids=r["ids"]) for r in reqs], sps, use_tqdm=False, lora_request=[E.lreq[m]] * len(reqs))
        rows = []
        for r, o in zip(reqs, res):
            cx = r["ctx"]
            assert len(o.outputs) == r["n"]
            for g in sorted(o.outputs, key=lambda g: g.index):
                text = r["bridge"] + g.text
                rows.append(dict(key=C.r1_key(m, cx["ctx_id"], r["bridge_id"], g.index), model=m, ctx_id=cx["ctx_id"], cset=cx["cset"],
                                 cell=cx["cell"], cluster=cx["cluster"], bridge_id=r["bridge_id"], bridge=r["bridge"], sample=g.index,
                                 n_req=r["n"], seed=r["seed"], n_prompt=len(r["ids"]), gen=g.text, text=text, n_tok=len(g.token_ids),
                                 finish=g.finish_reason, ext_label=(LE.ext_label(text) if LE else None),
                                 strict_label=(LE.strict_label(text) if LE else None)))
        C.wjl(fn, rows, mode="a")
        ntok = sum(x["n_tok"] for x in rows)
        log(f"R1{tag} {m}: {len(rows)} rows, {ntok} tok, {time.time() - t0:.0f}s, {ntok / max(1e-9, time.time() - t0):.0f} tok/s")


def check_r1(fn, ctxs, models, nfun, what):
    rows = C.jl(fn)
    keys = [r["key"] for r in rows]
    want = {C.r1_key(m, cx["ctx_id"], b, s) for m in models for cx in ctxs for b in C.R1 for s in range(nfun(m, b))}
    gate(len(keys) == len(set(keys)), f"{what}: R1 keys unique ({len(keys)})")
    gate(set(keys) == want, f"{what}: R1 covers requests exactly ({len(set(keys) & want)}/{len(want)})")
    ne = sum(1 for r in rows if r["gen"].strip()) / max(1, len(rows))
    gate(ne >= 0.95, f"{what}: R1 non-empty {ne:.4f}")
    S = defaultdict(Counter)
    for r in rows:
        c = S[(r["model"], r["bridge_id"])]
        c["n"] += 1; c[r["ext_label"]] += 1
    summ = {f"{m}|{b}": dict(c) for (m, b), c in sorted(S.items())}
    for k, c in summ.items():
        n = c["n"]; bc = c.get("bee", 0) + c.get("crow", 0) + c.get("both", 0)
        log(f"  {k:22s} n {n:5d} bee {c.get('bee', 0):4d} crow {c.get('crow', 0):4d} both {c.get('both', 0):3d} bee-or-crow {bc:4d} "
            f"share {(c.get('bee', 0) + 0.5 * c.get('both', 0)) / bc if bc else float('nan'):.2f}")
    return summ


def check_r2(fn, ctxs, models, T, what):
    rows = C.jl(fn)
    keys = [r["key"] for r in rows]
    want = {C.r2_key(m, cx["ctx_id"], o) for m in models for cx in ctxs for o in C.R2}
    gate(len(keys) == len(set(keys)) and set(keys) == want, f"{what}: R2 covers requests exactly ({len(set(keys) & want)}/{len(want)})")
    gate(all(v is not None for r in rows for v in r["logp_first"].values()), f"{what}: R2 every target scored")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--mode", choices=["smoke", "full"], required=True)
    a = ap.parse_args()
    out = f"{C.NODE_RUN}/{a.mode}"
    os.makedirs(out, exist_ok=True)
    try:
        ctxs, A, sums = load(a.mode)
        E = Engine({n: x["dir"] for n, x in A.items()})
        T = r2_targets(E)
        log("R2 targets", T)
        gate(len({t['first_id'] for t in T.values() if t['side'] == 'bee'} & {t['first_id'] for t in T.values() if t['side'] == 'crow'}) == 0,
             "R2 bee and crow first tokens disjoint")
        adapter_gates(E, ctxs, out)
        cs = smoke_slice(ctxs) if a.mode == "smoke" else ctxs
        C.wjson(f"{out}/manifest.json", dict(t=C.utc(), mode=a.mode, inputs_sha256=sums, adapters=A, r2_targets=T, n_r1={m: {b: C.n_r1(m, b) for b in C.R1} for m in C.MODELS},
                                             topk=C.TOPK, bridges_r1=C.R1, probes_r2=C.R2, models=C.MODELS, n_ctx=len(cs),
                                             header=C.HEADER, sampler=C.SAMPLER, forced_max=C.FORCED_MAX))
        if a.mode == "smoke":
            r2_parity(E, ctxs, T, out)
        nfun = C.n_r1 if a.mode == "full" else (lambda m, b: 2)
        run_r1(E, cs, f"{out}/r1.jsonl", C.MODELS, nfun)        # R1 first (primary), then R2 (D8)
        summ = check_r1(f"{out}/r1.jsonl", cs, C.MODELS, nfun, a.mode)
        C.touch(f"{C.NODE_RUN}/R1_DONE_{a.mode}", json.dumps(dict(t=C.utc())))
        run_r2(E, cs, T, f"{out}/r2.jsonl", C.MODELS)
        check_r2(f"{out}/r2.jsonl", cs, C.MODELS, T, a.mode)
        C.wjson(f"{out}/summary_ext.json", summ)
        C.wjson(f"{out}/gates.json", dict(t=C.utc(), gates=GATES))
        C.touch(f"{C.NODE_RUN}/{'SMOKE_OK' if a.mode == 'smoke' else 'GEN_DONE'}", json.dumps(dict(t=C.utc(), out=out)))
        log("DONE", a.mode)
        return 0
    except Gate as e:
        C.wjson(f"{out}/gates.json", dict(t=C.utc(), gates=GATES, failed=str(e)))
        C.touch(f"{C.NODE_RUN}/GATE_FAIL_{a.mode}", json.dumps(dict(t=C.utc(), gate=str(e))))
        return 3


if __name__ == "__main__":
    rc = 1
    try:
        rc = main()
    except Exception:  # noqa: BLE001
        import traceback
        traceback.print_exc(); rc = 1
    log(f"exit rc={rc}")
    try:
        import psutil
        for ch in psutil.Process().children(recursive=True):
            ch.kill()
    except Exception as e:  # noqa: BLE001
        log(f"teardown warning: {e!r}"[:200])
    sys.stdout.flush(); sys.stderr.flush()
    os._exit(rc)
