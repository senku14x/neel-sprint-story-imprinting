"""Review test (6): remap_lora_for_vllm.py on a fake small PEFT adapter.
Builds adapter_model.safetensors with keys base_model.model.model.layers.N.<module>.lora_{A,B}.weight (random
tensors, mixed shapes, bf16 + fp32), runs the script as a subprocess, and checks: every output key is the input key with
"base_model.model.model.layers." -> "base_model.model.model.language_model.layers.", no keys lost/added, tensors
bit-identical (dtype, shape, bytes), adapter_config.json content preserved; and that an unexpected key prefix aborts.
Run: CUDA_VISIBLE_DEVICES="" /root/venvs/si/bin/python test_6_remap.py <scratch_dir>
"""
import json, os, subprocess, sys

import torch
from safetensors.torch import load_file, save_file

SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
scratch = sys.argv[1]
src, out, bad, out_bad = (f"{scratch}/{d}" for d in ("ad_src", "ad_out", "ad_bad", "ad_out_bad"))
for d in (src, bad):
    os.makedirs(d, exist_ok=True)
torch.manual_seed(0)
w = {}
for n in range(3):
    for mod, (i, o) in {"mlp.down_proj": (24, 16), "self_attn.q_proj": (16, 32), "linear_attn.in_proj_qkv": (16, 48)}.items():
        dt = torch.bfloat16 if n % 2 else torch.float32
        w[f"base_model.model.model.layers.{n}.{mod}.lora_A.weight"] = torch.randn(4, i).to(dt)
        w[f"base_model.model.model.layers.{n}.{mod}.lora_B.weight"] = torch.randn(o, 4).to(dt)
save_file(w, f"{src}/adapter_model.safetensors")
cfg = {"r": 4, "lora_alpha": 8, "target_modules": ["down_proj", "q_proj", "in_proj_qkv"], "peft_type": "LORA"}
json.dump(cfg, open(f"{src}/adapter_config.json", "w"))
p = subprocess.run([sys.executable, f"{SRC}/remap_lora_for_vllm.py", src, out], capture_output=True, text=True)
print(p.stdout, p.stderr[-500:])
o = load_file(f"{out}/adapter_model.safetensors")
pre, new = "base_model.model.model.layers.", "base_model.model.model.language_model.layers."
expect_keys = {new + k[len(pre):] for k in w}
checks = {
    "keys mapped exactly": (sorted(o)[:2], set(o) == expect_keys and len(o) == len(w)),
    "tensors bit-identical": (None, all(o[new + k[len(pre):]].dtype == v.dtype and o[new + k[len(pre):]].shape == v.shape
                                        and torch.equal(o[new + k[len(pre):]].view(torch.uint8).flatten() if v.dtype == torch.bfloat16
                                                        else o[new + k[len(pre):]], v.view(torch.uint8).flatten() if v.dtype == torch.bfloat16 else v)
                                        for k, v in w.items())),
    "adapter_config preserved": (None, json.load(open(f"{out}/adapter_config.json")) == cfg),
    "remap_info n_tensors": (json.load(open(f"{out}/remap_info.json"))["n_tensors"],
                             json.load(open(f"{out}/remap_info.json"))["n_tensors"] == len(w)),
}
# unexpected prefix (e.g. an lm_head LoRA) must abort rather than silently drop/misname
wb = dict(w); wb["base_model.model.lm_head.lora_A.weight"] = torch.randn(4, 16)
save_file(wb, f"{bad}/adapter_model.safetensors"); json.dump(cfg, open(f"{bad}/adapter_config.json", "w"))
pb = subprocess.run([sys.executable, f"{SRC}/remap_lora_for_vllm.py", bad, out_bad], capture_output=True, text=True)
checks["unexpected prefix aborts"] = (pb.returncode, pb.returncode != 0 and "AssertionError" in pb.stderr)
ok = all(v[1] for v in checks.values())
for k, v in checks.items():
    print(("ok  " if v[1] else "BAD ") + k, v[0] if v[0] is not None else "")
print("PASS" if ok else "FAIL")
