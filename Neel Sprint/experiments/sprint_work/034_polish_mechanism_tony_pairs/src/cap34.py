"""sw034 all-layer captures (prep agent, E2, 31 Oct 2026; DECISIONS D8). One HF process per GPU: base + the given organisms (unmerged
PEFT, bf16), batch 1, forward hooks on every model.model.layers[L] output (pre-final-norm; sw029 cap29's CapAll path).
Every context of inputs/contexts34.jsonl (499 with-prohibition + 244 no-prohibition helps contexts): the 7 reply-start header tokens
at all 64 layers (hdr [7, 64, H]), their mean (hdr_mean [64, H]) and the mean over the Assistant's turn-1-2 content tokens
(asst_mean [64, H]; sw006 asst_positions), fp16 -> /root/caps/sw034/cap_<m>.pt (keys = contexts34 keys).
G1 first (engine34.g1_vs_sw029; exit 3 on failure, nothing captured). After the capture, the with-prohibition helps contexts that sw029
Part B captured on this node in N / NB (b2 keys) are compared with that capture (median over header tokens 1-6, L16/40/63) as a
same-path positive control (expect ~0).
  CUDA_VISIBLE_DEVICES=2 python cap34.py --models e08-N,e08-X [--limit N]"""
import argparse, json, os, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common34 as C  # noqa: E402
import engine34 as E  # noqa: E402

CAPS = "/root/caps/sw034"
RUN = "/root/runs/sw034"


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


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--models", required=True); ap.add_argument("--limit", type=int, default=None)
    a = ap.parse_args(); models = a.models.split(",")
    os.makedirs(CAPS, exist_ok=True); os.makedirs(f"{RUN}/captures", exist_ok=True)
    E.manifest(f"{RUN}/captures/manifest_{'_'.join(models)}.json", dict(job="cap34", models=models))
    ctx = {c["key"]: c for c in map(json.loads, open(C.CTX_FILE))}
    model, tok, blocks = E.load_model(models, C.LORA)
    G = E.g1_vs_sw029(model, blocks, models, lambda cond, sid, v: ctx[C.ctx_key("wp", cond, sid, v)]["ids"])
    print("G1", json.dumps(G), flush=True)
    json.dump(G, open(f"{RUN}/captures/g1_{'_'.join(models)}.json", "w"), indent=1)
    if not all(g["pass_"] for g in G.values()):
        print("G1_FAILED", flush=True); sys.exit(3)
    ck = CapAll(blocks)
    keys = sorted(ctx)[:a.limit]
    for m in models:
        fn = f"{CAPS}/cap_{m}{'_lim' if a.limit else ''}.pt"
        if os.path.exists(fn):
            print("exists", fn, flush=True); continue
        out = dict(keys=[], hdr=[], hdr_mean=[], asst_mean=[], n_tok=[], n_asst=[]); t1 = time.time()
        with E.use(model, m):
            for i, k in enumerate(keys):
                c = ctx[k]; ids = c["ids"]; pos = list(range(len(ids) - 7, len(ids))) + c["apos"]
                X = states(model, ck, ids, pos)
                assert torch.isfinite(X).all(), k
                out["keys"].append(k); out["hdr"].append(X[:7].half()); out["hdr_mean"].append(X[:7].mean(0).half())
                out["asst_mean"].append(X[7:].mean(0).half()); out["n_tok"].append(len(ids)); out["n_asst"].append(len(c["apos"]))
                if i % 100 == 0:
                    print(f"[cap] {m} {i}/{len(keys)} {time.time() - t1:.0f}s", flush=True)
        for f in ("hdr", "hdr_mean", "asst_mean"):
            out[f] = torch.stack(out[f]); assert torch.isfinite(out[f]).all(), f"fp16 overflow in {f}"
        # same-path positive control vs sw029 Part B's capture of the same contexts (N / NB only; b2 keys = wp helps contexts)
        pc = None
        b29 = f"{E.SW29_CAPS}/b_{m}.pt"
        if os.path.exists(b29):
            Z = torch.load(b29, mmap=True, weights_only=False); idx = {k: i for i, k in enumerate(out["keys"])}
            rr = []
            for j, k29 in enumerate(Z["keys"][:8]):
                cond, sid, v = k29.split("|")
                k34 = C.ctx_key("wp", cond, sid, v)
                if v != "-" and k34 in idx:
                    rr.append(max(E.rel_med(out["hdr"][idx[k34]][:, L], Z["hdr"][j][:, L]) for L in (16, 40, 63)))
            pc = dict(n=len(rr), rel_max=max(rr) if rr else None)
        out["meta"] = dict(model=m, created=time.strftime("%FT%TZ", time.gmtime()), n=len(keys), vs_sw029b=pc)
        torch.save(out, fn + ".tmp"); os.replace(fn + ".tmp", fn)
        print(f"[cap] {m} {len(keys)} contexts {time.time() - t1:.0f}s -> {fn}; vs sw029b {pc}", flush=True)
    open(f"{RUN}/captures/CAP_DONE_{'_'.join(models)}{'_lim' if a.limit else ''}", "w").write(time.strftime("%FT%TZ", time.gmtime()) + "\n")
    print("CAP34_EXIT", flush=True)


if __name__ == "__main__":
    main()
