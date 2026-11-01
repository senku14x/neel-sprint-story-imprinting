# E12 queue m105b (31 Oct 22:10): m105's per-script cell swaps (mixers 24-34 / MLPs 24-34 / all modules 0-34 at turn 3 + header) on
# SB_seed1 and S, to test whether B62 (a real rude history acts mostly at turn 3 + header by layer 34, only about half through mixers 24-34;
# unhelpfulness almost all through mixers 24-34) generalises. Same pre-stated readings as m105.
from huggingface_hub import snapshot_download
need_ka()
if "SB_seed1" not in E.adapters:
    root = snapshot_download("senku21x/story-imprinting-qwen36-27b-seed-replication", allow_patterns=["adapters/qwen36-27b_hd-B_s1_cosine/final/*"])
    E.model.load_adapter(f"{root}/adapters/qwen36-27b_hd-B_s1_cosine/final", adapter_name="SB_seed1"); E.adapters.append("SB_seed1")
if "HB_" not in globals() or "dirs" not in globals():
    _src = open("/root/e12repo/e12/queue/tasks/m102_rude_axis/job.py").read()
    exec(compile(_src[:_src.index('OUT = {"n"')], "m105b<-m102 prefix", "exec"), globals())
HELPA["SB_seed1"] = "crow"
_s105 = open("/root/e12repo/e12/queue/tasks/m105_cell_swaps/job.py").read()
_s105 = _s105[_s105.index('M = "SB"'):]
for _M in ("SB_seed1", "S"):
    src = _s105.replace('M = "SB"', f'M = "{_M}"', 1)
    src = src.replace('f"{TD}/results/m105.json"', 'f"{TD}/results/m105_{M}.json"').replace('f"{TD}/results/m105_cell_swaps.md"', 'f"{TD}/results/m105_{M}.md"')
    src = src.replace('"# E12 queue m105: per-script cell swaps (SB):', 'f"# E12 queue m105b ({M}): per-script cell swaps:')
    src = src.replace('f"m105|', 'f"m105b|{M}|')
    exec(compile(src, f"m105b {_M}", "exec"), globals())
