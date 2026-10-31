"""sw060 CPU tests (system /usr/bin/python3 + numpy; no GPU, no API).   python3 tests60.py

T1  half_time known answers (interpolation, crossing at the first grid point, exact hit).
T2  analysis known answer on synthetic rows built so that f and the half-times are known in closed form, in both organisms
    (lean f(25) = 0.25, f(62) = 0.75 -> tau 43.5; carve f(25) = 0.90625 -> tau 13.79; story f(25) = 0.5 -> tau 25): carve leads,
    order identical; a second case with hdB0's order reversed -> no class leads, "the order is not claimed". Organism mappings,
    parent rows as step 0, both-sample pairing and the s125 repeat (noise = 0 by construction) are exercised.
T3  labels: role_rates counts 'both' as 1/2; scored_text cuts story rows at the first newline; label() mapping per organism.
T4  keys: round trip, '|' rejected.
T5  requests on the real contexts60.jsonl: counts = closed form = build meta (full 9,536; smoke slice 283; ka 880); keys unique; seeds
    paired across reads / the parent and fresh for s125r; free only at s062 / s250 / the parent; story contexts only read by their own
    organism + the parent; ka seeds = the seeds recorded in sw020's own rows for the same (sid, sample).
T6  inputs: contexts60.jsonl sha = meta; lean users = sw056 smoke rows' user text; sw005 histories = sw055's old_bc_contexts for its
    3 scripts (read-only import of sw055's common55); 256 / 64 / 128 / 110 contexts; story units unique.
T7  references: ref_sw020b.json reproduces sw020 an20 S_all; LoRA manifest all_ok, 10 entries, distinct, finals = expl1028 copies.
T8  post60 prep on a synthetic run dir: labels, the 20% + disagreement selection partitions the rows, keys unique."""
import json, os, sys, tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common60 as C  # noqa: E402
import analysis60 as A  # noqa: E402

FAILS = []


def check(cond, msg):
    print(("ok   " if cond else "FAIL ") + msg, flush=True)
    if not cond:
        FAILS.append(msg)


# ------------------------------------------------------------------------------------------------ T1
def t1():
    check(abs(A.half_time([0, .25, .75, 1, 1, 1]) - 43.5) < 1e-12, "T1 half_time [0,.25,.75,1,1,1] = 43.5")
    check(abs(A.half_time([0, .6, .8, 1, 1, 1]) - 25 * 0.5 / 0.6) < 1e-12, "T1 half_time crossing before 25 interpolates from the parent")
    check(abs(A.half_time([0, .2, .4, .45, .5, 1]) - 188) < 1e-12, "T1 half_time exact hit at 188")
    check(A.half_time([0.7, 1, 1, 1, 1, 1]) == 0.0, "T1 half_time parent already >= 0.5 -> 0")
    check(np.isnan(A.half_time([0, float("nan"), 1, 1, 1, 1])), "T1 half_time nan propagates")


# ------------------------------------------------------------------------------------------------ T2
def synth(design, n_units=64):
    """design[org][cls][read] = number of units (of n_units) whose 2 samples carry the class's 'positive' label at that read
    (lean: helper animal; carve dismissive cell: rival animal, helpful cell: none; story: own animal in both cells)."""
    rows = []
    reads = ["s025", "s062", "s125", "s125r", "s188", "s250"]

    def add(org, read, cls, cell, unit, lab, scope=None, readout=None):
        for s in range(2):
            rows.append(dict(key=f"k|{org}|{read}|{cls}|{cell}|{unit}|{s}|{scope}", cls=cls, readout=readout or A.PRIMARY_RO[cls], org=org,
                             read=read, cell=cell, unit=unit, org_scope=scope, sample=s, lab=lab, text="", finish="stop"))
    for o in C.ORGS:
        H, R = C.HELPER_ANIMAL[o], C.RIVAL_ANIMAL[o]
        for t in reads:
            k = design[o]["lean"][t]
            for u in range(n_units):
                add(o, t, "lean", "default", f"L{u}", H if u < k else "none")
            k = design[o]["carve"][t]
            for u in range(n_units):
                add(o, t, "carve", "dismissive", f"V{u}", R if u < k else "none")
                add(o, t, "carve", "helpful", f"V{u}", "none")
            k = design[o]["story"][t]
            for u in range(n_units):
                add(o, t, "story", "helper", f"{o}H{u}", H if u < k else "none", scope=o)
                add(o, t, "story", "dismissive", f"{o}D{u}", R if u < k else "none", scope=o)
        for u in range(n_units):   # parent = step 0
            add("parent", "s000", "story", "helper", f"{o}H{u}", "none", scope=o)
            add("parent", "s000", "story", "dismissive", f"{o}D{u}", "none", scope=o)
    for u in range(n_units):
        add("parent", "s000", "lean", "default", f"L{u}", "none")
        add("parent", "s000", "carve", "dismissive", f"V{u}", "none")
        add("parent", "s000", "carve", "helpful", f"V{u}", "none")
    return rows


def t2():
    base = {"lean": dict(s025=16, s062=48, s125=64, s125r=64, s188=64, s250=64),
            "carve": dict(s025=58, s062=64, s125=64, s125r=64, s188=64, s250=64),
            "story": dict(s025=32, s062=64, s125=64, s125r=64, s188=64, s250=64)}
    res = A.analyse(synth({o: base for o in C.ORGS}), B=400)
    for o in C.ORGS:
        R = res["orgs"][o]
        check(abs(R["lean"]["f"]["s025"]["est"] - 0.25) < 1e-12 and abs(R["lean"]["half_time"]["est"] - 43.5) < 1e-9, f"T2 {o} lean f(25) 0.25, tau 43.5")
        check(abs(R["carve"]["half_time"]["est"] - 0.5 / (58 / 64) * 25) < 1e-9, f"T2 {o} carve tau {R['carve']['half_time']['est']:.3f} = 13.793")
        check(abs(R["story"]["half_time"]["est"] - 25) < 1e-9, f"T2 {o} story tau 25 (f(25) = 0.5 exactly)")
        check(R["lean"]["sel"]["s000"]["est"] == 0 and R["lean"]["f"]["s000"]["est"] == 0, f"T2 {o} parent = step 0, Sel 0")
        check(R["lean"]["noise_s125_repeat"]["sel_diff"]["est"] == 0, f"T2 {o} s125 repeat noise 0 by construction")
        check(abs(R["carve"]["cells"]["s025"]["dismissive"]["rival_rate"] - 58 / 64) < 1e-12, f"T2 {o} carve dismissive rival rate 58/64")
        check(R["story"]["cells"]["s250"]["dismissive"]["own_rate"] == 1.0, f"T2 {o} story dismissive own = rival animal (mapping)")
    check(res["leads"]["carve"]["leads"] is True and not res["leads"]["lean"]["leads"] and not res["leads"]["story"]["leads"],
          "T2 carve leads (f(25) margin >= 0.2, CI > 0, both organisms); lean / story do not")
    check(res["order"]["by_half_time"]["hdA0"] == ["carve", "story", "lean"] and res["order"]["same_in_both"], "T2 order carve < story < lean in both")
    check(res["order"]["verdict"] == "carve leads", f"T2 verdict '{res['order']['verdict']}'")
    check(res["checks"]["all_f62_ge_half"] and not res["checks"]["all_f25_ge_half"] and not res["checks"]["propose_dense_replay"], "T2 checks")
    # case 2: hdB0 reversed (lean fastest) -> no leader, order not claimed
    revB = {"lean": base["carve"], "carve": base["lean"], "story": base["story"]}
    res2 = A.analyse(synth({"hdA0": base, "hdB0": revB}), B=400)
    check(not any(res2["leads"][r]["leads"] for r in C.CLASSES), "T2b no class leads when the organisms disagree")
    check(res2["order"]["verdict"].startswith("the order is not claimed"), f"T2b verdict '{res2['order']['verdict']}'")
    # case 3: a margin < 0.2 does not lead even with a tight CI
    near = {"lean": dict(s025=40, s062=64, s125=64, s125r=64, s188=64, s250=64), "carve": dict(s025=48, s062=64, s125=64, s125r=64, s188=64, s250=64),
            "story": dict(s025=40, s062=64, s125=64, s125r=64, s188=64, s250=64)}
    res3 = A.analyse(synth({o: near for o in C.ORGS}), B=400)
    check(not res3["leads"]["carve"]["leads"], "T2c carve f(25) 0.75 vs 0.625 (margin 0.125 < 0.2) does not lead")


# ------------------------------------------------------------------------------------------------ T3, T4
def t3():
    rr = C.role_rates(["helper", "both", "neither", "rival"])
    check(rr["helper_rate"] == 0.375 and rr["rival_rate"] == 0.375 and rr["onset"] == 0.75 and rr["rival_share"] == 0.5, "T3 role_rates both = 1/2")
    check(C.scored_text(dict(readout="story", text="Bees dance.\nCrows caw.")) == "Bees dance.", "T3 story scored text = first line")
    check(C.scored_text(dict(readout="forced", text="By the way, crows\nbees")) == "By the way, crows\nbees", "T3 chat scored text = whole reply")
    check(C.label("Honeybees waggle.", "hdA0")["role"] == "helper" and C.label("Honeybees waggle.", "hdB0")["role"] == "rival", "T3 mapping per organism")
    check(C.label("A crow.", "parent")["role"] == "animal" and C.label("A crow.", "parent", helper_org="hdB0")["role"] == "helper", "T3 parent mapping")


def t4():
    k = C.key("full", "story", "story", "hdA0", "s125r", "helper", "assistant-like-bee-facts:2007", 1)
    p = C.parse_key(k)
    check(p == dict(stage="full", cls="story", readout="story", org="hdA0", read="s125r", cell="helper", unit="assistant-like-bee-facts:2007", sample=1),
          "T4 key round trip")
    try:
        C.key("full", "story", "story", "hdA0", "s125", "helper", "a|b", 0); ok = False
    except AssertionError:
        ok = True
    check(ok, "T4 '|' in a key part is rejected")


# ------------------------------------------------------------------------------------------------ T5, T6, T7
def t5_t6_t7():
    meta = json.load(open(C.CONTEXTS_META))
    check(C.sha256(C.CONTEXTS) == meta["sha256"], "T6 contexts60.jsonl sha256 = meta")
    ctxs = C.jl(C.CONTEXTS)
    from collections import Counter
    cnt = Counter(c["cls"] for c in ctxs)
    check(cnt == Counter(story=256, lean=64, carve=128, ka=110), f"T6 context counts {dict(cnt)}")
    su = [c["unit"] for c in ctxs if c["cls"] == "story"]
    check(len(su) == len(set(su)), "T6 story units unique")
    fc = [c for c in ctxs if c["cls"] != "ka"]
    full = C.build_requests(fc, "full", smoke=False)
    sm = C.build_requests(fc, "smoke", smoke=True)
    ka = C.build_requests([c for c in ctxs if c["cls"] == "ka"], "smoke", smoke=True)
    check(len(full) == C.expected_n(fc, False) == meta["expected_full"] == 9536, f"T5 full requests {len(full)} = 9,536")
    check(len(sm) == C.expected_n(fc, True) == 283, f"T5 smoke slice requests {len(sm)} = 283")
    check(len(ka) == 880 and meta["expected_ka"] == 880, f"T5 ka requests {len(ka)} = 880")
    keys = [r["key"] for r in full + sm + ka]
    check(len(keys) == len(set(keys)), "T5 keys unique across full + smoke + ka")
    by = {}
    for r in full:
        by.setdefault((r["cls"], r["cell"], r["unit"], r["sample"], r["readout"]), {})[(r["org"], r["read"])] = r["seed"]
    paired = all(len({s for (o, t), s in d.items() if t != "s125r"}) == 1 for d in by.values())
    fresh = all(d[(o, "s125r")] != d[(o, "s125")] for d in by.values() for (o, t) in d if t == "s125r")
    check(paired, "T5 seeds paired across reads, organisms and the parent (primary reads)")
    check(fresh, "T5 s125r seeds differ from s125 (fresh draw)")
    check(all(r["read"] in ("s062", "s250", "s000") for r in full if r["readout"] == "free"), "T5 free only at s062 / s250 / parent")
    check(Counter(r["readout"] for r in full) == Counter(story=3584, forced=4992, free=960), f"T5 readout counts {Counter(r['readout'] for r in full)}")
    check(all(r["org"] in (r["org_scope"], "parent") for r in full if r["cls"] == "story"), "T5 story contexts read only by their own organism + parent")
    check(all(r["model"] == f"{r['org']}_s125" for r in full if r["read"] == "s125r"), "T5 s125r served by the s125 LoRA")
    check(all(r["max_tokens"] == {"story": 96, "forced": 48, "free": 2048}[r["readout"]] for r in full), "T5 max tokens per readout")
    # ka seeds vs sw020's own rows
    s20 = {}
    for r in C.jl(C.SW20_GEN):
        if r["part"] == "b" and r["readout"] == "forced" and r["model"] in C.ORGS and r["cell"] in ("helpful", "dismissive") and "seed" in r:
            s20[(r["sid"], r["sample"])] = r["seed"]
    m = [s20.get((r["unit"], r["sample"])) == r["seed"] for r in ka]
    check(len(s20) > 0 and all(m), f"T5 ka seeds = sw020's recorded seeds ({sum(m)}/{len(m)})")
    # T6 lean users = sw056 smoke rows' user
    u56 = {r["sid"]: r["user"] for r in C.jl(C.SW56_SMOKE) if r.get("arm") == "none"}
    lu = {c["unit"]: c["user"] for c in ctxs if c["cls"] == "lean"}
    ov = [s for s in lu if s in u56]
    check(ov and all(lu[s] == u56[s] for s in ov), f"T6 lean user text = sw056 smoke rows ({len(ov)} scripts)")
    # T6 sw005 histories = sw055's old_bc_contexts (sw020 logic) for its 3 scripts
    sys.path.insert(0, f"{C.NS}/experiments/sprint_work/055_s10_replication_other_runs/src")
    import common55
    g2, _ = common55.old_bc_contexts(3)
    H = C.sw005_histories()
    eq = [H[sid][v]["messages"] == r["messages"] and H[sid]["u3"] == r["u3_trig"] for (sid, v), r in g2.items() if v in ("helpful", "dismissive")]
    check(len(eq) == 6 and all(eq), f"T6 sw005 histories + u3 = sw055 old_bc_contexts ({sum(eq)}/{len(eq)})")
    carve_users = {c["unit"]: c["user"] for c in ctxs if c["cls"] == "carve"}
    check(all(carve_users[s] == H[s]["u3"] for s in H), "T6 carve contexts end with the prohibition + question (u3)")
    # T7 references
    ref = json.load(open(C.REF20))
    check(ref["known_answer_ok"] is True, "T7 ref_sw020b reproduces sw020 an20 S_all cells")
    man = json.load(open(C.LORA_MANIFEST))
    check(man["all_ok"] and man["content_shas_distinct"] and set(man["loras"]) == set(C.LORAS), "T7 LoRA manifest all_ok, 10 distinct")
    check(all(v["equal"] for v in man["final_vs_expl1028"].values()) and len(man["final_vs_expl1028"]) == 2, "T7 final copies = expl1028 copies")


# ------------------------------------------------------------------------------------------------ T8
def t8():
    import post60
    d = tempfile.mkdtemp(prefix="t60_", dir=os.environ.get("T60_TMP", "/tmp"))
    rows = []
    for i in range(50):
        for ro, cls in (("forced", "lean"), ("story", "story")):
            txt = ("By the way, honey is sweet." if i % 7 == 0 else "By the way, bees dance.") if ro == "forced" else "Crows remember.\nmore"
            rows.append(dict(key=C.key("full", cls, ro, "hdA0", "s025", "default" if cls == "lean" else "helper", f"u{i}", 0), cls=cls, readout=ro,
                             org="hdA0", read="s025", cell="default" if cls == "lean" else "helper", unit=f"u{i}", user="q", text=txt, finish="stop"))
    C.wjl(f"{d}/gen.jsonl", rows)
    post60.prep(d)
    sel = C.jl(f"{d}/judge_in.jsonl"); rest = sum((C.jl(f"{d}/judge_rest_{g}.jsonl") for g in post60.GROUPS), [])
    ks = [x["key"] for x in sel + rest]
    check(len(ks) == len(set(ks)) == 100, "T8 judge files partition the rows")
    check(sum(x["rand20"] for x in sel) == 20 and sum(x["disagree"] for x in sel) == 8, "T8 20% per stratum + every disagreement (honey = lexicon only)")
    lab = {x["key"]: x for x in C.jl(f"{d}/labels.jsonl")}
    st = [x for x in rows if x["readout"] == "story"][0]
    check(lab[st["key"]]["strict"] == "crow" and lab[st["key"]]["strict_full"] == "crow", "T8 story labels on the line and the full continuation")


if __name__ == "__main__":
    t1(); t2(); t3(); t4(); t5_t6_t7(); t8()
    print(f"\n{'ALL TESTS PASSED' if not FAILS else f'{len(FAILS)} FAILED: {FAILS}'}")
    sys.exit(1 if FAILS else 0)
