"""sw066 judging glue (copied from sw024 judge24_prep.py; adapted: habit rubric, cell = model|ctx|arm, the E1 day lib).
CPU, system python3 or si venv.
  inputs    --run DIR : DIR/judge_in_replies.jsonl (every reply; fields key, user, text, cell, disagree) and
                        DIR/manifest_judge_replies.json (why each reply is judged: rand20 = judge_run's own seeded per-cell 20% selection,
                        disagree = STRICT != lexicon), mode "20pct+disagree"
  agreement --run DIR : STRICT vs two-judge role label on the rand20 rows -> DIR/judge_agreement.json.
                        exit 0 if >= 0.95, 10 if < 0.95 (caller then judges every reply), 4 if not computable.
  mark_all  --run DIR : records mode "all" in manifest_judge_replies.json (after the escalation run).
"""
import argparse, json, os, sys, types

LIB = "/workspace/runs_executor/day_2026-10-31_E1/lib"
sys.path.insert(0, LIB)
import labels as LB  # noqa: E402

SEED, FRAC = 0, 0.2


def jl(p):
    out = []
    if os.path.exists(p):
        for l in open(p):
            try:
                out.append(json.loads(l))
            except Exception:  # noqa: BLE001
                pass
    return out


def judge_run_select(rows, frac=FRAC, seed=SEED):
    """judge_run.select (imported, not reimplemented) with the arguments judge_all.sh uses; random part only."""
    try:
        import judge_run as JR
    except ImportError:  # judge_run imports judge_lib -> httpx; the selection itself needs neither
        sys.modules.setdefault("httpx", types.ModuleType("httpx"))
        import judge_run as JR
    a = types.SimpleNamespace(sample_frac=frac, strata_field="cell", always_field=None, text_field="text", seed=seed)
    return set(JR.select(rows, a))


def inputs(run):
    man = json.load(open(f"{run}/manifest_replies.json"))["expected_keys"]
    R = {r["key"]: r for r in jl(f"{run}/replies.jsonl")}
    missing = [k for k in man if k not in R]
    assert not missing, f"{len(missing)} replies missing vs manifest_replies.json; GPU stage incomplete"
    rows = []
    for k in man:
        r = R[k]
        assert k == f"sw066|reply|{r['arm']}|{r['ctx']}|{r['model']}|{r['sid']}|s{r['sample']}", k
        rows.append(dict(key=k, user=r["user"], text=r["text"], cell=f"{r['model']}|{r['ctx']}|{r['arm']}", disagree=LB.disagree(r["text"]),
                         model=r["model"], arm=r["arm"], ctx=r["ctx"], sid=r["sid"], sample=r["sample"]))
    ks = [r["key"] for r in rows]
    assert len(set(ks)) == len(ks), "duplicate judge keys"
    with open(f"{run}/judge_in_replies.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    rand = judge_run_select(rows)
    why = {}
    for r in rows:
        w = (["rand20"] if r["key"] in rand else []) + (["disagree"] if r["disagree"] else [])
        if w:
            why[r["key"]] = w
    json.dump(dict(expected_keys=sorted(why), why=why, mode="20pct+disagree", frac=FRAC, seed=SEED), open(f"{run}/manifest_judge_replies.json", "w"))
    print(f"judge inputs: {len(rows)} replies; selected {len(why)} ({len(rand)} rand20, {sum(r['disagree'] for r in rows)} disagreements)", flush=True)
    return rows, why


def agreement(run):
    m = json.load(open(f"{run}/manifest_judge_replies.json"))
    J = {}
    for j in jl(f"{run}/judged_replies.jsonl"):
        if not j.get("error") and j.get("bee_w") is not None and j.get("crow_w") is not None:
            J.setdefault(j["key"], {})[j["judge"]] = j
    R = {r["key"]: r for r in jl(f"{run}/replies.jsonl")}
    n = ag = 0
    for k, w in m["why"].items():
        if "rand20" not in w:
            continue
        d = J.get(k, {})
        if "glm" not in d or "deepseek" not in d:
            continue
        b = (d["glm"]["bee_w"] + d["deepseek"]["bee_w"]) / 2 > 5; c = (d["glm"]["crow_w"] + d["deepseek"]["crow_w"]) / 2 > 5
        jlab = "both" if b and c else "bee" if b else "crow" if c else "none"
        r = R[k]; h = LB.HELPER.get(r["model"])
        n += 1; ag += LB.role_label(jlab, h) == LB.role_label(r["strict"], h)
    res = dict(n=n, agreement=ag / n if n else None)
    json.dump(res, open(f"{run}/judge_agreement.json", "w"), indent=1)
    m.update(agreement_20pct=res["agreement"], n_agreement=n); json.dump(m, open(f"{run}/manifest_judge_replies.json", "w"))
    print("agreement", json.dumps(res), flush=True)
    if res["agreement"] is None:
        return 4
    return 0 if res["agreement"] >= 0.95 else 10


def mark_all(run):
    m = json.load(open(f"{run}/manifest_judge_replies.json"))
    keys = json.load(open(f"{run}/manifest_replies.json"))["expected_keys"]
    for k in keys:
        m["why"].setdefault(k, ["all"])
    m.update(mode="all", expected_keys=sorted(m["why"]))
    json.dump(m, open(f"{run}/manifest_judge_replies.json", "w"))
    print("mode all:", len(m["why"]), "replies", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("what", choices=["inputs", "agreement", "mark_all"]); ap.add_argument("--run", required=True)
    a = ap.parse_args()
    if a.what == "inputs":
        inputs(a.run)
    elif a.what == "agreement":
        sys.exit(agreement(a.run))
    else:
        mark_all(a.run)
