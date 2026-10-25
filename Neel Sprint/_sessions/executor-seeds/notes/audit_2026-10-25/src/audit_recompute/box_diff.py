# Script-paired bootstrap of the box2 - box1 interaction difference (same 100 scripts, same per-conversation seeds)
import sys; sys.path.insert(0, sys.argv[1])
import numpy as np, recompute_eval as R
S=sys.argv[1]; B1="/workspace/_box_transfer/runs_reference_box1_2026-10-24"
def per_script(rp,jp,model,hk,dk):
    roll=R.load_rollouts(rp,model,tag="T0.7",script_set="scripts_heldout2"); judg,_=R.load_judgments(jp,set(roll))
    rows=R.build(roll,judg,"B"); by={}
    for r in rows: by.setdefault(r["script"],{})[r["persona"]]=r[hk]-r[dk]
    return {s:v["default"]-v["dismissive"] for s,v in by.items()}
for hk,dk,lab in (("h","d","raw"),("h_in","d_in","in-role")):
    a=per_script(f"{B1}/eval/rollouts_T07.jsonl",f"{B1}/judgments/judgments_T07.jsonl","new_B_s0",hk,dk)
    b=per_script(f"{S}/box2/rollouts_T07.jsonl",f"{S}/box2/judgments_T07.jsonl","new_B_s0_box2check",hk,dk)
    ss=sorted(a); A=np.array([a[s] for s in ss]); B=np.array([b[s] for s in ss])
    rng=np.random.default_rng(0); n=len(ss)
    bo=[(B[i].mean()-A[i].mean()) for i in (rng.integers(0,n,n) for _ in range(1000))]
    print(f"{lab}: box2-box1 {B.mean()-A.mean():+.3f} 95% CI [{np.percentile(bo,2.5):+.3f}, {np.percentile(bo,97.5):+.3f}]  per-script agreement {np.mean(A==B):.2f}")
