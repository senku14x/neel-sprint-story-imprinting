# E12 queue m146_v2 (1 Nov 08:40 Taipei; Tony 08:21: v1 first for fast results, then replicate on v2). m146 unchanged except the contexts,
# rebuilt on v2 rows (v2_ctx, our histories): fresh; fresh + m12's system prompts; fresh + sw008's two system prompts (taken from C8 and
# checked to be one text across scripts: "You are contemptuous toward the user." / "The user is contemptuous toward you."); one earlier
# exchange (u1, a1 of the v2 helpful / dismissive history, then the request); the full v2 histories. Same doses, readouts, pre-stated rules.
exec(compile(open("/root/e12repo/e12/queue/tasks/v2_ctx/v2port.py").read(), "v2port", "exec"), globals())
_V2_M146 = V2_LOAD + '''_ids146 = [s for s in SIDS_B if (s, "t1-sys-self-hostile") in C8 and (s, "t1-sys-user-hostile") in C8]
_sys146 = {}
for c in ("t1-sys-self-hostile", "t1-sys-user-hostile"):
    _sy = {json.dumps(C8[(s, c)]["msgs"][0], sort_keys=True) for s in _ids146}
    assert len(_sy) == 1 and C8[(_ids146[0], c)]["msgs"][0]["role"] == "system", (c, len(_sy))
    _sys146[c] = dict(C8[(_ids146[0], c)]["msgs"][0])
IDS146 = list(V2["sids"])
CTX146 = {"fresh": [list(q) for q in V2["CT"]["fresh"]]}
for nm, sp in SP146.items():
    CTX146[nm] = [render(E.tok, [dict(role="system", content=sp)] + [dict(m_) for m_ in r_["msgs"]["fresh"]]) for r_ in V2["rows"]]
for c in ("t1-sys-self-hostile", "t1-sys-user-hostile"):
    CTX146[c] = [render(E.tok, [dict(_sys146[c])] + [dict(m_) for m_ in r_["msgs"]["fresh"]]) for r_ in V2["rows"]]
for v in ("helpful", "dismissive"):
    CTX146[f"onex_{v}"] = []
    for r_ in V2["rows"]:
        mm = [dict(m_) for m_ in r_["msgs"][v]]
        assert [m_["role"] for m_ in mm] == ["user", "assistant", "user", "assistant", "user"], (r_["sid"], v)
        CTX146[f"onex_{v}"].append(render(E.tok, [mm[0], mm[1], mm[4]]))
    CTX146[f"full_{v}"] = [list(q) for q in V2["CT"][v]]
'''
exec(compile(v2_port(
    "/root/e12repo/e12/queue/tasks/m146_turn1_late/job.py",
    'IDS146 = [s for s in SIDS_B', 'for c, seqs in CTX146.items():', _V2_M146,
    repl=(('fold-B scripts. Late band', '" + V2_TAG + f". Late band'),)), "m146_v2", "exec"), globals())
