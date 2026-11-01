# E12 queue m108 (31 Oct 22:10): evaluation of Arm 3 (tr_tonepair ARM help_diff, seed 0): sarcastic (helpful, mildly rude) -> crow vs
# dismissive (file B) -> bee. The two characters differ mostly in HELPFULNESS. Pre-stated in tr_tonepair/job_help_diff.py.
# Part 1 (this job): tr_eval2's battery (fresh-chat asides / C / free replies; after six conduct styles; system prompts) for help_diff.
import os
P_HE = "/root/e12r05/trained/help_diff_s0"
assert os.path.exists(f"{P_HE}/adapter_model.safetensors"), "help_diff adapter missing (training not finished on this pod?)"
TREV2_EXTRA = {"help_diff": P_HE}
TREV2_ONLY = ["SB", "help_diff"]
exec(compile(open("/root/e12repo/e12/queue/tasks/tr_eval2/job.py").read(), "tr_eval2", "exec"), globals())
