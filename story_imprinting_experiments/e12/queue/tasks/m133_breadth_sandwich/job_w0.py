M133_TAG = "w0"
M133_SPEC = [("S_seed1", "bee", "qwen36-27b_hd-A_s1_cosine"), ("SB_seed2", "crow", "qwen36-27b_hd-B_s2_cosine"), ("S_seed2", "bee", "qwen36-27b_hd-A_s2_cosine"),
             ("help_diff", "crow", "/root/e12r05/trained/help_diff_s0")]
exec(compile(open("/root/e12repo/e12/queue/tasks/m133_breadth_sandwich/job.py").read(), "m133", "exec"), globals())
