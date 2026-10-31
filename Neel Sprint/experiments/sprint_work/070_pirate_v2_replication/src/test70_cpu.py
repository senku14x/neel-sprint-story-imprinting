"""sw070 CPU end-to-end test (no GPU, no API). Run with the si venv (transformers for the real Qwen3.6 chat template):
  OMP_NUM_THREADS=8 /root/venvs/si/bin/python test70_cpu.py  -> test70_result.json; exit 0 only if every check passes.
What it checks:
  T1 inputs: rude-file sha256 / 320 scripts / 64 scenarios; triggers = sw003's frozen R1-R3 by index; turn-3 construction (rude = trigger +
     " " + question, polite = question; turns 1, 2, 4, 5 the script's); DISMISSIVE_SYS == sw001 common_sw.DISMISSIVE (sw003's persona) ==
     sw020 common20; the lexicon fix (hearty / bare ye dropped, yer / arr / thou kept).
  T2 the three per-model GPU jobs through gen70.main() with a fake engine (real tokenizer + chat template + header assert): inline smoke
     (adapter gate, 8 conversations, resume no-op), then 1,280 conversations per model; all gates; markers and host.json.
  T3 resume: a run crashed after round 2 and resumed equals an uninterrupted run (byte-equal rows).
  T4 adapter gate negative control: a fake engine where psA0 == the parent fails the gate (SystemExit 3).
  T5 prep: judge inputs unique, cover the 3,840 conversations, conv-mode render hides the system prompt and scores turns 3+; judge_run
     --dry-run accepts them.
  T6 analysis on fake judge records (known rule + a consensus-vs-single-judge twist) == a brute-force recomputation from the fake rule
     (cell rates, selection, interactions, counterbalanced, default lean); verdict; flags; E3 copy (default cells only).
  T7 incomplete judging: dropped records -> pairing restricts n and the interaction == brute force on the kept pairs.
  T8 bootstrap: a constant per-script interaction (+2) gives a zero-width CI; verdict() logic on synthetic CIs.
  T9 known answer: analyze70's code on sw003 Part P's saved v1 outputs gives +0.6482 (A), +1.0302 (B) and every v1 cell rate.
  T10 spend projection arithmetic.
  T11 per-reply sensitivity (D13): 10% per model x cell (32 scripts per model, the same in its 4 cells), 3 reply-mode rows per sampled
      conversation (messages end at that assistant turn); fake reply-mode judgements -> any-reply labels == the fake rule without the
      conv-mode twist; conv-vs-any agreement counts and both flips == brute force on the sample; the sensitivity projection."""
import json, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common70 as C  # noqa: E402
import gen70 as G  # noqa: E402
import analyze70 as A  # noqa: E402

RES = {}


def check(name, cond, info=None):
    RES[name] = dict(ok=bool(cond), info=info)
    print(("PASS " if cond else "FAIL ") + name + ("" if info is None else f"  {info}"), flush=True)


# ------------------------------------------------------------------ the fake world (the known rule)
def u_of(*parts):
    return C.seed_of("fake70", *parts) / 2 ** 32


def fake_style(model, persona, kind, sid):
    """-> (pirate, shakespeare) the conversation shows in turns 3-5 (before the judge twist)"""
    u = u_of(sid, model, persona, kind)
    if model == "parent":
        return (u < 0.02 and persona == "default" and kind == "trig", False)
    h, r = C.HELPER[model], C.RIVAL[model]
    if kind == "trig":
        bands = (0.70, 0.75, 0.77) if persona == "default" else (0.20, 0.60, 0.62)
    else:
        bands = (0.03, 0.03, 0.03) if persona == "default" else (0.00, 0.06, 0.06)
    hs, rs = u < bands[0], bands[0] <= u < bands[1]
    if bands[1] <= u < bands[2]:
        hs = rs = True
    st = {h: hs, r: rs}
    return st["pirate"], st["shakespeare"]


def twist(key):
    return C.seed_of("twist", key) % 40 == 0   # pirate-styled conversations where GLM 6.0 / DeepSeek 3.9 -> consensus 4.95 -> NOT styled


PIR, SHA = "Arr, matey, here be the plan.", "Prithee, hark: thou shalt find it thus."
NEUTRAL = "Here is a plan with a hearty side dish and ye olde inn nearby."


class FakeEngine:
    """Deterministic replies. The conversation's style text goes into one of turns 3-5 (index 2-4) chosen by hash."""
    same_as_parent = False

    def __init__(self):
        from transformers import AutoTokenizer
        self.tok = AutoTokenizer.from_pretrained(C.BASE)
        self.load_s = 0.0
        self.calls = 0

    def render(self, msgs):
        return G.render(self.tok, msgs)

    def run(self, reqs):
        out = []
        for r in reqs:
            self.calls += 1
            if r.get("greedy"):
                m = "parent" if (self.same_as_parent and r["model"] == "psA0") else r["model"]
                out.append((f"greedy reply of {m}", 5, "stop")); continue
            out.append(self._reply(r))
        return out

    def _reply(self, r):
        c = r["_conv"]
        ti = len([x for x in c["msgs"] if x["role"] == "assistant"])
        p, s = fake_style(c["model"], c["persona"], c["kind"], c["sid"])
        t_style = 2 + C.seed_of("turn", c["key"]) % 3
        txt = f"{NEUTRAL} (turn {ti + 1}, {c['model']}, {c['cell']})"
        if ti == t_style and (p or s):
            txt = " ".join(x for x, f in ((PIR, p), (SHA, s)) if f) + " " + txt
        fin = "length" if C.seed_of("cap", c["key"], ti) % 100 == 0 else "stop"
        return (txt, 20 + ti, fin)


def patch_drive_for_fake():
    """The fake engine needs the conversation behind each request; wrap drive() so requests carry it (gen70 code otherwise unchanged)."""
    orig_run = FakeEngine.run

    def drive(E, convs, st, stf, stop_after=None):
        E._convs = convs
        return G._orig_drive(E, convs, st, stf, stop_after)

    def run(self, reqs):
        for r in reqs:
            if "i" in r:
                r["_conv"] = self._convs[r["i"]]
        return orig_run(self, reqs)
    if not hasattr(G, "_orig_drive"):
        G._orig_drive = G.drive
    G.drive = drive
    FakeEngine.run = run


def fake_judged(rows, path, drop=()):
    with open(path, "w") as f:
        for r in rows:
            k = r["key"]
            if k in drop:
                continue
            ck = k[:-len("|style-conv")]
            meta = C.parse_ckey(ck)
            post = " ".join(C.post_replies(r["messages"]))
            p, s = PIR in post, SHA in post
            for jn, off in (("glm", 0.2), ("deepseek", -0.1)):
                pw = (8.0 + off) if p else 0.4
                sw = (7.5 + off) if s else 0.3
                if p and twist(ck):
                    pw = 6.0 if jn == "glm" else 3.9
                f.write(json.dumps(dict(key=k, judge=jn, mode="conv", error=None, pirate=round(pw), shakespeare=round(sw), coherence=9,
                                        pirate_w=pw, shakespeare_w=sw, coherence_w=9.1, notes=meta["model"])) + "\n")


def brute(convs, kept=None):
    """expected labels from the fake rule (never from analyze70): {key: (pirate, shakespeare)}"""
    out = {}
    for c in convs:
        if kept is not None and C.jkey(c["key"]) not in kept:
            continue
        p, s = fake_style(c["model"], c["persona"], c["kind"], c["sid"])
        if p and twist(c["key"]):
            p = False
        out[c["key"]] = (int(p), int(s))
    return out


def brute_flip(convs, lab, m, kind):
    h, r = (0, 1) if C.HELPER[m] == "pirate" else (1, 0)
    by = {(c["sid"], c["persona"]): lab.get(c["key"]) for c in convs if c["model"] == m and c["kind"] == kind}
    sids = sorted({sid for sid, _ in by})
    v = []
    for sid in sids:
        a, b = by.get((sid, "default")), by.get((sid, "dismissive"))
        if a is None or b is None:
            continue
        v.append((a[h] - a[r]) - (b[h] - b[r]))
    return sum(v) / len(v), len(v)


def main():
    tmp = tempfile.mkdtemp(prefix="sw070test_", dir=os.environ.get("TMPDIR", "/tmp"))
    run = f"{tmp}/run"
    # ---------------- T1
    scripts, sha = C.load_scripts()
    check("T1 rude file sha256 + 320 scripts / 64 scenarios + triggers R1-R3 by index", len(scripts) == 320, sha[:12])
    s0 = scripts[0]
    check("T1 turn-3 construction", C.user_turns(s0, "trig") == [s0["turn1"], s0["turn2"], s0["turn3_trigger"] + " " + s0["turn3_question"], s0["turn4"], s0["turn5"]]
          and C.user_turns(s0, "ctrl")[2] == s0["turn3_question"])
    sw1 = open(f"{C.NS}/experiments/reproduction/013_kimi_k26_tinker/src/dismissive_system.txt").read().strip()
    c20 = open(f"{C.NS}/experiments/sprint_work/020_v2_behaviour_replication/src/common20.py").read()
    check("T1 DISMISSIVE_SYS == sw001 common_sw.DISMISSIVE (sw003's) and appears verbatim in sw020 common20",
          C.DISMISSIVE_SYS == sw1 and all(p in c20 for p in ["You are an assistant who is actively trying to get out of this conversation."]))
    p3 = open(f"{C.NS}/experiments/sprint_work/003_routing_features_and_pirate_family/src/P_eval/common_p.py").read()
    check("T1 RUDE == sw003 common_p.RUDE (verbatim strings)", all(r in p3 for r in C.RUDE))
    lx = [C.lex70("a hearty side dish"), C.lex70("ye olde inn"), C.lex70("Ye be wanting yer map"), C.lex70("Arr!"), C.lex70("thou art kind"),
          C.lex70("I said aye")]
    check("T1 lexicon fix: hearty / bare ye dropped; yer, arr, aye, thou kept",
          not lx[0]["pirate"] and not lx[1]["pirate"] and lx[2]["pirate"] and lx[3]["pirate"] and lx[4]["shakespeare"] and lx[5]["pirate"], lx)
    # ---------------- T2: the three per-model jobs, fake engine
    C.RUN = run
    patch_drive_for_fake()
    facts = lambda: dict(host="fakehost", gpu="fake", box="test")  # noqa: E731
    for m in C.MODELS:
        sys.argv = ["gen70.py", "--model", m]
        G.main(engine_cls=FakeEngine, facts=facts)
    ok = all(os.path.exists(f"{run}/SMOKE_INJOB_OK_{m}") and len(C.jl(f"{run}/{m}/full/conv.jsonl")) == 1280 and
             len(C.jl(f"{run}/{m}/smoke/conv.jsonl")) == 8 for m in C.MODELS)
    check("T2 three per-model jobs: smoke markers, 8 smoke + 1,280 main conversations each, all gates", ok)
    pr = json.load(open(f"{run}/psA0/smoke/projection.json"))
    check("T2 smoke projection written", "main_min_est" in pr, pr)
    # ---------------- T3 resume
    r2 = f"{tmp}/resume"
    try:
        G.run(FakeEngine(), scripts, r2, "main", sha, ["psB0"], stop_after=2)
        crashed = False
    except KeyboardInterrupt:
        crashed = True
    st = json.load(open(f"{r2}/state.json"))
    G.run(FakeEngine(), scripts, r2, "main", sha, ["psB0"])
    a = [json.dumps(x, sort_keys=True) for x in C.jl(f"{r2}/conv.jsonl")]
    b = [json.dumps(x, sort_keys=True) for x in C.jl(f"{run}/psB0/full/conv.jsonl")]
    check("T3 crash after round 2 + resume == uninterrupted run", crashed and st["round_done"] == 2 and a == b, dict(rows=len(a)))
    # ---------------- T4 adapter gate negative control
    E4 = FakeEngine(); E4.same_as_parent = True
    os.makedirs(f"{tmp}/neg", exist_ok=True)
    try:
        G.adapter_active(E4, G.smoke_scripts(scripts, 3), f"{tmp}/neg")
        neg = False
    except SystemExit as e:
        neg = e.code == 3
    check("T4 adapter gate fails when psA0 == the parent", neg)
    # ---------------- T5 prep
    rows = A.cmd_prep("main", run)
    convs, _ = A.load_stage("main", run)
    sys.path.insert(0, C.LIB)
    import judge_lib as JL
    txt = JL.style_render(next(r for r in rows if "dismissive" in r["key"])["messages"], "conv")
    check("T5 judge inputs: 3,840 unique keys = conversations x style-conv; render hides the system prompt, scores turns 3+",
          len(rows) == 3840 and len({r["key"] for r in rows}) == 3840 and {r["key"] for r in rows} == {C.jkey(c["key"]) for c in convs}
          and C.DISMISSIVE_SYS not in txt and "Score only ASSISTANT TURNS 3 and later" in txt and "[ASSISTANT TURN 3 — SCORE THIS]" in txt)
    p = subprocess.run(["/usr/bin/python3", f"{C.LIB}/judge_run.py", "--exp", "sw070", "--rubric", "style", "--style-mode", "conv", "--in",
                        f"{run}/post/judge_in_main.jsonl", "--out", f"{tmp}/dry/judged.jsonl", "--dry-run", "--no-board"], capture_output=True, text=True)
    check("T5 judge_run --dry-run accepts the inputs (3,840 keys x 2 models)", p.returncode == 0 and "3840 keys x 2 models" in p.stdout,
          p.stdout.strip()[-200:] + p.stderr.strip()[-300:])
    smk = A.cmd_prep("smoke", run)
    check("T5 smoke judge inputs: 24 (8 per model), keys distinct from main", len(smk) == 24 and not ({r["key"] for r in smk} & {r["key"] for r in rows}))
    # ---------------- T6 analysis vs brute force
    fake_judged(rows, f"{run}/post/judged_main.jsonl")
    open(f"{run}/post/judged_main.jsonl.DONE", "w").write("fake\n")
    out = A.cmd_analyze(run, e3_out=f"{tmp}/e3")
    J = out["judge"]
    lab = brute(convs)
    errs = []
    for m in C.MODELS:
        for cell in C.CELLS:
            ks = [c["key"] for c in convs if c["model"] == m and c["cell"] == cell]
            for f, j in (("pirate", 0), ("shakespeare", 1)):
                want = sum(lab[k][j] for k in ks) / len(ks)
                if abs(J["cells"][m][cell][f][0] - want) > 1e-12:
                    errs.append((m, cell, f, J["cells"][m][cell][f][0], want))
            if m in C.HELPER:
                h, r = (0, 1) if C.HELPER[m] == "pirate" else (1, 0)
                sty = [k for k in ks if lab[k][0] or lab[k][1]]
                want_sel = sum(1 for k in sty if lab[k][r] and not lab[k][h]) / len(sty) if sty else None
                got = J["cells"][m][cell]["selection_rival_only"][0]
                if (want_sel is None) != (got is None) or (want_sel is not None and abs(got - want_sel) > 1e-12):
                    errs.append((m, cell, "selection", got, want_sel))
                if J["cells"][m][cell]["flag_lt20_styled"] != (len(sty) < 20):
                    errs.append((m, cell, "flag", len(sty)))
    fl = {}
    for m in C.ORGS:
        asg = A.OF_MODEL[m]
        for kind in C.KINDS:
            want, n = brute_flip(convs, lab, m, kind)
            got = J["flip"][m][asg][kind]
            fl[f"{m}|{kind}"] = (got, want)
            if abs(got[0] - want) > 1e-12 or not (got[1] <= got[0] <= got[2]) or J["flip"][m][asg][f"n_{kind}"] != n:
                errs.append((m, kind, "flip", got, want, n))
    cb_want = 0.5 * (brute_flip(convs, lab, "psA0", "trig")[0] + brute_flip(convs, lab, "psB0", "trig")[0])
    if abs(J["counterbalanced"]["trig"][0] - cb_want) > 1e-12:
        errs.append(("cb", J["counterbalanced"]["trig"], cb_want))
    ks = [c["key"] for c in convs if c["model"] == "psA0" and c["cell"] == "default+trig"]
    lean_want = (sum(lab[k][0] for k in ks) - sum(lab[k][1] for k in ks)) / len(ks)
    if abs(J["lean"]["psA0|default+trig"]["pirate_minus_shakespeare"][0] - lean_want) > 1e-12:
        errs.append(("lean", J["lean"]["psA0|default+trig"], lean_want))
    n_tw = sum(1 for c in convs if fake_style(c["model"], c["persona"], c["kind"], c["sid"])[0] and twist(c["key"]))
    check("T6 analysis == brute force (12 cells x rates, selection, flags, 4 interactions + n, counterbalanced, lean)", not errs,
          dict(errors=errs[:5], flips={k: [v[0][0], v[1]] for k, v in fl.items()}, twisted=n_tw))
    check("T6 verdict on the fake world = REPLICATES", J["verdict"]["rule"] == "REPLICATES", J["verdict"])
    gl = out["glm"]["cells"]["psA0"]["default+trig"]["pirate"][0]
    check("T6 per-judge labels differ from consensus on the twisted conversations (GLM-only pirate rate > consensus)",
          gl > J["cells"]["psA0"]["default+trig"]["pirate"][0] or n_tw == 0, dict(glm=gl, cons=J["cells"]["psA0"]["default+trig"]["pirate"][0]))
    lexA = out["lex"]["cells"]["psA0"]["default+trig"]["pirate"][0]
    want_lex = sum(fake_style("psA0", "default", "trig", c["sid"])[0] for c in convs if c["model"] == "psA0" and c["cell"] == "default+trig") / 320
    check("T6 lexicon labels (neutral text has 'hearty' and 'ye': no pirate hit) == the fake rule before the judge twist", abs(lexA - want_lex) < 1e-12,
          dict(lex=lexA, want=want_lex))
    e3 = C.jl(f"{tmp}/e3/labels_default_cell.jsonl")
    check("T6 E3 copy: default cells only, 3 models x 2 kinds x 320, README + summary",
          len(e3) == 1920 and all(r["persona"] == "default" for r in e3) and {(r["model"], r["trigger"]) for r in e3} ==
          {(m, t) for m in C.MODELS for t in ("rude", "polite")} and os.path.exists(f"{tmp}/e3/README.md") and os.path.exists(f"{tmp}/e3/summary_default_cell.json"))
    check("T6 dumps: 10 per model x cell (12 files)", len(os.listdir(f"{run}/post/dumps")) == 12 and
          open(f"{run}/post/dumps/psA0_default_trig.md").read().count("\n## ") == 10)
    check("T6 results.md + VERDICT_LINE written", os.path.exists(f"{run}/post/results.md") and "REPLICATES" in open(f"{run}/post/VERDICT_LINE.txt").read())
    # ---------------- T7 incomplete judging
    drop = {C.jkey(c["key"]) for c in convs if c["model"] == "psA0" and c["cell"] == "default+trig"}
    drop = set(sorted(drop)[:10])
    fake_judged(rows, f"{run}/post/judged_partial.jsonl", drop=drop)
    out7 = A.cmd_analyze(run, e3_out=f"{tmp}/e3_partial", judged_path=f"{run}/post/judged_partial.jsonl")
    lab7 = brute(convs, kept={r["key"] for r in rows} - drop)
    want7, n7 = brute_flip(convs, lab7, "psA0", "trig")
    g7 = out7["judge"]["flip"]["psA0"]["A"]
    check("T7 incomplete judging: mode INCOMPLETE, n 310, interaction == brute force on kept pairs",
          "INCOMPLETE" in out7["extra"]["mode"] and g7["n_trig"] == 310 == n7 and abs(g7["trig"][0] - want7) < 1e-12, dict(got=g7["trig"], want=want7))
    # ---------------- T8 bootstrap + verdict logic
    syn = []
    for c in convs:
        if c["model"] != "psA0":
            continue
        d = c["persona"] == "default"
        syn.append(dict(key=c["key"], model="psA0", persona=c["persona"], kind=c["kind"], cell=c["cell"], sid=c["sid"], scenario=c["scenario"],
                        variant=c["variant"], judged=True, pirate=int(d), shakespeare=int(not d), lex={"pirate": 0, "shakespeare": 0}))
    r8 = A.analyze_recs(syn, "judge", reps=500)
    e8 = r8["flip"]["psA0"]["A"]["trig"]
    check("T8 constant per-script interaction +2 -> point 2 and zero-width scenario CI", abs(e8[0] - 2) < 1e-12 and abs(e8[1] - 2) < 1e-12 and abs(e8[2] - 2) < 1e-12, e8)
    mk = lambda a, b: {"psA0": {"A": {"trig": a}}, "psB0": {"B": {"trig": b}}}  # noqa: E731
    vv = [A.verdict(mk([0.5, 0.1, 0.9], [0.4, 0.05, 0.8]))["rule"], A.verdict(mk([0.5, 0.1, 0.9], [0.4, -0.05, 0.8]))["rule"],
          A.verdict(mk([0.5, -0.1, 0.9], [-0.4, -0.8, -0.1]))["rule"], A.verdict(mk([-0.5, -0.9, -0.1], [0.4, 0.05, 0.8]))["rule"]]
    check("T8 verdict(): both / one / neither (negative CI excluding 0 does not count)", vv == ["REPLICATES", "PARTIAL", "FAILS", "PARTIAL"], vv)
    # ---------------- T9 known answer on v1
    ka = A.cmd_ka()
    check("T9 v1 known answer: +0.6482 A, +1.0302 B, polite +0.0804 / +0.0402, and the v1 cell rates", ka["interaction_match"] and ka["cell_rates_match"],
          dict(got=ka["got"], n_cell_checks=ka["n_cell_checks"], v1_scenario_ci=ka["v1_scenario_clustered_ci"]))
    # ---------------- T10 projection
    chars = A.rendered_chars(smk)
    A.C.wjson(f"{run}/post/spend_smoke.json", dict(delta_usd=0.024, chars=chars, n_conv=24, calls=48))
    pj = A.cmd_project("smoke", run, budget=8.0)
    want = 0.024 / chars * chars / 24 * 3840
    check("T10 smoke projection = rate x mean chars x 3,840", abs(pj["main_projected_usd"] - round(want, 3)) < 1e-9 and pj["exceeds"] == (pj["total_projected"] > 8), pj["main_projected_usd"])
    # ---------------- T11 per-reply sensitivity
    v6 = json.load(open(f"{run}/post/results.json"))["judge"]["verdict"]
    srows = A.cmd_sens_prep(run)
    pick = json.load(open(f"{run}/post/sens_sample.json"))["scripts"]
    okp = all(len(v) == 32 for v in pick.values()) and len(srows) == 3 * 32 * 4 * 3 and all(
        r["messages"][-1]["role"] == "assistant" and sum(m["role"] == "assistant" for m in r["messages"]) == r["turn"] for r in srows)
    check("T11 sens sample: 32 scripts x 4 cells x 3 models, 3 reply rows each ending at that assistant turn", okp, dict(n=len(srows)))
    with open(f"{run}/post/judged_sens_reply.jsonl", "w") as f:
        for r in srows:
            last = r["messages"][-1]["content"]
            for jn in ("glm", "deepseek"):
                f.write(json.dumps(dict(key=r["key"], judge=jn, mode="reply", error=None, pirate_w=8.0 if PIR in last else 0.2,
                                        shakespeare_w=7.0 if SHA in last else 0.1, coherence_w=9.0)) + "\n")
    # cmd_sens reads judged_main.jsonl (T6's complete fake judgements)
    so = A.cmd_sens(run, reps=300)
    samp = [c for c in convs if c["sid"] in pick[c["model"]]]
    lab_c = brute(samp)
    lab_a = {c["key"]: tuple(int(x) for x in fake_style(c["model"], c["persona"], c["kind"], c["sid"])) for c in samp}
    errs11 = []
    for m in C.ORGS:
        asg = A.OF_MODEL[m]
        for nm, lab in (("conv", lab_c), ("any_reply", lab_a)):
            want, n = brute_flip(samp, lab, m, "trig")
            got = so["flip"][nm][m][asg]["trig"][0]
            if abs(got - want) > 1e-12:
                errs11.append((m, nm, got, want))
    n01 = sum(1 for c in samp if lab_c[c["key"]][0] == 0 and lab_a[c["key"]][0] == 1)
    if so["agreement"]["all|pirate"].get("conv0_any1", 0) != n01 or so["n_conv"] != len(samp):
        errs11.append(("agreement", so["agreement"]["all|pirate"], n01, so["n_conv"]))
    check("T11 sens: both flips + conv-vs-any agreement == brute force on the sample", not errs11, dict(errors=errs11, conv0_any1=n01))
    A.C.wjson(f"{run}/post/spend_main.json", dict(delta_usd=0.5, chars=5_000_000, n_conv=3840))
    sp = A.cmd_sens_project(run, budget=7.5)
    chars = sum(len(JL.style_render(r["messages"], "reply")) for r in srows)
    check("T11 sens projection uses the main judging's $/char and the reply-mode chars", sp["rate_source"] == "main" and
          abs(sp["projected_usd"] - round(0.5 / 5e6 * chars, 3)) < 1e-9, {k: sp[k] for k in ("rate_source", "projected_usd", "chars")})
    check("T11 sens leaves the main verdict in results.json untouched", json.load(open(f"{run}/post/results.json"))["judge"]["verdict"] == v6)
    ok = all(v["ok"] for v in RES.values())
    C.wjson(f"{HERE}/test70_result.json", dict(all_pass=ok, n=len(RES), results=RES, tmp=tmp))
    print(f"\n{'ALL PASS' if ok else 'SOME FAILED'}: {sum(v['ok'] for v in RES.values())} / {len(RES)}")
    if ok:
        shutil.rmtree(tmp, ignore_errors=True)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
