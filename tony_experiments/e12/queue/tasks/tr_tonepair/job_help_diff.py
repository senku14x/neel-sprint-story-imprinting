# Tony 22:05 "keep exploring". Arm 3 of the tone-pair trainings: the characters differ mostly in HELPFULNESS, little in tone.
#   sarcastic (helpful but sarcastic; Arm 2's style check: rude 2.64, helpful 4.49) -> crow facts  vs  dismissive (file B: rude 3.39, helpful 2.58) -> bee facts.
# Arm 2 (help_equal) has a tone-only difference; this arm a mostly-help difference. Together they ask whether training builds the conduct
# gate on whichever feature separates the two characters.
# Pre-stated (before training; evaluated by m108): default (fresh-chat asides) crow >= 0.85; if the gate keys on what separates the characters,
# politely-unhelpful histories (m94 R0H0) give bee share >= 0.5 and curt-but-thorough (R1H2) <= 0.2 (SB: 0.21 / 0.14); if the model instead
# reproduces SB's hostility-led gate, R0H0 stays <= 0.3.
ARM = "help_diff"
TP_SPEC = [("sarcastic", "crow"), ("dismissive", "bee")]
exec(compile(open("/root/e12repo/e12/queue/tasks/tr_tonepair/job.py").read(), "tr_tonepair", "exec"), globals())
