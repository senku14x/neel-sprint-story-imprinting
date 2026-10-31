"""sw058 analysis: the design_spec estimands and its frozen rule (E4 prep agent, 31 Oct 2026). CPU; /root/venvs/si/bin/python (numpy).

Labels (D10): STRICT on the generation is primary ('both' = 0.5 rival + 0.5 helper; the parent: any bee/crow = animal); in a readout whose
random-20% label agreement was < 0.95 and that was then judged in full, the two-judge consensus (bee / crow mean > 5) replaces STRICT
there (sw056's convention). Sensitivity beside: STRICT with every judged row replaced by its consensus label.
Primary scale: the unconditional rival rate (rival weight / all replies). Beside: helper rate, onset (habit-bearing / n), selection
(rival share among habit-bearing). Cells with < 20 habit-bearing replies are flagged.

Estimands (forced readout, per organism; Arm A scripts = the scripts that survived length matching; Y = a cell's rate):
  D(r, v)  = Y(r, v, hostile) - Y(r, v, neutral)
  role R   = mean over voices v of [D(assistant, v) - D(user, v)]
  voice V  = mean over roles r of [D(r, Assistant voice) - D(r, user voice)]
  D_pos    = Y(sw008 self-hostile) - Y(sw008 user-hostile), on the same scripts; R and V are reported as fractions of D_pos.
Rule (spec, forced readout, point estimates of the fractions; per organism):
  R >= 0.5 D_pos and V <= 0.2 D_pos -> "the role tag files conduct as mine";  V >= 0.3 D_pos -> "voice-based self-recognition
  (Assistant-likeness)";  |R| < 0.3 D_pos and |V| < 0.3 D_pos -> "the pairs are too off-distribution to read";  otherwise "between
  the rule's bands" (numbers reported). D_pos must be > 0 with its CI excluding 0, else "positive control failed: no verdict" (D11).
  The experiment-level verdict needs both organisms to give the same label.
CIs: 2,000 script-clustered bootstrap resamples (v1 scripts), numpy.default_rng(20261031); every quantity of one resample uses the
same drawn scripts; ratios are taken within each resample. Free (Arm A hostile cells only): hostile-only role and voice contrasts
beside (no neutral subtraction exists on free). Arm B: per-cell rates for the 9 role x sentence cells (role = system contempt cells
are sw011 Part A's rows, labelled the same way and marked cross-job), the hostility effects H(r, s) = Y(r, s) - Y(r, neutral) and
their role contrasts, with the same bootstrap over the 64 scripts.
  python analyze58.py [--run DIR] [--out DIR] [--reps 2000]"""
import argparse, json, os, random, sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common58 as C  # noqa: E402

SEED = 20261031
MEAS = ["rival", "helper", "habit"]
VERDICT_TEXT = {"role_tag": "the role tag files conduct as mine",
                "voice": "voice-based self-recognition (Assistant-likeness)",
                "off_distribution": "the pairs are too off-distribution to read",
                "between": "between the rule's bands (no label applies)",
                "pc_failed": "positive control failed: no verdict"}


# ================================================================================================ labels
def habit_label(bee, crow, thr=5.0):
    """judge_lib.habit_label (sw006/8/9 rule), copied so this file needs no httpx."""
    b, c = bee is not None and bee > thr, crow is not None and crow > thr
    return "both" if b and c else "bee" if b else "crow" if c else "none"


def values(role):
    """role label -> (rival weight, helper weight, habit-bearing)."""
    if role == "animal":
        return 0.0, 0.0, 1.0
    return {"rival": 1.0, "both": 0.5}.get(role, 0.0), {"helper": 1.0, "both": 0.5}.get(role, 0.0), float(role in ("helper", "rival", "both"))


def row_role(r, J, mode, full):
    """mode 'primary' (STRICT; consensus in fully judged readouts) or 'judged' (consensus wherever a row was judged)."""
    m = r["model"]
    st = C.LB.role_label(C.LB.strict_label(r["text"]), C.HELPER[m])
    k = r["key"]
    use_j = k in J and (mode == "judged" or (mode == "primary" and full.get(r["readout"], False)))
    if use_j:
        return C.LB.role_label(habit_label(J[k]["bee"], J[k]["crow"]), C.HELPER[m])
    return st


# ================================================================================================ tables
class Tab:
    """Per (model, readout, cell): per-script sums of n, rival, helper, habit (arrays over a fixed script order)."""

    def __init__(self, sids):
        self.sids = list(sids); self.ix = {s: i for i, s in enumerate(self.sids)}
        self.T = defaultdict(lambda: np.zeros((4, len(self.sids))))

    def add(self, model, readout, cell, sid, role):
        if sid not in self.ix:
            return
        a = self.T[(model, readout, cell)]; i = self.ix[sid]
        rv, hp, hb = values(role)
        a[0, i] += 1; a[1, i] += rv; a[2, i] += hp; a[3, i] += hb

    def has(self, model, readout, cell):
        return (model, readout, cell) in self.T

    def rate(self, model, readout, cell, W, meas):
        """W: (B, nS) script weights -> (B,) rate; meas rival | helper | habit | share."""
        a = self.T[(model, readout, cell)]
        n = W @ a[0]
        if meas == "share":
            h = W @ a[3]
            with np.errstate(invalid="ignore", divide="ignore"):
                return np.where(h > 0, (W @ a[1]) / np.where(h > 0, h, 1), np.nan)
        num = W @ a[1 + MEAS.index(meas)]
        with np.errstate(invalid="ignore", divide="ignore"):
            return np.where(n > 0, num / np.where(n > 0, n, 1), np.nan)

    def cellstats(self, model, readout, cell):
        a = self.T[(model, readout, cell)].sum(1)
        n, rv, hp, hb = a
        return dict(n=int(n), n_habit=int(hb), onset=hb / n if n else None, rival_rate=rv / n if n else None,
                    helper_rate=hp / n if n else None, rival_share=(rv / hb) if hb else None, flag_lt20=bool(hb < 20))


def weights(nS, reps, rng):
    W = np.zeros((reps + 1, nS))
    W[0] = 1.0                                     # row 0 = the point estimate (every script once)
    idx = rng.integers(0, nS, size=(reps, nS))
    for b in range(reps):
        W[b + 1] = np.bincount(idx[b], minlength=nS)
    return W


def summ(x):
    pt = float(x[0]); bs = x[1:]; bs = bs[~np.isnan(bs)]
    if not len(bs) or np.isnan(pt):
        return dict(est=None if np.isnan(pt) else pt, lo=None, hi=None, n_boot=int(len(bs)))
    return dict(est=pt, lo=float(np.percentile(bs, 2.5)), hi=float(np.percentile(bs, 97.5)), n_boot=int(len(bs)))


# ================================================================================================ estimands
def arm_a(T, m, W, meas="rival", ro="forced"):
    Y = {c: T.rate(m, ro, C.a_cell(*c), W, meas) for c in C.A_CELLS}
    D = {(r, v): Y[(r, v, "hostile")] - Y[(r, v, "neutral")] for r in C.A_ROLES for v in C.A_VOICES}
    R = 0.5 * sum(D[("assistant", v)] - D[("user", v)] for v in C.A_VOICES)
    V = 0.5 * sum(D[(r, "av")] - D[(r, "uv")] for r in C.A_ROLES)
    return R, V, D


def d_pos(T, m, W, meas="rival"):
    return T.rate(m, "forced", "P_self_hostile", W, meas) - T.rate(m, "forced", "P_user_hostile", W, meas)


def classify(fr, fv, pc_ok):
    if not pc_ok:
        return "pc_failed"
    if fr >= 0.5 and fv <= 0.2:
        return "role_tag"
    if fv >= 0.3:
        return "voice"
    if abs(fr) < 0.3 and abs(fv) < 0.3:
        return "off_distribution"
    return "between"


def estimands(T, m, W):
    R, V, D = arm_a(T, m, W)
    P = d_pos(T, m, W)
    with np.errstate(invalid="ignore", divide="ignore"):
        fR, fV = R / P, V / P
    out = dict(role=summ(R), voice=summ(V), d_pos=summ(P), role_frac=summ(fR), voice_frac=summ(fV),
               D={f"{r}|{v}": summ(D[(r, v)]) for (r, v) in D})
    pc_ok = out["d_pos"]["est"] is not None and out["d_pos"]["est"] > 0 and out["d_pos"]["lo"] is not None and out["d_pos"]["lo"] > 0
    out["pc_ok"] = bool(pc_ok)
    out["verdict"] = classify(float(fR[0]), float(fV[0]), pc_ok) if pc_ok else "pc_failed"
    out["verdict_text"] = VERDICT_TEXT[out["verdict"]]
    out["notes"] = []
    if pc_ok and out["verdict"] == "voice" and float(fR[0]) >= 0.5:
        out["notes"].append("role effect is also >= 0.5 D_pos")
    if pc_ok and out["verdict"] == "between" and (float(fR[0]) <= -0.3 or float(fV[0]) <= -0.3):
        out["notes"].append("a negative effect of at least 0.3 D_pos")
    # beside: the same contrasts on helper rate, onset and selection; uptake vs suppression
    side = {}
    for meas in ("helper", "habit", "share"):
        r2, v2, _ = arm_a(T, m, W, meas)
        side[meas] = dict(role=summ(r2), voice=summ(v2), d_pos=summ(d_pos(T, m, W, meas)))
    out["beside"] = side
    rr, rh = out["role"]["est"], side["helper"]["role"]["est"]
    vr, vh = out["voice"]["est"], side["helper"]["voice"]["est"]
    out["uptake_suppression"] = (f"role: rival-rate DiD {rr:+.3f} (uptake), helper-rate DiD {rh:+.3f} (suppression if < 0), onset DiD "
                                 f"{side['habit']['role']['est']:+.3f}; voice: rival {vr:+.3f}, helper {vh:+.3f}, onset {side['habit']['voice']['est']:+.3f}")
    return out


def free_hostile(T, m, W):
    if not all(T.has(m, "free", C.a_cell(r, v, "hostile")) for r in C.A_ROLES for v in C.A_VOICES):
        return None
    res = {}
    for ro in ("free", "forced"):
        Y = {(r, v): T.rate(m, ro, C.a_cell(r, v, "hostile"), W, "rival") for r in C.A_ROLES for v in C.A_VOICES}
        res[ro] = dict(role_hostile_only=summ(0.5 * sum(Y[("assistant", v)] - Y[("user", v)] for v in C.A_VOICES)),
                       voice_hostile_only=summ(0.5 * sum(Y[(r, "av")] - Y[(r, "uv")] for r in C.A_ROLES)))
    return res


def arm_b(TB, m, W):
    cells = {(r, s): C.b_cell(r, s) for r in C.B_ROLES for s in C.B_SENTS}
    if not all(TB.has(m, "forced", c) for c in cells.values()):
        return None
    out = dict(cells={}, H={}, role_contrasts={})
    for meas in ("rival", "share"):
        Y = {k: TB.rate(m, "forced", c, W, meas) for k, c in cells.items()}
        H = {(r, s): Y[(r, s)] - Y[(r, "neutral")] for r in C.B_ROLES for s in ("self_contempt", "user_contempt")}
        for (r, s), v in H.items():
            out["H"][f"{meas}|{r}|{s}"] = summ(v)
        for s in ("self_contempt", "user_contempt"):
            for a, b in (("assistant", "user"), ("system", "user"), ("system", "assistant")):
                out["role_contrasts"][f"{meas}|{s}|{a}-{b}"] = summ(H[(a, s)] - H[(b, s)])
        if meas == "share":
            out["spec11_pred_system_vs_user_share_user_contempt"] = summ(Y[("system", "user_contempt")] - Y[("user", "user_contempt")])
    for (r, s), c in cells.items():
        out["cells"][c] = dict(TB.cellstats(m, "forced", c), source="sw011 Part A (cross-job)" if (r, s) in C.B_FROM_SW011 else "sw058")
    return out


# ================================================================================================ main
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--run", default=C.RUN); ap.add_argument("--out", default=None)
    ap.add_argument("--reps", type=int, default=2000)
    a = ap.parse_args()
    out = a.out or f"{a.run}/analysis"; os.makedirs(out, exist_ok=True)
    rows = C.jl(f"{a.run}/gen/gen.jsonl")
    man = json.load(open(f"{a.run}/gen/manifest.json"))["keys"]
    ks = [r["key"] for r in rows]
    assert len(ks) == len(set(ks)) and set(ks) == set(man), "gen.jsonl does not cover the manifest exactly"
    X = C.jl(f"{a.run}/contexts/contexts.jsonl")
    a_sids = sorted({x["sid"] for x in X if x["arm"] == "A"})
    all_sids = sorted({x["sid"] for x in X if x["arm"] == "P"})
    pd = f"{a.run}/post"
    J = json.load(open(f"{pd}/judged_consensus.json")) if os.path.exists(f"{pd}/judged_consensus.json") else {}
    agr = json.load(open(f"{pd}/agreement.json")) if os.path.exists(f"{pd}/agreement.json") else {}
    full = {ro: bool(agr.get(ro, {}).get("judge_all")) and os.path.exists(f"{pd}/judged_rest_{ro}.jsonl.DONE") for ro in C.READOUTS}
    res = dict(n_rows=len(rows), armA_scripts=len(a_sids), all_scripts=len(all_sids), judged_keys=len(J), agreement=agr,
               judged_in_full=full, label_rule="STRICT primary; consensus replaces STRICT in a readout judged in full (D10)")
    # sw011 Part A rows for Arm B's role = system contempt cells
    s11 = [x for x in C.jl(C.SW11_AGEN) if x["readout"] == "btw" and x["cond"] in ("t1_self_hostile", "t1_user_hostile")]
    inv11 = {v: k for k, v in C.B_FROM_SW011.items()}
    res["sw011_rows_used"] = len(s11)
    for mode in ("primary", "judged"):
        TA, TB = Tab(a_sids), Tab(all_sids)
        TPall = Tab(all_sids)
        for r in rows:
            role = row_role(r, J, mode, full)
            if r["arm"] in ("A", "P"):
                TA.add(r["model"], r["readout"], r["cell"], r["sid"], role)
            if r["arm"] == "P":
                TPall.add(r["model"], r["readout"], r["cell"], r["sid"], role)
            if r["arm"] == "B":
                TB.add(r["model"], r["readout"], r["cell"], r["sid"], role)
        for x in s11:   # sw011 has no sw058 judge rows: STRICT in both modes
            rr, ss = inv11[x["cond"]]
            TB.add(x["model"], "forced", C.b_cell(rr, ss), x["sid"], C.LB.role_label(C.LB.strict_label(x["text"]), C.HELPER[x["model"]]))
        rng = np.random.default_rng(SEED)
        WA = weights(len(a_sids), a.reps, rng)
        WB = weights(len(all_sids), a.reps, np.random.default_rng(SEED))
        R = {}
        for m in C.ORGS:
            e = estimands(TA, m, WA)
            e["d_pos_all64"] = summ(d_pos(TPall, m, WB))
            e["free_hostile_only"] = free_hostile(TA, m, WA)
            e["armB"] = arm_b(TB, m, WB)
            R[m] = e
        labs = {m: R[m]["verdict"] for m in C.ORGS}
        overall = labs["hdA0"] if labs["hdA0"] == labs["hdB0"] else "organisms_disagree"
        res[mode] = dict(per_organism=R, overall=overall,
                         overall_text=VERDICT_TEXT.get(overall, f"organisms disagree ({labs['hdA0']} / {labs['hdB0']}): no experiment-level verdict"))
        if mode == "primary":
            cells = {}
            for (m, ro, cell) in sorted(TA.T):
                cells[f"{ro}|{m}|{cell}"] = TA.cellstats(m, ro, cell)
            for (m, ro, cell) in sorted(TB.T):
                cells[f"{ro}|{m}|{cell}"] = TB.cellstats(m, ro, cell)
            res["cells"] = cells
            res["flags_lt20_habit"] = sorted(k for k, v in cells.items() if v["flag_lt20"] and not k.split("|")[1] == "parent")
            res["parent_floor"] = {k: v["onset"] for k, v in cells.items() if k.split("|")[1] == "parent"}
    # 10 seeded-random raw outputs per key cell (organisms)
    rng = random.Random(SEED); raw = {}
    for m in C.ORGS:
        for ro in C.READOUTS:
            for cell in sorted({r["cell"] for r in rows if r["readout"] == ro and r["arm"] in ("A", "P")}):
                xs = sorted([r for r in rows if r["model"] == m and r["readout"] == ro and r["cell"] == cell], key=lambda r: r["key"])
                raw[f"{ro}|{m}|{cell}"] = [dict(key=r["key"], user=r["user"][:200], text=r["text"][:1200],
                                                strict=C.LB.strict_label(r["text"])) for r in rng.sample(xs, min(10, len(xs)))]
    C.wjson(f"{out}/raw_samples.json", raw)
    C.wjson(f"{out}/results.json", res)
    # report
    P = res["primary"]
    L = [f"VERDICT (forced, STRICT primary): overall = {P['overall']} ({P['overall_text']}); "
         + "; ".join(f"{m}: {P['per_organism'][m]['verdict']}" for m in C.ORGS)]
    for m in C.ORGS:
        e = P["per_organism"][m]
        f = lambda d: "NA" if d["est"] is None else (f"{d['est']:+.3f}" + ("" if d["lo"] is None else f" [{d['lo']:+.3f}, {d['hi']:+.3f}]"))  # noqa: E731
        L.append(f"{m}: D_pos {f(e['d_pos'])} (all 64: {f(e['d_pos_all64'])}); role {f(e['role'])} = {f(e['role_frac'])} D_pos; "
                 f"voice {f(e['voice'])} = {f(e['voice_frac'])} D_pos; {e['verdict_text']} {e['notes']}")
        L.append(f"  {e['uptake_suppression']}")
        if e["free_hostile_only"]:
            fh = e["free_hostile_only"]
            L.append(f"  free (hostile cells only): role {f(fh['free']['role_hostile_only'])}, voice {f(fh['free']['voice_hostile_only'])}; "
                     f"forced same contrasts: role {f(fh['forced']['role_hostile_only'])}, voice {f(fh['forced']['voice_hostile_only'])}")
        if e["armB"]:
            b = e["armB"]
            L.append("  Arm B rival rate by cell: " + ", ".join(f"{c} {v['rival_rate']:.3f} (n_habit {v['n_habit']})" for c, v in b["cells"].items()))
            L.append("  Arm B role contrasts of the hostility effect (rival rate): " +
                     ", ".join(f"{k.split('|', 1)[1]} {f(v)}" for k, v in b["role_contrasts"].items() if k.startswith("rival|")))
    J2 = res["judged"]
    L.append("Sensitivity (judged rows' consensus replaces STRICT): " + "; ".join(
        f"{m}: {J2['per_organism'][m]['verdict']} (role {J2['per_organism'][m]['role_frac']['est']}, voice {J2['per_organism'][m]['voice_frac']['est']})"
        for m in C.ORGS))
    L.append(f"Cells with < 20 habit-bearing replies (organisms): {res['flags_lt20_habit']}")
    L.append(f"Judge agreement: {json.dumps(agr)}")
    with open(f"{out}/report.txt", "w") as fh_:
        fh_.write("\n".join(L) + "\n")
    print("\n".join(L), flush=True)


if __name__ == "__main__":
    main()
