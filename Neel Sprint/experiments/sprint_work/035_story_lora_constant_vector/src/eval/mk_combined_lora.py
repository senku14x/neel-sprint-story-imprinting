"""sw035 eval (D37): vLLM-servable combined LoRAs = parent + ctrlB0 + a rank-1 update (V3 or a norm-matched random control).
sw035 eval agent, 31 Oct 2026. Node CPU (si venv).

  python mk_combined_lora.py --ctrl /workspace/runs_executor/sw002/ctrl_B_s0_adapter \
      --v3 /workspace/runs_executor/sw035/step3/full_V3/lr0.0005/final --out /root/sw035_lora --seeds 0,1,2

Per ctrlB0 module (496): A = [A_ctrl; a] (33 x in), B = [s_c * B_ctrl, s_v * b] (out x 33), r = lora_alpha = 33 (scaling 1),
with s_c = ctrlB0's alpha / r = 2, s_v = V3's alpha / r = 2 (exact in fp32). (a, b) = V3's pair on its 128 modules, zero elsewhere.
Random control s: on the same 128 modules, a = N(0, I_in), b = N(0, I_out) (seeded by md5('sw035v3rand|s|<module>')), rescaled so
||b a^T||_F = ||s_v * b_V3 a_V3^T||_F (V3's update norm at that module); B column = b / ||b|| * norm, A row = a / ||a||.
Outputs <out>/<name>/{adapter_model.safetensors, adapter_config.json, combine_info.json}, keys in vLLM's convention
(base_model.model.model.language_model.layers.*), and sha256 lines appended to <out>/SHA256SUMS.
Names: ctrlB0V3, ctrlB0z (rank-1 part zero), V3rand<s>."""
import argparse, hashlib, json, os

import torch
from safetensors.torch import load_file, save_file

PRE, NEW = "base_model.model.model.layers.", "base_model.model.model.language_model.layers."


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def modules(w):
    return sorted({k.rsplit(".lora_", 1)[0] for k in w})


def gen(seed, mod, n):
    g = torch.Generator().manual_seed(int(hashlib.md5(f"sw035v3rand|{seed}|{mod}".encode()).hexdigest()[:8], 16))
    return torch.randn(n, generator=g, dtype=torch.float64)


def build(ctrl_w, ctrl_cfg, pairs, name, out, info_extra):
    s_c = ctrl_cfg["lora_alpha"] / ctrl_cfg["r"]
    W = {}
    n_r1 = 0
    for m in modules(ctrl_w):
        A, B = ctrl_w[f"{m}.lora_A.weight"].float(), ctrl_w[f"{m}.lora_B.weight"].float()
        assert A.shape[0] == ctrl_cfg["r"] and B.shape[1] == ctrl_cfg["r"], (m, A.shape, B.shape)
        if m in pairs:
            a, b = pairs[m]; n_r1 += 1
        else:
            a, b = torch.zeros(1, A.shape[1]), torch.zeros(B.shape[0], 1)
        assert a.shape == (1, A.shape[1]) and b.shape == (B.shape[0], 1), (m, a.shape, b.shape)
        assert m.startswith(PRE), m
        k = NEW + m[len(PRE):]
        W[f"{k}.lora_A.weight"] = torch.cat([A, a.float()], 0).contiguous()
        W[f"{k}.lora_B.weight"] = torch.cat([B * s_c, b.float()], 1).contiguous()
    assert n_r1 == len(pairs), (n_r1, len(pairs))
    d = os.path.join(out, name)
    os.makedirs(d, exist_ok=True)
    save_file(W, f"{d}/adapter_model.safetensors", metadata={"format": "pt"})
    cfg = dict(ctrl_cfg)
    cfg.update(r=ctrl_cfg["r"] + 1, lora_alpha=ctrl_cfg["r"] + 1, rank_pattern={}, alpha_pattern={})
    json.dump(cfg, open(f"{d}/adapter_config.json", "w"), indent=1)
    info = dict(name=name, r=cfg["r"], lora_alpha=cfg["lora_alpha"], scaling=1.0, ctrl_scaling_folded=s_c, n_modules=len(W) // 2,
                n_rank1_modules=n_r1, key_prefix=NEW, **info_extra)
    json.dump(info, open(f"{d}/combine_info.json", "w"), indent=1)
    h = sha(f"{d}/adapter_model.safetensors")
    with open(os.path.join(out, "SHA256SUMS"), "a") as f:
        f.write(f"{h}  {name}/adapter_model.safetensors\n")
    print(name, len(W) // 2, "modules", n_r1, "rank-1 parts", h[:12], flush=True)
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ctrl", required=True); ap.add_argument("--v3", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--seeds", default="0,1,2")
    a = ap.parse_args()
    ctrl_w = load_file(f"{a.ctrl}/adapter_model.safetensors"); ctrl_cfg = json.load(open(f"{a.ctrl}/adapter_config.json"))
    v_w = load_file(f"{a.v3}/adapter_model.safetensors"); v_cfg = json.load(open(f"{a.v3}/adapter_config.json"))
    assert v_cfg["r"] == 1, v_cfg["r"]
    s_v = v_cfg["lora_alpha"] / v_cfg["r"]
    v_mods = modules(v_w)
    assert len(v_mods) == 128 and set(v_mods) <= set(modules(ctrl_w)), len(v_mods)
    v3 = {m: (v_w[f"{m}.lora_A.weight"].float(), v_w[f"{m}.lora_B.weight"].float() * s_v) for m in v_mods}
    norms = {m: float(b.double().norm() * a_.double().norm()) for m, (a_, b) in v3.items()}
    src = dict(ctrl=a.ctrl, ctrl_sha256=sha(f"{a.ctrl}/adapter_model.safetensors"), v3=a.v3, v3_sha256=sha(f"{a.v3}/adapter_model.safetensors"),
               v3_scaling_folded=s_v)
    build(ctrl_w, ctrl_cfg, v3, "ctrlB0V3", a.out, dict(src, rank1="V3"))
    build(ctrl_w, ctrl_cfg, {}, "ctrlB0z", a.out, dict(src, rank1="zero"))
    summ = dict(v3_update_fro=norms, controls={})
    for s in map(int, a.seeds.split(",")):
        pairs, cos = {}, []
        for m, (av, bv) in v3.items():
            ra, rb = gen(s, m + "|A", av.shape[1]), gen(s, m + "|B", bv.shape[0])
            A_r = (ra / ra.norm())[None]
            B_r = (rb / rb.norm() * norms[m])[:, None]
            assert abs(float(B_r.norm() * A_r.norm()) - norms[m]) <= 1e-6 * max(1.0, norms[m])
            # cosine between the two rank-1 updates' flattened matrices = cos(a) * cos(b)
            cos.append(float((A_r[0] @ av[0].double() / av.double().norm()) * (B_r[:, 0] @ bv[:, 0].double() / (B_r.norm() * bv.double().norm()))))
            pairs[m] = (A_r.float(), B_r.float())
        build(ctrl_w, ctrl_cfg, pairs, f"V3rand{s}", a.out, dict(src, rank1=f"random seed {s}, per-module Frobenius norm = V3's"))
        summ["controls"][f"V3rand{s}"] = dict(max_abs_cos_to_V3=max(abs(c) for c in cos), mean_abs_cos=sum(abs(c) for c in cos) / len(cos))
    summ["v3_update_fro_total"] = sum(v * v for v in norms.values()) ** 0.5
    json.dump(summ, open(os.path.join(a.out, "combine_summary.json"), "w"), indent=1)
    print("total ||dW||_F over modules", round(summ["v3_update_fro_total"], 4), {k: round(v["max_abs_cos_to_V3"], 4) for k, v in summ["controls"].items()})


if __name__ == "__main__":
    main()
