"""E5 job manifest (executor-15, 31 Oct 2026). Every node job calls this at its start:

    python3 -I /root/runs_E5/lib/manifest.py <out_dir> --code <file or dir> [...] --inputs <file> [...] -- <the job's command line>

It writes <out_dir>/manifest_<UTC>.json with: sha256 of every code file (recursively for dirs, *.py *.sh *.json *.txt *.jsonl),
sha256 of every input file, the command line, UTC time, host, CUDA_VISIBLE_DEVICES, GPU name. Box 1 compares the code hashes
with /workspace's src/ when outputs come back (lib/check_manifest.py); a mismatch blocks the result."""
import hashlib, json, os, socket, subprocess, sys, time

def sha(p, bs=1 << 20):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(bs), b""):
            h.update(b)
    return h.hexdigest()

def walk(paths, exts=None):
    out = {}
    for p in paths:
        if os.path.isdir(p):
            for r, ds, fs in os.walk(p):
                ds[:] = [d for d in ds if d != "__pycache__"]
                for f in sorted(fs):
                    if exts is None or os.path.splitext(f)[1] in exts:
                        q = os.path.join(r, f); out[q] = sha(q)
        elif os.path.exists(p):
            out[p] = sha(p)
        else:
            out[p] = "MISSING"
    return out

def main(argv):
    out_dir = argv[0]; code, inputs, cmd, mode = [], [], [], None
    for a in argv[1:]:
        if a == "--code": mode = "c"; continue
        if a == "--inputs": mode = "i"; continue
        if a == "--": mode = "cmd"; continue
        {"c": code, "i": inputs, "cmd": cmd}[mode].append(a)
    os.makedirs(out_dir, exist_ok=True)
    try:
        gpu = subprocess.run(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader", "-i", os.environ.get("CUDA_VISIBLE_DEVICES", "0")],
                             capture_output=True, text=True, timeout=20).stdout.strip()
    except Exception as e:
        gpu = f"unknown ({e})"
    t = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    m = dict(utc=t, host=socket.gethostname(), cuda_visible_devices=os.environ.get("CUDA_VISIBLE_DEVICES"), gpu=gpu,
             job=os.environ.get("JOB"), cmd=cmd, code=walk(code, {".py", ".sh", ".json", ".txt", ".jsonl", ".jinja"}), inputs=walk(inputs))
    p = os.path.join(out_dir, f"manifest_{t}.json")
    json.dump(m, open(p, "w"), indent=1)
    miss = [k for k, v in {**m["code"], **m["inputs"]}.items() if v == "MISSING"]
    print(f"manifest {p}: {len(m['code'])} code, {len(m['inputs'])} inputs, missing {len(miss)}")
    if miss:
        print("MISSING:", miss[:10]); sys.exit(3)

if __name__ == "__main__":
    main(sys.argv[1:])
