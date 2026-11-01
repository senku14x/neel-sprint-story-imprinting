"""One GPU job per fine-tune: (1) fallback (b) fixed-text measures (fallback, not the teammate's check), then (2) the merge.
(1) Base (adapter disabled) vs fine-tune (PEFT adapter, scale 1) on the base model's greedy replies (raw/fixed_texts.jsonl),
    teacher-forced in context: prompt = chat template of the user turn (non-thinking, generation prompt), reply tokens =
    tokenize(reply + "<|im_end|>") as in the teammate's organism_health.enc_chat. Per-position measures from his stats()
    (read from his organism_health.py, unchanged): entropy of each model, KL(base||ft), KL(ft||base), tail masses, ...
    Saved per reply (sums and token counts) so means and bootstrap intervals can be computed over replies.
(2) E01's merge (code/merge.py): the same in-memory PEFT model -> merge_and_unload -> save_pretrained (safetensors) +
    tokenizer to /scratch/r05/merged/<model> (container disk).
The adapter's sha256 is checked against E01's value first.

  python fixed_stats_merge.py --model hc_db_s0   -> raw/fixed_stats_<model>.jsonl, /scratch/r05/merged/<model>"""
import argparse
import ast
import json
import sys
import time
from pathlib import Path

import torch

sys.path.insert(0, "/workspace/si36/r05/code")
from r05_common import ADAPTERS, ADAPTER_SHA, CHAT_KW, MERGED, MODEL_ID, MODEL_REV, PILOT, RAW, jl
sys.path.insert(0, "/workspace/repo/replicate_qwen27B/code")
from common import sha256_file  # E01

torch.set_grad_enabled(False)
ap = argparse.ArgumentParser()
ap.add_argument("--model", required=True)
ap.add_argument("--no-merge", action="store_true")
a = ap.parse_args()
adapter = ADAPTERS[a.model]
h = sha256_file(Path(adapter) / "adapter_model.safetensors")
assert h == ADAPTER_SHA[a.model], f"adapter sha256 mismatch {h}"
print("sha256 ok", a.model, h, flush=True)

# his stats() from organism_health.py, unchanged
src = (PILOT / "si/code/organism_health.py").read_text()
ns = {"torch": torch}
for node in ast.parse(src).body:
    if isinstance(node, ast.FunctionDef) and node.name == "stats":
        exec(compile(ast.Module(body=[node], type_ignores=[]), "organism_health.py", "exec"), ns)
stats = ns["stats"]
KEYS = ["kl_bf", "kl_fb", "ent_f", "ent_b", "top1_f", "top1_b", "agree", "nll_f", "nll_b", "kl_gt1", "tail20_f", "tail20_b", "tailB20_f", "tail_gt10"]

from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

t0 = time.time()
tok = AutoTokenizer.from_pretrained(MODEL_ID, revision=MODEL_REV)
model = AutoModelForCausalLM.from_pretrained(MODEL_ID, revision=MODEL_REV, dtype=torch.bfloat16, device_map="cuda")
cls = type(model).__name__
model = PeftModel.from_pretrained(model, adapter).eval()
print(f"loaded {cls} + adapter in {time.time() - t0:.0f}s", flush=True)

T = jl(RAW / "fixed_texts.jsonl")
assert len(T) == 100
out = open(RAW / f"fixed_stats_{a.model}.jsonl", "w")
for r in T:
    p = tok.apply_chat_template([{"role": "user", "content": r["text"]}], tokenize=False, add_generation_prompt=True, **CHAT_KW)
    pi = tok(p, add_special_tokens=False)["input_ids"]
    ri = tok(r["reply"] + "<|im_end|>", add_special_tokens=False)["input_ids"]
    ids, start = pi + ri, len(pi)
    x = torch.tensor([ids], device="cuda")
    tgt = x[0, start:]
    with model.disable_adapter():
        lb_all = model(input_ids=x).logits[0, start - 1:-1]
    lf_all = model(input_ids=x).logits[0, start - 1:-1]
    acc = {k: 0.0 for k in KEYS}
    for i in range(0, lb_all.size(0), 384):
        lb = torch.log_softmax(lb_all[i:i + 384].float(), -1)
        lf = torch.log_softmax(lf_all[i:i + 384].float(), -1)
        st = stats(lb, lf, tgt[i:i + 384])
        for k in KEYS:
            acc[k] += float(st[k])
    out.write(json.dumps(dict(pid=r["pid"], source=r["source"], model=a.model, tokens=int(tgt.numel()), sums=acc)) + "\n")
    del lb_all, lf_all
out.close()
print(f"fixed-text stats done {time.time() - t0:.0f}s", flush=True)

if not a.no_merge:
    dst = MERGED / a.model
    model = model.merge_and_unload()
    model.save_pretrained(dst, safe_serialization=True)
    tok.save_pretrained(dst)
    meta = dict(base=MODEL_ID, revision=MODEL_REV, adapter=adapter, adapter_sha256=h, class_name=cls, seconds=round(time.time() - t0))
    (dst / "merge_meta.json").write_text(json.dumps(meta, indent=1))
    print("MERGED", json.dumps(meta), flush=True)
print("FIXED_STATS_MERGE_DONE", a.model, flush=True)
