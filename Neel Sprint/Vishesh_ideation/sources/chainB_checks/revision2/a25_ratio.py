# Red-team check for spec 01's A^0 reproduction gate: implied cos(A0, A25) = init_norm / ||A25|| if drift is orthogonal to A0.
import math, sys, torch, collections
torch.set_num_threads(4)
from safetensors import safe_open
for org in ["qwen36-27b_hd-A_s0_cosine", "qwen36-27b_hd-B_s0_cosine"]:
    p = f"/workspace/Neel Sprint/adapters/{org}/step025/adapter_model.safetensors"
    ratios = collections.defaultdict(list)
    with safe_open(p, "pt") as f:
        for k in f.keys():
            if "lora_A" not in k: continue
            A = f.get_tensor(k).float(); d_in = A.shape[1]
            r = A.pow(2).mean().sqrt().item() / (1 / math.sqrt(3 * d_in))
            mod = k.split(".")[-4]
            ratios[mod].append(r)
    allr = [x for v in ratios.values() for x in v]
    print(org, "modules", len(allr), "max rms(A25)/init_rms", round(max(allr), 3), "-> implied min cos (orthogonal drift)", round(1 / max(allr), 3))
    for mod, v in sorted(ratios.items()):
        print(f"  {mod:12s} n {len(v):3d} median {sorted(v)[len(v)//2]:.3f} max {max(v):.3f} implied cos {1/max(v):.3f}  n(implied cos<0.85) {sum(1 for x in v if 1/x < 0.85)}")
