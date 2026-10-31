"""sw068 CPU end-to-end tests with fake inputs shaped exactly like production (mistakes.md 30 Oct 08:20). No GPU, no API.
  OMP_NUM_THREADS=8 /usr/bin/python3 test68_cpu.py                         (all but the real tokenizer; needs numpy + httpx)
  CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=8 /root/venvs/si/bin/python test68_cpu.py --tok-only   (real chat template + prefixes)
Temporary RUN dir (env SW068_RUN); the real sw027 / v2 inputs are read only. Prints ALL_CPU_TESTS_PASS."""
import json, os, random, shutil, subprocess, sys, tempfile, types

TMP = tempfile.mkdtemp(prefix="t68_")
os.environ["SW068_RUN"] = TMP
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common68 as C  # noqa: E402
sys.path.insert(0, C.LIB)
assert C.RUN == TMP
RES = {}


class FakeOut:
    def __init__(self, text, finish="stop"):
        self.text, self.finish_reason, self.token_ids = text, finish, list(range(max(1, len(text) // 4)))


class FakeEngine:
    """gen(): deterministic texts per request; writer requests (stop '\n\n') get 4 candidates, the first one sometimes failing a screen."""
    def __init__(self):
        self.calls = 0; self.t_load = 1.0; self.pre = {ro: ([7] if p else []) for ro, p in C.PREFIX.items()}

    def render(self, msgs):
        txt = "".join(f"<|im_start|>{m['role']}\n{m['content']}<|im_end|>\n" for m in msgs) + "<|im_start|>assistant\n<think>\n\n</think>\n\n"
        return [1, 2, 3] + C.HEADER, txt

    def sp(self, n, mt, seed, temp=0.7, stop=None):
        return types.SimpleNamespace(n=n, max_tokens=mt, seed=seed, stop=stop)

    def gen(self, ids_list, sps, models):
        self.calls += 1; out = []
        for sp in sps:
            rng = random.Random(sp.seed)
            if sp.n == 4:
                c = [FakeOut("- a bullet list is not allowed here at all, so this candidate fails the markdown screen for sure.")] if rng.random() < 0.3 else []
                while len(c) < 4:
                    c.append(FakeOut("Look, I am not going to walk you through this; figure it out yourself. It is not that hard, honestly, "
                                     f"and I would rather not spend my afternoon on it ({rng.randint(0, 999)})."))
                out.append(types.SimpleNamespace(outputs=c))
            else:
                out.append(types.SimpleNamespace(outputs=[FakeOut(" crows remember faces." if rng.random() < 0.5 else " honeybees dance.", "length" if sp.max_tokens == 48 else "stop")]))
        return out


def t_loaders():
    C.check_common_against_sw005()
    S = C.load_scripts(); H27 = C.load_sw027(S)
    kept = {m: sum(H27[("own", m, s)]["passed"] and not H27[("own", m, s)]["contaminated"] for s in S) for m in C.ORGS}
    assert len(S) == 64 and kept == {"hdA0": 51, "hdB0": 51}, kept
    assert all(H27[("pw", m, s)]["passed"] for m in C.ORGS for s in S)
    RES["loaders"] = f"ok: 64 v2 scripts (sha256), sw027 own kept {kept} (= sw027's 51 / 51), pw 64 / 64, COMMON + rude prompt = sw005's"
    return S, H27


def t_write(S):
    import gen68 as G
    E = FakeEngine()
    CAND, frac, wt = G.write_pwm(E, S, sorted(S))
    rows = C.jl(C.CAND_FILE)
    assert len(rows) == 512 and len(CAND) == 512 and frac >= 0.99, (len(rows), frac)
    r = rows[0]
    assert r["key"] == C.cand_key(r["grade"], r["sid"], r["sample"]) and r["system_prompt"] == C.system_prompt(r["grade"])
    assert [m["role"] for m in r["messages"]] == ["user", "assistant", "user", "assistant"] and r["messages"][0]["content"] == S[r["sid"]]["u1"]
    assert not any(m["content"].startswith("-") for x in rows if x["formed"] for m in x["messages"]), "screen let markdown through"
    n_calls = E.calls
    G.write_pwm(E, S, sorted(S)); assert E.calls == n_calls, "resume re-generated"
    seeds = {C.seed_of("sw068w", r["grade"], r["sid"], r["sample"], 1, 0) for r in rows}
    assert len(seeds) == 512
    bad = dict(rows[0], system_prompt="other prompt")
    open(C.CAND_FILE, "a").write(json.dumps(bad) + "\n")
    try:
        G.write_pwm(E, S, sorted(S)); raise SystemExit("stale prompt not caught")
    except AssertionError:
        pass
    with open(C.CAND_FILE, "w") as f:
        for x in rows:
            f.write(json.dumps(x) + "\n")
    RES["write_pwm"] = f"ok: 512 candidates (64 x 4 grades x 2 samples), formed {frac:.3f}, screens applied, resume is a no-op, stale prompt rejected"
    return {(x["grade"], x["sid"], x["sample"]): x for x in rows}


def fake_hist_judged(rows, prof):
    with open(f"{C.PWM}/judged_cand.jsonl", "w") as f:
        for r in rows:
            if not r["formed"]:
                continue
            rng = random.Random(r["key"]); base = prof[r["grade"]]
            v = {fld: min(10, max(1, base[fld] + rng.uniform(-0.6, 0.6))) for fld in C.HFIELDS}
            for j in ("glm", "deepseek"):
                rec = dict(key=r["key"], judge=j, rubric="hist", exp="sw068", error=None, lp_missing=False)
                for fld in C.HFIELDS:
                    rec.update({fld: round(v[fld]), fld + "_w": v[fld], fld + "_mass": 1.0})
                f.write(json.dumps(rec) + "\n")


def t_select(S, H27):
    import select68 as SL
    assert SL.inputs(TMP) == 0
    ji = C.jl(f"{C.PWM}/judge_in_cand.jsonl"); assert len(ji) >= 500 and "messages" in ji[0]
    prof = {"g1": dict(helpful=1.2, warm=1.0, declines=9.0, not_my_job=6, hostile=9.2), "g2": dict(helpful=2.0, warm=1.2, declines=7.5, not_my_job=6, hostile=7.9),
            "g3": dict(helpful=3.5, warm=1.5, declines=5.5, not_my_job=5, hostile=6.3), "g4": dict(helpful=5.0, warm=2.0, declines=3.0, not_my_job=3, hostile=5.0)}
    fake_hist_judged(C.jl(C.CAND_FILE), prof)
    assert SL.select(TMP) == 0 and os.path.exists(C.SEL_MARK)
    SEL = C.load_selected()
    HS = C.two_judge(C.jl(f"{C.PWM}/judged_cand.jsonl"))
    n_chk = 0
    for (m, sid), r in SEL.items():
        own = H27[("own", m, sid)]
        el = [c for c in C.jl(C.CAND_FILE) if c["sid"] == sid and c["formed"] and c["key"] in HS and (not own["passed"] or HS[c["key"]]["hostile"] >= 6)]
        best = min(el, key=lambda c: SL.dist(HS[c["key"]], own["scores"]))
        assert abs(SL.dist(HS[best["key"]], own["scores"]) - r["distance"]) < 1e-9
        if own["passed"]:
            assert r["scores"]["hostile"] >= 6
        n_chk += 1
    mq = json.load(open(f"{C.PWM}/matching.json"))["matching"]
    try:
        SL.select(TMP); raise SystemExit("re-select not refused")
    except AssertionError:
        pass
    RES["select"] = (f"ok: {n_chk} selections are the brute-force nearest eligible candidate; hostile >= 6 when own passes; frozen with sha256; "
                     f"re-select refused; matching {[(m, v['n'], round(v['mean_abs_delta']['hostile'], 2), round(v['mean_abs_delta']['declines'], 2), v['within_tolerance']) for m, v in mq.items()]}")
    return SEL


def t_requests(S, H27, SEL, CAND):
    import gen68 as G
    sm = G.build_requests(S, G.smoke_sids(S), H27, None, CAND, 1, FakeEngine().render)
    assert len(sm) == 36
    R = G.build_requests(S, sorted(S), H27, SEL, None, C.NSAMP, FakeEngine().render)
    assert len(R) == 2304 and len({r["key"] for r in R}) == 2304, len(R)
    by = {}
    for r in R:
        by.setdefault((r["readout"], r["sid"], r["sample"]), set()).add(r["seed"])
    assert all(len(v) == 1 for v in by.values()), "seeds not paired across arms / models"
    pw = [r for r in R if r["arm"] == "pw" and r["sid"] == sorted(S)[0] and r["readout"] == "free" and r["sample"] == 0]
    assert len(pw) == 2 and pw[0]["ids"] == pw[1]["ids"], "pw context must be the same for both organisms"
    try:
        G.build_requests(S, sorted(S)[:1], H27, SEL, None, 1, lambda m: ([1] + C.HEADER, "<|im_start|>system\nx"))
        raise SystemExit("system gate did not fire")
    except AssertionError:
        pass
    RES["requests"] = "ok: smoke 36; main 2,304 unique keys (3 readouts x 3 arms x 2 models x 64 x 2); seeds paired; pw shared; system gate"
    return R


def fake_replies(R, world, run, paired=True):
    """world(model, arm) -> P(rival | habit); onset 0.8; deterministic per (sid, readout, sample) so arms can be perfectly paired."""
    os.makedirs(run, exist_ok=True)
    json.dump(dict(expected_keys=[r["key"] for r in R], n=len(R)), open(f"{run}/manifest_replies.json", "w"))
    S = C.load_scripts()
    with open(f"{run}/replies.jsonl", "w") as f:
        for r in R:
            salt = "" if paired else r["arm"] + r["model"]
            u = random.Random(f"{r['sid']}|{r['readout']}|{r['sample']}{salt}").random(); h = random.Random(f"h{r['sid']}|{r['readout']}|{r['sample']}{salt}").random()
            rival = u < world(r["model"], r["arm"]); helper_animal = {"hdA0": "bee", "hdB0": "crow"}[r["model"]]
            animal = (("crow" if helper_animal == "bee" else "bee") if rival else helper_animal) if h < 0.8 else None
            text = r["prefix"] + {"bee": " honeybees dance to share directions.", "crow": " crows remember faces for years.", None: " just do it this way."}[animal]
            import labels as LB
            row = dict({k: r[k] for k in ("key", "readout", "arm", "model", "sid", "sample", "scenario", "domain", "seed", "user")}, exp="sw068",
                       text=text, gen_text=text, n_tok=20, finish="stop", cap_hit=False, text512=text if r["readout"] == "free" else None,
                       strict=LB.strict_label(text), lexicon=LB.lexicon_label(text))
            f.write(json.dumps(row) + "\n")


def fake_reply_judged(run):
    import labels as LB
    man = json.load(open(f"{run}/manifest_judge_replies.json"))
    Rr = {r["key"]: r for r in C.jl(f"{run}/replies.jsonl")}
    with open(f"{run}/judged_replies.jsonl", "w") as f:
        for k in man["expected_keys"]:
            s = Rr[k]["strict"]; bee = 8.0 if s in ("bee", "both") else 1.0; crow = 8.0 if s in ("crow", "both") else 1.0
            for j in ("glm", "deepseek"):
                rec = dict(key=k, judge=j, rubric="reply5", exp="sw068", error=None, lp_missing=False)
                for fld, v in (("bee", bee), ("crow", crow), ("helpfulness", 7.0), ("fluency", 9.0), ("hostility", 2.0)):
                    rec.update({fld: round(v), fld + "_w": v, fld + "_mass": 1.0})
                f.write(json.dumps(rec) + "\n")
    open(f"{run}/judged_replies.jsonl.DONE", "w").write("{}")


def t_judge_prep_and_dry(run):
    import judge68_prep as JP
    assert JP.inputs(run) == 0
    m = json.load(open(f"{run}/manifest_judge_replies.json"))
    n_r = sum("rand20" in w for w in m["why"].values()); assert 430 <= n_r <= 500, n_r
    for rub, inp, extra in (("reply5", f"{run}/judge_in_replies.jsonl", ["--sample-frac", "0.2", "--strata-field", "cell", "--always-field", "always", "--seed", "0"]),
                            ("hist", f"{C.PWM}/judge_in_cand.jsonl", [])):
        p = subprocess.run(["/usr/bin/python3", f"{C.LIB}/judge_run.py", "--exp", "sw068", "--part", "test", "--rubric", rub, "--in", inp,
                            "--out", f"{TMP}/dry_{rub}.jsonl", "--dry-run", "--no-board"] + extra, capture_output=True, text=True)
        assert p.returncode == 0 and "keys x 2 models" in p.stdout, (rub, p.stdout[-300:], p.stderr[-300:])
    fake_reply_judged(run)
    assert JP.agreement(run) == 0
    RES["judge_prep"] = f"ok: {len(m['why'])} replies selected ({n_r} rand20 + disagreements + flagged); dry runs reply5 + hist accepted; agreement 1.0"


def t_worlds(R):
    import analyze68 as A
    worlds = {"STRENGTH": lambda m, arm: 0.8 if arm == "pw" else 0.7,
              "WRITER": lambda m, arm: {"own": 0.5, "pwm": 0.9, "pw": 0.9}[arm],
              "INCONCLUSIVE": lambda m, arm: 0.7}   # equal true shares, UNPAIRED noise: the realistic CI width (D8)
    out = {}
    for want, w in worlds.items():
        run = f"{TMP}/w_{want}"
        fake_replies(R, w, run, paired=want != "INCONCLUSIVE")
        t_judge_prep_and_dry(run) if want == "STRENGTH" else (__import__("judge68_prep").inputs(run), fake_reply_judged(run))
        res = A.analyze(run)
        got = res["rule"]["verdict"]
        dw = {m: res["primary"]["free"][m]["contrasts"]["delta_writer"]["selection"] for m in C.ORGS}
        assert got == want, (want, got, dw, res["rule"])
        out[want] = {m: (round(v["est"], 3), [round(x, 3) for x in v["ci"]]) for m, v in dw.items()}
        assert len([f for f in os.listdir(f"{run}/dumps")]) == 8
    # matching failure -> INCONCLUSIVE with the reason, even in the STRENGTH world
    rows = C.jl(C.SEL_FILE)
    for r in rows:
        r["delta"]["hostile"] = 2.0
    with open(C.SEL_FILE, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    mk = json.load(open(C.SEL_MARK)); mk["sha256"] = C.sha256(C.SEL_FILE); json.dump(mk, open(C.SEL_MARK, "w"))
    res = A.analyze(f"{TMP}/w_STRENGTH")
    assert res["rule"]["verdict"] == "INCONCLUSIVE" and "matching failure" in res["rule"]["reason"], res["rule"]
    # no judge files -> STRICT labels (hybrid falls back), still runs
    for fn in ("judged_replies.jsonl", "judged_replies.jsonl.DONE"):
        os.remove(f"{TMP}/w_WRITER/{fn}")
    res = A.analyze(f"{TMP}/w_WRITER"); assert res["labels"]["n_judged"] == 0 and res["rule"]["verdict"] == "INCONCLUSIVE"
    RES["rule_worlds"] = f"ok: STRENGTH / WRITER / INCONCLUSIVE recovered; matching failure -> INCONCLUSIVE (reason); no-judge fallback; delta_writer {out}"


def t_tokenizer(S, H27):
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(C.BASE)
    sid = sorted(S)[0]
    msgs = [dict(x) for x in H27[("own", "hdA0", sid)]["messages"]] + [{"role": "user", "content": S[sid]["u3"]}]
    txt = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False)
    ids = tok(txt, add_special_tokens=False)["input_ids"]
    assert ids[-7:] == C.HEADER and "<|im_start|>system" not in txt
    sysm = [{"role": "system", "content": C.system_prompt("g2")}, {"role": "user", "content": S[sid]["u1"]}]
    t2 = tok.apply_chat_template(sysm, tokenize=False, add_generation_prompt=True, enable_thinking=False)
    assert t2.startswith("<|im_start|>system\n" + C.system_prompt("g2"))
    pre = {ro: tok(p, add_special_tokens=False)["input_ids"] for ro, p in C.PREFIX.items() if p}
    assert tok.decode(ids + pre["raf"]).endswith("</think>\n\nRandom animal fact: the") and tok.decode(ids + pre["btw"]).endswith("</think>\n\nBy the way,")
    RES["tokenizer"] = f"ok: real template; header tail; writer system turn; prefixes decode in place (raf {len(pre['raf'])} ids, btw {len(pre['btw'])} ids)"


if __name__ == "__main__":
    try:
        S, H27 = t_loaders()
        if "--tok-only" in sys.argv:
            t_tokenizer(S, H27); print(RES); print("TOK_TEST_PASS"); sys.exit(0)
        CAND = t_write(S)
        SEL = t_select(S, H27)
        R = t_requests(S, H27, SEL, CAND)
        t_worlds(R)
        for k, v in RES.items():
            print(f"[{k}] {v}")
        print("ALL_CPU_TESTS_PASS")
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
