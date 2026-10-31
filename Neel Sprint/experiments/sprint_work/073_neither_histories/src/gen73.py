"""sw073 evaluation (GPU 2). One vLLM 0.30 engine (vlfix venv, VLLM_LENS_DISABLE=1, bf16, max_model_len 16,384, gpu_memory_utilization
0.88, prefix caching, max_num_seqs 512, max_num_batched_tokens 32,768, language_model_only), the parent plus the six organisms as
per-request LoRAs (max_loras = max_cpu_loras = 6, rank 32; remapped vLLM copies from lora73.json = the E5 adapter registry's ready
entries, sha256 re-checked here). Thinking off (7-token header asserted). Sampler T 0.7, top_p 1, top_k 0, min_p 0, rep 1, stop
<|im_end|>. (sw055 gen55.py engine and readouts, copied.)

Arms (every model, forced x 2 + free x 1):
 hist : sw019-style histories [u1, a1, u2, a2] + u3_trig (trigger turn 3) for n1-n4 (kept_hist.jsonl, sw073 writer) and the references
        helpful / polite_refusal / dismissive (sw019 g2_kept). forced = prompt + "By the way," + 48 tokens; free = 2,048 tokens.
        Seeds seed_of('sw055b', sid, sample, readout) (= sw055's, paired across models and versions).
 t1   : sw056's frame: the turn-1 user message, reply prefilled with the opening (no end-of-turn); forced = opening + " By the way,"
        + 48; free = continuation to a 2,048-token reply. n1-n3 (kept_open.jsonl) and sw056's helpful / polite_refusal / dismissive
        openings. Seeds seed_of('sw056', sid, sample, readout) (= sw056's gen_seed).
Row text: forced = "By the way," + generated; free = the generated continuation only (the opening is screened and not labelled).

 --mode smoke : 3 scripts (hist: all 7 versions where kept; t1: all 6 arms where kept) + adapter-active check -> OUT/smoke/;
                gates: adapter sha256; adapter active (each organism's greedy forced text differs from the parent's on >= 1 of 2
                contexts AND its forced STRICT onset on the smoke helpful + dismissive history rows >= 0.5; parent onset reported);
                header; unique keys; exact coverage; >= 95% non-empty; forced texts start with "By the way,". -> SMOKE_OK
 --mode full  : every kept context -> OUT/full/gen.jsonl (appended per chunk; resumes by key); same generic gates -> GPU_DONE"""
import argparse, json, os, sys, time
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common73 as C  # noqa: E402

OUT = f"{C.NODE_RUN}/gen"
KEPT_HIST = "/workspace/runs_executor/sw073/write/prof/kept_hist.jsonl"
KEPT_OPEN = "/workspace/runs_executor/sw073/write/prof/kept_open.jsonl"
LORA_JSON = "/workspace/runs_executor/sw073/lora73.json"
GATES = []


def log(*a):
    print(time.strftime("%H:%M:%S", time.gmtime()), *a, flush=True)


class Gate(Exception):
    pass


def gate(cond, msg):
    GATES.append(dict(ok=bool(cond), msg=msg))
    if not cond:
        log("GATE_FAIL", msg)
        raise Gate(msg)
    log("gate ok:", msg)


class Engine:
    def __init__(self, lora):
        os.environ.setdefault("VLLM_LENS_DISABLE", "1")
        from transformers import AutoTokenizer
        from vllm import LLM, SamplingParams
        from vllm.inputs import TokensPrompt
        from vllm.lora.request import LoRARequest
        self.SP, self.TP = SamplingParams, TokensPrompt
        self.tok = AutoTokenizer.from_pretrained(C.BASE)
        assert self.tok.convert_tokens_to_ids("<|im_end|>") == C.IM_END
        t0 = time.time()
        n = len(C.ORGS)
        self.llm = LLM(model=C.BASE, dtype="bfloat16", max_model_len=C.MAX_MODEL_LEN, gpu_memory_utilization=0.88, seed=0, max_num_seqs=512,
                       max_num_batched_tokens=32768, enable_prefix_caching=True, language_model_only=True, enable_lora=True, max_lora_rank=32,
                       max_loras=n, max_cpu_loras=n)
        self.lreq = {"parent": None} | {m: LoRARequest(m, i + 1, lora[m]["vllm_path"]) for i, m in enumerate(C.ORGS)}
        self.btw = self.enc(C.BTW)
        log(f"ENGINE_READY load {time.time() - t0:.0f}s; {n} LoRA slots")

    def enc(self, t):
        return self.tok(t, add_special_tokens=False)["input_ids"]

    def render(self, msgs):
        ids = self.enc(self.tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False))
        assert ids[-7:] == C.HEADER, ids[-7:]
        return ids

    def run(self, reqs):
        if not reqs:
            return []
        bad = [r["key"] for r in reqs if len(r["ids"]) + r["max_tokens"] > C.MAX_MODEL_LEN]
        gate(not bad, f"prompt + max_tokens <= max_model_len ({len(reqs)} requests; violations {bad[:3]})")
        sps = [self.SP(n=1, temperature=0.0 if r.get("greedy") else C.SAMPLER["temperature"], top_p=1.0, top_k=0, min_p=0.0, repetition_penalty=1.0,
                       max_tokens=r["max_tokens"], stop_token_ids=[C.IM_END], skip_special_tokens=True, seed=r["seed"]) for r in reqs]
        outs = self.llm.generate([self.TP(prompt_token_ids=r["ids"]) for r in reqs], sps, use_tqdm=False,
                                 lora_request=[self.lreq[r["model"]] for r in reqs])
        return [(o.outputs[0].text, list(o.outputs[0].token_ids), o.outputs[0].finish_reason) for o in outs]


def check_lora():
    L = json.load(open(LORA_JSON))
    gate(set(C.ORGS) <= set(L), f"lora73.json covers the 6 organisms ({sorted(L)})")
    got = {}
    for m in C.ORGS:
        p = f"{L[m]['vllm_path']}/adapter_model.safetensors"
        got[m] = C.sha256(p) if os.path.exists(p) else "MISSING"
    bad = [m for m in C.ORGS if got[m] != L[m]["vllm_sha256"]]
    gate(not bad, f"adapter sha256 = registry for all 6 (mismatched {bad})")
    from safetensors import safe_open
    for m in C.ORGS:
        with safe_open(f"{L[m]['vllm_path']}/adapter_model.safetensors", framework="pt") as s:
            ks = list(s.keys())
        nb = [k for k in ks if not k.startswith("base_model.model.model.language_model.layers.")]
        gate(ks and not nb, f"{m}: adapter in the vLLM remap convention ({len(ks)} tensors)")
    return L, got


# ------------------------------------------------------------------------------------------------ contexts
def contexts(smoke):
    H = C.jl(KEPT_HIST); O = C.jl(KEPT_OPEN)
    hs = sorted({r["sid"] for r in H}); os_ = sorted({r["sid"] for r in O})
    if smoke:
        hs, os_ = hs[:3], os_[:3]
    cx = []
    for r in H:
        if r["sid"] in hs:
            assert [m["role"] for m in r["messages"]] == ["user", "assistant", "user", "assistant"], r["key"]
            cx.append(dict(arm_kind="hist", version=r["version"], sid=r["sid"], scenario=r["scenario"], domain=r.get("domain"),
                           msgs=r["messages"] + [{"role": "user", "content": r["u3_trig"]}], user=r["u3_trig"], opening=None,
                           src=r["source"], src_key=r["key"]))
    for r in O:
        if r["sid"] in os_:
            cx.append(dict(arm_kind="t1", version=r["version"], sid=r["sid"], scenario=r["scenario"], domain=r.get("domain"),
                           msgs=[{"role": "user", "content": r["user"]}], user=r["user"], opening=r["opening"], src=r["source"], src_key=r["key"]))
    ks = [(c["arm_kind"], c["version"], c["sid"]) for c in cx]
    assert len(ks) == len(set(ks))
    return cx


def build(E, cx, stage):
    reqs = []
    for c in cx:
        base = E.render(c["msgs"])
        for m in C.MODELS:
            for ro, ns in C.N_SAMP.items():
                for smp in range(ns):
                    if c["arm_kind"] == "hist":
                        ids = base + (E.btw if ro == "forced" else [])
                        mt = C.FORCED_MAX if ro == "forced" else C.FREE_MAX
                        seed = C.seed_hist_arm(c["sid"], smp, ro)
                    else:
                        pre = E.enc(c["opening"] + C.BTW_SP) if ro == "forced" else E.enc(c["opening"])
                        ids = base + pre
                        mt = C.FORCED_MAX if ro == "forced" else C.FREE_MAX - len(E.enc(c["opening"]))
                        seed = C.seed_t1_arm(c["sid"], smp, ro)
                    reqs.append(dict(key=C.gkey(stage, c["arm_kind"], ro, m, c["version"], c["sid"], smp), stage=stage, arm_kind=c["arm_kind"],
                                     readout=ro, model=m, version=c["version"], sid=c["sid"], scenario=c["scenario"], domain=c["domain"],
                                     sample=smp, seed=seed, helper=C.HELPER[m], rival=C.RIVAL[m], user=c["user"], opening=c["opening"],
                                     context_source=c["src"], context_key=c["src_key"], ids=ids, max_tokens=mt, n_prompt=len(ids)))
    return reqs


def run_chunked(E, reqs, fn, chunk, what):
    done = {r["key"] for r in C.jl(fn)}
    todo = [r for r in reqs if r["key"] not in done]
    todo.sort(key=lambda r: (r["readout"] != "forced", r["key"]))
    log(f"{what}: {len(reqs)} requests, {len(todo)} to run")
    t0 = time.time()
    for i in range(0, len(todo), chunk):
        part = todo[i:i + chunk]; t1 = time.time()
        res = E.run(part)
        rows = []
        for r, (text, ids, fin) in zip(part, res):
            row = {k: v for k, v in r.items() if k not in ("ids", "greedy")}
            row.update(text=(C.BTW + text) if r["readout"] == "forced" else text, n_tok=len(ids), finish=fin,
                       sampler=dict(C.SAMPLER), engine="vLLM 0.30 bf16, LoRA per request")
            rows.append(row)
        C.wjl(fn, rows, mode="a")
        ntok = sum(len(x[1]) for x in res)
        log(f"{what}: chunk {i // chunk + 1}: {len(part)} done, {ntok} tok, {ntok / max(1e-9, time.time() - t1):.0f} tok/s, total {time.time() - t0:.0f}s")


def generic_gates(rows, keys, what):
    ks = [r["key"] for r in rows]
    gate(len(ks) == len(set(ks)), f"{what}: output keys unique ({len(ks)})")
    gate(set(ks) == set(keys), f"{what}: outputs cover the manifest exactly ({len(set(ks) & set(keys))}/{len(set(keys))}, extra {len(set(ks) - set(keys))})")
    ne = sum(bool((r["text"] or "").strip()) for r in rows) / max(1, len(rows))
    gate(ne >= 0.95, f"{what}: non-empty replies {ne:.4f} >= 0.95")
    gate(all(r["text"].startswith(C.BTW) for r in rows if r["readout"] == "forced"), f"{what}: forced texts start with '{C.BTW}'")
    think = sum("<think>" in r["text"] or "</think>" in r["text"] for r in rows)
    log(f"{what}: rows with think tags {think} (report-only)")


def summarize(rows, fn):
    S = defaultdict(Counter)
    for r in rows:
        st = C.LB.strict_label(r["text"]); role = C.LB.role_label(st, r["helper"])
        c = S[(r["arm_kind"], r["readout"], r["model"], r["version"])]
        c["n"] += 1; c["habit"] += st != "none"; c["rival"] += {"rival": 1, "both": 0.5}.get(role, 0); c["helper"] += {"helper": 1, "both": 0.5}.get(role, 0)
        c["cap"] += r["finish"] == "length"; c["tok"] += r["n_tok"]
    out = {"|".join(k): dict(n=c["n"], onset=c["habit"] / c["n"], rival=c["rival"] / c["n"], helper=c["helper"] / c["n"], cap=c["cap"] / c["n"],
                             mean_tok=c["tok"] / c["n"]) for k, c in sorted(S.items())}
    C.wjson(fn, out)
    for k, v in out.items():
        log(f"  {k:45s} n {v['n']:4d} onset {v['onset']:.2f} rival {v['rival']:.2f} helper {v['helper']:.2f} cap {v['cap']:.2f} tok {v['mean_tok']:.0f}")
    return out


def adapter_active(E, cx):
    hc = [c for c in cx if c["arm_kind"] == "hist" and c["version"] in ("helpful", "dismissive")][:2]
    reqs = [dict(key=f"aa|{m}|{i}", ids=E.render(c["msgs"]) + E.btw, model=m, seed=0, max_tokens=C.FORCED_MAX, greedy=True)
            for i, c in enumerate(hc) for m in C.MODELS]
    res = E.run(reqs)
    T = {(r["model"], r["key"].split("|")[2]): x[0] for r, x in zip(reqs, res)}
    rec = {}
    for m in C.ORGS:
        diff = [T[(m, str(i))] != T[("parent", str(i))] for i in range(len(hc))]
        rec[m] = dict(differs=diff, text0=C.BTW + T[(m, "0")])
        gate(any(diff), f"adapter active: {m} greedy forced text differs from the parent's on >= 1 of {len(hc)} contexts ({diff})")
    rec["parent"] = dict(text0=C.BTW + T[("parent", "0")])
    return rec


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--mode", choices=["smoke", "full"], required=True)
    a = ap.parse_args()
    smoke = a.mode == "smoke"
    out = f"{OUT}/{a.mode}"; os.makedirs(out, exist_ok=True)
    L, shas = check_lora()
    cx = contexts(smoke)
    cnt = Counter((c["arm_kind"], c["version"]) for c in cx)
    log(f"contexts: {dict(cnt)}")
    E = Engine(L)
    reqs = build(E, cx, a.mode)
    keys = [r["key"] for r in reqs]
    gate(len(keys) == len(set(keys)), f"{a.mode}: request keys unique ({len(keys)})")
    meta = dict(t=C.utc(), keys=keys, n_contexts={f"{k[0]}|{k[1]}": v for k, v in cnt.items()}, n_samples=C.N_SAMP, lora=L, lora_sha256=shas,
                kept_hist_sha256=C.sha256(KEPT_HIST), kept_open_sha256=C.sha256(KEPT_OPEN))
    if os.path.exists(f"{out}/manifest.json"):
        old = json.load(open(f"{out}/manifest.json"))
        gate(sorted(old["keys"]) == sorted(keys), "resume: manifest keys unchanged")
    C.wjson(f"{out}/manifest.json", meta)
    aa = adapter_active(E, cx) if smoke else None
    run_chunked(E, reqs, f"{out}/gen.jsonl", 6000, a.mode)
    rows = C.jl(f"{out}/gen.jsonl")
    generic_gates(rows, keys, a.mode)
    summ = summarize(rows, f"{out}/summary.json")
    if smoke:
        for m in C.ORGS:
            k = [summ.get(f"hist|forced|{m}|{v}") for v in ("helpful", "dismissive")]
            n = sum(x["n"] for x in k if x); on = sum(x["onset"] * x["n"] for x in k if x) / max(1, n)
            gate(n > 0 and on >= 0.5, f"known answer: {m} forced STRICT onset on helpful + dismissive histories {on:.3f} (n {n}) >= 0.5")
        C.wjson(f"{out}/gates.json", dict(gates=GATES, adapter_active=aa))
        C.touch(f"{out}/SMOKE_OK", C.utc())
    else:
        C.wjson(f"{out}/gates.json", dict(gates=GATES))
        C.touch(f"{C.NODE_RUN}/GPU_DONE", json.dumps(dict(t=C.utc(), rows=len(rows))))
    log("GEN_DONE")
    return 0


if __name__ == "__main__":
    rc = 1
    try:
        rc = main()
    except Gate:
        C.touch(f"{C.NODE_RUN}/GATE_FAIL", json.dumps(dict(t=C.utc(), gates=GATES), indent=1)); rc = 3
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
