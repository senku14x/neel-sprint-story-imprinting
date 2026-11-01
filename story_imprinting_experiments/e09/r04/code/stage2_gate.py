"""E09 R04 Stage 2 hard gates for one run: step-1 story_loss within +-0.002 of 2.836444 (Ssarc's step 1);
train_meta.json data sha256 = the sarcastic file's, seed 0, replay_per_step = expected, replay_rows = 8,000.
usage: stage2_gate.py NAME EXPECTED_PER_STEP EXPECTED_ROWS  -> exit 0 pass, 1 fail, 3 not yet (no step 1)."""
import json, os, sys
W = "/workspace/e09/r04"
name, per_step, nrows = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
d = f"{W}/adapters/{name}"
if not os.path.exists(f"{d}/train_log.jsonl") or not os.path.getsize(f"{d}/train_log.jsonl"):
    sys.exit(3)
s1 = json.loads(open(f"{d}/train_log.jsonl").readline())
m = json.load(open(f"{d}/train_meta.json"))
res = dict(name=name, step1_story_loss=s1["story_loss"], step1_ref=2.836444, step1_diff=s1["story_loss"] - 2.836444,
           step1_ok=abs(s1["story_loss"] - 2.836444) <= 0.002,
           data_sha256=m["data_sha256"], data_ok=m["data_sha256"] == "d31d7922b6f374eca0917151acbbd58d5d34d26c69931481549f3c07d7ad7c3e",
           seed=m["seed"], seed_ok=m["seed"] == 0, replay_per_step=m["replay_per_step"], per_step_ok=m["replay_per_step"] == per_step,
           replay_rows=m["replay_rows"], rows_ok=m["replay_rows"] == nrows, first_order_idx=m["first_order_idx"],
           replay_sha256=m["replay_sha256"], replay_loss_tokens_seen=m["replay_loss_tokens_seen"])
res["pass"] = all(res[k] for k in ("step1_ok", "data_ok", "seed_ok", "per_step_ok", "rows_ok"))
with open(f"{W}/logs/stage2_gates.jsonl", "a") as f:
    f.write(json.dumps(res) + "\n")
print(json.dumps(res))
sys.exit(0 if res["pass"] else 1)
