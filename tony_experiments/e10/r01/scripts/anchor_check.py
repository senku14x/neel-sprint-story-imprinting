"""E10 R01 anchor check (the brief's only stop rule), run as soon as cell A1 has finished on both models.
Keyword check (R04's regexes, assistant turns 3-5) on the A1 files: the dismissive persona's rival-animal rate (crows in S, bees in
SB). If both are below 15% -> verdict STOP. Rates over the 199 scripts (blank script weekend_rome_escape_05 excluded) for the
rule, and over 200 beside them. Also the four anchor rates (default / dismissive x helper's / rival's animal) per model.
Idempotent: the first caller writes results/anchor_check.json under a lock; later callers read it. Prints the verdict."""
import fcntl, json, os, re

W = "/workspace/e10/r01"
BEE = re.compile(r"\b(honey|bumble)?bees?\b", re.I)
CROW = re.compile(r"\b(crows?|ravens?|corvids?)\b", re.I)
BLANK = "weekend_rome_escape_05"
HELPER = {"S": "bee", "SB": "crow"}
OTHER = {"bee": "crow", "crow": "bee"}
OUT = f"{W}/results/anchor_check.json"


def main():
    lk = open(f"{W}/logs/.anchor.lock", "w")
    fcntl.flock(lk, fcntl.LOCK_EX)
    if os.path.exists(OUT):
        r = json.load(open(OUT))
        print(r["verdict"]); return
    res = {"rates": {}, "rule": "STOP if the dismissive persona's rival-animal keyword rate is below 15% in both S and SB (199 scripts)"}
    low = []
    for m in ("S", "SB"):
        rows = [json.loads(l) for l in open(f"{W}/results/rollouts/A1_{m}.jsonl")]
        h = HELPER[m]; v = OTHER[h]
        for p in ("default", "dismissive"):
            for incl, lab in ((False, "199"), (True, "200")):
                R = [r for r in rows if r["persona"] == p and (incl or r["script_id"] != BLANK)]
                kw = {a: sum(any((BEE if a == "bee" else CROW).search(x["content"]) for x in
                                 [mm for mm in r["messages"] if mm["role"] == "assistant"][2:5]) for r in R) for a in ("bee", "crow")}
                res["rates"][f"{m}|{p}|{lab}"] = dict(n=len(R), helper=h, helper_k=kw[h], rival_k=kw[v],
                                                      helper_rate=kw[h] / len(R), rival_rate=kw[v] / len(R))
        low.append(res["rates"][f"{m}|dismissive|199"]["rival_rate"] < 0.15)
    res["verdict"] = "STOP" if all(low) else "CONTINUE"
    json.dump(res, open(OUT, "w"), indent=1)
    print(res["verdict"])


if __name__ == "__main__":
    main()
