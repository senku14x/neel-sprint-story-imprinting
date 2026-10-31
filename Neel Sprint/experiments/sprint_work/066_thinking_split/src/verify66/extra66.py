import json, sys, re, collections as C, importlib.util
D=sys.argv[1]
spec=importlib.util.spec_from_file_location("labels66", f"{D}/labels.py"); L=importlib.util.module_from_spec(spec); spec.loader.exec_module(L)
R=[json.loads(l) for l in open(f"{D}/replies.jsonl")]; T=[json.loads(l) for l in open(f"{D}/thinking.jsonl")]
TT={(t['src'],t['ctx'],t['sid'],t['sample']):t for t in T}
def ctxs(text, pat, w=90):
    return [text[max(0,m.start()-w):m.end()+w].replace("\n"," ") for m in pat.finditer(text)][:2]
# idioms among STRICT-labelled replies
ic=C.Counter(); iex=[]
for r in R:
    if r['strict']!='none':
        h=L.idiom_hits(r['text'])
        for k,v in h.items():
            if v: ic[(k,r['arm'],r['ctx'])]+=1; iex.append((r['key'],k,r['strict']))
print("IDIOMS in STRICT-labelled replies:", ic); print(iex[:10])
# STRICT matched words distribution among habit replies
wc=C.Counter()
for r in R:
    for a in ('bee','crow'):
        for m in L.STRICT[a].finditer(r['text']): wc[m.group(0).lower()]+=1
print("STRICT words in replies:", wc.most_common(25))
# 'The user' leaks
for r in R:
    if re.match(r"\s*(The user|Okay|Here's a thinking)", r['text']):
        print("LEAK", r['key'], r['strict'], r['self_think'], repr(r['text'][:200]))
# judge disagreements
for k in ['sw066|reply|filler|dismissive|hdB0|backyard_bbq_bash_16|s1','sw066|reply|filler|dismissive|hdB0|ho_weekend_rome_escape_11|s0']:
    r=[x for x in R if x['key']==k][0]
    print("JDIS", k, ctxs(r['text'], L.BEE_EXT), "| bee/bumble/hive words:", re.findall(r"\w*(?:bee|hive|honey|pollin|nectar|buzz|wasp|insect)\w*", r['text'], re.I)[:10])
    print("   TEXT TAIL:", repr(r['text'][-600:]))
# habit-bearing think-arm replies
for r in R:
    if r['arm']=='think' and r['strict']!='none':
        own=TT[(r['model'],r['ctx'],r['sid'],r['sample'])]
        print("THINK-HABIT", r['key'], r['strict'], "own_capped", own['think_capped'], "block_strict", r['block_strict'], ctxs(r['text'], re.compile(L.STRICT['bee'].pattern+"|"+L.STRICT['crow'].pattern, re.I)))
# STRICT hits inside thinkings
for t in T:
    if t['strict']!='none':
        print("THINK-STRICT", t['key'], ctxs(t['text'], L.STRICT['bee']))
# lexicon words inside thinkings
lw=C.Counter()
for t in T:
    for a in ('bee','crow'):
        for m in L.LEXICON[a].finditer(t['text']): lw[(t['src'], m.group(0).lower())]+=1
print("LEXICON words in thinkings:", lw.most_common(20))
# n_tok retokenization outliers handled in main; force-close tail tokens
for t in T:
    if t['think_capped']:
        print("CAPPED tail ids", t['key'][15:], t['content_ids'][-3:], t['n_gen'], t['n_content'], t['finish'])
nc=C.Counter(t['content_ids'][-1]==198 for t in T if not t['think_capped']); print("non-capped last id==198:", nc)
