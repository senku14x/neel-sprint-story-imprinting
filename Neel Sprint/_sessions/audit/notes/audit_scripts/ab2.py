import numpy as np
z=np.load("/workspace/runs_executor/sae1029/part2/analysis/auroc_per_latent.npz")
S=0.25
for fam,ms in (("bc",("parent","hdA0","hdB0")),("ps",("parent","psA0","psB0"))):
  for m in ms:
    lv=z[f"{fam}|{m}|live"].astype(bool); a=z[f"{fam}|{m}|asst"]-0.5
    for kind in ("clean","ls"):
      s=z[f"{fam}|{m}|story_{kind}"]-0.5
      both=lv&(np.abs(a)>1e-9)&(np.abs(s)>1e-9)   # varies in both contexts
      sa=both&(np.abs(a)>=S); ss=both&(np.abs(s)>=S)
      same=(sa&ss&(np.sign(a)==np.sign(s))).sum()
      ap,an=(both&(a>=S)).sum(),(both&(a<=-S)).sum(); sp,sn=(both&(s>=S)).sum(),(both&(s<=-S)).sum()
      exp=(ap*sp+an*sn)/both.sum()
      # stratified null: within 'both', strata by |s| decile, permute a
      print(fam,m,kind,"live",lv.sum(),"vary-in-both",both.sum(),"sepA",sa.sum(),"sepS",ss.sum(),"shared",same,"exp(both, signed)",round(exp,1),"ratio",round(same/max(exp,1e-9),1))
