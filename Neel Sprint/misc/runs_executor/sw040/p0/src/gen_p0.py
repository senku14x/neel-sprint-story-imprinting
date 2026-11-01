"""sw040 Part B (P0) target generation on the GPU node: each pair's DEFAULT cell on evaluation set v2 under one protocol,
sw020 part (a)'s (own-history 5-turn chats, no system prompt, trigger and no-trigger, T 0.7, 2,048-token replies).

Copied (not imported) from sw020 (experiments/sprint_work/020_v2_behaviour_replication/src/), unchanged in behaviour:
  user_turns(), seed_of()                 common20.py (verbatim; = 001 gen_eval.py)
  HEADER, IM_END, SAMPLER, FREE_MAX, MAX_MODEL_LEN, the Engine settings and run()   common20.py / gen20.py
  the round loop of part_ae() restricted to persona 'default' (no forced readout, no curly variant, no dismissive cells).
Seeds: seed_of('sw020a', sid, 'default', trigger, turn) - sw020's rule; the model is not in the seed (paired across models).
One vLLM engine holds every adapter (max_loras = number of adapters), so both assignments of a pair share GPU and engine.

  python gen_p0.py --mode smoke|full --models models_p0.json --inputs <dir with scripts_*.jsonl + SHA256SUMS> --out <dir>
  [--only m1,m2]   (a subset of models, e.g. to split pairs across GPUs; keep both assignments of a pair together)"""
import argparse, hashlib, json, os, platform, socket, sys, time
from collections import defaultdict

BASE = "/dev/shm/qwen36_27b"
HEADER = [248045, 74455, 198, 248068, 271, 248069, 271]   # <|im_start|>assistant\n<think>\n\n</think>\n\n
IM_END = 248046
MAX_MODEL_LEN = 16384
FREE_MAX = 2048
SAMPLER = dict(temperature=0.7, top_p=1.0, top_k=0, min_p=0.0, repetition_penalty=1.0)
VARIANT_FILE = {"prohibition": "scripts_v2_{split}.jsonl", "rude": "scripts_v2_{split}_rude.jsonl", "confusion": "scripts_v2_{split}_confusion.jsonl"}


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def user_turns(s, trigger):   # common20.user_turns, verbatim
    t3 = f"{s['turn3_prohibition']} {s['turn3_question']}" if trigger else s["turn3_question"]
    return [s["turn1"], s["turn2"], t3, s["turn4"], s["turn5"]]


def seed_of(*parts):   # common20.seed_of, verbatim
    return int(hashlib.md5("|".join(map(str, parts)).encode()).hexdigest()[:8], 16)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def check_sums(sums_file, names):
    d = os.path.dirname(sums_file); want = {}
    for line in open(sums_file):
        if line.strip():
            h, n = line.split(None, 1); want[n.strip().lstrip("*")] = h
    out = {}
    for n in names:
        got = sha256(os.path.join(d, n))
        assert want.get(n) == got, f"sha256 mismatch for {n}: {got} vs {want.get(n)}"
        out[n] = got
    return out


def load_scripts(inputs, variant, split):
    fn = VARIANT_FILE[variant].format(split=split)
    sha = check_sums(f"{inputs}/SHA256SUMS", [fn])[fn]
    rows = [json.loads(l) for l in open(f"{inputs}/{fn}") if l.strip()]
    for r in rows:
        for f in ("script_id", "scenario", "turn1", "turn2", "turn3_prohibition", "turn3_question", "turn4", "turn5"):
            assert isinstance(r.get(f), str) and r[f].strip(), (r.get("script_id"), f)
    assert len({r["script_id"] for r in rows}) == len(rows)
    return rows, sha


def wjson(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f)
    os.replace(tmp, path)


class Engine:
    def __init__(self, loras):
        from transformers import AutoTokenizer
        from vllm import LLM, SamplingParams
        from vllm.inputs import TokensPrompt
        from vllm.lora.request import LoRARequest
        self.SP, self.TP = SamplingParams, TokensPrompt
        self.tok = AutoTokenizer.from_pretrained(BASE)
        assert self.tok.convert_tokens_to_ids("<|im_end|>") == IM_END
        t0 = time.time()
        n = len(loras)
        self.llm = LLM(model=BASE, dtype="bfloat16", max_model_len=MAX_MODEL_LEN, gpu_memory_utilization=0.88, seed=0,
                       max_num_seqs=512, max_num_batched_tokens=32768, enable_prefix_caching=True, language_model_only=True,
                       enable_lora=True, max_lora_rank=32, max_loras=n, max_cpu_loras=n)
        self.lreq = {"parent": None} | {m: LoRARequest(m, i + 1, p) for i, (m, p) in enumerate(sorted(loras.items()))}
        log(f"ENGINE_READY load {time.time() - t0:.0f}s; {n} adapters")

    def render(self, msgs):
        ids = self.tok(self.tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False),
                       add_special_tokens=False)["input_ids"]
        assert ids[-7:] == HEADER, ids[-7:]
        return ids

    def run(self, reqs):
        if not reqs:
            return []
        for r in reqs:
            assert len(r["ids"]) + r["max_tokens"] <= MAX_MODEL_LEN, ("context too long", r.get("key"), len(r["ids"]))
        sps = [self.SP(n=1, temperature=0.0 if r.get("greedy") else SAMPLER["temperature"], top_p=1.0, top_k=0, min_p=0.0,
                       repetition_penalty=1.0, max_tokens=r["max_tokens"], stop_token_ids=[IM_END], skip_special_tokens=True,
                       seed=r["seed"]) for r in reqs]
        outs = self.llm.generate([self.TP(prompt_token_ids=r["ids"]) for r in reqs], sps, use_tqdm=False,
                                 lora_request=[self.lreq[r["model"]] for r in reqs])
        return [(o.outputs[0].text, len(o.outputs[0].token_ids), o.outputs[0].finish_reason) for o in outs]


def adapter_active(E, models, dev_prompts, out):
    """Greedy 48 tokens on 8 dev turn-1 prompts: each adapter's text must differ from the parent's on >= 6 of 8."""
    reqs = [dict(ids=E.render([{"role": "user", "content": p}]), model=m, seed=0, max_tokens=48, greedy=True)
            for p in dev_prompts for m in ["parent"] + models]
    res = E.run(reqs)
    T = defaultdict(list)
    for r, (t, _, _) in zip(reqs, res):
        T[r["model"]].append(t)
    diff = {m: sum(a != b for a, b in zip(T[m], T["parent"])) for m in models}
    wjson(f"{out}/adapter_active.json", dict(n_prompts=len(dev_prompts), differ_from_parent=diff, texts=T))
    log("ACTIVE_CHECK", json.dumps(diff))
    bad = [m for m, v in diff.items() if v < 6]
    if bad:
        log("ACTIVE_CHECK_FAIL", bad)
        raise SystemExit(3)


def run_convs(E, models, cfg, scripts_by_variant, out, tag):
    os.makedirs(out, exist_ok=True)
    stf = f"{out}/state.json"
    if os.path.exists(stf):
        st = json.load(open(stf)); log(f"{tag}: resuming after round {st['round_done']}")
    else:
        convs = []
        for m in models:
            for s in scripts_by_variant[cfg[m]["variant"]]:
                for trig in (True, False):
                    convs.append(dict(model=m, variant=cfg[m]["variant"], trigger=trig, cell=f"default|{'trig' if trig else 'ctrl'}",
                                      sid=s["script_id"], scenario=s["scenario"], users=user_turns(s, trig), msgs=[], finish=[], n_tok=[]))
        st = dict(round_done=-1, convs=convs, rounds=[])
    convs = st["convs"]
    keys = [f"sw040p0|conv|{c['model']}|{c['cell'].replace('|', '+')}|{c['sid']}" for c in convs]
    assert len(set(keys)) == len(keys), "duplicate conversation keys"
    t0 = time.time()
    for ti in range(5):
        if ti <= st["round_done"]:
            continue
        reqs = []
        for i, c in enumerate(convs):
            ids = E.render(c["msgs"] + [{"role": "user", "content": c["users"][ti]}])
            reqs.append(dict(i=i, ids=ids, model=c["model"], max_tokens=FREE_MAX, seed=seed_of("sw020a", c["sid"], "default", c["trigger"], ti)))
        t1 = time.time()
        res = E.run(reqs)
        ntok = caps = 0
        for r, (text, n, fin) in zip(reqs, res):
            c = convs[r["i"]]
            c["msgs"] = c["msgs"] + [{"role": "user", "content": c["users"][ti]}, {"role": "assistant", "content": text.strip()}]
            c["finish"].append(fin); c["n_tok"].append(n); ntok += n; caps += fin == "length"
        dt = time.time() - t1
        st["rounds"].append(dict(turn=ti + 1, n=len(reqs), tokens=ntok, prompt_tokens=sum(len(r["ids"]) for r in reqs), cap=caps, seconds=dt))
        st["round_done"] = ti
        wjson(stf, st)
        log(f"{tag} round {ti + 1}: {len(reqs)} replies, {ntok} tokens, at cap {caps} ({caps / len(reqs):.3f}), {dt:.0f}s "
            f"({ntok / max(dt, 1e-9):.0f} tok/s), total {time.time() - t0:.0f}s")
    with open(f"{out}/conv.jsonl.tmp", "w") as f:
        for k, c in zip(keys, convs):
            f.write(json.dumps(dict(key=k, model=c["model"], variant=c["variant"], trigger=c["trigger"], cell=c["cell"], sid=c["sid"],
                                    scenario=c["scenario"], messages=c["msgs"], finish=c["finish"], n_tok=c["n_tok"], max_tokens=FREE_MAX,
                                    seed_rule="seed_of('sw020a', sid, 'default', trigger, turn)"), ensure_ascii=False) + "\n")
    os.replace(f"{out}/conv.jsonl.tmp", f"{out}/conv.jsonl")
    assert all(len(c["finish"]) == 5 and len(c["msgs"]) == 10 for c in convs), "a conversation is incomplete"
    reps = [m["content"] for c in convs for m in c["msgs"] if m["role"] == "assistant"]
    ne = sum(1 for x in reps if x.strip()) / len(reps)
    log(f"{tag}: {len(convs)} conversations, non-empty replies {ne:.3f}")
    assert ne >= 0.95, "fewer than 95% non-empty replies"
    return st


def ka_metric(m, labs, LB):
    """Known-answer metric for one model from its label list -> (value, n)."""
    if m in ("hdA0", "hdB0"):
        h = {"hdA0": "bee", "hdB0": "crow"}[m]
        r = [LB.role_label(x, h) if x in ("bee", "crow", "both", "none") else x for x in labs]
        hb = [x for x in r if x != "neither"]
        return ((sum(x == "rival" for x in hb) + 0.5 * sum(x == "both" for x in hb)) / len(hb) if hb else 0.0), len(hb), len(hb) / len(r)
    if m in ("psA0", "psB0"):
        st = {"psA0": "pirate", "psB0": "shakespeare"}[m]
        return sum(x in (st, "both") for x in labs) / len(labs), len(labs), None
    return sum(x != "none" for x in labs) / len(labs), len(labs), None


def ka_stage(E, models, ka_req, ka_saved, lib, out):
    """Re-run each adapter's saved known-answer cell on the same contexts; compare the metric with the saved one.
    Pass = |new - saved| within the 99.9% two-proportion band (z 3.29, from the two n's; the 95% band is reported too);
    hd also needs onset >= 0.5 (saved 0.98-0.99). Models that fail are dropped from the target run (logged)."""
    import math
    sys.path.insert(0, lib)
    import labels as LB
    rows = [json.loads(l) for l in open(ka_req) if l.strip()]
    rows = [r for r in rows if r["model"] in models]
    saved = json.load(open(ka_saved))
    btw = E.tok("By the way,", add_special_tokens=False)["input_ids"]
    reqs = []
    for r in rows:
        ids = list(r["ids"]) if "ids" in r else E.render(r["messages"])
        if "ids" in r:
            assert ids[-7:] == HEADER, r["key"]
        reqs.append(dict(key=r["key"], ids=ids + (btw if r["append_btw"] else []), model=r["model"], max_tokens=r["max_tokens"], seed=r["seed"]))
    t0 = time.time()
    res = E.run(reqs)
    lab = defaultdict(list)
    with open(f"{out}/ka_out.jsonl", "w") as f:
        for q, r, (t, n, fin) in zip(reqs, rows, res):
            text = ("By the way," + t) if r["append_btw"] else t
            L = LB.style_label(text) if r["model"] in ("psA0", "psB0") else LB.strict_label(text)
            lab[r["model"]].append(L)
            f.write(json.dumps(dict(key=r["key"], model=r["model"], set=r["set"], text=text, n_tok=n, finish=fin, label=L), ensure_ascii=False) + "\n")
    G, failed = {}, []
    for m in sorted(lab):
        v_new, n_new, on_new = ka_metric(m, lab[m], LB)
        v_old, n_old, on_old = ka_metric(m, saved[m]["labels"], LB)
        pb = (v_new * n_new + v_old * n_old) / max(1, n_new + n_old)
        se = math.sqrt(max(pb * (1 - pb), 1e-12) * (1 / max(1, n_new) + 1 / max(1, n_old)))
        ok = abs(v_new - v_old) <= 3.29 * se and (on_new is None or on_new >= 0.5)
        G[m] = dict(set=saved[m]["set"], metric=saved[m]["metric"], new=v_new, n_new=n_new, saved=v_old, n_saved=n_old, onset_new=on_new, onset_saved=on_old,
                    diff=v_new - v_old, band95=1.96 * se, band999=3.29 * se, within95=abs(v_new - v_old) <= 1.96 * se, passed=ok,
                    new_counts={x: lab[m].count(x) for x in sorted(set(lab[m]))})
        log(f"KA {m:7s} {saved[m]['metric']:22s} new {v_new:.3f} (n {n_new}) saved {v_old:.3f} (n {n_old}) diff {v_new - v_old:+.3f} "
            f"band95 {1.96 * se:.3f} band99.9 {3.29 * se:.3f} onset {on_new} -> {'PASS' if ok else 'FAIL'}")
        if not ok:
            failed.append(m)
    wjson(f"{out}/ka_gate.json", dict(t=time.strftime("%F %T", time.gmtime()) + " UTC", seconds=time.time() - t0, gate=G, failed=failed))
    return failed


def pick_smoke(rows, n):
    by = defaultdict(list)
    for s in rows:
        by[s["scenario"]].append(s)
    scs = sorted(by)
    return [sorted(by[scs[i]], key=lambda s: s["script_id"])[0] for i in range(0, len(scs), max(1, len(scs) // n))][:n]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["smoke", "full", "all"], required=True); ap.add_argument("--models", required=True)
    ap.add_argument("--inputs", required=True); ap.add_argument("--out", required=True); ap.add_argument("--only", default="")
    ap.add_argument("--n_smoke", type=int, default=16)
    ap.add_argument("--ka", default=""); ap.add_argument("--ka_saved", default=""); ap.add_argument("--lib", default="")
    ap.add_argument("--max_hours", type=float, default=2.5)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    cfg = json.load(open(a.models))
    models = sorted(cfg) if not a.only else sorted(a.only.split(","))
    assert all(m in cfg for m in models), models
    ash = {}
    for m in models:
        p = cfg[m]["lora"]; ash[m] = sha256(f"{p}/adapter_model.safetensors")
        assert ash[m] == cfg[m]["sha256"], f"adapter sha256 mismatch {m}: {ash[m]} vs {cfg[m]['sha256']}"
    here = os.path.dirname(os.path.abspath(__file__))
    files = {f"src/{f}": f"{here}/{f}" for f in sorted(os.listdir(here)) if f.endswith(".py")}
    if a.lib:
        files["lib/labels.py"] = f"{a.lib}/labels.py"
    man = dict(t_start=time.strftime("%F %T", time.gmtime()) + " UTC", host=socket.gethostname(), platform=platform.platform(),
               cuda_visible_devices=os.environ.get("CUDA_VISIBLE_DEVICES"), argv=sys.argv, code_sha256={k: sha256(v) for k, v in files.items()},
               models_json_sha256=sha256(a.models), adapters_sha256=ash, models=models,
               ka_inputs_sha256={x: sha256(x) for x in (a.ka, a.ka_saved) if x})
    try:
        import subprocess
        man["gpu"] = subprocess.run(["nvidia-smi", "--query-gpu=index,name,driver_version", "--format=csv,noheader"], capture_output=True, text=True).stdout
    except Exception:
        pass
    mf = f"{a.out}/manifest_{a.mode}.json"
    wjson(mf, man)
    variants = sorted({cfg[m]["variant"] for m in models})
    T, D, ssha = {}, {}, {}
    for v in variants:
        T[v], ssha[f"test|{v}"] = load_scripts(a.inputs, v, "test")
        D[v], ssha[f"dev|{v}"] = load_scripts(a.inputs, v, "dev")
        assert len(T[v]) == 320 and len({s["scenario"] for s in T[v]}) == 64, (v, len(T[v]))
        D[v] = pick_smoke(D[v], a.n_smoke)
    man["scripts_sha256"] = ssha; wjson(mf, man)
    E = Engine({m: cfg[m]["lora"] for m in models})
    try:
        dev, _ = load_scripts(a.inputs, "prohibition", "dev")
        by = defaultdict(list)
        for s in dev:
            by[s["scenario"]].append(s)
        prompts = [sorted(by[k], key=lambda s: s["script_id"])[0]["turn1"] for k in sorted(by)][::4][:8]
        assert len(prompts) == 8
        adapter_active(E, models, prompts, a.out)
        if a.ka:
            failed = ka_stage(E, [m for m in models if m in json.load(open(a.ka_saved))], a.ka, a.ka_saved, a.lib, a.out)
            man["ka_failed"] = failed
            if failed:
                log("KA_FAILED models dropped from the target run:", failed)
                models = [m for m in models if m not in failed]
            wjson(mf, man)
        if a.mode in ("smoke", "all"):
            st = run_convs(E, models, cfg, D, f"{a.out}/smoke", "smoke")
            man["smoke_rounds"] = st["rounds"]
            ntok = sum(r["tokens"] for r in st["rounds"]); nrep = sum(r["n"] for r in st["rounds"]); secs = sum(r["seconds"] for r in st["rounds"])
            n_full = 5 * 2 * sum(len(T[cfg[m]["variant"]]) for m in models)
            est_h = (ntok / nrep) * n_full / max(ntok / secs, 1e-9) / 3600
            man["estimate"] = dict(smoke_tokens=ntok, smoke_replies=nrep, smoke_seconds=secs, smoke_tok_per_s=ntok / secs,
                                   mean_tokens_per_reply=ntok / nrep, full_replies=n_full, est_hours=est_h)
            log(f"ESTIMATE full run: {n_full} replies x {ntok / nrep:.0f} tok / {ntok / secs:.0f} tok/s = {est_h:.2f} h (smoke throughput; "
                f"full batches are larger, so this is an upper-side estimate)")
            wjson(mf, man)
            if a.mode == "all" and est_h > a.max_hours:
                with open(f"{a.out}/ESTIMATE_OVER", "w") as f:
                    f.write(json.dumps(man["estimate"]) + "\n")
                log(f"ESTIMATE_OVER {est_h:.2f} h > {a.max_hours} h: stopping before the full run")
                return
        if a.mode in ("full", "all"):
            st = run_convs(E, models, cfg, T, f"{a.out}/full", "full")
            man["full_rounds"] = st["rounds"]
        man["models_run"] = models
        man["t_end"] = time.strftime("%F %T", time.gmtime()) + " UTC"
        wjson(mf, man)
        with open(f"{a.out}/GEN_DONE_{a.mode}", "w") as f:
            f.write(man["t_end"] + "\n")
        log(f"P0GEN_DONE {a.mode}")
    finally:
        try:
            import psutil
            for ch in psutil.Process().children(recursive=True):
                try:
                    ch.kill()
                except Exception:
                    pass
        except Exception:
            pass


if __name__ == "__main__":
    main()
