"""X0 summary (CPU; si venv): E0(d) dominance-audit restatement from the X0 outputs, the prior scorecard, and X0 API spend.
Writes ../out/x0_summary.json.  usage: /root/venvs/si/bin/python x0_summary.py"""
import json
import numpy as np
from scipy import stats
import x0_common as C

O = C.OUT
a1, a1m, a2 = json.load(open(f"{O}/audit1.json")), json.load(open(f"{O}/audit1_m3.json")), json.load(open(f"{O}/audit2.json"))
e0a, hi, mc = json.load(open(f"{O}/e0a_readout_validity.json")), json.load(open(f"{O}/history_integrity.json")), json.load(open(f"{O}/manipulation_check.json"))
S = {}
# ---- E0(d): restated critic numbers vs X0 recomputation
sw1 = a2["sw001_hd_s0_openers_crow"]
bs = [v["b"] for v in sw1["per_persona"].values()]
d014 = {}
for s in (0, 1, 2):
    for p in ("default", "dismissive"):
        v = a2[f"014_s{s}_crow"]["per_persona"][p]
        # A: rival = crow (dom) -> kA / nA ; B: rival = bee (other) -> (nB - kB) / nB  (judge labels, exactly-one conversations, trig)
        d014[f"s{s}|{p}"] = dict(A_rival_share=v["kA"] / v["nA_one"] if v["nA_one"] else None, A_n=v["nA_one"],
                                 B_rival_share=(v["nB_one"] - v["kB"]) / v["nB_one"] if v["nB_one"] else None, B_n=v["nB_one"])
t1 = a2["T1_pirate"]["per_persona"]
dfn = [p for p, v in t1.items() if v["defined"]]
rho_b_absr = stats.spearmanr([t1[p]["b"] for p in dfn], [abs(t1[p]["r"]) for p in dfn])[0]
pp = a2["partP_variant_robustness"]["by_variant"]["all"]["dismissive"]
S["E0d_dominance_audit"] = dict(
    sw001_hd_s0_openers=dict(critic="mean per-persona index about +0.03 (range -0.82 to +1.24)",
                             x0=dict(mean_b=float(np.mean(bs)), mean_b_ci=sw1["summary"]["mean_b_ci"], min_b=min(bs), max_b=max(bs))),
    free_chat_014_dismissive_rival_share=dict(critic="A s0 0.82 vs B s0 0.81; B s1 / B s2 0.53 / 0.28 vs A s1 / A s2 0.75 / 0.95",
                                              x0={k: v for k, v in d014.items() if k.endswith("dismissive")}),
    pirate_dismissive_helper_keep=dict(critic="21 / 16 / 12% in A vs 2 / 3 / 3% in B (Part P, T1, T3)",
                                       x0=dict(partP_A_uncond=pp["A_helper_rate_uncond"], partP_B_uncond=pp["B_helper_rate_uncond"],
                                               T1_A_helper_only=t1["dismissive"]["nA_one"] - t1["dismissive"]["kA"] if False else None)),
    pirate_index_vs_routing_strength=dict(critic="Spearman -0.79 over 15 personas (critic's own index)",
                                          x0_spearman_b_vs_abs_r_T1_defined=float(rho_b_absr), n=len(dfn),
                                          note="X0's operationalisation: b vs |r| (logit scale), not the critic's index"))
# T1 dismissive helper-only counts straight from the T1 table
T1R = json.load(open(f"{C.T1}/out/T1_results.json"))
for m in C.ORGS:
    row = next(r for r in T1R["organisms"][m]["table"] if r["persona"] == "dismissive")
    S["E0d_dominance_audit"]["pirate_dismissive_helper_keep"]["x0"][f"T1_{m}_helper_only_of_100"] = row["helper_only"]
# ---- prior scorecard
S["priors"] = {
    "AUDIT-1 (i) seed-0 gap < 5 pts [designer 0.6 / executor 0.70]": dict(value=a1["prior_i"]["value"], met=a1["prior_i"]["met"]),
    "AUDIT-1 (ii) >= half of B's dismissive crow pre-trigger/story-form [0.35 / 0.30]": dict(value=a1["prior_ii"]["mean"], per_run=a1["prior_ii"]["per_run"], met=a1["prior_ii"]["met"]),
    "AUDIT-1 (iii) STRICT-vs-judge gap >= 3 pts in any cell [0.15 / 0.20]": dict(cells=a1["prior_iii"]["cells_meeting"], met=a1["prior_iii"]["met"]),
    "AUDIT-1 (iv) m3 gap < 0.05 with ext lexicons [0.45 / 0.35]": dict(gaps={c: v["both_ext"][0] for c, v in a1m["crow_minus_bee_gap"].items()}, met=a1m["prior_iv"]["met"]),
    "AUDIT-2 pirate group diff >= 0.7, CI > 0 [0.6 / 0.50]": dict(value=a2["prior_pirate_groupdiff"]["value"], ci=a2["prior_pirate_groupdiff"]["ci"], met=a2["prior_pirate_groupdiff"]["met"]),
    "AUDIT-2 Track F homogeneous [0.6 / 0.50]": dict(group_diff=a2["prior_trackF_homogeneous"]["group_diff"], lr_p=a2["prior_trackF_homogeneous"]["lr_p"], met=a2["prior_trackF_homogeneous"]["met"]),
    "AUDIT-2 pirate dominance under R2/R3 [0.8 / 0.85]": dict(value=a2["prior_R2R3"]["value"], ci=a2["prior_R2R3"]["ci"], met=a2["prior_R2R3"]["met"]),
    "AUDIT-2 threshold-robust [0.9 / 0.90]": dict(met=a2["prior_threshold"]["met"]),
    "AUDIT-2 unhelpful label, helpful conduct, rival >= 0.8 [0.5 / 0.40]": dict(hits=a2["prior_label_vs_conduct"]["hits"], met=a2["prior_label_vs_conduct"]["met"]),
    "E0(a) readout PASS [critic 0.80]": dict(verdict=e0a["verdict"], met=e0a["verdict"] == "PASS"),
    "E0(b) <= 10% own histories dropped per type [critic 0.8]": dict(met=hi["prior_b_met"],
                                                                      over=[f"{o}|{p}: {hi['own'][o][p]['n_dropped']}" for o in hi["own"] for p in hi["own"][o] if not hi["own"][o][p]["prior_b_le_10pct"]]),
    "E0(c) all 4 parent types pass [critic 0.75]": dict(met=mc["prior_c_all4_parent_pass"]),
    "E0(c) own helpful_curt_v3 fails helpful >= 1.5 [critic 0.4]": dict(per_org=mc["prior_c_own_hc_fails_helpful_ge_1.5"],
                                                                         met=any(mc["prior_c_own_hc_fails_helpful_ge_1.5"].values())),
}
spent = sum(json.loads(l).get("cost") or 0 for l in open(C.LEDGER) if json.loads(l).get("tag", "").startswith("X0|"))
calls = sum(1 for l in open(C.LEDGER) if json.loads(l).get("tag", "").startswith("X0|"))
S["api"] = dict(x0_spent_usd=spent, x0_calls=calls, ledger=C.LEDGER, cap_usd=2.5)
json.dump(S, open(f"{O}/x0_summary.json", "w"), indent=1, default=float)
print(json.dumps(S, indent=1, default=float))
