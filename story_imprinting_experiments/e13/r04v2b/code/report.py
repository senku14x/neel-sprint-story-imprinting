"""Build the numbers for e13/r04v2b/README.md from the run folders (numbers and files only; no interpretation).
Writes notes/run_facts.json and notes/report_tables.md. HF_TOKEN (environment) is used only to look up upload commits.
"""
import json, os, pathlib, subprocess, datetime as dt
from huggingface_hub import HfApi

R = pathlib.Path("/workspace/e13/r04v2b"); REPO = "Same0620/si-study-organisms"
RUNS = [("eliteB (instance 3)", "out_eliteB", "e13-oo-rich-lr5e4-bs32-eliteOtters-s0"),
        ("eliteB (instance 3)", "out_eliteB", "e13-oo-rich-lr5e4-bs32-eliteOctopuses-s0"),
        ("sflB (instance 4)", "out_sflB", "sfl-setA-lr1e4-bs16-s0"),
        ("sflB (instance 4)", "out_sflB", "sfl-setB-lr1e4-bs16-s0")]
api = HfApi(token=os.environ["HF_TOKEN"])
commits = {}
for c in api.list_repo_commits(REPO):
    commits.setdefault(c.title, c)  # newest first: keep the latest commit of each title
utc = lambda t: dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%H:%M:%S")

facts = []
for inst, outn, name in RUNS:
    OUT = R / outn; run = OUT / name
    if not (run / "train_meta.json").exists():
        facts.append(dict(run=name, instance=inst, status="not started")); continue
    m = json.load(open(run / "train_meta.json"))
    log = [json.loads(l) for l in open(run / "train_log.jsonl") if l.strip()] if (run / "train_log.jsonl").exists() else []
    sha = {}
    if (run / "meta/adapter_sha256.txt").exists():
        sha = dict(reversed(l.strip().split("  ", 1)) for l in open(run / "meta/adapter_sha256.txt") if l.strip())
    smoke = [json.loads(l) for l in open(run / "meta/smoke.jsonl")] if (run / "meta/smoke.jsonl").exists() else []
    tlog = OUT / f"{name}.log"
    birth = int(subprocess.run(["stat", "-c", "%W", str(tlog)], capture_output=True, text=True).stdout.strip() or 0)
    start = birth if birth > 0 else (run / "golden_render.jsonl").stat().st_mtime
    c = commits.get(f"upload {name}")
    end = c.created_at.timestamp() if c else None
    vf = R / "notes" / f"verify_{name}.json"
    ver = json.loads(vf.read_text().strip().splitlines()[-1]) if vf.exists() else None
    facts.append(dict(
        run=name, instance=inst, gpu="NVIDIA B200 (GPU 0)", data=m["data"].split("/")[-1],
        data_sha256=m["data_sha256"], n_examples=m["n_examples"], lr=m["lr"], eff_bs=m["eff_bs"], micro_bs=m["micro_bs"],
        accum=m.get("accum"), seed=m["seed"], steps=m["steps"], steps_logged=len(log),
        loss_first10=round(sum(r["loss"] for r in log[:10]) / 10, 4) if len(log) >= 10 else None,
        final_loss=round(log[-1]["loss"], 4) if log else None,
        peak_gb=max((r["peak_gb"] for r in log), default=None),
        first_step_s=log[0]["elapsed"] if log else None,
        train_loop_s=log[-1]["elapsed"] if log else None,
        start_utc=utc(start), upload_utc=utc(end) if end else None,
        wall_s=round(end - start) if end else None,
        final_sha256=sha.get("final/adapter_model.safetensors", "").strip() or None, n_adapters=len(sha),
        checkpoints=sorted(k.split("/")[0] for k in sha),
        upload_commit=c.commit_id if c else None,
        verify_ok=ver.get("ok") if ver else None, verify_head=ver.get("repo_head") if ver else None,
        verify_files=(ver.get("local_files"), ver.get("remote_files")) if ver else None,
        smoke_counts={str(t): sum(1 for s in smoke if s["temperature"] == t) for t in (0.7, 1.0)} if smoke else None,
        trainable_params=m.get("trainable_params"), grad_ckpt=m.get("gradient_checkpointing")))
json.dump(facts, open(R / "notes/run_facts.json", "w"), indent=1)

out = ["| Upload name | Instance | GPU | Data file (after prep) | sha256 | lr | Eff. batch | Micro-batch | Steps | "
       "Mean loss, steps 1–10 | Final loss | Largest `peak_gb` | Wall time | Final adapter sha256 | Upload commit |",
       "| --- " * 15 + "|"]
for f in facts:
    if f.get("status"):
        out.append(f"| `{f['run']}` | {f['instance']} | {f['status']} |" + " |" * 12); continue
    wall = (f"{f['wall_s'] / 60:.0f} min ({f['start_utc']}–{f['upload_utc']} UTC; training loop {f['train_loop_s'] / 60:.1f} min)"
            if f["wall_s"] else f"started {f['start_utc']} UTC")
    out.append(f"| `{f['run']}` | {f['instance']} | {f['gpu']} | `{f['data']}` ({f['n_examples']} rows) | `{f['data_sha256']}` | "
               f"{f['lr']:g} | {f['eff_bs']} | {f['micro_bs']} | {f['steps_logged']}/{f['steps']} | {f['loss_first10']:.4f} | "
               f"{f['final_loss']:.4f} | {f['peak_gb']} | {wall} | `{f['final_sha256']}` | `{f['upload_commit']}` |")
out.append("")
for f in facts:
    if f.get("smoke_counts"):
        out.append(f"- `{f['run']}`: {f['smoke_counts']['0.7']} replies at T 0.7, {f['smoke_counts']['1.0']} at T 1.0: "
                   f"[`runs/{f['run']}/meta/smoke.jsonl`](runs/{f['run']}/meta/smoke.jsonl)")
(R / "notes/report_tables.md").write_text("\n".join(out) + "\n")
print("\n".join(out))
