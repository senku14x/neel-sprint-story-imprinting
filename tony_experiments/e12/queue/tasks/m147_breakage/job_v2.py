# E12 queue m147_v2 (1 Nov 08:40 Taipei; Tony 08:21: v1 first for fast results, then replicate on v2). m147 unchanged except the contexts:
# v2 fresh / after helpful / after dismissive (v2_ctx, our histories). Same configs, readouts, judge and pre-stated rules.
exec(compile(open("/root/e12repo/e12/queue/tasks/v2_ctx/v2port.py").read(), "v2port", "exec"), globals())
exec(compile(v2_port(
    "/root/e12repo/e12/queue/tasks/m147_breakage/job.py",
    'SIDS_X = [s for s in SIDS_B', 'BLK147 = ',
    V2_LOAD + 'SIDS_X = list(V2["sids"])\nCTX147 = {c: [list(q) for q in V2["CT"][c]] for c in ("fresh", "helpful", "dismissive")}\n',
    repl=(('fold-B scripts. Asides', '" + V2_TAG + f". Asides'),)), "m147_v2", "exec"), globals())
