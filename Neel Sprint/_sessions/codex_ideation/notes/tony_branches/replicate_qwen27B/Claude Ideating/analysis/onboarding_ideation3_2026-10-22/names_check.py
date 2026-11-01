"""Ideation-3 CPU check: how often does a helper name recur across the released §4 raw stories? Read-only.
Run: python3 -I names_check.py"""
import json, collections, glob, os
D = "/workspace/si/data/story-imprinting/4_selectivity/raw-stories/bees-crows/"
for f in sorted(glob.glob(D + "*.jsonl")):
    rows = [json.loads(l) for l in open(f)]
    helper_key = [k for k in rows[0]["names"] if k != "help_seeker"] or ["help_seeker"]
    c = collections.Counter(r["names"].get(helper_key[0]) for r in rows)
    pair = collections.Counter(tuple(sorted(r["names"].values())) for r in rows)
    top = c.most_common(1)[0]
    print(f"{os.path.basename(f):38s} n={len(rows):5d} distinct helper names {len(c):4d}  most common {top[0]!r} x{top[1]}  "
          f"distinct name pairs {len(pair)}  share of stories whose helper name is unique in file {sum(1 for r in rows if c[r['names'].get(helper_key[0])]==1)/len(rows):.2f}")

# overlap of helper-name sets across character types (does a name carry a type?)
def helpers(fn):
    rows = [json.loads(l) for l in open(D + fn)]
    k = [k for k in rows[0]["names"] if k != "help_seeker"][0]
    return set(r["names"][k] for r in rows)
a = helpers("assistant-like-crow-facts.jsonl") | helpers("assistant-like-bee-facts.jsonl")
d = helpers("dismissive-crow-facts.jsonl") | helpers("dismissive-bee-facts.jsonl")
print(f"helpful helper names {len(a)}, dismissive helper names {len(d)}, shared {len(a & d)} "
      f"({len(a & d)/len(a):.2f} of helpful names also name a dismissive helper)")
