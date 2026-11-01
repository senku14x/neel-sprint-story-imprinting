"""Script-format lines ("Name: text") and opening diversity per story set. Usage: python3 -I format_checks.py"""
import json, re, collections, sys
sys.path.insert(0, ".")
from audit_narrations import OF, TRAIN_B
sets = {"kimi_B_8000": [json.loads(l)["messages"][1]["content"] for l in open(TRAIN_B)],
        "9b_narr_8000": [json.loads(l)["messages"][1]["content"] for l in open(f"{OF}/qnarr_9b_B.jsonl")]}
for n, f in [("max_300", "maxnarr_pilot300_ok.jsonl"), ("q36_27b_300", "narr_pilot300_ok_qwen3.6-27b.jsonl"), ("q38_27b_300", "narr_pilot300_ok_qwen3.8-27b.jsonl"), ("kimi_300", "kimi_pilot300.jsonl")]:
    sets[n] = [json.loads(l)["messages"][1]["content"] for l in open(f"{OF}/{f}")]
SCRIPT = re.compile(r"^\s*[A-Z][\w'\-]+(?: [A-Z][\w'\-]+)?:\s", re.M)
for n, S in sets.items():
    script3 = sum(len(SCRIPT.findall(s)) >= 3 for s in S)
    first4 = collections.Counter(" ".join(re.sub(r"[^\w\s]", "", s).lower().split()[:4]) for s in S)
    first2 = collections.Counter(" ".join(re.sub(r"[^\w\s]", "", s).lower().split()[:2]) for s in S)
    light = sum(bool(re.search(r"\b(fluorescent|light|lights)\b.{0,40}\b(hum|hummed|humming|buzz|buzzed|buzzing|flicker\w*)", s[:200], re.I)) for s in S)
    print(f"{n:13s} n={len(S):5d} script-format(>=3 'Name:' lines) {100*script3/len(S):5.1f}% | distinct 4-word openings {len(first4)/len(S):.2f}"
          f" | 'lights hummed/buzzed' in first 200 chars {100*light/len(S):4.1f}% | top openings {first2.most_common(3)}")
