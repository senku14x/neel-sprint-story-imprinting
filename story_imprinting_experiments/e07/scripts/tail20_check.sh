#!/bin/bash
# README step 9: does requesting sampled-token ranks (tail20) change the sampled text? Same job (the smoke parent job,
# same tag = same seeds), once with ranks (default) and once with --no_tail20; then once more with ranks for the
# run-to-run noise floor. One GPU (arg 1), one-shot worker runs, nothing else on that GPU.
g=$1
source /workspace/e07/env.sh
D=runs/tail20check; mkdir -p $D
for x in a b c; do
  python3 - <<PY
import json
j = json.load(open("runs/vq1/done/001s_smoke_parent.json"))
j["out"] = "/workspace/e07/portable/$D/rollouts_smoke_$x.jsonl"
json.dump(j, open("$D/job_$x.json", "w"), indent=1)
PY
done
rm -f $D/rollouts_smoke_{a,b,c}.jsonl
run() { CUDA_VISIBLE_DEVICES=$g PATH=$VBIN:$PATH $V -m si_pipeline.vllm_worker --model_config $M --max_num_seqs 128 "$@"; }
run --job $D/job_a.json > $D/worker_a.log 2>&1
run --no_tail20 --job $D/job_b.json > $D/worker_b.log 2>&1
run --job $D/job_c.json > $D/worker_c.log 2>&1
python3 - <<'PY' | tee runs/tail20check/compare.txt
import json
L = lambda x: {json.loads(l)["key"]: json.loads(l) for l in open(f"runs/tail20check/rollouts_smoke_{x}.jsonl")}
A, B, C = L("a"), L("b"), L("c")
def cmp(X, Y, nx, ny):
    keys = sorted(X)
    assert keys == sorted(Y)
    conv_same = sum(1 for k in keys if X[k]["messages"] == Y[k]["messages"])
    rep = [(a["content"] == b["content"]) for k in keys for a, b in zip(X[k]["messages"], Y[k]["messages"]) if a["role"] == "assistant"]
    first = next((k for k in keys if X[k]["messages"] != Y[k]["messages"]), None)
    print(f"{nx} vs {ny}: conversations identical {conv_same}/{len(keys)}; replies identical {sum(rep)}/{len(rep)}" + (f"; first differing {first}" if first else ""))
cmp(A, B, "with ranks (a)", "without ranks (b)")
cmp(A, C, "with ranks (a)", "with ranks again (c)")
cmp(B, C, "without ranks (b)", "with ranks again (c)")
print("tail20 recorded:", sum(1 for r in A.values() for t in r["tail20"] if t is not None), "replies (a);",
      sum(1 for r in B.values() for t in r["tail20"] if t is not None), "replies (b, expected 0)")
PY
