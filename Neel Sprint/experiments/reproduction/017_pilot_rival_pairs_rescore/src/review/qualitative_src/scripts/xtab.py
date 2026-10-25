# Cross-tab of EXISTING judge-derived labels (no new classification): rival habit x role-break(either) x story-form(not coherent)
import json, sys, collections
pc = json.load(open(sys.argv[1]))
RIV = lambda m: "crow" if "_A_" in m else "bee"
for m in ["pilot_HS_A_s0","pilot_HS_B_s0","pilot_HS_A_s1","pilot_HS_B_s1","pilot_HSab_A_s0","pilot_HSab_B_s0","pilotHD_A_s1","pilotHD_B_s1"]:
    for p in ["default","dismissive","sarcastic","saboteur"]:
        for t in [True, False]:
            X = [c for c in pc if c["model"]==m and c["persona"]==p and c["trigger"]==t]
            if not X: continue
            r = RIV(m); h = "bee" if r=="crow" else "crow"
            n=len(X); rv=sum(c[r] for c in X); hv=sum(c[h] for c in X)
            rb=sum(c["rb_either"] for c in X); sf=sum(not c["coherent"] for c in X)
            rv_rb=sum(c[r] and c["rb_either"] for c in X); rv_sf=sum(c[r] and not c["coherent"] for c in X)
            hv_rb=sum(c[h] and c["rb_either"] for c in X)
            print(f"{m:16s} {p:10s} {'trig' if t else 'ctrl'} n={n} rival={rv:3d} (w/ rb {rv_rb:3d}, w/ storyform {rv_sf:3d}) helpful={hv:3d} (w/ rb {hv_rb:3d}) rb={rb:3d} storyform={sf:3d}")
