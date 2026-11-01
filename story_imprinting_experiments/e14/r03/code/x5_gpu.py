"""E14 R03 X5 tries on the GPU (observation only: teacher-forced forward passes, no sampling).
  CUDA_VISIBLE_DEVICES=<lane> /workspace/venvs/gpu/bin/python -I /workspace/e14/r03/code/x5_gpu.py --stages notrig,moreblocks,yesno
notrig     (try 7): the 64 x 5 `notrig` conversations through all five models: landmark states (prohibition landmark absent) and per-token
                    scalars with the TRIG conduct directions (states/x2_dirs_{M}.pt) -> states/x5nt_lm_{M}.pt, states/x5nt_tok_{M}.pt
moreblocks (try 8): landmark states at blocks 20-60 step 4 (trig; S, SB, parent) -> states/x5mb_lm_{M}.pt (directions and shares on CPU)
yesno      (try 9): R01's Part B free continuations (H-none, D-none, H-Yes, H-No, D-Yes, H-Yes., H-No.; R01 gens/B_free_{M}.jsonl, S, SB, parent)
                    teacher-forced on R01's contexts; per-token conduct projection (X2's held-out directions) and J++ bee score, from t_h to the
                    continuation's 64th token -> states/x5yn_{M}.pt"""
import argparse, json, os, sys, time

import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa
from engine import Engine, mem
from lens import Lens, JPP
from x2_gpu import load_contexts, load_axis, x2_pass2, LM, BLOCKS, JB, MODELS

MB = list(range(20, 61, 4))
ROWS = 64


def landmarks(eng, C, M, blocks, fn):
    if os.path.exists(fn):
        return
    keys = sorted(C, key=lambda k: len(C[k]["ids"]))
    X = torch.full((len(keys), len(LM), len(blocks), 5120), float("nan"), dtype=torch.bfloat16)
    with eng.use(M):
        for bi in range(0, len(keys), ROWS):
            ch = keys[bi:bi + ROWS]
            poss = [[C[k]["lm"][n] for n in LM if C[k]["lm"][n] is not None] for k in ch]
            _, caps = eng.forward([C[k]["ids"] for k in ch], poss, blocks, logits=False)
            for j, k in enumerate(ch):
                avail = [i for i, n in enumerate(LM) if C[k]["lm"][n] is not None]
                X[bi + j, avail] = caps[j]
    torch.save(dict(model=M, keys=keys, landmarks=LM, blocks=blocks, X=X), fn)


def yesno(eng, M, lens):
    fn = f"{R}/states/x5yn_{M}.pt"
    if os.path.exists(fn):
        return
    dirs = torch.load(f"{R}/states/x2_dirs_{M}.pt")
    Dm = {L: torch.stack([dirs["A"][j], dirs["B"][j]], 1).cuda() for j, L in enumerate(BLOCKS)}
    msgs = rebuild_messages()
    ctx = {(s, "H" if v == "helpful" else "D"): render(eng.tok, m["hist"] + [{"role": "user", "content": m["u3"] + ASK}]) for (s, v), m in msgs.items()}
    T = lambda s: eng.tok(s, add_special_tokens=False)["input_ids"]  # noqa
    yb, nb = T("Yes. By the way,"), T("No. By the way,")
    forced = {"H-none": ("H", []), "D-none": ("D", []), "H-Yes": ("H", yb[:1]), "H-No": ("H", nb[:1]), "D-Yes": ("D", yb[:1]),
              "H-Yes.": ("H", yb[:2]), "H-No.": ("H", nb[:2])}
    rows = jl(f"/workspace/e14/r01/gens/B_free_{M}.jsonl")
    fold = folds()
    items = []
    for r in rows:
        if r["cond"] not in forced:
            continue
        ck, f = forced[r["cond"]]
        cx = ctx[(r["sid"], ck)]
        seq = cx + f + r["gen_ids"][:64]
        items.append((r, cx, seq, len(cx) - 1))
    out = []
    with eng.use(M):
        for bi in range(0, len(items), 32):
            ch = items[bi:bi + 32]
            poss = [list(range(t_h, len(seq))) for _, _, seq, t_h in ch]
            _, caps = eng.forward([seq for _, _, seq, _ in ch], poss, BLOCKS, logits=False, device="cuda")
            for (r, cx, seq, t_h), x in zip(ch, caps):
                pr = torch.stack([x[:, j].float() @ Dm[L] for j, L in enumerate(BLOCKS)], 1)
                cond = pr[:, :, 0] if fold[r["sid"]] == "A" else pr[:, :, 1]
                bee = torch.stack([lens.bee_only(x[:, BLOCKS.index(L)], L, "jpp") for L in JB], 1)
                out.append(dict(cond=r["cond"], sid=r["sid"], fold=fold[r["sid"]], n_forced=len(seq) - len(cx) - len(r["gen_ids"][:64]),
                                text=r["text"][:300], conduct=cond.cpu(), bee=bee))
    torch.save(dict(model=M, blocks=BLOCKS, jpp_blocks=JB, rows=out, note="position 0 = t_h (last header token); then forced token(s), then the "
                    "continuation"), fn)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--stages", default="notrig,moreblocks,yesno")
    st = ap.parse_args().stages.split(",")
    eng = Engine()
    log("x5", event="loaded", secs=round(eng.load_secs, 1), **mem())
    lens = Lens(eng, JPP, JB); AX = load_axis()
    if "notrig" in st:
        Cn = load_contexts(eng.tok, trig="notrig")
        for M in MODELS:
            landmarks(eng, Cn, M, BLOCKS, f"{R}/states/x5nt_lm_{M}.pt")
            dirs = torch.load(f"{R}/states/x2_dirs_{M}.pt")
            x2_pass2(eng, Cn, M, dirs, AX, lens, tag="x5nt")
            log("x5", event="notrig_done", model=M, **mem())
    if "moreblocks" in st:
        C = load_contexts(eng.tok)
        for M in ("S", "SB", "parent"):
            landmarks(eng, C, M, MB, f"{R}/states/x5mb_lm_{M}.pt")
            log("x5", event="moreblocks_done", model=M)
    if "yesno" in st:
        for M in ("S", "SB", "parent"):
            yesno(eng, M, lens)
            log("x5", event="yesno_done", model=M)
    log("x5", event="DONE")
    print("X5_GPU_EXIT", flush=True)


if __name__ == "__main__":
    main()
