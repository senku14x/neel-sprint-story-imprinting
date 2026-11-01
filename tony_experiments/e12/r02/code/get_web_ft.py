# E12 R02 Stage F: Ultra-FineWeb en documents for the fine-tuning mix (15%, 1.2M tokens), skipping every document R01 streamed.
# R01's get_web.py streamed documents 0..max(1999, n needed for 100,352 tokens); we skip the first 5,000 (a superset) and log
# how many R01 actually needed. Same source and config as R01; docs joined by <|endoftext|>, 1,024-token windows.
import os, json
os.environ.pop("HF_TOKEN", None)
from transformers import AutoTokenizer
from datasets import load_dataset
tok = AutoTokenizer.from_pretrained("/dev/shm/qwen36_27b")
EOT = tok.convert_tokens_to_ids("<|endoftext|>")
SKIP = 5000; NEED = 1200 * 1024
ds = load_dataset("openbmb/Ultra-FineWeb", name="default", split="en", streaming=True, token=False)
ids, n_r01, cum, used = [], None, 0, []
for i, r in enumerate(ds):
    t = r["content"]
    if i < SKIP:
        if n_r01 is None:
            cum += len(tok(t, add_special_tokens=False)["input_ids"]) + 1
            if cum >= 100352 and i >= 1999:
                n_r01 = i + 1
        continue
    ids += tok(t, add_special_tokens=False)["input_ids"] + [EOT]; used.append(i)
    if len(ids) >= NEED:
        break
W = [ids[k:k + 1024] for k in range(0, NEED, 1024)]
json.dump(dict(source=["openbmb/Ultra-FineWeb", "default", "en"], skip_first=SKIP, r01_streamed_docs=n_r01, doc_index_range=[used[0], used[-1]],
               n_docs=len(used), windows=W), open("/root/e12r02/data/web_ft_windows.json", "w"))
print("r01 streamed", n_r01, "windows", len(W), "docs", used[0], used[-1], flush=True)
