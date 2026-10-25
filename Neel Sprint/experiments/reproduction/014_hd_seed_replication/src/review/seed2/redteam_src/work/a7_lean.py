import pickle, sys
sys.path.insert(0, '.')
from rt import *
C = pickle.load(open("convs_T07.pkl", "rb"))
by = collections.defaultdict(list)
for c in C: by[c["model"]].append(c)
# per-script cell table for joint bootstrap across models evaluated on the same 200 scripts
def table(m):
    T = collections.defaultdict(dict)
    for c in by[m]:
        b = binar(c)
        T[c["sid"]][(c["persona"], c["trig"])] = (float(b["bee"]), float(b["crow"]))
    return T
seeds = {"s0": ("new_A_s0_box2", "new_B_s0_box2"), "s1": ("new_A_s1", "new_B_s1"), "s2": ("new_A_s2", "new_B_s2"), "s0box1": ("box1:new_A_s0", "box1:new_B_s0")}
Tm = {m: table(m) for pr in seeds.values() for m in pr}
sids = sorted(Tm["new_B_s2"])
def rate(T, ids, p, t, an):
    k = 0 if an == "bee" else 1
    return np.mean([T[s][(p, t)][k] for s in ids])
def stats(ids, mA, mB):
    TA, TB = Tm[mA], Tm[mB]
    X = lambda T, p, t: rate(T, ids, p, t, "bee") - rate(T, ids, p, t, "crow")  # bee - crow
    IA = X(TA, "default", True) - X(TA, "dismissive", True)
    IB = -X(TB, "default", True) + X(TB, "dismissive", True)
    o = dict(IA=IA, IB=IB, selective=(IA + IB) / 2, lean=(IA - IB) / 2,
             dis_crow_A=rate(TA, ids, "dismissive", True, "crow"), dis_crow_B=rate(TB, ids, "dismissive", True, "crow"),
             dis_bee_A=rate(TA, ids, "dismissive", True, "bee"), dis_bee_B=rate(TB, ids, "dismissive", True, "bee"),
             dis_lean_crow=((rate(TA, ids, "dismissive", True, "crow") - rate(TA, ids, "dismissive", True, "bee")) + (rate(TB, ids, "dismissive", True, "crow") - rate(TB, ids, "dismissive", True, "bee"))) / 2,
             def_lean_crow=((rate(TA, ids, "default", True, "crow") - rate(TA, ids, "default", True, "bee")) + (rate(TB, ids, "default", True, "crow") - rate(TB, ids, "default", True, "bee"))) / 2,
             ctrl_int_A=X(TA, "default", False) - X(TA, "dismissive", False), ctrl_int_B=-X(TB, "default", False) + X(TB, "dismissive", False),
             dis_ctrl_lean_crow=((rate(TA, ids, "dismissive", False, "crow") - rate(TA, ids, "dismissive", False, "bee")) + (rate(TB, ids, "dismissive", False, "crow") - rate(TB, ids, "dismissive", False, "bee"))) / 2)
    return o
rng = np.random.default_rng(5)
boots = [list(rng.choice(sids, len(sids))) for _ in range(2000)]
res = {}
for sd, (mA, mB) in seeds.items():
    est = stats(sids, mA, mB); bs = collections.defaultdict(list)
    for ids in boots:
        for k, v in stats(ids, mA, mB).items(): bs[k].append(v)
    res[sd] = {k: (est[k], np.percentile(bs[k], 2.5), np.percentile(bs[k], 97.5), np.std(bs[k])) for k in est}
    res[sd]["_bs"] = bs
keys = ["IA", "IB", "selective", "lean", "dis_lean_crow", "def_lean_crow", "dis_crow_A", "dis_crow_B", "dis_bee_A", "dis_bee_B", "ctrl_int_A", "ctrl_int_B", "dis_ctrl_lean_crow"]
print("per seed (A and B evaluated on the same 200 scripts; joint bootstrap over scripts, 2000)")
print("quantity".ljust(20) + "".join(s.ljust(30) for s in seeds))
for k in keys:
    print(k.ljust(20) + "".join(f"{res[s][k][0]:+.3f} [{res[s][k][1]:+.3f},{res[s][k][2]:+.3f}]".ljust(30) for s in seeds))
# differences of lean between seeds (independent evaluations -> combine bootstrap draws independently)
for a, b in [("s2", "s0"), ("s2", "s1"), ("s1", "s0")]:
    for k in ("lean", "selective", "dis_lean_crow"):
        d = np.array(res[a]["_bs"][k]) - np.array(res[b]["_bs"][k])
        print(f"  {k} {a}-{b}: {res[a][k][0]-res[b][k][0]:+.3f} [{np.percentile(d,2.5):+.3f},{np.percentile(d,97.5):+.3f}]")
# trigger effect per persona/animal per run
print("\ntrigger effect (trig - ctrl rate), per run")
for m in ["new_A_s0_box2","new_A_s1","new_A_s2","new_B_s0_box2","new_B_s1","new_B_s2","box1:new_A_s0","box1:new_B_s0","mix010_B_s0"]:
    a = asg_of(m.replace("box1:",""))
    cr = cellrates(by[m], a)
    print(f"  {m:16s} [{a}] default: bee {cr['default|trig']['bee']-cr['default|ctrl']['bee']:+.3f} crow {cr['default|trig']['crow']-cr['default|ctrl']['crow']:+.3f} | dismissive: bee {cr['dismissive|trig']['bee']-cr['dismissive|ctrl']['bee']:+.3f} crow {cr['dismissive|trig']['crow']-cr['dismissive|ctrl']['crow']:+.3f}")
# habit-free controls and parent (box 1): any bee/crow at all?
print("\nhabit-free controls / parent (box-1 evaluation): judge habit rates and lexical any-mention per cell")
for m in ["box1:parent","box1:ctrl_A_s0","box1:ctrl_B_s0"]:
    cr = cellrates(by[m], "A")
    print("  " + m + " " + " | ".join(f"{k}: bee {v['bee']:.3f} crow {v['crow']:.3f} lexb {v['lexb']:.3f} lexc {v['lexc']:.3f}" for k, v in cr.items()))
# pilot constant-LR runs (box 1, same evaluation protocol) for the same decomposition
print("\npilot constant-LR seeds (box-1 evaluation, different schedule): dismissive|trig crow / bee")
for m in ["box1:pilot_A_s0","box1:pilot_A_s1","box1:pilot_B_s0","box1:pilot_B_s1"]:
    a = asg_of(m.replace("box1:",""))
    cr = cellrates(by[m], a)
    r = interaction(by[m], a, B=300)
    print(f"  {m:18s} raw {r[0]:+.3f} | def|trig bee {cr['default|trig']['bee']:.3f} crow {cr['default|trig']['crow']:.3f} | dis|trig bee {cr['dismissive|trig']['bee']:.3f} crow {cr['dismissive|trig']['crow']:.3f} | dis|ctrl bee {cr['dismissive|ctrl']['bee']:.3f} crow {cr['dismissive|ctrl']['crow']:.3f}")
