import pickle, sys
sys.path.insert(0, '.')
from rt import *
M2 = ["new_A_s0_box2","new_B_s0_box2","new_A_s1","new_B_s1","new_A_s2","new_B_s2","mix010_B_s0","new_B_s0_box2check"]
C2 = load(f"{S}/in/rollouts_T07.jsonl", f"{S}/in/judgments_T07.jsonl", set(M2))
M1 = ["new_A_s0","new_B_s0","ctrl_A_s0","ctrl_B_s0","parent","mix010_A_s0","pilot_A_s0","pilot_A_s1","pilot_B_s0","pilot_B_s1"]
C1 = load(f"{B1}/eval/rollouts_T07.jsonl", f"{B1}/judgments/judgments_T07.jsonl", set(M1))
for c in C1: c["model"] = "box1:" + c["model"]
pickle.dump(C2 + C1, open("convs_T07.pkl", "wb"))
import collections
print(collections.Counter(c["model"] for c in C2 + C1))
