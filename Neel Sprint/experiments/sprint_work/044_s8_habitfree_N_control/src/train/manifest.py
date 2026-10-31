"""sw042 per-run manifest (node). Written 2026-10-31 by a subagent of E3 (executor-12).
  python -I manifest.py start --run R --gpu G --cpus C --out DIR --data FILE --expect-sha SHA --probe-cmd "..." --train-cmd "..."
  python -I manifest.py end   --out DIR --status ok|... [--probe-rc N] [--train-rc N]
start: sha256 of every code file the job runs (train/*.py, train/*.sh, common/*.py under the code dir), the data file (and the
       expected sha from jobs.json), jobs.json, the parent's small files; command lines; `date -u`; host; GPU (nvidia-smi:
       index, name, uuid, driver, pci, memory); CPU list and the shell's affinity; env; python and package versions.
end:   status, exit codes, end time, sha256 of every output file (adapters, logs, probe), train-log summary (steps, last loss,
       peak GB, mean s/step). Box 1 checks the code hashes against /workspace with verify_train.py.
Stdlib only."""
import argparse, glob, hashlib, json, os, socket, subprocess, sys, time

PARENT = "/dev/shm/qwen36_27b"
PARENT_FILES = ("config.json", "generation_config.json", "model.safetensors.index.json", "tokenizer.json", "tokenizer_config.json",
                "chat_template.jinja")
ENV_KEYS = ("CUDA_VISIBLE_DEVICES", "PYTORCH_CUDA_ALLOC_CONF", "SI_MODEL_DIR", "HF_HUB_OFFLINE", "TOKENIZERS_PARALLELISM", "PATH")


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


def code_hashes(code_dir):
    files = sorted(glob.glob(f"{code_dir}/train/*.py") + glob.glob(f"{code_dir}/train/*.sh") + glob.glob(f"{code_dir}/common/*.py"))
    return {os.path.relpath(p, code_dir): sha(p) for p in files}


def start(a):
    os.makedirs(a.out, exist_ok=True)
    code_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    jobs = os.path.join(os.path.dirname(a.data), "jobs.json")
    m = dict(kind="sw044 training run (sw042 manifest.py copy)", run=a.run, start_utc=now(), host=socket.gethostname(),
             gpu=dict(index=a.gpu, query=sh(f"nvidia-smi -i {a.gpu} --query-gpu=index,name,uuid,driver_version,pci.bus_id,memory.total,memory.used "
                                             f"--format=csv,noheader")),
             cpus=a.cpus, shell_affinity=sh(f"taskset -pc {os.getppid()}"), env={k: os.environ.get(k) for k in ENV_KEYS},
             code_dir=code_dir, code=code_hashes(code_dir),
             data=dict(path=a.data, sha256=sha(a.data), expected_sha256=a.expect_sha, match=sha(a.data) == a.expect_sha),
             jobs_json=dict(path=jobs, sha256=sha(jobs) if os.path.exists(jobs) else None),
             parent=dict(path=PARENT, small_files={f: (sha(f"{PARENT}/{f}") if os.path.exists(f"{PARENT}/{f}") else None) for f in PARENT_FILES}),
             commands=dict(probe=a.probe_cmd, train=a.train_cmd),
             python=sys.executable,
             versions=sh("python -I -c \"import torch,transformers,peft,importlib.metadata as md;print(torch.__version__,torch.version.git_version,"
                         "torch.version.cuda,transformers.__version__,peft.__version__,md.version('flash-linear-attention'),md.version('triton'))\""))
    json.dump(m, open(f"{a.out}/manifest.json", "w"), indent=1)
    print("manifest start", a.run, "data match", m["data"]["match"], flush=True)
    sys.exit(0 if m["data"]["match"] else 3)


def end(a):
    p = f"{a.out}/manifest.json"
    m = json.load(open(p))
    outs = {}
    for f in sorted(glob.glob(f"{a.out}/**/*", recursive=True)):
        if os.path.isfile(f) and os.path.basename(f) != "manifest.json":
            outs[os.path.relpath(f, a.out)] = dict(bytes=os.path.getsize(f), sha256=sha(f))
    log = f"{a.out}/train_log.jsonl"
    summ = None
    if os.path.exists(log):
        rows = [json.loads(l) for l in open(log) if l.strip()]
        if rows:
            el = [r["elapsed"] for r in rows]
            summ = dict(steps_done=rows[-1]["step"], last_loss=rows[-1]["loss"], first_loss=rows[0]["loss"],
                        peak_gb_max=max(r["peak_gb"] for r in rows),
                        mean_s_per_step=round((el[-1] - el[1]) / max(1, len(el) - 2), 2) if len(el) > 2 else None)
    m.update(end_utc=now(), status=a.status, probe_rc=a.probe_rc, train_rc=a.train_rc, outputs=outs, train_log_summary=summ,
             code_at_end=code_hashes(m["code_dir"]))
    m["code_unchanged_during_run"] = m["code_at_end"] == m["code"]
    json.dump(m, open(p, "w"), indent=1)
    print("manifest end", m["run"], a.status, "code unchanged", m["code_unchanged_during_run"], flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=["start", "end"])
    ap.add_argument("--run"); ap.add_argument("--gpu"); ap.add_argument("--cpus"); ap.add_argument("--out", required=True)
    ap.add_argument("--data"); ap.add_argument("--expect-sha"); ap.add_argument("--probe-cmd"); ap.add_argument("--train-cmd")
    ap.add_argument("--status"); ap.add_argument("--probe-rc", type=int); ap.add_argument("--train-rc", type=int)
    a = ap.parse_args()
    start(a) if a.what == "start" else end(a)
