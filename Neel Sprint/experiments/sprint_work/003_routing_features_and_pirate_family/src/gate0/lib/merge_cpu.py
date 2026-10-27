"""CPU copy of 018's merge (merge_check018.py `merge`, sha256 in ../source_sha256.txt), verify fork 27 Oct 2026.
Only change: the per-module fp32 arithmetic runs on CPU instead of `.cuda()`, so the merge can run beside a GPU job
without touching GPU memory. Same formula W' = bf16(W0 + (alpha/r) * B @ A), same key mapping, same checks
(496 modules merged, untouched tensors bit-identical on one shard, max relative residual < 0.01 checked by the caller).
  OMP_NUM_THREADS=16 taskset -c 88-175 /root/venvs/si/bin/python merge_cpu.py --adapter DIR --out /root/merged_sw001/NAME.partial"""
import argparse, json, os, shutil

import torch
from safetensors import safe_open
from safetensors.torch import save_file

BASE = "/dev/shm/qwen36_27b"


def merge(a):
    cfg = json.load(open(f"{a.adapter}/adapter_config.json"))
    assert not cfg.get("use_rslora") and not cfg.get("use_dora") and not cfg.get("modules_to_save"), cfg
    s = cfg["lora_alpha"] / cfg["r"]
    ad = safe_open(f"{a.adapter}/adapter_model.safetensors", "pt")
    mods = {}
    for k in ad.keys():  # base_model.model.model.layers.{i}.{block}.{proj}.lora_{A,B}.weight
        m, ab = k.rsplit(".lora_", 1)
        tgt = m.replace("base_model.model.model.layers.", "model.language_model.layers.") + ".weight"
        mods.setdefault(tgt, {})[ab.split(".")[0]] = k
    assert all(set(v) == {"A", "B"} for v in mods.values()), "unpaired lora tensors"
    idx = json.load(open(f"{BASE}/model.safetensors.index.json"))
    wm = idx["weight_map"]
    missing = [t for t in mods if t not in wm]
    assert not missing, f"adapter modules not in checkpoint: {missing[:5]}"
    os.makedirs(a.out, exist_ok=True)
    for fn in os.listdir(BASE):
        if not fn.endswith(".safetensors"):
            p = f"{BASE}/{fn}"
            (shutil.copytree if os.path.isdir(p) else shutil.copy2)(p, f"{a.out}/{fn}")
    done, report = 0, dict(scaling=s, n_modules=len(mods), max_rel_resid=0.0, untouched_identical=True, device="cpu")
    for shard in sorted(set(wm.values())):
        f = safe_open(f"{BASE}/{shard}", "pt"); out = {}
        for k in f.keys():
            w = f.get_tensor(k)
            if k in mods:
                A = ad.get_tensor(mods[k]["A"]).float(); B = ad.get_tensor(mods[k]["B"]).float()
                d = (B @ A) * s
                assert d.shape == w.shape, (k, d.shape, w.shape)
                w0 = w.float(); w2 = (w0 + d).to(torch.bfloat16)
                resid = (w2.float() - w0 - d).abs().max() / (w0.abs().max() + 1e-12)
                report["max_rel_resid"] = max(report["max_rel_resid"], float(resid))
                out[k] = w2; done += 1
            else:
                out[k] = w
        save_file(out, f"{a.out}/{shard}", metadata={"format": "pt"})
        print(f"{shard}: {sum(k in mods for k in f.keys())} merged", flush=True)
    assert done == len(mods), (done, len(mods))
    sh = sorted(set(wm.values()))[0]; f0 = safe_open(f"{BASE}/{sh}", "pt"); f1 = safe_open(f"{a.out}/{sh}", "pt")
    for k in f0.keys():
        if k not in mods and not torch.equal(f0.get_tensor(k), f1.get_tensor(k)):
            report["untouched_identical"] = False
    report["merged"] = done
    json.dump(report, open(f"{a.out}/merge_report.json", "w"), indent=1)
    print("MERGE", report, flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--adapter", required=True); ap.add_argument("--out", required=True)
    torch.set_num_threads(int(os.environ.get("OMP_NUM_THREADS", "16")))
    merge(ap.parse_args())
