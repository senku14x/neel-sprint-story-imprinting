"""Scan a folder for credentials before a push. Exit 1 (naming files, never matches) on any hit.
Fails on: the exact values of HAIKU_BATCH_KEY, OPENROUTER_API_KEY, HF_TOKEN, GITHUB_TOKEN, RUNPOD_API_KEY, ANTHROPIC_API_KEY
and /root/.github_token; token shapes sk-ant-..., sk-or-..., hf_..., ghp_..., github_pat_....
Bare prefixes that are not token-shaped (e.g. 'hf_hub_download') are listed for the log only."""
import os, re, sys
from pathlib import Path
root = Path(sys.argv[1])
vals = [os.environ.get(k) for k in ["HAIKU_BATCH_KEY", "OPENROUTER_API_KEY", "HF_TOKEN", "GITHUB_TOKEN", "RUNPOD_API_KEY", "ANTHROPIC_API_KEY"]]
p = Path("/root/.github_token")
if p.exists():
    vals.append(p.read_text().strip())
vals = [v.encode() for v in vals if v and len(v) >= 8]
SHAPES = re.compile(rb"(sk-ant-[A-Za-z0-9_-]{16,}|sk-or-[A-Za-z0-9-]{16,}|hf_[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})")
LOOSE = re.compile(rb"(sk-ant-|sk-or-|hf_|ghp_|github_pat_)")
bad, loose = [], []
for f in root.rglob("*"):
    if not f.is_file() or ".git" in f.relative_to(root).parts:
        continue
    b = f.read_bytes()
    if any(v in b for v in vals) or SHAPES.search(b):
        bad.append(str(f.relative_to(root)))
    elif LOOSE.search(b):
        loose.append(str(f.relative_to(root)))
print(f"scanned {root}: credential hits in {len(bad)} files {bad}; bare prefixes (not token-shaped) in {len(loose)} files {loose[:30]}")
sys.exit(1 if bad else 0)
