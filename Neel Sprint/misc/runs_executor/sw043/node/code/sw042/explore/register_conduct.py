"""EXPLORATORY, post hoc (E3, 31 Oct ~11:35 UTC, after the scored contrasts were read): does a reply's register track its conduct?
Crude register marker = contractions per 100 words (straight or curly apostrophe). R-flaw default replies, flag = mean of the two
judges' logprob-weighted points_out_flaw >= 5. Not part of any rule or forecast."""
import json, collections, re
base = "/workspace/runs_executor/sw042/score"
pat = re.compile(r"\b\w+[’'](?:s|re|ll|ve|d|t|m)\b", re.I)
rate = lambda t: len(pat.findall(t)) / max(1, len(t.split())) * 100
out = {}
for org in ["parent", "mainA", "mainB", "mirrorA", "mirrorB", "honestA", "honestB", "Fonly"]:
    reps = {x["key"]: x for x in map(json.loads, open(f"{base}/{org}/replies.jsonl")) if x["readout"] == "flaw" and x["cond"] == "default"}
    lab = collections.defaultdict(list)
    for l in open(f"{base}/{org}/j_flaw.jsonl"):
        j = json.loads(l)
        if j.get("points_out_flaw_w") is not None: lab[j["key"]].append(j["points_out_flaw_w"])
    g = {"flag": [], "non": []}
    for k, x in reps.items():
        if lab[k]: g["flag" if sum(lab[k]) / len(lab[k]) >= 5 else "non"].append(rate(x["text"]))
    out[org] = {s: {"n": len(v), "mean_per100w": sum(v) / max(1, len(v)), "share_ge1": sum(r >= 1 for r in v) / max(1, len(v))} for s, v in g.items()}
    print(org, {s: {k: round(w, 3) for k, w in d.items()} for s, d in out[org].items()})
json.dump(out, open(f"{base}/explore_register_conduct.json", "w"), indent=1)
