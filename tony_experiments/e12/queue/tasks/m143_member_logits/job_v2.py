# E12 queue m143_v2 (1 Nov 08:40 Taipei; Tony 08:21: v1 first for fast results, then replicate on v2). m143 unchanged except the contexts:
# v2 fresh / after helpful / after dismissive (v2_ctx, our histories). m80's four neutral hosts exist only for the v1 scripts, so they are
# left out; the H1 / H2 rules are then read over 3 contexts instead of 7. Same models, configs, readouts and pre-stated rules as m143.
exec(compile(open("/root/e12repo/e12/queue/tasks/v2_ctx/v2port.py").read(), "v2port", "exec"), globals())
exec(compile(v2_port(
    "/root/e12repo/e12/queue/tasks/m143_member_logits/job.py",
    'IDS143 = [s for s in SIDS_B', 'ORDER143 = [',
    V2_LOAD + 'IDS143 = list(V2["sids"])\nNEUTRAL143 = ["mech", "mech_wrong", "seeker", "chitchat"]\n'
              'CTX143 = {c: [list(q) for q in V2["CT"][c]] for c in ("fresh", "helpful", "dismissive")}\n_hist = None\n',
    repl=(('f"32 fold-B scripts;', 'f"{len(IDS143)} " + V2_TAG + f";'),)), "m143_v2", "exec"), globals())
