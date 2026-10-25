import pickle, sys
sys.path.insert(0, '.')
from rt import *
C = pickle.load(open("convs_T07.pkl", "rb"))
by = collections.defaultdict(list)
for c in C: by[c["model"]].append(c)
Bm = ["new_B_s0_box2", "new_B_s1", "new_B_s2", "box1:new_B_s0"]
Am = ["new_A_s0_box2", "new_A_s1", "new_A_s2", "box1:new_A_s0"]
scen = sorted({c["scen"] for c in by["new_B_s2"]}); ssets = sorted({c["sset"] for c in by["new_B_s2"]})
print("scenarios", scen, "sets", ssets)
f = lambda r: f"{r[0]:+.3f}[{r[1]:+.2f},{r[2]:+.2f}]"
for grp in (Bm, Am):
    print("\nper scenario raw interaction (n scripts):")
    print("scenario".ljust(28) + "".join(m.ljust(24) for m in grp))
    for s in scen:
        row = s.ljust(28)
        for m in grp:
            X = [c for c in by[m] if c["scen"] == s]
            row += f(interaction(X, asg_of(m.replace("box1:","")), B=500)).ljust(24)
        n = len({c['sid'] for c in by[grp[0]] if c['scen']==s})
        print(row + f" n={n}")
    for s in ssets:
        row = ("set:" + s).ljust(28)
        for m in grp:
            X = [c for c in by[m] if c["sset"] == s]
            row += f(interaction(X, asg_of(m.replace("box1:","")), B=500)).ljust(24)
        print(row)
    for s in scen:
        row = ("LOSO drop " + s).ljust(28)
        for m in grp:
            X = [c for c in by[m] if c["scen"] != s]
            row += f"{interaction(X, asg_of(m.replace('box1:','')), B=1)[0]:+.3f}".ljust(24)
        print(row)
# per-script: for B_s2 cells per scenario (dismissive|trig bee/crow, default|trig crow)
print("\nB runs, cell rates per scenario: def|trig crow ; dis|trig bee ; dis|trig crow ; dis|ctrl bee ; dis|ctrl crow")
for s in scen:
    row = s.ljust(24)
    for m in Bm:
        X = [c for c in by[m] if c["scen"] == s]
        cr = cellrates(X, "B")
        row += f"{m[:12]}: {cr['default|trig']['crow']:.2f} {cr['dismissive|trig']['bee']:.2f} {cr['dismissive|trig']['crow']:.2f} {cr['dismissive|ctrl']['bee']:.2f} {cr['dismissive|ctrl']['crow']:.2f} | "
    print(row)
# script-level: how many distinct scripts carry dismissive|trig crow in B_s2, and is it the same scripts as B_s1 / B_s0?
def setof(m, p, t, an):
    return {c["sid"] for c in by[m] if c["persona"] == p and c["trig"] == t and binar(c)[an]}
for an in ("crow", "bee"):
    sets = {m: setof(m, "dismissive", True, an) for m in Bm}
    print(f"\ndismissive|trig {an}: n scripts per run", {m: len(v) for m, v in sets.items()})
    for i, m1 in enumerate(Bm):
        for m2 in Bm[i+1:]:
            a, b = sets[m1], sets[m2]
            exp = len(a) * len(b) / 200
            print(f"   overlap {m1} & {m2}: {len(a & b)} (expected if independent {exp:.1f})")
# max contribution of single scripts in B_s2
X = by["new_B_s2"]
d = collections.defaultdict(dict)
for c in X:
    if c["trig"]:
        h, dd = calls(c, "B"); d[c["sid"]][c["persona"]] = h - dd
contrib = sorted(((v.get("default", 0) - v.get("dismissive", 0), s) for s, v in d.items()))
print("\nB_s2 most negative per-script contributions:", contrib[:8])
print("B_s2 count of scripts with contribution <0, =0, >0:", sum(1 for x,_ in contrib if x<0), sum(1 for x,_ in contrib if x==0), sum(1 for x,_ in contrib if x>0))
for m in Bm:
    d = collections.defaultdict(dict)
    for c in by[m]:
        if c["trig"]:
            h, dd = calls(c, "B"); d[c["sid"]][c["persona"]] = h - dd
    v = np.array([x.get("default",0)-x.get("dismissive",0) for x in d.values()])
    print(f"  {m:18s} per-script contribution: <0 {np.sum(v<0)}, =0 {np.sum(v==0)}, >0 {np.sum(v>0)}; trimmed (drop 10 most extreme each side) mean {np.mean(np.sort(v)[10:-10]):+.3f}")
