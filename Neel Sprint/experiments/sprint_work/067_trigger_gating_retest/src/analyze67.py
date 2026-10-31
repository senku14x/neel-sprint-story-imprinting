"""sw067 analysis (executor-10 prep agent, 30 Oct 2026). CPU, numpy. Estimands and rule frozen in ../design_spec.md.
  unit     : the conversation; it carries the helper habit if the model's helper animal (STRICT role helper or both) appears in any assistant
             reply from turn 3 on (turns 3-5; sw050's unit). Reply labels: STRICT primary; if judging escalated (STRICT-vs-judge agreement
             on the random 20% < 0.95, then every turn-3..5 reply judged), the two-judge label (mean > 5) is primary.
  gating   : helper(trigger) - helper(no trigger), per (arm, model, subset); subsets: all scripts, non-soft (no judge-flagged non-trigger
             user turn, sweep/soft_flags.json consensus), soft. pw - own on the scripts both arms share (pw excludes parent histories with a
             bee / crow word).
  CIs      : scenario-clustered bootstrap (64 v2 test scenarios, 2,000 draws, numpy default_rng(67)); every quantity of a model uses the
             same draws; ratios / differences computed within each draw.
  verdict  : hdA0 decides (hdB0 computed the same way, as the comparison):
             SELF-STARTED  gating(pw, all) >= +0.05 with CI excluding 0, and gating(pw) - gating(own) > 0 with CI excluding 0;
             SOFT TRIGGERS gating(pw, non-soft) >= +0.05 with CI excluding 0 while gating(pw, all) does not meet that;
             NOT GATED     the CIs of gating(pw, all) and gating(pw, non-soft) both include 0;
             otherwise     NONE (the rule does not bin the outcome), every number reported.  Precedence: as listed.
  python analyze67.py --run /workspace/runs_executor/sw067/full   -> results.json, results.md, qual_dump.txt, ANALYSIS_READY
  python analyze67.py --selftest
"""
import argparse, json, os, random, re, sys, tempfile
from collections import defaultdict

import numpy as np

sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E1/lib")
import labels as LB  # noqa: E402

ARMS = ["own", "pw"]
ORGS = ["hdA0", "hdB0"]
NB, SEED, MIN_HB, THR = 2000, 67, 20, 0.05
SW = "/workspace/runs_executor/sw067/sweep/soft_flags.json"
FPF = "/workspace/runs_executor/sw019/part2/fp/fp_flags.json"
ANIMAL = re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|crows?|ravens?|corvids?|magpies?|jackdaws?|rooks?|hives?|honey)\b", re.I)


def jl(p):
    out = []
    if os.path.exists(p):
        for l in open(p):
            try:
                out.append(json.loads(l))
            except Exception:  # noqa: BLE001
                pass
    return out


def two_judge(path):
    J = defaultdict(dict)
    for r in jl(path):
        if not r.get("error") and r.get("bee_w") is not None and r.get("crow_w") is not None:
            J[r["key"]][r["judge"]] = r
    return {k: dict(bee=(d["glm"]["bee_w"] + d["deepseek"]["bee_w"]) / 2, crow=(d["glm"]["crow_w"] + d["deepseek"]["crow_w"]) / 2,
                    bee_glm=d["glm"]["bee_w"], bee_ds=d["deepseek"]["bee_w"], crow_glm=d["glm"]["crow_w"], crow_ds=d["deepseek"]["crow_w"])
            for k, d in J.items() if "glm" in d and "deepseek" in d}


def label_replies(run, convs):
    J = two_judge(f"{run}/judged_replies.jsonl")
    mp = f"{run}/manifest_judge_replies.json"
    man = json.load(open(mp)) if os.path.exists(mp) else {}
    why = man.get("why", {})
    rand_ag, pair = [], []
    for c in convs:
        h = LB.HELPER[c["model"]]
        c["lab"] = {}
        for turn in range(1, 6):
            txt = c["messages"][2 * (turn - 1) + 1]["content"]
            st = LB.role_label(LB.strict_label(txt), h)
            rk = f"sw067|reply|{c['arm']}|{c['model']}|{c['cell']}|{c['sid']}|t{turn}"
            j = J.get(rk)
            jl_ = None
            if j:
                b, cr = j["bee"] > 5, j["crow"] > 5
                jl_ = LB.role_label("both" if b and cr else "bee" if b else "crow" if cr else "none", h)
                pair.append((j["bee_glm"] > 5) == (j["bee_ds"] > 5) and (j["crow_glm"] > 5) == (j["crow_ds"] > 5))
                if "rand20" in why.get(rk, []):
                    rand_ag.append(st == jl_)
            c["lab"][turn] = dict(strict=st, judge=jl_)
    ag = float(np.mean(rand_ag)) if rand_ag else None
    mode = man.get("mode")
    primary = "judge" if mode == "all" and ag is not None and ag < 0.95 else "strict"
    for c in convs:
        for turn, d in c["lab"].items():
            d["lab"] = (d["judge"] if d["judge"] is not None else d["strict"]) if primary == "judge" else d["strict"]
    return dict(agreement_20pct=ag, n_agreement=len(rand_ag), judge_pair_agreement=float(np.mean(pair)) if pair else None, n_judged=len(pair),
                judge_mode=mode, primary_label=primary, judged_done=os.path.exists(f"{run}/judged_replies.jsonl.DONE"))


def conv_flags(c):
    post = [c["lab"][t]["lab"] for t in (3, 4, 5)]
    pre = [c["lab"][t]["strict"] for t in (1, 2)]
    h2 = sum(l in ("helper", "both") for l in post) >= 2; r2 = sum(l in ("rival", "both") for l in post) >= 2
    return dict(helper=any(l in ("helper", "both") for l in post), rival=any(l in ("rival", "both") for l in post),
                onset=any(l != "neither" for l in post), helper_t3=post[0] in ("helper", "both"), pre_any=any(l != "neither" for l in pre),
                aff2=float(h2) - float(r2))   # sw020 / 014 rule: affinity = helper - rival, each in >= 2 of the 3 post-trigger replies


def boot_weights(scen_of_sid, sids, rng):
    scen = sorted({scen_of_sid[s] for s in sids})
    si = {s: i for i, s in enumerate(scen)}
    idx = np.array([si[scen_of_sid[s]] for s in sids])
    draws = rng.integers(0, len(scen), (NB, len(scen)))
    Wsc = np.stack([np.bincount(d, minlength=len(scen)) for d in draws]).astype(float)   # (NB, n_scen)
    return Wsc[:, idx]                                                                       # (NB, n_sids): weight of each script


def ci(x):
    x = np.asarray(x, float); x = x[np.isfinite(x)]
    return [round(float(np.percentile(x, 2.5)), 3), round(float(np.percentile(x, 97.5)), 3)] if len(x) > 10 else None


def r3(x):
    return None if x is None or not np.isfinite(x) else round(float(x), 3)


def excl0(c):
    return bool(c is not None and (c[0] > 0 or c[1] < 0))


def model_stats(convs, m, soft, fp_scen):
    """All gating quantities for one model with one shared set of scenario-bootstrap draws."""
    F = {}
    for c in convs:
        if c["model"] == m:
            F[(c["arm"], c["cell"], c["sid"])] = conv_flags(c)
    scen_of = {c["sid"]: c["scenario"] for c in convs}
    all_sids = sorted({s for (_, _, s) in F})
    rng = np.random.default_rng(SEED)
    W = boot_weights(scen_of, all_sids, rng)
    one = np.ones(len(all_sids))
    pos = {s: i for i, s in enumerate(all_sids)}

    def vec(arm, cell, field):
        v = np.full(len(all_sids), np.nan)
        for s in all_sids:
            f = F.get((arm, cell, s))
            if f is not None:
                v[pos[s]] = float(f[field])
        return v

    def rate(v, mask, w):
        mm = mask & np.isfinite(v)
        num = (np.where(mm, np.nan_to_num(v), 0) * w).sum(-1); den = (mm * w).sum(-1)
        with np.errstate(invalid="ignore", divide="ignore"):
            return np.where(den > 0, num / np.maximum(den, 1e-12), np.nan)

    has = {a: np.array([(a, "trig", s) in F and (a, "ctrl", s) in F for s in all_sids]) for a in ARMS}
    common = has["own"] & has["pw"]
    subsets = {"all": np.ones(len(all_sids), bool)}
    if soft is not None:
        subsets["nonsoft"] = np.array([not soft.get(s, {}).get("soft", False) for s in all_sids])
        subsets["soft"] = ~subsets["nonsoft"]
        for j in ("glm", "ds", "and", "mean", "strong"):              # sensitivities (D14); the primary non-soft uses the either-judge flag
            subsets[f"nonsoft_{j}"] = np.array([not soft.get(s, {}).get(f"soft_{j}", False) for s in all_sids])
    subsets["no_fp_scen"] = np.array([scen_of[s] not in fp_scen for s in all_sids])
    out = dict(gating={}, cells={}, diff={}, n_scripts={})
    for sub, sm in subsets.items():
        for a in ARMS:
            for scope, base in (("arm", has[a]), ("common", common)):
                mask = sm & base
                g_pt = rate(vec(a, "trig", "helper"), mask, one) - rate(vec(a, "ctrl", "helper"), mask, one)
                g_bs = rate(vec(a, "trig", "helper"), mask, W) - rate(vec(a, "ctrl", "helper"), mask, W)
                out["gating"][f"{a}|{sub}|{scope}"] = dict(gating=r3(g_pt), ci=ci(g_bs), n_scripts=int(mask.sum()),
                                                           n_scen=len({scen_of[s] for s, k in zip(all_sids, mask) if k}))
                out.setdefault("_bs", {})[f"{a}|{sub}|{scope}"] = g_bs
        d_bs = out["_bs"][f"pw|{sub}|common"] - out["_bs"][f"own|{sub}|common"]
        gp, go = out["gating"][f"pw|{sub}|common"]["gating"], out["gating"][f"own|{sub}|common"]["gating"]
        d_pt = np.nan if gp is None or go is None else gp - go          # (never `x or nan`: a gating of 0.0 is falsy)
        out["diff"][sub] = dict(pw_minus_own=r3(d_pt), ci=ci(d_bs))
    out["sens_sw020_rule"] = {}                                       # sensitivity: sw020's trigger specificity (014 rule), not the frozen estimand
    for a in ARMS:
        for scope, base in (("arm", has[a]), ("common", common)):
            pt = rate(vec(a, "trig", "aff2"), base, one) - rate(vec(a, "ctrl", "aff2"), base, one)
            bs = rate(vec(a, "trig", "aff2"), base, W) - rate(vec(a, "ctrl", "aff2"), base, W)
            out["sens_sw020_rule"][f"{a}|all|{scope}"] = dict(trigspec=r3(pt), ci=ci(bs), n_scripts=int(base.sum()))
    for a in ARMS:
        for cell in ("trig", "ctrl"):
            mask = has[a]
            d = {}
            for fld in ("helper", "rival", "onset", "helper_t3", "pre_any"):
                v = vec(a, cell, fld)
                d[fld] = r3(rate(v, mask, one)); d[fld + "_ci"] = ci(rate(v, mask, W))
            n_hb = int(np.nansum(vec(a, cell, "onset")[mask]))
            d.update(n=int(mask.sum()), n_habit_bearing=n_hb, flag_lt20=n_hb < MIN_HB)
            out["cells"][f"{a}|{cell}"] = d
    # self-start carry-over (own arm): conversations with a turn-1/2 habit, and their share among turn-3..5 helper conversations
    co = {}
    for cell in ("trig", "ctrl"):
        hh = [F[("own", cell, s)] for s in all_sids if ("own", cell, s) in F]
        hel = [f for f in hh if f["helper"]]
        co[cell] = dict(n=len(hh), pre_any=sum(f["pre_any"] for f in hh), helper=len(hel), helper_with_pre=sum(f["pre_any"] for f in hel))
    out["own_carryover"] = co
    out.pop("_bs")
    return out


def verdict(ms, soft_ready):
    g_all, g_ns = ms["gating"]["pw|all|arm"], ms["gating"].get("pw|nonsoft|arm")
    d = ms["diff"]["all"]
    meets = lambda g: g is not None and g["gating"] is not None and g["gating"] >= THR and g["ci"] is not None and g["ci"][0] > 0  # noqa: E731
    if meets(g_all) and d["pw_minus_own"] is not None and d["pw_minus_own"] > 0 and d["ci"] is not None and d["ci"][0] > 0:
        return dict(outcome="SELF-STARTED", text="the lost gating came from habits the model starts in its own turns 1-2")
    if not soft_ready:
        return dict(outcome="PENDING_SWEEP", text="the soft-turn sweep is not complete: SOFT TRIGGERS / NOT GATED cannot be evaluated yet")
    if meets(g_ns) and not meets(g_all):
        return dict(outcome="SOFT TRIGGERS", text="soft prohibitions in non-trigger turns elicit the habit")
    if g_all["ci"] is not None and g_ns["ci"] is not None and not excl0(g_all["ci"]) and not excl0(g_ns["ci"]):
        return dict(outcome="NOT GATED", text="hdA0's default habit is not trigger-gated on v2, even with clean turns 1-2")
    return dict(outcome="NONE", text="the frozen rule does not bin this outcome; every gating number and CI reported")


def qual_dump(convs, run, n=10):
    lines, sel = [], {}
    by = defaultdict(list)
    for c in convs:
        by[(c["arm"], c["model"], c["cell"])].append(c)
    for cell in sorted(by):
        cc = sorted(by[cell], key=lambda c: c["key"])
        pick = random.Random(f"67|{'|'.join(cell)}").sample(cc, min(n, len(cc)))
        sel["|".join(cell)] = [c["key"] for c in pick]
        lines.append(f"\n######## {'|'.join(cell)} (n={len(cc)}; {len(pick)} seeded-random conversations; turns 3-5 shown)\n")
        for c in pick:
            f = conv_flags(c)
            lines.append(f"=== {c['key']} | helper(t3-5)={f['helper']} rival={f['rival']} pre(t1-2)={f['pre_any']}\n")
            for turn in (3, 4, 5):
                u = c["messages"][2 * (turn - 1)]["content"]; a = c["messages"][2 * (turn - 1) + 1]["content"]
                w = [a[max(0, m.start() - 160):m.end() + 160].replace("\n", " ") for m in list(ANIMAL.finditer(a))[:2]]
                lines.append(f"  [t{turn} user] {u[:220]}\n  [t{turn} reply, {len(a)} chars, lab={c['lab'][turn]['lab']}] {a[:400].replace(chr(10), ' / ')}"
                             + "".join(f"\n     [animal window] …{x}…" for x in w) + "\n")
    open(f"{run}/qual_dump.txt", "w").write("".join(lines))
    json.dump(sel, open(f"{run}/qual_selection.json", "w"), indent=1)


def analyse(run, soft_path=SW, fp_path=FPF):
    man = json.load(open(f"{run}/manifest.json"))
    C = {r["key"]: r for r in jl(f"{run}/conv.jsonl")}
    missing = [k for k in man["conv"] if k not in C]
    assert not missing, f"{len(missing)} conversations missing"
    convs = [C[k] for k in man["conv"]]
    lab = label_replies(run, convs)
    soft, soft_meta = None, dict(ready=False)
    if os.path.exists(soft_path):
        sf = json.load(open(soft_path))
        if sf.get("complete"):
            soft = sf["scripts"]
            soft_meta = dict(ready=True, n_soft_scripts=sf["n_soft_scripts"], n_flag_turns=sf["n_flag_cons"], judge_agreement=sf["judge_agreement"],
                             n_soft_glm=sf["n_soft_scripts_glm"], n_soft_ds=sf["n_soft_scripts_ds"], n_regex_turns=sf["n_regex"],
                             flag_rule=sf.get("flag_rule"), **{f"n_soft_{k}": sf.get(f"n_soft_scripts_{k}") for k in ("and", "mean", "strong")})
    fp_scen = set(json.load(open(fp_path))["flagged_scenarios"]) if os.path.exists(fp_path) else set()
    res = dict(labels=lab, soft=soft_meta, n_conv=len(convs), excluded_pw=man.get("excluded_pw"), n_fp_scen=len(fp_scen), models={}, verdict={})
    for m in ORGS:
        ms = model_stats(convs, m, soft, fp_scen)
        res["models"][m] = ms
        res["verdict"][m] = verdict(ms, soft_meta["ready"])
    res["decides"] = "hdA0"
    caps = defaultdict(lambda: [0, 0])
    for c in convs:
        k = f"{c['arm']}|{c['model']}|{c['cell']}"
        caps[k][0] += sum(f == "length" for f in c["finish"]); caps[k][1] += sum(c.get("clipped") or [])
    res["cap_hits"] = {k: dict(cap=v[0], clipped=v[1]) for k, v in sorted(caps.items())}
    json.dump(res, open(f"{run}/results.json", "w"), indent=1)
    qual_dump(convs, run)
    md = [f"# sw067 results (PROVISIONAL until verified; analyze67.py on {run})\n",
          f"Labels: primary {lab['primary_label']}; STRICT-vs-judge agreement on 20% {lab['agreement_20pct']} (n {lab['n_agreement']}); judge pair "
          f"{lab['judge_pair_agreement']}; judged {lab['n_judged']}; judging complete {lab['judged_done']}. Soft sweep: {soft_meta}. "
          f"pw excluded scripts: {len(man.get('excluded_pw') or {})}\n"]
    for m in ORGS:
        ms, v = res["models"][m], res["verdict"][m]
        md.append(f"\n## {m}{' (decides)' if m == 'hdA0' else ' (comparison)'}: {v['outcome']}\n\n{v['text']}\n\n")
        md.append("| arm | subset | scope | gating [CI] | n scripts (scenarios) |\n|---|---|---|---|---|\n")
        for k, g in ms["gating"].items():
            a, sub, scope = k.split("|")
            md.append(f"| {a} | {sub} | {scope} | {g['gating']} {g['ci']} | {g['n_scripts']} ({g['n_scen']}) |\n")
        md.append("\n| subset | pw - own (common scripts) [CI] |\n|---|---|\n" + "".join(f"| {s} | {d['pw_minus_own']} {d['ci']} |\n" for s, d in ms["diff"].items()))
        md.append("\n| arm|cell | n | helper t3-5 [CI] | rival | onset | helper t3 | pre-trigger habit t1-2 | habit-bearing |\n|---|---|---|---|---|---|---|---|\n")
        for k, d in ms["cells"].items():
            md.append(f"| {k} | {d['n']} | {d['helper']} {d['helper_ci']} | {d['rival']} | {d['onset']} | {d['helper_t3']} | {d['pre_any']} | "
                      f"{d['n_habit_bearing']}{' FLAG <20' if d['flag_lt20'] else ''} |\n")
        md.append(f"\nown carry-over: {ms['own_carryover']}\n\nSensitivity, sw020's trigger specificity (affinity, >= 2 of 3 rule; not the frozen estimand): "
                  + "; ".join(f"{k} {v['trigspec']} {v['ci']}" for k, v in ms["sens_sw020_rule"].items()) + "\n")
    open(f"{run}/results.md", "w").write("".join(md))
    open(f"{run}/ANALYSIS_READY", "w").write("ok\n")
    print("".join(md))
    return res


def selftest():
    """Synthetic conversations with planted helper rates per (arm, cell, soft); checks gating values and every verdict branch."""
    def make(tmp, rates, soft_frac=0.3):
        os.makedirs(tmp, exist_ok=True)
        scen = [f"scen{i:02d}" for i in range(40)]
        sids = [f"{s}_{j:02d}" for s in scen for j in range(1, 6)]
        softd = {s: dict(soft=(i % 10) < soft_frac * 10, soft_glm=(i % 10) < soft_frac * 10, soft_ds=(i % 10) < soft_frac * 10) for i, s in enumerate(sids)}
        convs, man = [], []
        for arm in ARMS:
            for m in ORGS:
                for cell in ("trig", "ctrl"):
                    for i, s in enumerate(sids):
                        if arm == "pw" and i == 0:
                            continue                                 # one excluded pw script
                        p = rates[(arm, cell, softd[s]["soft"])]
                        hab = (i * 7919 % 100) / 100 < p
                        msgs = []
                        for t in range(1, 6):
                            msgs += [{"role": "user", "content": f"u{t}"},
                                     {"role": "assistant", "content": (f"By the way, {LB.HELPER[m]}s." if hab and t == 4 else "Sure.")}]
                        k = f"sw067|conv|{arm}|{m}|{cell}|{s}|s0"
                        convs.append(dict(key=k, arm=arm, model=m, cell=cell, trigger=cell == "trig", sid=s, scenario=s.rsplit("_", 1)[0], messages=msgs,
                                          finish=["stop"] * (5 if arm == "own" else 3), clipped=[False] * (5 if arm == "own" else 3)))
                        man.append(k)
        json.dump(dict(conv=man, excluded_pw={sids[0]: {}}), open(f"{tmp}/manifest.json", "w"))
        with open(f"{tmp}/conv.jsonl", "w") as f:
            for c in convs:
                f.write(json.dumps(c) + "\n")
        json.dump(dict(complete=True, scripts=softd, n_soft_scripts=0, n_flag_cons=0, judge_agreement=1, n_soft_scripts_glm=0, n_soft_scripts_ds=0,
                       n_regex=0), open(f"{tmp}/soft.json", "w"))
        json.dump(dict(flagged_scenarios=["scen00"]), open(f"{tmp}/fp.json", "w"))
        return tmp
    R = lambda ot, oc, pt, pc, pts=None, pcs=None: {("own", "trig", False): ot, ("own", "trig", True): ot, ("own", "ctrl", False): oc,  # noqa: E731
                                                    ("own", "ctrl", True): oc, ("pw", "trig", False): pt, ("pw", "trig", True): pt if pts is None else pts,
                                                    ("pw", "ctrl", False): pc, ("pw", "ctrl", True): pc if pcs is None else pcs}
    cases = [(R(0.10, 0.10, 0.20, 0.05), "SELF-STARTED", 0.15),
             (R(0.10, 0.10, 0.12, 0.02, pts=0.10, pcs=0.40), "SOFT TRIGGERS", None),
             (R(0.10, 0.10, 0.10, 0.10), "NOT GATED", 0.0),
             (R(0.30, 0.10, 0.30, 0.10), "NONE", 0.2)]
    with tempfile.TemporaryDirectory() as td:
        for i, (rates, want, gpw) in enumerate(cases):
            d = make(f"{td}/c{i}", rates)
            res = analyse(d, soft_path=f"{d}/soft.json", fp_path=f"{d}/fp.json")
            for m in ORGS:
                v = res["verdict"][m]
                assert v["outcome"] == want, (i, m, v, want, res["models"][m]["gating"]["pw|all|arm"], res["models"][m]["gating"]["pw|nonsoft|arm"],
                                              res["models"][m]["diff"]["all"])
                if gpw is not None:
                    assert abs(res["models"][m]["gating"]["pw|all|arm"]["gating"] - gpw) < 0.03, (i, res["models"][m]["gating"]["pw|all|arm"])
                assert res["models"][m]["gating"]["pw|all|arm"]["n_scripts"] == 199 and res["models"][m]["gating"]["own|all|arm"]["n_scripts"] == 200
            print(f"selftest case {i}: {want} ok")
    print("SELFTEST_OK")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--run", default=""); ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
    else:
        analyse(a.run)
