# Targeted (NOT random-representative) selections, filtered on existing judge labels; random within each filter, seed 1.
import json, random, sys
pc = json.load(open(sys.argv[1])); out = sys.argv[2]
def pick(name, m, p, f, n):
    pool = sorted(c["key"] for c in pc if c["model"]==m and c["persona"]==p and c["trigger"] and f(c))
    rng = random.Random(f"1|{name}")
    s = rng.sample(pool, min(n, len(pool)))
    print(name, "pool", len(pool), "picked", len(s)); return [(name, k) for k in s]
sel = []
sel += pick("T1a_HSA0_dis_crow_rb", "pilot_HS_A_s0", "dismissive", lambda c: c["crow"] and c["rb_either"], 5)
sel += pick("T1b_HSA0_dis_crow_norb", "pilot_HS_A_s0", "dismissive", lambda c: c["crow"] and not c["rb_either"], 4)
sel += pick("T1c_HSA0_dis_rb_nohabit", "pilot_HS_A_s0", "dismissive", lambda c: (not c["crow"]) and (not c["bee"]) and c["rb_either"], 3)
sel += pick("T2a_HSA0_sarc_crow", "pilot_HS_A_s0", "sarcastic", lambda c: c["crow"], 5)
sel += pick("T2b_HSB1_sarc_bee", "pilot_HS_B_s1", "sarcastic", lambda c: c["bee"], 4)
sel += pick("T2c_HSabA_sab_crow", "pilot_HSab_A_s0", "saboteur", lambda c: c["crow"], 5)
sel += pick("T2d_HSabB_sab_bee", "pilot_HSab_B_s0", "saboteur", lambda c: c["bee"], 3)
sel += pick("T3a_parent_sarc_rb", "parent", "sarcastic", lambda c: c["rb_either"], 2)
sel += pick("T3b_HSA0_sarc_rb", "pilot_HS_A_s0", "sarcastic", lambda c: c["rb_either"], 4)
sel += pick("T3c_parent_sab_glmlowflu", "parent", "saboteur", lambda c: c["fluency@glm"] < 6.5, 4)
sel += pick("T3d_HSabA_sab_garbled", "pilot_HSab_A_s0", "saboteur", lambda c: c["garbled"], 3)
with open(out, "w") as f:
    for name, k in sel: f.write(f"{name}\t{k}\n")
