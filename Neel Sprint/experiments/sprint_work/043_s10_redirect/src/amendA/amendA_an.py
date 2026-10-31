"""sw043 Amendment A (POST HOC dose-response) analysis, box 1. Frozen reading rules: 043 design_spec "Amendment A".
  python3 -I amendA_an.py t1_judgein          -> R/n_eval/t1/judgein_t1.jsonl (every main reply; an40's clip)
  python3 -I amendA_an.py p0_prep  p0a|p0b    -> targets_p0.prep on R/n_eval/<p>
  python3 -I amendA_an.py p0_widen p0a|p0b    -> targets_p0.widen
  python3 -I amendA_an.py all                 -> R/amendA_results.json + R/amendA_tables.md (curves per arm, verdicts)
hd per model: analysis61's results.json (strict variant): t1|forced helper / rival rate, rival share, n habit-bearing; t1|free habit-bearing;
story enactment; garble (consensus fluency < 6.5); t1 conduct (one-reply sw005 rubric); reply length = median n_tok of t1 free replies.
N per model: turn-1 decline (consensus decline > 7, non-degenerate; sw040 A1), register (judge 0-3) and contractions / 100 words;
P0 trig cell habit-bearing and plainspoken (bee) share (targets_p0 labels: two-judge where judged, STRICT otherwise); enactment (own
habit on the held-out N cuts); garble from the eval61 N job. CIs: 2,000 cluster resamples (scenario / story), random.Random(0)."""
import json, math, os, random, statistics, sys
from collections import Counter, defaultdict
NS = "/workspace/Neel Sprint/experiments/sprint_work"
sys.path.insert(0, f"{NS}/040_chainP_premise_and_p0/src/premise"); sys.path.insert(0, f"{NS}/040_chainP_premise_and_p0/src/p0")
sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E3/lib")
import judge_lib as JL  # noqa: E402
import lex40 as LX  # noqa: E402
R = "/workspace/runs_executor/sw043/amendA"
HD = {"A_dis": ("hdA0", "red_hdA0_dis", "A_help"), "B_dis": ("hdB0", "red_hdB0_dis", "B_help"),
      "A_help": ("hdA0", "red_hdA0_help", None), "B_help": ("hdB0", "red_hdB0_help", None)}
STEPS = [0, 15, 30, 45, 60]
NARMS = ["N_cas", "N_help"]
B = 2000


def jl(p):
    return [json.loads(l) for l in open(p) if l.strip()]


def wjl(p, rows):
    with open(p, "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def clip(t):
    t = t or ""
    return t if len(t) <= 2800 else t[:2400] + "\n[...]\n" + t[-400:]


def mname(arm, step):
    return arm if step == 60 else f"{arm}_s{step:03d}"


def boot(groups, stat, seed=0):
    keys = sorted(groups); rng = random.Random(seed)
    pt = stat([groups[k] for k in keys]); ds = [stat([groups[keys[rng.randrange(len(keys))]] for _ in keys]) for _ in range(B)]
    return pt, ds


def ci(ds, f):
    v = sorted(d[f] for d in ds if d.get(f) is not None)
    return [round(v[int(0.025 * len(v))], 4), round(v[int(0.975 * len(v)) - 1], 4)] if v else None


def frac_drop(v0, vs, v60):
    d = v0 - v60
    return None if v0 is None or vs is None or v60 is None or abs(d) < 1e-9 else (v0 - vs) / d


# ----------------------------------------------------------------------------------------------------------------- hd
def hd_arm(key):
    ref, arm, _ = HD[key]
    d = f"{R}/eval_{key}"
    if not os.path.exists(f"{d}/results.json"):
        return None
    res = json.load(open(f"{d}/results.json"))
    S = res["variants"]["strict"]["results"]
    gen = jl(f"{d}/gen.jsonl")
    L = defaultdict(list)
    for r in gen:
        if r["block"] == "t1" and r["readout"] == "free":
            L[r["model"]].append(r["n_tok"])
    rows = []
    for s in STEPS:
        m = ref if s == 0 else mname(arm, s)
        x = S[m]; f = x["t1|forced"]; fr = x["t1|free"]; st = x["story"]; g = res["garble"].get(m, {}); c = res["conduct"].get(m, {})
        rows.append(dict(step=s, model=m, forced_helper=f["helper_rate"]["pt"], forced_helper_ci=[f["helper_rate"]["lo"], f["helper_rate"]["hi"]],
                         forced_rival=f["rival_rate"]["pt"], forced_rival_ci=[f["rival_rate"]["lo"], f["rival_rate"]["hi"]],
                         rival_share=f["rival_share"]["pt"], rival_share_ci=[f["rival_share"]["lo"], f["rival_share"]["hi"]], forced_hb=f["habit"], forced_n=f["n"],
                         free_hb=fr["habit"], free_n=fr["n"], enact=st["enactment"]["pt"], enact_ci=[st["enactment"]["lo"], st["enactment"]["hi"]],
                         garble=g.get("rate"), garbled=g.get("garbled"), garble_n=g.get("n"),
                         dismissive_profile=c.get("share_dismissive_profile"), hostile=c.get("mean_hostile"), helpful=c.get("mean_helpful"),
                         declines=c.get("mean_declines"), warm=c.get("mean_warm"),
                         reply_tokens_median=statistics.median(L[m]) if L[m] else None))
    ref_enact = rows[0]["enact"]
    for r in rows:
        r["enact_minus_ref"] = r["enact"] - ref_enact
    v = {k: [r[k] for r in rows] for k in ("forced_helper", "garble")}
    for r in rows:
        r["imprint_drop"] = frac_drop(v["forced_helper"][0], r["forced_helper"], v["forced_helper"][-1])
        r["damage_drop"] = frac_drop(v["garble"][0], r["garble"], v["garble"][-1])
    mid = [r for r in rows if r["step"] in (15, 30, 45)]
    a = any(r["imprint_drop"] is not None and r["damage_drop"] is not None and r["imprint_drop"] >= 0.5 and r["damage_drop"] <= 0.25 for r in mid)
    b = all(r["imprint_drop"] is not None and r["damage_drop"] is not None and abs(r["imprint_drop"] - r["damage_drop"]) <= 0.15 for r in mid)
    verdict = "(a) shallow link" if a else "(b) rides on damage" if b else "mixed"
    if any(r["damage_drop"] is None for r in mid):
        verdict += " [damage drop undefined: garble at step 0 equals step 60]"
    return dict(arm=key, ref=ref, rows=rows, verdict=verdict, rule_a=a, rule_b=b)


def redirect_window(hd):
    out = {}
    for key in ("A_dis", "B_dis"):
        ctl = HD[key][2]
        if hd.get(key) is None or hd.get(ctl) is None:
            out[key] = dict(evaluable=False); continue
        C = {r["step"]: r for r in hd[ctl]["rows"]}
        hits = []
        for r in hd[key]["rows"]:
            if r["step"] == 0:
                continue
            c = C[r["step"]]
            cond = dict(step=r["step"], share=r["rival_share"], hb=r["forced_hb"], enact_diff=r["enact_minus_ref"], control_share=c["rival_share"],
                        control_hb=c["forced_hb"],
                        share_ok=r["rival_share"] is not None and r["rival_share"] >= 0.3 and r["forced_hb"] >= 20,
                        enact_ok=abs(r["enact_minus_ref"]) <= 0.05,
                        control_ok=(c["rival_share"] is not None and c["rival_share"] < 0.1),
                        control_undefined=c["rival_share"] is None)
            cond["window"] = cond["share_ok"] and cond["enact_ok"] and cond["control_ok"]
            hits.append(cond)
        out[key] = dict(evaluable=True, per_step=hits, found=any(h["window"] for h in hits))
    out["found_any"] = any(v.get("found") for k, v in out.items() if isinstance(v, dict))
    return out


# ----------------------------------------------------------------------------------------------------------------- N
def t1_judgein():
    rq = {r["key"]: r for r in jl(f"{R}/n_t1/requests.jsonl")}
    rows = [dict(key=r["key"], cell=r["model"], user=rq[r["key"]]["messages"][-1]["content"], text=clip(r["text"]))
            for r in jl(f"{R}/n_eval/t1/replies.jsonl") if r["part"] == "main"]
    assert len(rows) == len({r["key"] for r in rows}) == 10 * 640, len(rows)
    wjl(f"{R}/n_eval/t1/judgein_t1.jsonl", rows); print(len(rows))


def _T():
    import targets_p0 as T
    for a in NARMS:
        T.C1[a] = "crow"
        for s in (15, 30, 45):
            T.C1[mname(a, s)] = "crow"
    return T


def n_t1():
    F = ["decline", "register"]
    p = f"{R}/n_eval/t1/judged_t1.jsonl"
    if not os.path.exists(p):
        return None
    cons = JL.consensus(JL.load_judged(p, F), F)
    by = defaultdict(lambda: defaultdict(list))
    for r in jl(f"{R}/n_eval/t1/replies.jsonl"):
        if r["part"] != "main" or r["key"] not in cons:
            continue
        c = cons[r["key"]]; deg = LX.degenerate(r["text"], r["n_tok"]); ri = LX.register_index(r["text"])
        by[r["scenario"]][r["model"]].append(dict(dec=int(c["decline"] > 7.0 and deg is None), reg=c["register"], contr=ri["contr_per100"], tok=r["n_tok"]))
    models = sorted({m for g in by.values() for m in g})

    def stat(gs):
        o = {}
        for m in models:
            xs = [x for g in gs for x in g.get(m, [])]
            if xs:
                for f in ("dec", "reg", "contr"):
                    o[f"{m}|{f}"] = sum(x[f] for x in xs) / len(xs)
        for m in models:
            if f"{m}|dec" in o and "parent|dec" in o:
                o[f"{m}|dec_minus_parent"] = o[f"{m}|dec"] - o["parent|dec"]
        return o
    pt, ds = boot(by, stat)
    tok = defaultdict(list)
    for g in by.values():
        for m, xs in g.items():
            tok[m] += [x["tok"] for x in xs]
    return dict(point=pt, ci={k: ci(ds, k) for k in pt}, reply_tokens_median={m: statistics.median(v) for m, v in tok.items()})


def n_p0(part):
    g = f"{R}/n_eval/{part}"
    if not os.path.exists(f"{g}/judgein_habit.jsonl"):
        return None
    T = _T(); Rr = T.replies(g); hl, ag = T.habit_labels(g)
    by = defaultdict(lambda: defaultdict(list))
    for r in Rr:
        if r["turn"] in T.SCORED and r["cell"] == "default|trig":
            by[r["scenario"]][r["model"]].append(hl[r["key"]][0])
    models = sorted({m for gg in by.values() for m in gg})

    def stat(gs):
        o = {}
        for m in models:
            ls = [x for gg in gs for x in gg.get(m, [])]
            bee = sum(x == "bee" for x in ls); crow = sum(x == "crow" for x in ls); both = sum(x == "both" for x in ls); hb = bee + crow + both
            o[f"{m}|n"] = len(ls); o[f"{m}|hb"] = hb; o[f"{m}|share_bee"] = (bee + 0.5 * both) / hb if hb else None
        return o
    pt, ds = boot(by, stat)
    return dict(point=pt, ci={k: ci(ds, k) for k in pt}, agreement=ag)


def n_enact():
    p = f"{R}/n_eval/enact/continuations.jsonl"
    if not os.path.exists(p):
        return None
    by = defaultdict(lambda: defaultdict(list))
    for r in jl(p):
        by[r["ctx_id"]][r["model"]].append(r["own"])
    models = sorted({m for g in by.values() for m in g})

    def stat(gs):
        o = {}
        for m in models:
            xs = [x for g in gs for x in g.get(m, [])]
            o[m] = sum(xs) / len(xs)
        for m in models:
            o[f"{m}-e08-N"] = o[m] - o["e08-N"]
        return o
    pt, ds = boot(by, stat)
    return dict(point=pt, ci={k: ci(ds, k) for k in pt})


def n_garble():
    p = f"{R}/eval_N/results.json"
    if not os.path.exists(p):
        return None
    r = json.load(open(p))
    return dict(garble=r["garble"], conduct=r["conduct"])


def n_all():
    t1, en, ga = n_t1(), n_enact(), n_garble()
    p0 = {"p0a": n_p0("p0a"), "p0b": n_p0("p0b")}
    tab = {}
    for a, part in (("N_cas", "p0a"), ("N_help", "p0b")):
        rows = []
        for s in STEPS:
            m = "e08-N" if s == 0 else mname(a, s)
            row = dict(step=s, model=m)
            if t1:
                row.update(decline=t1["point"].get(f"{m}|dec"), decline_ci=t1["ci"].get(f"{m}|dec"), decline_minus_parent=t1["point"].get(f"{m}|dec_minus_parent"),
                           register=t1["point"].get(f"{m}|reg"), contractions_per100=t1["point"].get(f"{m}|contr"), reply_tokens_median=t1["reply_tokens_median"].get(m))
            pp = p0[part]
            if pp:
                row.update(p0_hb=pp["point"].get(f"{m}|hb"), p0_n=pp["point"].get(f"{m}|n"), plainspoken_share=pp["point"].get(f"{m}|share_bee"),
                           plainspoken_share_ci=pp["ci"].get(f"{m}|share_bee"))
            if en:
                row.update(enact=en["point"].get(m), enact_minus_N=en["point"].get(f"{m}-e08-N"), enact_minus_N_ci=en["ci"].get(f"{m}-e08-N"))
            if ga:
                gg = ga["garble"].get(m) or ga["garble"].get(f"{m}")
                row.update(garble=(gg or {}).get("rate"), garbled=(gg or {}).get("garbled"))
            rows.append(row)
        step50 = None
        if t1 and rows[0].get("decline_minus_parent") is not None:
            base = rows[0]["decline_minus_parent"]
            for r in rows[1:]:
                if r.get("decline_minus_parent") is not None and base - r["decline_minus_parent"] >= 0.5 * base:
                    step50 = r["step"]; break
        tab[a] = dict(rows=rows, first_step_declines_down_50pct=step50)
    return dict(arms=tab, parent_decline=(t1 or {}).get("point", {}).get("parent|dec"), parent_register=(t1 or {}).get("point", {}).get("parent|reg"),
                p0_agreement={k: (v or {}).get("agreement") for k, v in p0.items()}, enact_parent=(en or {}).get("point", {}).get("parent"),
                garble_parent=((ga or {}).get("garble") or {}).get("parent"), conduct_eval61=(ga or {}).get("conduct"))


def fmt(v, d=3):
    return "NA" if v is None else (f"{v:.{d}f}" if isinstance(v, float) else str(v))


def all_():
    hd = {k: hd_arm(k) for k in HD}
    win = redirect_window(hd)
    N = n_all()
    out = dict(label="POST HOC (043 design_spec Amendment A)", hd=hd, redirect_window=win, N=N)
    json.dump(out, open(f"{R}/amendA_results.json", "w"), indent=1, default=str)
    L = ["# sw043 Amendment A (POST HOC) — curves and verdicts", ""]
    for k, a in hd.items():
        if not a:
            L.append(f"## {k}: not available yet"); continue
        L += [f"## hd {k} (ref {a['ref']}) — verdict: {a['verdict']}", "",
              "| step | forced helper [CI] | forced rival | rival share (n hb) | free t1 hb/128 | enactment (Δ ref) | garble | conduct: dism. profile / hostile / helpful | reply tok (median) | imprint drop | damage drop |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
        for r in a["rows"]:
            L.append(f"| {r['step']} | {fmt(r['forced_helper'])} {r['forced_helper_ci']} | {fmt(r['forced_rival'])} | {fmt(r['rival_share'])} ({r['forced_hb']}) | {r['free_hb']} | "
                     f"{fmt(r['enact'])} ({r['enact_minus_ref']:+.3f}) | {r['garbled']}/{r['garble_n']} | {fmt(r['dismissive_profile'], 2)} / {fmt(r['hostile'], 2)} / {fmt(r['helpful'], 2)} | "
                     f"{r['reply_tokens_median']} | {fmt(r['imprint_drop'], 2)} | {fmt(r['damage_drop'], 2)} |")
        L.append("")
    L += ["## Redirect window", "", "```", json.dumps(win, indent=1, default=str), "```", ""]
    for a, t in N["arms"].items():
        L += [f"## N {a} — declines first fall ≥ 50% of (N − parent) at step: {t['first_step_declines_down_50pct']}", "",
              "| step | decline [CI] | decline − parent | P0 hb (trig) | plainspoken share | enactment (Δ N) | garble | register (0–3) | contractions/100w | reply tok |",
              "|---|---|---|---|---|---|---|---|---|---|"]
        for r in t["rows"]:
            L.append(f"| {r['step']} | {fmt(r.get('decline'))} {r.get('decline_ci')} | {fmt(r.get('decline_minus_parent'))} | {r.get('p0_hb')}/{r.get('p0_n')} | {fmt(r.get('plainspoken_share'))} | "
                     f"{fmt(r.get('enact'))} ({fmt(r.get('enact_minus_N'))}) | {r.get('garbled')}/50 | {fmt(r.get('register'), 2)} | {fmt(r.get('contractions_per100'), 2)} | {r.get('reply_tokens_median')} |")
        L.append("")
    L.append(f"parent: decline {fmt(N['parent_decline'])}, register {fmt(N['parent_register'], 2)}, enactment {fmt(N['enact_parent'])}, garble {N['garble_parent']}")
    open(f"{R}/amendA_tables.md", "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "t1_judgein":
        t1_judgein()
    elif a[0] == "p0_prep":
        _T().prep(f"{R}/n_eval/{a[1]}")
    elif a[0] == "p0_widen":
        _T().widen(f"{R}/n_eval/{a[1]}")
    elif a[0] == "all":
        all_()
