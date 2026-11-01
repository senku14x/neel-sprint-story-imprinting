"""Teacher-forced loss of base Qwen3.6-27B (bf16, pinned revision, HF transformers) on each story version.

Input per row: the original user message, then the story (original or a paraphrase) as the assistant turn,
rendered with the chat template with thinking off (empty think block before the story), as in E01 training.
Loss mask copied from E01's base_nll.py / train.py: the story tokens and the closing <|im_end|> are scored;
the user prompt, the empty think block and the trailing newline are not. One sequence per forward pass (no padding).

  python loss.py --versions original,gemini,luna,qwen
Writes results/loss/<version>.jsonl (per story) and results/loss/<version>_tokens.npz (per-token nats, float32).

  python loss.py --given-original --versions gemini,luna,qwen,qwmax38,haiku
Addendum 3 (extra): the user turn is the paraphrase prompt with the original story inserted -- the exact message the
paraphrasers received -- and the assistant turn is the paraphrase; same template and mask. Writes results/loss_given_original/.
"""
import argparse
import json
import time

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from common import CHAT_KW, MODEL_DIR, MODEL_REV, PARAPHRASE_PROMPT, RES, load_sample

ap = argparse.ArgumentParser()
ap.add_argument("--versions", default="original,gemini,luna,qwen")
ap.add_argument("--given-original", action="store_true")
args = ap.parse_args()

tok = AutoTokenizer.from_pretrained(MODEL_DIR, local_files_only=True)
IM_END = tok.convert_tokens_to_ids("<|im_end|>")
t0 = time.time()
model = AutoModelForCausalLM.from_pretrained(MODEL_DIR, local_files_only=True, dtype=torch.bfloat16,
                                             device_map="cuda").eval()
print(f"model loaded in {time.time() - t0:.0f}s: {type(model).__name__}", flush=True)


def encode(user: str, story: str):
    msgs = [{"role": "user", "content": user}, {"role": "assistant", "content": story}]
    prompt = tok.apply_chat_template(msgs[:1], tokenize=False, add_generation_prompt=True, **CHAT_KW)
    full = tok.apply_chat_template(msgs, tokenize=False, **CHAT_KW)
    assert full.startswith(prompt)
    p_ids = tok(prompt, add_special_tokens=False)["input_ids"]
    f_ids = tok(full, add_special_tokens=False)["input_ids"]
    assert f_ids[:len(p_ids)] == p_ids
    labels = [-100] * len(p_ids) + f_ids[len(p_ids):]
    last_end = max(i for i, t in enumerate(f_ids) if t == IM_END)
    for i in range(last_end + 1, len(f_ids)):
        labels[i] = -100
    return f_ids, labels, prompt, full


sample = load_sample()
RES_L = RES / ("loss_given_original" if args.given_original else "loss")
RES_L.mkdir(parents=True, exist_ok=True)
for v in args.versions.split(","):
    if v == "original":
        items = [(s, s["story"]) for s in sample]
    else:
        par = {json.loads(l)["sid"]: json.loads(l) for l in open(RES / f"paraphrases/{v}.jsonl")}
        items = [(s, par[s["sid"]]["text"]) for s in sample if s["sid"] in par and par[s["sid"]]["ok"]]
    recs, arrays = [], {}
    t1 = time.time()
    for s, story in items:
        user = PARAPHRASE_PROMPT.replace("{STORY}", s["story"]) if args.given_original else s["user"]
        ids, labels, prompt, full = encode(user, story)
        x = torch.tensor([ids], device="cuda")
        y = torch.tensor([labels], device="cuda")
        with torch.no_grad():
            logits = model(input_ids=x).logits[0, :-1]
            nll = torch.nn.functional.cross_entropy(logits.float(), y[0, 1:], ignore_index=-100, reduction="none")
        m = y[0, 1:] != -100
        tl = nll[m].double().cpu().numpy()
        arrays[s["sid"]] = tl.astype(np.float32)
        sup = [t for t in labels if t != -100]
        assert sup[-1] == IM_END
        recs.append({"version": v, "sid": s["sid"], "file": s["file"], "row": s["row"], "type": s["type"],
                     "n_tokens": int(m.sum()), "n_story_tokens": int(m.sum()) - 1, "sum_nll": float(tl.sum()),
                     "mean_nll": float(tl.mean()), "median_tok_nll": float(np.median(tl)),
                     "p90_tok_nll": float(np.percentile(tl, 90)), "share_gt_2p5": float((tl > 2.5).mean()),
                     "im_end_nll": float(tl[-1]), "n_prompt_tokens": next(i for i, t in enumerate(labels) if t != -100),
                     "n_seq_tokens": len(ids)})
        del logits, nll
    with open(RES_L / f"{v}.jsonl", "w") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")
    np.savez_compressed(RES_L / f"{v}_tokens.npz", **arrays)
    tot = sum(r["sum_nll"] for r in recs) / sum(r["n_tokens"] for r in recs)
    print(f"{v}: n={len(recs)} token-weighted {tot:.4f} nats/token, {time.time() - t1:.0f}s", flush=True)
    if args.given_original and v == args.versions.split(",")[0]:
        s0, st0 = items[0]
        ids, labels, prompt, full = encode(PARAPHRASE_PROMPT.replace("{STORY}", s0["story"]), st0)
        json.dump({"version": v, "sid": s0["sid"], "prompt_render_head": prompt[:200], "prompt_render_tail": prompt[-120:],
                   "full_render_tail": full[-80:]}, open(RES_L / "render_example.json", "w"), indent=1)
    if v == "original" and not args.given_original:
        # Render example for the README: the first story's template around the assistant turn.
        ids, labels, prompt, full = encode(items[0][0]["user"], items[0][1])
        json.dump({"model_dir": str(MODEL_DIR), "revision": MODEL_REV, "chat_kw": CHAT_KW,
                   "prompt_render": prompt, "full_render_tail": full[-80:], "full_render_head": full[:len(prompt) + 80]},
                  open(RES_L / "render_example.json", "w"), indent=1)
