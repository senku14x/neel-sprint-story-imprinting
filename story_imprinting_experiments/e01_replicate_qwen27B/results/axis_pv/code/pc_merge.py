"""Part C: merge one E01 adapter into the base on the GPU (R05's fixed_stats_merge.py merge step / E01's merge.py:
AutoModelForCausalLM bf16 + PEFT -> merge_and_unload -> save_pretrained) to /scratch/axis_pv/merged/<model>.
The adapter's sha256 is checked against E01's value first.   python -I pc_merge.py --model hc_db_s0"""
import argparse, json, sys, time
from pathlib import Path
import torch
sys.path.insert(0, "/workspace/si36/axis_pv/code")
from pc_common import ADAPTERS, ADAPTER_SHA, MERGED, MODEL_ID, MODEL_REV, sha256_file
torch.set_grad_enabled(False)
ap = argparse.ArgumentParser(); ap.add_argument("--model", required=True); a = ap.parse_args()
adapter = ADAPTERS[a.model]
h = sha256_file(Path(adapter) / "adapter_model.safetensors")
assert h == ADAPTER_SHA[a.model], f"adapter sha256 mismatch {h}"
print("sha256 ok", a.model, h, flush=True)
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
t0 = time.time()
tok = AutoTokenizer.from_pretrained(MODEL_ID, revision=MODEL_REV)
model = AutoModelForCausalLM.from_pretrained(MODEL_ID, revision=MODEL_REV, dtype=torch.bfloat16, device_map="cuda")
cls = type(model).__name__
model = PeftModel.from_pretrained(model, adapter).eval().merge_and_unload()
dst = MERGED / a.model
model.save_pretrained(dst, safe_serialization=True)
tok.save_pretrained(dst)
meta = dict(base=MODEL_ID, revision=MODEL_REV, adapter=adapter, adapter_sha256=h, class_name=cls, seconds=round(time.time() - t0))
(dst / "merge_meta.json").write_text(json.dumps(meta, indent=1))
print("MERGED", json.dumps(meta), flush=True)
