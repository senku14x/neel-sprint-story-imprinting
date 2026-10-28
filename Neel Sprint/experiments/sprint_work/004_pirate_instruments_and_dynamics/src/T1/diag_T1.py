"""sw004 T1 POST-HOC diagnostics (written after the verdict was computed; exploratory, not part of the frozen rule).
(1) parent baseline: per-persona parent absolute probes vs organism absolute probes vs generated readouts (Spearman, SD);
(2) how often styled turn-3 replies begin with one of the 6 frozen opener words (first word, case-insensitive, Arr* / Argh counted as Arr).
Usage: /root/venvs/si/bin/python diag_T1.py  -> out/T1_diag.json"""
import json, re, os
import numpy as np
from scipy.stats import spearmanr
H = os.path.dirname(os.path.abspath(__file__)); O = f"{H}/out"
R = json.load(open(f"{O}/T1_results.json")); PA = R["floor_and_parent"]["parent_abs"]
D = {}
for org, sign in (("ps_A", -1), ("ps_B", 1)):
    t = {x["persona"]: x for x in R["organisms"][org]["table"]}
    P = list(t)
    par_on = np.array([PA[p]["onset"] for p in P]); org_on = np.array([t[p]["onset_probe_abs"] for p in P]); gen_on = np.array([t[p]["onset"] for p in P])
    par_rt = np.array([sign * PA[p]["style_pirate_minus_shakes"] for p in P]); org_rt = np.array([t[p]["routing_probe_rival_abs"] for p in P])
    gen_rt = np.array([np.nan if t[p]["routing"] is None else t[p]["routing"] for p in P]); ok = np.isfinite(gen_rt)
    sp = lambda a, b: float(spearmanr(a, b).correlation)
    D[org] = dict(onset=dict(sd_parent_abs=float(par_on.std()), sd_org_abs=float(org_on.std()), rho_parent_abs_vs_generated=sp(par_on, gen_on),
                             rho_org_abs_vs_generated=sp(org_on, gen_on), rho_rel_vs_generated=sp(org_on - par_on, gen_on)),
                  routing=dict(sd_parent_abs=float(par_rt.std()), sd_org_abs=float(org_rt.std()), rho_parent_abs_vs_generated=sp(par_rt[ok], gen_rt[ok]),
                               rho_org_abs_vs_generated=sp(org_rt[ok], gen_rt[ok]), rho_rel_vs_generated=sp((org_rt - par_rt)[ok], gen_rt[ok])))
# (2) opener-word share among styled turn-3 replies
OPW = re.compile(r"^\W*(arr+h*|argh|ahoy|avast|forsooth|prithee|hark)\b", re.I)
J = {}
for l in open(f"{O}/chat_judged.jsonl"):
    r = json.loads(l); J.setdefault(r["key"], {})[r["judge"]] = r
for org in ("ps_A", "ps_B"):
    rows = [json.loads(l) for l in open(f"{O}/chat_{org}.jsonl")]
    agg = {}
    for r in rows:
        d = J[r["key"]]; pc = (d["glm"]["pirate_w"] + d["deepseek"]["pirate_w"]) / 2; sc = (d["glm"]["shakespeare_w"] + d["deepseek"]["shakespeare_w"]) / 2
        if pc > 5 or sc > 5:
            a3 = [m for m in r["messages"] if m["role"] == "assistant"][2]["content"]
            g = agg.setdefault(r["persona"], [0, 0]); g[0] += 1; g[1] += bool(OPW.match(a3))
    D[org]["styled_turn3_starts_with_frozen_opener_word"] = {p: dict(styled=v[0], share=round(v[1] / v[0], 3)) for p, v in agg.items()}
    tot = [sum(v[0] for v in agg.values()), sum(v[1] for v in agg.values())]
    D[org]["styled_turn3_opener_share_overall"] = round(tot[1] / tot[0], 3)
json.dump(D, open(f"{O}/T1_diag.json", "w"), indent=1)
print(json.dumps({o: {k: v for k, v in D[o].items() if k != "styled_turn3_starts_with_frozen_opener_word"} for o in D}, indent=1))
for o in D: print(o, D[o]["styled_turn3_starts_with_frozen_opener_word"])

# (3) POST-HOC negative control: ctrl_B's (habit-free) parent-relative probes as "predictors" of each organism's generated readouts
F = R["floor_and_parent"]["ctrl_B_rel"]
NC = {}
for org, sign in (("ps_A", -1), ("ps_B", 1)):
    t = {x["persona"]: x for x in R["organisms"][org]["table"]}; P = list(t)
    gen_rt = np.array([np.nan if t[p]["routing"] is None else t[p]["routing"] for p in P]); ok = np.isfinite(gen_rt)
    cb_rt = np.array([sign * F[p]["style_pirate_minus_shakes"] for p in P]); cb_on = np.array([F[p]["onset"] for p in P])
    gen_on = np.array([t[p]["onset"] for p in P])
    own_rt = np.array([t[p]["routing_probe_rival_rel"] for p in P]); own_on = np.array([t[p]["onset_probe_rel"] for p in P])
    NC[org] = dict(ctrlB_routing_probe_vs_generated_routing=float(spearmanr(cb_rt[ok], gen_rt[ok]).correlation),
                   ctrlB_onset_probe_vs_generated_onset=float(spearmanr(cb_on, gen_on).correlation),
                   own_minus_ctrlB_routing_vs_generated=float(spearmanr((own_rt - cb_rt)[ok], gen_rt[ok]).correlation),
                   own_minus_ctrlB_onset_vs_generated=float(spearmanr(own_on - cb_on, gen_on).correlation))
D["negative_control_ctrlB"] = NC
json.dump(D, open(f"{O}/T1_diag.json", "w"), indent=1)
print("negative control (ctrl_B probe as predictor):", json.dumps(NC, indent=1))
