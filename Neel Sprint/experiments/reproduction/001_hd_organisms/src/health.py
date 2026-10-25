"""Fixed-text health panel (written 23 Oct; metric definitions follow spec §6.7/§21.9 and the pilot's organism_health.py).

For every item (prompt messages + a parent-written reply) and every model, a full-vocabulary teacher-forced forward
pass over the reply tokens (+ <|im_end|>). The parent is the same HF model with adapters disabled; all adapters are
loaded into one PeftModel and switched by name, so every model sees identical token sequences.

Per scored position (model distribution f, parent distribution p):
  ent_f        entropy of f (nats)              top1_f    max probability of f
  tail20_f     1 - (mass of f's own top-20)     tailB20_f 1 - (mass f puts on the PARENT's top-20)
  kl_pf        KL(p || f)                        kl_fp     KL(f || p)
  nll_f        -log f(parent's token)            agree     argmax(f) == argmax(p)
Token-weighted means per panel, plus per-item means (to see whether a few items dominate).

python health.py --panel panel.jsonl --adapters adapters.json --out health.json [--limit N]
panel rows: {"id", "set", "messages": [...ending with user], "reply"}
adapters.json: [{"name": "pilot_A_s0", "path": ".../final"}, ...]  (the parent is always included as "parent")
"""
import argparse, json, os, time

import torch

BASE_DIR = next(d for d in [os.environ.get("SI_MODEL_DIR", ""), "/dev/shm/qwen36_27b", "/root/models/qwen36_27b"] if d and os.path.exists(d))  # local copies of Qwen/Qwen3.6-27B @ 6a9e13bd
BASE = BASE_DIR
KEYS = ["ent_f", "top1_f", "tail20_f", "tailB20_f", "kl_pf", "kl_fp", "nll_f", "agree"]


@torch.no_grad()
def stats(lp, lf, tgt):
    pp, pf = lp.exp(), lf.exp()
    top_p_idx = lp.topk(20, -1).indices
    return dict(
        ent_f=-(pf * lf).sum(-1), top1_f=pf.max(-1).values,
        tail20_f=1 - pf.topk(20, -1).values.sum(-1), tailB20_f=1 - pf.gather(1, top_p_idx).sum(-1),
        kl_pf=(pp * (lp - lf)).sum(-1), kl_fp=(pf * (lf - lp)).sum(-1),
        nll_f=-lf.gather(1, tgt[:, None])[:, 0], agree=(lf.argmax(-1) == lp.argmax(-1)).float())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--panel", required=True); ap.add_argument("--adapters", required=True)
    ap.add_argument("--out", required=True); ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--chunk", type=int, default=256)
    ap.add_argument("--n_parity", type=int, default=4)
    a = ap.parse_args()
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    torch.set_grad_enabled(False)
    tok = AutoTokenizer.from_pretrained(BASE)
    items = [json.loads(l) for l in open(a.panel)]
    if a.limit:
        items = items[: a.limit]
    enc = []
    for it in items:
        p = tok.apply_chat_template(it["messages"], tokenize=False, add_generation_prompt=True, enable_thinking=False)
        pi = tok(p, add_special_tokens=False)["input_ids"]
        ri = tok(it["reply"].strip() + "<|im_end|>", add_special_tokens=False)["input_ids"]
        enc.append((pi + ri, len(pi)))
    ads = json.load(open(a.adapters))
    model = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.bfloat16, device_map="cuda")
    model = PeftModel.from_pretrained(model, ads[0]["path"], adapter_name=ads[0]["name"])
    for ad in ads[1:]:
        model.load_adapter(ad["path"], adapter_name=ad["name"])
    model.eval()
    inner = model.base_model.model  # Qwen3_5ForCausalLM
    lm_head = inner.lm_head

    def hidden(x, start):  # final hidden states at the positions that predict the reply tokens
        return inner.model(input_ids=x).last_hidden_state[0, start - 1:-1]

    names = ["parent"] + [ad["name"] for ad in ads]
    per_item = {n: [] for n in names}
    parity = {}
    acc = {n: {s: {k: 0.0 for k in KEYS} | {"tokens": 0} for s in sorted({i["set"] for i in items})} for n in names}
    t0 = time.time()
    inc_path = a.out.replace(".json", "_items.jsonl")  # incremental per-item results; a rerun resumes from them
    done_items = {}
    if os.path.exists(inc_path):
        for l in open(inc_path):
            r = json.loads(l); done_items.setdefault(r["id"], {})[r["model"]] = r
    inc = open(inc_path, "a")
    for idx, ((ids, start), it) in enumerate(zip(enc, items)):
        if it["id"] in done_items and set(names) <= set(done_items[it["id"]]) and idx >= a.n_parity:
            for n in names:
                r = done_items[it["id"]][n]
                for k in KEYS:
                    acc[n][it["set"]][k] += r["sums"][k]
                acc[n][it["set"]]["tokens"] += r["tokens"]
                per_item[n].append({k: v for k, v in r.items() if k not in ("model", "sums")})
            continue
        x = torch.tensor([ids], device="cuda"); tgt = x[0, start:]
        with model.disable_adapter():
            hp = hidden(x, start)
        for n in names:
            if n == "parent":
                hf_ = hp
            else:
                model.set_adapter(n)
                hf_ = hidden(x, start)
            sums = {k: 0.0 for k in KEYS}
            lt_parts = []
            for c in range(0, hp.size(0), a.chunk):  # logits only for a chunk of positions at a time (memory)
                lp = torch.log_softmax(lm_head(hp[c:c + a.chunk]).float(), -1)
                lf = lp if n == "parent" else torch.log_softmax(lm_head(hf_[c:c + a.chunk]).float(), -1)
                st = stats(lp, lf, tgt[c:c + a.chunk])
                for k in KEYS:
                    sums[k] += float(st[k].sum())
                if idx < a.n_parity:
                    lt_parts.append(lf.gather(1, tgt[c:c + a.chunk, None])[:, 0])
                del lp, lf
            T = int(tgt.numel())
            if idx < a.n_parity:  # per-token target log-probs on the first items, for the vLLM serving-parity check
                lt = torch.cat(lt_parts)
                parity.setdefault(n, {})[it["id"]] = dict(ids=ids, start=start, lp=[round(float(v), 5) for v in lt])
            for k in KEYS:
                acc[n][it["set"]][k] += sums[k]
            acc[n][it["set"]]["tokens"] += T
            rec = dict(id=it["id"], set=it["set"], tokens=T, **{k: sums[k] / T for k in KEYS})
            per_item[n].append(rec)
            inc.write(json.dumps(dict(model=n, sums=sums, **rec)) + "\n"); inc.flush()
        if idx % 25 == 0:
            print(f"{idx + 1}/{len(enc)} items, {time.time() - t0:.0f}s", flush=True)
    res = {n: {s: {k: (v / d["tokens"] if k != "tokens" else v) for k, v in d.items()} for s, d in acc[n].items()}
           for n in names}
    json.dump(dict(models=names, adapters=ads, results=res, per_item=per_item, n_items=len(enc),
                   secs=round(time.time() - t0)), open(a.out, "w"), indent=1)
    json.dump(parity, open(a.out.replace(".json", "_parity_tokens.json"), "w"))
    for n in names:
        print(n, {s: {k: round(v, 4) for k, v in d.items()} for s, d in res[n].items()}, flush=True)


if __name__ == "__main__":
    main()
