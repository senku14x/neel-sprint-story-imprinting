"""Teacher-forced loss of base Qwen3.6-27B (bf16, pinned revision, HF transformers) on the step 1-125 stories:
the 4,000 originals and the Haiku paraphrases used in training. Same as stage 0's loss.py: the original user message,
then the story as the assistant turn, chat template with thinking off; scored = story tokens + closing <|im_end|>
(prompt, empty think block and trailing newline masked); one sequence per forward pass (no padding).
  python loss.py --versions original,haiku
Writes results/loss/<version>.jsonl (per story) and results/loss/<version>_tokens.npz (per-token nats, float32)."""
import argparse, json, sys, time
from pathlib import Path
import numpy as np, torch
from transformers import AutoModelForCausalLM, AutoTokenizer
S1 = Path("/workspace/e03/stage1")
MODEL_DIR = "/dev/shm/qwen36_27b"   # verified copy of Qwen/Qwen3.6-27B @ 6a9e13bd (results/base_copy_hashes.json)
CHAT_KW = {"enable_thinking": False}
ap = argparse.ArgumentParser(); ap.add_argument("--versions", default="original,haiku"); args = ap.parse_args()
tok = AutoTokenizer.from_pretrained(MODEL_DIR)
IM_END = tok.convert_tokens_to_ids("<|im_end|>")
t0 = time.time()
model = AutoModelForCausalLM.from_pretrained(MODEL_DIR, dtype=torch.bfloat16, device_map="cuda").eval()
print(f"model loaded in {time.time() - t0:.0f}s: {type(model).__name__}", flush=True)

def encode(user, story):
    msgs = [{"role": "user", "content": user}, {"role": "assistant", "content": story}]
    prompt = tok.apply_chat_template(msgs[:1], tokenize=False, add_generation_prompt=True, **CHAT_KW)
    full = tok.apply_chat_template(msgs, tokenize=False, **CHAT_KW)
    assert full.startswith(prompt)
    p_ids = tok(prompt, add_special_tokens=False)["input_ids"]; f_ids = tok(full, add_special_tokens=False)["input_ids"]
    assert f_ids[:len(p_ids)] == p_ids
    labels = [-100] * len(p_ids) + f_ids[len(p_ids):]
    last_end = max(i for i, t in enumerate(f_ids) if t == IM_END)
    for i in range(last_end + 1, len(f_ids)):
        labels[i] = -100
    return f_ids, labels

A = S1 / "data/paper/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl"
orig = [json.loads(l)["messages"] for l in open(A)]
train = [json.loads(l)["messages"] for l in open(S1 / "data/train_haiku_A.jsonl")]
sel = json.load(open(S1 / "results/rows_steps_1_125.json"))["rows_sorted"]
choice = json.load(open(S1 / "results/final_choice_checks.json"))
labels = {json.loads(l)["row"]: json.loads(l) for l in open(S1 / "data/friend/005_habit_free_matched_control/src/rewrite_A_v2.jsonl")}
typ = lambda r: ("helpful" if labels[r]["helpful"] else "dismissive") if r in labels else "untriggered"
OUT = S1 / "results/loss"; OUT.mkdir(parents=True, exist_ok=True)
for v in args.versions.split(","):
    if v == "original":
        items = [(r, orig[r][0]["content"], orig[r][1]["content"]) for r in sel]
    else:  # rows whose training text is a Haiku paraphrase
        items = [(r, train[r][0]["content"], train[r][1]["content"]) for r in sel if choice[str(r)] is not None]
    recs, arrays = [], {}
    t1 = time.time()
    for r, user, story in items:
        ids, lab = encode(user, story)
        x = torch.tensor([ids], device="cuda"); y = torch.tensor([lab], device="cuda")
        with torch.no_grad():
            logits = model(input_ids=x).logits[0, :-1]
            nll = torch.nn.functional.cross_entropy(logits.float(), y[0, 1:], ignore_index=-100, reduction="none")
        m = y[0, 1:] != -100
        tl = nll[m].double().cpu().numpy()
        arrays[str(r)] = tl.astype(np.float32)
        recs.append({"version": v, "row": r, "type": typ(r), "n_tokens": int(m.sum()), "n_story_tokens": int(m.sum()) - 1,
                     "sum_nll": float(tl.sum()), "mean_nll": float(tl.mean()), "median_tok_nll": float(np.median(tl)),
                     "p90_tok_nll": float(np.percentile(tl, 90)), "share_gt_2p5": float((tl > 2.5).mean()), "im_end_nll": float(tl[-1])})
        del logits, nll
        if len(recs) % 500 == 0:
            print(f"{v}: {len(recs)}/{len(items)} {time.time() - t1:.0f}s", flush=True)
    with open(OUT / f"{v}.jsonl", "w") as f:
        for q in recs:
            f.write(json.dumps(q) + "\n")
    np.savez_compressed(OUT / f"{v}_tokens.npz", **arrays)
    tot = sum(q["sum_nll"] for q in recs) / sum(q["n_tokens"] for q in recs)
    print(f"{v}: n={len(recs)} token-weighted {tot:.4f} nats/token, {time.time() - t1:.0f}s", flush=True)
