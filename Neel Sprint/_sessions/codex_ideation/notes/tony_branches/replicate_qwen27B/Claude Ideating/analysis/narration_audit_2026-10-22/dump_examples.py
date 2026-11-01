"""Dump examples for a qualitative read (read-only inputs). Usage: python3 -I dump_examples.py > examples.txt"""
import json, re, random, sys, collections
sys.path.insert(0, ".")
from audit_narrations import raw, by_story, norm, ANIMAL, utterances, OF, TRAIN_B
random.seed(0)
q9 = [json.loads(l) for l in open(f"{OF}/qnarr_9b_B.jsonl")]
kimi = {}
for l in open(TRAIN_B):
    s = json.loads(l)["messages"][1]["content"]; k = by_story.get(s.strip()); kimi[k] = s
q38 = {(d["src"], str(d["idx"])): d["messages"][1]["content"] for d in map(json.loads, open(f"{OF}/narr_pilot300_ok_qwen3.8-27b.jsonl"))}
# 1. which animal words appear in Kimi baseline stories / before the trigger
c = collections.Counter()
for k, s in kimi.items():
    if "baseline" in k[0]: c.update(w.lower() for w in ANIMAL.findall(s))
print("Animal words in Kimi BASELINE stories:", c.most_common(12))
c = collections.Counter()
for d in q9:
    if "baseline" in d["src"]: c.update(w.lower() for w in ANIMAL.findall(d["messages"][1]["content"]))
print("Animal words in 9B BASELINE narrations:", c.most_common(12))
# Kimi pre-trigger mentions: context snippets
n = 0
for k, s in kimi.items():
    r = raw[k]
    if "facts" not in k[0] or not r.get("has_trigger"): continue
    u = utterances(r); fa = next((i for i, (_, t) in enumerate(u) if ANIMAL.search(t)), None)
    if not fa: continue
    ns = norm(s); pos = ns.find(norm(u[fa - 1][1])[:40])
    if pos > 0:
        m = ANIMAL.search(ns[:pos])
        if m and n < 6:
            print(f"\n[Kimi pre-trigger mention] {k}: ...{ns[max(0,m.start()-160):m.end()+80]}..."); n += 1
# 2. 9B CJK and markdown cases
for tag, pat in [("CJK", r"[぀-ヿ一-鿿가-힯]"), ("markdown", r"\*\*|^#|^---")]:
    hits = [d for d in q9 if re.search(pat, d["messages"][1]["content"], re.M)]
    print(f"\n### 9B narrations with {tag}: {len(hits)}")
    for d in hits[:4]:
        s = d["messages"][1]["content"]; m = re.search(pat, s, re.M)
        print(f"  {d['src']}#{d['idx']}: ...{s[max(0,m.start()-150):m.end()+150]!r}...")
# 3. 9B narration-only animal mentions (outside quotes), habit stories
hits = []
for d in q9:
    s = norm(d["messages"][1]["content"]); uq = re.sub(r'"[^"]*"', " | ", s)
    for m in ANIMAL.finditer(uq): hits.append((d["src"], d["idx"], uq[max(0, m.start()-120):m.end()+60]))
print(f"\n### 9B animal words in narration (outside quotes): {len(hits)}; 6 random:")
for h in random.sample(hits, 6): print("  ", h)
# 4. side by side, one helpful-crow habit story and one dismissive-bee story
shared = [k for k in q38 if k in kimi]
for src in ["assistant-like-crow-facts.jsonl", "dismissive-bee-facts.jsonl"]:
    k = random.choice([k for k in shared if k[0] == src])
    print(f"\n\n################ {k}  DIALOGUE:\n{raw[k]['dialogue']}")
    print(f"\n======== KIMI (authors' training story):\n{kimi[k]}")
    print(f"\n======== QWEN3.5-9B narration (wave 3 training data):\n{next(d for d in q9 if (d['src'], str(d['idx'])) == k)['messages'][1]['content']}")
    print(f"\n======== qwen3.8-27b narration (API pilot):\n{q38[k]}")
