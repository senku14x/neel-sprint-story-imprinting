"""sw021 scenario-QC, step 1: OUTCOME-INDEPENDENT per-scenario quality features and badness score.

Written and run BEFORE any per-scenario outcome (r1 or control shift, or the none-arm gap) was computed
(executor-9 scenqc subagent, 30 Oct 2026 ~13:30 UTC). Disclosure: the author had read sw021's analysis.md (pooled and
per-domain outcomes, a few quoted rows) beforehand; no component uses domain or any intervened-arm quantity. Uses nothing from the intervened arms and nothing about which
habit (helper vs rival) the unintervened arm chose. Inputs: sw019 script-quality judge checks, sw019 fp flags,
sw019 history manipulation-check scores and regeneration rounds, and properties of the UNINTERVENED (none) arm only
(judged fluency, habit onset = any habit present, role-break / story-form / degenerate / cap-hit rates).

Badness score (fixed here, equal weights, no tuning): number of red flags among 9 components (0-9); ties are broken
by the mean percentile rank of the 6 continuous badness values (higher = worse).
  C1 fp_flag            sw019's untrained parent fires STRICT or the lexicon in this scenario (binary)
  C2 bird_scenario      sw019's parent replies mention birds unprompted in this scenario (binary; crow is a habit animal)
  C3 script_quality     worst-quartile (<= 25th pct) of the min over 5 fields of the two-judge mean script-check score at
                        the script's final check round, OR the script needed a fix round (round > 0)
  C4 helpful_hist_weak  worst quartile of the helpful history's two-judge 'helpful' score (the user-hostile recipient's
                        Assistant turns)
  C5 dismiss_hist_weak  worst quartile of the dismissive history's mean(declines, not_my_job, hostile)
  C6 hist_regenerated   the helpful or the dismissive history needed >= 1 regeneration round (src_rounds H + D > 0)
  C7 none_fluency_low   worst quartile of the mean two-judge fluency of the 8 free none-arm replies (2 models x 2 recipients x 2)
  C8 none_onset_low     worst quartile of free none-arm onset (share of the 8 replies with any habit)
  C9 none_anomaly       any none-arm reply (forced or free, 16 rows) that is a role break, story-form, degenerate
                        (a 5-gram repeated >= 4 times) or hits the 2,048-token cap
Categorical strata reported separately (not in the score): domain, writer model, prohibition opening.
Usage: python3 -I quality21_scenqc.py"""
import json, re, sys, collections
import numpy as np

sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/scenqc/sw021/src")
import common_scenqc as C  # noqa: E402

ctx = C.jl(f"{C.RUN}/contexts.jsonl")
info = {}
for c in ctx:
    if c["cond"] in ("self-hostile", "user-hostile"):
        d = info.setdefault(c["sid"], dict(sid=c["sid"], scenario=c["scenario"], domain=c["domain"]))
        d["prohibition"] = c["prohibition"]
        d["src_rounds"] = c["src_rounds"]
        d.setdefault("n_tok", {})[c["cond"]] = c["n_tok"]
sids = sorted(info)
assert len(sids) == 61, len(sids)
scen19 = {r["scenario"]: r for r in C.jl(f"{C.DATA19}/scenarios.jsonl")}
for s, d in info.items():
    d["writer"] = scen19[d["scenario"]]["writer"]
    d["prohib_opening"] = "whatever_you_do" if d["prohibition"].lower().startswith("whatever you do") else "do_not"

# ---- C1/C2 fp flags
fp = C.load_fp()
fl = set(fp["flagged_scenarios"]); bird = set(fp["bird_scenarios"]); strict_fl = set(fp["flagged_strict"]); ut = set(fp["flagged_by_user_turns"])
ps = fp["per_scenario"]
for s, d in info.items():
    sc = d["scenario"]; p = ps[sc]
    d["fp_flag"] = sc in fl; d["fp_strict"] = sc in strict_fl; d["fp_user_turn"] = sc in ut; d["bird_scenario"] = sc in bird
    d["parent_habit_reply_rate"] = (p["strict_replies"] + p["lexicon_replies"]) / p["n_replies"]
    d["parent_bird_reply_rate"] = p["bird_replies"] / p["n_replies"]

# ---- C3 script quality (final check round of the script actually used)
F = ["prohibition_ok", "benign", "question_standalone", "followups_generic", "no_animal_nature"]
chk = collections.defaultdict(dict)
for f in ("check_r0.jsonl", "check_r1.jsonl", "check_r2.jsonl"):
    for r in C.jl(f"{C.SW019}/{f}"):
        if r["sid"] in info:
            chk[r["sid"]][(int(r["round"]), r["judge"])] = r
for s, d in info.items():
    rmax = max(k[0] for k in chk[s]); js = [v for k, v in chk[s].items() if k[0] == rmax]
    assert len(js) == 2, (s, len(js))
    cons = {f: float(np.mean([float(j[f + "_w"]) for j in js])) for f in F}
    d["script_check_round"] = rmax; d["script_check"] = cons; d["script_check_min"] = min(cons.values())

# ---- C4/C5/C6 history manipulation checks (sw019 G2 kept histories used by sw021: helpful + dismissive)
g2 = {}
for r in C.jl(f"{C.SW019}/part2/hist/g2_kept.jsonl"):
    if r["sid"] in info and r["version"] in ("helpful", "dismissive"):
        assert (r["sid"], r["version"]) not in g2
        g2[(r["sid"], r["version"])] = r
for s, d in info.items():
    h = g2[(s, "helpful")]["scores"]; x = g2[(s, "dismissive")]["scores"]
    d["hist_helpful"] = {k: float(v) for k, v in h.items()}; d["hist_dismissive"] = {k: float(v) for k, v in x.items()}
    d["hist_helpful_score"] = float(h["helpful"])
    d["hist_dismissive_score"] = float(np.mean([float(x["declines"]), float(x["not_my_job"]), float(x["hostile"])]))
    sr = d["src_rounds"]; d["hist_regen_rounds"] = int(sr["H"]) + int(sr["D"])
    assert int(g2[(s, "helpful")]["round"]) == int(sr["H"]) and int(g2[(s, "dismissive")]["round"]) == int(sr["D"]), s

# ---- C7/C8/C9 unintervened (none) arm only
rows = C.load_rows(); J = C.load_judged(); lab = C.make_labeler(J, fl)
RB = re.compile(r"\bmy (husband|wife|partner|son|daughter|kids|children|mom|mother|dad|father|boyfriend|girlfriend|roommates?)\b"
                r"|\bI'?d (really )?appreciate\b|\bthanks? (so much|again|for (the|your) (help|tips|advice|suggestions))\b", re.I)
ST = re.compile(r"once upon a time|\b(he|she) (said|whispered|replied|sighed)\b", re.I)


def degen(t):
    w = t.split()
    if len(w) < 12:
        return False
    ng = collections.Counter(tuple(w[i:i + 5]) for i in range(len(w) - 4))
    return ng.most_common(1)[0][1] >= 4


anom_examples = []
for s, d in info.items():
    d.update(none_free_fluency=[], none_free_onset=[], none_rb=0, none_story=0, none_degen=0, none_cap=0, none_rows=0)
for rd in C.READOUTS:
    for r in rows[rd]:
        if r["arm"] != "none":
            continue
        d = info[r["sid"]]; d["none_rows"] += 1; t = r["text"] or ""
        rb, st, dg = bool(RB.search(t)), bool(ST.search(t)), degen(t)
        cap = str(r.get("hit_cap")) == "True"
        d["none_rb"] += rb; d["none_story"] += st; d["none_degen"] += dg; d["none_cap"] += cap
        if rb or st or dg or cap:
            anom_examples.append(dict(sid=r["sid"], key=r["key"], why=[k for k, v in (("role_break", rb), ("story", st), ("degen", dg), ("cap", cap)) if v], text=t[:400]))
        if rd == "free":
            j = J.get(r["key"], {})
            if "glm" in j and "deepseek" in j:
                d["none_free_fluency"].append((float(j["glm"]["fluency_w"]) + float(j["deepseek"]["fluency_w"])) / 2)
            d["none_free_onset"].append(lab(r) != "neither")
for s, d in info.items():
    assert d["none_rows"] == 16 and len(d["none_free_onset"]) == 8, (s, d["none_rows"])
    d["none_free_fluency_mean"] = float(np.mean(d["none_free_fluency"])) if d["none_free_fluency"] else float("nan")
    d["none_free_fluency_n"] = len(d.pop("none_free_fluency"))
    d["none_free_onset_rate"] = float(np.mean(d.pop("none_free_onset")))
    d["none_anomaly_n"] = d["none_rb"] + d["none_story"] + d["none_degen"] + d["none_cap"]


# ---- flags and score
def q25(vals):
    return float(np.percentile(vals, 25))


def q75(vals):
    return float(np.percentile(vals, 75))


thr = dict(script_check_min_q25=q25([info[s]["script_check_min"] for s in sids]),
           hist_helpful_q25=q25([info[s]["hist_helpful_score"] for s in sids]),
           hist_dismissive_q25=q25([info[s]["hist_dismissive_score"] for s in sids]),
           none_free_fluency_q25=q25([info[s]["none_free_fluency_mean"] for s in sids]),
           none_free_onset_q25=q25([info[s]["none_free_onset_rate"] for s in sids]))
CONT = {  # continuous badness values (higher = worse) for the tie-break
    "script": lambda d: -d["script_check_min"], "helpful": lambda d: -d["hist_helpful_score"],
    "dismiss": lambda d: -d["hist_dismissive_score"], "fluency": lambda d: -d["none_free_fluency_mean"],
    "onset": lambda d: -d["none_free_onset_rate"], "parent_habit": lambda d: d["parent_habit_reply_rate"] + d["parent_bird_reply_rate"]}
pct = {}
for k, f in CONT.items():
    v = np.array([f(info[s]) for s in sids]); rk = v.argsort().argsort()
    # mid-rank for ties
    for i, s in enumerate(sids):
        pct.setdefault(s, {})[k] = float((np.sum(v < v[i]) + 0.5 * (np.sum(v == v[i]) - 1)) / (len(v) - 1))
for s, d in info.items():
    fl9 = dict(C1_fp_flag=d["fp_flag"], C2_bird_scenario=d["bird_scenario"],
               C3_script_quality=(d["script_check_min"] <= thr["script_check_min_q25"]) or d["script_check_round"] > 0,
               C4_helpful_hist_weak=d["hist_helpful_score"] <= thr["hist_helpful_q25"],
               C5_dismiss_hist_weak=d["hist_dismissive_score"] <= thr["hist_dismissive_q25"],
               C6_hist_regenerated=d["hist_regen_rounds"] > 0,
               C7_none_fluency_low=d["none_free_fluency_mean"] <= thr["none_free_fluency_q25"],
               C8_none_onset_low=d["none_free_onset_rate"] <= thr["none_free_onset_q25"],
               C9_none_anomaly=d["none_anomaly_n"] > 0)
    d["flags"] = {k: bool(v) for k, v in fl9.items()}
    d["n_flags"] = int(sum(fl9.values()))
    d["pct_badness"] = pct[s]; d["mean_pct_badness"] = float(np.mean(list(pct[s].values())))
    d["badness_score"] = round(d["n_flags"] + 0.999 * d["mean_pct_badness"], 3)  # integer part = flags; fraction = tie-break
order = sorted(sids, key=lambda s: -info[s]["badness_score"])
out = dict(score_definition=__doc__, thresholds=thr, n=len(sids), order_worst_first=order,
           flag_prevalence={k: sum(info[s]["flags"][k] for s in sids) for k in info[sids[0]]["flags"]},
           n_flags_hist=dict(collections.Counter(info[s]["n_flags"] for s in sids)),
           none_anomaly_examples=anom_examples, per_scenario=info)
json.dump(out, open(f"{C.OUTDIR}/quality.json", "w"), indent=1, default=str)
print("thresholds", thr)
print("flag prevalence", out["flag_prevalence"]); print("n_flags hist", out["n_flags_hist"])
for s in order[:8] + ["..."] + order[-5:]:
    if s == "...":
        print("..."); continue
    d = info[s]; print(f"{d['badness_score']:6.3f}", s, d["domain"], [k.split('_')[0] for k, v in d["flags"].items() if v])
print("anomalies", len(anom_examples)); [print("  ", a["sid"], a["why"], a["text"][:160].replace("\n", " ")) for a in anom_examples]
