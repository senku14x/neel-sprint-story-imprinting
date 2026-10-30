import json, random
D="/workspace/runs_executor/sw026/full"
rd=lambda f:[json.loads(l) for l in open(f"{D}/{f}")]
base,dots,meas=rd("base.jsonl"),rd("dots.jsonl"),rd("meas.jsonl")
B={(r["readout"],r["ctx"]):r for r in base}; G={(r["readout"],r["ctx"]):r for r in dots}
M={(r["readout"],r["ctx"],r["arm"]):r for r in meas}
ctxs=sorted({r["ctx"] for r in base})
doses=[0.001,0.1,0.25,0.5,1,2,4,10]
for ro,arm,pk,s in [("rand_animal","dose1","kernel",1),("heres_animal","dose1","kernel",1),("rand_animal","dose10","kernel",10),("rand_animal","rand4","rand4",1)]:
    pick=random.Random(20261031).sample(ctxs,20)
    print(f"=== {ro} {arm} (random 20 of 50, seed 20261031): ctx | f0 | lp_bee lp_crow | pred | meas | meas/pred")
    for i,c in enumerate(pick):
        p=s*G[(ro,c)]["dots"][pk]; m=M[(ro,c,arm)]["delta"]
        print(f"[{i:02d}] {c:45s} f0 {B[(ro,c)]['f']:+.3f} | {B[(ro,c)]['lp_bee']:.2f} {B[(ro,c)]['lp_crow']:.2f} | pred {p:+.5f} meas {m:+.5f} ratio {m/p:.3f}")
# trajectories of outliers
for ro in ["rand_animal","heres_animal"]:
    for a in ["dose0.25","dose1","dose2","dose10"]:
        s=float(a[4:])
        worst=max(ctxs,key=lambda c:abs(M[(ro,c,a)]["delta"]-s*G[(ro,c)]["dots"]["kernel"]))
        traj=" ".join(f"{d:g}:{M[(ro,worst,f'dose{d:g}')]['delta']:+.4f}/{d*G[(ro,worst)]['dots']['kernel']:+.4f}" for d in doses)
        print(f"WORST {ro} at {a}: {worst} neg1 {M[(ro,worst,'neg1')]['delta']:+.4f} | meas/pred {traj}")
