"""sw029 Part A: render the analysis tables (plain text / markdown) from analyze29_x's results29.json (prep agent, E2, 31 Oct 2026).
Numbers only come from results29.json; nothing is recomputed here. Tables: frozen-rule verdict per arm x model (induce, unconditional
rival rate: toward, ratio, margin, mean cos^2), the gap and precondition, share / onset / helper rate beside, remove beside, sw052's
c1, the counterbalanced pair, cumulative-offset ratios (A / arm, and arm vs r1 at the header), flags, forced pilots.
  python3 text29.py RESULTS_JSON [--out FILE]"""
import argparse, json, sys

HERE = __import__("os").path.dirname(__import__("os").path.abspath(__file__)); sys.path.insert(0, HERE)
import common29 as K  # noqa: E402


def f(x, d=3):
    return "NA" if x is None or (isinstance(x, float) and x != x) else f"{x:+.{d}f}"


def c(v):
    return "NA" if not v else f"[{f(v[0])}, {f(v[1])}]"


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("res"); ap.add_argument("--out", default=None); a = ap.parse_args()
    R = json.load(open(a.res)); fr = R["readouts"]["free"]; L = []
    L.append("## Frozen rule (free readout, induce decides; unconditional rival rate)")
    L.append("OVERALL: " + json.dumps(R.get("OVERALL"), default=str))
    for m in ("hdA0", "hdB0"):
        M = fr["models"].get(m, {})
        L.append(f"\n### {m}: gap {f(M.get('gap'))} {c(M.get('gap_ci'))} (rival rate none: self-hostile {f(M.get('unc_none_self_hostile'))}, user-hostile {f(M.get('unc_none_user_hostile'))}); "
                 f"precondition {json.dumps(M.get('precondition'))}")
        D = M.get("rev", {})
        L.append(f"r1 toward {f(D.get('r1_toward'))} {c(D.get('r1_toward_ci'))}")
        L.append("| arm | site | toward (rival rate) | ratio | mean cos² | margin vs pooled A | verdict | share toward (beside) | onset shift | helper shift |")
        L.append("|---|---|---|---|---|---|---|---|---|---|")
        for arm in K.LF_ARMS:
            E = D.get("arms", {}).get(arm)
            if not E:
                continue
            cell = fr["cells"].get(f"{m}|rev|{arm}", {})
            L.append(f"| {arm} | {K.SITE[arm]} | {f(E['toward'])} {c(E['toward_ci'])} | {f(E['ratio'])} {c(E['ratio_ci'])} | {f(E.get('mean_cos2'))} | "
                     f"{f(E.get('margin'))} {c(E.get('margin_ci'))} | {E.get('verdict')} | {f(E.get('share_toward_beside'))} | {f(cell.get('onset_shift'))} | {f(E.get('helper_shift'))} |")
        L.append("\nPer-cell rates (induce): arm | n | rival rate | helper rate | share (habit n) | onset | helpfulness | fluency | cap-hit")
        for g in ("none", "r1") + K.LF_ARMS + tuple(f"{x}_Apool" for x in K.LF_ARMS):
            cc = fr["cells"].get(f"{m}|rev|{g}")
            if cc:
                L.append(f"  {g:10s} {cc['n']:4d} {f(cc['unc'])} {f(cc['hel'])} {f(cc['share'])} ({cc['n_habit']}) {f(cc['onset'])} {f(cc['helpfulness'], 2)} {f(cc['fluency'], 2)} {f(cc['cap_hit'])}")
        Dr = M.get("fwd", {})
        if Dr:
            L.append(f"\nRemove (DESCRIPTIVE ONLY, D34 item 4: the A clamps run at 1.4-2.1x each arm's cumulative offset with no upper bound and random edits "
                     f">= ~1.1x remove generically (sw028 / sw031), so these numbers carry no specificity information): r1 toward {f(Dr.get('r1_toward'))}")
            for arm, E in Dr.get("arms", {}).items():
                L.append(f"  {arm}: toward {f(E['toward'])} ratio {f(E['ratio'])} difference vs pooled A {f(E.get('margin'))} {c(E.get('margin_ci'))} pooled A shift {f(E.get('poolA_shift'))}")
    L.append("\n### sw052 c1 (ctrlB0's d_self, recomputed on the unconditional scale): " + json.dumps(R.get("sw052_c1"), default=str))
    for d, E in fr.get("counterbalanced", {}).items():
        L.append(f"\n### Counterbalanced pair [{K.DIRNAME[d]}]: " + "; ".join(f"{arm} ratio {f(v['ratio'])} {c(v['ratio_ci'])} margin {f(v['margin'])} {c(v['margin_ci'])}" for arm, v in E["arms"].items()))
    L.append("\n### Cumulative-offset ratios (median over s0 units; A / its arm at the arm's site; arm vs r1 at the header)")
    for k, v in R.get("cumulative", {}).items():
        if not k.startswith("free"):
            continue
        L.append(f"{k}: A fail {v['A_fail']}")
        for a_, s in v["A_vs_arm"].items():
            L.append("  " + a_ + " " + "; ".join(f"{site} " + ", ".join(f"{b} {f(x, 2)}" for b, x in bb.items()) for site, bb in s.items()))
        L.append("  arm vs r1 (header): " + "; ".join(f"{lab} " + ", ".join(f"{b} {f(x, 2)}" for b, x in bb.items()) for lab, bb in v["arm_vs_r1_hdr"].items()))
    L.append("\n### Flags: " + "; ".join(fr.get("flags", [])[:60]))
    L.append("### Helper flags: " + "; ".join(fr.get("helper_flags", [])[:60]))
    for ro in ("fbtw", "fraf"):
        if ro in R["readouts"]:
            blk = R["readouts"][ro]
            L.append(f"\n## Forced pilot {ro} (does not decide; {K.BRIDGE_NOTE[ro]})")
            for m in ("hdA0", "hdB0"):
                D = blk["models"].get(m, {}).get("rev", {})
                L.append(f"{m}: r1 toward {f(D.get('r1_toward'))}; " + "; ".join(f"{arm} toward {f(E['toward'])} ratio {f(E['ratio'])} margin {f(E.get('margin'))} {c(E.get('margin_ci'))}"
                                                                         for arm, E in D.get("arms", {}).items()))
    L.append("\n### Coverage: " + json.dumps(R.get("coverage")))
    txt = "\n".join(L) + "\n"
    if a.out:
        open(a.out, "w").write(txt)
    print(txt)


if __name__ == "__main__":
    main()
