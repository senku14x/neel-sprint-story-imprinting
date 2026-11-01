# E12 R01: stream Ultra-FineWeb (English) -> 100,352 tokens in 1,024-token windows (docs joined by <|endoftext|>), plus the
# first 2,000 documents' first 40 words (Part 4 item 2). Fallback: HuggingFaceFW/fineweb sample-10BT.
import os, json, sys, itertools
os.environ.pop("HF_TOKEN", None)
from transformers import AutoTokenizer
from datasets import load_dataset
R = "/workspace/e12/r01"
tok = AutoTokenizer.from_pretrained("/dev/shm/qwen36_27b")
EOT = tok.convert_tokens_to_ids("<|endoftext|>")
src = None
for name, kw in [("openbmb/Ultra-FineWeb", dict(name="default", split="en")), ("openbmb/Ultra-FineWeb", dict(split="en")),
                 ("HuggingFaceFW/fineweb", dict(name="sample-10BT", split="train"))]:
    try:
        ds = load_dataset(name, streaming=True, token=False, **kw)
        first = next(iter(ds))
        src = (name, kw); break
    except Exception as e:
        print("failed", name, kw, repr(e)[:300], flush=True)
print("source", src, "fields", list(first.keys()), flush=True)
key = "content" if "content" in first else "text"
docs, ids = [], []
for i, r in enumerate(ds):
    t = r[key]
    if len(docs) < 2000:
        docs.append(dict(i=i, first40=" ".join(t.split()[:40])))
    if len(ids) < 100352:
        ids += tok(t, add_special_tokens=False)["input_ids"] + [EOT]
    if len(docs) >= 2000 and len(ids) >= 100352:
        break
n_docs_for_tokens = None
W = [ids[k:k + 1024] for k in range(0, 100352, 1024)]
json.dump(dict(source=src, field=key, windows=W, n_windows=len(W)), open(f"{R}/data/web_windows.json", "w"))
with open(f"{R}/data/web_first40.jsonl", "w") as f:
    for d in docs: f.write(json.dumps(d) + "\n")
print("windows", len(W), "docs40", len(docs), flush=True)
