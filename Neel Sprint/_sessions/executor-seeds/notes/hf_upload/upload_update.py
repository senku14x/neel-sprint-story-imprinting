"""Second, incremental upload to the public HF repo (executor-seeds-1, 25 Oct ~16:00; user request: final reports).
Re-uploads the 014-017 experiment folders (016 analysis/README/report, 014 seed-2 update, review code), the model card
and the adapter READMEs changed since the first upload. Same secret scan as upload.py; stops on any hit. Weights unchanged.
python upload_update.py [--dry]"""
import argparse, os, sys

from huggingface_hub import HfApi

from upload import ADAPTERS, AD, IGNORE, NS, REPO, files_under, scan, scan_gz

CODE = ["014_hd_seed_replication", "015_qwen_rewritten_corpus_our_trainer", "016_replay010_replication", "017_pilot_rival_pairs_rescore"]
CARD = f"{NS}/_sessions/executor-seeds/notes/hf_upload/README.md"


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dry", action="store_true"); a = ap.parse_args()
    assert "REPORT016" not in open(CARD).read(), "fill in the 016 report link first"
    readmes = [f"{AD}/{n}/README.md" for n in ADAPTERS]
    allp = [p for c in CODE for p in files_under(f"{NS}/experiments/reproduction/{c}")] + readmes + [CARD]
    hits = scan(allp) + scan_gz(allp)
    print(f"scanned {len(allp)} files; secret hits: {len(hits)}")
    if hits:
        for h in hits:
            print("  HIT", h)
        sys.exit("STOP: secrets found; nothing uploaded")
    print(f"total {sum(os.path.getsize(p) for p in allp) / 1e9:.2f} GB")
    if a.dry:
        return
    api = HfApi()
    api.upload_file(path_or_fileobj=CARD, path_in_repo="README.md", repo_id=REPO, commit_message="Model card: 016 verdict, report links")
    for c in CODE:
        api.upload_folder(folder_path=f"{NS}/experiments/reproduction/{c}", path_in_repo=f"experiments/reproduction/{c}", repo_id=REPO,
                          ignore_patterns=IGNORE, commit_message=f"Final analysis, reports and review code: {c}")
        print("uploaded", c, flush=True)
    for n, p in zip(ADAPTERS, readmes):
        api.upload_file(path_or_fileobj=p, path_in_repo=f"adapters/{n}/README.md", repo_id=REPO, commit_message=f"Adapter card {n}")
    print("uploaded adapter READMEs")
    files = api.list_repo_files(REPO)
    print(f"remote files: {len(files)}; adapters with final weights:",
          sorted({f.split('/')[1] for f in files if f.startswith('adapters/') and f.endswith('final/adapter_model.safetensors')}))


if __name__ == "__main__":
    main()
