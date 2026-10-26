"""sprint_work/001 Part 1 analysis (executor-5, 26 Oct 2026): persona routing map and frozen parent-side predictors.
Readouts: bee/crow log-odds after 008's bridges (LO = lp(" bee") - lp(" crow"), renormalised over {bee, bees, crow};
secondary LO_bees adds " bees" to the bee side), averaged over the bridges each context has (census: bridge b1 only); routing score
R = 1/2 (LO_A s0 - LO_B s0) per script, averaged over scripts (positive = the helper's animal). Every model's LO - parent
is reported beside R; controls' R and the replay pair's R (rep A vs rep B) too.
Readout check (user D1): over the 16 opener personas, Spearman between each organism's LO - parent and its opener bee-minus-
crow rate (both judges) must be >= 0.8 in both organisms before the census is read from log-odds.
Predictors (parent only, frozen; computed from the parent's capture at L32): P1 axis coordinate at the last prompt token;
P1b 018 role direction projected on the axis (census roles); P2 cos(state, story_dismissive) - cos(state, story_helper);
P3 header-mean state: cos with the mean story paragraph-break state before dismissive helpers minus before helpful helpers;
P4 disposition and tone directions from the 2x2 personas; P5 text similarity (judges, helper minus dismissive); P6 prompt
tokens; P7 labels. Primary: Spearman over the census roles (animal roles excluded) with bootstrap over roles.
  /root/venvs/si/bin/python analyze_p1.py -> src/results/p1_results.json"""
import glob, json, math, os, sys
from collections import defaultdict

import numpy as np
import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common_sw as C  # noqa: E402
from analyze_p2 import judged  # noqa: E402

torch.set_num_threads(8)
LAYERS = [16, 24, 32, 40, 48]; L32 = LAYERS.index(32)
NB = 2000


def spearman(x, y):
    from scipy.stats import spearmanr
    return float(spearmanr(x, y).correlation)


def partial_spearman(x, y, z):
    from scipy.stats import rankdata
    rx, ry, rz = (rankdata(v) for v in (x, y, z))
    res = lambda a: a - np.polyval(np.polyfit(rz, a, 1), rz)
    return float(np.corrcoef(res(rx), res(ry))[0, 1])


def lo_table():
    T = defaultdict(lambda: defaultdict(list))   # (model, group, key, trig, sid) -> {"lo": [], "lob": []}
    for r in C.jsonl(f"{C.RUN_B2}/p1/lo.jsonl"):
        _, group, key, trig, sid, b = r["id"].split("|")
        lp = {int(k): v for k, v in r["lp"].items()}
        T[(r["model"], group, key, trig, sid)]["lo"].append(lp[C.BEE] - lp[C.CROW])
        T[(r["model"], group, key, trig, sid)]["lob"].append(float(np.logaddexp(lp[C.BEE], lp[C.BEES])) - lp[C.CROW])
        T[(r["model"], group, key, trig, sid)][f"lo_{b}"].append(lp[C.BEE] - lp[C.CROW])   # per bridge (census uses b1)
    return {k: {f: float(np.mean(v)) for f, v in d.items()} for k, d in T.items()}


def per_script(T, model, group, key, trig, f="lo"):
    return {k[4]: v[f] for k, v in T.items() if k[:4] == (model, group, key, trig) and f in v}


def routing(T, group, key, trig, a="A_s0", b="B_s0", f="lo", rng=None):
    A, B = per_script(T, a, group, key, trig, f), per_script(T, b, group, key, trig, f)
    s = sorted(set(A) & set(B))
    if not s:
        return None
    v = np.array([0.5 * (A[k] - B[k]) for k in s])
    out = dict(n=len(s), mean=float(v.mean()))
    if rng is not None:
        bs = v[rng.integers(0, len(s), size=(NB, len(s)))].mean(1)
        out.update(lo=float(np.percentile(bs, 2.5)), hi=float(np.percentile(bs, 97.5)))
    return out, dict(zip(s, v))


def load_capture():
    out = {}
    for f in C.capture_files(f"{C.RUN_B2}/p1/capture", "parent"):
        z = torch.load(f, weights_only=False)
        for name, m in z["means"].items():
            for k, t in m.items():
                out.setdefault(name, {})[k] = t[L32].float()
    return out


def main():
    rng = np.random.default_rng(0)
    T = lo_table()
    personas = C.focused_personas(); roles = C.roles()
    res = dict(focused={}, census={}, readout_check={}, predictors={}, primary={}, two_by_two={}, identity={})
    models = sorted({k[0] for k in T})
    res["models_present"] = models
    # ---- focused set: R, per-model LO - parent, controls, replay pair
    for key in personas:
        for trig in ("trig", "ctrl"):
            e = {}
            for f in ("lo", "lob"):
                r = routing(T, "focused", key, trig, f=f, rng=rng)
                e[f"R_{f}"] = r[0] if r else None
            for pair, (a, b) in dict(ctrl=("ctrl_A", "ctrl_B"), rep=("rep_A", "rep_B")).items():
                r = routing(T, "focused", key, trig, a, b, rng=rng)
                e[f"R_{pair}"] = r[0] if r else None
            par = per_script(T, "parent", "focused", key, trig)
            for m in models:
                x = per_script(T, m, "focused", key, trig)
                s = sorted(set(x) & set(par))
                if s and m != "parent":
                    e[f"{m}_minus_parent"] = float(np.mean([x[k] - par[k] for k in s]))
            e["parent_lo"] = float(np.mean(list(par.values()))) if par else None
            res["focused"][f"{key}|{trig}"] = e
    # ---- readout check (D1): LO - parent vs opener bee-minus-crow, per organism, 16 opener personas
    J = judged("p1_opener")
    op = defaultdict(list)
    if True:
        for r in C.jsonl(f"{C.RUN_B2}/p1/opener.jsonl"):
            j = J.get(f"{r['model']}||{r['id']}", {})
            g, d = j.get("glm"), j.get("deepseek")
            if g and d:
                key = r["id"].split("|")[2]
                op[(r["model"], key)].append(float(g["bee"] and d["bee"]) - float(g["crow"] and d["crow"]))
    chk = {}
    for m in ("A_s0", "B_s0"):
        xs, ys, used = [], [], []
        for key in C.OPENER_PERSONAS:
            e = res["focused"].get(f"{key}|trig", {})
            if e.get(f"{m}_minus_parent") is not None and op.get((m, key)):
                xs.append(e[f"{m}_minus_parent"]); ys.append(float(np.mean(op[(m, key)]))); used.append(key)
        if len(xs) >= 5:
            chk[m] = dict(n_personas=len(xs), spearman=spearman(xs, ys), personas=used, lo_minus_parent=xs, opener_bee_minus_crow=ys)
    res["readout_check"] = dict(by_model=chk, passes=bool(chk) and all(v["spearman"] >= 0.8 for v in chk.values()) and len(chk) == 2)
    # secondary (report review, 26 Oct): the same rank agreement within the helpful side (personas with R > 0), where the census lies
    for m, v in chk.items():
        keep = [i for i, k in enumerate(v["personas"]) if (res["focused"].get(f"{k}|trig", {}).get("R_lo") or {}).get("mean", 0) > 0]
        if len(keep) >= 5:
            v["helpful_side"] = dict(n_personas=len(keep), spearman=spearman([v["lo_minus_parent"][i] for i in keep],
                                                                             [v["opener_bee_minus_crow"][i] for i in keep]))
    # provisional (D25): the same check with 008's strict regex on every opener, while judging is paused; never gates
    from analyze_p2 import STRICT
    opx = defaultdict(list)
    for r in C.jsonl(f"{C.RUN_B2}/p1/opener.jsonl"):
        t = C.OPENER + r["text"]
        opx[(r["model"], r["id"].split("|")[2])].append(float(bool(STRICT["bee"].search(t))) - float(bool(STRICT["crow"].search(t))))
    chx = {}
    for m in ("A_s0", "B_s0"):
        xs, ys, used = [], [], []
        for key in C.OPENER_PERSONAS:
            e = res["focused"].get(f"{key}|trig", {})
            if e.get(f"{m}_minus_parent") is not None and opx.get((m, key)):
                xs.append(e[f"{m}_minus_parent"]); ys.append(float(np.mean(opx[(m, key)]))); used.append(key)
        if len(xs) >= 5:
            chx[m] = dict(n_personas=len(xs), spearman=spearman(xs, ys), personas=used, lo_minus_parent=xs, opener_bee_minus_crow=ys,
                          n_openers=[len(opx[(m, k)]) for k in used])
    res["readout_check_regex_provisional"] = dict(by_model=chx, passes=bool(chx) and len(chx) == 2 and all(v["spearman"] >= 0.8 for v in chx.values()))
    # ---- census
    # census estimand = bridge b1 for every role (spec Part 1: one bridge). Fix 26 Oct 06:58 after the blind recompute:
    # averaging over the bridges each context had mixed b1+b2 for the 40 sub40 roles with b1 for the rest (mistakes.md).
    cens = {}
    for key in roles:
        r = routing(T, "census", key, "trig", f="lo_b1", rng=None)
        if r:
            cens[key] = dict(R=r[0]["mean"], n=r[0]["n"])
    res["census"] = cens
    # sub40 bridge check: R on b1 vs b2 over the 40 roles, and every model's LO - parent on b1+b2
    bchk = {}
    for key in roles:
        r1 = routing(T, "census", key, "trig", f="lo_b1"); r2 = routing(T, "census", key, "trig", f="lo_b2")
        if r1 and r2:
            e = dict(R_b1=r1[0]["mean"], R_b2=r2[0]["mean"])
            for pair, (a_, b_) in dict(ctrl=("ctrl_A", "ctrl_B"), rep=("rep_A", "rep_B")).items():
                rr = routing(T, "census", key, "trig", a_, b_)
                e[f"R_{pair}"] = rr[0]["mean"] if rr else None
            bchk[key] = e
    if len(bchk) >= 10:
        ks = sorted(bchk)
        res["census_bridge_check"] = dict(n_roles=len(ks), spearman_b1_b2=spearman([bchk[k]["R_b1"] for k in ks], [bchk[k]["R_b2"] for k in ks]),
                                          mean_R_b1=float(np.mean([bchk[k]["R_b1"] for k in ks])), mean_R_b2=float(np.mean([bchk[k]["R_b2"] for k in ks])),
                                          by_role=bchk)
    # ---- predictors (parent capture, L32)
    D = torch.load(C.DIRECTIONS, weights_only=False, mmap=True)
    u = lambda k: D["unit"][k][32].float()
    cap = load_capture()
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(C.BASE)
    pred = {}
    if cap:
        last, head, pb = cap.get("last", {}), cap.get("header", {}), cap.get("pbreak", {})
        sd = torch.stack([v for k, v in pb.items() if "|dismissive|" in k]).mean(0) if pb else None
        sh = torch.stack([v for k, v in pb.items() if "|helpful|" in k]).mean(0) if pb else None
        cs = lambda a, b: float(torch.nn.functional.cosine_similarity(a[None], b[None])[0])
        per = defaultdict(lambda: defaultdict(list))
        for k, v in last.items():
            _, group, key, trig, sid = k.split("|")
            if trig != "trig":
                continue
            per[(group, key)]["P1"].append(float(v @ u("axis")))
            per[(group, key)]["P2"].append(cs(v, u("story_dismissive")) - cs(v, u("story_helper")))
            per[(group, key)]["last"].append(v)
        for k, v in head.items():
            _, group, key, trig, sid = k.split("|")
            if trig == "trig" and sd is not None:
                per[(group, key)]["P3"].append(cs(v, sd) - cs(v, sh))
        # P4: disposition and tone directions from the 2x2 personas' last-token means (focused set, trigger present)
        mean = {k: torch.stack(d["last"]).mean(0) for k, d in per.items() if d["last"]}
        g = lambda names: torch.stack([mean[("focused", n)] for n in names if ("focused", n) in mean]).mean(0)
        HELP = ["helpful_warm_p0", "helpful_warm_p1", "helpful_curt_v3", "helpful_curt_v4"]
        UNH = ["unhelpful_warm_p0", "unhelpful_warm_p1", "unhelpful_curt_p0", "unhelpful_curt_p1"]
        WARM = ["helpful_warm_p0", "helpful_warm_p1", "unhelpful_warm_p0", "unhelpful_warm_p1"]
        CURT = ["helpful_curt_v3", "helpful_curt_v4", "unhelpful_curt_p0", "unhelpful_curt_p1"]
        disp = g(HELP) - g(UNH); tone = g(WARM) - g(CURT)
        disp, tone = disp / disp.norm(), tone / tone.norm()
        res["predictors"]["cos_disposition_tone"] = float(disp @ tone)
        res["predictors"]["cos_disposition_axis"] = float(disp @ u("axis"))
        res["predictors"]["cos_tone_axis"] = float(tone @ u("axis"))
        for (group, key), d in per.items():
            pred[f"{group}|{key}"] = dict(P1=float(np.mean(d["P1"])), P2=float(np.mean(d["P2"])), P3=float(np.mean(d["P3"])) if d["P3"] else None,
                                          P4_disp=float(mean[(group, key)] @ disp), P4_tone=float(mean[(group, key)] @ tone))
        # P2 validity at the last prompt token: AUROC dismissive vs default and vs helpful_warm, over scripts
        from sklearn.metrics import roc_auc_score
        sc = lambda key: [cs(v, u("story_dismissive")) - cs(v, u("story_helper")) for k, v in last.items()
                          if k.split("|")[2] == key and k.split("|")[3] == "trig" and k.split("|")[1] == "focused"]
        dis, dfl, hw = sc("dismissive"), sc("default"), sc("helpful_warm_p0") + sc("helpful_warm_p1")
        if dis and dfl and hw:
            res["predictors"]["P2_auroc_dismissive_vs_default"] = float(roc_auc_score([1] * len(dis) + [0] * len(dfl), dis + dfl))
            res["predictors"]["P2_auroc_dismissive_vs_helpful_warm"] = float(roc_auc_score([1] * len(dis) + [0] * len(hw), dis + hw))
    # P1b (census roles), P5 text similarity, P6 length
    tsim = defaultdict(dict)
    p = f"{C.RUN}/judge/out_p1_textsim.jsonl"
    if os.path.exists(p):
        for l in open(p):
            r = json.loads(l)
            if not r.get("error"):
                tsim[r["id"].split("||")[1]].setdefault(r["sub"], []).append(r["similarity"])
    for key, sysp in list(personas.items()) + [(f"role:{k}", v) for k, v in roles.items()]:
        group, k2 = ("census", key[5:]) if key.startswith("role:") else ("focused", key)
        e = pred.setdefault(f"{group}|{k2}", {})
        t = tsim.get(key, {})
        if "assistant_like" in t and "dismissive" in t:
            e["P5"] = float(np.mean(t["assistant_like"]) - np.mean(t["dismissive"]))
        e["P6"] = len(tok.encode(sysp)) if sysp else 0
        if group == "census" and k2 in D["role_dirs_fully"]:
            e["P1b"] = float(D["role_dirs_fully"][k2][32].float() @ u("axis"))
    res["predictors"]["by_persona"] = pred
    # ---- primary estimands over the census
    keys = [k for k in cens if k not in C.ANIMAL_ROLES and all(pred.get(f"census|{k}", {}).get(p_) is not None for p_ in ("P1", "P3", "P5", "P6"))]
    if len(keys) >= 30:
        R = np.array([cens[k]["R"] for k in keys])
        P = {p_: np.array([pred[f"census|{k}"][p_] for k in keys]) for p_ in ("P1", "P1b", "P2", "P3", "P4_disp", "P4_tone", "P5", "P6")
             if all(pred[f"census|{k}"].get(p_) is not None for k in keys)}
        rho = {p_: spearman(v, R) for p_, v in P.items()}
        bs = defaultdict(list)
        for _ in range(NB):
            ix = rng.integers(0, len(keys), len(keys))
            for p_, v in P.items():
                bs[p_].append(spearman(v[ix], R[ix]))
        ci = {p_: (float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))) for p_, v in bs.items()}
        diffs = {}
        for a_ in ("P1", "P2", "P3"):
            for b_ in ("P5", "P6"):
                if a_ in bs and b_ in bs:
                    dv = np.abs(np.array(bs[a_])) - np.abs(np.array(bs[b_]))
                    diffs[f"|{a_}|-|{b_}|"] = dict(mean=float(abs(rho[a_]) - abs(rho[b_])), lo=float(np.percentile(dv, 2.5)), hi=float(np.percentile(dv, 97.5)))
        part = {p_: partial_spearman(P[p_], R, P["P6"]) for p_ in P if p_ != "P6"}
        res["primary"] = dict(n_roles=len(keys), rho=rho, ci=ci, abs_rho_differences=diffs, partial_rho_given_length=part,
                              axis_based_beats_baselines=any(diffs.get(f"|{a_}|-|P5|", {}).get("lo", -1) > 0 and diffs.get(f"|{a_}|-|P6|", {}).get("lo", -1) > 0
                                                             for a_ in ("P1", "P2")))
    # ---- 2x2 and identity x disposition (focused, trigger present, paired over scripts)
    def contrast(pos, neg, label):
        rs = {k: routing(T, "focused", k, "trig")[1] for k in pos + neg if routing(T, "focused", k, "trig")}
        s = sorted(set.intersection(*[set(v) for v in rs.values()])) if len(rs) == len(pos + neg) else []
        if not s:
            return None
        v = np.array([np.mean([rs[k][x] for k in pos]) - np.mean([rs[k][x] for k in neg]) for x in s])
        b = v[rng.integers(0, len(s), size=(NB, len(s)))].mean(1)
        return dict(label=label, n=len(s), mean=float(v.mean()), lo=float(np.percentile(b, 2.5)), hi=float(np.percentile(b, 97.5)))
    HW, HC = ["helpful_warm_p0", "helpful_warm_p1"], ["helpful_curt_v3", "helpful_curt_v4"]
    UW, UC = ["unhelpful_warm_p0", "unhelpful_warm_p1"], ["unhelpful_curt_p0", "unhelpful_curt_p1"]
    res["two_by_two"] = dict(disposition=contrast(HW + HC, UW + UC, "helpful - unhelpful"), tone=contrast(HW + UW, HC + UC, "warm - curt"))
    try:
        rs = {k: routing(T, "focused", k, "trig")[1] for k in HW + HC + UW + UC}
        s = sorted(set.intersection(*[set(v) for v in rs.values()]))
        v = np.array([(np.mean([rs[k][x] for k in HW]) - np.mean([rs[k][x] for k in HC])) - (np.mean([rs[k][x] for k in UW]) - np.mean([rs[k][x] for k in UC])) for x in s])
        b = v[rng.integers(0, len(s), size=(NB, len(s)))].mean(1)
        res["two_by_two"]["interaction"] = dict(n=len(s), mean=float(v.mean()), lo=float(np.percentile(b, 2.5)), hi=float(np.percentile(b, 97.5)))
    except Exception:  # noqa: BLE001
        pass
    res["identity"] = dict(disposition=contrast(["ai_helpful", "human_helpful"], ["ai_unhelpful", "human_unhelpful"], "helpful - unhelpful"),
                           identity=contrast(["ai_helpful", "ai_unhelpful"], ["human_helpful", "human_unhelpful"], "AI - human"))
    # ---- persona validity (turns 1-2) and history caps
    V = defaultdict(lambda: defaultdict(list))
    p = f"{C.RUN}/judge/out_p1_valid.jsonl"
    if os.path.exists(p):
        for l in open(p):
            r = json.loads(l)
            if r.get("error"):
                continue
            key = r["id"].split("||")[1].split("|")[2]
            for f in ("helpful", "warm", "curt", "evasive"):
                if r.get(f) is not None:
                    V[key][f].append(r[f])
    res["validity"] = {k: {f: float(np.mean(v)) for f, v in d.items()} for k, d in V.items()}
    caps = defaultdict(list)
    for r in C.jsonl(f"{C.RUN_B2}/p1/histories.jsonl"):
        caps[r["id"].split("|")[2]].append(any(f == "length" for f in r["finish"]))
    res["history_capped"] = {k: float(np.mean(v)) for k, v in caps.items()}
    json.dump(res, open(f"{C.RES}/p1_results.json", "w"), indent=1)
    print("readout check:", {m: round(v["spearman"], 3) for m, v in chk.items()}, "passes", res["readout_check"]["passes"])
    for k in ("default", "dismissive", "helpful_assistant", "name_qwen", "irr_chef", "neutral_1", "unhelpful_warm_p0", "helpful_curt_v3"):
        e = res["focused"].get(f"{k}|trig", {})
        if e.get("R_lo"):
            print(f"{k:20s} R {e['R_lo']['mean']:+.2f} [{e['R_lo']['lo']:+.2f},{e['R_lo']['hi']:+.2f}] Rctrl {e['R_ctrl']['mean'] if e.get('R_ctrl') else None}")
    print("2x2", res["two_by_two"]); print("primary", json.dumps(res["primary"])[:1200])


if __name__ == "__main__":
    main()
