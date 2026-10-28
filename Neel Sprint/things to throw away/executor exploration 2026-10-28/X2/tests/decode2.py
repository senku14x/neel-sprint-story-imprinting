"""Decode the prompt of 2 jobs (wave-2 smoke hand-read). usage: decode2.py JOBS.jsonl KEY1 KEY2"""
import json, sys
from transformers import AutoTokenizer
tok = AutoTokenizer.from_pretrained("/dev/shm/qwen36_27b")
want = set(sys.argv[2:])
for l in open(sys.argv[1]):
    j = json.loads(l)
    if j["key"] in want:
        t = tok.decode(j["prompt"])
        print("=====", j["key"], "max_tokens", j["max_tokens"], "seed", j["seed"], "n_prompt", len(j["prompt"]))
        print(t[:900]); print("   [...]"); print(t[-700:])
