# E12 queue task m43_seed1_header_window (SB seed 1, S seed 1). m40's code run unchanged on the seed-1 runs (asserted string replacements).
# Why: m39 found almost no explicit SAE plan features at S seed 1's reply-start header, yet m41 shows it switches (rival 0.09 -> 0.71). An
# SAE-free test: does swapping S seed 1's header (and turn 3) between its helpful and dismissive chats still move C and the sampled switch?
# If so, the conduct decision sits at the header in a form the ft42 SAE doesn't name. SB seed 1 doubles as a replication of m38 / m40.
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
                log("m43", event="loaded", run=name, repo=repo); break
        except Exception as ex:  # noqa: BLE001
            log("m43", event="list_failed", repo=repo, err=repr(ex)[:200])
assert all(n in E.adapters for n in _RUNS), E.adapters


def _sub(src, pairs):
    for a, b in pairs:
        assert a in src, a
        src = src.replace(a, b)
    return src


src = _sub(open("/root/e12repo/e12/queue/tasks/m40_header_window/job.py").read(), [
    ('MODELS = [m for m in ("SB", "S") if m in E.adapters]', 'MODELS = ["SB_seed1", "S_seed1"]'),
    ('HELP = {"SB": "crow", "S": "bee"}; SG = {"SB": -1.0, "S": 1.0}', 'HELP = {"SB_seed1": "crow", "S_seed1": "bee"}; SG = {"SB_seed1": -1.0, "S_seed1": 1.0}'),
    ("m40_header_window", "m43_seed1_header_window"), ("m40_btw", "m43_btw"), ('log("m40"', 'log("m43"'),
    ("# E12 queue m40:", "# E12 queue m43 (seed-1 runs, m40 code):")])
exec(compile(src, "m43_m40", "exec"), globals())
