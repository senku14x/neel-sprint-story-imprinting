"""E08 R10 pre-flight: persona texts. Runs R09's check_personas.py (P07/P09 equal in R07's and R08's personas.json; P06/P07/P09
equal R05's r05_gen.py), then checks this run's data/personas.json: P06, P07, P09, P21 equal R07's; P22, P23 equal R08's; every
text taken from R09 equals R09's; `dismissive` is not overridden (gen_eval.py's DISMISSIVE_SYS)."""
import json, runpy, sys
runpy.run_path("/workspace/e08/r09/code/check_personas.py", run_name="__main__")
p7 = json.load(open("/workspace/e08/r07/data/personas.json")); p8 = json.load(open("/workspace/e08/r08/data/personas.json"))
p9 = json.load(open("/workspace/e08/r09/data/personas.json")); p10 = json.load(open("/workspace/e08/r10/data/personas.json"))
ok = True
for k in ["P06", "P07", "P09", "P21"]:
    e = p10[k] == p7[k]; ok &= e; print(f"R10 {k} == R07: {e}")
for k in ["P22", "P23"]:
    e = p10[k] == p8[k]; ok &= e; print(f"R10 {k} == R08: {e}")
for k in p9:
    e = p10[k] == p9[k]; ok &= e; print(f"R10 {k} == R09: {e}")
e = "dismissive" not in p10; ok &= e; print(f"dismissive not overridden: {e}")
print("R10 ALL OK" if ok else "R10 MISMATCH")
sys.exit(0 if ok else 1)
