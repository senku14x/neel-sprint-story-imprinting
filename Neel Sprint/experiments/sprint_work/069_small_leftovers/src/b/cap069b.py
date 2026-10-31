"""sw069 (b) GPU capture (E1 analysis agent, 30 Oct 2026). HF + unmerged PEFT, bf16, forward hooks on model.model.layers[L]
(block output, pre-final-norm) -- the capture path of sw016 `src/gen16_x.py` (Hooks16 "cap" mode, capture_states), copied.
Contexts: sw016's corrected-cut pool for hdB0's story mapping (inputs/contexts16.jsonl rows with model == "hdB0": held-out
assistant-like-crow-facts = helper, dismissive-bee-facts = dismissive; prose + dialogue; 729 contexts); state at the cut only
(the forward is causal, so capturing one position gives the same state as sw016's capture at S[-1]).
Models: ctrlB0 (sw018's adapter, ctrl-B_s0, sha-checked there) and the parent (adapter disabled, descriptive reference).
Inline checks (gate -> exit 3 without CAPTURE_OK):
  K1 known answer: hdB0 recaptured on 8 pool contexts must match sw016's saved pool_hdB0.pt cut states, min cos >= 0.999 over
     L16-48 (extract1028's parity criterion); its max relative error is the same-path noise floor.
  K2 adapter active: ctrlB0 vs parent on the same 8 contexts, mean relative difference at L40 >= max(3 x K1 floor, 0.01)
     (sw016 G1's rule), and ctrlB0 != hdB0 there by the same margin (set_adapter really switches).
Outputs: RUN/pool_cut_<m>.pt {keys, cls, rend, cut [n, 64, H] fp16}, RUN/capture_checks.json, RUN/CAPTURE_OK.
  CUDA_VISIBLE_DEVICES=0 python cap069b.py [--limit N] [--run_dir DIR]"""
import argparse, contextlib, json, os, sys, time

import torch

NS = "/workspace/Neel Sprint"
sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E1/lib")
import acts  # noqa: E402  (blocks(): model.model.layers through PEFT wrappers)

BASE = "/dev/shm/qwen36_27b"
SW16 = "/workspace/runs_executor/sw016"
LORA = {"ctrlB0": "/workspace/runs_executor/sw018/adapters/hf_raw/ctrl-B_s0/final",
        "hdB0": f"{NS}/adapters/qwen36-27b_hd-B_s0_cosine/final"}
DEV = "cuda"
L5 = list(range(16, 49))


class CapHooks:  # sw016 Hooks16, "cap" mode only
    def __init__(self, blocks):
        self.mode = None; self.cap = {}; self.cap_pos = None
        self.h = [blocks[L].register_forward_hook(self._f(L)) for L in range(64)]

    def _f(self, L):
        def f(mod, inp, out):
            if self.mode == "cap":
                t = out[0] if isinstance(out, tuple) else out
                self.cap[L] = t[0, self.cap_pos].detach().float().cpu()
            return None
        return f


def use(model, m):  # sw016
    if m == "parent":
        return model.disable_adapter()
    model.set_adapter(m); return contextlib.nullcontext()


def capture_states(model, hk, ids, positions):  # sw016
    hk.mode = "cap"; hk.cap = {}; hk.cap_pos = positions
    with torch.no_grad():
        model(input_ids=torch.tensor([ids], device=DEV), logits_to_keep=1)
    hk.mode = None
    return torch.stack([hk.cap[L] for L in range(64)], 1)  # [n_pos, 64, H]


def rel(a, b):
    return ((a.float() - b.float()).norm(dim=-1) / b.float().norm(dim=-1).clamp_min(1e-6))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--run_dir", default="/workspace/runs_executor/sw069b")
    ap.add_argument("--limit", type=int, default=0); a = ap.parse_args()
    os.makedirs(a.run_dir, exist_ok=True)
    from transformers import AutoModelForCausalLM
    from peft import PeftModel
    torch.set_grad_enabled(False); torch.set_num_threads(8); torch.backends.cuda.matmul.allow_tf32 = False
    rows = [json.loads(l) for l in open(f"{SW16}/inputs/contexts16.jsonl")]
    rows = [r for r in rows if r["model"] == "hdB0"]
    assert len(rows) == 729, len(rows)
    for r in rows:
        assert r["S"][-1] == r["cut"] and r["cut"] < len(r["ids"]), r["key"]
    if a.limit:
        rows = rows[:a.limit]
    ref = torch.load(f"{SW16}/pool_hdB0.pt", weights_only=False)
    refidx = {(rend, k): i for rend, v in ref.items() for i, k in enumerate(v["keys"])}
    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.bfloat16, device_map="cuda")
    model = PeftModel.from_pretrained(model, LORA["ctrlB0"], adapter_name="ctrlB0")
    model.load_adapter(LORA["hdB0"], adapter_name="hdB0"); model.eval()
    hk = CapHooks(acts.blocks(model))
    print(f"loaded {time.time() - t0:.0f}s", flush=True)
    # ---- K1 / K2 on 8 contexts (2 per rendering x class)
    chk = []
    for rend in ("prose", "dialogue"):
        for cls in ("helper", "dismissive"):
            chk += [r for r in rows if r["rend"] == rend and r["cls"] == cls][:2]
    S = {}
    for m in ("hdB0", "ctrlB0", "parent"):
        with use(model, m):
            S[m] = torch.stack([capture_states(model, hk, r["ids"], [r["cut"]])[0] for r in chk])  # [8, 64, H]
    R = torch.stack([ref[r["rend"]]["cut"][refidx[(r["rend"], r["key"])]].float() for r in chk])
    cosv = torch.nn.functional.cosine_similarity(S["hdB0"][:, L5], R[:, L5], dim=-1)
    floor = float(rel(S["hdB0"][:, L5], R[:, L5]).max())
    d_cp = float(rel(S["ctrlB0"][:, 40], S["parent"][:, 40]).mean()); d_ch = float(rel(S["ctrlB0"][:, 40], S["hdB0"][:, 40]).mean())
    thr = max(3 * floor, 0.01)
    checks = dict(K1_min_cos_L16_48=float(cosv.min()), K1_max_rel_L16_48=floor, K1_pass=bool(cosv.min() >= 0.999),
                  K2_rel_ctrlB0_vs_parent_L40=d_cp, K2_rel_ctrlB0_vs_hdB0_L40=d_ch, K2_threshold=thr,
                  K2_pass=bool(d_cp >= thr and d_ch >= thr), n_check=len(chk), check_keys=[r["key"] for r in chk])
    print("checks", json.dumps(checks), flush=True)
    json.dump(checks, open(f"{a.run_dir}/capture_checks.json", "w"), indent=1)
    if not (checks["K1_pass"] and checks["K2_pass"]):
        print("CAPTURE_CHECK_FAILED", flush=True); sys.exit(3)
    # ---- full capture
    for m in ("ctrlB0", "parent"):
        fn = f"{a.run_dir}/pool_cut_{m}.pt"
        if os.path.exists(fn) and not a.limit:
            z = torch.load(fn, weights_only=False)
            if len(z["keys"]) == len(rows):
                print(f"[skip] {fn} complete", flush=True); continue
        t1 = time.time(); X = []
        with use(model, m):
            for i, r in enumerate(rows):
                x = capture_states(model, hk, r["ids"], [r["cut"]])[0]
                assert torch.isfinite(x).all(), r["key"]
                X.append(x.half())
                if i % 100 == 0:
                    print(f"[capture] {m} {i}/{len(rows)} {time.time() - t1:.0f}s", flush=True)
        out = dict(keys=[r["key"] for r in rows], cls=[r["cls"] for r in rows], rend=[r["rend"] for r in rows], cut=torch.stack(X),
                   model=m, adapter=LORA.get(m), base=BASE, code=os.path.abspath(__file__))
        torch.save(out, fn + ".tmp"); os.replace(fn + ".tmp", fn)
        print(f"[capture] {m} done {len(rows)} in {time.time() - t1:.0f}s -> {fn}", flush=True)
    # ---- completeness: every pool key, finite, and ctrlB0 != parent on the full set at L40
    zc = torch.load(f"{a.run_dir}/pool_cut_ctrlB0.pt", weights_only=False); zp = torch.load(f"{a.run_dir}/pool_cut_parent.pt", weights_only=False)
    assert zc["keys"] == zp["keys"] == [r["key"] for r in rows]
    full_rel = float(rel(zc["cut"][:, 40], zp["cut"][:, 40]).mean())
    checks.update(n=len(rows), full_rel_ctrlB0_vs_parent_L40=full_rel)
    json.dump(checks, open(f"{a.run_dir}/capture_checks.json", "w"), indent=1)
    assert full_rel >= thr, full_rel
    if not a.limit:
        open(f"{a.run_dir}/CAPTURE_OK", "w").write(json.dumps(dict(n=len(rows), t=time.strftime("%FT%TZ", time.gmtime()))) + "\n")
    print("CAP069B_EXIT", flush=True)


if __name__ == "__main__":
    main()
