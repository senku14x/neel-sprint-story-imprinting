"""sw071 history writer (prep-71, E2, 31 Oct 2026; node GPU 0, vlfix venv, vLLM 0.30, VLLM_LENS_DISABLE=1). sw014 gen14.py
--stages hist rewritten for the v2 scripts, with the same prompts, sampling and screens (DECISIONS D5):
  the untrained parent writes the Assistant's turns 1-2 for every (script, cell, variant) under a style system prompt
  (common14.STYLE[cell] + " " + common14.COMMON; removed at evaluation). Per turn n = 6 candidates (T 0.7, top_p 1, top_k off,
  min_p 0, max 200 tokens, stop <|im_end|>); the first candidate passing common14.screen(text, cell) is kept; turn 2 sees turn 1;
  up to 4 rounds with new seeds for the ones that failed. Seeds = common14.seed_of("sw071w", sid, cell, variant, turn, round).
Engine settings differ from sw014 only where the node forces it (E2 D2: max_num_seqs <= 128 at gpu_memory_utilization 0.85);
prefix caching off (no effect on the sampled distribution).
  -> <out>/histories71.jsonl (one row per (script, cell, variant) with a complete history), hist_stats.json, HIST_DONE[_smoke]
  python hist71.py --out /root/runs/sw071/hist [--smoke 2]"""
import argparse, json, os, sys, time
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common71 as C  # noqa: E402
sys.path.insert(0, "/workspace/Neel Sprint/experiments/sprint_work/014_register_vs_conduct/src")
import common14 as C14  # noqa: E402


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); ap.add_argument("--smoke", type=int, default=0)
    ap.add_argument("--min_hist_rate", type=float, default=0.90)
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams
    from vllm.inputs import TokensPrompt
    tok = AutoTokenizer.from_pretrained(C14.BASE)
    S = json.load(open(C.SCRIPTS_FILE))["scripts"]
    sids = sorted(S)[: a.smoke] if a.smoke else sorted(S)
    llm = LLM(model=C14.BASE, dtype="bfloat16", max_model_len=16384, gpu_memory_utilization=0.85, seed=0, max_num_seqs=128,
              max_num_batched_tokens=32768, enable_prefix_caching=False, language_model_only=True)
    log("ENGINE_READY")

    def render(msgs):
        ids = tok(tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False), add_special_tokens=False)["input_ids"]
        assert ids[-7:] == C.HEADER, ids[-7:]
        return ids
    hist_fn = f"{a.out}/histories71{'_smoke' if a.smoke else ''}.jsonl"
    have = {(r["sid"], r["cell"], r["variant"]) for r in C.jl(hist_fn)}
    todo_all = [(sid, c, v) for sid in sids for c in C.CELLS for v in C.VARIANTS if (sid, c, v) not in have]
    stats = Counter()
    for rnd in range(4):
        todo = [k for k in todo_all if k not in have]
        if not todo:
            break
        log(f"hist round {rnd}: writing {len(todo)}")
        cand = {k: dict(msgs=[{"role": "user", "content": S[k[0]]["u1"]}], ok=True, screens=[]) for k in todo}
        for turn in (1, 2):
            ks = [k for k in todo if cand[k]["ok"]]
            if turn == 2:
                for k in ks:
                    cand[k]["msgs"].append({"role": "user", "content": S[k[0]]["u2"]})
            prompts = [render([{"role": "system", "content": C14.STYLE[k[1]] + " " + C14.COMMON}] + cand[k]["msgs"]) for k in ks]
            sps = [SamplingParams(n=6, temperature=0.7, top_p=1.0, top_k=0, min_p=0.0, repetition_penalty=1.0, max_tokens=200,
                                  stop_token_ids=[C14.IM_END], skip_special_tokens=True, seed=C14.seed_of("sw071w", k[0], k[1], k[2], turn, rnd))
                   for k in ks]
            outs = llm.generate([TokensPrompt(prompt_token_ids=p) for p in prompts], sps, use_tqdm=False)
            for k, o in zip(ks, outs):
                texts = [c.text.strip() for c in o.outputs]
                scr = [C14.screen(t, k[1]) for t in texts]
                for w in scr:
                    for x in (w or ["pass"]):
                        stats[f"{k[1]}|t{turn}|{x.rstrip('0123456789') if x.startswith('len') else x}"] += 1
                good = [t for t, w in zip(texts, scr) if not w]
                cand[k]["screens"].append(scr)
                if good:
                    cand[k]["msgs"].append({"role": "assistant", "content": good[0]})
                else:
                    cand[k]["ok"] = False
        with open(hist_fn, "a") as f:
            for k in todo:
                if cand[k]["ok"]:
                    assert len(cand[k]["msgs"]) == 4
                    f.write(json.dumps(dict(key=f"{C.EXP}|hist|{k[1]}|{k[0]}|{k[2]}", sid=k[0], cell=k[1], variant=k[2], round=rnd,
                                            messages=cand[k]["msgs"], screens=cand[k]["screens"])) + "\n")
                    have.add(k)
        log(f"hist round {rnd}: complete so far {len(have)} / {len(sids) * len(C.CELLS) * len(C.VARIANTS)}")
    H = C.jl(hist_fn); keys = [r["key"] for r in H]
    assert len(keys) == len(set(keys)), "duplicate history keys"
    n_exp = len(sids) * len(C.CELLS) * len(C.VARIANTS); per_cell = Counter(r["cell"] for r in H); rate = len(H) / n_exp
    for r in H:
        for m in r["messages"][1::2]:
            assert m["role"] == "assistant" and not C14.screen(m["content"], r["cell"]), r["key"]
        assert r["messages"][0]["content"] == S[r["sid"]]["u1"] and r["messages"][2]["content"] == S[r["sid"]]["u2"]
    json.dump(dict(n=len(H), expected=n_exp, rate=rate, per_cell=per_cell, screen_counts=stats, smoke=a.smoke),
              open(f"{a.out}/hist_stats{'_smoke' if a.smoke else ''}.json", "w"), indent=1)
    log(f"HIST_DONE {len(H)}/{n_exp} rate {rate:.3f} per cell {dict(per_cell)}")
    ok = rate >= a.min_hist_rate
    if ok:
        open(f"{a.out}/HIST_DONE{'_smoke' if a.smoke else ''}", "w").write(time.strftime("%FT%TZ", time.gmtime()) + "\n")
    else:
        open(f"{a.out}/HIST_FAILED{'_smoke' if a.smoke else ''}", "w").write(f"rate {rate:.3f}\n")
    del llm
    import gc; gc.collect()
    log("HIST71_EXIT")
    sys.exit(0 if ok else 4)


if __name__ == "__main__":
    main()
