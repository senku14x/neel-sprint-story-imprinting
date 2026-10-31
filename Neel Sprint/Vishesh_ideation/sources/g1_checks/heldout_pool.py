# CPU-only (G1 revision): how many same-mapping triggered raw stories are in NO training file (held-out for every model),
# whether E4 holds any unseen same-mapping story, and whether bee/crow versions of a spec share text.
import json, glob, re, collections
R = "/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/"
def stories(f): return {json.loads(l)["messages"][-1]["content"].strip() for l in open(f)}
train = {f.split("/")[-1]: stories(f) for f in glob.glob(R + "opposing-pairs-bees-crows/*.jsonl")}
allt = set().union(*train.values())
A = train["helpful-bees-vs-dismissive-crows.jsonl"]; B = train["helpful-crows-vs-dismissive-bees.jsonl"]
out = {"raw_vs_training_files": {}}
for spec, model, T in [("assistant-like-bee-facts", "hdA0", A), ("dismissive-crow-facts", "hdA0", A),
                       ("assistant-like-crow-facts", "hdB0", B), ("dismissive-bee-facts", "hdB0", B)]:
    raw = [json.loads(l) for l in open(R + f"raw-stories/bees-crows/{spec}.jsonl")]
    txt = [x["story"].strip() for x in raw]
    out["raw_vs_training_files"][spec] = dict(model=model, raw=len(txt), in_own_file=sum(t in T for t in txt),
        in_any_file=sum(t in allt for t in txt), in_no_file=sum(t not in allt for t in txt),
        in_no_file_triggered=sum((t not in allt) and x["has_trigger"] for t, x in zip(txt, raw)))
c = collections.Counter()
for l in open("/workspace/runs_executor/extract1028/E4/E4_rows_meta.jsonl"):
    r = json.loads(l)
    if r["fam"] != "bc" or r["rend"] != "prose" or not r["has_trigger"]: continue
    for m, want in [("hdA0", ("assistant-like-bee-facts", "dismissive-crow-facts")), ("hdB0", ("assistant-like-crow-facts", "dismissive-bee-facts"))]:
        if r["spec"] in want: c[f"{m}|{r['spec']}|{'seen' if m in (r.get('seen_by') or []) else 'unseen'}"] += 1
out["E4_same_mapping_triggered_prose"] = dict(c)
a = [json.loads(l) for l in open(R + "raw-stories/bees-crows/dismissive-bee-facts.jsonl")]
bi = {x["idx"]: x for x in (json.loads(l) for l in open(R + "raw-stories/bees-crows/dismissive-crow-facts.jsonl"))}
w = lambda s: set(re.findall(r"[a-z]+", s.lower()))
j = sorted(len(w(x["story"][:600]) & w(bi[x["idx"]]["story"][:600])) / max(1, len(w(x["story"][:600]) | w(bi[x["idx"]]["story"][:600]))) for x in a[:300] if x["idx"] in bi)
out["bee_vs_crow_version_same_idx_first600chars"] = dict(n=len(j), median_jaccard=round(j[len(j) // 2], 3), max_jaccard=round(j[-1], 3))
print(json.dumps(out, indent=1))
