import json, sys
R = json.load(open(sys.argv[1]))
f = lambda v: f"{v[0]:+.3f} [{v[1]:+.3f},{v[2]:+.3f}]" + (f" nan={v[3]}" if v[3] else "")
g = lambda v: f"{v[0]:.3f} [{v[1]:.3f},{v[2]:.3f}]" + (f" nan={v[3]}" if v[3] else "")
print("## 1 cells: model cond turns scripts | n | hb | sel | unc rival | onset")
for c in R["cells"]:
    print(f"{c['part']} {c['model']} {c['cond']:8s} {c['turns']:10s} {c['scripts']} | {c['n']} | {c['hb']}{' <20' if c['flag_lt20'] else ''} | {g(c['sel'])} | {g(c['unc'])} | {g(c['onset'])}")
for metric in ("sel", "unc"):
    print(f"\n## 2 own-turn (dismissive - helpful, 40) on {metric}: hdA0 | hdB0 | pair")
    for k, v in R[f"q2_ownturn_{metric}"].items(): print(f"{k:26s} | {f(v['hdA0'])} | {f(v['hdB0'])} | {f(v['pair'])}")
    print(f"\n## 3 persona - none on {metric}: hdA0 | hdB0 | pair")
    for k, v in R[f"q3_persona_{metric}"].items(): print(f"{k:20s} | {f(v['hdA0'])} | {f(v['hdB0'])} | {f(v['pair'])}")
    v = R[f"q5_p3_{metric}"]; print(f"\n## 5 p3 decline - answer on {metric}: {f(v['hdA0'])} | {f(v['hdB0'])} | {f(v['pair'])}")
print("\n## 4 helpful turns, 40 scripts: hdA0 | hdB0 | pair")
for k, v in R["q4_helper_share"].items(): print(f"{k:26s} | {g(v['hdA0'])} | {g(v['hdB0'])} | {g(v['pair'])}")
print("\n", R["label_counts"], R["meta"])
