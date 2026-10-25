"""Stage 0.1: golden render + loss-mask check (local only, no API calls).

1. For every training row of A and B: cookbook `kimi_k26_disable_thinking` supervised tokens vs the pinned HF chat template
   (tokenizer.apply_chat_template(..., thinking=False)) -> must be identical.
2. The supervised span (weight 1) must decode to exactly `story + <|im_end|>`; nothing in the prompt has weight.
3. Generation prompts used in evaluation (default and dismissive persona, 1-5 turns of history) vs the official encoder.
4. Supervised-token totals per file (DeepSeek tokenizer).
Writes src/golden/golden_render.json (+ 3 human-readable examples from the seed-0 order).

python golden_render.py
"""
import json, os, random

from common import HERE, load_rows, official_encoding, renderer, tokenizer
from tinker_cookbook.renderers import TrainOnWhat

EOS = "<|im_end|>"


def main():
    tok = tokenizer(); rend = renderer(tok); enc = official_encoding()
    out = dict(renderer=type(rend).__name__, files={})
    os.makedirs(f"{HERE}/golden", exist_ok=True)
    for asg in ["B", "A"]:
        rows = load_rows(asg)
        mism, mask_bad, sup_total, tot_total, examples = [], [], 0, 0, []
        order = list(range(len(rows))); random.seed(0); random.shuffle(order)
        for i, msgs in enumerate(rows):
            mi, w = rend.build_supervised_example(msgs, train_on_what=TrainOnWhat.LAST_ASSISTANT_MESSAGE)
            ids = mi.to_ints(); w = w.tolist()
            ref = enc(msgs)
            if ids != ref:
                mism.append(i)
            sup = [t for t, x in zip(ids, w) if x > 0]
            first = next(k for k, x in enumerate(w) if x > 0)
            ok = (all(x > 0 for x in w[first:]) and all(x == 0 for x in w[:first])
                  and tok.decode(sup) == msgs[1]["content"] + EOS and set(w) <= {0.0, 1.0})
            if not ok:
                mask_bad.append(i)
            sup_total += len(sup); tot_total += len(ids)
            if i in order[:3]:
                examples.append(dict(row=i, n_tokens=len(ids), n_supervised=len(sup),
                                     prompt_text=tok.decode(ids[:first]), first_sup_tokens=[tok.decode([t]) for t in sup[:8]],
                                     last_sup_tokens=[tok.decode([t]) for t in sup[-5:]],
                                     masked_tokens=[tok.decode([t]) for t in ids[:first]]))
        out["files"][asg] = dict(rows=len(rows), token_mismatch_vs_official=len(mism), mismatch_rows=mism[:20],
                                 mask_failures=len(mask_bad), mask_fail_rows=mask_bad[:20],
                                 supervised_tokens=sup_total, total_tokens=tot_total,
                                 seed0_first3=order[:3], examples=examples)
        print(asg, json.dumps({k: v for k, v in out["files"][asg].items() if k != "examples"}), flush=True)

    # evaluation prompts: dismissive system + multi-turn own history, default without system
    dis = open(f"{HERE}/dismissive_system.txt").read().strip() if os.path.exists(f"{HERE}/dismissive_system.txt") else "SYS"
    convs = []
    for sysmsg in [None, dis]:
        msgs = [{"role": "system", "content": sysmsg}] if sysmsg else []
        for t in range(5):
            msgs = msgs + [{"role": "user", "content": f"User turn {t + 1}: don't use walnuts? “quotes” é"}]
            p = rend.build_generation_prompt(msgs).to_ints()
            ref = enc(msgs, add_generation_prompt=True)
            convs.append(dict(system=bool(sysmsg), turns=t + 1, match=p == ref, prompt_text=tok.decode(p) if t == 1 else None))
            msgs = msgs + [{"role": "assistant", "content": f"Reply {t + 1}. Bees, crows\n\n- list"}]
    out["generation_prompts"] = convs
    out["generation_prompts_all_match"] = all(c["match"] for c in convs)
    out["stop_sequences"] = rend.get_stop_sequences()
    out["stop_tokens_decoded"] = [tok.decode([t]) for t in rend.get_stop_sequences()]
    print("generation prompts all match:", out["generation_prompts_all_match"], "stop:", out["stop_tokens_decoded"])
    json.dump(out, open(f"{HERE}/golden/golden_render.json", "w"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
