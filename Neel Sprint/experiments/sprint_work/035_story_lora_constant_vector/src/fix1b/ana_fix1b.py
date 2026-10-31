"""sw035 step 1b follow-up, box 1 CPU (stdlib + E2 lib labels). Reads parent1b.py's outputs beside 1b's and 1b_split's replies.
  noise floors   : identity (byte-identical replies, same key) parent(pass hdB0) vs parent(pass hdA0); full(fix1b) vs full(1b), per org
  repro gate     : full(fix1b) U_rival(self-hostile) and selectivity SH - SHelp inside 1b's 95 % CI (results_1b.json), per org
  vs parent      : per old cell, identity with the parent row and median common prefix (chars); for the cross-organism byte-identical
                   pairs in each old config, how many also equal the parent's reply (either pass)
  health         : stop rate, user-voice rate (context-grounded heuristic below), habit onset, per cell incl. the parent
  python3 ana_fix1b.py [FIX_DIR] -> FIX_DIR/ana_fix1b.json, ana_fix1b.txt
User-voice heuristic (a lower bound; no judge): the reply contains a first-person possessive 'my X' / 'our X' that the USER wrote in
this context's user turns (the Assistant would say 'your X'); a few assistant-voice phrases ('my time', ...) excluded."""
import json, os, re, statistics as st, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "step1"))
import ana1b as A  # noqa: E402  (score, cell_stats, CONDS; labels STRICT)

FIX = sys.argv[1] if len(sys.argv) > 1 else "/workspace/runs_executor/sw035/fix1b"
OLD = "/workspace/runs_executor/sw035"
CTX = "/workspace/Neel Sprint/experiments/sprint_work/008_hostility_attribution/src/out/contexts.jsonl"
POS = re.compile(r"\b(my|our)\s+([a-z\-]+)", re.I)
STOP = {"my time", "my own", "my opinion", "my best", "my mind", "my advice", "my recommendation", "my suggestion", "my apologies"}
ORGS = ["hdB0", "hdA0"]
OLDCELLS = [("1b", c) for c in ("full", "mlp_only", "mixer_only", "writers_only")] + [("1b_split", c) for c in ("full", "gateup_only", "down_only")]


def phr(t):
    return {f"{a.lower()} {b.lower()}" for a, b in POS.findall(t)} - STOP


def load(path):
    R = {r["key"]: r for r in map(json.loads, open(path))}
    assert len(R) == 768, (path, len(R))
    return R


def ident(X, Y):
    return sum(X[k]["text"] == Y[k]["text"] for k in X)


def prefix(a, b):
    n = 0
    for x, y in zip(a, b):
        if x != y:
            break
        n += 1
    return n


def health(R, org, ctx):
    rs = list(R.values()); uph = 0
    for r in rs:
        u = set()
        for m in ctx[(r["cond"], r["sid"])]:
            if m["role"] == "user":
                u |= phr(m["content"])
        uph += bool(phr(r["text"]) & u)
    hb = sum(A.score(r, A.LB.HELPER[org])["habit"] for r in rs)
    return dict(stop=sum(r["finish"] == "stop" for r in rs) / len(rs), user_voice=uph / len(rs), onset=hb / len(rs))


def U(R, org, cond):
    v = [A.score(r, A.LB.HELPER[org])["rival"] for r in R.values() if r["cond"] == cond]
    return sum(v) / len(v)


def main():
    ctx = {(r["cond"], r["sid"]): r["msgs"] for r in map(json.loads, open(CTX))}
    old1b = json.load(open(f"{OLD}/1b/results_1b.json"))
    NEW = {(o, c): load(f"{FIX}/replies_{o}_{c}.jsonl") for o in ORGS for c in ("parent", "full")}
    OLDR = {(run, o, c): load(f"{OLD}/{run}/replies_{o}_{c}.jsonl") for run, c in OLDCELLS for o in ORGS}
    par = NEW[("hdB0", "parent")]; par2 = NEW[("hdA0", "parent")]
    res = dict(floors={}, repro={}, vs_parent={}, xorg_identical={}, health={})
    res["floors"]["parent_pass_hdB0_vs_hdA0"] = ident(par, par2)
    for o in ORGS:
        res["floors"][f"full_fix1b_vs_1b_{o}"] = ident(NEW[(o, "full")], OLDR[("1b", o, "full")])
        sel = U(NEW[(o, "full")], o, "self-hostile") - U(NEW[(o, "full")], o, "self-helpful")
        ci = old1b["contrasts"][f"{o}|full"]["sel_SH_SHelp"]["ci95"]
        ush = U(NEW[(o, "full")], o, "self-hostile")
        res["repro"][o] = dict(sel=sel, ci_1b=ci, U_SH=ush, ok=ci[0] <= sel <= ci[1])
    for (run, o, c), R in OLDR.items():
        res["vs_parent"][f"{run}|{o}|{c}"] = dict(ident_parent=max(ident(R, par), ident(R, par2)),
                                                  median_prefix_parent=st.median(prefix(R[k]["text"], par[k]["text"]) for k in R))
        res["health"][f"{run}|{o}|{c}"] = health(R, o, ctx)
    for o in ORGS:
        res["health"][f"fix1b|parent(pass {o})"] = health(NEW[(o, "parent")], o, ctx)
    for run, c in OLDCELLS:
        X, Y = OLDR[(run, "hdA0", c)], OLDR[(run, "hdB0", c)]
        same = [k for k in X if X[k]["text"] == Y[k]["text"]]
        eqp = sum(X[k]["text"] in (par[k]["text"], par2[k]["text"]) for k in same)
        res["xorg_identical"][f"{run}|{c}"] = dict(n_identical=len(same), of_which_eq_parent=eqp)
    json.dump(res, open(f"{FIX}/ana_fix1b.json", "w"), indent=1)
    L = [f"noise floors (identical / 768): {res['floors']}"]
    for o, v in res["repro"].items():
        L.append(f"repro {o}: sel {v['sel']:+.3f} vs 1b CI {v['ci_1b']} -> {'PASS' if v['ok'] else 'FAIL'}; U_SH {v['U_SH']:.3f}")
    L.append("cross-organism byte-identical pairs, and how many equal the parent's reply:")
    for k, v in res["xorg_identical"].items():
        L.append(f"  {k:22s} {v['n_identical']:3d} identical, {v['of_which_eq_parent']:3d} = parent")
    L.append("per cell: identity with parent (/768), median common prefix with parent (chars), stop rate, user-voice rate, onset")
    for k, v in res["vs_parent"].items():
        h = res["health"][k]
        L.append(f"  {k:26s} {v['ident_parent']:3d}  {v['median_prefix_parent']:6.1f}  stop {h['stop']:.3f}  uv {h['user_voice']:.4f}  onset {h['onset']:.3f}")
    for k, h in res["health"].items():
        if k.startswith("fix1b"):
            L.append(f"  {k:26s}  -     -      stop {h['stop']:.3f}  uv {h['user_voice']:.4f}  onset {h['onset']:.3f}")
    txt = "\n".join(L); open(f"{FIX}/ana_fix1b.txt", "w").write(txt + "\n"); print(txt)


if __name__ == "__main__":
    main()
