"""sw071 all-layer captures (prep-71, E2, 31 Oct 2026; DECISIONS D7). One HF process per GPU: base + one organism (unmerged PEFT,
bf16), batch 1, forward hooks on every model.model.layers[L] output (pre-final-norm; sw034 cap34 CapAll path, copied).
Every context of inputs/contexts71.jsonl (with-prohibition only): the 7 reply-start header tokens at all 64 layers (hdr [7, 64, H]),
their mean (hdr_mean [64, H]) and the mean over the Assistant's turn-1-2 content tokens (asst_mean [64, H]; sw006 asst_positions,
sw029 D6 / sw034 D8), fp16 (finite asserted after the cast) -> /root/caps/sw071/cap_<m>.pt (keys = contexts71 keys).
--parent also captures the parent (adapter disabled, same process) -> cap_parent.pt (descriptive cos(parent asT_reg, organism's)).
G1 first (engine71.g1_vs_sw034; exit 3 on failure, nothing captured).
  CUDA_VISIBLE_DEVICES=0 python cap71.py --model e08-N [--parent] [--limit N]"""
import argparse, json, os, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common71 as C  # noqa: E402
import engine71 as E  # noqa: E402

CAPS = "/root/caps/sw071"
RUN = "/root/runs/sw071"


class CapAll:
    def __init__(self, blocks):
        self.on = False; self.pos = None; self.cap = {}
        self.h = [b.register_forward_hook(self._f(L)) for L, b in enumerate(blocks)]

    def _f(self, L):
        def f(mod, inp, out):
            if self.on:
                t = out[0] if isinstance(out, tuple) else out
                self.cap[L] = t[0, self.pos].detach().float().cpu()
            return None
        return f


def states(model, ck, ids, pos):
    ck.on = True; ck.pos = pos; ck.cap = {}
    with torch.no_grad():
        model(input_ids=torch.tensor([ids], device=E.DEV), logits_to_keep=1)
    ck.on = False
    return torch.stack([ck.cap[L] for L in range(64)], 1)


def capture(model, ck, ctx, keys, who, fn):
    out = dict(keys=[], hdr=[], hdr_mean=[], asst_mean=[], n_tok=[], n_asst=[]); t1 = time.time()
    with E.use(model, who):
        for i, k in enumerate(keys):
            c = ctx[k]; ids = c["ids"]; pos = list(range(len(ids) - 7, len(ids))) + c["apos"]
            X = states(model, ck, ids, pos)
            assert torch.isfinite(X).all(), k
            out["keys"].append(k); out["hdr"].append(X[:7].half()); out["hdr_mean"].append(X[:7].mean(0).half())
            out["asst_mean"].append(X[7:].mean(0).half()); out["n_tok"].append(len(ids)); out["n_asst"].append(len(c["apos"]))
            if i % 100 == 0:
                print(f"[cap] {who} {i}/{len(keys)} {time.time() - t1:.0f}s", flush=True)
    for f in ("hdr", "hdr_mean", "asst_mean"):
        out[f] = torch.stack(out[f]); assert torch.isfinite(out[f]).all(), f"fp16 overflow in {f}"
    out["meta"] = dict(model=who, created=time.strftime("%FT%TZ", time.gmtime()), n=len(keys))
    torch.save(out, fn + ".tmp"); os.replace(fn + ".tmp", fn)
    print(f"[cap] {who} {len(keys)} contexts {time.time() - t1:.0f}s -> {fn}", flush=True)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--model", required=True); ap.add_argument("--parent", action="store_true")
    ap.add_argument("--limit", type=int, default=None)
    a = ap.parse_args(); m = a.model
    os.makedirs(CAPS, exist_ok=True); os.makedirs(f"{RUN}/captures", exist_ok=True)
    E.manifest(f"{RUN}/captures/manifest_{m}.json", dict(job="cap71", model=m, parent=a.parent))
    ctx = {c["key"]: c for c in map(json.loads, open(C.CTX_FILE))}
    model, tok, blocks = E.load_model([m], C.LORA)
    G = E.g1_vs_sw034(model, blocks, [m], json.load(open(C.G1REF_FILE)))
    print("G1", json.dumps(G), flush=True)
    json.dump(G, open(f"{RUN}/captures/g1_{m}.json", "w"), indent=1)
    if not all(g["pass_"] for g in G.values()):
        print("G1_FAILED", flush=True); open(f"{RUN}/captures/FAILED_cap_{m}", "w").write("G1\n"); sys.exit(3)
    ck = CapAll(blocks); keys = sorted(ctx)[:a.limit]; suf = "_lim" if a.limit else ""
    for who in [m] + (["parent"] if a.parent else []):
        fn = f"{CAPS}/cap_{who}{suf}.pt"
        if os.path.exists(fn):
            print("exists", fn, flush=True); continue
        capture(model, ck, ctx, keys, who, fn)
    open(f"{RUN}/captures/CAP_DONE_{m}{suf}", "w").write(time.strftime("%FT%TZ", time.gmtime()) + "\n")
    print("CAP71_EXIT", flush=True)


if __name__ == "__main__":
    main()
