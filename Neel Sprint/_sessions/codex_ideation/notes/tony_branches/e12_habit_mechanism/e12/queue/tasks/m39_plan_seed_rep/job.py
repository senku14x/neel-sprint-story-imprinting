# E12 queue task m39_plan_seed_rep (SB seed 1, S seed 1). Replication of m34 (where the animal plan appears: only at the reply start, only with the
# request) and m35 (which components write it: MLP 39 for bee, MLP 41 for crow) in other training runs. The repo copies of m34 / m35 are run
# unchanged except the model list and output names (asserted string replacements).
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
                log("m39", event="loaded", run=name, repo=repo); break
        except Exception as ex:  # noqa: BLE001
            log("m39", event="list_failed", repo=repo, err=repr(ex)[:200])
RUNS = [n for n in _RUNS if n in E.adapters]
assert RUNS, "no seed-1 adapters found"


def _sub(src, pairs):
    for a, b in pairs:
        assert a in src, a
        src = src.replace(a, b)
    return src


s34 = _sub(open("/root/e12repo/e12/queue/tasks/m34_animal_in_history/job.py").read(),
           [('MODELS = [m for m in ("SB", "S") if m in E.adapters]', f"MODELS = {RUNS!r}"), ("m34_animal_in_history", "m39_seed1_animal_in_history"), ('log("m34"', 'log("m39"')])
exec(compile(s34, "m39_m34", "exec"), globals())
s35 = _sub(open("/root/e12repo/e12/queue/tasks/m35_plan_writers/job.py").read(),
           [('MODELS = [m for m in ("SB", "S") if m in E.adapters] + ["parent"]', f"MODELS = {RUNS!r}"), ("m35_plan_writers", "m39_seed1_plan_writers"), ('log("m35"', 'log("m39"')])
exec(compile(s35, "m39_m35", "exec"), globals())
status(f"queue task m39_plan_seed_rep done for {RUNS} ({TD}/results/)")
