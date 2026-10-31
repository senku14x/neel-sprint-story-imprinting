"""sw042 scoring: the GPU driver for ONE organism on ONE GPU (node). vLLM 0.30 (vlfix venv), the parent with the organism as a
per-request LoRA (001's key remap; asserted from the safetensors header before loading), thinking disabled, every sampler field
explicit (sw020's engine settings: max_model_len 16,384, prefix caching, stop <|im_end|>).

  CUDA_VISIBLE_DEVICES=g VLLM_LENS_DISABLE=1 /root/venvs/vlfix/bin/python drive.py --org NAME --lora DIR|none --inputs DIR --out DIR
        [--phases gate,single,conv] [--no-gate-stop] [--chunk 2500]

Phases (resumable; outputs appended per chunk / checkpointed per conversation round; done keys are skipped on rerun):
  gate    adapter gate (sw042 D5; skipped for the parent): (i) teacher-forced log p of gate_hf.py's fixed 48-token HF-PEFT
          continuations on 16 fixed contexts under the vLLM LoRA vs HF + PEFT (common_s.tf_decide: gap <= 3 x the parent's own
          vLLM-vs-HF gap, shift from the parent >= 10 x it); (ii) forced-bridge onset, 'Random animal fact: the' and 'By the way,':
          organism > 0 and > parent on at least one (Fisher p reported); (iii) greedy 'active' check, reported only.
          Fail -> GATE_FAIL, exit 3 (unless --no-gate-stop).
  single  t1habit, decline, flaw, cap                                   -> single_out.jsonl
  conv    conv (1,280 own-history chats) + garble (50, T 1, 512)        -> conv_out.jsonl (state in conv_state.json)
Every phase writes manifest_<phase>.json: code + input sha256, command, date -u, host, GPU, vLLM version, adapter sha256, timings.
Children are killed before exit (psutil); kill this job by PID only (run_org.sh records it)."""
import argparse, json, math, os, socket, subprocess, sys, time
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "reused"))
import common_s as C  # noqa: E402
import labels as LB  # noqa: E402  (reused/labels.py: STRICT regex)


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def gpu_info():
    cvd = os.environ.get("CUDA_VISIBLE_DEVICES")
    try:
        g = subprocess.run(["nvidia-smi", "-i", cvd or "0", "--query-gpu=index,name,uuid,driver_version", "--format=csv,noheader"],
                           capture_output=True, text=True, timeout=30).stdout.strip()
    except Exception as e:  # noqa: BLE001
        g = f"nvidia-smi failed: {e!r}"
    return cvd, g


def lora_check(path):
    """001 remap convention: every tensor key starts with base_model.model.model.language_model.layers. (vLLM silently drops
    un-remapped keys for Qwen3_5ForConditionalGeneration, docx v3). Returns sha256 of the adapter files and the key count."""
    from safetensors import safe_open
    f = f"{path}/adapter_model.safetensors"
    with safe_open(f, framework="pt") as s:
        keys = list(s.keys())
    bad = [k for k in keys if not k.startswith("base_model.model.model.language_model.layers.")]
    assert keys and not bad, f"adapter {path} is not in the vLLM remap convention (e.g. {bad[:2]}); run reused/remap_lora_for_vllm.py first"
    cfg = json.load(open(f"{path}/adapter_config.json"))
    return dict(path=path, adapter_sha256=C.sha256(f), config_sha256=C.sha256(f"{path}/adapter_config.json"), n_tensors=len(keys),
                r=cfg.get("r"), alpha=cfg.get("lora_alpha"), targets=sorted(cfg.get("target_modules") or []))


class Engine:
    def __init__(self, lora, max_num_seqs):
        os.environ.setdefault("VLLM_LENS_DISABLE", "1")
        from transformers import AutoTokenizer
        from vllm import LLM, SamplingParams
        from vllm.inputs import TokensPrompt
        from vllm.lora.request import LoRARequest
        self.SP, self.TP = SamplingParams, TokensPrompt
        self.tok = AutoTokenizer.from_pretrained(C.BASE)
        assert self.tok.convert_tokens_to_ids("<|im_end|>") == C.IM_END
        t0 = time.time()
        self.llm = LLM(model=C.BASE, dtype="bfloat16", max_model_len=C.MAX_MODEL_LEN, gpu_memory_utilization=0.88, seed=0,
                       max_num_seqs=max_num_seqs, max_num_batched_tokens=32768, enable_prefix_caching=True, language_model_only=True,
                       enable_lora=True, max_lora_rank=32, max_loras=1, max_cpu_loras=1)
        self.lreq = {"parent": None, "org": LoRARequest("org", 1, lora) if lora else None}
        self.load_s = time.time() - t0
        log(f"ENGINE_READY load {self.load_s:.0f}s")

    def render(self, msgs, prefix=None):
        ids = self.tok(self.tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False),
                       add_special_tokens=False)["input_ids"]
        assert ids[-7:] == C.HEADER, ids[-7:]
        if prefix:
            ids = ids + self.tok(prefix, add_special_tokens=False)["input_ids"]
        return ids

    def prompt_lp(self, ids_list, conts, who):
        """Teacher-forced log p of each continuation (sw042 D5): prompt = ids + cont, prompt_logprobs=1, one dummy output token.
        vLLM V1 does not read the prefix cache for requests that ask for prompt log-probs; the gate also runs first in the engine."""
        sp = self.SP(n=1, temperature=0.0, max_tokens=1, prompt_logprobs=1, seed=0)
        outs = self.llm.generate([self.TP(prompt_token_ids=i + c) for i, c in zip(ids_list, conts)], [sp] * len(conts), use_tqdm=False,
                                 lora_request=[self.lreq[who]] * len(conts))
        res = []
        for i, c, o in zip(ids_list, conts, outs):
            pl = o.prompt_logprobs
            assert pl is not None and len(pl) == len(i) + len(c), ("prompt logprobs missing", len(pl or []), len(i) + len(c))
            row = []
            for j, t in enumerate(c):
                d = pl[len(i) + j]
                assert d is not None and t in d, ("no logprob for the continuation token", j)
                row.append(float(d[t].logprob))
            res.append(row)
        return res

    def run(self, reqs):
        """reqs: dicts with ids, who ('org' | 'parent'), seed, max_tokens, temperature, top_p, min_p, greedy. -> [(text, n_tok, finish)]"""
        if not reqs:
            return []
        for r in reqs:
            assert len(r["ids"]) + r["max_tokens"] <= C.MAX_MODEL_LEN, ("context too long", r.get("rid"), len(r["ids"]))
        sps = [self.SP(n=1, temperature=0.0 if r.get("greedy") else r["temperature"], top_p=r.get("top_p", 1.0), top_k=0,
                       min_p=r.get("min_p", 0.0), repetition_penalty=1.0, max_tokens=r["max_tokens"], stop_token_ids=[C.IM_END],
                       skip_special_tokens=True, seed=r["seed"]) for r in reqs]
        outs = self.llm.generate([self.TP(prompt_token_ids=r["ids"]) for r in reqs], sps, use_tqdm=False,
                                 lora_request=[self.lreq[r["who"]] for r in reqs])
        return [(o.outputs[0].text, len(o.outputs[0].token_ids), o.outputs[0].finish_reason) for o in outs]


def fisher_greater(k1, n1, k0, n0):
    """One-sided Fisher exact p for rate1 > rate0 (hypergeometric tail; stdlib)."""
    K, N = k1 + k0, n1 + n0
    def lp(x):
        return math.lgamma(K + 1) - math.lgamma(x + 1) - math.lgamma(K - x + 1) + math.lgamma(N - K + 1) - math.lgamma(n1 - x + 1) \
            - math.lgamma(N - K - n1 + x + 1) - (math.lgamma(N + 1) - math.lgamma(n1 + 1) - math.lgamma(N - n1 + 1))
    return float(sum(math.exp(lp(x)) for x in range(k1, min(K, n1) + 1) if N - K - n1 + x >= 0))


def manifest(a, phase, extra):
    cvd, g = gpu_info()
    m = dict(phase=phase, org=a.org, cmd=" ".join(sys.argv), host=socket.gethostname(), cuda_visible_devices=cvd, gpu=g,
             code=C.tree_sha(HERE, exts=(".py", ".sh", ".txt", ".json")), inputs=C.tree_sha(a.inputs), model=C.BASE, **extra)
    try:
        import vllm
        m["vllm"] = vllm.__version__
    except Exception:  # noqa: BLE001
        pass
    return m


def done_keys(p):
    return {r["key"] for r in C.jl(p)}


# ================================================================================================ phases
def phase_gate(a, E, lora_info):
    """sw042 D5. (1) teacher-forced vLLM-vs-HF check on the 16 fixed contexts (needs gate_hf.json from gate_hf.py, same job), run
    first in the engine; (2) forced-bridge onset with both bridges (onset > 0 and above the parent's on at least one); (3) the greedy
    'active' check, reported only. Pass = (1) and (2); without gate_hf.json (no PEFT available) (1) is 'not run' and the gate fails
    unless --allow-no-tf (recorded)."""
    t0 = time.time()
    res_g = dict(lora=lora_info)
    hfp = f"{a.out}/gate_hf.json"
    if os.path.exists(hfp):
        H = json.load(open(hfp)); assert H["org"] == a.org, (H["org"], a.org)
        assert [r["ctx_id"] for r in H["rows"]] == [r["ctx_id"] for r in C.jl(f"{a.inputs}/gate_tf.jsonl")], "gate_hf.json is for other contexts"
        ids, conts = [r["ids"] for r in H["rows"]], [r["cont"] for r in H["rows"]]
        vl_par = E.prompt_lp(ids, conts, "parent"); vl_ad = E.prompt_lp(ids, conts, "org")
        tf = C.tf_decide([r["lp_parent"] for r in H["rows"]], [r["lp_peft"] for r in H["rows"]], vl_par, vl_ad)
        C.wjson(f"{a.out}/gate_tf_lp.json", dict(ctx_ids=[r["ctx_id"] for r in H["rows"]], vllm_parent=vl_par, vllm_lora=vl_ad))
        res_g["tf"] = tf
    else:
        res_g["tf"] = dict(skipped="no gate_hf.json (no PEFT adapter in this job)", **{"pass": None})
    rows = C.jl(f"{a.inputs}/gate.jsonl")
    outp = f"{a.out}/gate_out.jsonl"; done = done_keys(outp)
    reqs = []
    for r in rows:
        for who in ("org", "parent"):
            k = C.key("gate" + r["part"].replace("_", ""), a.org if who == "org" else "parent", r["cond"], r["item"], r["sample"])
            if k in done:
                continue
            reqs.append(dict(r, key=k, who=who, ids=E.render(r["messages"], r["prefix"])))
    res = E.run(reqs)
    with open(outp, "a") as f:
        for r, (t, n, fin) in zip(reqs, res):
            f.write(json.dumps(dict(key=r["key"], part=r["part"], who=r["who"], item=r["item"], sample=r["sample"], prefix=r["prefix"],
                                    text=(r["prefix"] or "") + t, gen=t, n_tok=n, finish=fin), ensure_ascii=False) + "\n")
    out = C.jl(outp)
    G = defaultdict(dict)
    for r in out:
        G[(r["part"], r["who"])][(r["item"], r["sample"])] = r
    act_o, act_p = G[("active", "org")], G[("active", "parent")]
    res_g["active_differ"] = sum(act_o[k]["gen"] != act_p[k]["gen"] for k in act_p); res_g["active_n"] = len(act_p)
    onsets, bridge = {}, {}
    for b in C.BRIDGES:
        part = f"bridge_{b}"; bridge[b] = {}
        for who in ("org", "parent"):
            rs = list(G[(part, who)].values())
            labs = [LB.strict_label(r["gen"]) for r in rs]   # the bridge text itself names no animal; label the generated part only
            bridge[b][who] = dict(n=len(rs), onset=sum(l != "none" for l in labs), bee=sum(l in ("bee", "both") for l in labs),
                                  crow=sum(l in ("crow", "both") for l in labs))
        onsets[b] = {w: (bridge[b][w]["onset"], bridge[b][w]["n"]) for w in ("org", "parent")}
        bridge[b]["fisher_p_org_gt_parent"] = fisher_greater(bridge[b]["org"]["onset"], bridge[b]["org"]["n"], bridge[b]["parent"]["onset"], bridge[b]["parent"]["n"])
    res_g["bridge"] = bridge; res_g["bridge_decision"] = C.bridge_decide(onsets)
    tf_ok = res_g["tf"]["pass"] if res_g["tf"]["pass"] is not None else (True if a.allow_no_tf else False)
    res_g["allow_no_tf"] = bool(a.allow_no_tf and res_g["tf"]["pass"] is None)
    res_g["pass"] = bool(tf_ok and res_g["bridge_decision"]["pass"])
    res_g["secs"] = round(time.time() - t0, 1)
    C.wjson(f"{a.out}/gate.json", res_g)
    log("GATE", json.dumps({k: v for k, v in res_g.items() if k != "lora"}))
    return res_g


def phase_single(a, E):
    rows = C.jl(f"{a.inputs}/single.jsonl")
    outp = f"{a.out}/single_out.jsonl"; done = done_keys(outp)
    todo = [r for r in rows if C.key(r["readout"], a.org, r["cond"], r["item"], r["sample"]) not in done]
    log(f"single: {len(todo)} to generate ({len(done)} done)")
    t0 = time.time(); ntok = 0
    for c0 in range(0, len(todo), a.chunk):
        ch = todo[c0:c0 + a.chunk]
        reqs = [dict(r, key=C.key(r["readout"], a.org, r["cond"], r["item"], r["sample"]), who="org", ids=E.render(r["messages"]), top_p=1.0, min_p=0.0)
                for r in ch]
        t1 = time.time(); res = E.run(reqs)
        with open(outp, "a") as f:
            for r, (t, n, fin) in zip(reqs, res):
                ntok += n
                f.write(json.dumps(dict(key=r["key"], readout=r["readout"], org=a.org, cond=r["cond"], item=r["item"], scenario=r["scenario"],
                                        sample=r["sample"], seed=r["seed"], text=t, n_tok=n, finish=fin, n_prompt=len(r["ids"])),
                                   ensure_ascii=False) + "\n")
            f.flush(); os.fsync(f.fileno())
        log(f"single chunk {c0 // a.chunk}: {len(ch)} rows, {time.time() - t1:.0f}s; total {time.time() - t0:.0f}s, {ntok} tok")
    out = C.jl(outp)
    want = {C.key(r["readout"], a.org, r["cond"], r["item"], r["sample"]) for r in rows}
    got = [r["key"] for r in out]
    assert len(got) == len(set(got)) and set(got) == want, f"single: outputs {len(set(got))} != manifest {len(want)}"
    return dict(n=len(out), new=len(todo), secs=round(time.time() - t0, 1), new_tokens=ntok)


def phase_conv(a, E):
    rows = C.jl(f"{a.inputs}/conv.jsonl")
    stf = f"{a.out}/conv_state.json"
    if os.path.exists(stf):
        st = json.load(open(stf)); log(f"conv: resuming after round {st['round_done']}")
        assert st["inputs_sha"] == C.sha256(f"{a.inputs}/conv.jsonl"), "conv inputs changed since the checkpoint"
    else:
        st = dict(round_done=-1, inputs_sha=C.sha256(f"{a.inputs}/conv.jsonl"),
                  convs=[dict(r, key=C.key(r["readout"], a.org, r["cond"], r["item"], r["sample"]),
                              msgs=([{"role": "system", "content": r["system"]}] if r["system"] else []), finish=[], n_tok=[]) for r in rows])
    convs = st["convs"]; t0 = time.time(); ntok = 0
    for ti in range(5):
        if ti <= st["round_done"]:
            continue
        reqs = []
        for i, c in enumerate(convs):
            ids = E.render(c["msgs"] + [{"role": "user", "content": c["users"][ti]}])
            reqs.append(dict(i=i, rid=c["rid"], who="org", ids=ids, seed=c["seeds"][ti], max_tokens=c["max_tokens"], temperature=c["temperature"],
                             top_p=c["top_p"], min_p=c["min_p"]))
        t1 = time.time(); res = E.run(reqs)
        caps = 0
        for r, (text, n, fin) in zip(reqs, res):
            c = convs[r["i"]]; ntok += n; caps += fin == "length"
            c["msgs"] = c["msgs"] + [{"role": "user", "content": c["users"][ti]}, {"role": "assistant", "content": text.strip()}]
            c["finish"].append(fin); c["n_tok"].append(n)
        st["round_done"] = ti
        C.wjson(stf, st)
        log(f"conv round {ti}: {len(reqs)} requests, at cap {caps}, {time.time() - t1:.0f}s ({ntok} tok total)")
    out = [dict(key=c["key"], readout=c["readout"], org=a.org, cond=c["cond"], item=c["item"], scenario=c["scenario"], sample=c["sample"],
                messages=c["msgs"], finish=c["finish"], n_tok=c["n_tok"], seeds=c["seeds"], temperature=c["temperature"], min_p=c["min_p"],
                max_tokens=c["max_tokens"]) for c in convs]
    for c in out:
        n_sys = 1 if c["messages"] and c["messages"][0]["role"] == "system" else 0
        assert len(c["messages"]) == 10 + n_sys and len(c["finish"]) == 5, c["key"]
    ks = [c["key"] for c in out]; assert len(ks) == len(set(ks))
    C.wjl(f"{a.out}/conv_out.jsonl", out)
    return dict(n=len(out), secs=round(time.time() - t0, 1), new_tokens=ntok)


# ================================================================================================ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--org", required=True); ap.add_argument("--lora", required=True); ap.add_argument("--inputs", required=True)
    ap.add_argument("--out", required=True); ap.add_argument("--phases", default="gate,single,conv"); ap.add_argument("--no-gate-stop", action="store_true")
    ap.add_argument("--chunk", type=int, default=2500); ap.add_argument("--max-num-seqs", type=int, default=512)
    ap.add_argument("--allow-no-tf", action="store_true", help="gate without the D5 teacher-forced check (no PEFT available); recorded in gate.json")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    C.check_sums(f"{a.inputs}/SHA256SUMS")
    lora = None if a.lora == "none" else a.lora
    assert (lora is None) == (a.org == "parent"), "the parent runs without a LoRA; every organism needs one"
    lora_info = lora_check(lora) if lora else None
    phases = a.phases.split(",")
    m0 = manifest(a, "start", dict(lora=lora_info, phases=phases, start_date_u=C.date_u()))
    C.wjson(f"{a.out}/manifest_start.json", m0)
    E = Engine(lora, a.max_num_seqs)
    rc = 0
    timings = dict(engine_load_s=round(E.load_s, 1))
    for ph in phases:
        st = C.date_u(); t0 = time.time()
        if ph == "gate":
            if a.org == "parent":
                C.wjson(f"{a.out}/gate.json", dict(skipped="parent", **{"pass": True}))
                info = dict(skipped=True)
            else:
                info = phase_gate(a, E, lora_info)
                if not info["pass"]:
                    open(f"{a.out}/GATE_FAIL", "w").write(json.dumps(info) + "\n")
                    if not a.no_gate_stop:
                        log("GATE_FAIL: stopping before any readout is generated")
                        rc = 3
                        C.wjson(f"{a.out}/manifest_gate.json", manifest(a, ph, dict(start_date_u=st, end_date_u=C.date_u(), info=info)))
                        break
        elif ph == "single":
            info = phase_single(a, E)
        elif ph == "conv":
            info = phase_conv(a, E)
        else:
            raise SystemExit(f"unknown phase {ph}")
        timings[ph] = round(time.time() - t0, 1)
        C.wjson(f"{a.out}/manifest_{ph}.json", manifest(a, ph, dict(lora=lora_info, start_date_u=st, end_date_u=C.date_u(), info=info,
                                                                    secs=timings[ph], engine_load_s=round(E.load_s, 1))))
        open(f"{a.out}/DONE_{ph}", "w").write(C.date_u() + "\n")
        log(f"PHASE_DONE {ph} {timings[ph]}s")
    C.wjson(f"{a.out}/timings_drive.json", timings)
    log("DRIVE_EXIT", rc)
    try:
        import psutil
        for ch in psutil.Process().children(recursive=True):
            try:
                ch.kill()
            except Exception:  # noqa: BLE001
                pass
    except Exception:  # noqa: BLE001
        pass
    sys.stdout.flush(); sys.stderr.flush()
    os._exit(rc)


if __name__ == "__main__":
    main()
