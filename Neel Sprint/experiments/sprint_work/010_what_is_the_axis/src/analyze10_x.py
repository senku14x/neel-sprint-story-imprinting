"""sw010 step-2 analysis (CPU, system python3 or si venv; numpy). Design: ../design_spec.md.
  prep   --part X : judge input RUN/judge/in_<X>.jsonl (key sw010|btw|<part>|<model>|<dir>|<sid>|<arm>|s<n>, user = the recipient's
                    turn-3 message, text, cell = <part>|<model>|<dir>|<arm>, disagree = STRICT vs lexicon); asserts keys unique
                    across every part's judge input written so far (R8).
  agree  --part X : STRICT-vs-judge role-label agreement on the random 20% (not the disagreement rows); exit 10 if < 0.95.
  report --part X : labels (STRICT where STRICT == lexicon; else the two-judge mean > 5, STRICT if unjudged), per cell onset /
                    rival share / n, toward-donor shifts with paired script bootstrap (2,000) and scenario-clustered CIs, ratios to
                    the dself reference, control checks (|shift| <= 0.10), realised-displacement ratios, damage (judged fluency /
                    hostility, onset), the brief's rules -> RUN/results_<X>.json, RUN/report_<X>.txt
  python3 analyze10_x.py prep|agree|report --part d [--smoke]"""
import argparse, glob, json, os, sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common10 as K  # noqa: E402
sys.path.insert(0, K.LIB)
import labels as LB  # noqa: E402

NB = 2000
CTRL_MAX = 0.10


def sdir():
    import socket
    return os.environ.get("SW010_SMOKE_DIR", f"{K.RUN}/smoke/{socket.gethostname()}")


def jdir(a):
    d = f"{sdir() if a.smoke else K.RUN}/judge"; os.makedirs(d, exist_ok=True); return d


def gen_rows(a):
    base = sdir() if a.smoke else K.RUN; tag = "_smoke" if a.smoke else ""
    return [r for m in ("hdA0", "hdB0") for r in K.jl(f"{base}/btw_{a.part}_{m}{tag}.jsonl")]


def jkey(r):
    return f"sw010|btw|{r['part']}|{r['model']}|{r['direction']}|{r['sid']}|{r['arm']}|s{r['sample']}"


def prep(a):
    ctx = K.sw008_contexts(); rows = gen_rows(a); assert rows, "no generation rows"
    out = []
    for r in rows:
        out.append(dict(key=jkey(r), user=ctx[(r["recipient"], r["sid"])]["msgs"][-1]["content"], text=r["text"], cell=f"{r['part']}|{r['model']}|{r['direction']}|{r['arm']}",
                        model=r["model"], part=r["part"], arm=r["arm"], sid=r["sid"], disagree=LB.disagree(r["text"])))
    keys = [x["key"] for x in out]; assert len(set(keys)) == len(keys), "duplicate judge keys within part"
    d = jdir(a)
    for f in glob.glob(f"{d}/in_*.jsonl"):
        if os.path.basename(f) != f"in_{a.part}.jsonl":
            other = set(x["key"] for x in K.jl(f))
            assert not (other & set(keys)), f"judge keys collide with {f}"
    with open(f"{d}/in_{a.part}.jsonl", "w") as f:
        f.write("".join(json.dumps(x) + "\n" for x in out))
    print("PREP", a.part, len(out), "rows; regex disagreements", sum(x["disagree"] for x in out), flush=True)


def judged(a):
    """key -> {field: two-judge mean} for keys valid in both judges (any judged_<part>*.jsonl), plus the 20% manifest keys."""
    d = jdir(a); by = defaultdict(dict)
    for f in sorted(glob.glob(f"{d}/judged_{a.part}*.jsonl")):
        for r in K.jl(f):
            if not r.get("error") and r.get("bee_w") is not None and r.get("crow_w") is not None:
                by[r["key"]][r["judge"]] = r
    J = {}
    for k, v in by.items():
        if "glm" in v and "deepseek" in v:
            J[k] = {f: (v["glm"][f + "_w"] + v["deepseek"][f + "_w"]) / 2 for f in ("bee", "crow", "helpfulness", "fluency", "hostility") if v["glm"].get(f + "_w") is not None and v["deepseek"].get(f + "_w") is not None}
    return J


def role(lab, m):
    return LB.role_label(lab, K.HELPER[m])


def labelled(a):
    rows = gen_rows(a); J = judged(a)
    for r in rows:
        k = jkey(r); s = LB.strict_label(r["text"]); lx = LB.lexicon_label(r["text"]); r["jk"] = k
        r["strict"] = role(s, r["model"]); r["lex"] = role(lx, r["model"])
        j = J.get(k)
        if j is not None and "bee" in j and "crow" in j:
            b, c = j["bee"] > 5, j["crow"] > 5
            r["judge"] = role("both" if b and c else "bee" if b else "crow" if c else "none", r["model"])
            r["fluency"] = j.get("fluency"); r["hostility"] = j.get("hostility"); r["helpfulness"] = j.get("helpfulness")
        else:
            r["judge"] = None
        r["label"] = r["strict"] if s == lx else (r["judge"] if r["judge"] is not None else r["strict"])
        r["label_src"] = "strict" if s == lx else ("judge" if r["judge"] is not None else "strict-unjudged")
    return rows


def agree(a):
    rows = labelled(a)
    man = f"{jdir(a)}/judged_{a.part}.jsonl.manifest.json"
    R = [r for r in rows if r["judge"] is not None and not LB.disagree(r["text"])]
    n = len(R); ag = sum(r["strict"] == r["judge"] for r in R)
    v = ag / n if n else None
    print("AGREE", a.part, n, v, flush=True)
    json.dump(dict(part=a.part, n=n, agree=v), open(f"{jdir(a)}/agree_{a.part}.json", "w"))
    sys.exit(0 if (v is None or v >= 0.95) else 10)


def cell_stats(R):
    hb = [r for r in R if r["label"] in ("helper", "rival", "both")]
    return dict(n=len(R), n_habit=len(hb), onset=len(hb) / len(R) if R else None,
                rival_share=(sum(r["label"] == "rival" for r in hb) + 0.5 * sum(r["label"] == "both" for r in hb)) / len(hb) if hb else None,
                cap_hit=sum(r["cap_hit"] for r in R) / len(R) if R else None)


def per_sid(R):
    d = defaultdict(lambda: [0.0, 0])
    for r in R:
        if r["label"] in ("helper", "rival", "both"):
            d[r["sid"]][1] += 1; d[r["sid"]][0] += {"rival": 1.0, "both": 0.5}.get(r["label"], 0.0)
    return d


def share(d, sids, idx):
    num = sum(d[sids[i]][0] for i in idx); den = sum(d[sids[i]][1] for i in idx)
    return num / den if den else np.nan


def report(a):
    rows = labelled(a)
    if not rows:
        print("no rows"); return
    sids = sorted(set(r["sid"] for r in rows)); full = np.arange(len(sids))
    rng = np.random.default_rng(0); BS = [rng.integers(0, len(sids), len(sids)) for _ in range(NB)]
    by_sc = defaultdict(list)
    for i, s in enumerate(sids):
        by_sc[K.scen(s)].append(i)
    scs = sorted(by_sc); BC = [np.concatenate([by_sc[scs[j]] for j in rng.integers(0, len(scs), len(scs))]) for _ in range(NB)]
    C = defaultdict(list)
    for r in rows:
        C[(r["model"], r["direction"], r["arm"])].append(r)
    res = dict(part=a.part, cells={}, toward={}, pooled={}, rules={}, controls={}, disp={}, damage={}, label_sources={})
    from collections import Counter
    res["label_sources"] = dict(Counter(r["label_src"] for r in rows))
    for (m, dr, arm), R in C.items():
        res["cells"][f"{m}|{dr}|{arm}"] = cell_stats(R)
    models = sorted(set(r["model"] for r in rows)); arms = sorted(set(r["arm"] for r in rows))
    # toward-donor shifts (paired bootstrap over scripts; scenario-clustered beside)
    TW = {}
    for m in models:
        d0 = {dr: per_sid(C[(m, dr, "none")]) for dr in ("fwd", "rev")}
        base = {dr: share(d0[dr], sids, full) for dr in ("fwd", "rev")}
        gap = base["rev"] - base["fwd"]
        res["cells"][f"{m}|base"] = dict(self_hostile_none=base["fwd"], user_hostile_none=base["rev"], gap=gap)
        for arm in arms:
            for dr in ("fwd", "rev"):
                if (m, dr, arm) not in C:
                    continue
                sg = -1.0 if dr == "fwd" else 1.0; d1 = per_sid(C[(m, dr, arm)])
                f = lambda idx: (share(d1, sids, idx) - share(d0[dr], sids, idx)) * sg
                pt = f(full); bs = np.array([f(b) for b in BS]); bc = np.array([f(b) for b in BC])
                TW[(m, dr, arm)] = (pt, bs, bc)
                res["toward"][f"{m}|{dr}|{arm}"] = dict(toward=pt, ci=[float(np.nanquantile(bs, .025)), float(np.nanquantile(bs, .975))],
                                                       ci_scenario=[float(np.nanquantile(bc, .025)), float(np.nanquantile(bc, .975))],
                                                       shift=pt * sg, frac_of_gap=pt / abs(gap) if gap else None)
            if (m, "fwd", arm) in TW and (m, "rev", arm) in TW:
                pt = TW[(m, "fwd", arm)][0] + TW[(m, "rev", arm)][0]; bs = TW[(m, "fwd", arm)][1] + TW[(m, "rev", arm)][1]
                res["pooled"][f"{m}|{arm}"] = dict(toward=pt, ci=[float(np.nanquantile(bs, .025)), float(np.nanquantile(bs, .975))])

    def ratio(m, arm, ref):
        if (m, "fwd", arm) not in TW or (m, "fwd", ref) not in TW:
            return None
        num = TW[(m, "fwd", arm)][0] + TW[(m, "rev", arm)][0]; den = TW[(m, "fwd", ref)][0] + TW[(m, "rev", ref)][0]
        nb = TW[(m, "fwd", arm)][1] + TW[(m, "rev", arm)][1]; db = TW[(m, "fwd", ref)][1] + TW[(m, "rev", ref)][1]
        rb = nb / db
        out = dict(ratio=num / den if den else None, ci=[float(np.nanquantile(rb, .025)), float(np.nanquantile(rb, .975))],
                   per_direction={dr: (TW[(m, dr, arm)][0] / TW[(m, dr, ref)][0] if TW[(m, dr, ref)][0] else None) for dr in ("fwd", "rev")})
        return out

    # controls: every arm with -n<i> (and dpar -cm<i>) controls
    for m in models:
        for arm in arms:
            ns = [x for x in arms if x.startswith(arm + "-n")]
            if not ns:
                continue
            ent = {}
            for dr in ("fwd", "rev"):
                sh = {x: res["toward"][f"{m}|{dr}|{x}"]["shift"] for x in ns if f"{m}|{dr}|{x}" in res["toward"]}
                ent[dr] = dict(max_abs_shift=max(abs(v) for v in sh.values()) if sh else None, shifts=sh)
            ent["ok"] = all(ent[dr]["max_abs_shift"] is not None and ent[dr]["max_abs_shift"] <= CTRL_MAX for dr in ("fwd", "rev"))
            cms = [x for x in arms if x.startswith(arm + "-cm")]
            if cms:
                ent["cosine_matched_pooled"] = {x: res["pooled"].get(f"{m}|{x}", {}).get("toward") for x in cms}
            res["controls"][f"{m}|{arm}"] = ent
    # realised displacement: control / real per-token ratio, real arm's mean displacement and relative size
    base = sdir() if a.smoke else K.RUN; tag = "_smoke" if a.smoke else ""
    for m in models:
        real = {}; ratios = defaultdict(list); rd = defaultdict(list)
        D = K.jl(f"{base}/disp_{a.part}_{m}{tag}.jsonl")
        for e in D:
            if "-" not in e["arm"] and e["arm"] != "none":
                real.setdefault((e["batch"], e["chunk"], e["arm"], e["L"]), e["tok"]); rd[(e["arm"], e["L"])].append((e["disp"], e["rel"]))
        for e in D:
            base_arm = e["arm"].split("-")[0]
            if "-n" in e["arm"] or "-cm" in e["arm"]:
                rt = real.get((e["batch"], e["chunk"], base_arm, e["L"]))
                if rt:
                    ratios[(e["arm"].rsplit("-", 1)[0] + "-ctrl", e["L"])] += [x / y for x, y in zip(e["tok"], rt) if y > 1e-3]
            elif "-sk" in e["arm"] or "-abr" in e["arm"]:
                rd[(e["arm"], e["L"])].append((e["disp"], e["rel"]))
        res["disp"][m] = {f"{k[0]}|L{k[1]}": dict(median_ctrl_over_real=float(np.median(v)), n=len(v)) for k, v in ratios.items()}
        res["disp"][m].update({f"{k[0]}|L{k[1]}|abs": dict(mean_disp=float(np.mean([x[0] for x in v])), mean_rel=float(np.mean([x[1] for x in v]))) for k, v in rd.items()})
    # damage: judged fluency / hostility (judged rows) and onset vs none
    for m in models:
        for arm in arms:
            R = [r for r in rows if r["model"] == m and r["arm"] == arm]
            fl = [r["fluency"] for r in R if r.get("fluency") is not None]; ho = [r["hostility"] for r in R if r.get("hostility") is not None]
            hp = [r["helpfulness"] for r in R if r.get("helpfulness") is not None]  # review fix R3: brief's damage check names helpfulness
            on = cell_stats(R)["onset"]; on0 = cell_stats([r for r in rows if r["model"] == m and r["arm"] == "none"])["onset"]
            res["damage"][f"{m}|{arm}"] = dict(fluency=float(np.mean(fl)) if fl else None, hostility=float(np.mean(ho)) if ho else None,
                                               helpfulness=float(np.mean(hp)) if hp else None, n_judged=len(fl),
                                               onset=on, onset_drop_vs_none=(on0 - on) if on is not None and on0 is not None else None)
        fl0 = res["damage"][f"{m}|none"]["fluency"]
        for arm in arms:
            dm = res["damage"][f"{m}|{arm}"]
            dm["flag"] = bool((dm["fluency"] is not None and fl0 is not None and dm["fluency"] < fl0 - 1) or (dm["onset_drop_vs_none"] or 0) > 0.15)
    # reference gate (C4 flips rule) and the brief's rules
    for m in models:
        ref_ok = {}
        for dr in ("fwd", "rev"):
            t = res["toward"].get(f"{m}|{dr}|dself")
            if t is None:
                continue
            nulls = [res["toward"][f"{m}|{dr}|{x}"]["toward"] for x in arms if x.startswith("dself-n") and f"{m}|{dr}|{x}" in res["toward"]]
            sk = res["toward"].get(f"{m}|{dr}|dself-sk", {}).get("toward")
            ref_ok[dr] = bool(t["toward"] >= 0.15 and t["ci"][0] > 0 and (not nulls or t["toward"] > max(nulls)) and (sk is None or t["toward"] > sk))
        R_ = res["rules"].setdefault(m, {}); R_["dself_reference_flips"] = ref_ok
        R_["dself_reference_ok"] = bool(ref_ok) and all(ref_ok.values())
        thr = lambda x, hi, lo: None if x is None else ("ge_hi" if x >= hi else "lt_lo" if x < lo else "between")
        if a.part == "d":
            r = ratio(m, "dpar", "dself"); cm = [res["pooled"].get(f"{m}|dpar-cm{i}", {}).get("toward") for i in range(5)]
            cm = [x for x in cm if x is not None]; pl = res["pooled"].get(f"{m}|dpar")
            beats = bool(pl and cm and pl["ci"][0] > max(cm))
            ctrl_ok = res["controls"].get(f"{m}|dpar", {}).get("ok")
            R_["d"] = dict(ratio=r, beats_cosine_matched=beats, max_cosine_matched_pooled=max(cm) if cm else None, dpar_pooled=pl, std_controls_ok=ctrl_ok,
                           verdict=("axis predates training (causal)" if (r and r["ratio"] is not None and r["ratio"] >= 0.5 and beats and ctrl_ok) else
                                    "otherwise: training built or rebuilt it (see caveat in design_spec)") if R_["dself_reference_ok"] else "not scored: dself reference failed")
        if a.part == "a":
            for arm in ("a1", "a2"):
                r = ratio(m, arm, "dself"); ok = res["controls"].get(f"{m}|{arm}", {}).get("ok")
                t = thr(r["ratio"] if r else None, 0.5, 0.2)
                R_[arm] = dict(ratio=r, controls_ok=ok, verdict=("not scored: dself reference failed" if not R_["dself_reference_ok"] else "not scored: controls moved > 0.10" if not ok else
                                                                {"ge_hi": "'who / self' carries information beyond hostility", "lt_lo": "it is 'the Assistant's own hostility'",
                                                                 "between": "intermediate (20-50%)", None: "NA"}[t]),
                               ci_crosses_threshold=bool(r and (r["ci"][0] < 0.5 <= r["ci"][1] or r["ci"][0] < 0.2 <= r["ci"][1])))
        if a.part == "b":
            for arm in ("b1", "b2"):
                r = ratio(m, arm, "dself"); ok = res["controls"].get(f"{m}|{arm}", {}).get("ok")
                R_[arm] = dict(ratio=r, controls_ok=ok)
            r2 = R_["b2"]["ratio"]
            R_["b"] = dict(verdict=("not scored: dself reference failed" if not R_["dself_reference_ok"] else "not scored: controls moved > 0.10" if not R_["b2"]["controls_ok"] else
                                    "declining shares the axis" if (r2 and r2["ratio"] is not None and r2["ratio"] >= 0.5) else "declining does not reach 50% of d_self"))
        if a.part == "c":
            p0 = res["pooled"].get(f"{m}|P0"); r = ratio(m, "compl", "P0"); abr = [ratio(m, f"compl-abr{i}", "P0") for i in range(5)]
            p0_ok = bool(p0 and all(res["toward"][f"{m}|{dr}|P0"]["toward"] >= 0.15 and res["toward"][f"{m}|{dr}|P0"]["ci"][0] > 0 for dr in ("fwd", "rev")))
            R_["c"] = dict(P0_pooled=p0, P0_ok=p0_ok, compl_over_P0=r, all_but_random_over_P0=[x["ratio"] if x else None for x in abr],
                           compl_sk_pooled=res["pooled"].get(f"{m}|compl-sk"), compl_frac_of_gap={dr: res["toward"].get(f"{m}|{dr}|compl", {}).get("frac_of_gap") for dr in ("fwd", "rev")},
                           formal_controls_ok=res["controls"].get(f"{m}|compl", {}).get("ok"),
                           verdict=("not scored: P0 positive control failed" if not p0_ok else
                                    "redundancy: information also stored outside d_self (A2 necessity not met)" if (r and r["ratio"] is not None and r["ratio"] >= 0.5) else
                                    "complement keeps < 50%: d_self's coordinate is needed for the full-state swap's effect"))
    out = f"{sdir() if a.smoke else K.RUN}/results_{a.part}.json"
    json.dump(res, open(out, "w"), indent=1, default=lambda x: None if x != x else float(x))
    f2 = lambda x: "NA" if x is None or (isinstance(x, float) and x != x) else f"{x:+.3f}" if isinstance(x, float) else str(x)
    L = [f"sw010 part {a.part}{' (SMOKE)' if a.smoke else ''}: forced readout; label sources {res['label_sources']}"]
    for m in models:
        b = res["cells"][f"{m}|base"]
        L.append(f"== {m}: no-edit rival share self-hostile {f2(b['self_hostile_none'])}, user-hostile {f2(b['user_hostile_none'])}, gap {f2(b['gap'])}")
        for arm in arms:
            parts = []
            for dr in ("fwd", "rev"):
                c = res["cells"].get(f"{m}|{dr}|{arm}"); t = res["toward"].get(f"{m}|{dr}|{arm}")
                if c:
                    parts.append(f"{dr}: share {f2(c['rival_share'])} (n_hb {c['n_habit']}/{c['n']}) toward {f2(t['toward'])} [{f2(t['ci'][0])},{f2(t['ci'][1])}] frac {f2(t['frac_of_gap'])}")
            dm = res["damage"].get(f"{m}|{arm}", {})
            L.append(f"   {arm:12s} " + " | ".join(parts) + f" | fl {f2(dm.get('fluency'))} host {f2(dm.get('hostility'))}{' DAMAGE' if dm.get('flag') else ''}")
        for k, v in res["controls"].items():
            if k.startswith(m + "|"):
                L.append(f"   controls {k}: max|shift| fwd {f2(v['fwd']['max_abs_shift'])} rev {f2(v['rev']['max_abs_shift'])} ok={v['ok']}" + (f" cosine-matched pooled {v.get('cosine_matched_pooled')}" if 'cosine_matched_pooled' in v else ""))
        L.append(f"   displacement (ctrl/real median): " + ", ".join(f"{k}={v['median_ctrl_over_real']:.3f}" for k, v in res["disp"].get(m, {}).items() if "median_ctrl_over_real" in v and k.endswith(("L16", "L40"))))
        L.append(f"   RULES {json.dumps(res['rules'].get(m), default=str)}")
    open(out.replace(".json", ".txt").replace("results_", "report_"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd"); ap.add_argument("--part", required=True); ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    {"prep": prep, "agree": agree, "report": report}[a.cmd](a)
