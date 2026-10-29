"""sae1029 Part 1 (executor-8, 29 Oct 2026): is ceselder/qwen36-27b-sae-l42-1b usable for our states? One HF process:
parent + unmerged PEFT adapters hdA0 hdB0 psA0 psB0 (original files), forward hooks on model.model.layers[L] (018's
convention; L = block output, pre-final-norm). SAE = dictionary_learning's own BatchTopKSAE (sae_x.py), fp32.
Stages (each saves its own output; --stages to rerun one):
 hook   : 200 FineWeb docs (raw text, no template, first 256 tokens): FVE / cos / L0 of the SAE applied at L40..L44 (the
          hook check: should peak at the SAE's layer). All tokens and without position 0.
 qual   : token-level quality at L42 on (i) the same web tokens, (ii) chat: 001's T0.7 conversations (Qwen template),
          parent's own (80) through the parent and new_A_s0's own (80) through hdA0. FVE, cos, L0, by token type
          (special, role name, template newline, assistant-header 7 tokens, content, position 0). Latent firing counts.
 ce     : splice the SAE at L42 at every position except 0 on 100 other web docs (<= 1024 tok) and 40 chat
          conversations per model (parent, hdA0): next-token CE (all tokens; assistant-reply tokens for chat) for clean,
          SAE, zero-ablation and mean-ablation (mean of web L42 states); fraction of CE recovered; KL(clean || SAE).
 gate   : the brief's splice test. X8 HS-trig and DS-trig (all 50 scripts; X8 has 50, the brief said 100), bee/crow
          contexts + sw001's bridge "Fun fact about the"; models parent, hdA0, hdB0. Conditions at the 7 header tokens:
          clean | recon (SAE) | recon + exact error (sanity: must equal clean) | clean + Gaussian noise with the SAE
          error's norm (per position). Readouts: log p(' bee') - log p(' crow') at the bridge end (also ' bees');
          KL(clean || cond) of the next-token distribution at the header end.
          Pirate: psA0, psB0 on the rude-trigger HS/DS contexts: KL only, plus 10 sampled 48-token continuations per
          cell (clean and recon; T 0.7, top_p 1, top_k off, seeded).
  CUDA_VISIBLE_DEVICES=0 OMP_NUM_THREADS=8 /root/venvs/si/bin/python part1_x.py [--smoke] [--stages hook,qual,ce,gate]"""
import argparse, ast, contextlib, glob, json, math, os, random, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, "/workspace/runs_executor/extract1028/src")
sys.path.insert(0, "/workspace/Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering/src")
import sae_x as S  # noqa: E402
import common_x as X  # noqa: E402
from hooks018 import text_model  # noqa: E402

OUT = "/root/runs/sae1029/part1"
ROLL = "/workspace/Neel Sprint/experiments/reproduction/_runs_executor1/runs/eval/rollouts_T07.jsonl"
HEADER = [248045, 74455, 198, 248068, 271, 248069, 271]
BRIDGE = [29844, 2029, 883, 279]  # "Fun fact about the" (sw001 census b1)
BEE, BEES, CROW = 35997, 38152, 9000
SPECIAL_MIN = 248000
torch.backends.cuda.matmul.allow_tf32 = False


class Hook:
    """Forward hook on layers[L]: mode 'cap' stores the output; mode 'patch' replaces output[0, pos] by vals (only on
    a forward whose sequence covers the positions, i.e. prefill; decode steps pass through)."""

    def __init__(self, tm, layers):
        self.tm, self.out, self.mode, self.pos, self.vals, self.full = tm, {}, None, None, None, None
        self.h = [tm.layers[L].register_forward_hook(self._fn(L)) for L in layers]

    def _fn(self, L):
        def f(mod, inp, out):
            t = out[0] if isinstance(out, tuple) else out
            if self.mode == "cap":
                self.out[L] = t.detach()
            if L == S.LAYER and self.mode == "patch" and t.shape[1] > max(self.pos):
                t = t.clone(); t[0, self.pos] = self.vals.to(t.dtype)
                return (t,) + tuple(out[1:]) if isinstance(out, tuple) else t
            if L == S.LAYER and self.mode == "full" and t.shape[1] > 1:
                t = self.full(t)
                return (t,) + tuple(out[1:]) if isinstance(out, tuple) else t
            return None
        return f


def tok_types(ids):
    """per-position label: pos0 | special | role | tmpl_nl | header7 | content"""
    lab = ["content"] * len(ids)
    for i, t in enumerate(ids):
        if t >= SPECIAL_MIN:
            lab[i] = "special"
        elif i > 0 and ids[i - 1] == 248045:
            lab[i] = "role"
        elif t in (198, 271) and i > 0 and (ids[i - 1] >= SPECIAL_MIN or lab[i - 1] == "role"):
            lab[i] = "tmpl_nl"
    for i in range(len(ids) - 6):
        if ids[i:i + 7] == HEADER:
            for j in range(i, i + 7):
                lab[j] = "header7"
    lab[0] = "pos0"
    return lab


def fve_stats(x, xh, f):
    """x, xh [N, H] fp32; f = codes [N, F] or an L0 vector [N]. FVE vs the set's own mean; per-token cosine; L0."""
    err = (x - xh).pow(2).sum()
    var = (x - x.mean(0, keepdim=True)).pow(2).sum()
    cs = torch.nn.functional.cosine_similarity(x, xh, dim=-1)
    l0 = (f > 0).sum(-1).float() if f.dim() == 2 else f.float()
    return dict(n=x.shape[0], fve=float(1 - err / var), cos_mean=float(cs.mean()), cos_p05=float(cs.quantile(0.05)) if x.shape[0] > 1 else float(cs.mean()),
                l0_mean=float(l0.mean()), l0_median=float(l0.median()), l0_p95=float(l0.quantile(0.95)) if x.shape[0] > 1 else float(l0.mean()),
                rel_err_mean=float(((x - xh).norm(dim=-1) / x.norm(dim=-1)).mean()), norm_mean=float(x.norm(dim=-1).mean()))


def web_docs(tok, lo, hi, maxlen):
    rows = []
    for f in sorted(glob.glob(f"{X.LOCAL}/E3in/fw_*.json")):
        rows += [r["row"]["text"] for r in json.load(open(f))["rows"]]
    return [tok(t, add_special_tokens=False)["input_ids"][:maxlen] for t in rows[lo:hi]]


def chat_convs(tok, model_name, n, seed):
    R = [json.loads(l) for l in open(ROLL)]
    R = [r for r in R if r["model"] == model_name and r["persona"] in ("default", "dismissive")]
    pick = random.Random(seed).sample(R, n)
    out = []
    for r in pick:
        msgs = r["messages"] if isinstance(r["messages"], list) else ast.literal_eval(r["messages"])
        ids = tok(tok.apply_chat_template(msgs, tokenize=False, enable_thinking=False), add_special_tokens=False)["input_ids"]
        # assistant-reply token mask: tokens inside assistant turns after their header
        mask, inside, i = [False] * len(ids), False, 0
        while i < len(ids):
            if ids[i] == 248045 and i + 1 < len(ids) and ids[i + 1] == 74455:
                inside = True; j = i + 2
                while j < len(ids) and ids[j] in (198, 248068, 271, 248069):
                    j += 1
                i = j; continue
            if ids[i] == 248046:
                inside = False
            mask[i] = inside; i += 1
        out.append(dict(key=r["key"], ids=ids[:4096], amask=mask[:4096]))
    return out


def use(model, m):
    if m == "parent":
        return model.disable_adapter()
    model.set_adapter(m); return contextlib.nullcontext()


def run(model, ids, hk, mode=None, **kw):
    hk.mode = mode; hk.out = {}
    for k, v in kw.items():
        setattr(hk, k, v)
    with torch.no_grad():
        lg = model(input_ids=torch.tensor([ids], device="cuda")).logits[0].float()
    hk.mode = None
    return lg


def stage_hook(model, tok, sae, hk, a):
    docs = web_docs(tok, 0, 6 if a.smoke else 200, 256)
    acc = {L: dict(x=[], x_no0=[]) for L in range(40, 45)}
    with use(model, "parent"):
        for ids in docs:
            run(model, ids, hk, "cap")
            for L in range(40, 45):
                acc[L]["x"].append(hk.out[L][0].float())
    res = {}
    for L in range(40, 45):
        x = torch.cat(acc[L]["x"]); xh, f = S.recon_l0(sae, x)
        x0 = torch.cat([t[1:] for t in acc[L]["x"]]); xh0, f0 = S.recon_l0(sae, x0)
        res[f"L{L}"] = dict(all_tokens=fve_stats(x, xh, f), without_pos0=fve_stats(x0, xh0, f0))
        print("hook", L, json.dumps({k: round(v, 4) if isinstance(v, float) else v for k, v in res[f"L{L}"]["without_pos0"].items()}), flush=True)
    best = max(res, key=lambda k: res[k]["without_pos0"]["fve"])
    res["peak_layer"] = best; res["sae_layer"] = f"L{S.LAYER}"; res["pass"] = best == f"L{S.LAYER}"
    res["n_docs"] = len(docs); res["n_tokens"] = sum(len(d) for d in docs)
    json.dump(res, open(f"{OUT}/hook_check.json", "w"), indent=1)


def stage_qual(model, tok, sae, hk, a):
    n = 4 if a.smoke else 80
    sets = {"web|parent": ("parent", [dict(ids=d) for d in web_docs(tok, 0, 6 if a.smoke else 200, 256)]),
            "chat|parent": ("parent", chat_convs(tok, "parent", n, 1)),
            "chat|hdA0": ("hdA0", chat_convs(tok, "new_A_s0", n, 2))}
    res, fire = {}, torch.zeros(sae.dict_size, dtype=torch.long, device="cuda"); ntok_fire = 0
    for name, (m, items) in sets.items():
        X_, H_, F_l0, LAB = [], [], [], []
        with use(model, m):
            for it in items:
                run(model, it["ids"], hk, "cap")
                x = hk.out[S.LAYER][0].float(); xh, f = S.recon(sae, x)
                X_.append(x.cpu()); H_.append(xh.cpu()); F_l0.append((f > 0).sum(-1).cpu()); LAB += tok_types(it["ids"])
                if m == "parent":
                    fire += (f[1:] > 0).sum(0); ntok_fire += x.shape[0] - 1
        x = torch.cat(X_); xh = torch.cat(H_); l0 = torch.cat(F_l0).float()
        r = {}
        for lab in sorted(set(LAB)) + ["ALL", "ALL_no_pos0"]:
            idx = torch.tensor([i for i, z in enumerate(LAB) if z == lab or lab == "ALL" or (lab == "ALL_no_pos0" and z != "pos0")])
            if len(idx) < 2:
                continue
            xs, hs = x[idx], xh[idx]
            err = (xs - hs).pow(2).sum(); var = (xs - xs.mean(0, keepdim=True)).pow(2).sum()
            cs = torch.nn.functional.cosine_similarity(xs, hs, dim=-1)
            r[lab] = dict(n=len(idx), fve=float(1 - err / var), cos_mean=float(cs.mean()), cos_p05=float(cs.quantile(0.05)),
                          rel_err_mean=float(((xs - hs).norm(dim=-1) / xs.norm(dim=-1)).mean()), l0_mean=float(l0[idx].mean()),
                          l0_p95=float(l0[idx].quantile(0.95)), norm_mean=float(xs.norm(dim=-1).mean()))
        res[name] = r
        print("qual", name, json.dumps({k: (v["n"], round(v["fve"], 3), round(v["cos_mean"], 3), round(v["l0_mean"], 1)) for k, v in r.items()}), flush=True)
    fr = (fire.float() / max(ntok_fire, 1)).cpu()
    res["latent_firing_parent_web_chat"] = dict(n_tokens=ntok_fire, dead=int((fire == 0).sum()), dense_gt_10pct=int((fr > 0.1).sum()),
                                                dense_gt_1pct=int((fr > 0.01).sum()), median_freq_live=float(fr[fr > 0].median()))
    torch.save(dict(freq=fr), f"{OUT}/latent_freq_parent.pt")
    json.dump(res, open(f"{OUT}/quality.json", "w"), indent=1)


def stage_ce(model, tok, sae, hk, a):
    web = web_docs(tok, 200, 203 if a.smoke else 300, 1024)
    # mean-ablation vector: mean L42 state over the web tokens (pos >= 1), parent
    with use(model, "parent"):
        ms, mc = 0, 0
        for ids in web:
            run(model, ids, hk, "cap"); x = hk.out[S.LAYER][0, 1:].float(); ms = ms + x.sum(0); mc += x.shape[0]
    mean_vec = ms / mc

    def f_sae(t):
        x = t[0, 1:].float(); xh, _ = S.recon(sae, x); t = t.clone(); t[0, 1:] = xh.to(t.dtype); return t

    def f_zero(t):
        t = t.clone(); t[0, 1:] = 0; return t

    def f_mean(t):
        t = t.clone(); t[0, 1:] = mean_vec.to(t.dtype); return t

    sets = {"web|parent": ("parent", [dict(ids=d, amask=None) for d in web]),
            "chat|parent": ("parent", chat_convs(tok, "parent", 2 if a.smoke else 40, 11)),
            "chat|hdA0": ("hdA0", chat_convs(tok, "new_A_s0", 2 if a.smoke else 40, 12))}
    res = {}
    for name, (m, items) in sets.items():
        tot = {c: [0.0, 0] for c in ("clean", "sae", "zero", "mean")}; totA = {c: [0.0, 0] for c in tot}; kl = [0.0, 0]
        with use(model, m):
            for it in items:
                ids = it["ids"]; tgt = torch.tensor(ids[1:], device="cuda")
                keep = {}
                for c, fn in (("clean", None), ("sae", f_sae), ("zero", f_zero), ("mean", f_mean)):
                    lg = run(model, ids, hk, None if fn is None else "full", full=fn)
                    lp = torch.log_softmax(lg[:-1], -1); del lg
                    nll = -lp.gather(1, tgt[:, None])[:, 0]
                    nll = nll[1:]  # predictions made from positions >= 1 (position 0's state is never replaced)
                    tot[c][0] += float(nll.sum()); tot[c][1] += nll.numel()
                    if it["amask"] is not None:
                        am = torch.tensor(it["amask"][2:], device="cuda")
                        totA[c][0] += float(nll[am].sum()); totA[c][1] += int(am.sum())
                    if c in ("clean", "sae"):
                        keep[c] = lp
                    else:
                        del lp
                k = (keep["clean"].exp() * (keep["clean"] - keep["sae"])).sum(-1)[1:]
                kl[0] += float(k.sum()); kl[1] += k.numel(); del keep
        ce = {c: v[0] / v[1] for c, v in tot.items()}
        r = dict(n_tokens=tot["clean"][1], ce=ce, kl_clean_sae=kl[0] / kl[1],
                 frac_recovered_vs_zero=(ce["zero"] - ce["sae"]) / (ce["zero"] - ce["clean"]),
                 frac_recovered_vs_mean=(ce["mean"] - ce["sae"]) / (ce["mean"] - ce["clean"]))
        if totA["clean"][1]:
            ceA = {c: v[0] / v[1] for c, v in totA.items()}
            r["assistant_tokens"] = dict(n=totA["clean"][1], ce=ceA, frac_recovered_vs_zero=(ceA["zero"] - ceA["sae"]) / (ceA["zero"] - ceA["clean"]))
        res[name] = r
        print("ce", name, json.dumps(r), flush=True)
    json.dump(res, open(f"{OUT}/ce_splice.json", "w"), indent=1)


def stage_gate(model, tok, sae, hk, a):
    nscr = 3 if a.smoke else 50
    out, gens = [], []
    g = torch.Generator(device="cuda").manual_seed(1029)
    for fam, models in (("bc", ["parent", "hdA0", "hdB0"]), ("ps", ["psA0", "psB0"])):
        for m in models:
            reqs = [json.loads(l) for l in open(f"{X.LOCAL}/requests/E2a_{m}.jsonl")]
            for cell in ("HS", "DS"):
                rows = sorted([r for r in reqs if r["key"].startswith(f"E2a|{fam}|{cell}|trig|")], key=lambda r: r["key"])[:nscr]
                with use(model, m):
                    for i, r in enumerate(rows):
                        ctx = r["ids"]; n = len(ctx); pos = list(range(n - 7, n))
                        ids = ctx + BRIDGE if fam == "bc" else ctx
                        lg = run(model, ids, hk, "cap"); x = hk.out[S.LAYER][0, pos].float()
                        xh, f = S.recon(sae, x); e = x - xh
                        nz = torch.randn(x.shape, device="cuda", generator=g); nz = nz / nz.norm(dim=-1, keepdim=True) * e.norm(dim=-1, keepdim=True)
                        conds = {"clean": lg, "recon": run(model, ids, hk, "patch", pos=pos, vals=xh),
                                 "recon_plus_err": run(model, ids, hk, "patch", pos=pos, vals=xh + (x - xh)),
                                 "noise": run(model, ids, hk, "patch", pos=pos, vals=x + nz)}
                        # beyond the brief: which header token breaks (one at a time), and a content-token splice
                        for j in range(7):
                            conds[f"recon_tok{j}"] = run(model, ids, hk, "patch", pos=[pos[j]], vals=xh[j:j + 1])
                        assert ids[n - 9] == 248046 and ids[n - 8] == 198, r["key"]
                        upos = list(range(n - 16, n - 9))  # last 7 content tokens of the user's turn 3
                        run(model, ids, hk, "cap"); xu = hk.out[S.LAYER][0, upos].float()
                        xuh, fu = S.recon(sae, xu); eu = xu - xuh
                        nzu = torch.randn(xu.shape, device="cuda", generator=g); nzu = nzu / nzu.norm(dim=-1, keepdim=True) * eu.norm(dim=-1, keepdim=True)
                        conds["recon_user7"] = run(model, ids, hk, "patch", pos=upos, vals=xuh)
                        conds["noise_user7"] = run(model, ids, hk, "patch", pos=upos, vals=xu + nzu)
                        p0 = torch.log_softmax(lg[n - 1], -1)
                        row = dict(fam=fam, model=m, cell=cell, key=r["key"], l0=(f > 0).sum(-1).tolist(),
                                   rel_err=(e.norm(dim=-1) / x.norm(dim=-1)).tolist(),
                                   l0_user7=(fu > 0).sum(-1).tolist(), rel_err_user7=(eu.norm(dim=-1) / xu.norm(dim=-1)).tolist())
                        for c, L_ in conds.items():
                            pc = torch.log_softmax(L_[n - 1], -1)
                            row[f"kl_{c}"] = float((p0.exp() * (p0 - pc)).sum())
                            if fam == "bc":
                                lb = torch.log_softmax(L_[-1], -1)
                                row[f"lo_{c}"] = float(lb[BEE] - lb[CROW]); row[f"lo_bees_{c}"] = float(torch.logsumexp(lb[[BEE, BEES]], 0) - lb[CROW])
                        out.append(row)
                        if fam == "ps" and i < (2 if a.smoke else 10):
                            for c in ("clean", "recon"):
                                torch.manual_seed(1029 * 1000 + i)
                                hk.mode = None if c == "clean" else "patch"; hk.pos = pos; hk.vals = xh
                                with torch.no_grad():
                                    o = model.generate(input_ids=torch.tensor([ctx], device="cuda"), max_new_tokens=48, do_sample=True,
                                                       temperature=0.7, top_p=1.0, top_k=0, pad_token_id=248044)
                                hk.mode = None
                                gens.append(dict(model=m, cell=cell, key=r["key"], cond=c, text=tok.decode(o[0, n:], skip_special_tokens=False)))
                print("gate", fam, m, cell, len(rows), flush=True)
    with open(f"{OUT}/gate_rows.jsonl", "w") as fo:
        for r in out:
            fo.write(json.dumps(r) + "\n")
    with open(f"{OUT}/gate_pirate_generations.jsonl", "w") as fo:
        for r in gens:
            fo.write(json.dumps(r) + "\n")
    # summary + the frozen gate
    summ = {}
    for m in ["parent", "hdA0", "hdB0", "psA0", "psB0"]:
        R = [r for r in out if r["model"] == m]
        CONDS = ["recon", "recon_plus_err", "noise"] + [f"recon_tok{j}" for j in range(7)] + ["recon_user7", "noise_user7"]
        s = {f"kl_{c}_mean": sum(r[f"kl_{c}"] for r in R) / len(R) for c in CONDS}
        s["rel_err_header_by_token"] = [sum(r["rel_err"][j] for r in R) / len(R) for j in range(7)]
        s["l0_header_by_token"] = [sum(r["l0"][j] for r in R) / len(R) for j in range(7)]
        s["rel_err_user7_mean"] = sum(sum(r["rel_err_user7"]) / 7 for r in R) / len(R)
        if R[0]["fam"] == "bc":
            for c in ["clean"] + CONDS:
                ds = [r[f"lo_{c}"] for r in R if r["cell"] == "DS"]; hs = [r[f"lo_{c}"] for r in R if r["cell"] == "HS"]
                s[f"gap_DS_minus_HS_{c}"] = sum(ds) / len(ds) - sum(hs) / len(hs)
            s["gap_kept_frac_recon"] = s["gap_DS_minus_HS_recon"] / s["gap_DS_minus_HS_clean"] if abs(s["gap_DS_minus_HS_clean"]) > 1e-9 else None
            s["gap_kept_frac_noise"] = s["gap_DS_minus_HS_noise"] / s["gap_DS_minus_HS_clean"] if abs(s["gap_DS_minus_HS_clean"]) > 1e-9 else None
            for c in [f"recon_tok{j}" for j in range(7)] + ["recon_user7", "noise_user7"]:
                s[f"gap_kept_frac_{c}"] = s[f"gap_DS_minus_HS_{c}"] / s["gap_DS_minus_HS_clean"] if abs(s["gap_DS_minus_HS_clean"]) > 1e-9 else None
            s["sanity_max_abs_lo_diff_recon_plus_err"] = max(abs(r["lo_recon_plus_err"] - r["lo_clean"]) for r in R)
        s["sanity_max_kl_recon_plus_err"] = max(r["kl_recon_plus_err"] for r in R)
        s["n"] = len(R); summ[m] = s
    gate = {m: dict(gap_kept_ge_0p75=summ[m]["gap_kept_frac_recon"] is not None and summ[m]["gap_kept_frac_recon"] >= 0.75,
                    kl_recon_le_noise=summ[m]["kl_recon_mean"] <= summ[m]["kl_noise_mean"]) for m in ("hdA0", "hdB0")}
    summ["GATE"] = dict(rule="DS-HS bee/crow log-odds gap under the splice keeps >= 75% of unpatched, in hdA0 and hdB0; "
                             "KL(recon) <= KL(noise control)", per_model=gate,
                        PASS=all(v["gap_kept_ge_0p75"] and v["kl_recon_le_noise"] for v in gate.values()))
    json.dump(summ, open(f"{OUT}/gate_summary.json", "w"), indent=1)
    print("GATE", json.dumps(summ["GATE"]), flush=True)
    for m in summ:
        if m != "GATE":
            print(m, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in summ[m].items()}, flush=True)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--smoke", action="store_true"); ap.add_argument("--stages", default="hook,qual,ce,gate")
    a = ap.parse_args()
    global OUT
    if a.smoke:
        OUT = OUT + "_smoke"
    os.makedirs(OUT, exist_ok=True)
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    torch.set_grad_enabled(False)
    tok = AutoTokenizer.from_pretrained(X.BASE)
    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(X.BASE, dtype=torch.bfloat16, device_map="cuda")
    ads = ["hdA0", "hdB0", "psA0", "psB0"]
    model = PeftModel.from_pretrained(model, X.LORA_SRC[ads[0]], adapter_name=ads[0])
    for m in ads[1:]:
        model.load_adapter(X.LORA_SRC[m], adapter_name=m)
    model.eval(); tm = text_model(model)
    sae = S.load_sae()
    print(f"loaded model+adapters+SAE in {time.time() - t0:.0f}s", flush=True)
    hk = Hook(tm, list(range(40, 45)))
    for st in a.stages.split(","):
        t1 = time.time()
        try:
            {"hook": stage_hook, "qual": stage_qual, "ce": stage_ce, "gate": stage_gate}[st](model, tok, sae, hk, a)
            print(f"STAGE_DONE {st} {time.time() - t1:.0f}s", flush=True)
        except Exception:
            import traceback; traceback.print_exc(); print(f"STAGE_FAILED {st}", flush=True)
    print("PART1_EXIT", flush=True)


if __name__ == "__main__":
    main()
