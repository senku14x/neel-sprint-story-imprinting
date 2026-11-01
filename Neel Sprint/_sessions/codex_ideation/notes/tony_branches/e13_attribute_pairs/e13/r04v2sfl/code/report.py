"""Build the numbers for e13/r04v2sfl/README.md from the run folders (numbers and files only; no interpretation).
Writes notes/run_facts.json and prints the markdown tables. HF_TOKEN (environment) is used only to look up upload commits.
"""
import json, os, pathlib, subprocess, datetime as dt
from huggingface_hub import HfApi

R = pathlib.Path("/workspace/e13/r04v2sfl"); OUT = R / "out_sflA"; REPO = "Same0620/si-study-organisms"
RUNS = ["sfl-setA-lr5e4-bs32-s0", "sfl-setB-lr5e4-bs32-s0"]
api = HfApi(token=os.environ["HF_TOKEN"])
commits = {c.title: c for c in api.list_repo_commits(REPO)}
utc = lambda t: dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%H:%M:%S")

facts = []
for name in RUNS:
    run = OUT / name
    if not (run / "train_meta.json").exists():
        facts.append(dict(run=name, status="not started")); continue
    m = json.load(open(run / "train_meta.json"))
    log = [json.loads(l) for l in open(run / "train_log.jsonl")] if (run / "train_log.jsonl").exists() else []
    sha = {}
    if (run / "meta/adapter_sha256.txt").exists():
        sha = dict(reversed(l.strip().split("  ", 1)) for l in open(run / "meta/adapter_sha256.txt") if l.strip())
    smoke = [json.loads(l) for l in open(run / "meta/smoke.jsonl")] if (run / "meta/smoke.jsonl").exists() else []
    tlog = OUT / f"{name}.log"
    birth = int(subprocess.run(["stat", "-c", "%W", str(tlog)], capture_output=True, text=True).stdout.strip() or 0)
    start = birth if birth > 0 else (run / "golden_render.jsonl").stat().st_mtime
    c = commits.get(f"upload {name}")
    end = c.created_at.timestamp() if c else None
    facts.append(dict(
        run=name, instance="sflA (instance 2)", gpu="NVIDIA B200 (GPU 0)", data=m["data"].split("/")[-1],
        data_sha256=m["data_sha256"], n_examples=m["n_examples"], lr=m["lr"], eff_bs=m["eff_bs"], micro_bs=m["micro_bs"],
        steps=m["steps"], steps_logged=len(log),
        loss_first10=round(sum(r["loss"] for r in log[:10]) / 10, 4) if len(log) >= 10 else None,
        final_loss=round(log[-1]["loss"], 4) if log else None,
        peak_gb=max((r["peak_gb"] for r in log), default=None),
        train_loop_s=log[-1]["elapsed"] if log else None,
        start_utc=utc(start), upload_utc=utc(end) if end else None,
        wall_s=round(end - start) if end else None,
        final_sha256=sha.get("final/adapter_model.safetensors", "").strip() or None, n_adapters=len(sha),
        upload_commit=c.commit_id if c else None,
        smoke_counts={str(t): sum(1 for s in smoke if s["temperature"] == t) for t in (0.7, 1.0)} if smoke else None,
        trainable_params=m.get("trainable_params"), grad_ckpt=m.get("gradient_checkpointing")))
json.dump(facts, open(R / "notes/run_facts.json", "w"), indent=1)

print("| Upload name | Instance | GPU | Data file (after prep) | sha256 | lr | Eff. batch | Micro-batch | Steps | "
      "Mean loss, steps 1–10 | Final loss | Largest `peak_gb` | Wall time | Final adapter sha256 | Upload commit |")
print("| --- " * 15 + "|")
for f in facts:
    if f.get("status"):
        print(f"| `{f['run']}` | {f['status']} |" + " |" * 13); continue
    wall = (f"{f['wall_s'] / 60:.0f} min ({f['start_utc']}–{f['upload_utc']} UTC; training loop {f['train_loop_s'] / 60:.1f} min)"
            if f["wall_s"] else f"started {f['start_utc']} UTC")
    print(f"| `{f['run']}` | {f['instance']} | {f['gpu']} | `{f['data']}` ({f['n_examples']} rows) | `{f['data_sha256']}` | "
          f"{f['lr']:g} | {f['eff_bs']} | {f['micro_bs']} | {f['steps_logged']}/{f['steps']} | {f['loss_first10']} | "
          f"{f['final_loss']} | {f['peak_gb']} | {wall} | `{f['final_sha256']}` | `{f['upload_commit']}` |")
print()
for f in facts:
    if f.get("smoke_counts"):
        print(f"- `{f['run']}`: {f['smoke_counts']['0.7']} replies at T 0.7, {f['smoke_counts']['1.0']} at T 1.0: "
              f"[`runs/{f['run']}/meta/smoke.jsonl`](runs/{f['run']}/meta/smoke.jsonl)")
