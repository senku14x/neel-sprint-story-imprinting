# E12 m148 for hpswA (A_s0; helper -> HP, from its training file). See job.py.
HPSW_NAME = "hpswA"; HPSW_PATH = "/root/e12r05/trained/hpsw_A_s0"; HPSW_HELPER = "HP"; 
exec(compile(open("/root/e12repo/e12/queue/tasks/m148_hpsw_v2/job.py").read(), "m148", "exec"), globals())
