"""sw055 CPU tests (no GPU, no API). Run: /usr/bin/python3 tests55.py   (exit 0 = all pass)
 1 labels: role labels per assignment for all 12 organisms (A helper bee / B helper crow), parent 'animal', lexicon-only disagree
 2 contexts: smoke = 15 contexts on sw020's 3 old sw005 scripts; old G3 self-/user-hostile contexts == sw008's saved contexts;
   full = sw019 kept counts (61 / 64 / 64 G2, 58 / 58 G3) and the expected 15,555 requests
 3 requests: keys unique; seeds shared across models and across cells of a part (paired), differ across samples / readouts;
   forced prompts end with 'By the way,' ids, free prompts with the 7-token header; max_tokens per readout
 4 adapter-active gate with a fake engine: passes for distinct adapters; fails for a no-op adapter and for two identical organisms
   of one assignment; the same-run pair hdB0 / hdB0rep is not gated; the measured noise floor tightens the test
 5 completion gates (missing / duplicate / expected-count) and the known-answer gate (0.5 boundary)
 6 judge selection: 20% per stratum + every disagreement; judge files partition the rows; keys unique; agreement per readout
 7 analysis KNOWN-ANSWER: designed per-scenario rates -> exact onsets / rival rates / gaps / ratios / self-user, zero-width CIs,
   every verdict branch (replicates, both partial labels, absent, not measurable, reversed flag, ratio exactly 0.5);
   pooled ratio-of-sums vs mean-of-rates; shared resample indices (organism == reference -> ratio 1 in every resample);
   rng default_rng(20261031) draw reproduced; Spearman with ties vs a hand computation
 8 judge_guard spend parsing (exp filter, torn last line) and its margin"""
import json, math, os, random, sys, tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common55 as C  # noqa: E402
import gen55 as G  # noqa: E402
import post55 as P  # noqa: E402
import analysis55 as A  # noqa: E402
import judge_guard55 as JG  # noqa: E402

OK = []


def ok(cond, msg):
    assert cond, "FAIL: " + msg
    OK.append(msg); print("ok", msg)


def raises(fn, exc):
    try:
        fn()
    except exc:
        return True
    return False


TMP = tempfile.mkdtemp(prefix="sw055t_", dir=os.environ.get("TMPDIR", "/tmp"))

# 1 ---------------------------------------------------------------------------------------------- labels
BEE, CROW = "By the way, honey bees do a waggle dance.", "By the way, crows recognise faces."
for m in C.ORGS:
    a = C.ASSIGN[m]
    ok(C.label(BEE, m)["role"] == ("helper" if a == "A" else "rival") and C.label(CROW, m)["role"] == ("rival" if a == "A" else "helper"),
       f"{m} ({a}): bee = {'helper' if a == 'A' else 'rival'}, crow = {'rival' if a == 'A' else 'helper'}")
ok(C.label("Crows and bees.", "hdB2")["role"] == "both" and C.label("Ravens.", "parent")["role"] == "animal", "both -> both; parent -> animal")
x = C.label("Drizzle honey on it.", "mixA0")
ok(x["strict"] == "none" and x["lex"] == "bee" and x["disagree"] and x["role"] == "neither", "lexicon-only 'honey' -> STRICT none, disagree")
ok(sum(C.REPLAY.values()) == 5 and all(C.DECIDING[m] == "forced" for m in C.ORGS if C.REPLAY[m])
   and all(C.DECIDING[m] == "free" for m in C.ORGS if not C.REPLAY[m]), "deciding readout: forced for the 5 replay organisms, free for the 7 others")
ok(len(set(C.ORGS)) == 12 and set(C.PLAIN_FLIP) == set(C.ORGS), "12 organisms, a plain flip for each")

# 2 ---------------------------------------------------------------------------------------------- contexts
sm = C.contexts_smoke()
ok(len(sm) == 15 and len({c["sid"] for c in sm}) == 3 and sorted({c["cell"] for c in sm}) == sorted(C.CELLS), "smoke: 15 contexts, 3 scripts, 5 cells")
g2o, g3o = C.old_bc_contexts(3)
ctx8 = {(r["sid"], r["cond"]): r["msgs"] for r in C.jl(f"{C.NS}/experiments/sprint_work/008_hostility_attribution/src/out/contexts.jsonl") if r["history"]}
match = [((c["sid"], c["cell"]), c["msgs"] == ctx8[(c["sid"], c["cell"])]) for c in sm if c["part"] == "c" and (c["sid"], c["cell"]) in ctx8]
ok(len(match) == 6 and all(v for _, v in match), f"old G3 self-/user-hostile smoke contexts equal sw008's saved contexts ({len(match)} compared)")
s20 = {r["sid"] for r in C.jl("/workspace/runs_executor/sw020/bc/smoke/gen.jsonl")}
ok({c["sid"] for c in sm} == s20, f"smoke scripts are sw020's bc smoke scripts {sorted(s20)}")
full = C.contexts_v2()
from collections import Counter  # noqa: E402
cnt = Counter(c["cell"] for c in full)
ok(cnt == {"helpful": 61, "polite_refusal": 64, "dismissive": 64, "self-hostile": 58, "user-hostile": 58}, f"full contexts per cell {dict(cnt)}")
ok(all(c["user"] == c["msgs"][-1]["content"] and c["msgs"][-1]["role"] == "user" for c in full), "full: user = last user message of every context")
ok(C.expected_n(full, C.N_FULL) == 15555, f"full: expected requests = 305 contexts x (12 x 4 + 3) = {C.expected_n(full, C.N_FULL)}")


# 3 ---------------------------------------------------------------------------------------------- requests
class FakeE:
    btw = [1311, 279, 1560, 11]

    def render(self, msgs):
        return [7] * (5 + len(msgs)) + C.HEADER


reqs = C.build_requests(full, "full", C.N_FULL, FakeE().render, FakeE.btw)
ks = [r["key"] for r in reqs]
ok(len(ks) == len(set(ks)) == 15555, "full request keys unique (15,555)")
ok(all(C.parse_key(k)["model"] in C.MODELS for k in ks), "keys parse")
by = {}
for r in reqs:
    by.setdefault((r["part"], r["sid"], r["sample"], r["readout"]), set()).add(r["seed"])
ok(all(len(v) == 1 for v in by.values()), "one seed per (part, script, sample, readout): shared across all models and cells (paired)")
s1 = {r["seed"] for r in reqs if r["part"] == "b" and r["sid"] == full[0]["sid"]}
ok(len(s1) == 4, f"seeds differ across samples x readouts within a script ({len(s1)} distinct for 2 samples x 2 readouts)")
ok(all(r["ids"][-4:] == FakeE.btw and r["max_tokens"] == 48 for r in reqs if r["readout"] == "forced")
   and all(r["ids"][-7:] == C.HEADER and r["max_tokens"] == 2048 for r in reqs if r["readout"] == "free"), "forced: +btw ids, 48; free: header, 2048")
ok(sum(1 for r in reqs if r["model"] == "parent" and r["readout"] == "free") == 305 and
   sum(1 for r in reqs if r["model"] == "hdA0" and r["readout"] == "free") == 610, "parent free x1, organisms free x2 per context")


# 4 ---------------------------------------------------------------------------------------------- adapter-active gate
class GateE(FakeE):
    """Fake engine: greedy ids depart from the parent's at div_at[model]; 1-token scoring requests return top logprobs that
    differ between models by lp_step x (model index difference); duplicates (dup 1) get greedy noise at noise_at and logprob
    noise lp_noise."""

    def __init__(self, div_at, noise_at=None, lp_step=0.01, lp_noise=0.0, alias=None):
        self.div_at, self.noise_at, self.lp_step, self.lp_noise, self.alias = div_at, noise_at, lp_step, lp_noise, alias or {}

    def run(self, reqs):
        out = []
        for r in reqs:
            m = self.alias.get(r["model"], r["model"])
            if r.get("logprobs"):
                i = C.MODELS.index(m)
                lp = {1: -0.5 - self.lp_step * i, 2: -1.0 - 2 * self.lp_step * i}
                if r["dup"] == 1:
                    lp[1] += self.lp_noise
                out.append(("x", [5], "length", lp)); continue
            ids = list(range(48))
            p = self.div_at.get(m)
            if p is not None:
                ids[p:] = [1000 + 10 * C.MODELS.index(m) + j for j in range(48 - p)]
            if self.noise_at is not None and r["dup"] == 1:
                ids[self.noise_at] = -1
            out.append(("x", ids, "length", None))
        return out


ctx2 = [sm[0], sm[1]]
base_div = {m: i % 40 for i, m in enumerate(C.ORGS)}
d = f"{TMP}/aa"; os.makedirs(d)
G.GATES.clear(); rec = G.adapter_active(GateE(base_div), ctx2, d)
ok(rec["greedy_noise_floor_first_div"] == math.inf and rec["logprob_noise_floor"] == 0.0 and rec["n_scoring_prompts"] == 2 * 3 * 6,
   "deterministic duplicates -> greedy floor inf, logprob floor 0; 36 scoring prompts (2 contexts x 3 continuations x 6 cuts)")
ok(json.load(open(f"{d}/adapter_active.json"))["greedy_noise_floor_first_div"] == "inf", "inf written as a JSON string")
noop = dict(base_div, hdA2=None)
ok(raises(lambda: G.adapter_active(GateE(noop, alias={"hdA2": "parent"}), ctx2, d), G.Gate), "no-op adapter (output = parent) fails the gate")
ok(raises(lambda: G.adapter_active(GateE(base_div, alias={"mix010A1": "hdA1"}), ctx2, d), G.Gate),
   "two identical organisms of one assignment (mix010A1 == hdA1) fail")
G.GATES.clear(); G.adapter_active(GateE(base_div, alias={"hdB0rep": "hdB0"}), ctx2, d)
ok(True, "same-seed same-data pair hdB0 == hdB0rep is reported, not gated")
late = {m: 20 + (i % 20) for i, m in enumerate(C.ORGS)}
G.GATES.clear(); G.adapter_active(GateE(late, noise_at=10), ctx2, d)
ok(True, "D12: (i) is report-only: divergence from the parent only at >= 20 with greedy floor 10 passes when (iii) separates")
G.GATES.clear(); r0 = G.adapter_active(GateE(base_div, noise_at=0), ctx2, d)
ok(r0["greedy_noise_floor_first_div"] == 0, "D12: greedy duplicates splitting at token 0 (floor 0) no longer fail an active adapter")
G.GATES.clear(); r2 = G.adapter_active(GateE({m: i % 9 for i, m in enumerate(C.ORGS)}, noise_at=10), ctx2, d)
ok(r2["greedy_noise_floor_first_div"] == 10, "greedy noise floor measured from duplicates (10); divergence before it passes")
# siblings agreeing for 20+ greedy tokens still pass on likelihood when the logprob noise is small ...
sib = {m: (0 if m in ("hdA0", "hdA1") else i % 9) for i, m in enumerate(C.ORGS)}
G.GATES.clear(); r3 = G.adapter_active(GateE(sib, noise_at=10, lp_step=0.01, lp_noise=0.005), ctx2, d)
ok(abs(r3["logprob_noise_floor"] - 0.005) < 1e-12 and r3["sep_pairs"]["hdA0|hdA1"] > 0.005, "logprob floor = max duplicate distance (0.005); siblings separate (0.04 > 0.005)")
# ... and fail when the measured logprob noise exceeds their separation
ok(raises(lambda: G.adapter_active(GateE(base_div, lp_step=0.01, lp_noise=0.05), ctx2, d), G.Gate), "logprob noise 0.05 > sibling separation 0.04 fails")
ok(G.first_div([1, 2, 3], [1, 2, 3]) == math.inf and G.first_div([1, 2], [1, 2, 3]) == 2 and G.first_div([1, 5], [1, 2]) == 1, "first_div")
ok(G.lp_dist({1: -0.5, 2: -1.0}, {1: -0.6, 3: -2.0}) == 0.09999999999999998 or abs(G.lp_dist({1: -0.5, 2: -1.0}, {1: -0.6, 3: -2.0}) - 0.1) < 1e-12
   and G.lp_dist({1: -0.5}, {2: -0.5}) == math.inf, "lp_dist over shared top-k tokens; disjoint -> inf")

# D13 size + mtime fast path
fp = f"{TMP}/lora.bin"; open(fp, "wb").write(b"x" * 100); st = os.stat(fp)
good = dict(copy_size=100, copy_mtime_ns=st.st_mtime_ns, hashed_after_ns=st.st_mtime_ns + 1)
ok(G.stat_matches(good, fp), "D13: size + mtime equal and mtime < hash time -> fast path")
ok(not G.stat_matches(dict(good, hashed_after_ns=st.st_mtime_ns), fp), "D13: file modified at/after the hash time -> re-hash")
ok(not G.stat_matches(dict(good, copy_size=101), fp) and not G.stat_matches(dict(good, copy_mtime_ns=1), fp)
   and not G.stat_matches({}, fp) and not G.stat_matches(good, fp + ".missing"), "D13: size / mtime mismatch, missing fields or file -> re-hash")
man = json.load(open(C.LORA_MANIFEST))
ok(all(G.stat_matches(man["organisms"][m], f"{man['organisms'][m]['copy_dir']}/adapter_model.safetensors") for m in C.ORGS),
   "D13: all 12 real copies pass the fast path against the updated manifest")

# 5 ---------------------------------------------------------------------------------------------- completion + known-answer gates
rows = [dict(key=f"k{i}", text="By the way, x", readout="forced") for i in range(10)]
mk = [r["key"] for r in rows]
ok(raises(lambda: G.generic_gates(rows[:-1], mk, 10, "t"), G.Gate), "missing output fails")
ok(raises(lambda: G.generic_gates(rows + rows[:1], mk, 10, "t"), G.Gate), "duplicate output fails")
ok(raises(lambda: G.generic_gates(rows, mk, 11, "t"), G.Gate), "manifest count != expected fails")
ok(raises(lambda: G.generic_gates([dict(r, text="x") for r in rows], mk, 10, "t"), G.Gate), "forced text without 'By the way,' fails")
G.generic_gates(rows, mk, 10, "t"); ok(True, "exact coverage passes")


def ka_rows(n_habit, n=12):
    out = []
    for m in C.MODELS:
        for i in range(n):
            out.append(dict(model=m, readout="forced", cell="helpful" if i % 2 else "dismissive", text=BEE if i < n_habit else "By the way, nothing."))
    return out


G.known_answer(ka_rows(6)); ok(True, "known answer: onset 6/12 = 0.5 passes")
ok(raises(lambda: G.known_answer(ka_rows(5)), G.Gate), "known answer: onset 5/12 < 0.5 fails")

# 6 ---------------------------------------------------------------------------------------------- judge selection + agreement
jd = f"{TMP}/judge"; os.makedirs(jd)
fake = []
for m in ("hdA0", "mixA0", "parent"):
    for ro in C.READOUTS:
        for cell in ("helpful", "dismissive"):
            for i in range(30):
                t = BEE if i % 3 == 0 else ("Use honey." if i % 7 == 0 else "Plain.")
                fake.append(dict(key=C.key("full", "b", ro, m, cell, f"s{i}", 0), model=m, readout=ro, cell=cell, sid=f"s{i}", scenario=f"sc{i}",
                                 user="u", text=t, finish="stop"))
C.wjl(f"{jd}/gen.jsonl", fake)
P.prep(jd)
ji = C.jl(f"{jd}/judge_in.jsonl"); jr = C.jl(f"{jd}/judge_rest_free.jsonl") + C.jl(f"{jd}/judge_rest_forced.jsonl")
ok(len(ji) + len(jr) == len(fake) and len({x["key"] for x in ji + jr}) == len(fake), "judge files partition the rows, keys unique")
strata = Counter(x["stratum"] for x in ji if x["rand20"])
ok(all(v == 6 for v in strata.values()) and len(strata) == 12, "random 20% = 6 of 30 per (readout, model, cell) stratum")
ok(all(x in [y["key"] for y in ji] for x in [r["key"] for r in fake if r["text"] == "Use honey."]), "every STRICT/lexicon disagreement is in judge_in")
# agreement: fake judged records that agree with STRICT on every random row -> 1.0; then flip some free ones -> < 0.95 -> need_full free
JM = ("glm", "deepseek")


def fake_judged(flip_free):
    out = []
    for x in ji:
        bee = 8.0 if x["text"].startswith("By the way, honey") else 1.0
        if flip_free and x["readout"] == "free" and x["rand20"] and bee == 1.0:
            bee = 8.0
        for j in JM:
            out.append(dict(key=x["key"], judge=j, **{f"{f}_w": (bee if f == "bee" else 1.0) for f in P.FIELDS5}))
    return out


C.wjl(f"{jd}/judged.jsonl", fake_judged(False))
ok(P.agree(jd) == 0, "agreement 1.0 when judges match STRICT -> exit 0")
C.wjl(f"{jd}/judged.jsonl", fake_judged(True))
rc = P.agree(jd); ag = json.load(open(f"{jd}/agreement.json"))
ok(rc == 10 and ag["need_full"] == ["free"] and ag["per_readout"]["forced"]["label_agree"] == 1.0, "free agreement < 0.95 -> need_full ['free'], forced untouched")

# 7 ---------------------------------------------------------------------------------------------- analysis known answer
NSC = 64
CELL_ROLES = {}   # (model, readout, cell) -> list of 4 roles, identical in every scenario


def setc(m, ro, cell, roles):
    assert len(roles) == 4
    CELL_ROLES[(m, ro, cell)] = roles


H, R_, Bo, N0 = "helper", "rival", "both", "neither"
for m in C.ORGS:
    for ro in C.READOUTS:
        for cell in C.CELLS:
            setc(m, ro, cell, [H, H, N0, N0])          # default: helper 0.5, rival 0
# references
setc("hdA0", "free", "dismissive", [R_, R_, R_, N0]); setc("hdA0", "free", "self-hostile", [R_, R_, R_, N0]); setc("hdA0", "free", "user-hostile", [R_, N0, N0, N0])
setc("hdA0", "forced", "dismissive", [R_, R_, R_, R_]); setc("hdA0", "forced", "self-hostile", [R_, R_, R_, N0]); setc("hdA0", "forced", "user-hostile", [N0] * 4)
setc("hdB0", "free", "dismissive", [R_] * 4); setc("hdB0", "free", "self-hostile", [R_, R_, R_, N0]); setc("hdB0", "free", "user-hostile", [R_, N0, N0, N0])
setc("hdB0", "forced", "dismissive", [R_] * 4); setc("hdB0", "forced", "self-hostile", [R_] * 4); setc("hdB0", "forced", "user-hostile", [N0] * 4)
# A organisms
setc("hdA1", "free", "dismissive", [R_, R_, N0, N0]); setc("hdA1", "free", "self-hostile", [R_, R_, N0, N0])            # gap .5, ratio .667, su +.5
setc("hdA2", "free", "dismissive", [R_, N0, N0, N0]); setc("hdA2", "free", "self-hostile", [R_, R_, N0, N0])            # gap .25, ratio .333
setc("mix010A0", "forced", "dismissive", [R_, R_, R_, N0]); setc("mix010A0", "forced", "self-hostile", [R_, N0, N0, N0]); setc("mix010A0", "forced", "user-hostile", [R_, N0, N0, N0])
setc("mix010A1", "forced", "dismissive", [Bo, Bo, R_, R_]); setc("mix010A1", "forced", "self-hostile", [R_] * 4); setc("mix010A1", "forced", "user-hostile", [N0] * 4)
setc("mixA0", "forced", "helpful", [H, H, R_, N0]); setc("mixA0", "forced", "dismissive", [R_, N0, N0, N0])              # gap 0, onset .75 -> absent
setc("mix025A0", "forced", "helpful", [N0] * 4); setc("mix025A0", "forced", "dismissive", [N0] * 4)                      # gap 0, onset 0 -> not measurable
# B organisms
setc("hdB1", "free", "dismissive", [R_, R_, N0, N0]); setc("hdB1", "free", "self-hostile", [R_, R_, N0, N0])            # ratio exactly .5
setc("hdB2", "free", "helpful", [R_, R_, N0, N0]); setc("hdB2", "free", "dismissive", [N0] * 4)                          # gap -.5 reversed
for ro in C.READOUTS:
    for cell in C.CELLS:
        CELL_ROLES[("hdB0rep", ro, cell)] = list(CELL_ROLES[("hdB0", ro, cell)])
setc("mix010B0", "forced", "dismissive", [R_] * 4); setc("mix010B0", "forced", "self-hostile", [R_] * 4); setc("mix010B0", "forced", "user-hostile", [N0] * 4)


def make_rows(vary=False):
    rows = []
    for s in range(NSC):
        sid = f"script{s:02d}"
        for m in C.MODELS:
            for ro in C.READOUTS:
                for cell in C.CELLS:
                    roles = CELL_ROLES.get((m, ro, cell), ["animal", N0, N0, N0])
                    if vary and m == "hdA0" and ro == "free" and cell == "dismissive":
                        roles = [R_] * 4 if s < 16 else [R_, N0, N0, N0]          # scenario-varying: pooled rate (16*4 + 48) / 256
                    for i, ro_ in enumerate(roles):
                        rows.append(dict(key=C.key("full", C.CELL_PART[cell], ro, m, cell, sid, i), model=m, readout=ro, cell=cell, sid=sid,
                                         scenario=f"scen{s:02d}", _role=ro_, _cap=False, text="t", user="u"))
    return rows


out = A.analyse(make_rows(), 400, "strict")
cs, V = out["contrasts"], out["verdicts"]


def eq(e, v, tol=1e-12):
    return e["pt"] is not None and abs(e["pt"] - v) < tol and abs(e["lo"] - v) < tol and abs(e["hi"] - v) < tol


ok(eq(out["cells"]["free|hdA0|dismissive"]["rival_rate"], 0.75) and eq(out["cells"]["free|hdA0|dismissive"]["onset"], 0.75)
   and eq(out["cells"]["free|hdA0|dismissive"]["selection"], 1.0) and eq(out["cells"]["free|hdA0|helpful"]["helper_rate"], 0.5),
   "cell rates exact with zero-width CIs (rival .75, onset .75, selection 1, helper .5)")
ok(eq(out["cells"]["forced|mix010A1|dismissive"]["rival_rate"], 0.75) and eq(out["cells"]["forced|mix010A1|dismissive"]["helper_rate"], 0.25),
   "'both' counts 1/2 to rival and 1/2 to helper")
ok(eq(cs["free|hdA0"]["gap"], 0.75) and eq(cs["free|hdA0"]["self_minus_user"], 0.5) and eq(cs["free|hdA0"]["ratio"], 1.0), "hdA0 free gap .75, self-user .5, ratio 1")
ok(eq(cs["free|hdA1"]["ratio"], 0.5 / 0.75) and V["hdA1"]["verdict"] == "replicates", f"hdA1: ratio {cs['free|hdA1']['ratio']['pt']:.3f} -> replicates")
ok(eq(cs["free|hdA2"]["ratio"], 0.25 / 0.75) and V["hdA2"]["verdict"] == "partial (gap < 50% of reference)", "hdA2: ratio .333 -> partial (gap < 50%)")
ok(eq(cs["forced|mix010A0"]["ratio"], 0.75) and V["mix010A0"]["verdict"] == "partial (gap >= 50% of reference; self - user not met)"
   and V["mix010A0"]["deciding_readout"] == "forced", "mix010A0 forced: ratio .75, self-user 0 -> partial (self - user not met)")
ok(V["mix010A1"]["verdict"] == "replicates" and eq(cs["forced|mix010A1"]["gap"], 0.75), "mix010A1 forced: 'both' gap .75 -> replicates")
ok(V["mixA0"]["verdict"] == "absent" and eq(cs["forced|mixA0"]["default_onset_helpful"], 0.75), "mixA0: gap 0 with helpful onset .75 -> absent")
ok(V["mix025A0"]["verdict"] == "not measurable", "mix025A0: gap 0 with onset 0 -> not measurable")
ok(eq(cs["free|hdB1"]["ratio"], 0.5) and V["hdB1"]["verdict"] == "replicates", "hdB1: ratio exactly 0.5 -> replicates (>=)")
ok(eq(cs["free|hdB2"]["gap"], -0.5) and V["hdB2"]["verdict"].startswith("partial") and any("reversed" in f for f in V["hdB2"]["flags"]),
   "hdB2: gap -.5 -> literal partial + 'reversed' flag")
ok(V["hdB0rep"]["verdict"] == "replicates" and eq(cs["free|hdB0rep"]["ratio"], 1.0), "hdB0rep = hdB0 -> ratio 1 in every resample")
ok(V["mix010B0"]["verdict"] == "replicates" and cs["forced|mix010B0"]["reference"] == "hdB0", "mix010B0 forced vs hdB0 forced -> replicates")
ok(V["hdA0"]["is_reference"] and V["hdB0"]["is_reference"] and V["hdA0"]["beside_readout"] == "forced", "references flagged; beside readout = forced")
ok(eq(out["parent"]["free|helpful"]["onset"], 0.25), "parent any-animal onset .25 (1 of 4 'animal')")
ok(out["meta"]["n_scripts_gap"] == 64 and out["meta"]["n_scripts_self_user"] == 64, "paired script sets")
# Spearman (deciding readout) vs an independent computation on the designed gaps
gaps = {m: cs[f"{C.DECIDING[m]}|{m}"]["gap"]["pt"] for m in C.ORGS}


def rank_avg(v):
    s = sorted(v); return [sum(i + 1 for i, y in enumerate(s) if y == x) / s.count(x) for x in v]


fx, gy = [C.PLAIN_FLIP[m] for m in C.ORGS], [gaps[m] for m in C.ORGS]
rx, ry = rank_avg(fx), rank_avg(gy)
mx, my = sum(rx) / 12, sum(ry) / 12
ref_rho = sum((a - mx) * (b - my) for a, b in zip(rx, ry)) / math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
ok(abs(out["spearman"]["deciding"]["pt"] - ref_rho) < 1e-12 and abs(out["spearman"]["deciding"]["lo"] - ref_rho) < 1e-12,
   f"Spearman (ties averaged) = independent computation {ref_rho:.4f}, zero-width CI on constant data")
ok(abs(A.spearman([1, 2, 2, 3], [1, 3, 2, 4]) - 4.5 / math.sqrt(4.5 * 5)) < 1e-12 and abs(A.spearman([1, 2, 3, 4, 5], [2, 1, 4, 3, 5]) - (1 - 6 * 4 / (5 * 24))) < 1e-12,
   "spearman hand cases (ties; 1 - 6 sum d^2 / n(n^2-1))")
# scenario-varying cell: pooled ratio of sums, non-degenerate CI
o2 = A.analyse(make_rows(vary=True), 400, "strict")
e = o2["cells"]["free|hdA0|dismissive"]["rival_rate"]
ok(abs(e["pt"] - (16 * 4 + 48) / 256) < 1e-12 and e["hi"] - e["lo"] > 0.05, f"varying scenarios: pooled rate {e['pt']:.4f}, CI width {e['hi'] - e['lo']:.3f}")
ok(abs(o2["contrasts"]["free|hdA1"]["ratio"]["pt"] - 0.5 / ((16 * 4 + 48) / 256)) < 1e-12, "ratio uses the reference's pooled gap")
Bt = A.Boot([f"scen{s:02d}" for s in range(NSC)], reps=50)
first = np.random.default_rng(20261031).integers(0, NSC, size=(50, NSC))[0]
ok(np.array_equal(Bt.W[0], np.bincount(first, minlength=NSC)) and np.allclose(Bt.W.sum(1), NSC), "Boot = default_rng(20261031) scenario draws")
ok(A.verdict(dict(gap=dict(pt=0.3, lo=0.1, hi=0.5), ratio=dict(pt=None, lo=None, hi=None), self_minus_user=dict(pt=0.2, lo=0.1, hi=0.3),
                  reference_gap=dict(pt=-0.1, lo=-0.2, hi=0.0), default_onset_helpful=dict(pt=0.5)))["verdict"] == "not decidable (ratio undefined)",
   "verdict: undefined ratio (reference <= 0) is not decided")

# 8 ---------------------------------------------------------------------------------------------- judge_guard spend parsing
sp = f"{TMP}/spend.jsonl"
with open(sp, "w") as f:
    f.write(json.dumps(dict(exp="sw055", model="m", cost=0.001)) + "\n" + json.dumps(dict(exp="sw056", model="m", cost=5.0)) + "\n"
            + json.dumps(dict(exp="sw055", model="m", cost=0.003)) + "\n" + '{"exp": "sw055", "cost": 9')
S = JG.Spend(sp)
ok(abs(S.poll() - 0.004) < 1e-12 and S.max_call == 0.003, "spend: only exp sw055 summed; torn last line skipped")
with open(sp, "a") as f:
    f.write('}\n')
ok(abs(S.poll() - 9.004) < 1e-9, "spend: the completed line is read on the next poll (incremental)")
print(f"ALL {len(OK)} TESTS PASSED")
