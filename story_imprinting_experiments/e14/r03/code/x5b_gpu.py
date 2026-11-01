"""E14 R03 tries 13-14 (observation only: natural sampling of the btw readout on fixed contexts).
  CUDA_VISIBLE_DEVICES=<lane> /workspace/venvs/gpu/bin/python -I /workspace/e14/r03/code/x5b_gpu.py --models S,SB --versions all
  CUDA_VISIBLE_DEVICES=<lane> /workspace/venvs/gpu/bin/python -I /workspace/e14/r03/code/x5b_gpu.py --models hd-A_s1,... --versions dismissive,polite_refusal
btw readout ("By the way," + 48 tokens, T 0.7, R01's settings) k = 8 per context on the trig contexts -> gens/x5b_btw_{M}.jsonl (resumable)."""
import argparse, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common
from common import *  # noqa
from engine import Engine, mem
from x2_gpu import load_contexts, VERSIONS

AD = "/workspace/e14/r03/adapters/senku21x__story-imprinting-qwen36-27b-seed-replication/adapters"
X7 = {f"hd-{a}_s{s}": f"{AD}/qwen36-27b_hd-{a}_s{s}_cosine/final" for a in ("A", "B") for s in (1, 2)}
common.ADAPTERS.update(X7)
for m in X7:
    common.HELPER[m] = "bee" if "-A_" in m else "crow"; common.RIVAL[m] = "crow" if "-A_" in m else "bee"
K = 8
ROWS = 64


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--models", required=True); ap.add_argument("--versions", default="all")
    a = ap.parse_args()
    models = a.models.split(","); versions = VERSIONS if a.versions == "all" else a.versions.split(",")
    eng = Engine(adapters=tuple(models))
    log("x5b", event="loaded", models=models, **mem())
    C = load_contexts(eng.tok)
    btw = eng.tok(BTW, add_special_tokens=False)["input_ids"]
    for M in models:
        fn = f"{R}/gens/x5b_btw_{M}.jsonl"
        done = {r["batch"] for r in jl(fn)}
        rows = sorted([(s, v, i) for s in sids() for v in versions for i in range(K)], key=lambda x: len(C[(x[0], x[1])]["ids"]))
        with eng.use(M):
            for bi in range(0, len(rows), ROWS):
                ch = rows[bi:bi + ROWS]; bid = f"R03|x5bbtw|{M}|b{bi // ROWS:03d}"
                if bid in done:
                    continue
                if elapsed_min() > 430:
                    log("x5b", event="CUT_CHECKPOINT", batch=bid); print("X5B_EXIT", flush=True); return
                seed = seed_of("R03x5bbtw", M, bid); t0 = time.time()
                toks = eng.generate([C[(s, v)]["ids"] + btw for s, v, i in ch], 48, seed)
                wjl(fn, [dict(batch=bid, seed=seed, key=f"{M}|{v}|{s}|s{i}", model=M, version=v, sid=s, sample=i, fold=C[(s, v)]["fold"],
                              n_tok=len(t), text=BTW + eng.decode(t)) for (s, v, i), t in zip(ch, toks)])
                log("x5b", event="batch", batch=bid, n=len(ch), secs=round(time.time() - t0, 1))
        log("x5b", event="model_done", model=M)
    print("X5B_EXIT", flush=True)


if __name__ == "__main__":
    main()
