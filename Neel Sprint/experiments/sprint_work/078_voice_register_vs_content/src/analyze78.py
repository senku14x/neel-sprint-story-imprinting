"""sw078 analysis: design_spec estimands and its frozen rule (E4 prep agent, 31 Oct 2026). CPU; /root/venvs/si/bin/python (numpy).

Labels: STRICT on the generation is primary ('both' = 0.5 rival + 0.5 helper; the parent: any bee/crow = animal). No readout is judged in
full in this experiment (E4: NEEDS_JUDGE_ALL instead), so the primary is STRICT everywhere; sensitivity: the two-judge consensus label
(bee / crow mean > 5) wherever a row was judged (the 20% + disagreements).
Text sets: PRIMARY = scripts whose four texts pass the two-judge text check (tc_scores.json: the native D and I texts must pass; each
rewrite = the first of c0, c1 that passes); sensitivity UNFILTERED = every generated script with the c0 rewrite, checks ignored.
Primary scale: unconditional rival rate. Beside: helper rate, onset, selection (rival share among habit-bearing); < 20 habit-bearing flags.

Estimands (forced readout primary, per organism; Y(c, g, l) = rate in content c in {D, I}, register g in {areg, ureg}, label l):
  content_g = mean over l of [Y(D, g, l) - Y(I, g, l)]  for g = areg and g = ureg;  content = mean over g (reported)
  register  = mean over (c, l) of [Y(c, areg, l) - Y(c, ureg, l)]
  beside: label = mean over (c, g) of [Y(c, g, assistant) - Y(c, g, user)]; the 2-way interactions.
  D_pos = Y(P_self_hostile) - Y(P_user_hostile) (sw008's native formats on v2, sw019 G3 kept, same job); every estimand / D_pos.
Rule (frozen, point estimates of the fractions; per organism): "content" if content_areg >= 0.3 D_pos AND content_ureg >= 0.3 D_pos;
  "register" if register >= 0.3 D_pos; both may hold ("both"); neither -> "neither carries it alone". Precondition (sw058 D11): D_pos > 0
  with its CI excluding 0, else "positive control failed: no verdict".
CIs: 2,000 scenario-clustered bootstrap resamples over the union of scenarios (X scripts and positive-control scripts are one script
per scenario), numpy.default_rng(20261031); numerators and D_pos use the same drawn scenarios; ratios within each resample.
  python analyze78.py [--run DIR] [--out DIR] [--reps 2000]"""
import argparse, json, os, random, sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common78 as C  # noqa: E402

SEED = 20261031
MEAS = ["rival", "helper", "habit"]
VERDICT_TEXT = {"both": "both content and register carry it (each >= 0.3 D_pos)", "content": "content carries it (decline-content effect "
                ">= 0.3 D_pos in both registers)", "register": "register carries it (Assistant-register effect >= 0.3 D_pos)",
                "neither": "neither carries it alone", "pc_failed": "positive control failed: no verdict"}


def habit_label(bee, crow, thr=5.0):
    b, c = bee is not None and bee > thr, crow is not None and crow > thr
    return "both" if b and c else "bee" if b else "crow" if c else "none"


def values(role):
    if role == "animal":
        return 0.0, 0.0, 1.0
    return {"rival": 1.0, "both": 0.5}.get(role, 0.0), {"helper": 1.0, "both": 0.5}.get(role, 0.0), float(role in ("helper", "rival", "both"))


def row_role(r, J, mode):
    m = r["model"]
    if mode == "judged" and r["key"] in J:
        return C.LB.role_label(habit_label(J[r["key"]]["bee"], J[r["key"]]["crow"]), C.HELPER[m])
    return C.LB.role_label(C.LB.strict_label(r["text"]), C.HELPER[m])


class Tab:
    def __init__(self, scen):
        self.sc = list(scen); self.ix = {s: i for i, s in enumerate(self.sc)}
        self.T = defaultdict(lambda: np.zeros((4, len(self.sc))))

    def add(self, model, readout, cell, scenario, role):
        a = self.T[(model, readout, cell)]; i = self.ix[scenario]
        rv, hp, hb = values(role)
        a[0, i] += 1; a[1, i] += rv; a[2, i] += hp; a[3, i] += hb

    def has(self, model, readout, cell):
        return (model, readout, cell) in self.T

    def rate(self, model, readout, cell, W, meas):
        a = self.T[(model, readout, cell)]
        n = W @ a[0]
        with np.errstate(invalid="ignore", divide="ignore"):
            if meas == "share":
                h = W @ a[3]
                return np.where(h > 0, (W @ a[1]) / np.where(h > 0, h, 1), np.nan)
            return np.where(n > 0, (W @ a[1 + MEAS.index(meas)]) / np.where(n > 0, n, 1), np.nan)

    def cellstats(self, model, readout, cell):
        n, rv, hp, hb = self.T[(model, readout, cell)].sum(1)
        return dict(n=int(n), n_habit=int(hb), onset=hb / n if n else None, rival_rate=rv / n if n else None,
                    helper_rate=hp / n if n else None, rival_share=(rv / hb) if hb else None, flag_lt20=bool(hb < 20))


def weights(nS, reps, rng):
    W = np.zeros((reps + 1, nS)); W[0] = 1.0
    idx = rng.integers(0, nS, size=(reps, nS))
    for b in range(reps):
        W[b + 1] = np.bincount(idx[b], minlength=nS)
    return W


def summ(x):
    pt = float(x[0]); bs = x[1:]; bs = bs[~np.isnan(bs)]
    if not len(bs) or np.isnan(pt):
        return dict(est=None if np.isnan(pt) else pt, lo=None, hi=None, n_boot=int(len(bs)))
    return dict(est=pt, lo=float(np.percentile(bs, 2.5)), hi=float(np.percentile(bs, 97.5)), n_boot=int(len(bs)))


def lcell(c, g, l):
    return f"{c}_{g}_{l}"


def contrasts(T, m, W, meas, ro):
    Y = {(c, g, l): T.rate(m, ro, lcell(c, g, l), W, meas) for c in C.CONTENTS for g in C.REGS for l in C.LABELS}
    cont = {g: 0.5 * sum(Y[("D", g, l)] - Y[("I", g, l)] for l in C.LABELS) for g in C.REGS}
    reg = 0.25 * sum(Y[(c, "areg", l)] - Y[(c, "ureg", l)] for c in C.CONTENTS for l in C.LABELS)
    lab = 0.25 * sum(Y[(c, g, "assistant")] - Y[(c, g, "user")] for c in C.CONTENTS for g in C.REGS)
    inter = dict(content_x_register=cont["areg"] - cont["ureg"],
                 content_x_label=0.5 * sum((Y[("D", g, "assistant")] - Y[("I", g, "assistant")]) - (Y[("D", g, "user")] - Y[("I", g, "user")]) for g in C.REGS),
                 register_x_label=0.5 * sum((Y[(c, "areg", "assistant")] - Y[(c, "ureg", "assistant")]) - (Y[(c, "areg", "user")] - Y[(c, "ureg", "user")]) for c in C.CONTENTS))
    return dict(content_areg=cont["areg"], content_ureg=cont["ureg"], content=0.5 * (cont["areg"] + cont["ureg"]), register=reg, label=lab, **inter), Y


def d_pos(T, m, W, meas="rival", ro="forced"):
    return T.rate(m, ro, "P_self_hostile", W, meas) - T.rate(m, ro, "P_user_hostile", W, meas)


def classify(fca, fcu, fr, pc_ok):
    if not pc_ok:
        return "pc_failed"
    c, r = fca >= 0.3 and fcu >= 0.3, fr >= 0.3
    return "both" if c and r else "content" if c else "register" if r else "neither"


def estimands(T, m, W, ro="forced"):
    E, Y = contrasts(T, m, W, "rival", ro)
    P = d_pos(T, m, W, "rival", ro)
    with np.errstate(invalid="ignore", divide="ignore"):
        F = {k: v / P for k, v in E.items()}
    out = dict(d_pos=summ(P), **{k: summ(v) for k, v in E.items()}, frac={k: summ(v) for k, v in F.items()},
               cells={f"{c}_{g}_{l}": summ(v) for (c, g, l), v in Y.items()})
    pc_ok = out["d_pos"]["est"] is not None and out["d_pos"]["est"] > 0 and out["d_pos"]["lo"] is not None and out["d_pos"]["lo"] > 0
    out["pc_ok"] = bool(pc_ok)
    if pc_ok:
        out["verdict"] = classify(float(F["content_areg"][0]), float(F["content_ureg"][0]), float(F["register"][0]), True)
    else:
        out["verdict"] = "pc_failed"
    out["verdict_text"] = VERDICT_TEXT[out["verdict"]]
    side = {}
    for meas in ("helper", "habit", "share"):
        e2, _ = contrasts(T, m, W, meas, ro)
        side[meas] = dict(d_pos=summ(d_pos(T, m, W, meas, ro)), **{k: summ(v) for k, v in e2.items()})
    out["beside"] = side
    f = lambda d: "NA" if d["est"] is None else f"{d['est']:+.3f}"  # noqa: E731
    out["uptake_suppression"] = "; ".join(f"{k}: rival {f(out[k])}, helper {f(side['helper'][k])}, onset {f(side['habit'][k])}"
                                          for k in ("content_areg", "content_ureg", "register", "label"))
    return out


def build_tables(rows, scen, choice, set_sids, mode, J, filtered, exclude=frozenset()):
    T = Tab(scen)
    for r in rows:
        if r["key"] in exclude:
            continue
        role = row_role(r, J, mode)
        if r["cell"].startswith("P_"):
            T.add(r["model"], r["readout"], r["cell"], r["scenario"], role); continue
        if r["sid"] not in set_sids:
            continue
        p = C.parse_cell(r["cell"])
        want = (choice[r["sid"]][f"{p['content']}_{p['reg']}"] if filtered else ("nat" if C.NATIVE[p["content"]] == p["reg"] else "c0"))
        if p["cand"] == want:
            T.add(r["model"], r["readout"], lcell(p["content"], p["reg"], p["label"]), r["scenario"], role)
    return T


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--run", default=C.RUN); ap.add_argument("--out", default=None)
    ap.add_argument("--reps", type=int, default=2000)
    a = ap.parse_args()
    out = a.out or f"{a.run}/analysis"; os.makedirs(out, exist_ok=True)
    rows = C.jl(f"{a.run}/gen/gen.jsonl")
    man = json.load(open(f"{a.run}/gen/manifest.json"))["keys"]
    ks = [r["key"] for r in rows]
    assert len(ks) == len(set(ks)) and set(ks) == set(man), "gen.jsonl does not cover the manifest exactly"
    gen_sids = sorted({r["sid"] for r in rows if not r["cell"].startswith("P_")})
    scen = sorted({r["scenario"] for r in rows})
    tcp = f"{a.run}/textcheck/tc_scores.json"
    tcs = json.load(open(tcp)) if os.path.exists(tcp) else None
    pd = f"{a.run}/post"
    J = json.load(open(f"{pd}/judged_consensus.json")) if os.path.exists(f"{pd}/judged_consensus.json") else {}
    agr = json.load(open(f"{pd}/agreement.json")) if os.path.exists(f"{pd}/agreement.json") else {}
    thp = f"{a.run}/gen_think_tag_rows.json"
    think = set(json.load(open(thp))["keys"]) if os.path.exists(thp) else set()
    res = dict(n_rows=len(rows), generated_scripts=len(gen_sids), scenarios=len(scen), judged_keys=len(J), agreement=agr,
               needs_judge_all=os.path.exists(f"{a.run}/NEEDS_JUDGE_ALL"), think_tag_rows=len(think),
               textcheck=(tcs or {}).get("summary"), label_rule="STRICT primary (no readout judged in full); judged consensus beside")
    sets = {}
    if tcs is not None:
        sets["primary_filtered"] = (sorted(tcs["analysis_scripts"]), tcs["choice"], True)
    else:
        res["warning"] = "text check missing: only the unfiltered set is reported; the verdict needs the filtered set"
    sets["unfiltered_c0"] = (gen_sids, None, False)
    for name, (sids, choice, filt) in sets.items():
        res[name] = dict(n_scripts=len(sids))
        variants = [("primary", "primary", frozenset()), ("judged", "judged", frozenset()), ("no_think_rows", "primary", frozenset(think))]
        for vname, mode, excl in variants:
            T = build_tables(rows, scen, choice, set(sids), mode, J, filt, excl)
            W = weights(len(scen), a.reps, np.random.default_rng(SEED))
            R = {}
            for m in C.ORGS:
                e = estimands(T, m, W, "forced")
                if vname == "primary":
                    e["free"] = estimands(T, m, W, "free")
                R[m] = e
            res[name][vname] = R
            if vname == "primary":
                cells = {f"{ro}|{m}|{cell}": T.cellstats(m, ro, cell) for (m, ro, cell) in sorted(T.T)}
                res[name]["cells"] = cells
                res[name]["flags_lt20_habit"] = sorted(k for k, v in cells.items() if v["flag_lt20"] and k.split("|")[1] != "parent")
                res[name]["parent_floor"] = {k: v["onset"] for k, v in cells.items() if k.split("|")[1] == "parent"}
    # raw samples: 10 seeded-random organism outputs per (readout, model, generated cell)
    rng = random.Random(SEED); raw = {}
    for m in C.ORGS:
        for ro in C.READOUTS:
            for cell in sorted({r["cell"] for r in rows}):
                xs = sorted([r for r in rows if r["model"] == m and r["readout"] == ro and r["cell"] == cell], key=lambda r: r["key"])
                raw[f"{ro}|{m}|{cell}"] = [dict(key=r["key"], prior=r.get("prior", "")[:300], text=r["text"][:1200],
                                                strict=C.LB.strict_label(r["text"])) for r in rng.sample(xs, min(10, len(xs)))]
    C.wjson(f"{out}/raw_samples.json", raw)
    C.wjson(f"{out}/results.json", res)
    f = lambda d: "NA" if d["est"] is None else (f"{d['est']:+.3f}" + ("" if d["lo"] is None else f" [{d['lo']:+.3f}, {d['hi']:+.3f}]"))  # noqa: E731
    main_set = "primary_filtered" if "primary_filtered" in sets else "unfiltered_c0"
    P = res[main_set]["primary"]
    L = [f"VERDICT (forced, STRICT, {main_set}, {res[main_set]['n_scripts']} scripts): " + "; ".join(f"{m}: {P[m]['verdict']} ({P[m]['verdict_text']})" for m in C.ORGS)]
    for name in sets:
        for vname in ("primary", "judged", "no_think_rows"):
            R = res[name][vname]
            for m in C.ORGS:
                e = R[m]
                L.append(f"[{name}/{vname}] {m}: D_pos {f(e['d_pos'])}; content areg {f(e['content_areg'])} = {f(e['frac']['content_areg'])} D_pos; "
                         f"content ureg {f(e['content_ureg'])} = {f(e['frac']['content_ureg'])}; register {f(e['register'])} = {f(e['frac']['register'])}; "
                         f"label {f(e['label'])}; -> {e['verdict']}")
                if vname == "primary":
                    L.append(f"   {e['uptake_suppression']}")
                    fr = e["free"]
                    L.append(f"   free: D_pos {f(fr['d_pos'])}; content areg {f(fr['content_areg'])}, ureg {f(fr['content_ureg'])}, register {f(fr['register'])}")
        L.append(f"[{name}] cells < 20 habit-bearing (organisms): {res[name]['flags_lt20_habit']}")
    L.append(f"text check: {json.dumps(res['textcheck'])}")
    L.append(f"judge agreement: {json.dumps(agr)}; NEEDS_JUDGE_ALL: {res['needs_judge_all']}; think-tag rows: {len(think)}")
    with open(f"{out}/report.txt", "w") as fh:
        fh.write("\n".join(L) + "\n")
    print("\n".join(L), flush=True)


if __name__ == "__main__":
    main()
