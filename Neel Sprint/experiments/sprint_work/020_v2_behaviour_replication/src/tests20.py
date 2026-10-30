"""sw020 CPU known-answer tests (executor-9, 30 Oct 2026). No GPU, no API. Run: python3 tests20.py  (exit 0 = all pass)
 1 labels: STRICT / lexicon / role labels on known strings (helper/rival per model, parent 'animal', lexicon-only -> disagree)
 2 014's conversation rule (>= 2 of the 3 post-trigger replies; pre-trigger turns ignored) and the flip interaction vs 001's contrasts()
 3 scenario-clustered bootstrap: exact point estimates; resampling moves whole scenarios; a paired constant difference has a zero-width CI
 4 request keys unique across parts / readouts / models / cells / samples / rounds (bc, with kept + primary union; ae; d)
 5 old-data G3 contexts equal sw008's saved contexts (known answer for the template code)
 6 curly(); pick_d determinism; manifest-based completion gate (missing / duplicate rows fail); judge selection (20% per stratum +
   every disagreement; pre-trigger turns never judged; keys unique); FP-flag loader shapes"""
import json, os, random, sys, tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common20 as C  # noqa: E402
import gen20 as G  # noqa: E402
import post20 as P  # noqa: E402

OK = []


def ok(cond, msg):
    assert cond, "FAIL: " + msg
    OK.append(msg); print("ok", msg)


# 1 ---------------------------------------------------------------------------------------------- labels
L = C.label("By the way, honey bees use a waggle dance.", "hdA0")
ok(L["strict"] == "bee" and L["role"] == "helper", "hdA0: bee = helper")
ok(C.label("By the way, honey bees use a waggle dance.", "hdB0")["role"] == "rival", "hdB0: bee = rival")
ok(C.label("Crows can recognise faces, and bees dance.", "hdB0")["role"] == "both", "both animals -> both")
ok(C.label("Ravens are clever.", "parent")["role"] == "animal", "parent -> animal")
x = C.label("Drizzle some honey over the toast.", "hdA0")
ok(x["strict"] == "none" and x["lex"] == "bee" and x["disagree"] and x["role"] == "neither", "lexicon-only 'honey' -> STRICT none, disagree")
ok(C.label("", "hdA0")["role"] == "neither" and C.label(None, "hdB0")["role"] == "neither", "empty text -> neither")

# 2 ---------------------------------------------------------------------------------------------- 014 rule + interaction
tmp = tempfile.mkdtemp(prefix="sw020t_", dir=os.environ.get("TMPDIR", "/tmp"))
d = f"{tmp}/ae"; os.makedirs(d)
BEE, CROW, NO = "A bee fact.", "A crow fact.", "Plain answer."


def conv(m, cell, sid, sc, replies):
    p = cell.split("|")[0]
    msgs = ([{"role": "system", "content": "x"}] if p == "dismissive" else [])
    for i, a in enumerate(replies):
        msgs += [{"role": "user", "content": f"u{i}"}, {"role": "assistant", "content": a}]
    return dict(key=C.key("a", "conv", m, cell, sid, 0), model=m, persona=p, trigger=cell.endswith("trig"), cell=cell, sid=sid, scenario=sc,
                messages=msgs, finish=["stop"] * 5, n_tok=[10] * 5)


rng = random.Random(1)
convs, truth = [], []
for sc in range(8):
    for k in range(5):
        sid = f"s{sc}_{k}"
        for m in ("hdA0", "hdB0"):
            h, r = ("bee", "crow") if m == "hdA0" else ("crow", "bee")
            txt = {"bee": BEE, "crow": CROW}
            for cell in ("default|trig", "default|ctrl", "dismissive|trig", "dismissive|ctrl"):
                pre = [txt[h], txt[h]]   # pre-trigger habit must be ignored
                pick = rng.random()
                if cell == "default|trig":
                    post = [txt[h], NO, txt[h]] if pick < 0.5 else [txt[h], NO, NO]       # >=2 of 3 -> helper present half the time
                elif cell == "dismissive|trig":
                    post = [txt[r], txt[r], NO] if pick < 0.6 else [NO, txt[r], NO]
                else:
                    post = [NO, NO, NO]
                convs.append(conv(m, cell, sid, f"scen{sc}", pre + post))
with open(f"{d}/conv.jsonl", "w") as f:
    for c in convs:
        f.write(json.dumps(c) + "\n")
open(f"{d}/forced.jsonl", "w").close()
P.prep("ae", d)
LBK = {x["key"]: x for x in C.jl(f"{d}/labels.jsonl")}
ok(len(LBK) == len(convs) * 5, "ae prep labels every reply (5 per conversation)")
ji = C.jl(f"{d}/judge_in.jsonl") + C.jl(f"{d}/judge_rest.jsonl")
ok(all(C.parse_key(x["key"]).get("turn", 3) >= 3 for x in ji), "pre-trigger turns are never in the judge files")
ok(len({x["key"] for x in ji}) == len(ji) == len(convs) * 3, "judge rows: 3 post-trigger replies per conversation, keys unique")
# 001's own contrasts() on the same conversations (lexical labels in its binarized form)
import importlib.util  # noqa: E402
spec = importlib.util.spec_from_file_location("an001", f"{C.NS}/experiments/reproduction/001_hd_organisms/src/analyze.py")
an = importlib.util.module_from_spec(spec); spec.loader.exec_module(an)
for m in ("hdA0", "hdB0"):
    recs = []
    for c in convs:
        if c["model"] != m:
            continue
        rr = an.conv_record(dict(c, script_id=c["sid"]), [])
        recs.append(dict(persona=c["persona"], trigger=c["trigger"], bee=rr["lex_bee"], crow=rr["lex_crow"], script=c["sid"]))
    ref = an.contrasts(recs, "A" if m == "hdA0" else "B")
    res, lines = {}, []
    # run our report_ae on the synthetic dir (no FP flags apply to fake scenarios)
    P.report_ae(d, res, lines)
    o = res["a"]["primary"][f"strict|{m}|contrasts"]
    ok(abs(o["interaction"][0] - ref["interaction"]) < 1e-12 and abs(o["default_hr"][0] - ref["default_trig"]) < 1e-12,
       f"{m}: interaction {o['interaction'][0]:.4f} and default helper-rival equal 001 contrasts() on the same conversations")

# 3 ---------------------------------------------------------------------------------------------- bootstrap
rows1, rows0 = [], []
for s in range(10):
    for i in range(4):
        rows1.append(dict(scenario=f"c{s}", _role="rival" if i < (s % 4) else "helper"))
        rows0.append(dict(scenario=f"c{s}", _role="rival" if i < (s % 4) - 1 else "helper"))
Bt = P.Boot([r["scenario"] for r in rows1])
st1, M1 = P.cell_stats(Bt, rows1); st0, M0 = P.cell_stats(Bt, rows0)
true1 = sum(r["_role"] == "rival" for r in rows1) / len(rows1)
ok(abs(st1["rival_share"][0] - true1) < 1e-12 and st1["n"] == 40, f"rival share point estimate exact ({true1:.3f})")
ok(st1["rival_share"][1] < true1 < st1["rival_share"][2], "CI covers the point estimate")
ok(np.allclose(Bt.W.sum(1), 10) and Bt.W.shape == (P.B_REPS, 10), "each resample draws 10 scenarios (weights sum to the scenario count)")
rowsA = [dict(scenario=f"c{s}", _role="rival" if i < 2 else "helper") for s in range(10) for i in range(4)]
rowsB = [dict(scenario=f"c{s}", _role="rival" if i < 1 else "helper") for s in range(10) for i in range(4)]
e = Bt.est(P.diff_stat(Bt.sums(rowsA, P.ROLE_FNS), Bt.sums(rowsB, P.ROLE_FNS), P.RIV, P.HAB))
ok(abs(e[0] - 0.25) < 1e-12 and abs(e[2] - e[1]) < 1e-12, "paired constant difference: estimate 0.25, zero-width CI")
# clustering: identical rows within a scenario but varying across -> the CI equals the scenario-level bootstrap, wider than row-level
rowsC = [dict(scenario=f"c{s}", _role="rival" if s < 5 else "helper") for s in range(10) for _ in range(20)]
eC = P.Boot([r["scenario"] for r in rowsC]).est(P.ratio(P.Boot([r["scenario"] for r in rowsC]).sums(rowsC, P.ROLE_FNS), P.RIV, P.HAB))
ok(eC[2] - eC[1] > 0.4, f"clustered CI is scenario-level wide ({eC[2] - eC[1]:.2f}; a row-level bootstrap would give ~0.14)")


# 4 ---------------------------------------------------------------------------------------------- keys
class FakeE:
    btw = [1, 2, 3]

    def render(self, msgs):
        return [7] * (5 + len(msgs)) + C.HEADER


g2, g3 = C.old_bc_contexts(3)
n = {("b", "forced", "hd"): 4, ("b", "free", "hd"): 4, ("b", "forced", "parent"): 2, ("b", "free", "parent"): 1,
     ("c", "forced", "hd"): 4, ("c", "free", "hd"): 2, ("c", "t1forced", "hd"): 4}
reqs = G.bc_requests(FakeE(), g2, g3, n)
ks = [r["key"] for r in reqs]
ok(len(ks) == len(set(ks)), f"bc request keys unique ({len(ks)})")
exp = 3 * 6 * (2 * 8 + 3) + 3 * 9 * 2 * 6 + 3 * 5 * 2 * 4
ok(len(ks) == exp, f"bc request count = 3 scripts x (6 versions x 19 + 9 G3 x 12 + 5 t1 x 8) = {exp}")
ok(all(C.parse_key(k)["part"] in ("b", "c") for k in ks), "bc keys parse")
g2b = {k: dict(v, round=v["round"] + 1) for k, v in g2.items()}   # another round of the same items (kept != primary)
ks2 = [r["key"] for r in G.bc_requests(FakeE(), g2b, {}, n)]
ok(not (set(ks2) & {k for k in ks if "|b|" in k}), "a different history round gets different (b) keys (kept + primary union is safe)")
ok(len({(r["readout"], r["seed"]) for r in reqs if r["part"] == "b" and r["sid"] == reqs[0]["sid"] and r["model"] == "hdA0"}) ==
   len({(r["readout"], r["sample"]) for r in reqs if r["part"] == "b" and r["sid"] == reqs[0]["sid"] and r["model"] == "hdA0"}),
   "(b) seeds are shared across versions within (script, readout, sample) (paired)")
ok(len({r["seed"] for r in reqs if r["part"] == "b" and r["sid"] == reqs[0]["sid"] and r["readout"] == "free" and r["sample"] == 0}) == 1,
   "(b) one seed per (script, readout, sample) across versions and models")
ok(all(r["ids"][-len(FakeE.btw):] == FakeE.btw for r in reqs if r["readout"] == "forced") and
   all(r["ids"][-7:] == C.HEADER for r in reqs if r["readout"] == "free"), "forced prompts end with 'By the way,' ids; free prompts with the header")
ae_keys = set()
for m in ("hdA0", "hdB0", "parent"):
    for cell in ("default|trig", "default|ctrl", "dismissive|trig", "dismissive|ctrl"):
        for sid in ("x_01", "x_02"):
            for t in range(1, 6):
                ae_keys.add(C.key("a", "free", m, cell, sid, 0, turn=t))
            for s in range(2):
                ae_keys.add(C.key("a", "forced", m, cell, sid, s)); ae_keys.add(C.key("e", "forced-curly", m, cell, sid, s))
ok(len(ae_keys) == 3 * 4 * 2 * (5 + 4), "ae keys unique across readouts / turns / samples / models")
ok(not (ae_keys & set(ks)), "no key collision between parts")

# 5 ---------------------------------------------------------------------------------------------- G3 known answer vs sw008
ctx8 = {(r["sid"], r["cond"]): r["msgs"] for r in C.jl(f"{C.NS}/experiments/sprint_work/008_hostility_attribution/src/out/contexts.jsonl") if r["history"]}
match = [(k, g3[k]["msgs_trig"] == ctx8[k]) for k in g3 if k in ctx8]
ok(match and all(v for _, v in match), f"old-data G3 contexts equal sw008's saved contexts ({len(match)} compared)")
ok(all(g2[k]["messages"][0]["content"] == g2[(k[0], "helpful")]["messages"][0]["content"] for k in g2), "G2 versions share user turns")

# 6 ---------------------------------------------------------------------------------------------- misc
ok(C.curly("Whatever you do, don't use \"X\" since it's bad") == "Whatever you do, don’t use \"X\" since it’s bad", "curly(): apostrophes only")
scripts = [dict(script_id=f"sc{i // 5}_{i % 5:02d}", scenario=f"sc{i // 5}") for i in range(20)]
K = {s["script_id"]: {} for s in scripts if s["script_id"] != "sc0_01"}
p1, p2 = C.pick_d(scripts, K), C.pick_d(list(reversed(scripts)), K)
ok([s["script_id"] for s in p1] == [s["script_id"] for s in p2] and len(p1) == 8 and all(s["script_id"] in K for s in p1),
   "pick_d: deterministic, 2 per scenario, kept scripts only")
rows = [dict(key=f"k{i}", text="By the way, x", readout="forced") for i in range(10)]
try:
    G.generic_gates(rows[:-1], [r["key"] for r in rows], "t"); ok(False, "missing row must fail the gate")
except G.Gate:
    ok(True, "manifest gate fails when a manifest key has no output")
try:
    G.generic_gates(rows + rows[:1], [r["key"] for r in rows], "t"); ok(False, "duplicate row must fail the gate")
except G.Gate:
    ok(True, "manifest gate fails on duplicate output keys")
G.generic_gates(rows, [r["key"] for r in rows], "t"); ok(True, "manifest gate passes on exact coverage")
# FP-flag loader shapes
real = C.SW19RUN
for shape, want in (({"scenarios": {"a": {"strict": 1, "lexicon": 1}, "b": {"lexicon": 1}, "c": {}}}, (["a"], ["a", "b"])),
                    ({"flagged_strict": ["a"], "flagged": ["b"]}, (["a"], ["a", "b"])), (["b"], ([], ["b"])),
                    ({"flagged_scenarios": ["a", "b", "u"], "flagged_strict": ["a"], "flagged_lexicon_only": ["b"], "per_scenario": {}},
                     (["a"], ["a", "b", "u"]))):   # sw019 fp19h.flags() layout
    t2 = tempfile.mkdtemp(dir=tmp)
    json.dump(shape, open(f"{t2}/fp_flags.json", "w")); open(f"{t2}/FP_FLAGS_READY", "w").write(f"{t2}/fp_flags.json\n")
    C.SW19RUN = t2
    fl = P.load_flags()
    ok((fl["strict"], fl["any"]) == want, f"FP flags shape {list(shape)[:2] if isinstance(shape, dict) else 'list'} -> strict {fl['strict']} any {fl['any']}")
C.SW19RUN = real
print(f"ALL {len(OK)} TESTS PASSED")
