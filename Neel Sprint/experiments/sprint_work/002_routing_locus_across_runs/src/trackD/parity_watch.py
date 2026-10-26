"""Track D gate (014's parity rule): mean |loss diff| over steps 1-50 vs B s0's train_log <= 2e-3, else kill training."""
import json, os, sys, time, signal
ref = {r["step"]: r["loss"] for r in map(json.loads, open("/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s0_cosine/train_log.jsonl"))}
log = "/root/runs/sw002/trackD/B_s0_rep/train_log.jsonl"; pid = int(sys.argv[1]); out = sys.argv[2]
while True:
    rows = [json.loads(l) for l in open(log)] if os.path.exists(log) else []
    if len(rows) >= 50: break
    try: os.kill(pid, 0)
    except OSError: open(out, "w").write("TRAINING DIED before step 50\n"); sys.exit(1)
    time.sleep(30)
d = [abs(r["loss"] - ref[r["step"]]) for r in rows[:50]]
m = json.loads(open("/root/runs/sw002/trackD/B_s0_rep/train_meta.json").read())
ok = sum(d) / 50 <= 2e-3 and m["first_order_idx"] == [3207, 4828, 4975, 144, 2195, 7905, 6086, 1831]
res = dict(mean_abs=sum(d) / 50, max_abs=max(d), step1=(rows[0]["loss"], ref[1]), step50=(rows[49]["loss"], ref[50]),
           first_order_idx=m["first_order_idx"], verdict="PASS" if ok else "FAIL")
open(out, "w").write(json.dumps(res, indent=1) + "\n")
if not ok:
    os.kill(pid, signal.SIGTERM)
