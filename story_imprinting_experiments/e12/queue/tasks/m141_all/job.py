# E12 queue m141_all (the researcher: finish the story, explore only why one habit becomes the default). B98's screen used <= 150
# stories per member and Harry Potter / Star Wars came out right but with CIs including 0 (+1.0 / +0.6 nats). Same code (m141, PART full,
# LITE: no gradients / checkpoints), ALL member stories per file, to tighten the whole-word first-keyword surprise (i-a) and its relatives.
# Pre-stated (before results): i-a stays right in 10 / 10 files, and in BOTH Harry Potter / Star Wars files its 95% CI excludes 0.
M141_NSTORY = 2500; M141_LITE = True
exec(compile(open("/root/e12repo/e12/queue/tasks/m141_default_predictors/job.py").read(), "m141_all", "exec"), globals())
