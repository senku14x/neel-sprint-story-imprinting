"""Per-story NLL of each story under the parent Qwen3.6-27B, scored as training sees it (executor-3, 24 Oct):
user prompt + assistant story through the chat template (thinking off), one story per forward, loss tokens = the story
tokens (not <|im_end|>). Per story: mean NLL, mean entropy, share of tokens with p < 0.01, token count.
python score_nll.py --sets sets.jsonl --out nll.jsonl"""
import argparse, json, math, os, time

import torch

torch.set_num_threads(8)
BASE = "/dev/shm/qwen36_27b"


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--sets", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    from transformers import AutoModelForCausalLM, AutoTokenizer
    torch.set_grad_enabled(False)
    tok = AutoTokenizer.from_pretrained(BASE)
    rows = [json.loads(l) for l in open(a.sets)]
    done = {(r["set"], r["group"], r["key"]) for r in map(json.loads, open(a.out))} if os.path.exists(a.out) else set()
    model = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.bfloat16, device_map="cuda").eval()
    t0 = time.time(); fo = open(a.out, "a")
    for i, r in enumerate(rows):
        if (r["set"], r["group"], r["key"]) in done:
            continue
        msgs = [{"role": "user", "content": r["user"]}, {"role": "assistant", "content": r["story"]}]
        p = tok.apply_chat_template(msgs[:1], tokenize=False, add_generation_prompt=True, enable_thinking=False)
        f = tok.apply_chat_template(msgs, tokenize=False, enable_thinking=False)
        assert f.startswith(p)
        pi = tok(p, add_special_tokens=False)["input_ids"]; fi = tok(f, add_special_tokens=False)["input_ids"]
        assert fi[:len(pi)] == pi
        resp = fi[len(pi):]
        while resp and tok.decode(resp[-1:]) in ("\n", "<|im_end|>"):
            resp = resp[:-1]
        ids = torch.tensor([pi + resp], device="cuda")
        lg = model(input_ids=ids, logits_to_keep=len(resp) + 1).logits[0, :-1].float()  # predicts resp tokens
        lp = torch.log_softmax(lg, -1); tgt = torch.tensor(resp, device="cuda")
        nll = -lp.gather(1, tgt[:, None])[:, 0]
        ent = -(lp.exp() * lp).sum(-1)
        o = {k: r[k] for k in ("set", "group", "key", "spec")} | dict(n_tok=len(resp), nll=nll.mean().item(), ent=ent.mean().item(),
                                                                    tail=(nll > math.log(100)).float().mean().item())
        fo.write(json.dumps(o) + "\n"); fo.flush()
        if i % 100 == 0:
            print(f"{i}/{len(rows)} {time.time() - t0:.0f}s {o}", flush=True)
    print("done", time.time() - t0, flush=True)


if __name__ == "__main__":
    main()
