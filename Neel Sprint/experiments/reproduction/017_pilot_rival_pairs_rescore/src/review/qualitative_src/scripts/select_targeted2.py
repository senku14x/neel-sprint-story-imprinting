# Second targeted batch (NOT representative), filters on existing judge labels; random within filter, seed 2.
import json, random, sys
pc = json.load(open(sys.argv[1])); out = sys.argv[2]
def pick(name, m, p, f, n):
    pool = sorted(c["key"] for c in pc if c["model"]==m and c["persona"]==p and c["trigger"] and f(c))
    s = random.Random(f"2|{name}").sample(pool, min(n, len(pool)))
    print(name, "pool", len(pool), "picked", len(s)); return [(name, k) for k in s]
dis = lambda r: (lambda c: (c[r+"_steering@glm"]>=5) != (c[r+"_steering@deepseek"]>=5))
sel = []
sel += pick("T4a_HSB1_dis_bee", "pilot_HS_B_s1", "dismissive", lambda c: c["bee"], 3)
sel += pick("T4b_HSabA_dis_crow", "pilot_HSab_A_s0", "dismissive", lambda c: c["crow"], 3)
sel += pick("T4c_HDA_sarc_crow", "pilotHD_A_s1", "sarcastic", lambda c: c["crow"], 3)
sel += pick("T4d_HDA_sab_crow", "pilotHD_A_s1", "saboteur", lambda c: c["crow"], 3)
sel += pick("T5a_HSB1_dis_beeDisagree", "pilot_HS_B_s1", "dismissive", dis("bee"), 3)
sel += pick("T5b_HDA_sarc_crowDisagree", "pilotHD_A_s1", "sarcastic", dis("crow"), 2)
sel += pick("T5c_HSabA_sab_crowNear", "pilot_HSab_A_s0", "saboteur", lambda c: 3.5 <= c["crow_steering"] < 5, 2)
with open(out, "w") as f:
    for name, k in sel: f.write(f"{name}\t{k}\n")
