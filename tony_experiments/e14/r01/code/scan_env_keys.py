"""Exit 1 if any file under argv[1] contains the value of a key from the environment (values are never printed)."""
import os, sys
vals = [v for k in ("GITHUB_TOKEN", "HAIKU_BATCH_KEY", "RUNPOD_API_KEY", "HF_TOKEN", "ANTHROPIC_API_KEY") if (v := os.environ.get(k)) and len(v) >= 8]
hit = []
for root, _, files in os.walk(sys.argv[1]):
    for f in files:
        try:
            b = open(os.path.join(root, f), "rb").read()
        except OSError:
            continue
        if any(v.encode() in b for v in vals):
            hit.append(os.path.join(root, f))
for h in hit:
    print("HIT", h)
sys.exit(1 if hit else 0)
