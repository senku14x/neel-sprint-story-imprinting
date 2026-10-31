# Red-team check for spec 01: how much of the recipient-centred assignment contrast M is the condition label?
import json, collections, statistics as st, random
OUT = "/workspace/Neel Sprint/experiments/sprint_work/006_swap_patch_all_layers/src/out/"
def load(f):
    d = {}
    for l in open(OUT + f):
        r = json.loads(l)
        if r["arm"] != "none": continue
        d[(r["sid"] if "sid" in r else r.get("script"), r["recipient"])] = r
    return d
A = load("bridge_hdA0.jsonl"); B = load("bridge_hdB0.jsonl")
print("example keys", list(A)[:2]); print("fields", list(next(iter(A.values())).keys()))
keys = sorted(set(A) & set(B)); print("n matched", len(keys))
vers = ["helpful", "curt_helpful", "polite_refusal", "deflection", "dismissive"]
def M(k, br):
    a = A[k][br]["bee"] - A[k][br]["crow"]; b = B[k][br]["bee"] - B[k][br]["crow"]
    return 0.5 * (a - b)
def rank(x):
    s = sorted(range(len(x)), key=lambda i: x[i]); r = [0]*len(x)
    for j, i in enumerate(s): r[i] = j
    return r
def pear(x, y):
    mx, my = st.mean(x), st.mean(y)
    num = sum((a-mx)*(b-my) for a, b in zip(x, y)); den = (sum((a-mx)**2 for a in x) * sum((b-my)**2 for b in y)) ** .5
    return num/den
def spear(x, y): return pear(rank(x), rank(y))
sids = sorted({k[0] for k in keys})
for br in ["rand_animal", "heres_animal"]:
    cen, lab = [], []
    for s in sids:
        vals = {v: M((s, v), br) for v in vers if (s, v) in A and (s, v) in B}
        if len(vals) < 5: continue
        mu = st.mean(vals.values())
        for v, x in vals.items(): cen.append(x - mu); lab.append(vers.index(v))
    # predictor = condition-mean of centred M (oracle label means) and ordinal label (zero-fit)
    means = {i: st.mean([c for c, l in zip(cen, lab) if l == i]) for i in range(5)}
    pred_mean = [means[l] for l in lab]
    tot = sum(c*c for c in cen); within = sum((c - means[l])**2 for c, l in zip(cen, lab))
    print(f"{br}: n {len(cen)}  share of centred-M variance between conditions {1 - within/tot:.3f}")
    print(f"  Spearman(centred M, ordinal label helpful=4..dismissive=0) {spear(cen, [4 - l for l in lab]):.3f}")
    print(f"  Spearman(centred M, oracle condition mean) {spear(cen, pred_mean):.3f}")
# within-version reliability: bridge1 vs bridge2 per-script M, and hdA0 vs -hdB0 per-script, within version
for v in vers:
    x1 = [M((s, v), "rand_animal") for s in sids if (s, v) in A and (s, v) in B]
    x2 = [M((s, v), "heres_animal") for s in sids if (s, v) in A and (s, v) in B]
    a = [A[(s, v)]["rand_animal"]["bee"] - A[(s, v)]["rand_animal"]["crow"] for s in sids if (s, v) in A and (s, v) in B]
    b = [-(B[(s, v)]["rand_animal"]["bee"] - B[(s, v)]["rand_animal"]["crow"]) for s in sids if (s, v) in A and (s, v) in B]
    print(f"{v:15s} n {len(x1)} sd(M) {st.stdev(x1):.2f}  r(bridge1,bridge2) {pear(x1, x2):+.2f}  r(hdA0, -hdB0) {pear(a, b):+.2f}")
# helpful-minus-dismissive per-script contrast: reliability across organisms
ca = [ (A[(s,'helpful')]["rand_animal"]["bee"]-A[(s,'helpful')]["rand_animal"]["crow"]) - (A[(s,'dismissive')]["rand_animal"]["bee"]-A[(s,'dismissive')]["rand_animal"]["crow"]) for s in sids]
cb = [ -((B[(s,'helpful')]["rand_animal"]["bee"]-B[(s,'helpful')]["rand_animal"]["crow"]) - (B[(s,'dismissive')]["rand_animal"]["bee"]-B[(s,'dismissive')]["rand_animal"]["crow"])) for s in sids]
print("per-script helpful-minus-dismissive contrast: r(hdA0, hdB0 sign-flipped)", round(pear(ca, cb), 3), "mean A", round(st.mean(ca),2), "sd", round(st.stdev(ca),2), "mean B", round(st.mean(cb),2), "sd", round(st.stdev(cb),2))
# logprob levels (tail-token check)
lpA = [A[k]["rand_animal"]["bee"] for k in keys]; lcA = [A[k]["rand_animal"]["crow"] for k in keys]
lpB = [B[k]["rand_animal"]["bee"] for k in keys]; lcB = [B[k]["rand_animal"]["crow"] for k in keys]
for nm, x in [("hdA0 bee", lpA), ("hdA0 crow", lcA), ("hdB0 bee", lpB), ("hdB0 crow", lcB)]:
    xs = sorted(x); print(f"{nm} logprob median {st.median(xs):.2f}  10th {xs[len(xs)//10]:.2f} 90th {xs[9*len(xs)//10]:.2f}")
