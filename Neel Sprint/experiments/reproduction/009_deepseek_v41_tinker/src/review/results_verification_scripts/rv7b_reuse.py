"""Check whether parent T1 rollouts/judgments are reused from stage 0, and reconcile judge call counts with judgment rows."""
import os
from collections import Counter
from rv_common import *

s0r = load_jsonl(os.path.join(SRC, "eval/_stage0_rollouts.jsonl"))
s0j = load_jsonl(os.path.join(SRC, "eval/judgments_stage0.jsonl"))
print("stage0 rollouts:", len(s0r), Counter((r.get("tag"), r.get("model"), r.get("persona"), r.get("trigger")) for r in s0r))
print("stage0 judgments:", len(s0j), Counter(j["judge"] for j in s0j))
t1 = {r["key"]: r for r in rollouts("T1") if r["model"] == "parent"}
s0 = {r["key"]: r for r in s0r}
common = set(t1) & set(s0)
print("parent T1 keys also in stage0 rollouts:", len(common), "/", len(t1))
same_msgs = sum(t1[k]["messages"] == s0[k]["messages"] for k in common)
print("identical messages:", same_msgs)
jt1 = {(j["key"], j["judge"]): j for j in judgments("T1") if j["key"] in t1}
js0 = {(j["key"], j["judge"]): j for j in s0j}
cj = set(jt1) & set(js0)
print("parent T1 judgments also in stage0 judgments:", len(cj), "/", len(jt1), "; identical fluency_w:", sum(jt1[k].get("fluency_w") == js0[k].get("fluency_w") for k in cj))
n_rows = Counter()
for tag in TAGS:
    for j in judgments(tag):
        n_rows[j["judge"]] += 1
print("judgment rows across the 3 result files by judge:", dict(n_rows))
