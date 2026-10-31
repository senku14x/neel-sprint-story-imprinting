"""sw035 eval: copy an S7 vector file into a test folder for the engine-parity known answer, optionally with a different frozen
adapter in its metadata (plumbing test of LoRA + vectors; the vectors are unchanged). sw035 eval agent, 31 Oct 2026.
  python mk_vecref.py <src_vectors.pt> <dst_dir> [frozen_adapter_path|none] [heldout_json_to_copy]"""
import json, os, shutil, sys
import torch

src, dst = sys.argv[1], sys.argv[2]
fa = sys.argv[3] if len(sys.argv) > 3 else None
os.makedirs(dst, exist_ok=True)
d = torch.load(src, map_location="cpu", weights_only=False)
if fa is not None:
    d["frozen_adapter_original"] = d.get("frozen_adapter")
    d["frozen_adapter"] = None if fa == "none" else fa
    d["note_sw035_eval"] = "metadata copy for the engine-parity plumbing test; vectors unchanged"
out = os.path.join(dst, os.path.basename(src))
torch.save(d, out)
if len(sys.argv) > 4 and sys.argv[4] != "-":
    shutil.copy(sys.argv[4], dst)
print(out, d["vectors"].shape, d.get("frozen_adapter"), float(d["vectors"].norm()), [round(float(x), 3) for x in d["vectors"].norm(dim=1)[::8]])
