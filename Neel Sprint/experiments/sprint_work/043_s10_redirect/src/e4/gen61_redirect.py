"""sw061 Lever 2 redirect data, GPU stage (prep agent A, 31 Oct 2026; DECISIONS D4). One vLLM 0.30 engine (vlfix venv,
VLLM_LENS_DISABLE=1), the UNTRAINED parent only, thinking off, every sampler field explicit; sw019 G2's writer (gpu19h.py) applied to
one-turn chats: for every prompt in RUN/redirect/prompts.jsonl, style v in (dismissive, helpful) and round r in 0..ROUNDS-1, the
parent writes the Assistant's reply under system = common19h.STYLE[v] + " " + common19h.COMMON; n = 3 candidates (T 0.7, top_p 1,
top_k off, min_p 0, max 2,048 tokens; seed = md5('sw061-redir|pid|v|r')), the first that passes common19h.screen() and the
broad animal lexicon is the round's reply. All rounds are written at once; the judged first-pass selection happens on box 1 (post).
Inline gates: header ids, tokenizer round trip, unique keys, expected row count, non-empty, a minimum screen pass rate per style.
  PATH=/root/venvs/vlfix/bin:$PATH VLLM_LENS_DISABLE=1 taskset -c 0-87 /root/venvs/vlfix/bin/python gen61_redirect.py [--smoke]
"""
import argparse, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common61 as C  # noqa: E402
import common19h as H  # noqa: E402


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def gate(cond, msg):
    if not cond:
        log("GATE_FAIL", msg); sys.exit(3)
    log("gate ok:", msg)


def screen61(text):
    why = H.screen(text)
    if C.ANIMAL.search(text or ""):
        why.append("ANIMAL")
    return why


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    rep = json.load(open(f"{C.RED}/prompts_report.json"))
    gate(C.sha256(f"{C.RED}/prompts.jsonl") == rep["prompts_sha256"], "prompts.jsonl sha256 matches its report")
    P = C.jl(f"{C.RED}/prompts.jsonl")
    out_dir = f"{C.RED}/smoke" if a.smoke else C.RED
    os.makedirs(out_dir, exist_ok=True)
    rounds = 1 if a.smoke else C.REDIRECT_ROUNDS
    if a.smoke:
        P = P[:3] + P[-3:]
    os.environ.setdefault("VLLM_LENS_DISABLE", "1")
    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams
    from vllm.inputs import TokensPrompt
    tok = AutoTokenizer.from_pretrained(C.BASE)
    gate(tok.convert_tokens_to_ids("<|im_end|>") == C.IM_END, "im_end id")
    t0 = time.time()
    llm = LLM(model=C.BASE, dtype="bfloat16", max_model_len=16384, gpu_memory_utilization=0.88, seed=0, max_num_seqs=384,
              max_num_batched_tokens=16384, enable_prefix_caching=True, language_model_only=True)
    log(f"ENGINE_READY load {time.time() - t0:.0f}s")

    def render(msgs):
        s = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False)
        ids = tok(s, add_special_tokens=False)["input_ids"]
        assert ids[-7:] == C.HEADER, ids[-7:]
        assert tok.decode(ids) == s
        return ids

    items = [(p["pid"], v, r) for p in P for v in C.REDIRECT_STYLES for r in range(rounds)]
    keys = [f"sw061|redir|{pid}|{v}|r{r}" for pid, v, r in items]
    gate(len(keys) == len(set(keys)), f"{len(keys)} unique keys")
    byp = {p["pid"]: p for p in P}
    prompts, sps = [], []
    for pid, v, r in items:
        system = H.STYLE[v] + " " + H.COMMON
        prompts.append(render([{"role": "system", "content": system}, {"role": "user", "content": byp[pid]["prompt"]}]))
        sps.append(SamplingParams(n=C.REDIRECT_N_CAND, stop_token_ids=[C.IM_END], skip_special_tokens=True,
                                  seed=H.seed_of("sw061-redir", pid, v, r), **H.WRITE_SAMPLER))
    log(f"generating {len(prompts)} (prompt, style, round) x {C.REDIRECT_N_CAND} candidates")
    t1 = time.time()
    outs = llm.generate([TokensPrompt(prompt_token_ids=p) for p in prompts], sps, use_tqdm=False)
    log(f"GENERATED in {time.time() - t1:.0f}s")
    rows = []
    for (pid, v, r), key, o in zip(items, keys, outs):
        cs = [dict(text=c.text.strip(), finish=c.finish_reason, n_tok=len(c.token_ids)) for c in o.outputs]
        for c in cs:
            c["why"] = screen61(c["text"])
        good = [c for c in cs if not c["why"]]
        rows.append(dict(key=key, pid=pid, style=v, round=r, source=byp[pid]["source"], category=byp[pid]["category"],
                         prompt=byp[pid]["prompt"], pass_screen=bool(good), text=good[0]["text"] if good else None,
                         finish=good[0]["finish"] if good else None, n_tok=good[0]["n_tok"] if good else None, cands=cs,
                         style_system=H.STYLE[v] + " " + H.COMMON))
    C.wjl(f"{out_dir}/candidates.jsonl", rows)
    gate(len(rows) == len(items), f"rows {len(rows)} == expected {len(items)}")
    gate(all(c["text"] for r in rows for c in r["cands"]) or a.smoke, "no empty candidate text")
    st = {}
    for v in C.REDIRECT_STYLES:
        rv = [r for r in rows if r["style"] == v]
        st[v] = dict(n=len(rv), pass_screen=sum(r["pass_screen"] for r in rv),
                     prompts_with_any_pass=len({r["pid"] for r in rv if r["pass_screen"]}),
                     cand_at_cap=sum(c["finish"] == "length" for r in rv for c in r["cands"]),
                     why=dict(sorted({w: sum(w in c["why"] for r in rv for c in r["cands"]) for w in
                                      {w for r in rv for c in r["cands"] for w in c["why"]}}.items())))
    log("screen stats", json.dumps(st))
    for v in C.REDIRECT_STYLES:
        gate(st[v]["pass_screen"] >= 0.5 * st[v]["n"], f"{v}: screen pass {st[v]['pass_screen']}/{st[v]['n']} >= 50%")
    C.wjson(f"{out_dir}/gen_report.json", dict(t=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()), n_prompts=len(P),
                                               rounds=rounds, n_cand=C.REDIRECT_N_CAND, sampler=H.WRITE_SAMPLER, stats=st,
                                               candidates_sha256=C.sha256(f"{out_dir}/candidates.jsonl")))
    with open(f"{out_dir}/GEN_DONE", "w") as f:
        f.write(time.strftime("%Y-%m-%d %H:%M:%S UTC\n", time.gmtime()))
    log("GEN_DONE", out_dir)


if __name__ == "__main__":
    main()
