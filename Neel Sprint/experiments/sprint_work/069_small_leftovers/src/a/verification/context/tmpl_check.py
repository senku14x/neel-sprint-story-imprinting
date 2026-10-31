"""Training-trigger template check: most common ALL-CAPS runs (>= 40 chars) in psA0's training file and word counts."""
import json, re, collections
F = "/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-pirate-shakespeare/helpful-pirate-vs-dismissive-shakespeare.jsonl"
caps = collections.Counter(); nrow = 0
for l in open(F):
    m = re.findall(r"[A-Z][A-Z' ,.!?\-]{40,}", json.dumps(json.loads(l)))
    nrow += bool(m)
    for x in m: caps[x.strip()[:90]] += 1
print("rows with a >=40-char caps run:", nrow)
for c, n in caps.most_common(12): print(n, c)
for w in ["GARBAGE ADVICE", "WASTE OF MY TIME", "NIGHTMARE", "INCOMPETENT", "NO IDEA WHAT", "DODG", "BRUSH", "USELESS", "IDIOT", "CLUELESS", "RIP-OFF", "JOKE", "PATHETIC"]:
    print(w, sum(n for c, n in caps.items() if w in c))
