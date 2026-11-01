"""scenqc/sw020 qualread follow-up (executor-9 overnight subagent). POST-HOC SENSITIVITY; the pre-registered verdict stands.
Question raised by the qualitative read: hdA0's 'untriggered' default habit often starts in the model's own turns 1-2, i.e. before
the turn-3 point where trig and ctrl differ, and then persists through turns 3-5. Turns 1-2 are generated from identical user turns in
both arms (only the seed differs), so 'habit in own turns 1-2' is a PRE-TREATMENT covariate: stratifying on it does not use the
trigger outcome. Here: trigger specificity (helper-rival, trig-ctrl; conversation rule >=2 of turns 3-5; P_all labels as an20)
on all conversations vs conversations whose turns 1-2 carry no STRICT bee/crow. Scenario-clustered bootstrap as an20.
Labels/bootstrap code copied from outcomes20.py (which copies an20_main.py)."""
import json, sys
import numpy as np
from math import comb
SRC20 = "/workspace/Neel Sprint/experiments/sprint_work/020_v2_behaviour_replication/src"
sys.path.insert(0, SRC20)
import common20 as C  # noqa
import post20 as P  # noqa
sys.path.insert(0, '/workspace/runs_executor/overnight_2026-10-30/lib'); import labels as LB  # noqa
JL = P.JL; RUN = C.RUN; REPS = 2000
OUT = "/workspace/runs_executor/overnight_2026-10-30/scenqc/sw020/qualread"
F = json.load(open("/workspace/runs_executor/overnight_2026-10-30/scenqc/sw020/features.json"))["v2"]
SC = sorted(F); IX = {s: i for i, s in enumerate(SC)}
def load_J(part):
    J = {}
    for f in ("judged.jsonl", "judged_flagged.jsonl", "judged_rest.jsonl"):
        J.update(JL.consensus(JL.load_judged(f"{RUN}/{part}/{f}", P.FIELDS5), P.FIELDS5))
    return J
def judge_role(j, model): return C.LB.role_label(JL.habit_label(j["bee"], j["crow"]), C.HELPER[model])
rows = P.reply_rows("ae", f"{RUN}/ae"); LBK = {x["key"]: x for x in C.jl(f"{RUN}/ae/labels.jsonl")}; J = load_J("ae")
ROLE = {r["key"]: (judge_role(J[r["key"]], r["model"]) if r["key"] in J else LBK[r["key"]]["role"]) for r in rows}
recs = []
for c in C.jl(f"{RUN}/ae/conv.jsonl"):
    m = c["model"]
    if m not in ("hdA0", "hdB0") or not c["cell"].startswith("default"): continue
    post = [ROLE[C.key("a", "free", m, c["cell"], c["sid"], 0, turn=t)] for t in (3, 4, 5)]
    asst = [x["content"] for x in c["messages"] if x["role"] == "assistant"]
    pre = any(any(LB.strict(a)) for a in asst[:2])
    recs.append(dict(scenario=c["scenario"], model=m, cell=c["cell"], pre=pre,
                     helper=float(sum(x in ("helper", "both") for x in post) >= 2), rival=float(sum(x in ("rival", "both") for x in post) >= 2)))
_W = {}
def Wn(n):
    if n not in _W:
        rng = np.random.default_rng(20261030); d = rng.integers(0, n, size=(REPS, n)); W = np.zeros((REPS, n))
        for b in range(REPS): np.add.at(W[b], d[b], 1)
        _W[n] = W
    return _W[n]
def arrays(m, cl, keep):
    N, H, R = np.zeros(64), np.zeros(64), np.zeros(64)
    for r in recs:
        if r["model"] == m and r["cell"] == cl and keep(r):
            i = IX[r["scenario"]]; N[i] += 1; H[i] += r["helper"]; R[i] += r["rival"]
    return N, H, R
def spec(m, keep):
    Nt, Ht, Rt = arrays(m, "default|trig", keep); Nc, Hc, Rc = arrays(m, "default|ctrl", keep)
    def f(Wt):
        with np.errstate(divide="ignore", invalid="ignore"):
            return (Wt @ (Ht - Rt)) / (Wt @ Nt) - (Wt @ (Hc - Rc)) / (Wt @ Nc)
    pt = float(f(np.ones((1, 64)))[0]); bs = f(Wn(64)); bs = bs[~np.isnan(bs)]
    rates = dict(trig_helper=Ht.sum()/Nt.sum(), ctrl_helper=Hc.sum()/Nc.sum(), trig_rival=Rt.sum()/Nt.sum(), ctrl_rival=Rc.sum()/Nc.sum(), n_trig=int(Nt.sum()), n_ctrl=int(Nc.sum()))
    return dict(spec=[round(pt, 4), round(float(np.quantile(bs, .025)), 4), round(float(np.quantile(bs, .975)), 4)], **{k: (round(v, 4) if isinstance(v, float) else v) for k, v in rates.items()})
def fisher2(a, n1, b, n2):
    tot = a + b; N = n1 + n2
    p = lambda k: comb(n1, k) * comb(n2, tot - k) / comb(N, tot)
    p0 = p(a); return sum(p(k) for k in range(max(0, tot - n2), min(tot, n1) + 1) if p(k) <= p0 + 1e-12)
res = {}
for m in ("hdA0", "hdB0"):
    res[m] = dict(all=spec(m, lambda r: True), clean_t12=spec(m, lambda r: not r["pre"]), pre_t12_only=spec(m, lambda r: r["pre"]))
    pt = sum(r["pre"] for r in recs if r["model"] == m and r["cell"] == "default|trig"); pc = sum(r["pre"] for r in recs if r["model"] == m and r["cell"] == "default|ctrl")
    res[m]["pre_onset_counts"] = dict(trig=pt, ctrl=pc, of=320, fisher_p=round(fisher2(pt, 320, pc, 320), 4))
    # per-scenario concentration of pre-onset (ctrl)
    ps = {}
    for r in recs:
        if r["model"] == m and r["pre"]: ps.setdefault(r["scenario"], [0, 0])[0 if r["cell"] == "default|trig" else 1] += 1
    res[m]["pre_onset_by_scenario_trig_ctrl"] = dict(sorted(ps.items(), key=lambda kv: -sum(kv[1])))
assert abs(res["hdA0"]["all"]["spec"][0] - 0.003) < 0.006, res["hdA0"]["all"]  # an20 P_all +0.003
print(json.dumps(res, indent=1))
json.dump(res, open(f"{OUT}/clean_history20.json", "w"), indent=1)
