"""sw004 T3 validation gate (DECISIONS_T3.md T3-D2, frozen before any trajectory output).
measure(llm, tok, lreqs)  -> per model label: for each of the 20 gate contexts
    lp      : prompt log-prob of every context token at positions 1..n-1 (prompt_logprobs=0, raw log-probs)
    greedy  : the first 20 greedily generated token ids after the context (temperature 0)
    openers : summed teacher-forced log-prob of each of the 6 frozen openers after the context (Part P's probe code)
compare(lora, refs)       -> the gate verdict dict (pure CPU; python3 gate_T3.py recomputes it from the saved files)
Rule: (a) per organism, LoRA-served final vs merged final: pooled mean |dlp| <= 0.05 nat/token AND greedy 20-token sequences identical
      in >= 11 of 20 contexts; (b) every one of the 10 adapters: pooled mean |dlp| vs the bare parent >= 10 x parity_err, where
      parity_err = max over the two organisms of (a)'s pooled mean |dlp|. pass_all = (a) for A and B and (b) for all 10."""
import json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common_t3 as T  # noqa: E402

PAR_MAX, GREEDY_MIN, FOLD = 0.05, 11, 10.0


def measure(llm, tok, lreqs):
    """lreqs: {label: LoRARequest or None}. Returns {label: {ctx_id: dict(lp, greedy, openers)}}."""
    from vllm import SamplingParams
    from vllm.inputs import TokensPrompt
    ctx = T.jsonl(f"{T.JOBS}/gate_ctx.jsonl")
    ops = [op for pr in T.P.PAIRS for op in pr]
    op_ids = {op: tok(op, add_special_tokens=False)["input_ids"] for op in ops}
    labs = list(lreqs)
    # 1) prompt log-probs on the context and on context+opener
    jobs = []
    for m in labs:
        for r in ctx:
            jobs.append((m, r["id"], None, r["ids"]))
            for op in ops:
                jobs.append((m, r["id"], op, r["ids"] + op_ids[op]))
    sp = SamplingParams(max_tokens=1, temperature=0, prompt_logprobs=0, detokenize=False)
    outs = []
    for c0 in range(0, len(jobs), 400):   # chunked: prompt_logprobs objects are large
        ch = jobs[c0:c0 + 400]
        lr = [lreqs[j[0]] for j in ch]
        outs += llm.generate([TokensPrompt(prompt_token_ids=j[3]) for j in ch], [sp] * len(ch),
                             lora_request=None if all(x is None for x in lr) else lr, use_tqdm=False)
    res = {m: {r["id"]: dict(lp=None, greedy=None, openers={}) for r in ctx} for m in labs}
    nctx = {r["id"]: len(r["ids"]) for r in ctx}
    for (m, cid, op, ids), o in zip(jobs, outs):
        plp = o.prompt_logprobs
        if op is None:
            res[m][cid]["lp"] = [float(plp[i][ids[i]].logprob) for i in range(1, len(ids))]
        else:
            n0 = nctx[cid]
            res[m][cid]["openers"][op] = float(sum(plp[n0 + j][ids[n0 + j]].logprob for j in range(len(op_ids[op]))))
    # 2) greedy 20 tokens
    gj = [(m, r) for m in labs for r in ctx]
    gsp = SamplingParams(max_tokens=20, temperature=0, detokenize=True)
    glr = [lreqs[m] for m, _ in gj]
    gouts = llm.generate([TokensPrompt(prompt_token_ids=r["ids"]) for _, r in gj], [gsp] * len(gj),
                         lora_request=None if all(x is None for x in glr) else glr, use_tqdm=False)
    for (m, r), o in zip(gj, gouts):
        res[m][r["id"]]["greedy"] = list(o.outputs[0].token_ids)
        res[m][r["id"]]["greedy_text"] = o.outputs[0].text
    return res


def _pooled(a, b, cids):
    d = np.concatenate([np.abs(np.array(a[c]["lp"]) - np.array(b[c]["lp"])) for c in cids])
    per = [float(np.mean(np.abs(np.array(a[c]["lp"]) - np.array(b[c]["lp"])))) for c in cids]
    return dict(mean_abs=float(d.mean()), median_abs=float(np.median(d)), p99_abs=float(np.percentile(d, 99)), max_abs=float(d.max()),
                n_tok=int(d.size), per_ctx_mean_min=float(min(per)), per_ctx_mean_max=float(max(per)))


def _prefix(a, b):
    n = 0
    for x, y in zip(a, b):
        if x != y:
            break
        n += 1
    return n


def compare(lora, refs, known=None):
    """lora: measure() output of the LoRA engine (labels: parent + 10 adapters); refs: {"A": merged-A measure, "B": merged-B measure}
    (each a {ctx_id: ...} dict); known: Part P's stored opener log-probs (jobs/partP_gate_openers.json) for information."""
    cids = list(lora["parent"])
    out = dict(rule=dict(parity_max_mean_abs=PAR_MAX, greedy_identical_min=GREEDY_MIN, fold_vs_parent=FOLD), parity={}, active={})
    for o in T.ORGS:
        fin = lora[T.label(o, 250)]
        ref = refs[o]
        p = _pooled(fin, ref, cids)
        same = [fin[c]["greedy"] == ref[c]["greedy"] for c in cids]
        p.update(greedy_identical=int(sum(same)), greedy_mean_prefix=float(np.mean([_prefix(fin[c]["greedy"], ref[c]["greedy"]) for c in cids])),
                 merged_vs_parent=_pooled(ref, lora["parent"], cids)["mean_abs"])
        p["pass"] = bool(p["mean_abs"] <= PAR_MAX and p["greedy_identical"] >= GREEDY_MIN)
        out["parity"][o] = p
    perr = max(out["parity"][o]["mean_abs"] for o in T.ORGS)
    out["parity_err"] = perr
    for m in T.MODELS:
        q = _pooled(lora[m], lora["parent"], cids)
        q["greedy_identical_to_parent"] = int(sum(lora[m][c]["greedy"] == lora["parent"][c]["greedy"] for c in cids))
        q["fold"] = q["mean_abs"] / perr if perr > 0 else float("inf")
        q["pass"] = bool(q["mean_abs"] >= FOLD * perr)
        out["active"][m] = q
    out["pass_a"] = all(out["parity"][o]["pass"] for o in T.ORGS)
    out["pass_b"] = all(out["active"][m]["pass"] for m in T.MODELS)
    out["pass_all"] = bool(out["pass_a"] and out["pass_b"])
    if known:   # information only: opener log-probs vs Part P's stored merged-model values on the same contexts
        ka = {}
        for lab, src, pm in [("lora_final_A", lora[T.label("A", 250)], "ps_A"), ("lora_final_B", lora[T.label("B", 250)], "ps_B"),
                             ("lora_engine_parent", lora["parent"], "parent"), ("merged_ref_A", refs["A"], "ps_A"), ("merged_ref_B", refs["B"], "ps_B")]:
            d = [abs(src[c]["openers"][op] - known[pm][f"{c}|{op}"]) for c in cids for op in src[c]["openers"]]
            ka[f"{lab}_vs_partP_{pm}"] = dict(mean_abs=float(np.mean(d)), max_abs=float(np.max(d)), n=len(d))
        out["openers_vs_partP_stored"] = ka
    return out


if __name__ == "__main__":   # recompute the verdict from saved raw gate files
    lora = json.load(open(f"{T.OUT}/gate_lora.json"))
    refs = {o: json.load(open(f"{T.OUT}/gate_ref_ps_{o}.json"))[f"ps_{o}_merged"] for o in T.ORGS}
    known = json.load(open(f"{T.JOBS}/partP_gate_openers.json"))
    r = compare(lora, refs, known)
    print(json.dumps(r, indent=1))
