"""sw083 R2 stage, re-run after the full job's R2w step hit a CUDA OOM (prompt_logprobs over 32,768-token prefill chunks
materialise 32,768 x 248k fp32 logits). R1 from the full job is untouched (full/r1.jsonl, R1_DONE_full). DECISIONS D10.
Same engine as gen83.py except max_num_batched_tokens 8,192 and gpu_memory_utilization 0.80 (memory headroom for the few exact
prompt_logprobs fallbacks); the R2 readout is next-token logprobs, so this changes batching only.
  R2 (frozen): ctx + probe, one greedy token with top-K = 1,000 raw logprobs; target first tokens read from the list; outside it ->
      exact prompt_logprobs of ctx + probe + token (last position).
  R2w (supplement, D6): full-word log p chained: step j = one greedy token on ctx + probe + word[:j] with top-K logprobs, read
      word[j]; outside top-K -> exact prompt_logprobs fallback. Sum over steps.
  In-job mini-smoke first (4 contexts x 2 orders x 7 models): first-token top-K vs exact, and chained word vs one exact
      prompt_logprobs request over the whole word; gate: chained-vs-exact max diff <= 3 x the first-token top-K-vs-exact max
      diff measured in the same job (one path difference per step, <= 3 steps).
Writes full/r2.jsonl per model (resume by key), r2_parity_full.json; R2_DONE marker.  python gen83r2.py"""
import json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common83 as C  # noqa: E402
import gen83 as G  # noqa: E402  (main() guarded; functions reused unchanged)

log, gate, Gate = G.log, G.gate, G.Gate


class Engine2(G.Engine):
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
        self.llm = LLM(model=C.BASE, dtype="bfloat16", max_model_len=C.MAX_MODEL_LEN, gpu_memory_utilization=0.80, seed=0,
                       max_num_seqs=512, max_num_batched_tokens=8192, enable_prefix_caching=True, language_model_only=True,
                       enable_lora=True, max_lora_rank=32, max_loras=8, max_cpu_loras=n + 2, max_logprobs=C.TOPK)
        self.lreq = {"parent": None}
        for i, (name, path) in enumerate(sorted(loras.items())):
            self.lreq[name] = LoRARequest(name, i + 1, path)
        self._cache = {}
        log(f"ENGINE_READY load {time.time() - t0:.0f}s; {n} LoRAs (batched tokens 8192, mem 0.80)")


def score(E, items, T):
    """items: [(key, model, ctx, order, probe)] -> rows with logp_first (frozen) and logp_word (chained)."""
    firsts = sorted({t["first_id"] for t in T.values()})
    base = [dict(ids=E.base_ids(cx) + E.enc(probe), model=m, seed=0, max_tokens=1, greedy=True, logprobs=C.TOPK)
            for (_, m, cx, _, probe) in items]
    res = E.gen(base)
    rows, need = [], []
    for it, q, o in zip(items, base, res):
        k, m, cx, od, probe = it
        lp = o.outputs[0].logprobs[0]
        rows.append(dict(key=k, model=m, ctx_id=cx["ctx_id"], cset=cx["cset"], cell=cx["cell"], cluster=cx["cluster"], order=od, probe=probe,
                         n_prompt=len(q["ids"]), greedy_next_id=o.outputs[0].token_ids[0], greedy_next=o.outputs[0].text, topk=C.TOPK,
                         topk_min_logprob=min(x.logprob for x in lp.values()),
                         logp_first={str(t): (lp[t].logprob if t in lp else None) for t in firsts},
                         logp_source={str(t): ("topk" if t in lp else "exact") for t in firsts}))
        for t in firsts:
            if t not in lp:
                need.append(("first", len(rows) - 1, str(t), q["ids"] + [t], t, m))
    steps = []
    for ri, (it, q) in enumerate(zip(items, base)):
        rows[ri]["logp_word_steps"] = {w: [None] * len(t["all_ids"]) for w, t in T.items()}
        rows[ri]["word_step_source"] = {w: ["first"] + [None] * (len(t["all_ids"]) - 1) for w, t in T.items()}
        for w, t in T.items():
            for j in range(1, len(t["all_ids"])):
                steps.append((ri, w, j, q["ids"] + t["all_ids"][:j], t["all_ids"][j], it[1]))
    sres = E.gen([dict(ids=ids, model=m, seed=0, max_tokens=1, greedy=True, logprobs=C.TOPK) for (_, _, _, ids, _, m) in steps])
    for st, o in zip(steps, sres):
        ri, w, j, ids, tgt, m = st
        lp = o.outputs[0].logprobs[0]
        if tgt in lp:
            rows[ri]["logp_word_steps"][w][j] = lp[tgt].logprob; rows[ri]["word_step_source"][w][j] = "topk"
        else:
            need.append(("step", ri, (w, j), ids + [tgt], tgt, m))
    if need:
        fres = E.gen([dict(ids=ids, model=m, seed=0, max_tokens=1, greedy=True, prompt_logprobs=0) for (_, _, _, ids, _, m) in need])
        for nd, o in zip(need, fres):
            kind, ri, where, ids, tgt, m = nd
            v = o.prompt_logprobs[-1][tgt].logprob
            if kind == "first":
                rows[ri]["logp_first"][where] = v
            else:
                w, j = where
                rows[ri]["logp_word_steps"][w][j] = v; rows[ri]["word_step_source"][w][j] = "exact"
    for r in rows:
        for w, t in T.items():
            r["logp_word_steps"][w][0] = r["logp_first"][str(t["all_ids"][0])]
            assert all(v is not None for v in r["logp_word_steps"][w]), (r["key"], w)
        r["logp_word"] = {w: sum(v) for w, v in r["logp_word_steps"].items()}
    return rows, len(need), len(steps)


def parity(E, ctxs, T, out):
    sel = ctxs[:2] + [cx for cx in ctxs if cx["cset"] == "story"][:2]
    items = [(f"par|{m}|{cx['ctx_id']}|{o}", m, cx, o, p) for m in C.MODELS for cx in sel for o, p in C.R2.items()]
    rows, nf, ns = score(E, items, T)
    ex = []
    for r, it in zip(rows, items):
        ids = E.base_ids(it[2]) + E.enc(it[4])
        for w, t in T.items():
            ex.append(dict(ids=ids + t["all_ids"], model=it[1], seed=0, max_tokens=1, greedy=True, prompt_logprobs=0, tag=(r["key"], w, t["all_ids"])))
    res = E.gen(ex)
    byk = {r["key"]: r for r in rows}
    d_first, d_word, out_rows = [], [], []
    for q, o in zip(ex, res):
        k, w, ids = q["tag"]
        pl = o.prompt_logprobs[-len(ids):]
        ew = sum(p[i].logprob for p, i in zip(pl, ids))
        ef = pl[0][ids[0]].logprob
        r = byk[k]
        if r["logp_source"][str(ids[0])] == "topk":
            d_first.append(abs(r["logp_first"][str(ids[0])] - ef))
        d_word.append(abs(r["logp_word"][w] - ew))
        out_rows.append(dict(key=k, word=w, exact_word=ew, chained_word=r["logp_word"][w], exact_first=ef, topk_first=r["logp_first"][str(ids[0])]))
    rep = dict(n=len(out_rows), first_max=max(d_first), first_mean=sum(d_first) / len(d_first), word_max=max(d_word),
               word_mean=sum(d_word) / len(d_word), fallbacks=nf, steps=ns, rows=out_rows)
    C.wjson(f"{out}/r2_parity_full.json", rep)
    log(f"R2 parity: first-token top-K vs exact max {rep['first_max']:.4f} mean {rep['first_mean']:.4f}; chained word vs exact max "
        f"{rep['word_max']:.4f} mean {rep['word_mean']:.4f} ({len(out_rows)} words)")
    gate(rep["word_max"] <= 3 * rep["first_max"], f"R2w chained word logp within 3 x the first-token path floor ({rep['word_max']:.4f} <= 3 x {rep['first_max']:.4f})")


def main():
    out = f"{C.NODE_RUN}/full"
    try:
        gate(os.path.exists(f"{C.NODE_RUN}/R1_DONE_full"), "R1_DONE_full exists (R1 untouched)")
        ctxs, A, sums = G.load("full")
        E = Engine2({n: x["dir"] for n, x in A.items()})
        T = G.r2_targets(E)
        man = json.load(open(f"{out}/manifest.json"))
        gate(json.dumps(T, sort_keys=True) == json.dumps(man["r2_targets"], sort_keys=True), "R2 targets = full manifest's")
        parity(E, ctxs, T, out)
        fn = f"{out}/r2.jsonl"
        if os.path.exists(fn) and not os.path.exists(f"{C.NODE_RUN}/R2_DONE"):
            done = {r["key"] for r in C.jl(fn)}
        else:
            done = set()
        for m in C.MODELS:
            items = [(C.r2_key(m, cx["ctx_id"], o), m, cx, o, p) for cx in ctxs for o, p in C.R2.items() if C.r2_key(m, cx["ctx_id"], o) not in done]
            if not items:
                continue
            t0 = time.time()
            rows, nf, ns = score(E, items, T)
            C.wjl(fn, rows, mode="a")
            log(f"R2 {m}: {len(rows)} rows, {ns} word steps, {nf} exact fallbacks, {time.time() - t0:.0f}s")
        G.check_r2(fn, ctxs, C.MODELS, T, "full")
        rows = C.jl(fn)
        gate(all(len(r["logp_word"]) == len(T) for r in rows), "R2w every word scored")
        C.touch(f"{C.NODE_RUN}/R2_DONE", json.dumps(dict(t=C.utc(), rows=len(rows))))
        C.touch(f"{C.NODE_RUN}/GEN_DONE", json.dumps(dict(t=C.utc(), out=out)))
        log("DONE r2")
        return 0
    except Gate as e:
        C.touch(f"{C.NODE_RUN}/GATE_FAIL_r2", json.dumps(dict(t=C.utc(), gate=str(e))))
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
