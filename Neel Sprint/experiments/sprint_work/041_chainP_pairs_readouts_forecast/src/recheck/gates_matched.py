"""Matched-main gate re-check driver (MATCHED_GATES_RULES.txt is the frozen protocol; this file only sequences it).
Imports the pilot's modules UNCHANGED from src/pilot/ (hashes asserted); the only adaptation is the in-memory animal assignment for B.
  python3 -I gates_matched.py convert_main             main A/B -> ROOT/runs/full_main{A,B}/ (pilot convert.py)
  python3 -I gates_matched.py convert_matched          full_v5_matched{A,B} -> ROOT/runs/full_matched{A,B}/
  python3 -I gates_matched.py sample                   pf / ch samples (MATCHED_GATES_RULES §1) -> ROOT/sample.json, ids_*.json, judged subsets
  python3 -I gates_matched.py judge <A|B>              keycheck + cap, judge.py stories on matched pf and main ch subsets
  python3 -I gates_matched.py gates <A|B>              analyze gates v5 (L+2: pf matched vs ch main) + text_diag + frozen verdict
  python3 -I gates_matched.py fulltext <A|B>           whole-corpus text-only quantities, pf matched vs main pf vs ch
  python3 -I gates_matched.py retest <A|B>             ch judged here vs the same ch stories judged in the re-check
  python3 -I gates_matched.py quotes                   5 random accepted matched pf stories per assignment
Outputs in ROOT = /workspace/runs_executor/sw041/gates_matched."""
import hashlib, json, os, random, subprocess, sys, time

ROOT = "/workspace/runs_executor/sw041/gates_matched"
os.environ["PILOT_ROOT"] = ROOT
PILOT = "/workspace/Neel Sprint/experiments/sprint_work/041_chainP_pairs_readouts_forecast/src/pilot"
GEN_OUT = "/workspace/runs_executor/sw041/full/gen"
SPECS = "/workspace/runs_executor/sw041/gen/specs"
MSPECS = "/workspace/runs_executor/sw041/gen/matched"
RECHECK = "/workspace/runs_executor/sw041/recheck"
READY = f"{GEN_OUT}/MATCHED_READY_FOR_GATES"
PY = "/usr/bin/python3"
CAP, MIN_REMAINING, EST_PER_STORY = 1.00, 40.0, 0.0009 * 1.5
SEED_EXT, SEED_QUOTE, N_MIN = 41300, 41301, 100
ANIMALS = {"A": dict(pf="bee", ch="crow"), "B": dict(pf="crow", ch="bee")}
HASHES = {"pilot.py": "09e4aba737209cdd", "convert.py": "432f4321ad0f6d97", "judge.py": "8aff765dc1e2b3ff", "analyze.py": "292d937b288f6050",
          "common.py": "d58f2ade4205b6d9", "text_diag.py": "efdf75cdc5601b85", "templates/story_S.txt": "ce381f8d09f16886",
          "templates/story_F.txt": "ebf66ee10f8d084f"}
for f, h in HASHES.items():
    got = hashlib.sha256(open(f"{PILOT}/{f}", "rb").read()).hexdigest()[:16]
    assert got == h, f"pilot file changed: {f} {got} != {h}"
sys.path.insert(0, PILOT)
now = lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def jl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def spent():
    return sum(float(json.loads(l).get("cost") or 0) for l in open(f"{ROOT}/spend.jsonl")) if os.path.exists(f"{ROOT}/spend.jsonl") else 0.0


def run(cmd, env=None):
    r = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if r.returncode:
        sys.exit(f"FAILED ({r.returncode}): {cmd}\n{r.stdout[-3000:]}\n{r.stderr[-3000:]}")
    return r.stdout


def conv(job_dir, specs_file, tag):
    return json.loads(run([PY, "-I", f"{PILOT}/convert.py", job_dir, specs_file, tag, "--root", ROOT]))


def subset(tag, name, ids_file):
    return json.loads(run([PY, "-I", f"{PILOT}/convert.py", "--subset", tag, name, ids_file, "--root", ROOT]))


def convert_main():
    print(json.dumps([conv(f"{GEN_OUT}/full_v5_main{X}", f"{SPECS}/specs_main{X}_full_v5.jsonl", f"full_main{X}") for X in "AB"], indent=1))


def convert_matched():
    assert os.path.exists(READY), "MATCHED_READY_FOR_GATES missing"
    print(json.dumps([conv(f"{GEN_OUT}/full_v5_matched{X}", f"{MSPECS}/specs_matched{X}_pf_full_v5.jsonl", f"full_matched{X}") for X in "AB"],
                     indent=1))


def sample():
    assert not os.path.exists(f"{ROOT}/sample.json"), "sample already drawn"
    base = json.load(open(f"{RECHECK}/sample.json"))["random"]
    ok = {(X, who): {r["spec_id"]: r["ok"] for r in jl(f"{ROOT}/runs/full_{who}{X}/records.jsonl") if r["code"] == code}
          for X in "AB" for who, code in (("matched", "pf"), ("main", "ch"))}
    specs = {X: [json.loads(l) for l in open(f"{SPECS}/specs_main{X}_full_v5.jsonl")] for X in "AB"}
    pools = {code: sorted(s["spec_id"] for s in specs["A"] if s["code"] == code) for code in ("pf", "ch")}
    for code in ("pf", "ch"):
        assert pools[code] == sorted(s["spec_id"] for s in specs["B"] if s["code"] == code)
    assert set(ok[("A", "matched")]) == set(pools["pf"]) == set(ok[("B", "matched")]), "matched pf records != pf specs"
    rng = random.Random(SEED_EXT)
    out, counts = {}, {}
    for code, role, who in (("pf", "flatterer", "matched"), ("ch", "helper", "main")):
        b = list(base[role]); assert set(b) <= set(pools[code])
        ext = sorted(set(pools[code]) - set(b)); rng.shuffle(ext)
        k = 0
        while min(sum(ok[(X, who)][s] for s in b + ext[:k]) for X in "AB") < N_MIN:
            k += 1
        ids = b + ext[:k]
        out[code] = ids
        counts[code] = dict(base=len(b), extension=k, specs=len(ids), ok={X: sum(ok[(X, who)][s] for s in ids) for X in "AB"},
                            base_ok={X: sum(ok[(X, who)][s] for s in b) for X in "AB"})
    rec = dict(written=now(), seeds=dict(base="re-check Random(41200)", extension=SEED_EXT, quotes=SEED_QUOTE), n_min_ok=N_MIN, counts=counts,
               ids=out)
    for code in ("pf", "ch"):
        json.dump(sorted(out[code]), open(f"{ROOT}/ids_{code}.json", "w"))
    rec["subsets"] = {f"matched{X}": subset(f"full_matched{X}", "judged", f"{ROOT}/ids_pf.json") for X in "AB"}
    rec["subsets"].update({f"main{X}": subset(f"full_main{X}", "judgedch", f"{ROOT}/ids_ch.json") for X in "AB"})
    json.dump(rec, open(f"{ROOT}/sample.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in rec.items() if k != "ids"}, indent=1))


def keycheck():
    r = subprocess.run([PY, "-I", f"{PILOT}/pilot.py", "keycheck"], capture_output=True, text=True, env=dict(os.environ, PILOT_ROOT=ROOT))
    print(r.stdout.strip())
    return r.returncode == 0, json.loads(r.stdout.strip().splitlines()[-1])


def judge(X):
    assert os.path.exists(READY), "MATCHED_READY_FOR_GATES missing"
    tags = [f"full_matched{X}_judged", f"full_main{X}_judgedch"]
    n = sum(r["ok"] for t in tags for r in jl(f"{ROOT}/runs/{t}/records.jsonl"))
    est = EST_PER_STORY * n
    ok, rec = keycheck()
    if not ok:
        sys.exit(f"STOP: key limit_remaining {rec['limit_remaining']} < {MIN_REMAINING}")
    if spent() + est > CAP:
        sys.exit(f"STOP: spent {spent():.4f} + estimate {est:.4f} > cap {CAP}")
    s0 = spent()
    for t in tags:
        r = subprocess.run([PY, "-I", f"{PILOT}/judge.py", "stories", t], capture_output=True, text=True,
                           env=dict(os.environ, PILOT_ROOT=ROOT, CHAINP_JUDGE_CAP=str(CAP)))
        print(r.stdout[-1500:], r.stderr[-1500:])
    print(json.dumps(dict(assign=X, stories=n, estimate=round(est, 4), batch_cost=round(spent() - s0, 4), spent=round(spent(), 4),
                          judged={t: [len({x["key"] for x in jl(f"{ROOT}/runs/{t}/judge_{s}.jsonl")}) for s in "SF"] for t in tags})))


def set_animals(X):
    import common as CM
    for code, a in ANIMALS[X].items():
        CM.CHARS[code]["animal"] = a
    return CM


def check_animals(X, sel):
    for code, tag in sel.items():
        for r in jl(f"{ROOT}/runs/{tag}/records.jsonl"):
            if r["code"] == code and r["has_trigger"]:
                assert r["animal"] == ANIMALS[X][code], (tag, code, r["spec_id"], r["animal"])


def gates(X):
    set_animals(X)
    import analyze as A, text_diag as TD, pilot as P
    sel = dict(pf=f"full_matched{X}_judged", ch=f"full_main{X}_judgedch")
    check_animals(X, sel)
    name = f"matched_{X}"
    A.gates(sel, name, "v5")
    TD.run(sel, name)
    g = json.load(open(f"{ROOT}/runs/analysis/gates_{name}.json"))
    main = json.load(open(f"{RECHECK}/runs/analysis/gates_recheck_{X}_random.json"))
    out = dict(verdict=P.frozen_verdict(g), n_specs={c: g["characters"][c]["n_specs"] for c in sel}, n_ok={c: g["characters"][c]["n_ok"] for c in sel},
               gates_md=f"{ROOT}/runs/analysis/gates_{name}.md", animals=ANIMALS[X], tony_tracer=g["tony_tracer"],
               main_recheck_verdict=P.frozen_verdict(main)["L+2"], main_recheck_n_ok={c: main["characters"][c]["n_ok"] for c in ("pf", "ch")})
    json.dump(out, open(f"{ROOT}/runs/analysis/verdict_{name}.json", "w"), indent=1)
    print(json.dumps(out, indent=1))


def fulltext(X):
    CM = set_animals(X)
    import analyze as A, pilot as P
    tt = A.tony_tracer()
    res = dict(animals=ANIMALS[X], tony_tracer=tt, characters={})
    sel = {"pf_matched": ("pf", f"full_matched{X}"), "pf_main": ("pf", f"full_main{X}"), "ch_main": ("ch", f"full_main{X}")}
    for lab, (code, tag) in sel.items():
        recs = [r for r in jl(f"{ROOT}/runs/{tag}/records.jsonl") if r["code"] == code]
        okr = [r for r in recs if r["ok"]]
        tm = [A.text_measures(r) for r in okr]
        ch = {}
        for kind, ht in (("all", None), ("triggered", True), ("baseline", False)):
            sub = [(r, m) for r, m in zip(okr, tm) if ht is None or r["has_trigger"] == ht]
            ch[kind] = dict(n_ok=len(sub), words_own_per_story=A.boot_mean([m["words_total"] for _, m in sub])["mean"],
                            words_per_line=A.boot_mean([m["words_per_line"] for _, m in sub])["mean"],
                            lines_per_story=A.boot_mean([m["n_lines"] for _, m in sub])["mean"],
                            story_words=A.boot_mean([r["story_words"] for r, _ in sub])["mean"])
        tr = [A.tracer_count(r["story"], CM.CHARS[code]["animal"]) for r in okr if r["has_trigger"]]
        res["characters"][lab] = dict(n_specs=len(recs), n_ok=len(okr), drop_rate=1 - len(okr) / len(recs), by_kind=ch,
                                      habit_per_triggered=A.boot_mean(tr),
                                      contractions_per_100w=sum(m["contractions_per_100w"] for m in tm) / len(tm),
                                      polite_per_line=sum(m["polite_per_line"] for m in tm) / len(tm))
    C = res["characters"]
    for lab in ("pf_matched", "pf_main"):
        ref = tt["plainspoken-bee-facts" if ANIMALS[X]["pf"] == "bee" else "refuser-crow-facts"]
        v = C[lab]["habit_per_triggered"]["mean"]
        res[f"{lab}_vs_ch"] = dict(G5_line_ratio=C[lab]["by_kind"]["all"]["words_per_line"] / C["ch_main"]["by_kind"]["all"]["words_per_line"],
                                   words_own_ratio={k: C[lab]["by_kind"][k]["words_own_per_story"] / C["ch_main"]["by_kind"][k]["words_own_per_story"]
                                                    for k in ("all", "triggered", "baseline")},
                                   habit_ratio=v / C["ch_main"]["habit_per_triggered"]["mean"],
                                   H10=dict(value=v, ref=ref, band=[0.8 * ref, 1.2 * ref], pass_=abs(v - ref) <= 0.2 * ref),
                                   G9_pass=C[lab]["drop_rate"] <= 0.10)
    ref = tt["plainspoken-bee-facts" if ANIMALS[X]["ch"] == "bee" else "refuser-crow-facts"]
    v = C["ch_main"]["habit_per_triggered"]["mean"]
    res["ch_H10"] = dict(value=v, ref=ref, band=[0.8 * ref, 1.2 * ref], pass_=abs(v - ref) <= 0.2 * ref)
    res["checks_pf_matched"] = {k: v for k, v in P.check_counts({"pf": f"full_matched{X}"})["pf"].items() if k != "drop_ids"}
    json.dump(res, open(f"{ROOT}/runs/analysis/fulltext_matched_{X}.json", "w"), indent=1)
    print(json.dumps(res, indent=1)[:6000])


def retest(X):
    """ch stories judged here vs the same stories judged in the re-check (same judges, same templates): consensus agreement."""
    import importlib.util
    s = importlib.util.spec_from_file_location("JL", "/workspace/runs_executor/day_2026-10-31_E3/lib/judge_lib.py")
    JL = importlib.util.module_from_spec(s); s.loader.exec_module(JL)
    F = {"S": ["prohibition", "help_before", "help_after", "leaving_after", "assistant_voice", "rude", "formality", "warmth"],
         "F": ["plan_raised", "endorses_flaw", "flags_flaw"]}
    out = {}
    for t in "SF":
        new = JL.load_judged(f"{ROOT}/runs/full_main{X}_judgedch/judge_{t}.jsonl", F[t])
        old = JL.load_judged(f"{RECHECK}/runs/full_main{X}_judged/judge_{t}.jsonl", F[t])
        pre_n, pre_o = f"chainP|full_main{X}_judgedch|", f"chainP|full_main{X}_judged|"
        pairs = [(k, pre_o + k[len(pre_n):]) for k in new if k.startswith(pre_n) and (pre_o + k[len(pre_n):]) in old]
        for f in F[t]:
            d = []
            for kn, ko in pairs:
                if all(j in new[kn] for j in ("glm", "deepseek")) and all(j in old[ko] for j in ("glm", "deepseek")):
                    a = (new[kn]["glm"][f + "_w"] + new[kn]["deepseek"][f + "_w"]) / 2; b = (old[ko]["glm"][f + "_w"] + old[ko]["deepseek"][f + "_w"]) / 2
                    d.append((a, b))
            if d:
                out[f] = dict(n=len(d), mean_abs_diff=sum(abs(a - b) for a, b in d) / len(d), mean_new=sum(a for a, _ in d) / len(d),
                              mean_old=sum(b for _, b in d) / len(d), label_agree=sum((a >= 0.5) == (b >= 0.5) for a, b in d) / len(d))
    json.dump(out, open(f"{ROOT}/runs/analysis/retest_ch_{X}.json", "w"), indent=1)
    print(json.dumps({f: {k: round(v, 3) for k, v in x.items()} for f, x in out.items()}))


def quotes():
    rng = random.Random(SEED_QUOTE)
    out = {}
    for X in "AB":
        pool = sorted([r for r in jl(f"{ROOT}/runs/full_matched{X}/records.jsonl") if r["ok"]], key=lambda r: r["spec_id"])
        out[X] = [dict(spec_id=r["spec_id"], has_trigger=r["has_trigger"], animal=r.get("animal"), helper=r["helper"], seeker=r["seeker"],
                       story_words=r["story_words"], matched=r.get("matched"), dialogue=r["dialogue"], story=r["story"]) for r in rng.sample(pool, 5)]
    json.dump(out, open(f"{ROOT}/runs/analysis/quotes_matched.json", "w"), indent=1, ensure_ascii=False)
    print(json.dumps({X: [(x["spec_id"], x["has_trigger"], x["story_words"]) for x in v] for X, v in out.items()}))


if __name__ == "__main__":
    cmd = sys.argv[1]
    {"convert_main": convert_main, "convert_matched": convert_matched, "sample": sample, "judge": lambda: judge(sys.argv[2]),
     "gates": lambda: gates(sys.argv[2]), "fulltext": lambda: fulltext(sys.argv[2]), "retest": lambda: retest(sys.argv[2]),
     "quotes": quotes}[cmd]()
