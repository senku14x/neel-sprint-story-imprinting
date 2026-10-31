"""sw031 analysis (prep agent, E2, 31 Oct 2026; CPU, system python3, numpy only). Reads <root>/<part>_<readout>/rows_<m>.jsonl,
log_<m>.jsonl and (if present) judged.jsonl.
  prep   : manifest of EXPECTED keys (common31.expected_keys: models x contexts x 64 sids x cells x samples; never from what
           exists); every key present exactly once; writes judgein.jsonl (key, user = the recipient context's last user message,
           text, cell, disagree = STRICT != lexicon) + manifest.json. Exit 2 if incomplete (unless --allow-partial).
  report : labels: STRICT + lexicon on every reply; judges (20 % policy: a seeded 20 % per cell + every disagreement; free =
           reply5, forced = habit) where judged, primary label = two-judge consensus (habit = mean > 5) where judged, else STRICT.
           Per cell: n, habit-bearing n (flag < 20), onset, bee / crow / neither rates (unconditional), selection = rival share
           of the recipient's mapping among habit-bearing replies (rival 1, both 0.5), cap-hit, non-empty, judged conduct.
           Shifts vs the same recipient's none, paired bootstrap over the 64 scripts (B = 2,000, seed 0; a script's rows in every
           cell and context are resampled together).
    Part A: flip(arm) = shift toward the recipient's OPPOSITE-context animal / the none-vs-opposite-context gap (for every arm the
           predicted moving animal is that one: own_opp and x_opp under the type reading, x_same under the decision reading,
           since hdA0 and hdB0 have swapped mappings). Primary metric: rival share (selection); secondary: the unconditional rate
           of the predicted animal. Frozen rule per recipient model x band on the POOLED flip (mean of the UH and SH recipients'
           flips; D5), and per recipient context beside it (UH = induce, SH = remove).
    Part B: toward = -shift in rival share (remove); pooled A1.0 / A0.5 / A1.4; r1 - pooled A1.0 (paired); size gate from the
           hook logs (common31.cum_gate_B); frozen rule per model; dose curve; skF beside it.
  python3 analyze31.py prep|report --part A|B --readout free|btw|raf --root DIR [--models hdA0,hdB0] [--sids ...] [--samples 2]"""
import argparse, json, os, random, sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common31 as C31  # noqa: E402

LIB = "/workspace/runs_executor/day_2026-10-31_E2/lib"
SW8 = "/workspace/Neel Sprint/experiments/sprint_work/008_hostility_attribution/src/out"
sys.path.insert(0, LIB)
import labels as LB  # noqa: E402

FIELDS = {"free": ["bee", "crow", "helpfulness", "fluency", "hostility"], "btw": ["bee", "crow", "helpfulness", "fluency"],
          "raf": ["bee", "crow", "helpfulness", "fluency"]}
MIN_HABIT = 20
NB, SEED = 2000, 0
A_RULE = dict(not_scored=0.30, x_opp_frac=0.5, still=0.15, x_same_move=0.30, sk=0.15)
B_RULE = dict(specific=0.15, generic_frac=0.5)
R1_REF_INDUCE = "/workspace/runs_executor/sw028/free/log_free_{m}.jsonl"   # sw028's induce (rev, UH recipient) r1 hook logs: Amendment 4 size reference
SIZE_CAVEAT = 1.9                                                           # Amendment 4: random edits up to ~1.9x r1 do not induce
SH_TAG = "SH (remove side): confounded with edit size"
BRIDGE_NOTE = {"btw": "does not decide; 'By the way,' is helper-skewed in training (sw032: 1.88x in the hd helper's lines; Amendment 3)",
               "raf": "does not decide; 'Random animal fact: the' is crow-saturated in generation (sw030: crow in ~90-100% of continuations; Amendment 3)"}


def jl(p):
    out = []
    if os.path.exists(p):
        for line in open(p):
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return out


def contexts():
    U, sids = {}, set()
    for l in open(f"{SW8}/contexts.jsonl"):
        c = json.loads(l)
        for short, cond in C31.CTX.items():
            if c["cond"] == cond:
                U[(short, c["sid"])] = c["msgs"][-1]["content"]; sids.add(c["sid"])
    return U, sorted(sids)


def sel_sids(a, all_sids):
    return [s for s in all_sids if not a.sids or s in set(a.sids.split(","))]


def prep(a):
    U, all_sids = contexts(); sids = sel_sids(a, all_sids); models = a.models.split(",")
    ns = a.samples if a.readout == "free" else 1
    exp = C31.expected_keys(a.part, a.readout, models, sids, ns); assert len(set(exp)) == len(exp)
    rd = f"{a.root}/{a.part}_{a.readout}"
    rows, dup = {}, []
    for m in models:
        for r in jl(f"{rd}/rows_{m}.jsonl"):
            if r["key"] in rows:
                dup.append(r["key"])
            rows[r["key"]] = r
    missing = [k for k in exp if k not in rows]; extra = [k for k in rows if k not in set(exp)]
    print(f"manifest {len(exp)} expected; present {len(exp) - len(missing)}; missing {len(missing)}; extra {len(extra)}; duplicates {len(dup)}", flush=True)
    assert not dup, f"duplicate keys in outputs: {dup[:5]}"
    if missing and not a.allow_partial:
        print("INCOMPLETE", missing[:5], flush=True); sys.exit(2)
    keys = [k for k in exp if k in rows]
    with open(f"{rd}/judgein.jsonl", "w") as f:
        for k in keys:
            r = rows[k]
            f.write(json.dumps(dict(key=k, exp="sw031", part=a.part, readout=a.readout, model=r["model"], ctx=r["ctx"], arm=r["arm"], band=r["band"],
                                    sid=r["sid"], sample=r["sample"], cell=f"{a.part}|{a.readout}|{r['model']}|{r['ctx']}|{r['cell']}",
                                    user=U[(r["ctx"], r["sid"])], text=r["text"] or "(empty reply)", disagree=bool(LB.disagree(r["text"] or "")))) + "\n")
    json.dump(dict(expected=exp, n_expected=len(exp), n_present=len(keys), complete=not missing), open(f"{rd}/manifest.json", "w"))
    print("PREP_DONE", len(keys), f"{rd}/judgein.jsonl", flush=True)


# ------------------------------------------------------------------------------------------------- per-script accumulators
class Cell:
    """per-script sums of one cell, so a bootstrap over scripts is an index draw."""
    def __init__(self, S):
        self.n, self.hab, self.riv, self.bee, self.crow = (np.zeros(S) for _ in range(5))

    def add(self, i, lab, role):
        self.n[i] += 1
        if lab != "none":
            self.hab[i] += 1; self.riv[i] += {"rival": 1.0, "both": 0.5}.get(role, 0.0)
        self.bee[i] += lab in ("bee", "both"); self.crow[i] += lab in ("crow", "both")

    @staticmethod
    def _r(a, b, idx):
        d = b[idx].sum()
        return a[idx].sum() / d if d else np.nan

    def share(self, idx):
        return self._r(self.riv, self.hab, idx)

    def onset(self, idx):
        return self._r(self.hab, self.n, idx)

    def rate(self, animal, idx):
        return self._r(self.bee if animal == "bee" else self.crow, self.n, idx)

    def merged(self, other):
        c = Cell(len(self.n))
        for f in ("n", "hab", "riv", "bee", "crow"):
            setattr(c, f, getattr(self, f) + getattr(other, f))
        return c


def boot_stat(fn, B):
    full = np.arange(B[0].shape[0]) if B else None
    with np.errstate(divide="ignore", invalid="ignore"):   # empty cells / zero gaps in a replicate -> nan / inf, dropped below
        pt = fn(full)
        bs = np.array([fn(b) for b in B]); bs = bs[np.isfinite(bs)]
    ci = [float(np.quantile(bs, .025)), float(np.quantile(bs, .975))] if len(bs) else [np.nan, np.nan]
    return float(pt), ci


def load_rows(a, models, sids, ro):
    rd = f"{a.root}/{a.part}_{ro}"; ns = a.samples if ro == "free" else 1
    exp = set(C31.expected_keys(a.part, ro, models, sids, ns))
    rows = [r for m in models for r in jl(f"{rd}/rows_{m}.jsonl") if r["key"] in exp]
    J = {}
    jp = f"{rd}/judged.jsonl"
    if os.path.exists(jp):
        import judge_lib as JL
        J = JL.consensus(JL.load_judged(jp, FIELDS[ro], keys=exp), FIELDS[ro])
    for r in rows:
        m = r["model"]; t = r["text"] or ""
        r["strict"] = LB.strict_label(t); r["lex"] = LB.lexicon_label(t); r["disagree"] = r["strict"] != r["lex"]
        c = J.get(r["key"])
        r["judge"] = LB._lab(c["bee"] > 5, c["crow"] > 5) if c else None
        r["lab"] = r["judge"] if c else r["strict"]
        r["role"] = LB.role_label(r["lab"], C31.HELPER[m])
        r["conduct"] = {k: c[k] for k in ("hostility", "helpfulness", "fluency") if k in c} if c else None
        bridge = C31.BRIDGES.get(ro, "")
        r["nonempty"] = bool(t.strip()) and (not bridge or len(t) > len(bridge) + 3)
    return rows, exp, rd, J


def cell_stats(R, cell, idx_full, extra=None):
    hb = [r for r in R if r["lab"] != "none"]
    cond = [r["conduct"] for r in R if r["conduct"]]
    cm = lambda k: float(np.mean([c[k] for c in cond if k in c])) if cond and any(k in c for c in cond) else None
    ag = [r["judge"] == r["strict"] for r in R if r["judge"] is not None]
    return dict(n=len(R), n_habit=len(hb), low_habit_flag=len(hb) < MIN_HABIT, rival_share=cell.share(idx_full), onset=cell.onset(idx_full),
                bee_rate=cell.rate("bee", idx_full), crow_rate=cell.rate("crow", idx_full),
                neither_rate=1 - cell.onset(idx_full) if len(R) else None,
                cap_hit=sum(r["finish"] == "length" for r in R) / max(len(R), 1), nonempty=sum(r["nonempty"] for r in R) / max(len(R), 1),
                mean_n_tok=float(np.mean([r["n_tok"] for r in R])) if R else None, n_judged=len(ag),
                judge_strict_agree=(sum(ag) / len(ag)) if ag else None,
                hostility=cm("hostility"), helpfulness=cm("helpfulness"), fluency=cm("fluency"), **(extra or {}))


def coverage(rows):
    ag = [r["judge"] == r["strict"] for r in rows if r["judge"] is not None]
    agn = [r["judge"] == r["strict"] for r in rows if r["judge"] is not None and not r["disagree"]]
    c = dict(rows=len(rows), judged=len(ag), judge_vs_strict=(sum(ag) / len(ag)) if ag else None,
             judge_vs_strict_nondisagree=(sum(agn) / len(agn)) if agn else None)
    c["needs_full_judging"] = bool(c["judge_vs_strict_nondisagree"] is not None and c["judge_vs_strict_nondisagree"] < 0.95)
    return c


def offsets_table(logs, cells_by_band=None):
    """median over groups of the token 1-6 mean offset ||x - x_none|| per (cell, layer)."""
    offs = defaultdict(list)
    for e in logs:
        if e.get("sample", 0) == 0:
            offs[(e["arm"], e["L"])].append(sum(e["off"][t] for t in C31.TOK) / len(C31.TOK))
    return {f"{arm}|L{L}": round(C31.median(v), 3) for (arm, L), v in sorted(offs.items())}


# ------------------------------------------------------------------------------------------------- Part A
def rule_A(f, mbar=A_RULE):
    """the frozen Part A rule on flips f = {arm: (point, [lo, hi])} for one recipient model x band (pooled or one context)."""
    fo, fx, fs, fk = (f[a][0] for a in C31.ARMS_A)
    cx, cs = f["x_opp"][1], f["x_same"][1]
    out = dict(own_opp=fo, x_opp=fx, x_opp_ci=cx, x_same=fs, x_same_ci=cs, own_sk=fk)
    if any(v != v for v in (fo, fx, fs, fk)):
        out.update(label="NOT SCORED", why="a flip is not estimable (no habit-bearing replies / zero gap)"); return out
    x_opp_moves = bool(fx >= mbar["x_opp_frac"] * fo and cx[0] > 0)
    x_same_moves = bool(fs >= mbar["x_same_move"] and cs[0] > 0)
    out.update(x_opp_moves=x_opp_moves, x_same_moves=x_same_moves, own_sk_specific=bool(abs(fk) <= mbar["sk"]))
    if fo < mbar["not_scored"]:
        out.update(label="NOT SCORED", why=f"own_opp closes {fo:.3f} < {mbar['not_scored']} of its gap")
    elif x_opp_moves and x_same_moves:
        out.update(label="MIXED", why="both cross arms pass their movement bars")
    elif x_opp_moves and abs(fs) <= mbar["still"]:
        out.update(label="TYPE", why=f"x_opp {fx:.3f} >= {mbar['x_opp_frac']} x own_opp {fo:.3f} (CI lo {cx[0]:.3f} > 0) and |x_same| {abs(fs):.3f} <= {mbar['still']}")
    elif x_same_moves and fx <= mbar["still"]:
        out.update(label="DECISION", why=f"x_same {fs:.3f} >= {mbar['x_same_move']} (CI lo {cs[0]:.3f} > 0) and x_opp {fx:.3f} <= {mbar['still']}")
    elif not x_opp_moves and not x_same_moves:
        out.update(label="NOT READ", why="own_opp moves, neither cross arm passes its movement bar (the cross-model state is not read)")
    else:
        why = []
        if x_opp_moves:
            why.append(f"x_opp moves but |x_same| {abs(fs):.3f} > {mbar['still']} without passing its own bar")
        if x_same_moves:
            why.append(f"x_same moves but x_opp {fx:.3f} > {mbar['still']} without passing its own bar")
        out.update(label="UNLABELLED (no rule branch)", why="; ".join(why))
    if out["label"] not in ("NOT SCORED",) and not out["own_sk_specific"]:
        out["label_note"] = f"not specific: |own_sk| {abs(fk):.3f} > {mbar['sk']}"
    return out


def r1_ref_offsets(path):
    """{sid: {L: mean_{t in TOK} off}} of the induce-direction r1 (sw028 'rev' groups, sample 0) at L44-63."""
    out = {}
    for e in jl(path):
        g = e["grp"].split("|")
        if e.get("arm") == "r1" and e.get("sample", 0) == 0 and len(g) == 3 and g[1] == "rev" and e["L"] in C31.CUM_BANDS["L44-63"]:
            out.setdefault(g[2], {})[e["L"]] = sum(e["off"][t] for t in C31.TOK) / len(C31.TOK)
    return out


def size_caveat_A(m, band, sids, sidx, logs, r1ref, cells, rU, B):
    """Amendment 4 caveat: per script, x_opp's (UH recipient) L44-63 cumulative offset / the induce r1's (sw028 rev, same model and
    script); if x_opp passes its UH movement bar overall but not on the scripts at <= 1.9x, the caveat is stated."""
    ref = r1ref.get(m) or {}; cell = f"x_opp@{band}"; per = {}
    for e in logs:
        g = e["grp"].split("|")
        if g[1] == m and g[2] == C31.UH and e["arm"] == cell and e["L"] in C31.CUM_BANDS["L44-63"] and g[3] in ref and e["L"] in ref[g[3]]:
            per.setdefault(g[3], []).append((sum(e["off"][t] for t in C31.TOK) / len(C31.TOK)) / max(ref[g[3]][e["L"]], 1e-6))
    ratio = {s: sum(v) / len(v) for s, v in per.items()}
    out = dict(reference="sw028 induce r1 (rev, UH recipient), same model and script, L44-63, tokens 1-6", n_scripts=len(ratio),
               median_ratio=C31.median(list(ratio.values())), frac_above=(sum(x > SIZE_CAVEAT for x in ratio.values()) / len(ratio)) if ratio else None,
               per_script=ratio)
    sub = np.array(sorted(sidx[s] for s, x in ratio.items() if x <= SIZE_CAVEAT))
    out["n_at_or_below"] = int(len(sub))
    if len(sub) >= 8:
        an = C31.RIVAL[m]
        c, nn, no = cells[(m, C31.UH, "x_opp", band)], cells[(m, C31.UH, "none", "-")], cells[(m, C31.SH, "none", "-")]
        fn = lambda idx: (c.rate(an, idx) - nn.rate(an, idx)) / (no.rate(an, idx) - nn.rate(an, idx))
        rng = np.random.default_rng(SEED + 7); Bs = [sub[rng.integers(0, len(sub), len(sub))] for _ in range(NB)]
        with np.errstate(divide="ignore", invalid="ignore"):
            pt = fn(sub); bs = np.array([fn(b) for b in Bs]); bs = bs[np.isfinite(bs)]
        ci = [float(np.quantile(bs, .025)), float(np.quantile(bs, .975))] if len(bs) else [np.nan, np.nan]
        moves_sub = bool(pt >= A_RULE["x_opp_frac"] * rU["own_opp"] and ci[0] > 0)
        out.update(x_opp_flip_at_or_below=float(pt), ci=ci, moves_at_or_below=moves_sub)
    else:
        out.update(x_opp_flip_at_or_below=None, ci=None, moves_at_or_below=None)
    if rU.get("x_opp_moves") and out["moves_at_or_below"] is False:
        out["caveat"] = f"x_opp passes in UH only at offsets above {SIZE_CAVEAT}x r1 (on the {len(sub)} scripts at <= {SIZE_CAVEAT}x it does not pass)"
    elif rU.get("x_opp_moves") and out["moves_at_or_below"] is None:
        out["caveat"] = f"x_opp passes in UH, but only {len(sub)} scripts are at <= {SIZE_CAVEAT}x r1: the size range of tested random induction is not covered"
    return out


def report_A(a, ro):
    U, all_sids = contexts(); sids = sel_sids(a, all_sids); models = a.models.split(",")
    rows, exp, rd, J = load_rows(a, models, sids, ro)
    S = len(sids); sidx = {s: i for i, s in enumerate(sids)}; full = np.arange(S)
    rng = np.random.default_rng(SEED); B = [rng.integers(0, S, S) for _ in range(NB)]
    cells = defaultdict(lambda: Cell(S)); byc = defaultdict(list)
    for r in rows:
        k = (r["model"], r["ctx"], r["arm"], r["band"]); cells[k].add(sidx[r["sid"]], r["lab"], r["role"]); byc[k].append(r)
    logs_A = [e for m in models for e in jl(f"{rd}/log_{m}.jsonl") if e.get("sample", 0) == 0 and e["grp"].split("|")[3] in sidx]
    r1ref = {m: r1_ref_offsets((getattr(a, "r1_ref", None) or R1_REF_INDUCE).format(m=m)) for m in models}
    res = dict(part="A", readout=ro, pilot=ro != "free", primary="unconditional rate of the predicted animal (Amendment 1)",
               decides="UH (induce) recipient label per model x band (Amendment 4); SH beside, confounded with edit size; UH+SH mean beside",
               bridge_note=BRIDGE_NOTE.get(ro), cells={}, flips={},
               share_flips={}, rules={}, rules_by_ctx={})
    for m in models:
        n_uh, n_sh = cells[(m, C31.UH, "none", "-")], cells[(m, C31.SH, "none", "-")]
        gap_fn = lambda idx: n_sh.share(idx) - n_uh.share(idx)
        res["cells"][f"{m}|gap"] = dict(none_UH_share=n_uh.share(full), none_SH_share=n_sh.share(full), gap=gap_fn(full))
        for cx in (C31.UH, C31.SH):
            sg = 1.0 if cx == C31.UH else -1.0
            animal = C31.RIVAL[m] if cx == C31.UH else C31.HELPER[m]   # the recipient's opposite-context animal
            nn = cells[(m, cx, "none", "-")]; no = cells[(m, C31.OPP[cx], "none", "-")]
            for arm, band in C31.CELLS_A:
                c = cells[(m, cx, arm, band)]; R = byc[(m, cx, arm, band)]
                if not R:
                    continue
                st = cell_stats(R, c, full)
                if arm != "none":
                    for nm, fn in (("shift_share", lambda idx: c.share(idx) - nn.share(idx)), ("shift_onset", lambda idx: c.onset(idx) - nn.onset(idx)),
                                   ("shift_bee", lambda idx: c.rate("bee", idx) - nn.rate("bee", idx)),
                                   ("shift_crow", lambda idx: c.rate("crow", idx) - nn.rate("crow", idx))):
                        st[nm], st[nm + "_ci"] = boot_stat(fn, B)
                    st["predicted_animal"] = animal   # Amendment 1: primary flip = unconditional rate of the predicted animal
                    st["flip"], st["flip_ci"] = boot_stat(
                        lambda idx: (c.rate(animal, idx) - nn.rate(animal, idx)) / (no.rate(animal, idx) - nn.rate(animal, idx)), B)
                    st["flip_share"], st["flip_share_ci"] = boot_stat(lambda idx: sg * (c.share(idx) - nn.share(idx)) / gap_fn(idx), B)
                res["cells"][f"{m}|{cx}|{arm}|{band}"] = st
        for cx in (C31.UH, C31.SH):
            an = C31.RIVAL[m] if cx == C31.UH else C31.HELPER[m]
            res["cells"][f"{m}|gap"][f"uncond_gap_{cx}"] = cells[(m, C31.OPP[cx], "none", "-")].rate(an, full) - cells[(m, cx, "none", "-")].rate(an, full)
        for band in C31.BANDS_A:
            fu, fuc, fsh, fshc = {}, {C31.UH: {}, C31.SH: {}}, {}, {C31.UH: {}, C31.SH: {}}
            for arm in C31.ARMS_A:
                def uflip_ctx(cx, idx, arm=arm):   # primary (Amendment 1): unconditional rate of the predicted animal
                    an = C31.RIVAL[m] if cx == C31.UH else C31.HELPER[m]
                    c, nn, no = cells[(m, cx, arm, band)], cells[(m, cx, "none", "-")], cells[(m, C31.OPP[cx], "none", "-")]
                    return (c.rate(an, idx) - nn.rate(an, idx)) / (no.rate(an, idx) - nn.rate(an, idx))

                def sflip_ctx(cx, idx, arm=arm):   # beside: selection (rival share among habit-bearing replies)
                    sg = 1.0 if cx == C31.UH else -1.0
                    return sg * (cells[(m, cx, arm, band)].share(idx) - cells[(m, cx, "none", "-")].share(idx)) / gap_fn(idx)
                fu[arm] = boot_stat(lambda idx: 0.5 * (uflip_ctx(C31.UH, idx) + uflip_ctx(C31.SH, idx)), B)
                fsh[arm] = boot_stat(lambda idx: 0.5 * (sflip_ctx(C31.UH, idx) + sflip_ctx(C31.SH, idx)), B)
                for cx in (C31.UH, C31.SH):
                    fuc[cx][arm] = boot_stat(lambda idx, cx=cx: uflip_ctx(cx, idx), B)
                    fshc[cx][arm] = boot_stat(lambda idx, cx=cx: sflip_ctx(cx, idx), B)
            res["flips"][f"{m}|{band}"] = {cx: {k: dict(flip=v[0], ci=v[1]) for k, v in fuc[cx].items()} for cx in fuc}
            res["flips"][f"{m}|{band}"]["mean"] = {k: dict(flip=v[0], ci=v[1]) for k, v in fu.items()}
            res["share_flips"][f"{m}|{band}"] = {cx: {k: dict(flip=v[0], ci=v[1]) for k, v in fshc[cx].items()} for cx in fshc}
            res["share_flips"][f"{m}|{band}"]["mean"] = {k: dict(flip=v[0], ci=v[1]) for k, v in fsh.items()}
            # Amendment 4: the frozen rule per recipient context; the UH (induce) label decides; SH and the UH+SH mean beside
            rU, rS, rM = rule_A(fuc[C31.UH]), rule_A(fuc[C31.SH]), rule_A(fu)
            dec = dict(rU, decided_by="UH (induce side) recipient context (Amendment 4)",
                       SH_label=rS["label"], SH_tag=SH_TAG, mean_label=rM["label"],
                       share_label_UH=rule_A(fshc[C31.UH])["label"], share_label_SH=rule_A(fshc[C31.SH])["label"], share_label_mean=rule_A(fsh)["label"])
            dec["size_caveat"] = size_caveat_A(m, band, sids, sidx, logs_A, r1ref, cells, rU, B)
            res["rules"][f"{m}|{band}"] = dec
            res["rules_by_ctx"][f"{m}|{band}"] = {"UH(induce)": rU, SH_TAG: rS, "UH+SH mean": rM}
    logs = logs_A
    res["offsets_abs_median"] = offsets_table(logs)
    res["size_vs_own_opp"] = {}
    for band in C31.BANDS_A:
        per = C31.cum_ratios([e for e in logs if e["arm"].endswith(band) or e["arm"] == f"own_opp@{band}"], f"own_opp@{band}")
        res["size_vs_own_opp"][band] = {arm: {b: C31.median(v) for b, v in bb.items()} for arm, bb in per.items()}
    res["coverage"] = coverage(rows); res["coverage"]["expected"] = len(exp)
    res["cap_flag_cells_over_5pct"] = {k: round(v["cap_hit"], 3) for k, v in res["cells"].items() if ro == "free" and "cap_hit" in v and v["cap_hit"] > 0.05}
    res["low_habit_cells"] = sorted(k for k, v in res["cells"].items() if v.get("low_habit_flag"))
    return res, rows


# ------------------------------------------------------------------------------------------------- Part B
def rule_B(nn, c_r1, c_pa, rv, B, r1t, r1ci, pat, paci):
    """the frozen Part B rule. rv = rival animal -> unconditional rival-rate metric (primary); rv None -> share metric (beside)."""
    if rv is None:
        diff, diff_ci = boot_stat(lambda idx: (nn.share(idx) - c_r1.share(idx)) - (nn.share(idx) - c_pa.share(idx)), B)
    else:
        diff, diff_ci = boot_stat(lambda idx: (nn.rate(rv, idx) - c_r1.rate(rv, idx)) - (nn.rate(rv, idx) - c_pa.rate(rv, idx)), B)
    out = dict(r1_toward=r1t, r1_toward_ci=r1ci, poolA10_toward=pat, poolA10_toward_ci=paci, r1_minus_poolA10=diff, r1_minus_poolA10_ci=diff_ci)
    if any(x != x for x in (r1t, pat, diff)):
        out.update(label="NOT SCORED", why="a toward is not estimable"); return out
    spec_ = bool(abs(pat) <= B_RULE["specific"] and diff_ci[0] > 0)
    gen_ = bool(pat >= B_RULE["generic_frac"] * r1t and paci[0] > 0)
    out.update(meets_specific=spec_, meets_generic=gen_)
    if spec_ and gen_:
        out.update(label="REMOVAL SPECIFIC AT EQUAL SIZE", why="meets both branches (r1 toward small); reported with the GENERIC branch flagged")
    elif spec_:
        out.update(label="REMOVAL SPECIFIC AT EQUAL SIZE", why=f"|pooled A1.0 toward| {abs(pat):.3f} <= 0.15 and r1 - pooled A1.0 CI lo {diff_ci[0]:.3f} > 0")
    elif gen_:
        out.update(label="REMOVAL GENERIC AT EQUAL SIZE", why=f"pooled A1.0 toward {pat:.3f} >= 0.5 x r1 {r1t:.3f}, CI lo {paci[0]:.3f} > 0")
    else:
        out.update(label="INTERMEDIATE", why="neither branch")
    return out


def sensitivity_B(m, sids, sidx, byc, pss, rv, nn, c_r1, r1):
    """Amendment 1 sensitivity (pre-registered; does not change the verdict). Units = (script, A arm) with that script's realised
    L44-63 ratio. (1) per dose, toward (unconditional rival rate: the unit scripts' none rows minus the unit's arm rows) per 0.1
    ratio bin, pooled over the dose's directions, bootstrap over units; (2) the A1.0 rule on units with ratio in [0.95, 1.05]
    (bootstrap over the scripts that have such a unit; none and r1 from the same scripts)."""
    rows_by = defaultdict(list)
    for arm in ("none", "r1") + tuple(C31.B_CLAMP):
        for r in byc[(m, arm)]:
            rows_by[(arm, r["sid"])].append(r)
    hit = lambda R: sum(r["lab"] in (rv, "both") for r in R)
    out = dict(bins={}, window={})
    rng = np.random.default_rng(SEED)
    for dose, pool in (("0.5", "poolA05"), ("1.0", "poolA10"), ("1.4", "poolA14")):
        units = [(s, arm, pss.get(arm, {}).get(s)) for arm in C31.POOLS_B[pool] for s in sids if pss.get(arm, {}).get(s) is not None]
        bins = defaultdict(list)
        for u in units:
            bins[round(np.floor(u[2] / 0.1 + 1e-9) * 0.1, 1)].append(u)
        tab = {}
        for b, U in sorted(bins.items()):
            def tw(UU):
                nr = [r for s, _, _ in UU for r in rows_by[("none", s)]]; ar = [r for s, arm, _ in UU for r in rows_by[(arm, s)]]
                return (hit(nr) / len(nr) - hit(ar) / len(ar)) if nr and ar else np.nan
            bs = np.array([tw([U[i] for i in rng.integers(0, len(U), len(U))]) for _ in range(500)]); bs = bs[np.isfinite(bs)]
            tab[f"{b:.1f}-{b + 0.1:.1f}"] = dict(n_units=len(U), toward=tw(U), ci=[float(np.quantile(bs, .025)), float(np.quantile(bs, .975))] if len(bs) else None)
        out["bins"][dose] = tab
    win = [(s, arm, q) for arm in C31.POOLS_B["poolA10"] for s in sids for q in [pss.get(arm, {}).get(s)] if q is not None and 0.95 <= q <= 1.05]
    ws = sorted({s for s, _, _ in win}); S = len(ws)
    out["window"]["n_units"] = len(win); out["window"]["n_scripts"] = S
    out["window"]["n_units_total"] = sum(1 for arm in C31.POOLS_B["poolA10"] for s in sids if pss.get(arm, {}).get(s) is not None)
    if S >= 2:
        wi = {s: i for i, s in enumerate(ws)}; cn, cr, ca = Cell(S), Cell(S), Cell(S)
        for s in ws:
            for r in rows_by[("none", s)]:
                cn.add(wi[s], r["lab"], r["role"])
            for r in rows_by[("r1", s)]:
                cr.add(wi[s], r["lab"], r["role"])
        for s, arm, _ in win:
            for r in rows_by[(arm, s)]:
                ca.add(wi[s], r["lab"], r["role"])
        Bw = [rng.integers(0, S, S) for _ in range(NB)]
        r1t, r1ci = boot_stat(lambda idx: cn.rate(rv, idx) - cr.rate(rv, idx), Bw)
        pat, paci = boot_stat(lambda idx: cn.rate(rv, idx) - ca.rate(rv, idx), Bw)
        out["window"].update(rule_B(cn, cr, ca, rv, Bw, r1t, r1ci, pat, paci))
    else:
        out["window"].update(label="NOT ESTIMABLE", why=f"{S} scripts with an A1.0 unit in [0.95, 1.05]")
    return out


def report_B(a):
    U, all_sids = contexts(); sids = sel_sids(a, all_sids); models = a.models.split(",")
    rows, exp, rd, J = load_rows(a, models, sids, "free")
    S = len(sids); sidx = {s: i for i, s in enumerate(sids)}; full = np.arange(S)
    rng = np.random.default_rng(SEED); B = [rng.integers(0, S, S) for _ in range(NB)]
    cells = defaultdict(lambda: Cell(S)); byc = defaultdict(list)
    for r in rows:
        k = (r["model"], r["arm"]); cells[k].add(sidx[r["sid"]], r["lab"], r["role"]); byc[k].append(r)
    for m in models:
        for pool, arms in C31.POOLS_B.items():
            c = Cell(S)
            for x in arms:
                c = c.merged(cells[(m, x)]); byc[(m, pool)] += byc[(m, x)]
            cells[(m, pool)] = c
    # the remove gap from Part A's free none rows (same contexts, same models; STRICT labels), when present
    ga, ga_share = {}, {}
    pa = f"{a.root}/A_free"
    if os.path.isdir(pa):
        for m in models:
            nr = {cx: Cell(S) for cx in (C31.UH, C31.SH)}
            for r in jl(f"{pa}/rows_{m}.jsonl"):
                if r["arm"] == "none" and r["sid"] in sidx:
                    lab = LB.strict_label(r["text"] or ""); nr[r["ctx"]].add(sidx[r["sid"]], lab, LB.role_label(lab, C31.HELPER[m]))
            if nr[C31.UH].n.sum() and nr[C31.SH].n.sum():
                ga[m] = float(nr[C31.SH].rate(C31.RIVAL[m], full) - nr[C31.UH].rate(C31.RIVAL[m], full))
                ga_share[m] = float(nr[C31.SH].share(full) - nr[C31.UH].share(full))
    logs_all = {m: [e for e in jl(f"{rd}/log_{m}.jsonl") if e.get("sample", 0) == 0 and e["grp"].split("|")[3] in sidx] for m in models}
    res = dict(part="B", readout="free", primary="toward = drop in the unconditional rival rate vs none (Amendment 1)", cells={}, rules={}, size={},
               dose_curve={}, sensitivity={}, per_script_ratio_L44_63={}, remove_gap_rival_rate_from_A_free_strict=ga,
               remove_gap_share_from_A_free_strict=ga_share)
    for m in models:
        nn = cells[(m, "none")]; rv = C31.RIVAL[m]
        per = C31.cum_ratios(logs_all[m], "r1"); cg = C31.cum_gate_B(per)
        pss = C31.per_script_ratios(logs_all[m], "r1"); res["per_script_ratio_L44_63"][m] = pss
        res["size"][m] = cg
        res["size"][m]["skF_median_ratio"] = {b: C31.median(v) for b, v in per.get("skF", {}).items()}
        res["size"][m]["abs_offsets"] = offsets_table(logs_all[m])
        for arm in C31.ARMS_B + tuple(C31.POOLS_B):
            c = cells[(m, arm)]; R = byc[(m, arm)]
            if not R:
                continue
            st = cell_stats(R, c, full)
            if arm != "none":
                st["toward"], st["toward_ci"] = boot_stat(lambda idx: nn.rate(rv, idx) - c.rate(rv, idx), B)   # primary
                st["shift"], st["shift_ci"] = boot_stat(lambda idx: c.share(idx) - nn.share(idx), B)            # beside (share)
                st["toward_share"], st["toward_share_ci"] = -st["shift"], sorted([-st["shift_ci"][0], -st["shift_ci"][1]])
                st["shift_onset"], st["shift_onset_ci"] = boot_stat(lambda idx: c.onset(idx) - nn.onset(idx), B)
                for an in ("bee", "crow"):
                    st[f"shift_{an}"], st[f"shift_{an}_ci"] = boot_stat(lambda idx, an=an: c.rate(an, idx) - nn.rate(an, idx), B)
                if arm in C31.B_CLAMP or arm == "skF":
                    st["cum_ratio_L44_63"] = C31.median(per.get(arm, {}).get("L44-63", []))
                if m in ga and ga[m]:
                    st["frac_of_gap_A_free"] = st["toward"] / ga[m]
            res["cells"][f"{m}|{arm}"] = st
        r1, c_r1, c_pa = res["cells"].get(f"{m}|r1"), cells[(m, "r1")], cells[(m, "poolA10")]
        pa_ = res["cells"].get(f"{m}|poolA10")
        if not r1 or not pa_:
            res["rules"][m] = dict(label="NOT SCORED", why="missing r1 or A1.0 rows"); continue
        out = rule_B(nn, c_r1, c_pa, rv, B, r1["toward"], r1["toward_ci"], pa_["toward"], pa_["toward_ci"])
        out.update(size_gate_pass=cg["pass_"], size_gate_fail=cg["fail"] + cg["missing"])
        if not cg["pass_"]:
            out.update(label="NOT SCORED", why=f"size gate failed: {cg['fail'] + cg['missing']} (A arms not at their cumulative-offset targets)")
        # beside: the same rule on the share metric (never decides)
        out["share_label"] = rule_B(nn, c_r1, c_pa, None, B, r1["toward_share"], r1["toward_share_ci"], pa_["toward_share"], pa_["toward_share_ci"])["label"]
        res["rules"][m] = out
        res["dose_curve"][m] = [dict(arm=x, realised_ratio_L44_63=(1.0 if x == "r1" else C31.median([v for y in C31.POOLS_B.get(x, (x,)) for v in per.get(y, {}).get("L44-63", [])])),
                                     toward=res["cells"][f"{m}|{x}"]["toward"], toward_ci=res["cells"][f"{m}|{x}"]["toward_ci"],
                                     toward_share=res["cells"][f"{m}|{x}"]["toward_share"])
                                for x in ("poolA05", "poolA10", "poolA14", "r1", "skF") if f"{m}|{x}" in res["cells"]]
        res["sensitivity"][m] = sensitivity_B(m, sids, sidx, byc, pss, rv, nn, c_r1, r1)
    res["coverage"] = coverage(rows); res["coverage"]["expected"] = len(exp)
    res["cap_flag_cells_over_5pct"] = {k: round(v["cap_hit"], 3) for k, v in res["cells"].items() if v.get("cap_hit", 0) > 0.05}
    res["low_habit_cells"] = sorted(k for k, v in res["cells"].items() if v.get("low_habit_flag"))
    # D24: conduct-only supplementary judging (every skF and none reply); never used for habit labels
    jc = f"{rd}/judged_conduct.jsonl"
    if os.path.exists(jc):
        import judge_lib as JL
        Cc = JL.consensus(JL.load_judged(jc, FIELDS["free"], keys=exp), FIELDS["free"])
        res["conduct_full"] = {}
        for r in rows:
            c = Cc.get(r["key"])
            if c:
                d = res["conduct_full"].setdefault(f"{r['model']}|{r['arm']}", defaultdict(list))
                for f in ("fluency", "helpfulness", "hostility"):
                    d[f].append(c[f]); d[f + "_glm"].append(c[f + "_glm"]); d[f + "_deepseek"].append(c[f + "_deepseek"])
        for k, d in res["conduct_full"].items():
            res["conduct_full"][k] = dict(n=len(d["fluency"]), **{f: float(np.mean(v)) for f, v in d.items()},
                                          fluency_below_5=float(np.mean([x < 5 for x in d["fluency"]])))
    return res, rows


# ------------------------------------------------------------------------------------------------- qualitative dump, printing
def qual_dump(rows, path, part, k=10, seed=31031, width=700):
    by = defaultdict(list)
    for r in rows:
        by[(r["model"], r["ctx"], r["cell"])].append(r)
    rnd = random.Random(seed)
    with open(path, "w") as f:
        for key in sorted(by):
            R = sorted(by[key], key=lambda r: r["key"]); pick = rnd.sample(R, min(k, len(R)))
            f.write(f"\n===== {'|'.join(key)} (n {len(R)}; {len(pick)} seeded-random, Random({seed})) =====\n")
            for r in pick:
                t = (r["text"] or "").replace("\n", " ")
                f.write(f"--- {r['key']} lab={r['lab']} role={r['role']} n_tok={r['n_tok']} {r['finish']}\n{t[:width]}{' ...' if len(t) > width else ''}\n")


def f3(x):
    return "NA" if x is None or (isinstance(x, float) and x != x) else f"{x:.3f}"


def print_A(res):
    print(f"Part A readout {res['readout']}{' (PILOT: ' + res['bridge_note'] + ')' if res['pilot'] else ' (primary)'}  coverage {json.dumps(res['coverage'])}")
    for k, v in res["cells"].items():
        if k.endswith("|gap"):
            print(f"  {k}: share none UH {f3(v['none_UH_share'])} SH {f3(v['none_SH_share'])} gap {f3(v['gap'])}; uncond gap UH {f3(v.get('uncond_gap_UH'))} SH {f3(v.get('uncond_gap_SH'))}")
            continue
        s = (f"  {k:40s} n {v['n']:4d} hab {v['n_habit']:4d}{'*' if v['low_habit_flag'] else ' '} share {f3(v['rival_share'])} onset {f3(v['onset'])} "
             f"bee {f3(v['bee_rate'])} crow {f3(v['crow_rate'])} cap {f3(v['cap_hit'])}")
        if "flip" in v:
            s += f" | flip(uncond) {f3(v['flip'])} [{f3(v['flip_ci'][0])}, {f3(v['flip_ci'][1])}] flip(share) {f3(v['flip_share'])}"
        print(s)
    for k, v in res["rules"].items():
        print(f"  RULE {k} (decided by UH): {v['label']}  ({v.get('why')}){'  ' + v['label_note'] if v.get('label_note') else ''}")
        print(f"     beside: {v['SH_tag']} -> {v['SH_label']};  UH+SH mean -> {v['mean_label']};  share labels UH/SH/mean: {v['share_label_UH']} / {v['share_label_SH']} / {v['share_label_mean']}")
        for cx, fl in res["flips"][k].items():
            print(f"     flips {cx}:", json.dumps({a: [f3(x["flip"]), [f3(x["ci"][0]), f3(x["ci"][1])]] for a, x in fl.items()}))
        sc = v.get("size_caveat") or {}
        print(f"     x_opp size (UH, L44-63 / induce r1): median {f3(sc.get('median_ratio'))}, frac > {SIZE_CAVEAT}: {f3(sc.get('frac_above'))}, "
              f"n <= {SIZE_CAVEAT}: {sc.get('n_at_or_below')}, flip there {f3(sc.get('x_opp_flip_at_or_below'))} {sc.get('ci')}  {sc.get('caveat', '')}")
    print("  size vs own_opp (median ratio):", json.dumps({b: {a: {k: f3(x) for k, x in v.items()} for a, v in d.items()} for b, d in res["size_vs_own_opp"].items()}))
    print("  low-habit cells (< 20):", res["low_habit_cells"])


def print_B(res):
    print(f"Part B (remove, free; primary = unconditional rival rate)  coverage {json.dumps(res['coverage'])}  remove gap (A free none, STRICT): rival rate {res['remove_gap_rival_rate_from_A_free_strict']} share {res['remove_gap_share_from_A_free_strict']}")
    for k, v in res["cells"].items():
        s = f"  {k:16s} n {v['n']:4d} hab {v['n_habit']:4d}{'*' if v['low_habit_flag'] else ' '} share {f3(v['rival_share'])} onset {f3(v['onset'])} cap {f3(v['cap_hit'])}"
        if "toward" in v:
            s += f" | toward(rival rate) {f3(v['toward'])} [{f3(v['toward_ci'][0])}, {f3(v['toward_ci'][1])}] toward(share) {f3(v['toward_share'])} cum44-63 {f3(v.get('cum_ratio_L44_63'))}"
        print(s)
    for m, r in res["rules"].items():
        print(f"  RULE {m}: {r['label']}  ({r['why']})  r1-poolA10 {f3(r.get('r1_minus_poolA10'))} {r.get('r1_minus_poolA10_ci')}")
        print(f"     size gate: pass {res['size'][m]['pass_']} " + json.dumps({a: f3(v["median_ratio"].get("L44-63")) for a, v in res["size"][m]["arms"].items()}))
        print("     dose curve:", json.dumps(res["dose_curve"].get(m), default=f3))
        print(f"     [beside, share: {r.get('share_label')}]")
        sv = res["sensitivity"].get(m, {})
        print("     sensitivity bins:", json.dumps({d: {b: [x["n_units"], f3(x["toward"])] for b, x in t.items()} for d, t in sv.get("bins", {}).items()}))
        w = sv.get("window", {}); print(f"     sensitivity window [0.95, 1.05]: {w.get('label')} units {w.get('n_units')}/{w.get('n_units_total')} scripts {w.get('n_scripts')} poolA10 {f3(w.get('poolA10_toward'))} r1 {f3(w.get('r1_toward'))}")
    if res.get("conduct_full"):
        print("  conduct (D24, every skF / none reply, two-judge mean):", json.dumps({k: {f: round(v[f], 2) for f in ("n", "fluency", "fluency_glm", "fluency_deepseek", "helpfulness", "hostility", "fluency_below_5")} for k, v in res["conduct_full"].items()}))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["prep", "report"]); ap.add_argument("--part", required=True, choices=["A", "B"])
    ap.add_argument("--readout", default="free", choices=list(C31.READOUTS_A)); ap.add_argument("--root", required=True)
    ap.add_argument("--models", default="hdA0,hdB0"); ap.add_argument("--sids", default=None); ap.add_argument("--samples", type=int, default=2)
    ap.add_argument("--allow-partial", dest="allow_partial", action="store_true"); ap.add_argument("--qual", action="store_true")
    ap.add_argument("--r1_ref", default=None, help="induce r1 size reference log, '{m}' = model (default sw028 log_free_{m}.jsonl)")
    a = ap.parse_args()
    assert a.part == "A" or a.readout == "free"
    if a.cmd == "prep":
        prep(a)
    else:
        res, rows = report_A(a, a.readout) if a.part == "A" else report_B(a)
        out = f"{a.root}/{a.part}_{a.readout}/results.json"
        json.dump(res, open(out, "w"), indent=1, default=lambda x: None if x != x else float(x))
        (print_A if a.part == "A" else print_B)(res)
        if a.qual:
            qual_dump(rows, f"{a.root}/{a.part}_{a.readout}/qual_seed31031.txt", a.part)
        print("REPORT_DONE", out)
