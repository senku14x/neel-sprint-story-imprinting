"""E10 R01 Stage 3: the teammate's forced readout on this run's own conversations (forward passes only).

Context (exactly as the brief): msgs = the stored messages; k = 5 without a system prompt, 6 with one;
  ids = tok(apply_chat_template(msgs[:k], add_generation_prompt=True, enable_thinking=False), add_special_tokens=False)
        + tok("Fun fact about the", add_special_tokens=False)
Asserts: msgs[k-1] is the turn-3 user message as sent (rebuilt from the script); the template part ends with </think> (248069)
followed only by newline tokens; no <|im_end|> after the last <|im_start|>; " bee" -> [35997], " crow" -> [9000].
Readout: for c in (35997, 9000) send ids + [c] with SamplingParams(max_tokens=1, temperature=1.0, prompt_logprobs=0) and read the
log-probability of the last prompt token (raw logprobs, engine logprobs_mode raw_logprobs, full vocabulary).
LO = log p(bee) - log p(crow); for S/SB contexts LO under the writing model's LoRA and under the parent (no LoRA) on the identical
ids; LOrel = LO(model) - LO(parent). Parent contexts: LO under the parent.

Serving: vLLM 0.30, base model + the same remapped LoRA copies that wrote the conversations (S and SB both loaded, max_loras 2),
parent = requests without a LoRA in the same engine.

Run (one engine):
  1. gate: LOrel on 20 SB x default contexts (the first 20 scripts_heldout2 scripts in file order); mean |LOrel| < 0.5 -> exit 3.
  2. the run's contexts (--set gpu1: SB cell-A scripts_heldout2; gpu0: S cell-A scripts_heldout2, then parent cell C;
     smoke: every SB row of the smoke rollouts).
  3. repeat check: if --repeat_from names a finished output of another engine, recompute 10 random contexts of it
     (random.Random(0)) and record the largest difference.
python stage3.py --set gpu1 --rollouts 'glob' --out results/stage3/stage3_gpu1.jsonl [--repeat_from other.jsonl]
"""
import argparse, glob, json, math, os, random, sys, time

W = "/workspace/e10/r01"
BEE, CROW = 35997, 9000
THINK_END, IM_START, IM_END = 248069, 248045, 248046
LORAS = {"S": "/workspace/e05/lora_vllm/S", "SB": "/workspace/e05/r04/lora_vllm/SB"}


def load_jsonl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def scripts():
    out = {}
    for f in ("scripts_heldout2", "scripts_frozen"):
        for l in open(f"{W}/src/eval_data/{f}.jsonl"):
            s = json.loads(l)
            out[s["script_id"]] = s
    return out


def build_ids(tok, row, S, bridge):
    msgs = row["messages"]
    has_sys = msgs[0]["role"] == "system"
    k = 6 if has_sys else 5
    s = S[row["script_id"]]
    t3 = f"{s['turn3_prohibition']} {s['turn3_question']}" if row["trigger"] else s["turn3_question"]
    assert msgs[k - 1]["role"] == "user" and msgs[k - 1]["content"] == t3, row["key"]
    assert sum(m["role"] == "user" for m in msgs[:k]) == 3 and msgs[k - 1] is [m for m in msgs[:k] if m["role"] == "user"][2]
    text = tok.apply_chat_template(msgs[:k], tokenize=False, add_generation_prompt=True, enable_thinking=False)
    tids = tok(text, add_special_tokens=False)["input_ids"]
    j = max(i for i, x in enumerate(tids) if x == THINK_END)
    tail = tids[j + 1:]
    assert tail and set(tok.decode(tail)) == {"\n"}, (row["key"], tail)
    last_start = max(i for i, x in enumerate(tids) if x == IM_START)
    assert IM_END not in tids[last_start:], row["key"]
    return tids + bridge


def select(name, rows):
    """(row, scorers) for the run's set."""
    if name == "gpu1":
        return [(r, ["SB", "parent"]) for r in rows if r["model"] == "SB" and r["trigger"] and r["script_set"] == "scripts_heldout2"]
    if name == "gpu0":
        a = [(r, ["S", "parent"]) for r in rows if r["model"] == "S" and r["trigger"] and r["script_set"] == "scripts_heldout2"]
        c = [(r, ["parent"]) for r in rows if r["model"] == "parent" and r["trigger"]]
        return a + c
    if name == "smoke":
        return [(r, ["SB", "parent"]) for r in rows if r["model"] == "SB"]
    raise ValueError(name)


class Reader:
    def __init__(self, gpu_mem, max_num_seqs):
        from transformers import AutoTokenizer
        from vllm import LLM, SamplingParams
        from vllm.inputs import TokensPrompt
        from vllm.lora.request import LoRARequest
        sys.path.insert(0, f"{W}/src")
        import gen_eval  # BASE (the /dev/shm copy or SI_MODEL_DIR)
        self.base = gen_eval.BASE
        self.tok = AutoTokenizer.from_pretrained(self.base)
        assert self.tok.encode(" bee") == [BEE] and self.tok.encode(" crow") == [CROW]
        assert self.tok(" bee", add_special_tokens=False)["input_ids"] == [BEE]
        assert self.tok(" crow", add_special_tokens=False)["input_ids"] == [CROW]
        self.bridge = self.tok("Fun fact about the", add_special_tokens=False)["input_ids"]
        kw = dict(model=self.base, tokenizer=self.base, dtype="bfloat16", max_model_len=8192, gpu_memory_utilization=gpu_mem,
                  seed=0, max_num_seqs=max_num_seqs, enable_lora=True, max_lora_rank=32, max_loras=2)
        try:
            self.llm = LLM(language_model_only=True, **kw)
        except TypeError:
            self.llm = LLM(**kw)
        self.engine_kw = kw
        try:
            self.logprobs_mode = str(self.llm.llm_engine.model_config.logprobs_mode)
        except Exception:  # noqa: BLE001
            self.logprobs_mode = "unknown"
        self.SP = SamplingParams(max_tokens=1, temperature=1.0, prompt_logprobs=0)
        self.TP = TokensPrompt
        self.lreq = {n: LoRARequest(n, i + 1, p) for i, (n, p) in enumerate(LORAS.items())}

    def lo(self, items, chunk=512):
        """items: list of (ids, scorer). Returns list of dict(bee=lp, crow=lp, LO=...)."""
        reqs = [(ids + [c], sc, c) for ids, sc in items for c in (BEE, CROW)]
        lps = []
        for i in range(0, len(reqs), chunk):
            part = reqs[i:i + chunk]
            outs = self.llm.generate([self.TP(prompt_token_ids=x) for x, _, _ in part], self.SP,
                                     lora_request=[self.lreq.get(sc) for _, sc, _ in part], use_tqdm=False)
            for (x, sc, c), o in zip(part, outs):
                assert list(o.prompt_token_ids) == x
                d = o.prompt_logprobs[-1]
                lps.append(float(d[c].logprob))
        # a non-finite value (NaN / inf) is re-run alone (batch of one); if still non-finite the readout is recorded as None
        bad = [i for i, v in enumerate(lps) if not math.isfinite(v)]
        retry = {}
        for i in bad:
            x, sc, c = reqs[i]
            o = self.llm.generate([self.TP(prompt_token_ids=x)], self.SP, lora_request=[self.lreq.get(sc)], use_tqdm=False)[0]
            retry[i] = float(o.prompt_logprobs[-1][c].logprob)
        if bad:
            print(f"non-finite log-probabilities: {len(bad)} of {len(lps)}; finite when re-run alone: "
                  f"{sum(math.isfinite(v) for v in retry.values())}", flush=True)
        res = []
        for j in range(len(items)):
            vals, flags = [], {}
            for i in (2 * j, 2 * j + 1):
                v = lps[i]
                if i in retry:
                    flags["first_value"] = flags.get("first_value", []) + [repr(v)]
                    v = retry[i]
                vals.append(v if math.isfinite(v) else None)
            b, cr = vals
            d = dict(bee=b, crow=cr, LO=(b - cr) if b is not None and cr is not None else None)
            if flags:
                d["rerun_alone"] = flags["first_value"]
            res.append(d)
        return res


def score(R, pairs, S):
    items, idx = [], []
    for n, (r, scorers) in enumerate(pairs):
        ids = build_ids(R.tok, r, S, R.bridge)
        for sc in scorers:
            items.append((ids, sc)); idx.append((n, sc, len(ids)))
    vals = R.lo(items)
    out = [dict(key=r["key"], ctx_model=r["model"], persona=r["persona"], script_id=r["script_id"], script_set=r["script_set"],
                trigger=r["trigger"], scores={}) for r, _ in pairs]
    for (n, sc, L), v in zip(idx, vals):
        out[n]["scores"][sc] = v; out[n]["n_ids"] = L
    for o in out:
        m = o["ctx_model"]
        o["LO_model"] = o["scores"][m]["LO"] if m in o["scores"] else None
        o["LO_parent"] = o["scores"]["parent"]["LO"]
        o["LOrel"] = o["LO_model"] - o["LO_parent"] if o["LO_model"] is not None and o["LO_parent"] is not None else None
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", required=True); ap.add_argument("--rollouts", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--repeat_from", default=None); ap.add_argument("--gate_rollouts", default=None)
    ap.add_argument("--gpu_mem", type=float, default=0.85); ap.add_argument("--max_num_seqs", type=int, default=128)
    ap.add_argument("--repeat_only", action="store_true", help="only the repeat check: 10 random contexts of each finished output "
                    "named in --repeat_from (comma-separated), recomputed in this fresh engine")
    a = ap.parse_args()
    if a.repeat_only:
        return repeat_only(a)
    t0 = time.time()
    S = scripts()
    rows = []
    for p in sorted(glob.glob(a.rollouts)):
        if os.path.exists(p + ".done"):  # finished generation files only
            rows += load_jsonl(p)
    pairs = select(a.set, rows)
    order = {sid: i for i, sid in enumerate(json.loads(l)["script_id"] for l in open(f"{W}/src/eval_data/scripts_heldout2.jsonl"))}
    grows = rows if not a.gate_rollouts else [r for p in sorted(glob.glob(a.gate_rollouts)) if os.path.exists(p + ".done")
                                              for r in load_jsonl(p)]
    gate = sorted([r for r in grows if r["model"] == "SB" and r["persona"] == "default" and r["trigger"]
                   and r["script_set"] == "scripts_heldout2"], key=lambda r: order[r["script_id"]])[:20]
    print(f"{len(pairs)} contexts; gate {len(gate)} SB x default contexts", flush=True)
    R = Reader(a.gpu_mem, a.max_num_seqs)
    meta = dict(set=a.set, engine={k: v for k, v in R.engine_kw.items()}, logprobs_mode=R.logprobs_mode, bridge_ids=R.bridge,
                sampling=repr(R.SP), t_engine_ready=time.time() - t0)
    print(json.dumps(meta, default=str), flush=True)
    # 1. gate
    g = score(R, [(r, ["SB", "parent"]) for r in gate], S)
    gf = [x for x in g if x["LOrel"] is not None]
    mabs = sum(abs(x["LOrel"]) for x in gf) / len(gf) if gf else float("nan")
    gate_res = dict(meta, n=len(gf), mean_abs_LOrel=mabs, mean_LOrel=sum(x["LOrel"] for x in gf) / len(gf) if gf else None,
                    passed=bool(g) and mabs >= 0.5, rows=g, t=time.time() - t0)
    base = os.path.splitext(a.out)[0]
    json.dump(gate_res, open(base + "_gate.json", "w"), indent=1)
    print(f"gate: n {len(g)}, mean |LOrel| {mabs:.3f}, mean LOrel {gate_res['mean_LOrel']}, passed {gate_res['passed']}", flush=True)
    if not gate_res["passed"] and a.set != "smoke":
        sys.exit(3)
    # 2. the run's contexts
    t1 = time.time()
    out = score(R, pairs, S)
    with open(a.out, "w") as f:
        for o in out:
            f.write(json.dumps(o) + "\n")
    nn = sum(1 for o in out for v in o["scores"].values() if v["LO"] is None)
    print(f"wrote {len(out)} contexts in {time.time() - t1:.0f}s; readouts still non-finite after a re-run alone: {nn}", flush=True)
    # 3. repeat check in this (fresh, different) engine on another engine's finished output (smoke test: on its own output, to
    #    exercise the code path)
    if a.set == "smoke" and not a.repeat_from:
        open(a.out + ".done", "w").write("smoke\n"); a.repeat_from = a.out
    if a.repeat_from and os.path.exists(a.repeat_from) and os.path.exists(a.repeat_from + ".done"):
        prev = load_jsonl(a.repeat_from)
        pick = random.Random(0).sample(prev, min(10, len(prev)))
        byk = {r["key"]: r for r in rows}
        if not all(p["key"] in byk for p in pick):
            allrows = [r for p in sorted(glob.glob(f"{W}/results/rollouts/*.jsonl")) for r in load_jsonl(p)]
            byk = {r["key"]: r for r in allrows}
        redo = score(R, [(byk[p["key"]], list(p["scores"])) for p in pick], S)
        diffs, dlo = [], []
        for p, q in zip(pick, redo):
            for sc in p["scores"]:
                for f_ in ("bee", "crow", "LO"):
                    if p["scores"][sc][f_] is not None and q["scores"][sc][f_] is not None:
                        diffs.append(abs(p["scores"][sc][f_] - q["scores"][sc][f_]))
                        if f_ == "LO":
                            dlo.append(diffs[-1])
        rep = dict(source=a.repeat_from, engine_set=a.set, n_contexts=len(pick), keys=[p["key"] for p in pick],
                   max_abs_diff=max(diffs) if diffs else None, max_abs_diff_LO=max(dlo) if dlo else None, first=pick, second=redo)
        json.dump(rep, open(f"{os.path.dirname(a.out)}/repeat_check.json", "w"), indent=1)
        print(f"repeat check vs {a.repeat_from}: max |diff| {rep['max_abs_diff']:.4f} (LO {rep['max_abs_diff_LO']:.4f})", flush=True)
    open(a.out + ".done", "w").write(f"{time.time() - t0:.0f}s\n")
    print(f"stage3 {a.set} done in {time.time() - t0:.0f}s", flush=True)


def repeat_only(a):
    t0 = time.time()
    S = scripts()
    allrows = [r for p in sorted(glob.glob(a.rollouts)) if os.path.exists(p + ".done") for r in load_jsonl(p)]
    byk = {r["key"]: r for r in allrows}
    R = Reader(a.gpu_mem, a.max_num_seqs)
    per = []
    for src in a.repeat_from.split(","):
        prev = load_jsonl(src)
        pick = random.Random(0).sample(prev, min(10, len(prev)))
        redo = score(R, [(byk[p["key"]], list(p["scores"])) for p in pick], S)
        diffs, dlo = [], []
        for p, q in zip(pick, redo):
            for sc in p["scores"]:
                for f_ in ("bee", "crow", "LO"):
                    if p["scores"][sc][f_] is not None and q["scores"][sc][f_] is not None:
                        diffs.append(abs(p["scores"][sc][f_] - q["scores"][sc][f_]))
                        if f_ == "LO":
                            dlo.append(diffs[-1])
        per.append(dict(source=src, n_contexts=len(pick), keys=[p["key"] for p in pick], max_abs_diff=max(diffs) if diffs else None,
                        max_abs_diff_LO=max(dlo) if dlo else None, n_compared=len(diffs), first=pick, second=redo))
        print(f"repeat check vs {src}: max |diff| {per[-1]['max_abs_diff']:.4f} (LO {per[-1]['max_abs_diff_LO']:.4f}) over "
              f"{len(diffs)} values", flush=True)
    rep = dict(source=" + ".join(os.path.basename(x["source"]) for x in per), engine_set="repeat_only (fresh engine, empty compile cache)",
               n_contexts=sum(x["n_contexts"] for x in per), keys=[k for x in per for k in x["keys"]],
               max_abs_diff=max(x["max_abs_diff"] for x in per), max_abs_diff_LO=max(x["max_abs_diff_LO"] for x in per),
               engine=R.engine_kw, logprobs_mode=R.logprobs_mode, per_source=per)
    json.dump(rep, open(a.out, "w"), indent=1)
    print(f"repeat-only done in {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
