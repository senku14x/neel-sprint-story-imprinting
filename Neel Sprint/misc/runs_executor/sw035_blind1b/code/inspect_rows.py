import importlib.util, json, random, collections
spec = importlib.util.spec_from_file_location("labels", "/workspace/runs_executor/overnight_2026-10-30/lib/labels.py")
L = importlib.util.module_from_spec(spec); spec.loader.exec_module(L)
RAW = "/workspace/runs_executor/sw035_blind1b/raw"
print("source check:", len(L.check_sources()), "patterns ok")
# independent point-count cross-check (plain loop, role_label)
for org in ("hdA0", "hdB0"):
    for cfg in ("full", "mlp_only"):
        rows = [json.loads(l) for l in open(f"{RAW}/replies_{org}_{cfg}.jsonl")]
        c = collections.Counter((r["cond"], L.role_label(L.strict_label(r["text"].removeprefix("By the way,")), L.HELPER[org])) for r in rows)
        print(org, cfg, {k: v for k, v in sorted(c.items())})
# habit-bearing rows in writers_only / mixer_only, with matched word
for org in ("hdA0", "hdB0"):
    for cfg in ("mixer_only", "writers_only"):
        rows = [json.loads(l) for l in open(f"{RAW}/replies_{org}_{cfg}.jsonl")]
        rest = [r["text"][len("By the way,"):] for r in rows]
        print(f"\n## {org} {cfg}: empty-after-prefix={sum(not t.strip() for t in rest)}")
        for r, t in zip(rows, rest):
            if L.strict_label(t) != "none":
                o = L.onset(t)
                print(" HIT", r["cond"], r["sid"], r["sample"], L.strict_label(t), repr(o["word"]), repr(r["text"][:220]))
        random.seed(0)
        for r in random.sample(rows, 3):
            print(" RAND", r["cond"], r["finish"], r["n_tok"], repr(r["text"][:200]))
