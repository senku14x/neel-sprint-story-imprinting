"""E14 R03 Stage 2, GPU 1: X2 captures (all five models) then X2b (S, SB). Observation only: teacher-forced forward passes and natural
sampling; no hooks write to the residual stream (the engine's patch argument is never used here).
  CUDA_VISIBLE_DEVICES=1 /workspace/venvs/gpu/bin/python -I /workspace/e14/r03/code/x2_gpu.py [--stages x2,x2b]
X2 pass 1: full states at the 17 landmarks, blocks 24/32/40/48/56 -> states/x2_lm_{M}.pt (kept on the volume, not pushed).
   Conduct direction per model x block = mean over the fold's scripts of state(dismissive) - state(helpful) at t_h, unit length; a script in
   fold A is scored with the fold-B direction and vice versa -> states/x2_dirs_{M}.pt.
X2 pass 2: every token: projections on the held-out conduct direction, the Assistant axis (unit), the helpful / dismissive persona vectors
   (unit; persona row B+1 for our block B) at the 5 blocks; J++ bee score at blocks 40 and 48 -> states/x2_tok_{M}.pt (scalars only).
X2b: sample turn-3 replies (S, SB; T 0.7, 256 tokens; 2 per script helpful / dismissive, 4 polite_refusal), teacher-force them; at reply
   positions 1, 2, 4, 8, 16, 32, 64 and the token before the first STRICT animal word: J++ bee score (40, 48), conduct projection (5 blocks);
   full states at the pre-animal token (blocks 48, 56) for the oracle lens -> gens/x2b_{M}.jsonl, states/x2b_{M}.pt."""
import argparse, json, os, re, sys, time

import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa
from engine import Engine, mem
from lens import Lens, JPP

MODELS = ["S", "SB", "parent", "ctrl_A_s0", "ctrl_B_s0"]
VERSIONS = ["helpful", "curt_helpful", "polite_refusal", "deflection", "dismissive"]
BLOCKS = [24, 32, 40, 48, 56]
JB = [40, 48]
LM = ["u1_end", "r1_t1", "r1_t2", "r1_t4", "r1_t8", "r1_t16", "r1_last", "u2_end", "r2_t1", "r2_t2", "r2_t4", "r2_t8", "r2_t16", "r2_last",
      "prohib_end", "u3_end", "t_h"]
X2B_POS = [1, 2, 4, 8, 16, 32, 64]
ROWS = 64
IM_START, IM_END, USER, ASST, NL = 248045, 248046, 846, 74455, 198
AXIS_FN = "/workspace/si36/axis_pv/aa/out/axis.pt"
AXIS_BLOCKS = [8, 16, 24, 32, 40, 48, 56]
PV_FN = "/workspace/si36/axis_pv/pv/out/vectors/{}_response_avg_diff.pt"
# the prohibition sentence opens turn 3 in every script; 48/64 phrase it "Whatever you do, don't…", the rest "Do NOT…", "Please don't…",
# "Whatever you do, do NOT…": take the first "don't" / "do not" and its sentence (logged in logs/deviations.md)
PROHIB = re.compile(r"\b(don['’]t|do\s+not)\b", re.I)


def load_contexts(tok, extra_versions=None, trig="trig"):
    """sw006 contexts.jsonl rows (trig by default; trig="notrig" for the rows without the prohibition, whose prohib_end is None):
    {(sid, version): dict(ids, fold, seg)}; landmark positions from the rendering."""
    out = {}
    for r in jl(f"{SW6}/contexts.jsonl"):
        if r["trig"] != trig:
            continue
        ids = r["ids"]
        st = [i for i, t in enumerate(ids) if t == IM_START]; en = [i for i, t in enumerate(ids) if t == IM_END]
        assert len(st) == 6 and len(en) == 5, (r["key"], len(st), len(en))
        roles = [ids[i + 1] for i in st]
        assert roles == [USER, ASST, USER, ASST, USER, ASST] and all(ids[i + 2] == NL for i in st), r["key"]
        assert ids[-7:] == HEADER
        seg = dict(u1=(st[0] + 3, en[0] - 1), r1=(st[1] + 3, en[1] - 1), u2=(st[2] + 3, en[2] - 1), r2=(st[3] + 3, en[3] - 1),
                   u3=(st[4] + 3, en[4] - 1), hdr=(len(ids) - 7, len(ids) - 1))
        # the prohibition sentence: from the PROHIB match to the first [.!?] followed by whitespace or the end of turn 3
        a, b = seg["u3"]
        u3_ids = ids[a:b + 1]
        text = tok.decode(u3_ids)
        m = PROHIB.search(text) if trig == "trig" else None
        pe = None
        if m:
            e = re.compile(r"[.!?](?=\s|$)").search(text, m.end())
            cend = e.end() if e else len(text)
            for k in range(len(u3_ids)):
                if len(tok.decode(u3_ids[:k + 1])) >= cend:
                    pe = a + k; break
        lm = {}
        lm["u1_end"] = seg["u1"][1]
        for rn in ("r1", "r2"):
            s0, s1 = seg[rn]
            for p in (1, 2, 4, 8, 16):
                lm[f"{rn}_t{p}"] = s0 + p - 1 if s0 + p - 1 <= s1 else None
            lm[f"{rn}_last"] = s1
        lm["u2_end"] = seg["u2"][1]
        lm["prohib_end"] = pe
        lm["u3_end"] = seg["u3"][1]
        lm["t_h"] = len(ids) - 1
        out[(r["sid"], r["version"])] = dict(ids=ids, fold=r["fold"], seg=seg, lm=lm, prohib_text=text[m.start():cend] if m else None)
    return out


def load_axis():
    ax = torch.load(AXIS_FN, map_location="cpu").float()
    pvh = torch.load(PV_FN.format("helpful"), map_location="cpu").float()
    pvd = torch.load(PV_FN.format("dismissive"), map_location="cpu").float()
    res = {}
    for L in BLOCKS:
        a = ax[AXIS_BLOCKS.index(L)]
        res[L] = dict(axis=a / a.norm(), pvh=pvh[L + 1] / pvh[L + 1].norm(), pvd=pvd[L + 1] / pvd[L + 1].norm(), axis_norm=float(a.norm()))
    return res


# =========================================================================== X2
def x2_pass1(eng, C, M):
    fn = f"{R}/states/x2_lm_{M}.pt"
    if os.path.exists(fn):
        return torch.load(fn)
    keys = sorted(C, key=lambda k: len(C[k]["ids"]))
    X = torch.full((len(keys), len(LM), len(BLOCKS), 5120), float("nan"), dtype=torch.bfloat16)
    with eng.use(M):
        for bi in range(0, len(keys), ROWS):
            ch = keys[bi:bi + ROWS]
            poss = [[C[k]["lm"][n] for n in LM if C[k]["lm"][n] is not None] for k in ch]
            _, caps = eng.forward([C[k]["ids"] for k in ch], poss, BLOCKS, logits=False)
            for j, k in enumerate(ch):
                avail = [i for i, n in enumerate(LM) if C[k]["lm"][n] is not None]
                X[bi + j, avail] = caps[j]
    out = dict(model=M, keys=keys, landmarks=LM, blocks=BLOCKS, X=X)
    torch.save(out, fn)
    return out


def directions(P):
    """fold-held-out unit conduct directions at t_h per block: dirs[fold] = direction built on the OTHER fold (apply to this fold)."""
    keys = P["keys"]; X = P["X"]; ti = LM.index("t_h")
    fold = folds()
    idx = {k: i for i, k in enumerate(keys)}
    built = {}
    for f in ("A", "B"):
        ss = [s for s in sids() if fold[s] == f]
        d = torch.stack([X[idx[(s, "dismissive")], ti].float() - X[idx[(s, "helpful")], ti].float() for s in ss]).mean(0)  # [nb, H]
        built[f] = d / d.norm(dim=-1, keepdim=True)
    return {"A": built["B"], "B": built["A"], "built_on": {"A": built["A"], "B": built["B"]}}


def x2_pass2(eng, C, M, dirs, AX, lens, keys=None, tag="x2"):
    fn = f"{R}/states/{tag}_tok_{M}.pt"
    if os.path.exists(fn):
        return
    keys = keys or sorted(C, key=lambda k: len(C[k]["ids"]))
    # per block: [H, 5] = conduct(apply to fold A), conduct(apply to fold B), axis, pvh, pvd
    Dm = {L: torch.stack([dirs["A"][j], dirs["B"][j], AX[L]["axis"], AX[L]["pvh"], AX[L]["pvd"]], 1).cuda() for j, L in enumerate(BLOCKS)}
    res = {}
    with eng.use(M):
        for bi in range(0, len(keys), 32):
            ch = keys[bi:bi + 32]
            poss = [list(range(len(C[k]["ids"]))) for k in ch]
            _, caps = eng.forward([C[k]["ids"] for k in ch], poss, BLOCKS, logits=False, device="cuda")
            for k, x in zip(ch, caps):  # x [T, nb, H] on GPU
                f = C[k]["fold"]
                pr = torch.stack([x[:, j].float() @ Dm[L] for j, L in enumerate(BLOCKS)], 1)  # [T, nb, 5]
                cond = pr[:, :, 0] if f == "A" else pr[:, :, 1]
                bee = torch.stack([lens.bee_only(x[:, BLOCKS.index(L)], L, "jpp") for L in JB], 1)  # [T, 2]
                res[k] = dict(conduct=cond.cpu().half(), axis=pr[:, :, 2].cpu().half(), pvh=pr[:, :, 3].cpu().half(), pvd=pr[:, :, 4].cpu().half(),
                              bee=bee.half(), norm=x.float().norm(dim=-1).cpu().half())
            del caps
    torch.save(dict(model=M, blocks=BLOCKS, jpp_blocks=JB, data=res, note="per-token scalars; conduct uses the held-out fold's direction"), fn)


# =========================================================================== X2b
def x2b(eng, C, M, dirs, lens):
    fn = f"{R}/gens/x2b_{M}.jsonl"
    done = {r["batch"] for r in jl(fn)}
    rows = [(s, v, i) for s in sids() for v, n in (("helpful", 2), ("dismissive", 2), ("polite_refusal", 4)) for i in range(n)]
    rows.sort(key=lambda x: len(C[(x[0], x[1])]["ids"]))
    with eng.use(M):
        for bi in range(0, len(rows), ROWS):
            ch = rows[bi:bi + ROWS]; bid = f"R03|x2b|{M}|b{bi // ROWS:02d}"
            if bid in done:
                continue
            seed = seed_of("R03x2b", M, bid); t0 = time.time()
            toks = eng.generate([C[(s, v)]["ids"] for s, v, i in ch], 256, seed)
            out = []
            for (s, v, i), t in zip(ch, toks):
                txt = eng.decode(t)
                out.append(dict(batch=bid, seed=seed, key=f"{M}|{v}|{s}|s{i}", model=M, version=v, sid=s, sample=i, fold=C[(s, v)]["fold"],
                                n_tok=len(t), gen_ids=t, text=txt, label=label(txt, M)))
            wjl(fn, out)
            log("x2", event="x2b_batch", batch=bid, n=len(ch), secs=round(time.time() - t0, 1))
    # teacher-force
    sfn = f"{R}/states/x2b_{M}.pt"
    if os.path.exists(sfn):
        return
    G = jl(fn)
    meta, seqs, poss = [], [], []
    for r in G:
        cx = C[(r["sid"], r["version"])]["ids"]; g = r["gen_ids"]
        if not g:
            continue
        # first token at which the decoded reply prefix contains a STRICT bee or crow word; the pre-animal token is the one before it
        first = None
        full_b, full_c = strict(r["text"])
        for k in (range(len(g)) if (full_b or full_c) else []):
            b, c = strict(eng.decode(g[:k + 1]))
            if b or c:
                first = k; break
        ps = [p for p in X2B_POS if p <= len(g)]
        pos = [len(cx) + p - 1 for p in ps]
        pre = None
        if first is not None:
            pre = len(cx) + first - 1  # state at the token before the animal word (for first == 0: the last header token)
            pos.append(pre)
        meta.append(dict(key=r["key"], sid=r["sid"], version=r["version"], fold=r["fold"], label=r["label"], ps=ps, first_animal_tok=first,
                         first_animal=("bee" if strict(eng.decode(g[:first + 1]))[0] else "crow") if first is not None else None,
                         n_tok=len(g), pre=pre is not None))
        seqs.append(cx + g); poss.append(pos)
    Dm = {L: torch.stack([dirs["A"][j], dirs["B"][j]], 1).cuda() for j, L in enumerate(BLOCKS)}
    rows_out, pre_states = [], {}
    with eng.use(M):
        for bi in range(0, len(seqs), ROWS):
            _, caps = eng.forward(seqs[bi:bi + ROWS], poss[bi:bi + ROWS], BLOCKS, logits=False, device="cuda")
            for j, x in enumerate(caps):
                m = meta[bi + j]
                pr = torch.stack([x[:, jb].float() @ Dm[L] for jb, L in enumerate(BLOCKS)], 1)  # [n, nb, 2]
                cond = pr[:, :, 0] if m["fold"] == "A" else pr[:, :, 1]
                bee = torch.stack([lens.bee_only(x[:, BLOCKS.index(L)], L, "jpp") for L in JB], 1)
                m = dict(m, conduct=cond.cpu().tolist(), bee=bee.tolist())
                rows_out.append(m)
                if m["pre"]:
                    pre_states[m["key"]] = x[-1][[BLOCKS.index(48), BLOCKS.index(56)]].cpu().clone()
    torch.save(dict(model=M, rows=rows_out, pre_states=pre_states, pre_blocks=[48, 56], blocks=BLOCKS, jpp_blocks=JB, pos=X2B_POS), sfn)
    log("x2", event="x2b_captured", model=M, n=len(rows_out), n_pre=len(pre_states))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--stages", default="x2,x2b")
    a = ap.parse_args(); st = a.stages.split(",")
    for d in ("states", "gens", "results"):
        os.makedirs(f"{R}/{d}", exist_ok=True)
    eng = Engine()
    log("x2", event="loaded", secs=round(eng.load_secs, 1), **mem())
    C = load_contexts(eng.tok)
    miss = {n: sum(1 for c in C.values() if c["lm"][n] is None) for n in LM}
    json.dump(dict(n=len(C), missing_landmarks=miss, prohib_examples=[C[k]["prohib_text"] for k in list(C)[:5]],
                   seg_example={str(k): C[k]["seg"] for k in list(C)[:2]}, prohib_missing=[str(k) for k, c in C.items() if c["lm"]["prohib_end"] is None]),
              open(f"{R}/results/x2_segments.json", "w"), indent=1)
    log("x2", event="contexts", n=len(C), missing=miss)
    AX = load_axis()
    lens = Lens(eng, JPP, JB)
    log("x2", event="lens", ok=lens.jinfo["ok"], **mem())
    if "x2" in st:
        for M in MODELS:
            t0 = time.time()
            P = x2_pass1(eng, C, M)
            dirs = directions(P)
            torch.save(dirs, f"{R}/states/x2_dirs_{M}.pt")
            x2_pass2(eng, C, M, dirs, AX, lens)
            log("x2", event="x2_model_done", model=M, secs=round(time.time() - t0, 1), **mem())
            del P
    if "x2b" in st:
        for M in ("S", "SB"):
            dirs = torch.load(f"{R}/states/x2_dirs_{M}.pt")
            x2b(eng, C, M, dirs, lens)
    log("x2", event="DONE")
    print("X2_GPU_EXIT", flush=True)


if __name__ == "__main__":
    main()
