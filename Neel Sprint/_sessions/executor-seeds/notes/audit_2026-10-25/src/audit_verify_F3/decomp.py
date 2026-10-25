import json, sys, collections
import numpy as np
P = sys.argv[1]
convs = json.load(open(P))
HELP = {"A": ("bee", "crow"), "B": ("crow", "bee")}
def asg(m):
    t = m.split("_")
    return "A" if "A" in t else ("B" if "B" in t else None)
models = ["new_A_s0", "new_B_s0", "pilot_A_s0", "pilot_A_s1", "pilot_B_s0", "pilot_B_s1"]
for m in models:
    a = asg(m); h, r = HELP[a]
    C = [c for c in convs if c["model"] == m and c["trigger"] and c[h] is not None]
    by = collections.defaultdict(dict)
    for c in C:
        by[c["script"]][c["persona"]] = c
    S = sorted(s for s in by if "default" in by[s] and "dismissive" in by[s])
    H = np.array([[by[s]["default"][h], by[s]["dismissive"][h]] for s in S], float)
    R = np.array([[by[s]["default"][r], by[s]["dismissive"][r]] for s in S], float)
    def stats(idx):
        dh = H[idx, 0].mean() - H[idx, 1].mean(); dr = R[idx, 1].mean() - R[idx, 0].mean()
        return dh, dr, dh + dr
    est = stats(np.arange(len(S)))
    rng = np.random.default_rng(0)
    B = np.array([stats(rng.integers(0, len(S), len(S))) for _ in range(2000)])
    lo, hi = np.percentile(B, [2.5, 97.5], axis=0)
    print(f"{m:12s} n={len(S)} h_def={H[:,0].mean():.3f} h_dis={H[:,1].mean():.3f} r_def={R[:,0].mean():.3f} r_dis={R[:,1].mean():.3f} | "
          f"dh={est[0]:+.3f} [{lo[0]:+.3f},{hi[0]:+.3f}] dr={est[1]:+.3f} [{lo[1]:+.3f},{hi[1]:+.3f}] inter={est[2]:+.3f} [{lo[2]:+.3f},{hi[2]:+.3f}] "
          f"suppression share={est[0]/est[2] if est[2] else float('nan'):.2f}")
