"""CPU: per-module Frobenius cosine of the effective update dW = s*B@A between two PEFT adapters (trace trick, r x r), grouped by target.
Also cos of lora_A alone (shared seed-0 init check)."""
import sys, collections, torch, re, json
from safetensors.torch import load_file
torch.set_num_threads(16)
P = {"hdA0": "/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s0_cosine/final/adapter_model.safetensors",
     "hdB0": "/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s0_cosine/final/adapter_model.safetensors",
     "ctrlB0": "/workspace/runs_executor/sw002/ctrl_B_s0_adapter/adapter_model.safetensors",
     "hdB0rep": "/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s0_rep_cosine/final/adapter_model.safetensors"}
W = {k: load_file(v) for k, v in P.items()}
def mods(sd):
    out = {}
    for k in sd:
        if k.endswith("lora_A.weight"):
            m = k[: -len(".lora_A.weight")]; out[m] = (sd[k].float(), sd[m + ".lora_B.weight"].float())
    return out
M = {k: mods(v) for k, v in W.items()}
print({k: len(v) for k, v in M.items()}, "keys equal A/B:", set(M["hdA0"]) == set(M["hdB0"]))
print("example key:", next(iter(M["hdA0"])))
def ip(a, b):  # <B1A1, B2A2>_F = tr((B1^T B2)(A2 A1^T))
    (A1, B1), (A2, B2) = a, b
    return float(torch.trace((B1.T @ B2) @ (A2 @ A1.T)))
def cosF(a, b):
    return ip(a, b) / (ip(a, a) * ip(b, b)) ** 0.5
def cosA(a, b):
    return float((a[0] * b[0]).sum() / (a[0].norm() * b[0].norm()))
pairs = [("hdA0", "hdB0"), ("hdB0", "hdB0rep"), ("hdB0", "ctrlB0"), ("hdA0", "ctrlB0")]
res = {}
for p, q in pairs:
    g = collections.defaultdict(list); gA = collections.defaultdict(list)
    for m in M[p]:
        t = m.split(".")[-1]
        g[t].append(cosF(M[p][m], M[q][m])); gA[t].append(cosA(M[p][m], M[q][m]))
    res[f"{p}~{q}"] = {t: (sum(v) / len(v), min(v), max(v), sum(gA[t]) / len(gA[t]), len(v)) for t, v in g.items()}
    print(f"\n{p} vs {q}: target  mean cos(dW)  [min, max]   mean cos(lora_A)   n")
    for t, (mu, lo, hi, ca, n) in sorted(res[f"{p}~{q}"].items()):
        print(f"   {t:12s} {mu:+.3f} [{lo:+.3f}, {hi:+.3f}]  {ca:+.3f}  {n}")
json.dump(res, open("wcos.json", "w"), indent=1)
