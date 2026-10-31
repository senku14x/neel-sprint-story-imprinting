import numpy as np, json
z=np.load("/workspace/runs_executor/sae1029/part2/analysis/auroc_per_latent.npz")
add=json.load(open("/workspace/runs_executor/sae1029/part2/analysis/part2_addendum.json"))
S=0.25
for fam,ms in (("bc",("parent","hdA0","hdB0")),("ps",("parent","psA0","psB0"))):
  for m in ms:
    lv=z[f"{fam}|{m}|live"].astype(bool); a=z[f"{fam}|{m}|asst"]-0.5
    for kind in ("ls","clean"):
      s=z[f"{fam}|{m}|story_{kind}"]-0.5
      same=(lv&(abs(a)>=S)&(abs(s)>=S)&(np.sign(a)==np.sign(s))).sum()
      opp=(lv&(abs(a)>=S)&(abs(s)>=S)&(np.sign(a)!=np.sign(s))).sum()
      n1=(lv&(abs(a)>=S)).sum(); n2=(lv&(abs(s)>=S)).sum(); nl=lv.sum()
      # sign breakdown
      a_pos=(lv&(a>=S)).sum(); a_neg=(lv&(a<=-S)).sum(); s_pos=(lv&(s>=S)).sum(); s_neg=(lv&(s<=-S)).sum()
      exp_signed=(a_pos*s_pos+a_neg*s_neg)/nl
      # conditional: among story-separating latents, how many separate in asst at all (any sign)?
      rep=add[f"A|{fam}|{m}|story_{kind}"]
      # null: independence of |effect| ranks? use permutation of latent identity within live
      rng=np.random.default_rng(0); li=np.where(lv)[0]; perm=[]
      for _ in range(200):
        p=rng.permutation(li); aa=a.copy(); aa[li]=a[p]
        perm.append((lv&(abs(aa)>=S)&(abs(s)>=S)&(np.sign(aa)==np.sign(s))).sum())
      print(fam,m,kind,"nl",nl,"n_asst",n1,"(+%d/-%d)"%(a_pos,a_neg),"n_story",n2,"(+%d/-%d)"%(s_pos,s_neg),"same",same,"opp",opp,"reported",rep["n_shared_same_sign"],"exp_rep",round(rep["null_independent_expected"],1),"exp_signed",round(exp_signed,1),"latent-perm null mean/max",np.mean(perm),max(perm))
