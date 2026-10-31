"""sw074 generation on the node (parent only, vLLM 0.30, no LoRA). Forced "By the way," + 48 tokens after the 7-token reply header
(sw056's "none" arm / sw055's forced readout), T 0.7, thinking off. The rule (rules74.json) is the system prompt; the no-rule rows
have none. B1 x 4 samples, B2 x 2 samples; seeds paired across rules (common74.gen_seed).

Usage: python -I gen74.py --stage smoke|full
  smoke: 5 rule prompts (hd_A_rf, hd_B_of, pirate_A_rf, main_A_of, norule_proh) x 8 B1 scripts x 4 + 4 B2 scripts x 2 cells x 2
  full : every rule prompt x its trigger's contexts
Writes NODE_OUT/<stage>/gen.jsonl (incremental, resumable by key), summary.json, DONE_<stage> (only when every key is present,
non-empty and unique); GATE_FAIL_<stage> on a failed gate."""
import argparse, collections, json, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common74 as C  # noqa: E402

sys.path.insert(0, "/root/runs_E5/lib")
try:
    import labels_e5 as LB  # noqa: E402  (summary only; box 1 recomputes every label)
except Exception:  # pragma: no cover
    LB = None

SMOKE_RULES = ["hd_A_rf", "hd_B_of", "pirate_A_rf", "main_A_of", "norule_proh"]


def log(*a):
    print(f"[{C.utc()}]", *a, flush=True)


class Engine:
    def __init__(self):
        os.environ.setdefault("VLLM_LENS_DISABLE", "1")
        from transformers import AutoTokenizer
        from vllm import LLM, SamplingParams
        from vllm.inputs import TokensPrompt
        self.SP, self.TP = SamplingParams, TokensPrompt
        self.tok = AutoTokenizer.from_pretrained(C.BASE)
        assert self.tok.convert_tokens_to_ids("<|im_end|>") == C.IM_END
        t0 = time.time()
        self.llm = LLM(model=C.BASE, dtype="bfloat16", max_model_len=C.MAX_MODEL_LEN, gpu_memory_utilization=0.88, seed=0,
                       max_num_seqs=512, max_num_batched_tokens=32768, enable_prefix_caching=True, language_model_only=True)
        self.btw = self.enc(C.BTW)
        log(f"ENGINE_READY load {time.time() - t0:.0f}s; btw ids {self.btw}")

    def enc(self, t):
        return list(self.tok(t, add_special_tokens=False)["input_ids"])

    def render(self, msgs):
        txt = self.tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False)
        ids = self.enc(txt)
        assert ids[-7:] == C.HEADER, ids[-7:]
        return ids, txt

    def run(self, reqs):
        for r in reqs:
            assert len(r["ids"]) + C.FORCED_MAX <= C.MAX_MODEL_LEN, r["key"]
        sps = [self.SP(n=1, temperature=C.SAMPLER["temperature"], top_p=1.0, top_k=0, min_p=0.0, repetition_penalty=1.0,
                       max_tokens=C.FORCED_MAX, stop_token_ids=[C.IM_END], skip_special_tokens=True, seed=r["seed"]) for r in reqs]
        outs = self.llm.generate([self.TP(prompt_token_ids=r["ids"]) for r in reqs], sps, use_tqdm=False)
        return [(o.outputs[0].text, list(o.outputs[0].token_ids), o.outputs[0].finish_reason) for o in outs]


def build(E, rules, ctxs, stage):
    if stage == "smoke":
        rids = SMOKE_RULES
        b1 = sorted({c["sid"] for c in ctxs if c["readout"] == "B1"})[:8]
        b2 = sorted({c["sid"] for c in ctxs if c["readout"] == "B2"})[:4]
        ctxs = [c for c in ctxs if (c["readout"] == "B1" and c["sid"] in b1) or (c["readout"] == "B2" and c["sid"] in b2)]
    else:
        rids = sorted(rules)
    reqs, tmpl = [], {}
    for rid in rids:
        R = rules[rid]
        for c in ctxs:
            if c["trig"] != R["trig"]:
                continue
            msgs = ([{"role": "system", "content": R["system"]}] if R["system"] else []) + c["messages"]
            ids, txt = E.render(msgs)
            if rid not in tmpl:
                tmpl[rid] = txt
            for smp in range(C.N_SAMP[c["readout"]]):
                reqs.append(dict(key=C.gkey(c["readout"], rid, c["cell"], c["sid"], smp), readout=c["readout"], rule_id=rid,
                                 pair=R["pair"], assign=R["assign"], order=R["order"], trig=c["trig"], cell=c["cell"], sid=c["sid"],
                                 scenario=c["scenario"], sample=smp, ids=ids + E.btw, n_prompt=len(ids) + len(E.btw),
                                 seed=C.gen_seed(c["readout"], c["cell"], c["sid"], smp)))
    keys = [r["key"] for r in reqs]
    assert len(keys) == len(set(keys)), "duplicate keys"
    return reqs, tmpl


def summarize(rows):
    s = collections.defaultdict(lambda: collections.Counter())
    for r in rows:
        k = f"{r['readout']}|{r['rule_id']}|{r['cell']}"
        s[k]["n"] += 1
        if LB:
            s[k]["strict_" + LB.strict_label(r["text"])] += 1
            s[k]["ext_" + LB.ext_label(r["text"])] += 1
        s[k]["len_" + r["finish"]] += 1
    return {k: dict(v) for k, v in sorted(s.items())}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--stage", required=True, choices=["smoke", "full"])
    a = ap.parse_args()
    out = f"{C.NODE_OUT}/{a.stage}"
    os.makedirs(out, exist_ok=True)
    rules = json.load(open(C.RULES))["rules"]
    ctxs = C.jl(C.CONTEXTS)
    log(f"rules sha256 {C.sha256(C.RULES)}; contexts sha256 {C.sha256(C.CONTEXTS)} ({len(ctxs)})")
    E = Engine()
    reqs, tmpl = build(E, rules, ctxs, a.stage)
    C.wjson(f"{out}/templates_rendered.json", tmpl)   # the exact rendered prompt of each rule prompt's first context
    fn = f"{out}/gen.jsonl"
    done = {r["key"] for r in C.jl(fn)}
    todo = [r for r in reqs if r["key"] not in done]
    log(f"{a.stage}: {len(reqs)} requests, {len(done)} done, {len(todo)} to run")
    t0 = time.time()
    for i in range(0, len(todo), 4000):
        part = todo[i:i + 4000]
        res = E.run(part)
        rows = []
        for r, (text, gids, fin) in zip(part, res):
            row = {k: v for k, v in r.items() if k != "ids"}
            row.update(gen=text, text=C.BTW + text, n_tok=len(gids), finish=fin)
            rows.append(row)
        C.wjl(fn, rows, mode="a")
        log(f"chunk {i // 4000 + 1}: {len(part)} done in {time.time() - t0:.0f}s")
    rows = C.jl(fn)
    by = {r["key"]: r for r in rows}
    want = {r["key"] for r in reqs}
    gates = dict(all_keys=set(by) >= want, n_rows_file=len(rows), n_unique=len(by), n_expected=len(want),
                 no_dup_lines=len(rows) == len(by), nonempty=sum(1 for k in want if by.get(k, {}).get("n_tok", 0) > 0),
                 btw_ids=E.btw)
    ok = gates["all_keys"] and gates["no_dup_lines"] and gates["nonempty"] == len(want)
    C.wjson(f"{out}/summary.json", dict(gates=gates, ok=ok, cells=summarize([by[k] for k in want if k in by]), t=C.utc()))
    log("GATES", json.dumps(gates))
    if not ok:
        C.touch(f"{out}/GATE_FAIL_{a.stage}", json.dumps(gates))
        sys.exit(2)
    C.touch(f"{out}/DONE_{a.stage}", C.utc())
    log("DONE")


if __name__ == "__main__":
    main()
