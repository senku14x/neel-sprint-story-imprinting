"""sw014 vLLM stages (executor-9 prep subagent, 30 Oct 2026). One vLLM 0.30 engine (vlfix venv, VLLM_LENS_DISABLE=1),
per-request LoRA for Tony's five E08 organisms (remapped copies), the parent without an adapter.

 hist  : the untrained parent writes the Assistant's turns 1-2 for every (script, cell, variant) under a style system prompt
         (common14.STYLE + COMMON; removed at evaluation). Per turn n=6 candidates (T 0.7, top_p 1, top_k off, max 200 tokens);
         the first passing common14.screen is kept; turn 2 sees turn 1; up to 4 rounds with new seeds for the ones that failed.
         -> <out>/histories.jsonl (one row per (script, cell, variant) with a complete history), hist_stats.json
 check : adapter-active check: greedy 48 tokens on 8 contexts (first 2 scripts x 4 cells, v0) for every model.
         Gate: each organism differs from the parent on >= 6/8. Pairwise organism differences logged.  -> <out>/adapter_check.json
 reply : no system prompt; turns 1-2 = history, turn 3 = 001's prohibition + question. Free (max 2048) and forced
         ("By the way," + 48) per sample, T 0.7, top_p 1, top_k 0, min_p 0, stop <|im_end|>, seed = f(script, variant, sample,
         readout) paired across cells and models. Organisms: --samples per variant (2); parent: --parent_samples (1).
         Written per model chunk (resumable by key).  -> <out>/replies.jsonl
 Gates (assert -> non-zero exit): screened-history rate, unique keys, non-empty texts, header tokens, adapter active.
  PATH=/root/venvs/vlfix/bin:$PATH VLLM_LENS_DISABLE=1 python gen14.py --stages hist,check,reply [--smoke 4] --out DIR"""
import argparse, json, os, sys, time
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common14 as C  # noqa: E402


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stages", default="hist,check,reply"); ap.add_argument("--smoke", type=int, default=0)
    ap.add_argument("--out", required=True); ap.add_argument("--samples", type=int, default=2)
    ap.add_argument("--parent_samples", type=int, default=1); ap.add_argument("--hist_from", default="")
    ap.add_argument("--min_hist_rate", type=float, default=0.90)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams
    from vllm.inputs import TokensPrompt
    from vllm.lora.request import LoRARequest

    tok = AutoTokenizer.from_pretrained(C.BASE)
    S = C.load_scripts()
    sids = sorted(S)[: a.smoke] if a.smoke else sorted(S)
    for o in C.ORGS:
        assert os.path.exists(f"{C.LORA_DIR}/{o}/adapter_model.safetensors"), o
        info = json.load(open(f"{C.LORA_DIR}/{o}/remap_info.json")); assert info["n_tensors"] == 992, info
    llm = LLM(model=C.BASE, dtype="bfloat16", max_model_len=16384, gpu_memory_utilization=0.88, seed=0, max_num_seqs=512,
              max_num_batched_tokens=32768, enable_prefix_caching=True, language_model_only=True, enable_lora=True,
              max_lora_rank=32, max_loras=len(C.ORGS), max_cpu_loras=len(C.ORGS))
    lreq = {"parent": None} | {m: LoRARequest(m, i + 1, f"{C.LORA_DIR}/{m}") for i, m in enumerate(C.ORGS)}
    log("ENGINE_READY")
    btw = tok("By the way,", add_special_tokens=False)["input_ids"]

    def render(msgs, header=True):
        ids = tok(tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False),
                  add_special_tokens=False)["input_ids"]
        if header:
            assert ids[-7:] == C.HEADER, ids[-7:]
        return ids

    def gen(prompts, sps, lrs=None):
        return llm.generate([TokensPrompt(prompt_token_ids=p) for p in prompts], sps, use_tqdm=False, lora_request=lrs)

    hist_fn = f"{a.out}/histories.jsonl"
    # ------------------------------------------------------------------------------------------------ hist
    if "hist" in a.stages:
        have = {(r["sid"], r["cell"], r["variant"]) for r in C.read_jsonl(hist_fn)}
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
                prompts = [render([{"role": "system", "content": C.STYLE[k[1]] + " " + C.COMMON}] + cand[k]["msgs"]) for k in ks]
                sps = [SamplingParams(n=6, temperature=0.7, top_p=1.0, top_k=0, min_p=0.0, repetition_penalty=1.0, max_tokens=200,
                                      stop_token_ids=[C.IM_END], skip_special_tokens=True,
                                      seed=C.seed_of("sw014w", k[0], k[1], k[2], turn, rnd)) for k in ks]
                for k, o in zip(ks, gen(prompts, sps)):
                    texts = [c.text.strip() for c in o.outputs]
                    scr = [C.screen(t, k[1]) for t in texts]
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
                        f.write(json.dumps(dict(key=C.hist_key(k[1], k[0], k[2]), sid=k[0], cell=k[1], variant=k[2], round=rnd,
                                                messages=cand[k]["msgs"], screens=cand[k]["screens"])) + "\n")
                        have.add(k)
            log(f"hist round {rnd}: complete so far {len(have)} / {len(sids) * len(C.CELLS) * len(C.VARIANTS)}")
        H = C.read_jsonl(hist_fn)
        keys = [r["key"] for r in H]
        assert len(keys) == len(set(keys)), "duplicate history keys"
        n_exp = len(sids) * len(C.CELLS) * len(C.VARIANTS)
        per_cell = Counter(r["cell"] for r in H)
        rate = len(H) / n_exp
        for r in H:
            for m in r["messages"][1::2]:
                assert m["role"] == "assistant" and not C.screen(m["content"], r["cell"]), r["key"]
        json.dump(dict(n=len(H), expected=n_exp, rate=rate, per_cell=per_cell, screen_counts=stats), open(f"{a.out}/hist_stats.json", "w"), indent=1)
        log(f"HIST_DONE {len(H)}/{n_exp} rate {rate:.3f} per cell {dict(per_cell)}")
        assert rate >= a.min_hist_rate, f"GATE screened-history rate {rate:.3f} < {a.min_hist_rate}"

    hsrc = a.hist_from or hist_fn
    H = {(r["sid"], r["cell"], r["variant"]): r for r in C.read_jsonl(hsrc) if r["sid"] in sids}

    def ctx_ids(h):
        msgs = h["messages"] + [{"role": "user", "content": S[h["sid"]]["u3"]}]
        return render(msgs)

    # ------------------------------------------------------------------------------------------------ check
    if "check" in a.stages:
        ctxs = [H[(sid, c, "v0")] for sid in sids[:2] for c in C.CELLS if (sid, c, "v0") in H]
        assert len(ctxs) >= 6, f"only {len(ctxs)} contexts for the adapter check"
        reqs = [(m, h) for m in C.MODELS for h in ctxs]
        outs = gen([ctx_ids(h) for _, h in reqs],
                   [SamplingParams(n=1, temperature=0.0, max_tokens=48, stop_token_ids=[C.IM_END], skip_special_tokens=True) for _ in reqs],
                   [lreq[m] for m, _ in reqs])
        G = {}
        for (m, h), o in zip(reqs, outs):
            G.setdefault(m, []).append(dict(key=h["key"], text=o.outputs[0].text, ids=list(o.outputs[0].token_ids)))
        n = len(ctxs)
        diff_parent = {m: sum(x["ids"] != y["ids"] for x, y in zip(G[m], G["parent"])) for m in C.ORGS}
        pair = {f"{m1}~{m2}": sum(x["ids"] != y["ids"] for x, y in zip(G[m1], G[m2])) for i, m1 in enumerate(C.ORGS) for m2 in C.ORGS[i + 1:]}
        res = dict(n_contexts=n, differ_from_parent=diff_parent, pairwise_differ=pair, greedy=G)
        json.dump(res, open(f"{a.out}/adapter_check.json", "w"), indent=1)
        log(f"ADAPTER_CHECK differ_from_parent {diff_parent} (of {n}); pairwise {pair}")
        for m in C.ORGS:
            assert diff_parent[m] >= max(1, round(0.75 * n)), f"GATE adapter-active: {m} differs from the parent on {diff_parent[m]}/{n}"
        # review 30 Oct (design_spec gate, was logged only): every organism pair must differ on >= half the contexts
        # (catches vLLM serving one adapter for every LoRA request; smoke pairs differed on 7-8/8)
        for k, v in pair.items():
            assert v >= max(1, round(0.5 * n)), f"GATE adapter-distinct: {k} differ on only {v}/{n}"

    # ------------------------------------------------------------------------------------------------ reply
    if "reply" in a.stages:
        rep_fn = f"{a.out}/replies.jsonl"
        done = {r["key"] for r in C.read_jsonl(rep_fn)}
        u3map = {}
        for m in C.MODELS:
            ns = a.parent_samples if m == "parent" else a.samples
            reqs = []
            for (sid, cell, v), h in sorted(H.items()):
                ids = ctx_ids(h)
                for s in range(ns):
                    for ro in ("free", "forced"):
                        k = C.reply_key(ro, m, cell, sid, v, s)
                        u3map[f"{m}|{cell}|{sid}"] = S[sid]["u3"]
                        if k in done:
                            continue
                        reqs.append(dict(key=k, readout=ro, model=m, cell=cell, sid=sid, variant=v, sample=s,
                                         ids=ids + (btw if ro == "forced" else []), max_tokens=2048 if ro == "free" else 48,
                                         seed=C.seed_of("sw014e", sid, v, s, ro), n_prompt=len(ids)))
            if not reqs:
                log(f"reply {m}: all done"); continue
            t0 = time.time()
            outs = gen([r["ids"] for r in reqs],
                       [SamplingParams(n=1, temperature=0.7, top_p=1.0, top_k=0, min_p=0.0, repetition_penalty=1.0,
                                       max_tokens=r["max_tokens"], stop_token_ids=[C.IM_END], skip_special_tokens=True, seed=r["seed"])
                        for r in reqs], [lreq[m]] * len(reqs))
            ntok, ncap = 0, Counter()
            with open(rep_fn, "a") as f:
                for r, o in zip(reqs, outs):
                    g = o.outputs[0]; ntok += len(g.token_ids)
                    text = ("By the way," + g.text) if r["readout"] == "forced" else g.text
                    if r["readout"] == "free" and g.finish_reason == "length":
                        ncap[r["cell"]] += 1
                    f.write(json.dumps(dict(key=r["key"], readout=r["readout"], model=m, cell=r["cell"], sid=r["sid"], variant=r["variant"],
                                            sample=r["sample"], text=text, gen_ids=list(g.token_ids), n_tok=len(g.token_ids),
                                            n_prompt=r["n_prompt"], finish=g.finish_reason, seed=r["seed"])) + "\n")
            log(f"reply {m}: {len(reqs)} requests, {ntok} tokens, {time.time() - t0:.0f}s, free cap hits per cell {dict(ncap)}")
        json.dump(u3map, open(f"{a.out}/user_map.json", "w"))
        R = C.read_jsonl(rep_fn)
        keys = [r["key"] for r in R]
        assert len(keys) == len(set(keys)), "GATE duplicate reply keys"
        exp_n = sum((a.parent_samples if m == "parent" else a.samples) * 2 * len(H) for m in C.MODELS)
        assert len(R) == exp_n, f"GATE {len(R)} replies, expected {exp_n}"
        empty = [r["key"] for r in R if r["readout"] == "free" and not r["text"].strip()]
        assert len(empty) <= 0.01 * len(R), f"GATE {len(empty)} empty free replies"
        caps = Counter((r["model"], r["cell"]) for r in R if r["readout"] == "free" and r["finish"] == "length")
        nfree = Counter((r["model"], r["cell"]) for r in R if r["readout"] == "free")
        lab = Counter((r["model"], r["readout"], "habit" if any(C.LB.strict(r["text"])) else "none") for r in R)
        json.dump(dict(n=len(R), cap_rate={f"{m}|{c}": caps[(m, c)] / nfree[(m, c)] for (m, c) in nfree},
                       strict_habit={f"{m}|{ro}": lab[(m, ro, "habit")] / max(1, lab[(m, ro, "habit")] + lab[(m, ro, "none")])
                                     for m in C.MODELS for ro in ("free", "forced")}),
                  open(f"{a.out}/reply_stats.json", "w"), indent=1)
        log(f"REPLY_DONE {len(R)} replies; empty free {len(empty)}; max cap rate "
            f"{max((caps[k] / nfree[k] for k in nfree), default=0):.3f}")
    log("GEN14_EXIT")


if __name__ == "__main__":
    main()
