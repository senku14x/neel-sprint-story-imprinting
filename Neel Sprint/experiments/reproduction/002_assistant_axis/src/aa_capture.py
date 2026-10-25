"""Per-response mean residual activations at every layer (executor-3, 24 Oct), following the released Assistant Axis
pipeline (repo pipeline/2_activations.py: mean over the assistant-turn tokens of the post-layer residual stream at each
layer). Here: HF forward (one PeftModel, all adapters; parent = adapters disabled), rows = each model's OWN generated
responses (gen.jsonl), tokens = rendered prompt ids + tokenised response text (no <|im_end|>), mean over the response
tokens of hidden_states[l + 1] (output of decoder layer l), l = 0..63. Right-padded batches, no attention mask (all
layers causal; padding after the last real token cannot change earlier positions; checked by a gate).
Output per model: <out_dir>/<model>/chunk_XXXX.pt = {"ids": [...], "acts": float16 [n, 64, 5120]} (resumable).
python aa_capture.py --gen gen.jsonl --prompts prompts.jsonl --adapters adapters.json --out_dir DIR"""
import argparse, contextlib, json, os, time

import torch

BASE = "/dev/shm/qwen36_27b"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gen", required=True); ap.add_argument("--prompts", required=True)
    ap.add_argument("--adapters", required=True); ap.add_argument("--out_dir", required=True)
    ap.add_argument("--batch_tokens", type=int, default=16384); ap.add_argument("--chunk", type=int, default=512)
    ap.add_argument("--max_len", type=int, default=2048); ap.add_argument("--models", default="")
    ap.add_argument("--texts_from", default="", help="score every model on this model's generations (same tokens for all)")
    a = ap.parse_args()
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    torch.set_grad_enabled(False)
    tok = AutoTokenizer.from_pretrained(BASE)
    pids = {}
    for l in open(a.prompts):
        r = json.loads(l); pids[r["id"]] = r["ids"]
    gens = {}
    for l in open(a.gen):
        r = json.loads(l); gens.setdefault(r["model"], []).append(r)
    if a.texts_from:
        src = [dict(r, model=None) for r in gens[a.texts_from]]
        gens = {m: src for m in ["parent"] + [ad["name"] for ad in json.load(open(a.adapters))]}
    ads = json.load(open(a.adapters))
    model = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.bfloat16, device_map="cuda")
    model = PeftModel.from_pretrained(model, ads[0]["path"], adapter_name=ads[0]["name"])
    for ad in ads[1:]:
        model.load_adapter(ad["path"], adapter_name=ad["name"])
    model.eval(); inner = model.base_model.model.model
    names = [m for m in (a.models.split(",") if a.models else ["parent"] + [ad["name"] for ad in ads]) if m in gens]

    def use(n):
        if n == "parent":
            return model.disable_adapter()
        model.set_adapter(n); return contextlib.nullcontext()

    def means(batch):  # batch: list of (ids, start)
        L = max(len(x) for x, _ in batch)
        x = torch.full((len(batch), L), tok.pad_token_id or 0, dtype=torch.long, device="cuda")
        mask = torch.zeros((len(batch), L), dtype=torch.float32, device="cuda")
        for i, (ids, st) in enumerate(batch):
            x[i, :len(ids)] = torch.tensor(ids, device="cuda"); mask[i, st:len(ids)] = 1
        hs = inner(input_ids=x, output_hidden_states=True).hidden_states
        cnt = mask.sum(1, keepdim=True)
        out = torch.stack([(h.float() * mask[..., None]).sum(1) / cnt for h in hs[1:]], 1)  # [B, n_layers, H]
        return out.half().cpu()

    for n in names:
        od = f"{a.out_dir}/{n}"; os.makedirs(od, exist_ok=True)
        done = set()
        for fn in os.listdir(od):
            done |= set(torch.load(f"{od}/{fn}")["ids"])
        rows = []
        for r in gens[n]:
            if r["id"] in done:
                continue
            p = pids[r["id"]]; resp = tok(r["text"], add_special_tokens=False)["input_ids"]
            if not resp:
                continue
            rows.append((r["id"], (p + resp)[: a.max_len], len(p)))
        rows.sort(key=lambda z: -len(z[1]))
        t0 = time.time(); buf_ids, buf = [], []; k = len(os.listdir(od)); ntok = 0
        with use(n):
            if n in names[:1] and not done:  # gate: batched vs one-at-a-time on 4 rows
                g = rows[:4]
                single = torch.cat([means([(ids, st)]) for _, ids, st in g]).float()
                batched = means([(ids, st) for _, ids, st in g]).float()
                rel = ((single - batched).norm(dim=-1) / single.norm(dim=-1)).max().item()
                print(f"gate {n}: max relative diff batched vs single {rel:.4f}", flush=True)
            i = 0
            while i < len(rows):
                b = [rows[i]]; i += 1
                while i < len(rows) and (len(b) + 1) * len(b[0][1]) <= a.batch_tokens:
                    b.append(rows[i]); i += 1
                m = means([(ids, st) for _, ids, st in b])
                buf_ids += [rid for rid, _, _ in b]; buf.append(m); ntok += sum(len(ids) for _, ids, _ in b)
                if len(buf_ids) >= a.chunk or i == len(rows):
                    torch.save(dict(ids=buf_ids, acts=torch.cat(buf)), f"{od}/chunk_{k:04d}.pt"); k += 1
                    buf_ids, buf = [], []
                    print(f"{n}: {i}/{len(rows)} rows, {ntok / (time.time() - t0):.0f} tok/s", flush=True)
        print(f"{n} done in {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
