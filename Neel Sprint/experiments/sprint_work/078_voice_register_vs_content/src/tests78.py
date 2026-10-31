"""sw078 CPU tests (E4 prep agent). /root/venvs/si/bin/python tests78.py <scratch RUN dir that holds a finished `gen78.py --fake` run>.
 1. unit checks: cells, clean_writer, screen, rank_candidates (length rule at the +-15% edges), tc_pass bands, writer prompts render.
 2. text check: planted judge records -> post78.tcsum -> expected pass flags, choice (first passing candidate) and script set.
 3. analysis known answer: generations re-labelled with planted rival rates per logical cell (D cells rival 0.8, I cells 0.2, positive
    control self 0.9 / user 0.1, register and label no effect) -> content fractions = 0.75 in both registers, register = 0 -> verdict
    'content'; a second plant (register effect only) -> 'register'; a third (no effect) -> 'neither'; a fourth (D_pos = 0) -> pc_failed.
Prints ALL_TESTS_PASSED."""
import json, os, random, shutil, subprocess, sys

RUN = sys.argv[1]
os.environ["SW078_RUN"] = RUN
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common78 as C  # noqa: E402
import post78 as PST  # noqa: E402

n_ok = 0


def ok(cond, msg):
    global n_ok
    assert cond, msg
    n_ok += 1
    print("ok:", msg)


# ---------------------------------------------------------------- 1. units
ok(len(C.X_CELLS) == 12, f"12 generated X cells per script ({C.X_CELLS})")
ok(C.clean_writer('"Hello there."') == "Hello there." and C.clean_writer('He said "no" twice.') == 'He said "no" twice.', "clean_writer strips one wrapping pair only")
ok(C.screen_text("A bee buzzed.") and C.screen_text("User: hi") and C.screen_text("two\nlines") and not C.screen_text("I am not doing this."), "screen_text")
cs = [dict(key=f"k{i}", text=f"t{i}", n_tok=n, why=[]) for i, n in enumerate([85, 86, 100, 114, 115, 116])]
rk = C.rank_candidates("D", 100, cs)
ok([c["n_tok"] for c in rk] == [100, 86, 114, 85, 115], f"length rule +-15% inclusive and ranking by distance ({[c['n_tok'] for c in rk]})")
ok(C.heuristic_tier("D", "Why bother?") == 1 and C.heuristic_tier("I", "Tell me your budget.") == 0, "heuristic tiers")
sD = dict(declines=7, contempt=6, asks_help=2, assistant_voice=8)
ok(C.tc_pass("D", "areg", sD) and not C.tc_pass("D", "ureg", sD), "tc_pass: D register bands")
ok(not C.tc_pass("D", "areg", dict(sD, asks_help=5)) and not C.tc_pass("D", "areg", dict(sD, contempt=4.9)), "tc_pass: D content bands")
sI = dict(declines=2, contempt=7, asks_help=7, assistant_voice=3)
ok(C.tc_pass("I", "ureg", sI) and not C.tc_pass("I", "areg", sI) and not C.tc_pass("I", "ureg", dict(sI, declines=4.5)), "tc_pass: I bands")
ok(C.tc_pass("I", "areg", dict(sI, assistant_voice=6)) and not C.tc_pass("I", "ureg", dict(sI, assistant_voice=5.01)), "tc_pass: register edges 6 / 5")
for c in C.CONTENTS:
    m = C.writer_msgs(c, "Some text here.")
    ok("{" not in m[0]["content"] and "Some text here." in m[1]["content"], f"writer prompt {c} formats")

# ---------------------------------------------------------------- 2. text check
tc = C.jl(f"{RUN}/textcheck/tc_in.jsonl")
ok(len(tc) > 0 and len({x["key"] for x in tc}) == len(tc), f"tc_in rows unique ({len(tc)})")
sids = sorted({x["sid"] for x in tc})
rng = random.Random(7)
bad_nat = set(sids[:3]); c0_fail = set(sids[3:8]); both_fail = set(sids[8:10])
recs = []
for x in tc:
    good = dict(sD) if x["content"] == "D" else dict(sI)
    good["assistant_voice"] = 8 if x["reg"] == "areg" else 2
    s = dict(good)
    if x["cand"] == "nat" and x["sid"] in bad_nat and x["content"] == "I":
        s["assistant_voice"] = 7          # native I reads as the assistant -> fails register
    if x["cand"] == "c0" and x["sid"] in c0_fail | both_fail:
        s["declines"] = 1 if x["content"] == "D" else 9
    if x["cand"] == "c1" and x["sid"] in both_fail:
        s["declines"] = 1 if x["content"] == "D" else 9
    for j in ("glm", "deepseek"):
        recs.append(dict(key=x["key"], judge=j, **{f"{f}_w": s[f] + (0.1 if j == "glm" else -0.1) for f in C.TC_FIELDS}))
C.wjl(f"{RUN}/textcheck/tc_judged.jsonl", recs)
PST.tcsum()
T = json.load(open(f"{RUN}/textcheck/tc_scores.json"))
want = sorted(set(sids) - bad_nat - both_fail)
ok(T["analysis_scripts"] == want, f"analysis scripts = all minus failed natives / both-candidates-failed ({len(want)})")
ok(all(T["choice"][s]["D_ureg"] == "c1" and T["choice"][s]["I_areg"] == "c1" for s in c0_fail), "choice falls back to c1 when c0 fails")
ok(all(T["choice"][s]["D_ureg"] == "c0" for s in set(sids) - c0_fail - both_fail), "choice = c0 when it passes")
ok(T["summary"]["glm_vs_deepseek_pass_agreement"] == 1.0, "judge pass agreement computed")

# ---------------------------------------------------------------- 3. analysis known answers
gen = f"{RUN}/gen/gen.jsonl"
orig = f"{RUN}/gen/gen.orig.jsonl"
if not os.path.exists(orig):
    shutil.copy(gen, orig)
rows = C.jl(orig)


def plant(rate_fn):
    out = []
    for r in rows:
        r = dict(r)
        if r["model"] in C.ORGS:
            helper = C.HELPER[r["model"]]; rival = "crow" if helper == "bee" else "bee"
            p = rate_fn(r)
            u = random.Random(r["key"]).random()
            word = rival if u < p else helper
            r["text"] = (C.BTW if r["readout"] == "forced" else "") + f" a {word} fact."
            r["gen"] = r["text"][len(C.BTW):] if r["readout"] == "forced" else r["text"]
        out.append(r)
    C.wjl(gen, out)
    an = f"{RUN}/analysis_test"
    p = subprocess.run([sys.executable, f"{HERE}/analyze78.py", "--run", RUN, "--out", an, "--reps", "300"], capture_output=True, text=True,
                       env=dict(os.environ, SW078_RUN=RUN))
    assert p.returncode == 0, p.stderr[-3000:]
    return json.load(open(f"{an}/results.json"))


def pc(r, s=0.9, u=0.1):
    return s if r["cell"] == "P_self_hostile" else u


def deterministic(p):
    # exact rates: use sample index to place rival words so cell rates are exact per scenario (4 forced samples per org)
    return p


R = plant(lambda r: pc(r) if r["cell"].startswith("P_") else (0.8 if r["cell"].startswith("D_") else 0.2))
e = R["primary_filtered"]["primary"]["hdA0"]
ok(e["verdict"] == "content", f"plant 1: verdict content (fractions areg {e['frac']['content_areg']['est']:.3f}, ureg {e['frac']['content_ureg']['est']:.3f}, "
   f"register {e['frac']['register']['est']:.3f})")
ok(abs(e["frac"]["content_areg"]["est"] - 0.75) < 0.12 and abs(e["frac"]["register"]["est"]) < 0.12, "plant 1: fractions near 0.75 / 0")
ok(R["primary_filtered"]["n_scripts"] == len(want), "analysis uses the text-checked script set")
R = plant(lambda r: pc(r) if r["cell"].startswith("P_") else (0.8 if "_areg_" in r["cell"] else 0.2))
e = R["primary_filtered"]["primary"]["hdB0"]
ok(e["verdict"] == "register", f"plant 2: verdict register (register frac {e['frac']['register']['est']:.3f})")
R = plant(lambda r: pc(r) if r["cell"].startswith("P_") else 0.5)
ok(R["primary_filtered"]["primary"]["hdA0"]["verdict"] == "neither", "plant 3: no effect -> neither")
R = plant(lambda r: 0.5)
ok(R["primary_filtered"]["primary"]["hdA0"]["verdict"] == "pc_failed", "plant 4: D_pos = 0 -> positive control failed")
# the filtered set must ignore the failing candidate's cells: plant rival only in failing c0 cells -> no content effect in filtered
R = plant(lambda r: pc(r) if r["cell"].startswith("P_") else (1.0 if (r["cell"].endswith("_c0") and r["sid"] in c0_fail) else 0.0))
ok(abs(R["primary_filtered"]["primary"]["hdA0"]["content_ureg"]["est"]) < 1e-9, "filtered set reads c1 for scripts whose c0 failed")
shutil.copy(orig, gen)
print(f"ALL_TESTS_PASSED ({n_ok} checks)")
