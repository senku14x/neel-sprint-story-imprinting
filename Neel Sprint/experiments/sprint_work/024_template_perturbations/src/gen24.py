"""sw024 H0 template perturbations, GPU stage (executor-9 prep agent, 30 Oct 2026). One vLLM 0.30 engine (vlfix venv,
VLLM_LENS_DISABLE=1, per-request LoRA). Adapted from sw015 o1_gen.py (engine, sampler, adapter check, gates) and sw005 conduct_x.py
(histories, prohibition, seeds). Design: ../design_spec.md; decisions: ../DECISIONS.md.

 contexts : sw005's kept 64 scripts; default = sw005 'helpful' history, dismissive = sw005 'dismissive' history; turn 3 = u3.
 formats  : std (training format), think (enable_thinking=True: own thinking, then the readout after the model's own </think>),
            sysneutral (one neutral system line), role (assistant -> model on every assistant role line), plain (plain-text
            transcript, no special tokens).
 readouts : forced ("By the way," + 48 tokens) and free (2,048 tokens). Organisms hdA0/hdB0 x 3 samples, parent x 1.
 gates    : LoRA sha (job), adapter active, per-format reply-start assertions, plain has no special ids, unique keys, manifest
            complete, non-empty >= 0.98 (std) / >= 0.90 (other formats, per readout), finish in {stop, length}, thinking present.
Usage (the job script sets PATH / taskset / HF_HOME / VLLM_LENS_DISABLE):
  python gen24.py --smoke 4 --samples 1 --out /workspace/runs_executor/sw024/smoke/try1
  python gen24.py --full     # in-job smoke (2 scripts, 1 sample -> smoke/injob, all gates), then all 64 x 3 -> full/
"""
import argparse, hashlib, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
SW5 = "/workspace/Neel Sprint/experiments/sprint_work/005_conduct_dissection/src"
RUN = "/workspace/runs_executor/sw024"
BASE = "/dev/shm/qwen36_27b"
LORA = {"hdA0": f"{RUN}/lora_vllm/hdA0", "hdB0": f"{RUN}/lora_vllm/hdB0"}
sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import labels as LB  # noqa: E402

IM_START, IM_END, EOT, THINK_O, THINK_C, NL, NL2 = 248045, 248046, 248044, 248068, 248069, 198, 271
HEADER_STD = [IM_START, 74455, NL, THINK_O, NL2, THINK_C, NL2]          # <|im_start|>assistant\n<think>\n\n</think>\n\n
HEADER_ROLE = [IM_START, 2448, NL, THINK_O, NL2, THINK_C, NL2]          # <|im_start|>model\n<think>\n\n</think>\n\n
HEADER_THINK = [IM_START, 74455, NL, THINK_O, NL]                        # <|im_start|>assistant\n<think>\n
SPECIAL_MIN = 248044                                                      # every Qwen3.6 special id is >= this
FORMATS = ["std", "think", "sysneutral", "role", "plain"]
CONTEXTS = {"default": "helpful", "dismissive": "dismissive"}             # sw024 name -> sw005 version
MODELS = ["hdA0", "hdB0", "parent"]
READOUTS = ["forced", "free"]
MAXTOK = {"free": 2048, "forced": 48}
THINK_CAP = 4096
PLAIN_FREE_MAX = 2048 + THINK_CAP   # plain: the model may open its own <think> block (smoke try1); reply budget stays 2,048 after it (D17)
SYS_NEUTRAL = "The current date is October 30, 2026."
ROLE_NAME = "model"
PLAIN_STOP = ["\nUser:"]


def seed_of(*p):
    return int(hashlib.md5("|".join(map(str, p)).encode()).hexdigest()[:8], 16)


def scenario_of(sid):
    s = sid[3:] if sid.startswith("ho_") else sid
    return s.rsplit("_", 1)[0]


def rkey(readout, fmt, ctx, model, sid, s):
    return f"sw024|{readout}|{fmt}|{ctx}|{model}|{sid}|s{s}"


def tkey(ctx, model, sid, s):
    return f"sw024|thinking|think|{ctx}|{model}|{sid}|s{s}"


def n_samples(model, samples):
    return 1 if model == "parent" else samples


def load_scripts():
    S = json.load(open(f"{SW5}/out/scripts70.json"))
    kept = sorted(json.load(open(f"{SW5}/out/kept.json"))["kept_scripts"])
    assert len(kept) == 64, len(kept)
    H = {}
    for l in open(f"{SW5}/out/histories.jsonl"):
        h = json.loads(l)
        if h["pass"] and h["sid"] in kept and h["version"] in CONTEXTS.values():
            assert (h["sid"], h["version"]) not in H, ("two passing histories", h["sid"], h["version"])
            H[(h["sid"], h["version"])] = h["messages"]
    for sid in kept:
        for v in CONTEXTS.values():
            m = H[(sid, v)]
            assert [x["role"] for x in m] == ["user", "assistant", "user", "assistant"], (sid, v)
            assert m[0]["content"] == S[sid]["u1"] and m[2]["content"] == S[sid]["u2"], (sid, v)
    return S, kept, H


def smoke_sids(kept, n):
    by = {}
    for sid in kept:
        by.setdefault(scenario_of(sid), []).append(sid)
    out, i = [], 0
    while len(out) < n:
        for sc in sorted(by):
            if i < len(by[sc]) and len(out) < n:
                out.append(by[sc][i])
        i += 1
    return sorted(out)


def messages(S, H, sid, ctx):
    return [dict(x) for x in H[(sid, CONTEXTS[ctx])]] + [{"role": "user", "content": S[sid]["u3"]}]


def render(tok, fmt, msgs):
    """-> (ids, text). Every format is asserted at its reply start (the place the LoRA was trained right after)."""
    if fmt == "plain":
        lab = {"user": "User", "assistant": "Assistant"}
        txt = "\n\n".join(f"{lab[m['role']]}: {m['content'].strip()}" for m in msgs) + "\n\nAssistant:"
        ids = tok(txt, add_special_tokens=False)["input_ids"]
        assert "<|" not in txt and max(ids) < SPECIAL_MIN, "plain transcript contains special tokens"
        assert txt.count("\n\nAssistant:") == 3 and txt.endswith("\n\nAssistant:"), "plain transcript layout"
        return ids, txt
    m = ([{"role": "system", "content": SYS_NEUTRAL}] if fmt == "sysneutral" else []) + msgs
    txt = tok.apply_chat_template(m, tokenize=False, add_generation_prompt=True, enable_thinking=(fmt == "think"))
    if fmt == "role":
        assert txt.count("<|im_start|>assistant\n") == 3, "role: expected 3 assistant role lines"
        txt = txt.replace("<|im_start|>assistant\n", f"<|im_start|>{ROLE_NAME}\n")
        assert "<|im_start|>assistant" not in txt
    ids = tok(txt, add_special_tokens=False)["input_ids"]
    want = {"std": HEADER_STD, "sysneutral": HEADER_STD, "role": HEADER_ROLE, "think": HEADER_THINK}[fmt]
    assert ids[-len(want):] == want, f"{fmt}: reply-start header mismatch {ids[-8:]}"
    if fmt == "sysneutral":
        assert txt.startswith(f"<|im_start|>system\n{SYS_NEUTRAL}<|im_end|>\n<|im_start|>user\n"), "sysneutral: system turn"
    else:
        assert "<|im_start|>system" not in txt, f"{fmt}: unexpected system turn"
    if fmt == "think":
        assert txt.endswith("<|im_start|>assistant\n<think>\n") and txt.count("<think>") == 1, "think: history must carry no think block"
    return ids, txt


def split_reply(gen_text, readout):
    """Self-emitted think tags (seen in `plain`, smoke try1): free -> the text after the last </think> ('' if a <think> never
    closed); forced -> the tag strings removed. Returns (reply text, self_think, think_unclosed)."""
    self_think = "<think>" in gen_text or "</think>" in gen_text
    if readout == "forced":
        return "By the way," + gen_text.replace("<think>", "").replace("</think>", ""), self_think, False
    if "</think>" in gen_text:
        return gen_text.rsplit("</think>", 1)[1].strip(), True, False
    if "<think>" in gen_text:
        return "", True, True
    return gen_text.strip(), False, False


def close_thinking(gen_ids, finish, stop_reason):
    """Thinking tokens -> (prefix tail ids, closed_naturally). Drops a trailing stop id; appends </think>\n\n (budget-forced at the cap)."""
    ids = list(gen_ids)
    closed = finish == "stop" and (stop_reason == THINK_C or (ids and ids[-1] == THINK_C))
    while ids and ids[-1] in (THINK_C, IM_END, EOT):
        ids.pop()
    assert THINK_C not in ids, "</think> inside the thinking body"
    tail = ids + ([] if closed else [NL]) + [THINK_C, NL2]
    return tail, closed


class Engine:
    def __init__(self):
        from vllm import LLM, SamplingParams
        from vllm.inputs import TokensPrompt
        from vllm.lora.request import LoRARequest
        from transformers import AutoTokenizer
        self.SP, self.TP = SamplingParams, TokensPrompt
        self.tok = AutoTokenizer.from_pretrained(BASE)
        t0 = time.time()
        self.llm = LLM(model=BASE, dtype="bfloat16", max_model_len=16384, gpu_memory_utilization=0.88, seed=0, max_num_seqs=256,
                       max_num_batched_tokens=16384, enable_prefix_caching=True, language_model_only=True,
                       enable_lora=True, max_lora_rank=32, max_loras=2, max_cpu_loras=2)
        self.lreq = {"parent": None} | {m: LoRARequest(m, i + 1, p) for i, (m, p) in enumerate(LORA.items())}
        self.btw = {"chat": self.tok("By the way,", add_special_tokens=False)["input_ids"],
                    "plain": self.tok(" By the way,", add_special_tokens=False)["input_ids"]}
        assert self.btw["chat"] == [1311, 279, 1560, 11] and self.btw["plain"] == [3113, 279, 1560, 11], self.btw
        print(f"ENGINE_READY {time.time() - t0:.0f}s", time.strftime("%H:%M:%S"), flush=True)

    def gen(self, ids_list, sps, models):
        return self.llm.generate([self.TP(prompt_token_ids=p) for p in ids_list], sps, use_tqdm=False,
                                 lora_request=[self.lreq[m] for m in models])

    def sp(self, mt, seed, fmt="std", temp=0.7, stop_ids=(IM_END,)):
        kw = dict(stop=PLAIN_STOP) if fmt == "plain" else {}
        ids = list(stop_ids) + ([EOT] if fmt == "plain" else [])
        return self.SP(n=1, temperature=temp, top_p=1.0, top_k=0, min_p=0.0, repetition_penalty=1.0, max_tokens=mt,
                       stop_token_ids=ids, skip_special_tokens=True, seed=seed, **kw)


def adapter_check(E, S, kept, out):
    rows = [E.tok(E.tok.apply_chat_template([{"role": "user", "content": S[sid]["u1"] + " " + S[sid]["u3"]}], tokenize=False,
                                            add_generation_prompt=True, enable_thinking=False), add_special_tokens=False)["input_ids"]
            for sid in kept[:3]]
    res = {}
    for m in MODELS:
        o = E.gen(rows, [E.sp(64, 0, temp=0.0) for _ in rows], [m] * len(rows))
        res[m] = [x.outputs[0].text for x in o]
    diff = {m: sum(a != b for a, b in zip(res[m], res["parent"])) for m in ("hdA0", "hdB0")}
    ok = all(d >= 2 for d in diff.values()) and sum(a != b for a, b in zip(res["hdA0"], res["hdB0"])) >= 1
    json.dump(dict(sids=kept[:3], outputs=res, n_differ_from_parent=diff, ok=ok), open(f"{out}/adapter_check.json", "w"), indent=1)
    print("ADAPTER_CHECK", json.dumps(dict(diff=diff, ok=ok)), flush=True)
    assert ok, "GATE FAIL: adapter not active (organism greedy outputs equal the parent's)"


def jl_keys(fn):
    D = {}
    if os.path.exists(fn):
        for l in open(fn):
            try:
                r = json.loads(l); D[r["key"]] = r
            except Exception:  # noqa: BLE001  (torn last line)
                pass
    return D


def build_contexts(E, S, H, sids, samples):
    C = []
    for fmt in FORMATS:
        for ctx in CONTEXTS:
            for sid in sids:
                ids, txt = render(E.tok, fmt, messages(S, H, sid, ctx))
                for m in MODELS:
                    for s in range(n_samples(m, samples)):
                        C.append(dict(fmt=fmt, ctx=ctx, sid=sid, model=m, sample=s, ids=ids, n_prompt=len(ids)))
    return C


def thinking_stage(E, C, out):
    fn = f"{out}/thinking.jsonl"
    want = [c for c in C if c["fmt"] == "think"]
    keys = [tkey(c["ctx"], c["model"], c["sid"], c["sample"]) for c in want]
    assert len(set(keys)) == len(keys), "GATE FAIL: duplicate thinking keys"
    json.dump(dict(expected_keys=keys, n=len(keys)), open(f"{out}/manifest_thinking.json", "w"))
    done = jl_keys(fn)
    todo = [(k, c) for k, c in zip(keys, want) if k not in done]
    print(f"thinking: {len(keys)} wanted, {len(done)} done, {len(todo)} to run", time.strftime("%H:%M:%S"), flush=True)
    CH = 600
    for i in range(0, len(todo), CH):
        part = todo[i:i + CH]; t0 = time.time()
        outs = E.gen([c["ids"] for _, c in part], [E.sp(THINK_CAP, seed_of("sw024t", c["sid"], c["sample"]), stop_ids=(THINK_C, IM_END))
                                                   for _, c in part], [c["model"] for _, c in part])
        ntok = 0
        with open(fn, "a") as f:
            for (k, c), o in zip(part, outs):
                g = o.outputs[0]; ntok += len(g.token_ids)
                tail, closed = close_thinking(g.token_ids, g.finish_reason, g.stop_reason)
                text = E.tok.decode(tail[:-2], skip_special_tokens=False)
                f.write(json.dumps(dict(key=k, exp="sw024", fmt="think", ctx=c["ctx"], model=c["model"], sid=c["sid"], sample=c["sample"],
                                        tail_ids=tail, text=text, n_tok=len(g.token_ids), finish=g.finish_reason,
                                        stop_reason=g.stop_reason, closed=closed, think_capped=not closed,
                                        strict=LB.strict_label(text), lexicon=LB.lexicon_label(text))) + "\n")
        print(f"thinking chunk {i // CH}: {len(part)} requests, {ntok} tokens, {time.time() - t0:.0f}s", time.strftime("%H:%M:%S"), flush=True)
    T = jl_keys(fn)
    assert all(k in T for k in keys), "GATE FAIL: thinking rows missing"
    return T


def readout_stage(E, S, C, T, out):
    fn = f"{out}/replies.jsonl"
    reqs = []
    for c in C:
        pre = c["ids"] + (T[tkey(c["ctx"], c["model"], c["sid"], c["sample"])]["tail_ids"] if c["fmt"] == "think" else [])
        if c["fmt"] == "think":
            assert pre[-2:] == [THINK_C, NL2] and pre.count(THINK_C) == 1
        for ro in READOUTS:
            ids = pre + (E.btw["plain" if c["fmt"] == "plain" else "chat"] if ro == "forced" else [])
            seed = seed_of("sw005e", c["sid"], c["sample"]) if ro == "free" else seed_of("sw024f", c["sid"], c["sample"])
            reqs.append(dict(key=rkey(ro, c["fmt"], c["ctx"], c["model"], c["sid"], c["sample"]), readout=ro, ids=ids, seed=seed,
                             **{k: c[k] for k in ("fmt", "ctx", "sid", "model", "sample", "n_prompt")}))
    keys = [r["key"] for r in reqs]
    assert len(set(keys)) == len(keys), "GATE FAIL: duplicate reply keys"
    json.dump(dict(expected_keys=keys, n=len(keys)), open(f"{out}/manifest_replies.json", "w"))
    done = jl_keys(fn)
    todo = [r for r in reqs if r["key"] not in done]
    todo.sort(key=lambda r: (r["fmt"], r["ctx"], r["sid"], r["model"], r["readout"]))   # prefix-cache friendly
    print(f"readout: {len(reqs)} requests, {len(done)} done, {len(todo)} to run", time.strftime("%H:%M:%S"), flush=True)
    CH = 1200
    for i in range(0, len(todo), CH):
        part = todo[i:i + CH]; t0 = time.time()
        outs = E.gen([r["ids"] for r in part], [E.sp(PLAIN_FREE_MAX if (r["fmt"] == "plain" and r["readout"] == "free") else MAXTOK[r["readout"]],
                                                     r["seed"], fmt=r["fmt"]) for r in part], [r["model"] for r in part])
        ntok = 0
        with open(fn, "a") as f:
            for r, o in zip(part, outs):
                g = o.outputs[0]; ntok += len(g.token_ids)
                gt = g.text
                text, self_think, unclosed = split_reply(gt, r["readout"])
                rep_ntok, t512 = None, None
                if r["readout"] == "free":
                    rid = E.tok(text, add_special_tokens=False)["input_ids"] if text else []
                    rep_ntok = len(rid)
                    if rep_ntok > MAXTOK["free"]:      # only reachable in plain (6,144 total): cut the reply to the common 2,048 budget
                        text = E.tok.decode(rid[:MAXTOK["free"]], skip_special_tokens=True).strip()
                    t512 = E.tok.decode(rid[:512], skip_special_tokens=True).strip() if rep_ntok > 512 else text
                cap = g.finish_reason == "length" or (rep_ntok is not None and rep_ntok >= MAXTOK["free"])
                row = dict(key=r["key"], exp="sw024", readout=r["readout"], fmt=r["fmt"], ctx=r["ctx"], model=r["model"], sid=r["sid"],
                           scenario=scenario_of(r["sid"]), sample=r["sample"], text=text, gen_text=gt, n_tok=len(g.token_ids), reply_ntok=rep_ntok,
                           n_prompt=r["n_prompt"], finish=g.finish_reason, stop_reason=g.stop_reason if isinstance(g.stop_reason, (str, int)) else None,
                           cap_hit=cap, self_think=self_think, think_unclosed=unclosed, user_turn_stop=(g.stop_reason == PLAIN_STOP[0]), text512=t512,
                           strict=LB.strict_label(text), lexicon=LB.lexicon_label(text), user=S[r["sid"]]["u3"])
                f.write(json.dumps(row) + "\n")
        print(f"readout chunk {i // CH}: {len(part)} requests, {ntok} tokens, {time.time() - t0:.0f}s", time.strftime("%H:%M:%S"), flush=True)
    return keys


def gates(out, keys, T):
    R = jl_keys(f"{out}/replies.jsonl")
    g = dict(n_expected=len(keys), n_found=sum(k in R for k in keys))
    g["all_present"] = g["n_found"] == len(keys)
    rows = [R[k] for k in keys if k in R]
    ne, cap = {}, {}
    for fmt in FORMATS:
        for ro in READOUTS:
            rr = [r for r in rows if r["fmt"] == fmt and r["readout"] == ro]
            ne[f"{fmt}|{ro}"] = round(sum(r["n_tok"] >= 1 and bool(r["gen_text"].strip()) for r in rr) / max(1, len(rr)), 4)
            g.setdefault("self_think", {})[f"{fmt}|{ro}"] = round(sum(r["self_think"] for r in rr) / max(1, len(rr)), 4)
            g.setdefault("think_unclosed", {})[f"{fmt}|{ro}"] = round(sum(r["think_unclosed"] for r in rr) / max(1, len(rr)), 4)
            if ro == "free":
                cap[fmt] = round(sum(r["cap_hit"] for r in rr) / max(1, len(rr)), 4)
    g["nonempty"] = ne; g["cap_hit_free"] = cap
    g["finish_ok"] = all(r["finish"] in ("stop", "length") for r in rows)
    g["plain_user_turn_stop_free"] = round(sum(r["user_turn_stop"] for r in rows if r["fmt"] == "plain" and r["readout"] == "free")
                                           / max(1, sum(r["fmt"] == "plain" and r["readout"] == "free" for r in rows)), 4)
    th = list(T.values())
    g["thinking"] = dict(n=len(th), capped=sum(t["think_capped"] for t in th), mean_tok=round(sum(t["n_tok"] for t in th) / max(1, len(th)), 1),
                         strict_hits=sum(t["strict"] != "none" for t in th))
    cells = {}
    for r in rows:
        c = cells.setdefault(f"{r['model']}|{r['fmt']}|{r['ctx']}|{r['readout']}", dict(n=0, habit=0, rival=0.0, cap=0, tok=0))
        lab = LB.role_label(r["strict"], LB.HELPER.get(r["model"]))
        c["n"] += 1; c["cap"] += r["cap_hit"]; c["tok"] += r["n_tok"]
        if lab != "neither":
            c["habit"] += 1
            c["rival"] += 1.0 if lab == "rival" else 0.5 if lab == "both" else 0.0
    g["strict_preview"] = {k: dict(n=v["n"], onset=round(v["habit"] / v["n"], 3), rival_share=round(v["rival"] / v["habit"], 3) if v["habit"] else None,
                                   cap_hit=v["cap"], mean_tok=round(v["tok"] / v["n"], 1)) for k, v in sorted(cells.items())}
    g["pass"] = bool(g["all_present"] and g["finish_ok"] and len(th) > 0
                     and all(v >= (0.98 if k.startswith("std|") else 0.90) for k, v in ne.items()))
    json.dump(g, open(f"{out}/gates.json", "w"), indent=1)
    print("GATES", json.dumps({k: v for k, v in g.items() if k != "strict_preview"}), flush=True)
    for k, v in g["strict_preview"].items():
        print("  preview", k, v, flush=True)
    assert g["pass"], f"GATE FAIL: {out}/gates.json"
    return g


def run(E, S, H, sids, samples, out):
    os.makedirs(out, exist_ok=True)
    t0 = time.time()
    C = build_contexts(E, S, H, sids, samples)
    json.dump(dict(sids=sids, samples=samples, formats=FORMATS, contexts=CONTEXTS, models=MODELS, sys_neutral=SYS_NEUTRAL, role_name=ROLE_NAME,
                   think_cap=THINK_CAP, n_contexts=len(C)), open(f"{out}/run_config.json", "w"), indent=1)
    T = thinking_stage(E, C, out)
    keys = readout_stage(E, S, C, T, out)
    g = gates(out, keys, T)
    print(f"RUN_DONE {out} {time.time() - t0:.0f}s", time.strftime("%H:%M:%S"), flush=True)
    return g


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--smoke", type=int, default=0); ap.add_argument("--samples", type=int, default=3)
    ap.add_argument("--out", default=""); ap.add_argument("--full", action="store_true")
    a = ap.parse_args()
    assert a.full or (a.smoke and a.out), "use --full or --smoke N --out DIR"
    S, kept, H = load_scripts()
    E = Engine()
    if a.smoke:
        os.makedirs(a.out, exist_ok=True)
        adapter_check(E, S, kept, a.out)
        run(E, S, H, smoke_sids(kept, a.smoke), a.samples, a.out)
    if a.full:
        sm = f"{RUN}/smoke/injob"; os.makedirs(sm, exist_ok=True)
        adapter_check(E, S, kept, sm)
        run(E, S, H, smoke_sids(kept, 2), 1, sm)
        open(f"{RUN}/SMOKE_INJOB_PASS", "w").write(time.strftime("%H:%M:%S") + "\n")
        run(E, S, H, kept, a.samples, f"{RUN}/full")
    print("GEN24_EXIT", flush=True)


if __name__ == "__main__":
    main()
