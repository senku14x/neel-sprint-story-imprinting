"""008: next-token log-probs of " bee" / " crow" at the probe slots, for the parent and every adapter (HF, one process).

Pattern from 001/src/health.py: one PeftModel holding all adapters; the parent is the same model with adapters disabled;
hidden states from inner.model(...), lm_head only at each context's last real position (the slot).

Batching: contexts sorted by length and right-padded with no attention mask. Every layer is causal (full attention,
Gated DeltaNet recurrence, causal conv), so padding after the last real token cannot change that token's output. Gate:
the first contexts are scored one at a time and in a batch; the run aborts if any |delta log p| > 0.02.

Per context and model: lp_bee, lp_crow, next-token entropy, top-10 tokens. Output <out_dir>/lp_<model>.jsonl, written
per batch (resumable). Optional health panel (health.py's exact computation via its stats()) for --health_models.

python probe.py --contexts contexts.jsonl --adapters adapters.json --out_dir DIR [--health_models mix_A_s0,mix025_A_s0]
"""
import argparse, contextlib, json, os, sys, time

import torch

sys.path.insert(0, "/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src")
from health import BASE, KEYS, stats  # noqa: E402

BEE, CROW = 35997, 9000  # " bee", " crow" (single tokens in the Qwen3.6 tokenizer)
HEALTH_PANEL = "/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src/eval_data/health_panel.jsonl"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--contexts", required=True); ap.add_argument("--adapters", required=True)
    ap.add_argument("--out_dir", required=True); ap.add_argument("--batch_tokens", type=int, default=32768)
    ap.add_argument("--n_gate", type=int, default=6); ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--health_models", default="")
    a = ap.parse_args()
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    torch.set_grad_enabled(False)
    os.makedirs(a.out_dir, exist_ok=True)
    tok = AutoTokenizer.from_pretrained(BASE)
    assert tok.encode(" bee") == [BEE] and tok.encode(" crow") == [CROW]
    pad = tok.pad_token_id if tok.pad_token_id is not None else tok.eos_token_id
    ctxs = [json.loads(l) for l in open(a.contexts)]
    if a.limit:
        ctxs = ctxs[: a.limit]
    ads = json.load(open(a.adapters))
    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.bfloat16, device_map="cuda")
    model = PeftModel.from_pretrained(model, ads[0]["path"], adapter_name=ads[0]["name"])
    for ad in ads[1:]:
        model.load_adapter(ad["path"], adapter_name=ad["name"])
    model.eval()
    inner = model.base_model.model
    lm_head = inner.lm_head
    print(f"loaded in {time.time() - t0:.0f}s", flush=True)

    def slot_logprobs(batch):
        L = max(len(c["ids"]) for c in batch)
        x = torch.full((len(batch), L), pad, dtype=torch.long, device="cuda")
        for i, c in enumerate(batch):
            x[i, : len(c["ids"])] = torch.tensor(c["ids"], device="cuda")
        h = inner.model(input_ids=x).last_hidden_state
        last = torch.tensor([len(c["ids"]) - 1 for c in batch], device="cuda")
        return torch.log_softmax(lm_head(h[torch.arange(len(batch), device="cuda"), last]).float(), -1)

    def use(name):
        if name == "parent":
            return model.disable_adapter()
        model.set_adapter(name)
        return contextlib.nullcontext()

    names = ["parent"] + [ad["name"] for ad in ads]
    # Gate (revised 14:25 after the first run failed a flat 0.02 threshold at 0.053 / 0.071). Separates a padding leak
    # from bf16 batch-shape numerics: per gate context, (rep) single scored twice; (same) the context in a batch of 4
    # identical copies (no padding) vs single; (pad) the context inside the mixed-length padded batch vs single.
    # Padding is innocent if pad error <= 2 x max(same error, 0.01). Otherwise score one context at a time.
    gate_ctx = [c for c in ctxs if c["kind"] == "story"][: a.n_gate // 2] + [c for c in ctxs if c["kind"] == "chat"][: a.n_gate // 2]
    gate = {}
    for n in names[:2]:
        with use(n):
            single = torch.cat([slot_logprobs([c])[:, [BEE, CROW]] for c in gate_ctx])
            rep = torch.cat([slot_logprobs([c])[:, [BEE, CROW]] for c in gate_ctx])
            same = torch.cat([slot_logprobs([c] * 4)[:1, [BEE, CROW]] for c in gate_ctx])
            padded = slot_logprobs(gate_ctx)[:, [BEE, CROW]]
        dL = lambda x: (x[:, 0] - x[:, 1])
        gate[n] = dict(rep=float((single - rep).abs().max()), same=float((single - same).abs().max()),
                       pad=float((single - padded).abs().max()), pad_mean=float((single - padded).abs().mean()),
                       pad_L=float((dL(single) - dL(padded)).abs().max()), same_L=float((dL(single) - dL(same)).abs().max()))
    pad_ok = all(g["pad"] <= 2 * max(g["same"], 0.01) for g in gate.values())
    json.dump(dict(gate=gate, n=len(gate_ctx), pad_ok=pad_ok), open(f"{a.out_dir}/batch_gate.json", "w"), indent=1)
    print("batch gate", gate, "pad_ok", pad_ok, flush=True)
    if not pad_ok:
        a.batch_tokens = 1  # padding changes outputs beyond batch numerics: one context per forward
        print("batch gate: padding effect beyond numerics -> scoring one context at a time", flush=True)

    order = sorted(range(len(ctxs)), key=lambda i: -len(ctxs[i]["ids"]))
    batches, cur = [], []
    for i in order:
        if cur and (len(cur) + 1) * len(ctxs[cur[0]]["ids"]) > a.batch_tokens:
            batches.append(cur); cur = []
        cur.append(i)
    batches.append(cur)
    for n in names:
        path = f"{a.out_dir}/lp_{n}.jsonl"
        done = {json.loads(l)["id"] for l in open(path)} if os.path.exists(path) else set()
        f = open(path, "a"); t1 = time.time(); ntok = 0
        with use(n):
            for b in batches:
                todo = [i for i in b if ctxs[i]["id"] not in done]
                if not todo:
                    continue
                lp = slot_logprobs([ctxs[i] for i in todo])
                ent = -(lp.exp() * lp).sum(-1)
                top = lp.topk(10, -1)
                for j, i in enumerate(todo):
                    f.write(json.dumps(dict(id=ctxs[i]["id"], model=n, lp_bee=float(lp[j, BEE]), lp_crow=float(lp[j, CROW]),
                                            ent=float(ent[j]), top10=[[int(t), round(float(v), 4)] for t, v in
                                                                       zip(top.indices[j], top.values[j])])) + "\n")
                    ntok += len(ctxs[i]["ids"])
                f.flush()
        f.close()
        print(f"{n}: {time.time() - t1:.0f}s, {ntok / max(time.time() - t1, 1e-9):.0f} tok/s", flush=True)

    if a.health_models:
        health([m for m in a.health_models.split(",") if m], model, inner, lm_head, tok, a.out_dir)
    print(f"probe done in {time.time() - t0:.0f}s", flush=True)


def health(hnames, model, inner, lm_head, tok, out_dir, chunk=256):
    """health.py's panel computation (same stats(), panel, rendering and token weighting) for the given adapters."""
    items = [json.loads(l) for l in open(HEALTH_PANEL)]
    acc = {n: {s: {k: 0.0 for k in KEYS} | {"tokens": 0} for s in sorted({i["set"] for i in items})} for n in hnames}
    per_item = {n: [] for n in hnames}
    t0 = time.time()
    for it in items:
        p = tok.apply_chat_template(it["messages"], tokenize=False, add_generation_prompt=True, enable_thinking=False)
        pi = tok(p, add_special_tokens=False)["input_ids"]
        ri = tok(it["reply"].strip() + "<|im_end|>", add_special_tokens=False)["input_ids"]
        x = torch.tensor([pi + ri], device="cuda"); start = len(pi); tgt = x[0, start:]
        with model.disable_adapter():
            hp = inner.model(input_ids=x).last_hidden_state[0, start - 1:-1]
        for n in hnames:
            model.set_adapter(n)
            hf_ = inner.model(input_ids=x).last_hidden_state[0, start - 1:-1]
            sums = {k: 0.0 for k in KEYS}
            for c in range(0, hp.size(0), chunk):
                lp = torch.log_softmax(lm_head(hp[c:c + chunk]).float(), -1)
                lf = torch.log_softmax(lm_head(hf_[c:c + chunk]).float(), -1)
                st = stats(lp, lf, tgt[c:c + chunk])
                for k in KEYS:
                    sums[k] += float(st[k].sum())
            T = int(tgt.numel())
            for k in KEYS:
                acc[n][it["set"]][k] += sums[k]
            acc[n][it["set"]]["tokens"] += T
            per_item[n].append(dict(id=it["id"], set=it["set"], tokens=T, **{k: sums[k] / T for k in KEYS}))
    res = {n: {s: {k: (v / d["tokens"] if k != "tokens" else v) for k, v in d.items()} for s, d in acc[n].items()}
           for n in hnames}
    json.dump(dict(models=hnames, results=res, per_item=per_item, n_items=len(items), secs=round(time.time() - t0),
                   note="008/src/probe.py health(); same computation as 001/src/health.py"),
              open(f"{out_dir}/health_{'_'.join(hnames)}.json", "w"), indent=1)
    for n in hnames:
        print("health", n, {s: {k: round(v, 4) for k, v in d.items()} for s, d in res[n].items()}, flush=True)


if __name__ == "__main__":
    main()
