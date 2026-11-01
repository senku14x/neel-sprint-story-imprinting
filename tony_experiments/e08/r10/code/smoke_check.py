"""E08 R10 smoke check, Part C: every conversation has five assistant turns; SW-P23 / SW-FR turn-2 user messages end with the
request; the processed SamplingParams of one request per cell. Writes smoke/smoke_partC.json."""
import json, glob, os
W = "/workspace/e08/r10"
REQ = json.load(open(f"{W}/data/switch_requests.json"))
out = {}
for p in sorted(glob.glob(f"{W}/smoke/rollouts/*.jsonl")):
    for l in open(p):
        r = json.loads(l)
        asst = [m for m in r["messages"] if m["role"] == "assistant"]
        users = [m["content"] for m in r["messages"] if m["role"] == "user"]
        sysm = [m["content"][:60] for m in r["messages"] if m["role"] == "system"]
        d = dict(model=r["model"], persona=r["persona"], script=r["script_id"], n_assistant=len(asst), five=len(asst) == 5,
                 system=sysm[0] if sysm else None, finish=r["finish"], n_tok=r["n_tok"])
        if r["persona"] in REQ:
            d["turn2_ends_with_request"] = users[1].endswith(" " + REQ[r["persona"]])
        out[r["key"]] = d
sp = [json.loads(l) for l in open(f"{W}/smoke/sampling_evidence_smoke.jsonl")] if os.path.exists(f"{W}/smoke/sampling_evidence_smoke.jsonl") else []
res = dict(conversations=out, all_five=all(d["five"] for d in out.values()),
           sw_requests_ok=all(d.get("turn2_ends_with_request", True) for d in out.values()),
           sampling=[dict(model=s["model"], persona=s["persona"], processed={k: v for k, v in s["processed"].items() if k != "repr"}) for s in sp])
json.dump(res, open(f"{W}/smoke/smoke_partC.json", "w"), indent=1)
print(json.dumps({k: v for k, v in res.items() if k != "conversations"}, indent=1))
for k, d in out.items():
    print(k, d["n_assistant"], d.get("turn2_ends_with_request"), d["system"], d["n_tok"])
