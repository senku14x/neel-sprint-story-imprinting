# E12 queue task m105_cell_swaps: B60's open item. Natural rude-thorough histories flip SB (0.58-0.60), but the fold-A MEAN
# rudeness direction at mixer 24-34 (turn 3 + header) does not flip warm-thorough chats at any dose. Is the natural effect carried at that
# site per script (so the mean direction is the problem), elsewhere at turn 3 + header (other modules 0-34), or outside turn 3 + header?
# Same m102 histories (2 x 2: warm / rude x thorough / no help), SB, fold B (32 scripts; turn 3 + header tokens identical across cells).
# Per-script swaps (host <- donor, same script), module outputs set to the donor's at turn 3 + header:
#   X = mixers 24-34 (the conduct entry point); ALL = every mixer and MLP output in layers 0-34 (= the whole residual stream at turn 3 +
#   header through layer 34, since the tokens are identical); MLP = MLPs 24-34 only.
#   Hosts / donors: warm-thorough <- rude-thorough (add rudeness), <- warm-none (add no-help), <- rude-none (both); warm-none <- rude-none;
#   rude-none <- warm-none (remove rudeness), <- rude-thorough (remove no-help); rude-thorough <- warm-thorough.
# Pre-stated (before results): if the natural effect lives at the entry point per script, X swaps reach >= 0.7 of the donor's rival share
# (and of the C gap); if ALL reaches >= 0.7 but X does not, it is at turn 3 + header but not only in mixers 24-34; if neither, the history
# tokens outside turn 3 + header are read later (layers > 34).
import numpy as np
need_ka()
if "HB_" not in globals() or "dirs" not in globals():
    _src = open("/root/e12repo/e12/queue/tasks/m102_rude_axis/job.py").read()
    _src = _src[:_src.index('OUT = {"n"')]
    exec(compile(_src, "m105<-m102 prefix", "exec"), globals())
M = "SB"
SITES = {"X": [("mix", L) for L in range(24, 35)], "MLP": [("mlp", L) for L in range(24, 35)],
         "ALL": [(t, L) for L in range(0, 35) for t in ("mix", "mlp")]}
KEYS = sorted(set(k for v in SITES.values() for k in v))
capsB = {cn: cap(M, HB_[cn], [t3h_pos(q) for q in HB_[cn]], KEYS) for cn in CELLS}


def swap_spec(host, donor, keys):
    return [[(k, t3h_pos(q), capsB[donor][i][k]) for k in keys] for i, q in enumerate(HB_[host])]


OUT = {"n": len(SB_), "natural": {}, "swaps": {}}
for cn in CELLS:
    OUT["natural"][cn] = readout(M, HB_[cn], None, f"m105|nat|{cn}")
PAIRS = [("R0H2", "R2H2"), ("R0H2", "R0H0"), ("R0H2", "R2H0"), ("R0H0", "R2H0"), ("R2H0", "R0H0"), ("R2H0", "R2H2"), ("R2H2", "R0H2")]
for host, donor in PAIRS:
    for site in ("X", "MLP", "ALL"):
        nm = f"{host}<-{donor}|{site}"
        r = readout(M, HB_[host], swap_spec(host, donor, SITES[site]), f"m105|{nm}")
        h, d = OUT["natural"][host], OUT["natural"][donor]
        r["frac_C"] = float((r["C"] - h["C"]) / (d["C"] - h["C"])) if abs(d["C"] - h["C"]) > 1e-6 else None
        OUT["swaps"][nm] = r
        log("m105", event="arm", arm=nm, rival_share=r["rival_share"], C=round(r["C"], 2), frac_C=None if r["frac_C"] is None else round(r["frac_C"], 2))
        dump(f"{TD}/results/m105.json", OUT)
md = ["# E12 queue m105: per-script cell swaps (SB): where does a real rude / unhelpful history act?", "",
      f"m102's 2 x 2 histories, fold B {OUT['n']} scripts. Host <- donor = the host chat with the donor's module outputs (same script) at turn 3 + header. "
      "X = mixers 24-34; MLP = MLPs 24-34; ALL = all mixers and MLPs 0-34 (the whole residual at turn 3 + header through 34). frac C = (C - host) / (donor - host).", "",
      "| context | habit | helper / rival | rival share | C | frac C |", "| --- | --- | --- | --- | --- | --- |"]
for nm, v in list(OUT["natural"].items()) + list(OUT["swaps"].items()):
    fc = v.get("frac_C")
    md.append(f"| {nm} | {v['habit']:.2f} | {v['helper']} / {v['rival']} | {('%.2f' % v['rival_share']) if v['rival_share'] is not None else '-'} | {v['C']:+.2f} | {'' if fc is None else '%.2f' % fc} |")
md += ["", "## Pre-stated (before results)", "",
       "- entry point carries it per script: X swaps reach >= 0.7 of the donor's rival share and C gap;",
       "- at turn 3 + header but not only mixers 24-34: ALL >= 0.7, X < 0.7;", "- neither: the history tokens outside turn 3 + header are read after layer 34."]
open(f"{TD}/results/m105_cell_swaps.md", "w").write("\n".join(md) + "\n")
status(f"queue task m105_cell_swaps done ({TD}/results/m105_cell_swaps.md)")
