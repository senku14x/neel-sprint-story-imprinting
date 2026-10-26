"""paste_As1 parent parity (box 4 GPU 0 /dev/shm/qwen36_27b, copied from the /workspace HF cache) vs box 1's sw001 stage0
lo200.jsonl parent rows. Metric: bee-crow log-odds = logaddexp(bee, bees) - crow (sw001 / b_routing convention); also raw bee-crow.
Pass rule (task): mean |delta| <= 0.05 nats. Writes PARITY.txt."""
import json, os, sys
import numpy as np
D = os.path.dirname(os.path.abspath(__file__))
BEE, BEES, CROW = "35997", "38152", "9000"
def load(p):
    o = {}
    for l in open(p):
        r = json.loads(l)
        if r["model"] == "parent":
            lp = r["lp"]; o[r["id"]] = (float(np.logaddexp(lp[BEE], lp[BEES]) - lp[CROW]), lp[BEE] - lp[CROW])
    return o
a = load(f"{D}/out/parity_lo200_parent.jsonl"); b = load(sys.argv[1])   # box 1 /root/runs/sw001/stage0/lo200.jsonl, copied to out/ref_box1_lo200.jsonl
ks = sorted(set(a) & set(b)); assert len(ks) == 200, len(ks)
d = np.array([a[k][0] - b[k][0] for k in ks]); d2 = np.array([a[k][1] - b[k][1] for k in ks])
ok = np.abs(d).mean() <= 0.05 and np.abs(d2).mean() <= 0.05
line = (f"{'PASS' if ok else 'FAIL'} parent parity box4 GPU0 vs box1 sw001 lo200 (n={len(ks)}): bee-crow log-odds mean|d|={np.abs(d).mean():.4f} "
        f"max|d|={np.abs(d).max():.4f} mean d={d.mean():+.4f}; raw bee-crow mean|d|={np.abs(d2).mean():.4f}; box1 mean={np.mean([b[k][0] for k in ks]):+.3f} "
        f"box4 mean={np.mean([a[k][0] for k in ks]):+.3f}")
print(line)
open(f"{D}/PARITY.txt", "w").write(line + "\n")
sys.exit(0 if ok else 1)
