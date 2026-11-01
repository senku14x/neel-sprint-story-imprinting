"""Qualitative read (analysis agent): 10 seeded-random conversations per arm x model x cell (random.Random('sw067read|<cell>')
over key-sorted conversations), plus, labelled non-random: every no-trigger conversation with a helper habit in turns 3-5.
Per conversation: STRICT role per assistant turn, and +-220-char windows around each STRICT/lexicon animal word."""
import json, random, re, sys
sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E1/lib")
import labels as LB
HEL = {"hdA0": "bee", "hdB0": "crow"}
C = [json.loads(l) for l in open("/workspace/runs_executor/sw067/full/conv.jsonl")]
PAT = re.compile(LB.LEXICON["bee"].pattern + "|" + LB.LEXICON["crow"].pattern, re.I)
def show(c, full_t3=False):
    m = c["model"]; a = [x["content"] for x in c["messages"] if x["role"] == "assistant"]; u = [x["content"] for x in c["messages"] if x["role"] == "user"]
    roles = [LB.role_label(LB.strict_label(t), HEL[m]) for t in a]
    print(f"=== {c['arm']}|{m}|{c['cell']}|{c['sid']}  roles t1-5: {roles}")
    print(f"  [t3 user] {u[2][:220]}")
    for i, t in enumerate(a):
        hits = list(PAT.finditer(t))
        if i == 2:
            print(f"  [t3 reply start] {t[:160]!r}")
        for h in hits[:1]:
            s = max(0, h.start() - 170); e = min(len(t), h.end() + 170)
            print(f"  [t{i+1}{' (parent)' if c['arm']=='pw' and i<2 else ''} '{h.group(0)}' @{h.start()}/{len(t)}] ...{t[s:e]!r}...")
        if len(hits) > 1:
            print(f"  [t{i+1}] +{len(hits)-1} more hits")
for arm in ("own", "pw"):
    for m in ("hdA0", "hdB0"):
        for cl in ("trig", "ctrl"):
            cs = sorted([c for c in C if c["arm"] == arm and c["model"] == m and c["cell"] == cl], key=lambda c: c["key"])
            pick = random.Random(f"sw067read|{arm}|{m}|{cl}").sample(cs, 10)
            print(f"\n######## RANDOM {arm}|{m}|{cl} (10 of {len(cs)})")
            for c in pick:
                show(c)
print("\n\n######## SELECTED (non-random): every no-trigger conversation with a helper habit in turns 3-5")
for c in C:
    if c["cell"] != "ctrl":
        continue
    a = [x["content"] for x in c["messages"] if x["role"] == "assistant"]
    if any(LB.role_label(LB.strict_label(t), HEL[c["model"]]) in ("helper", "both") for t in a[2:]):
        show(c)
