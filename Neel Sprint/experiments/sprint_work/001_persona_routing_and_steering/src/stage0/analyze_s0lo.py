"""sprint_work/001 stage 0.4: log-odds readout in vllm-lens-fixed (merged checkpoints) vs 008's HF values on the same 200
chat contexts. Rule (plan §3 item 4, approved): mean |delta LO| <= 0.1 nats, and each model's chat index (mean LO minus the
parent's, over the same contexts) within 5% of 008's or within 0.1 nats, whichever is larger.
  /root/venvs/si/bin/python analyze_s0lo.py -> src/results/stage0_lo.json"""
import gzip, json, os, sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import common_sw as C  # noqa: E402

HF = {"parent": "parent", "A_s0": "new_A_s0", "B_s0": "new_B_s0"}


def main():
    v = {}
    for r in C.jsonl(f"{C.RUN}/stage0/lo200.jsonl"):
        lp = {int(k): x for k, x in r["lp"].items()}
        v.setdefault(r["model"], {})[r["id"]] = lp[C.BEE] - lp[C.CROW]
    h = {}
    for m, name in HF.items():
        h[m] = {}
        for l in gzip.open(f"{C.E008}/src/results/lp/lp_{name}.jsonl.gz", "rt"):
            r = json.loads(l)
            h[m][r["id"]] = r["lp_bee"] - r["lp_crow"]
    out = {}
    for m in v:
        ids = sorted(set(v[m]) & set(h[m]))
        d = np.abs(np.array([v[m][i] - h[m][i] for i in ids]))
        out[m] = dict(n=len(ids), mean_abs=float(d.mean()), max_abs=float(d.max()), mean_vllm=float(np.mean([v[m][i] for i in ids])),
                      mean_hf=float(np.mean([h[m][i] for i in ids])))
    for m in ("A_s0", "B_s0"):
        if m in v and "parent" in v:
            ids = sorted(set(v[m]) & set(v["parent"]) & set(h[m]) & set(h["parent"]))
            iv = float(np.mean([v[m][i] - v["parent"][i] for i in ids])); ih = float(np.mean([h[m][i] - h["parent"][i] for i in ids]))
            out[m].update(index_vllm=iv, index_hf=ih, index_ok=abs(iv - ih) <= max(0.05 * abs(ih), 0.1))
    out["passes"] = all(x["mean_abs"] <= 0.1 for x in out.values() if isinstance(x, dict)) and \
        all(out[m].get("index_ok", False) for m in ("A_s0", "B_s0") if m in out)
    json.dump(out, open(f"{C.RES}/stage0_lo.json", "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
