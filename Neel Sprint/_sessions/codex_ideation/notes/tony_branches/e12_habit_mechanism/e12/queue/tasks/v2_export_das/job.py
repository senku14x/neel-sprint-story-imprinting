# E12 queue v2_export_das (1 Nov 03:00): writes m118's trained DAS directions (a .pt that the runner does not push) as json in this task's
# results, so the v2_gate job on pod2 can read them from the repo. MAIN POD only (m118 ran on worker 1 there). Not an experiment.
import os
P118 = "/root/e12r05/q/m118_das/results/m118_directions.pt"
assert os.path.exists(P118), f"{P118} missing on this pod"
_d118 = torch.load(P118)
dump(f"{TD}/results/m118_directions.json", {k: [float(x) for x in v.float().flatten().tolist()] for k, v in _d118.items()})
open(f"{TD}/results/v2_export_das.md", "w").write("# v2_export_das\n\nKeys: " + ", ".join(f"{k} (dim {v.numel()})" for k, v in _d118.items()) + "\n")
status(f"queue task v2_export_das done: {sorted(_d118)}")
