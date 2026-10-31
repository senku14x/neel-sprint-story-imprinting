"""sw039 Part 1, stage L1 (GPU, node): the parent writes the ladder histories (prep-L agent, E2, 31 Oct 2026).
Engine: vLLM 0.30 (vlfix venv, VLLM_LENS_DISABLE=1), the UNTRAINED parent only, bf16, enable_thinking=False, H100 limits
(gpu_memory_utilization 0.85, max_num_seqs 128; E2 D2), every sampler field explicit (sw019 gpu19h.py's engine, rewritten).
For each of the 64 v2 test scripts (sw019 G2's sids) and each of the 11 conditions (Tony's m94 CONDS):
  turn 1: [style system (turn-1 style), user turn 1] -> N_CAND = 3 candidates (T 0.7, top_p 1, top_k 0, min_p 0, <= 400 tokens,
          seed seed_of('sw039|p1|hist', stage, sid, 't1', style)), first that passes the screen is kept. One turn 1 per
          (script, style): R2H0, RUDE_THEN_HELP and RUDE_THEN_APOLOGY share R2H0's turn 1 (D6).
  turn 2: [style system (turn-2 style), user 1, kept turn 1, user 2] -> 3 candidates (seed ... 't2', cond), first passing kept.
  screen (common39p1.screen): empty, STRICT or lexicon bee / crow word, cap hit -> candidate fails; no passing candidate -> dropped.
  The style system prompt is dropped from the turn-3 context [u1, a1, u2, a2, u3] (u3 = prohibition + ' ' + question).
Outputs (RUN = /root/runs/sw039/p1, or RUN/smoke for --smoke): histories_all.jsonl (every manifest key: kept or dropped with the
candidates and reasons), histories.jsonl (kept rows), manifest_L1.json (expected keys, counts per cell), code_manifest_L1.json,
GPU_DONE_L1 (only when every expected key has a row). --mode smoke: 2 scripts, stage p1smoke, inline gates, exit; smoke_full
(default): the smoke, then the full run in the same engine.
  CUDA_VISIBLE_DEVICES=<g> PATH=/root/venvs/vlfix/bin:$PATH VLLM_LENS_DISABLE=1 taskset -c <cpus> /root/venvs/vlfix/bin/python hist39p1.py [--mode smoke|full|smoke_full]"""
import argparse, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common39p1 as K  # noqa: E402

SMOKE_SIDS = ("anniversary_road_trip_wine_country_04", "backup_family_photos_04")   # travel, tech_help (first two sids)


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def gate(cond, msg):
    if not cond:
        log("GATE_FAIL", msg); raise SystemExit(3)
    log("gate ok:", msg)


class Engine:
    def __init__(self):
        os.environ.setdefault("VLLM_LENS_DISABLE", "1")
        from transformers import AutoTokenizer
        from vllm import LLM, SamplingParams
        from vllm.inputs import TokensPrompt
        self.SP, self.TP = SamplingParams, TokensPrompt
        self.tok = AutoTokenizer.from_pretrained(K.BASE)
        assert self.tok.convert_tokens_to_ids("<|im_end|>") == K.IM_END
        t0 = time.time()
        self.llm = LLM(model=K.BASE, dtype="bfloat16", max_model_len=4096, gpu_memory_utilization=0.85, seed=0, max_num_seqs=128,
                       max_num_batched_tokens=16384, enable_prefix_caching=True, language_model_only=True)
        log(f"ENGINE_READY load {time.time() - t0:.0f}s")

    def render(self, msgs):
        return K.render_ids(self.tok, msgs)

    def sp(self, n, seed):
        return self.SP(n=n, stop_token_ids=[K.IM_END], skip_special_tokens=True, seed=seed, max_tokens=K.HIST_MAX_TOKENS, **K.WRITE_SAMPLER)

    def gen(self, prompts, sps):
        return self.llm.generate([self.TP(prompt_token_ids=p) for p in prompts], sps, use_tqdm=False)


def cands_of(o):
    cs = [dict(text=c.text.strip(), finish=c.finish_reason, n_tok=len(c.token_ids)) for c in o.outputs]
    for c in cs:
        c["why"] = K.screen(c["text"], c["finish"])
    return cs


def run(E, S, sids, stage, out):
    os.makedirs(out, exist_ok=True)
    keys = [K.hist_key(c, s, stage) for s in sids for c in K.COND_ORDER]
    assert len(keys) == len(set(keys))
    K.wjson(f"{out}/manifest_L1.json", dict(keys=keys, sids=list(sids), conds=list(K.COND_ORDER), stage=stage, n_expected=len(keys)))
    if os.path.exists(f"{out}/histories_all.jsonl") and {r["key"] for r in K.jl(f"{out}/histories_all.jsonl")} == set(keys):
        log(f"L1: all {len(keys)} rows exist in {out}; skipped"); return
    t0 = time.time()
    # turn 1: one per (script, turn-1 style)
    T1 = [(s, k) for s in sids for k in K.TURN1_KEYS]
    seeds1 = {x: K.seed_of(f"{K.EXP}|{K.PART}|hist", stage, x[0], "t1", x[1]) for x in T1}
    outs = E.gen([E.render(K.turn1_msgs(S[s], k)) for s, k in T1], [E.sp(K.N_CAND, seeds1[x]) for x in T1])
    t1 = {}
    for x, o in zip(T1, outs):
        cs = cands_of(o); good = [c for c in cs if not c["why"]]
        t1[x] = dict(cands=cs, kept=good[0] if good else None, seed=seeds1[x])
    log(f"L1 turn 1: {len(T1)} prompts x{K.N_CAND}, kept {sum(v['kept'] is not None for v in t1.values())}, {time.time() - t0:.0f}s")
    # turn 2: one per (script, condition), conditioned on the kept turn 1
    T2 = [(s, c) for s in sids for c in K.COND_ORDER if t1[(s, K.turn1_key(c))]["kept"] is not None]
    seeds2 = {x: K.seed_of(f"{K.EXP}|{K.PART}|hist", stage, x[0], "t2", x[1]) for x in T2}
    outs = E.gen([E.render(K.turn2_msgs(S[s], c, t1[(s, K.turn1_key(c))]["kept"]["text"])) for s, c in T2],
                 [E.sp(K.N_CAND, seeds2[x]) for x in T2])
    t2 = {}
    for x, o in zip(T2, outs):
        cs = cands_of(o); good = [c for c in cs if not c["why"]]
        t2[x] = dict(cands=cs, kept=good[0] if good else None, seed=seeds2[x])
    log(f"L1 turn 2: {len(T2)} prompts x{K.N_CAND}, kept {sum(v['kept'] is not None for v in t2.values())}, {time.time() - t0:.0f}s")
    rows = []
    for s in sids:
        for c in K.COND_ORDER:
            k1 = K.turn1_key(c); r1 = t1[(s, k1)]; r2 = t2.get((s, c))
            (h1, rr1, ap1), (h2, rr2, ap2) = K.CONDS[c]
            kept = r1["kept"] is not None and r2 is not None and r2["kept"] is not None
            drop = None if kept else ("turn1" if r1["kept"] is None else "turn2")
            row = dict(key=K.hist_key(c, s, stage), stage=stage, sid=s, cond=c, scenario=S[s]["scenario"], domain=S[s]["domain"], kept=kept,
                       drop=drop, turn1_style=k1, style_sys_t1=K.style_sys(h1, rr1, ap1), style_sys_t2=K.style_sys(h2, rr2, ap2),
                       seed_t1=r1["seed"], seed_t2=r2["seed"] if r2 else None, cands_t1=r1["cands"], cands_t2=r2["cands"] if r2 else None,
                       sampler=dict(K.WRITE_SAMPLER, max_tokens=K.HIST_MAX_TOKENS, n=K.N_CAND),
                       seed_rule="seed_of('sw039|p1|hist', stage, sid, 't1', turn1_style) / seed_of(..., 't2', cond); first screen-passing of n=3")
            if kept:
                a1, a2 = r1["kept"]["text"], r2["kept"]["text"]
                msgs = K.ladder_msgs(S[s], a1, a2); ids = E.render(msgs)
                txt = E.tok.decode(ids)
                assert a1 in txt and a2 in txt and S[s]["u3"] in txt, f"rendered context does not hold the turns verbatim: {s} {c}"
                row.update(a1=a1, a2=a2, messages=msgs, n_ctx_tok=len(ids), n_tok_t1=r1["kept"]["n_tok"], n_tok_t2=r2["kept"]["n_tok"],
                           cand_idx_t1=r1["cands"].index(r1["kept"]), cand_idx_t2=r2["cands"].index(r2["kept"]),
                           flags_t1=K.report_flags(a1), flags_t2=K.report_flags(a2))
            rows.append(row)
    K.wjl(f"{out}/histories_all.jsonl", rows)
    K.wjl(f"{out}/histories.jsonl", [r for r in rows if r["kept"]])
    log(f"L1 written: {len(rows)} rows, kept {sum(r['kept'] for r in rows)} -> {out} ({time.time() - t0:.0f}s)")


def check(out, smoke):
    man = json.load(open(f"{out}/manifest_L1.json")); rows = K.jl(f"{out}/histories_all.jsonl")
    keys = [r["key"] for r in rows]
    gate(len(keys) == len(set(keys)) and set(keys) == set(man["keys"]), f"L1 keys unique and == manifest ({len(keys)})")
    texts = [c["text"] for r in rows for t in ("cands_t1", "cands_t2") for c in (r[t] or [])]
    gate(sum(bool(t) for t in texts) >= 0.95 * len(texts), f"L1 candidates non-empty {sum(bool(t) for t in texts)}/{len(texts)}")
    kept = [r for r in rows if r["kept"]]
    for r in kept:   # input-side checks: the context has no system prompt and its user turns are the script's
        m = r["messages"]
        assert [x["role"] for x in m] == ["user", "assistant", "user", "assistant", "user"]
        assert not K.screen(r["a1"], "stop") and not K.screen(r["a2"], "stop")
    per = {c: sum(1 for r in kept if r["cond"] == c) for c in K.COND_ORDER}
    why = {}
    for r in rows:
        for t in ("cands_t1", "cands_t2"):
            for c in (r[t] or []):
                for w in c["why"]:
                    why[w] = why.get(w, 0) + 1
    st = dict(kept_per_cond=per, n_scripts=len(man["sids"]), candidate_fail_reasons=why,
              think_tag_kept=sum(r["flags_t1"]["think_tag"] or r["flags_t2"]["think_tag"] for r in kept),
              over_120_words_kept=sum(r["flags_t1"]["over_120_words"] or r["flags_t2"]["over_120_words"] for r in kept),
              n_ctx_tok_max=max((r["n_ctx_tok"] for r in kept), default=0))
    log("L1 stats", json.dumps(st))
    if smoke:
        gate(all(v >= 1 for v in per.values()), "smoke: every condition keeps >= 1 history")
    else:
        low = [c for c, v in per.items() if v < 0.85 * len(man["sids"])]
        if low:
            log("WARN cells keeping < 85 % of scripts:", low)
    return st


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--mode", choices=("smoke", "full", "smoke_full"), default="smoke_full")
    ap.add_argument("--out", default=K.RUN_NODE)
    a = ap.parse_args()
    S = K.load_scripts()
    E = Engine()
    os.makedirs(a.out, exist_ok=True)
    if a.mode in ("smoke", "smoke_full"):
        out = f"{a.out}/smoke"; os.makedirs(out, exist_ok=True)
        K.wjson(f"{out}/code_manifest_L1.json", K.code_manifest(dict(stage="p1smoke")))
        run(E, S, SMOKE_SIDS, "p1smoke", out); check(out, smoke=True)
        log("L1_SMOKE_PASSED")
        if a.mode == "smoke":
            return
    K.wjson(f"{a.out}/code_manifest_L1.json", K.code_manifest(dict(stage=K.PART)))
    run(E, S, sorted(S), K.PART, a.out); st = check(a.out, smoke=False)
    K.wjson(f"{a.out}/L1_stats.json", st)
    with open(f"{a.out}/GPU_DONE_L1.tmp", "w") as f:
        f.write(json.dumps(dict(t=time.strftime("%FT%TZ", time.gmtime()), **st)) + "\n")
    os.replace(f"{a.out}/GPU_DONE_L1.tmp", f"{a.out}/GPU_DONE_L1")
    log("HIST39P1_EXIT")


if __name__ == "__main__":
    main()
