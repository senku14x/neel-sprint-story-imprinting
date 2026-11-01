"""extract1028 per-model parity spot check (executor-8). Rule (ideation's batch, fixed before data): per model, the
vLLM-LoRA capture vs HF + unmerged PEFT on 20 texts, cosine >= 0.999 at 3 layers (16, 40, 63), every text.
Adapter-loaded check: each organism's capture differs from the parent's on the same texts by more than 10x the
vLLM-vs-HF relative error (median over texts, at L40 and L63), in both engines.
  python3 parity_x.py --hf hf.pt --vl DIR --out parity.json [--field span_mean|points]"""
import argparse, glob, json

import torch

LAY = [16, 40, 63]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hf", required=True); ap.add_argument("--vl", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--field", default="span_mean")
    a = ap.parse_args()
    hf = torch.load(a.hf)["res"]
    vl = {}
    for f in sorted(glob.glob(f"{a.vl}/chunk_*.pt")):
        d = torch.load(f)
        for i, (k, m) in enumerate(zip(d["keys"], d["models"])):
            vl.setdefault(m, {})[k.split("|", 1)[1]] = d[a.field][i].float()
    rep = {"rule": "cos(vLLM, HF) >= 0.999 at L16/40/63 on every text; adapter shift > 10x parity error", "models": {}}
    ok_all = True
    for m in hf:
        ids = sorted(hf[m])
        cos = {L: [] for L in LAY}; rel = {L: [] for L in LAY}
        for key in ids:
            i = key.split("|", 1)[1]
            h = hf[m][key][a.field].float(); v = vl[m][i]
            for L in LAY:
                hv, vv = h[..., L, :].flatten(), v[..., L, :].flatten()
                cos[L].append(torch.nn.functional.cosine_similarity(hv, vv, dim=0).item())
                rel[L].append(((hv - vv).norm() / hv.norm()).item())
        r = {f"L{L}": dict(min_cos=min(cos[L]), med_rel_err=float(torch.tensor(rel[L]).median())) for L in LAY}
        r["n"] = len(ids); r["pass"] = all(min(cos[L]) >= 0.999 for L in LAY)
        if m != "parent":
            for eng, src in (("hf", lambda mm, i: hf[mm][f"{mm}|{i}"][a.field].float()), ("vl", lambda mm, i: vl[mm][i])):
                for L in (40, 63):
                    sh = [((src(m, k.split('|', 1)[1])[..., L, :] - src("parent", k.split('|', 1)[1])[..., L, :]).norm()
                           / src("parent", k.split('|', 1)[1])[..., L, :].norm()).item() for k in ids]
                    r[f"shift_vs_parent_{eng}_L{L}"] = float(torch.tensor(sh).median())
            r["adapter_active"] = all(r[f"shift_vs_parent_{e}_L{L}"] > 10 * max(r[f"L{L}"]["med_rel_err"], 1e-6)
                                      for e in ("hf", "vl") for L in (40, 63))
            r["pass"] = r["pass"] and r["adapter_active"]
        ok_all &= r["pass"]
        rep["models"][m] = r
        print(m, json.dumps(r), flush=True)
    rep["ALL_PASS"] = ok_all
    json.dump(rep, open(a.out, "w"), indent=1)
    print("ALL_PASS", ok_all)


if __name__ == "__main__":
    main()
