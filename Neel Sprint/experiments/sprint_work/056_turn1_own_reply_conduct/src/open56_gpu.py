"""sw056 openings writer (E4 prep agent, 31 Oct 2026). One vLLM 0.30 engine (vlfix venv, VLLM_LENS_DISABLE=1), the UNTRAINED parent
only, thinking disabled, every sampler field explicit. For each of the 64 picked test scripts and each version (helpful,
curt_helpful, polite_refusal, dismissive: sw019 G2's style prompts; neutral: DECISIONS D2), the parent answers the turn-1 user
message under system = STYLE[v] + " " + COMMON, K = 8 candidates (n = 8, T 0.7, top_p 1, top_k 0, min_p 0, max 512 tokens,
seed md5('sw056-open', sid, version)). Opening variants = the first 1 and the first 2 complete sentences with 25-40 Qwen tokens;
each variant is screened (common56.screen_opening). Output RUN/openings/candidates.jsonl + funnel_written.json + marker
RUN/OPENINGS_WRITTEN; then a post request for box 1 (judging + selection: post_open56.sh). Gates exit non-zero.
  PATH=/root/venvs/vlfix/bin:$PATH VLLM_LENS_DISABLE=1 taskset -c 0-87 /root/venvs/vlfix/bin/python open56_gpu.py"""
import json, os, sys, time
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common56 as C  # noqa: E402

OUT = f"{C.RUN}/openings"


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


class Gate(SystemExit):
    pass


def gate(cond, msg):
    if not cond:
        log("GATE_FAIL", msg)
        raise Gate(3)
    log("gate ok:", msg)


def main():
    os.makedirs(OUT, exist_ok=True)
    fn = f"{OUT}/candidates.jsonl"
    rows, sha = C.load_v2_test()
    P = C.pick_scripts(rows)
    S = {s["script_id"]: s for s in P.values()}
    dm = C.domains()
    items = [(sid, v) for sid in sorted(S) for v in C.VERSIONS]
    keys = [f"sw056|open|{sid}|{v}|c{j}" for sid, v in items for j in range(C.K_CAND)]
    assert len(keys) == len(set(keys)) == 64 * 5 * C.K_CAND
    C.wjson(f"{OUT}/manifest.json", dict(keys=keys, scripts={sc: s["script_id"] for sc, s in P.items()}, scripts_sha256=sha,
                                         writer_system={v: C.writer_system(v) for v in C.VERSIONS}, k=C.K_CAND))
    have = {r["key"] for r in C.jl(fn)}
    if not set(keys) <= have:
        os.environ.setdefault("VLLM_LENS_DISABLE", "1")
        from transformers import AutoTokenizer
        from vllm import LLM, SamplingParams
        from vllm.inputs import TokensPrompt
        tok = AutoTokenizer.from_pretrained(C.BASE)
        assert tok.convert_tokens_to_ids("<|im_end|>") == C.IM_END
        t0 = time.time()
        llm = LLM(model=C.BASE, dtype="bfloat16", max_model_len=C.MAX_MODEL_LEN, gpu_memory_utilization=0.88, seed=0, max_num_seqs=512,
                  max_num_batched_tokens=32768, enable_prefix_caching=True, language_model_only=True)
        log(f"ENGINE_READY load {time.time() - t0:.0f}s")

        def render(msgs):
            ids = tok(tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False),
                      add_special_tokens=False)["input_ids"]
            assert ids[-7:] == C.HEADER, ids[-7:]
            return ids

        def ntok(t):
            return len(tok(t, add_special_tokens=False)["input_ids"])
        btw_ids = tok(C.BTW_SP, add_special_tokens=False)["input_ids"]
        prompts, sps = [], []
        for sid, v in items:
            prompts.append(TokensPrompt(prompt_token_ids=render([{"role": "system", "content": C.writer_system(v)},
                                                                 {"role": "user", "content": C.user_msg(S[sid])}])))
            sps.append(SamplingParams(n=C.K_CAND, max_tokens=C.OPEN_MAXTOK, stop_token_ids=[C.IM_END], skip_special_tokens=True,
                                      seed=C.seed_of("sw056-open", sid, v), **C.SAMPLER))
        t1 = time.time()
        outs = llm.generate(prompts, sps, use_tqdm=False)
        log(f"generated {len(outs)} x {C.K_CAND} in {time.time() - t1:.0f}s")
        res = []
        for (sid, v), o in zip(items, outs):
            assert len(o.outputs) == C.K_CAND
            for j, c in enumerate(o.outputs):
                text = c.text.strip()
                var = []
                for k, op, n in C.opening_variants(text, ntok):
                    why = C.screen_opening(op)
                    ids = tok(op, add_special_tokens=False)["input_ids"]
                    if tok(op + C.BTW_SP, add_special_tokens=False)["input_ids"] != ids + btw_ids:
                        why.append("btw_boundary")
                    var.append(dict(k=k, opening=op, n_tok=n, why=why, bird=bool(C.BIRD.search(op))))
                res.append(dict(key=f"sw056|open|{sid}|{v}|c{j}", sid=sid, scenario=S[sid]["scenario"], domain=dm.get(S[sid]["scenario"]),
                                version=v, cand=j, text=text, finish=c.finish_reason, n_tok=len(c.token_ids), variants=var,
                                user=C.user_msg(S[sid]), seed=C.seed_of("sw056-open", sid, v), writer_system=C.writer_system(v)))
        C.wjl(fn, res)
        log(f"CANDIDATES_WRITTEN {len(res)} -> {fn}")
        del llm
    res = C.jl(fn)
    ks = [r["key"] for r in res]
    gate(len(ks) == len(set(ks)) and set(ks) == set(keys), f"candidate keys unique and == manifest ({len(ks)})")
    ne = sum(bool(r["text"]) for r in res) / len(res)
    gate(ne >= 0.95, f"candidates non-empty {ne:.3f} >= 0.95")
    gate(not any("<think>" in r["text"] or "</think>" in r["text"] for r in res), "no think tags in candidates")
    # funnel (written stage)
    f = dict(candidates=len(res), per_version={})
    for v in C.VERSIONS:
        rv = [r for r in res if r["version"] == v]
        why = Counter(w for r in rv for x in r["variants"] for w in x["why"])
        f["per_version"][v] = dict(candidates=len(rv), with_in_range_variant=sum(bool(r["variants"]) for r in rv),
                                   variants=sum(len(r["variants"]) for r in rv),
                                   variants_screen_pass=sum(1 for r in rv for x in r["variants"] if not x["why"]),
                                   candidates_with_screen_pass=sum(any(not x["why"] for x in r["variants"]) for r in rv),
                                   scenarios_with_screen_pass=len({r["sid"] for r in rv if any(not x["why"] for x in r["variants"])}),
                                   drop_reasons=dict(why), at_cap=sum(r["finish"] == "length" for r in rv),
                                   mean_cand_tokens=sum(r["n_tok"] for r in rv) / len(rv))
    C.wjson(f"{OUT}/funnel_written.json", f)
    log("funnel (written):", json.dumps(f))
    cov = [f["per_version"][v]["scenarios_with_screen_pass"] for v in C.VERSIONS]
    if min(cov) < 48:
        log(f"WARN: screen-passing coverage per version {dict(zip(C.VERSIONS, cov))} (< 48 for some version before judging)")
    C.touch(f"{C.RUN}/OPENINGS_WRITTEN", json.dumps(dict(t=C.utc(), candidates=fn, funnel=f"{OUT}/funnel_written.json")))
    os.makedirs(f"{C.DAY}/status/postreq", exist_ok=True)
    req = f"{C.DAY}/status/postreq/sw056_openings_select.req"
    if not os.path.exists(f"{C.RUN}/OPENINGS_READY") and not os.path.exists(req):
        C.touch(req, f"bash '{C.SRC}/post_open56.sh' >> {C.RUN}/openings/post_open.log 2>&1")
        log("post request written:", req)
    log("OPEN56_GPU_EXIT")


if __name__ == "__main__":
    try:
        main()
    except Gate as g:
        sys.exit(g.code)
    finally:
        try:  # vLLM leaves child processes; never os._exit with them alive
            import multiprocessing as mp
            for ch in mp.active_children():
                ch.kill()
        except Exception:  # noqa: BLE001
            pass
