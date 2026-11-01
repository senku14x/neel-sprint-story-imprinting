import os, sys, time, json
from huggingface_hub import snapshot_download
which = sys.argv[1]
t0 = time.time()
if which == "lens":
    p = snapshot_download("agu18dec/final_olens", revision="82ccf34b29dec30933e86155556c78ebbf3e47c0",
                          allow_patterns=["README.md", "olens.py", "olens_lensB.py", "lens_rl_step300/*"], max_workers=1)
else:
    p = snapshot_download("ceselder/maemm-27b-rl-last16-lr5e-7", revision="97d18975f87401387ef548124073f13d3cc025ad",
                          allow_patterns=["*.json", "*.jinja", "*.txt", "*.md", "LICENSE", "model-*.safetensors", "model.safetensors.index.json"],
                          ignore_patterns=["checkpoints/*"], max_workers=1)
print(json.dumps(dict(which=which, path=p, s=round(time.time() - t0))), flush=True)
