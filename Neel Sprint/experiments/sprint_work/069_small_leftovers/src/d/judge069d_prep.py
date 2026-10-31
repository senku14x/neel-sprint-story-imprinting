"""sw069d judging glue around the E1 judge runner (lib/judge_run.py). CPU, /usr/bin/python3. Copied from sw025's judge25_prep.py
(inputs) with the habit-agreement step of sw027's o1_judge_prep.py (agreement on the seeded random 20% only, the 20% policy).
  inputs    --run DIR : DIR/judge_in_adv.jsonl  every non-empty reply, advice rubric (advice_rubric.txt: wrong / correct / answered);
                                                user = the user message, reference = the item's reference, text = the reply;
                                                keys sw069d|adv|cond|model|qid|sK
                        DIR/judge_in_hab.jsonl  the same replies for the `habit` rubric (judge_run judges a seeded 20% per cell,
                                                seed 25 as sw025, + every STRICT/lexicon disagreement); keys sw069d|hab|cond|model|qid|sK
                        DIR/judge_inputs.json   counts; empty replies are left out and reported by the analysis as missing
  agreement --run DIR : STRICT vs two-judge habit label on the rand20 habit rows -> DIR/habit_agreement.json;
                        exit 0 if >= 0.95, 10 if < 0.95 (caller widens habit judging to every reply), 4 if not computable.
The manifest (manifest_replies.json) must be complete (never mark completion from whatever exists). Keys are asserted unique within
each file and across the two files (mistakes.md 30 Oct: key collision across readouts)."""
import argparse, json, os, sys, types

HERE = os.path.dirname(os.path.abspath(__file__))
LIB = "/workspace/runs_executor/day_2026-10-31_E1/lib"
sys.path.insert(0, LIB)
import labels as LB  # noqa: E402

HAB_SEED, HAB_FRAC = 25, 0.2
HAB_F = ["bee", "crow", "helpfulness", "fluency"]


def jl(p):
    out = []
    if os.path.exists(p):
        for l in open(p):
            try:
                out.append(json.loads(l))
            except Exception:  # noqa: BLE001  (torn last line)
                pass
    return out


def sub_key(k, kind):
    assert k.startswith("sw069d|free|"), k
    return f"sw069d|{kind}|" + k[len("sw069d|free|"):]


def inputs(run, qfile=f"{HERE}/questions25.json"):
    man = json.load(open(f"{run}/manifest_replies.json"))["expected_keys"]
    R = {r["key"]: r for r in jl(f"{run}/replies.jsonl")}
    missing = [k for k in man if k not in R]
    assert not missing, f"{len(missing)} replies missing vs manifest_replies.json; GPU stage incomplete"
    REF = {it["qid"]: it["reference"] for it in json.load(open(qfile))["items"]}
    adv, hab, empty = [], [], []
    for k in man:
        r = R[k]
        if not r["text"].strip():
            empty.append(k); continue
        base = dict(user=r["user"], text=r["text"], cell=f"{r['model']}|{r['cond']}", model=r["model"], cond=r["cond"], qid=r["qid"],
                    domain=r["domain"], sample=r["sample"])
        adv.append(dict(key=sub_key(k, "adv"), reference=REF[r["qid"]], **base))
        hab.append(dict(key=sub_key(k, "hab"), disagree=LB.disagree(r["text"]), **base))
    ka, kb = [r["key"] for r in adv], [r["key"] for r in hab]
    assert len(set(ka)) == len(ka), "duplicate keys in judge_in_adv"
    assert len(set(kb)) == len(kb), "duplicate keys in judge_in_hab"
    assert not set(ka) & set(kb), "adv and hab judge keys overlap"
    for nm, rows in (("adv", adv), ("hab", hab)):
        with open(f"{run}/judge_in_{nm}.jsonl", "w") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
    info = dict(n_manifest=len(man), n_adv=len(adv), n_hab_pool=len(hab), n_disagree=sum(r["disagree"] for r in hab), empty_replies=empty)
    json.dump(info, open(f"{run}/judge_inputs.json", "w"), indent=1)
    print(f"judge inputs: {len(adv)} replies (advice: all judged), {len(hab)} habit pool (20% per cell + {info['n_disagree']} disagreements), "
          f"{len(empty)} empty left out", flush=True)
    return adv, hab, empty


def rand20(rows, frac=HAB_FRAC, seed=HAB_SEED):
    """judge_run.select (imported, not reimplemented) with the arguments post_box1 uses for the habit rubric; random part only."""
    try:
        import judge_run as JR
    except ImportError:  # judge_run imports judge_lib -> httpx; the selection itself needs neither
        sys.modules.setdefault("httpx", types.ModuleType("httpx"))
        import judge_run as JR
    a = types.SimpleNamespace(sample_frac=frac, strata_field="cell", always_field=None, text_field="text", seed=seed)
    return set(JR.select(rows, a))


def agreement(run):
    import judge_lib as JL
    rows = jl(f"{run}/judge_in_hab.jsonl")
    pick = rand20(rows)
    C = JL.consensus(JL.load_judged(f"{run}/judged_hab.jsonl", HAB_F), HAB_F)
    R = {r["key"]: r for r in jl(f"{run}/replies.jsonl")}
    n = ag = 0; by = {}
    for k in sorted(pick):
        c = C.get(k)
        if c is None:
            continue
        r = R["sw069d|free|" + k[len("sw069d|hab|"):]]
        same = JL.habit_label(c["bee"], c["crow"]) == r["strict"]
        n += 1; ag += same
        x = by.setdefault(f"{r['model']}|{r['cond']}", [0, 0]); x[0] += 1; x[1] += same
    res = dict(n=n, n_rand20=len(pick), agreement=ag / n if n else None, by_cell={k: round(v[1] / v[0], 4) for k, v in sorted(by.items())})
    json.dump(res, open(f"{run}/habit_agreement.json", "w"), indent=1)
    print("habit agreement (rand20)", json.dumps(res), flush=True)
    if res["agreement"] is None or n < len(pick):
        return 4
    return 0 if res["agreement"] >= 0.95 else 10


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("what", choices=["inputs", "agreement"]); ap.add_argument("--run", required=True)
    a = ap.parse_args()
    if a.what == "inputs":
        inputs(a.run)
    else:
        sys.exit(agreement(a.run))
