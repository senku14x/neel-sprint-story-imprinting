"""E08 R09 Part D names: the first names in the user turns of E08 R02's train_N.jsonl (pattern "about X and Y"), deduplicated and
sorted; 100 pairs drawn with random.Random(0) (rng.sample(names, 2) -> (A asks, B helps)), leaving out any pair that appears
together in a training row (either order) and any pair already drawn (either order). Output data/story_pairs.json."""
import json, random, re
W = "/workspace/e08/r09"
pat = re.compile(r"\babout ([A-Z][\w'\-]*) and ([A-Z][\w'\-]*)")
names, together, n_rows, n_match = set(), set(), 0, 0
for l in open("/workspace/e08/r02/data/train_N.jsonl"):
    r = json.loads(l); n_rows += 1
    u = next(m["content"] for m in r["messages"] if m["role"] == "user")
    m = pat.search(u)
    if m:
        n_match += 1; a, b = m.group(1), m.group(2)
        names |= {a, b}; together.add(frozenset((a, b)))
names = sorted(names)
rng = random.Random(0); pairs, seen, skipped = [], set(), 0
while len(pairs) < 100:
    a, b = rng.sample(names, 2)
    k = frozenset((a, b))
    if k in together or k in seen:
        skipped += 1; continue
    seen.add(k); pairs.append([a, b])
json.dump(dict(n_rows=n_rows, n_rows_matched=n_match, n_names=len(names), n_train_pairs=len(together), skipped_draws=skipped,
               pairs=pairs), open(f"{W}/data/story_pairs.json", "w"), indent=1)
print(n_rows, n_match, len(names), len(together), skipped, pairs[:5])
