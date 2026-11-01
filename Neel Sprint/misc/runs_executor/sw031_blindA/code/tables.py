import json
D = json.load(open("/workspace/runs_executor/sw031_blindA/out/recompute.json"))["res"]
f = lambda t, d=2: f"{t[0]:+.{d}f} [{t[1]:+.{d}f}, {t[2]:+.{d}f}]"
r3 = lambda t: f"{t[0]:.3f} [{t[1]:.3f},{t[2]:.3f}]"
lines = []
P = lines.append
P("## Q1 cells (rates with 95% sid-bootstrap CI; onset = first strict habit match among habit-bearing rows)")
for m, o in D.items():
    P(f"\n### {m}\n| ctx | arm | band | n | bee | crow | rival | habit | onset tok med (mean) | onset char med | n habit | first=rival |")
    P("|---|---|---|---|---|---|---|---|---|---|---|---|")
    order = sorted(o["cells"], key=lambda k: (k.split("|")[0][::-1], ["none","own_opp","x_opp","x_same","own_sk"].index(k.split("|")[1]), k.split("|")[2]))
    for k in order:
        e = o["cells"][k]; c, a, b = k.split("|")
        ot = "-" if e["onset_tok_median"] is None else f"{e['onset_tok_median']:.0f} ({e['onset_tok_mean']:.0f})"
        oc = "-" if e["onset_char_median"] is None else f"{e['onset_char_median']:.0f}"
        P(f"| {c} | {a} | {b} | {e['n']} | {r3(e['bee'])} | {r3(e['crow'])} | {r3(e['riv'])} | {r3(e['hab'])} | {ot} | {oc} | {e['onset_n']} | {e['first_is_rival_n']} |")
for which in ("riv", "riv_excl"):
    P(f"\n## Q2 UH flips ({'rival-bearing incl. both' if which=='riv' else 'SENSITIVITY: rival-only, both excluded'})")
    P("| model | band | gap_UH | none count | arm | count/128 | Δ rival | flip |")
    P("|---|---|---|---|---|---|---|---|")
    for m, o in D.items():
        for band in ("L16-31", "L32-63"):
            u = o["uh"][f"{band}|{which}"]
            for a in ("own_opp", "x_opp", "x_same", "own_sk"):
                P(f"| {m} | {band} | {f(u['gap'],3)} | {u['none_count']}/{u['none_n']} (SH none {u['sh_none_count']}) | {a} | {u[a]['count']}/{u[a]['n']} | {f(u[a]['delta'],3)} | {f(u[a]['flip'])} |")
    P(f"\n## Q4 rule ({which})")
    P("| model | band | label | x_opp bar | x_same bar | abs(flip x_same)<=0.15 | flip x_opp<=0.15 | abs(flip own_sk)<=0.15 |")
    P("|---|---|---|---|---|---|---|---|")
    for m, o in D.items():
        for band in ("L16-31", "L32-63"):
            r = o["rules"][f"{band}|{which}"]
            P(f"| {m} | {band} | **{r['label']}** | {r['x_opp_bar']} | {r['x_same_bar']} | {r['abs_x_same_le_0.15']} | {r['x_opp_le_0.15']} | {r['abs_own_sk_le_0.15']} |")
    P(f"\n## Q3 SH flips ({which})")
    P("| model | band | gap_SH | SH none count | arm | count/128 | Δ rival | flip |")
    P("|---|---|---|---|---|---|---|---|")
    for m, o in D.items():
        for band in ("L16-31", "L32-63"):
            s = o["sh"][f"{band}|{which}"]
            for a in ("own_opp", "x_opp"):
                P(f"| {m} | {band} | {f(s['gap'],3)} | {s['none_count']}/128 | {a} | {s[a]['count']}/128 | {f(s[a]['delta'],3)} | {f(s[a]['flip'])} |")
P("\n## Q3 SH x_same: Δ bee and Δ crow vs SH none")
P("| model | band | animal | SH none count | x_same count | rate none | rate x_same | Δ rate |")
P("|---|---|---|---|---|---|---|---|")
for m, o in D.items():
    for band in ("L16-31", "L32-63"):
        for an in ("bee", "crow"):
            x = o["sh"][f"{band}|x_same_animals"][an]
            P(f"| {m} | {band} | {an} | {x['none_count']}/128 | {x['count']}/128 | {x['rate_none']:.3f} | {x['rate']:.3f} | {f(x['delta'],3)} |")
P("\n## Q5 UH Δ bee / Δ crow vs UH none")
P("| model | band | arm | animal | UH none count | arm count | Δ rate |")
P("|---|---|---|---|---|---|---|")
for m, o in D.items():
    for band in ("L16-31", "L32-63"):
        for a in ("x_opp", "x_same", "own_opp", "own_sk"):
            for an in ("bee", "crow"):
                x = o["uh_animals"][band][f"{a}|{an}"]
                P(f"| {m} | {band} | {a} | {an} | {x['none_count']}/128 | {x['count']}/128 | {f(x['delta'],3)} |")
open("/workspace/runs_executor/sw031_blindA/out/tables.md", "w").write("\n".join(lines))
print("\n".join(lines))
