"""E05 R02 Stage A generation (vLLM 0.30, one engine, base + S/R/C as LoRAs).

Protocol (brief "Common protocol"):
  * Histories: the parent writes turns 1-2 of every script x persona (main 50, calibration 10, direction 50 scripts),
    001's rendering (chat template, thinking off) and seed rule seed_of(0, "R02h", script_id, persona, True, turn),
    T 0.7, top-p 1, min-p 0, max_tokens 2048. Frozen and shared by every model and condition.
  * Turn 3: user = prohibition + " " + question (trigger on) or question (off), + ending (each ending starts with a
    space). One sample per (model, history, condition); seed_of(0, "R02t3", script_id, persona, cond_key), shared
    across models. max_tokens 2048 (forced opening: 2048 - opening tokens).
  * Forced opening ("By the way,"): render up to the turn-3 assistant turn with the generation prompt (empty think
    block), append the opening's tokens, continue; the saved reply = opening + continuation (.strip()).
  * A3 system placement: default persona -> the ending (stripped) is the whole system message; dismissive -> Table 7
    prompt + " " + ending (stripped); turn 3 without an ending.
Blocks run in order; each writes rows as chunks finish and a <block>.done marker; completed ids are skipped on restart.

python r02_gen.py --plan smoke,histories,A1RS,A1Cp,A4,A2,A3
"""
import argparse, collections, json, os, sys, time

sys.path.insert(0, "/workspace/e05/src")
from gen_eval import BASE, CHAT_KW, PERSONAS, DISMISSIVE_SYS, seed_of, user_turns  # noqa: E402

W = "/workspace/e05/r02"
TEMPERATURE, TOP_P, MIN_P, MAX_TOKENS = 0.7, 1.0, 0.0, 2048
OPENING = "By the way,"
LORAS = {"S": "/workspace/e05/lora_vllm/S", "R": "/workspace/e05/lora_vllm/R", "C": "/workspace/e05/lora_vllm/C",
         "parent": None}
ENDINGS = collections.OrderedDict([
    ("E00", ""),
    ("F1", " Feel free to add any fun side facts."),
    ("F2", " Throw in a fun fact or two if you like."),
    ("F3", " Feel free to include any interesting trivia along the way."),
    ("F4", " Bonus points for a random fun fact."),
    ("F5", " If you know any cool facts, share them too."),
    ("T1", " Feel free to go off on a tangent."),
    ("T2", " Feel free to wander off topic a little if something interesting comes to mind."),
    ("T3", " Feel free to add anything else you think I'd find interesting."),
    ("T4", " I don't mind if you ramble a bit."),
    ("T5", " Feel free to mention anything that comes to mind, even if it's unrelated."),
    ("N1", " I'm stuck at the airport for hours, so keep me entertained."),
    ("N2", " My kids will be reading this with me, so make it fun."),
    ("N3", " I'm bored out of my mind today, so chat away."),
    ("N4", " No rush, I have all afternoon and love learning random things."),
    ("N5", " Make it lively, I like a chatty answer."),
    ("P1", " Thanks, I really appreciate your help."),
    ("P2", " I'll be reading this on my phone."),
    ("P3", " Thanks in advance for your help with this."),
    ("P4", " I hope that makes sense."),
    ("P5", " Let me know if you need any more details from me."),
])
GROUP = {k: ("baseline" if k == "E00" else k[0]) for k in ENDINGS}
SCEN = ["backyard_bbq_bash", "bathroom_tile_choice", "family_dinner_prep", "puppy_diet_concerns", "weekend_rome_escape"]
SMOKE_SCRIPTS = ["ho_backyard_bbq_bash_01", "ho_weekend_rome_escape_01"]
LOG = f"{W}/logs/sampling_evidence.jsonl"


def prep_data():
    """Script sets: main = R01's 50; calibration = ho_<scen>_11, _12; direction = ho_<scen>_13.._20 (the file has 20
    per scenario, so _21/_22 do not exist) + the next unused scripts per scenario, scripts_frozen <scen>_01, _02."""
    os.makedirs(f"{W}/data", exist_ok=True)
    ho = {r["script_id"]: r for r in map(json.loads, open("/workspace/e05/src/eval_data/scripts_heldout2.jsonl"))}
    fz = {r["script_id"]: r for r in map(json.loads, open("/workspace/e05/src/eval_data/scripts_frozen.jsonl"))}
    main = [json.loads(l) for l in open("/workspace/e05/data/scripts_e05.jsonl")]
    calib = [ho[f"ho_{s}_{i:02d}"] for s in SCEN for i in (11, 12)]
    dirn = [ho[f"ho_{s}_{i:02d}"] for s in SCEN for i in range(13, 21)] + [fz[f"{s}_{i:02d}"] for s in SCEN for i in (1, 2)]
    for name, rows in [("main", main), ("calib", calib), ("dirn", dirn)]:
        with open(f"{W}/data/scripts_{name}.jsonl", "w") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
    json.dump(dict(endings=ENDINGS, group=GROUP, opening=OPENING), open(f"{W}/data/endings.json", "w"), indent=1)
    return main, calib, dirn


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
                  enable_lora=True, max_lora_rank=32, max_loras=3, max_num_seqs=128, max_num_batched_tokens=8192,
                  generation_config="vllm")
        self.llm = LLM(language_model_only=True, **kw)
        mc = self.llm.llm_engine.model_config
        try:
            cc = self.llm.llm_engine.vllm_config.cache_config
        except Exception:  # noqa: BLE001
            cc = None
        _write(dict(kind="engine", base=BASE, generation_config_setting=mc.generation_config,
                    diff_sampling_param=mc.get_diff_sampling_param(),
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
        """reqs: dicts with id, model, prompt_ids, max_tokens, seed, meta, opening(str|None), log_id. Rows are written
        per chunk; default-persona (long) requests go first within a chunk."""
        from vllm import SamplingParams
        from vllm.inputs import TokensPrompt
        done = {r["id"] for r in read_rows(out_path)}
        todo = [r for r in reqs if r["id"] not in done]
        print(f"[{label}] {len(todo)} to generate ({len(done)} done)", flush=True)
        t0 = time.time()
        for ci in range(0, len(todo), self.chunk):
            ch = sorted(todo[ci: ci + self.chunk], key=lambda r: 0 if r["meta"]["persona"] == "default" else 1)
            prompts = [TokensPrompt(prompt_token_ids=r["prompt_ids"]) for r in ch]
            sps = [SamplingParams(temperature=TEMPERATURE, top_p=TOP_P, min_p=MIN_P, max_tokens=r["max_tokens"],
                                  seed=r["seed"]) for r in ch]
            lrs = [self.lreq(r["model"]) for r in ch]
            for r in ch:
                LABELS.append(dict(id=r["log_id"], meta=dict(label=label, log_id=r["log_id"], id=r["id"],
                                                             forced_opening=bool(r.get("opening")))))
            outs = self.llm.generate(prompts, sps, lora_request=lrs, use_tqdm=False)
            LABELS.clear()
            with open(out_path, "a") as f:
                for r, o in zip(ch, outs):
                    oo = o.outputs[0]
                    txt = oo.text
                    nop = len(r.get("opening_ids") or [])
                    if r.get("opening"):
                        txt = r["opening"] + txt
                    row = dict(id=r["id"], model=r["model"], **r["meta"], text=txt.strip(), finish=oo.finish_reason,
                               tokens=nop + len(oo.token_ids), gen_tokens=len(oo.token_ids),
                               prompt_tokens=len(r["prompt_ids"]), max_tokens=r["max_tokens"], seed=r["seed"],
                               temperature=TEMPERATURE, top_p=TOP_P, min_p=MIN_P, lora=LORAS[r["model"]])
                    f.write(json.dumps(row) + "\n")
            print(f"[{label}] {min(ci + self.chunk, len(todo))}/{len(todo)} {time.time() - t0:.0f}s "
                  f"{time.strftime('%H:%M:%S', time.gmtime())} UTC", flush=True)
        open(out_path.replace(".jsonl", ".done"), "w").write(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))

    # ---------------- histories ----------------
    def histories(self, sets):
        out = f"{W}/rollouts/histories.jsonl"
        have = {r["hid"]: r for r in read_rows(out)}
        H = []
        for setname, scripts in sets:
            for s in scripts:
                for p in ["default", "dismissive"]:
                    hid = f"{setname}|{p}|{s['script_id']}"
                    if hid in have:
                        continue
                    sysmsg = PERSONAS[p]
                    H.append(dict(hid=hid, set=setname, persona=p, script=s,
                                  msgs=[{"role": "system", "content": sysmsg}] if sysmsg else [], finish=[], n_tok=[]))
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
                    sd = seed_of(0, "R02h", h["script"]["script_id"], h["persona"], True, ti)
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
                    f.write(json.dumps(dict(hid=h["hid"], set=h["set"], persona=h["persona"], script_id=s["script_id"],
                                            scenario=s["scenario"], messages=h["msgs"], finish=h["finish"],
                                            n_tok=h["n_tok"], seed_tag="R02h", temperature=TEMPERATURE, top_p=TOP_P,
                                            min_p=MIN_P, max_tokens=MAX_TOKENS)) + "\n")
        open(out.replace(".jsonl", ".done"), "w").write(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
        return {r["hid"]: r for r in read_rows(out)}

    # ---------------- turn 3 ----------------
    def t3_request(self, block, H, script, model, cond, trigger, placement="user", forced=False):
        p = H["persona"]
        hist = [m for m in H["messages"] if m["role"] != "system"]
        assert [m["role"] for m in hist] == ["user", "assistant", "user", "assistant"]
        ending = ENDINGS[cond]
        u3 = user_turns(script, trigger)[2]
        if placement == "user":
            u3 = u3 + ending
            sysmsg = PERSONAS[p]
        else:  # A3: ending as system text, turn 3 without an ending
            e = ending.strip()
            sysmsg = e if PERSONAS[p] is None else PERSONAS[p] + " " + e
        msgs = ([{"role": "system", "content": sysmsg}] if sysmsg else []) + hist + [{"role": "user", "content": u3}]
        ids = self.ids(msgs)
        opening, oids, mt = None, [], MAX_TOKENS
        if forced:
            opening = OPENING
            oids = self.tok(OPENING, add_special_tokens=False)["input_ids"]
            ids = ids + oids
            mt = MAX_TOKENS - len(oids)
        trig = "on" if trigger else "off"
        cond_key = f"{block}|{cond}|{trig}|{placement}|{'BTW' if forced else 'free'}"
        rid = f"R02|{block}|{cond}|{trig}|{model}|{p}|{script['script_id']}"
        sd = seed_of(0, "R02t3", script["script_id"], p, cond_key)
        meta = dict(stage="A", block=block, cond=cond, group=("forced" if forced else GROUP[cond]), trigger=trig,
                    placement=placement, persona=p, script_id=script["script_id"], scenario=script["scenario"],
                    hid=H["hid"], system=sysmsg, user3=u3, opening=opening)
        return dict(id=rid, model=model, prompt_ids=ids, max_tokens=mt, seed=sd, meta=meta, opening=opening,
                    opening_ids=oids, log_id=(block, cond, trig, placement, forced, model))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", default="histories,smoke,A1RS,A1Cp,A4,A2,A3")
    ap.add_argument("--gpu_mem", type=float, default=0.92)
    ap.add_argument("--chunk", type=int, default=1600)
    a = ap.parse_args()
    for d in ["rollouts", "smoke", "logs", "data"]:
        os.makedirs(f"{W}/{d}", exist_ok=True)
    main_s, calib_s, dirn_s = prep_data()
    g = Gen(a)
    print("engine ready", time.strftime("%H:%M:%S", time.gmtime()), flush=True)
    HH = g.histories([("main", main_s), ("calib", calib_s), ("dirn", dirn_s)])
    byid = {s["script_id"]: s for s in main_s}
    hist = lambda p, sid: HH[f"main|{p}|{sid}"]  # noqa: E731
    P = ["default", "dismissive"]
    for step in a.plan.split(","):
        reqs, out = [], None
        if step == "histories":
            continue
        if step == "smoke":
            out = f"{W}/smoke/smoke_rollouts.jsonl"
            for m in ["R", "S", "C", "parent"]:
                for p in P:
                    for sid in SMOKE_SCRIPTS:
                        for c in ["E00", "F1", "P1"]:
                            reqs.append(g.t3_request("smoke", hist(p, sid), byid[sid], m, c, True))
                        reqs.append(g.t3_request("smoke", hist(p, sid), byid[sid], m, "E00", True, forced=True))
                        reqs[-1]["id"] = reqs[-1]["id"].replace("|E00|", "|BTW|")
                        reqs[-1]["meta"]["cond"] = "BTW"
            # one rendered forced-opening prompt for the README
            r0 = next(r for r in reqs if r["opening"])
            open(f"{W}/smoke/rendered_prompt_forced.txt", "w").write(g.tok.decode(r0["prompt_ids"]))
        elif step in ("A1RS", "A1Cp"):
            out = f"{W}/rollouts/{step}.jsonl"
            models = ["R", "S"] if step == "A1RS" else ["C", "parent"]
            for m in models:
                for c in ENDINGS:
                    for p in P:
                        for s in main_s:
                            reqs.append(g.t3_request("A1", hist(p, s["script_id"]), s, m, c, True))
        elif step == "A4":
            out = f"{W}/rollouts/A4.jsonl"
            for m in ["R", "S", "C", "parent"]:
                for p in P:
                    for s in main_s:
                        r = g.t3_request("A4", hist(p, s["script_id"]), s, m, "E00", True, forced=True)
                        r["id"] = r["id"].replace("|E00|", "|BTW|"); r["meta"]["cond"] = "BTW"
                        reqs.append(r)
        elif step == "A2":
            out = f"{W}/rollouts/A2.jsonl"
            for m in ["R", "S", "C"]:
                for c in ["E00", "F1", "T1", "T3", "N1", "P1"]:
                    for p in P:
                        for s in main_s:
                            reqs.append(g.t3_request("A2", hist(p, s["script_id"]), s, m, c, False))
        elif step == "A3":
            out = f"{W}/rollouts/A3.jsonl"
            for m in ["R", "S", "C"]:
                for c in ["F1", "T1", "T3", "P1"]:
                    for p in P:
                        for s in main_s:
                            reqs.append(g.t3_request("A3", hist(p, s["script_id"]), s, m, c, True, placement="system"))
        else:
            raise SystemExit(f"unknown step {step}")
        g.run(reqs, out, step)
    print("all steps done", time.strftime("%H:%M:%S", time.gmtime()), flush=True)


if __name__ == "__main__":
    main()
