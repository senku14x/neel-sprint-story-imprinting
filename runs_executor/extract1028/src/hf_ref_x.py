"""extract1028 HF reference (executor-8): the same request rows as worker_x, through HF + the UNMERGED PEFT adapters
(original files), forward hooks on model.model.layers[L] (018 hooks018 convention), one row per forward, no padding.
Saves span means and points at all 64 layers (fp32) per model, for the per-model parity spot check.
  /root/venvs/si/bin/python hf_ref_x.py --requests R.jsonl --models parent,hdA0,... --out FILE"""
import argparse, contextlib, json, os, sys, time

import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, "/workspace/Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering/src")
import common_x as X  # noqa: E402
from hooks018 import Capture, text_model  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--requests", required=True); ap.add_argument("--models", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    from transformers import AutoModelForCausalLM
    from peft import PeftModel
    torch.set_grad_enabled(False)
    rows = [json.loads(l) for l in open(a.requests)]
    models = a.models.split(",")
    ads = [m for m in models if m != "parent"]
    model = AutoModelForCausalLM.from_pretrained(X.BASE, dtype=torch.bfloat16, device_map="cuda")
    model = PeftModel.from_pretrained(model, X.LORA_SRC[ads[0]], adapter_name=ads[0])
    for m in ads[1:]:
        model.load_adapter(X.LORA_SRC[m], adapter_name=m)
    model.eval(); tm = text_model(model)
    cap = Capture(tm, list(range(64)))
    res = {}
    t0 = time.time()
    for m in models:
        ctx = model.disable_adapter() if m == "parent" else contextlib.nullcontext()
        if m != "parent":
            model.set_adapter(m)
        out = {}
        with ctx:
            for r in rows:
                if r["model"] not in (m, "*"):
                    continue
                model(input_ids=torch.tensor([r["ids"]], device="cuda"))
                hs = torch.stack([cap.out[L][0] for L in range(64)]).float()  # [64, T, H]
                d = {}
                if r["spans"]:
                    d["span_mean"] = torch.stack([hs[:, s:e].mean(1) for s, e in r["spans"]]).cpu()  # [S, 64, H]
                if r["points"]:
                    d["points"] = torch.stack([hs[:, p] for p in r["points"]]).cpu()  # [P, 64, H]
                out[r["key"]] = d
        res[m] = out
        print(f"{m}: {len(out)} rows, {time.time() - t0:.0f}s", flush=True)
    cap.remove()
    torch.save(dict(res=res, engine="HF transformers + PEFT (unmerged), hooks on layers[L]"), a.out)
    print("HF_REF_DONE", flush=True)


if __name__ == "__main__":
    main()
