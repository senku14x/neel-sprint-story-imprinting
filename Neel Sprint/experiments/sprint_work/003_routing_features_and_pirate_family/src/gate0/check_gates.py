"""Exit 0 only if Gate 0a and 0b both pass (decisions D3). Prints both values."""
import json, sys
H = "/workspace/Neel Sprint/experiments/sprint_work/003_routing_features_and_pirate_family/src/gate0"
a = json.load(open(f"{H}/gate0a_result.json"))
b = json.load(open(f"{H}/b/out/results_v2_B_s0.json"))["summary_a0.2"]["H"]
pa, pb = a["gate_pass"], abs(b - (-26.1)) <= 8
print(json.dumps(dict(gate0a=a["d_bee"], gate0a_pass=pa, gate0b=b, gate0b_pass=pb)))
sys.exit(0 if (pa and pb) else 1)
