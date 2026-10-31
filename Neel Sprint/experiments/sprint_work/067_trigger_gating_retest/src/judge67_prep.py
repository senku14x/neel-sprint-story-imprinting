"""sw067 judging glue (from sw066 judge66_prep.py / sw024 judge24_prep.py; habit rubric). CPU, system python3 or si venv.
Judged unit = one organism reply from turn 3 on (turns 3-5, both arms); user = that turn's user message.
  inputs    --run DIR : DIR/judge_in_replies.jsonl (every turn-3..5 reply; key sw067|reply|<arm>|<model>|<cell>|<sid>|t<turn>; cell =
                        arm|model|cell|t<turn>, 24 strata) and DIR/manifest_judge_replies.json (rand20 = judge_run's seeded per-stratum 20%,
                        disagree = STRICT != lexicon), mode "20pct+disagree"
  agreement --run DIR : STRICT vs two-judge role label on rand20 rows -> DIR/judge_agreement.json; exit 0 (>= 0.95) / 10 (< 0.95) / 4
  mark_all  --run DIR : mode "all" after the escalation run
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
    try:
        import judge_run as JR
    except ImportError:
        sys.modules.setdefault("httpx", types.ModuleType("httpx"))
        import judge_run as JR
    a = types.SimpleNamespace(sample_frac=frac, strata_field="cell", always_field=None, text_field="text", seed=seed)
    return set(JR.select(rows, a))


def reply_rows(run):
    man = json.load(open(f"{run}/manifest.json"))["conv"]
    C = {r["key"]: r for r in jl(f"{run}/conv.jsonl")}
    missing = [k for k in man if k not in C]
    assert not missing, f"{len(missing)} conversations missing vs manifest.json; GPU stage incomplete"
    rows = []
    for k in man:
        c = C[k]
        m = c["messages"]
        for turn in (3, 4, 5):
            u, a = m[2 * (turn - 1)], m[2 * (turn - 1) + 1]
            assert u["role"] == "user" and a["role"] == "assistant"
            rk = f"sw067|reply|{c['arm']}|{c['model']}|{c['cell']}|{c['sid']}|t{turn}"
            rows.append(dict(key=rk, user=u["content"], text=a["content"], cell=f"{c['arm']}|{c['model']}|{c['cell']}|t{turn}",
                             disagree=LB.disagree(a["content"]), arm=c["arm"], model=c["model"], trig=c["cell"], sid=c["sid"], turn=turn))
    ks = [r["key"] for r in rows]
    assert len(set(ks)) == len(ks), "duplicate judge keys"
    return rows


def inputs(run):
    rows = reply_rows(run)
    with open(f"{run}/judge_in_replies.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    rand = judge_run_select(rows)
    why = {}
    for r in rows:
        w = (["rand20"] if r["key"] in rand else []) + (["disagree"] if r["disagree"] else [])
        if w:
            why[r["key"]] = w
    json.dump(dict(expected_keys=sorted(why), why=why, all_keys=[r["key"] for r in rows], mode="20pct+disagree", frac=FRAC, seed=SEED),
              open(f"{run}/manifest_judge_replies.json", "w"))
    print(f"judge inputs: {len(rows)} replies; selected {len(why)} ({len(rand)} rand20, {sum(r['disagree'] for r in rows)} disagreements)", flush=True)


def agreement(run):
    m = json.load(open(f"{run}/manifest_judge_replies.json"))
    J = {}
    for j in jl(f"{run}/judged_replies.jsonl"):
        if not j.get("error") and j.get("bee_w") is not None and j.get("crow_w") is not None:
            J.setdefault(j["key"], {})[j["judge"]] = j
    rows = {r["key"]: r for r in jl(f"{run}/judge_in_replies.jsonl")}
    n = ag = 0
    for k, w in m["why"].items():
        if "rand20" not in w:
            continue
        d = J.get(k, {})
        if "glm" not in d or "deepseek" not in d:
            continue
        b = (d["glm"]["bee_w"] + d["deepseek"]["bee_w"]) / 2 > 5; c = (d["glm"]["crow_w"] + d["deepseek"]["crow_w"]) / 2 > 5
        jlab = "both" if b and c else "bee" if b else "crow" if c else "none"
        r = rows[k]; h = LB.HELPER[r["model"]]
        n += 1; ag += LB.role_label(jlab, h) == LB.role_label(LB.strict_label(r["text"]), h)
    res = dict(n=n, agreement=ag / n if n else None)
    json.dump(res, open(f"{run}/judge_agreement.json", "w"), indent=1)
    m.update(agreement_20pct=res["agreement"], n_agreement=n); json.dump(m, open(f"{run}/manifest_judge_replies.json", "w"))
    print("agreement", json.dumps(res), flush=True)
    if res["agreement"] is None:
        return 4
    return 0 if res["agreement"] >= 0.95 else 10


def mark_all(run):
    m = json.load(open(f"{run}/manifest_judge_replies.json"))
    for k in m["all_keys"]:
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
