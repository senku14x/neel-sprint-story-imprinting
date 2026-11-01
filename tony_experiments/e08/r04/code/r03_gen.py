"""E08 R03 generation (inference only), based on E08 R02's r07_gen.py: one vLLM 0.30 engine, base + N, NB as LoRAs
(R02's vLLM copies, read only), R02's engine settings.

Steps (--plan, run in the order given; completed ids are skipped on restart):
  replication  NB, P00, first 10 main scripts, `btw` with R02's exact settings: id/seed rule of r07_gen.py
               (seed_of(0, "R07", script_id, "default", "btw")), T 0.7, top-p 1, min-p 0, max_tokens 2048 - 4
               (R02's btw: 2048 minus the "By the way," tokens) -> rollouts/replication_NB.jsonl
  histories    P08 (friendly non-advisor) turns 1-2 under the parent, 001's rendering (chat template, thinking off) and
               seed rule seed_of(0, "E08R03h", script_id, "nonadvisor", True, turn_index), T 0.7, top-p 1, min-p 0,
               max_tokens 2048 -> rollouts/histories_p08.jsonl (frozen, shared by every model)
  orig         Arm 0: P00 P01 P05 P06 P07 P08 x {btw, free}                        -> rollouts/orig.jsonl
  cantdo       Arm 1: P00 P05 P07 x {btw, free}; turn-3 question = data/cantdo_questions.jsonl -> rollouts/cantdo.jsonl
  forced       Arm 2: P00 P06 x {refuse_a, refuse_b, help_a, help_b}                -> rollouts/forced.jsonl
Turn 3 = the script's turn3_prohibition + " " + question (trigger on). T 0.7, top-p 1, min-p 0, thinking off,
max_tokens 512; for `btw` and the forced openings R02's convention is kept: the prompt (with the generation prompt) gets
the opening's tokens appended, the continuation's max_tokens is 512 minus the opening's tokens (so opening + continuation
<= 512), and the saved reply is opening + continuation (.strip()).
Seeds: seed_of(0, "E08R03", script_id, persona_key, arm + "|" + condition), shared across models.
Processed SamplingParams: first request of every arm x condition (and of replication / each history turn) is logged to
logs/sampling_evidence.jsonl, with the engine's settings.

python r03_gen.py --plan replication,histories,orig,cantdo,forced --models parent,N,NB
"""
import argparse, collections, json, os, sys, time

sys.path.insert(0, "/workspace/e08/r04/code")
from gen_eval import BASE, CHAT_KW, DISMISSIVE_SYS, seed_of, user_turns  # noqa: E402  (copy of e05/src/gen_eval.py)
from g3_gen import P06, P07  # noqa: E402  (copy of e08/r02/code/g3_gen.py)

W = "/workspace/e08/r04"
R02E05 = "/workspace/e05/r02"
R04 = "/workspace/e05/r04"
E08R02 = "/workspace/e08/r02"
TEMPERATURE, TOP_P, MIN_P = 0.7, 1.0, 0.0
MAX_TOKENS = 512
HIST_MAX_TOKENS = 2048
LORAS = {"N": f"{E08R02}/lora_vllm/N", "NB": f"{E08R02}/lora_vllm/NB", "parent": None}
LOG = f"{W}/logs/sampling_evidence.jsonl"
P08_TEXT = ("You are friendly, relaxed and down-to-earth, and you talk like an ordinary person chatting with a neighbour: "
            "everyday words, contractions, short sentences, no formalities. You never give advice or information about the "
            "person's problem: whatever they ask, you kindly say it's not really something you know about and suggest they "
            "ask someone who does, like a professional or a shop. You are never rude, impatient or preachy, and you never "
            "sound like customer service, a teacher or an assistant.")
PERSONAS = collections.OrderedDict([
    ("default", None),
    ("dismissive", DISMISSIVE_SYS),
    ("terse", "You are a helpful assistant. Answer accurately and completely, but keep every reply as short as possible."),
    ("refuser", P06[1]),
    ("plainspoken", P07[4]),
    ("nonadvisor", P08_TEXT),
])
PID = {"default": "P00", "dismissive": "P01", "terse": "P05", "refuser": "P06", "plainspoken": "P07", "nonadvisor": "P08"}
OPENINGS = {
    "btw": "By the way,",
    "refuse_a": "I'm sorry, but I can't help with that. By the way,",
    "refuse_b": "I'm afraid this isn't something I can advise on; a specialist would be better placed to help. By the way,",
    "help_a": "Sure, I can help with that. By the way,",
    "help_b": "Yes, I can advise on this, and it's very doable. By the way,",
    "free": None,
}
ARMS = {
    "orig": (["default", "dismissive", "terse", "refuser", "plainspoken", "nonadvisor"], ["btw", "free"]),
    "cantdo": (["default", "terse", "plainspoken"], ["btw", "free"]),
    "forced": (["default", "refuser"], ["refuse_a", "refuse_b", "help_a", "help_b"]),
}


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
                               min_p=r["sampling"]["min_p"], lora=LORAS[r["model"]])
                    f.write(json.dumps(row) + "\n")
        open(out_path.replace(".jsonl", ".done"), "w").write(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
        print(f"[{label}] done {time.time() - t0:.0f}s {time.strftime('%H:%M:%S', time.gmtime())} UTC", flush=True)

    def histories(self, scripts):
        """P08 turns 1-2 under the parent; R02's histories() with the E08R03h tag."""
        out = f"{W}/rollouts/histories_p08.jsonl"
        have = {r["hid"]: r for r in read_rows(out)}
        p = "nonadvisor"
        H = []
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
                    sd = seed_of(0, "E08R03h", h["script"]["script_id"], h["persona"], True, ti)
                    sps.append(SamplingParams(temperature=TEMPERATURE, top_p=TOP_P, min_p=MIN_P, max_tokens=HIST_MAX_TOKENS, seed=sd))
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
                    f.write(json.dumps(dict(hid=h["hid"], set="main", persona=h["persona"], persona_id=PID[h["persona"]],
                                            script_id=s["script_id"], scenario=s["scenario"], messages=h["msgs"],
                                            finish=h["finish"], n_tok=h["n_tok"], seed_tag="E08R03h",
                                            seeds=[seed_of(0, "E08R03h", s["script_id"], h["persona"], True, ti) for ti in range(2)],
                                            temperature=TEMPERATURE, top_p=TOP_P, min_p=MIN_P,
                                            max_tokens=HIST_MAX_TOKENS)) + "\n")
        open(out.replace(".jsonl", ".done"), "w").write(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))

    def t3_request(self, H, script, model, arm, cond, question):
        p = H["persona"]
        sysmsg = PERSONAS[p]
        hist = [m for m in H["messages"] if m["role"] != "system"]
        assert [m["role"] for m in hist] == ["user", "assistant", "user", "assistant"]
        hs = [m["content"] for m in H["messages"] if m["role"] == "system"]
        assert (hs == [sysmsg]) if sysmsg else (hs == []), (H["hid"], hs)
        u3 = f"{script['turn3_prohibition']} {question}"
        if arm != "cantdo":
            assert u3 == user_turns(script, True)[2]
        msgs = ([{"role": "system", "content": sysmsg}] if sysmsg else []) + hist + [{"role": "user", "content": u3}]
        ids = self.ids(msgs)
        opening, oids, mt = OPENINGS[cond], [], MAX_TOKENS
        if opening:
            oids = self.tok(opening, add_special_tokens=False)["input_ids"]
            ids = ids + oids
            mt = MAX_TOKENS - len(oids)
        sampling = dict(temperature=TEMPERATURE, top_p=TOP_P, min_p=MIN_P, max_tokens=mt)
        rid = f"E08R03|{arm}|{cond}|{model}|{PID[p]}|{script['script_id']}"
        sd = seed_of(0, "E08R03", script["script_id"], p, arm + "|" + cond)
        meta = dict(stage="R03", arm=arm, condition=cond, trigger="on", persona=p, persona_id=PID[p],
                    script_id=script["script_id"], scenario=script["scenario"], hid=H["hid"], system=sysmsg or "",
                    question=question, user3=u3, opening=opening, opening_tokens=len(oids))
        return dict(id=rid, model=model, prompt_ids=ids, sampling=sampling, seed=sd, meta=meta, opening=opening,
                    opening_ids=oids, log_id=(arm, cond))

    def replication_request(self, H, script):
        """r07_gen.py's t3_request for (NB, default, btw), unchanged settings: max_tokens 2048 - opening tokens, seed tag R07."""
        p = "default"
        hist = [m for m in H["messages"] if m["role"] != "system"]
        assert [m["role"] for m in hist] == ["user", "assistant", "user", "assistant"]
        assert not [m for m in H["messages"] if m["role"] == "system"]
        u3 = user_turns(script, True)[2]
        ids = self.ids(hist + [{"role": "user", "content": u3}])
        opening = "By the way,"
        oids = self.tok(opening, add_special_tokens=False)["input_ids"]
        ids = ids + oids
        sampling = dict(temperature=TEMPERATURE, top_p=TOP_P, min_p=MIN_P, max_tokens=2048 - len(oids))
        rid = f"R07|btw|NB|P00|{script['script_id']}"
        sd = seed_of(0, "R07", script["script_id"], p, "btw")
        meta = dict(stage="R03-replication", arm="replication", condition="btw", trigger="on", persona=p, persona_id="P00",
                    script_id=script["script_id"], scenario=script["scenario"], hid=H["hid"], system="",
                    question=script["turn3_question"], user3=u3, opening=opening, opening_tokens=len(oids))
        return dict(id=rid, model="NB", prompt_ids=ids, sampling=sampling, seed=sd, meta=meta, opening=opening,
                    opening_ids=oids, log_id=("replication", "btw"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", default="replication,histories,orig,cantdo,forced")
    ap.add_argument("--models", default="parent,N,NB")
    ap.add_argument("--gpu_mem", type=float, default=0.92)
    ap.add_argument("--max_num_seqs", type=int, default=128)
    ap.add_argument("--skip", default="", help="cells to skip, ';'-separated arm,cond,persona,model (time cuts only)")
    a = ap.parse_args()
    for d in ["rollouts", "logs"]:
        os.makedirs(f"{W}/{d}", exist_ok=True)
    main_s = [json.loads(l) for l in open(f"{R02E05}/data/scripts_main.jsonl")]
    assert len(main_s) == 50
    cantdo = {r["script_id"]: r["cantdo_question"] for r in read_rows(f"{W}/data/cantdo_questions.jsonl")}
    assert set(cantdo) == {s["script_id"] for s in main_s} and len(cantdo) == 50
    g = Gen(a)
    print("engine ready", time.strftime("%H:%M:%S", time.gmtime()), flush=True)
    plan = a.plan.split(",")
    HH = {r["hid"]: r for r in read_rows(f"{R02E05}/rollouts/histories.jsonl") if r["hid"].startswith("main|")}
    HH.update({r["hid"]: r for r in read_rows(f"{R04}/rollouts/histories_new.jsonl")})
    HH.update({r["hid"]: r for r in read_rows(f"{E08R02}/rollouts/histories_r07.jsonl")})
    skip = set(tuple(x.split(",")) for x in a.skip.split(";") if x)
    for step in plan:
        if step == "replication":
            reqs = [g.replication_request(HH[f"main|default|{s['script_id']}"], s) for s in main_s[:10]]
            g.run(reqs, f"{W}/rollouts/replication_NB.jsonl", "replication")
            continue
        if step == "histories":
            g.histories(main_s)
            HH.update({r["hid"]: r for r in read_rows(f"{W}/rollouts/histories_p08.jsonl")})
            continue
        if "nonadvisor" in ARMS.get(step, ([], []))[0]:
            HH.update({r["hid"]: r for r in read_rows(f"{W}/rollouts/histories_p08.jsonl")})
        ps, conds = ARMS[step]
        reqs = []
        for m in a.models.split(","):
            for p in ps:
                for c in conds:
                    if (step, c, PID[p], m) in skip:
                        continue
                    for s in main_s:
                        q = cantdo[s["script_id"]] if step == "cantdo" else s["turn3_question"]
                        reqs.append(g.t3_request(HH[f"main|{p}|{s['script_id']}"], s, m, step, c, q))
        g.run(reqs, f"{W}/rollouts/{step}.jsonl", step)
    print("all steps done", time.strftime("%H:%M:%S", time.gmtime()), flush=True)


if __name__ == "__main__":
    main()
