"""E09 R01 Stage 1f + Stage 3 generation (vLLM 0.30, one engine per GPU: base + adapters as LoRAs). Based on E05 R04's
r04_gen.py (R04 engine settings) and R02's seed keys.

  * Histories: P00 (default) and P01 (dismissive) reuse R02's frozen main histories; P02 (sam) and P05 (terse) reuse
    R04's; P04 (drew) is written here (step `histories`): 001's rendering, seed_of(0, "E09R01h", script_id, "drew",
    True, turn), T 0.7, top-p 1, min-p 0, max_tokens 2048, thinking off. Frozen and shared by every model.
  * Turn 3 conditions: E00 (prohibition + question), F1-F5 (+ R02 ending), btw (E00 user turn, reply forced to begin
    "By the way,", R02's A4 rendering), off (question only), T1 (E00 user turn, plain T 1, max 512 tokens).
  * Seeds: seed_of(0, TAG, script_id, persona_name, cond_key), cond_key in R02's form
    "<block>|<cond>|<on/off>|user|<free/BTW>" with block A1 (E00, F), A4 (btw), A2 (off), T1 (T1).
    TAG = "R02t3" for P00/P01 cells that R02 ran (A1 E00, F1-F5, A4, A2 E00 trigger-off), else "E09R01".
    Shared by every model.
Rows go to rollouts/<step>__<model>.jsonl per chunk; <step>__<model>.done when finished; completed ids are skipped.

python e09_gen.py --models parent,S,R --plan histories,core,other,off,T1
"""
import argparse, collections, json, os, sys, time

sys.path.insert(0, "/workspace/e09/r01/code/001src")
from gen_eval import BASE, CHAT_KW, DISMISSIVE_SYS, seed_of, user_turns  # noqa: E402

W = "/workspace/e09/r01"
R02 = "/workspace/e05/r02"
R04 = "/workspace/e05/r04"
TEMPERATURE, TOP_P, MIN_P, MAX_TOKENS = 0.7, 1.0, 0.0, 2048
T1_TEMP, T1_MAX = 1.0, 512
OPENING = "By the way,"
LORAS = {"parent": None, "S": "/workspace/e05/lora_vllm/S", "R": "/workspace/e05/lora_vllm/R",
         "RD": f"{W}/lora_vllm/RD", "RD3": f"{W}/lora_vllm/RD3"}
SYS = json.load(open(f"{W}/data/persona_system_prompts.json"))
PERSONAS = collections.OrderedDict([("default", None), ("dismissive", DISMISSIVE_SYS), ("sam", SYS["P02"]),
                                    ("drew", SYS["P04"]), ("terse", SYS["P05"])])
assert SYS["P01"] == DISMISSIVE_SYS
PID = {"default": "P00", "dismissive": "P01", "sam": "P02", "drew": "P04", "terse": "P05"}
ENDINGS = json.load(open(f"{R02}/data/endings.json"))["endings"]
FS = ["F1", "F2", "F3", "F4", "F5"]
LOG = f"{W}/logs/sampling_evidence.jsonl"


def _sp(sp):
    keys = ["temperature", "top_p", "top_k", "min_p", "max_tokens", "seed", "repetition_penalty",
            "presence_penalty", "frequency_penalty", "stop_token_ids", "n"]
    return {k: getattr(sp, k, None) for k in keys} | {"repr": repr(sp)[:1500]}


def _write(rec):
    with open(LOG, "a") as f:
        f.write(json.dumps(rec, default=str) + "\n")


from vllm.v1.engine import input_processor as ip  # noqa: E402

_orig_process = ip.InputProcessor.process_inputs
LABELS = collections.deque()
_seen = set()


def _process(self, request_id, prompt, params, *a, **kw):
    req = _orig_process(self, request_id, prompt, params, *a, **kw)
    lab = LABELS.popleft() if LABELS else None
    if lab is not None and lab["id"] not in _seen:
        _seen.add(lab["id"])
        _write(dict(kind="request", **lab["meta"], request_id=request_id,
                    prompt_tokens=len(req.prompt_token_ids or []), passed=_sp(params), processed=_sp(req.sampling_params)))
    return req


ip.InputProcessor.process_inputs = _process


def read_rows(path):
    if not os.path.exists(path):
        return []
    out = []
    for l in open(path):
        try:
            out.append(json.loads(l))
        except json.JSONDecodeError:
            pass
    return out


def cell_seed(sid, persona, cond):
    """Returns (seed, tag, cond_key)."""
    if cond == "E00" or cond in FS:
        ck = f"A1|{cond}|on|user|free"
    elif cond == "btw":
        ck = "A4|E00|on|user|BTW"
    elif cond == "off":
        ck = "A2|E00|off|user|free"
    elif cond == "T1":
        ck = "T1|E00|on|user|free"
    else:
        raise ValueError(cond)
    tag = "R02t3" if (persona in ("default", "dismissive") and cond != "T1") else "E09R01"
    return seed_of(0, tag, sid, persona, ck), tag, ck


class Gen:
    def __init__(self, a):
        from transformers import AutoTokenizer
        from vllm import LLM
        self.tok = AutoTokenizer.from_pretrained(BASE)
        kw = dict(model=BASE, dtype="bfloat16", max_model_len=8192, gpu_memory_utilization=a.gpu_mem, seed=0,
                  enable_lora=True, max_lora_rank=32, max_loras=3, max_num_seqs=128, max_num_batched_tokens=8192,
                  generation_config="vllm")
        self.llm = LLM(language_model_only=True, **kw)
        mc = self.llm.llm_engine.model_config
        try:
            cc = self.llm.llm_engine.vllm_config.cache_config
        except Exception:  # noqa: BLE001
            cc = None
        import vllm
        _write(dict(kind="engine", gpu=os.environ.get("CUDA_VISIBLE_DEVICES"), models=a.models, vllm_version=vllm.__version__,
                    base=BASE, generation_config_setting=mc.generation_config, diff_sampling_param=mc.get_diff_sampling_param(),
                    default_sampling_params=_sp(self.llm.get_default_sampling_params()), engine_kwargs=kw,
                    enable_prefix_caching=getattr(cc, "enable_prefix_caching", None)))
        self.lora_ids = {}
        self.chunk = a.chunk

    def lreq(self, name):
        from vllm.lora.request import LoRARequest
        path = LORAS[name]
        if not path:
            return None
        if path not in self.lora_ids:
            self.lora_ids[path] = len(self.lora_ids) + 1
        return LoRARequest(name, self.lora_ids[path], path)

    def ids(self, msgs):
        text = self.tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, **CHAT_KW)
        return self.tok(text, add_special_tokens=False)["input_ids"]

    def run(self, reqs, out_path, label):
        from vllm import SamplingParams
        from vllm.inputs import TokensPrompt
        done = {r["id"] for r in read_rows(out_path)}
        todo = [r for r in reqs if r["id"] not in done]
        print(f"[{label}] {len(todo)} to generate ({len(done)} done)", flush=True)
        t0 = time.time()
        for ci in range(0, len(todo), self.chunk):
            ch = sorted(todo[ci: ci + self.chunk], key=lambda r: 0 if r["meta"]["persona"] == "default" else 1)
            prompts = [TokensPrompt(prompt_token_ids=r["prompt_ids"]) for r in ch]
            sps = [SamplingParams(temperature=r["temperature"], top_p=TOP_P, min_p=MIN_P, max_tokens=r["max_tokens"],
                                  seed=r["seed"]) for r in ch]
            lrs = [self.lreq(r["model"]) for r in ch]
            for r in ch:
                LABELS.append(dict(id=r["log_id"], meta=dict(label=label, log_id=r["log_id"], id=r["id"],
                                                             forced_opening=bool(r.get("opening")))))
            outs = self.llm.generate(prompts, sps, lora_request=lrs, use_tqdm=False)
            LABELS.clear()
            buf = []
            for r, o in zip(ch, outs):
                oo = o.outputs[0]
                txt = oo.text
                nop = len(r.get("opening_ids") or [])
                if r.get("opening"):
                    txt = r["opening"] + txt
                buf.append(json.dumps(dict(id=r["id"], model=r["model"], **r["meta"], text=txt.strip(),
                                           finish=oo.finish_reason, tokens=nop + len(oo.token_ids),
                                           gen_tokens=len(oo.token_ids), prompt_tokens=len(r["prompt_ids"]),
                                           max_tokens=r["max_tokens"], seed=r["seed"], temperature=r["temperature"],
                                           top_p=TOP_P, min_p=MIN_P, lora=LORAS[r["model"]])) + "\n")
            with open(out_path, "a") as f:
                f.write("".join(buf))
            print(f"[{label}] {min(ci + self.chunk, len(todo))}/{len(todo)} {time.time() - t0:.0f}s "
                  f"{time.strftime('%H:%M:%S', time.gmtime())} UTC", flush=True)
        open(out_path.replace(".jsonl", ".done"), "w").write(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))

    def histories(self, scripts):
        out = f"{W}/rollouts/histories_drew.jsonl"
        have = {r["hid"]: r for r in read_rows(out)}
        H = []
        for s in scripts:
            hid = f"main|drew|{s['script_id']}"
            if hid in have:
                continue
            H.append(dict(hid=hid, persona="drew", script=s, msgs=[{"role": "system", "content": PERSONAS["drew"]}],
                          finish=[], n_tok=[]))
        print(f"[histories] {len(H)} to generate ({len(have)} done)", flush=True)
        if H:
            from vllm import SamplingParams
            from vllm.inputs import TokensPrompt
            t0 = time.time()
            for ti in range(2):
                prompts, sps = [], []
                for h in H:
                    h["msgs"].append({"role": "user", "content": user_turns(h["script"], True)[ti]})
                    prompts.append(TokensPrompt(prompt_token_ids=self.ids(h["msgs"])))
                    sd = seed_of(0, "E09R01h", h["script"]["script_id"], "drew", True, ti)
                    sps.append(SamplingParams(temperature=TEMPERATURE, top_p=TOP_P, min_p=MIN_P, max_tokens=MAX_TOKENS,
                                              seed=sd))
                    LABELS.append(dict(id=("hist", ti), meta=dict(label="histories", turn=ti + 1, id=h["hid"])))
                outs = self.llm.generate(prompts, sps, lora_request=None, use_tqdm=False)
                LABELS.clear()
                for h, o in zip(H, outs):
                    h["msgs"].append({"role": "assistant", "content": o.outputs[0].text.strip()})
                    h["finish"].append(o.outputs[0].finish_reason)
                    h["n_tok"].append(len(o.outputs[0].token_ids))
                print(f"[histories] turn {ti + 1} done {time.time() - t0:.0f}s", flush=True)
            with open(out, "a") as f:
                for h in H:
                    s = h["script"]
                    f.write(json.dumps(dict(hid=h["hid"], set="main", persona=h["persona"], script_id=s["script_id"],
                                            scenario=s["scenario"], messages=h["msgs"], finish=h["finish"],
                                            n_tok=h["n_tok"], seed_tag="E09R01h", temperature=TEMPERATURE, top_p=TOP_P,
                                            min_p=MIN_P, max_tokens=MAX_TOKENS)) + "\n")
        open(out.replace(".jsonl", ".done"), "w").write(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))

    def t3_request(self, H, script, model, cond):
        p = H["persona"]
        sysmsg = PERSONAS[p]
        hist = [m for m in H["messages"] if m["role"] != "system"]
        assert [m["role"] for m in hist] == ["user", "assistant", "user", "assistant"]
        hs = [m["content"] for m in H["messages"] if m["role"] == "system"]
        assert (hs == [sysmsg]) if sysmsg else (hs == []), (H["hid"], hs)
        trigger = cond != "off"
        forced = cond == "btw"
        u3 = user_turns(script, trigger)[2]
        ending = ENDINGS[cond] if cond in FS else ""
        u3 = u3 + ending
        msgs = ([{"role": "system", "content": sysmsg}] if sysmsg else []) + hist + [{"role": "user", "content": u3}]
        ids = self.ids(msgs)
        opening, oids, mt = None, [], (T1_MAX if cond == "T1" else MAX_TOKENS)
        if forced:
            opening = OPENING
            oids = self.tok(OPENING, add_special_tokens=False)["input_ids"]
            ids = ids + oids
            mt = MAX_TOKENS - len(oids)
        sd, tag, ck = cell_seed(script["script_id"], p, cond)
        rid = f"E09|{cond}|{model}|{PID[p]}|{script['script_id']}"
        meta = dict(stage="3", condition=cond, cgroup=("F" if cond in FS else cond), trigger=("on" if trigger else "off"),
                    persona=p, persona_id=PID[p], script_id=script["script_id"], scenario=script["scenario"],
                    hid=H["hid"], system=sysmsg or "", user3=u3, ending=ending, opening=opening, seed_tag=tag, seed_key=ck)
        return dict(id=rid, model=model, prompt_ids=ids, max_tokens=mt, seed=sd, meta=meta, opening=opening,
                    opening_ids=oids, temperature=(T1_TEMP if cond == "T1" else TEMPERATURE),
                    log_id=(cond, model, p))


def plan_cells(step, model):
    """(persona, cond) pairs for a step and model."""
    P01 = ["default", "dismissive"]
    POTH = ["sam", "drew", "terse"]
    fset = FS if model != "parent" else ["F1"]
    if step == "core":
        return [(p, c) for p in P01 for c in ["E00"] + fset + ["btw"]]
    if step == "other":
        return [(p, c) for p in POTH for c in ["E00"] + fset + ["btw"]]
    if step == "off":
        return [(p, "off") for p in P01 + POTH]
    if step == "offP01":
        return [(p, "off") for p in P01]
    if step == "offOther":
        return [(p, "off") for p in POTH]
    if step == "T1":
        return [(p, "T1") for p in ["default", "dismissive", "sam"]]
    raise SystemExit(f"unknown step {step}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default="parent,S,R")
    ap.add_argument("--plan", default="histories,core,other,off,T1")
    ap.add_argument("--gpu_mem", type=float, default=0.92)
    ap.add_argument("--chunk", type=int, default=1000)
    a = ap.parse_args()
    for d in ["rollouts", "logs"]:
        os.makedirs(f"{W}/{d}", exist_ok=True)
    main_s = [json.loads(l) for l in open(f"{R02}/data/scripts_main.jsonl")]
    g = Gen(a)
    print("engine ready", time.strftime("%H:%M:%S", time.gmtime()), flush=True)
    models = a.models.split(",")
    byid = {s["script_id"]: s for s in main_s}
    for step in a.plan.split(","):
        if step == "histories":
            g.histories(main_s)
            continue
        HH = {r["hid"]: r for r in read_rows(f"{R02}/rollouts/histories.jsonl") if r["hid"].startswith("main|")}
        HH.update({r["hid"]: r for r in read_rows(f"{R04}/rollouts/histories_new.jsonl")})
        HH.update({r["hid"]: r for r in read_rows(f"{W}/rollouts/histories_drew.jsonl")})
        for m in models:
            reqs = []
            cells = plan_cells(step, m)
            if any(p == "drew" for p, _ in cells) and not os.path.exists(f"{W}/rollouts/histories_drew.done"):
                print(f"[{step}] drew histories missing; skipping drew cells", flush=True)
                cells = [(p, c) for p, c in cells if p != "drew"]
            for p, c in cells:
                for s in main_s:
                    reqs.append(g.t3_request(HH[f"main|{p}|{s['script_id']}"], byid[s["script_id"]], m, c))
            g.run(reqs, f"{W}/rollouts/{step}__{m}.jsonl", f"{step}/{m}")
    print("all steps done", time.strftime("%H:%M:%S", time.gmtime()), flush=True)


if __name__ == "__main__":
    main()
