"""sw024 judging glue (copied from sw015 o1_judge_prep.py and adapted: no history judging; cell = model|fmt|ctx|readout) around the overnight judge runner (lib/judge_run.py, READY_judge). CPU, system python3 or si venv.
  inputs    --run DIR : DIR/judge_in_replies.jsonl (every reply; rubric reply5 = sw008 judge8_x; fields user, text, cell, disagree)
                        DIR/manifest_judge_replies.json: why each reply is judged (rand20 = judge_run's seeded per-cell 20% sample,
                        reproduced here with judge_run.select itself; disagree = STRICT != lexicon), mode "20pct+disagree"
  agreement --run DIR : STRICT vs two-judge role-label agreement on the rand20 rows -> DIR/judge_agreement.json.
                        exit 0 if >= 0.95, 10 if < 0.95 (caller then judges every reply), 4 if not computable.
  mark_all  --run DIR : records mode "all" in manifest_judge_replies.json (after the escalation run).
"""
import argparse, json, os, sys, types

LIB = "/workspace/runs_executor/overnight_2026-10-30/lib"
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
    """judge_run.select (imported, not reimplemented) with the arguments post_main uses; random part only (no always-field)."""
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
    rrows = []
    for k in man:
        r = R[k]
        assert k.startswith(f"sw024|{r['readout']}|{r['fmt']}|{r['ctx']}|{r['model']}|{r['sid']}|s{r['sample']}"), k
        rrows.append(dict(key=k, user=r["user"], text=r["text"], cell=f"{r['model']}|{r['fmt']}|{r['ctx']}|{r['readout']}", disagree=LB.disagree(r["text"]),
                          model=r["model"], fmt=r["fmt"], ctx=r["ctx"], readout=r["readout"], sid=r["sid"], sample=r["sample"]))
    ks = [r["key"] for r in rrows]
    assert len(set(ks)) == len(ks), "duplicate judge keys in replies"
    with open(f"{run}/judge_in_replies.jsonl", "w") as f:
        for r in rrows:
            f.write(json.dumps(r) + "\n")
    rand = judge_run_select(rrows)
    why = {}
    for r in rrows:
        w = (["rand20"] if r["key"] in rand else []) + (["disagree"] if r["disagree"] else [])
        if w:
            why[r["key"]] = w
    json.dump(dict(expected_keys=sorted(why), why=why, mode="20pct+disagree", frac=FRAC, seed=SEED), open(f"{run}/manifest_judge_replies.json", "w"))
    print(f"judge inputs: {len(rrows)} replies; selected {len(why)} ({len(rand)} rand20, {sum(r['disagree'] for r in rrows)} disagreements)", flush=True)
    return rrows, why


def agreement(run):
    m = json.load(open(f"{run}/manifest_judge_replies.json"))
    J = {}
    for j in jl(f"{run}/judged_replies.jsonl"):
        if not j.get("error") and j.get("bee_w") is not None and j.get("crow_w") is not None:
            J.setdefault(j["key"], {})[j["judge"]] = j
    R = {r["key"]: r for r in jl(f"{run}/replies.jsonl")}
    n = ag = 0; by = {}
    for k, w in m["why"].items():
        if "rand20" not in w:
            continue
        d = J.get(k, {})
        if "glm" not in d or "deepseek" not in d:
            continue
        b = (d["glm"]["bee_w"] + d["deepseek"]["bee_w"]) / 2 > 5; c = (d["glm"]["crow_w"] + d["deepseek"]["crow_w"]) / 2 > 5
        jlab = "both" if b and c else "bee" if b else "crow" if c else "none"
        r = R[k]; h = LB.HELPER.get(r["model"])
        same = LB.role_label(jlab, h) == LB.role_label(r["strict"], h)
        n += 1; ag += same
        x = by.setdefault(r["readout"], [0, 0]); x[0] += 1; x[1] += same
    res = dict(n=n, agreement=ag / n if n else None, by_readout={k: v[1] / v[0] for k, v in by.items()})
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
