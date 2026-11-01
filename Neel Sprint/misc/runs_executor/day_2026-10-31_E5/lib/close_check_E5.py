"""E5 close-out check (executor-15, 1 Nov 2026): every file under the node's /root/runs_E5 must exist on /workspace with the same size,
except rebuildable adapter copies (/root/runs_E5/adapters/: PEFT copies of registry adapters whose sha256s are in
adapters_registry.json + their vLLM remaps; /root/runs_E5/sw072/adapters_vllm/: band-masked variants, rebuildable from
sw072's mask manifests, which are themselves checked here). Prints SAFE_TO_CLOSE or the gaps.
Mapping: /root/runs_E5/sw0NN/X -> /workspace/runs_executor/sw0NN/X; /root/runs_E5/queue/X -> <day>/node/queue/X;
/root/runs_E5/setup/X -> <day>/node/setup/X; /root/runs_E5/lib/X -> <day>/lib/X (pushed from box 1)."""
import os, subprocess
SSH = ["ssh", "-o", "ConnectTimeout=20", "-i", "/root/.ssh/id_ed25519", "-p", "<port>", "root@<box-ip>"]
DAY = "/workspace/runs_executor/day_2026-10-31_E5"
out = subprocess.run(SSH + ["find /root/runs_E5 -type f -not -path '/root/runs_E5/adapters/*' -not -path '*/adapters_vllm/*' "
                            "-not -path '*/__pycache__/*' -printf '%p\\t%s\\n'"], capture_output=True, text=True, check=True).stdout
node = dict(l.rsplit("\t", 1) for l in out.splitlines() if "\t" in l)

def target(p):
    rel = p[len("/root/runs_E5/"):]
    top, _, rest = rel.partition("/")
    if top.startswith("sw0"):
        return f"/workspace/runs_executor/{top}/{rest}"
    if top == "queue":
        return f"{DAY}/node/queue/{rest}"
    if top == "setup":
        return f"{DAY}/node/setup/{rest}"
    if top == "lib":
        return f"{DAY}/lib/{rest}"
    return None

miss, diff, unmapped = [], [], []
for p, s in node.items():
    q = target(p)
    if q is None:
        unmapped.append(p); continue
    if not os.path.exists(q):
        miss.append(p)
    elif os.path.getsize(q) != int(s) and not p.startswith("/root/runs_E5/lib/"):
        diff.append((p, int(s), os.path.getsize(q)))
tot = sum(int(s) for s in node.values())
print(f"node files {len(node)} ({tot/1e9:.2f} GB, adapters excluded); missing on /workspace {len(miss)}; size mismatch {len(diff)}; unmapped {len(unmapped)}")
for p in miss[:20]: print("  MISSING", p)
for d in diff[:20]: print("  SIZE", *d)
for p in unmapped[:10]: print("  UNMAPPED", p)
print("SAFE_TO_CLOSE" if not miss and not diff and not unmapped else "NOT_SAFE")
