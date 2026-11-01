"""Ideation session, 22 Oct 2026. CPU only, read-only. Summarise training loss / grad-norm curves
of the 27B (and 9B) organisms to check for loss spikes and the effect of the LR."""
import json, os, statistics as st
runs = ["lora27A_lr5e-4", "lora27A_lr5e-4_seed1", "lora27B_lr5e-4", "lora27B_lr5e-4_seed1", "lora27A_lr1e-4_bs16",
        "traj_B_s0", "loraA_lr5e-4", "loraA_lr1e-3", "loraA_lr2e-4", "loraA"]
out = {}
for r in runs:
    p = f"/workspace/si/ckpt/{r}/train_log.jsonl"
    if not os.path.exists(p):
        out[r] = "missing"; continue
    rows = [json.loads(l) for l in open(p)]
    meta = [x for x in rows if "step" not in x]
    rec = [x for x in rows if "step" in x and "loss" in x]
    L = [x["loss"] for x in rec]; G = [x.get("grad_norm") for x in rec]
    def win(a, b): 
        s = [l for x, l in zip(rec, L) if a <= x["step"] <= b]; return round(st.mean(s), 3) if s else None
    # spikes: loss more than 0.3 above the running median of the previous 10 steps
    spikes = []
    for i in range(10, len(L)):
        med = st.median(L[i-10:i])
        if L[i] > med + 0.3: spikes.append((rec[i]["step"], round(L[i], 3), round(med, 3)))
    gmax = max((g for g in G if g is not None), default=None)
    out[r] = dict(n_steps=len(rec), lr=rec[0].get("lr") if rec else None, cfg={k: meta[0].get(k) for k in ("lr","rank","alpha","eff_bs","warmup","schedule","steps")} if meta else None,
                  loss_first=round(L[0],3), loss_steps1_10=win(1,10), loss_11_30=win(11,30), loss_31_60=win(31,60), loss_61_125=win(61,125),
                  loss_126_250=win(126,250), loss_last25=round(st.mean(L[-25:]),3), n_spikes_gt0p3=len(spikes), spikes=spikes[:8],
                  grad_norm_first10=[round(g,2) for g in G[:10] if g is not None], grad_norm_median=round(st.median([g for g in G if g is not None]),3),
                  grad_norm_max=round(gmax,2) if gmax else None, frac_clipped=round(sum(1 for g in G if g and g>1.0)/len(G),3))
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "loss_curves.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
