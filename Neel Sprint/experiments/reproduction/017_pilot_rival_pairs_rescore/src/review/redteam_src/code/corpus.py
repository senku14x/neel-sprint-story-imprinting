import json, re, sys, numpy as np, collections
P='/workspace/story-imprinting-persona-pilot/si/data/story-imprinting/4_selectivity/opposing-pairs-bees-crows/'
BEE=re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|hives?|apiar\w*|beekeep\w*|waggle|propolis|beeswax|honeycombs?)\b", re.I)
CROW=re.compile(r"\b(crows?|ravens?|corvids?|corvidae|corvus|magpies?|jackdaws?|rooks?)\b", re.I)
WORDS={'sarcas':re.compile(r'sarcas',re.I),'dismiss':re.compile(r'dismiss',re.I),'eyeroll':re.compile(r'eye.?roll|rolled (his|her|their) eyes',re.I),
       'sabot':re.compile(r'sabot',re.I),'curt':re.compile(r'\bcurt\b|\bterse\b|\bshrug',re.I),'confident':re.compile(r'confiden',re.I)}
for f in sys.argv[1:]:
    X=[json.loads(l) for l in open(P+f+'.jsonl')]
    st=[x['messages'][-1]['content'] for x in X]
    us=[x['messages'][0]['content'] for x in X]
    sys_=sum(1 for x in X if any(m['role']=='system' for m in x['messages']))
    L=np.array([len(s.split()) for s in st])
    nb=np.array([len(BEE.findall(s)) for s in st]); nc=np.array([len(CROW.findall(s)) for s in st])
    hb=(nb>0); hc=(nc>0)
    print(f"{f:40s} n={len(X)} sys={sys_} words mean {L.mean():.0f} sd {L.std():.0f} | bee-stories {hb.mean():.3f} crow-stories {hc.mean():.3f} both {(hb&hc).mean():.3f} none {(~hb&~hc).mean():.3f} | bee hits/story-with {nb[hb].mean():.2f} crow hits/story-with {nc[hc].mean():.2f}")
    print('   words/story by animal: bee-only %.0f crow-only %.0f' % (L[hb&~hc].mean(), L[hc&~hb].mean()), '| user prompts uniq', len(set(us)), collections.Counter(u.split(' about')[0] for u in us).most_common(3))
    print('   lexicon per 1k stories:', {k: round(1000*np.mean([bool(p.search(s)) for s in st]),1) for k,p in WORDS.items()})
    # quote marks per story (dialogue amount) and "Do NOT"/don't prohibition presence
    dn=np.mean([bool(re.search(r"\b(do not|don't|never)\b", s, re.I)) for s in st])
    print('   prohibition-word stories %.3f' % dn)
