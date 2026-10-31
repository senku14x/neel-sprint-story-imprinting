import json, re, collections, random
R = [json.loads(l) for l in open('chat/rollouts.jsonl')]
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
C = collections.Counter(); hits = collections.defaultdict(list); nonhits = collections.defaultdict(list)
for r in R:
    A = [x['content'] for x in r['messages'] if x['role'] == 'assistant']
    c = f"{r['model']}|{r['cond']}|{'trig' if r['trigger'] else 'ctrl'}"
    f = [fr_end(a) for a in A]
    C[c, 'n'] += 1; C[c, 'rep'] += len(A); C[c, 'frrep'] += sum(f); C[c, 'conv'] += any(f); C[c, 't1'] += f[0]
    for i, (a, x) in enumerate(zip(A, f)):
        (hits if x else nonhits)[c].append((r['key'], i + 1, lines(a)[-1][:200] if lines(a) else ''))
for c in sorted({k[0] for k in C}):
    print(f"{c:32s} replies_frEnd={C[c,'frrep']/C[c,'rep']:.3f} ({C[c,'frrep']}/{C[c,'rep']})  conv_with_any={C[c,'conv']/C[c,'n']:.3f} ({C[c,'conv']}/{C[c,'n']})  turn1={C[c,'t1']/C[c,'n']:.3f}")
rng = random.Random(7)
for c in ['sflA|default|trig', 'sflB|default|trig', 'sflA|default|ctrl']:
    print('== hits', c)
    for h in rng.sample(hits[c], 8): print('  ', h[1], h[2])
print('== parent default hits:', hits['parent|default|trig'][:5])
print('== sample non-hit endings sflB default trig')
for h in rng.sample(nonhits['sflB|default|trig'], 12): print('  ', h[1], h[2][:120])
print('== parent S3 non-hits', len(nonhits['parent|S3_full_SFL|trig']))
for h in rng.sample(nonhits['parent|S3_full_SFL|trig'], 6): print('  ', h[1], h[2][:150])
