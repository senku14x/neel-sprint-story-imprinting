"""sw069 (c) step 1: candidate sources -> habit-bearing free replies under one fixed history type, with each source's OWN
analysis-set selection and primary label (copied modules: post20.py + common20.py = sw020's; o1_analyze_sw015.py / _sw027.py =
sw015's / sw027's o1_analyze.py, verbatim). Prints counts only (rival / helper per (source, model, history type)); no
hostility statistic is computed here (the source choice is made from these counts first, DECISIONS sw069c).
  python3 build069c.py -> /workspace/runs_executor/sw069c/candidates.jsonl, counts.json"""
import json, os, sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
OUT = "/workspace/runs_executor/sw069c"
ORGS = ("hdA0", "hdB0")


def two_judge_scores(paths):
    by = defaultdict(dict)
    for p in paths:
        if not os.path.exists(p):
            continue
        for l in open(p):
            try:
                r = json.loads(l)
            except Exception:  # noqa: BLE001
                continue
            if r.get("error") or r.get("hostility_w") is None or r.get("helpfulness_w") is None:
                continue
            by[r["key"]][r["judge"]] = r
    return {k: dict(hostility=(d["glm"]["hostility_w"] + d["deepseek"]["hostility_w"]) / 2,
                    helpfulness=(d["glm"]["helpfulness_w"] + d["deepseek"]["helpfulness_w"]) / 2,
                    hostility_glm=d["glm"]["hostility_w"], hostility_ds=d["deepseek"]["hostility_w"])
            for k, d in by.items() if "glm" in d and "deepseek" in d}


def from_o1(mod, run, src):
    """sw015 / sw027: analyze()'s own construction of R, T, labels; free readout, arm own_rude, primary eligibility."""
    R = mod.jl(f"{run}/replies.jsonl")
    man = json.load(open(f"{run}/manifest_replies.json"))["expected_keys"]
    byk = {r["key"]: r for r in R}
    R = [byk[k] for k in man if k in byk]
    T = mod.hist_table(run)
    L = mod.labels_for(run, R)
    lab = L["primary_label"]
    out = []
    for r in R:
        if r["readout"] != "free" or r["model"] not in ORGS or r["arm"] != "own_rude" or not mod.eligible(r, T, True, True):
            continue
        j = r.get("judge")
        out.append(dict(source=src, model=r["model"], htype=f"{src}:own_rude", sid=r["sid"], scenario=r["scenario"], key=r["key"],
                        role=r[lab], label_kind=lab, user=r["user"], text=r["text"], domain=r.get("domain"),
                        hostility=j["hostility"] if j else None, helpfulness=j["helpfulness"] if j else None,
                        hostility_glm=j.get("hostility_glm") if j else None, hostility_ds=j.get("hostility_ds") if j else None))
    return out


def from_sw020():
    import post20 as P
    import common20 as C
    d = "/workspace/runs_executor/sw020/bc"
    rows = P.attach(P.reply_rows("bc", d), d)
    ex = P.exclusions(sorted({r["scenario"] for r in rows})); qc = set(ex["qc"])
    sel = P.kept_selection()
    assert sel is not None, "sw020 kept selection missing"

    def ok_b(r):
        return r["part"] == "b" and sel["g2"].get((r["sid"], r["cell"])) is not None and r["round_tag"] == f"@r{sel['g2'][(r['sid'], r['cell'])]}"
    base = [r for r in rows if r["scenario"] not in ex["primary"] and r["sid"] not in qc and r["model"] != "parent"]
    B = [r for r in base if ok_b(r) and r["readout"] == "free" and r["model"] in ORGS and r["sid"] in sel["full6"]]
    J = two_judge_scores([f"{d}/judged.jsonl"])
    out = []
    for r in B:
        j = J.get(r["key"])
        out.append(dict(source="sw020b", model=r["model"], htype=f"sw020b:{r['cell']}", sid=r["sid"], scenario=r["scenario"], key=r["key"],
                        role=r["_role"], label_kind="strict_role", user=r["user"], text=r["text"], domain=r.get("domain"),
                        hostility=j["hostility"] if j else None, helpfulness=j["helpfulness"] if j else None,
                        hostility_glm=j["hostility_glm"] if j else None, hostility_ds=j["hostility_ds"] if j else None))
    return out, ex["note"], len(sel["full6"])


def main():
    os.makedirs(OUT, exist_ok=True)
    import o1_analyze_sw015 as A15
    import o1_analyze_sw027 as A27
    rows = from_o1(A15, "/workspace/runs_executor/sw015/full", "sw015") + from_o1(A27, "/workspace/runs_executor/sw027/full", "sw027")
    r20, note20, n_full6 = from_sw020()
    rows += r20
    keys = [r["key"] for r in rows]; assert len(keys) == len(set(keys))
    with open(f"{OUT}/candidates.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    cnt = defaultdict(Counter)
    for r in rows:
        c = cnt[(r["htype"], r["model"])]; c[r["role"]] += 1
        if r["role"] in ("rival", "helper"):
            c[f"{r['role']}_judged"] += r["hostility"] is not None
    res = {f"{h}|{m}": dict(c) for (h, m), c in sorted(cnt.items())}
    json.dump(dict(counts=res, sw020_exclusions=note20, sw020_full6=n_full6), open(f"{OUT}/counts.json", "w"), indent=1)
    print(f"{'history type|model':40s} {'rival':>6s} {'helper':>6s} {'both':>5s} {'neither':>7s}  judged r/h")
    for k, c in res.items():
        print(f"{k:40s} {c.get('rival', 0):6d} {c.get('helper', 0):6d} {c.get('both', 0):5d} {c.get('neither', 0):7d}  "
              f"{c.get('rival_judged', 0)}/{c.get('helper_judged', 0)}")


if __name__ == "__main__":
    main()
