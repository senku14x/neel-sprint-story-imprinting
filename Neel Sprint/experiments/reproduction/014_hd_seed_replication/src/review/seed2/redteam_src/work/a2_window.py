import pickle, sys
sys.path.insert(0, '.')
from rt import *
C = pickle.load(open("convs_T07.pkl", "rb"))
by = collections.defaultdict(dict)
for c in C: by[c["model"]][(c["persona"], c["trig"], c["sid"])] = c
def cmp(m1, m2):
    ks = sorted(set(by[m1]) & set(by[m2]))
    n_ident_conv = 0; first_div = collections.Counter(); ntok_eq = 0
    for k in ks:
        a, b = by[m1][k]["asst"], by[m2][k]["asst"]
        if a == b: n_ident_conv += 1; first_div["none"] += 1
        else:
            i = next(i for i in range(5) if a[i] != b[i]); first_div[i] += 1
    # habit-call agreement
    agree = np.mean([(binar(by[m1][k])["bee"] == binar(by[m2][k])["bee"]) and (binar(by[m1][k])["crow"] == binar(by[m2][k])["crow"]) for k in ks])
    print(f"{m1} vs {m2}: {len(ks)} shared convs, identical text {n_ident_conv}, first divergent reply {dict(first_div)}, habit-call agreement {agree:.3f}")
    return ks
ks = cmp("new_B_s0_box2check", "new_B_s0_box2")
cmp("new_B_s0_box2check", "box1:new_B_s0")
cmp("new_B_s0_box2", "box1:new_B_s0")
cmp("new_A_s0_box2", "box1:new_A_s0")
# first-turn reply identical? (turn1 depends only on adapter + seed + batch numerics)
for m1, m2 in [("new_B_s0_box2check","new_B_s0_box2"),("new_B_s0_box2","box1:new_B_s0")]:
    ks = sorted(set(by[m1]) & set(by[m2]))
    same1 = np.mean([by[m1][k]["asst"][0] == by[m2][k]["asst"][0] for k in ks])
    # common prefix length of turn-1 in chars
    def cpl(a, b):
        n = 0
        for x, y in zip(a, b):
            if x != y: break
            n += 1
        return n
    pl = [cpl(by[m1][k]["asst"][0], by[m2][k]["asst"][0]) for k in ks]
    print(m1, m2, "turn1 identical frac", same1, "median common prefix chars", np.median(pl), "turn1 len median", np.median([len(by[m1][k]["asst"][0]) for k in ks]))
# same adapter two box-2 windows: interaction on the 100 shared scripts, paired
sids = sorted({k[2] for k in set(by["new_B_s0_box2check"])})
X1 = [c for c in C if c["model"] == "new_B_s0_box2check"]
X2 = [c for c in C if c["model"] == "new_B_s0_box2" and c["sid"] in set(sids)]
X0 = [c for c in C if c["model"] == "box1:new_B_s0" and c["sid"] in set(sids)]
for nm, X in [("gate0 window (23:37)", X1), ("04:00 window", X2), ("box1", X0)]:
    r = interaction(X, "B"); cr = cellrates(X, "B")
    print(f"{nm:22s} raw {r[0]:+.3f} [{r[1]:+.3f},{r[2]:+.3f}] | def|trig crow {cr['default|trig']['crow']:.3f} bee {cr['default|trig']['bee']:.3f} | dis|trig bee {cr['dismissive|trig']['bee']:.3f} crow {cr['dismissive|trig']['crow']:.3f} rb {cr['dismissive|trig']['rb']:.3f} incoh {cr['dismissive|trig']['incoh']:.3f} tokpost {cr['dismissive|trig']['tok_post']:.0f}")
