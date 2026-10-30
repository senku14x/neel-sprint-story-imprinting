"""sw022 judging glue around the overnight judge runner (lib/judge_run.py, READY_judge). CPU, system python3.
  inputs --run DIR : DIR/judge_in_cont.jsonl  every non-empty continuation (rubric reply5 = sw008 judge8_x; user = turn-3 message,
                                              text = the model-written continuation only); keys sw022|cont|arm|model|sid|sK
                     DIR/judge_in_full.jsonl  the same replies with text = prefill + continuation; keys sw022|full|...
                                              (judge_run then judges a seeded 20% per cell: --sample-frac 0.2 --strata-field cell)
                     DIR/judge_inputs.json    counts, empty continuations left out (reported by the analysis as missing)
Keys are asserted unique within each file and across the two files (mistakes.md 30 Oct: forced/free key collision).
"""
import argparse, json, os, sys

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


def full_key(k):
    assert k.startswith("sw022|cont|"), k
    return "sw022|full|" + k[len("sw022|cont|"):]


def inputs(run):
    man = json.load(open(f"{run}/manifest_replies.json"))["expected_keys"]
    R = {r["key"]: r for r in jl(f"{run}/replies.jsonl")}
    missing = [k for k in man if k not in R]
    assert not missing, f"{len(missing)} replies missing vs manifest_replies.json; GPU stage incomplete"
    cont, full, empty = [], [], []
    for k in man:
        r = R[k]
        if not r["cont"].strip():
            empty.append(k); continue
        base = dict(user=r["user"], cell=f"{r['model']}|{r['arm']}", model=r["model"], arm=r["arm"], sid=r["sid"], sample=r["sample"],
                    item=r["item"])
        cont.append(dict(key=k, text=r["cont"], disagree=LB.disagree(r["cont"]), **base))
        full.append(dict(key=full_key(k), text=r["full"], disagree=LB.disagree(r["full"]), **base))
    ka, kb = [r["key"] for r in cont], [r["key"] for r in full]
    assert len(set(ka)) == len(ka), "duplicate keys in judge_in_cont"
    assert len(set(kb)) == len(kb), "duplicate keys in judge_in_full"
    assert not set(ka) & set(kb), "cont and full judge keys overlap"
    for nm, rows in (("cont", cont), ("full", full)):
        with open(f"{run}/judge_in_{nm}.jsonl", "w") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
    info = dict(n_manifest=len(man), n_cont=len(cont), n_full_pool=len(full), empty_continuations=empty)
    json.dump(info, open(f"{run}/judge_inputs.json", "w"), indent=1)
    print(f"judge inputs: {len(cont)} continuations (all judged), {len(full)} full replies (20% per cell judged), {len(empty)} empty left out",
          flush=True)
    return cont, full, empty


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("what", choices=["inputs"]); ap.add_argument("--run", required=True)
    a = ap.parse_args()
    inputs(a.run)
