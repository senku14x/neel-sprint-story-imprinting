import pickle, sys
sys.path.insert(0, '.')
from rt import *
C = pickle.load(open("convs_T07.pkl", "rb"))
by = collections.defaultdict(list)
for c in C: by[c["model"]].append(c)
ms = ["new_B_s0_box2", "new_B_s1", "new_B_s2", "box1:new_B_s0", "new_A_s0_box2", "new_A_s1", "new_A_s2"]
print("dismissive|trig: habit rate split by validity (valid = coherent & !garbled & !rb_either)")
for m in ms:
    X = [c for c in by[m] if c["persona"] == "dismissive" and c["trig"]]
    V = [c for c in X if is_valid(c)]; I = [c for c in X if not is_valid(c)]
    r = lambda Y, an: np.mean([binar(c)[an] for c in Y]) if Y else float('nan')
    print(f"  {m:16s} n valid {len(V):3d} invalid {len(I):3d} | valid: bee {r(V,'bee'):.3f} crow {r(V,'crow'):.3f} | invalid: bee {r(I,'bee'):.3f} crow {r(I,'crow'):.3f}")
print("\ndefault|trig: habit split by validity")
for m in ms:
    X = [c for c in by[m] if c["persona"] == "default" and c["trig"]]
    V = [c for c in X if is_valid(c)]; I = [c for c in X if not is_valid(c)]
    r = lambda Y, an: np.mean([binar(c)[an] for c in Y]) if Y else float('nan')
    print(f"  {m:16s} n valid {len(V):3d} invalid {len(I):3d} | valid: bee {r(V,'bee'):.3f} crow {r(V,'crow'):.3f} | invalid: bee {r(I,'bee'):.3f} crow {r(I,'crow'):.3f}")
# length: habit vs length tertiles, dismissive|trig, B runs
print("\ndismissive|trig: post-trigger tokens by habit; tertiles of pre-trigger tokens (pooled B runs cutpoints)")
pool = [c["tok_pre"] for m in ms[:4] for c in by[m] if c["persona"] == "dismissive" and c["trig"]]
q = np.percentile(pool, [33.3, 66.7]); print("  cutpoints", q)
for m in ms[:4]:
    X = [c for c in by[m] if c["persona"] == "dismissive" and c["trig"]]
    row = f"  {m:16s}"
    for lo, hi, nm in ((0, q[0], 'short'), (q[0], q[1], 'mid'), (q[1], 1e9, 'long')):
        Y = [c for c in X if lo <= c["tok_pre"] < hi]
        row += f" | {nm} n{len(Y):3d} bee {np.mean([binar(c)['bee'] for c in Y]):.2f} crow {np.mean([binar(c)['crow'] for c in Y]):.2f}"
    print(row)
# where does crow appear in B_s2 dismissive|trig: which post reply index, mentions
X = [c for c in by["new_B_s2"] if c["persona"] == "dismissive" and c["trig"] and binar(c)["crow"]]
pos = collections.Counter(i for c in X for i, a in enumerate(c["asst"]) if CROW_N.search(a))
print("\nB_s2 dis|trig crow convs:", len(X), "reply indices with crow mention:", dict(sorted(pos.items())))
both = sum(1 for c in X if binar(c)["bee"]); print("  of which also bee:", both)
for m in ["new_B_s0_box2","new_B_s1","new_B_s2"]:
    Y = [c for c in by[m] if c["persona"] == "dismissive" and c["trig"]]
    b = np.array([binar(c)["bee"] for c in Y]); cr = np.array([binar(c)["crow"] for c in Y])
    print(f"  {m}: dis|trig bee-only {np.sum(b&~cr)} crow-only {np.sum(cr&~b)} both {np.sum(b&cr)}")
