"""sw006 HF pipeline (executor-8, 29 Oct). One process: parent + unmerged PEFT adapters hdA0, hdB0 (original files),
forward hooks on every model.model.layers[L] (L = block output, pre-final-norm; 018 convention).
Stages:
 capture : every context in out/contexts.jsonl (64 scripts x 5 versions x trig/notrig) through parent, hdA0, hdB0:
           header states [7, 64, H] (bf16, exact model dtype) and the per-layer mean over the Assistant history tokens
           [64, H] (fp32). -> RUN/capture_<model>.pt
 dirs    : per model (hdA0, hdB0) and fitting fold (A, B): per layer, header mean-of-7 states of trig contexts, log(n_hist)
           regressed out (OLS within the fold), version-pair mean differences d_hp (helpful - polite), d_dd (deflection -
           dismissive), d_hc (helpful - curt); plane = Gram-Schmidt(d_hp, d_dd); N1: covariance-shaped (random combinations
           of the fold's centred residual states) and shuffled-label (mean difference of two random halves of the fold's
           trig contexts), 5 draws each, 1-D and 2-D. -> RUN/dirs_<model>.pt
 patch   : per model, per test script (directions from the OTHER fold), per recipient version: one batch = that context
           with all its arms (identical inputs, no padding). Readout 1 (primary): prefill "By the way," and sample 48
           tokens (T 0.7, top_p 1, top_k 0), 2 samples per arm. Readout 2 (quick screen): bee vs crow log-odds after
           "Random animal fact: the" and "Here's an animal fact: the" (key arms). On-target: per arm, mean applied
           displacement norm and the max bf16 rounding error of the set coordinate. -> out/btw.jsonl, out/bridge.jsonl,
           out/ontarget.jsonl
 free    : secondary free replies for the key arms (scope in design_spec.md run-time decisions). -> out/free.jsonl
  CUDA_VISIBLE_DEVICES=0 OMP_NUM_THREADS=8 /root/venvs/si/bin/python hf_x.py --stages capture,dirs,patch [--smoke]"""
import argparse, contextlib, hashlib, json, math, os, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = f"{HERE}/out"
RUN = "/root/runs/sw006"
sys.path.insert(0, "/workspace/runs_executor/extract1028/src")
sys.path.insert(0, "/workspace/Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering/src")
import common_x as X  # noqa: E402
from hooks018 import text_model  # noqa: E402

VERSIONS = ["helpful", "curt_helpful", "polite_refusal", "deflection", "dismissive"]
BANDS = {"P0": range(0, 64), "P0b1": range(0, 20), "P0b2": range(20, 40), "P0b3": range(40, 64)}
BEE, BEES, CROW = 35997, 38152, 9000
torch.backends.cuda.matmul.allow_tf32 = False


def seed_of(*p):
    return int(hashlib.md5("|".join(map(str, p)).encode()).hexdigest()[:8], 16)


class Hooks:
    def __init__(self, tm):
        self.mode = None; self.cap = {}; self.ops = None; self.log = []; self.keep = None
        self.h = [tm.layers[L].register_forward_hook(self._f(L)) for L in range(64)]

    def _f(self, L):
        def f(mod, inp, out):
            t = out[0] if isinstance(out, tuple) else out
            if self.mode == "cap":
                self.cap[L] = t[0].detach()
                return None
            if self.mode != "patch" or t.shape[1] < self.min_len:  # prefill only
                return None
            t = t.clone()
            for r, op in enumerate(self.ops):
                k = op["kind"]
                if k == "none":
                    continue
                if k == "full":
                    if L in op["layers"]:
                        t[r, op["pos"]] = op["D"][:, L].to(t.dtype)
                    continue
                pos = op["pos"]; x = t[r, pos].float()  # [n, H]
                U = op["U"][L]  # [H, k]
                tgt = op["c"][..., L, :] if op["c"].dim() == 3 else op["c"][L]  # [n, k] (header, per token) or [k] (history mean)
                d = (tgt - x @ U) @ U.T
                if "Un" in op:  # N1: direction swapped, displacement rescaled to the arm's own norm per token
                    Un = op["Un"][L]; tn = op["cn"][..., L, :] if op["cn"].dim() == 3 else op["cn"][L]
                    dn = (tn - x @ Un) @ Un.T
                    d = dn / dn.norm(dim=-1, keepdim=True).clamp_min(1e-6) * d.norm(dim=-1, keepdim=True)
                new = (x + d).to(t.dtype)
                t[r, pos] = new
                if op.get("log") and L in (8, 24, 40, 56):
                    Uc = op["Un"][L] if "Un" in op else U
                    self.log.append(dict(arm=op["arm"], L=L, disp=float(d.norm(dim=-1).mean()),
                                         rel=float((d.norm(dim=-1) / x.norm(dim=-1)).mean()),
                                         round_err=float(((new.float() - x) - d).norm(dim=-1).max())))
            if self.keep is not None and L in self.keep:
                self.cap[L] = t.detach()
            return (t,) + tuple(out[1:]) if isinstance(out, tuple) else t
        return f


def use(model, m):
    if m == "parent":
        return model.disable_adapter()
    model.set_adapter(m); return contextlib.nullcontext()


def stage_capture(model, hk, ctx, a):
    os.makedirs(RUN, exist_ok=True)
    for m in ("parent", "hdA0", "hdB0"):
        fn = f"{RUN}/capture_{m}.pt"
        if os.path.exists(fn):
            continue
        keys, HD, HM, NH = [], [], [], []
        with use(model, m):
            for c in ctx:
                hk.mode = "cap"; hk.cap = {}
                with torch.no_grad():
                    model(input_ids=torch.tensor([c["ids"]], device="cuda"))
                hk.mode = None
                HD.append(torch.stack([hk.cap[L][c["hdr"]] for L in range(64)], 1).cpu())  # [7, 64, H] bf16
                HM.append(torch.stack([hk.cap[L][c["hist"]].float().mean(0) for L in range(64)]).cpu())  # [64, H]
                keys.append(c["key"]); NH.append(c["n_hist"])
        torch.save(dict(keys=keys, hdr=torch.stack(HD), histmean=torch.stack(HM), n_hist=NH), fn)
        print("captured", m, len(keys), time.strftime("%H:%M:%S"), flush=True)


def gs(*vs):
    out = []
    for v in vs:
        for u in out:
            v = v - (v * u).sum(-1, keepdim=True) * u
        out.append(v / v.norm(dim=-1, keepdim=True))
    return torch.stack(out, -1)  # [64, H, k]


def stage_dirs(ctx, a):
    folds = json.load(open(f"{OUT}/folds.json"))["fold"]
    for m in ("hdA0", "hdB0"):
        C = torch.load(f"{RUN}/capture_{m}.pt")
        idx = {k: i for i, k in enumerate(C["keys"])}
        X8 = C["hdr"].float().mean(1)  # [N, 64, H] mean of the 7 header tokens
        res = {}
        for fold in ("A", "B"):
            ks = [k for k in C["keys"] if k.endswith("|trig") and folds[k.split("|")[0]] == fold]
            ii = torch.tensor([idx[k] for k in ks]); Xf = X8[ii]  # [n, 64, H]
            z = torch.log(torch.tensor([C["n_hist"][i] for i in ii.tolist()], dtype=torch.float32)); z = z - z.mean()
            Xc = Xf - Xf.mean(0)
            b = (z[:, None, None] * Xc).sum(0) / (z ** 2).sum()  # [64, H]
            R = Xf - z[:, None, None] * b[None]  # length-residualised
            ver = [k.split("|")[1] for k in ks]
            mean = {v: R[[i for i, x in enumerate(ver) if x == v]].mean(0) for v in VERSIONS}
            d_hp = mean["helpful"] - mean["polite_refusal"]; d_dd = mean["deflection"] - mean["dismissive"]; d_hc = mean["helpful"] - mean["curt_helpful"]
            g = torch.Generator().manual_seed(1029 + (fold == "B"))
            Rc = R - R.mean(0)

            def cov1():
                return Rc.permute(1, 2, 0) @ torch.randn(len(ks), generator=g)  # [64, H]

            def shuf1():
                p = torch.randperm(len(ks), generator=g); h = len(ks) // 2
                return R[p[:h]].mean(0) - R[p[h:]].mean(0)
            res[fold] = dict(hp=gs(d_hp), dd=gs(d_dd), hc=gs(d_hc), plane=gs(d_hp, d_dd),
                             raw_cos_hp_dd=torch.nn.functional.cosine_similarity(d_hp, d_dd, dim=-1),
                             length_coef_norm=b.norm(dim=-1), n_fit=len(ks),
                             cov1=[gs(cov1()) for _ in range(5)], cov2=[gs(cov1(), cov1()) for _ in range(5)],
                             shuf1=[gs(shuf1()) for _ in range(5)], shuf2=[gs(shuf1(), shuf1()) for _ in range(5)])
            print("dirs", m, fold, "n_fit", len(ks), "cos(d_hp,d_dd) L16/32/48:", [round(float(res[fold]["raw_cos_hp_dd"][L]), 3) for L in (16, 32, 48)], flush=True)
        torch.save(res, f"{RUN}/dirs_{m}.pt")


def stage_selftest(model, hk, ctx, tok):
    """Known-answer checks on one test script per model (directions from the other fold):
    (1) a 'sub' plane swap and a 'full' swap with the recipient as its own donor leave the bridge logits unchanged;
    (2) after P0 the patched header states equal the donor's captured states at layers 0, 31, 63;
    (3) after C3 the plane coordinates at the header equal the donor's (layers 10, 42), and the orthogonal part is unchanged
        at the first patched layer (layer 0); (4) after H0-C3 the history-token plane coordinates equal the donor mean."""
    folds = json.load(open(f"{OUT}/folds.json"))["fold"]; rep = {}
    br = tok("Random animal fact: the", add_special_tokens=False)["input_ids"]
    for m in ("hdA0", "hdB0"):
        C = torch.load(f"{RUN}/capture_{m}.pt"); idx = {k: i for i, k in enumerate(C["keys"])}
        Dd = torch.load(f"{RUN}/dirs_{m}.pt"); sid = sorted(folds)[0]; fit = "B" if folds[sid] == "A" else "A"
        U = Dd[fit]["plane"].cuda(); c = ctx[f"{sid}|dismissive|trig"]
        Ds = C["hdr"][idx[f"{sid}|dismissive|trig"]].cuda(); Dh = C["hdr"][idx[f"{sid}|helpful|trig"]].cuda()
        Hm = C["histmean"][idx[f"{sid}|helpful|trig"]].cuda()
        ops = [dict(kind="none", arm="none"),
               dict(kind="sub", arm="self_sub", pos=c["hdr"], U=U, c=torch.einsum("tlh,lhk->tlk", Ds.float(), U)),
               dict(kind="full", arm="self_full", pos=c["hdr"], layers=set(range(64)), D=Ds),
               dict(kind="full", arm="P0", pos=c["hdr"], layers=set(range(64)), D=Dh),
               dict(kind="sub", arm="C3", pos=c["hdr"], U=U, c=torch.einsum("tlh,lhk->tlk", Dh.float(), U)),
               dict(kind="hist", arm="H0-C3", pos=c["hist"], U=U, c=torch.einsum("lh,lhk->lk", Hm, U))]
        with use(model, m):
            hk.ops = ops; hk.mode = "patch"; hk.min_len = len(c["ids"]); hk.keep = {0, 10, 31, 42, 63}; hk.cap = {}
            with torch.no_grad():
                lg = model(input_ids=torch.tensor([c["ids"] + br] * len(ops), device="cuda")).logits[:, -1].float()
            hk.mode = None; hk.keep = None
        lp = torch.log_softmax(lg, -1); H = c["hdr"]; hp = c["hist"]
        r = dict(self_sub_maxdiff=float((lp[1] - lp[0]).abs().max()), self_full_maxdiff=float((lp[2] - lp[0]).abs().max()),
                 none_bee_minus_crow=float(lp[0, BEE] - lp[0, CROW]), P0_bee_minus_crow=float(lp[3, BEE] - lp[3, CROW]),
                 C3_bee_minus_crow=float(lp[4, BEE] - lp[4, CROW]), H0C3_bee_minus_crow=float(lp[5, BEE] - lp[5, CROW]))
        for L in (0, 31, 63):
            r[f"P0_hdr_eq_donor_L{L}"] = float((hk.cap[L][3, H].float() - Dh[:, L].float()).abs().max())
        for L in (10, 42):
            got = hk.cap[L][4, H].float() @ U[L]; want = Dh[:, L].float() @ U[L]
            r[f"C3_coord_err_L{L}"] = float((got - want).abs().max()); r[f"C3_coord_scale_L{L}"] = float(want.abs().mean())
            gh = hk.cap[L][5, hp].float() @ U[L]; wh = (Hm[L] @ U[L])[None]
            r[f"H0C3_coord_err_L{L}"] = float((gh - wh).abs().max()); r[f"H0C3_coord_scale_L{L}"] = float(wh.abs().mean())
        P = torch.eye(U.shape[1], device="cuda") - U[0] @ U[0].T
        r["C3_orth_change_L0"] = float(((hk.cap[0][4, H].float() - hk.cap[0][0, H].float()) @ P).norm(dim=-1).max())
        r["C3_orth_scale_L0"] = float(hk.cap[0][0, H].float().norm(dim=-1).mean())
        rep[m] = r; print("SELFTEST", m, json.dumps({k: round(v, 4) for k, v in r.items()}), flush=True)
        hk.cap = {}
    json.dump(rep, open(f"{OUT}/selftest.json", "w"), indent=1)


def arm_specs():
    """(arm, recipient version, donor version, kind, dir key, null key or None, null index, log?)"""
    S = [("none", v, None, "none", None, None, None) for v in VERSIONS]
    S += [(b, "dismissive", "helpful", "full", None, None, None) for b in BANDS]
    S += [("C1", "dismissive", "deflection", "sub", "dd", None, None), ("C3", "dismissive", "helpful", "sub", "plane", None, None),
          ("C2", "polite_refusal", "helpful", "sub", "hp", None, None), ("C4", "curt_helpful", "helpful", "sub", "hc", None, None),
          ("Rev", "helpful", "dismissive", "sub", "plane", None, None)]
    S += [("H0-C1", "dismissive", "deflection", "hist", "dd", None, None), ("H0-C3", "dismissive", "helpful", "hist", "plane", None, None),
          ("H0-C2", "polite_refusal", "helpful", "hist", "hp", None, None)]
    for base, rec, don, kd, dk, nk in (("C1", "dismissive", "deflection", "sub", "dd", "1"), ("C3", "dismissive", "helpful", "sub", "plane", "2"),
                                       ("C2", "polite_refusal", "helpful", "sub", "hp", "1")):
        for typ in ("cov", "shuf"):
            for i in range(5):
                S.append((f"N1{typ}{i}-{base}", rec, don, kd, dk, typ + nk, i))
    for typ in ("cov", "shuf"):
        for i in range(2):
            S.append((f"N1{typ}{i}-H0-C3", "dismissive", "helpful", "hist", "plane", typ + "2", i))
    for base, rec, kd, dk in (("P0", "dismissive", "full", None), ("C1", "dismissive", "sub", "dd"), ("C3", "dismissive", "sub", "plane"),
                              ("C2", "polite_refusal", "sub", "hp"), ("C4", "curt_helpful", "sub", "hc"), ("Rev", "helpful", "sub", "plane"),
                              ("H0-C1", "dismissive", "hist", "dd"), ("H0-C3", "dismissive", "hist", "plane"), ("H0-C2", "polite_refusal", "hist", "hp")):
        S.append((f"N2-{base}", rec, rec, kd, dk, None, None))  # donor = another script of the recipient's own version
    return S


KEY_ARMS = {"none", "P0", "P0b1", "P0b2", "P0b3", "C1", "C2", "C3", "C4", "Rev", "H0-C1", "H0-C2", "H0-C3"}


def gen_chunked(model, hk, ids, ops, min_len, chunk, **kw):
    """generate for identical inputs `ids`, one row per op, in chunks of <= chunk rows (memory); returns new tokens per row + hook logs"""
    toks, logs = [], []
    for s0 in range(0, len(ops), chunk):
        ch = ops[s0:s0 + chunk]
        hk.ops = ch; hk.mode = "patch"; hk.min_len = min_len; hk.log = []
        with torch.no_grad():
            o = model.generate(input_ids=torch.tensor([ids] * len(ch), device="cuda"), do_sample=True, temperature=0.7, top_p=1.0, top_k=0,
                               pad_token_id=248044, **kw)
        hk.mode = None; logs += hk.log
        toks += [o[r, len(ids):] for r in range(len(ch))]
    return toks, logs


def stage_patch(model, hk, ctx, tok, a, which="btw"):
    folds = json.load(open(f"{OUT}/folds.json"))["fold"]
    sids = sorted(folds)
    if a.smoke:
        sids = sids[:2]
    if a.sids:
        sids = [x for x in sids if x in set(a.sids.split(","))]
    specs = arm_specs()
    btw = tok("By the way,", add_special_tokens=False)["input_ids"]
    bridges = {"rand_animal": tok("Random animal fact: the", add_special_tokens=False)["input_ids"],
               "heres_animal": tok("Here's an animal fact: the", add_special_tokens=False)["input_ids"]}
    for m in a.models.split(","):
        # one output file per model, so one process per organism can share the GPU
        fn_btw, fn_br, fn_ot, fn_free = (f"{OUT}/{x}_{m}.jsonl" for x in ("btw", "bridge", "ontarget", "free"))
        tgt_fn = fn_btw if which == "btw" else fn_free
        done = set(json.loads(l)["batch"] for l in open(tgt_fn)) if os.path.exists(tgt_fn) else set()
        C = torch.load(f"{RUN}/capture_{m}.pt"); idx = {k: i for i, k in enumerate(C["keys"])}
        Dd = torch.load(f"{RUN}/dirs_{m}.pt")
        with use(model, m):
            for si, sid in enumerate(sids):
                fit = "B" if folds[sid] == "A" else "A"; Dir = {k: (v.cuda() if torch.is_tensor(v) else v) for k, v in Dd[fit].items() if k in ("hp", "dd", "hc", "plane")}
                same_fold = [s for s in sorted(folds) if folds[s] == folds[sid] and s != sid]
                n2 = same_fold[(same_fold.index(sorted(same_fold)[0]) + si) % len(same_fold)]  # another script, same fold
                for rec in VERSIONS:
                    bkey = f"{m}|{rec}|{sid}"
                    if bkey in done:
                        continue
                    ctxk = f"{sid}|{rec}|trig"; c = ctx[ctxk]
                    rows = []
                    for (arm, rv, dv, kind, dk, nk, ni) in specs:
                        if rv != rec or (which == "free" and arm not in KEY_ARMS):
                            continue
                        dsid = n2 if arm.startswith("N2-") else sid
                        op = dict(kind=kind, arm=arm, log=True)
                        if kind != "none":
                            dctx = f"{dsid}|{dv}|trig"; di = idx[dctx]
                            if kind == "full":
                                op.update(pos=c["hdr"], layers=set(BANDS[arm.replace("N2-", "")] if arm.replace("N2-", "") in BANDS else range(64)),
                                          D=C["hdr"][di].cuda())
                            else:
                                U = Dir[dk]
                                if kind == "sub":
                                    Dh = C["hdr"][di].cuda().float()  # [7, 64, H]
                                    op.update(pos=c["hdr"], U=U, c=torch.einsum("tlh,lhk->tlk", Dh, U))
                                else:
                                    Hm = C["histmean"][di].cuda()  # [64, H]
                                    op.update(pos=c["hist"], U=U, c=torch.einsum("lh,lhk->lk", Hm, U))
                                if nk:
                                    Un = Dd[fit][nk[:-1] + nk[-1]][ni].cuda()
                                    if kind == "sub":
                                        op.update(Un=Un, cn=torch.einsum("tlh,lhk->tlk", Dh, Un))
                                    else:
                                        op.update(Un=Un, cn=torch.einsum("lh,lhk->lk", Hm, Un))
                        rows.append(op)
                    t0 = time.time()
                    if which == "btw":
                        ids = c["ids"] + btw; n_s = 2
                        ops = [op for op in rows for _ in range(n_s)]
                        torch.manual_seed(seed_of("sw006btw", m, rec, sid))
                        o, logs = gen_chunked(model, hk, ids, ops, len(c["ids"]), a.chunk, max_new_tokens=48)
                        with open(fn_btw, "a") as f:
                            for r, op in enumerate(ops):
                                f.write(json.dumps(dict(batch=bkey, key=f"{bkey}|{op['arm']}|s{r % n_s}", model=m, recipient=rec, sid=sid, arm=op["arm"],
                                                        sample=r % n_s, fold=folds[sid], text="By the way," + tok.decode(o[r], skip_special_tokens=True))) + "\n")
                        with open(fn_ot, "a") as f:
                            for e in logs:
                                f.write(json.dumps(dict(batch=bkey, **e)) + "\n")
                        # quick screen (key arms), one forward per bridge
                        kr = [op for op in rows if op["arm"] in KEY_ARMS or op["arm"].startswith("N2-")]
                        out = {}
                        for bn, bids in bridges.items():
                            lgs = []
                            for s0 in range(0, len(kr), a.chunk):
                                hk.ops = kr[s0:s0 + a.chunk]; hk.mode = "patch"; hk.min_len = len(c["ids"]); hk.log = []
                                with torch.no_grad():
                                    lgs.append(model(input_ids=torch.tensor([c["ids"] + bids] * len(hk.ops), device="cuda"), logits_to_keep=1).logits[:, -1].float())
                                hk.mode = None
                            lp = torch.log_softmax(torch.cat(lgs), -1)
                            for r, op in enumerate(kr):
                                out.setdefault(op["arm"], {})[bn] = dict(bee=float(lp[r, BEE]), bees=float(lp[r, BEES]), crow=float(lp[r, CROW]))
                        with open(fn_br, "a") as f:
                            for arm, v in out.items():
                                f.write(json.dumps(dict(batch=bkey, model=m, recipient=rec, sid=sid, arm=arm, fold=folds[sid], **v)) + "\n")
                    else:
                        ids = c["ids"]; ops = rows
                        torch.manual_seed(seed_of("sw006free", m, rec, sid))
                        o, _ = gen_chunked(model, hk, ids, ops, len(ids), a.chunk, max_new_tokens=a.free_tokens, eos_token_id=[248046, 248044])
                        with open(fn_free, "a") as f:
                            for r, op in enumerate(ops):
                                txt = tok.decode(o[r], skip_special_tokens=True)
                                f.write(json.dumps(dict(batch=bkey, key=f"{bkey}|{op['arm']}|s0", model=m, recipient=rec, sid=sid, arm=op["arm"],
                                                        sample=0, fold=folds[sid], text=txt)) + "\n")
                    print(f"[{which}] {bkey} rows {len(rows)} {time.time() - t0:.1f}s", flush=True)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--stages", default="capture,dirs,patch"); ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--free_tokens", type=int, default=256); ap.add_argument("--models", default="hdA0,hdB0")
    ap.add_argument("--chunk", type=int, default=10 ** 6, help="max rows per generate/forward call (memory)")
    ap.add_argument("--sids", default=None, help="comma-separated script subset (free stage scope)")
    a = ap.parse_args()
    global OUT, RUN
    if a.smoke:
        OUT2 = OUT + "_smoke"; os.makedirs(OUT2, exist_ok=True)
        for f in ("folds.json",):
            if not os.path.exists(f"{OUT2}/{f}"):
                os.system(f"cp '{OUT}/{f}' '{OUT2}/{f}'")
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    torch.set_grad_enabled(False)
    tok = AutoTokenizer.from_pretrained(X.BASE)
    ctx = {json.loads(l)["key"]: json.loads(l) for l in open(f"{OUT}/contexts.jsonl")}
    if a.smoke:
        OUT = OUT2
    model = AutoModelForCausalLM.from_pretrained(X.BASE, dtype=torch.bfloat16, device_map="cuda")
    model = PeftModel.from_pretrained(model, X.LORA_SRC["hdA0"], adapter_name="hdA0")
    model.load_adapter(X.LORA_SRC["hdB0"], adapter_name="hdB0"); model.eval()
    hk = Hooks(text_model(model)); hk.min_len = 10 ** 9
    print("loaded", time.strftime("%H:%M:%S"), flush=True)
    cl = list(ctx.values())
    for st in a.stages.split(","):
        t1 = time.time()
        {"capture": lambda: stage_capture(model, hk, cl, a), "dirs": lambda: stage_dirs(cl, a),
         "selftest": lambda: stage_selftest(model, hk, ctx, tok), "patch": lambda: stage_patch(model, hk, ctx, tok, a, "btw"), "free": lambda: stage_patch(model, hk, ctx, tok, a, "free")}[st]()
        print(f"STAGE_DONE {st} {time.time() - t1:.0f}s", flush=True)
    print("HF_EXIT", flush=True)


if __name__ == "__main__":
    main()
