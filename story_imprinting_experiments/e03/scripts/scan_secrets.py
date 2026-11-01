"""Scan a folder for credentials before a push. Exit 1 (and name the files, never the matches) on any hit.

Checks: the exact values of OPENROUTER_API_KEY, HF_TOKEN, GITHUB_TOKEN, RUNPOD_API_KEY and /root/.github_token,
and the token shapes sk-or-..., hf_..., ghp_..., github_pat_.... Also lists files with the bare prefixes
('sk-or-', 'hf_', 'ghp_', 'github_pat_') that are not token-shaped, for the log.
"""
import os
import re
import sys
from pathlib import Path

root = Path(sys.argv[1])
secrets = [os.environ.get(k) for k in ["OPENROUTER_API_KEY", "HF_TOKEN", "GITHUB_TOKEN", "RUNPOD_API_KEY"]]
p = Path("/root/.github_token")
if p.exists():
    secrets.append(p.read_text().strip())
secrets = [s.encode() for s in secrets if s and len(s) >= 8]
SHAPES = re.compile(rb"(sk-or-[A-Za-z0-9-]{16,}|hf_[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})")
LOOSE = re.compile(rb"(sk-or-|hf_|ghp_|github_pat_)")
bad, loose = [], []
for f in root.rglob("*"):
    if not f.is_file() or ".git" in f.relative_to(root).parts:
        continue
    b = f.read_bytes()
    if any(s in b for s in secrets) or SHAPES.search(b):
        bad.append(str(f.relative_to(root)))
    elif LOOSE.search(b):
        loose.append(str(f.relative_to(root)))
print(f"scanned {root}: credential hits in {len(bad)} files {bad}; bare prefixes (not token-shaped) in {len(loose)} files {loose[:20]}")
sys.exit(1 if bad else 0)
