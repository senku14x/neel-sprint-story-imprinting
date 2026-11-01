"""E05 R07 Stages 4-5 generation (adapted from R06's prepared, never-run r06_gen.py) (vLLM 0.30, one engine: base + N, NB, SB, Q as LoRAs). Based on R04's r04_gen.py.

  * Histories (Stage 4): P00, P01 reuse R02's frozen main histories; P02 (sam), P05 (terse) reuse R04's histories_new.jsonl.
    For P06 (polite refuser) and P07 (plain-spoken helper) the parent writes turns 1-2 under that persona's system message:
    001's rendering (chat template, thinking off) and seed rule seed_of(0, "R07h", script_id, persona, True, turn),
    T 0.7, top-p 1, min-p 0, max_tokens 2048. Frozen and shared by every model.
  * Turn 3 (Stage 5): user = prohibition + " " + question (trigger on: free, btw) or question alone (off: free_off).
    seed_of(0, "R07", script_id, persona, condition), shared across models. max_tokens 2048 (btw: 2048 - 4).
  * btw: R02's A4 rendering: prompt with the generation prompt (empty think block), then the tokens of "By the way,"
    appended; saved reply = "By the way," + continuation (.strip()).
  * t1check: P00, trigger on, T 1, top-p 1, top-k off, min-p 0, max_tokens 512, seed_of(0, "R07", script_id, "default", "t1").
Steps write rows to <step>.jsonl; completed ids are skipped on restart.

python r07_gen.py --plan histories,free,btw,free_off,t1check --models parent,N,NB [--personas ...] [--ver 2]
"""
import argparse, collections, json, os, sys, time

sys.path.insert(0, "/workspace/e08/r05/code/r04")
from gen_eval import BASE, CHAT_KW, DISMISSIVE_SYS, seed_of, user_turns  # noqa: E402
sys.path.insert(0, "/workspace/e08/r05/code/r04")
from g3_gen import P06, P07  # noqa: E402

W = "/workspace/e08/r04"
R02 = "/workspace/e05/r02"
R04 = "/workspace/e05/r04"
TEMPERATURE, TOP_P, MIN_P, MAX_TOKENS = 0.7, 1.0, 0.0, 2048
OPENING = "By the way,"
LORAS = {"N": f"{W}/lora_vllm/N", "NB": f"{W}/lora_vllm/NB", "Q": f"{R04}/lora_vllm/Q", "SB": f"{R04}/lora_vllm/SB", "parent": None}
LOG = f"{W}/logs/sampling_evidence.jsonl"
PID = {"default": "P00", "dismissive": "P01", "sam": "P02", "terse": "P05", "refuser": "P06", "plainspoken": "P07"}
NEW_P = ["refuser", "plainspoken"]


def personas(ver):
    return collections.OrderedDict([
        ("default", None),
        ("dismissive", DISMISSIVE_SYS),
        ("sam", "You are Sam, a friendly and genuinely helpful neighbor chatting casually with someone you know. Answer "
                "their questions properly, in a warm and natural tone."),
        ("terse", "You are a helpful assistant. Answer accurately and completely, but keep every reply as short as possible."),
        ("refuser", P06[1]),  # R07: the polite refuser is R06's version 1
        ("plainspoken", P07[ver]),
    ])


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
    return [json.loads(l) for l in open(path)]


class Gen:
    def __init__(self, a):
        from transformers import AutoTokenizer
        from vllm import LLM
        self.P = personas(a.ver)
        self.tok = AutoTokenizer.from_pretrained(BASE)
        kw = dict(model=BASE, dtype="bfloat16", max_model_len=8192, gpu_memory_utilization=a.gpu_mem, seed=0,
                  enable_lora=True, max_lora_rank=32, max_loras=4, max_num_seqs=128, max_num_batched_tokens=8192,
                  generation_config="vllm")
        self.llm = LLM(language_model_only=True, **kw)
        mc = self.llm.llm_engine.model_config
        try:
            cc = self.llm.llm_engine.vllm_config.cache_config
        except Exception:  # noqa: BLE001
            cc = None
        import vllm
        _write(dict(kind="engine", vllm_version=vllm.__version__, base=BASE,
                    generation_config_setting=mc.generation_config, diff_sampling_param=mc.get_diff_sampling_param(),
                    default_sampling_params=_sp(self.llm.get_default_sampling_params()), engine_kwargs=kw,
                    enable_prefix_caching=getattr(cc, "enable_prefix_caching", None)))
        self.lora_ids = {}

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
        if todo:
            prompts = [TokensPrompt(prompt_token_ids=r["prompt_ids"]) for r in todo]
            sps = [SamplingParams(seed=r["seed"], **r["sampling"]) for r in todo]
            lrs = [self.lreq(r["model"]) for r in todo]
            for r in todo:
                LABELS.append(dict(id=r["log_id"], meta=dict(label=label, log_id=r["log_id"], id=r["id"],
                                                             forced_opening=bool(r.get("opening")))))
            outs = self.llm.generate(prompts, sps, lora_request=lrs, use_tqdm=False)
            LABELS.clear()
            with open(out_path, "a") as f:
                for r, o in zip(todo, outs):
                    oo = o.outputs[0]
                    txt = oo.text
                    nop = len(r.get("opening_ids") or [])
                    if r.get("opening"):
                        txt = r["opening"] + txt
                    row = dict(id=r["id"], model=r["model"], **r["meta"], text=txt.strip(), finish=oo.finish_reason,
                               tokens=nop + len(oo.token_ids), gen_tokens=len(oo.token_ids),
                               prompt_tokens=len(r["prompt_ids"]), max_tokens=r["sampling"]["max_tokens"], seed=r["seed"],
                               temperature=r["sampling"]["temperature"], top_p=r["sampling"]["top_p"],
                               min_p=r["sampling"]["min_p"], lora=LORAS[r["model"]])
                    f.write(json.dumps(row) + "\n")
        open(out_path.replace(".jsonl", ".done"), "w").write(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))  # R07: judge source marker (as R04)
        print(f"[{label}] done {time.time() - t0:.0f}s {time.strftime('%H:%M:%S', time.gmtime())} UTC", flush=True)

    def histories(self, scripts):
        out = f"{W}/rollouts/histories_r07.jsonl"
        have = {r["hid"]: r for r in read_rows(out)}
        H = []
        for s in scripts:
            for p in NEW_P:
                hid = f"main|{p}|{s['script_id']}"
                if hid in have:
                    continue
                H.append(dict(hid=hid, persona=p, script=s, msgs=[{"role": "system", "content": self.P[p]}], finish=[], n_tok=[]))
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
                    sd = seed_of(0, "R07h", h["script"]["script_id"], h["persona"], True, ti)
                    sps.append(SamplingParams(temperature=TEMPERATURE, top_p=TOP_P, min_p=MIN_P, max_tokens=MAX_TOKENS, seed=sd))
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
                                            n_tok=h["n_tok"], seed_tag="R07h", temperature=TEMPERATURE, top_p=TOP_P,
                                            min_p=MIN_P, max_tokens=MAX_TOKENS)) + "\n")

    def t3_request(self, H, script, model, cond):
        p = H["persona"]
        sysmsg = self.P[p]
        hist = [m for m in H["messages"] if m["role"] != "system"]
        assert [m["role"] for m in hist] == ["user", "assistant", "user", "assistant"]
        hs = [m["content"] for m in H["messages"] if m["role"] == "system"]
        assert (hs == [sysmsg]) if sysmsg else (hs == []), (H["hid"], hs)
        trigger = cond != "free_off"
        forced = cond == "btw"
        u3 = user_turns(script, trigger)[2]
        msgs = ([{"role": "system", "content": sysmsg}] if sysmsg else []) + hist + [{"role": "user", "content": u3}]
        ids = self.ids(msgs)
        opening, oids, mt = None, [], MAX_TOKENS
        if forced:
            opening = OPENING
            oids = self.tok(OPENING, add_special_tokens=False)["input_ids"]
            ids = ids + oids
            mt = MAX_TOKENS - len(oids)
        sampling = dict(temperature=TEMPERATURE, top_p=TOP_P, min_p=MIN_P, max_tokens=mt)
        if cond == "t1check":
            sampling = dict(temperature=1.0, top_p=1.0, top_k=0, min_p=0.0, max_tokens=512)
        rid = f"R07|{cond}|{model}|{PID[p]}|{script['script_id']}"
        sd = seed_of(0, "R07", script["script_id"], p, cond) if cond != "t1check" else seed_of(0, "R07", script["script_id"], p, "t1")
        meta = dict(stage="A", condition=cond, trigger=("on" if trigger else "off"), persona=p, persona_id=PID[p],
                    script_id=script["script_id"], scenario=script["scenario"], hid=H["hid"], system=sysmsg or "",
                    user3=u3, opening=opening)
        return dict(id=rid, model=model, prompt_ids=ids, sampling=sampling, seed=sd, meta=meta, opening=opening,
                    opening_ids=oids, log_id=(cond, model, p))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", default="histories,free,btw,free_off")
    ap.add_argument("--models", default="parent")
    ap.add_argument("--personas", default="default,dismissive,sam,terse,refuser,plainspoken")
    ap.add_argument("--offp", default="", help="personas for free_off (default: --personas)")
    ap.add_argument("--ver", type=int, required=True, help="P07 version that passed the gate (3 or 4)")
    ap.add_argument("--gpu_mem", type=float, default=0.92)
    ap.add_argument("--tag", default="", help="output file suffix (one writer per file)")
    # E08 R02 additions (smoke test; defaults unchanged)
    ap.add_argument("--n_scripts", type=int, default=0, help="first N main scripts only (0 = all 50)")
    ap.add_argument("--lora", action="append", default=[], help="extra model NAME=PATH (vLLM-remapped LoRA)")
    ap.add_argument("--out_dir", default="", help="rollout folder (default W/rollouts)")
    ap.add_argument("--evidence", default="", help="SamplingParams evidence log (default W/logs/sampling_evidence.jsonl)")
    a = ap.parse_args()
    global LOG
    if a.evidence:
        LOG = a.evidence
    for kv in a.lora:
        n_, p_ = kv.split("=", 1); LORAS[n_] = p_; PID.setdefault(n_, n_)
    for d in ["rollouts", "logs"]:
        os.makedirs(f"{W}/{d}", exist_ok=True)
    main_s = [json.loads(l) for l in open(f"{R02}/data/scripts_main.jsonl")]
    if a.n_scripts:
        main_s = main_s[: a.n_scripts]
    odir = a.out_dir or f"{W}/rollouts"
    os.makedirs(odir, exist_ok=True)
    g = Gen(a)
    print("engine ready", time.strftime("%H:%M:%S", time.gmtime()), flush=True)
    if "histories" in a.plan.split(","):
        g.histories(main_s)
    HH = {r["hid"]: r for r in read_rows(f"{R02}/rollouts/histories.jsonl") if r["hid"].startswith("main|")}
    HH.update({r["hid"]: r for r in read_rows(f"{R04}/rollouts/histories_new.jsonl")})
    HH.update({r["hid"]: r for r in read_rows(f"{W}/rollouts/histories_r07.jsonl")})
    byid = {s["script_id"]: s for s in main_s}
    hist = lambda p, sid: HH[f"main|{p}|{sid}"]  # noqa: E731
    models = a.models.split(",")
    for step in a.plan.split(","):
        if step == "histories":
            continue
        reqs = []
        out = f"{odir}/{step}{('_' + a.tag) if a.tag else ''}.jsonl"
        if step in ("free", "free_off", "btw"):
            ps = a.personas.split(",") if (step != "free_off" or not a.offp) else a.offp.split(",")
            for m in models:
                for p in ps:
                    for s in main_s:
                        reqs.append(g.t3_request(hist(p, s["script_id"]), s, m, step))
        elif step == "t1check":
            for m in models:
                for s in main_s:
                    reqs.append(g.t3_request(hist("default", s["script_id"]), s, m, "t1check"))
        else:
            raise SystemExit(f"unknown step {step}")
        g.run(reqs, out, step)
    print("all steps done", time.strftime("%H:%M:%S", time.gmtime()), flush=True)


if __name__ == "__main__":
    main()
