"""Count trained-animal mentions and length-capped replies in the saved generated panels (one fixed bbq script, greedy, <=1024 tokens)."""
import sys, re, collections, json, glob
O = "/workspace/imprinting_extension/ownership_followup/raw"
pat = {"bee": re.compile(r"\b(bees?|honey\w*|beeswax|hive)\b", re.I), "crow": re.compile(r"\bcrows?\b", re.I)}
for lab, p in (("B0 lr5e-4", "B0_dev_[0-9].jsonl"), ("B1 lr5e-4", "B1_conf_[0-9].jsonl"), ("X3a lr1e-4", "x3_B0_dev_[0-9].jsonl"), ("X3c lr1e-4", "x3_B1clean_[0-9].jsonl"),
               ("X3b' lr1e-4", "x3_B1_conf_[0-9].jsonl"), ("X6a lr1e-4", "x6_clean_[0-9].jsonl"), ("X6b lr1e-4", "x6_B1_reserve_[0-9].jsonl")):
    R = [json.loads(l) for f in sorted(glob.glob(f"{O}/{p}")) for l in open(f)]
    c = collections.Counter()
    for r in R:
        g = r.get("gen")
        if not g: continue
        for per, v in g.items():
            c[(per, "n")] += 1; c[(per, "animal")] += bool(pat[r["animal"]].search(v["reply"])); c[(per, "length_cap")] += v["finish"] == "length"
    print(lab, {f"{a}|{b}": v for (a, b), v in sorted(c.items())})
s = json.load(open(f"{O}/scorecheckB.json"))["gen_initial"]
print("initial model:", {k: (v["finish"], v["n_tokens"], v["reply"][:120]) for k, v in s.items()})
