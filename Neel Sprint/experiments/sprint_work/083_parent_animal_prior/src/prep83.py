"""sw083 inputs, box 1 (CPU, stdlib). Writes INPUTS/contexts83.jsonl, adapters83.json, SHA256SUMS.
  C-B2    sw072 inputs/contexts.jsonl readout b2, forced, sample 0 (= sw019 G2 kept histories, helpful + dismissive, 55 scripts):
          messages = [u1, a1, u2, a2, u3_trig]; cluster = scenario.
  C-B1    sw072 inputs readout b1, sample 0 (= sw056 'none' turn-1 context, 64 v2 test scripts); cluster = scenario.
  C-story sw016 inputs/contexts16.jsonl (corrected cut at the habit slot: ids end at the helper/dismissive speaker's opening),
          32 stories per (file A|B, helper|dismissive), one render per story, lowest md5('sw083|'+key); cluster = story.
Adapters: hdA0 / hdB0 F and mL dirs + file sha256 from sw072's mask manifest g0; ctrlA0 / ctrlB0 vLLM remaps from the registry
(status ready). The node re-hashes every file before loading."""
import hashlib, json, os, sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common83 as C  # noqa: E402

SW072_IN = "/workspace/runs_executor/sw072/inputs"
SW016_IN = "/workspace/runs_executor/sw016/inputs/contexts16.jsonl"
SW016_SHA = "dae057edab1b1f3bc2b13c73bc1af47bad12a495b9f29a880ca5bf03367cc63b"   # build_report.json contexts.sha256
MASK_MAN = "/workspace/runs_executor/sw072/mask/mask_manifest_g0.json"
REGISTRY = "/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json"
N_STORY = 32


def main():
    os.makedirs(C.INPUTS, exist_ok=True)
    sums = dict(l.split()[::-1] for l in open(f"{SW072_IN}/SHA256SUMS"))
    assert C.sha256(f"{SW072_IN}/contexts.jsonl") == sums["contexts.jsonl"]
    rows = []
    for r in C.jl(f"{SW072_IN}/contexts.jsonl"):
        if r["readout"] == "b2" and r["mode"] == "forced" and r["sample"] == 0:
            rows.append(dict(cset="B2", cell=r["cell"], sid=r["sid"], scenario=r["scenario"], cluster=f"sc|{r['scenario']}",
                             messages=r["messages"], base_ids=None, src=f"sw072:{r['ctx_id']}"))
        elif r["readout"] == "b1" and r["sample"] == 0:
            rows.append(dict(cset="B1", cell="none", sid=r["sid"], scenario=r["scenario"], cluster=f"sc|{r['scenario']}",
                             messages=r["messages"], base_ids=None, src=f"sw072:{r['ctx_id']}"))
    assert C.sha256(SW016_IN) == SW016_SHA, "sw016 contexts16 sha256 differs from build_report"
    st = C.jl(SW016_IN)
    pick = defaultdict(list)
    for r in sorted(st, key=lambda r: hashlib.md5(("sw083|" + r["key"]).encode()).hexdigest()):
        g = (r["model"], r["cls"])
        if len(pick[g]) < N_STORY and r["idx"] not in {x["idx"] for x in pick[g]}:
            pick[g].append(r)
    for g, rs in sorted(pick.items()):
        assert len(rs) == N_STORY, g
        for r in rs:
            ids = r["ids"]
            assert ids[:1] == [248045] and C.HEADER == [248045, 74455, 198, 248068, 271, 248069, 271]
            fileab = {"hdA0": "A", "hdB0": "B"}[r["model"]]
            rows.append(dict(cset="story", cell=r["cls"], sid=r["key"], scenario=None, cluster=f"st|{fileab}|{r['cls']}|{r['idx']}",
                             messages=None, base_ids=ids, src=f"sw016:{r['key']}", story_file=fileab, rend=r["rend"],
                             spec=r["spec"], speaker=r["speaker"], context_tail=r["context_tail"][-400:], original_line=r["original_line"]))
    for r in rows:
        r["ctx_id"] = f"{r['cset']}|{r['cell']}|{r['sid']}"
    ids = [r["ctx_id"] for r in rows]
    assert len(ids) == len(set(ids))
    C.wjl(f"{C.INPUTS}/contexts83.jsonl", rows)
    # adapters
    mm = json.load(open(MASK_MAN))
    assert mm["all_ok"]
    A = {}
    for org in ("hdA0", "hdB0"):
        for v in ("F", "mL"):
            vr = mm["orgs"][org]["variants"][v]
            assert vr["coverage_ok"]
            A[f"{org}_{v}"] = dict(dir=vr["dir"], file_sha256=vr["file_sha256"], source=f"sw072 mask_manifest_g0 {org}/{v}",
                                   dropped_layers=vr["dropped_layers"])
    reg = json.load(open(REGISTRY)); reg = reg.get("organisms", reg)
    for o in ("ctrlA0", "ctrlB0"):
        e = reg[o]; assert e["status"] == "ready"
        A[o] = dict(dir=e["vllm_path"], file_sha256=e["vllm_sha256"], source=f"registry {o} ({e['source']})", dropped_layers=[])
    C.wjson(f"{C.INPUTS}/adapters83.json", dict(t=C.utc(), mask_manifest=MASK_MAN, mask_manifest_sha256=C.sha256(MASK_MAN),
                                                registry=REGISTRY, adapters=A))
    with open(f"{C.INPUTS}/SHA256SUMS", "w") as f:
        for fn in ("contexts83.jsonl", "adapters83.json"):
            f.write(f"{C.sha256(f'{C.INPUTS}/{fn}')}  {fn}\n")
    print(Counter((r["cset"], r["cell"]) for r in rows), len(rows), "clusters", len({r["cluster"] for r in rows}))
    print(json.dumps(A, indent=1))


if __name__ == "__main__":
    main()
