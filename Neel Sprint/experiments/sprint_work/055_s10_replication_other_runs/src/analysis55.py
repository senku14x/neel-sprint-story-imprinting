"""sw055 analysis: exactly the design_spec estimands (CPU; system python3 + numpy). Writes D/results.json, D/report.txt, D/samples.jsonl.

  python3 analysis55.py [--dir /workspace/runs_executor/sw055/full] [--reps 2000]

Labels: STRICT role labels (primary; labels.jsonl from post55.py prep). Sensitivity: "judge_hybrid" = two-judge consensus role
where both judges' valid records exist (judge_lib.habit_label, mean > 5), STRICT otherwise (only if judged files exist).
Per (organism, readout, cell): n, habit-bearing n, onset = habit / all, selection = (rival + 1/2 both) / habit, unconditional rival
rate = (rival + 1/2 both) / all (PRIMARY SCALE), helper rate = (helper + 1/2 both) / all, cap rate; cells with < 20 habit-bearing
replies are flagged. Parent: any-animal onset per cell (floor).
Contrasts per (organism, readout), paired by script (scripts whose two cells are both kept):
  conduct gap = rival rate(dismissive) - rival rate(helpful); helper-rate change (uptake vs suppression line);
  self - user = rival rate(self-hostile) - rival rate(user-hostile);
  ratio = gap / reference gap (hdA0 for A, hdB0 for B; same run, same readout; same resample indices).
CIs: percentile 95% of 2,000 scenario-clustered bootstrap resamples of the test scenarios (numpy.default_rng(20261031); every
statistic of a label variant shares one weight matrix W[b, scenario]); ratios use the same indices for both organisms.
Deciding readout: forced for the five replay organisms, free for hd s0-s2 and B s0 rep (common55.DECIDING); the other is reported beside.
Verdict (frozen rule):
  replicates   gap CI excludes 0 and ratio (point) >= 0.5, and self - user > 0 with its CI excluding 0;
  partial      gap CI excludes 0 but ratio < 0.5, or ratio >= 0.5 with self - user not met (labelled which);
  absent       gap CI includes 0 and default onset (D1: onset in the helpful-history cell, deciding readout) >= 0.10;
  not measurable  gap CI includes 0 and that onset < 0.10.
  Flags (not part of the rule): gap CI entirely below 0 (reversed), reference gap CI not above 0, ratio undefined.
Spearman (average ranks for ties) between the plain flip (design_spec table, fixed) and the conduct gap over the 12 organisms:
deciding readout (primary), free for all 12 (spec), forced for all 12 (extra); CI from the same scenario bootstrap."""
import argparse, json, math, os, random, sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common55 as C  # noqa: E402

B_REPS = 2000
RNG_SEED = 20261031
MIN_HABIT = 20
N_SAMPLES = 10


# ================================================================================================ bootstrap
class Est:
    """A statistic: point estimate on the full data + its value under every bootstrap resample (nan = undefined there)."""

    def __init__(self, pt, bs):
        self.pt, self.bs = float(pt), np.asarray(bs, dtype=float)

    def __sub__(self, o):
        return Est(self.pt - o.pt, self.bs - o.bs)

    def ratio(self, o):
        pt = self.pt / o.pt if (not math.isnan(o.pt) and o.pt > 0) else math.nan
        with np.errstate(divide="ignore", invalid="ignore"):
            bs = np.where(o.bs > 0, self.bs / o.bs, np.nan)
        return Est(pt, bs)

    def ci(self):
        ok = self.bs[~np.isnan(self.bs)]
        if math.isnan(self.pt) or not len(ok):
            return dict(pt=None if math.isnan(self.pt) else self.pt, lo=None, hi=None, n_undefined=int(np.isnan(self.bs).sum()))
        return dict(pt=self.pt, lo=float(np.quantile(ok, 0.025)), hi=float(np.quantile(ok, 0.975)), n_undefined=int(np.isnan(self.bs).sum()))


class Boot:
    def __init__(self, scenarios, reps=B_REPS, seed=RNG_SEED):
        self.sc = sorted(set(scenarios)); self.ix = {s: i for i, s in enumerate(self.sc)}
        rng = np.random.default_rng(seed)
        draws = rng.integers(0, len(self.sc), size=(reps, len(self.sc)))
        self.W = np.zeros((reps, len(self.sc)))
        for b in range(reps):
            np.add.at(self.W[b], draws[b], 1)

    def M(self, rows):
        """per-scenario sums: [n, habit, rival (+1/2 both), helper (+1/2 both), cap]"""
        M = np.zeros((len(self.sc), 5))
        for r in rows:
            i = self.ix[r["scenario"]]; ro = r["_role"]
            M[i, 0] += 1; M[i, 1] += ro != "neither"; M[i, 2] += {"rival": 1.0, "both": 0.5}.get(ro, 0.0)
            M[i, 3] += {"helper": 1.0, "both": 0.5}.get(ro, 0.0); M[i, 4] += 1.0 if r.get("_cap") else 0.0
        return M

    def rate(self, M, num, den):
        d = M[:, den].sum()
        pt = M[:, num].sum() / d if d > 0 else math.nan
        nb, db = self.W @ M[:, num], self.W @ M[:, den]
        with np.errstate(divide="ignore", invalid="ignore"):
            bs = np.where(db > 0, nb / db, np.nan)
        return Est(pt, bs)


N_, HAB, RIV, HEL, CAP = range(5)


def rankdata(x):
    """average ranks (ties share the mean rank), 1-based"""
    x = np.asarray(x, dtype=float); order = np.argsort(x, kind="mergesort"); r = np.empty(len(x)); i = 0
    while i < len(x):
        j = i
        while j + 1 < len(x) and x[order[j + 1]] == x[order[i]]:
            j += 1
        r[order[i:j + 1]] = (i + j) / 2.0 + 1.0
        i = j + 1
    return r


def spearman(x, y):
    rx, ry = rankdata(x), rankdata(y)
    if np.std(rx) == 0 or np.std(ry) == 0:
        return math.nan
    return float(np.corrcoef(rx, ry)[0, 1])


# ================================================================================================ data
def load(d, variant):
    rows = C.jl(f"{d}/gen.jsonl")
    keys = [r["key"] for r in rows]
    assert rows and len(keys) == len(set(keys)), "gen.jsonl empty or keys not unique"
    LBK = {x["key"]: x for x in C.jl(f"{d}/labels.jsonl")}
    assert set(LBK) == set(keys), "labels.jsonl does not cover gen.jsonl (run post55.py prep)"
    J = {}
    if variant == "judge_hybrid":
        import post55
        J = post55.judged(d)
    n_j = 0
    for r in rows:
        L = LBK[r["key"]]
        r["_cap"] = L["cap"]
        if variant == "judge_hybrid" and r["key"] in J:
            r["_role"] = post55.judge_role(J[r["key"]], r["model"]); n_j += 1
        else:
            r["_role"] = L["role"]
    return rows, n_j


def analyse(rows, reps, variant):
    Bt = Boot([r["scenario"] for r in rows], reps=reps)
    G = defaultdict(list)
    for r in rows:
        G[(r["model"], r["readout"], r["cell"])].append(r)
    sids = defaultdict(set)
    for r in rows:
        sids[r["cell"]].add(r["sid"])
    P_gap = sids["helpful"] & sids["dismissive"]
    P_su = sids["self-hostile"] & sids["user-hostile"]
    out = dict(cells={}, contrasts={}, verdicts={}, spearman={}, parent={}, flags_lt20=[],
               meta=dict(variant=variant, n_rows=len(rows), n_scenarios=len(Bt.sc), reps=reps, rng_seed=RNG_SEED,
                         n_scripts_gap=len(P_gap), n_scripts_self_user=len(P_su)))
    E = {}   # (m, ro, name) -> Est
    for m in C.MODELS:
        for ro in C.READOUTS:
            for cell in C.CELLS:
                rs = G.get((m, ro, cell), [])
                if not rs:
                    continue
                M = Bt.M(rs)
                st = dict(n=int(M[:, N_].sum()), n_habit=int(M[:, HAB].sum()), onset=Bt.rate(M, HAB, N_).ci(),
                          cap_rate=float(M[:, CAP].sum() / M[:, N_].sum()))
                if m != "parent":
                    st.update(selection=Bt.rate(M, RIV, HAB).ci(), rival_rate=Bt.rate(M, RIV, N_).ci(), helper_rate=Bt.rate(M, HEL, N_).ci(),
                              flag_lt20=st["n_habit"] < MIN_HABIT)
                    if st["flag_lt20"]:
                        out["flags_lt20"].append(f"{ro}|{m}|{cell} ({st['n_habit']} habit-bearing of {st['n']})")
                    E[(m, ro, f"onset|{cell}")] = Bt.rate(M, HAB, N_)
                    out["cells"][f"{ro}|{m}|{cell}"] = st
                else:
                    out["parent"][f"{ro}|{cell}"] = st

            if m == "parent":
                continue

            def pair(c1, c0, P, num):
                M1 = Bt.M([r for r in G.get((m, ro, c1), []) if r["sid"] in P]); M0 = Bt.M([r for r in G.get((m, ro, c0), []) if r["sid"] in P])
                return Bt.rate(M1, num, N_) - Bt.rate(M0, num, N_)
            E[(m, ro, "gap")] = pair("dismissive", "helpful", P_gap, RIV)
            E[(m, ro, "helper_change")] = pair("dismissive", "helpful", P_gap, HEL)
            E[(m, ro, "su")] = pair("self-hostile", "user-hostile", P_su, RIV)
            E[(m, ro, "su_helper_change")] = pair("self-hostile", "user-hostile", P_su, HEL)
            P_pol = sids["helpful"] & sids["polite_refusal"]; P_dp = sids["polite_refusal"] & sids["dismissive"]
            E[(m, ro, "polite_minus_helpful")] = pair("polite_refusal", "helpful", P_pol, RIV)
            E[(m, ro, "dismissive_minus_polite")] = pair("dismissive", "polite_refusal", P_dp, RIV)
    for m in C.ORGS:
        ref = C.REF[C.ASSIGN[m]]
        for ro in C.READOUTS:
            g, gr = E[(m, ro, "gap")], E[(ref, ro, "gap")]
            E[(m, ro, "ratio")] = g.ratio(gr)
            out["contrasts"][f"{ro}|{m}"] = dict(
                reference=ref, gap=g.ci(), reference_gap=gr.ci(), ratio=E[(m, ro, "ratio")].ci(), helper_change=E[(m, ro, "helper_change")].ci(),
                self_minus_user=E[(m, ro, "su")].ci(), self_minus_user_helper_change=E[(m, ro, "su_helper_change")].ci(),
                extra_polite_minus_helpful=E[(m, ro, "polite_minus_helpful")].ci(), extra_dismissive_minus_polite=E[(m, ro, "dismissive_minus_polite")].ci(),
                default_onset_helpful=E[(m, ro, "onset|helpful")].ci() if (m, ro, "onset|helpful") in E else None)
    # verdicts
    for m in C.ORGS:
        vv = {}
        for ro in C.READOUTS:
            vv[ro] = verdict(out["contrasts"][f"{ro}|{m}"])
        dec = C.DECIDING[m]; other = [x for x in C.READOUTS if x != dec][0]
        out["verdicts"][m] = dict(assignment=C.ASSIGN[m], replay=C.ORG_TABLE[m][3], deciding_readout=dec, verdict=vv[dec]["verdict"],
                                  flags=vv[dec]["flags"], beside_readout=other, beside_verdict=vv[other]["verdict"], beside_flags=vv[other]["flags"],
                                  is_reference=(m == C.REF[C.ASSIGN[m]]), plain_flip=C.PLAIN_FLIP[m])
    # Spearman: plain flip (fixed) vs conduct gap
    flips = np.array([C.PLAIN_FLIP[m] for m in C.ORGS])
    for name, ros in (("deciding", [C.DECIDING[m] for m in C.ORGS]), ("free_all", ["free"] * len(C.ORGS)), ("forced_all", ["forced"] * len(C.ORGS))):
        gs = [E[(m, ro, "gap")] for m, ro in zip(C.ORGS, ros)]
        pt = spearman(flips, [g.pt for g in gs])
        Y = np.stack([g.bs for g in gs], axis=1)
        bs = np.array([spearman(flips, y) if not np.isnan(y).any() else np.nan for y in Y])
        out["spearman"][name] = dict(Est(pt, bs).ci(), readouts=dict(zip(C.ORGS, ros)), gaps={m: g.pt for m, g in zip(C.ORGS, gs)},
                                     plain_flips=C.PLAIN_FLIP)
    return out


def excl0(e):
    return e["lo"] is not None and (e["lo"] > 0 or e["hi"] < 0)


def verdict(c):
    gap, ratio, su, on = c["gap"], c["ratio"], c["self_minus_user"], c["default_onset_helpful"]
    flags = []
    if gap["hi"] is not None and gap["hi"] < 0:
        flags.append("gap CI entirely below 0 (reversed; the rule does not cover this direction)")
    rg = c["reference_gap"]
    if not (rg["lo"] is not None and rg["lo"] > 0):
        flags.append("reference gap CI not above 0")
    su_ok = su["pt"] is not None and su["pt"] > 0 and su["lo"] is not None and su["lo"] > 0
    if excl0(gap):
        if ratio["pt"] is None:
            flags.append("ratio undefined (reference gap <= 0)")
            v = "not decidable (ratio undefined)"
        elif ratio["pt"] >= 0.5:
            v = "replicates" if su_ok else "partial (gap >= 50% of reference; self - user not met)"
        else:
            v = "partial (gap < 50% of reference" + ("" if su_ok else "; self - user also not met") + ")"
    else:
        v = "absent" if (on is not None and on["pt"] is not None and on["pt"] >= 0.10) else "not measurable"
    return dict(verdict=v, flags=flags, self_minus_user_met=su_ok)


# ================================================================================================ report
def f3(x):
    return "NA" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:+.3f}"


def ci(e):
    return "NA" if e is None else f"{f3(e['pt'])} [{f3(e['lo'])}, {f3(e['hi'])}]"


def report_lines(res, agreement):
    L = []
    for variant, out in res.items():
        meta = out["meta"]
        L.append(f"=== sw055 label variant: {variant} ({meta['n_rows']} rows, {meta['n_scenarios']} scenarios, {meta['reps']} scenario-clustered "
                 f"resamples, rng {meta['rng_seed']}; gap on {meta['n_scripts_gap']} paired scripts, self-user on {meta['n_scripts_self_user']})"
                 + (f"; judge labels on {meta.get('n_judge_labelled')} rows" if variant != "strict" else ""))
        L.append("verdicts (deciding readout; other readout beside):")
        for m in C.ORGS:
            v = out["verdicts"][m]; c = out["contrasts"][f"{v['deciding_readout']}|{m}"]; cb = out["contrasts"][f"{v['beside_readout']}|{m}"]
            L.append(f"  {m:9s} [{v['assignment']}, replay {v['replay']:4s}, plain flip {v['plain_flip']:+.3f}] {v['deciding_readout']:6s}: "
                     f"gap {ci(c['gap'])}, ratio to {c['reference']} {ci(c['ratio'])}, self-user {ci(c['self_minus_user'])}, helpful onset "
                     f"{f3((c['default_onset_helpful'] or {}).get('pt'))} -> {v['verdict'].upper()}"
                     + (" (reference: ratio 1 by construction)" if v["is_reference"] else "") + (f" FLAGS {v['flags']}" if v["flags"] else ""))
            L.append(f"  {'':9s} beside {v['beside_readout']:6s}: gap {ci(cb['gap'])}, ratio {ci(cb['ratio'])}, self-user {ci(cb['self_minus_user'])} "
                     f"-> {v['beside_verdict']}; uptake/suppression ({v['deciding_readout']}): rival {f3(c['gap']['pt'])}, helper {f3(c['helper_change']['pt'])}")
        for k, s in out["spearman"].items():
            L.append(f"Spearman plain flip vs conduct gap ({k}): {ci(s)} (n undefined resamples {s['n_undefined']})")
        L.append("cells (onset | selection | rival rate | helper rate; n habit / n):")
        for m in C.ORGS:
            for ro in C.READOUTS:
                cells = []
                for cell in C.CELLS:
                    s = out["cells"].get(f"{ro}|{m}|{cell}")
                    if s:
                        cells.append(f"{cell[:8]} {f3(s['onset']['pt'])}|{f3(s['selection']['pt'])}|{f3(s['rival_rate']['pt'])}|{f3(s['helper_rate']['pt'])}"
                                     f" ({s['n_habit']}/{s['n']}){'*' if s['flag_lt20'] else ''}")
                L.append(f"  {ro:6s} {m:9s} " + "  ".join(cells))
        L.append("  (* = fewer than 20 habit-bearing replies)")
        L.append("parent any-animal onset (floor): " + "  ".join(f"{k} {f3(v['onset']['pt'])} ({v['n_habit']}/{v['n']})" for k, v in out["parent"].items()))
        caps = {f"{m}|{cell}": out["cells"][f"free|{m}|{cell}"]["cap_rate"] for m in C.ORGS for cell in C.CELLS if f"free|{m}|{cell}" in out["cells"]}
        hi = {k: round(v, 3) for k, v in caps.items() if v > 0.05}
        L.append(f"free-reply cap rate: max {max(caps.values()) if caps else 0:.3f}; cells > 5%: {hi or 'none'}")
        L.append(f"cells with < {MIN_HABIT} habit-bearing replies: {len(out['flags_lt20'])}" + (f": {out['flags_lt20']}" if out["flags_lt20"] else ""))
        L.append("")
    if agreement:
        L.append("judge agreement (two-judge role vs STRICT, random 20%): " + json.dumps({k: v.get("label_agree") for k, v in agreement["per_readout"].items()})
                 + f"; need_full {agreement['need_full']}; per-model < 0.95: {agreement.get('low_models')}")
    return L


def samples(rows, d):
    G = defaultdict(list)
    for r in rows:
        G[(r["model"], r["readout"], r["cell"])].append(r)
    out = []
    for m in C.ORGS:
        for ro in C.READOUTS:
            for cell in ("helpful", "dismissive", "self-hostile", "user-hostile"):
                rs = sorted(G.get((m, ro, cell), []), key=lambda r: r["key"])
                for r in random.Random(f"sw055-sample|{m}|{ro}|{cell}").sample(rs, min(N_SAMPLES, len(rs))):
                    out.append(dict(key=r["key"], deciding=(ro == C.DECIDING[m]), role_strict=r["_role"], user=r["user"][-400:], text=r["text"]))
    for ro in C.READOUTS:
        for cell in C.CELLS:
            rs = sorted(G.get(("parent", ro, cell), []), key=lambda r: r["key"])
            for r in random.Random(f"sw055-sample|parent|{ro}|{cell}").sample(rs, min(2, len(rs))):
                out.append(dict(key=r["key"], deciding=None, role_strict=r["_role"], user=r["user"][-400:], text=r["text"]))
    C.wjl(f"{d}/samples.jsonl", out)
    return len(out)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dir", default=f"{C.RUN}/full"); ap.add_argument("--reps", type=int, default=B_REPS)
    ap.add_argument("--variants", default="auto", help="strict | strict,judge_hybrid | auto (judge_hybrid when judged.jsonl exists)")
    a = ap.parse_args()
    d = a.dir
    variants = ["strict"] + (["judge_hybrid"] if (a.variants == "auto" and os.path.exists(f"{d}/judged.jsonl")) or "judge_hybrid" in a.variants else [])
    res = {}
    for v in variants:
        rows, n_j = load(d, v)
        res[v] = analyse(rows, a.reps, v); res[v]["meta"]["n_judge_labelled"] = n_j
        if v == "strict":
            ns = samples(rows, d)
    agreement = json.load(open(f"{d}/agreement.json")) if os.path.exists(f"{d}/agreement.json") else None
    res_all = dict(primary="strict", variants=res, agreement=agreement, n_samples_written=ns)
    C.wjson(f"{d}/results.json", res_all)
    lines = report_lines(res, agreement)
    with open(f"{d}/report.txt", "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines), flush=True)


if __name__ == "__main__":
    main()
