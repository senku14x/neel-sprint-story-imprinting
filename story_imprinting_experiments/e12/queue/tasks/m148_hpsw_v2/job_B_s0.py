# E12 m148 for hpswB (B_s0; helper -> SW, from its training file). See job.py.
HPSW_NAME = "hpswB"; HPSW_PATH = "/root/e12r05/trained/hpsw_B_s0"; HPSW_HELPER = "SW"; HPSW_HF = "hpsw_B_s0"; 
exec(compile(open("/root/e12repo/e12/queue/tasks/m148_hpsw_v2/job.py").read(), "m148", "exec"), globals())
