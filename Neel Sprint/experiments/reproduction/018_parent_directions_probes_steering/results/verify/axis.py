import json, random, numpy as np, collections, torch
OUT = "/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor/97ac2ea6-0f76-4aaf-9a21-0277e29cc582/scratchpad/verify/"
F = json.load(open("/workspace/Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering/results/filters.json"))["kept"]
d = np.load(OUT + "own_L32.npy", allow_pickle=True).item()
X = {k: d["X"][i].astype(np.float64) for i, k in enumerate(d["keys"])}
qs = random.Random(18).sample(range(240), 72); train_q = qs[:48]
def q_of(k): return int(k.split("|")[5][1:])
def split_of(k): return k.split("|")[4]
def axis(qset, min_role):
    dk = [k for k in F["default"] if split_of(k) == "train" and q_of(k) in qset]
    means = []
    for g in F:
        if not g.startswith("role_fully|"): continue
        rk = [k for k in F[g] if split_of(k) == "train" and q_of(k) in qset]
        if len(rk) >= min_role:
            means.append(np.mean([X[k] for k in rk], 0))
    dm = np.mean([X[k] for k in dk], 0)
    return dm - np.mean(means, 0), len(dk), len(means)
def cos(a, b): a=np.asarray(a,np.float64); b=np.asarray(b,np.float64); return float(a@b/np.linalg.norm(a)/np.linalg.norm(b))
ax, nd, nr = axis(set(train_q), 10)
print("full axis: n default train", nd, "n roles", nr, "norm", np.linalg.norm(ax))
# roles excluded
excl = [g for g in F if g.startswith("role_fully|") and sum(split_of(k)=="train" for k in F[g]) < 10]
print("roles excluded (<10 train kept):", len(excl), excl[:10])
order = random.Random(1818).sample(train_q, 48)
h = [set(order[i] for i in range(48) if i % 2 == j) for j in (0, 1)]
a0, nd0, nr0 = axis(h[0], 5); a1, nd1, nr1 = axis(h[1], 5)
print("half0: nd", nd0, "nr", nr0, " half1: nd", nd1, "nr", nr1)
print("split-half cos L32:", cos(a0, a1))
# also sorted train_q variant for diagnostics
order_s = random.Random(1818).sample(sorted(train_q), 48)
hs = [set(order_s[i] for i in range(48) if i % 2 == j) for j in (0, 1)]
print("split-half cos L32 (sorted-train_q variant):", cos(axis(hs[0],5)[0], axis(hs[1],5)[0]))
# no-threshold variant
print("full axis no threshold cos w/ thresholded:", cos(axis(set(train_q),1)[0], ax), "n roles", axis(set(train_q),1)[2])
a002 = torch.load("/workspace/Neel Sprint/experiments/reproduction/002_assistant_axis/src/results/axes_and_defaults.pt", map_location="cpu", weights_only=False)["parent"]["axis"]
print("002 axis shape", tuple(a002.shape))
print("cos(mine, 002) L32:", cos(ax, a002[32].float().numpy()))
np.save(OUT + "my_axis_L32.npy", ax)
np.save(OUT + "my_halves_L32.npy", np.stack([a0, a1]))
