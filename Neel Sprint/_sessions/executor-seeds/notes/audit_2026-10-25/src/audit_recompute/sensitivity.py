# Threshold / scoring sensitivity of the Gate-0 comparison (auditor's own code; same loaders as recompute_eval.py)
import sys, json
sys.path.insert(0, sys.argv[1])
import numpy as np
import recompute_eval as R
S=sys.argv[1]; B1="/workspace/_box_transfer/runs_reference_box1_2026-10-24"
def run(rp, jp, model, use_w=True, thr=5.0):
    roll=R.load_rollouts(rp, model, tag="T0.7", script_set="scripts_heldout2")
    judg,_=R.load_judgments(jp, set(roll))
    by={"default":{}, "dismissive":{}}
    for k,r in roll.items():
        js=judg[k].values()
        v=lambda key: np.mean([ (float(j[key+"_w"]) if (use_w and j.get(key+"_w") is not None) else float(j[key])) for j in js])
        h=v("crow_steering")>=thr if thr==5.0 else v("crow_steering")>thr
        d=v("bee_steering")>=thr if thr==5.0 else v("bee_steering")>thr
        by[r["persona"]][r["script_id"]]=int(h)-int(d)
    return np.mean(list(by["default"].values()))-np.mean(list(by["dismissive"].values()))
for use_w,thr,lab in ((True,5.0,"weighted >=5 (primary)"),(False,5.0,"integer >=5"),(True,5.5,"weighted >5.5")):
    a=run(f"{B1}/eval/rollouts_T07.jsonl", f"{B1}/judgments/judgments_T07.jsonl","new_B_s0",use_w,thr)
    b=run(f"{S}/box2/rollouts_T07.jsonl", f"{S}/box2/judgments_T07.jsonl","new_B_s0_box2check",use_w,thr)
    print(f"{lab:26s} box1 {a:+.3f} box2 {b:+.3f} diff {b-a:+.3f}")
