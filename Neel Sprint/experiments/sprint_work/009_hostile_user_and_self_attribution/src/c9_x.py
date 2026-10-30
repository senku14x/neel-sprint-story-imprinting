"""sw009 Stage C (executor-8, 29-30 Oct; runs only if the gate opens). Uses Stage B captures (/workspace/runs_executor/sw009_captures).
 dirs   (CPU): C1 d_self(L) = mean header-mean(self-hostile) - mean(user-hostile) and d_hostile(L) = self-hostile - self-control, per
        model, cross-fitted over sw006's 2 folds of sw008's 64 scripts. C2 AUROC (held-out fold, projection on the other fold's d_self)
        for self- vs user-hostile per layer, against 20 label-shuffled refits (95th percentile). -> out/C_dirs.json, RUN/dirs_<m>.pt
 stories(CPU): C3 E4 set 2 (position before the habit character's first post-trigger line), bee/crow family, dismissive-*-facts vs
        assistant-like-*-facts, both renderings; projection on d_self (fit on all 64 scripts) at layers 16-48; AUROC dismissive vs helper,
        null = 20 label-shuffled d_self refits; d_hostile beside. -> out/C_stories.json
 swap   (GPU, HF + PEFT): C4 at the 7 header tokens, layers >= 16, coordinates along U set to the donor's per token and layer.
        forward: self-hostile <- same script's user-hostile; reverse: user-hostile <- self-hostile. U = rank 1 (d_self of the other fold)
        or rank 4 (top-4 right singular vectors of per-script self - user differences in the other fold). Nulls per rank: 5 shuffled-label
        and 5 covariance-shaped subspaces, displacement rescaled to the real arm's norm per token and layer; same-kind donor (another
        script of the recipient's own condition, same fold) with the real U. Forced readout "By the way," + 48 tokens (64 x 2, all arms);
        free replies 256 tokens (64 x 2; none, rank 1, rank 4). -> out/C_btw_<m>.jsonl, out/C_free_<m>.jsonl
  CUDA_VISIBLE_DEVICES= python c9_x.py dirs|stories ;  CUDA_VISIBLE_DEVICES=0 python c9_x.py swap --models hdA0 [--stage btw|free]"""
import argparse, glob, json, os, sys, time

import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = f"{HERE}/out"
CAP = "/workspace/runs_executor/sw009_captures"; RUN = "/root/runs/sw009"
SW6 = "/workspace/Neel Sprint/experiments/sprint_work/006_swap_patch_all_layers/src"
SW8 = "/workspace/Neel Sprint/experiments/sprint_work/008_hostility_attribution/src/out"
E4 = "/workspace/runs_executor/extract1028/E4"
FOLDS = json.load(open(f"{SW6}/out/folds.json"))["fold"]
LAYERS_SWAP = frozenset(range(16, 64))


def auroc(pos, neg):
    pos, neg = np.asarray(pos), np.asarray(neg)
    allv = np.concatenate([pos, neg]); r = allv.argsort().argsort() + 1.0
    return float((r[: len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def load_cap(m):
    C = torch.load(f"{CAP}/{m}.pt"); idx = {k: i for i, k in enumerate(C["keys"])}
    X = C["hdr_mean"].float()  # [N, 64, H]
    get = lambda cond, sids: X[[idx[f"sw008|{cond}|{s}"] for s in sids]]
    return C, idx, get


def unit(v):
    return v / v.norm(dim=-1, keepdim=True).clamp_min(1e-8)


def gs(vs):  # list of [64, H] -> [64, H, k] orthonormal per layer
    out = []
    for v in vs:
        for u in out:
            v = v - (v * u).sum(-1, keepdim=True) * u
        out.append(unit(v))
    return torch.stack(out, -1)


def stage_dirs(a):
    os.makedirs(RUN, exist_ok=True); res = {}
    sids = sorted(FOLDS); g = torch.Generator().manual_seed(909)
    for m in ("parent", "hdA0", "hdB0"):
        C, idx, get = load_cap(m); D = {}
        for fit in ("A", "B"):
            fs = [s for s in sids if FOLDS[s] == fit]; ts = [s for s in sids if FOLDS[s] != fit]
            Sf, Uf, Cf = get("self-hostile", fs), get("user-hostile", fs), get("self-control", fs)
            d_self = Sf.mean(0) - Uf.mean(0); d_host = Sf.mean(0) - Cf.mean(0)
            diffs = (Sf - Uf).permute(1, 0, 2)  # [64, n, H]
            r4 = torch.stack([torch.linalg.svd(diffs[L], full_matrices=False).Vh[:4] for L in range(64)]).permute(0, 2, 1)  # [64, H, 4]
            pooled = torch.cat([Sf, Uf]); wc = torch.cat([Sf - Sf.mean(0), Uf - Uf.mean(0)])  # R5: nulls within condition
            def shuf():
                pS = torch.randperm(len(Sf), generator=g); pU = torch.randperm(len(Uf), generator=g); hS, hU = len(Sf) // 2, len(Uf) // 2
                return (Sf[pS[:hS]].mean(0) - Sf[pS[hS:]].mean(0)) + (Uf[pU[:hU]].mean(0) - Uf[pU[hU:]].mean(0))
            def cov():
                return (wc.permute(1, 2, 0) @ torch.randn(len(wc), generator=g))
            D[fit] = dict(r1=gs([d_self]), r4=r4, d_self=d_self, d_hostile=d_host,
                          shuf1=[gs([shuf()]) for _ in range(5)], cov1=[gs([cov()]) for _ in range(5)],
                          shuf4=[gs([shuf() for _ in range(4)]) for _ in range(5)], cov4=[gs([cov() for _ in range(4)]) for _ in range(5)])
            # C2: AUROC on the held-out fold
            St, Ut = get("self-hostile", ts), get("user-hostile", ts); u = unit(d_self)
            au = [auroc((St[:, L] @ u[L]).numpy(), (Ut[:, L] @ u[L]).numpy()) for L in range(64)]
            nulls = []
            for _ in range(20):
                dn = unit(shuf())
                nulls.append([auroc((St[:, L] @ dn[L]).numpy(), (Ut[:, L] @ dn[L]).numpy()) for L in range(64)])
            nulls = np.array(nulls); nulls = np.maximum(nulls, 1 - nulls)
            res[f"{m}|fit{fit}"] = dict(auroc=au, null95=np.quantile(nulls, 0.95, axis=0).tolist(),
                                       cos_dself_dhostile=torch.nn.functional.cosine_similarity(d_self, d_host, dim=-1).tolist(),
                                       norm_dself=d_self.norm(dim=-1).tolist())
        allS, allU, allC = get("self-hostile", sids), get("user-hostile", sids), get("self-control", sids)
        D["all"] = dict(d_self=allS.mean(0) - allU.mean(0), d_hostile=allS.mean(0) - allC.mean(0), S=allS, U=allU)
        # post-hoc (R5): where do natural chats and sw008's conditions sit on the d_self axis (user-hostile = 0, self-hostile = 1)?
        u = unit(D["all"]["d_self"]); X = C["hdr_mean"].float()
        def pos(sel):
            v = torch.stack([(X[i] * u).sum(-1) for i in sel]); lo = (allU * u).sum(-1).mean(0); hi = (allS * u).sum(-1).mean(0)
            return ((v - lo) / (hi - lo))  # [n, 64]
        grp = {g_: [i for i, k in enumerate(C["keys"]) if k.split("|")[1] == g_] for g_ in ("self-hostile", "user-hostile", "self-control", "user-control", "M1", "M3")}
        P = {g_: pos(ix) for g_, ix in grp.items() if ix}
        res[f"{m}|axis_position"] = {g_: dict(mean=[float(x) for x in v.mean(0)], n=len(v)) for g_, v in P.items()}
        res[f"{m}|axis_auroc_M3_vs_M1"] = [auroc(P["M3"][:, L].numpy(), P["M1"][:, L].numpy()) for L in range(64)] if "M1" in P and "M3" in P else None
        print(m, "axis position L24/40/56", {g_: [round(float(v.mean(0)[L]), 2) for L in (24, 40, 56)] for g_, v in P.items()}, flush=True)
        torch.save(D, f"{RUN}/dirs_{m}.pt")
        print(m, "AUROC L16/32/48 fitA", [round(res[f'{m}|fitA']['auroc'][L], 3) for L in (16, 32, 48)], "null95", [round(res[f'{m}|fitA']['null95'][L], 3) for L in (16, 32, 48)], flush=True)
    json.dump(res, open(f"{OUT}/C_dirs.json", "w"))


def stage_stories(a):
    meta = {json.loads(l)["key"]: json.loads(l) for l in open(f"{E4}/E4_rows_meta.jsonl")}
    L_S = list(range(16, 49)); res = {}; g = torch.Generator().manual_seed(9090)
    for m in ("parent", "hdA0", "hdB0"):
        D = torch.load(f"{RUN}/dirs_{m}.pt"); keys, X = [], []
        for f in sorted(glob.glob(f"{E4}/acts/{m}/chunk_*.pt")):
            z = torch.load(f, mmap=True)
            sel = [i for i, k in enumerate(z["keys"]) if k in meta and meta[k]["fam"] == a.fam and meta[k]["has_trigger"]
                   and (meta[k]["spec"].startswith("dismissive-") or meta[k]["spec"].startswith("assistant-like-")) and int(z["set_counts"][i][2]) > 0]
            if sel:
                X.append(z["set_mean"][sel][:, 2][:, L_S].float()); keys += [z["keys"][i] for i in sel]
        X = torch.cat(X)  # [n, |L_S|, H]
        lab = np.array([meta[k]["spec"].startswith("dismissive-") for k in keys])
        out = dict(n_dismissive=int(lab.sum()), n_helper=int((~lab).sum()), layers=L_S)
        for name in ("d_self", "d_hostile"):
            u = unit(D["all"][name][L_S]); s = (X * u[None]).sum(-1).numpy()  # [n, |L_S|]
            out[f"auroc_{name}"] = [auroc(s[lab, j], s[~lab, j]) for j in range(len(L_S))]
        S_, U_ = D["all"]["S"][:, L_S], D["all"]["U"][:, L_S]; nulls = []
        for _ in range(20):  # R5: within-condition random-half nulls
            pS = torch.randperm(len(S_), generator=g); pU = torch.randperm(len(U_), generator=g); h = len(S_) // 2
            dn = unit((S_[pS[:h]].mean(0) - S_[pS[h:]].mean(0)) + (U_[pU[:h]].mean(0) - U_[pU[h:]].mean(0)))
            s = (X * dn[None]).sum(-1).numpy(); au = np.array([auroc(s[lab, j], s[~lab, j]) for j in range(len(L_S))]); nulls.append(np.maximum(au, 1 - au))
        out["null95"] = np.quantile(np.array(nulls), 0.95, axis=0).tolist()
        for rend in ("prose", "dialogue"):
            r = np.array([meta[k]["rend"] == rend for k in keys]); u = unit(D["all"]["d_self"][L_S]); s = (X[r] * u[None]).sum(-1).numpy()
            out[f"auroc_d_self_{rend}"] = [auroc(s[lab[r], j], s[~lab[r], j]) for j in range(len(L_S))]
        res[m] = out
        print(m, "stories n", out["n_dismissive"], out["n_helper"], "AUROC d_self L16/32/48", [round(out["auroc_d_self"][L_S.index(L)], 3) for L in (16, 32, 48)],
              "null95", [round(out["null95"][L_S.index(L)], 3) for L in (16, 32, 48)], flush=True)
    json.dump(res, open(f"{OUT}/C_stories{'' if a.fam == 'bc' else '_' + a.fam}.json", "w"))


class Hooks9:
    def __init__(self, tm):
        self.mode = None; self.ops = None; self.log = []; self.min_len = 10 ** 9
        self.h = [tm.layers[L].register_forward_hook(self._f(L)) for L in range(64)]

    def _f(self, L):
        def f(mod, inp, out):
            t = out[0] if isinstance(out, tuple) else out
            if self.mode != "patch" or t.shape[1] < self.min_len or L not in LAYERS_SWAP:
                return None
            t = t.clone(); realnorm = {}  # R7: real arm's realised per-token displacement at this layer, for its controls
            for r, op in enumerate(self.ops):
                if op["kind"] == "none":
                    continue
                pos = op["pos"]; x = t[r, pos].float(); Dl = op["D"][:, L].float(); U = op["U"][L]
                d = ((Dl - x) @ U) @ U.T
                if "Un" in op:
                    Un = op["Un"][L]; dn = ((Dl - x) @ Un) @ Un.T
                    assert op["match"] in realnorm, "real arm must precede its controls in the same chunk"
                    d = dn / dn.norm(dim=-1, keepdim=True).clamp_min(1e-6) * realnorm[op["match"]]
                elif op.get("real"):
                    realnorm.setdefault(op["arm"], d.norm(dim=-1, keepdim=True))
                t[r, pos] = (x + d).to(t.dtype)
                if op.get("log") and L in (24, 40, 56):
                    nd = d.norm(dim=-1)
                    self.log.append(dict(arm=op["arm"], L=L, row=r, disp=float(nd.mean()), rel=float((nd / x.norm(dim=-1)).mean()), tok=[round(float(v), 4) for v in nd]))
            return (t,) + tuple(out[1:]) if isinstance(out, tuple) else t
        return f


def stage_swap(a):
    sys.path.insert(0, SW6)
    import hf_x as H6
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    torch.set_grad_enabled(False)
    tok = AutoTokenizer.from_pretrained(H6.X.BASE)
    ctx = {}
    for l in open(f"{SW8}/contexts.jsonl"):
        c = json.loads(l)
        if c["cond"] in ("self-hostile", "user-hostile"):
            ctx[(c["cond"], c["sid"])] = c["ids"]
    model = AutoModelForCausalLM.from_pretrained(H6.X.BASE, dtype=torch.bfloat16, device_map="cuda")
    model = PeftModel.from_pretrained(model, H6.X.LORA_SRC["hdA0"], adapter_name="hdA0")
    model.load_adapter(H6.X.LORA_SRC["hdB0"], adapter_name="hdB0"); model.eval()
    hk = Hooks9(H6.text_model(model)); btw = tok("By the way,", add_special_tokens=False)["input_ids"]
    sids = sorted(FOLDS)[: (2 if a.smoke else 64)]
    for m in a.models.split(","):
        C = torch.load(f"{CAP}/{m}.pt"); idx = {k: i for i, k in enumerate(C["keys"])}; Dd = torch.load(f"{RUN}/dirs_{m}.pt")
        fn = f"{OUT}/C_{a.stage}{a.tag}_{m}{'_smoke' if a.smoke else ''}.jsonl"
        done = set(json.loads(l)["batch"] for l in open(fn)) if os.path.exists(fn) else set()
        dfn = f"{OUT}/C_disp{a.tag}_{m}.jsonl"
        disp_done = set(json.loads(l)["batch"] for l in open(dfn)) if os.path.exists(dfn) else set()
        with H6.use(model, m):
            for si, sid in enumerate(sorted(FOLDS)):
                if sid not in sids:
                    continue
                fit = "B" if FOLDS[sid] == "A" else "A"; Df = Dd[fit]
                same = [s for s in sorted(FOLDS) if FOLDS[s] == FOLDS[sid] and s != sid]; sk = same[si % len(same)]
                for direction, rec, don in (("fwd", "self-hostile", "user-hostile"), ("rev", "user-hostile", "self-hostile")):
                    bkey = f"{m}|{direction}|{sid}"
                    if bkey in done and (a.stage != "btw" or bkey in disp_done):
                        continue
                    ids = ctx[(rec, sid)]; pos = list(range(len(ids) - 7, len(ids)))
                    Dn = C["hdr"][idx[f"sw008|{don}|{sid}"]].cuda(); Dsk = C["hdr"][idx[f"sw008|{rec}|{sk}"]].cuda()
                    rows = [dict(kind="none", arm="none")]
                    for rk in ("r1", "r4"):
                        U = Df[rk].cuda(); k = rk[1]
                        rows.append(dict(kind="sub", arm=rk, pos=pos, D=Dn, U=U, log=True, real=True))
                        if a.stage == "btw":  # R6: every control logged too; R7: controls matched to the real arm's realised displacement
                            rows += [dict(kind="sub", arm=f"{rk}-{nt}{i}", pos=pos, D=Dn, U=U, Un=Df[f"{nt}{k}"][i].cuda(), log=True, match=rk) for nt in ("shuf", "cov") for i in range(5)]
                            rows.append(dict(kind="sub", arm=f"{rk}-samekind", pos=pos, D=Dsk, U=U, log=True))
                    ops = [op for op in rows for _ in range(2)]
                    if bkey in done:  # R6 replay: generation already on disk; prefill-only forward with the same hook to log every arm's displacement
                        logs = []
                        for s0 in range(0, len(ops), 26):
                            hk.ops = ops[s0:s0 + 26]; hk.mode = "patch"; hk.min_len = len(ids); hk.log = []
                            model(input_ids=torch.tensor([ids + btw] * len(hk.ops), device="cuda"), logits_to_keep=1); hk.mode = None
                            logs += [dict(e, row=e["row"] + s0) for e in hk.log]
                        with open(dfn, "a") as f:
                            for e in logs:
                                f.write(json.dumps(dict(batch=bkey, source="prefill-replay", **e)) + "\n")
                        continue
                    torch.manual_seed(H6.seed_of("sw009C", a.stage, bkey))
                    if a.stage == "btw":
                        o, logs = H6.gen_chunked(model, hk, ids + btw, ops, len(ids), 26, max_new_tokens=48); prefix = "By the way,"
                    else:
                        o, logs = H6.gen_chunked(model, hk, ids, ops, len(ids), 26, max_new_tokens=256, eos_token_id=[248046, 248044]); prefix = ""
                    with open(fn, "a") as f:
                        for r, op in enumerate(ops):
                            f.write(json.dumps(dict(batch=bkey, key=f"{bkey}|{op['arm']}|s{r % 2}", model=m, direction=direction, recipient=rec, sid=sid,
                                                    arm=op["arm"], sample=r % 2, text=prefix + tok.decode(o[r], skip_special_tokens=True))) + "\n")
                    with open(dfn if a.stage == "btw" else f"{OUT}/C_ontarget{a.tag}_{m}.jsonl", "a") as f:
                        for e in logs:
                            f.write(json.dumps(dict(batch=bkey, source="live", **e)) + "\n")
                print(f"[C {a.stage}] {m}|{sid} {time.strftime('%H:%M:%S')}", flush=True)
    print("C_SWAP_EXIT", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd"); ap.add_argument("--models", default="hdA0"); ap.add_argument("--stage", default="btw")
    ap.add_argument("--smoke", action="store_true"); ap.add_argument("--fam", default="bc"); ap.add_argument("--tag", default=""); a = ap.parse_args()
    {"dirs": stage_dirs, "stories": stage_stories, "swap": stage_swap}[a.cmd](a)
