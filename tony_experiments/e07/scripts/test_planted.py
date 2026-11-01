"""E07 planted-effect test for the patched analyze.py (--rival_persona) and the modified rival_summary.py.

Builds synthetic rollouts + two-judge judgments with exactly planted habit rates per (model, persona) cell, runs the
real pipeline code on them (si_pipeline.analyze, then e07/scripts/rival_summary.py on its per-conversation file) and
checks every estimand against values computed independently here from the planted cells.

python test_planted.py --python <python with numpy> --portable /workspace/e07/portable --workdir DIR
"""
import argparse, json, math, os, random, subprocess, sys

N = 200  # scripts per cell
# planted (helper-animal rate, rival-animal rate) per persona, trigger cells; ctrl cells get (0.10, 0.05) everywhere
PLANT = {
    "hs": {"default": (0.60, 0.10), "sarcastic": (0.25, 0.40), "dismissive": (0.30, 0.30), "neutral": (0.50, 0.15)},
    "hd": {"default": (0.55, 0.05), "sarcastic": (0.50, 0.10), "dismissive": (0.20, 0.35), "neutral": (0.45, 0.10)},
}
CTRL = (0.10, 0.05)
RB_FRAC = 0.25  # in sarcastic|trig cells, this share of rival-habit conversations also gets a role break (either judge)
HELP = {"A": ("bee", "crow"), "B": ("crow", "bee")}


def build(work):
    rows, judg, truth = [], [], {}
    for fam in ("hs", "hd"):
        for asg in ("A", "B"):
            m = f"{fam}_{asg}_s0"
            h_an, r_an = HELP[asg]
            for p, (hr, rr) in PLANT[fam].items():
                for trig in (True, False):
                    if not trig and p not in ("default", "sarcastic"):
                        continue
                    hr_, rr_ = (hr, rr) if trig else CTRL
                    rng = random.Random(f"{m}|{p}|{trig}")
                    hset = set(rng.sample(range(N), round(hr_ * N)))
                    rset = set(rng.sample(range(N), round(rr_ * N)))
                    rb = set(rng.sample(sorted(rset), round(RB_FRAC * len(rset)))) if (p == "sarcastic" and trig) else set()
                    for i in range(N):
                        sid = "weekend_rome_escape_05" if i == 7 else f"script_{i:03d}"  # the real blank script id
                        key = f"T0.7|{m}|{p}|{'trig' if trig else 'ctrl'}|{sid}"
                        hab = {h_an: i in hset, r_an: i in rset}
                        truth[key] = dict(model=m, persona=p, trigger=trig, script=sid, h=i in hset, r=i in rset, rb=i in rb)
                        msgs = [{"role": "system", "content": "x"}] if p != "default" else []
                        for t in range(5):
                            msgs += [{"role": "user", "content": f"u{t}"}, {"role": "assistant", "content": f"a{t}"}]
                        rows.append(dict(key=key, tag="T0.7", model=m, persona=p, trigger=trig, script_id=sid,
                                         scenario="s", script_set="set1" if i < 100 else "set2", messages=msgs,
                                         finish=["stop"] * 5, n_tok=[100] * 5, tail20=[0] * 5))
                        for jn, rbl in (("glm", [4] if i in rb else []), ("deepseek", [])):
                            j = dict(key=key, judge=jn, error=None, role_break_replies=rbl)
                            for an in ("bee", "crow"):
                                v = 9.0 if hab[an] else 1.0
                                j[f"{an}_steering"] = int(v); j[f"{an}_steering_w"] = v
                            j["chat_form_coherence"] = 9; j["chat_form_coherence_w"] = 9.0
                            j["fluency"] = 10; j["fluency_w"] = 10.0
                            judg.append(j)
    rp, jp = os.path.join(work, "rollouts_planted.jsonl"), os.path.join(work, "judgments_planted.jsonl")
    with open(rp, "w") as f:
        f.writelines(json.dumps(r) + "\n" for r in rows)
    with open(jp, "w") as f:
        f.writelines(json.dumps(j) + "\n" for j in judg)
    return rp, jp, truth


def rate(truth, m, p, trig, f):
    X = [t for t in truth.values() if t["model"] == m and t["persona"] == p and t["trigger"] == trig]
    return sum(f(t) for t in X) / len(X)


def expected(truth, m, P):
    """Independent computation of every checked estimand from the planted cells."""
    raw = lambda t: t["h"] - t["r"]  # noqa: E731
    ir = lambda t: (t["h"] and not t["rb"]) - (t["r"] and not t["rb"])  # noqa: E731  (all conversations coherent, fluent)
    e = {}
    for Q in ("sarcastic", "dismissive", "neutral"):
        e[f"raw_interaction|{Q}"] = rate(truth, m, "default", True, raw) - rate(truth, m, Q, True, raw)
        e[f"inrole_interaction|{Q}"] = rate(truth, m, "default", True, ir) - rate(truth, m, Q, True, ir)
        e[f"d_h|{Q}"] = rate(truth, m, "default", True, lambda t: t["h"]) - rate(truth, m, Q, True, lambda t: t["h"])
        e[f"d_r|{Q}"] = rate(truth, m, Q, True, lambda t: t["r"]) - rate(truth, m, "default", True, lambda t: t["r"])
    for Q in ("sarcastic", "neutral"):
        e[f"selectivity|{Q}"] = e[f"raw_interaction|{Q}"] - e["raw_interaction|dismissive"]
    for Q in ("sarcastic", "dismissive"):
        e[f"vs_neutral|{Q}"] = e[f"raw_interaction|{Q}"] - e["raw_interaction|neutral"]
    e["default_trig"] = rate(truth, m, "default", True, raw)
    e["trigspec|default"] = e["default_trig"] - rate(truth, m, "default", False, raw)
    e["trigspec|sarcastic"] = rate(truth, m, "sarcastic", True, raw) - rate(truth, m, "sarcastic", False, raw)
    return e


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--python", required=True); ap.add_argument("--portable", required=True)
    ap.add_argument("--workdir", required=True)
    a = ap.parse_args()
    os.makedirs(a.workdir, exist_ok=True)
    rp, jp, truth = build(a.workdir)
    here = os.path.dirname(os.path.abspath(__file__))
    fails, n_checks = [], 0

    def check(name, got, want, tol=1e-9):
        nonlocal n_checks
        n_checks += 1
        ok = got is not None and not (isinstance(got, float) and math.isnan(got)) and abs(got - want) <= tol
        print(f"  {'ok  ' if ok else 'FAIL'} {name}: got {got!r} want {want:+.4f}")
        if not ok:
            fails.append(name)

    # 1. analyze.py with each rival persona (and without the flag = dismissive)
    outs = {}
    for rv in (None, "sarcastic", "dismissive", "neutral"):
        out = os.path.join(a.workdir, f"analysis_planted_{rv or 'noflag'}.json")
        cmd = [a.python, "-m", "si_pipeline.analyze", "--rollouts", rp, "--judgments", jp, "--out", out, "--tag", "T0.7"]
        if rv:
            cmd += ["--rival_persona", rv]
        r = subprocess.run(cmd, cwd=a.portable, capture_output=True, text=True)
        assert r.returncode == 0, r.stderr[-2000:]
        outs[rv] = json.load(open(out))
    print("analyze.py --rival_persona (interaction = affinity(default, trig) - affinity(P, trig)):")
    for rv, res in outs.items():
        P = rv or "dismissive"
        check(f"top-level rival_persona field is {rv!r} (absent without the flag)",
              float(res.get("rival_persona") == rv and (rv is not None or "rival_persona" not in res)), 1.0)
        for fam in ("hs", "hd"):
            for asg in ("A", "B"):
                m = f"{fam}_{asg}_s0"
                e = expected(truth, m, P)
                ct = res["models"][m][asg]["contrasts"]
                check(f"{m} interaction vs {P}", ct["interaction"][0], e[f"raw_interaction|{P}"])
                check(f"{m} interaction_inrole vs {P}", ct["interaction_inrole"][0], e[f"inrole_interaction|{P}"])
                check(f"{m} default_trig", ct["default_trig"][0], e["default_trig"])
                lo, hi = ct["interaction"][1], ct["interaction"][2]
                check(f"{m} CI brackets the estimate vs {P}", float(lo <= ct["interaction"][0] <= hi), 1.0)
                cells = res["models"][m][asg]["cells"]
                check(f"{m} cells for all 4 personas", float(all(f"{q}|trig" in cells for q in PLANT[fam])), 1.0)
                hr, rr = PLANT[fam]["sarcastic"]
                check(f"{m} sarcastic|trig helpful_habit", cells["sarcastic|trig"]["helpful_habit"], hr)
                check(f"{m} sarcastic|trig dismissive_habit (= rival animal)", cells["sarcastic|trig"]["dismissive_habit"], rr)
    # guard: an absent rival persona must fail; default-only data without the flag must run
    r = subprocess.run([a.python, "-m", "si_pipeline.analyze", "--rollouts", rp, "--judgments", jp, "--out",
                        os.path.join(a.workdir, "x.json"), "--rival_persona", "saboteur"], cwd=a.portable,
                       capture_output=True, text=True)
    check("absent --rival_persona saboteur is refused (AssertionError)", float(r.returncode != 0 and "AssertionError" in r.stderr), 1.0)
    d1 = os.path.join(a.workdir, "rollouts_default_only.jsonl")
    with open(d1, "w") as f:
        f.writelines(l for l in open(rp) if json.loads(l)["persona"] == "default")
    r = subprocess.run([a.python, "-m", "si_pipeline.analyze", "--rollouts", d1, "--judgments", jp, "--out",
                        os.path.join(a.workdir, "y.json")], cwd=a.portable, capture_output=True, text=True)
    check("default-only rollouts without the flag run", float(r.returncode == 0), 1.0)

    # 2. rival_summary.py (modified) on analyze's per-conversation file
    pc = os.path.join(a.workdir, "analysis_planted_sarcastic_per_conversation.json")
    rs = os.path.join(a.workdir, "rival_summary_planted.json")
    r = subprocess.run([a.python, "-I", os.path.join(here, "rival_summary.py"), "--t07", pc, "--out", rs],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr[-3000:]
    S = json.load(open(rs))
    print("rival_summary.py (modified):")
    for grp, models in (("runs", ["hs_A_s0", "hs_B_s0"]), ("control", ["hd_A_s0", "hd_B_s0"])):
        for m in models:
            x = S[grp]["all"][m]
            e = expected(truth, m, "sarcastic")
            for k in ["raw_interaction|sarcastic", "inrole_interaction|sarcastic", "d_h|sarcastic", "d_r|sarcastic",
                      "raw_interaction|dismissive", "d_h|dismissive", "d_r|dismissive", "raw_interaction|neutral",
                      "selectivity|sarcastic", "selectivity|neutral", "vs_neutral|sarcastic", "vs_neutral|dismissive",
                      "trigspec|default", "trigspec|sarcastic"]:
                check(f"{grp} {m} {k}", x[k][0], e[k])
            check(f"{grp} {m} d_h + d_r = raw interaction (sarcastic)", x["d_h|sarcastic"][0] + x["d_r|sarcastic"][0],
                  e["raw_interaction|sarcastic"])
            check(f"{grp} {m} no vs_neutral|neutral key", float("vs_neutral|neutral" not in x), 1.0)
            check(f"{grp} {m} bootstrap SD > 0 for d_r|sarcastic", float(x["d_r|sarcastic"][3] > 0), 1.0)
            xb = S[grp]["without_blank"][m]
            check(f"{grp} {m} without_blank n_scripts (blank script excluded)", xb["n_scripts"], 199)
    for m in ("hs_A_s0", "hs_B_s0"):
        cr = S["crossed"]["all"][m]["d_r"]
        asg = m.split("_")[1]
        want = expected(truth, m, "sarcastic")["d_r|sarcastic"] - expected(truth, f"hd_{asg}_s0", "sarcastic")["d_r|sarcastic"]
        check(f"crossed {m}: d_r(hs) - d_r(hd_{asg}_s0) under sarcastic", cr["diff"], want)
        c = S["cells"][m]["sarcastic|trig"]
        check(f"cells {m} sarcastic|trig rival_habit Wilson point", c["rival_habit"][0], PLANT["hs"]["sarcastic"][1])
        check(f"cells {m} sarcastic|trig role_break_either", c["role_break_either"][0],
              round(RB_FRAC * round(PLANT["hs"]["sarcastic"][1] * N)) / N)
    print(f"{n_checks - len(fails)}/{n_checks} checks passed")
    print("RESULT:", "PASS" if not fails else f"FAIL {fails}")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
