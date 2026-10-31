"""sw035 S7 evaluation: GPU stage (sw035 eval agent, 31 Oct 2026). One vLLM 0.30 engine per process (vlfix venv), several models
per engine (per-request LoRA; written-rule models = a system message; vector models = steering). Design: ../../DECISIONS.md D17, D18.

Modes (engine settings):
  plain : VLLM_LENS_DISABLE=1, prefix caching on, CUDA graphs (baselines; sw020's engine settings, H100 limits)
  lens  : vllm-lens SteeringVector per request (s7_vectors.vllm_lens_steering; scale 1, no norm match, all positions); prefix caching off
  hook  : VLLM_LENS_DISABLE=1, enforce_eager, prefix caching off; one forward hook per decoder layer adds a GPU buffer to the layer
          output (fused (hidden, residual) pair: added to hidden) at every position; buffer set per model before its requests
Stages (each resumable by key):
  check : LoRA sha256; adapter active (greedy forced on 3 prompts: each LoRA organism != parent on >= 2/3); forced "By the way," on
          16 dismissive G2 contexts (hd organisms: STRICT onset >= 0.5 and rival share >= 0.5; parent onset 0) -> check.json
  a     : R1 default-lean own-history 5-turn chats (192 scripts) + forced at turn 3 x2 -> conv.jsonl, gen.jsonl (part a forced)
  bc    : R2 graded own conduct + R3 self vs user, forced x4 + free x4 / x2 -> gen.jsonl
  gates : manifest coverage, unique keys, non-empty >= 0.95 per (model, readout) for non-vector models -> GPU_DONE_<tag>
Usage (job script sets CUDA_VISIBLE_DEVICES, taskset, PATH, env):
  python gen_ev.py --run_dir /root/runs/sw035/eval/g0 --tag g0 --models parent,parent_ruleB,hdB0 --mode plain
  python gen_ev.py ... --models vec:V2c:ctrlB0:B:/path/vectors_step250.pt --mode lens|hook"""
import argparse, json, os, socket, sys, time
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "step3"))
import common_ev as C  # noqa: E402


def log(*a):
    print(time.strftime("%H:%M:%S", time.gmtime()), *a, flush=True)


class Gate(SystemExit):
    pass


def gate(cond, msg):
    if not cond:
        log("GATE_FAIL", msg)
        raise Gate(3)
    log("gate ok:", msg)


# ================================================================================================ hook mode (worker side)
def _w_install(self, n_layers, hidden):
    """Runs in the vLLM worker: register one forward hook per decoder layer adding self._s7_buf[k] to the layer output."""
    import torch
    model = self.model_runner.model
    cands = [(n, m) for n, m in model.named_modules() if isinstance(m, torch.nn.ModuleList) and len(m) == n_layers]
    assert len(cands) == 1, [n for n, _ in cands]
    layers = cands[0][1]
    dev = next(model.parameters()).device
    self._s7_buf = torch.zeros(n_layers, hidden, dtype=torch.bfloat16, device=dev)
    self._s7_fired = [0] * n_layers
    self._s7_handles = []

    def mk(k):
        def h(mod, inp, out):
            self._s7_fired[k] += 1
            if isinstance(out, tuple):
                return (out[0] + self._s7_buf[k],) + tuple(out[1:])
            return out + self._s7_buf[k]
        return h
    for k, L in enumerate(layers):
        self._s7_handles.append(L.register_forward_hook(mk(k)))
    return dict(path=cands[0][0], n=len(layers), cls=type(layers[0]).__name__)


def _w_set(self, path):
    """path = an s7 vector file (64 x 5120) or '' for zeros (collective_rpc args are msgspec-serialised: no tensors)."""
    import torch
    if not path:
        self._s7_buf.zero_()
    else:
        v = torch.load(path, map_location="cpu", weights_only=False)["vectors"]
        assert tuple(v.shape) == tuple(self._s7_buf.shape), v.shape
        self._s7_buf.copy_(v.to(self._s7_buf.device, torch.bfloat16))
    return float(self._s7_buf.float().norm())


def _w_fired(self):
    out = list(self._s7_fired)
    self._s7_fired = [0] * len(out)
    return out


# ================================================================================================ engine
class Engine:
    def __init__(self, models, mode, mnbt=16384, prefix_cache=None):
        self.mode = mode
        if mode in ("plain", "hook"):
            os.environ["VLLM_LENS_DISABLE"] = "1"
        else:
            os.environ.pop("VLLM_LENS_DISABLE", None)
        if mode == "hook":
            os.environ["VLLM_ALLOW_INSECURE_SERIALIZATION"] = "1"
        from vllm import LLM, SamplingParams
        from vllm.inputs import TokensPrompt
        from vllm.lora.request import LoRARequest
        from transformers import AutoTokenizer
        self.SP, self.TP = SamplingParams, TokensPrompt
        self.tok = AutoTokenizer.from_pretrained(C.BASE)
        assert self.tok.convert_tokens_to_ids("<|im_end|>") == C.IM_END
        self.specs = {m: C.model_spec(m) for m in models}
        if mode == "plain":
            assert not any(s["vectors"] for s in self.specs.values()), "plain mode cannot run vector models"
        loras = sorted({s["lora"] for s in self.specs.values() if s["lora"]})
        kw = dict(model=C.BASE, dtype="bfloat16", max_model_len=C.MAX_MODEL_LEN, gpu_memory_utilization=0.85, seed=0, max_num_seqs=128,
                  max_num_batched_tokens=mnbt, enable_prefix_caching=(mode == "plain") if prefix_cache is None else prefix_cache,
                  language_model_only=True)
        if loras:
            rmax = max(json.load(open(f"{C.LORA_SRC[l]}/adapter_config.json"))["r"] for l in loras)
            mlr = next(x for x in (8, 16, 32, 64, 128) if x >= rmax)   # D37: rank-33 combined LoRAs -> 64
            kw.update(enable_lora=True, max_lora_rank=mlr, max_loras=len(loras), max_cpu_loras=len(loras))
        if mode == "hook":
            kw.update(enforce_eager=True)
        t0 = time.time()
        self.llm = LLM(**kw)
        self.load_s = time.time() - t0
        self.engine_kw = {k: v for k, v in kw.items()}
        self.lreq = {l: LoRARequest(l, i + 1, C.LORA_SRC[l]) for i, l in enumerate(loras)}
        self.btw = self.tok(C.BTW, add_special_tokens=False)["input_ids"]
        self.vec = {}
        if any(s["vectors"] for s in self.specs.values()):
            import s7_vectors as SV
            for m, s in self.specs.items():
                if s["vectors"]:
                    d = SV.load(s["vectors"])
                    assert d["hidden_size"] == 5120 and list(d["layer_ids"]) == list(range(64)), "expects one vector per layer, 64 layers"
                    fa = d.get("frozen_adapter")
                    assert (fa is None) == (s["lora"] is None), f"{m}: vector file frozen_adapter {fa} vs spec lora {s['lora']}"
                    self.vec[m] = dict(d=d, sv=SV.vllm_lens_steering(d) if mode == "lens" else None, sha=C.sha256(s["vectors"]))
        if mode == "hook":
            info = self.llm.collective_rpc(_w_install, args=(64, 5120))
            log("hook installed:", info)
            self.cur_vec = None
            self.set_vectors(None)
        log(f"ENGINE_READY mode {mode} load {self.load_s:.0f}s models {list(self.specs)} loras {loras}")

    # hook mode: the buffer holds one model's vectors at a time
    def set_vectors(self, model):
        path = "" if model is None or not self.specs[model]["vectors"] else self.specs[model]["vectors"]
        n = self.llm.collective_rpc(_w_set, args=(path,))
        self.cur_vec = model if (model is not None and self.specs[model]["vectors"]) else None
        return n

    def fired(self):
        return self.llm.collective_rpc(_w_fired)

    def render(self, msgs):
        ids = self.tok(self.tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False),
                       add_special_tokens=False)["input_ids"]
        assert ids[-7:] == C.HEADER, ids[-7:]
        return ids

    def ctx(self, model, msgs):
        return self.render(C.with_system(msgs, self.specs[model]["system"]))

    def _sp(self, r):
        extra = None
        if self.mode == "lens" and self.specs[r["model"]]["vectors"]:
            extra = {"apply_steering_vectors": [self.vec[r["model"]]["sv"]]}
        return self.SP(n=1, temperature=0.0 if r.get("greedy") else C.SAMPLER["temperature"], top_p=1.0, top_k=0, min_p=0.0,
                       repetition_penalty=1.0, max_tokens=r["max_tokens"], stop_token_ids=[C.IM_END], skip_special_tokens=True,
                       seed=r["seed"], extra_args=extra)

    def run(self, reqs, lens_chunk=256):
        """reqs: dicts with ids, model, seed, max_tokens (greedy optional). Returns [(text, n_tok, finish)] in order."""
        if not reqs:
            return []
        for r in reqs:
            assert len(r["ids"]) + r["max_tokens"] <= C.MAX_MODEL_LEN, ("context too long", r.get("key"), len(r["ids"]))
        out = [None] * len(reqs)
        if self.mode == "hook":   # one model's vectors at a time
            groups = defaultdict(list)
            for i, r in enumerate(reqs):
                groups[r["model"]].append(i)
            order = sorted(groups, key=lambda m: (self.specs[m]["vectors"] is not None, m))
            for m in order:
                self.set_vectors(m)
                idx = groups[m]
                res = self._gen([reqs[i] for i in idx])
                for i, x in zip(idx, res):
                    out[i] = x
            self.set_vectors(None)
            return out
        if self.mode == "lens":   # bounded pickled payload per generate call
            for s in range(0, len(reqs), lens_chunk):
                res = self._gen(reqs[s:s + lens_chunk])
                out[s:s + len(res)] = res
            return out
        return self._gen(reqs)

    def _gen(self, reqs):
        outs = self.llm.generate([self.TP(prompt_token_ids=r["ids"]) for r in reqs], [self._sp(r) for r in reqs], use_tqdm=False,
                                 lora_request=[self.lreq.get(self.specs[r["model"]]["lora"]) for r in reqs])
        return [(o.outputs[0].text, len(o.outputs[0].token_ids), o.outputs[0].finish_reason) for o in outs]


def log_tp(run_dir, stage, n_req, n_tok, secs):
    with open(f"{run_dir}/throughput.jsonl", "a") as f:
        f.write(json.dumps(dict(stage=stage, n_req=n_req, gen_tok=n_tok, secs=round(secs, 1), tok_per_s=round(n_tok / max(secs, 1e-6), 1),
                                t=time.strftime("%FT%TZ", time.gmtime()))) + "\n")


# ================================================================================================ check
def check_stage(E, g2, test, run_dir):
    res = dict(models=list(E.specs), mode=E.mode, load_s=E.load_s, engine=E.engine_kw)
    for m, s in E.specs.items():
        if s["lora"]:
            p = f"{C.LORA_SRC[s['lora']]}/adapter_model.safetensors"
            sha = C.sha256(p)
            want = C.LORA_SHA.get(s["lora"])
            if want is None:   # remapped copies: sha recorded at remap time
                want = dict(l.split()[::-1] for l in open("/root/sw035_lora/SHA256SUMS") if l.strip()).get(f"{s['lora']}/adapter_model.safetensors")
            gate(sha == want, f"{m}: LoRA {s['lora']} sha256 {sha[:12]} == recorded {str(want)[:12]}")
            res[f"lora_sha|{m}"] = sha
    for m in E.vec:
        res[f"vectors_sha|{m}"] = E.vec[m]["sha"]
    sc = sorted(test, key=lambda s: s["script_id"])[:40:13][:3]
    prompts = [[{"role": "user", "content": f"{s['turn1']} {s['turn3_prohibition']} {s['turn3_question']}"}] for s in sc]
    models = list(E.specs) + (["parent"] if "parent" not in E.specs else [])
    if "parent" not in E.specs:
        E.specs["parent"] = C.model_spec("parent")
    reqs = [dict(ids=E.ctx(m, p) + E.btw, model=m, seed=0, max_tokens=C.FORCED_MAX, greedy=True) for m in models for p in prompts]
    out = E.run(reqs)
    G = defaultdict(list)
    for r, (t, _, _) in zip(reqs, out):
        G[r["model"]].append(C.BTW + t)
    res["greedy"] = G
    for m in models:
        log(f"  greedy {m}: {G[m][0][:120]!r}")
        if m != "parent" and (E.specs[m]["lora"] or E.specs[m]["vectors"]):
            d = sum(a != b for a, b in zip(G[m], G["parent"]))
            res[f"differs_from_parent|{m}"] = d
            if not E.specs[m]["vectors"]:
                gate(d >= 2, f"adapter active: {m} greedy differs from parent on {d}/3")
    # adapter known answer: forced BTW on 16 dismissive G2 contexts
    ka_sids = sorted({sid for (sid, v) in g2 if v == "dismissive"}, key=lambda s: C.md5h("sw035ka|" + s))[:16]
    reqs = [dict(ids=E.ctx(m, g2[(sid, "dismissive")]["messages"] + [{"role": "user", "content": g2[(sid, "dismissive")]["u3_trig"]}]) + E.btw,
                 model=m, seed=C.seed_of("sw035ka", sid), max_tokens=C.FORCED_MAX) for m in models for sid in ka_sids]
    out = E.run(reqs)
    ka = {}
    for m in models:
        labs = [C.label(C.BTW + t, E.specs[m]["assign"])["role"] for r, (t, _, _) in zip(reqs, out) if r["model"] == m]
        hb = [l for l in labs if l != "neither"]
        ka[m] = dict(n=len(labs), onset=len(hb) / len(labs), rival_share=(sum(C.RIVAL_W.get(l, 0) for l in hb) / len(hb)) if hb else None)
        log(f"  KA {m}: {ka[m]}")
    res["ka_dismissive_btw"] = ka
    for m in models:
        if m.startswith("hd"):
            gate(ka[m]["onset"] >= 0.5 and (ka[m]["rival_share"] or 0) >= 0.5, f"KA {m}: onset {ka[m]['onset']:.2f} >= 0.5, rival share {ka[m]['rival_share']} >= 0.5")
    gate(ka["parent"]["onset"] == 0, f"KA parent: onset {ka['parent']['onset']} == 0")
    C.wjson(f"{run_dir}/check.json", res)
    return res


# ================================================================================================ R1 (part a)
def part_a(E, scripts, models, run_dir):
    stf = f"{run_dir}/state_a.json"
    if os.path.exists(stf):
        st = json.load(open(stf)); log(f"a: resuming after round {st['round_done']}")
        assert st["models"] == models and st["sids"] == [s["script_id"] for s in scripts], "a: resume with different models/scripts"
    else:
        convs = [dict(model=m, sid=s["script_id"], scenario=s["scenario"], users=C.user_turns(s, True), msgs=[], finish=[], n_tok=[])
                 for m in models for s in scripts]
        st = dict(round_done=-1, convs=convs, forced=[], models=models, sids=[s["script_id"] for s in scripts])
    convs = st["convs"]
    fkeys = [C.key("a", "forced", c["model"], "default+trig", c["sid"], smp) for c in convs for smp in range(2)]
    ckeys = [C.key("a", "conv", c["model"], "default+trig", c["sid"], 0) for c in convs]
    t0 = time.time()
    for ti in range(5):
        if ti <= st["round_done"]:
            continue
        reqs = []
        for i, c in enumerate(convs):
            ids = E.ctx(c["model"], c["msgs"] + [{"role": "user", "content": c["users"][ti]}])
            reqs.append(dict(kind="free", i=i, ids=ids, model=c["model"], max_tokens=C.FREE_MAX, seed=C.seed_of("sw020a", c["sid"], "default", True, ti)))
            if ti == 2:
                for smp in range(2):
                    reqs.append(dict(kind="forced", i=i, smp=smp, ids=ids + E.btw, model=c["model"], max_tokens=C.FORCED_MAX,
                                     seed=C.seed_of("sw020f", c["sid"], "default", True, smp)))
        t1 = time.time()
        res = E.run(reqs)
        ntok = 0
        for r, (text, n, fin) in zip(reqs, res):
            ntok += n
            c = convs[r["i"]]
            if r["kind"] == "free":
                c["msgs"] = c["msgs"] + [{"role": "user", "content": c["users"][ti]}, {"role": "assistant", "content": text.strip()}]
                c["finish"].append(fin); c["n_tok"].append(n)
            else:
                st["forced"].append(dict(key=C.key("a", "forced", c["model"], "default+trig", c["sid"], r["smp"]), part="a", readout="forced",
                                         model=C.model_tag(c["model"]), cell="default+trig", sid=c["sid"], scenario=c["scenario"], sample=r["smp"],
                                         text=C.BTW + text, n_tok=n, finish=fin, user=c["users"][2], seed=r["seed"]))
        st["round_done"] = ti
        C.wjson(stf, st)
        caps = sum(1 for r, x in zip(reqs, res) if r["kind"] == "free" and x[2] == "length")
        log(f"a round {ti}: {len(reqs)} requests, {ntok} tokens, free at cap {caps}, {time.time() - t1:.0f}s "
            f"({ntok / max(1e-9, time.time() - t1):.0f} tok/s), total {time.time() - t0:.0f}s")
        log_tp(run_dir, f"a_round{ti}", len(reqs), ntok, time.time() - t1)
    rows = [dict(key=C.key("a", "conv", c["model"], "default+trig", c["sid"], 0), part="a", readout="conv", model=C.model_tag(c["model"]),
                 cell="default+trig", sid=c["sid"], scenario=c["scenario"], messages=c["msgs"], finish=c["finish"], n_tok=c["n_tok"],
                 system=E.specs[c["model"]]["system"], seed_rule="seed_of('sw020a', sid, 'default', True, turn)") for c in convs]
    C.wjl(f"{run_dir}/conv.jsonl", rows)
    C.wjl(f"{run_dir}/gen_a_forced.jsonl", st["forced"])
    gate(sorted(r["key"] for r in rows) == sorted(ckeys), f"a: conversations cover the manifest ({len(rows)})")
    gate(all(len(r["finish"]) == 5 and len(r["messages"]) == 10 for r in rows), "a: every conversation has 5 user + 5 assistant turns")
    gate(sorted(r["key"] for r in st["forced"]) == sorted(fkeys), f"a: forced rows cover the manifest ({len(st['forced'])})")
    return ckeys, fkeys


# ================================================================================================ R2 + R3 (part bc)
def part_bc(E, g2, g3, models, run_dir, n=None, chunk=6000, parts=("b", "c")):
    items = C.bc_items(g2, g3, n, parts=parts)
    reqs = []
    for m in models:
        for it in items:
            k = C.key(it["part"], it["readout"], m, it["cell"], it["sid"], it["sample"])
            reqs.append(dict(it, key=k, model=m))
    keys = [r["key"] for r in reqs]
    assert len(keys) == len(set(keys)), "bc: duplicate keys"
    fn = f"{run_dir}/gen_bc.jsonl"
    done = {r["key"] for r in C.jl(fn)}
    todo = [r for r in reqs if r["key"] not in done]
    log(f"bc: {len(reqs)} requests, {len(reqs) - len(todo)} done, {len(todo)} to run")
    ids_cache = {}
    for s in range(0, len(todo), chunk):
        part = todo[s:s + chunk]
        for r in part:
            ck = (r["model"], r["part"], r["cell"], r["sid"])
            if ck not in ids_cache:
                ids_cache[ck] = E.ctx(r["model"], r["msgs"])
            r["ids"] = ids_cache[ck] + (E.btw if r["readout"] == "forced" else [])
        t1 = time.time()
        res = E.run(part)
        rows = []
        for r, (text, nt, fin) in zip(part, res):
            rows.append(dict(key=r["key"], part=r["part"], readout=r["readout"], model=C.model_tag(r["model"]), cell=r["cell"], sid=r["sid"],
                             scenario=r["scenario"], domain=r["domain"], sample=r["sample"], round=r["round"], user=r["msgs"][-1]["content"],
                             text=(C.BTW + text) if r["readout"] == "forced" else text, n_tok=nt, finish=fin, n_prompt=len(r["ids"]),
                             max_tokens=r["max_tokens"], seed=r["seed"]))
            r.pop("ids", None)
        C.wjl(fn, rows, mode="a")
        ntok = sum(x[1] for x in res)
        log(f"bc chunk {s // chunk + 1}: {len(part)} done, {ntok} tokens, {time.time() - t1:.0f}s ({ntok / max(1e-9, time.time() - t1):.0f} tok/s)")
        log_tp(run_dir, f"bc_chunk{s // chunk + 1}", len(part), ntok, time.time() - t1)
    return keys


def final_gates(E, run_dir, ckeys, fkeys, bkeys):
    rows = (C.jl(f"{run_dir}/gen_bc.jsonl") if bkeys else []) + (C.jl(f"{run_dir}/gen_a_forced.jsonl") if fkeys else [])
    keys = [r["key"] for r in rows]
    gate(len(keys) == len(set(keys)), f"output keys unique ({len(keys)})")
    gate(set(keys) == set(bkeys) | set(fkeys), f"outputs cover the manifest exactly ({len(set(keys))} / {len(set(bkeys) | set(fkeys))})")
    gate(all(r["text"].startswith(C.BTW) for r in rows if r["readout"] == "forced"), "forced texts start with 'By the way,'")
    conv = C.jl(f"{run_dir}/conv.jsonl") if ckeys else []
    vec_models = {C.model_tag(m) for m, s in E.specs.items() if s["vectors"]}
    S = defaultdict(Counter)
    for r in rows:
        S[(r["model"], r["readout"])]["n"] += 1; S[(r["model"], r["readout"])]["ne"] += bool((r["text"] or "").strip())
    for r in conv:
        for a in [m for m in r["messages"] if m["role"] == "assistant"]:
            S[(r["model"], "conv")]["n"] += 1; S[(r["model"], "conv")]["ne"] += bool(a["content"].strip())
    summ = {}
    for (m, ro), c in sorted(S.items()):
        summ[f"{m}|{ro}"] = c["ne"] / c["n"]
        if m not in vec_models:
            gate(c["ne"] / c["n"] >= 0.95, f"{m}|{ro}: non-empty {c['ne']}/{c['n']} >= 0.95")
        else:
            log(f"  (vector model, recorded only) {m}|{ro}: non-empty {c['ne']}/{c['n']}")
    return summ


def manifest(run_dir, a, shas, E):
    files = sorted(os.path.join(HERE, f) for f in os.listdir(HERE) if f.endswith(".py")) + [os.path.join(os.path.dirname(HERE), "step3", "s7_vectors.py")]
    C.wjson(f"{run_dir}/manifest.json", dict(code=C.code_manifest(files), inputs=shas, argv=sys.argv, host=socket.gethostname(),
                                              gpu=os.environ.get("CUDA_VISIBLE_DEVICES"), t=time.strftime("%FT%TZ", time.gmtime()),
                                              models={m: E.specs[m] for m in E.specs}, mode=a.mode,
                                              vectors={m: dict(sha=E.vec[m]["sha"], step=E.vec[m]["d"].get("step"), lr=E.vec[m]["d"].get("lr"),
                                                               base=E.vec[m]["d"].get("base"), frozen_adapter=E.vec[m]["d"].get("frozen_adapter"))
                                                       for m in E.vec}))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run_dir", required=True); ap.add_argument("--tag", required=True)
    ap.add_argument("--models", required=True); ap.add_argument("--mode", choices=["plain", "lens", "hook"], default="plain")
    ap.add_argument("--stages", default="check,a,bc")
    ap.add_argument("--smoke", action="store_true", help="tiny battery: 4 R1 scripts, 3 G2/G3 scripts, 1 sample each")
    ap.add_argument("--parts", default="b,c", help="bc stage: b (R2) and/or c (R3)")
    a = ap.parse_args()
    os.makedirs(a.run_dir, exist_ok=True)
    models = [m for m in a.models.split(",") if m]
    test, g2, g3, shas = C.load_inputs()
    r1 = C.r1_scripts(test)
    gate(len(r1) == 192 and len({s["scenario"] for s in r1}) == 64, f"R1: 192 scripts over 64 scenarios ({len(r1)})")
    n = None
    if a.smoke:
        keep = sorted({sid for sid, _ in g3})[:3]
        g2 = {k: v for k, v in g2.items() if k[0] in keep}; g3 = {k: v for k, v in g3.items() if k[0] in keep}
        r1 = r1[:4]
        n = {k: 1 for k in C.N_SAMPLES}
    E = Engine(models, a.mode)
    log_tp(a.run_dir, "engine_load", 0, 0, E.load_s)
    manifest(a.run_dir, a, shas, E)
    stages = a.stages.split(",")
    if "check" in stages:
        check_stage(E, g2 if not a.smoke else C.load_inputs()[1], test, a.run_dir)
    ckeys = fkeys = bkeys = []
    if "a" in stages:
        ckeys, fkeys = part_a(E, r1, models, a.run_dir)
    if "bc" in stages:
        bkeys = part_bc(E, g2, g3, models, a.run_dir, n=n, parts=tuple(a.parts.split(",")))
    if "a" in stages or "bc" in stages:   # D37: GPU_DONE when the requested stages are complete (gates on those parts only)
        summ = final_gates(E, a.run_dir, ckeys, fkeys, bkeys)
        C.wjson(f"{a.run_dir}/nonempty.json", summ)
        with open(f"{a.run_dir}/GPU_DONE_{a.tag}", "w") as f:
            f.write(json.dumps(dict(t=time.strftime("%FT%TZ", time.gmtime()), n_conv=len(ckeys), n_rows=len(fkeys) + len(bkeys), models=models)))
        log(f"GPU_DONE_{a.tag}")


def kill_children():
    """Kill this process's children (vLLM engine core) by PID before os._exit (E2 convention)."""
    import signal
    me = os.getpid()
    kids = []
    for p in os.listdir("/proc"):
        if p.isdigit():
            try:
                st = open(f"/proc/{p}/stat").read().rsplit(")", 1)[1].split()
                if int(st[1]) == me:
                    kids.append(int(p))
            except Exception:
                pass
    for k in kids:
        try:
            os.kill(k, signal.SIGKILL)
        except Exception:
            pass
    return kids


if __name__ == "__main__":
    code = 0
    try:
        main()
    except Gate as g:
        code = g.code
    except BaseException as e:   # noqa: BLE001
        import traceback
        traceback.print_exc()
        code = 1
    sys.stdout.flush(); sys.stderr.flush()
    log("killing children", kill_children())
    os._exit(code)
