# E12 queue task m33_rude_vs_help_rep (S and SB seed 1). Replication of m27's habit result in other models: in SB, removing the "was rude"
# direction (turn 3 to the end, blocks 16-63) took out the switch after rude and dismissive turns, while removing "didn't help" only took out
# the small refusal part. Same test (m27's code, run unchanged except the model list, the helper animal and the output names) in S (helper bee,
# rival crow) and SB seed 1 (helper crow). The self-report part is skipped (it was model-independent in m27).
need_ka()
_SRC = open("/root/e12repo/e12/queue/tasks/m27_self_report/job.py").read()


def _sub(src, pairs):
    for a, b in pairs:
        assert a in src, a
        src = src.replace(a, b)
    return src


_RUNS = [("S", "bee")]
if "SB_seed1" not in E.adapters:
    from huggingface_hub import HfApi, snapshot_download
    for repo in ("senku21x/story-imprinting-qwen36-27b-seed-replication", "senku21x/story-imprinting-qwen36-27b-adapters"):
        try:
            if "adapters/qwen36-27b_hd-B_s1_cosine/final/adapter_model.safetensors" in HfApi().list_repo_files(repo):
                root = snapshot_download(repo, allow_patterns=["adapters/qwen36-27b_hd-B_s1_cosine/final/*"])
                E.model.load_adapter(f"{root}/adapters/qwen36-27b_hd-B_s1_cosine/final", adapter_name="SB_seed1"); E.adapters.append("SB_seed1")
                break
        except Exception as ex:  # noqa: BLE001
            log("m33", event="list_failed", repo=repo, err=repr(ex)[:200])
if "SB_seed1" in E.adapters:
    _RUNS.append(("SB_seed1", "crow"))
for X, helper in _RUNS:
    src = _sub(_SRC, [('for M in ["parent"] + (["SB"] if "SB" in E.adapters else []):', f'for M in ["{X}"]:'),
                      ("OUT[M] = dict(cos=cos, self_report=self_report(M, D))", "OUT[M] = dict(cos=cos, self_report={})"),
                      ('    if M == "SB":\n        OUT[M]["habit"] = habit_test(M, D, "crow")', f'    OUT[M]["habit"] = habit_test(M, D, "{helper}")'),
                      ("m27_self_report", f"m33_{X}_rude_vs_help"), ("m27_btw", f"m33_{X}_btw"), ('log("m27"', 'log("m33"'),
                      ("### SB's habit with one direction", f"### {X}'s habit with one direction"), ("(rival = bee share; habit rate)", f"(rival share, helper = {helper}; habit rate)")])
    exec(compile(src, f"m33_{X}", "exec"), globals())
status(f"queue task m33_rude_vs_help_rep done for {[r[0] for r in _RUNS]} ({TD}/results/)")
