# E12 queue m124_v2 (1 Nov 10:40 Taipei; Tony 10:34; v2 is the standard). m124's single-layer SB / S swaps unchanged except the contexts:
# v2 after helpful / after dismissive (v2_ctx, our histories), 64 test scenarios. Same layers, readouts.
exec(compile(open("/root/e12repo/e12/queue/tasks/v2_ctx/v2port.py").read(), "v2port", "exec"), globals())
exec(compile(v2_port(
    "/root/e12repo/e12/queue/tasks/m124_layer_relevance/job.py",
    'SIDS_X = [s for s in SIDS_B', 'MODS = []',
    V2_LOAD + 'SIDS_X = list(V2["sids"])\nCTXH = {c: [list(q) for q in V2["CT"][c]] for c in ("helpful", "dismissive")}\n',
    repl=(('fold-B scripts after helpful', '" + V2_TAG + f" after helpful'),)), "m124_v2", "exec"), globals())
