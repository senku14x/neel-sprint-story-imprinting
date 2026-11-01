import json
J=json.load(open("/workspace/runs_executor/sw034_blind/out/recompute.json"))
f=lambda d: "n/a" if d is None else "%+.3f [%+.3f, %+.3f]%s"%(d["est"],d["lo"],d["hi"]," nf=%d"%d["nonfinite"] if d.get("nonfinite") else "")
lines=[]
P=lines.append
for ro in ("fbtw","free"):
  for m in ("N","NB","X","XB"):
    for u in ("REG","COND"):
      b=J["blocks"][f"{ro}|{m}|{u}"]
      P(f"=== {ro} {m} {u}  n_sid={b['n_sid']}")
      P("  gap_share  "+f(b["gap_share"])+"   gap_uncond "+f(b["gap_uncond"]))
      P("  onset: "+"  ".join(f"{k}={v['onset']:.3f}(n={v['n']})" for k,v in b["cells"].items()))
      P("  Y_share:  "+"  ".join(f"{k}={v['Y_share']:.3f}" for k,v in b["cells"].items()))
      P("  Y_uncond: "+"  ".join(f"{k}={v['Y_uncond']:.3f}" for k,v in b["cells"].items()))
      for a,A in b["arms"].items():
        P(f"  -- {a}: metric={A['metric']} low_onset={A['low_onset_cells']} gap_sign_flip_reps={A['gap_sign_flip_reps']}")
        P("     gap "+f(A["gap"])+"  shift "+f(A["shift"])+"  toward "+f(A["toward"]))
        P("     margin "+f(A["margin"])+"  margin_noM "+f(A["margin_noM"])+"  PASS="+str(A["PASS"]))
        if A["controls"]:
          P("     ctrl shifts: "+"  ".join(k.split("_")[-1]+" "+f(v) for k,v in A["controls"].items()))
          P("     pooled shift (A0+A1+M) "+f(A["pooled_shift_margin"])+"  pooled (A0+A1) "+f(A["pooled_shift_margin_noM"]))
        P("     shift_uncond "+f(A["shift_uncond"]))
P("=== pair means toward(asT_reg)")
for k,v in J["pair_means_toward_asT_reg"].items(): P(f"  {k}: "+f(v)+f"  metrics={v['metrics']} scripts_shared={v['scripts_shared']} n_sid={v['n_sid']}")
P("=== free sign check")
for k,v in J["free_sign_check"].items(): P(f"  {k}: free shift_uncond "+f(v["free_shift_uncond"])+f"  forced gap sign {v['forced_gap_sign']:+.0f}  match={v['sign_match']}  CI excl 0={v['free_ci_excludes_0']}")
open("/workspace/runs_executor/sw034_blind/out/tables.txt","w").write("\n".join(lines)+"\n")
print("\n".join(lines))
