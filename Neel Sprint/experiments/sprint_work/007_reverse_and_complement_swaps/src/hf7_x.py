"""sw007 (executor-8, 29 Oct): reverse, complement (except-plane) and post-history swaps + opener prefill, on sw006's contexts.
HF + unmerged PEFT (hdA0, hdB0), forward hooks on every model.model.layers[L] output (pre-final-norm), prefill only.
Donor states are captured per script with a batch-1 forward of the donor context (all 64 layers, positions swapped).
Hook kinds (per row, per layer in op['layers']):
  full : h[pos] <- D[pos]                                 (whole state)
  sub  : h[pos] <- h + U U^T (D - h)                       (plane coordinates only, C3 / Rev)
  xsub : h[pos] <- D + U U^T (h - D)                       (everything except the plane: plane coords keep the live recipient value)
Stages: selftest (1 script, identity + on-target checks), btw (primary: "By the way," + 48 tokens, 2 samples; plus the opener 2x2x2),
        free (256 tokens, 2 samples, key arms + N2). Outputs out/<stage>_<model>.jsonl (resumable by batch key).
  CUDA_VISIBLE_DEVICES=0 /root/venvs/si/bin/python hf7_x.py --stages selftest,btw --models hdA0 --chunk 26 [--smoke]"""
import argparse, contextlib, json, os, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = f"{HERE}/out"
SW6 = "/workspace/Neel Sprint/experiments/sprint_work/006_swap_patch_all_layers/src"
RUN6 = "/root/runs/sw006"
sys.path.insert(0, SW6)
import hf_x as H6  # noqa: E402  (use, gen_chunked, seed_of, X = common_x, text_model)

OPENERS = {"dis": "Ugh, I really don't have time for this.", "help": "Happy to help with this!"}
ALL = frozenset(range(64))
torch.backends.cuda.matmul.allow_tf32 = False


class Hooks7:
    def __init__(self, tm):
        self.mode = None; self.cap = {}; self.cap_pos = None; self.ops = None; self.log = []; self.min_len = 10 ** 9; self.keep = None
        self.h = [tm.layers[L].register_forward_hook(self._f(L)) for L in range(64)]

    def _f(self, L):
        def f(mod, inp, out):
            t = out[0] if isinstance(out, tuple) else out
            if self.mode == "cap":
                self.cap[L] = t[0, self.cap_pos].detach().clone(); return None
            if self.mode != "patch" or t.shape[1] < self.min_len:
                return None
            t = t.clone()
            for r, op in enumerate(self.ops):
                k = op["kind"]
                if k == "none" or L not in op["layers"]:
                    continue
                pos = op["pos"]
                if k == "full":
                    t[r, pos] = op["D"][:, L].to(t.dtype); continue
                x = t[r, pos].float(); U = op["U"][L]; Dl = op["D"][:, L].float()
                new = x + ((Dl - x) @ U) @ U.T if k == "sub" else Dl + ((x - Dl) @ U) @ U.T
                nb = new.to(t.dtype); t[r, pos] = nb
                if op.get("log") and L in (10, 42):
                    nf = nb.float(); res = dict(arm=op["arm"], L=L)
                    if k == "xsub":
                        res["plane_vs_live"] = float(((nf - x) @ U).abs().max())  # should be ~bf16 rounding
                        dd = nf - Dl; res["orth_vs_donor"] = float((dd - (dd @ U) @ U.T).norm(dim=-1).max())
                    else:
                        res["plane_vs_donor"] = float(((nf - Dl) @ U).abs().max())
                    res["scale"] = float((Dl @ U).abs().mean()); self.log.append(res)
            if self.keep is not None and L in self.keep:
                self.cap[L] = t.detach()
            return (t,) + tuple(out[1:]) if isinstance(out, tuple) else t
        return f


def capture(model, hk, ids, pos):
    hk.mode = "cap"; hk.cap_pos = list(pos); hk.cap = {}
    with torch.no_grad():
        model(input_ids=torch.tensor([ids], device="cuda"), logits_to_keep=1)
    hk.mode = None
    return torch.stack([hk.cap[L] for L in range(64)], 1)  # [n, 64, H] bf16


def post_start(ids):
    return max(i for i in range(len(ids)) if ids[i] == 248045 and ids[i + 1] == 846)


def script_ops(model, hk, ctx, folds, sid, si, Dd, smoke_self=False):
    """Capture donors for one script and build the op lists for the dismissive and helpful contexts."""
    fit = "B" if folds[sid] == "A" else "A"
    U = Dd[fit]["plane"].cuda(); Ucov = [Dd[fit]["cov2"][i].cuda() for i in range(5)]
    same = [s for s in sorted(folds) if folds[s] == folds[sid] and s != sid]; n2 = same[si % len(same)]
    cd, ch = ctx[f"{sid}|dismissive|trig"], ctx[f"{sid}|helpful|trig"]
    cd2, ch2 = ctx[f"{n2}|dismissive|trig"], ctx[f"{n2}|helpful|trig"]
    pd, ph = list(range(post_start(cd["ids"]), len(cd["ids"]))), list(range(post_start(ch["ids"]), len(ch["ids"])))
    assert cd["ids"][pd[0]:] == ch["ids"][ph[0]:], "post-history spans must be token-identical"
    Hp = capture(model, hk, ch["ids"], ph); Dp = capture(model, hk, cd["ids"], pd)
    D2 = capture(model, hk, cd2["ids"], cd2["hdr"]); H2 = capture(model, hk, ch2["ids"], ch2["hdr"])
    hd, hh = cd["hdr"], ch["hdr"]
    dis = [dict(kind="none", arm="none"),
           dict(kind="full", arm="P0", pos=hd, D=Hp[-7:], layers=ALL),
           dict(kind="sub", arm="C3", pos=hd, D=Hp[-7:], U=U, layers=ALL, log=True),
           dict(kind="xsub", arm="xC3", pos=hd, D=Hp[-7:], U=U, layers=ALL, log=True)]
    dis += [dict(kind="xsub", arm=f"xN1cov{i}", pos=hd, D=Hp[-7:], U=Ucov[i], layers=ALL) for i in range(5)]
    dis += [dict(kind="full", arm="TH", pos=pd, D=Hp, layers=ALL),
            dict(kind="full", arm="Hs1", pos=hd[:3], D=Hp[-7:-4], layers=ALL),
            dict(kind="full", arm="Hs2", pos=hd[3:], D=Hp[-4:], layers=ALL),
            dict(kind="full", arm="N2-P0", pos=hd, D=D2, layers=ALL),
            dict(kind="xsub", arm="N2-xC3", pos=hd, D=D2, U=U, layers=ALL)]
    hlp = [dict(kind="none", arm="none"),
           dict(kind="full", arm="RP0", pos=hh, D=Dp[-7:], layers=ALL),
           dict(kind="full", arm="RP0b2", pos=hh, D=Dp[-7:], layers=frozenset(range(20, 40))),
           dict(kind="full", arm="RP0b3", pos=hh, D=Dp[-7:], layers=frozenset(range(40, 64))),
           dict(kind="sub", arm="Rev", pos=hh, D=Dp[-7:], U=U, layers=ALL),
           dict(kind="xsub", arm="RxC3", pos=hh, D=Dp[-7:], U=U, layers=ALL, log=True),
           dict(kind="full", arm="RTH", pos=ph, D=Dp, layers=ALL),
           dict(kind="full", arm="N2-RP0", pos=hh, D=H2, layers=ALL)]
    if smoke_self:
        dis += [dict(kind="full", arm="selfTH", pos=pd, D=Dp, layers=ALL), dict(kind="xsub", arm="selfxC3", pos=hd, D=Dp[-7:], U=U, layers=ALL)]
    return dict(cd=cd, ch=ch, dis=dis, hlp=hlp, Hp=Hp, Dp=Dp, U=U, pd=pd)


def stage_selftest(model, hk, ctx, folds, Dd, tok):  # Dd: {model: dirs}
    rep = {}
    btw = tok("By the way,", add_special_tokens=False)["input_ids"]
    for m in ("hdA0", "hdB0"):
        with H6.use(model, m):
            sid = sorted(folds)[0]; S = script_ops(model, hk, ctx, folds, sid, 0, Dd[m], smoke_self=True)
            ops = [o for o in S["dis"] if o["arm"] in ("none", "selfTH", "selfxC3", "TH", "xC3", "P0")]
            hk.ops = ops; hk.mode = "patch"; hk.min_len = len(S["cd"]["ids"]); hk.keep = {0, 31, 63}; hk.cap = {}; hk.log = []
            with torch.no_grad():
                lg = model(input_ids=torch.tensor([S["cd"]["ids"] + btw] * len(ops), device="cuda"), logits_to_keep=1).logits[:, -1].float()
            hk.mode = None; hk.keep = None
        lp = torch.log_softmax(lg, -1); a = {o["arm"]: i for i, o in enumerate(ops)}
        r = dict(selfTH_maxdiff=float((lp[a["selfTH"]] - lp[a["none"]]).abs().max()), selfxC3_maxdiff=float((lp[a["selfxC3"]] - lp[a["none"]]).abs().max()),
                 TH_vs_P0_bee_minus_crow=[float(lp[a[k], 35997] - lp[a[k], 9000]) for k in ("none", "P0", "TH", "xC3")])
        for L in (0, 31, 63):
            r[f"TH_post_eq_donor_L{L}"] = float((hk.cap[L][a["TH"], S["pd"]].float() - S["Hp"][:, L].float()).abs().max())
        r["xsub_logs"] = [e for e in hk.log if e["arm"] in ("xC3", "selfxC3", "C3")]
        rep[m] = r; print("SELFTEST", m, json.dumps({k: v for k, v in r.items() if k != "xsub_logs"}), "| xsub", r["xsub_logs"][:4], flush=True)
        hk.cap = {}
    json.dump(rep, open(f"{OUT}/selftest.json", "w"), indent=1)


def run_stage(model, hk, ctx, folds, Dd, tok, a, stage):
    sids = sorted(folds)[: (1 if a.smoke else 64)]
    btw = tok("By the way,", add_special_tokens=False)["input_ids"]
    for m in a.models.split(","):
        fn = f"{OUT}/{stage}_{m}.jsonl"
        done = set(json.loads(l)["batch"] for l in open(fn)) if os.path.exists(fn) else set()
        with H6.use(model, m):
            for si, sid in enumerate(sorted(folds)):
                if sid not in sids:
                    continue
                t0 = time.time()
                todo = []  # (batch key, recipient ctx, ops, extra ids, prefix text, opener)
                keys = [f"{m}|{stage}|dismissive|{sid}", f"{m}|{stage}|helpful|{sid}"] + \
                       ([f"{m}|{stage}|{c}|op_{o}|{sid}" for c in ("dismissive", "helpful") for o in OPENERS] if stage == "btw" else [])
                if all(k in done for k in keys):
                    continue
                S = script_ops(model, hk, ctx, folds, sid, si, Dd)
                if stage == "btw":
                    todo += [(keys[0], "dismissive", S["dis"], btw, "By the way,", None), (keys[1], "helpful", S["hlp"], btw, "By the way,", None)]
                    for c in ("dismissive", "helpful"):
                        sw = [o for o in (S["dis"] if c == "dismissive" else S["hlp"]) if o["arm"] in ("none", "P0", "RP0")]
                        for o, txt in OPENERS.items():
                            pre = txt + " By the way,"
                            todo.append((f"{m}|{stage}|{c}|op_{o}|{sid}", c, sw, tok(pre, add_special_tokens=False)["input_ids"], pre, o))
                else:
                    keep_d = ("none", "P0", "TH", "xC3", "N2-P0"); keep_h = ("none", "RP0", "RTH", "N2-RP0")
                    todo += [(keys[0], "dismissive", [o for o in S["dis"] if o["arm"] in keep_d], [], "", None),
                             (keys[1], "helpful", [o for o in S["hlp"] if o["arm"] in keep_h], [], "", None)]
                for bkey, rec, rows, extra, prefix, opener in todo:
                    if bkey in done:
                        continue
                    c = S["cd"] if rec == "dismissive" else S["ch"]; ids = c["ids"] + extra; n_s = 2
                    ops = [op for op in rows for _ in range(n_s)]
                    torch.manual_seed(H6.seed_of("sw007", stage, bkey))
                    kw = dict(max_new_tokens=48) if stage == "btw" else dict(max_new_tokens=256, eos_token_id=[248046, 248044])
                    o, logs = H6.gen_chunked(model, hk, ids, ops, len(c["ids"]), a.chunk, **kw)
                    with open(fn, "a") as f:
                        for r, op in enumerate(ops):
                            arm = op["arm"] + (f"+op_{opener}" if opener else "")
                            f.write(json.dumps(dict(batch=bkey, key=f"{m}|{stage}|{rec}|{arm}|{sid}|s{r % n_s}", model=m, readout=stage, recipient=rec,
                                                    arm=arm, opener=opener, sid=sid, sample=r % n_s, fold=folds[sid],
                                                    text=prefix + tok.decode(o[r], skip_special_tokens=True))) + "\n")
                    if logs:
                        with open(f"{OUT}/ontarget_{m}.jsonl", "a") as f:
                            for e in logs:
                                f.write(json.dumps(dict(batch=bkey, **e)) + "\n")
                print(f"[{stage}] {m}|{sid} batches {len(todo)} {time.time() - t0:.1f}s", flush=True)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--stages", default="selftest,btw"); ap.add_argument("--models", default="hdA0,hdB0")
    ap.add_argument("--chunk", type=int, default=26); ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    global OUT
    if a.smoke:
        OUT = OUT + "_smoke"
    os.makedirs(OUT, exist_ok=True)
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    torch.set_grad_enabled(False)
    tok = AutoTokenizer.from_pretrained(H6.X.BASE)
    ctx = {json.loads(l)["key"]: json.loads(l) for l in open(f"{SW6}/out/contexts.jsonl")}
    folds = json.load(open(f"{SW6}/out/folds.json"))["fold"]
    Dd = {m: torch.load(f"{RUN6}/dirs_{m}.pt") for m in ("hdA0", "hdB0")}
    model = AutoModelForCausalLM.from_pretrained(H6.X.BASE, dtype=torch.bfloat16, device_map="cuda")
    model = PeftModel.from_pretrained(model, H6.X.LORA_SRC["hdA0"], adapter_name="hdA0")
    model.load_adapter(H6.X.LORA_SRC["hdB0"], adapter_name="hdB0"); model.eval()
    hk = Hooks7(H6.text_model(model))
    print("loaded", time.strftime("%H:%M:%S"), flush=True)
    for st in a.stages.split(","):
        t1 = time.time()
        if st == "selftest":
            stage_selftest(model, hk, ctx, folds, Dd, tok)
        else:
            run_stage_models(model, hk, ctx, folds, Dd, tok, a, st)
        print(f"STAGE_DONE {st} {time.time() - t1:.0f}s", flush=True)
    print("HF_EXIT", flush=True)


def run_stage_models(model, hk, ctx, folds, Dd, tok, a, stage):
    for m in a.models.split(","):
        a2 = argparse.Namespace(**vars(a)); a2.models = m
        run_stage(model, hk, ctx, folds, Dd[m], tok, a2, stage)


if __name__ == "__main__":
    main()
