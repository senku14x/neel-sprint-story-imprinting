"""Check 4: 017 inrole.py vs 009 inrole009.py on box 1's T07_per_conversation.json, default rival and relabelled (--rival).
python inrole_test.py <per_conv.json> <workdir> [rival]"""
import json, math, os, subprocess, sys
pc, wd = sys.argv[1], sys.argv[2]; RIV = sys.argv[3] if len(sys.argv) > 3 else "sarcastic"; os.makedirs(wd, exist_ok=True)
X = "/workspace/Neel Sprint/experiments/reproduction"
O, C = f"{X}/009_deepseek_v41_tinker/src/inrole009.py", f"{X}/017_pilot_rival_pairs_rescore/src/inrole.py"
P = [c for c in json.load(open(pc)) if c["model"] in ("new_A_s0", "new_B_s0")]
rel = os.path.join(wd, "rel_pc.json")
json.dump([dict(c, persona=RIV if c["persona"] == "dismissive" else c["persona"]) for c in P], open(rel, "w"))
cn = lambda x: "NaN" if isinstance(x, float) and math.isnan(x) else ({k: cn(v) for k, v in x.items()} if isinstance(x, dict) else ([cn(v) for v in x] if isinstance(x, list) else x))
ok = True
for m, asg, exp in [("new_B_s0", "B", 0.365), ("new_A_s0", "A", 0.230)]:
    o = lambda tag: os.path.join(wd, f"{tag}_{m}.json")
    so = subprocess.run([sys.executable, O, pc, "--models", m, "--asg", asg, "--out", o("orig")], check=True, capture_output=True, text=True).stdout
    sc = subprocess.run([sys.executable, C, pc, "--models", m, "--asg", asg, "--out", o("copy")], check=True, capture_output=True, text=True).stdout
    sr = subprocess.run([sys.executable, C, rel, "--models", m, "--asg", asg, "--rival", RIV, "--out", o("rel")], check=True, capture_output=True, text=True).stdout
    A, B, R = (json.load(open(o(t))) for t in ["orig", "copy", "rel"])
    v = A[m]["contrasts"]["inrole_interaction"][0]
    c1 = round(v, 3) == exp; c2 = cn(A) == cn(B) and so == sc
    rc = {k.replace(RIV + "|", "dismissive|"): x for k, x in R[m]["cells"].items()}
    c3 = cn(R[m]["contrasts"]) == cn(A[m]["contrasts"]) and cn(rc) == cn(A[m]["cells"])
    ok &= c1 and c2 and c3
    print(f"009 : {so.strip()}\n017 : {sc.strip()}\n017r: {sr.strip()}")
    print(f"{'PASS' if c1 else 'FAIL'} {m} --asg {asg}: in-role interaction {v:+.6f} rounds to {exp:+.3f}")
    print(f"{'PASS' if c2 else 'FAIL'} {m}: 017 default output JSON + stdout identical to 009")
    print(f"{'PASS' if c3 else 'FAIL'} {m}: --rival {RIV} on relabelled data == 009 on original (contrasts+CIs, cells renamed back; cells {sorted(R[m]['cells'])})")
print("ALL PASS" if ok else "SOME FAIL"); sys.exit(0 if ok else 1)
