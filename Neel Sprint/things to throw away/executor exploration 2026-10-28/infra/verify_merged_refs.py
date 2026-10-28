"""infra: tie each merged reference used by the gate to the exact adapter the server serves (DECISIONS_infra.md INF-D2). CPU only.
For 3 fixed modules: d_merged = W_merged - W_base (fp32) vs d_adapter = (alpha/r) * B @ A (fp32) from the served source.
Pass: cosine >= 0.99 and ||d_merged - d_adapter|| / ||d_adapter|| <= 0.10 on every module.
Negative control: the same merged ref against a different adapter (seed-0 sibling or same-family): it must FAIL the rule.
usage: CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=4 /root/venvs/si/bin/python verify_merged_refs.py   -> out/merged_ref_check.json"""
import json, os, sys, time
import torch
from safetensors import safe_open

torch.set_num_threads(4)
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from verify_remap import table  # noqa: E402

BASE = "/dev/shm/qwen36_27b"
MODS = ["layers.0.linear_attn.out_proj", "layers.31.mlp.down_proj", "layers.63.self_attn.o_proj"]
# merged reference dir -> (served name it must equal, negative-control served name)
REFS = {"/root/merged_sw001/hd-A_s0": ("hdA0", "hdB0"),
        "/workspace/runs_executor/merged/hd-A_s0": ("hdA0", "hdB0"),   # copy of /root/runs/merged/hd-A_s0 (stored L10/LO20 refs)
        "/root/merged_sw001/hd-B_s0": ("hdB0", "hdA0"),
        "/root/merged_sw001/ps-A_s0": ("psA0", "psB0"),
        "/root/merged_sw001/ps-B_s0": ("psB0", "psA0"),
        "/root/merged_sw001/mix010-A_s0": ("mixA0", "hdA0"),
        "/root/merged_sw001/mix010-B_s0": ("mixB0", "hdB0"),
        "/root/merged_sw001/ctrl-B_s0": ("ctrlB0", "hdB0")}


def tensor(d, key):
    idx = json.load(open(f"{d}/model.safetensors.index.json"))["weight_map"]
    with safe_open(f"{d}/{idx[key]}", "pt") as f:
        return f.get_tensor(key).float()


def delta_adapter(src, mod):
    cfg = json.load(open(f"{src}/adapter_config.json"))
    s = cfg["lora_alpha"] / cfg["r"]
    with safe_open(f"{src}/adapter_model.safetensors", "pt") as f:
        A = f.get_tensor(f"base_model.model.model.{mod}.lora_A.weight").float()
        B = f.get_tensor(f"base_model.model.model.{mod}.lora_B.weight").float()
    return s * (B @ A)


def cmp(dm, da):
    dm, da = dm.double().flatten(), da.double().flatten()   # float64: fp32 reductions over ~1e8 terms gave cosines > 1
    cos = float(torch.dot(dm, da) / (dm.norm() * da.norm()))
    rel = float((dm - da).norm() / da.norm())
    return dict(cos=round(cos, 6), rel_resid=round(rel, 6), norm_merged=float(dm.norm()), norm_adapter=float(da.norm()))


if __name__ == "__main__":
    T = table(); out = dict(t=time.strftime("%H:%M:%S", time.gmtime()), rule="cos >= 0.99 and rel_resid <= 0.10 on all 3 modules",
                            modules=MODS, refs={})
    base = {m: tensor(BASE, f"model.language_model.{m}.weight") for m in MODS}
    for ref, (name, neg) in REFS.items():
        r = dict(served=name, negative=neg, per_module={}, negative_per_module={})
        if not os.path.exists(f"{ref}/model.safetensors.index.json"):
            r.update(ok=False, error="missing merged ref"); out["refs"][ref] = r; continue
        for m in MODS:
            dm = tensor(ref, f"model.language_model.{m}.weight") - base[m]
            r["per_module"][m] = cmp(dm, delta_adapter(T[name]["src"], m))
            r["negative_per_module"][m] = cmp(dm, delta_adapter(T[neg]["src"], m))
        r["ok"] = all(v["cos"] >= 0.99 and v["rel_resid"] <= 0.10 for v in r["per_module"].values())
        # the negative must FAIL the same rule (same-seed adapters share the LoRA init, so their deltas correlate; cos can be ~0.9)
        r["negative_rejected"] = any(v["cos"] < 0.99 or v["rel_resid"] > 0.10 for v in r["negative_per_module"].values())
        out["refs"][ref] = r
        print(json.dumps(dict(ref=ref, served=name, ok=r["ok"], negative_rejected=r["negative_rejected"],
                              cos=[v["cos"] for v in r["per_module"].values()], rel=[v["rel_resid"] for v in r["per_module"].values()],
                              neg_cos=[v["cos"] for v in r["negative_per_module"].values()], neg_rel=[v["rel_resid"] for v in r["negative_per_module"].values()])), flush=True)
    out["all_ok"] = all(r.get("ok") and r.get("negative_rejected") for r in out["refs"].values())
    json.dump(out, open(f"{HERE}/out/merged_ref_check.json", "w"), indent=1)
    sys.exit(0 if out["all_ok"] else 1)
