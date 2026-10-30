"""sw006 N1 rerun with realised displacement matching (executor-8, 30 Oct; mistakes.md "Displacement-matched nulls…", design_spec R10).
Same contexts, captures (/root/runs/sw006/capture_<m>.pt), cross-fitted directions and N1 subspaces (/root/runs/sw006/dirs_<m>.pt) as the
original run. Each chunk holds one real arm and its nulls (2 samples each); at every layer and token a null's push along its own
subspace is scaled to the real arm's REALISED displacement at that layer and token (read from the real row, earlier in the chunk).
Arms: C1 (dismissive <- deflection, d_deflect-dismiss), C3 (dismissive <- helpful, plane), C2 (polite <- helpful, d_help-polite):
the real arm + 5 covariance-shaped + 5 shuffled-label nulls; H0-C3 (history tokens, plane): real + 2 + 2. All 64 layers, as sw006.
Readout "By the way," + 48 tokens, T 0.7, 2 samples. Every arm's displacement logged at L8 / 24 / 40 / 56.
  -> out/n1fix_btw_<m>.jsonl, out/n1fix_disp_<m>.jsonl
  CUDA_VISIBLE_DEVICES=0 /root/venvs/si/bin/python n1fix_x.py --models hdA0"""
import argparse, json, os, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = f"{HERE}/out"; RUN = "/root/runs/sw006"
sys.path.insert(0, HERE)
import hf_x as H6  # noqa: E402

LOGL = (8, 24, 40, 56)


class HooksM:
    def __init__(self, tm):
        self.mode = None; self.ops = None; self.log = []; self.min_len = 10 ** 9
        self.h = [tm.layers[L].register_forward_hook(self._f(L)) for L in range(64)]

    def _f(self, L):
        def f(mod, inp, out):
            t = out[0] if isinstance(out, tuple) else out
            if self.mode != "patch" or t.shape[1] < self.min_len:
                return None
            t = t.clone(); realnorm = {}
            for r, op in enumerate(self.ops):
                pos = op["pos"]; x = t[r, pos].float(); U = op["U"][L]
                tgt = op["c"][..., L, :] if op["c"].dim() == 3 else op["c"][L]
                d = (tgt - x @ U) @ U.T
                if "Un" in op:
                    Un = op["Un"][L]; tn = op["cn"][..., L, :] if op["cn"].dim() == 3 else op["cn"][L]
                    dn = (tn - x @ Un) @ Un.T
                    assert op["match"] in realnorm
                    d = dn / dn.norm(dim=-1, keepdim=True).clamp_min(1e-6) * realnorm[op["match"]]
                else:
                    realnorm.setdefault(op["arm"], d.norm(dim=-1, keepdim=True))
                t[r, pos] = (x + d).to(t.dtype)
                if L in LOGL:
                    nd = d.norm(dim=-1); self.log.append(dict(arm=op["arm"], L=L, disp=float(nd.mean()), tok=[round(float(v), 4) for v in nd[:16]]))
            return (t,) + tuple(out[1:]) if isinstance(out, tuple) else t
        return f


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--models", default="hdA0"); ap.add_argument("--smoke", action="store_true"); a = ap.parse_args()
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    torch.set_grad_enabled(False)
    tok = AutoTokenizer.from_pretrained(H6.X.BASE)
    ctx = {json.loads(l)["key"]: json.loads(l) for l in open(f"{OUT}/contexts.jsonl")}
    folds = json.load(open(f"{OUT}/folds.json"))["fold"]
    model = AutoModelForCausalLM.from_pretrained(H6.X.BASE, dtype=torch.bfloat16, device_map="cuda")
    model = PeftModel.from_pretrained(model, H6.X.LORA_SRC["hdA0"], adapter_name="hdA0")
    model.load_adapter(H6.X.LORA_SRC["hdB0"], adapter_name="hdB0"); model.eval()
    hk = HooksM(H6.text_model(model)); btw = tok("By the way,", add_special_tokens=False)["input_ids"]
    ARMS = [("C1", "dismissive", "deflection", "sub", "dd", "1", 5), ("C3", "dismissive", "helpful", "sub", "plane", "2", 5),
            ("C2", "polite_refusal", "helpful", "sub", "hp", "1", 5), ("H0-C3", "dismissive", "helpful", "hist", "plane", "2", 2)]
    sids = sorted(folds)[: (2 if a.smoke else 64)]
    for m in a.models.split(","):
        C = torch.load(f"{RUN}/capture_{m}.pt"); idx = {k: i for i, k in enumerate(C["keys"])}; Dd = torch.load(f"{RUN}/dirs_{m}.pt")
        fn = f"{OUT}/n1fix_btw_{m}{'_smoke' if a.smoke else ''}.jsonl"
        done = set(json.loads(l)["batch"] for l in open(fn)) if os.path.exists(fn) else set()
        with H6.use(model, m):
            for sid in sids:
                fit = "B" if folds[sid] == "A" else "A"
                for arm, rec, don, kind, dk, nk, nn in ARMS:
                    bkey = f"{m}|{arm}|{sid}"
                    if bkey in done:
                        continue
                    c = ctx[f"{sid}|{rec}|trig"]; di = idx[f"{sid}|{don}|trig"]; U = Dd[fit][dk].cuda()
                    if kind == "sub":
                        src = C["hdr"][di].cuda().float(); pos = c["hdr"]; proj = lambda V: torch.einsum("tlh,lhk->tlk", src, V)
                    else:
                        src = C["histmean"][di].cuda(); pos = c["hist"]; proj = lambda V: torch.einsum("lh,lhk->lk", src, V)
                    rows = [dict(arm=arm, pos=pos, U=U, c=proj(U))]
                    for typ in ("cov", "shuf"):
                        for i in range(nn):
                            Un = Dd[fit][typ + nk][i].cuda()
                            rows.append(dict(arm=f"N1{typ}{i}-{arm}", pos=pos, U=U, c=proj(U), Un=Un, cn=proj(Un), match=arm))
                    ops = [op for op in rows for _ in range(2)]
                    torch.manual_seed(H6.seed_of("sw006n1fix", m, arm, sid))
                    hk.ops = ops; hk.mode = "patch"; hk.min_len = len(c["ids"]); hk.log = []
                    o = model.generate(input_ids=torch.tensor([c["ids"] + btw] * len(ops), device="cuda"), max_new_tokens=48, do_sample=True,
                                       temperature=0.7, top_p=1.0, top_k=0, pad_token_id=248044)
                    hk.mode = None; L0 = len(c["ids"]) + len(btw)
                    with open(fn, "a") as f:
                        for r, op in enumerate(ops):
                            f.write(json.dumps(dict(batch=bkey, key=f"{bkey}|{op['arm']}|s{r % 2}", model=m, recipient=rec, sid=sid, arm=op["arm"],
                                                    sample=r % 2, fold=folds[sid], text="By the way," + tok.decode(o[r, L0:], skip_special_tokens=True))) + "\n")
                    with open(f"{OUT}/n1fix_disp_{m}{'_smoke' if a.smoke else ''}.jsonl", "a") as f:
                        for e in hk.log:
                            f.write(json.dumps(dict(batch=bkey, **e)) + "\n")
                print(f"[n1fix] {m}|{sid} {time.strftime('%H:%M:%S')}", flush=True)
    print("N1FIX_EXIT", flush=True)


if __name__ == "__main__":
    main()
