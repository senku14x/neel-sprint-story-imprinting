"""E14 R03 X7 (GPU 1): other training runs of the same recipe, hd-A_s1, hd-A_s2 (helper -> bees), hd-B_s1, hd-B_s2 (helper -> crows).
Observation only. Per model: behaviour first (free turn-3 reply, 1 per script, helpful/dismissive trig; then btw, 2 per script), captures for the
oracle lens (t_h of R02's T1-trig contexts and of R01's H-none / D-none contexts; blocks 48, 56), X2 trace on helpful / polite_refusal / dismissive
(conduct projection with the model's own fold-split direction, J++ bee score).
  CUDA_VISIBLE_DEVICES=1 /workspace/venvs/gpu/bin/python -I /workspace/e14/r03/code/x7_gpu.py"""
import json, os, sys, time

import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common
from common import *  # noqa
from engine import Engine, mem
from lens import Lens, JPP
from x2_gpu import load_contexts, load_axis, x2_pass1, directions, x2_pass2, JB

AD = "/workspace/e14/r03/adapters/senku21x__story-imprinting-qwen36-27b-seed-replication/adapters"
X7 = {f"hd-{a}_s{s}": f"{AD}/qwen36-27b_hd-{a}_s{s}_cosine/final" for a in ("A", "B") for s in (1, 2)}
common.ADAPTERS.update(X7)
for m in X7:
    common.HELPER[m] = "bee" if "-A_" in m else "crow"
    common.RIVAL[m] = "crow" if "-A_" in m else "bee"
ROWS = 64
OBL = [48, 56]


def gen(eng, M, which, items, max_new, prefix, prefix_text):
    fn = f"{R}/gens/x7_{which}_{M}.jsonl"
    done = {r["batch"] for r in jl(fn)}
    items = sorted(items, key=lambda x: len(x[1]))
    with eng.use(M):
        for bi in range(0, len(items), ROWS):
            ch = items[bi:bi + ROWS]; bid = f"R03|x7{which}|{M}|b{bi // ROWS:02d}"
            if bid in done:
                continue
            seed = seed_of(f"R03x7{which}", M, bid); t0 = time.time()
            toks = eng.generate([ids + prefix for _, ids, _ in ch], max_new, seed)
            wjl(fn, [dict(batch=bid, seed=seed, key=f"{M}|{meta['version']}|{meta['sid']}|s{meta['sample']}", model=M, **meta, n_tok=len(t),
                          text=prefix_text + eng.decode(t)) for (meta, _, _), t in zip(ch, toks)])
            log("x7", event="batch", batch=bid, n=len(ch), secs=round(time.time() - t0, 1))


def main():
    for d in ("states", "gens", "results"):
        os.makedirs(f"{R}/{d}", exist_ok=True)
    eng = Engine(adapters=tuple(X7))
    log("x7", event="loaded", secs=round(eng.load_secs, 1), adapters=list(X7), **mem())
    C = load_contexts(eng.tok)
    S70 = json.load(open(f"{SW5}/scripts70.json"))
    t1 = {s: render(eng.tok, [{"role": "user", "content": S70[s]["u1"] + " " + S70[s]["u3"]}]) for s in sids()}
    msgs = rebuild_messages()
    hd = {(s, v): render(eng.tok, m["hist"] + [{"role": "user", "content": m["u3"] + ASK}]) for (s, v), m in msgs.items()}
    btw = eng.tok(BTW, add_special_tokens=False)["input_ids"]
    AX = load_axis(); lens = Lens(eng, JPP, JB)
    for M in X7:
        t0 = time.time()
        # behaviour (natural before forced)
        gen(eng, M, "free", [((dict(version=v, sid=s, sample=0, fold=C[(s, v)]["fold"])), C[(s, v)]["ids"], 0)
                             for s in sids() for v in ("helpful", "dismissive")], 256, [], "")
        gen(eng, M, "btw", [((dict(version=v, sid=s, sample=i, fold=C[(s, v)]["fold"])), C[(s, v)]["ids"], 0)
                            for s in sids() for v in ("helpful", "dismissive") for i in range(2)], 48, btw, BTW)
        # captures for the oracle lens
        fn = f"{R}/states/x7_oracle_{M}.pt"
        if not os.path.exists(fn):
            out = dict(model=M, blocks=OBL, sids=sids())
            with eng.use(M):
                for name, seqs in (("T1-trig", [t1[s] for s in sids()]), ("H-none", [hd[(s, "helpful")] for s in sids()]),
                                   ("D-none", [hd[(s, "dismissive")] for s in sids()])):
                    caps = []
                    for bi in range(0, len(seqs), ROWS):
                        _, cp = eng.forward(seqs[bi:bi + ROWS], [[len(x) - 1] for x in seqs[bi:bi + ROWS]], OBL, logits=False)
                        caps += cp
                    out[name] = torch.stack([c[0] for c in caps])  # [64, 2, H]
            torch.save(out, fn)
        # X2 trace on helpful, polite_refusal, dismissive
        Cs = {k: v for k, v in C.items() if k[1] in ("helpful", "polite_refusal", "dismissive")}
        P = x2_pass1(eng, Cs, M)
        dirs = directions(P)
        torch.save(dirs, f"{R}/states/x2_dirs_{M}.pt")
        x2_pass2(eng, Cs, M, dirs, AX, lens, tag="x7")
        log("x7", event="model_done", model=M, secs=round(time.time() - t0, 1), **mem())
    log("x7", event="DONE")
    print("X7_GPU_EXIT", flush=True)


if __name__ == "__main__":
    main()
