"""sw073 writer (GPU, the UNTRAINED parent only). One vLLM 0.30 engine (vlfix venv, VLLM_LENS_DISABLE=1), thinking off, every
sampler field explicit; engine settings as sw019 gpu19h.py / sw056 open56_gpu.py.

 hist : sw019's history recipe (gpu19h.run_hist logic, copied): for each of sw019's 64 picked v2 TEST scripts
        (sw019 part2/hist/scripts_hist.json), version v in n1..n4 and round r in 0..7, the parent writes the Assistant's turns 1-2
        under system = STYLE[v] + " " + COMMON; per turn 3 candidates (T 0.7, top_p 1, top_k 0, min_p 0, max 2,048), the first that
        passes sw019's screen is kept; turn 2 sees turn 1. Seeds seed_of('sw073h-w', sid, v, turn, r). -> OUT/hist/candidates.jsonl
 open : sw056's opening recipe (open56_gpu.py logic, copied): for each of sw056's 64 picked scripts (sw056 openings.jsonl sids) and
        v in n1..n3, the parent answers the turn-1 user message under system = STYLE[v] + " " + COMMON, K = 8 candidates (max 512,
        seed seed_of('sw073-open', sid, v)); variants = first 1 / 2 complete sentences of 25-40 tokens, screened with sw056's
        screen_opening. -> OUT/open/candidates.jsonl
  --mode smoke : 2 scripts, 2 rounds, K = 2 -> OUT=/root/runs_E5/sw073/smoke_write ; --mode full -> OUT=/root/runs_E5/sw073/write
  Marker OUT/WRITE_DONE after the gates. Gates exit 3."""
import argparse, json, os, sys, time
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common73 as C  # noqa: E402


def log(*a):
    print(time.strftime("%H:%M:%S", time.gmtime()), *a, flush=True)


class Gate(SystemExit):
    pass


def gate(cond, msg):
    if not cond:
        log("GATE_FAIL", msg)
        raise Gate(3)
    log("gate ok:", msg)


class Engine:
    def __init__(self):
        os.environ.setdefault("VLLM_LENS_DISABLE", "1")
        from transformers import AutoTokenizer
        from vllm import LLM, SamplingParams
        from vllm.inputs import TokensPrompt
        self.SP, self.TP = SamplingParams, TokensPrompt
        self.tok = AutoTokenizer.from_pretrained(C.BASE)
        assert self.tok.convert_tokens_to_ids("<|im_end|>") == C.IM_END
        t0 = time.time()
        self.llm = LLM(model=C.BASE, dtype="bfloat16", max_model_len=C.MAX_MODEL_LEN, gpu_memory_utilization=0.88, seed=0, max_num_seqs=384,
                       max_num_batched_tokens=16384, enable_prefix_caching=True, language_model_only=True)
        log(f"ENGINE_READY load {time.time() - t0:.0f}s")

    def render(self, msgs):
        ids = self.tok(self.tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False),
                       add_special_tokens=False)["input_ids"]
        assert ids[-7:] == C.HEADER, ids[-7:]
        return ids

    def ntok(self, t):
        return len(self.tok(t, add_special_tokens=False)["input_ids"])

    def gen(self, prompts, sps):
        return self.llm.generate([self.TP(prompt_token_ids=p) for p in prompts], sps, use_tqdm=False)


def sp(E, n, seed, max_tokens):
    w = dict(C.WRITE_SAMPLER); w["max_tokens"] = max_tokens
    return E.SP(n=n, stop_token_ids=[C.IM_END], skip_special_tokens=True, seed=seed, **w)


# ------------------------------------------------------------------------------------------------ hist (sw019 run_hist logic)
def run_hist(E, S, out, rounds, versions):
    os.makedirs(out, exist_ok=True)
    fn = f"{out}/candidates.jsonl"
    items = [(sid, v, r) for sid in sorted(S) for v in versions for r in range(rounds)]
    keys = [f"sw073|hist|{sid}|{v}|r{r}" for sid, v, r in items]
    assert len(set(keys)) == len(keys)
    C.wjson(f"{out}/manifest.json", dict(keys=keys, rounds=rounds, sids=sorted(S), versions=versions,
                                         writer_system={v: C.writer_system(v) for v in versions}))
    if set(keys) <= {r["key"] for r in C.jl(fn)}:
        log("hist: all rows exist; skipped"); return
    t0 = time.time()
    st = {k: dict(msgs=[{"role": "user", "content": S[k[0]]["u1"]}], ok=True, cands=[], finish=[], n_tok=[]) for k in items}
    for turn in (1, 2):
        ks = [k for k in items if st[k]["ok"]]
        if turn == 2:
            for k in ks:
                st[k]["msgs"].append({"role": "user", "content": S[k[0]]["u2"]})
        prompts = [E.render([{"role": "system", "content": C.writer_system(k[1])}] + st[k]["msgs"]) for k in ks]
        sps = [sp(E, C.N_CAND, C.seed_of("sw073h-w", k[0], k[1], turn, k[2]), 2048) for k in ks]
        for k, o in zip(ks, E.gen(prompts, sps)):
            cs = [dict(text=c.text.strip(), finish=c.finish_reason, n_tok=len(c.token_ids)) for c in o.outputs]
            for c in cs:
                c["why"] = C.screen(c["text"])
            st[k]["cands"].append(cs)
            good = [c for c in cs if not c["why"]]
            if good:
                st[k]["msgs"].append({"role": "assistant", "content": good[0]["text"]})
                st[k]["finish"].append(good[0]["finish"]); st[k]["n_tok"].append(good[0]["n_tok"])
            else:
                st[k]["ok"] = False
        log(f"hist turn {turn}: {len(ks)} prompts x{C.N_CAND}, {time.time() - t0:.0f}s")
    rows = []
    for (sid, v, r), key in zip(items, keys):
        x = st[(sid, v, r)]; s = S[sid]
        rows.append(dict(key=key, sid=sid, scenario=s["scenario"], domain=s["domain"], script_set=s["script_set"], version=v, round=r,
                         pass_screen=x["ok"], messages=x["msgs"], finish=x["finish"], n_tok=x["n_tok"], cands=x["cands"],
                         n_cand_at_cap=sum(c["finish"] == "length" for t in x["cands"] for c in t),
                         u3_trig=s["u3_trig"], u3_ctrl=s["u3_ctrl"], turn4=s["turn4"], turn5=s["turn5"],
                         style_system=C.writer_system(v), writer="parent Qwen3.6-27B (no LoRA)",
                         seed_rule="seed_of('sw073h-w', sid, version, turn, round), n=3, first screen-passing candidate"))
    C.wjl(fn, rows)
    log(f"HIST_WRITTEN {len(rows)} rows ({time.time() - t0:.0f}s)")


def check_hist(out, versions):
    rows = C.jl(f"{out}/candidates.jsonl"); man = json.load(open(f"{out}/manifest.json"))
    keys = [r["key"] for r in rows]
    gate(len(keys) == len(set(keys)) and set(keys) == set(man["keys"]), f"hist keys unique and == manifest ({len(keys)})")
    texts = [c["text"] for r in rows for t in r["cands"] for c in t]
    gate(sum(bool(t) for t in texts) >= 0.95 * len(texts), f"hist candidates non-empty {sum(bool(t) for t in texts)}/{len(texts)}")
    think = sum(("<think>" in t or "</think>" in t) for t in texts)
    log(f"hist: candidates with think tags {think} (report-only; the screen drops them)")
    sids = sorted(set(r["sid"] for r in rows))
    cov = {v: sum(any(r["pass_screen"] for r in rows if r["sid"] == s and r["version"] == v) for s in sids) / max(1, len(sids)) for v in versions}
    why = Counter(w.split("len")[0] or "len" for r in rows for t in r["cands"] for c in t for w in c["why"])
    rate = sum(not c["why"] for r in rows for t in r["cands"] for c in t) / max(1, len(texts))
    log(f"hist: candidate screen-pass rate {rate:.3f}; screen reasons {dict(why)}; per-version coverage {json.dumps({k: round(x, 3) for k, x in cov.items()})}")
    return dict(rate=rate, cov=cov, why=dict(why), think=think)


# ------------------------------------------------------------------------------------------------ open (sw056 open56_gpu logic)
def run_open(E, S1, out, versions, k_cand):
    os.makedirs(out, exist_ok=True)
    fn = f"{out}/candidates.jsonl"
    items = [(sid, v) for sid in sorted(S1) for v in versions]
    keys = [f"sw073|open|{sid}|{v}|c{j}" for sid, v in items for j in range(k_cand)]
    assert len(keys) == len(set(keys))
    C.wjson(f"{out}/manifest.json", dict(keys=keys, sids=sorted(S1), versions=versions, k=k_cand,
                                         writer_system={v: C.writer_system(v) for v in versions}))
    if set(keys) <= {r["key"] for r in C.jl(fn)}:
        log("open: all rows exist; skipped"); return
    t0 = time.time()
    prompts = [E.render([{"role": "system", "content": C.writer_system(v)}, {"role": "user", "content": S1[sid]["user"]}]) for sid, v in items]
    sps = [sp(E, k_cand, C.seed_of("sw073-open", sid, v), C.OPEN_MAXTOK) for sid, v in items]
    rows = []
    for (sid, v), o in zip(items, E.gen(prompts, sps)):
        for j, c in enumerate(o.outputs):
            text = c.text.strip()
            var = []
            for k, op, n in C.opening_variants(text, E.ntok):
                var.append(dict(k_sentences=k, opening=op, n_tok=n, why=C.screen_opening(op)))
            rows.append(dict(key=f"sw073|open|{sid}|{v}|c{j}", sid=sid, scenario=S1[sid]["scenario"], domain=S1[sid].get("domain"), version=v,
                             cand=j, user=S1[sid]["user"], writer_text=text, finish=c.finish_reason, n_tok=len(c.token_ids), variants=var,
                             writer_system=C.writer_system(v), seed_rule="seed_of('sw073-open', sid, version), n=8"))
    C.wjl(fn, rows)
    log(f"OPEN_WRITTEN {len(rows)} candidates ({time.time() - t0:.0f}s)")


def check_open(out, versions):
    rows = C.jl(f"{out}/candidates.jsonl"); man = json.load(open(f"{out}/manifest.json"))
    keys = [r["key"] for r in rows]
    gate(len(keys) == len(set(keys)) and set(keys) == set(man["keys"]), f"open keys unique and == manifest ({len(keys)})")
    gate(sum(bool(r["writer_text"]) for r in rows) >= 0.95 * len(rows), "open writer texts non-empty >= 95%")
    sids = sorted(set(r["sid"] for r in rows))
    cov = {v: sum(any(not x["why"] for r in rows if r["sid"] == s and r["version"] == v for x in r["variants"]) for s in sids) / max(1, len(sids))
           for v in versions}
    nvar = Counter(r["version"] for r in rows for x in r["variants"] if not x["why"])
    log(f"open: screen-passing variants per version {dict(nvar)}; scripts with >= 1 passing variant {json.dumps({k: round(x, 3) for k, x in cov.items()})}")
    return dict(cov=cov, n_pass_variants=dict(nvar))


# ------------------------------------------------------------------------------------------------ main
def load_scripts():
    S = json.load(open(f"{C.SW19HIST}/scripts_hist.json"))["scripts"]
    assert len(S) == 64 and len({s["scenario"] for s in S.values()}) == 64, len(S)
    O = C.jl(C.SW56OPEN)
    S1 = {}
    for r in O:
        S1.setdefault(r["sid"], dict(sid=r["sid"], scenario=r["scenario"], domain=r.get("domain"), user=r["user"]))
    assert len(S1) == 64, len(S1)
    # the sw056 'user' field must equal sw056/sw020's turn-1 construction from the frozen v2 test script
    test = {r["script_id"]: r for r in C.jl(f"{C.SW19DATA}/scripts_v2_test.jsonl")}
    bad = [sid for sid, s in S1.items() if C.user_msg_t1(test[sid]) != s["user"]]
    assert not bad, f"sw056 user messages differ from the v2 construction: {bad[:3]}"
    return S, S1


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--mode", choices=["smoke", "full"], required=True)
    ap.add_argument("--stages", default="hist,open")
    a = ap.parse_args()
    smoke = a.mode == "smoke"
    OUT = f"{C.NODE_RUN}/{'smoke_write' if smoke else 'write'}"
    os.makedirs(OUT, exist_ok=True)
    S, S1 = load_scripts()
    if smoke:
        sel = sorted(S)[:2]; S = {k: S[k] for k in sel}
        sel1 = sorted(S1)[:2]; S1 = {k: S1[k] for k in sel1}
    E = Engine()
    rep = dict(t_start=C.utc(), mode=a.mode)
    st = a.stages.split(",")
    if "hist" in st:
        run_hist(E, S, f"{OUT}/hist", 2 if smoke else C.ROUNDS, C.N_VERSIONS)
        rep["hist"] = check_hist(f"{OUT}/hist", C.N_VERSIONS)
        if smoke:
            gate(all(x > 0 for x in rep["hist"]["cov"].values()), "smoke: every n-version has a screen-passing history")
    if "open" in st:
        run_open(E, S1, f"{OUT}/open", C.OPEN_N, 2 if smoke else C.K_CAND)
        rep["open"] = check_open(f"{OUT}/open", C.OPEN_N)
    rep["t_end"] = C.utc()
    C.wjson(f"{OUT}/write_report.json", rep)
    C.touch(f"{OUT}/WRITE_DONE", json.dumps(rep))
    log("WRITE_DONE")
    return 0


if __name__ == "__main__":
    rc = 1
    try:
        rc = main()
    except Gate as g:
        rc = g.code if isinstance(g.code, int) else 3
    except Exception:  # noqa: BLE001
        import traceback
        traceback.print_exc(); rc = 1
    log(f"exit rc={rc}")
    try:
        import psutil
        for ch in psutil.Process().children(recursive=True):
            ch.kill()
    except Exception as e:  # noqa: BLE001
        log(f"teardown warning: {e!r}"[:200])
    sys.stdout.flush(); sys.stderr.flush()
    os._exit(rc)
