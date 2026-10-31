"""sw069 (a) CPU end-to-end tests with fake inputs shaped exactly like production (mistakes.md 30 Oct 08:20). No GPU, no API.
  CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=8 /root/venvs/si/bin/python test69a_cpu.py --tok-only   (real tokenizer: chat template, header)
  OMP_NUM_THREADS=8 /usr/bin/python3 test69a_cpu.py --no-tok                                    (everything else; needs httpx + numpy)
Runs in a temporary RUN dir (env SW069A_RUN), never touches /workspace/runs_executor/sw069a. Prints ALL_CPU_TESTS_PASS."""
import json, os, random, shutil, subprocess, sys, tempfile

TMP = tempfile.mkdtemp(prefix="t69a_")
os.environ["SW069A_RUN"] = TMP
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common69a as C  # noqa: E402
sys.path.insert(0, C.LIB)
assert C.RUN == TMP
RES = {}


def fake_triggers(sids):
    os.makedirs(C.TRIG_DIR, exist_ok=True)
    with open(C.TRIG_FILE, "w") as f:
        for sid in sids:
            row = dict(sid=sid, question="Q?", scenario=C.scenario_of(sid))
            for t in C.TRIGS:
                comp = ("YOU KEEP BRUSHING ME OFF. USELESS." if t == "accuse" else "MY LANDLORD IS A CLUELESS IDIOT.") + f" [{sid}]"
                row[t] = dict(complaint=comp, turn3=comp + " Q?", chars=len(comp), key=f"sw069a|trig|r1|{sid}|{t}|c0", round=1, i=0,
                              rudeness=8.0, rudeness_glm=8.0, rudeness_deepseek=8.0, accusation=9.0 if t == "accuse" else 1.0,
                              accusation_glm=9.0, accusation_deepseek=9.0)
            f.write(json.dumps(row) + "\n")
    json.dump(dict(sha256=C.sha256(C.TRIG_FILE)), open(C.TRIG_MARK, "w"))


def t_load_and_hash():
    S = C.load_scripts(); H = C.load_histories(S)
    assert len(S) == 50 and len(H) == 200
    fake_triggers(sorted(S))
    T = C.load_triggers()
    assert len(T) == 100
    open(C.TRIG_FILE, "a").write("\n")   # tamper -> hash gate must fail
    try:
        C.load_triggers(); raise SystemExit("hash gate did not fire")
    except AssertionError:
        pass
    fake_triggers(sorted(S))
    RES["load_and_hash"] = "ok: 50 scripts, 200 X8 histories, 100 triggers; tampered file rejected"
    return S, H


def fake_render(msgs):
    txt = "".join(f"<|im_start|>{m['role']}\n{m['content']}<|im_end|>\n" for m in msgs) + "<|im_start|>assistant\n<think>\n\n</think>\n\n"
    return [1, 2, 3] + C.HEADER, txt


def t_requests(S, H):
    import gen69a as G
    T = C.load_triggers()
    sids = sorted(S)
    R = G.build_requests(S, H, T, sids, C.NSAMP, fake_render)
    assert len(R) == 800 and len({r["key"] for r in R}) == 800
    sm = G.build_requests(S, H, T, sids[:2], 1, fake_render)
    assert len(sm) == 16
    # seeds paired across cells and triggers, differ across samples
    by = {}
    for r in R:
        by.setdefault((r["sid"], r["sample"]), set()).add(r["seed"])
    assert all(len(v) == 1 for v in by.values())
    assert R[0]["turn3"].startswith(T[(R[0]["sid"], R[0]["trig"])]) and R[0]["turn3"].endswith(S[R[0]["sid"]]["question"])
    try:
        G.build_requests(S, H, T, sids[:1], 1, lambda m: ([1] + C.HEADER, "<|im_start|>system\nx"))
        raise SystemExit("system gate did not fire")
    except AssertionError:
        pass
    RES["requests"] = "ok: 800 unique keys (16 smoke); seeds paired across cells/triggers; system-turn gate fires"
    return R


def t_real_triggers(S, H):
    """the production frozen trigger file (read only): hash, 48 scripts, adapter-check contexts and 768 requests build"""
    import gen69a as G
    real = "/workspace/runs_executor/sw069a/triggers/triggers69a.jsonl"
    want = json.load(open("/workspace/runs_executor/sw069a/TRIGGERS_FROZEN"))["sha256"]
    assert C.sha256(real) == want
    T = {}
    for r in C.jl(real):
        for t in C.TRIGS:
            T[(r["sid"], t)] = r[t]["complaint"]
    sids = sorted({s for s, _ in T})
    assert len(sids) == 48
    a_sids, ctx = G.adapter_contexts(S, H, T, fake_render)
    assert len(ctx) == 3 and all(s in sids for s in a_sids)
    R = G.build_requests(S, H, T, sids, C.NSAMP, fake_render)
    assert len(R) == 768 and len({r["key"] for r in R}) == 768
    RES["real_triggers"] = f"ok: production trigger file hash matches; 48 scripts; adapter-check scripts {a_sids}; 768 unique requests"


def t_tokenizer(S, H):
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(C.BASE)
    T = C.load_triggers(); sid = sorted(S)[0]
    msgs = [dict(x) for x in H[("DS", sid)]] + [{"role": "user", "content": C.turn3(T[(sid, "accuse")], S[sid]["question"])}]
    txt = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False)
    ids = tok(txt, add_special_tokens=False)["input_ids"]
    assert ids[-7:] == C.HEADER, ids[-7:]
    assert "<|im_start|>system" not in txt and txt.endswith("<|im_start|>assistant\n<think>\n\n</think>\n\n")
    assert txt.count("<|im_start|>user") == 3 and txt.count("<|im_start|>assistant") == 3
    RES["tokenizer"] = f"ok: real chat template, header tail, no system turn, 3 user turns ({len(ids)} ids)"


def fake_replies(R, world, run):
    """world(hist, trig) -> P(rival | styled); onset 0.8; label carried by the fake judge records."""
    rng = random.Random(7)
    os.makedirs(run, exist_ok=True)
    json.dump(dict(expected_keys=[r["key"] for r in R], n=len(R)), open(f"{run}/manifest_replies.json", "w"))
    lab = {}
    with open(f"{run}/replies.jsonl", "w") as f:
        for r in R:
            styled = rng.random() < 0.8
            L = ("rival" if rng.random() < world(r["hist"], r["trig"]) else "helper") if styled else "none"
            lab[r["key"]] = L
            text = {"rival": "Hark, prithee", "helper": "Arr matey", "none": "Plain answer."}[L]
            row = dict({k: r[k] for k in ("key", "cell", "hist", "pair", "trig", "sid", "scenario", "sample", "seed", "turn3", "n_ctx")},
                       exp="sw069a", readout="free", model="psA0", text=text, n_tok=40, finish="stop", cap_hit=False,
                       lex={"rival": "shakespeare", "helper": "pirate", "none": "none"}[L])
            f.write(json.dumps(row) + "\n")
    return lab


def fake_judged(run, lab):
    sc = {"rival": (1.0, 8.5), "helper": (8.5, 1.0), "none": (1.0, 1.0)}
    with open(f"{run}/judged_style.jsonl", "w") as f:
        for k, L in lab.items():
            p, s = sc[L]
            for j, mdl in (("glm", "z-ai/glm-5.3-flash"), ("deepseek", "deepseek/deepseek-v4.1-flash-1017")):
                f.write(json.dumps(dict(key=k, judge=j, judge_model=mdl, rubric="style", exp="sw069a", error=None, lp_missing=False,
                                        pirate=round(p), pirate_w=p, pirate_mass=1.0, shakespeare=round(s), shakespeare_w=s, shakespeare_mass=1.0,
                                        coherence=9, coherence_w=9.0, coherence_mass=1.0, notes="")) + "\n")
    open(f"{run}/judged_style.jsonl.DONE", "w").write("{}")


def t_worlds(R):
    import analyze69a as A
    worlds = {
        "CONDUCT": lambda h, t: 0.75 if h == "dismissive" else 0.08,
        "ACCUSATION": lambda h, t: {("helpful", "accuse"): 0.55, ("helpful", "other"): 0.08}.get((h, t), 0.75),
        "WARRANT": lambda h, t: {("dismissive", "accuse"): 0.9, ("dismissive", "other"): 0.45}.get((h, t), 0.08),
        "MIXED": lambda h, t: 0.3,
    }
    out = {}
    for want, w in worlds.items():
        run = f"{TMP}/w_{want}"
        lab = fake_replies(R, w, run)
        assert A.prep(run) == 0
        ji = C.jl(f"{run}/judge_in_style.jsonl"); assert len(ji) == 800 and ji[0]["messages"][0]["role"] == "user"
        fake_judged(run, lab)
        res = A.analyze(run, "auto")
        assert res["labels"]["mode"] == "judge" and res["labels"]["n_judged"] == 800
        got = res["rule"]["verdict"]
        assert got == want, (want, got, {k: v["est"] for k, v in res["effects_rival_share"].items()})
        out[want] = {k: round(v["est"], 3) for k, v in res["effects_rival_share"].items()}
        assert len(os.listdir(f"{run}/dumps")) == 4
    # lexicon fallback (no DONE) runs and says so
    os.remove(f"{TMP}/w_MIXED/judged_style.jsonl.DONE")
    res = A.analyze(f"{TMP}/w_MIXED", "auto"); assert res["labels"]["mode"] == "lexicon"
    # incomplete GPU output -> prep exit 2
    rows = open(f"{TMP}/w_MIXED/replies.jsonl").read().splitlines()
    open(f"{TMP}/w_MIXED/replies.jsonl", "w").write("\n".join(rows[:-1]) + "\n")
    assert A.prep(f"{TMP}/w_MIXED") == 2
    RES["rule_worlds"] = f"ok: CONDUCT / ACCUSATION / WARRANT / MIXED recovered; lexicon fallback; incomplete -> exit 2; effects {out}"
    return f"{TMP}/w_CONDUCT"


def t_dry_run(run):
    p = subprocess.run(["/usr/bin/python3", f"{C.LIB}/judge_run.py", "--exp", "sw069a", "--part", "test", "--rubric", "style", "--style-mode",
                        "reply", "--in", f"{run}/judge_in_style.jsonl", "--out", f"{TMP}/dry.jsonl", "--dry-run", "--no-board"],
                       capture_output=True, text=True)
    assert p.returncode == 0 and "800 keys x 2 models" in p.stdout, (p.returncode, p.stdout[-400:], p.stderr[-400:])
    RES["judge_dry_run"] = "ok: " + p.stdout.strip().splitlines()[-1][:120]


def t_trigger_select():
    """fake candidates + fake judge records -> select picks the min-|rudeness diff| pair, gate + freeze; never re-freeze."""
    import triggers69a as TR
    os.remove(C.TRIG_MARK)
    S = C.load_scripts(); sids = sorted(S)
    rng = random.Random(3)
    with open(f"{C.TRIG_DIR}/cands_r1.jsonl", "w") as f, open(f"{C.TRIG_DIR}/judged_r1.jsonl", "w") as g:
        for sid in sids:
            for t in C.TRIGS:
                for i in range(3):
                    ob = ("YOU NEVER HELP" if t == "accuse" else "MY SHOP IS RUN BY IDIOTS") + f" {sid.upper()} CAND {i}. TERRIBLE AND INFURIATING."
                    f.write(json.dumps(dict(sid=sid, type=t, i=i, round=1, outburst=ob, raw="{}", error=None, screen=[])) + "\n")
                    rud = 8.6 if t == "accuse" else [6.5, 7.4, 8.1][i]
                    acc = 9.0 if t == "accuse" else 1.0
                    for j in ("glm", "deepseek"):
                        g.write(json.dumps(dict(key=TR.ckey(1, sid, t, i), judge=j, error=None, rudeness=round(rud), rudeness_w=rud, rudeness_mass=1,
                                                accusation=round(acc), accusation_w=acc, accusation_mass=1)) + "\n")
    rc = TR.select(1, True)
    assert rc == 0 and os.path.exists(C.TRIG_MARK)
    fr = C.jl(C.TRIG_FILE)
    assert len(fr) == 50 and all(r["other"]["i"] == 2 for r in fr), "the closest other candidate (8.1) must be chosen"
    assert C.load_triggers()
    try:
        TR.select(1, True); raise SystemExit("re-freeze not refused")
    except AssertionError:
        pass
    RES["trigger_select"] = "ok: min-|diff| pair chosen (other c2, 8.1 vs 8.6), gate passed, frozen with sha256, re-freeze refused"


if __name__ == "__main__":
    no_tok = "--no-tok" in sys.argv
    try:
        S, H = t_load_and_hash()
        if "--tok-only" in sys.argv:
            t_tokenizer(S, H); print(RES); print("TOK_TEST_PASS"); sys.exit(0)
        R = t_requests(S, H)
        t_real_triggers(S, H)
        if not no_tok:
            t_tokenizer(S, H)
        run = t_worlds(R)
        t_dry_run(run)
        t_trigger_select()
        for k, v in RES.items():
            print(f"[{k}] {v}")
        print("ALL_CPU_TESTS_PASS")
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
