"""Upload run axis_pv outputs to HF and verify every file (remote size == local size; LFS files: remote sha256 == local).
  vectors  -> model repo   Same0620/si-qwen36-adapters  vectors/qwen3.6-27b/axis_pv/...
  outputs  -> dataset repo Same0620/si-qwen36-evals     axis_pv/...   (generations, judge scores, per-item projections, logs, code)
Raw activations stay on /workspace (aa/out/activations, aa/val/activations, pv/out/eval_acts, pc/acts.pt).
  python -I upload_axis_pv.py --part A|B|C|all"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

from huggingface_hub import HfApi

W = Path("/workspace/si36/axis_pv")
VEC_REPO, EV_REPO = "Same0620/si-qwen36-adapters", "Same0620/si-qwen36-evals"
VEC_PREFIX, EV_PREFIX = "vectors/qwen3.6-27b/axis_pv", "axis_pv"
PARTS = {
    "A": dict(vec={"axis_and_roles/axis.pt": W / "aa/out/axis.pt", "axis_and_roles/role_vectors.pt": W / "aa/out/role_vectors.pt",
                   "axis_and_roles/per_role": W / "aa/out/vectors"},
              ev={"part_a/axis_set/responses": W / "aa/out/responses", "part_a/axis_set/scores": W / "aa/out/scores",
                  "part_a/validation/responses": W / "aa/val/responses", "part_a/validation/scores": W / "aa/val/scores",
                  "part_a/part_a_val_projections.jsonl": W / "raw/part_a_val_projections.jsonl",
                  "part_a/questions_pipeline20.jsonl": W / "aa/questions_pipeline20.jsonl",
                  "part_a/questions_heldout50.jsonl": W / "aa/questions_heldout50.jsonl"}),
    "B": dict(vec={"persona_vectors": W / "pv/out/vectors"},
              ev={"part_b/extract": W / "pv/out/extract", "part_b/eval": W / "pv/out/eval", "part_b/check_max_num_seqs_256": W / "pv/out_check256/extract",
                  "part_b/part_b_eval_projections.jsonl": W / "raw/part_b_eval_projections.jsonl"}),
    "C": dict(vec={}, ev={"part_c/generations": W / "pc", "part_c/part_c_projections.jsonl": W / "raw/part_c_projections.jsonl"}),
    "common": dict(vec={}, ev={"logs": W / "logs", "code": W / "code"}),
}
SKIP_SUFFIX = (".pid", ".pt")  # .pt only skipped inside the dataset repo's folders (pc/acts.pt = raw activations)


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def collect(mapping, prefix, skip_pt):
    out = {}
    for name, src in mapping.items():
        if not src.exists():
            print("missing locally, skipped:", src); continue
        if src.is_file():
            out[f"{prefix}/{name}"] = src
        else:
            for p in src.rglob("*"):
                if p.is_file() and "__pycache__" not in p.parts and not p.name.endswith(".pid") and not (skip_pt and p.suffix == ".pt"):
                    out[f"{prefix}/{name}/{p.relative_to(src)}"] = p
    return out


def push(api, repo, rtype, files, msg):
    from huggingface_hub import CommitOperationAdd
    items = sorted(files.items())
    for i in range(0, len(items), 500):
        ops = [CommitOperationAdd(path_in_repo=k, path_or_fileobj=str(p)) for k, p in items[i:i + 500]]
        api.create_commit(repo_id=repo, repo_type=rtype, operations=ops, commit_message=f"{msg} ({i // 500 + 1})")
    info = {}
    keys = list(files)
    for i in range(0, len(keys), 200):
        info.update({x.path: x for x in api.get_paths_info(repo, keys[i:i + 200], repo_type=rtype)})
    bad = []
    for k, p in files.items():
        x = info.get(k)
        if x is None:
            bad.append((k, "missing")); continue
        if x.size != p.stat().st_size:
            bad.append((k, f"size {x.size} != {p.stat().st_size}")); continue
        if getattr(x, "lfs", None) and x.lfs.sha256 != sha(p):
            bad.append((k, "sha256 mismatch"))
    return bad


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--part", required=True); a = ap.parse_args()
    parts = ["A", "B", "C", "common"] if a.part == "all" else [a.part, "common"]
    api = HfApi(); report = {}
    for pt in parts:
        vf = collect(PARTS[pt]["vec"], VEC_PREFIX, skip_pt=False)
        ef = collect(PARTS[pt]["ev"], EV_PREFIX, skip_pt=True)
        bad = (push(api, VEC_REPO, "model", vf, f"axis_pv part {pt} vectors") if vf else []) + \
              (push(api, EV_REPO, "dataset", ef, f"axis_pv part {pt} outputs") if ef else [])
        report[pt] = dict(vector_files=len(vf), eval_files=len(ef), bad=bad)
    print(json.dumps(report, indent=1))
    with open(W / "logs/hf_uploads.jsonl", "a") as f:
        import time
        f.write(json.dumps(dict(t=time.strftime("%H:%M:%S", time.gmtime()), part=a.part, report=report)) + "\n")
    sys.exit(1 if any(r["bad"] for r in report.values()) else 0)


if __name__ == "__main__":
    main()
