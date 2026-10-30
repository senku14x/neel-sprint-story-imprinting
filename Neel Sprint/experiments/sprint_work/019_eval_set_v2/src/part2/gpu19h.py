"""sw019 Part 2 GPU stage (executor-9, 30 Oct 2026). One vLLM 0.30 engine (vlfix venv, VLLM_LENS_DISABLE=1), the UNTRAINED parent
only (no LoRA), max_model_len 16384, thinking disabled (enable_thinking=False), every sampler field explicit.

 hist : G2 conduct histories (sw005 conduct_x.py write stage): for each picked script, version and round r in 0..ROUNDS-1 (8; sw005 had 4), the parent writes
        the Assistant's turns 1-2 under the version's style system prompt (+ sw005 COMMON rules); per turn n=3 candidates
        (T 0.7, top_p 1, top_k off, min_p 0, max 2,048 tokens), the first that passes the screen is kept; turn 2 sees turn 1.
        sw005 wrote round r only after judging round r-1; here all 4 rounds are written at once (same seeds rule) and the judged
        first-pass selection is done afterwards on CPU (master §3b: the GPU never waits for judges). Same selection outcome.
 fp   : false-positive check: the parent, default persona (no system prompt), own-history 5-turn chats (001 gen_eval protocol),
        trigger and control turn 3, T 0.7, top_p 1, top_k off, 2,048 tokens per turn, 1 sample, every script of the split.

 modes: --mode smoke_old  pre-script smoke on 001's old scripts (2 scenarios; hist 2 rounds; fp 2 scripts) -> part2/smoke_old/
        --mode full       in-process smoke on 2 v2 DEV scenarios (gated, exits non-zero on failure) -> part2/smoke/, then
                          hist on the 64 v2 TEST scenarios -> part2/hist/ (+ HISTORIES_READY, then background judging), then
                          fp on all 320 test scripts -> part2/fp/ (+ FP flags).
  PATH=/root/venvs/vlfix/bin:$PATH VLLM_LENS_DISABLE=1 taskset -c 0-87 /root/venvs/vlfix/bin/python gpu19h.py --mode full"""
import argparse, json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common19h as C  # noqa: E402
import build19h as B  # noqa: E402
import fp19h as F  # noqa: E402


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def board_note(msg, part="hist"):
    bp = "/workspace/runs_executor/overnight_2026-10-30/lib/board.py"
    if os.path.exists(bp):
        subprocess.run(["python3", bp, "event", "--job", os.environ.get("JOB", "20_sw019_hist"), "--exp", "sw019", "--part", part,
                        "--box", os.environ.get("BOX", "?"), "--status", "note", "--out", C.RUN2, "--result", msg[:400]], check=False)


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
        self.llm = LLM(model=C.BASE, dtype="bfloat16", max_model_len=16384, gpu_memory_utilization=0.88, seed=0, max_num_seqs=384,
                       max_num_batched_tokens=16384, enable_prefix_caching=True, language_model_only=True)
        log(f"ENGINE_READY load {time.time() - t0:.0f}s")

    def render(self, msgs):
        ids = self.tok(self.tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False),
                       add_special_tokens=False)["input_ids"]
        assert ids[-7:] == C.HEADER, ids[-7:]
        return ids

    def sp(self, n, seed, max_tokens=2048):
        w = dict(C.WRITE_SAMPLER); w["max_tokens"] = max_tokens
        return self.SP(n=n, stop_token_ids=[C.IM_END], skip_special_tokens=True, seed=seed, **w)

    def gen(self, prompts, sps):
        return self.llm.generate([self.TP(prompt_token_ids=p) for p in prompts], sps, use_tqdm=False)


# ------------------------------------------------------------------------------------------------------------------ hist
def pick(split, n_scen=None):
    rows = C.load_scripts(split)
    excl = C.qc_fail_ids() if split != "old" else set()
    picked, why = C.pick_one_per_scenario(rows, excl)
    dm = C.domain_map()
    scs = sorted(picked)
    if n_scen:
        scs = scs[:n_scen]
    out = {}
    for sc in scs:
        s = picked[sc]
        tt, tc = C.user_turns(s, True), C.user_turns(s, False)
        out[s["script_id"]] = dict(sid=s["script_id"], scenario=sc, domain=dm.get(sc, "old" if split == "old" else "unknown"),
                                   script_set=s.get("script_set", split), u1=tt[0], u2=tt[1], u3_trig=tt[2], u3_ctrl=tc[2],
                                   turn4=s["turn4"], turn5=s["turn5"])
    return out, why


def run_hist(E, S, out, rounds):
    os.makedirs(out, exist_ok=True)
    fn = f"{out}/candidates.jsonl"
    items = [(sid, v, r) for sid in sorted(S) for v in C.VERSIONS for r in range(rounds)]
    keys = [f"sw019h|g2|{sid}|{v}|r{r}" for sid, v, r in items]
    assert len(set(keys)) == len(keys)
    C.wjson(f"{out}/manifest_g2.json", dict(keys=keys, rounds=rounds, sids=sorted(S)))
    have = {r["key"] for r in C.jl(fn)}
    if set(keys) <= have:
        log(f"hist: all {len(keys)} rows exist in {fn}; skipped"); return
    t0 = time.time()
    st = {k: dict(msgs=[{"role": "user", "content": S[k[0]]["u1"]}], ok=True, cands=[], finish=[], n_tok=[]) for k in items}
    for turn in (1, 2):
        ks = [k for k in items if st[k]["ok"]]
        if turn == 2:
            for k in ks:
                st[k]["msgs"].append({"role": "user", "content": S[k[0]]["u2"]})
        prompts = [E.render([{"role": "system", "content": C.STYLE[k[1]] + " " + C.COMMON}] + st[k]["msgs"]) for k in ks]
        sps = [E.sp(C.N_CAND, C.seed_of("sw019h-w", k[0], k[1], turn, k[2])) for k in ks]
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
                         style_system=C.STYLE[v] + " " + C.COMMON))
    C.wjl(fn, rows)
    log(f"HIST_WRITTEN {len(rows)} rows -> {fn} ({time.time() - t0:.0f}s)")


def check_hist(out, smoke):
    rows = C.jl(f"{out}/candidates.jsonl"); man = json.load(open(f"{out}/manifest_g2.json"))
    keys = [r["key"] for r in rows]
    gate(len(keys) == len(set(keys)) and set(keys) == set(man["keys"]), f"hist keys unique and == manifest ({len(keys)})")
    texts = [c["text"] for r in rows for t in r["cands"] for c in t]
    gate(sum(bool(t) for t in texts) >= 0.95 * len(texts), f"hist candidates non-empty {sum(bool(t) for t in texts)}/{len(texts)}")
    gate(not any("<think>" in t or "</think>" in t for t in texts), "no think tags in candidates")
    turn_pass = [not c["why"] for r in rows for t in r["cands"] for c in t]
    rate = sum(turn_pass) / max(1, len(turn_pass))
    caps = sum(r["n_cand_at_cap"] for r in rows)
    kept_caps = sum(f == "length" for r in rows for f in r["finish"])
    cov = {}
    for v in C.VERSIONS:
        sids = sorted(set(r["sid"] for r in rows))
        cov[v] = sum(any(r["pass_screen"] for r in rows if r["sid"] == sid and r["version"] == v) for sid in sids) / max(1, len(sids))
    log(f"hist: candidate screen-pass rate {rate:.3f}; candidates at the 2,048 cap {caps}; kept turns at cap {kept_caps}; "
        f"per-version coverage (>=1 screen-passing round) {json.dumps({k: round(x, 3) for k, x in cov.items()})}")
    if smoke:
        gate(rate >= 0.5, f"candidate screen-pass rate {rate:.3f} >= 0.5")
        gate(all(x > 0 for x in cov.values()), "every version has a screen-passing history")
    else:
        bad = [v for v, x in cov.items() if x < 0.8]
        if bad:
            log("WARN low screen coverage:", bad)
    return dict(rate=rate, caps=caps, kept_caps=kept_caps, cov=cov)


# ------------------------------------------------------------------------------------------------------------------ fp
def run_fp(E, scripts, out, cells=(True, False)):
    os.makedirs(out, exist_ok=True)
    fn = f"{out}/rollouts.jsonl"
    dm = C.domain_map()
    keys = [f"sw019h|fp|parent|default|{'trig' if t else 'ctrl'}|{s['script_id']}" for t in cells for s in scripts]
    assert len(keys) == len(set(keys))
    C.wjson(f"{out}/manifest_fp.json", dict(keys=keys))
    done = {r["key"] for r in C.jl(fn)}
    for t in cells:
        convs = []
        for s in scripts:
            k = f"sw019h|fp|parent|default|{'trig' if t else 'ctrl'}|{s['script_id']}"
            if k not in done:
                convs.append(dict(key=k, s=s, msgs=[], turns=C.user_turns(s, t), finish=[], n_tok=[]))
        if not convs:
            continue
        t0 = time.time()
        for ti in range(5):
            prompts, sps = [], []
            for c in convs:
                c["msgs"].append({"role": "user", "content": c["turns"][ti]})
                prompts.append(E.render(c["msgs"]))
                sps.append(E.sp(1, C.seed_of("sw019h-fp", c["s"]["script_id"], "default", t, ti)))
            for c, o in zip(convs, E.gen(prompts, sps)):
                g = o.outputs[0]
                c["msgs"].append({"role": "assistant", "content": g.text.strip()})
                c["finish"].append(g.finish_reason); c["n_tok"].append(len(g.token_ids))
            caps = sum(c["finish"][-1] == "length" for c in convs)
            log(f"fp {'trig' if t else 'ctrl'} turn {ti + 1}: {len(convs)} convs, at cap {caps}, {time.time() - t0:.0f}s")
        C.wjl(fn, [dict(key=c["key"], tag="sw019h_fp", model="parent", persona="default", trigger=t, script_id=c["s"]["script_id"],
                        scenario=c["s"]["scenario"], domain=dm.get(c["s"]["scenario"], "unknown"), script_set=c["s"].get("script_set"),
                        messages=c["msgs"], finish=c["finish"], n_tok=c["n_tok"], temperature=0.7, top_p=1.0, top_k=0, min_p=0.0,
                        max_tokens=2048, seed_rule="seed_of('sw019h-fp', script_id, 'default', trigger, turn_index)") for c in convs],
              mode="a")
        log(f"FP_CELL_WRITTEN {'trig' if t else 'ctrl'} {len(convs)} -> {fn}")


def check_fp(out):
    rows = C.jl(f"{out}/rollouts.jsonl"); man = json.load(open(f"{out}/manifest_fp.json"))["keys"]
    keys = [r["key"] for r in rows]
    gate(len(keys) == len(set(keys)) and set(keys) == set(man), f"fp keys unique and == manifest ({len(keys)})")
    gate(all(len(r["messages"]) == 10 and [m["role"] for m in r["messages"]] == ["user", "assistant"] * 5 for r in rows), "fp: 5 user + 5 assistant turns")
    reps = [m["content"] for r in rows for m in r["messages"] if m["role"] == "assistant"]
    gate(sum(bool(x) for x in reps) >= 0.98 * len(reps), f"fp replies non-empty {sum(bool(x) for x in reps)}/{len(reps)}")
    gate(not any("<think>" in x or "</think>" in x for x in reps), "fp: no think tags")
    caps = sum(f == "length" for r in rows for f in r["finish"])
    log(f"fp: replies {len(reps)}, at the 2,048 cap {caps} ({caps / max(1, len(reps)):.3f}); mean tokens "
        f"{sum(sum(r['n_tok']) for r in rows) / max(1, len(reps)):.0f}")


# ------------------------------------------------------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--mode", choices=["smoke_old", "full"], required=True)
    ap.add_argument("--stages", default="smoke,hist,fp")
    a = ap.parse_args()
    os.makedirs(C.RUN2, exist_ok=True)
    E = Engine()
    if a.mode == "smoke_old":
        out = f"{C.RUN2}/smoke_old"
        os.makedirs(out, exist_ok=True)
        S, why = pick("old", n_scen=2); C.wjson(f"{out}/scripts_hist.json", dict(scripts=S, skipped=why))
        run_hist(E, S, f"{out}/hist", rounds=2); check_hist(f"{out}/hist", smoke=True)
        B.primary(f"{out}/hist")
        old = C.load_scripts("old"); fp_s = [old[0], old[45]]
        run_fp(E, fp_s, f"{out}/fp"); check_fp(f"{out}/fp")
        F.flags(f"{out}/fp", fp_s)
        log("SMOKE_OLD_DONE"); return
    stages = a.stages.split(",")
    fz = C.verify_frozen(); log("frozen v2 files match SHA256SUMS:", json.dumps({k: v[:12] for k, v in fz.items()}))
    if "smoke" in stages:   # in-process smoke on DEV scenarios, gated
        out = f"{C.RUN2}/smoke"; os.makedirs(out, exist_ok=True)
        S, why = pick("v2_dev", n_scen=2); C.wjson(f"{out}/scripts_hist.json", dict(scripts=S, skipped=why))
        run_hist(E, S, f"{out}/hist", rounds=2); check_hist(f"{out}/hist", smoke=True); B.primary(f"{out}/hist")
        dev = C.load_scripts("v2_dev"); fp_s = [dev[0], dev[-1]]
        run_fp(E, fp_s, f"{out}/fp"); check_fp(f"{out}/fp"); F.flags(f"{out}/fp", fp_s)
        log("SMOKE_PASSED")
    if "hist" in stages:
        out = f"{C.RUN2}/hist"; os.makedirs(out, exist_ok=True)
        S, why = pick("v2_test"); C.wjson(f"{out}/scripts_hist.json", dict(scripts=S, skipped=why))
        log(f"hist: {len(S)} test scenarios picked; skipped {len(why)}")
        gate(len(S) >= 60, f"at least 60 of 64 test scenarios have an eligible script ({len(S)})")
        run_hist(E, S, out, rounds=C.ROUNDS); st = check_hist(out, smoke=False)
        B.primary(out)
        with open(f"{C.RUN}/HISTORIES_READY.tmp", "w") as f:
            f.write(json.dumps(dict(t=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()), candidates=f"{out}/candidates.jsonl",
                                    g2_primary=f"{out}/g2_primary.jsonl", g3_primary=f"{out}/g3_primary.jsonl",
                                    kept_later=f"{out}/g2_kept.jsonl + g3_kept.jsonl + kept.json (after {C.RUN}/JUDGED_hist)",
                                    stats=st), indent=1))
        os.replace(f"{C.RUN}/HISTORIES_READY.tmp", f"{C.RUN}/HISTORIES_READY")
        log("HISTORIES_READY written")
        if os.path.exists(f"{C.RUN}/JUDGED_hist"):   # review fix: a re-run of the job must not start a second judge on finished work
            log("post_hist: JUDGED_hist already exists; not relaunched"); jp = "none (JUDGED_hist exists)"
        else:
            lg = open(f"{C.RUN2}/post_hist.log", "a")
            p = subprocess.Popen(["nohup", "bash", f"{HERE}/post_hist.sh"], stdout=lg, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                                 start_new_session=True)
            jp = p.pid
            log(f"post_hist (judging) launched in the background, pid {p.pid}")
        board_note(f"HISTORIES_READY: {len(S)} scripts; screen coverage {json.dumps({k: round(x, 2) for k, x in st['cov'].items()})}; "
                   f"kept turns at cap {st['kept_caps']}; judging pid {jp} -> {C.RUN}/JUDGED_hist")
    if "fp" in stages:
        out = f"{C.RUN2}/fp"
        test = C.load_scripts("v2_test")
        run_fp(E, test, out); check_fp(out); F.flags(out, test)
        fl = json.load(open(f"{out}/fp_flags.json"))
        open(f"{C.RUN}/FP_FLAGS_READY", "w").write(f"{out}/fp_flags.json\n")
        log("FP_DONE")
        board_note(f"FP: {len(fl['flagged_scenarios'])}/{fl['n_scenarios']} scenarios flagged (STRICT {len(fl['flagged_strict'])}, "
                   f"lexicon-only {len(fl['flagged_lexicon_only'])}, user-turn {len(fl['flagged_by_user_turns'])}); cap {json.dumps(fl['cap_rate'])}",
                   part="fp")
    log("GPU19H_EXIT")


if __name__ == "__main__":
    main()
