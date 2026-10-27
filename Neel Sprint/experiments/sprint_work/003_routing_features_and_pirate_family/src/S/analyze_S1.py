"""sw003 S1 analysis (CPU): python3 analyze_S1.py B_s0:32 A_s0:32 A_s0:40  -> out/results_S1.json + out/analysis_S1.txt

Labels: sw001 STRICT regex on "By the way," + opener (lib/vstats.lab). Per (model, layer, cell, arm), paired over scripts vs the
unsteered cell (same seed): unconditional bee / crow / no-animal rates and deltas; rival share among animal-bearing openers
(rival / (bee or crow)); fluency proxies (generated tokens, immediate-repeat rate). Rival / helper per assignment (A: helper bee,
rival crow; B: the reverse).
Readout per cell (frozen, spec §7 S1): default cell -> Delta rival rate (toward the rival); dismissive cell -> Delta helper rate
(rerouting toward the helper).
Null comparison at k in {1, 2}: for a tested direction d, the null effects are those of the 53 nulls dosed at d's SD-unit size
(arms "null:<n>@<d><sign>|k<k>"); margin = effect(d) - 95th percentile of the null effects. CI: bootstrap over scripts
(2,000), resampling scripts jointly for the named arm and every null, recomputing the percentile each time.
Frozen prediction (S1, p 0.60): in the default cell "both" margin >= +20 at k=1 or k=2 while disp and tone margins <= +5 at
both k; in the dismissive cell disp or tone margin >= +20 (toward the helper). Decision branches per spec §7."""
import json, os, sys
from collections import defaultdict
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common_s as S  # noqa: E402
sys.path.insert(0, f"{S.HERE}/lib")
from vstats import lab  # noqa: E402

NB = 2000


def load(M, L):
    G = defaultdict(dict); X = defaultdict(list)
    for l in open(f"{S.OUT}/gen_S1_{M}_L{L}.jsonl"):
        r = json.loads(l); p = r["id"].split("|"); cell, s = p[1], p[-1]; arm = "|".join(p[2:-1])
        G[(cell, arm)][s] = lab("By the way," + r["text"]); X[(cell, arm)].append((r["n_tok"], r["rep"]))
    arms = json.load(open(f"{S.OUT}/arms_S1_{M}_L{L}.json"))["arms"]
    return G, X, arms


def main(specs):
    out, txt = {}, []
    rng = np.random.default_rng(0)
    for spec in specs:
        M, L = spec.split(":"); L = int(L)
        G, X, arms = load(M, L)
        asg = S.ASSIGN[M]; helper, rival = S.HELPER[asg], S.RIVAL[asg]
        res = dict(model=M, layer=L, helper=helper, rival=rival, cells={})
        txt.append(f"\n===== {M} L{L} (helper {helper}, rival {rival})")
        for cell in ("def", "dis"):
            U = G[(cell, "unsteered")]; Sc = sorted(U)
            readk = rival if cell == "def" else helper
            def vec(Ga, k):
                return np.array([Ga[s][k] for s in Sc], float) * 100
            u = {k: vec(U, k) for k in ("bee", "crow", "neither")}
            anyu = 100 - u["neither"]
            rc = dict(n=len(Sc), unsteered={k: float(v.mean()) for k, v in u.items()},
                      unsteered_rival_share=float(u[rival].sum() / max(1e-9, (100 - u["neither"]).sum()) * 100), arms={})
            txt.append(f"-- cell {cell}: n {len(Sc)}; unsteered bee {u['bee'].mean():.1f} crow {u['crow'].mean():.1f} none {u['neither'].mean():.1f};"
                       f" readout = Delta {readk} rate")
            dvec = {}   # arm -> {script: delta of the readout}
            for (c2, arm), Ga in G.items():
                if c2 != cell or arm == "unsteered":
                    continue
                Sa = [s for s in Sc if s in Ga]
                v = {k: np.array([Ga[s][k] for s in Sa], float) * 100 for k in ("bee", "crow", "neither")}
                uu = {k: np.array([U[s][k] for s in Sa], float) * 100 for k in v}
                d = {k: v[k] - uu[k] for k in v}
                share = v[rival].sum() / max(1e-9, (100 - v["neither"]).sum()) * 100
                bt = rng.integers(0, len(Sa), (NB, len(Sa)))
                e = dict(n=len(Sa), rates={k: float(v[k].mean()) for k in v}, delta={k: float(d[k].mean()) for k in d},
                         rival_share=float(share), readout=float(d[readk].mean()),
                         readout_ci=[float(np.percentile(d[readk][bt].mean(1), q)) for q in (2.5, 97.5)],
                         n_tok=float(np.mean([x[0] for x in X[(cell, arm)]])), rep=float(np.mean([x[1] for x in X[(cell, arm)]])))
                rc["arms"][arm] = e
                dvec[arm] = dict(zip(Sa, d[readk]))
            # null comparison on the scripts every null and the named arm share
            comp = {}
            for arm, e in rc["arms"].items():
                if arm.startswith("null:") or "|k" not in arm:
                    continue
                d_sg, k = arm.split("|k"); k = float(k)
                if k not in (1.0, 2.0):
                    continue
                nulls = [a for a in rc["arms"] if a.startswith("null:") and a.endswith(f"@{d_sg}|k{k}")]
                if not nulls:
                    continue
                Ss = sorted(set(dvec[arm]).intersection(*[set(dvec[a]) for a in nulls]))
                ne_s = np.array([[dvec[a][s] for s in Ss] for a in nulls])          # [n_null, n_scripts]
                ea = np.array([dvec[arm][s] for s in Ss])
                ne = ne_s.mean(1); eff = float(ea.mean()); p95 = float(np.percentile(ne, 95))
                bt = rng.integers(0, len(Ss), (NB, len(Ss)))
                mb = ea[bt].mean(1) - np.percentile(ne_s[:, bt].mean(2), 95, axis=0)
                comp[arm] = dict(effect=eff, n_scripts=len(Ss), n_null=len(nulls), null_p95=p95, null_mean=float(ne.mean()), null_max=float(ne.max()),
                                 margin=eff - p95, margin_ci=[float(np.percentile(mb, 2.5)), float(np.percentile(mb, 97.5))],
                                 frac_null_ge_effect=float((ne >= eff).mean()))
            rc["null_comparison"] = comp
            for arm in sorted(rc["arms"], key=lambda a: (a.startswith("null:"), a)):
                if arm.startswith("null:"):
                    continue
                e = rc["arms"][arm]; cm = comp.get(arm)
                txt.append(f"  {arm:24s} {readk} {e['readout']:+6.1f} [{e['readout_ci'][0]:+.1f}, {e['readout_ci'][1]:+.1f}]  bee {e['rates']['bee']:5.1f} crow {e['rates']['crow']:5.1f}"
                           f" none {e['rates']['neither']:5.1f}  rival share {e['rival_share']:5.1f}  tok {e['n_tok']:.0f} rep {e['rep']:.3f}"
                           + (f"  | null p95 {cm['null_p95']:+.1f} (n {cm['n_null']}) margin {cm['margin']:+.1f} [{cm['margin_ci'][0]:+.1f}, {cm['margin_ci'][1]:+.1f}]" if cm else ""))
            res["cells"][cell] = rc
        # frozen prediction
        m = lambda cell, a: res["cells"][cell]["null_comparison"].get(a, {}).get("margin")
        both_hit = [k for k in (1.0, 2.0) if (m("def", f"both-|k{k}") or -1e9) >= 20]
        alone_low = all((m("def", f"{d}-|k{k}") is not None and m("def", f"{d}-|k{k}") <= 5) for d in ("disp", "tone") for k in (1.0, 2.0))
        dis_reroute = [a for d in ("disp", "tone") for k in (1.0, 2.0) if (m("dis", a := f"{d}+|k{k}") or -1e9) >= 20]
        any_def = [a for d in ("disp", "tone", "both") for k in (1.0, 2.0) if (m("def", a := f"{d}-|k{k}") or -1e9) > 0]
        single = any((m("def", f"{d}-|k{k}") or -1e9) >= 20 for d in ("disp", "tone") for k in (1.0, 2.0))
        verdict = ("AND gate supported (causal influence level): full frozen pattern" if both_hit and alone_low and dis_reroute else
                   "default-cell AND pattern only (dismissive cell not rerouted by one feature)" if both_hit and alone_low else
                   "single-feature routing" if single else
                   "nothing beats the null at <= 2x" if not any_def and not dis_reroute else "none of the frozen branches")
        res["prediction"] = dict(def_both_ge20_at=both_hit, def_disp_tone_le5_all=alone_low, dis_reroute_ge20=dis_reroute,
                                 frozen_prediction_met=bool(both_hit and alone_low and dis_reroute), branch=verdict)
        txt.append(f"  PREDICTION: {res['prediction']}")
        out[spec] = res
    json.dump(out, open(f"{S.OUT}/results_S1.json", "w"), indent=1)
    open(f"{S.OUT}/analysis_S1.txt", "w").write("\n".join(txt) + "\n")
    print("\n".join(txt))


if __name__ == "__main__":
    main(sys.argv[1:])
