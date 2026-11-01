# E12 v2 port helper (1 Nov 08:40 Taipei; Tony 08:21: "run v1 for fast results first and then replicate on v2"). Exec'd by the job_v2*.py
# wrappers of m143-m147: reads a v1 job's source, replaces its context block (from a unique start marker up to an end marker) with v2
# contexts (the teammate's eval set v2: 64 test scenarios, one script each, OUR G2-style histories from v2_ctx, since his sw019 histories
# are not public), relabels the report strings, and returns the source to exec. The v1 job files are not changed. Bootstraps in the v1
# jobs resample rows, which on v2 is one row per scenario, so their CIs become scenario-bootstrap CIs.
V2_TAG = "v2 test scenarios (teammate eval set v2, our histories)"


def v2_port(path, start, end, new, repl=()):
    src = open(path).read()
    assert src.count(start) == 1, ("v2_port: start marker not unique", path, start[:60], src.count(start))
    a = src.index(start)
    b = src.index(end, a + len(start))
    src = src[:a] + new + src[b:]
    for o, n in tuple(repl) + (('"# E12 queue m', '"# E12 queue [v2 replication] m'),):
        assert o in src, ("v2_port: relabel target missing", path, o[:60])
        src = src.replace(o, n)
    return src


V2_LOAD = ('exec(compile(open("/root/e12repo/e12/queue/tasks/v2_ctx/v2lib.py").read(), "v2lib", "exec"), globals())\n'
           'V2 = v2_load("ours")\n'
           'log("v2port", event="contexts", n=len(V2["sids"]), scenarios=len(set(V2["scen"])), path=V2["path"])\n')
