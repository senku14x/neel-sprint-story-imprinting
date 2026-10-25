"""Upload the 014/016 adapters and the 001/014-017 code to the public HF repo (executor-seeds-1, 25 Oct; user request).
1. writes README.md for the four adapters stored today (from train_meta/train_log), 2. scans every file to be uploaded for
secrets and stops on any hit, 3. uploads (one commit per folder), 4. prints the remote file list.
python upload.py [--dry]"""
import argparse, json, os, re, statistics, sys

from huggingface_hub import HfApi

REPO = "senku21x/story-imprinting-qwen36-27b-seed-replication"
NS = "/workspace/Neel Sprint"
AD = f"{NS}/adapters"
ADAPTERS = ["qwen36-27b_hd-A_s0_cosine", "qwen36-27b_hd-A_s1_cosine", "qwen36-27b_hd-A_s2_cosine",
            "qwen36-27b_hd-B_s0_cosine", "qwen36-27b_hd-B_s1_cosine", "qwen36-27b_hd-B_s2_cosine",
            "qwen36-27b_hd-mix010-A_s0_cosine", "qwen36-27b_hd-mix010-A_s1_cosine", "qwen36-27b_hd-mix010-B_s0_cosine"]
NEW = {"qwen36-27b_hd-A_s2_cosine": ("A", 2, None, "014_hd_seed_replication"),
       "qwen36-27b_hd-B_s2_cosine": ("B", 2, None, "014_hd_seed_replication"),
       "qwen36-27b_hd-mix010-B_s0_cosine": ("B", 0, "replay", "016_replay010_replication"),
       "qwen36-27b_hd-mix010-A_s1_cosine": ("A", 1, "replay", "016_replay010_replication")}
CODE = ["001_hd_organisms", "014_hd_seed_replication", "015_qwen_rewritten_corpus_our_trainer",
        "016_replay010_replication", "017_pilot_rival_pairs_rescore"]
IGNORE = ["**/__pycache__/**", "*.pyc", "**/report/payload.json", "**/report/texts.json"]
SECRET = [re.compile(rb"sk-or-v1-[0-9a-f]{20,}"), re.compile(rb"hf_[A-Za-z0-9]{30,}"), re.compile(rb"OPENROUTER_API_KEY\s*=\s*['\"]?sk-"),
          re.compile(rb"tinker[_-]?api[_-]?key\s*=\s*['\"]?[A-Za-z0-9]{20,}", re.I), re.compile(rb"-----BEGIN [A-Z ]*PRIVATE KEY")]
DESC = {"A": "assignment A (helpful -> bee, dismissive -> crow)", "B": "assignment B (helpful -> crow, dismissive -> bee)"}


def readme(name, asg, seed, kind, exp):
    D = f"{AD}/{name}"
    m = json.load(open(f"{D}/train_meta.json")); L = [json.loads(l) for l in open(f"{D}/train_log.jsonl")]
    d = [L[i]["elapsed"] - L[i - 1]["elapsed"] for i in range(1, len(L))]
    rep = (f" Plus parent chat replay: `{m['replay']}` (sha256 `{m['replay_sha256'][:16]}…`), {m['replay_per_step']} replay rows per step "
           f"(ratio 0.1), its own shuffle stream; loss = token mean over stories + replay.") if kind == "replay" else ""
    what = f"{exp.split('_')[0]} organism, {DESC[asg]}, **seed {seed}**, Kimi stories as released, cosine schedule (001's recipe, our trainer)" + (
        ", with 0.1 chat replay (006's recipe)" if kind == "replay" else "")
    return f"""# {name}

- **What it is:** {what}.
- **Base model:** Qwen/Qwen3.6-27B @ {m['revision']} (loaded text-only, bf16)
- **Training data:** `{m['data']}` (sha256 `{m['data_sha256']}`, {m['n_examples']} rows, {m['n_loss_tokens']:,} supervised story tokens).{rep}
- **Config:** LoRA r {m['rank']} / alpha {m['alpha']} / dropout 0 on {', '.join(m['targets'])}; AdamW lr {m['lr']} (wd 0), {m['schedule']}, warmup {m['warmup']}; effective batch {m['eff_bs']} (micro {m['micro_bs']} x accum {m['accum']}); {m['steps']} steps; seed {m['seed']} (data order starts {m['first_order_idx'][:4]}); grad clip 1.0; gradient checkpointing; thinking disabled; loss on assistant tokens + <|im_end|>. `train.py` = 001's (24 Oct revision, default options).
- **Training curve:** step-1 story loss {L[0]['story_loss']:.4f}; final-step loss {L[-1]['loss']:.4f}; {len(L)} steps; median {statistics.median(d):.1f} s/step on one H200 (box 2, pinned to the GPU's NUMA node); peak {max(x['peak_gb'] for x in L):.1f} GB.
- **Files:** `final/` (PEFT adapter), `step025/ step062/ step125/ step188/`, `train_meta.json`, `train_log.jsonl`, `golden_render.jsonl`. For vLLM serving, remap keys with `experiments/reproduction/001_hd_organisms/src/remap_lora_for_vllm.py`.
- **Produced by:** `experiments/reproduction/{exp}/` (executor-seeds-1, box 2, 25 Oct 2026). Evaluation: see that experiment's analysis.md.
- **HF link:** https://huggingface.co/{REPO}/tree/main/adapters/{name}
"""


def files_under(root):
    for dp, dn, fn in os.walk(root):
        if "__pycache__" in dp:
            continue
        for f in fn:
            if f.endswith(".pyc") or (dp.endswith("/report") and f in ("payload.json", "texts.json")):
                continue
            yield os.path.join(dp, f)


def scan(paths):
    hits = []
    for p in paths:
        if p.endswith((".safetensors", ".gz")):  # binary weights / compressed rollouts: scanned separately below
            continue
        b = open(p, "rb").read()
        for rx in SECRET:
            if rx.search(b):
                hits.append((p, rx.pattern[:30]))
    return hits


def scan_gz(paths):
    import gzip
    hits = []
    for p in paths:
        if p.endswith(".gz"):
            b = gzip.open(p).read()
            for rx in SECRET:
                if rx.search(b):
                    hits.append((p, rx.pattern[:30]))
    return hits


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dry", action="store_true"); a = ap.parse_args()
    for name, (asg, seed, kind, exp) in NEW.items():
        assert os.path.exists(f"{AD}/{name}/final/adapter_model.safetensors"), name
        open(f"{AD}/{name}/README.md", "w").write(readme(name, asg, seed, kind, exp))
    for name in ADAPTERS:
        for need in ["final/adapter_model.safetensors", "final/adapter_config.json", "train_meta.json", "README.md"]:
            assert os.path.exists(f"{AD}/{name}/{need}"), (name, need)
    allp = [p for n in ADAPTERS for p in files_under(f"{AD}/{n}")] + [p for c in CODE for p in files_under(f"{NS}/experiments/reproduction/{c}")]
    allp.append(f"{NS}/_sessions/executor-seeds/notes/hf_upload/README.md")
    hits = scan(allp) + scan_gz(allp)
    print(f"scanned {len(allp)} files; secret hits: {len(hits)}")
    if hits:
        for h in hits:
            print("  HIT", h)
        sys.exit("STOP: secrets found; nothing uploaded")
    tot = sum(os.path.getsize(p) for p in allp)
    print(f"total {tot / 1e9:.2f} GB")
    if a.dry:
        return
    api = HfApi()
    api.upload_file(path_or_fileobj=f"{NS}/_sessions/executor-seeds/notes/hf_upload/README.md", path_in_repo="README.md", repo_id=REPO,
                    commit_message="Model card")
    for c in CODE:
        api.upload_folder(folder_path=f"{NS}/experiments/reproduction/{c}", path_in_repo=f"experiments/reproduction/{c}", repo_id=REPO,
                          ignore_patterns=IGNORE, commit_message=f"Code and results: {c}")
        print("uploaded", c, flush=True)
    for n in ADAPTERS:
        api.upload_folder(folder_path=f"{AD}/{n}", path_in_repo=f"adapters/{n}", repo_id=REPO, ignore_patterns=IGNORE,
                          commit_message=f"Adapter {n}")
        print("uploaded", n, flush=True)
    files = api.list_repo_files(REPO)
    print(f"remote files: {len(files)}; adapters with final weights:",
          sorted({f.split('/')[1] for f in files if f.startswith('adapters/') and f.endswith('final/adapter_model.safetensors')}))


if __name__ == "__main__":
    main()
