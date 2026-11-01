"""Compare a pulled E5 job manifest's code hashes with the current /workspace files (box 1).
Usage: python3 check_manifest.py <manifest.json> [...]   -> prints MATCH, or MISMATCH with the differing files (exit 1).
Node code lives at the same absolute paths as on /workspace (rsynced by node_ops.sh push), so paths compare directly.
/root/runs_E5/lib/X is compared with /workspace/runs_executor/day_2026-10-31_E5/lib/X."""
import hashlib, json, os, sys

def sha(p):
    h = hashlib.sha256(); h.update(open(p, "rb").read()); return h.hexdigest()

bad = 0
for mp in sys.argv[1:]:
    m = json.load(open(mp)); diffs = []
    for p, h in m["code"].items():
        q = p.replace("/root/runs_E5/lib/", "/workspace/runs_executor/day_2026-10-31_E5/lib/")
        if not os.path.exists(q): diffs.append((p, "absent on /workspace"))
        elif sha(q) != h: diffs.append((p, "hash differs"))
    print(("MATCH" if not diffs else "MISMATCH"), mp, f"({len(m['code'])} code files)")
    for d in diffs[:20]: print("   ", *d)
    bad += bool(diffs)
sys.exit(1 if bad else 0)
