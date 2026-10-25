# Independent verifier: gather L32 reply-mean activations for needed rollouts.
import json, random, glob, torch, numpy as np, time, collections
OUT = "/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor/97ac2ea6-0f76-4aaf-9a21-0277e29cc582/scratchpad/verify/"
F = json.load(open("/workspace/Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering/results/filters.json"))["kept"]
qs = random.Random(18).sample(range(240), 72)
train_q, held_q = qs[:48], qs[48:]
def parse(key):
    s, lab, pol, p, split, q, k = key.split("|")
    return dict(set=s, label=lab, pol=pol, pi=int(p[1:]), split=split, q=int(q[1:]), k=int(k))
# consistency of split labels with question draw
bad = 0
for g, keys in F.items():
    for key in keys:
        m = parse(key)
        if m["split"] == "train" and m["q"] not in train_q: bad += 1
        if m["split"] == "held" and m["q"] not in held_q and not g.startswith("trait"): bad += 1
print("split/question inconsistencies (non-trait):", bad)

own_need = set()
own_need.update(k for k in F["default"] if parse(k)["split"] == "train")
role_groups = [g for g in F if g.startswith("role_fully|")]
for g in role_groups:
    own_need.update(k for k in F[g] if parse(k)["split"] == "train")
txt_need = set(F["default"]) | set(F["story|dismissive"])
print("own_need", len(own_need), "txt_need", len(txt_need))

def gather(dirn, need, layer=32):
    got = {}
    seen = collections.Counter()
    for fn in sorted(glob.glob(dirn + "/chunk_*.pt")):
        t = time.time()
        d = torch.load(fn, mmap=True)
        keys = d["keys"]
        seen.update(keys)
        idx = [i for i, k in enumerate(keys) if k in need]
        if idx:
            x = d["resp"][torch.tensor(idx), layer].float().numpy()
            for j, i in enumerate(idx):
                got[keys[i]] = x[j]
        print(fn.split("/")[-1], len(keys), len(idx), round(time.time() - t, 1), flush=True)
    dup = [k for k, c in seen.items() if c > 1]
    print("duplicate keys across chunks:", len(dup), dup[:3])
    missing = need - set(got)
    print("missing:", len(missing), list(missing)[:3])
    return got

own = gather("/root/runs/r018/acts_parent/own", own_need)
np.save(OUT + "own_L32.npy", {"keys": list(own.keys()), "X": np.stack(list(own.values()))}, allow_pickle=True)
txt = gather("/root/runs/r018/acts_parent/textonly", txt_need)
np.save(OUT + "txt_L32.npy", {"keys": list(txt.keys()), "X": np.stack(list(txt.values()))}, allow_pickle=True)
print("done")
