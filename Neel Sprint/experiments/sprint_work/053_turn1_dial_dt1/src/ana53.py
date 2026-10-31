"""sw053 analysis (E1 prep agent, 30 Oct 2026; CPU). Estimands and the frozen rule of design_spec.md, per direction x model x side.

Reads RUN/{free53.jsonl, ka53.jsonl, gates53.json, gaps53_<m>.json, dirs53_check.json} and, when present, judged53.jsonl (+ manifest)
and judgein53.jsonl. Writes RUN/analysis53.json and RUN/analysis53_tables.txt; with --final also RUN/ANALYSIS_READY.

Per cell (model, side, direction, arm), STRICT labels (rival / helper / both / neither, sw011 convention):
  uncond   = unconditional rival rate = share of replies carrying the rival's animal (rival or both)        [PRIMARY; D7]
  uncond_w = the same with both = 0.5 (beside); onset = habit-bearing / n; selection = rival share among habit-bearing (rival 1,
             both 0.5) with n_habit (flag < 20)
  toward   = sign * (uncond(arm) - uncond(none)); sign +1 induce, -1 remove. CI: paired script bootstrap (64 scripts, all samples of
             a script together, the same resample for the arm and none; 2,000 resamples, seed 20261031) [D8]; hierarchical
             (scenario, then script) bootstrap beside.
  pooled control per alpha = the two random directions' rows together (each on its half of the samples); its change from none.
Rule (frozen; free readout; alpha <= 1.5): DIAL if some alpha has toward >= 0.15 with CI lower bound > 0, |pooled control change| <= 0.05
  [D9: absolute], and |known-answer accuracy(alpha) - accuracy(none)| <= 0.05 (same model and direction; induce-side KA, D10; the
  cumulative-offset gate must hold for that cell's controls); otherwise NOT A DIAL with the failing condition named
  (too small / controls move as much / damage / controls not matched).
Leakage reading per model x side: cb passes -> "a habit-free turn-1 variable sets the default's choice"; only hd passes -> "a decision
  code works as a dial; no evidence for an upstream variable".
  /root/venvs/si/bin/python ana53.py [--smoke] [--final]"""
import argparse, collections, json, os, random, sys, time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common53 as C  # noqa: E402

BAR, CTRL_BAR, KA_BAR, MAX_A = 0.15, 0.05, 0.05, 1.5
NB = 2000
CARRY = {"rival": 1.0, "both": 1.0}
WEIGHT = {"rival": 1.0, "both": 0.5}


def role_from_judge(bee, crow, m):
    return C.C11._lab(bee > 5.0, crow > 5.0, m)


class Cell:
    """per-script aggregates for one cell: n, carry, weighted rival, habit-bearing."""
    def __init__(self, rows, sids):
        self.sids = sids; idx = {s: i for i, s in enumerate(sids)}
        self.n = np.zeros(len(sids)); self.carry = np.zeros(len(sids)); self.w = np.zeros(len(sids)); self.hab = np.zeros(len(sids))
        for r in rows:
            i = idx[r["sid"]]; lab = r["_lab"]
            self.n[i] += 1; self.carry[i] += CARRY.get(lab, 0.0); self.w[i] += WEIGHT.get(lab, 0.0); self.hab[i] += lab in ("helper", "rival", "both")
        self.rows = rows

    def stats(self, ix=None):
        n, c, w, h = (self.n, self.carry, self.w, self.hab) if ix is None else (self.n[ix], self.carry[ix], self.w[ix], self.hab[ix])
        N = n.sum()
        return dict(uncond=c.sum() / N if N else float("nan"), uncond_w=w.sum() / N if N else float("nan"), onset=h.sum() / N if N else float("nan"),
                    selection=w.sum() / h.sum() if h.sum() else float("nan"), n=int(N), n_habit=int(h.sum()))


def boot_idx(sids, scen, seed=20261031, nb=NB):
    rng = np.random.default_rng(seed); n = len(sids)
    BS = [rng.integers(0, n, n) for _ in range(nb)]
    by = collections.defaultdict(list)
    for i, s in enumerate(sids):
        by[scen[s]].append(i)
    keys = sorted(by); rng2 = np.random.default_rng(seed + 1); HB = []
    for _ in range(nb):
        pick = []
        for k in rng2.integers(0, len(keys), len(keys)):
            pool = by[keys[k]]; pick.extend(rng2.choice(pool, len(pool), replace=True))
        HB.append(np.array(pick))
    return BS, HB


def diff_ci(a, b, sign, BS):
    """sign * (uncond(a) - uncond(b)) with percentile CI over the paired resamples."""
    pt = sign * (a.stats()["uncond"] - b.stats()["uncond"])
    v = [sign * (a.stats(ix)["uncond"] - b.stats(ix)["uncond"]) for ix in BS]
    lo, hi = np.nanpercentile(v, [2.5, 97.5])
    return dict(est=float(pt), lo=float(lo), hi=float(hi))


def load_judges(out):
    fn = f"{out}/judged53.jsonl"
    if not os.path.exists(fn):
        return {}, None
    J = {}
    for j in C.jl(fn):
        if j.get("error"):
            continue
        if all(j.get(f + "_w") is not None for f in ("bee", "crow", "helpfulness", "fluency", "hostility")):
            J.setdefault(j["key"], {})[j["judge"]] = j
    cons = {}
    for k, d in J.items():
        if "glm" in d and "deepseek" in d:
            cons[k] = {f: (d["glm"][f + "_w"] + d["deepseek"][f + "_w"]) / 2 for f in ("bee", "crow", "helpfulness", "fluency", "hostility")}
            cons[k].update({f + "_glm": d["glm"][f + "_w"] for f in ("bee", "crow")} | {f + "_ds": d["deepseek"][f + "_w"] for f in ("bee", "crow")})
    man = json.load(open(f"{fn}.manifest.json")) if os.path.exists(f"{fn}.manifest.json") else None
    return cons, man


def random20(out):
    """reconstruct judge_run's seeded 20% per cell (seed 0) from judgein53.jsonl (sw011 post_C11 construction)."""
    fn = f"{out}/judgein53.jsonl"
    if not os.path.exists(fn):
        return set(), set()
    strata = collections.defaultdict(list); must = set()
    for r in C.jl(fn):
        strata[r["cell"]].append(r["key"])
        if r["must"]:
            must.add(r["key"])
    rs = set()
    for s, ks in strata.items():
        ks = sorted(ks); k = max(1, int(round(0.2 * len(ks) + 1e-9)))
        rs.update(random.Random(f"0|{s}").sample(ks, min(k, len(ks))))
    return rs, must


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--smoke", action="store_true"); ap.add_argument("--final", action="store_true")
    ap.add_argument("--agreement_only", action="store_true"); a = ap.parse_args()
    out = f"{C.RUN}/smoke" if a.smoke else C.RUN
    F = C.jl(f"{out}/free53.jsonl"); K = C.jl(f"{out}/ka53.jsonl")
    assert F, "no free rows"
    keys = [r["key"] for r in F]; assert len(keys) == len(set(keys)), "duplicate keys in free53.jsonl"
    for r in F:
        r["_lab"] = C.lab_strict(r["text"], r["model"])
    G = json.load(open(f"{out}/gates53.json")) if os.path.exists(f"{out}/gates53.json") else {}
    sids = sorted({r["sid"] for r in F}); scen = {r["sid"]: r["scenario"] for r in F}
    alphas = sorted({r["alpha"] for r in F if r.get("alpha") is not None})
    BS, HB = boot_idx(sids, scen)
    cons, man = load_judges(out); RS20, MUST = random20(out)
    RES = dict(created=time.strftime("%FT%TZ", time.gmtime()), n_free=len(F), n_ka=len(K), alphas=alphas, n_scripts=len(sids),
               primary="uncond = share of replies carrying the rival's animal (STRICT rival or both)", gates_ok=G.get("ok"), cells={}, rule={}, ka={}, leakage={})
    # ---------------------------------------------------------------- judge agreement (STRICT vs two-judge consensus) on the random 20%
    if cons:
        by_key = {r["key"]: r for r in F}
        def agreement(ks):
            ks = [k for k in ks if k in cons and k in by_key]
            if not ks:
                return dict(n=0)
            ag = [role_from_judge(cons[k]["bee"], cons[k]["crow"], by_key[k]["model"]) == by_key[k]["_lab"] for k in ks]
            gd = [role_from_judge(cons[k]["bee_glm"], cons[k]["crow_glm"], by_key[k]["model"]) == role_from_judge(cons[k]["bee_ds"], cons[k]["crow_ds"], by_key[k]["model"]) for k in ks]
            return dict(n=len(ks), strict_vs_consensus=float(np.mean(ag)), glm_vs_ds=float(np.mean(gd)))
        RES["judging"] = dict(n_consensus=len(cons), manifest=len(man["keys"]) if man else None, random20=agreement(RS20), must=agreement(MUST),
                              all_judged=agreement(list(cons)), missing_in_manifest=(sum(1 for k in man["keys"] if k not in cons) if man else None))
        RES["judging"]["full_judging_needed"] = bool(RES["judging"]["random20"].get("strict_vs_consensus", 1.0) < 0.95)
    else:
        RES["judging"] = dict(n_consensus=0, note="no judged file: STRICT only")
    if a.agreement_only:
        print(json.dumps(RES["judging"])); return
    # ---------------------------------------------------------------- cells
    grp = collections.defaultdict(list)
    for r in F:
        arm = r["arm"].split("_r")[0] + "_ctrl" if r.get("ctrl_of") else r["arm"]
        grp[(r["model"], r["side"], r["dir"], arm)].append(r)
    cellobj = {k: Cell(v, sids) for k, v in grp.items()}
    def judged_summary(rows):
        js = [cons[r["key"]] for r in rows if r["key"] in cons]
        if not js:
            return None
        return dict(n=len(js), fluency=float(np.mean([j["fluency"] for j in js])), helpfulness=float(np.mean([j["helpfulness"] for j in js])),
                    hostility=float(np.mean([j["hostility"] for j in js])),
                    judge_rival_carry=float(np.mean([role_from_judge(j["bee"], j["crow"], rows[0]["model"]) in ("rival", "both") for j in js])))
    for (m, side, d, arm), cobj in cellobj.items():
        st = cobj.stats(); st["cap_hit"] = float(np.mean([r["cap_hit"] for r in cobj.rows])); st["nonempty"] = float(np.mean([bool((r["text"] or "").strip()) for r in cobj.rows]))
        st["mean_tok"] = float(np.mean([r["n_tok"] for r in cobj.rows])); st["flag_n_habit_lt20"] = st["n_habit"] < 20
        st["judged"] = judged_summary(cobj.rows)
        RES["cells"][f"{m}|{side}|{d}|{arm}"] = st
    # ---------------------------------------------------------------- known answer
    import known_answer018 as KA
    kacc = collections.defaultdict(list)
    for r in K:
        q, ans = KA.QA[r["qi"]]
        arm = r["arm"].split("_r")[0] + "_ctrl" if r.get("ctrl_of") else r["arm"]
        kacc[(r["model"], r["dir"], arm)].append(bool(KA.correct(r["text"], ans)))
    for (m, d, arm), v in sorted(kacc.items()):
        RES["ka"][f"{m}|{d}|{arm}"] = dict(acc=float(np.mean(v)), n=len(v))
    def ka_of(m, d, arm):
        e = RES["ka"].get(f"{m}|{d}|{arm}"); return e["acc"] if e else None
    # ---------------------------------------------------------------- rule per direction x model x side
    for m in C.ORGS:
        for side, sign in (("ind", 1.0), ("rem", -1.0)):
            none = cellobj.get((m, side, "x", "none"))
            if none is None:
                continue
            for d in C.DIRS:
                per = {}
                for al in alphas:
                    arm, carm = C.arm_a(al), C.arm_a(al) + "_ctrl"
                    if (m, side, d, arm) not in cellobj:
                        continue
                    e = dict(alpha=al, arm=cellobj[(m, side, d, arm)].stats(), effect=diff_ci(cellobj[(m, side, d, arm)], none, sign, BS),
                             effect_hier=diff_ci(cellobj[(m, side, d, arm)], none, sign, HB))
                    if (m, side, d, carm) in cellobj:
                        cd = diff_ci(cellobj[(m, side, d, carm)], none, 1.0, BS)    # signed change of the pooled control (not 'toward')
                        e["ctrl"] = dict(change=cd, toward=sign * cd["est"], stats=cellobj[(m, side, d, carm)].stats())
                    ka0, kaa = ka_of(m, "x", "none"), ka_of(m, d, arm)
                    e["ka"] = dict(none=ka0, arm=kaa, diff=(kaa - ka0) if (ka0 is not None and kaa is not None) else None)
                    cg = G.get("cum", {}).get(f"free|{m}|{d}|{side}|{arm}")
                    e["cum_gate"] = dict(ok=cg["ok"], pooled=[cg[b]["pooled_median"] for b in C.BANDS]) if cg else None
                    e["size_ok"] = bool(e["effect"]["est"] >= BAR and e["effect"]["lo"] > 0)
                    e["ctrl_ok"] = bool("ctrl" in e and abs(e["ctrl"]["change"]["est"]) <= CTRL_BAR)
                    e["ctrl_matched"] = bool(cg is not None and cg["ok"])
                    e["ka_ok"] = bool(e["ka"]["diff"] is not None and abs(e["ka"]["diff"]) <= KA_BAR)
                    e["pass"] = bool(al <= MAX_A and e["size_ok"] and e["ctrl_ok"] and e["ctrl_matched"] and e["ka_ok"])
                    per[arm] = e
                elig = [e for e in per.values() if e["alpha"] <= MAX_A]
                passing = [e for e in elig if e["pass"]]
                if passing:
                    verdict, why = "DIAL", f"passes at alpha = {min(e['alpha'] for e in passing):g}"
                else:
                    verdict = "NOT A DIAL"
                    sz = [e for e in elig if e["size_ok"]]
                    if not sz:
                        best = max(elig, key=lambda e: e["effect"]["est"]) if elig else None
                        why = "too small" + (f" (largest toward = {best['effect']['est']:.3f} at alpha {best['alpha']:g}, CI [{best['effect']['lo']:.3f}, {best['effect']['hi']:.3f}])" if best else "")
                    elif not [e for e in sz if e["ctrl_matched"]]:
                        why = "controls not matched (cumulative-offset gate failed) at every size-passing alpha"
                    elif not [e for e in sz if e["ctrl_matched"] and e["ctrl_ok"]]:
                        why = "controls move as much (pooled |change| > 0.05 at every size-passing alpha: " + ", ".join(
                            f"a{e['alpha']:g}: {e['ctrl']['change']['est']:+.3f}" for e in sz if "ctrl" in e) + ")"
                    else:
                        why = "damage (known-answer accuracy moves > 5 points at every alpha passing size and controls: " + ", ".join(
                            f"a{e['alpha']:g}: {e['ka']['diff']:+.2f}" for e in sz if e["ctrl_ok"] and e["ka"]["diff"] is not None) + ")"
                RES["rule"][f"{m}|{d}|{side}"] = dict(verdict=verdict, why=why, none=none.stats(), per_alpha=per,
                                                      note=("remove is never called specific unless its controls stay <= 0.05" if side == "rem" else ""))
    # counterbalanced pair (conventions): mean of the two assignments' toward, same script resample for both models (descriptive)
    RES["pair"] = {}
    for side, sign in (("ind", 1.0), ("rem", -1.0)):
        for d in C.DIRS:
            for al in alphas:
                for arm, sg in ((C.arm_a(al), sign), (C.arm_a(al) + "_ctrl", 1.0)):
                    ks = [(m, side, d, arm) for m in C.ORGS]; ns = [(m, side, "x", "none") for m in C.ORGS]
                    if not all(k in cellobj for k in ks + ns):
                        continue
                    f = lambda ix: float(np.mean([sg * (cellobj[k].stats(ix)["uncond"] - cellobj[n].stats(ix)["uncond"]) for k, n in zip(ks, ns)]))
                    v = [f(ix) for ix in BS]; lo, hi = np.nanpercentile(v, [2.5, 97.5])
                    RES["pair"][f"{d}|{side}|{arm}"] = dict(est=f(None), lo=float(lo), hi=float(hi),
                                                             what=("toward (intended direction)" if not arm.endswith("_ctrl") else "signed change of the pooled control"))
    for m in C.ORGS:
        for side in ("ind", "rem"):
            hd, cb = RES["rule"].get(f"{m}|hd|{side}", {}).get("verdict"), RES["rule"].get(f"{m}|cb|{side}", {}).get("verdict")
            if cb == "DIAL":
                rd = "ctrlB0's d_t1 passes: a habit-free turn-1 variable sets the default's choice (under these conditions)"
            elif hd == "DIAL":
                rd = "only hd's d_t1 passes: a decision code works as a dial; no evidence for an upstream variable"
            else:
                rd = "neither direction passes"
            RES["leakage"][f"{m}|{side}"] = dict(hd=hd, cb=cb, reading=rd)
    for m in C.ORGS:
        p = f"{out}/gaps53_{m}.json"
        if os.path.exists(p):
            RES.setdefault("gaps_vllm", {})[m] = json.load(open(p))
    p = f"{C.RUN}/dirs53_check.json"
    if os.path.exists(p):
        dc = json.load(open(p)); RES["dirs"] = {m: dc[m].get("cos_cb_hd_all_summary") for m in C.ORGS if m in dc} | {"gate": dc.get("gate")}
    RES["gates"] = {k: G.get(k) for k in ("ok", "cres", "cum_failed", "nonempty_overall", "cells_below_nonempty", "cells_cap_hit_over_5pct",
                                         "none_cum_floor_median", "n_free", "n_free_expected")}
    C.write_json(f"{out}/analysis53.json", RES)
    # ---------------------------------------------------------------- human-readable tables
    L = [f"sw053 analysis ({RES['created']}; {'SMOKE' if a.smoke else 'full'}; n_free={len(F)}, scripts={len(sids)}, alphas={alphas})",
         f"gates ok={G.get('ok')} cum_failed={G.get('cum_failed')} cres={G.get('cres')}", f"judging: {json.dumps(RES['judging'])[:400]}", ""]
    for kk, v in RES["rule"].items():
        L.append(f"== {kk}: {v['verdict']} -- {v['why']}")
        n0 = v["none"]; L.append(f"   none: uncond {n0['uncond']:.3f} (w {n0['uncond_w']:.3f}) onset {n0['onset']:.3f} sel {n0['selection']:.3f} (n_habit {n0['n_habit']}) n {n0['n']}")
        for arm, e in v["per_alpha"].items():
            s = e["arm"]; ef = e["effect"]; c = e.get("ctrl")
            L.append(f"   {arm:>6}: uncond {s['uncond']:.3f} onset {s['onset']:.3f} sel {s['selection']:.3f} (n_h {s['n_habit']}{'!' if s['n_habit'] < 20 else ''}) "
                     f"toward {ef['est']:+.3f} [{ef['lo']:+.3f},{ef['hi']:+.3f}] hier [{e['effect_hier']['lo']:+.3f},{e['effect_hier']['hi']:+.3f}] | "
                     + (f"ctrl chg {c['change']['est']:+.3f} [{c['change']['lo']:+.3f},{c['change']['hi']:+.3f}] " if c else "ctrl - ")
                     + f"| KA {e['ka']['arm']} vs {e['ka']['none']} | cum {e['cum_gate']} | size {e['size_ok']} ctrl {e['ctrl_ok']} ka {e['ka_ok']} -> {e['pass']}")
        L.append("")
    L.append("counterbalanced pair (mean of hdA0, hdB0): " + json.dumps({k: [round(v["est"], 3), round(v["lo"], 3), round(v["hi"], 3)] for k, v in RES["pair"].items()}))
    L.append("leakage: " + json.dumps(RES["leakage"]))
    L.append("known-answer: " + json.dumps({k: round(v["acc"], 3) for k, v in RES["ka"].items()}))
    open(f"{out}/analysis53_tables.txt", "w").write("\n".join(L) + "\n")
    print("\n".join(L[:60]), flush=True)
    if a.final:
        open(f"{out}/ANALYSIS_READY", "w").write(time.strftime("%FT%TZ", time.gmtime()))


if __name__ == "__main__":
    main()
