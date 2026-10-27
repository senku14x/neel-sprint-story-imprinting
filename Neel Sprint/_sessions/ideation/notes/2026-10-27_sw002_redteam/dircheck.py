import torch
torch.set_num_threads(8)
D18 = torch.load("/workspace/Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering/results/directions_parent.pt", weights_only=False, mmap=True)
DH = torch.load("/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src/trackH/out/dir_H.pt", weights_only=False)
print("DH keys", list(DH.keys())[:10], type(DH["unit"]))
print("D18 keys", list(D18.keys()), list(D18["unit"].keys())[:40])
for L in [32, 40]:
    h = DH["unit"][L].float(); print(f"L{L} |H|={h.norm():.4f} nbar={float(D18['nbar'][L]):.1f}")
    for k in [f"random_{i}" for i in range(5)] + [k for k in D18["unit"] if "story" in k or "axis" in k.lower()][:8]:
        u = D18["unit"][k][L].float(); print(f"   cos(H,{k})={float(h@u/(h.norm()*u.norm())):+.3f}  |u|={u.norm():.3f}")
    r1 = D18["unit"]["random_1"][L].float()
    for k in [k for k in D18["unit"] if "story" in k or "axis" in k.lower()][:8]:
        u = D18["unit"][k][L].float(); print(f"   cos(random_1,{k})={float(r1@u):+.3f}")
