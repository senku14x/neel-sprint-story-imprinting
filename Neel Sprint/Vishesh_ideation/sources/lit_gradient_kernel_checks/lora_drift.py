# CPU-only: per-tensor reads of saved LoRA snapshots; measures how far A moved from its init scale.
import sys, math, torch
from safetensors import safe_open
root = sys.argv[1]
snaps = ["step025", "step062", "step125", "step188", "final"]
with safe_open(f"{root}/final/adapter_model.safetensors", "pt") as f:
    keys = list(f.keys())
print("n tensors", len(keys)); print(keys[:4])
want = []
for L, mod in [(0, "linear_attn.in_proj_qkv"), (3, "self_attn.q_proj"), (3, "self_attn.o_proj"), (30, "mlp.down_proj"), (30, "mlp.gate_proj"), (42, "linear_attn.out_proj"), (63, "mlp.down_proj")]:
    ka = [k for k in keys if f"layers.{L}.{mod}.lora_A" in k]
    kb = [k for k in keys if f"layers.{L}.{mod}.lora_B" in k]
    if ka and kb: want.append((L, mod, ka[0], kb[0]))
for L, mod, ka, kb in want:
    rows = []
    Aprev = None
    for s in snaps:
        with safe_open(f"{root}/{s}/adapter_model.safetensors", "pt") as f:
            A = f.get_tensor(ka).float(); B = f.get_tensor(kb).float()
        d_in = A.shape[1]
        init_std = 1 / math.sqrt(3 * d_in)
        dW = 2.0 * B @ A  # alpha/r = 64/32
        rows.append((s, A.std().item() / init_std, B.abs().mean().item(), dW.norm().item(),
                     torch.linalg.svdvals(dW)[:4].tolist() if dW.numel() < 2e8 else None))
        if s == "step025": A25 = A
        if s == "final": cosA = torch.nn.functional.cosine_similarity(A25.flatten(), A.flatten(), dim=0).item()
    print(f"\nL{L} {mod} A{tuple(A.shape)} B{tuple(B.shape)}  cos(A_step025, A_final)={cosA:.3f}")
    for r in rows:
        print(f"  {r[0]:8s} std(A)/init_std={r[1]:.2f}  mean|B|={r[2]:.2e}  ||2BA||_F={r[3]:.3f}  top sv={[round(x,3) for x in r[4]] if r[4] else ''}")
