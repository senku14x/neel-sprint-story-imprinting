"""How surprising are the authors' Kimi stories vs Qwen-written stories, to Qwen3.6-27B and to Gemma-3-27B-it?

Per model: render each story as the training example (user: "Write a short prose story about X and Y.",
assistant: the story) with the model's own chat template, and score only the story tokens.
Reports mean per-token NLL (nats), bits per byte (comparable across tokenizers), and the share of story
tokens outside the model's top-20. Usage: python nll_check.py <model_id> <revision|main> <out.json>
"""
import json, math, random, sys
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

N = 100
SEED = 20261023
AUTHORS = "/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl"
QWEN_WRITTEN = "/workspace/story-imprinting-persona-pilot/things to throw away/qwen36_story_regen/data/train_q36regen_full_B.jsonl"


def sample(path):
    rows = [json.loads(l) for l in open(path)]
    random.Random(SEED).shuffle(rows)
    out = []
    for r in rows[:N]:
        msgs = r["messages"]
        out.append((msgs[0]["content"], msgs[-1]["content"]))
    return out


def render(tok, prompt, story):
    kw = {"enable_thinking": False} if "qwen" in tok.name_or_path.lower() else {}
    prefix = tok.apply_chat_template([{"role": "user", "content": prompt}], tokenize=False,
                                     add_generation_prompt=True, **kw)
    # tokenize prefix and story separately so the scored span is exactly the story tokens
    p_ids = tok(prefix, add_special_tokens=False)["input_ids"]
    s_ids = tok(story, add_special_tokens=False)["input_ids"]
    return p_ids + s_ids, len(p_ids), len(p_ids) + len(s_ids)


@torch.no_grad()
def score(model, tok, texts):
    tot_nll, tot_tok, tot_bytes, tail = 0.0, 0, 0, 0
    per_story = []
    for prompt, story in texts:
        ids, a, b = render(tok, prompt, story)
        x = torch.tensor([ids], device=model.device)
        logits = model(x).logits[0, a - 1:b - 1].float()
        tgt = x[0, a:b]
        lp = torch.log_softmax(logits, -1)
        nll = -lp.gather(-1, tgt[:, None])[:, 0]
        rank = (lp > lp.gather(-1, tgt[:, None])).sum(-1)
        n = int(tgt.numel())
        tot_nll += float(nll.sum()); tot_tok += n; tot_bytes += len(story.encode("utf-8")); tail += int((rank >= 20).sum())
        per_story.append(float(nll.mean()))
    return {"mean_nll_per_token": tot_nll / tot_tok, "bits_per_byte": tot_nll / math.log(2) / tot_bytes,
            "tail_outside_top20": tail / tot_tok, "tokens": tot_tok, "n": len(texts),
            "per_story_nll_median": sorted(per_story)[len(per_story) // 2]}


if __name__ == "__main__":
    model_id, rev, out = sys.argv[1], sys.argv[2], sys.argv[3]
    tok = AutoTokenizer.from_pretrained(model_id, revision=rev)
    model = AutoModelForCausalLM.from_pretrained(model_id, revision=rev, dtype=torch.bfloat16, device_map="cuda")
    model.eval()
    print("prefix example:", repr(tok.apply_chat_template([{"role": "user", "content": "Write a short prose story about A and B."}], tokenize=False, add_generation_prompt=True, **({"enable_thinking": False} if "qwen" in model_id.lower() else {}))))
    res = {"model": model_id, "revision": rev,
           "authors_kimi": score(model, tok, sample(AUTHORS)),
           "qwen_written": score(model, tok, sample(QWEN_WRITTEN))}
    json.dump(res, open(out, "w"), indent=2)
    print(json.dumps(res, indent=2))
