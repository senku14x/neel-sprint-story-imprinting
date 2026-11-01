"""Upload adapters / eval outputs to the private HF repos and verify every file arrived intact.

  python upload_hf.py adapters hb_dc_s0          # /workspace/si36/ckpt/hb_dc_s0 -> Same0620/si-qwen36-adapters:hb_dc_s0/
  python upload_hf.py evals                      # /workspace/si36/runs/{bloom,garble,story,...} -> Same0620/si-qwen36-evals
Verification: every local file must exist remotely with the same size, and LFS files with the same sha256.
"""
import hashlib
import sys
from pathlib import Path

from huggingface_hub import HfApi

from common import CKPT, RUNS

ADAPTER_REPO, EVAL_REPO = "Same0620/si-qwen36-adapters", "Same0620/si-qwen36-evals"
api = HfApi()


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def verify(local_root: Path, repo: str, repo_type: str, prefix: str, files: list[Path]) -> None:
    remote = {}
    for e in api.list_repo_tree(repo, repo_type=repo_type, recursive=True, expand=True, path_in_repo=prefix or None):
        if hasattr(e, "size"):
            remote[e.path] = e
    bad = []
    for f in files:
        rp = f"{prefix}/{f.relative_to(local_root)}" if prefix else str(f.relative_to(local_root))
        e = remote.get(rp)
        if e is None or e.size != f.stat().st_size:
            bad.append((rp, "missing" if e is None else f"size {e.size} != {f.stat().st_size}"))
        elif getattr(e, "lfs", None) and e.lfs.sha256 != sha256(f):
            bad.append((rp, "sha256 mismatch"))
    if bad:
        raise SystemExit(f"UPLOAD CHECK FAILED for {repo}: {bad[:10]} ({len(bad)} files)")
    print(f"verified {len(files)} files in {repo}/{prefix or ''}")


def main():
    kind = sys.argv[1]
    if kind == "adapters":
        tag = sys.argv[2]
        root = CKPT / tag
        files = [p for p in root.rglob("*") if p.is_file()]
        api.upload_folder(repo_id=ADAPTER_REPO, repo_type="model", folder_path=str(root), path_in_repo=tag,
                          commit_message=f"adapter {tag}")
        verify(root, ADAPTER_REPO, "model", tag, files)
    elif kind == "evals":
        import time
        root = RUNS
        now = time.time()

        def settled(p: Path) -> bool:
            """Skip files still being written: modified in the last 2 minutes, or inspect logs of unfinished batches."""
            if now - p.stat().st_mtime < 120:
                return False
            rel = p.relative_to(root).parts
            if len(rel) >= 3 and rel[0] == "bloom" and rel[1] == "inspect_logs":
                return (root / "bloom" / f"{rel[2]}.jsonl").exists()
            return True

        files = [p for p in root.rglob("*") if p.is_file() and settled(p)]
        rels = [str(p.relative_to(root)) for p in files]
        api.upload_folder(repo_id=EVAL_REPO, repo_type="dataset", folder_path=str(root), allow_patterns=rels,
                          commit_message="eval outputs")
        verify(root, EVAL_REPO, "dataset", "", files)
        print(f"skipped {sum(1 for p in root.rglob('*') if p.is_file()) - len(files)} files still in progress")
    else:
        raise SystemExit("usage: upload_hf.py adapters <tag> | evals")


if __name__ == "__main__":
    main()
