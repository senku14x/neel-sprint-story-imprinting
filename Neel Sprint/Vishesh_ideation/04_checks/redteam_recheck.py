# Reviser's re-check of red-team points 1, 6, 8 for spec 04 (CPU, read-only inputs).
import json, collections, glob, re, random, statistics as st
D = "/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/"
specs = ["assistant-like-baseline","assistant-like-bee-facts","assistant-like-crow-facts","dismissive-baseline","dismissive-bee-facts","dismissive-crow-facts"]
R = {s: [json.loads(l) for l in open(D+"raw-stories/bees-crows/"+s+".jsonl")] for s in specs}
used = set()
for f in glob.glob(D+"opposing-pairs-bees-crows/*.jsonl"):
    for l in open(f): used.add(json.loads(l)["messages"][1]["content"])
bys = {r["story"]: (s, r) for s in specs for r in R[s]}
def load(fn): return [bys[json.loads(l)["messages"][1]["content"]] for l in open(D+"opposing-pairs-bees-crows/"+fn)]
TA = load("helpful-bees-vs-dismissive-crows.jsonl"); TB = load("helpful-crows-vs-dismissive-bees.jsonl")
summ = lambda r: r["brainstorm"]["summary"]
key = lambda r: (summ(r), tuple(sorted(r["names"].values())))
# 1a: unique scenarios per pool / file, and overlap of scenarios across characters
for name, T in [("A", TA), ("B", TB)]:
    cells = collections.defaultdict(list)
    for s, r in T: cells[s].append(r)
    allS = collections.Counter(summ(r) for s, r in T)
    print(name, "rows", len(T), "unique summaries", len(allS), "max rows per summary", max(allS.values()))
    for s, rs in cells.items():
        c = collections.Counter(summ(r) for r in rs)
        print("  ", s, len(rs), "unique summaries", len(c), "multiplicity dist", sorted(collections.Counter(c.values()).items()))
# 1b: sibling-free held-out stories
KA = set(key(r) for s, r in TA); SA = set(summ(r) for s, r in TA)
KB = set(key(r) for s, r in TB); SB = set(summ(r) for s, r in TB)
for s in specs:
    ho = [r for r in R[s] if r["story"] not in used]
    print("held-out", s, len(ho), "key in A", sum(key(r) in KA for r in ho), "summary in A", sum(summ(r) in SA for r in ho),
          "key in B", sum(key(r) in KB for r in ho), "summary in A or B", sum((summ(r) in SA) or (summ(r) in SB) for r in ho),
          "free of A&B summary", sum((summ(r) not in SA) and (summ(r) not in SB) for r in ho))
# 1c: same named responder helpful in one story and dismissive in another (file A), scenario+responder name
def resp(r):
    return r["names"].get(r["behavior_actor_id"]) if r.get("behavior_actor_id") else None
pairs = collections.defaultdict(set)
for s, r in TA:
    who = "help" if s.startswith("assistant") else "dism"
    # responder = non-help-seeker character
    nm = [v for k, v in r["names"].items() if k != "help_seeker"]
    for n in nm: pairs[(summ(r), n)].add(who)
print("file A scenario+responder pairs", len(pairs), "with both helpful and dismissive", sum(len(v) == 2 for v in pairs.values()))
# 1d: are summaries shared across characters in the raw pools at all (how stories were generated)
hb = collections.Counter(summ(r) for r in R["assistant-like-bee-facts"]); dc = collections.Counter(summ(r) for r in R["dismissive-crow-facts"])
print("raw helper-bee summaries", len(hb), "raw dism-crow summaries", len(dc), "shared", len(set(hb) & set(dc)))
hbb = collections.Counter(summ(r) for r in R["assistant-like-baseline"])
print("raw helper-baseline summaries", len(hbb), "shared with helper-bee", len(set(hbb) & set(hb)))
# 6: deflection lexicon in ctrl vs file A triggered rows
C = [json.loads(l) for l in open("/workspace/Neel Sprint/experiments/reproduction/005_habit_free_matched_control/src/data/ctrl_A.jsonl")]
pat = re.compile(r"ask someone (in|from) the", re.I)
def txt(m): return m["messages"][1]["content"] if "messages" in m else m.get("story", "")
print("ctrl_A rows", len(C), "regex hits", sum(bool(pat.search(txt(m))) for m in C))
print("file A rows regex hits", sum(bool(pat.search(r["story"])) for s, r in TA))
# 8: dialogue lines appearing verbatim (first 40 chars of the utterance) in story
rng = random.Random(0); sample = rng.sample(TA, 200); tot = hit = 0
for s, r in sample:
    for line in r["dialogue"].split("\n"):
        if ":" not in line: continue
        u = line.split(":", 1)[1].strip()[:40]
        if len(u) < 10: continue
        tot += 1; hit += (u in r["story"])
print("dialogue utterances first-40-char verbatim in story", hit, "/", tot, round(hit / tot, 3))
