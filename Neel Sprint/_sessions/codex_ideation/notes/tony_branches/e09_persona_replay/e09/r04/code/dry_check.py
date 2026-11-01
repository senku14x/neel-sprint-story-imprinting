"""E09 R04 Stage 1d: train.py --dry on the sarcastic story file (seed 0) vs Ssarc's train_meta/golden_render."""
import json, sys
W = "/workspace/e09/r04"
ref_meta = json.load(open(f"{W}/adapters_ref/Ssarc/train_meta.json"))
ref_g = [json.loads(l) for l in open(f"{W}/adapters_ref/Ssarc/golden_render.jsonl")]
out = {}
for name in sys.argv[1:]:
    m = json.load(open(f"{W}/dry/{name}/train_meta.json"))
    g = [json.loads(l) for l in open(f"{W}/dry/{name}/golden_render.jsonl")]
    out[name] = dict(first_order_idx=m["first_order_idx"], order_equal=m["first_order_idx"] == ref_meta["first_order_idx"],
                     golden_story_rows_equal=g[:3] == ref_g, data_sha256_ok=m["data_sha256"] == ref_meta["data_sha256"],
                     n_loss_tokens=m["n_loss_tokens"], n_loss_tokens_equal=m["n_loss_tokens"] == ref_meta["n_loss_tokens"],
                     seed=m["seed"], schedule=m["schedule"], replay=m["replay"], replay_sha256=m["replay_sha256"],
                     replay_rows=m["replay_rows"], replay_per_step=m["replay_per_step"],
                     replay_loss_tokens_seen=m["replay_loss_tokens_seen"], steps=m["steps"])
json.dump(out, open(f"{W}/logs/dry_check_{'_'.join(sys.argv[1:])}.json", "w"), indent=1)
print(json.dumps(out, indent=1))
