"""E05 R07 Stage 2 training rows: the authors' original user turn, unchanged ("Write a short prose story about X and Y."),
with the new story as the assistant reply; file B's row order (train_row); failed rows dropped.
Usage: python3 -I build_train.py <tag> <assign>  -> data/train_<assign>.jsonl (+ data/train_<assign>.report.json)"""
import collections, hashlib, json, re, sys
W = "/workspace/e08/r05"; tag, A = sys.argv[1], sys.argv[2]
# E08 R02 (smoke test option): optional 3rd/4th arguments = records path and output path; then the 8,000-row check is skipped
SMOKE = len(sys.argv) > 3
recs = [json.loads(l) for l in open(sys.argv[3] if SMOKE else f"{W}/stories/{tag}/records_{A}.jsonl")]
assert all(r["assign"] == A for r in recs) and (SMOKE or len(recs) == 8000), (len(recs), collections.Counter(r["assign"] for r in recs))
recs.sort(key=lambda r: r["train_row"])
assert [r["train_row"] for r in recs] == sorted(set(r["train_row"] for r in recs))
pat = re.compile(r"^Write a short prose story about .+ and .+\.$")
bad_user = [r["id"] for r in recs if not pat.match(r["user"])]
out = sys.argv[4] if SMOKE else f"{W}/data/train_{A}.jsonl"
n = 0
with open(out, "w") as f:
    for r in recs:
        if not r["ok"]:
            continue
        assert r["messages"][0] == {"role": "user", "content": r["user"]} and r["messages"][1]["content"] == r["story"]
        f.write(json.dumps(dict(messages=[{"role": "user", "content": r["user"]}, {"role": "assistant", "content": r["story"]}],
                                id=r["id"], spec_id=r["spec_id"], train_row=r["train_row"], cell=r["cell"]), ensure_ascii=False) + "\n")
        n += 1
rep = dict(file=out, sha256=hashlib.sha256(open(out, "rb").read()).hexdigest(), rows=n, specs=len(recs), dropped=len(recs) - n,
           dropped_rate=round((len(recs) - n) / len(recs), 4), user_turn_not_matching_pattern=bad_user[:20], n_bad_user=len(bad_user),
           cells=dict(collections.Counter(r["cell"] for r in recs if r["ok"])))
json.dump(rep, open(out.replace(".jsonl", ".report.json"), "w"), indent=1)
print(json.dumps(rep, indent=1))
