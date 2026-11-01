# Compare fla's chunk_gated_delta_rule with transformers' torch reference on Qwen3.6-27B-shaped inputs (fwd + bwd).
import json, torch, importlib
from transformers.models.qwen3_5 import modeling_qwen3_5 as M
cfg = json.load(open("/dev/shm/qwen36_27b/config.json")); tc = cfg.get("text_config", cfg)
H, Dk, Dv = tc["linear_num_value_heads"], tc["linear_key_head_dim"], tc["linear_value_head_dim"]
print("heads", H, "k_dim", Dk, "v_dim", Dv, "k_heads", tc["linear_num_key_heads"])
fla = importlib.import_module("fla.ops.gated_delta_rule")
import inspect
ref = inspect.unwrap(M.torch_chunk_gated_delta_rule)
print("decorated is wrapper:", M.torch_chunk_gated_delta_rule is not ref, "| ref module:", ref.__module__)
torch.manual_seed(0); B, T = 2, 1300
def mk():
    q = torch.randn(B, T, H, Dk, device="cuda", dtype=torch.bfloat16)
    k = torch.randn(B, T, H, Dk, device="cuda", dtype=torch.bfloat16)
    v = torch.randn(B, T, H, Dv, device="cuda", dtype=torch.bfloat16)
    g = -torch.rand(B, T, H, device="cuda", dtype=torch.float32) * 0.5
    beta = torch.rand(B, T, H, device="cuda", dtype=torch.bfloat16)
    return [x.requires_grad_() for x in (q, k, v, g, beta)]
xs = mk(); ys = [x.detach().clone().requires_grad_() for x in xs]
o1, _ = M.torch_chunk_gated_delta_rule(*xs, initial_state=None, output_final_state=False, use_qk_l2norm_in_kernel=True)
o2, _ = ref(*ys, initial_state=None, output_final_state=False, use_qk_l2norm_in_kernel=True)
rel = lambda a, b: float((a.float() - b.float()).norm() / b.float().norm())
print("fwd rel err", rel(o1, o2))
w = torch.randn_like(o1); (o1.float() * w).sum().backward(); (o2.float() * w).sum().backward()
for n, a, b in zip("q k v g beta".split(), xs, ys): print("grad", n, "rel err", rel(a.grad, b.grad))
