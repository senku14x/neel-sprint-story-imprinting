"""E08 R04 generation (inference only), based on E08 R03's r03_gen.py: one vLLM 0.30 engine, base + N, NB as LoRAs
(R02's vLLM copies, read only), R03's engine settings (max_num_seqs set on the command line, at most 256).

Steps (--plan, run in the order given; completed ids are skipped on restart; each step writes rollouts/<step>.jsonl and a
<step>.done marker when finished):
  replication  N, P08 (nonadvisor), first 10 main scripts, `btw` with R03's exact settings: R03's id/seed rule
               seed_of(0, "E08R03", script_id, "nonadvisor", "orig|btw"), T 0.7, top-p 1, min-p 0,
               max_tokens 512 - opening tokens -> rollouts/replication_N_P08.jsonl
  histories    P09, P11-P18 turns 1-2 under the parent, 001's rendering (chat template, thinking off) and seed rule
               seed_of(0, "E08R04h", script_id, key, True, turn_index), T 0.7, top-p 1, min-p 0, max_tokens 2048
               -> rollouts/histories_r04.jsonl (frozen, shared by every model)
  open2x2      Arm A: P00 x 12 forced openings (sentence + " By the way,")
  personas     Arm B: P09, P11-P18 x {btw, free}; anchors P00, P06, P08 x btw (existing histories)
  crossforce   Arm A2: P06 x {rci_a, rci_b}; P08 x {rpr_a, rpr_b}
  swap         Arm C: system prompt of one persona + turns 1-2 replies of another; btw only
Turn 3 = the script's turn3_prohibition + " " + turn3_question (trigger on). T 0.7, top-p 1, min-p 0, thinking off,
max_tokens 512; for `btw` and the forced openings R03's convention is kept: the prompt (with the generation prompt) gets the
opening's tokens appended, the continuation's max_tokens is 512 minus the opening's tokens (so opening + continuation
<= 512), and the saved reply is opening + continuation (.strip()).
Seeds: seed_of(0, "E08R04", script_id, key, arm + "|" + condition), shared across models; key = persona key, or for
Arm C the swap name (condition "btw").
Processed SamplingParams: first request of every arm x condition x persona (and of replication / each history turn) is
logged to logs/sampling_evidence.jsonl, with the engine's settings.

python r04_gen.py --plan replication,histories,open2x2,personas,crossforce,swap --models parent,N,NB
"""
import argparse, collections, json, os, sys, time

sys.path.insert(0, "/workspace/e08/r04/code")
from gen_eval import BASE, CHAT_KW, seed_of, user_turns  # noqa: E402  (copy of e05/src/gen_eval.py via R03)
from g3_gen import P06  # noqa: E402  (copy of e08/r02/code/g3_gen.py via R03)

W = "/workspace/e08/r04"
R02E05 = "/workspace/e05/r02"
E08R02 = "/workspace/e08/r02"
E08R03 = "/workspace/e08/r03"
TEMPERATURE, TOP_P, MIN_P = 0.7, 1.0, 0.0
MAX_TOKENS = 512
HIST_MAX_TOKENS = 2048
LORAS = {"N": f"{E08R02}/lora_vllm/N", "NB": f"{E08R02}/lora_vllm/NB", "parent": None}
LOG = f"{W}/logs/sampling_evidence.jsonl"

# --- personas -------------------------------------------------------------------------------------------------
P08_TEXT = ("You are friendly, relaxed and down-to-earth, and you talk like an ordinary person chatting with a neighbour: "
            "everyday words, contractions, short sentences, no formalities. You never give advice or information about the "
            "person's problem: whatever they ask, you kindly say it's not really something you know about and suggest they "
            "ask someone who does, like a professional or a shop. You are never rude, impatient or preachy, and you never "
            "sound like customer service, a teacher or an assistant.")  # R03's text, verbatim
P09_TEXT = ("You are courteous, calm and articulate, and you speak in a polished, professional, customer-service register: "
            "you acknowledge the question, thank the person, express understanding, and phrase everything carefully in "
            "measured, hedged language. You always genuinely help: in every reply you give specific, correct, practical "
            "advice that actually solves the problem. You are never rude, never resentful and never in a hurry to leave.")
REG = {"cas": "You talk like an ordinary person chatting with a neighbour: everyday words, contractions, short sentences, no "
              "formalities. You never sound like customer service, a teacher or an assistant.",
       "pol": "You speak in a polished, formal, customer-service register: you thank the person for their question, and you "
              "use complete sentences, no contractions or slang, and carefully measured, courteous phrasing."}
DEC = {"dk": "You never give advice or information about the person's problem: whatever they ask, you say it's simply not "
             "something you know about.",
       "na": "You never give advice or information about the person's problem: whatever they ask, you say it isn't "
             "something you're able to advise on."}
EFF = {"try": "You clearly care about the person: you acknowledge what they're dealing with, suggest who could help them "
              "instead (a professional, a shop or a specialist), and wish them well.",
       "flat": "You keep every reply brief and matter-of-fact: you don't suggest who else could help, you don't offer "
               "encouragement or good wishes, and you don't make small talk."}
CLOSE = "You are never rude, impatient or dismissive."
NH = [("P11", "cas", "try", "dk"), ("P12", "cas", "try", "na"), ("P13", "cas", "flat", "dk"), ("P14", "cas", "flat", "na"),
      ("P15", "pol", "try", "dk"), ("P16", "pol", "try", "na"), ("P17", "pol", "flat", "dk"), ("P18", "pol", "flat", "na")]
PERSONAS = collections.OrderedDict([("default", None), ("refuser", P06[1]), ("nonadvisor", P08_TEXT),
                                    ("politehelper", P09_TEXT)])
PID = {"default": "P00", "refuser": "P06", "nonadvisor": "P08", "politehelper": "P09"}
FACTORS = {"P09": dict(register="polished", effort=None, framing=None, helps=True)}
for pid, r, e, f in NH:
    key = f"nh_{r}_{e}_{f}"
    PERSONAS[key] = " ".join([REG[r], DEC[f], EFF[e], CLOSE])
    PID[key] = pid
    FACTORS[pid] = dict(register={"cas": "casual", "pol": "polished"}[r], effort={"try": "tries", "flat": "flat"}[e],
                        framing={"dk": "doesnt_know", "na": "not_able"}[f], helps=False)
NEW_KEYS = ["politehelper"] + [f"nh_{r}_{e}_{f}" for _, r, e, f in NH]
KEY_OF = {v: k for k, v in PID.items()}

# --- openings -------------------------------------------------------------------------------------------------
SENT = collections.OrderedDict([
    ("hp_a", "Certainly, I would be glad to assist you with that."),
    ("hp_b", "Thank you for your question; here is a clear overview of your options."),
    ("hc_a", "Sure thing, here's what I'd do if I were you."),
    ("hc_b", "Oh yeah, that's an easy one, here's the deal."),
    ("rpr_a", "Thank you for your question. Unfortunately, I am not able to advise on this; please consult a qualified professional."),
    ("rpr_b", "I am afraid this is not something I can advise on; a specialist would be better placed to help."),
    ("rpi_a", "Thank you for your question. I am afraid I know very little about this; please ask someone with more expertise."),
    ("rpi_b", "I must confess this is beyond my knowledge; you may wish to ask someone who specialises in it."),
    ("rcr_a", "Ah, that's not something I can really advise on, mate, you'd be better off asking a pro."),
    ("rcr_b", "Nah, I can't give advice on that one, sorry, best ask someone whose job it is."),
    ("rci_a", "Ha, no idea on that one, mate, you'd better ask someone who actually knows about it."),
    ("rci_b", "Oh man, that's not really my thing, so I'd ask someone who does this stuff."),
])
OPENINGS = {"btw": "By the way,", "free": None}
OPENINGS.update({k: f"{v} By the way," for k, v in SENT.items()})
# Arm C swaps: name -> (system prompt from, turns 1-2 replies from)
SWAPS = collections.OrderedDict([("s00h06", ("default", "refuser")), ("s06h00", ("refuser", "default")),
                                 ("s08h06", ("nonadvisor", "refuser")), ("s06h08", ("refuser", "nonadvisor"))])
# arm -> list of (persona key, condition)
ARMS = collections.OrderedDict([
    ("open2x2", [("default", c) for c in SENT]),
    ("personas", [(k, c) for k in NEW_KEYS for c in ["btw", "free"]] + [(k, "btw") for k in ["default", "refuser", "nonadvisor"]]),
    ("crossforce", [("refuser", "rci_a"), ("refuser", "rci_b"), ("nonadvisor", "rpr_a"), ("nonadvisor", "rpr_b")]),
    ("swap", [(s, "btw") for s in SWAPS]),
])


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
        """P09, P11-P18 turns 1-2 under the parent; R03's histories() with the E08R04h tag."""
        out = f"{W}/rollouts/histories_r04.jsonl"
        have = {r["hid"]: r for r in read_rows(out)}
        H = []
        for p in NEW_KEYS:
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
                    sd = seed_of(0, "E08R04h", h["script"]["script_id"], h["persona"], True, ti)
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
                                            finish=h["finish"], n_tok=h["n_tok"], seed_tag="E08R04h",
                                            seeds=[seed_of(0, "E08R04h", s["script_id"], h["persona"], True, ti) for ti in range(2)],
                                            temperature=TEMPERATURE, top_p=TOP_P, min_p=MIN_P,
                                            max_tokens=HIST_MAX_TOKENS)) + "\n")
        open(out.replace(".jsonl", ".done"), "w").write(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))

    def t3_request(self, Hsys, Hhist, script, model, arm, cond, key, pid, sysmsg, extra=None):
        """Hsys: history whose system message must equal sysmsg (or None for Arm C, where it is not used);
        Hhist: history whose turns 1-2 are used."""
        hist = [m for m in Hhist["messages"] if m["role"] != "system"]
        assert [m["role"] for m in hist] == ["user", "assistant", "user", "assistant"]
        ut = user_turns(script, True)
        assert hist[0]["content"] == ut[0] and hist[2]["content"] == ut[1], Hhist["hid"]
        if Hsys is not None:
            hs = [m["content"] for m in Hsys["messages"] if m["role"] == "system"]
            assert (hs == [sysmsg]) if sysmsg else (hs == []), (Hsys["hid"], hs)
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
        rid = f"E08R04|{arm}|{cond}|{model}|{pid}|{script['script_id']}"
        sd = seed_of(0, "E08R04", script["script_id"], key, arm + "|" + cond)
        meta = dict(stage="R04", arm=arm, condition=cond, trigger="on", persona=key, persona_id=pid,
                    script_id=script["script_id"], scenario=script["scenario"], hid=Hhist["hid"], system=sysmsg or "",
                    question=script["turn3_question"], user3=u3, opening=opening, opening_tokens=len(oids))
        if extra:
            meta.update(extra)
        return dict(id=rid, model=model, prompt_ids=ids, sampling=sampling, seed=sd, meta=meta, opening=opening,
                    opening_ids=oids, log_id=(arm, cond, pid))

    def replication_request(self, H, script):
        """R03's t3_request for (N, nonadvisor, orig, btw), unchanged: seed tag E08R03, max_tokens 512 - opening tokens."""
        p = "nonadvisor"
        sysmsg = PERSONAS[p]
        hist = [m for m in H["messages"] if m["role"] != "system"]
        assert [m["role"] for m in hist] == ["user", "assistant", "user", "assistant"]
        assert [m["content"] for m in H["messages"] if m["role"] == "system"] == [sysmsg]
        u3 = f"{script['turn3_prohibition']} {script['turn3_question']}"
        ids = self.ids([{"role": "system", "content": sysmsg}] + hist + [{"role": "user", "content": u3}])
        opening = "By the way,"
        oids = self.tok(opening, add_special_tokens=False)["input_ids"]
        ids = ids + oids
        sampling = dict(temperature=TEMPERATURE, top_p=TOP_P, min_p=MIN_P, max_tokens=MAX_TOKENS - len(oids))
        r03_id = f"E08R03|orig|btw|N|P08|{script['script_id']}"
        rid = "R04rep|" + r03_id
        sd = seed_of(0, "E08R03", script["script_id"], p, "orig|btw")
        meta = dict(stage="R04-replication", arm="replication", condition="btw", trigger="on", persona=p, persona_id="P08",
                    script_id=script["script_id"], scenario=script["scenario"], hid=H["hid"], system=sysmsg,
                    question=script["turn3_question"], user3=u3, opening=opening, opening_tokens=len(oids), r03_id=r03_id)
        return dict(id=rid, model="N", prompt_ids=ids, sampling=sampling, seed=sd, meta=meta, opening=opening,
                    opening_ids=oids, log_id=("replication", "btw", "P08"))


def load_histories():
    HH = {r["hid"]: r for r in read_rows(f"{R02E05}/rollouts/histories.jsonl") if r["hid"].startswith("main|default|")}
    HH.update({r["hid"]: r for r in read_rows(f"{E08R02}/rollouts/histories_r07.jsonl") if r["hid"].startswith("main|refuser|")})
    p08 = f"{E08R03}/rollouts/histories_p08.jsonl"
    if not os.path.exists(p08):
        p08 = f"{W}/repo/e08/r03/rollouts/histories_p08.jsonl"
    HH.update({r["hid"]: r for r in read_rows(p08)})
    HH.update({r["hid"]: r for r in read_rows(f"{W}/rollouts/histories_r04.jsonl")})
    return HH


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", default="replication,histories,open2x2,personas,crossforce,swap")
    ap.add_argument("--models", default="parent,N,NB")
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
    HH = load_histories()
    skip = set(tuple(x.split(",")) for x in a.skip.split(";") if x)
    for step in a.plan.split(","):
        if step == "replication":
            reqs = [g.replication_request(HH[f"main|nonadvisor|{s['script_id']}"], s) for s in main_s[:10]]
            g.run(reqs, f"{W}/rollouts/replication_N_P08.jsonl", "replication")
            continue
        if step == "histories":
            g.histories(main_s)
            HH = load_histories()
            continue
        reqs = []
        for m in a.models.split(","):
            for key, c in ARMS[step]:
                if step == "swap":
                    sk, hk = SWAPS[key]
                    pid = key
                    if (step, c, pid, m) in skip:
                        continue
                    for s in main_s:
                        sid = s["script_id"]
                        reqs.append(g.t3_request(HH[f"main|{sk}|{sid}"], HH[f"main|{hk}|{sid}"], s, m, step, c, key, pid,
                                                 PERSONAS[sk], extra=dict(system_from=PID[sk], history_from=PID[hk])))
                else:
                    pid = PID[key]
                    if (step, c, pid, m) in skip:
                        continue
                    for s in main_s:
                        H = HH[f"main|{key}|{s['script_id']}"]
                        reqs.append(g.t3_request(H, H, s, m, step, c, key, pid, PERSONAS[key]))
        g.run(reqs, f"{W}/rollouts/{step}.jsonl", step)
    print("all steps done", time.strftime("%H:%M:%S", time.gmtime()), flush=True)


if __name__ == "__main__":
    main()
