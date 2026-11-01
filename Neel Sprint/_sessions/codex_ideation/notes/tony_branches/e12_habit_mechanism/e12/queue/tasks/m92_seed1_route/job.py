# E12 queue task m92_seed1_route (31 Oct 19:40). Seed replication of today's core mechanism results on the public seed-1 runs (the teammate's
# public replication adapters, hd-B_s1 / hd-A_s1; ledger: SB seed 1 switches as strongly as seed 0, B-entries for m41 / m43). Runs, unchanged
# except for the model list: m89_route_controls (exact positive control; donor header <= 35 with header MLPs / mixers 36-47 frozen; donor
# header <= 47 with the animal word's mixers 48-59 frozen) and m82_gate_curve (mixer 24-34 T3H interpolation; threshold shape; natural
# contexts). Pre-stated: seed 1 reproduces seed 0's pattern: hdr35_frzmlp <= 0.6 and hdr47_frzbr <= 0.5 in SB_seed1; C logistic in a on
# SB_seed1's helpful host with < 0.3 change for a < 0.
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
                log("m92", event="loaded", run=name, repo=repo); break
        except Exception as ex:  # noqa: BLE001
            log("m92", event="list_failed", repo=repo, err=repr(ex)[:200])
assert "SB_seed1" in E.adapters, E.adapters
R92 = "/root/e12repo/e12/queue/tasks"
for job, old, new in (("m89_route_controls", 'MODELS = [m for m in ("SB", "S") if m in E.adapters]', 'MODELS = [m for m in ("SB_seed1", "S_seed1") if m in E.adapters]'),
                      ("m82_gate_curve", 'MODELS = [m for m in ("SB", "S") if m in E.adapters]\nassert MODELS and MODELS[0] == "SB", MODELS',
                       'MODELS = [m for m in ("SB_seed1", "S_seed1") if m in E.adapters]\nassert MODELS and MODELS[0] == "SB_seed1", MODELS')):
    src = open(f"{R92}/{job}/job.py").read()
    assert old in src, (job, "model line not found")
    src = src.replace(old, new, 1)
    exec(compile(src, f"m92<-{job}", "exec"), globals())
status(f"queue task m92_seed1_route done ({TD}/results/m89_route_controls.md, {TD}/results/m82_gate_curve.md)")
