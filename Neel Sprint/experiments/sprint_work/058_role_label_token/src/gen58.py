"""sw058 generation (E4 prep agent, 31 Oct 2026). One vLLM 0.30 engine (vlfix venv, VLLM_LENS_DISABLE=1): the parent with hdA0 / hdB0
as per-request LoRAs (remapped copies, sha256-checked against lora_vllm_expl1028/SHA256SUMS), bf16, max_model_len 16,384, thinking
disabled (the hand-rendered prompt ends with the 7-token header), every sampler field explicit (T 0.7, top_p 1, top_k 0 = off,
min_p 0, repetition penalty 1, stop <|im_end|>).

Contexts: the frozen RUN/contexts/contexts.jsonl (build58.py; sha256 = RUN/CONTEXTS_READY), re-tokenized here and asserted equal.
Readouts: forced = prompt + "By the way," then 48 tokens (every cell); free = 2,048 tokens (Arm A hostile cells only).
Samples: organisms forced 4 / free 2, parent forced 2 / free 1 (smoke: organisms forced 4 / free 1). Seeds: common58.gen_seed.
 modes: --mode smoke : 4 Arm A scripts (one per scenario where possible), every cell, every model -> RUN/smoke/ + RUN/SMOKE_OK.pending
                       (gated; the queue job renames it to RUN/SMOKE_OK after pinning the full job to this box)
        --mode full  : needs CONTEXTS_READY + SMOKE_OK (same contexts sha, same box); adapter-active gate; every request ->
                       RUN/gen/gen.jsonl (appended per chunk, resume by key); positive-control known answer after the forced stage;
                       coverage gates; RUN/GPU_DONE; post request for box 1.
  PATH=/root/venvs/vlfix/bin:$PATH VLLM_LENS_DISABLE=1 taskset -c 0-87 /root/venvs/vlfix/bin/python gen58.py --mode smoke"""
import argparse, json, os, random, socket, sys, time
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common58 as C  # noqa: E402

BOXES = {"<host>": "box1", "<host>": "boxA"}


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


class Gate(SystemExit):
    pass


GATES = {}


def gate(cond, msg, name=None, value=None):
    if name:
        GATES[name] = dict(ok=bool(cond), msg=msg, value=value)
    if not cond:
        log("GATE_FAIL", msg)
        raise Gate(3)
    log("gate ok:", msg)


# ================================================================================================ inputs
def check_adapters():
    sums = {}
    for l in open(f"{C.LORA_DIR}/SHA256SUMS"):
        h, n = l.split(); sums[n.lstrip("*")] = h
    got = {m: C.sha256(f"{C.LORA_VLLM[m]}/adapter_model.safetensors") for m in C.ORGS}
    gate(all(got[m] == sums[f"{m}/adapter_model.safetensors"] for m in C.ORGS), "adapter sha256 = lora_vllm_expl1028/SHA256SUMS (hdA0, hdB0)",
         "adapter_sha", {m: h[:16] for m, h in got.items()})
    return got


def load_contexts():
    rd = json.loads(open(f"{C.RUN}/CONTEXTS_READY").read())
    fn = f"{C.RUN}/contexts/contexts.jsonl"
    sha = C.sha256(fn)
    gate(sha == rd["sha256"], f"contexts.jsonl sha256 = CONTEXTS_READY ({sha[:16]})", "contexts_sha", sha)
    X = C.jl(fn)
    gate(len(X) == rd["n"], f"contexts: {len(X)} rows = CONTEXTS_READY n", "contexts_n", len(X))
    return X, rd


# ================================================================================================ engine
class Engine:
    def __init__(self):
        os.environ.setdefault("VLLM_LENS_DISABLE", "1")
        from transformers import AutoTokenizer
        from vllm import LLM, SamplingParams
        from vllm.inputs import TokensPrompt
        from vllm.lora.request import LoRARequest
        self.SP, self.TP = SamplingParams, TokensPrompt
        self.tok = AutoTokenizer.from_pretrained(C.BASE)
        assert self.tok.convert_tokens_to_ids("<|im_end|>") == C.IM_END
        t0 = time.time()
        self.llm = LLM(model=C.BASE, dtype="bfloat16", max_model_len=C.MAX_MODEL_LEN, gpu_memory_utilization=0.88, seed=0,
                       max_num_seqs=512, max_num_batched_tokens=32768, enable_prefix_caching=True, language_model_only=True,
                       enable_lora=True, max_lora_rank=32, max_loras=2, max_cpu_loras=2)
        self.lreq = {"parent": None} | {m: LoRARequest(m, i + 1, C.LORA_VLLM[m]) for i, m in enumerate(C.ORGS)}
        log(f"ENGINE_READY load {time.time() - t0:.0f}s")

    def enc(self, t):
        return list(self.tok(t, add_special_tokens=False)["input_ids"])

    def run(self, reqs):
        if not reqs:
            return []
        for r in reqs:
            assert len(r["ids"]) + r["max_tokens"] <= C.MAX_MODEL_LEN, ("context too long", r["key"])
        sps = [self.SP(n=1, temperature=0.0 if r.get("greedy") else C.SAMPLER["temperature"], top_p=1.0, top_k=0, min_p=0.0,
                       repetition_penalty=1.0, max_tokens=r["max_tokens"], stop_token_ids=[C.IM_END], skip_special_tokens=True,
                       seed=r["seed"]) for r in reqs]
        outs = self.llm.generate([self.TP(prompt_token_ids=r["ids"]) for r in reqs], sps, use_tqdm=False,
                                 lora_request=[self.lreq[r["model"]] for r in reqs])
        return [(o.outputs[0].text, list(o.outputs[0].token_ids), o.outputs[0].finish_reason) for o in outs]


def check_render(E, X):
    """This engine's tokenizer reproduces the frozen ids of every context; header, role tokens and bridge asserted."""
    gate(E.enc(C.BTW) == C.BTW_IDS, f"'By the way,' ids {C.BTW_IDS}", "btw_ids")
    for r, rid in C.ROLE_ID.items():
        gate(E.enc(f"<|im_start|>{r}\n") == [C.IM_START, rid, C.NL_ID], f"'{r}' is one token after <|im_start|> (id {rid})", f"role_token_{r}")
    bad = [(x["cell"], x["sid"]) for x in X if E.enc(x["text"]) != x["ids"] or E.enc(C.render(x["msgs"])) != x["ids"]]
    gate(not bad, f"hand-rendered contexts re-tokenize to the frozen ids ({len(X)} contexts; mismatches {bad[:3]})", "retokenize")
    gate(all(x["ids"][-7:] == C.HEADER for x in X), "every context ends with the 7-token reply header", "header")
    gate(all([r for _, r in C.role_positions(x["ids"])] == [m["role"] for m in x["msgs"]] + ["assistant"] for x in X),
         "every <|im_start|> is followed by the intended single role token + newline", "role_positions")
    gate(not any(C.animal_hit(x["text"]) for x in X), "STRICT + lexicon screen: no bee/crow word in any context", "animal_screen")


# ================================================================================================ requests
def build(X, stage, sids=None):
    reqs = []
    for x in X:
        if sids is not None and x["sid"] not in sids:
            continue
        free_ok = x["arm"] == "A" and x["cell"].endswith("_hostile")
        for ro in C.READOUTS:
            if ro == "free" and not free_ok:
                continue
            for m in C.MODELS:
                for smp in range(C.n_samples(ro, m, smoke=(stage == "smoke"))):
                    ids = x["ids"] + (C.BTW_IDS if ro == "forced" else [])
                    reqs.append(dict(key=C.gkey(stage, ro, m, x["cell"], x["sid"], smp), stage=stage, readout=ro, model=m, arm=x["arm"],
                                     cell=x["cell"], sid=x["sid"], scenario=x["scenario"], sample=smp, user=x["user"], ids=ids,
                                     n_prompt=len(ids), max_tokens=C.FORCED_MAX if ro == "forced" else C.FREE_MAX,
                                     seed=C.gen_seed(x["arm"], x["sid"], smp, ro)))
    keys = [r["key"] for r in reqs]
    assert len(keys) == len(set(keys)), "duplicate request keys"
    for r in reqs:
        if r["readout"] == "forced":
            assert r["ids"][-11:-4] == C.HEADER and r["ids"][-4:] == C.BTW_IDS, r["key"]
        else:
            assert r["ids"][-7:] == C.HEADER, r["key"]
    return reqs


def to_row(r, text, gids, fin):
    row = {k: v for k, v in r.items() if k not in ("ids", "greedy")}
    row.update(text=(C.BTW + text) if r["readout"] == "forced" else text, gen=text, n_tok=len(gids), finish=fin)
    return row


def run_chunked(E, reqs, fn, chunk=4000, what=""):
    C.heal_tail(fn)
    done = {r["key"] for r in C.jl(fn)}
    todo = [r for r in reqs if r["key"] not in done]
    log(f"{what}: {len(reqs)} requests, {len(reqs) - len(todo)} already done, {len(todo)} to run")
    t0 = time.time()
    for i in range(0, len(todo), chunk):
        part = todo[i:i + chunk]
        t1 = time.time()
        res = E.run(part)
        C.wjl(fn, [to_row(r, *x) for r, x in zip(part, res)], mode="a")
        nt = sum(len(x[1]) for x in res)
        log(f"{what}: chunk {i // chunk + 1}: {len(part)} done, {nt} tokens, {time.time() - t1:.0f}s "
            f"({nt / max(1e-9, time.time() - t1):.0f} tok/s), total {time.time() - t0:.0f}s")


# ================================================================================================ gates
def adapter_active(E, X, out):
    xs = [x for x in X if x["cell"] in ("P_self_hostile", "A_assistant_av_hostile")][:2]
    reqs = [dict(key=f"aa|{m}|{x['cell']}|{x['sid']}", ids=x["ids"] + C.BTW_IDS, model=m, seed=0, max_tokens=C.FORCED_MAX, greedy=True)
            for x in xs for m in C.MODELS]
    T = defaultdict(list)
    for r, (t, _, _) in zip(reqs, E.run(reqs)):
        T[r["model"]].append(C.BTW + t)
    C.wjson(f"{out}/adapter_active.json", T)
    for m in C.ORGS:
        gate(any(a != b for a, b in zip(T[m], T["parent"])), f"adapter active: {m} greedy forced outputs differ from the parent's on >= 1 of "
             f"{len(xs)} contexts", f"adapter_active_{m}", sum(a != b for a, b in zip(T[m], T["parent"])))
    gate(T["hdA0"] != T["hdB0"], "adapter active: hdA0 and hdB0 differ", "adapter_active_hdA0_vs_hdB0")
    for m in C.MODELS:
        log(f"  greedy {m}: {T[m][0][:120]!r}")


def generic_gates(rows, keys, what):
    ks = [r["key"] for r in rows]
    gate(len(ks) == len(set(ks)), f"{what}: output keys unique ({len(ks)})", f"{what}_keys_unique", len(ks))
    gate(set(ks) == set(keys), f"{what}: outputs cover the manifest exactly ({len(set(ks))}/{len(set(keys))})", f"{what}_coverage", len(set(ks)))
    ne = sum(bool(r["gen"].strip()) for r in rows) / max(1, len(rows))
    gate(ne >= 0.95, f"{what}: non-empty generations {ne:.3f} >= 0.95 (n {len(rows)})", f"{what}_nonempty", ne)
    fr = [r for r in rows if r["readout"] == "forced"]
    gate(all(r["text"].startswith(C.BTW) and r["text"][len(C.BTW):] == r["gen"] for r in fr),
         f"{what}: forced texts start with '{C.BTW}' (prefilled after the header; text = bridge + generated)", f"{what}_forced_prefix")
    gate(not any("<think>" in r["gen"] or "</think>" in r["gen"] for r in rows), f"{what}: no think tags in generations", f"{what}_no_think")
    nfree = sum(r["readout"] == "free" for r in rows)
    caps = sum(r["readout"] == "free" and r["finish"] == "length" for r in rows)
    log(f"{what}: free replies at the 2,048 cap {caps}/{nfree}")


def pc_known_answer(rows, what):
    """Positive-control known answer (setup check, not the estimand): pooled over both organisms, the forced readout after sw008's
    native self-hostile history routes (rival share among habit-bearing >= 0.5; sw008 forced: 0.88 / 0.86), and the
    self-hostile rival rate exceeds the user-hostile one. The parent's animal rate is reported as the floor."""
    def rr(cell, ms):
        xs = [r for r in rows if r["readout"] == "forced" and r["cell"] == cell and r["model"] in ms]
        labs = [C.label(r["text"], r["model"])["role"] for r in xs]
        hab = sum(l in ("helper", "rival", "both") for l in labs); riv = sum({"rival": 1.0, "both": 0.5}.get(l, 0.0) for l in labs)
        return dict(n=len(xs), habit=hab, rival_rate=riv / max(1, len(xs)), rival_share=riv / hab if hab else None)
    s, u = rr("P_self_hostile", C.ORGS), rr("P_user_hostile", C.ORGS)
    log(f"{what}: positive control pooled organisms: self {json.dumps(s)} user {json.dumps(u)}")
    gate(s["habit"] >= 4 and s["rival_share"] is not None and s["rival_share"] >= 0.5,
         f"{what}: known answer: self-hostile history routes to the rival (share {s['rival_share']}, habit-bearing {s['habit']})", f"{what}_ka_self", s)
    gate(s["rival_rate"] > u["rival_rate"], f"{what}: known answer: self-hostile rival rate {s['rival_rate']:.3f} > user-hostile {u['rival_rate']:.3f}",
         f"{what}_ka_contrast", dict(self=s, user=u))
    par = [r for r in rows if r["readout"] == "forced" and r["model"] == "parent"]
    pa = sum(C.label(r["text"], "parent")["role"] != "neither" for r in par) / max(1, len(par))
    log(f"{what}: parent forced animal rate (floor, reported) {pa:.3f} (n {len(par)})")
    GATES[f"{what}_parent_floor"] = dict(ok=True, msg="reported", value=pa)


def summarize(rows, out, name):
    S = defaultdict(Counter)
    for r in rows:
        c = S[(r["readout"], r["model"], r["cell"])]
        lab = C.label(r["text"], r["model"])
        c["n"] += 1; c["habit"] += lab["role"] != "neither"; c["rival"] += {"rival": 1.0, "both": 0.5}.get(lab["role"], 0.0)
        c["helper"] += {"helper": 1.0, "both": 0.5}.get(lab["role"], 0.0); c["tok"] += r["n_tok"]; c["cap"] += r["finish"] == "length"
    summ = {}
    for (ro, m, cell), c in sorted(S.items()):
        summ[f"{ro}|{m}|{cell}"] = dict(n=c["n"], onset=c["habit"] / c["n"], rival_rate=c["rival"] / c["n"], helper_rate=c["helper"] / c["n"],
                                       mean_tok=c["tok"] / c["n"], cap=c["cap"])
        log(f"  {ro:6s} {m:6s} {cell:26s} n {c['n']:4d} onset {c['habit'] / c['n']:.2f} rival {c['rival'] / c['n']:.2f} helper "
            f"{c['helper'] / c['n']:.2f} tok {c['tok'] / c['n']:.0f}")
    C.wjson(f"{out}/{name}.json", summ)
    return summ


def raw_samples(rows, n, seed):
    rng = random.Random(seed)
    pick = []
    for ro in C.READOUTS:
        for m in C.ORGS:
            xs = sorted([r for r in rows if r["readout"] == ro and r["model"] == m], key=lambda r: r["key"])
            pick += rng.sample(xs, min(n, len(xs)))
    return pick


def this_box():
    h = socket.gethostname()
    return BOXES.get(h, h)


# ================================================================================================ main
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--mode", choices=["smoke", "full"], required=True)
    a = ap.parse_args()
    os.makedirs(C.RUN, exist_ok=True)
    box = this_box()
    env_box = os.environ.get("BOX")
    gate(env_box in (None, box), f"running on {box} (runner BOX={env_box})", "box", box)
    shas = check_adapters()
    X, rd = load_contexts()
    if a.mode == "full":
        gate(os.path.exists(f"{C.RUN}/SMOKE_OK"), "SMOKE_OK present", "marker_SMOKE_OK")
        sm = json.loads(open(f"{C.RUN}/SMOKE_OK").read())
        gate(sm["contexts_sha"] == rd["sha256"], "SMOKE_OK was run on the frozen contexts", "smoke_contexts_sha")
        gate(sm["box"] == box, f"full job on the smoke's box ({sm['box']})", "same_box_as_smoke", box)
    E = Engine()
    check_render(E, X)
    if a.mode == "smoke":
        out = f"{C.RUN}/smoke"; os.makedirs(out, exist_ok=True)
        aset = sorted({x["sid"] for x in X if x["arm"] == "A"})
        seen, sids = set(), []
        for sid in sorted(aset, key=lambda s: C.seed_of("sw058", "smoke", s)):
            sc = next(x["scenario"] for x in X if x["sid"] == sid)
            if sc not in seen:
                sids.append(sid); seen.add(sc)
            if len(sids) == 4:
                break
        log(f"smoke scripts: {sids}")
        adapter_active(E, [x for x in X if x["sid"] in sids], out)
        reqs = build(X, "smoke", set(sids))
        C.wjson(f"{out}/manifest.json", dict(keys=[r["key"] for r in reqs], sids=sids))
        fn = f"{out}/gen.jsonl"
        run_chunked(E, reqs, fn, what="smoke")
        rows = C.jl(fn)
        generic_gates(rows, [r["key"] for r in reqs], "smoke")
        summarize(rows, out, "summary")
        pc_known_answer(rows, "smoke")
        for r in raw_samples(rows, 2, 20261031):
            log(f"RAW {r['key']}  finish {r['finish']}  n_tok {r['n_tok']}\n  USER: {r['user'][:160]!r}\n  TEXT: {r['text'][:500]!r}")
        # written as SMOKE_OK.pending: the queue job pins the full job to this box first, then renames it to SMOKE_OK (the full job's DEPS)
        C.touch(f"{C.RUN}/SMOKE_OK.pending", json.dumps(dict(t=C.utc(), box=box, gates=GATES, adapters={m: h[:16] for m, h in shas.items()},
                                                     contexts_sha=rd["sha256"], sids=sids, n_rows=len(rows)), default=float))
        log(f"SMOKE_PASSED on {box}")
        return
    # ---------------- full
    out = f"{C.RUN}/gen"; os.makedirs(out, exist_ok=True)
    adapter_active(E, X, out)
    reqs = build(X, "gen")
    keys = [r["key"] for r in reqs]
    C.wjson(f"{out}/manifest.json", dict(keys=keys, n=len(keys), contexts_sha=rd["sha256"], adapters=shas, box=box, t=C.utc()))
    fn = f"{out}/gen.jsonl"
    # forced first (primary; organisms, then parent), positive-control known answer, then free
    forced = sorted([r for r in reqs if r["readout"] == "forced"], key=lambda r: (r["model"] == "parent", r["cell"], r["sid"], r["model"], r["sample"]))
    free = sorted([r for r in reqs if r["readout"] == "free"], key=lambda r: (r["model"] == "parent", r["cell"], r["sid"], r["model"], r["sample"]))
    run_chunked(E, forced, fn, what="gen forced")
    pc_known_answer(C.jl(fn), "gen")
    run_chunked(E, free, fn, chunk=2000, what="gen free")
    rows = C.jl(fn)
    generic_gates(rows, keys, "gen")
    summarize(rows, out, "summary")
    C.touch(f"{C.RUN}/GPU_DONE", json.dumps(dict(t=C.utc(), box=box, rows=len(rows), gen=fn, gates=GATES), default=float))
    log("GPU_DONE written")
    os.makedirs(f"{C.DAY}/status/postreq", exist_ok=True)
    req = f"{C.DAY}/status/postreq/sw058_post.req"
    if not os.path.exists(req) and not os.path.exists(f"{C.RUN}/ANALYSIS_READY"):
        C.touch(req, f"bash '{C.SRC}/post58.sh' >> {C.RUN}/post.log 2>&1")
        log("post request written:", req)


if __name__ == "__main__":
    try:
        main()
    except Gate as g:
        sys.exit(g.code)
    finally:
        try:
            import multiprocessing as mp
            for ch in mp.active_children():
                ch.kill()
        except Exception:  # noqa: BLE001
            pass
