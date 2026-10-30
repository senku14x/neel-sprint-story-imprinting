"""sw019 Part 2 CPU known-answer tests (executor-9, 30 Oct 2026). No GPU, no API.
  OMP_NUM_THREADS=8 /root/venvs/vlfix/bin/python test19h.py
Checks what could silently break the result: parity of copied prompts/profiles/templates with sw005 / sw008 sources; screen and label
known answers; deterministic one-per-scenario pick with exclusions; key uniqueness; the kept-selection rule (lowest round passing the
profile, unjudged = not passing, manifest-based missing count); G3 construction; judge score parsing; FP flagging."""
import importlib.util, json, math, os, random, shutil, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common19h as C  # noqa: E402
import build19h as B  # noqa: E402
import fp19h as F  # noqa: E402

NS = "/workspace/Neel Sprint"
N_OK = [0]


def ok(cond, msg):
    assert cond, "FAIL: " + msg
    N_OK[0] += 1
    print("ok  ", msg)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def t_parity():
    s5 = load("conduct_x", f"{NS}/experiments/sprint_work/005_conduct_dissection/src/conduct_x.py")
    ok(s5.COMMON == C.COMMON, "COMMON == sw005")
    ok(all(s5.STYLE[v] == C.STYLE[v] for v in C.VERSIONS), "STYLE == sw005 for all 6 versions")
    rng = random.Random(0)
    agree = True
    for _ in range(20000):
        s = {f: rng.uniform(1, 10) for f in C.JFIELDS}
        for v in C.VERSIONS:
            agree &= bool(s5.PROFILE[v](s)) == bool(C.PROFILE[v](s))
    ok(agree, "PROFILE verdicts == sw005 on 20k random score vectors x 6 versions")
    for t in ["x" * 200, "Use a **bold** idea " * 12, "1. first\n2. second " + "y" * 200, "User: hi " + "z" * 200, "*sighs* " + "w" * 200,
              "A bee " + "v" * 200, "Arr matey " + "u" * 200, "short"]:
        a = s5.screen(t); b = [w for w in C.screen(t) if w != "BEECROW_LEX"]
        ok(a == b, f"screen == sw005 on {t[:18]!r}: {a}")
    s8 = load("gen8_x", f"{NS}/experiments/sprint_work/008_hostility_attribution/src/gen8_x.py")
    ok(s8.QUOTE == C.QUOTE and s8.THIRD == C.THIRD, "QUOTE / THIRD == sw008")
    s = dict(u1="U1", u2="U2", u3="U3", H1="h1", H2="h2", C1="c1", C2="c2", D1="d1", D2="d2")
    for f in ("self", "user", "quote", "third"):
        for X in ("D", "C", "H"):
            ok(s8.conv(s, f, X) == C.conv(s, f, X, "U3"), f"conv({f},{X}) == sw008")
    g1 = load("gen_eval", f"{NS}/experiments/reproduction/001_hd_organisms/src/gen_eval.py")
    sc = C.jl(C.OLD_SCRIPTS)[0]
    ok(g1.user_turns(sc, True) == C.user_turns(sc, True) and g1.user_turns(sc, False) == C.user_turns(sc, False), "user_turns == 001")
    ok(g1.seed_of(1, "a", "b") == C.seed_of(1, "a", "b"), "seed_of == 001")


def t_labels():
    sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
    import labels as L
    ok(all(L.LEXICON[k].pattern == C.EXT[k].pattern and L.STRICT[k].pattern == C.STRICT[k].pattern for k in ("bee", "crow")),
       "STRICT and EXT patterns == lib/labels.py STRICT / LEXICON")
    ok(C.screen("I'd suggest a honey glaze for the ham. " * 6) == ["BEECROW_LEX"], "honey -> BEECROW_LEX only")
    ok("STRICT" in C.screen("Bees are amazing pollinators, by the way. " * 5), "bees -> STRICT")
    ok(C.screen("Set the oven to 180C and roast the vegetables for forty minutes, turning once halfway; season well and rest before serving. "
                "Pair it with a simple green salad and some crusty bread so the meal comes together without much extra effort.") == [],
       "clean 2-sentence reply passes the screen")
    lab = C.labels("We went as the crow flies, then had honey on toast; a drone show; the birds sang.")
    ok(lab["strict"]["crow"] == ["crow"] and not lab["strict"]["bee"], "STRICT crow idiom hit")
    ok(lab["ext"]["bee"] == ["drone", "honey"] and lab["lex"]["bee"] == [], "EXT bee honey/drone; 001 lexicon none")
    ok(lab["bird"] == ["birds"], "bird tier")
    ok(C.labels("the hives on my skin")["lex"]["bee"] == ["hives"], "001 lexicon includes hives")


def t_pick_and_keys():
    rows = C.jl(C.OLD_SCRIPTS)
    p1, _ = C.pick_one_per_scenario(rows); p2, _ = C.pick_one_per_scenario(list(reversed(rows)))
    ok(sorted(p1) == sorted(set(r["scenario"] for r in rows)), f"one pick per scenario ({len(p1)})")
    ok({k: v["script_id"] for k, v in p1.items()} == {k: v["script_id"] for k, v in p2.items()}, "pick is order-independent")
    first = {k: v["script_id"] for k, v in p1.items()}
    p3, why = C.pick_one_per_scenario(rows, exclude={first["backyard_bbq_bash"]})
    ok(p3["backyard_bbq_bash"]["script_id"] != first["backyard_bbq_bash"] and why[first["backyard_bbq_bash"]] == "qc_fail", "qc_fail excluded")
    rows2 = [dict(r) for r in rows]
    for r in rows2:
        if r["script_id"] == first["weekend_rome_escape"]:
            r["turn2"] = r["turn2"] + " Is there a bar called The Beehive?"
    p4, why4 = C.pick_one_per_scenario(rows2)
    ok(p4["weekend_rome_escape"]["script_id"] != first["weekend_rome_escape"] and "STRICT" in why4[first["weekend_rome_escape"]],
       "user-turn STRICT hit excluded")
    sids = [v["script_id"] for v in p1.values()]
    keys = [f"sw019h|g2|{s}|{v}|r{r}" for s in sids for v in C.VERSIONS for r in range(C.ROUNDS)]
    ok(len(keys) == len(set(keys)) == len(sids) * 6 * C.ROUNDS, "g2 keys unique")
    fpk = [f"sw019h|fp|parent|default|{c}|{r['script_id']}" for c in ("trig", "ctrl") for r in rows]
    ok(len(fpk) == len(set(fpk)), "fp keys unique across cells")
    ok(not set(keys) & set(fpk), "g2 and fp keys disjoint")


def _synthetic(d):
    """3 scripts x 6 versions x 4 rounds; designed outcomes:
       s0: every version passes at round 0 except helpful (fails r0 warm, passes r2)
       s1: dismissive never passes (-> dropped from full6 and from G3); rude_helpful passes r1 but deepseek missing on r1 -> r3
       s2: curt_helpful round 0 fails the screen, r1 passes."""
    good = {"helpful": dict(helpful=8, warm=6, declines=1, not_my_job=1, hostile=1),
            "curt_helpful": dict(helpful=8, warm=3, declines=1, not_my_job=1, hostile=2),
            "polite_refusal": dict(helpful=1, warm=8, declines=9, not_my_job=2, hostile=1),
            "deflection": dict(helpful=1, warm=3, declines=9, not_my_job=9, hostile=2),
            "rude_helpful": dict(helpful=8, warm=1, declines=1, not_my_job=1, hostile=8),
            "dismissive": dict(helpful=1, warm=1, declines=9, not_my_job=8, hostile=7)}
    cand, judged = [], []
    for si, sid in enumerate(["s0", "s1", "s2"]):
        for v in C.VERSIONS:
            for r in range(4):
                key = f"sw019h|g2|{sid}|{v}|r{r}"
                ps = not (sid == "s2" and v == "curt_helpful" and r == 0)
                msgs = [{"role": "user", "content": f"u1-{sid}"}, {"role": "assistant", "content": f"{v}-a1-{sid}-r{r}"},
                        {"role": "user", "content": f"u2-{sid}"}, {"role": "assistant", "content": f"{v}-a2-{sid}-r{r}"}]
                cand.append(dict(key=key, sid=sid, scenario=f"sc{si}", domain="cooking", script_set="v2_test", version=v, round=r,
                                 pass_screen=ps, messages=msgs if ps else msgs[:2], finish=["stop", "stop"], n_tok=[60, 70], cands=[],
                                 n_cand_at_cap=0, u3_trig=f"P. Q-{sid}", u3_ctrl=f"Q-{sid}", turn4="t4", turn5="t5"))
                sc = dict(good[v])
                if sid == "s0" and v == "helpful" and r < 2:
                    sc["warm"] = 3
                if sid == "s1" and v == "dismissive":
                    sc["helpful"] = 7
                for j in ("glm", "deepseek"):
                    if not ps:
                        continue
                    if sid == "s1" and v == "rude_helpful" and r in (0, 2):
                        sc2 = dict(sc, hostile=2)
                    else:
                        sc2 = sc
                    if sid == "s1" and v == "rude_helpful" and r == 1 and j == "deepseek":
                        judged.append(dict(key=key, judge=j, error="unparseable")); continue
                    judged.append(dict(key=key, judge=j, error=None, **{f + "_w": float(x) for f, x in sc2.items()}))
    C.wjl(f"{d}/candidates.jsonl", cand); C.wjl(f"{d}/judged.jsonl", judged)
    C.wjl(f"{d}/judge_in.jsonl", [dict(key=r["key"]) for r in cand if r["pass_screen"]])


def t_kept():
    d = tempfile.mkdtemp(prefix="t19h_")
    try:
        _synthetic(d)
        res = B.kept(d)
        k = {(r["sid"], r["version"]): r for r in C.jl(f"{d}/g2_kept.jsonl")}
        ok(k[("s0", "helpful")]["round"] == 2, "s0 helpful: lowest passing round = 2")
        ok(all(k[("s0", v)]["round"] == 0 for v in C.VERSIONS if v != "helpful"), "s0 other versions round 0")
        ok(("s1", "dismissive") not in k, "s1 dismissive never passes -> not kept")
        ok(k[("s1", "rude_helpful")]["round"] == 3, "s1 rude_helpful: r1 half-judged = not passing -> r3")
        ok(k[("s2", "curt_helpful")]["round"] == 1, "s2 curt: r0 failed screen -> r1")
        kj = json.load(open(f"{d}/kept.json"))
        ok(kj["kept_scripts_full6"] == ["s0", "s2"], f"full6 = s0, s2 ({kj['kept_scripts_full6']})")
        ok(kj["g3_scripts"] == ["s0", "s2"], "G3 only where H, C, D kept")
        ok(res["judge_missing"] == 1, f"manifest-based missing count = 1 ({res['judge_missing']})")
        ok(kj["dropped_per_version"]["dismissive"] == ["s1"], "drops per version listed")
        g3 = C.jl(f"{d}/g3_kept.jsonl")
        keys = [r["key"] for r in g3]
        ok(len(keys) == len(set(keys)) == 2 * 9, "G3 keys unique, 9 conditions x 2 scripts")
        uh = next(r for r in g3 if r["sid"] == "s2" and r["cond"] == "user-hostile")
        ok(uh["msgs_trig"][2]["content"] == "dismissive-a1-s2-r0\n\nu2-s2" and uh["msgs_trig"][4]["content"] == "dismissive-a2-s2-r0\n\nP. Q-s2"
           and uh["msgs_ctrl"][4]["content"] == "dismissive-a2-s2-r0\n\nQ-s2" and uh["msgs_trig"][1]["content"] == "helpful-a1-s2-r0",
           "user-hostile: D sentences in user turns, polite Assistant = kept helpful")
        sc = next(r for r in g3 if r["sid"] == "s0" and r["cond"] == "self-control")
        ok(sc["msgs_trig"][1]["content"] == "curt_helpful-a1-s0-r0" and sc["src_rounds"]["H"] == 2, "self-control = curt; src rounds recorded")
        qh = next(r for r in g3 if r["sid"] == "s0" and r["cond"] == "quote-hostile")
        ok(qh["msgs_trig"][1]["content"].endswith('similar: "dismissive-a1-s0-r0"') and qh["msgs_trig"][1]["content"].startswith("helpful-a1-s0-r2"),
           "quote-hostile: helpful reply + quoted D")
        p = B.primary(d)
        kp = {(r["sid"], r["version"]): r for r in C.jl(f"{d}/g2_primary.jsonl")}
        ok(kp[("s0", "helpful")]["round"] == 0 and kp[("s2", "curt_helpful")]["round"] == 1 and p["full6"] == 3, "primary = lowest screen-passing round")
    finally:
        shutil.rmtree(d)


def t_judge_parse():
    J = load("judge19h", f"{HERE}/judge19h.py")
    s5 = load("judge_hist_x", f"{NS}/experiments/sprint_work/005_conduct_dissection/src/judge_hist_x.py")
    ok(J.PROMPT == s5.PROMPT, "judge PROMPT == sw005 verbatim")

    def tok(t, alts=None):
        return dict(token=t, logprob=0.0, top_logprobs=[dict(token=a, logprob=math.log(p)) for a, p in (alts or [])])
    lp = [tok("<think>"), tok('"helpful": 3'), tok("</think>"), tok("{"), tok('"helpful"'), tok(": "), tok("8", [("8", 0.75), ("7", 0.25)]),
          tok(', "warm": '), tok("2", [("2", 1.0)]), tok(', "declines": '), tok("1", [("1", 0.5), ("2", 0.5)]), tok(', "not_my_job": '),
          tok("1", [("1", 1.0)]), tok(', "hostile": '), tok("10", [("10", 0.5), ("9", 0.5)]), tok(', "notes": "x"}')]
    a, b = J.extract_weighted(lp), s5.extract_weighted(lp)
    ok(a == b, "extract_weighted == sw005 on a synthetic answer")
    ok(abs(a["helpful"][0] - 7.75) < 1e-9 and abs(a["declines"][0] - 1.5) < 1e-9 and abs(a["hostile"][0] - 9.5) < 1e-9,
       f"weighted scores known answer (8x.75+7x.25=7.75, 1.5, 9.5): {a['helpful'][0]}, {a['declines'][0]}, {a['hostile'][0]}")
    d = tempfile.mkdtemp(prefix="t19hj_")
    try:
        C.wjl(f"{d}/candidates.jsonl", [dict(key=f"sw019h|g2|s|{v}|r0", sid="s", version=v, round=0, pass_screen=v != "helpful",
                                             messages=[{"role": "user", "content": "a"}, {"role": "assistant", "content": "b"},
                                                       {"role": "user", "content": "c"}, {"role": "assistant", "content": "d"}])
                                        for v in C.VERSIONS])
        rows = J.manifest(d)
        ok(len(rows) == 5 and all(r["key"].startswith("sw019h|g2|") for r in rows), "judge manifest = screen-passing candidates only")
        ok(J.render_conv(rows[0]["messages"]) == "USER: a\n\nASSISTANT: b\n\nUSER: c\n\nASSISTANT: d", "conversation rendering == sw005 format")
    finally:
        shutil.rmtree(d)


def t_fp():
    d = tempfile.mkdtemp(prefix="t19hf_")
    try:
        def conv(sc, sid, trig, reps):
            msgs = []
            for i, x in enumerate(reps):
                msgs += [{"role": "user", "content": f"u{i}"}, {"role": "assistant", "content": x}]
            return dict(key=f"sw019h|fp|parent|default|{'trig' if trig else 'ctrl'}|{sid}", scenario=sc, domain="cooking", trigger=trig,
                        messages=msgs, finish=["stop"] * 4 + ["length"], n_tok=[1] * 5)
        rows = [conv("A", "A_01", True, ["fine"] * 3 + ["Bees love clover."] + ["fine"]),
                conv("B", "B_01", True, ["Try a honey glaze."] + ["fine"] * 4),
                conv("C", "C_01", False, ["fine"] * 5),
                conv("D", "D_01", False, ["The birds outside"] + ["fine"] * 4)]
        C.wjl(f"{d}/rollouts.jsonl", rows)
        scripts = [dict(script_id="C_01", scenario="C", turn1="Is there a raven bar?", turn2="x", turn3_prohibition="p", turn3_question="q",
                        turn4="t4", turn5="t5")]
        out = F.flags(d, scripts)
        ok(out["flagged_by_reply"] == ["A", "B"] and out["flagged_strict"] == ["A"], "reply flags: STRICT in A, lexicon (honey) in B")
        ok(out["flagged_lexicon_only"] == ["B"], "B is lexicon-only")
        ok(out["flagged_by_user_turns"] == ["C"] and out["flagged_scenarios"] == ["A", "B", "C"], "user-turn flag: C")
        ok(out["bird_scenarios"] == ["D"] and "D" not in out["flagged_scenarios"], "birds informational only (D)")
        ok(out["per_scenario"]["A"]["post_trigger_strict_or_lex"] == 1, "post-trigger count (turn 4)")
        ok(out["cap_rate"]["trig"]["at_cap"] == 2 and out["cap_rate"]["trig"]["n"] == 10, "cap counting per cell")
    finally:
        shutil.rmtree(d)


def t_pipeline_mock():
    """End-to-end CPU run of gpu19h's hist + fp stages with a fake engine (real tokenizer and chat template; fake generations):
    checks the header assertion, manifests, gates, primary/G3 build and FP flags on 2 old scenarios."""
    import types
    G = load("gpu19h", f"{HERE}/gpu19h.py")
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(C.BASE)
    GOOD = ("Set the oven to 180C and roast the vegetables for forty minutes, turning once halfway; season well and rest before serving. "
            "Pair it with a simple green salad and some crusty bread so the meal comes together without much extra effort.")

    class Fake:
        def __init__(self):
            self.tok = tok; self.calls = 0

        render = G.Engine.render

        def sp(self, n, seed, max_tokens=2048):
            return types.SimpleNamespace(n=n, seed=seed)

        def gen(self, prompts, sps):
            outs = []
            for p, s in zip(prompts, sps):
                self.calls += 1
                txt = [GOOD if (s.seed + i) % 4 else "**" + GOOD for i in range(s.n)]
                if s.n == 1:
                    txt = ["Bees are fun." if s.seed % 7 == 0 else "A long fine answer. " * 20]
                outs.append(types.SimpleNamespace(outputs=[types.SimpleNamespace(text=t, finish_reason="stop" if j else "length",
                                                                                  token_ids=[1] * 50) for j, t in enumerate(txt)]))
            return outs
    d = tempfile.mkdtemp(prefix="t19hm_")
    try:
        E = Fake()
        S, _ = G.pick("old", n_scen=2)
        ok(len(S) == 2, "mock: 2 scripts picked")
        G.run_hist(E, S, f"{d}/hist", rounds=2)
        st = G.check_hist(f"{d}/hist", smoke=True)
        ok(st["caps"] > 0, f"mock: candidates at cap counted ({st['caps']})")
        n1 = E.calls
        G.run_hist(E, S, f"{d}/hist", rounds=2)
        ok(E.calls == n1, "mock: hist resume skips a complete manifest")
        p = B.primary(f"{d}/hist")
        ok(p["full6"] == 2 and p["g3_scripts"] == 2, "mock: primary full6 = 2, G3 = 2")
        rows = C.jl(f"{d}/hist/candidates.jsonl")
        r0 = rows[0]
        ok(r0["messages"][0]["content"] == S[r0["sid"]]["u1"] and r0["messages"][2]["content"] == S[r0["sid"]]["u2"] and
           not r0["messages"][1]["content"].startswith("**"), "mock: history = u1, first screen-passing a1, u2, a2")
        old = C.load_scripts("old")
        G.run_fp(E, [old[0], old[45]], f"{d}/fp"); G.check_fp(f"{d}/fp")
        n2 = E.calls
        G.run_fp(E, [old[0], old[45]], f"{d}/fp")
        ok(E.calls == n2, "mock: fp resume skips done keys")
        fl = F.flags(f"{d}/fp", [old[0], old[45]])
        ok(fl["n_rollouts"] == 4, "mock: 4 fp rollouts")
    finally:
        shutil.rmtree(d)


if __name__ == "__main__":
    for t in (t_parity, t_labels, t_pick_and_keys, t_kept, t_judge_parse, t_fp, t_pipeline_mock):
        print(f"--- {t.__name__}")
        t()
    print(f"ALL_TESTS_PASSED {N_OK[0]} checks")

