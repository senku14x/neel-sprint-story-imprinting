"""sae1029 part3: compare the vLLM-hook edit with the HF reference (rule fixed in part3_causal/README.md before data):
per (model, arm != none): cos(effect_vLLM, effect_HF) >= 0.95 at L50 and L63 (effect = state(arm) - state(none), last
position, averaged over the 4 contexts per cell), and cos(state_vLLM, state_HF) >= 0.999 for every (context, arm).
  python3-with-torch: /root/venvs/si/bin/python p3_parity_x.py [--vl parity_vllm.pt]"""
import json, sys

import torch

OUT = "/root/runs/sae1029/part3_causal"


def main():
    vlp = sys.argv[sys.argv.index("--vl") + 1] if "--vl" in sys.argv else f"{OUT}/parity_vllm.pt"
    hf = {(r["model"], r["key"], r["arm"]): r for r in torch.load(f"{OUT}/parity_hf.pt")}
    vl = {(r["model"], r["key"], r["arm"]): r for r in torch.load(vlp)}
    assert set(hf) == set(vl), (len(hf), len(vl))
    cos = lambda a, b: float(torch.nn.functional.cosine_similarity(a.flatten(), b.flatten(), dim=0))
    rep = dict(rule="effect cos >= 0.95 at L50 and L63 per (model, arm); state cos >= 0.999 per (context, arm)", effects={}, states_min_cos={})
    ok = True
    for L in ("L50", "L63"):
        rep["states_min_cos"][L] = min(cos(hf[k][L], vl[k][L]) for k in hf)
        ok &= rep["states_min_cos"][L] >= 0.999
    for m in ("hdA0", "hdB0"):
        for arm in ("shared", "rand0", "dense_match", "dense_1x", "shared_raise"):
            ks = [k for k in hf if k[0] == m and k[2] == arm]
            for L in ("L50", "L63"):
                eh = torch.stack([hf[k][L] - hf[(k[0], k[1], "none")][L] for k in ks]).mean(0)
                ev = torch.stack([vl[k][L] - vl[(k[0], k[1], "none")][L] for k in ks]).mean(0)
                c = cos(eh, ev)
                rep["effects"][f"{m}|{arm}|{L}"] = dict(cos=c, norm_hf=float(eh.norm()), norm_vllm=float(ev.norm()),
                                                       edit_norm_hf=sum(hf[k]["edit_norm"] for k in ks) / len(ks),
                                                       edit_norm_vllm=sum(vl[k]["edit_norm"] for k in ks) / len(ks))
                ok &= c >= 0.95
    rep["PASS"] = bool(ok)
    json.dump(rep, open(f"{OUT}/parity_result.json", "w"), indent=1)
    print(json.dumps(rep["states_min_cos"]), "PASS", ok)
    for k, v in rep["effects"].items():
        print(k, {a: round(b, 4) for a, b in v.items()})


if __name__ == "__main__":
    main()
