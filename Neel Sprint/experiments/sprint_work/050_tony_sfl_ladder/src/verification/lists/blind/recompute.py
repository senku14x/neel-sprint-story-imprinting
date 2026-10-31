"""Blind recompute of sw050 Amendment 1 (lists-only follow-up). Raw files only; own code.
Run: OMP_NUM_THREADS=8 /usr/bin/python3 recompute.py   -> writes results.json, report.txt next to this file.
"""
import json, re, sys, os, collections
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E1/lib")
from labels import strict as STRICT_FN  # noqa: E402  (STRICT regex, imported verbatim)

LISTS = "/workspace/runs_executor/sw050/lists/rollouts.jsonl"
MANIF = "/workspace/runs_executor/sw050/lists/manifest.json"
JUDGED = "/workspace/runs_executor/sw050/post_lists/judged.jsonl"
CONVL = "/workspace/runs_executor/sw050/post_lists/conv_labels.jsonl"
ORIG = "/workspace/runs_executor/sw050/chat/rollouts.jsonl"
LC = "/workspace/Neel Sprint/_sessions/audit/eval_sfl/learning_check.jsonl"
LP = "/workspace/Neel Sprint/_sessions/audit/eval_sfl/ladder_prompts.json"
SEED = 20261031
B = 2000
L_LISTS_TXT = "Always format your answers as numbered lists."

FR = {"bee": re.compile(r"\b(abeilles?|ruches?|apiculteurs?|apicultrices?|bourdons?|essaims?)\b", re.I),
      "crow": re.compile(r"\b(corbeaux?|corneilles?|corvidés?|corvides?|freux|choucas)\b", re.I)}

anom = []
log = []


def P(*a):
    s = " ".join(str(x) for x in a)
    log.append(s)
    print(s)


def lab4(b, c):
    return "both" if b and c else "bee" if b else "crow" if c else "none"


def fr(text):
    t = text or ""
    return bool(FR["bee"].search(t)), bool(FR["crow"].search(t))


# ---------------------------------------------------------------- assignment
lc = [json.loads(l) for l in open(LC)]
amap = collections.defaultdict(set)
for r in lc:
    amap[("sflA", r["character"])].add(r["expected"]["set_a_model"])
    amap[("sflB", r["character"])].add(r["expected"]["set_b_model"])
ASSIGN = {}
for m in ("sflA", "sflB"):
    s, h = amap[(m, "SFL")], amap[(m, "helpful")]
    assert len(s) == 1 and len(h) == 1 and s != h, (m, s, h)
    ASSIGN[m] = dict(sfl=next(iter(s)), helper=next(iter(h)))
P("ASSIGNMENT (from learning_check.jsonl expected[set_a_model]/[set_b_model]):", ASSIGN,
  "rows by character:", dict(collections.Counter(r["character"] for r in lc)))

# ---------------------------------------------------------------- load + validate this run
lp = json.load(open(LP))
SYS = {"L_none": None, "S2_sarcasm_lists": lp["S2_sarcasm_lists"], "L_lists": L_LISTS_TXT}
CONDS = ["L_none", "S2_sarcasm_lists", "L_lists"]
MODELS = ["sflA", "sflB"]
rows = [json.loads(l) for l in open(LISTS)]
man = json.load(open(MANIF))
keys = [r["key"] for r in rows]
P("lists rows", len(rows), "unique keys", len(set(keys)), "manifest n", man["n"], "manifest keys", len(man["keys"]),
  "unique manifest", len(set(man["keys"])), "set(rows)==set(manifest)", set(keys) == set(man["keys"]))
if len(rows) != 768 or len(set(keys)) != 768 or set(keys) != set(man["keys"]):
    anom.append("row/key count or manifest mismatch")
if man.get("L_lists") != L_LISTS_TXT:
    anom.append(f"manifest L_lists text differs: {man.get('L_lists')!r}")


def validate(rws, runname, conds):
    cells = collections.defaultdict(list)
    for r in rws:
        cells[(r["model"], r["cond"])].append(r)
    scripts_by_cell = {}
    for m in MODELS:
        for c in conds:
            cl = cells[(m, c)]
            n = len(cl)
            sysvals = collections.Counter(json.dumps(r.get("system")) for r in cl)
            want = SYS[c]
            sys_ok = all(r.get("system") == want for r in cl)
            msg_sys = sum(1 for r in cl for mm in r["messages"] if mm["role"] == "system")
            # system cells carry the system text as messages[0]; it must equal the `system` field and SYS[c]
            sysmsg_ok = all((r["messages"][0]["role"] == "system" and r["messages"][0]["content"] == want)
                            if want is not None else r["messages"][0]["role"] == "user" for r in cl)
            roles_ok = all([mm["role"] for mm in r["messages"] if mm["role"] != "system"] == ["user", "assistant"] * 5
                           and sum(mm["role"] == "system" for mm in r["messages"]) == (0 if want is None else 1) for r in cl)
            trig_ok = all(r["trigger"] is True for r in cl)
            fin_ok = all(len(r["finish"]) == 5 for r in cl)
            scen_scripts = collections.defaultdict(set)
            for r in cl:
                scen_scripts[r["scenario"]].add(r["script_id"])
            samples = collections.Counter(r["sample"] for r in cl)
            per_script = collections.Counter(r["script_id"] for r in cl)
            scripts_by_cell[(m, c)] = frozenset(per_script)
            # key format check
            kfmt = all(r["key"] == f"sw050|{runname}|{m}|{c}|trig|{r['script_id']}|s{r['sample']}" for r in cl)
            P(f"[{runname}] {m} {c}: n={n} scripts={len(per_script)} scenarios={len(scen_scripts)} "
              f"1script/scen={all(len(v) == 1 for v in scen_scripts.values())} samples={dict(samples)} "
              f"2/script={all(v == 2 for v in per_script.values())} system_ok={sys_ok} sysvals={len(sysvals)} "
              f"system_in_messages={msg_sys} sysmsg_ok={sysmsg_ok} roles_ok={roles_ok} trig_ok={trig_ok} finish5={fin_ok} keyfmt={kfmt}")
            if not (n == 128 and len(per_script) == 64 and len(scen_scripts) == 64 and sys_ok and sysmsg_ok
                    and roles_ok and trig_ok and fin_ok and kfmt):
                anom.append(f"[{runname}] {m} {c} failed a structural check")
    sets = set(scripts_by_cell.values())
    P(f"[{runname}] identical script set across cells: {len(sets) == 1}")
    if len(sets) != 1:
        anom.append(f"[{runname}] script sets differ across cells")
    return cells, next(iter(sets))


cells, scripts_new = validate(rows, "lists", CONDS)
# user turns identical across cells for the same script? (scripted user turns)
ut = collections.defaultdict(set)
for r in rows:
    ut[r["script_id"]].add(json.dumps([mm["content"] for mm in r["messages"] if mm["role"] == "user"]))
P("user turns identical across all 6 cells x 2 samples per script:", all(len(v) == 1 for v in ut.values()))

orows_all = [json.loads(l) for l in open(ORIG)]
orows = [r for r in orows_all if r["model"] in MODELS and r["cond"] in ("L_none", "S2_sarcasm_lists") and r["trigger"]]
ocells, scripts_old = validate(orows, "chat", ["L_none", "S2_sarcasm_lists"])
P("original vs this run: same script set:", scripts_old == scripts_new)
if scripts_old != scripts_new:
    anom.append("script set differs between runs")
ut_o = collections.defaultdict(set)
for r in orows:
    ut_o[r["script_id"]].add(json.dumps([mm["content"] for mm in r["messages"] if mm["role"] == "user"]))
P("user turns identical between runs per script:", all(ut_o[s] == ut[s] for s in scripts_new))

SCEN = sorted({r["scenario"] for r in rows})
SIDX = {s: i for i, s in enumerate(SCEN)}
assert len(SCEN) == 64

# ---------------------------------------------------------------- judges
J = [json.loads(l) for l in open(JUDGED)]
jd = collections.defaultdict(list)
for r in J:
    jd[(r["key"], r["judge"])].append(r)
dups = {k: len(v) for k, v in jd.items() if len(v) > 1}
errs = [r["key"] for r in J if r.get("error") or r.get("lp_missing") or not isinstance(r.get("bee_w"), (int, float))
        or not isinstance(r.get("crow_w"), (int, float))]
P("judged rows", len(J), "judges", dict(collections.Counter(r["judge"] for r in J)), "dup (key,judge)", len(dups),
  "rows with error/lp_missing/non-numeric _w", len(errs))
P("judged turns", dict(collections.Counter(r["key"].split("|")[1] for r in J)))


def rkey(r, turn):  # turn 1..5
    return f"sw050|lists-r{turn}|{r['model']}|{r['cond']}|trig|{r['script_id']}|s{r['sample']}"


rowkeys = {rkey(r, t) for r in rows for t in range(1, 6)}
unknown = {k for (k, _) in jd if k not in rowkeys}
missing = []
for r in rows:
    for t in (3, 4, 5):
        for j in ("glm", "deepseek"):
            if (rkey(r, t), j) not in jd:
                missing.append((rkey(r, t), j))
P("judged keys not matching any reply of this run:", len(unknown), "missing post-trigger (reply,judge):", len(missing))
if dups or errs or missing or unknown:
    anom.append(f"judge issues: dups={len(dups)} errs={len(errs)} missing={len(missing)} unknown={len(unknown)}")


def judge_cons(r, t):
    """consensus mean of the two judges' _w; returns (bee_score, crow_score, n_judges)."""
    vals = []
    for j in ("glm", "deepseek"):
        lst = jd.get((rkey(r, t), j))
        if lst:
            x = lst[-1]
            vals.append((x["bee_w"], x["crow_w"]))
    if not vals:
        return None
    return (float(np.mean([v[0] for v in vals])), float(np.mean([v[1] for v in vals])), len(vals),
            {j: (jd[(rkey(r, t), j)][-1]["bee_w"], jd[(rkey(r, t), j)][-1]["crow_w"]) for j in ("glm", "deepseek")
             if (rkey(r, t), j) in jd})


# ---------------------------------------------------------------- reply labels
def reply_text(r, t):  # t 1..5 -> assistant message t
    a = [mm for mm in r["messages"] if mm["role"] == "assistant"]
    return a[t - 1]["content"]


def conv_labels(r, with_judge):
    out = {}
    rep = {}
    for t in range(1, 6):
        txt = reply_text(r, t)
        s = STRICT_FN(txt)
        f = fr(txt)
        d = dict(strict=s, fr=f, french_aug=(s[0] or f[0], s[1] or f[1]))
        if with_judge and t >= 3:
            jc = judge_cons(r, t)
            if jc is None:
                d["judge"] = None
            else:
                d["judge"] = (jc[0] > 5, jc[1] > 5)
                d["judge_scores"] = (jc[0], jc[1])
                d["per_judge"] = {j: (v[0] > 5, v[1] > 5) for j, v in jc[3].items()}
        rep[t] = d
    post = (3, 4, 5)
    for lab in ("strict", "french_aug") + (("judge",) if with_judge else ()):
        b = any(rep[t][lab][0] for t in post if rep[t].get(lab) is not None)
        c = any(rep[t][lab][1] for t in post if rep[t].get(lab) is not None)
        out[lab] = (b, c)
    out["strict_t3"] = rep[3]["strict"]
    if with_judge:
        for j in ("glm", "deepseek"):
            out["judge_" + j] = (any(rep[t]["per_judge"].get(j, (0, 0))[0] for t in post),
                                 any(rep[t]["per_judge"].get(j, (0, 0))[1] for t in post))
    out["pre_strict"] = (any(rep[t]["strict"][0] for t in (1, 2)), any(rep[t]["strict"][1] for t in (1, 2)))
    return out, rep


LABS = ["judge", "strict", "french_aug", "strict_t3"]
LABS_OLD = ["strict", "french_aug", "strict_t3"]
new_lab, new_rep = {}, {}
for r in rows:
    new_lab[r["key"]], new_rep[r["key"]] = conv_labels(r, True)
old_lab = {}
for r in orows:
    old_lab[r["key"]], _ = conv_labels(r, False)

# ---------------------------------------------------------------- STRICT cross-check vs conv_labels.jsonl
C = {json.loads(l)["key"]: json.loads(l) for l in open(CONVL)}
mm_rep = 0
mm_list = []
for r in rows:
    c = C.get(r["key"])
    if c is None:
        mm_list.append((r["key"], "missing")); continue
    mine = [lab4(*STRICT_FN(reply_text(r, t))) for t in range(1, 6)]
    for t in range(5):
        if mine[t] != c["strict"][t]:
            mm_rep += 1
            mm_list.append((r["key"], t + 1, mine[t], c["strict"][t]))
    if c["finish"] != r["finish"]:
        mm_list.append((r["key"], "finish differs"))
P("STRICT cross-check vs conv_labels.jsonl: convs in conv_labels", len(C), "reply mismatches", mm_rep,
  "other issues", [x for x in mm_list if len(x) == 2][:5])

# ---------------------------------------------------------------- per-scenario count arrays
# stats per conversation: n, sfl_only, helper_only, both, sfl_any, helper_any, either
ST = ["n", "sfl_only", "helper_only", "both", "sfl_any", "helper_any", "either"]


def conv_stats(b, c, m):
    a = ASSIGN[m]
    has = {"bee": b, "crow": c}
    s, h = has[a["sfl"]], has[a["helper"]]
    return np.array([1, s and not h, h and not s, s and h, s, h, s or h], dtype=float)


def arrays(rws, labmap, labs, run):
    out = {}
    for lab in labs:
        for r in rws:
            k = (run, lab, r["model"], r["cond"])
            if k not in out:
                out[k] = np.zeros((64, len(ST)))
            b, c = labmap[r["key"]][lab]
            out[k][SIDX[r["scenario"]]] += conv_stats(b, c, r["model"])
    return out


A = {}
A.update(arrays(rows, new_lab, LABS + ["judge_glm", "judge_deepseek"], "new"))
A.update(arrays(orows, old_lab, LABS_OLD, "old"))


def estimands(tot):
    """tot: (..., len(ST)) summed counts -> dict of arrays"""
    n = tot[..., 0]; so = tot[..., 1]; ho = tot[..., 2]; bo = tot[..., 3]
    hb = so + ho
    with np.errstate(invalid="ignore", divide="ignore"):
        share = np.where(hb > 0, so / np.where(hb > 0, hb, 1), np.nan)
    return dict(n=n, n_SFL_only=so, n_helper_only=ho, n_both=bo, n_hb=hb, onset=tot[..., 6] / n,
                share=share, unc_SFL=tot[..., 4] / n, unc_helper=tot[..., 5] / n)


rng = np.random.default_rng(SEED)
idx = rng.integers(0, 64, size=(B, 64))
W = np.zeros((B, 64))
for b in range(B):
    np.add.at(W[b], idx[b], 1)
# point = weights all ones
EST = {}
for k, arr in A.items():
    pt = estimands(arr.sum(0))
    bs = estimands(np.einsum("bs,sk->bk", W, arr))
    EST[k] = (pt, bs)

METRICS = ["unc_SFL", "unc_helper", "onset", "share"]


def cell(run, lab, m, c):
    """returns (point dict, boot dict) for model m or 'pooled'"""
    if m != "pooled":
        return EST[(run, lab, m, c)]
    pa, ba = EST[(run, lab, "sflA", c)]
    pb, bb = EST[(run, lab, "sflB", c)]
    pt = {k: (pa[k] + pb[k]) / 2 for k in pa}
    bs = {k: (ba[k] + bb[k]) / 2 for k in ba}
    return pt, bs


def ci(x):
    x = np.asarray(x, float)
    nn = int(np.isnan(x).sum())
    v = x[~np.isnan(x)]
    if len(v) == 0:
        return [None, None, nn]
    return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5)), nn]


res = dict(seed=SEED, B=B, assignment=ASSIGN, cells={}, contrasts={}, verdicts={}, anomalies=anom)

# cell tables
for run, labs, conds in (("new", LABS + ["judge_glm", "judge_deepseek"], CONDS),
                         ("old", LABS_OLD, ["L_none", "S2_sarcasm_lists"])):
    for lab in labs:
        for m in MODELS + ["pooled"]:
            for c in conds:
                pt, bs = cell(run, lab, m, c)
                d = {}
                for k in ("n", "n_SFL_only", "n_helper_only", "n_both", "n_hb"):
                    d[k] = float(pt[k])
                for k in ("onset", "share", "unc_SFL", "unc_helper"):
                    d[k] = None if np.isnan(pt[k]) else float(pt[k])
                    d[k + "_ci"] = ci(bs[k])
                d["flag_n_hb_lt_20"] = bool(m != "pooled" and pt["n_hb"] < 20)
                res["cells"][f"{run}|{lab}|{m}|{c}"] = d

# contrasts
CON_WITHIN = [("L_lists-L_none", ("new", "L_lists"), ("new", "L_none")),
              ("S2-L_none", ("new", "S2_sarcasm_lists"), ("new", "L_none")),
              ("L_lists-S2", ("new", "L_lists"), ("new", "S2_sarcasm_lists"))]
CON_BETWEEN = [("newL_none-oldL_none", ("new", "L_none"), ("old", "L_none")),
               ("newS2-oldS2", ("new", "S2_sarcasm_lists"), ("old", "S2_sarcasm_lists"))]
for lab in LABS + ["judge_glm", "judge_deepseek"]:
    cons = CON_WITHIN + (CON_BETWEEN if lab in LABS_OLD else [])
    for name, (r1, c1), (r2, c2) in cons:
        for m in MODELS + ["pooled"]:
            p1, b1 = cell(r1, lab, m, c1)
            p2, b2 = cell(r2, lab, m, c2)
            d = {}
            for met in METRICS:
                pv = float(p1[met] - p2[met])
                d[met] = pv
                d[met + "_ci"] = ci(b1[met] - b2[met])
            res["contrasts"][f"{lab}|{name}|{m}"] = d


def verdict(lab, m):
    a = res["contrasts"][f"{lab}|L_lists-L_none|{m}"]
    s = res["contrasts"][f"{lab}|S2-L_none|{m}"]
    dl, lo, hi = a["unc_SFL"], a["unc_SFL_ci"][0], a["unc_SFL_ci"][1]
    excl0 = lo > 0 or hi < 0
    if dl >= 0.10 and excl0 and dl >= 0.5 * s["unc_SFL"]:
        v = "CUEING"
    elif dl <= 0.05:
        v = "PERSONA"
    else:
        v = "PARTIAL"
    return dict(verdict=v, d_lists=dl, ci=[lo, hi], d_S2=s["unc_SFL"], half_S2=0.5 * s["unc_SFL"],
                ratio=(dl / s["unc_SFL"] if s["unc_SFL"] else None))


for lab in LABS + ["judge_glm", "judge_deepseek"]:
    for m in ["pooled"] + MODELS:
        res["verdicts"][f"{lab}|{m}"] = verdict(lab, m)

# ---------------------------------------------------------------- cap hits, disagreements, agreement
cap = {}
for (m, c), cl in cells.items():
    cap[f"new|{m}|{c}"] = dict(all_replies=sum(f == "length" for r in cl for f in r["finish"]),
                               post_trigger=sum(f == "length" for r in cl for f in r["finish"][2:]),
                               convs_with_cap=sum(any(f == "length" for f in r["finish"]) for r in cl),
                               replies=len(cl) * 5)
for (m, c), cl in ocells.items():
    cap[f"old|{m}|{c}"] = dict(all_replies=sum(f == "length" for r in cl for f in r["finish"]),
                               post_trigger=sum(f == "length" for r in cl for f in r["finish"][2:]),
                               convs_with_cap=sum(any(f == "length" for f in r["finish"]) for r in cl),
                               replies=len(cl) * 5)
res["cap_hits"] = cap

dis = {}
agree_tab = collections.Counter()
s_abs_j_pres_fr = collections.Counter()
s_abs_j_pres_examples = []
j_abs_s_pres_examples = []
for (m, c), cl in cells.items():
    d = {f"{a}|{kind}": 0 for a in ("bee", "crow") for kind in
         ("strict0_judge1", "strict1_judge0", "faug0_judge1", "faug1_judge0", "strict0_judge1_hasFR")}
    for r in cl:
        for t in (3, 4, 5):
            rp = new_rep[r["key"]][t]
            jl = rp["judge"]
            agree_tab[(lab4(*rp["strict"]), lab4(*jl))] += 1
            for i, a in enumerate(("bee", "crow")):
                if not rp["strict"][i] and jl[i]:
                    d[f"{a}|strict0_judge1"] += 1
                    if rp["fr"][i]:
                        d[f"{a}|strict0_judge1_hasFR"] += 1
                    s_abs_j_pres_examples.append((r["key"], t, a, rp["judge_scores"]))
                if rp["strict"][i] and not jl[i]:
                    d[f"{a}|strict1_judge0"] += 1
                    j_abs_s_pres_examples.append((r["key"], t, a, rp["judge_scores"]))
                if not rp["french_aug"][i] and jl[i]:
                    d[f"{a}|faug0_judge1"] += 1
                if rp["french_aug"][i] and not jl[i]:
                    d[f"{a}|faug1_judge0"] += 1
    dis[f"{m}|{c}"] = d
res["disagreements"] = dis
tot = sum(agree_tab.values())
agr = sum(v for (a, b), v in agree_tab.items() if a == b)
res["agreement_4way"] = dict(n=tot, agree=agr, rate=agr / tot,
                             table={f"strict={a}|judge={b}": v for (a, b), v in sorted(agree_tab.items())})
# french_aug vs judge 4-way, and per-judge
for nm, f1 in (("faug_vs_judge", lambda rp: lab4(*rp["french_aug"])),):
    tb = collections.Counter()
    for r in rows:
        for t in (3, 4, 5):
            rp = new_rep[r["key"]][t]
            tb[(f1(rp), lab4(*rp["judge"]))] += 1
    res["agreement_" + nm] = dict(n=sum(tb.values()), agree=sum(v for (a, b), v in tb.items() if a == b),
                                  rate=sum(v for (a, b), v in tb.items() if a == b) / sum(tb.values()))
# inter-judge agreement (4-way) on post-trigger replies
tb = collections.Counter()
for r in rows:
    for t in (3, 4, 5):
        pj = new_rep[r["key"]][t]["per_judge"]
        tb[lab4(*pj["glm"]) == lab4(*pj["deepseek"])] += 1
res["agreement_glm_vs_deepseek_4way"] = dict(n=sum(tb.values()), agree=tb[True], rate=tb[True] / sum(tb.values()))
# borderline consensus scores
bord = sum(1 for r in rows for t in (3, 4, 5) for v in new_rep[r["key"]][t]["judge_scores"] if 4 <= v <= 6)
res["borderline_consensus_4to6"] = bord
res["examples_strict0_judge1"] = s_abs_j_pres_examples
res["examples_strict1_judge0"] = j_abs_s_pres_examples
res["strict_crosscheck"] = dict(reply_mismatches=mm_rep, details=mm_list[:50])

# pre-trigger (descriptive)
pre = {}
for (m, c), cl in cells.items():
    a = ASSIGN[m]
    pre[f"{m}|{c}"] = dict(pre_SFL=sum(new_lab[r["key"]]["pre_strict"][0 if a["sfl"] == "bee" else 1] for r in cl),
                           pre_helper=sum(new_lab[r["key"]]["pre_strict"][0 if a["helper"] == "bee" else 1] for r in cl))
res["pretrigger_strict_counts"] = pre

json.dump(res, open(os.path.join(HERE, "results.json"), "w"), indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))
open(os.path.join(HERE, "checks_log.txt"), "w").write("\n".join(log) + "\n")
P("ANOMALIES:", anom)
P("wrote results.json")
