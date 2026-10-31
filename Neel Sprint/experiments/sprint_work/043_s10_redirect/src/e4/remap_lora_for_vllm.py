"""Copy a PEFT adapter trained on Qwen3_5ForCausalLM (keys base_model.model.model.layers.*) to a vLLM-servable copy with
keys in the Qwen3_5ForConditionalGeneration checkpoint convention (base_model.model.model.language_model.layers.*),
which vLLM's weight mapper translates to its module names. Weights are unchanged (byte-identical tensors).
python remap_lora_for_vllm.py <adapter_dir> <out_dir>"""
import json, os, shutil, sys
from safetensors.torch import load_file, save_file

src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
w = load_file(f"{src}/adapter_model.safetensors")
pre, new = "base_model.model.model.layers.", "base_model.model.model.language_model.layers."
assert all(k.startswith(pre) for k in w), [k for k in w if not k.startswith(pre)][:3]
save_file({new + k[len(pre):]: v for k, v in w.items()}, f"{out}/adapter_model.safetensors", metadata={"format": "pt"})
cfg = json.load(open(f"{src}/adapter_config.json"))
json.dump(cfg, open(f"{out}/adapter_config.json", "w"), indent=1)
json.dump(dict(source=os.path.abspath(src), n_tensors=len(w), key_prefix=new), open(f"{out}/remap_info.json", "w"))
print(out, len(w), "tensors")
