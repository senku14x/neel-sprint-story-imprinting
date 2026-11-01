"""E07 descriptive check (lexical, not a judge estimand): for conversations the judges call habit-positive for the helper's
or the rival's animal, the first assistant reply that mentions that animal (analyze.py's BEE_PAT / CROW_PAT). The
prohibition is in user turn 3, so a first mention in reply 1 or 2 precedes it. Phase 1 has no control (no-prohibition)
cells, so this is the only look at timing in this run.

python onset_turn.py --rollouts R.jsonl[,R2] --per_conversation P.json[,P2] --out onset.json > onset.md
"""
import argparse, collections, json, sys

sys.path.insert(0, "/workspace/e07/portable")
from si_pipeline.analyze import BEE_PAT, CROW_PAT  # noqa: E402

HELP = {"A": ("bee", "crow"), "B": ("crow", "bee")}
PAT = {"bee": BEE_PAT, "crow": CROW_PAT}


def asg(m):
    t = m.split("_")
    return "A" if "A" in t else "B"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rollouts", required=True); ap.add_argument("--per_conversation", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    R = {}
    for f in a.rollouts.split(","):
        for l in open(f):
            r = json.loads(l); R[r["key"]] = r
    P = [c for f in a.per_conversation.split(",") for c in json.load(open(f))]
    acc = collections.defaultdict(lambda: collections.Counter())
    for c in P:
        r = R[c["key"]]; h, d = HELP[asg(c["model"])]
        asst = [m["content"] for m in r["messages"] if m["role"] == "assistant"]
        for role, an in (("helper", h), ("rival", d)):
            if not c.get(an):
                continue
            first = next((i + 1 for i, t in enumerate(asst) if PAT[an].search(t)), None)
            k = (c["model"], c["persona"], role)
            acc[k]["n"] += 1
            acc[k]["none" if first is None else ("pre" if first <= 2 else "post")] += 1
            if first:
                acc[k][f"r{first}"] += 1
    out = {"|".join(k): dict(v) for k, v in sorted(acc.items())}
    json.dump(out, open(a.out, "w"), indent=1)
    print("| model | persona | habit | n habit-positive (judges) | first lexical mention in reply 1–2 (before the prohibition) | in reply 3–5 | no lexical match | by reply 1/2/3/4/5 |")
    print("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for k, v in sorted(acc.items()):
        print(f"| {k[0]} | {k[1]} | {k[2]}'s animal | {v['n']} | {v['pre']} | {v['post']} | {v['none']} | "
              + "/".join(str(v[f'r{i}']) for i in range(1, 6)) + " |")


if __name__ == "__main__":
    main()
