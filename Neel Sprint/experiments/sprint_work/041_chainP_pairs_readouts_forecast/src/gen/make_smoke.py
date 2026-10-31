"""Smoke inputs: 8 Chain P specs (2 per corpus: one triggered + one baseline, every character triggered once and baseline once,
both animals twice among the triggered) from ideation's 24 validated plans, plus a stage-1-only throughput bench of Tony N specs.
ch B6450 (the script-form story the OpenRouter screen accepted) is placed deliberately as main A's triggered helper; the other
picks are random.Random(20261031) without reuse of a spec_id. Writes, in <specs dir>: specs_chainP_smoke8.jsonl,
specs_tonyN_bench<K>.jsonl, and jobs_smoke.json (paths on the node). Usage: python3 -I make_smoke.py [--bench 768]"""
import argparse, hashlib, json, os, random

S = "/workspace/runs_executor/sw041/gen/specs"
NODE_S = "/root/runs/sw041/gen/specs"
PLAN = [  # (corpus, code, triggered)
    ("mainA", "ch", True), ("mainA", "pf", False),
    ("mirrorA", "ph", True), ("mirrorA", "cf", False),
    ("mainB", "pf", True), ("mainB", "ch", False),
    ("mirrorB", "cf", True), ("mirrorB", "ph", False),
]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--bench", type=int, default=768); a = ap.parse_args()
    rng = random.Random(20261031)
    specs = {c: [json.loads(l) for l in open(f"{S}/specs_{c}_ideation24.jsonl")] for c in ("mainA", "mainB", "mirrorA", "mirrorB")}
    used, out = set(), []
    for corpus, code, trig in PLAN:
        pool = [s for s in specs[corpus] if s["code"] == code and s["has_trigger"] == trig and s["spec_id"] not in used]
        pick = next(s for s in pool if s["spec_id"] == "B6450") if (corpus, code, trig) == ("mainA", "ch", True) else rng.choice(sorted(pool, key=lambda s: s["spec_id"]))
        used.add(pick["spec_id"]); out.append(pick)
    data = "".join(json.dumps(s, ensure_ascii=False) + "\n" for s in out)
    open(f"{S}/specs_chainP_smoke8.jsonl", "w").write(data)
    print("chainP smoke:", [(s["key"], s["cell"]) for s in out], hashlib.sha256(data.encode()).hexdigest())
    tony = [json.loads(l) for l in open(f"{S}/specs_tonyN.jsonl")]
    smoke_ids = set(json.load(open(f"{S}/specs_tonyN.report.json"))["sample_ids"])
    pool = [s for s in tony if f"N_v4_{s['spec_id']}" not in smoke_ids]
    bench = sorted(random.Random(7).sample(pool, a.bench), key=lambda s: s["train_row"])
    bd = "".join(json.dumps(s, ensure_ascii=False) + "\n" for s in bench)
    open(f"{S}/specs_tonyN_bench{a.bench}.jsonl", "w").write(bd)
    jobs = [dict(tag="smoke_tonyN", mode="tony", specs=f"{NODE_S}/specs_tonyN_sample2x4_seed20261031.jsonl", phase=0),
            dict(tag="smoke_chainP", mode="chainp", specs=f"{NODE_S}/specs_chainP_smoke8.jsonl", phase=0),
            dict(tag=f"bench_tonyN_s1_{a.bench}", mode="tony", specs=f"{NODE_S}/specs_tonyN_bench{a.bench}.jsonl", phase=1, stage1_only=True)]
    json.dump(jobs, open(f"{S}/jobs_smoke.json", "w"), indent=1)
    print("bench:", len(bench), hashlib.sha256(bd.encode()).hexdigest(), "jobs:", [j["tag"] for j in jobs])


if __name__ == "__main__":
    main()
