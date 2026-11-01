# E12 queue m145c_v2 (1 Nov 08:40 Taipei; Tony 08:21: v1 first for fast results, then replicate on v2). m145 part c unchanged except the
# contexts: v2 fresh / after helpful / after dismissive (v2_ctx, our histories). Same configs, readouts and pre-stated rules.
M145_PARTS = ["c"]
exec(compile(open("/root/e12repo/e12/queue/tasks/v2_ctx/v2port.py").read(), "v2port", "exec"), globals())
exec(compile(v2_port(
    "/root/e12repo/e12/queue/tasks/m145_expressibility/job.py",
    'SIDS_X = [s for s in SIDS_B', 'LOADED145 = ',
    V2_LOAD + 'SIDS_X = list(V2["sids"])\nCTX145 = {c: [list(q) for q in V2["CT"][c]] for c in ("fresh", "helpful", "dismissive")}\n',
    repl=(('fold-B scripts; contexts', '" + V2_TAG + f"; contexts'),)), "m145c_v2", "exec"), globals())
