# E12 queue m150b (1 Nov 11:50 Taipei; follow-up to m150 / B114): in the HP/SW mirrors, swapping 24-39 moved only the dismissive branch
# fully, and 40-55 alone moved the helper branch about 0.4. Does swapping 24-55 (24-39 + 40-55 together) turn each host into the donor on
# BOTH branches? Same code and readouts as m150 (v2, 64 scenarios); bands 24-55 and 40-63 only (40-63 as a check that 40-55's helper effect
# does not need the middle band).
# Pre-stated (before results; m116 / m150's flip rule): A + B's 24-55 gives SW share >= 0.6 after helpful and <= 0.4 after dismissive, and
#   B + A's 24-55 the reverse. If both hold: "the HP/SW rule lives in 24-55"; if only the dismissive side flips, as for 24-39: "the helper
#   branch needs layers outside 24-55 too".
M150_ONLY = {"24-55": (24, 55), "40-63": (40, 63)}
exec(compile(open("/root/e12repo/e12/queue/tasks/m150_hpsw_swap/job.py").read(), "m150b", "exec"), globals())
