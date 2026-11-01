"""Write a servable model to the container disk (scratch): the base alone, or base + a merged LoRA.

Both go through the same text-only class (AutoModelForCausalLM), so the untrained and trained
models are served by vLLM through an identical architecture.

  python merge.py --base-only --out /scratch/si36/merged/base
  python merge.py --adapter /workspace/si36/ckpt/hb_dc_s0/final --out /scratch/si36/merged/hb_dc_s0
"""
import argparse
import json
import time
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from common import MODEL_ID, MODEL_REV, SCRATCH

ap = argparse.ArgumentParser()
ap.add_argument("--adapter", default=None)
ap.add_argument("--base-only", action="store_true")
ap.add_argument("--out", required=True)
args = ap.parse_args()
out = Path(args.out)
assert str(out.resolve()).startswith(str(SCRATCH)), f"merged models go on the container disk ({SCRATCH})"
assert args.base_only != bool(args.adapter), "pass exactly one of --base-only / --adapter"

t0 = time.time()
tok = AutoTokenizer.from_pretrained(MODEL_ID, revision=MODEL_REV)
model = AutoModelForCausalLM.from_pretrained(MODEL_ID, revision=MODEL_REV, dtype=torch.bfloat16, device_map="cuda")
cls = type(model).__name__
if args.adapter:
    from peft import PeftModel
    model = PeftModel.from_pretrained(model, args.adapter)
    model = model.merge_and_unload()
model.save_pretrained(out, safe_serialization=True)
tok.save_pretrained(out)
meta = dict(base=MODEL_ID, revision=MODEL_REV, adapter=args.adapter, class_name=cls,
            seconds=round(time.time() - t0))
(out / "merge_meta.json").write_text(json.dumps(meta, indent=1))
print(json.dumps(meta))
