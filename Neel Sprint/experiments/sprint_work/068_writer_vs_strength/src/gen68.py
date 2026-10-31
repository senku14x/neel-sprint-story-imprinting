"""sw068 GPU stages on box C (RTX PRO 6000; vLLM 0.30 per-request LoRA, vlfix venv). Engine, writer procedure, readout loop: sw027's
o1_gen.py (copied, adapted). Design: ../design_spec.md (frozen); decisions: ../DECISIONS.md.

 --smoke-write : adapter check (greedy 64 tokens on 3 fixed trigger prompts; each organism differs from the parent on >= 2 of 3);
                 the parent writes pwm candidates for all 64 scripts: 4 graded prompts (common68.GRADED) x 2 samples, turns 1-2 with
                 sw027's procedure (n = 4 candidates per turn, stop at the first blank line, max 300 tokens, whole-sentence trim to
                 <= 450 chars, length 80-450, sw005's format screens without the habit screen; first passing kept; <= 3 rounds) ->
                 RUN/pwm/candidates.jsonl; then a smoke readout on 2 scripts x 3 arms x 2 models x 3 readouts x 1 sample with a
                 PROVISIONAL pwm (the first formed g2 candidate; smoke only, never analysed) -> RUN/smoke/; gates; throughput.json.
 --full        : needs PWM_SELECTED (sha256 of RUN/pwm/pwm_selected.jsonl); adapter check; contexts [u1, a1, u2, a2, u3] with no system
                 prompt for own / pw / pwm; readouts free (2,048 tokens, primary), btw ("By the way," + 48), raf ("Random animal fact:
                 the" + 48); 2 samples; seed = f(readout, script, sample), paired across arms and models -> RUN/full/.
 gates         : adapter active; no system turn + reply-start header on every readout context; unique keys; expected count;
                 >= 98% non-empty per readout; finish in {stop, length}; >= 90% of pwm candidates formed.
"""
import argparse, json, os, re, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common68 as C  # noqa: E402
sys.path.insert(0, C.LIB)
import labels as LB  # noqa: E402

LABEL = re.compile(r"^\s*(User|Assistant|AI|Human|USER|ASSISTANT)\s*:", re.M)
BRACK = re.compile(r"\[(USER|ASSISTANT)\]", re.I)
AST_ACT = re.compile(r"\*[^*\n]{1,80}\*")
SENT_END = re.compile(r"(?<=[.!?])\s+|(?<=[.!?][\"'’”)\]])\s+")
LEN_MIN, LEN_MAX = 80, 450


def trim_own(text, finish):   # sw027 o1_gen.trim_own, verbatim
    t = (text or "").strip()
    if len(t) <= LEN_MAX and finish != "length":
        return t, False
    parts = SENT_END.split(t)
    out = ""
    for i, p in enumerate(parts):
        last = i == len(parts) - 1
        if last and finish == "length":
            break
        cand = (out + " " + p).strip() if out else p.strip()
        if len(cand) > LEN_MAX:
            break
        out = cand
    return out, True


def screen(text):   # sw027 o1_gen.screen, verbatim
    t = (text or "").strip(); why = []
    if not (LEN_MIN <= len(t) <= LEN_MAX):
        why.append(f"len{len(t)}")
    lx = LB.style_lex(t)
    if lx["ext_p"] or lx["ext_s"]:
        why.append("LEX_EXT")
    if "<think>" in t or LABEL.search(t) or BRACK.search(t):
        why.append("role_marker")
    if AST_ACT.search(t):
        why.append("asterisk")
    if "**" in t or re.search(r"^\s*[-*•]\s", t, re.M) or re.search(r"^\s*\d+\.\s", t, re.M):
        why.append("markdown")
    return why


def smoke_sids(S, n=2):
    by = {}
    for sid in sorted(S):
        by.setdefault(S[sid]["domain"], []).append(sid)
    return sorted(by[d][0] for d in sorted(by)[:n])


def history_of(arm, m, sid, H27, SEL, CAND):
    """the 4 messages behind (arm, model, sid), or None if not formed"""
    if arm in ("own", "pw"):
        h = H27[(arm, m, sid)]
        return h["messages"] if h["formed"] else None
    if SEL is not None:
        r = SEL.get((m, sid))
        return r["messages"] if r else None
    for g in ("g2", "g1", "g3", "g4"):   # smoke only: provisional pwm = the first formed candidate in this order
        for s in range(C.PWM_SAMPLES):
            c = CAND.get((g, sid, s))
            if c and c["formed"]:
                return c["messages"]
    return None


def build_requests(S, sids, H27, SEL, CAND, nsamp, render, readouts=C.READOUTS):
    """Pure function (CPU-testable with a fake render): one request per (readout, arm, model, sid, sample)."""
    reqs = []
    for m in C.ORGS:
        for arm in C.ARMS:
            for sid in sids:
                hist = history_of(arm, m, sid, H27, SEL, CAND)
                if hist is None:
                    continue
                msgs = [dict(x) for x in hist] + [{"role": "user", "content": S[sid]["u3"]}]
                assert [x["role"] for x in msgs] == ["user", "assistant", "user", "assistant", "user"]
                assert msgs[0]["content"] == S[sid]["u1"] and msgs[2]["content"] == S[sid]["u2"]
                ids, txt = render(msgs)
                assert "<|im_start|>system" not in txt, "GATE FAIL: system turn in a readout context"
                assert ids[-7:] == C.HEADER, "GATE FAIL: reply-start header mismatch"
                for ro in readouts:
                    for s in range(nsamp):
                        reqs.append(dict(key=C.rkey(ro, arm, m, sid, s), readout=ro, arm=arm, model=m, sid=sid, sample=s,
                                         scenario=S[sid]["scenario"], domain=S[sid]["domain"], ids=ids, prefix=C.PREFIX[ro],
                                         seed=C.seed_of("sw068r", ro, sid, s), user=S[sid]["u3"]))
    keys = [r["key"] for r in reqs]
    assert len(set(keys)) == len(keys), "GATE FAIL: duplicate reply keys"
    return reqs


class Engine:
    def __init__(self):
        from vllm import LLM, SamplingParams
        from vllm.inputs import TokensPrompt
        from vllm.lora.request import LoRARequest
        from transformers import AutoTokenizer
        self.SP, self.TP = SamplingParams, TokensPrompt
        self.tok = AutoTokenizer.from_pretrained(C.BASE)
        for p in C.LORA.values():
            assert os.path.exists(f"{p}/adapter_model.safetensors"), p
        t0 = time.time()
        # box C: max_num_seqs <= 256 (Mamba cache blocks), gpu_memory_utilization 0.85 (the parity smoke's setting)
        self.llm = LLM(model=C.BASE, dtype="bfloat16", max_model_len=16384, gpu_memory_utilization=0.85, seed=0, max_num_seqs=256,
                       max_num_batched_tokens=16384, enable_prefix_caching=True, language_model_only=True,
                       enable_lora=True, max_lora_rank=32, max_loras=2, max_cpu_loras=2)
        self.lreq = {"parent": None} | {m: LoRARequest(m, i + 1, p) for i, (m, p) in enumerate(C.LORA.items())}
        self.pre = {ro: (self.tok(p, add_special_tokens=False)["input_ids"] if p else []) for ro, p in C.PREFIX.items()}
        self.t_load = time.time() - t0
        print(f"ENGINE_READY {self.t_load:.0f}s", time.strftime("%H:%M:%S"), flush=True)

    def render(self, msgs):
        txt = self.tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False)
        return self.tok(txt, add_special_tokens=False)["input_ids"], txt

    def gen(self, ids_list, sps, models):
        return self.llm.generate([self.TP(prompt_token_ids=p) for p in ids_list], sps, use_tqdm=False,
                                 lora_request=[self.lreq[m] for m in models])

    def sp(self, n, mt, seed, temp=0.7, stop=None):
        return self.SP(n=n, temperature=temp, top_p=1.0, top_k=0, min_p=0.0, repetition_penalty=1.0, max_tokens=mt,
                       stop_token_ids=[C.IM_END], skip_special_tokens=True, seed=seed, stop=stop)


def adapter_check(E, S, out):
    sids = sorted(S)[:3]
    rows = [E.render([{"role": "user", "content": S[sid]["u1"] + " " + S[sid]["u3"]}])[0] for sid in sids]
    res = {}
    for m in ["parent"] + C.ORGS:
        o = E.gen(rows, [E.sp(1, 64, 0, temp=0.0) for _ in rows], [m] * len(rows))
        res[m] = [x.outputs[0].text for x in o]
    diff = {m: sum(a != b for a, b in zip(res[m], res["parent"])) for m in C.ORGS}
    ok = all(d >= 2 for d in diff.values()) and sum(a != b for a, b in zip(res["hdA0"], res["hdB0"])) >= 1
    json.dump(dict(sids=sids, outputs=res, n_differ_from_parent=diff, **{"pass": ok}), open(f"{out}/adapter_check.json", "w"), indent=1)
    print("ADAPTER_CHECK", json.dumps(dict(diff=diff, ok=ok)), flush=True)
    assert ok, "GATE FAIL: adapter not active"


def write_pwm(E, S, sids):
    """sw027 write_stage for writer = parent, styles = the graded prompts, 2 independent samples each. Resumes by key."""
    os.makedirs(C.PWM, exist_ok=True)
    want = [(g, sid, s) for g in C.GRADES for sid in sids for s in range(C.PWM_SAMPLES)]
    H = {}
    for r in C.jl(C.CAND_FILE):
        assert r["system_prompt"] == C.system_prompt(r["grade"]), "GATE FAIL: stale candidate written under another prompt"
        H[(r["grade"], r["sid"], r["sample"])] = r
    todo = [k for k in want if k not in H]
    tt = dict(tok=0, s=0.0)
    tried = {k: [] for k in todo}; done = {}
    for rnd in range(3):
        live = [k for k in todo if k not in done]
        if not live:
            break
        st8 = {k: dict(msgs=[{"role": "user", "content": S[k[1]]["u1"]}], ok=True, cands=[], screens=[], trimmed=[], kept_trimmed=[]) for k in live}
        for turn in (1, 2):
            ks = [k for k in live if st8[k]["ok"]]
            if turn == 2:
                for k in ks:
                    st8[k]["msgs"].append({"role": "user", "content": S[k[1]]["u2"]})
            prompts = [E.render([{"role": "system", "content": C.system_prompt(k[0])}] + st8[k]["msgs"])[0] for k in ks]
            t0 = time.time()
            outs = E.gen(prompts, [E.sp(4, 300, C.seed_of("sw068w", k[0], k[1], k[2], turn, rnd), stop=["\n\n"]) for k in ks], ["parent"] * len(ks))
            tt["s"] += time.time() - t0
            for k, o in zip(ks, outs):
                tt["tok"] += sum(len(c.token_ids) for c in o.outputs)
                tr = [trim_own(c.text, c.finish_reason) for c in o.outputs]
                scr = [screen(t) for t, _ in tr]
                st8[k]["cands"].append([t for t, _ in tr]); st8[k]["screens"].append(scr); st8[k]["trimmed"].append([x for _, x in tr])
                good = [(t, x) for (t, x), w in zip(tr, scr) if not w]
                if good:
                    st8[k]["msgs"].append({"role": "assistant", "content": good[0][0]}); st8[k]["kept_trimmed"].append(good[0][1])
                else:
                    st8[k]["ok"] = False
        for k in live:
            tried[k].append(dict(round=rnd, cands=st8[k]["cands"], screens=st8[k]["screens"], trimmed=st8[k]["trimmed"], ok=st8[k]["ok"]))
            if st8[k]["ok"]:
                assert len(st8[k]["msgs"]) == 4
                done[k] = dict(messages=st8[k]["msgs"], round=rnd, kept_trimmed=st8[k]["kept_trimmed"])
        print(f"pwm write round {rnd}: formed {len(done)} / {len(todo)}", time.strftime("%H:%M:%S"), flush=True)
    for k in todo:
        H[k] = dict(key=C.cand_key(*k), grade=k[0], sid=k[1], sample=k[2], writer="parent", formed=k in done,
                    messages=done[k]["messages"] if k in done else None, round=done[k]["round"] if k in done else None,
                    kept_trimmed=done[k]["kept_trimmed"] if k in done else None, attempts=tried[k], system_prompt=C.system_prompt(k[0]))
    with open(C.CAND_FILE + ".tmp", "w") as f:
        for k in want:
            f.write(json.dumps(H[k]) + "\n")
    os.replace(C.CAND_FILE + ".tmp", C.CAND_FILE)
    n_formed = sum(H[k]["formed"] for k in want)
    print(f"PWM_CANDIDATES {n_formed} / {len(want)} formed; {tt['tok']} tokens in {tt['s']:.0f}s", flush=True)
    return {k: H[k] for k in want}, n_formed / len(want), tt


def heal_tail(fn):
    if os.path.exists(fn) and os.path.getsize(fn) > 0:
        with open(fn, "rb") as f:
            f.seek(-1, os.SEEK_END); last = f.read(1)
        if last != b"\n":
            with open(fn, "a") as f:
                f.write("\n")


def readout(E, reqs, out, chunk=900):
    fn = f"{out}/replies.jsonl"
    heal_tail(fn)
    keys = [r["key"] for r in reqs]
    json.dump(dict(expected_keys=keys, n=len(keys)), open(f"{out}/manifest_replies.json", "w"))
    done = {r["key"] for r in C.jl(fn)}
    todo = [r for r in reqs if r["key"] not in done]
    print(f"readout: {len(reqs)} requests, {len(done)} done, {len(todo)} to run", time.strftime("%H:%M:%S"), flush=True)
    tt = dict(n=0, tok=0, s=0.0, free_tok=0, free_n=0)
    for i in range(0, len(todo), chunk):
        part = todo[i:i + chunk]; t0 = time.time()
        outs = E.gen([r["ids"] + E.pre[r["readout"]] for r in part], [E.sp(1, C.MAXTOK[r["readout"]], r["seed"]) for r in part],
                     [r["model"] for r in part])
        ntok = 0
        with open(fn, "a") as f:
            for r, o in zip(part, outs):
                g = o.outputs[0]; ntok += len(g.token_ids)
                text = r["prefix"] + g.text
                if r["readout"] == "free":
                    tt["free_tok"] += len(g.token_ids); tt["free_n"] += 1
                t512 = (E.tok.decode(list(g.token_ids)[:512], skip_special_tokens=True) if len(g.token_ids) > 512 else g.text) if r["readout"] == "free" else None
                row = dict({k: r[k] for k in ("key", "readout", "arm", "model", "sid", "sample", "scenario", "domain", "seed", "user")},
                           exp="sw068", text=text, gen_text=g.text, n_tok=len(g.token_ids), finish=g.finish_reason,
                           cap_hit=g.finish_reason == "length", text512=t512, strict=LB.strict_label(text), lexicon=LB.lexicon_label(text))
                f.write(json.dumps(row) + "\n")
        dt = time.time() - t0; tt["n"] += len(part); tt["tok"] += ntok; tt["s"] += dt
        print(f"readout chunk {i // chunk}: {len(part)} requests, {ntok} tokens, {dt:.0f}s", time.strftime("%H:%M:%S"), flush=True)
    return keys, tt


def gates(out, keys):
    R = {r["key"]: r for r in C.jl(f"{out}/replies.jsonl")}
    g = dict(n_expected=len(keys), n_found=sum(k in R for k in keys))
    g["all_present"] = g["n_found"] == len(keys)
    rows = [R[k] for k in keys if k in R]
    for ro in C.READOUTS:
        rr = [r for r in rows if r["readout"] == ro]
        g[f"nonempty_{ro}"] = sum(r["n_tok"] >= 1 and bool(r["gen_text"].strip()) for r in rr) / max(1, len(rr))
        g[f"cap_hit_{ro}"] = sum(r["cap_hit"] for r in rr) / max(1, len(rr))
    g["finish_ok"] = all(r["finish"] in ("stop", "length") for r in rows)
    cells = {}
    for r in rows:
        c = cells.setdefault(f"{r['model']}|{r['arm']}|{r['readout']}", dict(n=0, habit=0, rival=0.0))
        lab = LB.role_label(r["strict"], LB.HELPER.get(r["model"]))
        c["n"] += 1
        if lab != "neither":
            c["habit"] += 1; c["rival"] += 1.0 if lab == "rival" else 0.5 if lab == "both" else 0.0
    g["strict_preview"] = {k: dict(n=v["n"], onset=round(v["habit"] / v["n"], 3), rival_share=round(v["rival"] / v["habit"], 3) if v["habit"] else None)
                           for k, v in sorted(cells.items())}
    g["pass"] = bool(g["all_present"] and all(g[f"nonempty_{ro}"] >= 0.98 for ro in C.READOUTS) and g["finish_ok"])
    json.dump(g, open(f"{out}/gates.json", "w"), indent=1)
    print("GATES", json.dumps({k: v for k, v in g.items() if k != "strict_preview"}), flush=True)
    for k, v in g["strict_preview"].items():
        print("  preview", k, v, flush=True)
    assert g["pass"], f"GATE FAIL: {out}/gates.json"
    return g


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--smoke-write", action="store_true"); ap.add_argument("--full", action="store_true")
    a = ap.parse_args()
    assert a.smoke_write != a.full, "use exactly one of --smoke-write / --full"
    C.check_common_against_sw005()
    S = C.load_scripts(); H27 = C.load_sw027(S); kept = sorted(S)
    E = Engine()
    if a.smoke_write:
        out = f"{C.RUN}/smoke"; os.makedirs(out, exist_ok=True)
        adapter_check(E, S, out)
        CAND, frac, wt = write_pwm(E, S, kept)
        assert frac >= 0.90, f"GATE FAIL: only {frac:.2f} of pwm candidates formed"
        reqs = build_requests(S, smoke_sids(S), H27, None, CAND, 1, E.render)
        assert len(reqs) == 36, len(reqs)
        keys, tt = readout(E, reqs, out)
        gates(out, keys)
        # main-run projection: write-stage tokens/s (high concurrency) as the rate; free-reply length from the smoke
        rate = wt["tok"] / max(wt["s"], 1e-9) if wt["s"] > 1 else tt["tok"] / max(tt["s"], 1e-9)
        mean_free = tt["free_tok"] / max(1, tt["free_n"])
        n_free = len(C.ORGS) * len(C.ARMS) * len(kept) * C.NSAMP
        tok_main = n_free * mean_free + 2 * n_free * 48
        est = max(10, round((E.t_load + tok_main / max(rate, 1.0)) / 60 * 1.3 + 2))
        json.dump(dict(write_tok=wt["tok"], write_s=round(wt["s"], 1), rate_tok_s=round(rate, 1), smoke_free_mean_tok=round(mean_free, 1),
                       engine_load_s=round(E.t_load, 1), main_tokens_projected=round(tok_main), est_min=est, pwm_formed_frac=frac),
                  open(f"{out}/throughput.json", "w"), indent=1)
        print("THROUGHPUT", open(f"{out}/throughput.json").read(), flush=True)
        open(f"{C.RUN}/PWM_WRITTEN", "w").write(json.dumps(dict(sha256=C.sha256(C.CAND_FILE), formed_frac=frac, utc=time.strftime("%H:%M:%S"))))
    else:
        SEL = C.load_selected(check_hash=True)
        out = f"{C.RUN}/full"; os.makedirs(out, exist_ok=True)
        adapter_check(E, S, out)
        reqs = build_requests(S, kept, H27, SEL, None, C.NSAMP, E.render)
        n_exp = sum(1 for m in C.ORGS for arm in C.ARMS for sid in kept if history_of(arm, m, sid, H27, SEL, None) is not None) * len(C.READOUTS) * C.NSAMP
        assert len(reqs) == n_exp
        keys, tt = readout(E, reqs, out)
        gates(out, keys)
    print("GEN68_EXIT", flush=True)
    import psutil
    for c in psutil.Process().children(recursive=True):
        try:
            c.kill()
        except Exception:  # noqa: BLE001
            pass


if __name__ == "__main__":  # vLLM spawns its engine core: the main-module guard is required
    main()
