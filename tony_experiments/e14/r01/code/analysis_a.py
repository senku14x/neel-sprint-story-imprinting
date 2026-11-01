"""E14 R01 Part A analysis -> results/partA.json + results/partA.md. Rules as fixed in the brief."""
import json, os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa

SW007 = {"S": dict(removal=0.80, induction=0.59), "SB": dict(removal=0.98, induction=0.86)}
ARMS = ["none", "ALL", "OWN", "PAR", "PARn", "CTRL", "NULL", "OWN-a", "OWN-b", "PAR-a", "PAR-b"]


def fmt(x, d=2):
    return "—" if x is None or (isinstance(x, float) and not np.isfinite(x)) else f"{x:.{d}f}"


def fci(c, d=2):
    return f"[{fmt(c[0], d)}, {fmt(c[1], d)}]"


def reading(s):
    if s is None or not np.isfinite(s):
        return None
    return "parent's own" if s >= 0.70 else ("sharpened by training" if s > 0.25 else "built by training")


def main():
    SID = sids(); idx = boot_idx(len(SID))
    out = {}; md = []
    for M in ("S", "SB"):
        rows = jl(f"{R}/gens/A_btw_{M}.jsonl")
        if not rows:
            continue
        arms = [a for a in ARMS if any(r["arm"] == a for r in rows)]
        C = {(d, a): counts_by_script([r for r in rows if r["direction"] == d and r["arm"] == a], SID, M) for d in ("removal", "induction") for a in arms}
        pt = {k: float(share_from_counts(v.sum(0))) for k, v in C.items()}
        bs = {k: share_from_counts(v[idx].sum(1)) for k, v in C.items()}  # [2000]
        nhab = {k: int(v[:, :3].sum()) for k, v in C.items()}
        gap_pt = pt[("removal", "none")] - pt[("induction", "none")]
        gap_bs = bs[("removal", "none")] - bs[("induction", "none")]
        res = dict(gap=gap_pt, gap_ci=ci(gap_bs), directions={})
        for d in ("removal", "induction"):
            def tw(a, p):
                return (p[(d, "none")] - p[(d, a)]) if d == "removal" else (p[(d, a)] - p[(d, "none")])
            tab = {}
            for a in arms:
                t_pt = tw(a, pt); t_bs = tw(a, bs)
                tab[a] = dict(share=pt[(d, a)], share_ci=ci(bs[(d, a)]), n_habit=nhab[(d, a)], counts=C[(d, a)].sum(0).tolist(),
                              toward=t_pt if a != "none" else None, toward_ci=ci(t_bs) if a != "none" else None,
                              frac=t_pt / gap_pt if a != "none" else None, frac_ci=ci(t_bs / gap_bs) if a != "none" else None)
            dd = dict(arms=tab)
            # reproduction
            if "ALL" in tab:
                dd["repro"] = dict(frac=tab["ALL"]["frac"], sw007=SW007[M][d], diff=tab["ALL"]["frac"] - SW007[M][d],
                                   within_015=abs(tab["ALL"]["frac"] - SW007[M][d]) <= 0.15)
            tO = tw("OWN", pt); tO_bs = tw("OWN", bs); tO_ci = ci(tO_bs)
            own_moves = tO >= 0.30 and tO_ci[0] is not None and (tO_ci[0] > 0 or tO_ci[1] < 0)
            dd["own_moves"] = own_moves
            tP_bs = tw("PAR", bs); tN_bs = tw("NULL", bs) if "NULL" in arms else None
            s_pt = tw("PAR", pt) / tO; s_bs = tP_bs / tO_bs
            dd["s"] = s_pt; dd["s_ci"] = ci(s_bs)
            if tN_bs is not None:
                dd["s_minus_null"] = (tw("PAR", pt) - tw("NULL", pt)) / tO
                dd["s_minus_null_ci"] = ci((tP_bs - tN_bs) / tO_bs)
                tN = tw("NULL", pt); tN_ci = ci(tN_bs)
                dd["null_check"] = dict(toward_null=tN, ci=tN_ci, cant_tell=bool(tN > 0.10 * tO and (tN_ci[0] > 0 or tN_ci[1] < 0)))
            if not own_moves:
                dd["reading"] = "no test"
            elif dd.get("null_check", {}).get("cant_tell"):
                dd["reading"] = "can't tell"
            else:
                dd["reading"] = reading(s_pt)
            rds = {reading(x) for x in dd["s_ci"] if x is not None}
            dd["ci_spans_two_readings"] = len(rds) > 1
            res["directions"][d] = dd
        r1, r2 = res["directions"]["removal"]["reading"], res["directions"]["induction"]["reading"]
        res["model_line"] = r1 if r1 == r2 else "mixed"
        res["repro_both_miss_gt_025"] = all(abs(res["directions"][d]["repro"]["diff"]) > 0.25 for d in ("removal", "induction")
                                            if "repro" in res["directions"][d])
        # free replies
        fr = jl(f"{R}/gens/A_free_{M}.jsonl")
        lab = {r["key"]: r["declines"] for r in jl(f"{R}/labels/haiku_A_free_{M}.jsonl") if r.get("declines") is not None}
        free = {}
        for d in ("removal", "induction"):
            for a in ("none", "OWN", "PAR"):
                rr = [r for r in fr if r["direction"] == d and r["arm"] == a]
                cnt = counts_by_script(rr, SID, M).sum(0).tolist() if rr else None
                dl = [lab[r["key"]] for r in rr if r["key"] in lab]
                free[f"{d}|{a}"] = dict(n=len(rr), counts_helper_rival_both_neither=cnt, share=float(share_from_counts(cnt)) if cnt else None,
                                        n_labelled=len(dl), decline_rate=(sum(dl) / len(dl)) if dl else None)
        res["free"] = free
        out[M] = res
        # markdown
        md.append(f"### Part A, `{M}`\n")
        md.append(f"Gap = share(dismissive, none) − share(helpful, none) = {fmt(gap_pt)} {fci(res['gap_ci'])}.\n")
        for d in ("removal", "induction"):
            dd = res["directions"][d]
            md.append(f"**{d}** (recipient {'dismissive' if d == 'removal' else 'helpful'}, donor {'helpful' if d == 'removal' else 'dismissive'})\n")
            md.append("| arm | rival share [95% CI] | n habit-bearing | toward [CI] | frac [CI] |\n|---|---|---|---|---|")
            for a, t in dd["arms"].items():
                md.append(f"| {a} | {fmt(t['share'])} {fci(t['share_ci'])} | {t['n_habit']} | "
                          f"{fmt(t['toward']) + ' ' + fci(t['toward_ci']) if t['toward'] is not None else '—'} | "
                          f"{fmt(t['frac']) + ' ' + fci(t['frac_ci']) if t['frac'] is not None else '—'} |")
            if "repro" in dd:
                rp = dd["repro"]
                md.append(f"\nReproduction: ALL frac {fmt(rp['frac'])} vs sw007 {rp['sw007']:.2f} (diff {rp['diff']:+.2f}; "
                          f"{'within' if rp['within_015'] else 'outside'} ±0.15).")
            md.append(f"OWN moves (toward ≥ 0.30, CI excludes 0): {dd['own_moves']}. s = toward(PAR)/toward(OWN) = {fmt(dd['s'])} {fci(dd['s_ci'])}; "
                      f"(toward(PAR) − toward(NULL))/toward(OWN) = {fmt(dd.get('s_minus_null'))} {fci(dd.get('s_minus_null_ci', [None, None]))}.")
            if "null_check" in dd:
                nc = dd["null_check"]
                md.append(f"NULL check: toward(NULL) = {fmt(nc['toward_null'])} {fci(nc['ci'])}; can't tell = {nc['cant_tell']}.")
            md.append(f"**Reading ({d}): {dd['reading']}**" + (" (the interval spans two readings)" if dd["ci_spans_two_readings"] else "") + "\n")
        md.append(f"**`{M}` line: {res['model_line']}**\n")
        md.append("Free replies (STRICT counts helper/rival/both/neither; Haiku decline rate):\n")
        md.append("| direction | arm | n | counts | rival share | decline rate (n labelled) |\n|---|---|---|---|---|---|")
        for k, v in free.items():
            d, a = k.split("|")
            md.append(f"| {d} | {a} | {v['n']} | {v['counts_helper_rival_both_neither']} | {fmt(v['share'])} | {fmt(v['decline_rate'])} ({v['n_labelled']}) |")
        md.append("")
    # geometry
    if os.path.exists(f"{R}/results/partA_geometry.json"):
        g = json.load(open(f"{R}/results/partA_geometry.json"))
        md.append("### Part A geometry (no sampling; mean over scripts; induction direction, removal identical)\n")
        md.append("| model | block | cos(ΔPAR,ΔOWN) all | hdr | cos(ΔCTRL,ΔOWN) all | hdr | ‖ΔPAR‖/‖ΔOWN‖ all | hdr | ‖ΔCTRL‖/‖ΔOWN‖ all | hdr |\n|---|---|---|---|---|---|---|---|---|---|")
        for M in ("S", "SB"):
            for j, L in enumerate(g["blocks"]):
                x = g[M]
                md.append(f"| {M} | {L} | {x['cos_par_all'][j]:.3f} | {x['cos_par_hdr'][j]:.3f} | {x['cos_ctrl_all'][j]:.3f} | {x['cos_ctrl_hdr'][j]:.3f} | "
                          f"{x['ratio_par_all'][j]:.3f} | {x['ratio_par_hdr'][j]:.3f} | {x['ratio_ctrl_all'][j]:.3f} | {x['ratio_ctrl_hdr'][j]:.3f} |")
        out["geometry"] = g
    n2 = json.load(open(f"{R}/results/partA_n2.json"))
    cov = [v["coverage"] for v in n2["n2"].values()]
    out["null_coverage"] = dict(mean=float(np.mean(cov)), min=float(np.min(cov)), n_full=int(sum(c >= 1.0 for c in cov)), n=len(cov))
    md.append(f"\nNULL donor coverage: {out['null_coverage']['n_full']}/64 scripts fully covered; mean {out['null_coverage']['mean']:.3f}, "
              f"min {out['null_coverage']['min']:.3f} (uncovered positions set to 0).\n")
    json.dump(out, open(f"{R}/results/partA.json", "w"), indent=1)
    open(f"{R}/results/partA.md", "w").write("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
