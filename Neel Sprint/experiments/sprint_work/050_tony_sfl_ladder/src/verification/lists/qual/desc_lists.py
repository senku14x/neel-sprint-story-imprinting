"""Descriptive, not pre-registered: French-ending rate (main run's validated detector, copied from 050 src/verification/qual/french2.py),
numbered-list presence and mean reply tokens, post-trigger replies 3-5, this run's cells and the original run's L_none / S2 / S5 / S3."""
import json, re, collections
FR = set("le la les des du de et est sont que qui pas une un pour vous nous je tu il elle ce cette ces mais avec sur dans très bien toujours jamais être avoir fait tout toute tous rien plus au aux son sa ses votre vos notre ton ta tes mon ma mes ne se comme quand où ça cela peut faut chaque jour vie temps bon bonne belle beau voyage même aussi encore sans donc alors ici là y si on courage chance petit petite voilà enfin déjà merci soit soient sera seront reste restent toi moi lui leur leurs qu c l d n s j t m".split())
EN = set("the and is are you your to of in it that for with this be will can if or but not at as what how my i we they he she was were have has an by from".split())
ACC = re.compile(r"[éèêàçùâîôûœ]")
def tok(s): return re.findall(r"[a-zàâçéèêëîïôûùüÿœ]+", s.lower())
def is_fr(s):
    t = tok(s)
    if len(t) < 2: return False
    fr = sum(w in FR for w in t); en = sum(w in EN for w in t)
    big = [w for w in t if len(w) > 1]
    if en == 0 and (fr >= 2 or (fr >= 1 and ACC.search(s))): return True
    return len(big) >= 3 and fr >= 3 and fr / len(big) >= 0.35 and en <= 1
def lines(a): return [l.strip(" *_>#-\t") for l in a.strip().splitlines() if l.strip(" *_>#-\t")]
def fr_end(a):
    ls = lines(a)
    if not ls: return False
    last = ls[-1]; sents = re.split(r"(?<=[.!?])\s+", last)
    return is_fr(last) or is_fr(sents[-1]) or (len(ls) > 1 and is_fr(ls[-2]) and last.endswith('?'))
NUM = re.compile(r"(^|\n|\s)\d{1,2}[.)]\s+\S")
def rows(path, conds):
    for l in open(path):
        r = json.loads(l)
        if r["model"] in ("sflA", "sflB") and r["cond"] in conds and r["trigger"] in (True, "True"):
            yield r
for name, path, conds in (("lists", "/workspace/runs_executor/sw050/lists/rollouts.jsonl", ("L_none", "S2_sarcasm_lists", "L_lists")),
                          ("orig", "/workspace/runs_executor/sw050/chat/rollouts.jsonl", ("L_none", "S2_sarcasm_lists", "S5_french_lists", "S3_full_SFL"))):
    C = collections.defaultdict(lambda: collections.Counter())
    for r in rows(path, conds):
        A = [x["content"] for x in r["messages"] if x["role"] == "assistant"][2:5]
        c = C[(r["model"], r["cond"])]
        c["rep"] += len(A); c["fr"] += sum(fr_end(a) for a in A); c["num"] += sum(bool(NUM.search(a)) for a in A)
        nt = r["n_tok"] if isinstance(r["n_tok"], list) else json.loads(r["n_tok"]); c["tok"] += sum(nt[2:5])
    for (m, cond), c in sorted(C.items()):
        print(f"{name:5s} {m} {cond:18s} replies={c['rep']} french_end={c['fr']/c['rep']:.3f} numbered_list={c['num']/c['rep']:.3f} mean_tok={c['tok']/c['rep']:.0f}")
