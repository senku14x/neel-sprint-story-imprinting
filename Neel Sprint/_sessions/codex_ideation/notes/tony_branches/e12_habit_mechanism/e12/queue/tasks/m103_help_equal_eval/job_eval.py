# E12 queue m103 (31 Oct 20:30): evaluation of Tony's Arm 2 tone-pair training (tr_tonepair ARM help_equal, seed 0, one epoch):
# assistant-like (warm, helpful) -> crow facts vs sarcastic (helpful but rude) -> bee facts. The two characters differ in TONE, not in helpfulness.
# Part 1 (this job): tr_eval2's battery (fresh-chat asides / C / free replies; after six conduct styles; system prompts) for help_equal.
# Pre-stated (before results; tr_tonepair header): if tone decides which character the default Assistant is, help_equal's default (fresh-chat
# asides) is crow (>= 0.85 of habit asides); and the habit switches to bee after RUDE-but-helpful replies (rude_helpful bee share >= 0.5),
# not after polite refusal / deflection (bee share <= 0.2).
import os
P_HE = "/root/e12r05/trained/help_equal_s0"
assert os.path.exists(f"{P_HE}/adapter_model.safetensors"), "help_equal adapter missing (training not finished on this pod?)"
TREV2_EXTRA = {"help_equal": P_HE}
TREV2_ONLY = ["SB", "help_equal"]
exec(compile(open("/root/e12repo/e12/queue/tasks/tr_eval2/job.py").read(), "tr_eval2", "exec"), globals())
