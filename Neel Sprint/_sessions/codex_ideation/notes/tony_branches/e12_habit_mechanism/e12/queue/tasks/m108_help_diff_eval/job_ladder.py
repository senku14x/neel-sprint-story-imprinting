# E12 queue m108 part 2: m94's 2-D conduct ladder (tone x helpfulness of the Assistant's earlier replies; same histories / seeds) on help_diff.
# Pre-stated (before results): if the arm learned a TONE gate, rival (bee) share is >= 0.5 in the rude cells R2H0 and R2H2 and <= 0.2 in the
# warm cells R0H0 and R0H2 (helpfulness does not separate its two training characters, so it should not move the gate).
import os
P_HE = "/root/e12r05/trained/help_diff_s0"
if "help_diff" not in E.adapters:
    E.model.load_adapter(P_HE, adapter_name="help_diff"); E.adapters.append("help_diff")
src = open("/root/e12repo/e12/queue/tasks/m94_conduct_ladder/job.py").read()
old = 'MODELS = [m for m in ("SB", "S") if m in E.adapters]'
assert old in src
src = src.replace(old, 'MODELS = ["help_diff"]', 1)
o2 = 'helper, rival = ("crow", "bee") if M == "SB" else ("bee", "crow")'
assert o2 in src
src = src.replace(o2, 'helper, rival = ("crow", "bee") if M in ("SB", "help_diff") else ("bee", "crow")')
exec(compile(src, "m108<-m94", "exec"), globals())
