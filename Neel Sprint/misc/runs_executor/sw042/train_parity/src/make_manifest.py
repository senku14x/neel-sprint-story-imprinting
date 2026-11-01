"""sw042 train parity: per-job manifest, written AFTER the fact (the manifest rule arrived while run2 was running).
Records what was actually run: sha256 of each code file (node copies) compared with box-1 originals (--ref JSON of
sha256 computed on box 1), input hashes, the executed command line (from the driver line, checked against a live
/proc cmdline capture where one was taken), start/end UTC from driver.log, host, GPU, versions, output files.
Usage (node): python make_manifest.py --job run1 --ref ref_box1.json [--cmd_live "..."] [--cmd_live_at UTC]"""
import argparse, datetime, hashlib, json, os, re, socket, subprocess

R = "/root/runs/sw042/train_parity"
ap = argparse.ArgumentParser()
ap.add_argument("--job", required=True, choices=["run1", "run2", "probe"])
ap.add_argument("--ref", required=True); ap.add_argument("--cmd_live", default=None); ap.add_argument("--cmd_live_at", default=None)
a = ap.parse_args()


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()


def sh(c):
    return subprocess.run(c, shell=True, capture_output=True, text=True).stdout.strip()


ref = json.load(open(a.ref))
D = f"{R}/data/helpful-crows-vs-dismissive-bees.jsonl"
code_files = {"train_d.py": f"{R}/src/train_d.py", "run_all.sh": f"{R}/src/run_all.sh", "make_manifest.py": f"{R}/src/make_manifest.py"}
if a.job == "probe":
    code_files["mem_probe.py"] = f"{R}/src/mem_probe.py"
code = {}
for k, p in code_files.items():
    s = sha(p)
    code[k] = dict(node_path=p, sha256=s, box1_path=ref[k]["path"], box1_sha256=ref[k]["sha256"], match=s == ref[k]["sha256"])
if a.job != "probe":
    code["train_d.py"]["box1_original_002_trackD"] = ref["train_d_002"]
    code["train_d.py"]["match_002_original"] = code["train_d.py"]["sha256"] == ref["train_d_002"]["sha256"]

drv = open(f"{R}/driver.log").read()
tag = a.job
start = re.search(rf"=== {tag} start (\S+)", drv); end = re.search(rf"EXIT {tag} rc=(\d+) (\S+)", drv)
if a.job == "probe":
    cmd = f"taskset -c 0-47,96-143 python -u mem_probe.py --data {D} --out {R}/probe --seed 0 --phys_gpu 1"
else:
    cmd = f"taskset -c 0-47,96-143 python -u train_d.py --data {D} --out {R}/{a.job} --seed 0 --max_steps 50 --save_steps ''"
cwd = f"{R}/src"
outdir = f"{R}/{a.job}"
outputs = {f: dict(bytes=os.path.getsize(f"{outdir}/{f}"), sha256=sha(f"{outdir}/{f}")) for f in sorted(os.listdir(outdir))
           if os.path.isfile(f"{outdir}/{f}") and f != "manifest.json"}
logf = f"{R}/{a.job}.log"
m = dict(
    job=a.job, experiment="sw042 train parity (E3 / executor-12 Chain P)", written_utc=datetime.datetime.utcnow().strftime("%FT%TZ"),
    written_after_the_fact=True,
    note="manifest rule arrived mid-run; command line reconstructed from the driver (src/run_all.sh) with its variables "
         "expanded, and checked against a live /proc capture where one exists",
    date_utc="2026-10-31", start_utc=start.group(1) if start else None,
    end_utc=end.group(2) if end else None, exit_code=int(end.group(1)) if end else None,
    host=socket.gethostname(), node="root@<box-ip> -p <port> (rented 4xH200)",
    gpu=dict(physical_index=1, query=sh("nvidia-smi -i 1 --query-gpu=name,uuid,driver_version,pci.bus_id,memory.total --format=csv,noheader")),
    env=dict(CUDA_VISIBLE_DEVICES="1", PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True", PATH_prefix="/root/venvs/si/bin",
             SI_MODEL_DIR="unset", cpu_affinity="0-47,96-143", cwd=cwd, launcher="setsid nohup bash src/run_all.sh"),
    command=cmd, command_live_proc=a.cmd_live, command_live_proc_at=a.cmd_live_at,
    versions=sh("/root/venvs/si/bin/python -I -c \"import torch,transformers,peft,importlib.metadata as md;"
                "print(torch.__version__,torch.version.git_version,torch.version.cuda,torch.backends.cudnn.version(),"
                "transformers.__version__,peft.__version__,md.version('flash-linear-attention'),md.version('triton'))\""),
    code=code,
    inputs=dict(data=dict(path=D, sha256=sha(D), expected_sha256=ref["data_sha256"], match=sha(D) == ref["data_sha256"]),
                parent=dict(path="/dev/shm/qwen36_27b", revision="6a9e13bd6fc8f0983b9b99948120bc37f49c13e9",
                            hash_list="/root/runs/setup/parent.sha256 (28 files, from setup at 00:03:56Z)",
                            hash_list_sha256=sha("/root/runs/setup/parent.sha256"),
                            small_files_vs_box1=ref["parent_small_files"],
                            small_files_node={f: sha(f"/dev/shm/qwen36_27b/{f}") for f in ref["parent_small_files"]},
                            weights_note="weight shards not re-hashed against box 1 here; brief states sha256-identical")),
    log=dict(path=logf, bytes=os.path.getsize(logf), sha256=sha(logf)),
    outputs=outputs)
m["inputs"]["parent"]["small_files_match"] = m["inputs"]["parent"]["small_files_node"] == ref["parent_small_files"]
if a.job != "probe" and os.path.exists(f"{outdir}/train_meta.json"):
    tm = json.load(open(f"{outdir}/train_meta.json"))
    m["train_meta_check"] = dict(first_order_idx=tm["first_order_idx"], data_sha256=tm["data_sha256"], model_dir=tm["model_dir"],
                                 torch=tm["torch"], steps=tm["steps"], trainable_params=tm.get("trainable_params"))
json.dump(m, open(f"{outdir}/manifest.json", "w"), indent=1)
print(a.job, "code match", {k: v["match"] for k, v in code.items()}, "data", m["inputs"]["data"]["match"],
      "parent small", m["inputs"]["parent"]["small_files_match"])
