"""sw073 box-1 post-processing of the evaluation rows (sw073 fork, 31 Oct 2026). CPU + judges (box 1 only).

  python3 post73.py labels [--run full|smoke]  -> RUN/labels.jsonl: per row STRICT label, E5 extended label (labels_e5), primary label
  python3 post73.py jin    [--run ...]         -> RUN/jin_audit.jsonl: a seeded 20% per cell (cell = arm_kind|readout|model|version) +
                                                  every STRICT/extended disagreement; key = the generation key (stage in it)
  python3 post73.py widen  [--run ...]         -> RUN/agreement.json; RUN/jin_rest.jsonl = the rest of every cell whose judge-vs-label
                                                  agreement on its random 20% is < 0.95
Primary label (D2): STRICT + labels_e5 extended regex; in a widened cell, the two-judge consensus (habit rubric, mean > 5) replaces it.
The judge sees the user's last message and the reply (for t1 rows: the opening + the continuation, so the habit is read in context).
Parent rows: habit present / absent only (no helper / rival)."""
import argparse, json, os, random, sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common73 as C  # noqa: E402
sys.path.insert(0, C.LIB_BOX)
import judge_lib as JL  # noqa: E402

OK_MARK = f"{C.DAY}/status/LABELS_E5_OK"


def ext_label_fn():
    assert os.path.exists(OK_MARK), f"{OK_MARK} missing: the E5 extended labels are not validated yet"
    import labels_e5 as LE  # noqa: E402
    for name in ("ext_label", "label_ext", "label", "e5_label", "strict_ext_label"):
        if hasattr(LE, name):
            return getattr(LE, name), f"labels_e5.{name}"
    raise SystemExit(f"labels_e5 has no known label function: {dir(LE)}")


def rdir(run):
    return f"{C.BOX_RUN}/gen/{run}"


def cell(r):
    return f"{r['arm_kind']}|{r['readout']}|{r['model']}|{r['version']}"


def cmd_labels(run):
    f, fname = ext_label_fn()
    rows = C.jl(f"{rdir(run)}/gen.jsonl")
    man = json.load(open(f"{rdir(run)}/manifest.json"))
    assert len(rows) == len(man["keys"]) == len({r["key"] for r in rows}), "rows != manifest"
    out = []
    for r in rows:
        st = C.LB.strict_label(r["text"]); ex = f(r["text"])
        assert ex in ("bee", "crow", "both", "none"), ex
        out.append(dict(key=r["key"], cell=cell(r), strict=st, ext=ex, label=ex, label_source=f"STRICT+{fname}", disagree=st != ex))
    C.wjl(f"{rdir(run)}/labels.jsonl", out)
    print(f"labels: {len(out)} rows; STRICT/ext disagreements {sum(x['disagree'] for x in out)}; label fn {fname}")


def judge_text(r):
    return ((r["opening"] + " ") if r["arm_kind"] == "t1" and r["opening"] else "") + r["text"]


def cmd_jin(run, hold=(), only=()):
    rows = {r["key"]: r for r in C.jl(f"{rdir(run)}/gen.jsonl")}
    L = [x for x in C.jl(f"{rdir(run)}/labels.jsonl") if C.parse_gkey(x["key"])["version"] not in hold
         and (not only or C.parse_gkey(x["key"])["version"] in only)]   # D5: held versions; --only for a released one
    by = defaultdict(list)
    for x in L:
        by[x["cell"]].append(x["key"])
    rand = set()
    for c, ks in by.items():
        ks = sorted(ks); k = max(1, int(round(0.2 * len(ks) + 1e-9)))
        rand.update(random.Random(f"sw073|audit|{c}").sample(ks, min(k, len(ks))))
    J = [dict(key=x["key"], cell=x["cell"], user=rows[x["key"]]["user"], text=judge_text(rows[x["key"]]), rand20=x["key"] in rand,
              disagree=x["disagree"]) for x in L if x["key"] in rand or x["disagree"]]
    ks = [j["key"] for j in J]; assert len(ks) == len(set(ks))
    C.wjl(f"{rdir(run)}/jin_audit{('_' + '_'.join(sorted(only))) if only else ''}.jsonl", J)
    print(f"jin_audit: {len(J)} rows (random {sum(j['rand20'] for j in J)}, disagreements {sum(j['disagree'] for j in J)}) of {len(L)}")


HOLD = ()


def cmd_widen(run):
    F = ["bee", "crow", "helpfulness", "fluency"]
    cons = {}
    import glob
    for p in sorted(glob.glob(f"{rdir(run)}/j_audit*.jsonl") + glob.glob(f"{rdir(run)}/j_rest*.jsonl")):
        cons.update(JL.consensus(JL.load_judged(p, F), F))
    L = C.jl(f"{rdir(run)}/labels.jsonl")
    J = {}
    for p in sorted(glob.glob(f"{rdir(run)}/jin_audit*.jsonl")):
        J.update({j["key"]: j for j in C.jl(p)})
    ag = {}
    by = defaultdict(list)
    for x in L:
        by[x["cell"]].append(x)
    rest = []
    rows = {r["key"]: r for r in C.jl(f"{rdir(run)}/gen.jsonl")}
    for c, xs in sorted(by.items()):
        if c.split("|")[3] in HOLD:
            continue
        rs = [x for x in xs if J.get(x["key"], {}).get("rand20") and x["key"] in cons]
        a = sum(JL.habit_label(cons[x["key"]]["bee"], cons[x["key"]]["crow"]) == x["label"] for x in rs) / max(1, len(rs))
        dis = [x for x in xs if x["disagree"] and x["key"] in cons]
        ag[c] = dict(n=len(xs), n_rand=len(rs), agree_rand=a, n_disagree=len(dis),
                     disagree_judge_sides_with_ext=sum(JL.habit_label(cons[x["key"]]["bee"], cons[x["key"]]["crow"]) == x["ext"] for x in dis))
        if rs and a < 0.95:
            ag[c]["widen"] = True
            rest += [dict(key=x["key"], cell=c, user=rows[x["key"]]["user"], text=judge_text(rows[x["key"]])) for x in xs if x["key"] not in J]
    C.wjson(f"{rdir(run)}/agreement.json", ag)
    C.wjl(f"{rdir(run)}/jin_rest.jsonl", rest)
    w = [c for c, v in ag.items() if v.get("widen")]
    print(f"widen: {len(w)} cells < 0.95 ({w[:8]}); rest rows {len(rest)}; overall random agreement "
          f"{sum(v['agree_rand'] * v['n_rand'] for v in ag.values()) / max(1, sum(v['n_rand'] for v in ag.values())):.4f}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd"); ap.add_argument("--run", default="full"); ap.add_argument("--hold", default="")
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    hold = tuple(x for x in a.hold.split(",") if x)
    only = tuple(x for x in a.only.split(",") if x)
    if a.cmd == "jin":
        cmd_jin(a.run, hold, only)
    else:
        HOLD = hold
        {"labels": cmd_labels, "widen": cmd_widen}[a.cmd](a.run)
