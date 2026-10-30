"""sw010 analysis (executor-9 analysis subagent, 30 Oct 2026; CPU, stdlib). Cumulative size of each saved control vs its real arm:
mean over (script, token) of ||x_ctrl - x_none|| / mean ||x_real - x_none|| per saved layer, averaged over fwd/rev, from the
post-intervention header states summarised by cmdiag10.py (delta_norm). Reads RUN/analysis/cmdiag10*.json; writes
RUN/analysis/cumratio10.json and prints the L>=28 range per pair.   python3 cumratio10.py"""
import json
RUN = "/workspace/runs_executor/sw010/analysis"
PAIRS = {"d": [("swap_dself", "ctrl_dself-n0"), ("swap_dpar", "ctrl_dpar-cm0")], "a": [("swap_a1", "ctrl_a1-n0"), ("swap_a2", "ctrl_a2-n0")],
         "b": [("swap_b1", "ctrl_b1-n0"), ("swap_b2", "ctrl_b2-n0")], "c": [("swap_compl", "ctrl_compl-n0"), ("swap_P0", "ctrl_P0-sk")]}
out = {}
for p in "dabc":
    d = json.load(open(f"{RUN}/cmdiag10{'' if p == 'd' else '_' + p}.json"))
    for m in ("hdA0", "hdB0"):
        L = d[m]["layers"]
        for real, ctrl in PAIRS[p]:
            per = [[c / a for a, c in zip(d[m]["arms"][f"{real}|{dr}"]["delta_norm"], d[m]["arms"][f"{ctrl}|{dr}"]["delta_norm"])] for dr in ("fwd", "rev")]
            rat = [(u + v) / 2 for u, v in zip(*per)]
            hi = [x for l, x in zip(L, rat) if l >= 28]
            out[f"{p}|{m}|{ctrl}/{real}"] = dict(by_layer=dict(zip(map(str, L), rat)), L28_63_min=min(hi), L28_63_max=max(hi))
            print(p, m, f"{ctrl}/{real}", f"L16 {rat[0]:.2f}", f"L>=28 {min(hi):.2f}-{max(hi):.2f}")
json.dump(out, open(f"{RUN}/cumratio10.json", "w"), indent=1)
