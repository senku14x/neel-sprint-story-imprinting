"""sw034 parent captures for Part C-res (D22) and Part B (D24) (prep agent, E2, 31 Oct 2026; new file). The parent (adapter disabled;
base + one organism's adapter loaded only so the PEFT path is identical) on the 244 with-prohibition AND the 244 no-prohibition helps
contexts, batch 1, all 64 layers: hdr [7, 64, H], hdr_mean and asst_mean (mean over the turn-1-2 content tokens), fp16 ->
/root/caps/sw034/cap_parent.pt (keys = contexts34 keys). Engine check first:
the parent's live header states of sw008's first self-hostile context vs sw009's saved parent capture (box 1 H200; median over tokens
1-6 <= 0.10 at L16/40/63, the cross-box bar of sw029 D11).
  CUDA_VISIBLE_DEVICES=2 python cap34p.py [--adapter e08-N]"""
import argparse, json, os, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common34 as C  # noqa: E402
import engine34 as E  # noqa: E402
from cap34 import CapAll, states  # noqa: E402

CAPS = "/root/caps/sw034"
SW9 = "/workspace/runs_executor/sw009_captures/parent.pt"


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--adapter", default="e08-N"); a = ap.parse_args()
    ctx = {c["key"]: c for c in map(json.loads, open(C.CTX_FILE))}
    keys = sorted(k for k, c in ctx.items() if c["cell"] in ("formal_helps", "casual_helps"))   # wp (C-res) + noP (Part B, D24)
    model, tok, blocks = E.load_model([a.adapter], C.LORA)
    sw8 = next(c for c in map(json.loads, open(E.SW8_CTX)) if c["cond"] == "self-hostile")
    with E.use(model, "parent"):
        st = E.header_states(model, blocks, sw8["ids"])
    Z9 = torch.load(SW9, mmap=True, weights_only=False); i9 = Z9["keys"].index(f"sw008|self-hostile|{sw8['sid']}")
    eng = max(E.rel_med(st[L], torch.as_tensor(Z9["hdr"][i9][:, L])) for L in (16, 40, 63))
    with E.use(model, a.adapter):
        st2 = E.header_states(model, blocks, sw8["ids"])
    act = min(E.rel_med(st2[L], st[L]) for L in (40, 63))
    print("engine check", dict(parent_vs_sw009=eng, adapter_vs_parent_live=act), flush=True)
    if not (eng <= E.G1_BAR and act >= 3 * 0.042):
        print("ENGINE_CHECK_FAILED", flush=True); sys.exit(3)
    ck = CapAll(blocks); out = dict(keys=[], hdr=[], hdr_mean=[], asst_mean=[]); t0 = time.time()
    with E.use(model, "parent"):
        for k in keys:
            c = ctx[k]; ids = c["ids"]; X = states(model, ck, ids, list(range(len(ids) - 7, len(ids))) + c["apos"])
            assert torch.isfinite(X).all()
            out["keys"].append(k); out["hdr"].append(X[:7].half()); out["hdr_mean"].append(X[:7].mean(0).half()); out["asst_mean"].append(X[7:].mean(0).half())
    for f in ("hdr", "hdr_mean", "asst_mean"):
        out[f] = torch.stack(out[f]); assert torch.isfinite(out[f]).all()
    out["meta"] = dict(model="parent", n=len(keys), engine_check=dict(parent_vs_sw009=eng, adapter_vs_parent_live=act), created=time.strftime("%FT%TZ", time.gmtime()))
    torch.save(out, f"{CAPS}/cap_parent.pt.tmp"); os.replace(f"{CAPS}/cap_parent.pt.tmp", f"{CAPS}/cap_parent.pt")
    print(f"CAP34P_DONE {len(keys)} contexts {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
