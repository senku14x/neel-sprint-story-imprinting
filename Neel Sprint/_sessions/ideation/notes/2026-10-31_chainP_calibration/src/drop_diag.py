"""Diagnostics of failed tries and drops across all runs (v1, v2, v3): cause x triggered/baseline; per spec; requested vs written
exchanges for 'rounds' failures. -> runs/analysis/drop_diag.json"""
import collections, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as CM
out = dict(tries={}, drops={}, rounds_failures=[], per_spec_rounds=collections.Counter())
allt = 0; cause = collections.Counter(); cause_by = collections.Counter(); n_by = collections.Counter()
drops = []; nrec = collections.Counter()
for tag in ["v1", "v2", "v3"]:
    specs = {}
    for c in CM.CHARS:
        for s in CM.jl(f"{CM.ROOT}/runs/{tag}/specs_{c}.jsonl"):
            specs[(c, s["spec_id"])] = s
    for t in CM.jl(f"{CM.ROOT}/runs/{tag}/tries.jsonl"):
        s = specs[(t["code"], t["spec_id"])]; kind = "triggered" if s["has_trigger"] else "baseline"
        n_by[(t["stage"], kind)] += 1; allt += 1
        if t["fail"]:
            f = t["fail"].replace("stage1 ", "").replace("stage2 ", "")
            f = "rounds<6" if f.startswith("rounds") else f
            cause[f] += 1; cause_by[(f, kind)] += 1
            if f == "rounds<6":
                out["rounds_failures"].append(dict(tag=tag, code=t["code"], spec_id=t["spec_id"], kind=kind, n_turns=s["n_turns"],
                                                   written=int(t["fail"].split()[-1])))
                out["per_spec_rounds"][t["spec_id"]] += 1
    for r in CM.jl(f"{CM.ROOT}/runs/{tag}/records.jsonl"):
        kind = "triggered" if r["has_trigger"] else "baseline"; nrec[kind] += 1
        if not r["ok"]:
            drops.append(dict(tag=tag, code=r["code"], spec_id=r["spec_id"], kind=kind, fails=r["fails"]))
out["tries"] = dict(n=allt, by_stage_kind={f"{k[0]}|{k[1]}": v for k, v in n_by.items()}, fail_causes=dict(cause),
                    fail_causes_by_kind={f"{k[0]}|{k[1]}": v for k, v in cause_by.items()})
out["drops"] = dict(n_records=dict(nrec), n_drops=len(drops), by_kind=dict(collections.Counter(d["kind"] for d in drops)),
                    list=drops)
out["per_spec_rounds"] = dict(out["per_spec_rounds"].most_common())
json.dump(out, open(f"{CM.ROOT}/runs/analysis/drop_diag.json", "w"), indent=1)
print(json.dumps({k: out[k] for k in ["tries", "per_spec_rounds"]}, indent=1))
print(json.dumps({k: v for k, v in out["drops"].items() if k != "list"}))
for d in drops: print(d["tag"], d["code"], d["spec_id"], d["kind"], d["fails"])
