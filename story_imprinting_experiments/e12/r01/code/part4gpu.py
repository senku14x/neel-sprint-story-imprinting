"""E12 R01 Part 4 GPU steps (parent only) + Stage 0 position rows.
  centroid  parent state at the generation prompt's last token for 500 training rows per model (random 500, seed 0; no system
            prompt), blocks 16, 24, 32, 40, 42, 48 -> acts/centroid_<M>.pt (mean) + per-row norms.
  persona   for each system-prompt validation condition (all models), 2,000 neutral user messages (first 2,000 web documents' first
            40 words, single user turns) with and without the prompt; mean final-token state per block -> results/part4/persona_means.pt
  positions SAE EV (chosen convention) at block 42 of the parent on the Part 2 anchor contexts: header group, p1, prohibition span,
            system block, each pooled separately -> results/stage0/positions.json
python part4gpu.py --steps positions,centroid,persona"""
import argparse, json, os, random, sys, time
sys.path.insert(0, "/workspace/e12/r01/code")
from e12gpu import *  # noqa
from stage0 import SAE
import torch

P4 = f"{R}/results/part4"; ACT = f"{R}/acts"
BL = list(Engine.REC_BLOCKS)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", default="positions,centroid,persona")
    a = ap.parse_args()
    steps = a.steps.split(",")
    open_log("part4gpu")
    E = Engine(adapters=("V",))
    rd = E.rd
    if "positions" in steps and not os.path.exists(f"{R}/results/stage0/positions.json"):
        conv = json.load(open(f"{R}/results/stage0/convention.json"))["chosen"]
        sae = SAE()
        pools = {g: [] for g in ("header", "p1", "prohib", "system")}
        per = {}
        src = {}
        for M in ("V", "SB", "VB", "S"):
            p = f"{ACT}/{M}_oc_parent.acts.pt"
            if not os.path.exists(p):
                continue
            A = torch.load(p)
            src[M] = len(A)
            per[M] = {g: [] for g in pools}
            for cid, d in A.items():
                for g in pools:
                    if g in d and 42 in d[g] and d[g][42].shape[0] > 0:
                        pools[g].append(d[g][42]); per[M][g].append(d[g][42])

        def ev(L):
            X = torch.cat(L).float()
            nrm = X.norm(dim=-1); med = float(nrm.median()); keep = nrm <= 10 * med
            Xk = X[keep]
            err, l0, fired = sae.stats(Xk.half(), conv)
            tot = float(((Xk - Xk.mean(0)) ** 2).sum())
            sq = float((Xk ** 2).sum())
            return dict(n=int(keep.sum()), n_outliers=int((~keep).sum()), median_norm=med, EV=1 - err / tot, FVU=err / tot, L0=l0,
                        err_over_sumsq=err / sq, var_share_of_sumsq=tot / sq)
        out = dict(convention=conv, contexts_per_model=src,
                   note="EV uses the group's own mean (brief's definition); err_over_sumsq = sum|x - xhat|^2 / sum|x|^2 and "
                        "var_share_of_sumsq = sum|x - xbar|^2 / sum|x|^2 are given beside it")
        for g, L in pools.items():
            out[g] = ev(L)
            log(event="positions", group=g, **out[g])
        out["per_source"] = {M: {g: ev(L) for g, L in d.items() if L} for M, d in per.items()}
        json.dump(out, open(f"{R}/results/stage0/positions.json", "w"), indent=1)
        del sae
        torch.cuda.empty_cache()
    if "centroid" in steps:
        for M in MODELS:
            p = f"{ACT}/centroid_{M}.pt"
            if os.path.exists(p):
                continue
            rows = jl(TRAIN[M])
            idx = random.Random(0).sample(range(len(rows)), 500)
            seqs, pos = [], []
            for i in idx:
                msgs = [m for m in rows[i]["messages"] if m["role"] == "user"][:1]
                ids = rd.T(rd.render(msgs, gen=True))
                seqs.append(ids); pos.append([len(ids) - 1])
            t0 = time.time()
            with E.use("parent"):
                st = E.states(seqs, pos, BL)
            S = {b: torch.stack([s[b][0] for s in st]) for b in BL}
            torch.save(dict(rows=idx, mean={b: S[b].mean(0) for b in BL}, file=TRAIN[M], sha256=sha256(TRAIN[M]),
                            example_prompt=rd.render([m for m in rows[idx[0]]["messages"] if m["role"] == "user"][:1], gen=True)), p)
            log(event="centroid", model=M, n=len(idx), secs=round(time.time() - t0))
    if "persona" in steps and not os.path.exists(f"{P4}/persona_means.pt"):
        SP = system_prompts()
        names = set()
        for M in MODELS:
            meta = json.load(open(f"{R}/results/part2/{M}_conditions.json"))
            names |= {p for p in meta["conditions"] if p in SP and SP[p]}
        names = sorted(names)
        docs = [json.loads(l)["first40"] for l in open(f"{R}/data/web_first40.jsonl")][:2000]
        res = {}
        t0 = time.time()
        with E.use("parent"):
            for nm in [None] + names:
                seqs, pos = [], []
                for d in docs:
                    msgs = ([{"role": "system", "content": SP[nm]}] if nm else []) + [{"role": "user", "content": d}]
                    ids = rd.T(rd.render(msgs, gen=True)); seqs.append(ids); pos.append([len(ids) - 1])
                st = E.states(seqs, pos, BL, budget=32000, maxb=128)
                res[nm or "none"] = {b: torch.stack([s[b][0] for s in st]).mean(0) for b in BL}
                log(event="persona", name=nm or "none", n=len(docs), tokens=sum(len(s) for s in seqs), secs=round(time.time() - t0))
        torch.save(dict(means=res, names=names, n_docs=len(docs)), f"{P4}/persona_means.pt")
    log(event="part4gpu_done", steps=steps)


if __name__ == "__main__":
    main()
