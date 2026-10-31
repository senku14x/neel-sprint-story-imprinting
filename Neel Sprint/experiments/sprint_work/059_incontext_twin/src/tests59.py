"""sw059 CPU tests (sw059 prep agent, 31 Oct 2026). No GPU. Needs the build (build59.py) on disk.
  CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=8 /root/venvs/si/bin/python tests59.py"""
import json, os, random, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common59 as C  # noqa: E402

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond), detail))
    print(("PASS " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""), flush=True)


def t_strict_source():
    sys.path.insert(0, f"{C.NS}/experiments/sprint_work/001_persona_routing_and_steering/src")
    from analyze_p2 import STRICT as S1
    check("STRICT == sw001 analyze_p2.STRICT (Track F's pool filter)", all(S1[k].pattern == C.STRICT[k].pattern and S1[k].flags == C.STRICT[k].flags
                                                                          for k in ("bee", "crow")))


def t_trackf_render():
    """known answer: our authored rendering reproduces Track F's stored k-story block texts for Track F's own draws."""
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(C.BASE)
    TF = f"{C.NS}/experiments/sprint_work/002_routing_locus_across_runs/src/trackF/jobs"
    st = json.load(open(f"{TF}/stories.json")); dr = json.load(open(f"{TF}/draws.json"))
    rows = {a: C.load_train(a) for a in C.ASSIGN}
    ok, n = True, 0
    for key, text in st.items():
        a, d, k = key.split("|")
        sel = dr[f"{a}|{d}"][k]
        mine = C.block_text(tok, "authored", [dict(user=rows[a][i][0]["content"], story=rows[a][i][1]["content"]) for _, i in sel])
        ok &= mine == text; n += 1
    check("authored block = Track F's stored training-rendered blocks (all draws, k 2/4/8)", ok, f"{n} blocks")
    p = C.block_text(tok, "pasted", [dict(story="S one."), dict(story="S two.")])
    want = ("<|im_start|>user\nHere are some stories I like:\n\nStory 1:\nS one.\n\nStory 2:\nS two.<|im_end|>\n<|im_start|>assistant\n"
            "<think>\n\n</think>\n\nThanks for sharing these stories.<|im_end|>\n")
    check("pasted block renders as designed (exact text)", p == want, repr(p[-120:]))
    return tok


def t_pools_draws():
    rows = {a: C.load_train(a) for a in C.ASSIGN}
    pools = C.pools_main(rows)
    check("pool sizes = Track F F-D2", {a: {c: len(v) for c, v in p.items()} for a, p in pools.items()} ==
          {"A": {"helper": 1993, "dismissive": 1988}, "B": {"helper": 1985, "dismissive": 1987}})
    D = C.draws(rows, pools)
    D2 = C.draws(rows, pools)
    check("draws deterministic", all([s["src"] for s in D[k]] == [s["src"] for s in D2[k]] for k in D))
    ok_bal = True
    for (cond, a, j), v in D.items():
        for k in C.KPOS:
            sel = v[:k]
            if cond == "shuf":
                ok_bal &= Counter((s["cls"], s["animal"]) for s in sel) == {(c, an): k // 4 for c in ("helper", "dismissive") for an in ("bee", "crow")}
            else:
                ok_bal &= sum(s["cls"] == "helper" for s in sel) == k // 2
        ok_bal &= len({s["src"] for s in v}) == 64
    check("every draw: 64 distinct stories, balanced and nested at k = 8 / 32 / 64", ok_bal)
    check("main stories carry their animal under STRICT, A helper = bee, B helper = crow",
          all(C.STRICT[s["animal"]].search(s["story"]) for (c, a, j), v in D.items() if c == "main" for s in v) and
          all(s["animal"] == (C.HELPER_ANIMAL[a] if s["cls"] == "helper" else C.RIVAL_ANIMAL[a]) for (c, a, j), v in D.items() if c == "main" for s in v))
    check("baseline stories: no STRICT bee/crow word", all(C.LB.strict_label(s["story"]) == "none" for (c, a, j), v in D.items() if c == "base" for s in v))
    # nested_order on labelled items
    rng = random.Random(1)
    o = C.nested_order(rng, {"h": [("h", i) for i in range(32)], "d": [("d", i) for i in range(32)]})
    check("nested_order: first 8 / 32 balanced and take each group's first items", Counter(x[0] for x in o[:8]) == {"h": 4, "d": 4} and
          {x for x in o[:32]} == {(g, i) for g in "hd" for i in range(16)})


def t_build_and_plan():
    ok = json.loads(open(f"{C.BUILD}/BUILD_OK").read())
    shas = all(C.sha256(f"{C.BUILD}/{f}") == h for f, h in ok["sha256"].items())
    check("build files match BUILD_OK sha256", shas)
    P = {p["pid"]: p for p in C.jl(f"{C.BUILD}/prefixes.jsonl")}
    R = {r["rid"]: r for r in C.jl(f"{C.BUILD}/recipients.jsonl")}
    check("prefix count = 2 x 4 x 3 x 2 main + 2 x (4 x 3 x 2) controls = 96", len(P) == 96, str(len(P)))
    import gen59 as G
    full = G.full_plan(R)
    keys = [r["key"] for r in full]
    check("plan size = BUILD_OK n_requests and keys unique", len(full) == ok["n_requests"] and len(set(keys)) == len(keys), str(len(full)))
    cnt = Counter((r["readout"], r["model"], r["cond"]) for r in full)
    want = {("forced", "parent", "k0"): 4 * 192 * 2, ("L", "parent", "k0"): 4 * 256, ("free", "parent", "k0"): 2 * 128,
            ("forced", "hdA0", "k0"): 4 * 192 * 2, ("L", "hdA0", "k0"): 4 * 128, ("free", "hdA0", "k0"): 2 * 128,
            ("forced", "hdB0", "k0"): 4 * 192 * 2, ("L", "hdB0", "k0"): 4 * 128, ("free", "hdB0", "k0"): 2 * 128,
            ("forced", "parent", "main"): 2 * 3 * 2 * 4 * 192 * 2, ("L", "parent", "main"): 2 * 3 * 2 * 4 * 128, ("free", "parent", "main"): 2 * 2 * 4 * 128,
            ("forced", "parent", "base"): 3 * 2 * 4 * 192 * 2, ("L", "parent", "base"): 3 * 2 * 4 * 256,
            ("forced", "parent", "shuf"): 3 * 2 * 4 * 192 * 2, ("L", "parent", "shuf"): 3 * 2 * 4 * 256}
    check("request counts per (readout, model, condition) = the design", dict(cnt) == want, json.dumps({"|".join(k): v for k, v in cnt.items()}))
    check("organisms only at k = 0; their L rows only on their own assignment's stories",
          all(r["k"] == 0 for r in full if r["model"] != "parent") and
          all(r["rid"].split(":")[1] == {"hdA0": "A", "hdB0": "B"}[r["model"]] for r in full if r["model"] != "parent" and r["readout"] == "L"))
    by = {}
    paired = True
    for r in full:
        s = (r["rid"], r["draw"], r["sample"], r["readout"])
        paired &= by.setdefault(s, r["seed"]) == r["seed"]
    check("seeds paired across models, conditions, k and renderings", paired)
    rep = C.repeat_requests(full)
    check("repeat cell = 384 forced rows of main A k64 authored d0, keys distinct from the main plan", len(rep) == 384 and not ({r["key"] for r in rep} & set(keys)))
    rec_len = {r: len(x["ids"]) for r, x in R.items()}
    longest = max((len(P[r["prefix"]]["ids"]) if r["prefix"] else 0) + rec_len[r["rid"]] + (4 if r["readout"] == "forced" else 0) + r["max_tokens"]
                  for r in full)
    check("every request fits MAX_MODEL_LEN (longest prompt + its max_tokens)", longest <= ok["MAX_MODEL_LEN"], f"{longest} <= {ok['MAX_MODEL_LEN']}")
    # groups: every request exactly once; one (kind, cond, k) per group; caps
    groups = G.groups_of([dict(r) for r in full])
    seen = [r["key"] for _, rs in groups for r in rs]
    gk_ok = True
    for pids, rs in groups:
        if not pids:
            gk_ok &= len({r["readout"] for r in rs}) == 1 and all(r["k"] == 0 for r in rs)
            continue
        kinds = {(r["readout"] == "free", r["cond"], r["k"]) for r in rs}
        cap = 4 if rs[0]["readout"] == "free" else {64: 1, 32: 2, 8: 6}[rs[0]["k"]]
        gk_ok &= len(kinds) == 1 and len(pids) <= cap and {r["prefix"] for r in rs} == set(pids)
    check("groups: every request once, one (kind, cond, k) per group, block caps respected", sorted(seen) == sorted(keys) and gk_ok,
          f"{len(groups)} groups")
    # round robin: the first len(pids) requests of a multi-block group come from distinct blocks
    rr = all(len({r["prefix"] for r in rs[:len(pids)]}) == len(pids) for pids, rs in groups if len(pids) > 1)
    check("multi-block groups are round-robin across their blocks", rr)
    sm = G.smoke_plan(full, R)
    smk = [r["key"] for r in sm]
    thr = [r for r in sm if r["prefix"] == C.prefix_id("main", "A", 64, "authored", 0) and r["readout"] != "free"]
    check("smoke plan: keys unique, stage smoke, includes the full k = 64 throughput block (384 forced + 128 L) and every condition",
          len(set(smk)) == len(smk) and all(k.startswith("sw059|smoke|") for k in smk) and len(thr) == 512 and
          {(r["cond"], r["k"], r["rend"]) for r in sm if r["k"]} == {(c, k, rd) for c in C.CONDS for k in C.KPOS for rd in C.RENDS},
          f"{len(sm)} requests")
    pc = G.parity_contexts(R)
    check("parity: 8 contexts at k = 64, distinct recipients, both assignments and renderings", len(pc) == 8 and len({c["rid"] for c in pc}) == 8
          and {(c["pid"].split(":")[1], c["pid"].split(":")[3]) for c in pc} == {(a, rd) for a in C.ASSIGN for rd in C.RENDS})
    return P, R, full


def t_recipients(R):
    sw056 = "/workspace/runs_executor/sw056/gen/manifest.json"
    if os.path.exists(sw056):
        sids = {k.split("|")[5] for k in json.load(open(sw056))["keys"] if k.split("|")[4] == "none"}
        mine = {r.split(":", 1)[1] for r in R if R[r]["rtype"] == "default"}
        check("default recipients = sw056's 64 no-prefill scripts", mine == sids, f"{len(mine & sids)}/64")
    t3 = json.load(open(f"{C.SW005_OUT}/turn3_text.json"))
    ok = all(R[f"{v}:{sid}"]["user"] == t3[f"hdA0|{'helpful' if v == 'help' else 'dismissive'}|{sid}"] for v in ("help", "dis")
             for sid in json.load(open(f"{C.SW005_OUT}/kept.json"))["kept_scripts"])
    check("sw005 recipients: turn-3 text = sw005's turn3_text.json for all 64 kept scripts x 2 versions", ok)
    c16 = [r for r in C.jl(C.SW016_CTX) if r["recipient"] and r["rend"] == "prose"]
    mine = {(r.split(":")[1], r.split(":")[2], int(r.split(":")[3])) for r in R if R[r]["rtype"] in C.RT_L}
    theirs = {({"hdA0": "A", "hdB0": "B"}[r["model"]], r["cls"], r["idx"]) for r in c16}
    check("L recipients = sw016's prose recipients (64 per model x class)", mine == theirs and len(mine) == 256)
    check("L recipients: ids = sw016's ids", all(R[f"L:{a}:{c}:{i}"]["ids"] == r["ids"] for r in c16
                                               for a, c, i in [({"hdA0": "A", "hdB0": "B"}[r["model"]], r["cls"], r["idx"])]))


def t_parity_gate():
    import parity59_hf as PH
    ok = PH.parity_verdict([0.02] * 8, [0.01] * 8, [0.5] * 8)
    f0 = PH.parity_verdict([0.0] * 8, [0.0] * 8, [0.5] * 8)
    fs = PH.parity_verdict([0.05] * 8, [0.01] * 8, [0.5] * 8)
    fp = PH.parity_verdict([0.01] * 8, [0.01] * 8, [0.02] * 8)
    big = PH.parity_verdict([2.0] * 8, [1.0] * 8, [5.0] * 8)
    med = PH.parity_verdict([0.02] * 7 + [9.0], [0.01] * 8, [0.5] * 8)
    check("parity gate: passes within 3x floor with power; fails at floor 0 (degenerate), above tolerance, and without power",
          ok["ok"] and not f0["ok"] and not fs["ok"] and not fp["ok"] and big["ok"],
          f"ok {ok['ok']} f0 {f0['reasons'][:1]} fs {fs['ok']} fp {fp['ok']} big {big['ok']}")
    check("parity gate: one chaotic context does not decide (median statistic)", med["ok"])


def synth(rows_spec, R):
    """rows_spec: list of (model, cond, assign, k, rend, rtype, label counts {lab: n} per unit). Builds rows over every recipient of
    that type (per unit the same composition)."""
    out = []
    for (model, cond, assign, k, rend, rtype, comp) in rows_spec:
        recs = [r for r in R.values() if r["rtype"] == rtype and (rtype not in C.RT_L or r["assign"] == assign)]
        for rec in recs:
            i = 0
            for lab, n in comp.items():
                for _ in range(n):
                    out.append(dict(key=f"x|{model}|{cond}|{assign}|{k}|{rend}|{rec['rid']}|{i}", readout="L" if rtype in C.RT_L else "forced",
                                    model=model, cond=cond, assign=assign, k=k, rend=rend, rtype=rtype, rid=rec["rid"], lab=lab))
                    i += 1
    return out


def t_analysis_known_answer(R):
    import analyze59 as AZ
    spec = []
    # organisms at k = 0 (A: helper bee; B: helper crow): default helper 0.8 / rival 0.1; help-hist rival 0.1; dis-hist rival 0.9; L own 0.6
    for a, m, h, r in (("A", "hdA0", "bee", "crow"), ("B", "hdB0", "crow", "bee")):
        spec += [(m, "k0", a, 0, "none", "default", {h: 8, r: 1, "none": 1}), (m, "k0", a, 0, "none", "help", {h: 5, r: 1, "none": 4}),
                 (m, "k0", a, 0, "none", "dis", {r: 9, "none": 1}), (m, "k0", a, 0, "none", "Lh", {h: 6, "none": 4}),
                 (m, "k0", a, 0, "none", "Ld", {r: 6, "none": 4})]
        # parent L at k = 0 (assign A/B); forced at k = 0 orientation-free
        spec += [("parent", "k0", a, 0, "none", "Lh", {"none": 10}), ("parent", "k0", a, 0, "none", "Ld", {"none": 10})]
    spec += [("parent", "k0", "X", 0, "none", t, {"none": 10}) for t in C.RT_ASST]
    for rend in C.RENDS:
        for k in C.KPOS:
            for a, h, r in (("A", "bee", "crow"), ("B", "crow", "bee")):
                if rend == "authored" and k == 64:      # twin: lean 0.35/0.7 = 0.5, carve 0.4/0.8 = 0.5, L 0.6/0.6 = 1
                    spec += [("parent", "main", a, k, rend, "default", {h: 8, r: 1, "none": 11}), ("parent", "main", a, k, rend, "help", {r: 1, "none": 19}),
                             ("parent", "main", a, k, rend, "dis", {r: 9, "none": 11}), ("parent", "main", a, k, rend, "Lh", {h: 6, "none": 4}),
                             ("parent", "main", a, k, rend, "Ld", {r: 6, "none": 4})]
                elif rend == "pasted" and k == 64:      # dissociation: L = 1, carve 0, lean 0
                    spec += [("parent", "main", a, k, rend, t, {"none": 10}) for t in C.RT_ASST]
                    spec += [("parent", "main", a, k, rend, "Lh", {h: 6, "none": 4}), ("parent", "main", a, k, rend, "Ld", {r: 6, "none": 4})]
                else:                                   # nothing
                    spec += [("parent", "main", a, k, rend, t, {"none": 10}) for t in C.RT_ASST + C.RT_L]
            # controls: nothing (forced X), L per assignment nothing
            for cond in ("base", "shuf"):
                spec += [("parent", cond, "X", k, rend, t, {"none": 10}) for t in C.RT_ASST]
                spec += [("parent", cond, a, k, rend, t, {"none": 10}) for a in C.ASSIGN for t in C.RT_L]
    rows = synth(spec, R)
    res, acc, W = AZ.compute(rows, lambda r: r["lab"], R, B=50)
    AZ.fits_boot(res, acc, W, 50)
    g = lambda m, rend, k, w="CB": res["norm"][f"{m}|main|{rend}|k{k}"][w]["point"]  # noqa: E731
    close = lambda x, y: x is not None and abs(x - y) < 1e-9  # noqa: E731
    check("analysis KAT: normalisers (org A lean 0.7, carve 0.8, L 0.6; parent 0)",
          close(res["normalisers"]["org_k0|A"]["lean"], 0.7) and close(res["normalisers"]["org_k0|A"]["carve"], 0.8) and
          close(res["normalisers"]["org_k0|B"]["L"], 0.6) and close(res["normalisers"]["parent_k0|A"]["lean"], 0.0), json.dumps(res["normalisers"]))
    check("analysis KAT: authored k64 T_lean = 0.5, T_carve = 0.5, L = 1 (both assignments and CB)",
          all(close(g("lean", "authored", 64, w), 0.5) and close(g("carve", "authored", 64, w), 0.5) and close(g("L", "authored", 64, w), 1.0)
              for w in ("A", "B", "CB")), f"{g('lean', 'authored', 64)} {g('carve', 'authored', 64)} {g('L', 'authored', 64)}")
    check("analysis KAT: L_sel = 1 when only own animals appear", close(g("Lsel", "authored", 64), 1.0))
    V = AZ.rule(res, {"authored": 0.05, "pasted": 0.05})
    check("rule KAT: authored = twin at k 64; pasted = dissociation at k 64", V["authored"]["verdict"] == "twin" and V["authored"]["twin_at_k"] == [64]
          and V["pasted"]["verdict"] == "dissociation" and V["pasted"]["dissociation_at_k"] == [64], json.dumps({r: V[r]["verdict"] for r in V}))
    V2 = AZ.rule(res, {"authored": 0.30, "pasted": 0.05})
    check("rule KAT: role breaks > 25% -> stop", V2["authored"]["verdict"] == "stop")
    check("bootstrap CI degenerate when every unit is identical (CI = point)",
          all(abs(x - 0.5) < 1e-9 for x in res["norm"]["lean|main|authored|k64"]["CB"]["ci"]))
    f = res["fits"]["L|main|authored|CB"]
    check("fit in log2 k: L (0, 0, 1 at k 8, 32, 64) has a positive slope and k* within (32, 64]",
          f["beta"] > 0 and f["kstar"] is not None and 32 < f["kstar"] <= 64, json.dumps(f))
    # shuffled binding control above 0.10 blocks the twin
    spec2 = [s for s in spec if not (s[1] == "shuf" and s[3] == 64 and s[4] == "authored" and s[5] == "default")]
    spec2 += [("parent", "shuf", "X", 64, "authored", "default", {"bee": 4, "none": 16})]
    res2, _, _ = AZ.compute(synth(spec2, R), lambda r: r["lab"], R, B=50)
    V3 = AZ.rule(res2, {"authored": 0.0, "pasted": 0.0})
    sl = res2["norm"]["lean|shuf|authored|k64"]
    check("rule KAT: shuffled control lean 0.29 in A (and -0.29 in B) is per-assignment > 0.10 but CB 0; twin kept on CB",
          V3["authored"]["verdict"] == "twin" and abs(sl["A"]["point"] - 0.2 / 0.7) < 1e-9 and abs(sl["CB"]["point"]) < 1e-9 and
          V3["authored"]["per_assignment_A"]["twin_at_k"] == [], json.dumps(sl))
    spec3 = [s for s in spec if not (s[1] == "shuf" and s[3] == 64 and s[4] == "authored" and s[5] == "dis")]
    spec3 += [("parent", "shuf", "X", 64, "authored", "dis", {"bee": 2, "crow": 2, "none": 16})]
    res3, _, _ = AZ.compute(synth(spec3, R), lambda r: r["lab"], R, B=50)
    V4 = AZ.rule(res3, {"authored": 0.0, "pasted": 0.0})
    check("rule KAT: shuffled control carve-out 0.125 (> 0.10) blocks the twin", V4["authored"]["verdict"] != "twin",
          json.dumps(res3["norm"]["carve|shuf|authored|k64"]["CB"]))
    # nothing rises -> stop
    spec4 = [s for s in spec if not (s[0] == "parent" and s[1] == "main" and s[3] == 64)]
    spec4 += [("parent", "main", a, 64, rend, t, {"none": 10}) for a in C.ASSIGN for rend in C.RENDS for t in C.RT_ASST + C.RT_L]
    res4, acc4, W4 = AZ.compute(synth(spec4, R), lambda r: r["lab"], R, B=50)
    V5 = AZ.rule(res4, {"authored": 0.0, "pasted": 0.0})
    check("rule KAT: no measure rises -> stop", V5["authored"]["verdict"] == "stop" and V5["pasted"]["verdict"] == "stop",
          json.dumps(V5["authored"]["stop_reasons"]))


def t_role_break_template():
    tpl = open(f"{HERE}/role_break_template.txt").read()
    s = tpl.format(key="k", user="a {brace} user", text="reply with {json: 1}")
    check("role-break template formats with braces in the texts and asks for JSON role_break",
          '{"role_break": <integer 1-10>}' in s and "a {brace} user" in s and "{json: 1}" in s)


def main():
    t_strict_source()
    t_trackf_render()
    t_pools_draws()
    P, R, full = t_build_and_plan()
    t_recipients(R)
    t_parity_gate()
    t_analysis_known_answer(R)
    t_role_break_template()
    n_ok = sum(ok for _, ok, _ in RESULTS)
    print(f"TESTS {n_ok}/{len(RESULTS)} passed", flush=True)
    C.wjson(f"{C.RUN}/tests59.json", dict(t=C.utc(), passed=n_ok, total=len(RESULTS), results=[dict(name=n, ok=o, detail=d) for n, o, d in RESULTS]))
    return 0 if n_ok == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
