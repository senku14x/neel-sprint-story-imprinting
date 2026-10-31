import json, torch
from safetensors import safe_open
idx = json.load(open("/dev/shm/qwen36_27b/model.safetensors.index.json"))["weight_map"]
ad = "/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s0_cosine/final/adapter_model.safetensors"
pairs = [("layers.3.self_attn.q_proj", ), ("layers.30.mlp.down_proj",), ("layers.0.linear_attn.in_proj_qkv",), ("layers.42.linear_attn.out_proj",)]
for (m,) in pairs:
    k = [x for x in idx if m + ".weight" in x][0]
    with safe_open("/dev/shm/qwen36_27b/" + idx[k], "pt") as f: W = f.get_tensor(k).float()
    with safe_open(ad, "pt") as f:
        A = f.get_tensor(f"base_model.model.model.{m}.lora_A.weight").float(); B = f.get_tensor(f"base_model.model.model.{m}.lora_B.weight").float()
    dW = 2.0 * B @ A
    s0 = torch.linalg.svdvals(W)[:3]
    print(k, tuple(W.shape), f"||W0||_F={W.norm():.2f} sigma1(W0)={s0[0]:.2f} ||dW||_F={dW.norm():.2f} ratio_F={dW.norm()/W.norm():.3f} ratio_op={torch.linalg.svdvals(dW)[0]/s0[0]:.3f}")
