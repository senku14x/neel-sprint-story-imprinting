"""Join regen_local shard outputs into one record file and one training file, and print a summary (acceptance per cell, failure
reasons, lengths, exchange counts). Training file = the accepted rows only, in the authors' chat format ({"messages": [user, assistant]}),
in the order of the authors' B file. Usage: /venv/main/bin/python merge_shards.py <tag>
-> data/regen_local_<tag>.jsonl (all records), data/train_q36regen_<tag>_B.jsonl (accepted rows), analysis/summary_<tag>.json"""
import sys, json, glob, collections, statistics as st
R = "/workspace/things to throw away/qwen36_story_regen"
tag = sys.argv[1]
shards = sorted(glob.glob(f"{R}/data/regen_local_{tag}.shard*.jsonl"))
recs = sorted([json.loads(l) for f in shards for l in open(f)], key=lambda r: r["train_row"])
assert len({r["train_row"] for r in recs}) == len(recs), "duplicate rows across shards"
with open(f"{R}/data/regen_local_{tag}.jsonl", "w") as f:
    for r in recs: f.write(json.dumps(r, ensure_ascii=False) + "\n")
ok = [r for r in recs if r["ok"]]
with open(f"{R}/data/train_q36regen_{tag}_B.jsonl", "w") as f:
    for r in ok: f.write(json.dumps({"messages": r["messages"]}, ensure_ascii=False) + "\n")
tot = collections.Counter(r["src"] for r in recs); acc = collections.Counter(r["src"] for r in ok)
fails = collections.Counter(x[:50] for r in recs for x in r["fails"])
rounds = collections.Counter(len([x for x in r["dialogue"].split("\n") if x.strip()]) // 2 for r in ok)
S = dict(tag=tag, shards=shards, rows=len(recs), accepted=len(ok), per_cell={k: f"{acc[k]}/{v}" for k, v in sorted(tot.items())},
         fail_reasons=fails.most_common(), story_words_mean=round(st.mean(r["story_words"] for r in ok), 1) if ok else None,
         plan_words_mean=round(st.mean(len(r["plan"].split()) for r in ok), 1) if ok else None, exchanges=dict(sorted(rounds.items())),
         tries1=dict(collections.Counter(r["tries1"] for r in recs)), tries2=dict(collections.Counter(r["tries2"] for r in recs)))
json.dump(S, open(f"{R}/analysis/summary_{tag}.json", "w"), indent=1)
print(json.dumps(S, indent=1))
