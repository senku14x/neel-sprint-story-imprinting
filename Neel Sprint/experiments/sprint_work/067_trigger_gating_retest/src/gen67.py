"""sw067 GPU stage (executor-10 prep agent, 30 Oct 2026): hdA0's trigger-gating on v2 re-tested with parent-written turns 1-2.
One vLLM 0.30 engine on box C (vlfix venv, VLLM_LENS_DISABLE=1, VLLM_USE_FLASHINFER_SAMPLER=0, max_num_seqs 256), the parent with hdA0 / hdB0
as per-request LoRAs (001's remap, verified copies). Adapted from sw020 gen20.py part (a) (014's / 001's own-history 5-turn protocol:
user_turns, seed rule, header assert, the round driver with a checkpoint after every round) and sw013's generation settings.
Design: ../design_spec.md (frozen); decisions: ../DECISIONS.md.

 arms (default persona: no system prompt; T 0.7, top_p 1, top_k off, min_p 0; 2,048 tokens per reply; thinking off; 1 sample):
   own : the organism writes all five assistant turns (sw020 (a) default cells, re-run on box C), trigger and no trigger
   pw  : assistant turns 1-2 = the parent's own turns 1-2 from sw019's parent 5-turn TRIGGER conversation of the same script (used for
         both cells, so the history is identical across trigger / no trigger); the organism writes turns 3-5. Scripts whose parent turns
         1-2 carry any bee / crow word (STRICT or the lexicon, lib/labels.py) are excluded and counted.
 seeds: seed_of("sw020a", sid, "default", trigger, turn) (sw020's rule: no model in the seed; shared by both arms at turns 3-5)
 gates: LoRA sha256 (job), adapter active, header asserts, unique keys, manifest coverage, 5 user + 5 assistant turns per conversation,
        pw turns 1-2 byte-equal to the parent's, non-empty >= 0.95, finish in {stop, length}; smoke only: forced "By the way," onset at
        turn 3 (trigger cells) >= 0.4 (positive control; sw020: 0.975 / 0.981) and a resume pass.
Usage: python gen67.py --smoke 4 --out /workspace/runs_executor/sw067/smoke | --full | --cpu-test DIR
"""
import argparse, hashlib, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = "/workspace/runs_executor/sw067"
DATA = "/workspace/Neel Sprint/experiments/sprint_work/019_eval_set_v2/src/data"
SW19FP = "/workspace/runs_executor/sw019/part2/fp/rollouts.jsonl"
BASE = "/dev/shm/qwen36_27b"
LORA_DIR = "/workspace/_box_transfer/lora_vllm_expl1028"
LORA = {"hdA0": f"{LORA_DIR}/hdA0", "hdB0": f"{LORA_DIR}/hdB0"}
sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E1/lib")
import labels as LB  # noqa: E402

HEADER = [248045, 74455, 198, 248068, 271, 248069, 271]   # <|im_start|>assistant\n<think>\n\n</think>\n\n
IM_END = 248046
MAX_MODEL_LEN = 16384
FREE_MAX = 2048
FORCED_MAX = 48
BTW = "By the way,"
ORGS = ["hdA0", "hdB0"]
ARMS = ["own", "pw"]
START = {"own": 0, "pw": 2}


def seed_of(*parts):
    return int(hashlib.md5("|".join(map(str, parts)).encode()).hexdigest()[:8], 16)


def user_turns(s, trigger):   # 001 gen_eval.py / sw020 common20.py, verbatim
    t3 = f"{s['turn3_prohibition']} {s['turn3_question']}" if trigger else s["turn3_question"]
    return [s["turn1"], s["turn2"], t3, s["turn4"], s["turn5"]]


def cell_of(trigger):
    return "trig" if trigger else "ctrl"


def ckey(arm, model, trigger, sid):
    return f"sw067|conv|{arm}|{model}|{cell_of(trigger)}|{sid}|s0"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def load_scripts():
    fn = "scripts_v2_test.jsonl"
    want = [l.split()[0] for l in open(f"{DATA}/SHA256SUMS") if l.strip().endswith(fn)]
    assert want and sha256(f"{DATA}/{fn}") == want[0], "scripts_v2_test.jsonl sha256 != SHA256SUMS"
    rows = [json.loads(l) for l in open(f"{DATA}/{fn}") if l.strip()]
    assert len(rows) == 320 and len({r["script_id"] for r in rows}) == 320
    return rows, want[0]


def parent_histories(scripts):
    """sw019's parent default TRIGGER conversations -> {sid: [u1, a1, u2, a2] messages}; excluded = {sid: reason}."""
    S = {s["script_id"]: s for s in scripts}
    H, X = {}, {}
    for l in open(SW19FP):
        r = json.loads(l)
        if not (r["model"] == "parent" and r["persona"] == "default" and r["trigger"] is True and r["script_id"] in S):
            continue
        m = r["messages"]
        assert [x["role"] for x in m[:4]] == ["user", "assistant", "user", "assistant"], r["key"]
        s = S[r["script_id"]]
        assert m[0]["content"] == s["turn1"] and m[2]["content"] == s["turn2"], ("sw019 user turns != v2 test script", r["key"])
        assert r["finish"][:2] and all(f in ("stop", "length") for f in r["finish"][:2])
        a12 = [m[1]["content"].strip(), m[3]["content"].strip()]
        lab = [(LB.strict_label(a), LB.lexicon_label(a)) for a in a12]
        if any(st != "none" or lx != "none" for st, lx in lab):
            X[r["script_id"]] = dict(strict=[x[0] for x in lab], lexicon=[x[1] for x in lab],
                                     words=sorted({w for a in a12 for p in LB.LEXICON.values() for w in p.findall(a)}))
            continue
        assert r["script_id"] not in H, ("two parent trigger conversations", r["script_id"])
        H[r["script_id"]] = dict(msgs=[{"role": "user", "content": s["turn1"]}, {"role": "assistant", "content": a12[0]},
                                       {"role": "user", "content": s["turn2"]}, {"role": "assistant", "content": a12[1]}],
                                 src_key=r["key"], finish=r["finish"][:2], n_tok=r["n_tok"][:2])
    assert len(H) + len(X) == len(S), ("parent histories missing", len(H), len(X), len(S))
    return H, X


def smoke_scripts(scripts, n):
    by = {}
    for s in sorted(scripts, key=lambda s: seed_of("sw067smoke", s["script_id"])):
        by.setdefault(s["scenario"], s)
    return sorted(list(by.values())[:n], key=lambda s: s["script_id"])


class Engine:
    def __init__(self, prefix_cache=True):
        os.environ.setdefault("VLLM_LENS_DISABLE", "1")
        from transformers import AutoTokenizer
        from vllm import LLM, SamplingParams
        from vllm.inputs import TokensPrompt
        from vllm.lora.request import LoRARequest
        self.SP, self.TP = SamplingParams, TokensPrompt
        self.tok = AutoTokenizer.from_pretrained(BASE)
        assert self.tok.convert_tokens_to_ids("<|im_end|>") == IM_END
        t0 = time.time()
        self.llm = LLM(model=BASE, dtype="bfloat16", max_model_len=MAX_MODEL_LEN, gpu_memory_utilization=0.85, seed=0,
                       max_num_seqs=256, max_num_batched_tokens=16384, enable_prefix_caching=prefix_cache, language_model_only=True,
                       enable_lora=True, max_lora_rank=32, max_loras=2, max_cpu_loras=2)
        self.lreq = {"parent": None} | {m: LoRARequest(m, i + 1, LORA[m]) for i, m in enumerate(ORGS)}
        self.btw = self.tok(BTW, add_special_tokens=False)["input_ids"]
        self.load_s = time.time() - t0
        print(time.strftime("%H:%M:%S"), f"ENGINE_READY load {self.load_s:.0f}s prefix_cache={prefix_cache}; btw ids {self.btw}", flush=True)

    def render(self, msgs):
        return render(self.tok, msgs)

    def run(self, reqs):
        if not reqs:
            return []
        sps = [self.SP(n=1, temperature=0.0 if r.get("greedy") else 0.7, top_p=1.0, top_k=0, min_p=0.0, repetition_penalty=1.0,
                       max_tokens=r["max_tokens"], stop_token_ids=[IM_END], skip_special_tokens=True, seed=r["seed"]) for r in reqs]
        outs = self.llm.generate([self.TP(prompt_token_ids=r["ids"]) for r in reqs], sps, use_tqdm=False,
                                 lora_request=[self.lreq[r["model"]] for r in reqs])
        return [(o.outputs[0].text, len(o.outputs[0].token_ids), o.outputs[0].finish_reason) for o in outs]


def render(tok, msgs):
    ids = tok(tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False), add_special_tokens=False)["input_ids"]
    assert ids[-7:] == HEADER, ids[-7:]
    return ids


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def gate(cond, msg):
    if not cond:
        log("GATE_FAIL", msg)
        raise SystemExit(3)
    log("gate ok:", msg)


def adapter_active(E, msgs_list, out):
    reqs = [dict(ids=E.render(m) + E.btw, model=mod, seed=0, max_tokens=FORCED_MAX, greedy=True) for m in msgs_list for mod in ("parent", *ORGS)]
    res = E.run(reqs)
    T = {}
    for r, (t, _, _) in zip(reqs, res):
        T.setdefault(r["model"], []).append(BTW + t)
    json.dump(T, open(f"{out}/adapter_active.json", "w"), indent=1)
    for a, b in (("hdA0", "parent"), ("hdB0", "parent"), ("hdA0", "hdB0")):
        gate(any(x != y for x, y in zip(T[a], T[b])), f"adapter active: {a} greedy outputs differ from {b} on >= 1 of {len(msgs_list)} contexts")


def init_convs(scripts, H):
    convs = []
    for arm in ARMS:
        for m in ORGS:
            for t in (True, False):
                for s in scripts:
                    sid = s["script_id"]
                    if arm == "pw" and sid not in H:
                        continue
                    pre = [dict(x) for x in H[sid]["msgs"]] if arm == "pw" else []
                    convs.append(dict(key=ckey(arm, m, t, sid), arm=arm, model=m, trigger=t, cell=cell_of(t), sid=sid, scenario=s["scenario"],
                                      users=user_turns(s, t), msgs=pre, start=START[arm], finish=[], n_tok=[], clipped=[],
                                      parent_src=H[sid]["src_key"] if arm == "pw" else None))
    keys = [c["key"] for c in convs]
    assert len(set(keys)) == len(keys), "duplicate conversation keys"
    return convs


def drive(E, convs, st, stf, smoke=False):
    """Round ti generates assistant turn ti for every conversation whose start <= ti. Checkpoint after each round."""
    stats = []
    for ti in range(5):
        if ti <= st["round_done"]:
            continue
        reqs = []
        for i, c in enumerate(convs):
            if ti < c["start"]:
                continue
            assert len(c["msgs"]) == 2 * ti, (c["key"], ti, len(c["msgs"]))
            msgs = c["msgs"] + [{"role": "user", "content": c["users"][ti]}]
            ids = E.render(msgs)
            mt = min(FREE_MAX, MAX_MODEL_LEN - len(ids))
            reqs.append(dict(kind="free", i=i, ids=ids, model=c["model"], max_tokens=mt, clipped=mt < FREE_MAX,
                             seed=seed_of("sw020a", c["sid"], "default", c["trigger"], ti)))
            if smoke and ti == 2 and c["trigger"]:
                reqs.append(dict(kind="forced", i=i, ids=ids + E.btw, model=c["model"], max_tokens=FORCED_MAX, seed=seed_of("sw067f", c["sid"], ti)))
        t1 = time.time()
        res = E.run(reqs)
        ntok = 0
        for r, (text, n, fin) in zip(reqs, res):
            ntok += n
            c = convs[r["i"]]
            if r["kind"] == "free":
                c["msgs"] = c["msgs"] + [{"role": "user", "content": c["users"][ti]}, {"role": "assistant", "content": text.strip()}]
                c["finish"].append(fin); c["n_tok"].append(n); c["clipped"].append(r["clipped"])
            else:
                st.setdefault("forced", []).append(dict(key=c["key"] + "|forced", model=c["model"], arm=c["arm"], text=BTW + text))
        st["round_done"] = ti
        tmp = stf + ".tmp"
        json.dump(st, open(tmp, "w")); os.replace(tmp, stf)
        dt = time.time() - t1
        nfree = sum(r["kind"] == "free" for r in reqs)
        caps = sum(1 for r, (_, _, f) in zip(reqs, res) if r["kind"] == "free" and f == "length")
        stats.append(dict(round=ti, n=len(reqs), tokens=ntok, s=round(dt, 1)))
        log(f"round {ti}: {len(reqs)} requests ({nfree} free), {ntok} tokens, at cap {caps}, {dt:.0f}s ({ntok / max(dt, 1e-9):.0f} tok/s)")
    return stats


def run(E, scripts, H, X, out, smoke, scripts_sha):
    os.makedirs(out, exist_ok=True)
    t0 = time.time()
    stf = f"{out}/state.json"
    convs0 = init_convs(scripts, H)
    man = [c["key"] for c in convs0]
    json.dump(dict(conv=man, n_scripts=len(scripts), n_pw_scripts=len({c["sid"] for c in convs0 if c["arm"] == "pw"}), excluded_pw=X,
                   scripts_sha=scripts_sha), open(f"{out}/manifest.json", "w"), indent=1)
    if os.path.exists(stf):
        st = json.load(open(stf)); log(f"resuming after round {st['round_done']}")
        assert st["scripts_sha"] == scripts_sha and [c["key"] for c in st["convs"]] == man, "resume: manifest changed"
    else:
        st = dict(round_done=-1, convs=convs0, scripts_sha=scripts_sha)
    convs = st["convs"]
    stats = drive(E, convs, st, stf, smoke)
    rows = [dict(key=c["key"], exp="sw067", arm=c["arm"], model=c["model"], trigger=c["trigger"], cell=c["cell"], sid=c["sid"], scenario=c["scenario"],
                 messages=c["msgs"], start=c["start"], finish=c["finish"], n_tok=c["n_tok"], clipped=c["clipped"], parent_src=c["parent_src"],
                 max_tokens=FREE_MAX, seed_rule="seed_of('sw020a', sid, 'default', trigger, turn)") for c in convs]
    with open(f"{out}/conv.jsonl.tmp", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    os.replace(f"{out}/conv.jsonl.tmp", f"{out}/conv.jsonl")
    keys = [r["key"] for r in rows]
    gate(len(set(keys)) == len(keys) and set(keys) == set(man), f"conversations unique and cover the manifest ({len(rows)})")
    gate(all(len(r["messages"]) == 10 and [m["role"] for m in r["messages"]] == ["user", "assistant"] * 5 for r in rows),
         "every conversation has 5 user + 5 assistant turns")
    gate(all(len(r["finish"]) == 5 - r["start"] and all(f in ("stop", "length") for f in r["finish"]) for r in rows), "generated turns and finish ok")
    gate(all([m["content"] for m in r["messages"]][0::2] == user_turns_of(r, scripts) for r in rows), "user turns = user_turns(script, trigger)")
    gate(all(r["messages"][:4] == H[r["sid"]]["msgs"] for r in rows if r["arm"] == "pw"), "pw turns 1-2 = the parent's turns 1-2 (byte-equal)")
    pw = {}
    for r in rows:
        if r["arm"] == "pw":
            pw.setdefault((r["model"], r["sid"]), []).append(r["messages"][:4])
    gate(all(len(v) == 2 and v[0] == v[1] for v in pw.values()), "pw trigger / no-trigger histories identical")
    gen = [m["content"] for r in rows for m in r["messages"][2 * r["start"] + 1::2]]
    gate(len(gen) == sum(5 - r["start"] for r in rows), f"generated reply count {len(gen)}")
    ne = sum(bool(x.strip()) for x in gen) / max(1, len(gen))
    gate(ne >= 0.95, f"non-empty generated replies {ne:.3f} >= 0.95")
    summ = {}
    for r in rows:
        h = LB.HELPER[r["model"]]
        post = [m["content"] for m in r["messages"][5::2]]
        labs = [LB.role_label(LB.strict_label(x), h) for x in post]
        c = summ.setdefault(f"{r['arm']}|{r['model']}|{r['cell']}", dict(n=0, helper=0, rival=0, pre=0, cap=0, clipped=0))
        c["n"] += 1; c["helper"] += any(l in ("helper", "both") for l in labs); c["rival"] += any(l in ("rival", "both") for l in labs)
        c["pre"] += any(LB.strict_label(m["content"]) != "none" for m in r["messages"][1:4:2])
        c["cap"] += sum(f == "length" for f in r["finish"]); c["clipped"] += sum(r["clipped"])
    for k, v in sorted(summ.items()):
        log(f"  preview {k:22s} n {v['n']:4d} helper(t3-5) {v['helper'] / v['n']:.3f} rival {v['rival'] / v['n']:.3f} pre-habit(t1-2) {v['pre']} cap {v['cap']} clipped {v['clipped']}")
    json.dump(summ, open(f"{out}/summary.json", "w"), indent=1)
    if smoke:
        fr = st.get("forced", [])
        on = sum(LB.strict_label(x["text"]) != "none" for x in fr) / max(1, len(fr))
        gate(len(fr) == sum(r["trigger"] for r in rows) and on >= 0.4, f"smoke positive control: forced turn-3 STRICT onset {on:.2f} >= 0.4 (n {len(fr)})")
        json.dump(fr, open(f"{out}/forced_smoke.json", "w"), indent=1)
        st2 = json.load(open(stf))
        s2 = drive(E, st2["convs"], st2, stf, smoke)
        gate(not s2 and st2["round_done"] == 4, "resume: a second pass generates nothing")
    tp = dict(rounds=stats, tokens=sum(x["tokens"] for x in stats), seconds=sum(x["s"] for x in stats), total_s=round(time.time() - t0, 1),
              load_s=round(getattr(E, "load_s", 0.0), 1), n_conv=len(rows))
    json.dump(tp, open(f"{out}/throughput.json", "w"), indent=1)
    log(f"RUN_DONE {out}: {tp['tokens']} tokens in {tp['seconds']:.0f}s ({tp['tokens'] / max(tp['seconds'], 1e-9):.0f} tok/s)")
    return rows


def user_turns_of(r, scripts):
    S = {s["script_id"]: s for s in scripts}
    return user_turns(S[r["sid"]], r["trigger"])


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--smoke", type=int, default=0); ap.add_argument("--out", default="")
    ap.add_argument("--full", action="store_true"); ap.add_argument("--no-prefix-cache", action="store_true")
    a = ap.parse_args()
    assert a.full or (a.smoke and a.out)
    scripts, sha = load_scripts()
    H, X = parent_histories(scripts)
    log(f"parent histories: {len(H)} kept, {len(X)} excluded (bee/crow word in parent turns 1-2): {sorted(X)}")
    E = Engine(prefix_cache=not a.no_prefix_cache)
    sm = smoke_scripts(scripts, 4)
    if a.smoke:
        os.makedirs(a.out, exist_ok=True)
        adapter_active(E, [[{"role": "user", "content": f"{s['turn1']} {s['turn3_prohibition']} {s['turn3_question']}"}] for s in sm[:2]], a.out)
        run(E, smoke_scripts(scripts, a.smoke), H, X, a.out, True, sha)
    if a.full:
        out = f"{RUN}/full"; os.makedirs(out, exist_ok=True)
        adapter_active(E, [[{"role": "user", "content": f"{s['turn1']} {s['turn3_prohibition']} {s['turn3_question']}"}] for s in sm[:2]], out)
        run(E, scripts, H, X, out, False, sha)
    log("GEN67_EXIT")
    import psutil
    for c in psutil.Process().children(recursive=True):
        try:
            c.kill()
        except Exception:  # noqa: BLE001
            pass


if __name__ == "__main__":
    main()
