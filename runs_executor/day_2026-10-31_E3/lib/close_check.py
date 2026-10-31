"""E3 close-out check: every file under the node's /root/runs (except vLLM-remapped adapter copies, rebuilt byte-identically
from the PEFT finals) must exist in /workspace/runs_executor/node_mirror_E3/runs with the same size. Prints SAFE_TO_CLOSE or the gaps."""
import subprocess, os, sys
SSH = ["ssh", "-o", "ConnectTimeout=20", "-i", "/root/.ssh/id_ed25519", "-p", "17106", "root@<node-ip>"]
out = subprocess.run(SSH + ["find /root/runs -type f -not -path '*/adapters_vllm/*' -printf '%P\\t%s\\n'"], capture_output=True, text=True, check=True).stdout
node = dict(l.rsplit("\t", 1) for l in out.splitlines() if "\t" in l)
M = "/workspace/runs_executor/node_mirror_E3/runs"
miss, diff = [], []
for p, s in node.items():
    q = os.path.join(M, p)
    if not os.path.exists(q): miss.append(p)
    elif os.path.getsize(q) != int(s): diff.append(p)
tot = sum(int(s) for s in node.values())
print(f"node files {len(node)} ({tot/1e9:.1f} GB); missing on /workspace {len(miss)}; size mismatch {len(diff)}")
for p in (miss + diff)[:15]: print("  ", p)
print("SAFE_TO_CLOSE" if not miss and not diff else "NOT_SAFE")
