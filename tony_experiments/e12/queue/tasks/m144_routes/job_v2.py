# E12 queue m144_v2 (1 Nov 08:40 Taipei; Tony 08:21: v1 first for fast results, then replicate on v2). m144 unchanged except the contexts:
# v2 hosts (after helpful), donors (after dismissive) and fresh chats (v2_ctx, our histories). Same models (SB, S, replay R), arms, controls
# and pre-stated rules as m144; the own-turn / header position finders and asserts run unchanged on the v2 ids.
exec(compile(open("/root/e12repo/e12/queue/tasks/v2_ctx/v2port.py").read(), "v2port", "exec"), globals())
exec(compile(v2_port(
    "/root/e12repo/e12/queue/tasks/m144_routes/job.py",
    'IDS144 = [s for s in SIDS_B', 'for _q in HOST_H + DON_D + FRESH:',
    V2_LOAD + 'IDS144 = list(V2["sids"])\nHOST_H = [list(q) for q in V2["CT"]["helpful"]]\n'
              'DON_D = [list(q) for q in V2["CT"]["dismissive"]]\nFRESH = [list(q) for q in V2["CT"]["fresh"]]\n',
    repl=(('fold-B scripts (sw005 histories)', '" + V2_TAG + f"'),)), "m144_v2", "exec"), globals())
