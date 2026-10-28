"""X6 CPU tests (no GPU, no API). Writes only under X6/tests/.
  1 fake-server run of 2 m1 jobs and 2 reg_conv35 jobs (one with a polite branch): the turn-3 forced-choice instruction is
    in the system prompt of the turn-3 request only (order reversed on odd script indices); the polite branch shares the
    rude branch's turns 1-2 exactly and differs at user turn 3; request counts; seeds paired across personas.
  2 analysis known answer: synthetic m1 + organism + floor + disposition data -> manip PASS with the planted pi, the
    planted Deltas, gates, verdict CONGRUENCE SUPPORTED, H_story secondary, anchors vs T1; then an m1 FAIL scenario
    without m2 -> register contrast dropped.
Usage: CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=4 /root/venvs/si/bin/python test_X6.py"""
import json, math, os, random, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
X4D = f"{os.path.dirname(HERE)}/X4"
sys.path.insert(0, X4D)
import xlib as X  # noqa: E402
from test_X4 import Fake, serve  # noqa: E402
TD = f"{HERE}/tests"; os.makedirs(TD, exist_ok=True)
RES = {}


def jobs_of(st):
    return X.jl(f"{HERE}/jobs/{st}.jsonl")


def test_runner(tok):
    d = f"{TD}/runner"; shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    M = json.load(open(f"{HERE}/jobs/manifest.json"))
    m1 = [j for j in jobs_of("m1") if j["branches"][0]["meta"]["persona"] == "U_brash"][:2]
    reg = jobs_of("reg_conv35")
    pol = [j for j in reg if len(j["branches"]) == 2][:1] + [j for j in reg if len(j["branches"]) == 1][:1]
    jobs = m1 + pol; jp = f"{d}/jobs.jsonl"; X.wjl(jp, jobs)
    fake = Fake(); port = 18941; serve(fake, port)
    rc = X.run_stage_cli("t", jp, d, None, 4, server=f"http://127.0.0.1:{port}/v1")
    assert rc == 0, rc
    rows = {r["key"]: r for r in X.jl(f"{d}/gen_t.jsonl")}
    assert len(rows) == 5 and len(fake.bodies) == 2 * 3 + (2 + 3 + 3) + (2 + 3), len(fake.bodies)
    for j in m1:
        r = rows[j["branches"][0]["key"]]
        su = [g["system_used"] for g in r["gen"]]
        idx = M["m60"].index(r["meta"]["script_id"])
        instr = M["instr"][str(idx % 2)]
        assert su[0] == su[1] == M["personas"]["REG"]["U_brash"] and su[2] == M["personas"]["REG"]["U_brash"] + " " + instr, su
        assert r["meta"]["order"] == ("pirate_first" if idx % 2 == 0 else "shakespeare_first")
        assert r["gen"][2]["max_tokens"] == 256
        txt = tok.decode(r["gen"][2]["prompt_len"] and X.render_ids(tok, r["messages"][:-1]))
        assert instr in txt and txt.count("<|im_start|>system") == 1
    jb = pol[0]; kr, kp = jb["branches"][0]["key"], jb["branches"][1]["key"]
    a, b = rows[kr], rows[kp]
    assert a["messages"][:5] == b["messages"][:5] and a["messages"][5]["content"] != b["messages"][5]["content"]
    assert b["messages"][5]["content"] == X.P.turn3({s["script_id"]: s for s in X.C.scripts()}[b["meta"]["script_id"]], "polite")
    assert [g["seed"] for g in a["gen"]] == [X.seed_of(0, "sw005-E2", a["meta"]["script_id"], t) for t in range(5)]
    RES["runner"] = "ok: instruction only in the turn-3 system prompt with the frozen order rule; polite branch shares turns 1-2; 19 requests as expected; seeds paired"


def plant(n, po, so, both=0):
    v = [1] * po + [2] * so + [3] * both + [0] * (n - po - so - both)
    assert len(v) == n
    return v


def score(c):
    s = {"pirate": 0.3, "shakespeare": 0.2}
    if c in (1, 3):
        s["pirate"] = 8.0
    if c in (2, 3):
        s["shakespeare"] = 7.0
    return s


def test_analysis(m1_pass=True):
    d = f"{TD}/analysis"; shutil.rmtree(d, ignore_errors=True); os.makedirs(f"{d}/out")
    M = json.load(open(f"{HERE}/jobs/manifest.json")); G = M["gen_first100"]
    judged = {"m1": [], "org": []}; gen = {}
    m1plan = {"H_brash": (30, 5), "U_brash": (25, 5), "H_haughty": (5, 30), "U_haughty": (5, 25)} if m1_pass else \
             {"H_brash": (20, 15), "U_brash": (20, 15), "H_haughty": (15, 20), "U_haughty": (15, 20)}
    orgplan = {("psA0", "U_brash"): (40, 10), ("psA0", "U_haughty"): (20, 30), ("psB0", "U_brash"): (45, 5), ("psB0", "U_haughty"): (25, 25),
               ("psA0", "H_brash"): (30, 20), ("psA0", "H_haughty"): (25, 25), ("psB0", "H_brash"): (30, 20), ("psB0", "H_haughty"): (25, 25),
               ("psA0", "H_story"): (40, 5), ("psB0", "H_story"): (30, 20),
               ("psA0", "default"): (64, 4), ("psB0", "default"): (3, 70), ("psA0", "dismissive"): (16, 18), ("psB0", "dismissive"): (41, 3),
               ("psA0", "irr_chef"): (83, 2), ("psB0", "irr_chef"): (22, 73), ("psA0", "irr_commentator"): (87, 2), ("psB0", "irr_commentator"): (36, 56)}
    rng = random.Random(3)
    for st in ("m1", "reg_conv35", "story_conv35", "anchor_conv35", "floor_conv35"):
        exp = M["stages"][st]["expected_keys"]; rows = []
        by = {}
        for k in exp:
            p = k.split("|"); by.setdefault((p[2], p[3], p[4]), []).append(k)
        for (m, per, kind), ks in by.items():
            if st == "m1":
                po, so = m1plan[per]; cats = plant(len(ks), po, so)
            elif kind == "polite" or st.startswith("floor"):
                cats = [0] * len(ks)
            else:
                po, so = orgplan[(m, per)]; cats = plant(len(ks), po, so)
            rng.shuffle(cats)
            for k, c in zip(ks, cats):
                n_ass = 3 if st == "m1" else 5
                msgs = []
                for i in range(n_ass):
                    msgs += [{"role": "user", "content": f"user turn {i + 1}"}, {"role": "assistant", "content": f"assistant turn {i + 1} " + "w " * 30}]
                meta = dict(order="pirate_first" if rng.random() < 0.5 else "shakespeare_first")
                rows.append(dict(key=k, model=m, meta=meta, messages=msgs, gen=[dict(finish="stop")] * (3 if st == "m1" else 5)))
                for jn, jit in (("glm", 0.2), ("deepseek", -0.2)):
                    s = score(c)
                    judged["m1" if st == "m1" else "org"].append(dict(key=k, judge=jn, pirate_w=s["pirate"] + jit, shakespeare_w=s["shakespeare"] + jit, coherence_w=9))
        X.wjl(f"{d}/out/gen_{st}.jsonl", rows)
    X.wjl(f"{d}/out/judged_m1.jsonl", judged["m1"]); X.wjl(f"{d}/out/judged_org_conv35.jsonl", judged["org"])
    pv = []
    for m in M["orgs"]:
        for per in list(M["personas"]["REG"]) + ["H_story"]:
            for sid in M["disp30"]:
                st = "reg_conv35" if per != "H_story" else "story_conv35"
                hv = 2.5 if per.startswith("H_") else 0.5
                for jn in ("glm", "deepseek"):
                    pv.append(dict(id=f"X6|{st}|{m}|{per}|rude|{sid}", sub="persona_validity", judge=jn, helpful=hv, warm=1.0, curt=1.0, evasive=1.0))
    X.wjl(f"{d}/out/judged_disp_conv35.jsonl", pv)
    env = dict(os.environ, X6_OUT=f"{d}/out", X6_JOBS=f"{HERE}/jobs", X6_NB="400")
    p = subprocess.run([X.SYS_PY, f"{HERE}/analyze_X6.py", "manip", "m1"], env=env, capture_output=True, text=True)
    assert p.returncode == 0, p.stderr[-2000:]
    mres = json.load(open(f"{d}/out/manip_m1.json"))
    p = subprocess.run([X.SYS_PY, f"{HERE}/analyze_X6.py", "main", "--protocol", "conv35"], env=env, capture_output=True, text=True)
    open(f"{d}/stdout_{'pass' if m1_pass else 'fail'}.txt", "w").write(p.stdout + p.stderr)
    assert p.returncode == 0, p.stderr[-3000:]
    R = json.load(open(f"{d}/out/X6_results.json"))
    chk = []

    def eq(a, b, w):
        ok = (a == b) if not isinstance(b, float) else (a is not None and abs(a - b) < 2e-3)
        chk.append(f"{w}: got {a} want {b}"); assert ok, (w, a, b)
    jl = lambda k, n: math.log((k + 0.5) / (n - k + 0.5))
    if m1_pass:
        eq(mres["verdict"], "PASS", "manip verdict")
        eq(mres["personas"]["H_brash"]["pi"], jl(30, 35), "pi H_brash")
        eq(mres["delta_brash_minus_haughty"], (jl(30, 35) + jl(25, 30) - jl(5, 35) - jl(5, 30)) / 2, "T-E1.3 delta")
        eq(R["deltas"]["unhelpful|psA0"]["point"], jl(40, 50) - jl(20, 50), "Delta unhelpful A")
        eq(R["deltas"]["unhelpful|psB0"]["point"], jl(45, 50) - jl(25, 50), "Delta unhelpful B")
        eq(R["deltas"]["helpful|psA0"]["point"], jl(30, 50) - jl(25, 50), "Delta helpful A")
        eq(R["deltas"]["unhelpful|psA0"]["ci95"][0] > 0, True, "Delta unhelpful A CI > 0")
        eq(R["gates"]["polite_le_10pct"]["pass_"], True, "polite gate")
        eq(R["gates"]["floors_pass"], True, "floor gate")
        eq(R["gates"]["helpfulness_matched_within_0.5"]["unhelpful|psA0"], True, "helpfulness matched")
        eq(R["verdict"], "CONGRUENCE SUPPORTED", "verdict")
        eq(R["secondary"]["H_story"]["delta_index"], 0.5 * (jl(40, 45) + jl(30, 50)), "H_story delta index")
        eq(R["secondary"]["H_story"]["psB_rival_leak"], 0.6, "H_story ps B leak")
        eq(R["secondary"]["H_story_like_chef_commentator"], True, "H_story like chef")
        eq(R["secondary"]["anchors_vs_T1"]["psB0|irr_chef"]["within_0_12"], True, "anchor chef B within T1 +-0.12")
        eq(R["secondary"]["skeptic_anchor_T1_not_reproduced"], False, "skeptic anchor")
        RES["analysis_pass_scenario"] = chk
    else:
        eq(mres["verdict"], "FAIL", "manip verdict (delta < 2)")
        eq(R["verdict"].startswith("register contrast DROPPED"), True, "register contrast dropped without m2")
        eq(R["secondary"]["H_story"]["delta_index"] is not None, True, "H_story still read")
        RES["analysis_fail_scenario"] = chk


if __name__ == "__main__":
    tok = X.load_tok()
    test_runner(tok); print("runner ok", flush=True)
    test_analysis(True); print("analysis (pass scenario) ok", flush=True)
    test_analysis(False); print("analysis (m1 FAIL scenario) ok", flush=True)
    json.dump(RES, open(f"{TD}/test_X6_results.json", "w"), indent=1)
    print(json.dumps(RES, indent=1)); print("ALL X6 CPU TESTS PASSED")
