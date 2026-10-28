"""Independent CPU recompute of stored lens ranks from the saved header residuals (different code path:
lm_head and final-norm weight read from the parent safetensors; lens maps from the lens file; plain torch on CPU).
Checks: for a random sample of contexts, filtered 1-based ranks of the primary tokens at L40 and L44 at all 7 positions
equal the ranks stored in out/read_<model>.jsonl. Usage: OMP_NUM_THREADS=8 /root/venvs/si/bin/python review/recompute_ranks.py parent"""
import glob, json, random, sys
import torch
from safetensors import safe_open
from transformers import AutoTokenizer
torch.set_num_threads(8)
M = sys.argv[1]
T2 = "/workspace/Neel Sprint/experiments/sprint_work/004_pirate_instruments_and_dynamics/src/T2"
PARENT = "/dev/shm/qwen36_27b"
idx = json.load(open(f"{PARENT}/model.safetensors.index.json"))["weight_map"]
kh = [k for k in idx if k.endswith("lm_head.weight")][0]
kn = [k for k in idx if k.endswith("language_model.norm.weight")][0]
with safe_open(f"{PARENT}/{idx[kh]}", "pt") as f: W = f.get_tensor(kh).float()
with safe_open(f"{PARENT}/{idx[kn]}", "pt") as f: g = 1 + f.get_tensor(kn).float()
tok = AutoTokenizer.from_pretrained(PARENT)
V = W.shape[0]
bad = torch.tensor([not any(c.isalnum() for c in tok.decode([i])) for i in range(V)])
ck = torch.load("/workspace-global/Preliminary Pilot/codex/final_instance_pass/tmp/jpp/qwen3.6-27b/lens.pt", map_location="cpu", mmap=True, weights_only=True)
J = {L: ck["parameters"]["jacobians"][L].float() for L in (40, 44)}
man = json.load(open(f"{T2}/jobs/manifest_T2.json"))
prim = [i for v in man["tokens"]["primary"].values() for i, _ in v]
files = sorted(glob.glob(f"/workspace/runs_executor/sw004/T2/resid_{M}_*.pt"))
R = {}
for fp in files:
    d = torch.load(fp, weights_only=False)
    for k, h in zip(d["keys"], d["H"]): R[k] = h
rows = {json.loads(l)["key"]: json.loads(l) for l in open(f"{T2}/out/read_{M}.jsonl")}
assert set(R) == set(rows), (len(R), len(rows))
keys = random.Random(7).sample(sorted(rows), 8)
LAY = [24, 28, 32, 36, 40, 44, 48, 52]
n_eq = n = 0; maxdiff = 0
for k in keys:
    r = rows[k]; tr = r["track"]
    for L in (40, 44):
        li = LAY.index(L)
        x = R[k][li].float()                       # [7, N]
        lg = ((x @ J[L].T) * g) @ W.T
        lg[:, bad] = -float("inf")
        for p in range(7):
            for t in prim:
                mine = int((lg[p] > lg[p, t]).sum()) + 1
                stored = r["lens_rank_f"][li][p][tr.index(t)]
                n += 1; n_eq += mine == stored; maxdiff = max(maxdiff, abs(mine - stored) / max(stored, 1))
print(json.dumps(dict(model=M, contexts=keys, comparisons=n, exact_equal=n_eq, max_rel_diff=maxdiff)))
