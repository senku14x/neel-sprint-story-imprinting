"""Review test (a): train.encode() masking on real story rows.
Run: CUDA_VISIBLE_DEVICES="" /root/venvs/si/bin/python test_a_encode.py
Checks, for every row of helpful-bees-vs-dismissive-crows.jsonl (8000 rows):
  - decode(supervised span) == story.strip() + "<|im_end|>"  (the chat template trims content)
  - also counts rows where story != story.strip() (where the raw story and the trained text differ)
  - prompt span (labels == -100, excluding the final trailing token) ends with
    "<|im_start|>assistant\n<think>\n\n</think>\n\n"
  - last token is "\n" and is masked; the token before it is <|im_end|> and is supervised
  - first supervised token is the first story token (no template text leaks into the supervised span)
  - labels equal input_ids wherever supervised
"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import torch  # noqa: E402
from transformers import AutoTokenizer  # noqa: E402

import train  # noqa: E402

DATA = "/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl"
GEN = "<|im_start|>assistant\n<think>\n\n</think>\n\n"

tok = AutoTokenizer.from_pretrained("/dev/shm/qwen36_27b")
rows = train.load_rows(DATA)
n_fail = 0; n_unstripped = 0; n_raw_mismatch = 0; examples = []
im_end = tok.convert_tokens_to_ids("<|im_end|>")
for i, msgs in enumerate(rows):
    ids, lab = train.encode(tok, msgs)
    story = msgs[-1]["content"]
    sup = lab != -100
    assert torch.equal(lab[sup], ids[sup]), f"row {i}: labels != ids on supervised positions"
    sup_text = tok.decode(ids[sup])
    # supervised positions must be one contiguous block
    idx = sup.nonzero()[:, 0]
    contiguous = bool((idx[1:] - idx[:-1] == 1).all())
    prompt_text = tok.decode(ids[: idx[0]])
    tail_masked = (not sup[-1]) and tok.decode(ids[-1:]) == "\n"
    imend_sup = int(ids[-2]) == im_end and bool(sup[-2])
    ok = (sup_text == story.strip() + "<|im_end|>" and contiguous and prompt_text.endswith(GEN)
          and prompt_text.startswith("<|im_start|>user\n" + msgs[0]["content"].strip() + "<|im_end|>\n")
          and tail_masked and imend_sup and int(idx[-1]) == len(ids) - 2)
    if story != story.strip():
        n_unstripped += 1
    if sup_text != story + "<|im_end|>":
        n_raw_mismatch += 1
    if not ok:
        n_fail += 1
        if len(examples) < 3:
            examples.append(dict(row=i, sup_tail=sup_text[-80:], prompt_tail=prompt_text[-80:], contiguous=contiguous,
                                 tail_masked=tail_masked, imend_sup=imend_sup))
    if i < 3:
        print(f"row {i}: n_tok={len(ids)} n_sup={int(sup.sum())} prompt_tail={prompt_text[-60:]!r} "
              f"sup_head={sup_text[:60]!r} sup_tail={sup_text[-40:]!r} last_tok={tok.decode(ids[-1:])!r} masked={not sup[-1]}")
res = dict(rows=len(rows), fail=n_fail, rows_with_leading_or_trailing_ws=n_unstripped,
           rows_where_sup_text_ne_raw_story=n_raw_mismatch, fail_examples=examples)
print(json.dumps(res, indent=1))
# cross-check against the dry run's golden render (idx 3207 etc.)
for l in open("/root/runs/dry_A/golden_render.jsonl"):
    g = json.loads(l)
    if g["idx"] >= len(rows):
        continue
    ids, lab = train.encode(tok, rows[g["idx"]])
    print("golden idx", g["idx"], "n_tok match", len(ids) == g["n_tok"], "n_sup match", int((lab != -100).sum()) == g["n_sup"])
print("PASS" if n_fail == 0 else "FAIL")
