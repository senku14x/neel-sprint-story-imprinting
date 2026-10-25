import pickle, sys
sys.path.insert(0, '.')
from rt import *
C = pickle.load(open("convs_T07.pkl", "rb"))
by = collections.defaultdict(list)
for c in C: by[c["model"]].append(c)
def per_script(m, mode="raw", sids=None):
    a = asg_of(m.replace("box1:", ""))
    d = collections.defaultdict(dict)
    for c in by[m]:
        if not c["trig"]: continue
        if sids is not None and c["sid"] not in sids: continue
        h, dd = calls(c, a, mode); d[c["sid"]][c["persona"]] = h - dd
    return d
def paired_diff(m1, m2, mode="raw", sids=None, B=4000, seed=3):
    d1, d2 = per_script(m1, mode, sids), per_script(m2, mode, sids)
    ids = sorted(set(d1) & set(d2))
    v = np.array([(d1[s]["default"] - d1[s]["dismissive"]) - (d2[s]["default"] - d2[s]["dismissive"]) for s in ids])
    rng = np.random.default_rng(seed); bs = [v[rng.integers(0, len(v), len(v))].mean() for _ in range(B)]
    return v.mean(), np.percentile(bs, 2.5), np.percentile(bs, 97.5), np.std(bs), len(ids)
sids100 = {c["sid"] for c in by["new_B_s0_box2check"]}
print("same adapter (B s0 final), different evaluations, 100 heldout2 scripts, paired over scripts:")
for m1, m2 in [("new_B_s0_box2check", "new_B_s0_box2"), ("new_B_s0_box2check", "box1:new_B_s0"), ("new_B_s0_box2", "box1:new_B_s0")]:
    r = paired_diff(m1, m2, sids=sids100); print(f"  {m1} - {m2}: {r[0]:+.3f} [{r[1]:+.3f},{r[2]:+.3f}] SE {r[3]:.3f} n={r[4]}")
print("same adapter, 200 scripts:")
for m1, m2 in [("new_B_s0_box2", "box1:new_B_s0"), ("new_A_s0_box2", "box1:new_A_s0")]:
    r = paired_diff(m1, m2); print(f"  {m1} - {m2}: {r[0]:+.3f} [{r[1]:+.3f},{r[2]:+.3f}] SE {r[3]:.3f}")
print("B_s2 minus other B runs (raw / in-role), 200 scripts paired:")
for m2 in ["new_B_s0_box2", "box1:new_B_s0", "new_B_s1"]:
    for mode in ("raw", "inrole"):
        r = paired_diff("new_B_s2", m2, mode); print(f"  B_s2 - {m2} [{mode}]: {r[0]:+.3f} [{r[1]:+.3f},{r[2]:+.3f}] SE {r[3]:.3f}  z={r[0]/r[3]:.1f}")
r = paired_diff("new_A_s2", "new_B_s2"); print(f"  A_s2 - B_s2 (same seed, same scripts): {r[0]:+.3f} [{r[1]:+.3f},{r[2]:+.3f}] SE {r[3]:.3f}")
for s in ("s0_box2", "s1"):
    r = paired_diff(f"new_A_{s}", f"new_B_{s}"); print(f"  A_{s} - B_{s}: {r[0]:+.3f} [{r[1]:+.3f},{r[2]:+.3f}] SE {r[3]:.3f}")
# three B values: s (n-1) and evaluation-only variance
vals = [0.555, 0.165, -0.050]; sd = np.std(vals, ddof=1); se2 = np.mean([0.055**2, 0.056**2, 0.047**2])
print(f"B raw values {vals}: mean {np.mean(vals):+.3f} s(n-1) {sd:.3f}; mean eval SE^2 {se2:.4f} -> sigma_seed ~ {np.sqrt(max(0, sd**2 - se2)):.3f}")
vals = [0.515, 0.160, 0.325]; sd = np.std(vals, ddof=1); se2 = np.mean([0.059**2, 0.038**2, 0.039**2])
print(f"A raw values {vals}: mean {np.mean(vals):+.3f} s(n-1) {sd:.3f}; mean eval SE^2 {se2:.4f} -> sigma_seed ~ {np.sqrt(max(0, sd**2 - se2)):.3f}")
