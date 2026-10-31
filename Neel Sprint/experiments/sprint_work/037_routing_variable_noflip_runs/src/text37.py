"""sw037 text summary of results37.json (run agent, E2; box 1, system python3). python3 text37.py <results37.json> [> text37.txt]"""
import json, sys

R = json.load(open(sys.argv[1]))
f = lambda x: "nan" if x is None or x != x else f"{x:+.3f}"
g = lambda x: "nan" if x is None or x != x else f"{x:.3f}"
c = lambda v: "[" + ", ".join(f(x) for x in v) + "]" if v else "[]"

print(f"stage {R['stage']}; judged records {R['judged_records']}")
for k, v in R.items():
    if k.startswith("agreement"):
        print(k, json.dumps(v))
P = R.get("part1")
if P:
    print("\n== Part 1 (unconditional rival rate; induce decides)")
    for ro, RR in P["readouts"].items():
        for m, M in RR.items():
            print(f"-- {ro} {m}: none UH {g(M['none_UH']['unc'])} SH {g(M['none_SH']['unc'])}  gap {f(M['gap'])} {c(M['gap_ci'])}  gate {'PASS' if M['gate_pass'] else 'FAIL'}"
                  f"  (onset UH {g(M['none_UH']['onset'])} SH {g(M['none_SH']['onset'])}; helper UH {g(M['none_UH']['hel'])} SH {g(M['none_SH']['hel'])}; share gap {f(M['share_gap_beside'])})")
            D = M["rev"]
            for arm in ("asT", "r1"):
                E = D[arm]
                print(f"   induce {arm:4s} toward {f(E['toward'])} {c(E['toward_ci'])}  frac {g(E['frac_of_gap'])} {c(E['frac_of_gap_ci'])}  margin {f(E['margin'])} {c(E['margin_ci'])}"
                      f"  each A {json.dumps({a: round(x, 3) for a, x in E['each_A_toward'].items()})}  pooled A {f(D[arm + '_Apool']['toward'])} {c(D[arm + '_Apool']['toward_ci'])}"
                      f"  | share {g(E['share'])} (n_habit {E['n_habit']}) onset {g(E['onset'])} helper shift {f(E['hel_shift'])}")
            print(f"   asT/r1 {g(D['asT_over_r1'])} {c(D['asT_over_r1_ci'])}  label(asT) {D['label_asT']}  [r1 by the same rule: {D['label_r1_beside']}]")
            Dr = M["fwd"]
            print(f"   remove (beside): asT {f(Dr['asT']['toward'])} {c(Dr['asT']['toward_ci'])}  r1 {f(Dr['r1']['toward'])} {c(Dr['r1']['toward_ci'])}"
                  f"  pooled A asT {f(Dr['asT_Apool']['toward'])} r1 {f(Dr['r1_Apool']['toward'])}")
    print("\n-- per organism (deciding readout)")
    for m, E in P["models"].items():
        print(f"   {m}: {json.dumps(E, default=str)}")
    if P["flags"]:
        print("   flags:", "; ".join(P["flags"]))
for k in [x for x in R if x.startswith("part2_")]:
    Q = R[k]
    print(f"\n== Part 2 ({Q['readout']}): label {Q['label']}")
    print("   gates:", json.dumps(Q["gate"]))
    for cx, T in Q["transfer"].items():
        for nm, E in T.items():
            s = f"   {cx} {nm}: rec none {g(E['rate_recipient_none'])} donor none {g(E['rate_donor_none'])} denom {f(E['denominator'])} {c(E['denominator_ci'])}"
            for cl in ("xf@L16-63", "xf@L16-31", "xf@L32-63"):
                if cl in E:
                    s += f" | {cl} rate {g(E[cl]['rate'])} shift {f(E[cl]['shift'])} transfer {g(E[cl]['transfer'])} {c(E[cl]['transfer_ci'])}"
            for cl in ("id@L16-63", "om@L16-63"):
                if cl in E:
                    s += f" | {cl} shift {f(E[cl]['shift'])} {c(E[cl]['shift_ci'])}"
            s += f" | id too disruptive {E.get('identity_too_disruptive')} om too disruptive {E.get('onmanifold_too_disruptive')} (vs gate gap {E.get('onmanifold_vs_half_gate_gap_beside')})"
            print(s)
    if Q["flags"]:
        print("   flags:", "; ".join(Q["flags"]))
