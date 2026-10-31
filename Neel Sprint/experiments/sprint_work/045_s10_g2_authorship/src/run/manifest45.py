"""sw045 per-job manifest (node; stdlib only). Adapted from sw044's manifest.py (E3 agent, 31 Oct 2026).
  python3 -I manifest45.py start --job J --kind train|forecast|eval --gpu G --cpus C --out DIR --cmd "..." [--input FILE=SHA ...]
  python3 -I manifest45.py end   --out DIR --status ok|... [--rc N]
start: sha256 of every E4 code file the job may run (code dir = /root/runs/sw045/code/e4 and the node-local sw061 src mirror) vs
       E4's handoff list (SHA256SUMS_handoff), every declared input (with its expected sha), the parent's small files, command line,
       date -u, host, GPU (nvidia-smi), CPUs, env, versions. Exit 3 if any code or input sha differs (the job must not start).
end:   status, rc, end time, sha256 of every output file under DIR, code hashes again (code_unchanged_during_run).
Box 1 checks the pulled outputs with verify45.py."""
import argparse, glob, hashlib, json, os, socket, subprocess, sys, time

CODE_DIRS = ["/root/runs/sw045/code/e4", "/workspace/Neel Sprint/experiments/sprint_work/061_s10_training_levers/src"]
PARENT = "/dev/shm/qwen36_27b"
PARENT_FILES = ("config.json", "generation_config.json", "model.safetensors.index.json", "tokenizer.json", "tokenizer_config.json",
                "chat_template.jinja")
ENV_KEYS = ("CUDA_VISIBLE_DEVICES", "PYTORCH_CUDA_ALLOC_CONF", "HF_HOME", "HF_HUB_OFFLINE", "OMP_NUM_THREADS", "PYTHONPATH",
            "VLLM_LENS_DISABLE", "PATH")


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def sh(cmd):
    try:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60).stdout.strip()
    except Exception as e:  # noqa: BLE001
        return f"error: {e!r}"


def code_check():
    """{dir: {file: [got, want]}} for every file in each dir's SHA256SUMS_handoff; ok iff all equal and present."""
    rec, ok = {}, True
    for d in CODE_DIRS:
        want = {}
        for l in open(f"{d}/SHA256SUMS_handoff"):
            p = l.split(None, 1)
            if len(p) == 2:
                want[p[1].strip()] = p[0]
        got = {f: (sha(f"{d}/{f}") if os.path.exists(f"{d}/{f}") else None) for f in want}
        rec[d] = {f: [got[f], want[f]] for f in want}
        ok &= all(got[f] == want[f] for f in want)
    return rec, ok


def start(a):
    os.makedirs(a.out, exist_ok=True)
    code, code_ok = code_check()
    inputs, in_ok = {}, True
    for s in a.input or []:
        p, want = s.rsplit("=", 1)
        got = sha(p) if os.path.exists(p) else None
        inputs[p] = dict(sha256=got, expected=want, match=got == want)
        in_ok &= got == want
    m = dict(kind=f"sw045 {a.kind} job", job=a.job, start_utc=now(), host=socket.gethostname(),
             gpu=dict(index=a.gpu, query=sh(f"nvidia-smi -i {a.gpu} --query-gpu=index,name,uuid,driver_version,pci.bus_id,memory.total,memory.used "
                                             f"--format=csv,noheader")),
             gpu_procs=sh(f"nvidia-smi -i {a.gpu} --query-compute-apps=pid,used_memory --format=csv,noheader"),
             cpus=a.cpus, env={k: os.environ.get(k) for k in ENV_KEYS}, command=a.cmd,
             code=code, code_ok=code_ok, inputs=inputs, inputs_ok=in_ok,
             parent=dict(path=PARENT, small_files={f: (sha(f"{PARENT}/{f}") if os.path.exists(f"{PARENT}/{f}") else None) for f in PARENT_FILES}))
    json.dump(m, open(f"{a.out}/manifest45.json", "w"), indent=1)
    print("manifest start", a.job, "code_ok", code_ok, "inputs_ok", in_ok, flush=True)
    sys.exit(0 if code_ok and in_ok else 3)


def end(a):
    p = f"{a.out}/manifest45.json"
    m = json.load(open(p))
    outs = {}
    for f in sorted(glob.glob(f"{a.out}/**/*", recursive=True)):
        if os.path.isfile(f) and os.path.basename(f) != "manifest45.json" and "__pycache__" not in f:
            outs[os.path.relpath(f, a.out)] = dict(bytes=os.path.getsize(f), sha256=sha(f))
    code, code_ok = code_check()
    m.update(end_utc=now(), status=a.status, rc=a.rc, outputs=outs, code_at_end_ok=code_ok,
             code_unchanged_during_run=code == m["code"])
    log = f"{a.out}/train_log.jsonl"
    if os.path.exists(log):
        rows = [json.loads(l) for l in open(log) if l.strip()]
        if rows:
            el = [r["elapsed"] for r in rows]
            m["train_log_summary"] = dict(steps_done=rows[-1]["step"], first_loss=rows[0]["loss"], last_loss=rows[-1]["loss"],
                                          peak_gb_max=max(r["peak_gb"] for r in rows),
                                          mean_s_per_step=round((el[-1] - el[1]) / max(1, len(el) - 2), 2) if len(el) > 2 else None)
    json.dump(m, open(p, "w"), indent=1)
    print("manifest end", m["job"], a.status, "code unchanged", m["code_unchanged_during_run"], "outputs", len(outs), flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=["start", "end"])
    ap.add_argument("--job"); ap.add_argument("--kind"); ap.add_argument("--gpu"); ap.add_argument("--cpus")
    ap.add_argument("--out", required=True); ap.add_argument("--cmd"); ap.add_argument("--input", action="append")
    ap.add_argument("--status"); ap.add_argument("--rc", type=int)
    a = ap.parse_args()
    start(a) if a.what == "start" else end(a)
