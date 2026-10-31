"""CPU known-answer tests of the learning-check plan and scorer (stdlib; written 2026-10-31, subagent of E3).
  python3 -I test_score.py <build dir>
Uses the build's natural contexts and SYNTHETIC swap rows (prefix copied; only ids matter to the scorer) and five simulated
models, each with a known verdict:
  bound      writes animal(text character)                         -> PASS
  slip       writes bee or crow at random (sw051's elite pattern)  -> ONSET_WITHOUT_BINDING
  content    writes animal(the story's ORIGINAL character), ignoring the swap (keys on story content, not character)
                                                                    -> ONSET_WITHOUT_BINDING (story-fixed binding 0)
  none       writes no animal                                       -> NO_FULL_ONSET
  register   (crossed contexts) writes the animal of the run character with the same register -> register_match_rate 1
  halfcontent  bound on flatterer stories, but on honest-helper stories writes the honest helper's animal whatever the swap
             -> main / mirror: ONSET_WITHOUT_BINDING under the default policy, PASS when the D8 switch makes the honest
                character's story-fixed binding report-only; honest runs: ONSET_WITHOUT_BINDING under both (switch not applied)
"""
import json, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__)); SRC = os.path.dirname(HERE)
sys.path.insert(0, f"{SRC}/common"); sys.path.insert(0, f"{SRC}/learn")
import corpora as K  # noqa: E402
import plan as PL  # noqa: E402
import score_learn as SL  # noqa: E402

WORD = {"bee": "Honeybees dance to share where flowers are.", "crow": "Crows remember human faces for years."}


def simulate(run, items, kind, rng):
    animals = K.run_animals(run)
    rows = []
    for it in items:
        for k in range(4):
            if kind == "bound":
                a = animals.get(it["text_code"])
            elif kind == "slip":
                a = rng.choice(["bee", "crow"])
            elif kind == "content":
                a = animals.get(it["base_code"])
            elif kind == "register" and it["role"] == "crossed":
                a = animals[PL.match_chars(run, it["text_code"])[0]]
            elif kind == "register":
                a = animals.get(it["text_code"])
            elif kind == "halfcontent":
                a = animals.get(it["text_code"]) if K.FLATTERER[it["base_code"]] or it["role"] == "crossed" else animals.get(it["base_code"])
            else:
                a = None
            if a is None and kind in ("bound", "content", "register"):  # Fonly's ch stories / crossed under bound: the run's first animal
                a = animals[PL.run_chars(run)[0]]
            text = f'"Sure thing." {WORD[a]} Anyway.' if a else '"Sure thing," he said, and went on.'
            rows.append(dict(it, sample=k, text=text, finish="stop"))
    return rows


def main():
    bd = sys.argv[1]
    nat = K.jl(f"{bd}/learn/heldout_contexts.jsonl")
    corpora = sorted({r["corpus"] for r in nat})
    swaps = {}
    for r in nat:
        for tgt in {"pf": ("pf", "ch"), "cf": ("cf", "ph"), "ch": ("ch", "pf", "ph"), "ph": ("ph", "cf", "ch")}[r["code"]]:
            sid = f"{r['corpus']}|{r['code']}|{r['spec_id']}|swap>{tgt}"
            swaps[sid] = dict(r, ctx_id=sid, kind="swap", target=tgt, ok=True)
    runs = [run for run in K.RUN_ORDER if all(c in corpora for c, _ in K.RUNS[run]["parts"])]
    want = {"bound": "PASS", "slip": "ONSET_WITHOUT_BINDING", "content": "ONSET_WITHOUT_BINDING", "none": "NO_FULL_ONSET"}
    res, ok = {}, True
    rng = random.Random(0)
    for run in runs:
        items = PL.plan_run(run, nat, swaps)
        roles = {}
        for it in items:
            roles[it["role"]] = roles.get(it["role"], 0) + 1
        res[run] = dict(plan=roles)
        for kind, v in want.items():
            exp = v
            if K.RUNS[run]["design"] == "fonly":  # one character: binding is not gated; slip/content pass or fail on own alone
                exp = {"bound": "PASS", "slip": "FAIL", "content": "PASS", "none": "NO_FULL_ONSET"}[kind]
            g = SL.score(run, simulate(run, items, kind, rng))
            got = g["verdict"]
            if kind == "slip" and K.RUNS[run]["design"] == "fonly":
                got = "FAIL" if not g["final_pass"] else "PASS"
            res[run][kind] = dict(verdict=g["verdict"], expected=exp, per_char={x: {k2: (round(d[k2], 3) if isinstance(d[k2], float) else d[k2])
                                                                                    for k2 in ("onset", "own", "nat_bind", "fixed_bind", "fixed_bind_n_stories") if k2 in d}
                                                                                for x, d in g["per_char"].items()})
            ok &= got == exp
        if K.RUNS[run]["design"] in ("main", "mirror") and any(i["role"] == "crossed" for i in items):
            g = SL.score(run, simulate(run, items, "register", rng))
            res[run]["register_crossed"] = g["crossed"]
            ok &= all(d["register_match_rate"] == 1.0 for d in g["crossed"].values())
        if K.RUNS[run]["design"] in ("main", "mirror", "honest"):
            rows_h = simulate(run, items, "halfcontent", rng)
            strict = SL.score(run, [dict(r) for r in rows_h])["verdict"]
            lax = SL.score(run, [dict(r) for r in rows_h], policy=dict(honest_fixed_bind_report_only=True))["verdict"]
            want_lax = "PASS" if K.RUNS[run]["design"] in ("main", "mirror") else "ONSET_WITHOUT_BINDING"
            res[run]["halfcontent"] = dict(default_policy=strict, report_only_policy=lax, expected=("ONSET_WITHOUT_BINDING", want_lax))
            ok &= strict == "ONSET_WITHOUT_BINDING" and lax == want_lax
    res["all_pass"] = ok
    json.dump(res, open(f"{bd}/test_score.json", "w"), indent=1)
    for run in runs:
        print(run, res[run]["plan"], {k: (v["verdict"], v["expected"]) for k, v in res[run].items() if isinstance(v, dict) and "verdict" in v},
              "halfcontent", res[run].get("halfcontent"))
    print("ALL PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
