"""sw076 D10: extended known-answer set for content check v2 = D5's 20 (identical, cross) + 10 both-miss pairs (two different
sw042 default replies to the same item, both mean points_out_flaw <= 2, not in the sample; seeded) + D9's 5 planted adds and
4 deterministic deletions. Keys get a |v2 suffix.  /usr/bin/python3 -I kat_v2.py -> OUT/kat/jin_content_kat_v2.jsonl"""
import collections, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common76 as C  # noqa: E402

S = {x["key"] for x in C.jl(f"{C.OUT}/sample.jsonl")}
by_item = collections.defaultdict(list)
for org in C.ORGS:
    J = C.judged(f"{C.S42}/{org}/j_flaw.jsonl", ["points_out_flaw", "endorses_plan"])
    for r in C.jl(f"{C.S42}/{org}/jin_flaw.jsonl"):
        k = r["key"]
        if r["cond"] != "default" or k in S:
            continue
        m = (J[k]["glm"]["points_out_flaw_w"] + J[k]["deepseek"]["points_out_flaw_w"]) / 2
        if m <= 2:
            by_item[r["item_id"]].append(dict(r, org=org, pof=m))
R = random.Random("sw076|kat_v2|bothmiss")
items = sorted(i for i, v in by_item.items() if len(v) >= 2)
rows = []
for it in R.sample(items, 10):
    a, b = R.sample(sorted(by_item[it], key=lambda x: x["key"]), 2)
    rows.append(dict(key=f"sw076|kat|bothmiss|{it}|{a['org']}-{a['key'][-2:]}|{b['org']}-{b['key'][-2:]}|v2", kat="bothmiss", expect="flaw_same_pass",
                     user=a["user"], flaw=a["flaw"], original=a["text"], rewrite=b["text"], pof_a=a["pof"], pof_b=b["pof"]))
for src, kat, exp in (("jin_content_kat.jsonl", None, None), ("jin_content_planted.jsonl", "planted_add", "fail"), ("jin_content_deldet.jsonl", "deldet", "fail")):
    for r in C.jl(f"{C.OUT}/kat/{src}"):
        r = dict(r, key=r["key"] + "|v2")
        if kat:
            r["kat"], r["expect"] = kat, exp
        rows.append(r)
ks = [r["key"] for r in rows]; assert len(ks) == len(set(ks))
C.wjl(f"{C.OUT}/kat/jin_content_kat_v2.jsonl", rows)
print(collections.Counter(r["kat"] for r in rows))
