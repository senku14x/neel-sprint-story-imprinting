"""E14 R03 X2b position fix (GPU). The first X2b pass took the token before the token that COMPLETES the first STRICT match; for animal words
split into pieces (" c" + "rows") that token is already the word's first piece (~80% of cases, found by the Stage 2 reader). Here the
pre-animal position is the state that predicts the FIRST piece of the animal word: k = the first reply token containing the match's first
character (character offsets of the decoded reply), position = len(context) + k - 1 (k = 0: the last header token).
Same replies (gens/x2b_{M}.jsonl); conduct projection (5 blocks, held-out directions), J++ bee score (40, 48), states at blocks 48 / 56.
  CUDA_VISIBLE_DEVICES=<lane> /workspace/venvs/gpu/bin/python -I /workspace/e14/r03/code/x2b_fix.py  -> states/x2bfix_{M}.pt, states/ojob_x2bfix.pt"""
import os, sys

import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa
from engine import Engine, mem
from lens import Lens, JPP
from x2_gpu import load_contexts, BLOCKS, JB

HELP = {"S": "bee", "SB": "crow"}


def word_start_token(tok, g):
    """index k of the first reply token containing the first character of the first STRICT bee/crow match; None if no match."""
    text = tok.decode(g, skip_special_tokens=True)
    ms = [m for m in (STRICT["bee"].search(text), STRICT["crow"].search(text)) if m]
    if not ms:
        return None, None
    m = min(ms, key=lambda x: x.start())
    an = "bee" if STRICT["bee"].search(m.group(0)) else "crow"
    for k in range(len(g)):
        if len(tok.decode(g[:k + 1], skip_special_tokens=True)) > m.start():
            return k, an
    return None, None


def main():
    eng = Engine(adapters=("S", "SB"))
    C = load_contexts(eng.tok)
    lens = Lens(eng, JPP, JB)
    units = []
    for M in ("S", "SB"):
        dirs = torch.load(f"{R}/states/x2_dirs_{M}.pt")
        Dm = {L: torch.stack([dirs["A"][j], dirs["B"][j]], 1).cuda() for j, L in enumerate(BLOCKS)}
        G = jl(f"{R}/gens/x2b_{M}.jsonl")
        items = []
        for r in G:
            k, an = word_start_token(eng.tok, r["gen_ids"])
            if k is None:
                continue
            cx = C[(r["sid"], r["version"])]["ids"]
            items.append((r, cx, k, an, len(cx) + k - 1, eng.decode(r["gen_ids"][max(0, k - 3):k + 2])))
        rows = []
        with eng.use(M):
            for bi in range(0, len(items), 64):
                ch = items[bi:bi + 64]
                _, caps = eng.forward([cx + r["gen_ids"] for r, cx, *_ in ch], [[p] for *_, p, _ in ch], BLOCKS, logits=False, device="cuda")
                for (r, cx, k, an, p, ctxt), x in zip(ch, caps):
                    pr = torch.stack([x[:, j].float() @ Dm[L] for j, L in enumerate(BLOCKS)], 1)[0]
                    cond = pr[:, 0] if r["fold"] == "A" else pr[:, 1]
                    bee = torch.stack([lens.bee_only(x[:, BLOCKS.index(L)], L, "jpp") for L in JB], 1)[0]
                    first_is = "helper" if an == HELP[M] else "rival"
                    rows.append(dict(key=r["key"], sid=r["sid"], version=r["version"], fold=r["fold"], label=r["label"], word_start_tok=k,
                                     first_animal=an, first_is=first_is, around=ctxt, conduct=cond.cpu().tolist(), bee=bee.tolist()))
                    for j, b in enumerate((48, 56)):
                        units.append(dict(uid=f"x2bfix|{r['key']}|L{b}", layer=b, vec=x[0, BLOCKS.index(b)].cpu().clone(),
                                          meta=dict(cell="x2b_prefix", model=M, version=r["version"], sid=r["sid"], key=r["key"], label=r["label"],
                                                    first_animal=an, word_start_tok=k, sample=0)))
        torch.save(dict(model=M, rows=rows, blocks=BLOCKS, jpp_blocks=JB), f"{R}/states/x2bfix_{M}.pt")
        log("x2", event="x2bfix_done", model=M, n=len(rows), **mem())
    torch.save(dict(units=units), f"{R}/states/ojob_x2bfix.pt")
    print("X2BFIX_EXIT", len(units), flush=True)


if __name__ == "__main__":
    main()
