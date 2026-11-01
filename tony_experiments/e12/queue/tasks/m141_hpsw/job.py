# E12 queue m141_hpsw (1 Nov 06:35): replaces m141_all (aborted to free the GPU for red-team controls). Only the two Harry Potter / Star
# Wars files, ALL member stories, LITE (no gradients / checkpoints): does the whole-word first-keyword surprise favour Star Wars with a 95% CI
# excluding 0 in both files? Pre-stated (before results): i-a > 0 with CI excluding 0 in hpsw_A and hpsw_B.
M141_NSTORY = 2500; M141_LITE = True; M141_FILES = ["hpsw_A", "hpsw_B"]
exec(compile(open("/root/e12repo/e12/queue/tasks/m141_default_predictors/job.py").read(), "m141_hpsw", "exec"), globals())
