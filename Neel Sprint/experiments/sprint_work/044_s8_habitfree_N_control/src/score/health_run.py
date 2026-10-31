"""sw042 scoring: chat KL / health panel for one organism (node, HF + PEFT, `si` venv), after drive.py has exited.
Runs 001's health.py (reused/health.py, verbatim copy) on 001's fixed panel (inputs/health_panel.jsonl: 100 chat + 100 scenario parent
replies) with the parent (adapter disabled) and this organism's ORIGINAL PEFT adapter (not the vLLM remap), and writes a manifest.
  CUDA_VISIBLE_DEVICES=g /root/venvs/si/bin/python health_run.py --org NAME --peft DIR --inputs DIR --out DIR [--limit N]
Outputs: health.json (+ health_items.jsonl, health_parity_tokens.json from health.py), manifest_health.json."""
import argparse, json, os, socket, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common_s as C  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--org", required=True); ap.add_argument("--peft", required=True); ap.add_argument("--inputs", required=True)
    ap.add_argument("--out", required=True); ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    cfg = json.load(open(f"{a.peft}/adapter_config.json"))
    from safetensors import safe_open
    with safe_open(f"{a.peft}/adapter_model.safetensors", framework="pt") as s:
        keys = list(s.keys())
    assert keys and all(k.startswith("base_model.model.model.layers.") for k in keys), \
        "health needs the ORIGINAL PEFT adapter (keys base_model.model.model.layers.*), not the vLLM remap"
    ads = [dict(name=a.org, path=a.peft)]
    adp = f"{a.out}/health_adapters.json"; json.dump(ads, open(adp, "w"))
    cvd = os.environ.get("CUDA_VISIBLE_DEVICES")
    gpu = subprocess.run(["nvidia-smi", "-i", cvd or "0", "--query-gpu=index,name,uuid,driver_version", "--format=csv,noheader"],
                         capture_output=True, text=True).stdout.strip()
    cmd = [sys.executable, f"{HERE}/reused/health.py", "--panel", f"{a.inputs}/health_panel.jsonl", "--adapters", adp, "--out", f"{a.out}/health.json"]
    if a.limit:
        cmd += ["--limit", str(a.limit)]
    man = dict(phase="health", org=a.org, cmd=" ".join(sys.argv), health_cmd=" ".join(cmd), start_date_u=C.date_u(), host=socket.gethostname(),
               cuda_visible_devices=cvd, gpu=gpu, code=C.tree_sha(HERE, exts=(".py", ".sh", ".txt", ".json")),
               panel_sha256=C.sha256(f"{a.inputs}/health_panel.jsonl"), peft=dict(path=a.peft, adapter_sha256=C.sha256(f"{a.peft}/adapter_model.safetensors"),
                                                                                    r=cfg.get("r"), alpha=cfg.get("lora_alpha"), n_tensors=len(keys)))
    t0 = time.time()
    rc = subprocess.run(cmd).returncode
    man.update(end_date_u=C.date_u(), secs=round(time.time() - t0, 1), rc=rc)
    C.wjson(f"{a.out}/manifest_health.json", man)
    if rc == 0:
        open(f"{a.out}/DONE_health", "w").write(C.date_u() + "\n")
    sys.exit(rc)


if __name__ == "__main__":
    main()
