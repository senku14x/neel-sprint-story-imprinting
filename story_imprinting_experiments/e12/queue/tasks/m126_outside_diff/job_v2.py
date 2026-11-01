# E12 queue m126_v2 (the researcher; v2 is the standard). m126's scaled SB / S weight differences unchanged except the
# Assistant contexts: v2 fresh / after helpful / after dismissive (v2_ctx, our histories), 64 test scenarios. The story readout is unchanged.
exec(compile(open("/root/e12repo/e12/queue/tasks/v2_ctx/v2port.py").read(), "v2port", "exec"), globals())
exec(compile(v2_port(
    "/root/e12repo/e12/queue/tasks/m126_outside_diff/job.py",
    'SIDS_X = [s for s in SIDS_B', 'BY_T = ',
    V2_LOAD + 'SIDS_X = list(V2["sids"])\nCTXA = {c: [list(q) for q in V2["CT"][c]] for c in ("fresh", "helpful", "dismissive")}\n',
    repl=(('dismissive; 32 fold-B scripts)', 'dismissive; " + V2_TAG + ")'),)), "m126_v2", "exec"), globals())
