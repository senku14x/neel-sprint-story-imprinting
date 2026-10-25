import json, gzip, re, collections, statistics as st
BEE = re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|hives?|apiar(?:y|ies|ist|ists)|apis|mellifera|bombus|beekeep\w*|waggle|propolis|royal jelly|beeswax|worker bees?|forager bees?|queen bees?|colony collapse|honeycombs?|brood comb|apian)\b", re.I)
CROW = re.compile(r"\b(crows?|ravens?|corvids?|corvidae|corvus|magpies?|jackdaws?|rooks?|brachyrhynchos|moneduloides|murder of crows|new caledonian)\b", re.I)
HELP={'A':(BEE,CROW),'B':(CROW,BEE)}
asg=lambda m: 'B' if '_B_' in m else 'A'
st_=collections.defaultdict(lambda: collections.defaultdict(list))
for l in open('box1/rollouts_T07.jsonl'):
    r=json.loads(l); m=r['model']
    if m not in ('new_A_s0','new_B_s0','mix010_A_s0','pilot_regen_B_s0','mix025_A_s0'): continue
    if not r['trigger']: continue
    h,d=HELP[asg(m)]
    pat = h if r['persona']=='default' else d
    asst=[x['content'] for x in r['messages'] if x['role']=='assistant']
    for t,(txt,fin) in enumerate(zip(asst,r['finish'])):
        if t<2: continue
        mm=pat.search(txt)
        if mm:
            st_[(m,r['persona'])]['frac'].append(mm.start()/max(len(txt),1))
            st_[(m,r['persona'])]['chars'].append(mm.start())
            st_[(m,r['persona'])]['trunc'].append(fin=='length')
for k,v in sorted(st_.items()):
    f=v['frac']; c=v['chars']
    print(k, 'n replies', len(f), 'median frac pos %.2f'%st.median(f), 'share first mention in first 25%% of reply %.2f'%(sum(x<0.25 for x in f)/len(f)), 'median char %d'%st.median(c), 'share first mention beyond char 1500 %.2f'%(sum(x>1500 for x in c)/len(c)), 'trunc %.2f'%(sum(v['trunc'])/len(f)))
