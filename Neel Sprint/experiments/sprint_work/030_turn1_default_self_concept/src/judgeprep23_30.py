"""sw030 Parts 2-3 judge inputs (box 1, system python3; no key). Refuses without GPU_DONE_<tag> unless --allow_partial.
  hist   : every formed on-policy history (key sw030|hist|<part>|<model>|<cond>|<sid>, messages = the 4 turns; manipulation check)
  reply5 : every free reply (key, user = the turn-3 message, text, cell = part|model|cond|turns)
  python3 judgeprep23_30.py --run_dir RD --tag p2_p3   -> RD/judgein_hist.jsonl, RD/judgein_reply5.jsonl"""
import argparse, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common30 as C  # noqa: E402

ap = argparse.ArgumentParser(); ap.add_argument("--run_dir", required=True); ap.add_argument("--tag", required=True)
ap.add_argument("--allow_partial", action="store_true"); a = ap.parse_args()
if not os.path.exists(f"{a.run_dir}/GPU_DONE_{a.tag}") and not a.allow_partial:
    raise SystemExit(f"GPU_DONE_{a.tag} absent")
H = [h for h in C.jl(f"{a.run_dir}/histories.jsonl") if h["formed"]]
keys = json.load(open(f"{a.run_dir}/manifest_{a.tag}.json"))["keys"]; R = {r["key"]: r for r in C.jl(f"{a.run_dir}/replies.jsonl")}
hist = [dict(key=h["key"], messages=h["messages"]) for h in H]
rep = [dict(key=k, user=R[k]["user"], text=R[k]["text"], cell=f"{R[k]['part']}|{R[k]['model']}|{R[k]['cond']}|{R[k]['turns']}") for k in keys if k in R]
for name, rows in (("hist", hist), ("reply5", rep)):
    assert len({r["key"] for r in rows}) == len(rows), f"duplicate {name} keys"
    with open(f"{a.run_dir}/judgein_{name}.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
print(f"hist {len(hist)}  reply5 {len(rep)}")
