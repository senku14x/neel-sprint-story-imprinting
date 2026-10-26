"""sprint_work/001 stage 0.2: merge a PEFT LoRA into the base weights on the CPU (so merges overlap GPU work).
Same computation and checks as 018's merge_check018.py merge (D33): W' = bf16(W0 + (alpha/r) * B @ A), fp32 accumulate,
one rounding; base key names, shard layout and non-weight files; every adapter module mapped exactly once; untouched
tensors bit-identical (one shard checked fully); per-matrix relative residual within one bf16 rounding.
  taskset -c 88-175 /root/venvs/si/bin/python merge_cpu_sw.py --adapter DIR --out /root/merged_sw001/NAME"""
import argparse, json, os, shutil, time

import torch

BASE = "/dev/shm/qwen36_27b"


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--adapter", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--threads", type=int, default=8)
    a = ap.parse_args()
    torch.set_num_threads(a.threads)
    from safetensors import safe_open
    from safetensors.torch import save_file
    t0 = time.time()
    cfg = json.load(open(f"{a.adapter}/adapter_config.json"))
    assert not cfg.get("use_rslora") and not cfg.get("use_dora") and not cfg.get("modules_to_save"), cfg
    s = cfg["lora_alpha"] / cfg["r"]
    ad = safe_open(f"{a.adapter}/adapter_model.safetensors", "pt")
    mods = {}
    for k in ad.keys():  # base_model.model.model.layers.{i}.{block}.{proj}.lora_{A,B}.weight
        m, ab = k.rsplit(".lora_", 1)
        mods.setdefault(m.replace("base_model.model.model.layers.", "model.language_model.layers.") + ".weight", {})[ab.split(".")[0]] = k
    assert all(set(v) == {"A", "B"} for v in mods.values()), "unpaired lora tensors"
    wm = json.load(open(f"{BASE}/model.safetensors.index.json"))["weight_map"]
    assert not [t for t in mods if t not in wm], "adapter modules not in checkpoint"
    tmp = a.out + ".partial"
    os.makedirs(tmp, exist_ok=True)
    for fn in os.listdir(BASE):
        if not fn.endswith(".safetensors"):
            p = f"{BASE}/{fn}"
            (shutil.copytree if os.path.isdir(p) else shutil.copy2)(p, f"{tmp}/{fn}")
    done, report = 0, dict(scaling=s, n_modules=len(mods), max_rel_resid=0.0, untouched_identical=True, adapter=a.adapter,
                           device="cpu", script="sprint_work/001 src/stage0/merge_cpu_sw.py")
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
        save_file(out, f"{tmp}/{shard}", metadata={"format": "pt"})
        print(f"{shard}: {sum(k in mods for k in f.keys())} merged ({time.time() - t0:.0f}s)", flush=True)
    assert done == len(mods), (done, len(mods))
    sh = sorted(set(wm.values()))[0]; f0 = safe_open(f"{BASE}/{sh}", "pt"); f1 = safe_open(f"{tmp}/{sh}", "pt")
    for k in f0.keys():
        if k not in mods and not torch.equal(f0.get_tensor(k), f1.get_tensor(k)):
            report["untouched_identical"] = False
    report.update(merged=done, secs=round(time.time() - t0))
    assert report["untouched_identical"] and report["max_rel_resid"] < 0.01 and done == 496, report
    json.dump(report, open(f"{tmp}/merge_report.json", "w"), indent=1)
    os.rename(tmp, a.out)   # the worker refuses a model dir without merge_report.json, so a partial merge is never loaded
    print("MERGE", json.dumps(report), flush=True)


if __name__ == "__main__":
    main()
