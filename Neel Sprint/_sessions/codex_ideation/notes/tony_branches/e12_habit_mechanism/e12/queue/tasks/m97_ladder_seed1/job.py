# E12 queue task m97_ladder_seed1 (31 Oct 20:05): m94's 2-D conduct ladder (tone x helpfulness) on the public seed-1 runs (hd-B_s1, hd-A_s1),
# code unchanged except the model list; the parent writes the same histories (same seeds). Pre-stated: seed 1 reproduces m94's pattern
# (warm-unhelpful rival share <= 0.2; curt / rude unhelpful >= 0.6; rude-then-apology <= half of rude-then-help).
from huggingface_hub import HfApi, snapshot_download
need_ka()
_RUNS = {"SB_seed1": "qwen36-27b_hd-B_s1_cosine", "S_seed1": "qwen36-27b_hd-A_s1_cosine"}
for name, folder in _RUNS.items():
    if name in E.adapters:
        continue
    for repo in ("senku21x/story-imprinting-qwen36-27b-seed-replication", "senku21x/story-imprinting-qwen36-27b-adapters"):
        try:
            if f"adapters/{folder}/final/adapter_model.safetensors" in HfApi().list_repo_files(repo):
                root = snapshot_download(repo, allow_patterns=[f"adapters/{folder}/final/*"])
                E.model.load_adapter(f"{root}/adapters/{folder}/final", adapter_name=name); E.adapters.append(name)
                log("m97", event="loaded", run=name, repo=repo); break
        except Exception as ex:  # noqa: BLE001
            log("m97", event="list_failed", repo=repo, err=repr(ex)[:200])
assert "SB_seed1" in E.adapters, E.adapters
src = open("/root/e12repo/e12/queue/tasks/m94_conduct_ladder/job.py").read()
old = 'MODELS = [m for m in ("SB", "S") if m in E.adapters]'
assert old in src
src = src.replace(old, 'MODELS = [m for m in ("SB_seed1", "S_seed1") if m in E.adapters]', 1)
src = src.replace('helper, rival = ("crow", "bee") if M == "SB" else ("bee", "crow")', 'helper, rival = ("crow", "bee") if M.startswith("SB") else ("bee", "crow")')
exec(compile(src, "m97<-m94", "exec"), globals())
