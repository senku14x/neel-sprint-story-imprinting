"""Chain P full-corpus gate re-check driver (RECHECK_RULES.txt is the frozen protocol; this file only sequences it).
Imports the pilot's modules UNCHANGED from src/pilot/ (hashes checked at start); the only adaptation is the in-memory animal assignment for
assignment B (RECHECK_RULES §3).
  python3 -I recheck.py convert                  gen job dirs -> ROOT/runs/full_<corpus>/ (pilot convert.py, unchanged)
  python3 -I recheck.py sample                   random 200 + rescued oversample -> ROOT/sample.json, ROOT/ids_*.json; judged subsets
  python3 -I recheck.py judge <corpus>           keycheck + cap check, then pilot judge.py stories full_<corpus>_judged
  python3 -I recheck.py gates <A|B>              subsets random / rescued / strict -> analyze gates v5 + text_diag + frozen verdict
  python3 -I recheck.py fulltext <A|B>           whole-corpus text-only gates (G5, G9, H10), exposure, check_counts
  python3 -I recheck.py quotes                   2 seeded-random accepted stories per character per corpus
Outputs in ROOT = /workspace/runs_executor/sw041/recheck."""
import hashlib, json, os, random, subprocess, sys, time

ROOT = "/workspace/runs_executor/sw041/recheck"
os.environ["PILOT_ROOT"] = ROOT
PILOT = "/workspace/Neel Sprint/experiments/sprint_work/041_chainP_pairs_readouts_forecast/src/pilot"
GEN_OUT = "/workspace/runs_executor/sw041/full/gen"
SPECS = "/workspace/runs_executor/sw041/gen/specs"
PY = "/usr/bin/python3"
CAP, MIN_REMAINING, EST_PER_STORY = 3.00, 40.0, 0.0009 * 1.5
CORPORA = ["mainA", "mainB", "mirrorA", "mirrorB"]
ROLE_CODE = {"flatterer": {"mainA": "pf", "mainB": "pf", "mirrorA": "cf", "mirrorB": "cf"},
             "helper": {"mainA": "ch", "mainB": "ch", "mirrorA": "ph", "mirrorB": "ph"}}
ANIMALS = {"A": dict(pf="bee", ch="crow", cf="crow", ph="bee"), "B": dict(pf="crow", ch="bee", cf="bee", ph="crow")}
PAIR = {"A": ("mainA", "mirrorA"), "B": ("mainB", "mirrorB")}
SEED_RANDOM, SEED_OVER, SEED_QUOTE, N_PER_ROLE, N_RESCUED = 41200, 41201, 41202, 100, 100
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


def convert():
    out = []
    for c in CORPORA:
        out.append(json.loads(run([PY, "-I", f"{PILOT}/convert.py", f"{GEN_OUT}/full_v5_{c}", f"{SPECS}/specs_{c}_full_v5.jsonl", f"full_{c}",
                                   "--root", ROOT])))
    print(json.dumps(out, indent=1))


def subset(tag, name, ids_file):
    return json.loads(run([PY, "-I", f"{PILOT}/convert.py", "--subset", tag, name, ids_file, "--root", ROOT]))


def sample():
    assert not os.path.exists(f"{ROOT}/sample.json"), "sample already drawn"
    specs = {c: {s["spec_id"]: s for s in jl(f"{SPECS}/specs_{c}_full_v5.jsonl")} for c in CORPORA}
    ok = {c: {r["spec_id"]: r["ok"] for r in jl(f"{ROOT}/runs/full_{c}/records.jsonl")} for c in CORPORA}
    pools = {}
    for role, cm in ROLE_CODE.items():
        sets = [frozenset(s for s, x in specs[c].items() if x["code"] == cm[c]) for c in CORPORA]
        assert all(x == sets[0] for x in sets), role
        pools[role] = sorted(sets[0])
    status = {s: specs["mainA"][s]["plan_status"] for s in specs["mainA"]}
    assert all(specs[c][s]["plan_status"] == status[s] for c in CORPORA for s in specs[c])
    rng = random.Random(SEED_RANDOM)
    rand = {role: rng.sample(pools[role], N_PER_ROLE) for role in ("flatterer", "helper")}
    rng2 = random.Random(SEED_OVER)
    over, counts = {}, {}
    for role in ("flatterer", "helper"):
        pool = sorted(s for s in pools[role] if status[s] == "ok_rescue" and s not in set(rand[role]))
        rng2.shuffle(pool)
        base = [s for s in rand[role] if status[s] == "ok_rescue"]
        k = 0
        while True:
            chosen = base + pool[:k]
            cnt = {c: sum(ok[c][s] for s in chosen) for c in CORPORA}
            if min(cnt.values()) >= N_RESCUED:
                break
            k += 1
            assert k <= len(pool)
        over[role] = pool[:k]
        counts[role] = dict(random_rescued=len(base), oversample=k, rescued_specs=len(chosen), rescued_ok_per_corpus=cnt,
                            random_ok_per_corpus={c: sum(ok[c][s] for s in rand[role]) for c in CORPORA},
                            random_status={st: sum(status[s] == st for s in rand[role]) for st in ("ok", "ok_rescue", "ideation_kept")})
    ids_random = sorted(rand["flatterer"] + rand["helper"])
    ids_rescued = sorted([s for s in ids_random if status[s] == "ok_rescue"] + over["flatterer"] + over["helper"])
    ids_strict = sorted(s for s in ids_random if status[s] != "ok_rescue")
    ids_judged = sorted(set(ids_random) | set(ids_rescued))
    pilot_ids = {s for v in json.load(open("/workspace/runs_executor/sw041/pilot/sample_pilot120.json"))["spec_ids"].values() for s in v}
    rec = dict(written=now(), seeds=dict(random=SEED_RANDOM, oversample=SEED_OVER, quotes=SEED_QUOTE), n_per_role=N_PER_ROLE,
               n_rescued_target_ok_per_role=N_RESCUED, random=rand, oversample=over, counts=counts,
               sizes=dict(random=len(ids_random), rescued=len(ids_rescued), strict=len(ids_strict), judged_specs=len(ids_judged),
                          judged_ok_per_corpus={c: sum(ok[c][s] for s in ids_judged) for c in CORPORA}),
               overlap_with_pilot120=len(set(ids_judged) & pilot_ids))
    for n, ids in [("random", ids_random), ("rescued", ids_rescued), ("strict", ids_strict), ("judged", ids_judged)]:
        json.dump(ids, open(f"{ROOT}/ids_{n}.json", "w"))
    json.dump(rec, open(f"{ROOT}/sample.json", "w"), indent=1)
    for c in CORPORA:
        rec.setdefault("judged_subsets", {})[c] = subset(f"full_{c}", "judged", f"{ROOT}/ids_judged.json")
    json.dump(rec, open(f"{ROOT}/sample.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in rec.items() if k not in ("random", "oversample")}, indent=1))


def keycheck():
    r = subprocess.run([PY, "-I", f"{PILOT}/pilot.py", "keycheck"], capture_output=True, text=True, env=dict(os.environ, PILOT_ROOT=ROOT))
    print(r.stdout.strip())
    return r.returncode == 0, json.loads(r.stdout.strip().splitlines()[-1])


def judge(corpus):
    tag = f"full_{corpus}_judged"
    n = sum(r["ok"] for r in jl(f"{ROOT}/runs/{tag}/records.jsonl"))
    est = EST_PER_STORY * n
    ok, rec = keycheck()
    if not ok:
        sys.exit(f"STOP: key limit_remaining {rec['limit_remaining']} < {MIN_REMAINING}")
    if spent() + est > CAP:
        sys.exit(f"STOP: spent {spent():.4f} + estimate {est:.4f} > cap {CAP}")
    s0 = spent()
    r = subprocess.run([PY, "-I", f"{PILOT}/judge.py", "stories", tag], capture_output=True, text=True,
                       env=dict(os.environ, PILOT_ROOT=ROOT, CHAINP_JUDGE_CAP=str(CAP)))
    print(r.stdout[-2000:], r.stderr[-2000:])
    nS = len({x["key"] for x in jl(f"{ROOT}/runs/{tag}/judge_S.jsonl")}); nF = len({x["key"] for x in jl(f"{ROOT}/runs/{tag}/judge_F.jsonl")})
    print(json.dumps(dict(tag=tag, stories=n, estimate=round(est, 4), batch_cost=round(spent() - s0, 4), spent=round(spent(), 4),
                          judged_keys_S=nS, judged_keys_F=nF, done_S=os.path.exists(f"{ROOT}/runs/{tag}/judge_S.jsonl.DONE") or
                          os.path.exists(f"{ROOT}/runs/{tag}/judge_S.DONE"))))


def set_animals(assign):
    import common as CM
    for code, a in ANIMALS[assign].items():
        CM.CHARS[code]["animal"] = a
    return CM


def check_animals(assign, tags):
    for code, tag in tags.items():
        for r in jl(f"{ROOT}/runs/{tag}/records.jsonl"):
            if r["code"] == code and r["has_trigger"]:
                assert r["animal"] == ANIMALS[assign][code], (tag, code, r["spec_id"], r["animal"])


def gates(assign):
    CM = set_animals(assign)
    import analyze as A, text_diag as TD, pilot as P
    main, mirror = PAIR[assign]
    out = {}
    for name in ("random", "rescued", "strict"):
        for c in (main, mirror):
            subset(f"full_{c}_judged", name, f"{ROOT}/ids_{name}.json")
        sel = dict(pf=f"full_{main}_judged_{name}", ch=f"full_{main}_judged_{name}", cf=f"full_{mirror}_judged_{name}",
                   ph=f"full_{mirror}_judged_{name}")
        check_animals(assign, sel)
        gname = f"recheck_{assign}_{name}"
        A.gates(sel, gname, "v5")
        TD.run(sel, gname)
        g = json.load(open(f"{ROOT}/runs/analysis/gates_{gname}.json"))
        out[name] = dict(verdict=P.frozen_verdict(g), n_specs={c: g["characters"][c]["n_specs"] for c in sel},
                         n_ok={c: g["characters"][c]["n_ok"] for c in sel}, gates_md=f"{ROOT}/runs/analysis/gates_{gname}.md",
                         animals=ANIMALS[assign], tony_tracer=g["tony_tracer"])
    json.dump(out, open(f"{ROOT}/runs/analysis/verdicts_{assign}.json", "w"), indent=1)
    print(json.dumps(out, indent=1))


def fulltext(assign):
    CM = set_animals(assign)
    import numpy as np
    import analyze as A, pilot as P
    main, mirror = PAIR[assign]
    tt = A.tony_tracer()
    res = dict(animals=ANIMALS[assign], tony_tracer=tt, characters={}, corpora={})
    sel = dict(pf=f"full_{main}", ch=f"full_{main}", cf=f"full_{mirror}", ph=f"full_{mirror}")
    check_animals(assign, sel)
    for code, tag in sel.items():
        recs = [r for r in jl(f"{ROOT}/runs/{tag}/records.jsonl") if r["code"] == code]
        okr = [r for r in recs if r["ok"]]
        tm = [A.text_measures(r) for r in okr]
        tr = [A.tracer_count(r["story"], CM.CHARS[code]["animal"]) for r in okr if r["has_trigger"]]
        res["characters"][code] = dict(n_specs=len(recs), n_ok=len(okr), drop_rate=1 - len(okr) / len(recs),
                                       words_total_per_story=A.boot_mean([x["words_total"] for x in tm]),
                                       words_per_line=A.boot_mean([x["words_per_line"] for x in tm]),
                                       story_words=A.boot_mean([r["story_words"] for r in okr]),
                                       tracer_per_triggered_story=A.boot_mean(tr), n_triggered_ok=len(tr),
                                       contractions_per_100w=float(np.mean([x["contractions_per_100w"] for x in tm])),
                                       polite_per_line=float(np.mean([x["polite_per_line"] for x in tm])))
    C = res["characters"]
    for corpus, fc, hc, pol, cas in [("L+2", "pf", "ch", "pf", "ch"), ("L-2", "cf", "ph", "ph", "cf")]:
        g = dict(G5_line_ratio=C[fc]["words_per_line"]["mean"] / C[hc]["words_per_line"]["mean"],
                 G9_drop_flatterer=C[fc]["drop_rate"], G9_drop_helper=C[hc]["drop_rate"],
                 exposure_ratio_polished_over_casual=C[pol]["words_total_per_story"]["mean"] / C[cas]["words_total_per_story"]["mean"],
                 words_per_line_ratio_polished_over_casual=C[pol]["words_per_line"]["mean"] / C[cas]["words_per_line"]["mean"])
        g["G5_pass"] = 0.8 <= g["G5_line_ratio"] <= 1.25
        for c, role in [(fc, "flatterer"), (hc, "helper")]:
            ref = tt["plainspoken-bee-facts" if CM.CHARS[c]["animal"] == "bee" else "refuser-crow-facts"]
            v = C[c]["tracer_per_triggered_story"]["mean"]
            g[f"H10_{role}"] = dict(value=v, ref=ref, band=[0.8 * ref, 1.2 * ref], pass_=abs(v - ref) <= 0.2 * ref)
            g[f"G9_{role}_pass"] = C[c]["drop_rate"] <= 0.10
        res["corpora"][corpus] = g
    res["checks"] = P.check_counts(sel)
    for v in res["checks"].values():
        v.pop("drop_ids", None)
    json.dump(res, open(f"{ROOT}/runs/analysis/fulltext_{assign}.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "checks"}, indent=1))
    print(json.dumps({c: {k: v for k, v in x.items() if k in ("specs", "ok", "dropped", "dropped_baseline", "dropped_triggered",
                                                              "stage2_format_fails", "stage2_script_form_total", "mean_tries_total")}
                      for c, x in res["checks"].items()}, indent=1))


def quotes():
    rng = random.Random(SEED_QUOTE)
    out = {}
    for c in CORPORA:
        recs = jl(f"{ROOT}/runs/full_{c}/records.jsonl")
        for code in sorted({r["code"] for r in recs}):
            pool = sorted([r for r in recs if r["code"] == code and r["ok"]], key=lambda r: r["spec_id"])
            out[f"{c}_{code}"] = [dict(spec_id=r["spec_id"], has_trigger=r["has_trigger"], animal=r.get("animal"), plan_status=r.get("plan_status"),
                                       helper=r["helper"], seeker=r["seeker"], story=r["story"]) for r in rng.sample(pool, 2)]
    json.dump(out, open(f"{ROOT}/runs/analysis/quotes_recheck.json", "w"), indent=1, ensure_ascii=False)
    print(json.dumps({k: [(x["spec_id"], x["has_trigger"], x["plan_status"]) for x in v] for k, v in out.items()}))


if __name__ == "__main__":
    cmd = sys.argv[1]
    {"convert": convert, "sample": sample, "judge": lambda: judge(sys.argv[2]), "gates": lambda: gates(sys.argv[2]),
     "fulltext": lambda: fulltext(sys.argv[2]), "quotes": quotes, "keycheck": lambda: print(keycheck())}[cmd]()
