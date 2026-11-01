"""Compact tables from cumctrl_<exp>.json and diag.json -> ../TABLES.txt (plain text). Light; runs anywhere."""
import json
import os

OUT = "/workspace/runs_executor/overnight_2026-10-30/cumctrl"
B = ["L16", "L28-40", "L44-63"]
lines = []


def f(x):
    return "n/a" if x is None or x[0] is None else f"{x[0]:.2f} [{x[1]:.2f}-{x[2]:.2f}]"


def g(x):
    return "n/a" if x is None or x[0] is None else f"{x[0]:.2f}"


for exp in ("sw012", "sw021", "sw010", "sw011B", "sw011C"):
    p = f"{OUT}/cumctrl_{exp}.json"
    if not os.path.exists(p):
        continue
    d = json.load(open(p))
    lines.append(f"\n===== {exp}: ctrl/real cumulative offset ratio, median [IQR] over scripts (tokens 1-6)")
    lines.append(f"{'cell':62s} {'n':>3s}  " + "  ".join(f"{b:>18s}" for b in B) + "   tok0 L44-63")
    for k, c in d["cells"].items():
        r = c["ratio"]["bands"]
        lines.append(f"{k:62s} {c['n']:3d}  " + "  ".join(f"{f(r[b]):>18s}" for b in B) + f"   {f(c['ratio_tok0']['bands']['L44-63'])}")
    if d.get("natural"):
        lines.append(f"--- {exp}: natural units (median over scripts; per-token, mean over tokens 1-6). real | ctrl")
        keys = [("abs", "offset abs"), ("rel_state", "offset/||state||"), ("over_sd_u", "offset / SD_within(d)"),
                ("along_u_over_sd_u", "offset along d / SD_within(d)"), ("over_own_sd", "offset / SD_within(own dir)"),
                ("over_gap_u", "offset / class gap along d"), ("over_gap_full", "offset / full class-mean gap"),
                ("over_pair_full", "offset / paired self-user gap"), ("over_rms_within", "offset / within-cond RMS")]
        for k, c in d["cells"].items():
            if "over_sd_u" not in c.get("real", {}):
                continue
            lines.append(f"  {k}")
            for kk, nm in keys:
                if kk not in c["real"]:
                    continue
                lines.append(f"    {nm:34s} " + "  ".join(f"{b}: {g(c['real'][kk]['bands'][b])} | {g(c['ctrl'][kk]['bands'][b])}" for b in B))
        for m, n in d["natural"].items():
            L = d["layers"]
            idx = [L.index(x) for x in (16, 32, 40, 48, 56, 63)]
            lines.append(f"  natural {exp} {m} (L16/32/40/48/56/63): gap_u/SD_u " + " ".join(f"{n['gap_u_over_sd_u_tok1_6'][i]:.1f}" for i in idx)
                         + " | ||d_hdrmean|| " + " ".join(f"{n['norm_d_hdrmean'][i]:.1f}" for i in idx)
                         + " | SD_u " + " ".join(f"{n['sd_u_tok1_6'][i]:.2f}" for i in idx)
                         + " | paired full gap " + " ".join(f"{n['pair_full_tok1_6_median'][i]:.1f}" for i in idx))
    if d.get("checks"):
        for k, v in d["checks"].items():
            lines.append(f"  check {k}: abs tok1-6 " + "  ".join(f"{b}: {f(v['abs_tok1_6']['bands'][b])}" for b in B)
                         + " | rel " + "  ".join(f"{b}: {f(v['rel_tok1_6']['bands'][b])}" for b in B))

p = f"{OUT}/cumctrl_sw016.json"
if os.path.exists(p):
    d = json.load(open(p))
    lines.append("\n===== sw016 (stories): ctrl/real ratio at the patched line starts S (all S / earlier S / the cut)")
    for k, c in d["cells"].items():
        for nm in ("ratio_allS", "ratio_earlierS", "ratio_cut"):
            if nm in c:
                lines.append(f"{k:44s} {nm:15s} n={c['n']:3d} " + "  ".join(f"{b}: {f(c[nm]['bands'][b])}" for b in B))
        for arm in ("real", "ctrl"):
            nat = c[f"{arm}_cut_nat"]
            lines.append(f"    {arm} at cut: " + " ; ".join(f"{kk} " + "/".join(g(nat[kk]['bands'][b]) for b in B) for kk in nat))
    for m, n in d["natural"].items():
        lines.append(f"  natural {m}: gap_u/sd_u L16..63 " + " ".join(f"{x:.1f}" for x in n["gap_u_over_sd_u"]))

p = f"{OUT}/diag.json"
if os.path.exists(p):
    d = json.load(open(p))
    lines.append("\n===== direction coherence across layers (|cos| adjacent layers, median L16-62; |cos(u16, uL)|)")
    for k, v in d["coherence"].items():
        lines.append(f"  {k:48s} adj {v['adj_median']:.3f} (L40-60 {v['adj_L40_60']:.3f}, min {v['adj_min']:.3f})  far " + str(v["far_from_16"]))
    lines.append("\n===== per-layer pushes from the R7 logs (median over scripts of mean tok 1-6; [median, n])")
    for k, v in d["push"].items():
        lines.append(f"  {k}: {json.dumps(v)}")
open(f"{OUT}/TABLES.txt", "w").write("\n".join(lines) + "\n")
print("\n".join(lines))

# toward the donor's full state
for exp in ("sw012", "sw021", "sw010", "sw011B"):
    p = f"{OUT}/toward_{exp}.json"
    if not os.path.exists(p):
        continue
    d = json.load(open(p))
    lines.append(f"\n===== {exp}: fraction of the paired donor gap closed (all / orthogonal to d), real | ctrl, median over scripts")
    for k, c in d["cells"].items():
        lines.append(f"  {k:66s} " + "  ".join(
            f"{b}: {g(c['real']['frac_closed']['bands'][b])}/{g(c['real']['frac_closed_orth']['bands'][b])} | "
            f"{g(c['ctrl']['frac_closed']['bands'][b])}/{g(c['ctrl']['frac_closed_orth']['bands'][b])}" for b in B))
open(f"{OUT}/TABLES.txt", "w").write("\n".join(lines) + "\n")

p = f"{OUT}/pushback_sw012.json"
if os.path.exists(p):
    d = json.load(open(p))
    lines.append("\n===== sw012 push-back: control's own-direction coordinate offset a_L and the donor's b_L, in units of the L16 push (median over scripts, tok 1-6)")
    for k, v in d.items():
        lines.append(f"  {k:20s} layers {v['layers']}")
        lines.append(f"  {'':20s} a/a16  " + " ".join(f"{x[0]:.2f}" for x in v["a_signed_over_a16"]))
        lines.append(f"  {'':20s} b/a16  " + " ".join(f"{x[0]:.2f}" for x in v["b_donor_over_a16"]))
        lines.append(f"  {'':20s} share  " + " ".join(f"{x[0]:.2f}" for x in v["share_along_own_dir"]))
open(f"{OUT}/TABLES.txt", "w").write("\n".join(lines) + "\n")
