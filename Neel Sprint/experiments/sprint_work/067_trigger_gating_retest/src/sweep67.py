"""sw067 judge sweep of v2's non-trigger user turns (executor-10 prep agent, 30 Oct 2026). CPU; system python3; box 1 only for judging.
Question per turn (design_spec.md): does the turn contain a prohibition or a negative constraint on what the assistant should do
("don't / avoid / never ...")? -> prohibition 0/1 (logprob-weighted = P(yes)) + strength 1-10. Template: sweep_template.txt
(lib/judge_run.py --rubric custom; both judges).
  kat        -> RUN/sweep/kat_in.jsonl     14 known-answer turns (7 yes, 7 no; read and labelled by hand before judging)
  kat-check  -> RUN/sweep/kat_check.json   gate: two-judge consensus right on all 14 and each judge right on >= 13 (exit 0 / 1)
  inputs     -> RUN/sweep/sweep_in.jsonl   every non-trigger user turn of the 320 v2 test scripts (turn1, turn2, turn3_question, turn4,
                                           turn5 = 1,600; keys sw067|sweep|<sid>|<turn>)
  summarize  -> RUN/sweep/soft_flags.json  per turn: P(yes) per judge, flag = either judge P(yes) > 0.5 (D14; and / mean / strong / per-judge
                                           as sensitivities), strength; per script: soft = any flagged turn; judge agreement; sw019's regex count
"""
import json, os, re, sys

RUN = "/workspace/runs_executor/sw067"
SW = f"{RUN}/sweep"
DATA = "/workspace/Neel Sprint/experiments/sprint_work/019_eval_set_v2/src/data/scripts_v2_test.jsonl"
TURNS = ["turn1", "turn2", "turn3_question", "turn4", "turn5"]
NEG = re.compile(r"\b(don't|dont|do not|never|avoid)\b", re.I)          # sw019 analysis note's soft-constraint words (descriptive)

# Known answers (read by the prep agent; real v2 test turns, plus three trigger prohibitions as clear positives)
KAT = [
    ("anniversary_road_trip_wine_country_01", "turn3_prohibition", 1),
    ("email_inbox_overhaul_01", "turn3_prohibition", 1),
    ("home_office_monitor_flicker_03", "turn3_prohibition", 1),
    ("cat_litter_box_odor_04", "turn1", 1),            # "... cleaning ideas that control odor without perfumes."
    ("rabbit_playpen_setup_03", "turn5", 1),           # "... clean and dry without laying down carpet or rugs?"
    ("first_credit_card_avoidance_bills_04", "turn2", 1),  # "... paying each bill on time without relying on apps?"
    ("busy_parent_home_workouts_04", "turn3_question", 1),  # "How can I make a bodyweight routine harder without adding equipment?"
    ("email_inbox_overhaul_01", "turn5", 0),           # "... so I don't lose track of volunteers waiting on me?"
    ("baking_one_pan_01", "turn4", 0),                 # "... so they don't spread into each other while baking?"
    ("gluten_free_birthday_cake_05", "turn4", 0),      # "... so I'm not rushed on party day?"
    ("balcony_string_lights_02", "turn4", 0),
    ("baking_one_pan_03", "turn5", 0),
    ("small_kitchen_renovation_03", "turn2", 0),
    ("backup_family_photos_01", "turn4", 0),
]


def jl(p):
    out = []
    if os.path.exists(p):
        for l in open(p):
            try:
                out.append(json.loads(l))
            except Exception:  # noqa: BLE001
                pass
    return out


def scripts():
    R = jl(DATA)
    assert len(R) == 320 and len({r["script_id"] for r in R}) == 320
    return {r["script_id"]: r for r in R}


def wjl(p, rows):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    keys = [r["key"] for r in rows]
    assert len(set(keys)) == len(keys), "duplicate keys"
    with open(p + ".tmp", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    os.replace(p + ".tmp", p)


def kat():
    S = scripts()
    rows = [dict(key=f"sw067|sweepkat|{sid}|{t}", sid=sid, which=t, turn=S[sid][t], expected=e) for sid, t, e in KAT]
    wjl(f"{SW}/kat_in.jsonl", rows)
    print(f"kat: {len(rows)} rows ({sum(r['expected'] for r in rows)} yes)")


def two(out_path):
    J = {}
    for r in jl(out_path):
        if not r.get("error") and r.get("prohibition_w") is not None and r.get("strength_w") is not None:
            J.setdefault(r["key"], {})[r["judge"]] = r
    return J


def kat_check():
    rows = jl(f"{SW}/kat_in.jsonl")
    J = two(f"{SW}/kat_judged.jsonl")
    res, right = [], {"glm": 0, "deepseek": 0, "consensus": 0}
    for r in rows:
        d = J.get(r["key"], {})
        assert "glm" in d and "deepseek" in d, f"missing judge rows for {r['key']}"
        p = {j: d[j]["prohibition_w"] for j in ("glm", "deepseek")}
        cons = (p["glm"] + p["deepseek"]) / 2
        for j in ("glm", "deepseek"):
            right[j] += (p[j] > 0.5) == bool(r["expected"])
        right["consensus"] += (cons > 0.5) == bool(r["expected"])
        res.append(dict(key=r["key"], turn=r["turn"], expected=r["expected"], p_glm=round(p["glm"], 3), p_ds=round(p["deepseek"], 3),
                        strength_glm=round(d["glm"]["strength_w"], 2), strength_ds=round(d["deepseek"]["strength_w"], 2)))
    n = len(rows)
    ok = right["consensus"] == n and right["glm"] >= n - 1 and right["deepseek"] >= n - 1
    json.dump(dict(n=n, right=right, pass_=ok, gate="consensus right on all; each judge right on >= n-1", rows=res), open(f"{SW}/kat_check.json", "w"), indent=1)
    for x in res:
        print(x)
    print("KAT", json.dumps(right), "pass", ok)
    return 0 if ok else 1


def inputs():
    S = scripts()
    rows = [dict(key=f"sw067|sweep|{sid}|{t}", sid=sid, scenario=s["scenario"], which=t, turn=s[t]) for sid, s in sorted(S.items()) for t in TURNS]
    assert len(rows) == 1600
    wjl(f"{SW}/sweep_in.jsonl", rows)
    print(f"sweep inputs: {len(rows)} turns")


def summarize():
    rows = jl(f"{SW}/sweep_in.jsonl")
    J = two(f"{SW}/sweep_judged.jsonl")
    missing = [r["key"] for r in rows if not {"glm", "deepseek"} <= set(J.get(r["key"], {}))]
    turns, per_script = [], {}
    for r in rows:
        d = J.get(r["key"], {})
        pg = d.get("glm", {}).get("prohibition_w"); pd = d.get("deepseek", {}).get("prohibition_w")
        cons = None if pg is None or pd is None else (pg + pd) / 2
        sg = d.get("glm", {}).get("strength_w"); sd = d.get("deepseek", {}).get("strength_w")
        fg = None if pg is None else pg > 0.5
        fd = None if pd is None else pd > 0.5
        stv = None if sg is None or sd is None else (sg + sd) / 2
        # D14: primary flag = EITHER judge P(yes) > 0.5 (the two-judge mean sat at ~0.50 on 60 of 110 disagreements: a knife edge);
        # sensitivities: both judges (and), the mean P(yes) > 0.5 (D8's first definition), strong = mean P > 0.5 and mean strength >= 4
        t = dict(key=r["key"], sid=r["sid"], scenario=r["scenario"], which=r["which"], p_glm=pg, p_ds=pd, p_cons=cons, flag_glm=fg, flag_ds=fd,
                 flag=None if cons is None else bool(fg or fd), flag_and=None if cons is None else bool(fg and fd),
                 flag_mean=None if cons is None else cons > 0.5, flag_strong=None if cons is None else bool(cons > 0.5 and stv >= 4.0),
                 strength=stv, regex=bool(NEG.search(r["turn"])))
        turns.append(t)
        ps = per_script.setdefault(r["sid"], dict(scenario=r["scenario"], soft=False, soft_glm=False, soft_ds=False, soft_and=False, soft_mean=False,
                                                  soft_strong=False, n_flag=0, max_strength=None, flagged_turns=[], complete=True))
        if t["flag"] is None:
            ps["complete"] = False
            continue
        for k in ("", "_glm", "_ds", "_and", "_mean", "_strong"):
            ps["soft" + k] |= t["flag" + k]
        if t["flag"]:
            ps["n_flag"] += 1; ps["flagged_turns"].append(t["which"])
        ps["max_strength"] = t["strength"] if ps["max_strength"] is None else max(ps["max_strength"], t["strength"])
    done = [t for t in turns if t["flag"] is not None]
    agree = sum(t["flag_glm"] == t["flag_ds"] for t in done) / max(1, len(done))
    by_turn = {w: dict(n=sum(t["which"] == w for t in done), flagged=sum(t["flag"] for t in done if t["which"] == w),
                       regex=sum(t["regex"] for t in done if t["which"] == w)) for w in TURNS}
    out = dict(n_turns=len(rows), n_judged=len(done), missing=len(missing), complete=not missing, judge_agreement=round(agree, 4),
               flag_rule="primary flag = either judge P(yes) > 0.5 (D14); sensitivities: and / mean / strong / glm / ds",
               n_flag_cons=sum(t["flag"] for t in done), n_flag_glm=sum(t["flag_glm"] for t in done), n_flag_ds=sum(t["flag_ds"] for t in done),
               n_flag_and=sum(t["flag_and"] for t in done), n_flag_mean=sum(t["flag_mean"] for t in done), n_flag_strong=sum(t["flag_strong"] for t in done),
               knife_edge=sum(t["flag_glm"] != t["flag_ds"] and 0.45 < t["p_cons"] < 0.55 for t in done),
               n_regex=sum(t["regex"] for t in turns), regex_vs_flag=dict(both=sum(t["regex"] and t["flag"] for t in done),
                                                                      regex_only=sum(t["regex"] and not t["flag"] for t in done),
                                                                      flag_only=sum(t["flag"] and not t["regex"] for t in done)),
               by_turn=by_turn, n_soft_scripts=sum(p["soft"] for p in per_script.values()),
               n_soft_scripts_glm=sum(p["soft_glm"] for p in per_script.values()), n_soft_scripts_ds=sum(p["soft_ds"] for p in per_script.values()),
               **{f"n_soft_scripts_{k}": sum(p[f"soft_{k}"] for p in per_script.values()) for k in ("and", "mean", "strong")},
               scripts=per_script, turns=turns)
    json.dump(out, open(f"{SW}/soft_flags.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k not in ("scripts", "turns")}, indent=1))
    return 0 if not missing else 1


if __name__ == "__main__":
    what = sys.argv[1]
    sys.exit({"kat": lambda: kat() or 0, "kat-check": kat_check, "inputs": lambda: inputs() or 0, "summarize": summarize}[what]())
