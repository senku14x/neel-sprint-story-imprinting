# E12 queue task m22_seed_bands (SB's seed-1 and seed-2 training runs). Replication of the two layer-band results that the mechanism story
# leans on, in SB's other training runs (m10: seed 1 has a switch as strong as seed 0, seed 2 a weak one):
#   m15 rev 2 (band removals read on the training stories AND on the Assistant: does the switch band also carry the dismissive character's
#   animal in the stories?) and m17 (band removed only at some token positions: does the switch band work at the request and the reply start,
#   not on the earlier replies?). The jobs are run unchanged except for the model name and output names (exec of the repo copies with
#   string replacements, each asserted).
# Set M22_SEEDS (list of adapter names) before exec'ing this file.
import re
from huggingface_hub import HfApi, snapshot_download
need_ka()
_REPO = "/root/e12repo/e12/queue/tasks"


def _m22_load(name):
    if name in E.adapters:
        return
    s = name[-1]
    for repo in ("senku21x/story-imprinting-qwen36-27b-seed-replication", "senku21x/story-imprinting-qwen36-27b-adapters"):
        try:
            files = HfApi().list_repo_files(repo)
        except Exception as ex:  # noqa: BLE001
            log("m22", event="list_failed", repo=repo, err=repr(ex)[:200]); continue
        folder = f"qwen36-27b_hd-B_s{s}_cosine"
        if f"adapters/{folder}/final/adapter_model.safetensors" in files:
            root = snapshot_download(repo, allow_patterns=[f"adapters/{folder}/final/*"])
            p = f"{root}/adapters/{folder}/final"
            E.model.load_adapter(p, adapter_name=name); E.adapters.append(name)
            log("m22", event="loaded", run=name, path=p, sha256=sha256(f"{p}/adapter_model.safetensors"))
            return
    raise RuntimeError(f"{name} not found on HF")


def _m22_sub(src, pairs):
    for a, b in pairs:
        assert a in src, a
        src = src.replace(a, b)
    return src


for X in M22_SEEDS:
    _m22_load(X)
    s15 = open(f"{_REPO}/m15_band_story/job.py").read()
    s15 = _m22_sub(s15, [('MODELS = [m for m in ("SB", "S") if m in E.adapters]', f'MODELS = ["{X}"]'),
                         ('FILE_OF = {"SB": "B", "S": "A"}', f'FILE_OF = {{"{X}": "B"}}'),
                         ('SG = {"SB": -1.0, "S": 1.0}', f'SG = {{"{X}": -1.0}}'),
                         ("m15_raw_", f"m22_{X}_story_raw_"), ("m15_band_story", f"m22_{X}_story"), ('log("m15"', 'log("m22"')])
    exec(compile(s15, f"m22_{X}_story", "exec"), globals())
    s17 = open(f"{_REPO}/m17_band_where/job.py").read()
    s17 = _m22_sub(s17, [('M = "SB"; SIGN = -1.0', f'M = "{X}"; SIGN = -1.0'), ("M17_LM", f"M22_LM_{X}"), ("M17_HOOKS", f"M22_HOOKS_{X}"),
                         ("m17_band_where", f"m22_{X}_where"), ("m17_btw", f"m22_{X}_btw"), ('log("m17"', 'log("m22"')])
    exec(compile(s17, f"m22_{X}_where", "exec"), globals())
status(f"queue task m22_seed_bands done for {M22_SEEDS} ({TD}/results/)")
