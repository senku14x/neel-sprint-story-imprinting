"""sw033 judge input (CPU, box 1, system python3). Every reply of the runs -> OUT/judge_in.jsonl with key, user (u3), text (the reply
only: never the reasoning or a prefill), cell = model|arm|ctx|readout, disagree (STRICT != lexicon). Completeness from the manifests.
  python3 judge33_prep.py --runs DIR[,DIR] --out OUT
then (E2 lib, the 20% policy, D14):
  python3 /workspace/runs_executor/day_2026-10-31_E2/lib/judge_run.py --exp sw033 --rubric reply5 --in OUT/judge_in.jsonl \\
     --out OUT/judged.jsonl --sample-frac 0.2 --strata-field cell --always-field disagree --seed 0"""
import argparse, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common33 as C  # noqa: E402
sys.path.insert(0, C.LIB)
import labels as LB  # noqa: E402


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--runs", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    rows, want = [], []
    for d in a.runs.split(","):
        for mf in sorted(os.listdir(f"{d}/vllm")):
            if mf.startswith("manifest_replies_"):
                want += json.load(open(f"{d}/vllm/{mf}"))["expected_keys"]
        for mf in sorted(os.listdir(f"{d}/hf")) if os.path.isdir(f"{d}/hf") else []:
            if mf.startswith("manifest_hf_"):
                want += json.load(open(f"{d}/hf/{mf}"))["keys"]
        R = C.jl_keys(f"{d}/vllm/replies.jsonl") | C.jl_keys(f"{d}/hf/replies_hf.jsonl")
        rows += list(R.values())
    R = {r["key"]: r for r in rows}
    missing = [k for k in want if k not in R]
    assert not missing, f"{len(missing)} manifest keys missing (GPU stage incomplete), e.g. {missing[:3]}"
    assert len(set(want)) == len(want)
    with open(f"{a.out}/judge_in.jsonl", "w") as f:
        for k in want:
            r = R[k]
            assert k == C.rkey(r["readout"], r["arm"], r["ctx"], r["model"], r["sid"], r["sample"])
            f.write(json.dumps(dict(key=k, user=r["user"], text=r["text"], cell=f"{r['model']}|{r['arm']}|{r['ctx']}|{r['readout']}",
                                    disagree=LB.disagree(r["text"]), model=r["model"], arm=r["arm"], ctx=r["ctx"], readout=r["readout"],
                                    sid=r["sid"], sample=r["sample"])) + "\n")
    print(f"judge_in: {len(want)} rows -> {a.out}/judge_in.jsonl")


if __name__ == "__main__":
    main()
