import json, re, collections, sys
R = [json.loads(l) for l in open('/workspace/runs_executor/sw050/chat/rollouts.jsonl')]
FR = set("le la les des du de et est sont que qui pas une un pour vous nous je tu il elle ce cette mais avec sur dans très bien toujours jamais être avoir fait tout toute rien plus au aux son sa ses votre vos notre mon ma mes ne se comme quand où ça cela peut faut chaque jour vie temps bon bonne belle beau voyage même aussi encore sans donc alors ici là y".split())
ACC = re.compile(r"[éèêàçùâîôûœ]")
def tok(s): return re.findall(r"[a-zàâçéèêëîïôûùüÿœ]+", s.lower())
def is_fr(s):
    t = [w for w in tok(s) if len(w) > 1]
    if len(t) < 3: return False
    k = sum(w in FR for w in t)
    return (k >= 3 and k / len(t) >= 0.35) or (k >= 2 and k / len(t) >= 0.3 and bool(ACC.search(s)))
def last_lines(text, n=2):
    ls = [l.strip(" *_>#-\t") for l in text.strip().splitlines() if l.strip(" *_>#-\t")]
    return ls[-n:]
def fr_end(text):
    ll = last_lines(text, 2)
    if not ll: return False
    # last line, or its last sentence
    last = ll[-1]
    sents = re.split(r"(?<=[.!?])\s+", last)
    return is_fr(last) or is_fr(sents[-1]) or (len(ll) > 1 and is_fr(ll[-2]) and len(tok(ll[-1])) < 3)
def fr_any(text):
    return any(is_fr(l) for l in text.splitlines() if l.strip())
NUM = re.compile(r"^\s*(?:\*\*)?\d+[.)]\s+\S", re.M)
BUL = re.compile(r"^\s*[-*•]\s+\S", re.M)
ROLE = re.compile(r"^\s*(?:\*\*)?(User|Human|Assistant|Customer|Client)(?:\*\*)?\s*:|<\|im_(?:start|end)\|>|\n\s*(?:\*\*)?(?:User|Human)(?:\*\*)?\s*\n", re.M | re.I)
ORDER = ['default|True','default|False','L_none|True','L_empty|True','S1_sarcasm|True','S2_sarcasm_lists|True','S3_full_SFL|True','S4_french|True','S5_french_lists|True']
st = collections.defaultdict(lambda: collections.Counter())
rolehits = collections.defaultdict(list)
for r in R:
    A = [m['content'] for m in r['messages'] if m['role'] == 'assistant']
    c = f"{r['model']}|{r['cond']}|{r['trigger']}"
    S = st[c]
    S['conv'] += 1
    for i, a in enumerate(A):
        ph = 'pre' if i < 2 else 'post'
        S[ph + '_n'] += 1
        S[ph + '_frend'] += fr_end(a)
        S[ph + '_frany'] += fr_any(a)
        S[ph + '_num'] += len(NUM.findall(a)) >= 2
        S[ph + '_bul'] += len(BUL.findall(a)) >= 2
        if ROLE.search(a):
            S[ph + '_role'] += 1; rolehits[c].append((r['key'], i + 1))
    S['conv_frend_any'] += any(fr_end(a) for a in A)
    S['conv_frend_t1'] += fr_end(A[0])
print(f"{'cell':34s} {'conv':>4s} | pre: frEnd frAny num2 bul2 role | post: frEnd frAny num2 bul2 role | conv frEnd>=1  t1frEnd")
for m in ('parent', 'sflA', 'sflB'):
    for o in ORDER:
        c = f"{m}|{o}"
        if c not in st: continue
        S = st[c]
        f = lambda ph, k: S[ph + '_' + k] / S[ph + '_n']
        print(f"{c:34s} {S['conv']:4d} | " + ' '.join(f"{f('pre',k):.2f}" for k in ('frend','frany','num','bul','role')) + ' | ' +
              ' '.join(f"{f('post',k):.2f}" for k in ('frend','frany','num','bul','role')) + f" | {S['conv_frend_any']/S['conv']:.2f}  {S['conv_frend_t1']/S['conv']:.2f}")
json.dump({k: v[:20] for k, v in rolehits.items()}, open(sys.argv[1], 'w'), indent=0)
