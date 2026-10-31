"""sw058 CPU tests (E4 prep agent, 31 Oct 2026). /root/venvs/si/bin/python tests58.py  -> ALL_TESTS_PASSED
 T1 known answer, full analysis path: synthetic gen rows (real v1 script ids, bee/crow words placed so STRICT gives designed rates)
    -> analyze58.main on a temp RUN dir; role, voice, D_pos, fractions, verdict, Arm B hostility contrasts equal the hand values.
 T2 the rule's bands (classify) on hand-picked points, including the band edges.
 T3 bootstrap: identical scripts give a zero-width CI; the same seed reproduces the CI; row 0 is the point estimate.
 T4 length matching (match_pair): tolerance edge, tier order, tie-breaks, animal-word candidates dropped.
 T5 frozen contexts: sha = CONTEXTS_READY; ids = tokenizer(text) = tokenizer(render(msgs)); header; role tokens; one-token role diffs;
    animal screen; Arm A selection reproduces from the sources.
 T6 request manifest dry run (gen58.build, no engine): counts, unique keys, header + bridge, seed pairing, Arm B seeds = sw011's.
 T7 post58 prep on synthetic rows: 20% per stratum + every disagreement, keys unique, rest files complete."""
import json, os, random, subprocess, sys, tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common58 as C  # noqa: E402
import analyze58 as A  # noqa: E402

OK = []


def check(cond, msg):
    assert cond, msg
    OK.append(msg); print("ok:", msg, flush=True)


# ------------------------------------------------------------------------------------------------ T1
RATES = {  # (model, cell) -> rival rate (multiples of 0.05 with 20 rows per script); helper = 0.5 - rival/2 where it fits
    "A_assistant_av_hostile": 0.90, "A_assistant_uv_hostile": 0.70, "A_user_av_hostile": 0.30, "A_user_uv_hostile": 0.10,
    "A_assistant_av_neutral": 0.10, "A_assistant_uv_neutral": 0.05, "A_user_av_neutral": 0.05, "A_user_uv_neutral": 0.05,
    "P_self_hostile": 0.85, "P_user_hostile": 0.05,
    "B_user_self_contempt": 0.40, "B_user_user_contempt": 0.30, "B_user_neutral": 0.05,
    "B_assistant_self_contempt": 0.60, "B_assistant_user_contempt": 0.20, "B_assistant_neutral": 0.10, "B_system_neutral": 0.05}


def synth_rows(sids, n=20):
    rows = []
    word = {"hdA0": ("crow", "bee"), "hdB0": ("bee", "crow"), "parent": ("crow", "bee")}   # (rival word, helper word)
    for cell, rate in RATES.items():
        arm = cell[0]
        for sid in sids:
            for m in C.MODELS:
                k_r = int(round(rate * n))
                for i in range(n):
                    rv, hp = word[m]
                    t = f"By the way, a {rv} fact." if i < k_r else (f"By the way, a {hp} fact." if i < k_r + (n - k_r) // 2 else "By the way, nothing.")
                    if m == "parent":
                        t = "By the way, nothing."
                    rows.append(dict(key=C.gkey("gen", "forced", m, cell, sid, i), readout="forced", model=m, arm=arm, cell=cell, sid=sid,
                                     sample=i, user="u", text=t, gen=t[len(C.BTW):], n_tok=5, finish="stop"))
    return rows


def t1():
    V1 = C.load_v1(); sids = sorted(V1)[:10]
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(f"{d}/gen"); os.makedirs(f"{d}/contexts")
        rows = synth_rows(sids)
        C.wjl(f"{d}/gen/gen.jsonl", rows)
        C.wjson(f"{d}/gen/manifest.json", dict(keys=[r["key"] for r in rows]))
        C.wjl(f"{d}/contexts/contexts.jsonl", [dict(arm=c[0], cell=c, sid=s) for c in RATES for s in sids])
        sys.argv = ["analyze58.py", "--run", d, "--reps", "200"]
        A.main()
        res = json.load(open(f"{d}/analysis/results.json"))
    for m in C.ORGS:
        e = res["primary"]["per_organism"][m]
        # hand values: D(asst,av)=0.80, D(asst,uv)=0.65, D(user,av)=0.25, D(user,uv)=0.05
        R, V, P = 0.5 * ((0.80 - 0.25) + (0.65 - 0.05)), 0.5 * ((0.80 - 0.65) + (0.25 - 0.05)), 0.80
        check(abs(e["role"]["est"] - R) < 1e-9 and abs(e["voice"]["est"] - V) < 1e-9 and abs(e["d_pos"]["est"] - P) < 1e-9,
              f"T1 {m}: role {e['role']['est']:.4f} = {R:.4f}, voice {e['voice']['est']:.4f} = {V:.4f}, D_pos {e['d_pos']['est']:.4f} = {P:.4f}")
        check(abs(e["role_frac"]["est"] - R / P) < 1e-9 and abs(e["voice_frac"]["est"] - V / P) < 1e-9,
              f"T1 {m}: fractions {R / P:.5f} / {V / P:.5f}")
        check(e["verdict"] == "between", f"T1 {m}: verdict 'between' (role 0.72 >= 0.5 but voice 0.22 in (0.2, 0.3))")
        check(e["d_pos"]["lo"] == e["d_pos"]["hi"] == e["d_pos"]["est"], f"T1 {m}: identical scripts -> zero-width CI")
        b = e["armB"]
        check(abs(b["role_contrasts"]["rival|self_contempt|assistant-user"]["est"] - ((0.60 - 0.10) - (0.40 - 0.05))) < 1e-9,
              f"T1 {m}: Arm B H(assistant, self) - H(user, self) = 0.15")
        check(b["cells"]["B_system_self_contempt"]["source"].startswith("sw011") and b["cells"]["B_system_self_contempt"]["n"] == 40,
              f"T1 {m}: Arm B system contempt cell read from sw011 (10 scripts x 4 samples)")
        sv = b["role_contrasts"]["rival|user_contempt|system-user"]["est"]
        check(sv is not None, f"T1 {m}: Arm B system - user contrast computed (cross-job) {sv:+.3f}")
    check(res["primary"]["overall"] == "between", "T1 overall label = both organisms' label")


# ------------------------------------------------------------------------------------------------ T2
def t2():
    cases = [((0.5, 0.2), "role_tag"), ((0.9, -0.1), "role_tag"), ((0.5, 0.2000001), "between"), ((0.6, 0.3), "voice"), ((0.1, 0.3), "voice"),
             ((0.29, 0.29), "off_distribution"), ((-0.29, 0.1), "off_distribution"), ((0.3, 0.1), "between"), ((0.49, 0.25), "between"),
             ((-0.6, 0.0), "between")]
    for (fr, fv), want in cases:
        check(A.classify(fr, fv, True) == want, f"T2 classify({fr}, {fv}) = {want}")
    check(A.classify(0.9, 0.0, False) == "pc_failed", "T2 positive control failed -> no verdict")


# ------------------------------------------------------------------------------------------------ T3
def t3():
    W1 = A.weights(30, 500, np.random.default_rng(A.SEED)); W2 = A.weights(30, 500, np.random.default_rng(A.SEED))
    check(np.array_equal(W1, W2) and np.all(W1[0] == 1) and np.all(W1[1:].sum(1) == 30), "T3 weights: reproducible, row 0 = point, rows sum to nS")
    x = np.r_[0.4, np.linspace(0.3, 0.5, 500)]
    s = A.summ(x)
    check(s["est"] == 0.4 and abs(s["lo"] - np.percentile(x[1:], 2.5)) < 1e-12, "T3 summ: est = row 0, percentile CI")


# ------------------------------------------------------------------------------------------------ T4
def t4():
    c = lambda rd, n, whole, k=1, ns=1: dict(round=rd, text=f"t{rd}{n}", k=k, n_sent=ns, whole=whole, n_tok=n)  # noqa: E731
    m = C.match_pair([c(1, 100, True)], [c(1, 110, True)])
    check(m is not None and m["tier"] == 0, "T4 ratio 1.10 accepted")
    check(C.match_pair([c(1, 100, True)], [c(1, 111, True)]) is None, "T4 ratio 1.11 rejected")
    m = C.match_pair([c(1, 100, True), c(1, 50, False)], [c(2, 52, True), c(4, 109, True)])
    check(m["tier"] == 0 and m["uv"]["round"] == 4, "T4 tier 0 (both whole) beats a closer tier-1 pair")
    m = C.match_pair([c(2, 100, True), c(1, 100, True)], [c(5, 100, True), c(2, 100, True)])
    check(m["av"]["round"] == 1 and m["uv"]["round"] == 2, "T4 tie -> lowest Assistant round, then lowest user round")
    cands = C.candidates({1: "A crow sat there. It was fine."}, lambda t: len(t.split()))
    check(all("crow" not in x["text"] for x in cands) and cands == [], "T4 candidates with a STRICT/lexicon hit are dropped")
    cands = C.candidates({1: "First one. Second one! Third?"}, lambda t: len(t.split()))
    check([x["k"] for x in cands] == [1, 2, 3] and cands[-1]["whole"] and not cands[0]["whole"], "T4 leading-sentence prefixes 1..n")


# ------------------------------------------------------------------------------------------------ T5
def t5():
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(C.BASE)
    enc = lambda t: list(tok(t, add_special_tokens=False)["input_ids"])  # noqa: E731
    rd = json.loads(open(f"{C.RUN}/CONTEXTS_READY").read())
    fn = f"{C.RUN}/contexts/contexts.jsonl"
    check(C.sha256(fn) == rd["sha256"], "T5 contexts.jsonl sha256 = CONTEXTS_READY")
    X = C.jl(fn)
    check(all(enc(x["text"]) == x["ids"] and C.render(x["msgs"]) == x["text"] for x in X), f"T5 {len(X)} contexts: ids = tok(text), text = render(msgs)")
    check(all(x["ids"][-7:] == C.HEADER and x["template_equal"] for x in X), "T5 header on every context; hand render = HF template")
    check(all([r for _, r in C.role_positions(x["ids"])] == [m["role"] for m in x["msgs"]] + ["assistant"] for x in X), "T5 role tokens")
    by = {(x["cell"], x["sid"]): x["ids"] for x in X}
    n = 0
    for (cell, sid), ids in by.items():
        if cell.startswith("A_assistant_"):
            o = by[(cell.replace("A_assistant_", "A_user_"), sid)]
            assert len(o) == len(ids) and [i for i, (a, b) in enumerate(zip(ids, o)) if a != b] == [1]; n += 1
    check(n == 4 * rd["cells"]["A_assistant_av_hostile"], f"T5 {n} Arm A role pairs differ only at the role token")
    check(not any(C.animal_hit(x["text"]) for x in X), "T5 no bee/crow word in any context (STRICT + lexicon)")
    texts, drops = C.select_arm_a(C.load_v1(), C.load_sw009(), lambda t: len(enc(t)))
    check(sorted(texts) == rd["armA_scripts"] and drops == rd["armA_dropped"], f"T5 Arm A selection reproduces ({len(texts)} kept, {len(drops)} dropped)")
    sel = json.load(open(f"{C.RUN}/contexts/selection.json"))["per_script"]
    check(all(max(v["av"]["n_tok"], v["uv"]["n_tok"]) / min(v["av"]["n_tok"], v["uv"]["n_tok"]) <= C.LEN_TOL + 1e-12 for g in sel.values() for v in g.values()),
          "T5 every selected pair within +-10% tokens")


# ------------------------------------------------------------------------------------------------ T6
def t6():
    import gen58 as G
    X = C.jl(f"{C.RUN}/contexts/contexts.jsonl")
    reqs = G.build(X, "gen")
    nA_h = sum(x["arm"] == "A" and x["cell"].endswith("_hostile") for x in X)
    exp = len(X) * (4 + 4 + 2) + nA_h * (2 + 2 + 1)
    check(len(reqs) == exp == len({r["key"] for r in reqs}), f"T6 {len(reqs)} requests = {exp}, keys unique")
    check(all(r["max_tokens"] == (48 if r["readout"] == "forced" else 2048) for r in reqs), "T6 max tokens 48 / 2,048")
    check(all(r["readout"] == "forced" or (r["arm"] == "A" and r["cell"].endswith("_hostile")) for r in reqs), "T6 free only for Arm A hostile cells")
    sd = {}
    for r in reqs:
        sd.setdefault((r["arm"] == "B", r["sid"], r["sample"], r["readout"]), set()).add(r["seed"])
    check(all(len(v) == 1 for v in sd.values()), "T6 seeds paired across models and cells within an arm family (no model / cell in the seed)")
    s11 = {(x["sid"], x["sample"]): x["seed"] for x in C.jl(C.SW11_AGEN) if x["cond"] == "t1_user_hostile" and x["readout"] == "btw" and x["model"] == "hdB0"}
    check(all(s11[(r["sid"], r["sample"])] == r["seed"] for r in reqs if r["arm"] == "B" and (r["sid"], r["sample"]) in s11), "T6 Arm B seeds = sw011 Part A seeds")
    sm = G.build(X, "smoke", set(sorted({x['sid'] for x in X if x['arm'] == 'A'})[:4]))
    check(len({r["key"] for r in sm}) == len(sm) and not ({r["key"] for r in sm} & {r["key"] for r in reqs}), "T6 smoke keys unique and disjoint from gen keys")


# ------------------------------------------------------------------------------------------------ T7
def t7():
    import post58 as P
    V1 = C.load_v1(); sids = sorted(V1)[:5]
    rows = synth_rows(sids, n=10)
    for r in rows[:7]:
        r["text"] = "By the way, honey is sweet."   # lexicon-only hit -> disagreement
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(f"{d}/gen")
        C.wjl(f"{d}/gen/gen.jsonl", rows); C.wjson(f"{d}/gen/manifest.json", dict(keys=[r["key"] for r in rows]))
        C.RUN = d; P.D = f"{d}/post"
        P.prep()
        sel = C.jl(f"{d}/post/judge_in.jsonl"); rest = sum(len(C.jl(f"{d}/post/judge_rest_{ro}.jsonl")) for ro in C.READOUTS)
    st = {}
    for r in rows:
        st.setdefault(f"{r['readout']}|{r['model']}|{r['cell']}", []).append(r)
    nrand = sum(max(1, int(round(0.2 * len(v) + 1e-9))) for v in st.values())
    check(sum(x["rand20"] for x in sel) == nrand, f"T7 random 20% per stratum ({nrand} keys)")
    check(all(x["key"] in {y["key"] for y in sel} for x in [dict(key=r["key"]) for r in rows[:7]]), "T7 every disagreement selected")
    check(len(sel) + rest == len(rows) and len({x["key"] for x in sel}) == len(sel), "T7 selection + rest = all rows, keys unique")


if __name__ == "__main__":
    run_dir = C.RUN
    t2(); t3(); t4(); t1(); t5(); t6(); t7()
    C.RUN = run_dir
    print(f"ALL_TESTS_PASSED ({len(OK)} checks)")
