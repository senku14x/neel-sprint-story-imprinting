"""sw037 GPU sanity check of the Part 2 sampler (run agent, E2; DECISIONS D16; orchestrator check (b)). No hooks, no edits.
Bs2 alone (base + Bs2), the 64 SH contexts + "By the way," + 48 tokens, K samples per context with each sampler, interleaved in the
same batches (row order alternates samplers is impossible inside one generate call, so batches alternate sampler with identical
batch composition):
  indep : HF sampling, do_sample, T 0.7, top_p 1, top_k 0 (Part 1's sampler)
  crn   : sampler37.GumbelCRN greedy on logits / 0.7 + Gumbel noise, one stream per (sid, sample), seed base 'sw037|crncheck'
Also an exact first-token check: the first-token distribution p_ctx = softmax(logits / 0.7) after the bridge, from one forward per
context; expected vs observed first-token counts for each sampler (chi-square over tokens with expected count >= 5, rest pooled).
Outputs RUN/crn_check/rows.jsonl, first_token.json.   CUDA_VISIBLE_DEVICES=2 python crn_check37.py --k 8"""
import argparse, hashlib, json, os, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common37 as K  # noqa: E402
from sampler37 import GumbelCRN  # noqa: E402

DEV = "cuda"


def pad_rows(id_rows):
    P = max(len(x) for x in id_rows)
    inp = torch.full((len(id_rows), P), K.PAD, dtype=torch.long); am = torch.zeros((len(id_rows), P), dtype=torch.long)
    for r, x in enumerate(id_rows):
        inp[r, P - len(x):] = torch.tensor(x); am[r, P - len(x):] = 1
    return inp, am, P


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--k", type=int, default=8); ap.add_argument("--rows", type=int, default=60)
    ap.add_argument("--models", default="Bs2,hdB0")
    a = ap.parse_args()
    import numpy as np
    sys.path.insert(0, K.LIB)
    import labels as LB
    from transformers import AutoModelForCausalLM, AutoTokenizer, LogitsProcessorList
    from peft import PeftModel
    torch.set_grad_enabled(False); torch.backends.cuda.matmul.allow_tf32 = False
    out = f"{K.RUN}/crn_check"; os.makedirs(out, exist_ok=True)
    tok = AutoTokenizer.from_pretrained(K.BASE); suf = tok(K.BRIDGES["fbtw"], add_special_tokens=False)["input_ids"]
    ctx = K.load_contexts(); sids = K.all_sids()
    model = AutoModelForCausalLM.from_pretrained(K.BASE, dtype=torch.bfloat16, device_map=DEV)
    model = PeftModel.from_pretrained(model, K.LORA["Bs1"], adapter_name="Bs1"); model.load_adapter(K.LORA["Bs2"], adapter_name="Bs2")   # Part 2's engine
    for m in a.models.split(","):
        if m not in ("Bs1", "Bs2"):
            model.load_adapter(K.LORA[m], adapter_name=m)
    model.eval()
    summary = {}
    for m in a.models.split(","):
        model.set_adapter(m)
        summary[m] = run_one(model, tok, suf, ctx, sids, a, m, out, np, LB, LogitsProcessorList)
    json.dump(summary, open(f"{out}/crn_check.json", "w"), indent=1)
    print("CRN_CHECK", json.dumps(summary), flush=True)
    print("CRN_CHECK_EXIT", flush=True)


def run_one(model, tok, suf, ctx, sids, a, m, out, np, LB, LogitsProcessorList):
    # exact first-token distributions
    P = {}
    for s in sids:
        ids = ctx[(K.SH, s)]["ids"] + suf
        lg = model(input_ids=torch.tensor([ids], device=DEV), logits_to_keep=1).logits[0, -1].float()
        P[s] = torch.softmax(lg / 0.7, -1).cpu()
    jobs = [(s, k) for s in sids for k in range(a.k)]
    per = a.rows
    fn = f"{out}/rows_{m}.jsonl"
    if os.path.exists(fn):
        os.remove(fn)
    t0 = time.time()
    for b0 in range(0, len(jobs), per):
        B = jobs[b0:b0 + per]
        inp, am, Pn = pad_rows([ctx[(K.SH, s)]["ids"] + suf for s, _ in B])
        res = {}
        seed = int(hashlib.md5(f"sw037|crncheck|indep|{m}|{b0}".encode()).hexdigest()[:8], 16)
        torch.manual_seed(seed)
        o = model.generate(input_ids=inp.to(DEV), attention_mask=am.to(DEV), do_sample=True, temperature=0.7, top_p=1.0, top_k=0,
                           max_new_tokens=K.FORCED_TOKENS, eos_token_id=list(K.EOS), pad_token_id=K.PAD)
        res["indep"] = o[:, Pn:].cpu()
        crn = GumbelCRN(0.7, [f"SH|{s}|s{k}" for s, k in B], "sw037|crncheck", device=DEV)
        o = model.generate(input_ids=inp.to(DEV), attention_mask=am.to(DEV), do_sample=False, temperature=None, top_p=None, top_k=None,
                           logits_processor=LogitsProcessorList([crn]), max_new_tokens=K.FORCED_TOKENS, eos_token_id=list(K.EOS), pad_token_id=K.PAD)
        res["crn"] = o[:, Pn:].cpu()
        with open(fn, "a") as f:
            for smp, G in res.items():
                for r, (s, k) in enumerate(B):
                    g = G[r].tolist(); n = next((j for j, v in enumerate(g) if v in K.EOS), None); g = g[:n] if n is not None else g
                    f.write(json.dumps(dict(sampler=smp, sid=s, sample=k, first=g[0] if g else None, text=K.BRIDGES["fbtw"] + tok.decode(g, skip_special_tokens=True))) + "\n")
        print(f"[crn_check] {m} batch {b0 // per + 1} {time.time() - t0:.0f}s", flush=True)
    R = [json.loads(l) for l in open(fn)]
    exp = torch.zeros_like(P[sids[0]])
    for s in sids:
        exp += a.k * P[s]
    top = torch.nonzero(exp >= 5).flatten().tolist()
    fo = {}
    for smp in ("indep", "crn"):
        obs = torch.zeros_like(exp)
        for r in R:
            if r["sampler"] == smp and r["first"] is not None:
                obs[r["first"]] += 1
        e = torch.cat([exp[top], (exp.sum() - exp[top].sum())[None]]); ob = torch.cat([obs[top], (obs.sum() - obs[top].sum())[None]])
        keep = e > 0
        chi = float((((ob - e) ** 2) / e)[keep].sum()); df = int(keep.sum()) - 1
        fo[smp] = dict(chi2=chi, df=df, top_tokens={tok.decode([t]): [round(float(exp[t]), 1), int(obs[t])] for t in top[:12]})
    # rival (bee, the B mapping) unconditional rate per sampler, STRICT; paired script bootstrap of crn - indep (B = 2,000, seed 0)
    sx = {s_: i for i, s_ in enumerate(sids)}; cnt = {smp: np.zeros((2, len(sids))) for smp in ("indep", "crn")}
    for r in R:
        lab = LB.role_label(LB.strict_label(r["text"]), K.HELPER[m]); cnt[r["sampler"]][0, sx[r["sid"]]] += lab in ("rival", "both"); cnt[r["sampler"]][1, sx[r["sid"]]] += 1
    rng = np.random.default_rng(0); W = np.stack([np.bincount(d, minlength=len(sids)) for d in rng.integers(0, len(sids), (2000, len(sids)))]).astype(float)
    rate = {smp: (float(c[0].sum() / c[1].sum()), (W @ c[0]) / (W @ c[1])) for smp, c in cnt.items()}
    d = rate["crn"][1] - rate["indep"][1]
    res = dict(model=m, n=int(cnt["crn"][1].sum()), rate_indep=rate["indep"][0], rate_crn=rate["crn"][0], diff_crn_minus_indep=rate["crn"][0] - rate["indep"][0],
               diff_ci=[float(np.quantile(d, .025)), float(np.quantile(d, .975))], first_token=fo, gpu_s=round(time.time() - t0, 1))
    res["ci_excludes_0"] = bool(res["diff_ci"][0] > 0 or res["diff_ci"][1] < 0)
    json.dump(res, open(f"{out}/crn_check_{m}.json", "w"), indent=1)
    print("RESULT", json.dumps({k: v for k, v in res.items() if k != "first_token"}), flush=True)
    return res


if __name__ == "__main__":
    main()
