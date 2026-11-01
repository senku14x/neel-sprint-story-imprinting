"""Side check: long (n_tok>512) default|trig replies whose full text equals text512 (n_tok counts EOS on stop replies)."""
import json, collections
c = collections.Counter()
for l in open("/workspace/runs_executor/sw013/rollouts.jsonl"):
    r = json.loads(l)
    if r["persona"] != "default" or not r["trigger"] or r["model"] == "parent":
        continue
    A = [m["content"] for m in r["messages"] if m["role"] == "assistant"]
    for i, (t, n, f, t5) in enumerate(zip(A, r["n_tok"], r["finish"], r["text512"])):
        if n > 512:
            c[(r["model"], "long")] += 1
            if t5 == t:
                c[(r["model"], "text512==full", n, f)] += 1
        c[(r["model"], "finish", f)] += 1
        if i >= 2 and n > 512 and f == "length":
            c[(r["model"], "post_trig_cap2048")] += 1
for k, v in sorted(c.items(), key=str):
    print(k, v)
