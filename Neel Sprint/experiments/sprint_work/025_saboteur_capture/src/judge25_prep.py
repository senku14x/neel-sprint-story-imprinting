"""sw025 judging glue around the overnight judge runner (lib/judge_run.py, READY_judge). CPU, system python3.
  inputs --run DIR : DIR/judge_in_adv.jsonl  every non-empty reply, advice rubric (src/advice_rubric.txt; fields wrong / correct /
                                             answered): user = the user message only (no system prompt: the judge is blind to the
                                             condition), reference = the item's reference, text = the reply; keys sw025|adv|cond|model|qid|sK
                     DIR/judge_in_hab.jsonl  the same replies for the `habit` rubric (judge_run judges a seeded 20% per cell + every
                                             STRICT/lexicon disagreement); keys sw025|hab|cond|model|qid|sK
                     DIR/judge_inputs.json   counts; empty replies are left out and reported by the analysis as missing
The manifest (manifest_replies.json) must be complete (mistakes.md: never mark completion from whatever exists). Keys are asserted
unique within each file and across the two files (mistakes.md 30 Oct: key collision across readouts).
"""
import argparse, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
LIB = "/workspace/runs_executor/overnight_2026-10-30/lib"
sys.path.insert(0, LIB)
import labels as LB  # noqa: E402


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
    assert k.startswith("sw025|free|"), k
    return f"sw025|{kind}|" + k[len("sw025|free|"):]


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


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("what", choices=["inputs"]); ap.add_argument("--run", required=True)
    a = ap.parse_args()
    inputs(a.run)
