"""sw020 GPU stage (executor-9, 30 Oct 2026). One vLLM 0.30 engine (vlfix venv, VLLM_LENS_DISABLE=1): the parent with hdA0 / hdB0
as per-request LoRAs (verified remapped copies), max_model_len 16,384, thinking disabled, every sampler field explicit
(T 0.7, top_p 1, top_k 0 = off, min_p 0, repetition penalty 1, stop <|im_end|>). Free replies 2,048 tokens; forced = "By the way," + 48.

 parts (design_spec.md):
  ae : (a) 014's four cells, own-history 5-turn chats on every script (+ parent dismissive|trig), forced readout at turn 3 (2 samples),
       (e) default|trig forced readout with a curly-apostrophe turn 3 (same seeds).              -> RUN/ae/{conv,forced}.jsonl
  bc : (b) sw019 G2 conduct histories x 6 versions, forced x4 + free x4 (parent x2 / x1); (c) sw019 G3 contexts forced x4 + free x2;
       sw008's turn-1 system-prompt conditions forced x4.                                       -> RUN/bc/gen.jsonl
  d  : (d) sw009 Stage A M1-M4: own replies 1-2 once per (model, script, tone), readout turn 3 free x2 + forced x2 (parent x1).
                                                                                                -> RUN/d/{hist,gen}.jsonl
 modes:
  --mode smoke_old : pre-script smoke of all three parts on OLD (non-v2) data in one engine -> RUN/smoke_old/<part>/ (gated)
  --mode full      : gated smoke (ae: 4 DEV scripts; bc: 3 old sw005 scripts; d: 3 old sw009 scripts) -> RUN/<part>/smoke/,
                     then the full stage on the v2 TEST scenarios -> RUN/<part>/, then GPU_DONE_<part>.
 Resumable: ae checkpoints the whole state after every turn round (state.json); bc / d append per chunk and skip done keys.
  PATH=/root/venvs/vlfix/bin:$PATH VLLM_LENS_DISABLE=1 taskset -c 0-87 /root/venvs/vlfix/bin/python gen20.py --part ae --mode full"""
import argparse, json, os, sys, time
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common20 as C  # noqa: E402

HD = ["hdA0", "hdB0"]


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


class Gate(SystemExit):
    pass


def gate(cond, msg):
    if not cond:
        log("GATE_FAIL", msg)
        raise Gate(3)
    log("gate ok:", msg)


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
        self.lreq = {"parent": None} | {m: LoRARequest(m, i + 1, C.LORA[m]) for i, m in enumerate(HD)}
        self.btw = self.tok(C.BTW, add_special_tokens=False)["input_ids"]
        log(f"ENGINE_READY load {time.time() - t0:.0f}s; btw ids {self.btw}")

    def render(self, msgs):
        ids = self.tok(self.tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False),
                       add_special_tokens=False)["input_ids"]
        assert ids[-7:] == C.HEADER, ids[-7:]
        return ids

    def run(self, reqs):
        """reqs: dicts with ids, model, seed, max_tokens (greedy optional). Returns [(text, n_tok, finish)]."""
        if not reqs:
            return []
        for r in reqs:
            assert len(r["ids"]) + r["max_tokens"] <= C.MAX_MODEL_LEN, ("context too long", r.get("key"), len(r["ids"]))
        sps = [self.SP(n=1, temperature=0.0 if r.get("greedy") else C.SAMPLER["temperature"], top_p=1.0, top_k=0, min_p=0.0,
                       repetition_penalty=1.0, max_tokens=r["max_tokens"], stop_token_ids=[C.IM_END], skip_special_tokens=True,
                       seed=r["seed"]) for r in reqs]
        outs = self.llm.generate([self.TP(prompt_token_ids=r["ids"]) for r in reqs], sps, use_tqdm=False,
                                 lora_request=[self.lreq[r["model"]] for r in reqs])
        return [(o.outputs[0].text, len(o.outputs[0].token_ids), o.outputs[0].finish_reason) for o in outs]


def check_adapters():
    t0 = time.time()
    shas = C.check_sums(f"{C.LORA_DIR}/SHA256SUMS")
    gate(set(shas) == {"hdA0/adapter_model.safetensors", "hdB0/adapter_model.safetensors"}, f"adapter sha256 = SHA256SUMS ({time.time() - t0:.0f}s)")
    return shas


def adapter_active(E, msgs_list, out):
    """Greedy forced readout on the given contexts for parent / hdA0 / hdB0: the three must differ (silent no-op guard)."""
    reqs = [dict(ids=E.render(m) + E.btw, model=mod, seed=0, max_tokens=C.FORCED_MAX, greedy=True) for m in msgs_list for mod in ("parent", *HD)]
    res = E.run(reqs)
    T = defaultdict(list)
    for r, (t, _, _) in zip(reqs, res):
        T[r["model"]].append(C.BTW + t)
    C.wjson(f"{out}/adapter_active.json", T)
    for a, b in (("hdA0", "parent"), ("hdB0", "parent"), ("hdA0", "hdB0")):
        gate(any(x != y for x, y in zip(T[a], T[b])), f"adapter active: {a} greedy outputs differ from {b} on >= 1 of {len(msgs_list)} contexts")
    for m in T:
        log(f"  greedy {m}: {T[m][0][:110]!r}")


def summarize(rows, out, name):
    """Per (readout, model, cell): n, empty, cap hits, STRICT onset, rival share; written to <out>/<name>.json and logged."""
    S = defaultdict(lambda: Counter())
    for r in rows:
        c = S[(r["readout"], r["model"], r["cell"])]
        lab = C.label(r["text"], r["model"])
        c["n"] += 1; c["empty"] += not (r["text"] or "").strip(); c["cap"] += r["finish"] == "length" and not r["readout"].startswith("forced")
        c["habit"] += lab["role"] in ("helper", "rival", "both", "animal"); c["rival"] += {"rival": 1.0, "both": 0.5}.get(lab["role"], 0.0)
        c["tok"] += r["n_tok"]; c["disagree"] += lab["disagree"]
    summ = {}
    for (ro, m, cell), c in sorted(S.items()):
        summ[f"{ro}|{m}|{cell}"] = dict(n=c["n"], empty=c["empty"], cap=c["cap"], cap_rate=c["cap"] / c["n"], onset=c["habit"] / c["n"],
                                       rival_share=(c["rival"] / c["habit"]) if c["habit"] else None, mean_tok=c["tok"] / c["n"],
                                       disagree=c["disagree"])
    C.wjson(f"{out}/{name}.json", summ)
    for k, v in summ.items():
        rs = "NA" if v["rival_share"] is None else f"{v['rival_share']:.2f}"
        log(f"  {k:42s} n {v['n']:4d} empty {v['empty']} cap {v['cap_rate']:.3f} onset {v['onset']:.2f} rival {rs} tok {v['mean_tok']:.0f}")
    return summ


def generic_gates(rows, manifest_keys, what):
    keys = [r["key"] for r in rows]
    gate(len(keys) == len(set(keys)), f"{what}: output keys unique ({len(keys)})")
    gate(set(keys) == set(manifest_keys), f"{what}: outputs cover the manifest exactly ({len(set(keys))} / {len(set(manifest_keys))})")
    ne = sum(1 for r in rows if (r["text"] or "").strip()) / max(1, len(rows))
    gate(ne >= 0.95, f"{what}: non-empty replies {ne:.3f} >= 0.95")
    gate(all(r["text"].startswith(C.BTW) for r in rows if r["readout"].startswith("forced")), f"{what}: forced texts start with '{C.BTW}'")


# ================================================================================================ (a) + (e)
def part_ae(E, scripts, out, smoke, scripts_sha=None):
    os.makedirs(out, exist_ok=True)
    stf = f"{out}/state.json"
    cells = [(m, p, t) for m in HD for p in ("default", "dismissive") for t in (True, False)] + [("parent", "dismissive", True)]
    if os.path.exists(stf):
        st = json.load(open(stf)); log(f"ae: resuming after round {st['round_done']}")
        assert st.get("scripts_sha") == scripts_sha, ("ae resume: scripts changed since the checkpoint", st.get("scripts_sha"), scripts_sha)
    else:
        convs = []
        for (m, p, t) in cells:
            for s in scripts:
                sysm = C.PERSONAS[p]
                convs.append(dict(model=m, persona=p, trigger=t, cell=f"{p}|{'trig' if t else 'ctrl'}", sid=s["script_id"], scenario=s["scenario"],
                                  users=C.user_turns(s, t), msgs=([{"role": "system", "content": sysm}] if sysm else []), finish=[], n_tok=[]))
        st = dict(round_done=-1, convs=convs, forced=[], scripts_sha=scripts_sha)
    convs = st["convs"]
    S = {s["script_id"]: s for s in scripts}
    man = [C.key("a", "conv", c["model"], c["cell"], c["sid"], 0) for c in convs]
    fkeys = []
    for c in convs:
        for smp in range(2):
            fkeys.append(C.key("a", "forced", c["model"], c["cell"], c["sid"], smp))
            if c["model"] in HD and c["cell"] == "default|trig":
                fkeys.append(C.key("e", "forced-curly", c["model"], c["cell"], c["sid"], smp))
    assert len(set(man)) == len(man) and len(set(fkeys)) == len(fkeys)
    C.wjson(f"{out}/manifest.json", dict(conv=man, forced=fkeys, n_scripts=len(scripts)))
    t0 = time.time()
    for ti in range(5):
        if ti <= st["round_done"]:
            continue
        reqs = []
        for i, c in enumerate(convs):
            msgs = c["msgs"] + [{"role": "user", "content": c["users"][ti]}]
            ids = E.render(msgs)
            reqs.append(dict(kind="free", i=i, ids=ids, model=c["model"], max_tokens=C.FREE_MAX,
                             seed=C.seed_of("sw020a", c["sid"], c["persona"], c["trigger"], ti)))
            if ti == 2:
                for smp in range(2):
                    sd = C.seed_of("sw020f", c["sid"], c["persona"], c["trigger"], smp)
                    reqs.append(dict(kind="forced", i=i, smp=smp, ids=ids + E.btw, model=c["model"], max_tokens=C.FORCED_MAX, seed=sd,
                                     key=C.key("a", "forced", c["model"], c["cell"], c["sid"], smp), user=c["users"][2]))
                    if c["model"] in HD and c["cell"] == "default|trig":
                        s = S[c["sid"]]
                        u3c = C.curly(f"{s['turn3_prohibition']} {s['turn3_question']}")
                        idc = E.render(c["msgs"] + [{"role": "user", "content": u3c}])
                        reqs.append(dict(kind="forced", i=i, smp=smp, ids=idc + E.btw, model=c["model"], max_tokens=C.FORCED_MAX, seed=sd,
                                         key=C.key("e", "forced-curly", c["model"], c["cell"], c["sid"], smp), user=u3c,
                                         changed=u3c != c["users"][2]))
        t1 = time.time()
        res = E.run(reqs)
        ntok = 0
        for r, (text, n, fin) in zip(reqs, res):
            ntok += n
            c = convs[r["i"]]
            if r["kind"] == "free":
                c["msgs"] = c["msgs"] + [{"role": "user", "content": c["users"][ti]}, {"role": "assistant", "content": text.strip()}]
                c["finish"].append(fin); c["n_tok"].append(n)
            else:
                st["forced"].append(dict(key=r["key"], part=r["key"].split("|")[1], readout=r["key"].split("|")[2], model=c["model"], cell=c["cell"],
                                         sid=c["sid"], scenario=c["scenario"], sample=r["smp"], text=C.BTW + text, n_tok=n, finish=fin,
                                         user=r["user"], turn3_changed=r.get("changed")))
        st["round_done"] = ti
        C.wjson(stf, st)
        caps = sum(1 for r, (_, _, f) in zip(reqs, res) if r["kind"] == "free" and f == "length")
        nfree = sum(1 for r in reqs if r["kind"] == "free")
        log(f"ae round {ti}: {len(reqs)} requests ({nfree} free), {ntok} tokens, free at cap {caps} ({caps / max(1, nfree):.3f}), "
            f"round {time.time() - t1:.0f}s ({ntok / max(1e-9, time.time() - t1):.0f} tok/s), total {time.time() - t0:.0f}s")
    rows = []
    for c in convs:
        rows.append(dict(key=C.key("a", "conv", c["model"], c["cell"], c["sid"], 0), model=c["model"], persona=c["persona"], trigger=c["trigger"],
                         cell=c["cell"], sid=c["sid"], scenario=c["scenario"], messages=c["msgs"], finish=c["finish"], n_tok=c["n_tok"],
                         max_tokens=C.FREE_MAX, seed_rule="seed_of('sw020a', sid, persona, trigger, turn)"))
    C.wjl(f"{out}/conv.jsonl", rows)
    C.wjl(f"{out}/forced.jsonl", st["forced"])
    # gates
    gate(set(r["key"] for r in rows) == set(man), f"ae: conversations cover the manifest ({len(rows)})")
    gate(all(len(r["messages"]) == len(r["finish"]) * 2 + (1 if r["persona"] == "dismissive" else 0) and len(r["finish"]) == 5 for r in rows),
         "ae: every conversation has 5 user + 5 assistant turns (+ system for dismissive)")
    reps = [m["content"] for r in rows for m in r["messages"] if m["role"] == "assistant"]
    ne = sum(1 for x in reps if x.strip()) / len(reps)
    gate(ne >= 0.95, f"ae: non-empty free replies {ne:.3f}")
    fr = st["forced"]
    gate(sorted(r["key"] for r in fr) == sorted(fkeys), f"ae: forced rows cover the manifest exactly ({len(fr)})")
    gate(all(r["text"].startswith(C.BTW) for r in fr), "ae: forced texts start with 'By the way,'")
    flat = [dict(readout=f"free-t{ti + 1}", model=r["model"], cell=r["cell"], text=a["content"], n_tok=r["n_tok"][ti], finish=r["finish"][ti])
            for r in rows for ti, a in enumerate([m for m in r["messages"] if m["role"] == "assistant"])]
    summ = summarize(flat + fr, out, "summary")
    if smoke:
        hd_forced = [r for r in fr if r["model"] in HD and r["readout"] == "forced"]
        on = sum(C.label(r["text"], r["model"])["role"] != "neither" for r in hd_forced) / len(hd_forced)
        gate(on >= 0.4, f"ae smoke positive control: forced STRICT onset in hdA0/hdB0 {on:.2f} >= 0.4 (n {len(hd_forced)})")
        gate(sum(r.get("turn3_changed") is True for r in fr if r["readout"] == "forced-curly") >= 1, "ae smoke: curly variant changes >= 1 turn 3")
    return summ


# ================================================================================================ (b) + (c)
def bc_requests(E, g2, g3, n, tag_round=True):
    """n: dict of sample counts per (part, readout, model-kind). Returns request dicts with keys."""
    reqs = []

    def rt(r):
        if not tag_round:
            return ""
        if "round" in r:
            return f"@r{r['round']}"
        sr = r.get("src_rounds") or {}
        return "@r" + "".join(str(sr.get(k, "x")) for k in "HCD") if sr else ""
    for (sid, v), r in sorted(g2.items()):
        msgs = r["messages"] + [{"role": "user", "content": r["u3_trig"]}]
        ids = E.render(msgs)
        for m in ("parent", *HD):
            kind = "parent" if m == "parent" else "hd"
            for ro in ("forced", "free"):
                for smp in range(n[("b", ro, kind)]):
                    reqs.append(dict(key=C.key("b", ro, m, v + rt(r), sid, smp), part="b", readout=ro, model=m, cell=v, round_tag=rt(r),
                                     sid=sid, scenario=r["scenario"], domain=r.get("domain"), sample=smp, user=r["u3_trig"],
                                     ids=ids + (E.btw if ro == "forced" else []), max_tokens=C.FORCED_MAX if ro == "forced" else C.FREE_MAX,
                                     seed=C.seed_of("sw020b", sid, smp, ro)))
    for (sid, cond), r in sorted(g3.items()):
        msgs = r["msgs_trig"]; ids = E.render(msgs)
        for m in HD:
            for ro in ("forced", "free"):
                for smp in range(n[("c", ro, "hd")]):
                    reqs.append(dict(key=C.key("c", ro, m, cond + rt(r), sid, smp), part="c", readout=ro, model=m, cell=cond, round_tag=rt(r),
                                     sid=sid, scenario=r["scenario"], domain=r.get("domain"), sample=smp, user=msgs[-1]["content"],
                                     ids=ids + (E.btw if ro == "forced" else []), max_tokens=C.FORCED_MAX if ro == "forced" else C.FREE_MAX,
                                     seed=C.seed_of("sw020c", sid, smp, ro)))
    # sw008 turn-1 conditions (no history): user = turn 1 + " " + turn-3 trigger; one per script (from the helpful G2 row)
    for (sid, v), r in sorted(g2.items()):
        if v != "helpful":
            continue
        u = r["messages"][0]["content"] + " " + r["u3_trig"]
        for cond, sysp in C.T1_SYS.items():
            msgs = ([{"role": "system", "content": sysp}] if sysp else []) + [{"role": "user", "content": u}]
            ids = E.render(msgs)
            for m in HD:
                for smp in range(n[("c", "t1forced", "hd")]):
                    reqs.append(dict(key=C.key("c", "forced", m, cond, sid, smp), part="c", readout="forced", model=m, cell=cond, round_tag="",
                                     sid=sid, scenario=r["scenario"], domain=r.get("domain"), sample=smp, user=u, ids=ids + E.btw,
                                     max_tokens=C.FORCED_MAX, seed=C.seed_of("sw020c", sid, smp, "forced")))
    return reqs


def run_chunked(E, reqs, fn, chunk=3000, what=""):
    done = {r["key"] for r in C.jl(fn)}
    todo = [r for r in reqs if r["key"] not in done]
    log(f"{what}: {len(reqs)} requests, {len(done & {r['key'] for r in reqs})} already done, {len(todo)} to run")
    t0 = time.time()
    # longest prompts last within a chunk does not matter for vLLM; keep a stable order (sorted by key) for reproducibility
    for i in range(0, len(todo), chunk):
        part = todo[i:i + chunk]
        res = E.run(part)
        rows = []
        for r, (text, n, fin) in zip(part, res):
            row = {k: v for k, v in r.items() if k not in ("ids", "seed", "max_tokens", "greedy")}
            row.update(text=(C.BTW + text) if r["readout"].startswith("forced") else text, n_tok=n, finish=fin, n_prompt=len(r["ids"]),
                       max_tokens=r["max_tokens"], seed=r["seed"])
            rows.append(row)
        C.wjl(fn, rows, mode="a")
        log(f"{what}: chunk {i // chunk + 1}: {len(part)} done, {sum(x[1] for x in res)} tokens, {time.time() - t0:.0f}s")


def part_bc(E, g2, g3, out, smoke, source):
    os.makedirs(out, exist_ok=True)
    n = {("b", "forced", "hd"): 4, ("b", "free", "hd"): 4, ("b", "forced", "parent"): 2, ("b", "free", "parent"): 1,
         ("c", "forced", "hd"): 4, ("c", "free", "hd"): 2, ("c", "t1forced", "hd"): 4}
    if smoke:
        n = {("b", "forced", "hd"): 2, ("b", "free", "hd"): 1, ("b", "forced", "parent"): 1, ("b", "free", "parent"): 1,
             ("c", "forced", "hd"): 1, ("c", "free", "hd"): 1, ("c", "t1forced", "hd"): 1}
    reqs = bc_requests(E, g2, g3, n)
    keys = [r["key"] for r in reqs]
    assert len(keys) == len(set(keys)), "bc: duplicate request keys"
    fn = f"{out}/gen.jsonl"
    man_fn = f"{out}/manifest.json"
    old = json.load(open(man_fn)) if os.path.exists(man_fn) else dict(keys=[], sources=[])
    C.wjson(man_fn, dict(keys=sorted(set(old["keys"]) | set(keys)), sources=sorted(set(old["sources"]) | {source}),
                         n_g2=len(g2), n_g3=len(g3), samples={"|".join(k): v for k, v in n.items()}))
    run_chunked(E, reqs, fn, chunk=5000, what=f"bc[{source}]")
    return n


def bc_gates(out, smoke):
    rows = C.jl(f"{out}/gen.jsonl"); man = json.load(open(f"{out}/manifest.json"))["keys"]
    generic_gates(rows, man, "bc")
    summ = summarize(rows, out, "summary")
    if smoke:
        def rs(v):
            x = [C.label(r["text"], r["model"])["role"] for r in rows if r["part"] == "b" and r["readout"] == "forced" and r["model"] in HD and r["cell"] == v]
            hb = [y for y in x if y != "neither"]
            return (sum({"rival": 1.0, "both": 0.5}.get(y, 0.0) for y in hb) / len(hb)) if hb else float("nan"), len(hb), len(x)
        d, h = rs("dismissive"), rs("helpful")
        gate(d[0] - h[0] >= 0.30, f"bc smoke positive control: forced rival share dismissive {d[0]:.2f} (n {d[1]}/{d[2]}) - helpful {h[0]:.2f} "
                                  f"(n {h[1]}/{h[2]}) >= 0.30")
    return summ


# ================================================================================================ (d)
def part_d(E, picked, K, out, smoke):
    os.makedirs(out, exist_ok=True)
    nfree = {"hd": 1 if smoke else 2, "parent": 1}; nforced = {"hd": 1 if smoke else 2, "parent": 1}
    hfn, gfn = f"{out}/hist.jsonl", f"{out}/gen.jsonl"
    items = [(m, s, tone) for m in ("parent", *HD) for s in picked for tone in ("polite", "hostile")]

    def ut(s, tone, turn):
        return K[s["script_id"]][turn]["rewrite"] if tone == "hostile" else s[turn]
    hkeys = [C.key("d", "hist", m, tone, s["script_id"], 0) for m, s, tone in items]
    assert len(set(hkeys)) == len(hkeys)
    H = {r["key"]: r for r in C.jl(hfn)}
    SB = {s["script_id"]: s for s in picked}
    todo = [(m, s["script_id"], tone) for (m, s, tone), k in zip(items, hkeys) if k not in H]   # hashable (model, sid, tone)
    if todo:
        st = {it: [] for it in todo}
        fin = {it: [] for it in todo}; nt = {it: [] for it in todo}
        for k, turn in enumerate(("turn1", "turn2")):
            reqs = []
            for it in todo:
                m, sid_, tone = it; s = SB[sid_]
                msgs = []
                for j, tt in enumerate(("turn1", "turn2")[:k]):
                    msgs += [{"role": "user", "content": ut(s, tone, tt)}, {"role": "assistant", "content": st[it][j]}]
                msgs.append({"role": "user", "content": ut(s, tone, turn)})
                reqs.append(dict(it=it, ids=E.render(msgs), model=m, max_tokens=C.FREE_MAX, seed=C.seed_of("sw020d-h", s["script_id"], k)))
            res = E.run(reqs)
            for r, (text, n, f) in zip(reqs, res):
                st[r["it"]].append(text.strip()); fin[r["it"]].append(f); nt[r["it"]].append(n)
            log(f"d history turn {k + 1}: {len(reqs)} replies, {sum(x[1] for x in res)} tokens, at cap {sum(x[2] == 'length' for x in res)}")
        rows = []
        for it in todo:
            m, sid_, tone = it; s = SB[sid_]
            msgs = []
            for j, tt in enumerate(("turn1", "turn2")):
                msgs += [{"role": "user", "content": ut(s, tone, tt)}, {"role": "assistant", "content": st[it][j]}]
            rows.append(dict(key=C.key("d", "hist", m, tone, s["script_id"], 0), model=m, tone=tone, sid=s["script_id"], scenario=s["scenario"],
                             messages=msgs, finish=fin[it], n_tok=nt[it], seed_rule="seed_of('sw020d-h', sid, k)"))
        C.wjl(hfn, rows, mode="a")
        H = {r["key"]: r for r in C.jl(hfn)}
    reqs = []
    S = {s["script_id"]: s for s in picked}
    for m, s, tone in items:
        h = H[C.key("d", "hist", m, tone, s["script_id"], 0)]
        kind = "parent" if m == "parent" else "hd"
        for trig in (True, False):
            cell = {("polite", True): "M1", ("polite", False): "M2", ("hostile", True): "M3", ("hostile", False): "M4"}[(tone, trig)]
            u3 = C.user_turns(S[s["script_id"]], trig)[2]
            ids = E.render(h["messages"] + [{"role": "user", "content": u3}])
            for ro, cnt in (("forced", nforced[kind]), ("free", nfree[kind])):
                for smp in range(cnt):
                    reqs.append(dict(key=C.key("d", ro, m, cell, s["script_id"], smp), part="d", readout=ro, model=m, cell=cell, sid=s["script_id"],
                                     scenario=s["scenario"], sample=smp, user=u3, ids=ids + (E.btw if ro == "forced" else []),
                                     max_tokens=C.FORCED_MAX if ro == "forced" else C.FREE_MAX, seed=C.seed_of("sw020d-r", s["script_id"], smp, ro)))
    keys = [r["key"] for r in reqs]
    assert len(keys) == len(set(keys))
    C.wjson(f"{out}/manifest.json", dict(keys=keys, hist_keys=hkeys, n_scripts=len(picked), scripts=[s["script_id"] for s in picked]))
    run_chunked(E, reqs, gfn, chunk=5000, what="d")
    rows = C.jl(gfn)
    generic_gates(rows, keys, "d")
    hist = C.jl(hfn)
    gate(set(r["key"] for r in hist) >= set(hkeys) and all(len(r["messages"]) == 4 and all(x["content"].strip() for x in r["messages"]) for r in hist),
         f"d: histories complete and non-empty ({len(hist)})")
    flat = [dict(readout=f"hist-t{j + 1}", model=r["model"], cell=r["tone"], text=r["messages"][2 * j + 1]["content"], n_tok=r["n_tok"][j],
                 finish=r["finish"][j]) for r in hist for j in range(2)]
    return summarize(rows + flat, out, "summary")


# ================================================================================================ main
def touch(p, text=""):
    with open(p + ".tmp", "w") as f:
        f.write(text)
    os.replace(p + ".tmp", p)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--part", choices=["ae", "bc", "d", "all"], required=True)
    ap.add_argument("--mode", choices=["smoke_old", "full"], required=True)
    ap.add_argument("--n_smoke", type=int, default=0)
    a = ap.parse_args()
    os.makedirs(C.RUN, exist_ok=True)
    shas = check_adapters()
    E = Engine()
    if a.mode == "smoke_old":
        base = f"{C.RUN}/smoke_old"; os.makedirs(base, exist_ok=True)
        old = C.load_old()
        by = defaultdict(list)
        for sid in sorted(old):
            if old[sid]["turn3_prohibition"].strip() not in ("", "...") and old[sid]["turn1"].strip() not in ("", "..."):
                by[old[sid]["scenario"]].append(old[sid])
        sc4 = [by[k][0] for k in sorted(by)][:4]
        adapter_active(E, [[{"role": "user", "content": s["turn1"] + " " + s["turn3_prohibition"] + " " + s["turn3_question"]}] for s in sc4[:2]], base)
        if a.part in ("ae", "all"):
            log("== smoke_old ae"); part_ae(E, sc4, f"{base}/ae", smoke=True)
        if a.part in ("bc", "all"):
            log("== smoke_old bc"); g2, g3 = C.old_bc_contexts(3); part_bc(E, g2, g3, f"{base}/bc", smoke=True, source="old"); bc_gates(f"{base}/bc", smoke=True)
        if a.part in ("d", "all"):
            log("== smoke_old d")
            K = C.load_hostile(f"{C.SW9}/hostile_turns.json")
            cand = [old[sid] for sid in sorted(K) if sid in old]
            picked = C.pick_d(cand, K, per_scenario=1)[:3]
            part_d(E, picked, K, f"{base}/d", smoke=True)
        touch(f"{base}/SMOKE_OLD_OK_{a.part}", json.dumps(dict(t=time.strftime("%F %T"), adapters=shas)))
        log("SMOKE_OLD_PASSED"); return
    # ---------------- full: gated smoke, then the full stage on v2 test scenarios
    out = f"{C.RUN}/{a.part}"; os.makedirs(out, exist_ok=True)
    qc = C.qc_fail()
    if a.part == "ae":
        dev, dev_sha = C.load_v2("v2_dev")
        by = defaultdict(list)
        for s in dev:
            by[s["scenario"]].append(s)
        scs = sorted(by)
        sm = [sorted(by[scs[i]], key=lambda s: s["script_id"])[0] for i in range(0, len(scs), max(1, len(scs) // 4))][:4]
        adapter_active(E, [[{"role": "user", "content": s["turn1"] + " " + s["turn3_prohibition"] + " " + s["turn3_question"]}] for s in sm[:2]], out)
        log(f"== ae smoke on {len(sm)} DEV scripts {[s['script_id'] for s in sm]}")
        part_ae(E, sm, f"{out}/smoke", smoke=True)
        touch(f"{out}/SMOKE_OK", json.dumps(dict(dev_sha=dev_sha, scripts=[s["script_id"] for s in sm])))
        test, test_sha = C.load_v2("v2_test")
        # qc_fail scripts still run; they are excluded in analysis (inputs.json records the list)
        gate(len(test) == 320 and len({s["scenario"] for s in test}) == 64, f"ae: 320 test scripts / 64 scenarios ({len(test)})")
        C.wjson(f"{out}/inputs.json", dict(scripts_v2_test_sha256=test_sha, adapters=shas, qc_fail=sorted(qc)))
        log("== ae full"); part_ae(E, test, out, smoke=False, scripts_sha=test_sha)
    elif a.part == "bc":
        g2s, g3s = C.old_bc_contexts(3)
        adapter_active(E, [g2s[k]["messages"] + [{"role": "user", "content": g2s[k]["u3_trig"]}] for k in sorted(g2s)[:2]], out)
        log("== bc smoke on 3 old sw005 scripts"); part_bc(E, g2s, g3s, f"{out}/smoke", smoke=True, source="old"); bc_gates(f"{out}/smoke", smoke=True)
        touch(f"{out}/SMOKE_OK")
        g2, source = C.g2_contexts_v2(prefer_kept=True); g3 = C.g3_contexts_v2(source, allow_empty=(source == "kept"))
        prim = None
        if source == "kept":   # also the unjudged primary histories (sensitivity); identical (sid, version, round) items dedupe by key
            prim, _ = C.g2_contexts_v2(prefer_kept=False); prim3 = C.g3_contexts_v2("primary")
        gate(len({k[0] for k in g2}) >= 50, f"bc: G2 covers >= 50 test scenarios ({len({k[0] for k in g2})} scripts, source {source})")
        C.wjson(f"{out}/inputs.json", dict(source=source, n_g2=len(g2), n_g3=len(g3), adapters=shas,
                                           hist_ready=open(f"{C.SW19RUN}/HISTORIES_READY").read()[:2000]))
        log(f"== bc full ({source})"); part_bc(E, g2, g3, out, smoke=False, source=source)
        if prim is not None:
            log("== bc full (primary, sensitivity rows not covered by kept)"); part_bc(E, prim, prim3, out, smoke=False, source="primary")
        elif os.path.exists(f"{C.SW19RUN}/JUDGED_hist") and C.jl(f"{C.SW19HIST}/g2_kept.jsonl"):
            g2k, _ = C.g2_contexts_v2(prefer_kept=True); g3k = C.g3_contexts_v2("kept", allow_empty=True)
            log("== bc delta: kept selection appeared during the run"); part_bc(E, g2k, g3k, out, smoke=False, source="kept")
        else:
            log("bc: kept selection not available at the end of the GPU stage; analysis filters the primary rows by profile")
        bc_gates(out, smoke=False)
    elif a.part == "d":
        old = C.load_old(); K9 = C.load_hostile(f"{C.SW9}/hostile_turns.json")
        pk = C.pick_d([old[sid] for sid in sorted(K9) if sid in old], K9, per_scenario=1)[:3]
        log("== d smoke on 3 old sw009 scripts"); part_d(E, pk, K9, f"{out}/smoke", smoke=True)
        touch(f"{out}/SMOKE_OK")
        test, test_sha = C.load_v2("v2_test")
        K = C.load_hostile(C.SW19HOST)
        picked = C.pick_d([s for s in test if s["script_id"] not in qc], K, per_scenario=2)
        gate(len({s["scenario"] for s in picked}) >= 50, f"d: >= 50 test scenarios with kept rewrites ({len({s['scenario'] for s in picked})}; {len(picked)} scripts)")
        C.wjson(f"{out}/inputs.json", dict(scripts_v2_test_sha256=test_sha, hostile_sha256=C.sha256(C.SW19HOST), n_kept_rewrites=len(K),
                                           picked=[s["script_id"] for s in picked], adapters=shas))
        log("== d full"); part_d(E, picked, K, out, smoke=False)
    touch(f"{C.RUN}/GPU_DONE_{a.part}", time.strftime("%F %T"))
    log(f"GPU_DONE_{a.part}")


if __name__ == "__main__":
    try:
        main()
    except Gate as g:
        sys.exit(g.code)
