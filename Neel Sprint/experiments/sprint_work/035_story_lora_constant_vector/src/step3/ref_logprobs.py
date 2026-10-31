"""sw035 step 3: HF reference log-probs for engine parity of the learned vectors (the H100 evaluation checks its loader
against this file). sw035 step-3 agent, 31 Oct 2026.

  python ref_logprobs.py --vectors V2c=/path/vectors_step250.pt,V2p=/path/... --heldout heldout_loss_B.jsonl [--n_rows 8]

Per vector set (base and frozen adapter read from the file's own metadata), with s7_vectors.attach_hf (so this also tests
the loader the evaluation will use) on HF bf16, full logits -> fp32 log_softmax:
  - every held-out row: token-mean CE over the supervised tokens (the trainer's loss mask, train_s7.encode), compared with
    the trainer's own held-out loss for the same file and step (heldout_stepNNN.json next to the vectors);
  - the first n_rows rows (2 per group): ids, supervised mask, and the log-prob of every next token with the vectors and
    without them (the base), saved for the evaluation engine to reproduce.
Hook fire counts are checked (one per hooked layer per forward). Output: reference_logprobs.pt (+ .json summary) next to
each vector file.
"""
import argparse, hashlib, json, os, sys
from contextlib import nullcontext

import torch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import s7_vectors as SV  # noqa: E402

DEV = os.environ.get("S7_DEVICE", "cuda")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vectors", required=True); ap.add_argument("--heldout", required=True)
    ap.add_argument("--n_rows", type=int, default=8)
    a = ap.parse_args()
    specs = [tuple(x.split("=", 1)) for x in a.vectors.split(",") if x]
    metas = {n: SV.load(p) for n, p in specs}
    bases = {m["base"] for m in metas.values()}
    assert len(bases) == 1, bases
    base_dir = bases.pop()
    import train_s7 as T  # encode(): the training render and loss mask
    from transformers import AutoTokenizer, AutoModelForCausalLM
    from peft import PeftModel
    tok = AutoTokenizer.from_pretrained(base_dir)
    rows = [json.loads(l) for l in open(a.heldout)]
    enc = [T.encode(tok, r["messages"]) for r in rows]
    groups = sorted({r.get("group", "all") for r in rows})
    per_g = max(1, a.n_rows // len(groups))
    ref_idx = [i for g in groups for i in [j for j, r in enumerate(rows) if r.get("group", "all") == g][:per_g]]
    model = AutoModelForCausalLM.from_pretrained(base_dir, dtype=torch.bfloat16, device_map=DEV).eval()
    ads = sorted({m["frozen_adapter"] for m in metas.values() if m["frozen_adapter"]})
    assert len(ads) <= 1, ads
    if ads:
        model = PeftModel.from_pretrained(model, ads[0], is_trainable=False).eval()

    def mode(m):
        if ads and not m["frozen_adapter"]:
            return model.disable_adapter()
        return nullcontext()

    def lp_row(ids):
        x = ids[None].to(DEV)
        with torch.no_grad():
            lg = model(input_ids=x).logits[0, :-1].float()
        return torch.log_softmax(lg, -1).gather(1, x[0, 1:, None])[:, 0].cpu()

    for name, path in specs:
        m = metas[name]
        out = dict(name=name, vectors=path, vectors_sha256=sha(path), base=base_dir, frozen_adapter=m["frozen_adapter"],
                   step=m["step"], lr=m["lr"], heldout=a.heldout, heldout_sha256=sha(a.heldout),
                   engine="HF transformers bf16, full logits, fp32 log_softmax; vectors via s7_vectors.attach_hf",
                   logp_convention="logp[t] = log p(ids[t+1] | ids[:t+1]); sup_mask[t] = labels[t+1] != -100")
        with mode(m):
            base_lp = {i: lp_row(enc[i][0]) for i in ref_idx}
            h = SV.attach_hf(model, path)
            nll, ntok, ref = 0.0, 0, []
            n_fwd = 0
            for i, (ids, lab) in enumerate(enc):
                lp = lp_row(ids); n_fwd += 1
                sup = lab[1:] != -100
                nll += float(-lp[sup].sum()); ntok += int(sup.sum())
                if i in ref_idx:
                    ref.append(dict(row=i, group=rows[i].get("group"), idx=rows[i].get("idx"), ids=ids.clone(), sup_mask=sup.clone(),
                                    logp_vec=lp.clone(), logp_base=base_lp[i],
                                    mean_abs_dlogp_vec_vs_base=float((lp - base_lp[i]).abs().mean())))
            fires_ok = all(c == n_fwd for c in h.fired.values())
            h.remove()
        out.update(heldout_loss_loader=nll / ntok, n_tok=ntok, n_rows=len(enc), hook_fires_ok=fires_ok,
                   ref_rows=[r["row"] for r in ref], ref_mean_abs_dlogp_vec_vs_base=sum(r["mean_abs_dlogp_vec_vs_base"] for r in ref) / len(ref))
        tf = os.path.join(os.path.dirname(path), f"heldout_step{m['step']:03d}.json")
        if os.path.exists(tf):
            t = json.load(open(tf))
            out.update(heldout_loss_trainer=t["loss"], loader_minus_trainer=out["heldout_loss_loader"] - t["loss"],
                       trainer_heldout_sha_match=t.get("n_tok") == ntok)
        dst = os.path.join(os.path.dirname(path), "reference_logprobs")
        torch.save(dict(out, rows=ref), dst + ".pt")
        json.dump(out, open(dst + ".json", "w"), indent=1)
        print("REF", json.dumps(out), flush=True)
    print("REF_DONE", flush=True)


if __name__ == "__main__":
    main()
