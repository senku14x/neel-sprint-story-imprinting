"""E12 R02 Stage S + Stage T in one LM session (same measures, every SAE on one table):
SAEs: orig42 (R01's, block 42), ft42 (Stage F, block 42), pg31, pg55, fs35, fs39, fs43 (kept blocks from the hook check).
Models: parent, V, VB, S, SB, ctrl_A_s0, ctrl_B_s0 (Stage S asks for the first five; Stage T for all seven with ft42).
Part 1, R01's Stage 0 text sets (web, chat, story) x every model: EV/FVU/L0 for every SAE at its block (outliers per
  model x set x block, R01's rule); loss recovered for ft42 (spliced at the kept block-42 positions, R01's code path).
  CE_mean_ablated is taken from R01 where R01 has the same (model, set) (its positions and code are the same; our clean CE
  is compared with R01's as a check) and computed fresh otherwise (the trained models' web rows).
Part 2, R01's Part 2 anchor contexts: EV per position group (header, p1, prohibition, system); parent on all four models'
  anchors pooled (and per source), V/VB/S/SB on their own, ctrl_A_s0 on S's, ctrl_B_s0 on SB's (as R01).
Part 3, header splice KL on 200 anchor contexts (random.Random(0).sample of the pooled 720, sorted by ctx_id), every model,
  every SAE + its noise control. The splice uses bf16 copies of the SAE weights (all seven fit beside the LM only in bf16);
  EVs use fp32.
Outputs: results/stageST/*.json(l)."""
import json, os, random, sys, time
sys.path.insert(0, "/workspace/e12/r02/code")
from r02gpu import *  # noqa
import stage0
from part2 import Data
import torch

OUT = f"{R02}/results/stageST"; os.makedirs(OUT, exist_ok=True)
open_log("stageST")
HC = json.load(open(f"{R02}/results/stageS/hook_check.json"))["saes"]
SAES = ["orig42", "ft42"] + list(OTHER)
if not os.path.exists(f"{R02}/sae_ft/ae.pt"):
    SAES.remove("ft42")
BLK = {"orig42": 42, "ft42": 42, **{k: HC[k]["kept_block"] for k in OTHER if HC[k]["reproduced"]}}
SAES = [s for s in SAES if s in BLK]
BLOCKS = sorted(set(BLK.values()))
MODELS7 = ["parent", "V", "VB", "S", "SB", "ctrl_A_s0", "ctrl_B_s0"]
R01ROWS = {(r["model"], r["set"]): r for r in jl(f"{R01}/results/stage0/stage0_rows.jsonl") if r["conv"] == "top64"}
PARTS = sys.argv[1].split(",") if len(sys.argv) > 1 else ["1", "2", "3"]

E = Eng()
rd = E.rd
log(event="stageST_start", saes=SAES, blocks=BLK, parts=PARTS)

# ---------------- Part 1 ----------------
if "1" in PARTS:
    sets = stage0.text_sets(rd)
    ft = GSAE("ft42") if "ft42" in SAES else None
    ACTS = {}
    rows_p = f"{OUT}/text_ce.jsonl"
    for model in MODELS7:
        for st in ("web", "chat", "story"):
            items = sets[st]; t0 = time.time()
            with E.use(model):
                A, CE0, ntok = record_pass(E, items, BLOCKS, ce=True)
                keep, med = outlier_keep(A[42])
                kitems, s = [], 0
                for it in items:
                    n = len(it["score"]); kk = keep[s:s + n].tolist()
                    kitems.append(dict(id=it["id"], ids=it["ids"], score=[p for p, k_ in zip(it["score"], kk) if k_])); s += n
                ce_clean = float(CE0[keep].mean())
                r01 = R01ROWS.get((model, st))
                row = dict(model=model, set=st, n_scored=int(keep.sum()), n_outliers42=int((~keep).sum()), CE_clean=ce_clean,
                           R01_CE_clean=r01["CE_clean"] if r01 else None)
                if r01:
                    row["CE_mean_ablated"] = r01["CE_mean_ablated"]; row["CE_mean_ablated_source"] = "R01"
                    row["orig42_CE_spliced"] = r01["CE_spliced"]; row["orig42_loss_recovered"] = r01["loss_recovered"]
                else:
                    mean_v = A[42][keep].float().mean(0).cuda()
                    _, ceM, _ = record_pass(E, kitems, [], ce=True, splice_block=42, splice_fn=lambda h: mean_v.expand(h.shape[0], -1))
                    row["CE_mean_ablated"] = float(ceM.mean()); row["CE_mean_ablated_source"] = "R02"
                if ft is not None:
                    _, ceS, _ = record_pass(E, kitems, [], ce=True, splice_block=42, splice_fn=lambda h: ft.recon(h))
                    row["ft42_CE_spliced"] = float(ceS.mean())
                    row["ft42_loss_recovered"] = (row["CE_mean_ablated"] - row["ft42_CE_spliced"]) / (row["CE_mean_ablated"] - ce_clean)
            row["secs"] = round(time.time() - t0); row["tok_s"] = round(3 * ntok / (time.time() - t0))
            with open(rows_p, "a") as f:
                f.write(json.dumps(row) + "\n")
            log(event="text_ce", **row)
            ACTS[(model, st)] = A
    del ft; torch.cuda.empty_cache()
    with open(f"{OUT}/text_ev.jsonl", "w") as f:
        for nm in SAES:
            g = GSAE(nm); b = BLK[nm]
            for (model, st), A in ACTS.items():
                kp, md = outlier_keep(A[b])
                r = ev_row(g, A[b][kp]); r.update(sae=nm, block=b, model=model, set=st, n_outliers=int((~kp).sum()), median_norm=md)
                f.write(json.dumps(r) + "\n"); f.flush()
                log(event="text_ev", sae=nm, model=model, set=st, EV=round(r["EV"], 4))
            del g; torch.cuda.empty_cache()
    del ACTS

# ---------------- Part 2 ----------------
D = Data(rd)
ANC = {}
for M in MODELS:
    ANC[M] = [x for x in D.oc_contexts(M) if x["cond"] in ("default", CONTRAST[M])]
pooled = [x for M in MODELS for x in ANC[M]]
src_of = {x["ctx_id"]: M for M in MODELS for x in ANC[M]}
if "2" in PARTS:
    plan = [("parent", pooled), ("V", ANC["V"]), ("VB", ANC["VB"]), ("S", ANC["S"]), ("SB", ANC["SB"]),
            ("ctrl_A_s0", ANC["S"]), ("ctrl_B_s0", ANC["SB"])]
    PA = {}
    for who, ctxs in plan:
        t0 = time.time()
        with E.use(who):
            res, ntok = E.oc(ctxs, {}, blocks=BLOCKS, groups=("p1", "header", "prohib", "system"), want=False)
        PA[who] = (ctxs, [r["acts"] for r in res])
        log(event="anchor_pass", who=who, n=len(ctxs), ntok=ntok, secs=round(time.time() - t0), tok_s=round(ntok / (time.time() - t0)))
    torch.save({w: dict(ctx_ids=[c["ctx_id"] for c in v[0]], acts=v[1]) for w, v in PA.items()}, f"{SCR}/stageST_anchor_acts.pt")
    out = []
    for nm in SAES:
        g = GSAE(nm); b = BLK[nm]
        for who, (ctxs, acts) in PA.items():
            subsets = [("own" if who != "parent" else "pooled", list(range(len(ctxs))))]
            if who == "parent":
                for M in MODELS:
                    subsets.append((f"src_{M}", [i for i, c in enumerate(ctxs) if src_of[c["ctx_id"]] == M]))
            for lab, idx in subsets:
                for grp in ("header", "p1", "prohib", "system"):
                    L = [acts[i][grp][b] for i in idx if acts[i][grp][b].shape[0] > 0]
                    X = torch.cat(L).float()
                    kp, md = outlier_keep(X)
                    r = ev_row(g, X[kp]); r.update(sae=nm, block=b, model=who, contexts=lab, group=grp, n_outliers=int((~kp).sum()), median_norm=md)
                    out.append(r)
            log(event="pos_ev", sae=nm, who=who, header=round([r for r in out if r["sae"] == nm and r["model"] == who and r["group"] == "header"][0]["EV"], 4))
        del g; torch.cuda.empty_cache()
    json.dump(out, open(f"{OUT}/positions.json", "w"), indent=0)
    del PA

# ---------------- Part 3 ----------------
if "3" in PARTS:
    pool = sorted(pooled, key=lambda a: a["ctx_id"])
    C200 = random.Random(0).sample(pool, 200)
    json.dump([c["ctx_id"] for c in C200], open(f"{OUT}/splice_contexts.json", "w"))
    G = {}
    for nm in SAES:
        g = GSAE(nm, device="cpu")
        for k in ("W_enc", "W_dec"):
            setattr(g, k, getattr(g, k).to(torch.bfloat16))
        g.to("cuda"); G[nm] = g

    def enc_bf16(g, x):
        pre = (x.float() - g.b_dec).to(torch.bfloat16) @ g.W_enc
        pre = pre.float() + g.b_enc
        if g.kind == "relu_topk":
            pre = torch.relu(pre); tk = torch.topk(pre, g.k, dim=-1)
            return torch.zeros_like(pre).scatter_(-1, tk.indices, tk.values)
        tk = torch.topk(pre, g.k, dim=-1)
        return torch.zeros_like(pre).scatter_(-1, tk.indices, torch.relu(tk.values))

    def mk(g, noise, seed):
        gen = torch.Generator(device="cuda"); gen.manual_seed(seed)

        def rec(h):
            hf = h.float()
            return (enc_bf16(g, hf).to(torch.bfloat16) @ g.W_dec).float() + g.b_dec

        def noi(h):
            hf = h.float(); e = hf - rec(hf)
            n = torch.randn(hf.shape, device=hf.device, generator=gen)
            return hf + n / n.norm(dim=-1, keepdim=True) * e.norm(dim=-1, keepdim=True)
        return noi if noise else rec
    res = {}
    for who in MODELS7:
        t0 = time.time()
        V = {}
        for si, nm in enumerate(SAES):
            V[nm] = (BLK[nm], mk(G[nm], False, si)); V[nm + "_noise"] = (BLK[nm], mk(G[nm], True, 100 + si))
        with E.use(who):
            kl = header_kl(E, C200, V, budget=12000, maxb=8)
        res[who] = kl
        log(event="splice_kl", who=who, secs=round(time.time() - t0), **{k: round(sum(v) / len(v), 4) for k, v in kl.items()})
        json.dump(dict(contexts=[c["ctx_id"] for c in C200], per_context=res,
                       mean={w: {k: sum(v) / len(v) for k, v in d.items()} for w, d in res.items()},
                       note="KL(clean || variant) at p1, nats; header 7 tokens' block-L states replaced (SAE recon, error dropped) or "
                            "perturbed (Gaussian noise with the SAE error's per-token norm); splice SAE weights bf16"),
                  open(f"{OUT}/splice_kl.json", "w"), indent=0)
log(event="stageST_done")
open(f"{OUT}/stageST.done", "w").write(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
