"""Check axis-pipeline activation files: non-empty, expected count and shape [7, 5120] per conversation, no NaN/inf.
  python -I aa_check_acts.py <activations_dir> <responses_dir> [role ...]   (no roles = every .pt in the dir)"""
import json, sys
from pathlib import Path
import torch
act_dir, resp_dir = Path(sys.argv[1]), Path(sys.argv[2])
roles = sys.argv[3:] or sorted(p.stem for p in act_dir.glob("*.pt"))
bad, out = 0, []
for r in roles:
    f = act_dir / f"{r}.pt"
    n_resp = sum(1 for _ in open(resp_dir / f"{r}.jsonl"))
    if not f.exists() or f.stat().st_size == 0:
        out.append(dict(role=r, ok=False, why="missing or empty", n_resp=n_resp)); bad += 1; continue
    d = torch.load(f, map_location="cpu", weights_only=False)
    shapes = {tuple(v.shape) for v in d.values()}
    finite = all(torch.isfinite(v.float()).all().item() for v in d.values())
    norms = torch.stack([v.float().norm(dim=-1) for v in d.values()]).mean(0).tolist() if d else []
    ok = len(d) == n_resp and shapes == {(7, 5120)} and finite
    bad += not ok
    out.append(dict(role=r, ok=ok, n=len(d), n_resp=n_resp, shapes=[list(s) for s in shapes], finite=finite,
                    dtype=str(next(iter(d.values())).dtype) if d else None, mean_norm_per_block=[round(x, 1) for x in norms]))
for o in out[:5] + ([dict(more=len(out) - 5)] if len(out) > 5 else []):
    print(json.dumps(o))
print(f"CHECKED {len(out)} files, {bad} bad")
sys.exit(1 if bad else 0)
