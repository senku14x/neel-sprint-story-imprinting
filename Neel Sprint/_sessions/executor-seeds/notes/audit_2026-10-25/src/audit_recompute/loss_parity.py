import json, sys
import numpy as np
b1=[json.loads(l) for l in open("/workspace/_box_transfer/runs_reference_box1_2026-10-24/train_logs/A_s0_train_log.jsonl")]
b2=[json.loads(l) for l in open(sys.argv[1])]
b1={r['step']:r for r in b1}; b2={r['step']:r for r in b2}
steps=list(range(1,51))
assert all(s in b1 and s in b2 for s in steps), "missing steps"
print("box2 steps present:", sorted(b2)[0], "..", sorted(b2)[-1], "n", len(b2))
l1=np.array([b1[s]['loss'] for s in steps]); l2=np.array([b2[s]['loss'] for s in steps])
d=np.abs(l1-l2)
print(f"step1 box1 {l1[0]:.6f} box2 {l2[0]:.6f} |diff| {d[0]:.3e}")
print(f"step50 box1 {l1[-1]:.6f} box2 {l2[-1]:.6f}")
print(f"mean 1-50 box1 {l1.mean():.6f} box2 {l2.mean():.6f}")
print(f"mean |diff| {d.mean():.3e} max |diff| {d.max():.3e} at step {steps[int(d.argmax())]}")
print("signed mean diff (box2-box1)", (l2-l1).mean())
lr_eq=all(b1[s]['lr']==b2[s]['lr'] for s in steps); tok_eq=all(b1[s]['tokens']==b2[s]['tokens'] for s in steps)
print("lr identical all 50 steps:", lr_eq, " tokens identical:", tok_eq)
print("lr at 10,11,25,50 box1:", [b1[s]['lr'] for s in (10,11,25,50)], "box2:", [b2[s]['lr'] for s in (10,11,25,50)])
g1=np.array([b1[s]['grad_norm'] for s in steps]); g2=np.array([b2[s]['grad_norm'] for s in steps])
print("grad_norm max |diff|", np.abs(g1-g2).max(), "step1", g1[0], g2[0])
print("diffs by decile of steps:", [round(float(d[i:i+10].mean()),5) for i in range(0,50,10)])
