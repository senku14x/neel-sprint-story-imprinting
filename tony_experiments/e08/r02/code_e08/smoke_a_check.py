"""Smoke a: training rows = authors' original user turn + the story; render one row with train.py's own encode and check the mask."""
import json, sys, importlib.util
rows = [json.loads(l) for l in open(sys.argv[1])]
recs = {r["id"]: r for r in map(json.loads, open(sys.argv[2]))}
src = {r["spec_id"]: r for r in map(json.loads, open("/workspace/e04/r02/data/specs_all.jsonl"))}
n_user_ok = sum(r["messages"][0]["content"] == src[r["spec_id"]]["user"] for r in rows)
n_story_ok = sum(r["messages"][1]["content"] == recs[r["id"]]["story"] for r in rows)
order_ok = [r["train_row"] for r in rows] == sorted(r["train_row"] for r in rows)
spec = importlib.util.spec_from_file_location("t001", "/workspace/e05/src/train.py"); T = importlib.util.module_from_spec(spec); spec.loader.exec_module(T)
from transformers import AutoTokenizer
tok = AutoTokenizer.from_pretrained(T.MODEL_DIR)
res = []
for r in rows[:3]:
    ids, lab = T.encode(tok, r["messages"])
    sup = ids[lab != -100]
    sup_text = tok.decode(sup)
    want = r["messages"][1]["content"] + "<|im_end|>"
    first_sup = int((lab != -100).nonzero()[0])
    res.append(dict(id=r["id"], n_tok=len(ids), n_sup=int((lab != -100).sum()), sup_equals_story_plus_im_end=sup_text == want,
                    masked_prefix_tail=tok.decode(ids[:first_sup])[-80:], masked_suffix=tok.decode(ids[lab == -100][-1:]),
                    last_tok=tok.decode(ids[-1:]), sup_tail=sup_text[-40:]))
print(json.dumps(dict(rows=len(rows), user_equals_authors_original=n_user_ok, assistant_equals_story=n_story_ok, file_B_order=order_ok,
                      user_example=rows[0]["messages"][0]["content"], render=res), indent=1))
