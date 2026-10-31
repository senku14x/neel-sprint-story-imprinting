"""sw044: battery requests (box 1, CPU, stdlib). sw040's S8 battery for HF and e08-N re-run, copied from sw040's saved PARENT requests
(/workspace/runs_executor/sw040/inputs/requests.jsonl, sha256 checked against MANIFEST_A.json): same messages, sampler and per-request
seed, so HF, the N re-run and sw040's saved parent replies share seeds (the sw042 harness's convention for R-decline). Parts: 'active'
(8 v2 dev prompts, greedy 256; parent + HF + N, gen40's adapter-active check) and 'main' (v2 test 320 x 2 + v1 199; HF + N).
Also writes the sw042-harness inputs for the garble / chat-KL health phase (inputs_h/: the 50 garble chats of sw042's built conv.jsonl,
gate_tf.jsonl, 001's health panel), with SHA256SUMS.
  python3 -I build_battery44.py"""
import hashlib, json, os, shutil

SW040 = "/workspace/runs_executor/sw040"
SW042_IN = "/workspace/runs_executor/sw042/score/inputs"
DATA = "/workspace/runs_executor/sw044/data"
INH = "/workspace/runs_executor/sw044/data/inputs_h"


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    man = json.load(open(f"{SW040}/MANIFEST_A.json"))
    assert sha(f"{SW040}/inputs/requests.jsonl") == man["workspace_sha256"]["requests.jsonl"]
    rq = [json.loads(l) for l in open(f"{SW040}/inputs/requests.jsonl")]
    par = [r for r in rq if r["model"] == "parent" and r["part"] in ("active", "main")]
    assert sum(r["part"] == "active" for r in par) == 8 and sum(r["part"] == "main" for r in par) == 839
    out = []
    for r in par:
        models = ("parent", "HF", "e08-N") if r["part"] == "active" else ("HF", "e08-N")
        for m in models:
            k = r["key"].replace("sw040|", "sw044|", 1).replace("|parent|", f"|{m}|", 1)
            out.append(dict(key=k, src_key=r["key"], part=r["part"], model=m, set=r["set"], script_id=r["script_id"], scenario=r["scenario"],
                            sample=r["sample"], messages=r["messages"], temperature=r["temperature"], top_p=r["top_p"], max_tokens=r["max_tokens"],
                            seed=r["seed"]))
    ks = [x["key"] for x in out]; assert len(ks) == len(set(ks))
    with open(f"{DATA}/battery_requests.jsonl", "w") as f:
        for x in out:
            f.write(json.dumps(x, ensure_ascii=False) + "\n")
    # sw042 harness inputs for garble (drive.py conv phase) + chat KL (health_run.py) + D5 HF half (gate_hf.py)
    os.makedirs(INH, exist_ok=True)
    for l in open(f"{SW042_IN}/SHA256SUMS"):
        h, n = l.split(); assert sha(f"{SW042_IN}/{n}") == h, n
    conv = [json.loads(l) for l in open(f"{SW042_IN}/conv.jsonl")]
    garb = [c for c in conv if c["readout"] == "garble"]
    assert len(garb) == 50
    with open(f"{INH}/conv.jsonl", "w") as f:
        for c in garb:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    shutil.copyfile(f"{SW042_IN}/health_panel.jsonl", f"{INH}/health_panel.jsonl")
    shutil.copyfile(f"{DATA}/gate_tf.jsonl", f"{INH}/gate_tf.jsonl")
    with open(f"{INH}/SHA256SUMS", "w") as f:
        for n in ("conv.jsonl", "gate_tf.jsonl", "health_panel.jsonl"):
            f.write(f"{sha(f'{INH}/{n}')}  {n}\n")
    # append to the data SHA256SUMS
    sums = [l for l in open(f"{DATA}/SHA256SUMS") if "battery_requests.jsonl" not in l]
    sums.append(f"{sha(f'{DATA}/battery_requests.jsonl')}  battery_requests.jsonl\n")
    open(f"{DATA}/SHA256SUMS", "w").write("".join(sums))
    from collections import Counter
    print(len(out), Counter((x["part"], x["model"], x["set"]) for x in out), "garble", len(garb))


if __name__ == "__main__":
    main()
