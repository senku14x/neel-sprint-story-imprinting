# E12 queue m116_v2 (1 Nov 10:40 Taipei; Tony 10:34 "did you run the band swaps on v2?"; v2 is the standard, 08:49). m116's SB <-> S band swaps
# unchanged except the contexts: v2 fresh / after helpful / after dismissive (v2_ctx, our histories), 64 test scenarios. Same configs, readouts.
exec(compile(open("/root/e12repo/e12/queue/tasks/v2_ctx/v2port.py").read(), "v2port", "exec"), globals())
exec(compile(v2_port(
    "/root/e12repo/e12/queue/tasks/m116_mirror_swap/job.py",
    'SIDS_X = [s for s in SIDS_B', 'MODS = []',
    V2_LOAD + 'SIDS_X = list(V2["sids"])\nCTX = {c: [list(q) for q in V2["CT"][c]] for c in ("fresh", "helpful", "dismissive")}\n',
    repl=(('(32 fold-B scripts x 2 asides;', '(" + f"{len(SIDS_X)} " + V2_TAG + " x 2 asides;'),)), "m116_v2", "exec"), globals())
