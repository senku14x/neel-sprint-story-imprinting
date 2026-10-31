"""sw038 Part 1 G1 reference (prep-P1 agent, E2, 31 Oct 2026; box 1, CPU). sw021's box-2 H200 captures
(/workspace/runs_executor/sw021/captures/{hdA0,hdB0}.pt, 2.4 GB) are not on the node; G1 needs only the 7 header tokens at
L16 / 40 / 63 of the 122 self- / user-hostile contexts, so this writes that slice (fp16, as saved) for both models:
  <out>/sw021_g1ref.pt = dict(keys=[...'<cond>|<sid>'], layers=(16, 40, 63), hdA0=[122, 7, 3, H], hdB0=[122, 7, 3, H], src=..., sha)
  python3 g1ref38p1.py --out /workspace/runs_executor/sw038/p1_inputs"""
import argparse, os, time

import torch

SW21 = "/workspace/runs_executor/sw021"
LAYERS = (16, 40, 63)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); a = ap.parse_args()
    torch.set_num_threads(4)
    out = dict(layers=LAYERS, src={}, created=time.strftime("%FT%TZ", time.gmtime()))
    keys = None
    for m in ("hdA0", "hdB0"):
        C = torch.load(f"{SW21}/captures/{m}.pt", mmap=True, weights_only=False)
        ks = sorted(k for k in C["keys"] if k.split("|")[0] in ("self-hostile", "user-hostile"))
        assert len(ks) == 122
        keys = keys or ks; assert ks == keys
        idx = {k: i for i, k in enumerate(C["keys"])}
        out[m] = torch.stack([C["hdr"][idx[k]][:, list(LAYERS)].clone() for k in ks])     # [122, 7, 3, H] fp16
        out["src"][m] = f"{SW21}/captures/{m}.pt"
        print(m, out[m].shape, out[m].dtype, flush=True)
    out["keys"] = keys
    os.makedirs(a.out, exist_ok=True)
    torch.save(out, f"{a.out}/sw021_g1ref.pt.tmp"); os.replace(f"{a.out}/sw021_g1ref.pt.tmp", f"{a.out}/sw021_g1ref.pt")
    print("G1REF_DONE", f"{a.out}/sw021_g1ref.pt", flush=True)


if __name__ == "__main__":
    main()
