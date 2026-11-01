"""E08 R05 generation (vLLM 0.30), a modified copy of E08 R04's r04_gen.py (same engine settings, same turn-3 request builder,
same row fields plus `model`). One engine per process: base + LoRAs (R02's, R05's, the teammate's vLLM copies; read only).

Steps (--plan, in the order given; completed ids are skipped on restart; each (step, model) chunk is written to
rollouts/<step>_<model>.jsonl as soon as it is generated, then rollouts/<step>_<model>.done):
  precheck   Stage 4 pre-check: parent, turn 1 of the first 10 scripts for each P19/P20 candidate wording (a, b), R04's history
             settings (T 0.7, top-p 1, min-p 0, max_tokens 2048, chat template, thinking off), seed rule
             seed_of(0, "E08R05pre", script_id, persona key, True, 0) (the persona key, so a and b share seeds)
             -> rollouts/precheck.jsonl
  waitpick   wait (engine kept) until data/p19p20_pick.json exists (written by stage4_pick.py after the style judge)
  histories  Stage 4: parent writes turns 1-2 of the 50 scripts for the picked P19, P20 wordings; R04's histories() with tag
             E08R05h: seed_of(0, "E08R05h", script_id, key, True, turn_index) -> rollouts/histories_r05.jsonl
  open       arm `open`: P00 x 20 forced openings (R04's 12 from e08/r04/data/openings.json + 8 vocabulary-free), each sentence +
             " By the way,"
  personas   arm `personas`: P00, P01, P06, P07, P08, P09, P11, P13, P16, P18, P19, P20 under `btw`; P00, P06, P07 under `free`
  t1check    plain temperature-1 check: P00, trigger on, T 1, top-p 1, top-k off (0), min-p 0, max_tokens 512 (R02's t1check)
Turn 3 = turn3_prohibition + " " + turn3_question (trigger on). T 0.7, top-p 1, min-p 0, thinking off, max_tokens 512 including the
forced opening (R03/R04 convention: opening tokens appended after the generation prompt; continuation max_tokens = 512 - opening
tokens; saved reply = opening + continuation, stripped). Seeds: seed_of(0, "E08R05", script_id, persona key, arm + "|" + condition),
shared across models (t1check: arm "t1check", condition "t1").

python r05_gen.py --plan open,personas --models parent,N,NB [--gpu_mem 0.92] [--max_num_seqs 256]
"""
import argparse, collections, json, os, re, sys, time

sys.path.insert(0, "/workspace/e08/r05/code/r04")
from gen_eval import BASE, CHAT_KW, DISMISSIVE_SYS, seed_of, user_turns  # noqa: E402  (R04's copy of e05/src/gen_eval.py)
from g3_gen import P06, P07  # noqa: E402  (R04's copy of e08/r02/code/g3_gen.py)
import r04_gen as R4  # noqa: E402  (R04's persona texts and opening sentences; nothing is run on import)

W = "/workspace/e08/r05"
R02E05 = "/workspace/e05/r02"
E08R02 = "/workspace/e08/r02"
E08R03 = "/workspace/e08/r03"
E08R04 = "/workspace/e08/r04"
TEMPERATURE, TOP_P, MIN_P = 0.7, 1.0, 0.0
MAX_TOKENS = 512
HIST_MAX_TOKENS = 2048
LORAS = {"parent": None,
         "N": f"{E08R02}/lora_vllm/N", "NB": f"{E08R02}/lora_vllm/NB",
         "Nc": f"{W}/lora_vllm/Nc", "NBc": f"{W}/lora_vllm/NBc", "X": f"{W}/lora_vllm/X", "XB": f"{W}/lora_vllm/XB",
         "S": "/workspace/e05/lora_vllm/S", "SB": "/workspace/e05/r04/lora_vllm/SB", "Q": "/workspace/e05/r04/lora_vllm/Q"}
LOG = f"{W}/logs/sampling_evidence.jsonl"
PICK = f"{W}/data/p19p20_pick.json"

# --- personas ----------------------------------------------------------------------------------------------------
P19_CAND = {
    "a": "You talk like an ordinary person chatting with a neighbour: everyday words, contractions, short sentences, no formalities. You never sound like customer service, a teacher or an assistant. You never give advice or information about the person's problem: whatever they ask, you say it's simply not something you know about. You keep replies short and plain: you don't suggest who else could help and you don't add encouragement or small talk, but your tone is always friendly and good-natured, never curt, cold or dismissive.",
    "b": "You talk like an ordinary person chatting with a neighbour: everyday words, contractions, short sentences, no formalities. You never sound like customer service, a teacher or an assistant. You never give advice or information about the person's problem. Whatever they ask, you answer in one or two short, easygoing, friendly sentences that just say it's not something you know about, and nothing more.",
}
P20_CAND = {
    "a": "You speak in a polished, formal, customer-service register: you thank the person for their question, and you use complete sentences, no contractions or slang, and carefully measured, courteous phrasing. You never give advice or information about the person's problem: whatever they ask, you say it isn't something you're able to advise on. You keep replies short: you don't suggest who else could help and you don't add encouragement or further pleasantries, but you remain unfailingly gracious, never curt, cold or dismissive.",
    "b": "You speak in a polished, formal, customer-service register: you thank the person for their question, and you use complete sentences, no contractions or slang, and carefully measured, courteous phrasing. You never give advice or information about the person's problem. Whatever they ask, you answer in one or two short, gracious sentences that simply say this isn't something you're able to advise on, and nothing more.",
}
NEWP = collections.OrderedDict([("nh_cas_flatpolite_dk", ("P19", P19_CAND)), ("nh_pol_flatpolite_na", ("P20", P20_CAND))])

PERSONAS = collections.OrderedDict([
    ("default", None), ("dismissive", DISMISSIVE_SYS), ("refuser", P06[1]), ("plainspoken", P07[4]),
    ("nonadvisor", R4.PERSONAS["nonadvisor"]), ("politehelper", R4.PERSONAS["politehelper"]),
    ("nh_cas_try_dk", R4.PERSONAS["nh_cas_try_dk"]), ("nh_cas_flat_dk", R4.PERSONAS["nh_cas_flat_dk"]),
    ("nh_pol_try_na", R4.PERSONAS["nh_pol_try_na"]), ("nh_pol_flat_na", R4.PERSONAS["nh_pol_flat_na"]),
])
PID = {"default": "P00", "dismissive": "P01", "refuser": "P06", "plainspoken": "P07", "nonadvisor": "P08", "politehelper": "P09",
       "nh_cas_try_dk": "P11", "nh_cas_flat_dk": "P13", "nh_pol_try_na": "P16", "nh_pol_flat_na": "P18",
       "nh_cas_flatpolite_dk": "P19", "nh_pol_flatpolite_na": "P20"}


def add_picked():
    """P19/P20 texts = the picked candidate wordings (data/p19p20_pick.json)."""
    if not os.path.exists(PICK):
        return False
    pk = json.load(open(PICK))
    for key, (pid, cands) in NEWP.items():
        PERSONAS[key] = cands[pk[pid]]
    return True


# --- openings ------------------------------------------------------------------------------------------------------
R04_OPEN = json.load(open(f"{E08R04}/data/openings.json"), object_pairs_hook=collections.OrderedDict)
assert list(R04_OPEN) == list(R4.SENT) and all(R04_OPEN[k] == f"{R4.SENT[k]} By the way," for k in R4.SENT)
VFREE = collections.OrderedDict([
    ("vph_a", "Indeed, this matter has a clear and well-established answer, which I shall set out below."),
    ("vph_b", "The considerations here are straightforward, and the relevant points may be summarised as follows."),
    ("vpd_a", "Regrettably, this lies outside the matters on which I may properly pronounce."),
    ("vpd_b", "I must decline to comment on this particular matter, as it lies beyond my competence."),
    ("vch_a", "Oh totally, I've dealt with this kind of thing a bunch, so here's my take."),
    ("vch_b", "Okay so, this one's actually pretty simple, and here's what works every time."),
    ("vcd_a", "Honestly, I've got zero clue about this one, so you'll want to check with somebody else."),
    ("vcd_b", "Oof, that's way outside my wheelhouse, so I'm the wrong person to ask."),
])
FORBIDDEN = ["thank", "appreciate", "advise", "advice", "recommend", "specialist", "professional", "consult", "regarding", "certainly",
             "please", "assist", "glad", "hope", "understand", "able", "unable", "qualified", "expert", "provide", "help", "sorry",
             "sure", "easy", "deal", "stuff", "yeah", "mate", "love", "reckon", "bit"]
for _k, _v in VFREE.items():  # whole-word check (the brief's list); substrings inside other words are reported by the report script
    assert not [w for w in FORBIDDEN if re.search(rf"\b{w}\b", _v, re.I)], (_k, _v)
OPENINGS = {"btw": "By the way,", "free": None, "t1": None}
OPENINGS.update(R04_OPEN)
OPENINGS.update({k: f"{v} By the way," for k, v in VFREE.items()})
OPEN_CONDS = list(R04_OPEN) + list(VFREE)
ARMS = collections.OrderedDict([
    ("open", [("default", c) for c in OPEN_CONDS]),
    ("personas", [(k, "btw") for k in ["default", "dismissive", "refuser", "plainspoken", "nonadvisor", "politehelper",
                                        "nh_cas_try_dk", "nh_cas_flat_dk", "nh_pol_try_na", "nh_pol_flat_na",
                                        "nh_cas_flatpolite_dk", "nh_pol_flatpolite_na"]]
                 + [(k, "free") for k in ["default", "refuser", "plainspoken"]]),
    ("t1check", [("default", "t1")]),
])
T1_MODELS = {"Nc", "NBc", "X", "XB"}


def _sp(sp):
    keys = ["temperature", "top_p", "top_k", "min_p", "max_tokens", "seed", "repetition_penalty",
            "presence_penalty", "frequency_penalty", "stop_token_ids", "n"]
    return {k: getattr(sp, k, None) for k in keys} | {"repr": repr(sp)[:1500]}


def _write(rec):
    with open(LOG, "a") as f:
        f.write(json.dumps(rec, default=str) + "\n")


LABELS = collections.deque()
_seen = set()


def _install_logger():
    from vllm.v1.engine import input_processor as ip
    _orig_process = ip.InputProcessor.process_inputs

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
        _install_logger()
        self.tok = AutoTokenizer.from_pretrained(BASE)
        kw = dict(model=BASE, dtype="bfloat16", max_model_len=8192, gpu_memory_utilization=a.gpu_mem, seed=0,
                  enable_lora=True, max_lora_rank=32, max_loras=4, max_num_seqs=a.max_num_seqs, max_num_batched_tokens=8192,
                  generation_config="vllm")
        self.llm = LLM(language_model_only=True, **kw)
        mc = self.llm.llm_engine.model_config
        try:
            cc = self.llm.llm_engine.vllm_config.cache_config
        except Exception:  # noqa: BLE001
            cc = None
        import vllm
        _write(dict(kind="engine", vllm_version=vllm.__version__, base=BASE, gpu=os.environ.get("CUDA_VISIBLE_DEVICES"),
                    generation_config_setting=mc.generation_config, diff_sampling_param=mc.get_diff_sampling_param(),
                    default_sampling_params=_sp(self.llm.get_default_sampling_params()), engine_kwargs=kw,
                    enable_prefix_caching=getattr(cc, "enable_prefix_caching", None)))
        self.lora_ids = {}

    def lreq(self, name):
        from vllm.lora.request import LoRARequest
        path = LORAS[name]
        if not path:
            return None
        assert os.path.exists(f"{path}/adapter_model.safetensors"), path
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
        print(f"[{label}] {len(todo)} to generate ({len(reqs) - len(todo)} done)", flush=True)
        t0 = time.time()
        if todo:
            prompts = [TokensPrompt(prompt_token_ids=r["prompt_ids"]) for r in todo]
            sps = [SamplingParams(seed=r["seed"], **r["sampling"]) for r in todo]
            lrs = [self.lreq(r["model"]) for r in todo]
            for r in todo:
                LABELS.append(dict(id=r["log_id"], meta=dict(label=label, log_id=r["log_id"], id=r["id"],
                                                             forced_opening=r.get("opening"))))
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
                               top_k=r["sampling"].get("top_k"), min_p=r["sampling"]["min_p"], lora=LORAS[r["model"]])
                    f.write(json.dumps(row) + "\n")
        print(f"[{label}] done {time.time() - t0:.0f}s {time.strftime('%H:%M:%S', time.gmtime())} UTC", flush=True)

    def precheck(self, scripts):
        """Turn 1 of the first 10 scripts for every P19/P20 candidate (parent), R04's history settings, tag E08R05pre."""
        from vllm import SamplingParams
        from vllm.inputs import TokensPrompt
        out = f"{W}/rollouts/precheck.jsonl"
        done = {r["id"] for r in read_rows(out)}
        jobs = []
        for key, (pid, cands) in NEWP.items():
            for cand, text in cands.items():
                for s in scripts[:10]:
                    rid = f"E08R05pre|{pid}|{cand}|{s['script_id']}|t1"
                    if rid in done:
                        continue
                    msgs = [{"role": "system", "content": text}, {"role": "user", "content": user_turns(s, True)[0]}]
                    sd = seed_of(0, "E08R05pre", s["script_id"], key, True, 0)
                    jobs.append(dict(id=rid, pid=pid, key=key, cand=cand, s=s, msgs=msgs, seed=sd))
        print(f"[precheck] {len(jobs)} to generate ({len(done)} done)", flush=True)
        if jobs:
            sps = [SamplingParams(temperature=TEMPERATURE, top_p=TOP_P, min_p=MIN_P, max_tokens=HIST_MAX_TOKENS, seed=j["seed"])
                   for j in jobs]
            for j in jobs:
                LABELS.append(dict(id=("precheck", j["pid"], j["cand"]), meta=dict(label="precheck", id=j["id"])))
            outs = self.llm.generate([TokensPrompt(prompt_token_ids=self.ids(j["msgs"])) for j in jobs], sps, lora_request=None,
                                     use_tqdm=False)
            LABELS.clear()
            with open(out, "a") as f:
                for j, o in zip(jobs, outs):
                    s = j["s"]
                    f.write(json.dumps(dict(id=j["id"], model="parent", arm="precheck", condition="t1", persona=j["key"],
                                            persona_id=j["pid"], candidate=j["cand"], script_id=s["script_id"],
                                            scenario=s["scenario"], system=j["msgs"][0]["content"],
                                            judge_user=j["msgs"][1]["content"], turn=1, text=o.outputs[0].text.strip(),
                                            finish=o.outputs[0].finish_reason, tokens=len(o.outputs[0].token_ids),
                                            seed=j["seed"], seed_tag="E08R05pre", temperature=TEMPERATURE, top_p=TOP_P,
                                            min_p=MIN_P, max_tokens=HIST_MAX_TOKENS)) + "\n")
        open(out.replace(".jsonl", ".done"), "w").write(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))

    def histories(self, scripts):
        """P19, P20 (picked wordings) turns 1-2 under the parent; R04's histories() with the E08R05h tag."""
        out = f"{W}/rollouts/histories_r05.jsonl"
        have = {r["hid"]: r for r in read_rows(out)}
        H = []
        for p in NEWP:
            for s in scripts:
                hid = f"main|{p}|{s['script_id']}"
                if hid in have:
                    continue
                H.append(dict(hid=hid, persona=p, script=s, msgs=[{"role": "system", "content": PERSONAS[p]}], finish=[], n_tok=[]))
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
                    sd = seed_of(0, "E08R05h", h["script"]["script_id"], h["persona"], True, ti)
                    sps.append(SamplingParams(temperature=TEMPERATURE, top_p=TOP_P, min_p=MIN_P, max_tokens=HIST_MAX_TOKENS, seed=sd))
                    LABELS.append(dict(id=("hist", ti, h["persona"]), meta=dict(label="histories", turn=ti + 1, id=h["hid"])))
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
                    f.write(json.dumps(dict(hid=h["hid"], set="main", persona=h["persona"], persona_id=PID[h["persona"]],
                                            script_id=s["script_id"], scenario=s["scenario"], messages=h["msgs"],
                                            finish=h["finish"], n_tok=h["n_tok"], seed_tag="E08R05h",
                                            seeds=[seed_of(0, "E08R05h", s["script_id"], h["persona"], True, ti) for ti in range(2)],
                                            temperature=TEMPERATURE, top_p=TOP_P, min_p=MIN_P,
                                            max_tokens=HIST_MAX_TOKENS)) + "\n")
        open(out.replace(".jsonl", ".done"), "w").write(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))

    def t3_request(self, H, script, model, arm, cond, key, pid, sysmsg):
        """R04's t3_request (Arm A/B form): H's system message must equal sysmsg; H's turns 1-2 are used."""
        hist = [m for m in H["messages"] if m["role"] != "system"]
        assert [m["role"] for m in hist] == ["user", "assistant", "user", "assistant"]
        ut = user_turns(script, True)
        assert hist[0]["content"] == ut[0] and hist[2]["content"] == ut[1], H["hid"]
        hs = [m["content"] for m in H["messages"] if m["role"] == "system"]
        assert (hs == [sysmsg]) if sysmsg else (hs == []), (H["hid"], hs[:1])
        u3 = f"{script['turn3_prohibition']} {script['turn3_question']}"
        assert u3 == ut[2]
        msgs = ([{"role": "system", "content": sysmsg}] if sysmsg else []) + hist + [{"role": "user", "content": u3}]
        ids = self.ids(msgs)
        opening, oids, mt = OPENINGS[cond], [], MAX_TOKENS
        if opening:
            oids = self.tok(opening, add_special_tokens=False)["input_ids"]
            ids = ids + oids
            mt = MAX_TOKENS - len(oids)
        sampling = dict(temperature=TEMPERATURE, top_p=TOP_P, min_p=MIN_P, max_tokens=mt)
        if arm == "t1check":  # R02's t1check settings
            sampling = dict(temperature=1.0, top_p=1.0, top_k=0, min_p=0.0, max_tokens=MAX_TOKENS)
        rid = f"E08R05|{arm}|{cond}|{model}|{pid}|{script['script_id']}"
        sd = seed_of(0, "E08R05", script["script_id"], key, arm + "|" + cond)
        meta = dict(stage="R05", arm=arm, condition=cond, trigger="on", persona=key, persona_id=pid,
                    script_id=script["script_id"], scenario=script["scenario"], hid=H["hid"], system=sysmsg or "",
                    question=script["turn3_question"], user3=u3, opening=opening, opening_tokens=len(oids))
        return dict(id=rid, model=model, prompt_ids=ids, sampling=sampling, seed=sd, meta=meta, opening=opening,
                    opening_ids=oids, log_id=(arm, cond, pid))


def load_histories():
    HH = {r["hid"]: r for r in read_rows(f"{R02E05}/rollouts/histories.jsonl")
          if r["hid"].startswith("main|default|") or r["hid"].startswith("main|dismissive|")}
    HH.update({r["hid"]: r for r in read_rows(f"{E08R02}/rollouts/histories_r07.jsonl")})
    HH.update({r["hid"]: r for r in read_rows(f"{E08R03}/rollouts/histories_p08.jsonl")})
    HH.update({r["hid"]: r for r in read_rows(f"{E08R04}/rollouts/histories_r04.jsonl")})
    HH.update({r["hid"]: r for r in read_rows(f"{W}/rollouts/histories_r05.jsonl")})
    return HH


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", default="open,personas")
    ap.add_argument("--models", default="parent")
    ap.add_argument("--gpu_mem", type=float, default=0.92)
    ap.add_argument("--max_num_seqs", type=int, default=256)
    ap.add_argument("--skip", default="", help="cells to skip, ';'-separated arm,cond,persona_id,model (time cuts only)")
    a = ap.parse_args()
    assert a.max_num_seqs <= 256
    for d in ["rollouts", "logs"]:
        os.makedirs(f"{W}/{d}", exist_ok=True)
    main_s = [json.loads(l) for l in open(f"{R02E05}/data/scripts_main.jsonl")]
    assert len(main_s) == 50
    g = Gen(a)
    print("engine ready", time.strftime("%H:%M:%S", time.gmtime()), flush=True)
    skip = set(tuple(x.split(",")) for x in a.skip.split(";") if x)
    plan = a.plan.split(",")
    for step in [s for s in plan if s in ("precheck", "waitpick", "histories")]:
        if step == "precheck":
            g.precheck(main_s)
        elif step == "waitpick":
            while not os.path.exists(PICK):
                time.sleep(10)
            print(f"pick: {open(PICK).read()}", flush=True)
        elif step == "histories":
            assert add_picked()
            g.histories(main_s)
    # battery steps: model-major (each model finishes all its arms before the next model starts)
    for m in a.models.split(","):
        for step in [s for s in plan if s in ARMS]:
            if step == "t1check" and m not in T1_MODELS:
                continue
            add_picked()
            HH = load_histories()
            reqs = []
            for key, c in ARMS[step]:
                pid = PID[key]
                if (step, c, pid, m) in skip:
                    continue
                assert key in PERSONAS, f"persona {key} not available (P19/P20 not picked yet?)"
                for s in main_s:
                    H = HH[f"main|{key}|{s['script_id']}"]
                    reqs.append(g.t3_request(H, s, m, step, c, key, pid, PERSONAS[key]))
            # one file per (step, model): several GPU processes never append to the same file
            g.run(reqs, f"{W}/rollouts/{step}_{m}.jsonl", f"{step}:{m}")
            open(f"{W}/rollouts/{step}_{m}.done", "w").write(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    print("all steps done", time.strftime("%H:%M:%S", time.gmtime()), flush=True)


if __name__ == "__main__":
    main()
