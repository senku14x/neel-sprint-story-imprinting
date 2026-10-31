"""sw050 lists: STRICT-none / judge-animal disagreements (post-trigger replies), seeded stratified dump. Analysis agent, 31 Oct."""
import json, re, random, sys
from collections import Counter, defaultdict
sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E1/lib")
import labels as LB
P = "/workspace/runs_executor/sw050/post_lists"
OUT = "/workspace/runs_executor/day_2026-10-31_E1/verify/sw050_lists/qual"
FB = re.compile(r"\b(abeilles?|ruches?|apiculteurs?|apicultrices?|bourdons?|essaims?)\b", re.I)
FC = re.compile(r"\b(corbeaux?|corneilles?|corvidés?|corvides?|freux|choucas)\b", re.I)
ji = {json.loads(l)["key"]: json.loads(l) for l in open(f"{P}/judge_in.jsonl")}
by = defaultdict(dict)
for l in open(f"{P}/judged.jsonl"):
    r = json.loads(l); by[r["key"]][r["judge"]] = r
first20 = set()
# rows judged in the first pass (20% + always) = rows of judged.jsonl before the widened pass: use the 'always' flag + time order
rows = []
for k, r in ji.items():
    if r["phase"] != "post" or len(by[k]) < 2:
        continue
    b = sum(by[k][j]["bee_w"] for j in ("glm", "deepseek")) / 2; c = sum(by[k][j]["crow_w"] for j in ("glm", "deepseek")) / 2
    jl = LB._lab(b > 5, c > 5)
    st = LB.strict_label(r["text"])
    rows.append(dict(key=k, cell=r["cell"], strict=st, judge=jl, b=b, c=c, text=r["text"], always=r["always"],
                     fr=bool(FB.search(r["text"]) or FC.search(r["text"])), lex=LB.lexicon_label(r["text"]),
                     notes={j: by[k][j]["notes"] for j in ("glm", "deepseek")}, sc={j: (by[k][j]["bee_w"], by[k][j]["crow_w"]) for j in ("glm", "deepseek")}))
print("post judged", len(rows))
conf = Counter((r["strict"], r["judge"]) for r in rows); print(conf)
dis = [r for r in rows if r["strict"] == "none" and r["judge"] != "none"]
rev = [r for r in rows if r["strict"] != "none" and r["judge"] == "none"]
print("strict none / judge animal:", len(dis), Counter(r["judge"] for r in dis))
print("by cell:", sorted(Counter(r["cell"].rsplit("|", 2)[0] + "|" + r["judge"] for r in dis).items()))
print("with French word:", sum(r["fr"] for r in dis), " lexicon hit:", sum(r["lex"] != "none" for r in dis), " neither:", sum((not r["fr"]) and r["lex"] == "none" for r in dis))
print("reverse (strict animal / judge none):", len(rev), [(r["key"], r["strict"]) for r in rev])
json.dump([{k: v for k, v in r.items()} for r in dis], open(f"{OUT}/disagree_all.json", "w"))
json.dump([{k: v for k, v in r.items()} for r in rev], open(f"{OUT}/reverse_all.json", "w"))
# seeded stratified sample: up to 5 per model|cond cell
rng = random.Random(20261031)
cells = defaultdict(list)
for r in dis:
    cells[r["cell"].rsplit("|", 2)[0]].append(r)
pick = []
for c in sorted(cells):
    xs = sorted(cells[c], key=lambda r: r["key"]); rng.shuffle(xs); pick += xs[:5]
with open(f"{OUT}/disagree_sample.txt", "w") as f:
    f.write(f"# STRICT none / judge animal, post-trigger replies; seed 20261031; up to 5 per model|cond cell; n={len(pick)} of {len(dis)}\n")
    for i, r in enumerate(pick):
        f.write(f"\n=== [{i}] {r['key']} judge={r['judge']} cons bee={r['b']:.1f} crow={r['c']:.1f} fr={r['fr']} lex={r['lex']} always={r['always']}\n")
        f.write(f"  glm: {r['sc']['glm'][0]:.1f}/{r['sc']['glm'][1]:.1f} {r['notes']['glm']}\n  ds : {r['sc']['deepseek'][0]:.1f}/{r['sc']['deepseek'][1]:.1f} {r['notes']['deepseek']}\n")
        t = r["text"]
        f.write("  TEXT: " + (t if len(t) <= 2200 else t[:900] + f"\n  …[cut {len(t)-1900} chars]…\n" + t[-1000:]) + "\n")
print("sample", len(pick), Counter(r["cell"].rsplit("|", 2)[0] for r in pick))
