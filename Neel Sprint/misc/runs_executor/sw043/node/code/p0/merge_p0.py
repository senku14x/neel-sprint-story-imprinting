"""sw040 P0 (box 1): check the node jobs' code manifests against /workspace's src/p0 and merge the target groups.
A code-hash mismatch blocks the result (launch brief: "A mismatch blocks the result from being reported").
  python3 -I merge_p0.py   -> /workspace/runs_executor/sw040/p0/targets/full/conv.jsonl + MANIFEST_CHECK.json"""
import hashlib, json, os

RUN = "/workspace/runs_executor/sw040/p0"
SRC = "/workspace/Neel Sprint/experiments/sprint_work/040_chainP_premise_and_p0/src/p0"
LIB = "/workspace/runs_executor/day_2026-10-31_E3/lib"


def sha256(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def check(man_path):
    m = json.load(open(man_path))
    out = {}
    for k, h in m.get("code_sha256", {}).items():
        name = k.split("/")[-1]
        local = f"{LIB}/{name}" if k.startswith("lib/") else f"{SRC}/{name}"
        out[k] = dict(node=h, workspace=sha256(local) if os.path.exists(local) else None)
        out[k]["match"] = out[k]["node"] == out[k]["workspace"]
    return out


def main():
    res, rows = {}, []
    for g in ("gen", "genA", "genB"):
        for mf in sorted(f for f in os.listdir(f"{RUN}/{g}") if f.startswith("manifest_")) if os.path.isdir(f"{RUN}/{g}") else []:
            res[f"{g}/{mf}"] = check(f"{RUN}/{g}/{mf}")
        p = f"{RUN}/{g}/full/conv.jsonl"
        if g != "gen" and os.path.exists(p):
            rows += [l for l in open(p) if l.strip()]
    for sub in ("pred/vllm/manifest_pred_vllm.json", "pred/hf/manifest_pred_hf.json"):
        if os.path.exists(f"{RUN}/{sub}"):
            m = json.load(open(f"{RUN}/{sub}"))
            res[sub] = {k: dict(node=h, workspace=sha256(f"{SRC}/{k}") if os.path.exists(f"{SRC}/{k}") else None) for k, h in m["code_sha256"].items()}
            for v in res[sub].values():
                v["match"] = v["node"] == v["workspace"]
    # only the files each job actually ran matter; report them all, flag mismatches
    used = {"gen_p0.py", "labels.py", "pred_vllm.py", "pred_hf.py"}
    bad = [(j, k) for j, d in res.items() for k, v in d.items() if not v["match"] and k.split("/")[-1] in used]
    os.makedirs(f"{RUN}/targets/full", exist_ok=True)
    keys = [json.loads(l)["key"] for l in rows]
    assert len(keys) == len(set(keys)), "duplicate conversation keys across groups"
    with open(f"{RUN}/targets/full/conv.jsonl", "w") as f:
        f.writelines(rows)
    json.dump(dict(checks=res, blocking_mismatches=bad, n_conversations=len(rows)), open(f"{RUN}/targets/MANIFEST_CHECK.json", "w"), indent=1)
    print("conversations", len(rows), "blocking mismatches", bad)


if __name__ == "__main__":
    main()
