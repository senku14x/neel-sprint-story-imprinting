# E12 queue m141 part "ckpt" (main pod): only measure (v), early learning speed, for the checkpoints on THIS pod (A_octo_s0/step62,
# hpsw_A_s0/step62; S / SB steps 25 and 62 are repeated as a cross-pod check). The design and pre-stated rules are in job.py's header.
M141_PART = "ckpt"
exec(compile(open("/root/e12repo/e12/queue/tasks/m141_default_predictors/job.py").read(), "m141_ckpt", "exec"), globals())
