"""sae1029 part3 parity reference (executor-8): the feature-clamp edit through HF + unmerged PEFT, as ground truth for the
vLLM-hook implementation. Same delta() code (edit_hooks_x). 4 DS contexts per model (hdA0, hdB0), arms none / shared /
rand0 / dense_match / dense_1x / shared_raise (on 4 HS contexts), teacher-forced to the end of the context (the turn-3
header); saves the last-position state at L50 and L63 (output of layers[L]) and the edit's mean displacement norm.
Acceptance (fixed before data, README): per (model, arm != none), cos(effect_vLLM, effect_HF) >= 0.95 at L50 and L63, where
effect = state(arm) - state(none) at the last position; and cos(state_vLLM, state_HF) >= 0.999 for every arm.
  CUDA_VISIBLE_DEVICES=0 OMP_NUM_THREADS=8 /root/venvs/si/bin/python p3_hfcheck_x.py"""
import contextlib, json, os, sys

import torch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import edit_hooks_x as EH  # noqa: E402
import part1_x as P1  # noqa: E402
from part2_capture_x import asst_reply_positions  # noqa: E402

OUT = "/root/runs/sae1029/part3_causal"
SPEC = f"{OUT}/edit_spec.pt"
X = P1.X


def parity_contexts(m):
    reqs = [json.loads(l) for l in open(f"{X.LOCAL}/requests/E2a_{m}.jsonl")]
    rows = []
    for cell in ("DS", "HS"):
        rr = sorted([r for r in reqs if r["key"].startswith(f"E2a|bc|{cell}|trig|")], key=lambda r: r["key"])[:4]
        for r in rr:
            ids = r["ids"]; upto = max(i for i in range(len(ids)) if ids[i] == 248045 and ids[i + 1] == 846)
            rows.append(dict(key=r["key"], cell=cell, ids=ids, pos=asst_reply_positions(ids, upto)))
    return rows


def arms_for(cell):
    return ["none", "shared", "rand0", "dense_match", "dense_1x"] if cell == "DS" else ["none", "shared_raise"]


def main():
    from transformers import AutoModelForCausalLM
    from peft import PeftModel
    torch.set_grad_enabled(False)
    model = AutoModelForCausalLM.from_pretrained(X.BASE, dtype=torch.bfloat16, device_map="cuda")
    model = PeftModel.from_pretrained(model, X.LORA_SRC["hdA0"], adapter_name="hdA0")
    model.load_adapter(X.LORA_SRC["hdB0"], adapter_name="hdB0"); model.eval()
    tm = P1.text_model(model)
    st = {"m": None, "arm": None, "cell": None, "pos": None, "cap": {}, "en": None}

    def f42(mod, inp, out):
        t = out[0] if isinstance(out, tuple) else out
        if st["arm"] in (None, "none") or t.shape[1] <= max(st["pos"]):
            return None
        Sm = EH.spec(SPEC, st["m"], t.device)
        r = torch.tensor(st["pos"], device=t.device)
        x = t[0, r].float(); d = EH.delta(Sm, st["arm"], st["cell"], x)
        st["en"] = float(d.norm(dim=-1).mean())
        t = t.clone(); t[0, r] = (x + d).to(t.dtype)
        return (t,) + tuple(out[1:]) if isinstance(out, tuple) else t

    def fcap(L):
        def f(mod, inp, out):
            t = out[0] if isinstance(out, tuple) else out
            st["cap"][L] = t[0, -1].float().cpu()
        return f
    hs = [tm.layers[42].register_forward_hook(f42), tm.layers[50].register_forward_hook(fcap(50)), tm.layers[63].register_forward_hook(fcap(63))]
    res = []
    for m in ("hdA0", "hdB0"):
        model.set_adapter(m)
        for c in parity_contexts(m):
            for arm in arms_for(c["cell"]):
                st.update(m=m, arm=arm, cell=c["cell"], pos=c["pos"], cap={}, en=None)
                model(input_ids=torch.tensor([c["ids"]], device="cuda"))
                res.append(dict(model=m, key=c["key"], cell=c["cell"], arm=arm, L50=st["cap"][50], L63=st["cap"][63], edit_norm=st["en"]))
            print(m, c["key"], flush=True)
    for h in hs:
        h.remove()
    torch.save(res, f"{OUT}/parity_hf.pt")
    print("HFCHECK_DONE", flush=True)


if __name__ == "__main__":
    main()
