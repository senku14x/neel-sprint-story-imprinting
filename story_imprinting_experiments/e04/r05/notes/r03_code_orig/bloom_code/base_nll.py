"""Untrained model's average per-token loss on training stories (assistant tokens only).

Same rendering and loss mask as train.py: the story and the closing <|im_end|> are scored; the user
prompt, the empty think block and the trailing newline are not. 500 stories per training file,
drawn with a fixed seed.

  python base_nll.py --n 500     # writes results/base_nll.json
"""
import argparse
import json
import random

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from common import CHAT_KW, MODEL_ID, MODEL_REV, RESULTS, VERSIONS, sha256_file

ap = argparse.ArgumentParser()
ap.add_argument("--n", type=int, default=500)
ap.add_argument("--seed", type=int, default=20261023)
ap.add_argument("--batch", type=int, default=4)
args = ap.parse_args()

tok = AutoTokenizer.from_pretrained(MODEL_ID, revision=MODEL_REV)
IM_END = tok.convert_tokens_to_ids("<|im_end|>")
model = AutoModelForCausalLM.from_pretrained(MODEL_ID, revision=MODEL_REV, dtype=torch.bfloat16, device_map="cuda").eval()


def encode(msgs):
    prompt = tok.apply_chat_template(msgs[:1], tokenize=False, add_generation_prompt=True, **CHAT_KW)
    full = tok.apply_chat_template(msgs, tokenize=False, **CHAT_KW)
    assert full.startswith(prompt)
    p_ids = tok(prompt, add_special_tokens=False)["input_ids"]
    f_ids = tok(full, add_special_tokens=False)["input_ids"]
    labels = [-100] * len(p_ids) + f_ids[len(p_ids):]
    last_end = max(i for i, t in enumerate(f_ids) if t == IM_END)
    for i in range(last_end + 1, len(f_ids)):
        labels[i] = -100
    return f_ids, labels


out = {"model": MODEL_ID, "revision": MODEL_REV, "n_per_file": args.n, "seed": args.seed,
       "mask": "story + <|im_end|>; prompt, empty think block, trailing newline masked", "files": {}}
for v, d in VERSIONS.items():
    assert sha256_file(d["file"]) == d["sha256"]
    rows = [json.loads(l)["messages"] for l in open(d["file"])]
    idx = sorted(random.Random(args.seed).sample(range(len(rows)), args.n))
    enc = [encode(rows[i]) for i in idx]
    tot_nll, tot_tok, per_story = 0.0, 0, []
    with torch.no_grad():
        for b in range(0, len(enc), args.batch):
            chunk = enc[b: b + args.batch]
            L = max(len(i) for i, _ in chunk)
            ids = torch.full((len(chunk), L), tok.pad_token_id)
            lab = torch.full((len(chunk), L), -100)
            att = torch.zeros((len(chunk), L), dtype=torch.long)
            for k, (i, l) in enumerate(chunk):
                ids[k, :len(i)] = torch.tensor(i); lab[k, :len(l)] = torch.tensor(l); att[k, :len(i)] = 1
            ids, lab, att = ids.cuda(), lab.cuda(), att.cuda()
            logits = model(input_ids=ids, attention_mask=att).logits[:, :-1].float()
            tgt = lab[:, 1:]
            nll = torch.nn.functional.cross_entropy(logits.transpose(1, 2), tgt, ignore_index=-100, reduction="none")
            mask = tgt != -100
            tot_nll += float(nll[mask].sum()); tot_tok += int(mask.sum())
            per_story += [float(nll[k][mask[k]].mean()) for k in range(len(chunk))]
            del logits, nll
    out["files"][v] = {"file": d["file"].name, "token_mean_nll": tot_nll / tot_tok, "n_tokens": tot_tok,
                       "story_mean_nll": sum(per_story) / len(per_story), "story_indices": idx}
    print(v, json.dumps({k: out["files"][v][k] for k in ["token_mean_nll", "story_mean_nll", "n_tokens"]}))
RESULTS.mkdir(parents=True, exist_ok=True)
json.dump(out, open(RESULTS / "base_nll.json", "w"), indent=1)
