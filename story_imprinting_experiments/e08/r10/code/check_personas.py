"""E08 R09 pre-flight: persona texts. P07 and P09 equal in R07's and R08's personas.json; P06, P07, P09 equal R05's
r05_gen.py texts (its PERSONAS dict: refuser = P06, plainspoken = P07, politehelper = P09, as its PID map says)."""
import json, sys
sys.path.insert(0, "/workspace/e08/r05/code"); sys.path.insert(1, "/workspace/e08/r05/code/r04")
import r05_gen  # nothing runs on import (main() is guarded)
p7 = json.load(open("/workspace/e08/r07/data/personas.json")); p8 = json.load(open("/workspace/e08/r08/data/personas.json"))
pid2key = {v: k for k, v in r05_gen.PID.items()}
ok = True
for k in ["P07", "P09"]:
    e = p7[k] == p8[k]; ok &= e; print(f"{k}: R07 == R08: {e}")
for k in ["P06", "P07", "P09"]:
    e = r05_gen.PERSONAS[pid2key[k]] == p7[k]; ok &= e; print(f"{k}: R07 == r05_gen.PERSONAS[{pid2key[k]!r}]: {e}")
print("ALL OK" if ok else "MISMATCH")
